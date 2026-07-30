#!/usr/bin/env python
"""Cross-validate the four durable Iter011 closeout records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
SPINUP_ROOT = REPO_ROOT / "development/spinup_surrogate"
REPORT = SPINUP_ROOT / "iterations/iter011.md"
SUMMARY = SPINUP_ROOT / "ITERATION_SUMMARY.md"
REGISTRY = SPINUP_ROOT / "registry.csv"
CURRENT = SPINUP_ROOT / "handoff/CURRENT.md"
SLURM_ROOT = SPINUP_ROOT / "slurm/iter011"
SUMMARY_ROOT = SPINUP_ROOT / "summaries/iter011"
OUTPUT_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output"
)
CONTROL = "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf"
CANDIDATE = "s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop"
HISTORICAL_BASELINE = "s32_tanh_lbfgs_a50_lr1e3_full45"
EXPECTED_SUMMARY_FILES = {
    "iter011_feature_importance_heatmap_top15.png",
    "iter011_feature_importance_rmse_top15.png",
    "iter011_paired_gate_analysis.json",
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop_"
        "r2_train_validation_hist.png"
    ),
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop_"
        "rmse_train_validation_hist.png"
    ),
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop_vs_"
        "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf_r2_validation_paired.png"
    ),
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop_vs_"
        "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf_rmse_validation_paired.png"
    ),
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf_"
        "r2_train_validation_hist.png"
    ),
    (
        "iter011_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf_"
        "rmse_train_validation_hist.png"
    ),
    f"{CANDIDATE}_feature_stability.json",
    f"{CANDIDATE}_importance_100seed.json",
    f"{CANDIDATE}_summary.json",
    f"{CONTROL}_feature_stability.json",
    f"{CONTROL}_importance_100seed.json",
    f"{CONTROL}_summary.json",
}
EXPECTED_SLURM_FILES = {
    "aggregate_iter011.slurm",
    "analyze_iter011_paired.py",
    "case.train_surrogate_spinup_iter011.slurm",
    "iter011_source_manifest.sha256",
    "iter011_variants.tsv",
    "materialize_iter011_variants.sh",
    "validate_iter011.py",
    "validate_iter011.slurm",
    "validate_iter011_results.py",
    "validate_iter011_handoff.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing record: {path}")
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    require(match is not None, f"missing section: {heading}")
    return match.group("body").strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats_seeds(variant: str) -> list[int]:
    stats_dir = (
        OUTPUT_ROOT
        / f"spinup_surrogate_iter011_{variant}"
        / "surrogate_spinup"
    )
    paths = sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json"))
    seeds = []
    for path in paths:
        match = re.fullmatch(r"surrogate_spinup_stats_seed(\d+)\.json", path.name)
        require(match is not None, f"unexpected stats filename: {path}")
        seeds.append(int(match.group(1)))
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-iteration-job-count", type=int, required=True)
    args = parser.parse_args()
    require(
        args.active_iteration_job_count == 0,
        "completed Iter011 cannot have active jobs",
    )

    report = read(REPORT)
    summary = read(SUMMARY)
    registry_text = read(REGISTRY)
    current = read(CURRENT)
    records = {
        "report": report,
        "summary": summary,
        "current": current,
    }

    require("# iter011" in report, "report iteration ID mismatch")
    require("- Status: `completed`" in report, "report status mismatch")
    require("Iteration Summary: iter001-iter011" in summary, "summary latest ID mismatch")
    require("Current Handoff (Iter011 closed)" in current, "current latest ID mismatch")
    require("- Status: `completed`" in current, "current status mismatch")
    require("- Phase: `closed`" in current, "current phase mismatch")
    require("- Active job IDs: none." in current, "current active-job claim mismatch")

    for name, text in records.items():
        require(CONTROL in text, f"{name} missing control")
        require(CANDIDATE in text, f"{name} missing candidate")
        require(HISTORICAL_BASELINE in text, f"{name} missing historical baseline")
        require("10001-10100" in text, f"{name} missing seed range")
        require("summaries/iter011" in text, f"{name} missing summary path")
        require("0.827271" in text, f"{name} missing control TOTSOMC median R2")
        require("0.827497" in text, f"{name} missing control TOTSOMN median R2")
        require("0.801217" in text, f"{name} missing candidate TOTSOMC median R2")
        require("0.801178" in text, f"{name} missing candidate TOTSOMN median R2")
        require("0.25 / 0.24" in text, f"{name} missing control warnings")
        require("0.22 / 0.23" in text, f"{name} missing candidate warnings")

    require(
        "sequential drop32 correlation filtering" in summary.lower(),
        "summary objective mismatch",
    )
    require(
        "reject the correlation-0.80 candidate" in summary,
        "summary conclusion mismatch",
    )
    require(
        "No Iter011 candidate is promoted" in current,
        "current no-promotion conclusion mismatch",
    )
    require(
        "Promotion decision: no Iter011 candidate promotion" in report,
        "report no-promotion conclusion mismatch",
    )

    report_plan = section(report, "Proposed Next-Iteration Plan (Planning Only)")
    current_plan = section(current, "Next Iteration Plan (Planning Only)")
    require(report_plan == current_plan, "report/current next-iteration plans differ")
    for token in (
        "`iter012`",
        "`0.90` and `0.95`",
        "exactly 300 seed JSONs",
        "fresh runtime contract",
        "planning-only",
    ):
        require(token in report_plan, f"next plan missing: {token}")

    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    iter011_rows = [row for row in rows if row["iter_id"] == "iter011"]
    require(len(iter011_rows) == 1, "registry must contain exactly one iter011 row")
    row = iter011_rows[0]
    require(row["status"] == "completed", "registry status mismatch")
    require(
        row["objective"] == "Sequential DROP32 correlation filtering",
        "registry objective mismatch",
    )
    require(row["seed_range"] == "10001-10100", "registry seed range mismatch")
    require(row["variants"].split("|") == [CONTROL, CANDIDATE], "registry variants mismatch")
    require(row["best_variant"] == CONTROL, "registry prospective selection mismatch")
    require(row["best_r2_val_totsomc_median"] == "0.827271", "registry C R2 mismatch")
    require(row["best_r2_val_totsomn_median"] == "0.827497", "registry N R2 mismatch")
    require(
        row["summary_root"] == "development/spinup_surrogate/summaries/iter011",
        "registry summary path mismatch",
    )
    require("No promotion" in row["notes"], "registry conclusion mismatch")
    require("iter009 alpha-50 full45" in row["notes"], "registry baseline mismatch")

    actual_summary_files = {
        path.name for path in SUMMARY_ROOT.iterdir() if path.is_file()
    }
    require(
        actual_summary_files == EXPECTED_SUMMARY_FILES,
        "summary artifact set mismatch: "
        f"missing={sorted(EXPECTED_SUMMARY_FILES - actual_summary_files)} "
        f"extra={sorted(actual_summary_files - EXPECTED_SUMMARY_FILES)}",
    )
    for name in EXPECTED_SUMMARY_FILES:
        require((SUMMARY_ROOT / name).stat().st_size > 0, f"empty summary artifact: {name}")

    actual_slurm_files = {path.name for path in SLURM_ROOT.iterdir() if path.is_file()}
    require(
        actual_slurm_files == EXPECTED_SLURM_FILES,
        "Iter011 Slurm/control artifact set mismatch",
    )
    require(stats_seeds(CONTROL) == list(range(10001, 10101)), "control seed set mismatch")
    require(
        stats_seeds(CANDIDATE) == list(range(10001, 10101)),
        "candidate seed set mismatch",
    )

    paired = json.loads(
        (SUMMARY_ROOT / "iter011_paired_gate_analysis.json").read_text(encoding="utf-8")
    )
    require(paired["seed_count"] == 100, "paired seed count mismatch")
    require(
        paired["control"] == CONTROL and paired["candidate"] == CANDIDATE,
        "paired variant identity mismatch",
    )
    require(
        paired["candidate_schema"]["feature_count"] == 21,
        "paired schema count mismatch",
    )
    require(
        paired["candidate_schema"]["stable_across_seeds"] is True,
        "paired schema stability mismatch",
    )
    require(
        paired["decision"]["candidate_full_gate_pass"] is False,
        "paired gate decision mismatch",
    )
    require(
        paired["decision"]["prospective_selection"] == CONTROL,
        "paired prospective selection mismatch",
    )
    require(
        paired["decision"]["historical_retained_baseline_unchanged"]
        == HISTORICAL_BASELINE,
        "paired historical baseline mismatch",
    )

    submitted_aggregate = (
        OUTPUT_ROOT
        / "spinup_surrogate_iter011_aggregate"
        / "aggregate_iter011.slurm"
    )
    require(submitted_aggregate.is_file(), "missing submitted aggregate script")
    require(
        sha256(submitted_aggregate) == sha256(SLURM_ROOT / "aggregate_iter011.slurm"),
        "aggregate submitted copy differs from canonical",
    )

    require(
        "Ready/Blocked Status for Current Iteration" not in current,
        "current contains stale ready/blocked section",
    )
    require("Status: `in_progress`" not in current, "current has stale status")
    require("Phase: `production" not in current, "current has stale phase")
    require("pending aggregation" not in current, "current has stale aggregation text")
    require(
        "Latest Iteration Reference" in current and "iter011.md" in current,
        "current latest reference mismatch",
    )

    print(
        "Iter011 four-record handoff validation passed: "
        "report, cumulative summary, registry, and CURRENT agree; "
        "200 exact leaves, 15 summary artifacts, no active jobs, "
        "candidate rejected, historical Iter009 baseline retained, "
        "and the planning-only Iter012 plan matches verbatim."
    )


if __name__ == "__main__":
    main()
