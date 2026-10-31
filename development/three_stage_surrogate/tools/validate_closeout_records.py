#!/usr/bin/env python3
"""Cross-check durable closeout records and compact published evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN = ROOT / "development" / "three_stage_surrogate"
OUTPUT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/"
    "surrogate_input_data"
)
ITERATION = "iter001"
PLAN_SHA256 = "347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c"
OBJECTIVE = "Initialize and validate reusable ABBY/JERC surrogate input data without training"
SUMMARY_PATH = "development/three_stage_surrogate/summaries/iter001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-job-count", type=int, required=True)
    args = parser.parse_args()
    require(args.active_job_count == 0, "active Iter001 jobs remain")

    report = (CAMPAIGN / "iterations" / "iter001.md").read_text()
    cumulative = (CAMPAIGN / "ITERATION_SUMMARY.md").read_text()
    handoff = (CAMPAIGN / "handoff" / "CURRENT.md").read_text()
    compact = (CAMPAIGN / "summaries" / "iter001" / "summary.md").read_text()

    for text, label in (
        (report, "report"),
        (cumulative, "cumulative summary"),
        (handoff, "handoff"),
        (compact, "compact summary"),
    ):
        require("iter001" in text, f"{label} lacks iteration identity")
        require("data_initialization" in text, f"{label} lacks work type")
        require("819" in text and "205" in text, f"{label} split counts drifted")
        require("ABBY" in text and "JERC" in text, f"{label} site scope drifted")
        require("r0001" in text, f"{label} snapshot revision drifted")
        require("no training" in text.lower(), f"{label} no-training boundary drifted")

    require("- Status: `completed`" in report, "report is not completed")
    require("- Phase: `closed`" in report, "report phase is not closed")
    require(f"- Locked plan SHA-256: `{PLAN_SHA256}`" in report, "report plan hash drifted")
    require("- Status: `completed`" in handoff, "handoff is not completed")
    require("- Phase: `closed`" in handoff, "handoff phase is not closed")
    require("- Active job scope: none" in handoff, "handoff retains active job scope")
    require("Package state: `closed`" in handoff, "handoff package state is not closed")
    require(PLAN_SHA256 in handoff and PLAN_SHA256 in compact, "plan hash agreement failed")
    require("Iter002" in report and "Iter002" in cumulative and "Iter002" in handoff,
            "next iteration identity drifted")
    require("fresh" in report.lower() and "approval" in report.lower(),
            "report lacks fresh-approval boundary")
    require("fresh" in handoff.lower() and "approval" in handoff.lower(),
            "handoff lacks fresh-approval boundary")

    with (CAMPAIGN / "registry.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 1, "registry must contain exactly one closed iteration")
    row = rows[0]
    require(row["iteration_id"] == ITERATION, "registry iteration ID drifted")
    require(row["status"] == "completed", "registry status drifted")
    require(row["work_type"] == "data_initialization", "registry work type drifted")
    require(row["objective"] == OBJECTIVE, "registry objective drifted")
    require(row["acceptance_result"] == "pass", "registry result drifted")
    require(row["summary_path"] == SUMMARY_PATH, "registry summary path drifted")
    require(row["closeout_mode"] == "committed", "registry closeout mode drifted")
    require("expected_parent=174a7f6c33acbf111ef67533d6ef69ea33c91565" in row["closeout_identity"],
            "registry expected parent drifted")
    require("expected_subject=Initialize ABBY JERC surrogate input data" in row["closeout_identity"],
            "registry expected subject drifted")

    validation = json.loads(
        (CAMPAIGN / "summaries" / "iter001" / "iter001_validation_report.json").read_text()
    )
    require(validation["result"] == "pass" and validation["no_training"] is True,
            "validation report did not pass no-training gate")
    require(validation["member_count"] == 1024 and validation["parameter_count"] == 18,
            "validation report member/parameter counts drifted")
    require(validation["development_count"] == 819 and validation["fixed_test_count"] == 205,
            "validation report split counts drifted")
    require([item["site"] for item in validation["sites"]] == ["ABBY", "JERC"],
            "validation report site order drifted")
    require(all(item["members"] == 1024 and item["hours"] == 61320
                for item in validation["sites"]), "site coverage drifted")

    catalog = json.loads((OUTPUT / "catalog.json").read_text())
    require(catalog["schema"] == "three-stage-surrogate-catalog-v1", "catalog schema drifted")
    require(catalog["current_snapshot"] == "manifests/dataset_snapshot_r0001.json",
            "catalog current snapshot drifted")
    snapshot_path = OUTPUT / catalog["current_snapshot"]
    require(sha256(snapshot_path) == catalog["current_snapshot_sha256"],
            "catalog snapshot hash mismatch")
    snapshot = json.loads(snapshot_path.read_text())
    require(snapshot["revision"] == "r0001", "snapshot revision drifted")
    require(snapshot["member_count"] == 1024, "snapshot member count drifted")
    require(snapshot["sites"] == ["ABBY", "JERC"], "snapshot site order drifted")
    require(snapshot["hour_count_by_site"] == {"ABBY": 61320, "JERC": 61320},
            "snapshot hour coverage drifted")
    for relative, identity in snapshot["artifacts"].items():
        artifact = OUTPUT / relative
        require(artifact.is_file(), f"published artifact missing: {relative}")
        require(artifact.stat().st_size == identity["size_bytes"],
                f"published artifact size drifted: {relative}")

    for job_id in ("24428809", "24428935", "24430059", "24430075", "24430091"):
        require(job_id in report, f"job accounting absent from report: {job_id}")
    require("ITER001_PREFLIGHT_OK" in report, "preflight pass marker absent")
    require("PREPARE_SURROGATE_INPUT_OK" in report, "preparation pass marker absent")
    require("VALIDATE_SURROGATE_INPUT_OK" in report, "validation pass marker absent")

    print(
        "ITER001_FOUR_RECORD_VALIDATE_PASS "
        "records=report,summary,registry,handoff "
        "snapshot=r0001 sites=ABBY,JERC members=1024 split=819/205 active_jobs=0"
    )


if __name__ == "__main__":
    main()
