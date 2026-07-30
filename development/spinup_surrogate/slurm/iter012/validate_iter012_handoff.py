#!/usr/bin/env python3
"""Cross-check the four authoritative Iter012 records and released artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SPINUP = ROOT / "development" / "spinup_surrogate"
SUMMARY = SPINUP / "summaries" / "iter012"
EXPECTED = {
    "drop32": {
        "path": Path(
            "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
            "spinup_surrogate_iter012_drop32/surrogate_spinup/"
            "spinup_surrogate_iter012_drop32.pkl"
        ),
        "size": 80440,
        "sha256": "56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e",
        "features": 32,
    },
    "drop21_corr080": {
        "path": Path(
            "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
            "spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/"
            "spinup_surrogate_iter012_drop21_corr080.pkl"
        ),
        "size": 68048,
        "sha256": "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023",
        "features": 21,
    },
}
NEXT_PLAN = """## Proposed Next-Iteration Plan (Planning Only)

Iter012 is the terminal spinup-surrogate development release. No Iter013 experiment is proposed.
Future work, under a separate objective and runtime contract, may integrate a released spinup
artifact with a real forcing-surrogate artifact and validate actual forcing-target predictions."""
SUMMARY_ROOT = "development/spinup_surrogate/summaries/iter012"
OBJECTIVE = "Final versioned spinup-surrogate release"
HEADLINE = {
    "drop32": ("0.827271", "0.827497"),
    "drop21_corr080": ("0.801217", "0.801178"),
}
REQUIRED_REPO_PATHS = (
    "README.md",
    "development/hpc/puma.md",
    "development/spinup_surrogate/WORKFLOW.md",
    "development/spinup_surrogate/ITERATION_SUMMARY.md",
    "development/spinup_surrogate/registry.csv",
    "development/spinup_surrogate/handoff/CURRENT.md",
    "development/spinup_surrogate/iterations/iter012.md",
    "development/spinup_surrogate/slurm/iter012",
    "development/spinup_surrogate/summaries/iter012",
)


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
    require(args.active_job_count == 0, "active Iter012 jobs remain")

    report = (SPINUP / "iterations" / "iter012.md").read_text()
    cumulative = (SPINUP / "ITERATION_SUMMARY.md").read_text()
    handoff = (SPINUP / "handoff" / "CURRENT.md").read_text()
    readme = (ROOT / "README.md").read_text()

    # Primary four-record consistency.
    require("- Iteration ID: `iter012`" in report, "report iteration ID drifted")
    require("- Status: `completed`" in report, "iteration report is not completed")
    require("# Spinup Surrogate Iteration Summary: iter001-iter012" in cumulative,
            "cumulative summary does not include Iter012")
    require("- Latest iteration: `iter012`" in handoff, "handoff latest ID drifted")
    require("- Status: `completed`" in handoff, "handoff is not completed")
    require("- Phase: `closed`" in handoff, "handoff phase is not closed")
    require(NEXT_PLAN in report, "iteration report next-plan text drifted")
    handoff_plan = NEXT_PLAN.replace(
        "## Proposed Next-Iteration Plan (Planning Only)",
        "## Next Iteration Plan (Planning Only)",
    )
    require(handoff_plan in handoff, "handoff next-plan text drifted")

    with (SPINUP / "registry.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    row = next((item for item in rows if item["iter_id"] == "iter012"), None)
    require(row is not None, "registry lacks iter012")
    require(row["status"] == "completed", "registry Iter012 is not completed")
    require(row["objective"] == OBJECTIVE, "registry objective drifted")
    require(row["best_variant"] == "drop32", "registry recommendation drifted")
    require(row["summary_root"] == SUMMARY_ROOT,
            "registry summary path drifted")
    require(row["seed_range"] == "10001 reproduction; full 900-row fit",
            "registry reproduction/full-fit scope drifted")
    require(row["variants"].split("|") == ["drop32", "drop21_corr080"],
            "registry variant policy/count drifted")
    require(row["best_r2_val_totsomc_median"] == HEADLINE["drop32"][0],
            "registry TOTSOMC headline metric drifted")
    require(row["best_r2_val_totsomn_median"] == HEADLINE["drop32"][1],
            "registry TOTSOMN headline metric drifted")

    for text, label in ((report, "report"), (cumulative, "summary"), (handoff, "handoff")):
        require("iter012" in text, f"{label} lacks latest iteration ID")
        require("drop32" in text and "drop21_corr080" in text,
                f"{label} variant set drifted")
        require("900" in text and "10001" in text,
                f"{label} reproduction/full-fit scope drifted")
        require(SUMMARY_ROOT in text, f"{label} summary path drifted")
        require("release" in text.lower() and "compact" in text.lower(),
                f"{label} release conclusion drifted")
    require("recommended accuracy-oriented" in report.lower(),
            "report recommendation drifted")
    require("recommended accuracy-oriented" in cumulative.lower(),
            "summary recommendation drifted")
    require("recommended `drop32`" in handoff.lower(),
            "handoff recommendation drifted")
    require("failed" in report.lower() and "median-rmse-ratio" in report.lower(),
            "report compact gate outcome drifted")
    require("failed" in cumulative.lower() and "rmse-ratio" in cumulative.lower(),
            "summary compact gate outcome drifted")
    require("failed" in handoff.lower() and "rmse-ratio" in handoff.lower(),
            "handoff compact gate outcome drifted")
    for variant, metrics in HEADLINE.items():
        for metric in metrics:
            require(metric in report, f"{variant} metric {metric} absent from report")
            require(metric in cumulative, f"{variant} metric {metric} absent from summary")
            require(metric in handoff, f"{variant} metric {metric} absent from handoff")

    require("Status: `planned`" not in report, "report retains planned status")
    require("Status: `in_progress`" not in handoff, "handoff retains in-progress status")
    require("Iter011 closed" not in handoff, "handoff retains stale latest heading")
    require("No Iter013 experiment is proposed" in cumulative,
            "cumulative next-iteration boundary drifted")
    require("separate objective and runtime contract" in report,
            "report lacks fresh-contract boundary")
    require("separate objective and runtime contract" in handoff,
            "handoff lacks fresh-contract boundary")

    decision_path = SUMMARY / "iter012_release_decision.json"
    decision = json.loads(decision_path.read_text())
    require(decision["iteration"] == "iter012" and decision["passed"] is True,
            "release decision did not pass")

    for variant, expected in EXPECTED.items():
        artifact = expected["path"]
        require(artifact.is_file(), f"{variant} artifact missing")
        require(artifact.stat().st_size == expected["size"], f"{variant} size drifted")
        require(sha256(artifact) == expected["sha256"], f"{variant} hash drifted")
        gate = decision["variants"][variant]
        require(gate["passed"] is True, f"{variant} decision gate failed")
        require(gate["manifest_gate"]["artifact_size_bytes"] == expected["size"],
                f"{variant} decision size drifted")
        require(gate["manifest_gate"]["artifact_sha256"] == expected["sha256"],
                f"{variant} decision hash drifted")
        manifest = json.loads((SUMMARY / f"{variant}_artifact_manifest.json").read_text())
        require(manifest["artifact_sha256"] == expected["sha256"],
                f"{variant} summary manifest hash drifted")
        require(manifest["artifact_size_bytes"] == expected["size"],
                f"{variant} summary manifest size drifted")
        feature_phrase = f"{expected['features']}-feature"
        require(feature_phrase in report and feature_phrase in cumulative,
                f"{variant} feature count drifted in report or summary")
        require(f"{expected['features']} features" in handoff,
                f"{variant} feature count drifted in handoff")
        require(
            f"| `{variant}` |" in readme
            and f"| {expected['features']} |" in readme,
            f"{variant} feature count drifted in README",
        )
        require(expected["sha256"] in report, f"{variant} hash absent from report")
        require(expected["sha256"] in cumulative, f"{variant} hash absent from summary")
        require(expected["sha256"] in handoff, f"{variant} hash absent from handoff")

    require(decision["forcing_bridge"]["drop32"]["passed"] is True,
            "drop32 forcing bridge failed")
    require(decision["forcing_bridge"]["drop21_corr080"]["passed"] is True,
            "drop21 forcing bridge failed")
    for relative in REQUIRED_REPO_PATHS:
        require((ROOT / relative).exists(), f"referenced repository path missing: {relative}")
    for name in (
        "drop32_artifact_manifest.json",
        "drop32_validation_report.json",
        "drop21_corr080_artifact_manifest.json",
        "drop21_corr080_validation_report.json",
        "iter012_forcing_bridge_validation.json",
        "iter012_release_decision.json",
    ):
        require((SUMMARY / name).is_file(), f"required release evidence missing: {name}")
    print("PASS: Iter012 four-record handoff and artifact validation")


if __name__ == "__main__":
    main()
