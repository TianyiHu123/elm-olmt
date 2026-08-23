#!/usr/bin/env python3
"""Cross-validate Iter016 four durable records and aggregate evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"
REQUIRED_WORK_UNITS = {
    "preflight",
    "pool_rebuild_abby",
    "pool_rebuild_jerc",
    "production_array_abby",
    "production_array_jerc",
    "analysis",
}
ALLOWED = REQUIRED_WORK_UNITS | {"handoff_validation"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER016_HANDOFF_VALIDATE_FAIL: {message}")


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

    report = read(COUPLING_ROOT / "iterations" / "iter016.md")
    summary = read(COUPLING_ROOT / "ITERATION_SUMMARY.md")
    handoff = read(COUPLING_ROOT / "handoff" / "CURRENT.md")
    registry_lines = read(COUPLING_ROOT / "registry.csv").splitlines()

    require(aggregate.get("status") == "pass", "aggregate status is not pass")
    require(int(aggregate.get("leaves", 0)) == 18, "aggregate leaf count")
    require(len(aggregate.get("sites", [])) == 2, "two site records required")
    require(accounting, "empty accounting")
    require(all(row.get("package_id") == "iter016" for row in accounting), "package_id mismatch")
    require(all(row.get("work_unit") in ALLOWED for row in accounting), "unknown work unit")
    completed = {
        row.get("work_unit")
        for row in accounting
        if row.get("state") == "COMPLETED" and row.get("work_unit") in REQUIRED_WORK_UNITS
    }
    require(REQUIRED_WORK_UNITS <= completed, "required work units missing from accounting")
    require(
        "iter016" in handoff
        and (
            "Active iteration: `iter016`" in handoff
            or "Last closed iteration: `iter016`" in handoff
        ),
        "handoff iteration mismatch",
    )
    require("iter016" in report.lower(), "iteration report missing iter016")
    require("## iter016" in summary.lower() or "iter016 -" in summary.lower(), "summary missing iter016")
    require(any(line.startswith("iter016,") for line in registry_lines), "registry missing iter016 row")

    summary_root = COUPLING_ROOT / "summaries" / "iter016"
    for name in ("aggregate_result.json", "ITER016_REPORT.md", "abby_equifinality_diagnosis.json"):
        require((summary_root / name).is_file(), f"missing summary artifact {name}")

    labels = " ".join(
        f"{row['site']}={row['diagnostic_label']}" for row in aggregate.get("sites", [])
    )
    print(f"ITER016_HANDOFF_VALIDATE_PASS leaves=18 {labels}")


if __name__ == "__main__":
    main()
