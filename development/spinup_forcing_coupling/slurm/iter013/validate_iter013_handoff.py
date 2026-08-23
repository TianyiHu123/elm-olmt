#!/usr/bin/env python3
"""Cross-validate Iter013 four durable records and aggregate evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER013_HANDOFF_VALIDATE_FAIL: {message}")


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

    report = read(COUPLING_ROOT / "iterations" / "iter013.md")
    summary = read(COUPLING_ROOT / "ITERATION_SUMMARY.md")
    handoff = read(COUPLING_ROOT / "handoff" / "CURRENT.md")
    registry_lines = read(COUPLING_ROOT / "registry.csv").splitlines()

    require(aggregate.get("status") == "pass", "aggregate status is not pass")
    require("ABBY" in aggregate.get("sites", {}), "missing ABBY aggregate site")
    require("JERC" in aggregate.get("sites", {}), "missing JERC aggregate site")
    abby = aggregate["sites"]["ABBY"]
    jerc = aggregate["sites"]["JERC"]
    decision = str(aggregate.get("decision", ""))
    require(abby["geometry_class"] in decision, "ABBY geometry absent from decision")
    require(jerc["geometry_class"] in decision, "JERC geometry absent from decision")
    require(abby["selection_class"] in decision, "ABBY selection absent from decision")
    require(jerc["selection_class"] in decision, "JERC selection absent from decision")

    required_units = {"preflight", "analysis_abby", "analysis_jerc", "aggregate"}
    allow = required_units | {"handoff_validation"}
    require(accounting, "empty accounting")
    require(len(accounting) <= 8, "scheduler-task ceiling exceeded")
    job_ids = [row.get("job_id") for row in accounting]
    require(all(job_ids) and len(job_ids) == len(set(job_ids)), "bad job IDs")
    require(
        all(row.get("work_unit") in allow for row in accounting),
        "unknown accounting work unit",
    )
    for unit in required_units:
        rows = [row for row in accounting if row.get("work_unit") == unit]
        require(rows, f"missing accounting row for {unit}")
        require(
            any(row.get("state") == "COMPLETED" and row.get("exit_code") == "0:0" for row in rows),
            f"{unit} not COMPLETED 0:0",
        )

    require("- Status: `completed`" in report or "Status: `completed`" in report, "report not completed")
    require("Active iteration: `iter013`" in handoff, "handoff active iteration mismatch")
    require("- Status: `completed`" in handoff or "Status: `completed`" in handoff, "handoff not completed")
    require("## iter013" in summary or "## Iter013" in summary or "iter013 -" in summary.lower(), "summary missing iter013")
    require(any(line.startswith("iter013,") for line in registry_lines), "registry missing iter013 row")
    require("Phase: `closed`" in handoff or "- Phase: `closed`" in handoff, "handoff not closed")

    print(
        "ITER013_HANDOFF_VALIDATE_PASS "
        f"abby={abby['geometry_class']}/{abby['selection_class']} "
        f"jerc={jerc['geometry_class']}/{jerc['selection_class']}"
    )


if __name__ == "__main__":
    main()
