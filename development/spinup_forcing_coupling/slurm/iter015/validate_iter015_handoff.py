#!/usr/bin/env python3
"""Cross-validate Iter015 four durable records and aggregate evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"
SITES = ("ABBY", "JERC")
RESOLUTIONS = ("hourly", "daily")
SCALES = ("0.50", "0.75", "1.00")
SEEDS = ("9009", "9010", "9011")
REQUIRED_WORK_UNITS = {"preflight", "pool_rebuild_abby", "pool_rebuild_jerc", "analysis"} | {
    f"production_{site}_{resolution}_{scale}_{seed}"
    for site in ("abby", "jerc")
    for resolution in RESOLUTIONS
    for scale in SCALES
    for seed in SEEDS
}
ALLOWED_WORK_UNITS = REQUIRED_WORK_UNITS | {"handoff_validation"}
DECISIONS = {
    "preferred_configuration_supported",
    "default_configuration_retained",
    "inconclusive_metric_tradeoff",
    "inconclusive_no_unique_preference",
    "inconclusive_seed_instability",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER015_HANDOFF_VALIDATE_FAIL: {message}")


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--accounting", type=Path, required=True)
    args = parser.parse_args()

    aggregate = json.loads(read(args.aggregate))
    with args.accounting.open(newline="", encoding="utf-8") as handle:
        accounting = list(csv.DictReader(handle))

    report = read(COUPLING_ROOT / "iterations" / "iter015.md")
    summary = read(COUPLING_ROOT / "ITERATION_SUMMARY.md")
    handoff = read(COUPLING_ROOT / "handoff" / "CURRENT.md")
    registry_lines = read(COUPLING_ROOT / "registry.csv").splitlines()

    require(aggregate.get("status") == "pass", "aggregate status is not pass")
    require(int(aggregate.get("leaves", 0)) == 36, "aggregate leaf count")
    decisions = aggregate.get("decisions") or []
    require(len(decisions) == 2, "two site decisions required")
    require({row.get("site") for row in decisions} == set(SITES), "site set")
    for row in decisions:
        require(row.get("decision") in DECISIONS, f"{row.get('site')} decision invalid")
        require(bool(row.get("integrity_pass")), f"{row.get('site')} integrity")

    require(accounting, "empty accounting")
    require(len(accounting) <= 52, "scheduler-task ceiling exceeded")
    job_ids = [row.get("job_id") for row in accounting]
    require(all(job_ids) and len(job_ids) == len(set(job_ids)), "bad job IDs")
    require(all(row.get("package_id") == "iter015" for row in accounting), "package_id mismatch")
    require(
        all(row.get("work_unit") in ALLOWED_WORK_UNITS for row in accounting),
        "unknown accounting work unit",
    )
    completed = {
        row.get("work_unit")
        for row in accounting
        if row.get("state") == "COMPLETED" and row.get("work_unit") in REQUIRED_WORK_UNITS
    }
    require(REQUIRED_WORK_UNITS <= completed, "required work units missing from accounting")

    require("Active iteration: `iter015`" in handoff, "handoff active iteration mismatch")
    require("- Status: `completed`" in report or "Status: `completed`" in report, "report not completed")
    require("- Status: `completed`" in handoff or "Status: `completed`" in handoff, "handoff not completed")
    require("Phase: `closed`" in handoff, "handoff not closed")
    require("## iter015" in summary.lower() or "iter015 -" in summary.lower(), "summary missing iter015")
    require(any(line.startswith("iter015,") for line in registry_lines), "registry missing iter015 row")

    summary_root = COUPLING_ROOT / "summaries" / "iter015"
    for name in (
        "aggregate_result.json",
        "site_decisions.csv",
        "six_configuration_site_table.csv",
        "ITER015_REPORT.md",
    ):
        require((summary_root / name).is_file(), f"missing summary artifact {name}")

    labels = " ".join(f"{row['site']}={row['decision']}" for row in decisions)
    print(f"ITER015_HANDOFF_VALIDATE_PASS leaves=36 {labels}")


if __name__ == "__main__":
    main()
