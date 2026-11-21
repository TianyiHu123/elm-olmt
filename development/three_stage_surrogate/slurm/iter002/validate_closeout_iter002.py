#!/usr/bin/env python3
"""Static cross-record and external-evidence validator for Iter002 closeout."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = ROOT / "development" / "three_stage_surrogate"
OUTPUT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/"
    "iter002_abby_jerc_spinup_baseline"
)
PLAN_SHA256 = "9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
OPERATIONAL_ARTIFACT = "4c42e818e124a2f72ed54635ae02979afeb7ec10518c15be187b8775e6947064"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_package(package: Path, kind: str, train: int, validation: int) -> None:
    manifest = json.loads((package / "package_manifest.json").read_text())
    require(manifest["run_kind"] == kind, f"{kind} package role drifted")
    for relative, identity in manifest["files"].items():
        path = package / relative
        require(path.is_file(), f"{kind} package file missing: {relative}")
        require(path.stat().st_size == identity["size_bytes"], f"{kind} size drifted: {relative}")
        require(sha256(path) == identity["sha256"], f"{kind} hash drifted: {relative}")
    artifact_manifest = json.loads((package / "artifact" / "artifact_manifest.json").read_text())
    require(artifact_manifest["target_transform"] == "natural_log", f"{kind} target transform drifted")
    require(len(artifact_manifest["fit_scope"]["train_member_ids"]) == train, f"{kind} train count drifted")
    require(len(artifact_manifest["fit_scope"]["validation_member_ids"]) == validation,
            f"{kind} validation count drifted")
    artifact = package / "artifact" / artifact_manifest["artifact_filename"]
    require(sha256(artifact) == artifact_manifest["artifact_sha256"], f"{kind} artifact hash drifted")
    metrics = json.loads((package / "metrics.json").read_text())
    require(metrics["target_transform"] == "natural_log", f"{kind} metrics transform drifted")
    require(len(metrics["rows"]) == 24, f"{kind} metric coverage drifted")
    require(len(metrics["validation_minus_training_gaps"]) == 12, f"{kind} gap coverage drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-job-count", type=int, required=True)
    args = parser.parse_args()
    require(args.active_job_count == 0, "active Iter002 jobs remain")

    report = (CAMPAIGN / "iterations" / "iter002.md").read_text()
    cumulative = (CAMPAIGN / "ITERATION_SUMMARY.md").read_text()
    handoff = (CAMPAIGN / "handoff" / "CURRENT.md").read_text()
    compact = (CAMPAIGN / "summaries" / "iter002" / "summary.md").read_text()
    for text, label in ((report, "report"), (cumulative, "summary"), (handoff, "handoff"), (compact, "compact")):
        require("iter002" in text, f"{label} lacks iteration identity")
        require("implementation" in text, f"{label} lacks work type")
        require("ABBY" in text and "JERC" in text, f"{label} site scope drifted")
        require("819" in text and "205" in text, f"{label} split boundary drifted")
        require("r0001" in text, f"{label} snapshot identity drifted")
        require("optimization_recommended" in text, f"{label} decision drifted")

    require("- Status: `completed`" in report and "- Phase: `closed`" in report,
            "report is not closed/completed")
    require(f"- Locked plan SHA-256: `{PLAN_SHA256}`" in report, "report plan identity drifted")
    require("- Status: `completed`" in handoff and "- Phase: `closed`" in handoff,
            "handoff is not closed/completed")
    require("- Active job scope: none" in handoff, "handoff retains active job scope")
    require("Package state: `closed`" in handoff, "handoff package state drifted")
    require(PLAN_SHA256 in handoff and PLAN_SHA256 in compact, "plan identity agreement failed")

    report_proposal = report.split("### Iter003 - ABBY/JERC spinup configuration experiment", 1)[1]
    report_proposal = report_proposal.split("## Closeout Checklist", 1)[0].strip()
    handoff_proposal = handoff.split("### Iter003 - ABBY/JERC spinup configuration experiment", 1)[1].strip()
    require(report_proposal == handoff_proposal, "Iter003 proposal differs between report and handoff")
    require("Fresh consolidated kickoff approval" in report and "Fresh consolidated kickoff approval" in handoff,
            "fresh-approval boundary drifted")

    with (CAMPAIGN / "registry.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    require([row["iteration_id"] for row in rows] == ["iter001", "iter002"], "registry identity/order drifted")
    row = rows[-1]
    require(row["status"] == "completed" and row["work_type"] == "implementation", "registry status/type drifted")
    require(row["acceptance_result"] == "pass", "registry acceptance result drifted")
    require("Optimization recommended" in row["decision"], "registry decision drifted")
    require(row["summary_path"] == "development/three_stage_surrogate/summaries/iter002",
            "registry summary path drifted")
    require(row["closeout_mode"] == "committed", "registry closeout mode drifted")
    require("expected_parent=66975fc84b635624f3c1fa4ae00afd77195f4e3b" in row["closeout_identity"],
            "registry expected parent drifted")

    smoke = OUTPUT / "runs" / "smoke_80_20" / "attempt_2" / "package"
    operational = OUTPUT / "runs" / "operational_655_164" / "attempt_2" / "package"
    validate_package(smoke, "smoke", 80, 20)
    validate_package(operational, "operational", 655, 164)
    operational_manifest = json.loads((operational / "artifact" / "artifact_manifest.json").read_text())
    require(operational_manifest["artifact_sha256"] == OPERATIONAL_ARTIFACT,
            "operational artifact identity drifted")

    external_validation = OUTPUT / "runs" / "validation" / "attempt_2" / "validation_report.json"
    compact_validation = CAMPAIGN / "summaries" / "iter002" / "iter002_validation_report.json"
    require(sha256(external_validation) == sha256(compact_validation), "validation report copy drifted")
    validation = json.loads(external_validation.read_text())
    require(validation["result"] == "pass", "independent validation did not pass")
    require(validation["fixed_test_access"] is False and validation["all_819_prediction_created"] is False,
            "scope boundary drifted")
    require(validation["fresh_process_reload_match"] is True, "reload equivalence drifted")
    require(validation["flexible_prediction_counts"] == {
        "operational164": 164, "single": 1, "smoke20": 20, "subset": 7
    }, "prediction count coverage drifted")

    for job_id in ("24450843", "24450877", "24450974", "24451007", "24453838", "24453852"):
        require(job_id in report, f"job accounting absent from report: {job_id}")
    require("ITER002_PREFLIGHT_OK" in report and "ITER002_VALIDATE_OK" in report,
            "pass markers absent from report")
    print(
        "ITER002_FOUR_RECORD_VALIDATE_PASS "
        "records=report,summary,registry,handoff result=pass "
        "decision=optimization_recommended active_jobs=0"
    )


if __name__ == "__main__":
    main()
