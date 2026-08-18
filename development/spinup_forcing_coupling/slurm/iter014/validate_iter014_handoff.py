#!/usr/bin/env python3
"""Cross-validate Iter014 four durable records and aggregate evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"

REQUIRED_WORK_UNITS = {
    "preflight",
    "pool_rebuild_hybrid_high_l_maximin",
    "production_hybrid_high_l_maximin_9009",
    "production_hybrid_high_l_maximin_9010",
    "production_hybrid_high_l_maximin_9011",
    "evaluate",
    "aggregate",
}
OPTIONAL_WORK_UNITS = {
    "pool_rebuild_rank_dominated",
    "production_rank_dominated_9009",
    "production_rank_dominated_9010",
    "production_rank_dominated_9011",
}
ALLOWED_WORK_UNITS = REQUIRED_WORK_UNITS | OPTIONAL_WORK_UNITS | {"handoff_validation"}
DECISIONS = {
    "repair_supported",
    "partial_repair",
    "not_supported",
    "geometry_gate_failed",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER014_HANDOFF_VALIDATE_FAIL: {message}")


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

    report = read(COUPLING_ROOT / "iterations" / "iter014.md")
    summary = read(COUPLING_ROOT / "ITERATION_SUMMARY.md")
    handoff = read(COUPLING_ROOT / "handoff" / "CURRENT.md")
    registry_lines = read(COUPLING_ROOT / "registry.csv").splitlines()

    require(aggregate.get("status") == "pass", "aggregate status is not pass")
    require(aggregate.get("site") == "JERC", "aggregate site mismatch")
    overall = str(aggregate.get("overall_decision", ""))
    require(overall in DECISIONS, "overall decision missing/invalid")
    variants = aggregate.get("variants", {})
    require(set(variants) == {"rank_dominated", "hybrid_high_l_maximin"}, "variant set")
    for rule, payload in variants.items():
        require(payload.get("decision") in DECISIONS, f"{rule} decision invalid")
        require(payload.get("site") == "JERC", f"{rule} site")

    require(accounting, "empty accounting")
    require(len(accounting) <= 18, "scheduler-task ceiling exceeded")
    job_ids = [row.get("job_id") for row in accounting]
    require(all(job_ids) and len(job_ids) == len(set(job_ids)), "bad job IDs")
    require(
        all(row.get("work_unit") in ALLOWED_WORK_UNITS for row in accounting),
        "unknown accounting work unit",
    )
    require(
        all(row.get("package_id") == "iter014" for row in accounting),
        "package_id mismatch",
    )
    for unit in REQUIRED_WORK_UNITS:
        rows = [row for row in accounting if row.get("work_unit") == unit]
        require(rows, f"missing accounting row for {unit}")
        require(
            any(
                row.get("state") == "COMPLETED" and row.get("exit_code") == "0:0"
                for row in rows
            ),
            f"{unit} not COMPLETED 0:0",
        )

    require(
        "- Status: `completed`" in report or "Status: `completed`" in report,
        "report not completed",
    )
    require("Active iteration: `iter014`" in handoff, "handoff active iteration mismatch")
    require(
        "- Status: `completed`" in handoff or "Status: `completed`" in handoff,
        "handoff not completed",
    )
    require(
        "## iter014" in summary or "## Iter014" in summary or "iter014 -" in summary.lower(),
        "summary missing iter014",
    )
    require(any(line.startswith("iter014,") for line in registry_lines), "registry missing iter014 row")
    require("Phase: `closed`" in handoff or "- Phase: `closed`" in handoff, "handoff not closed")
    require(overall in report, "overall decision absent from iteration report")
    require(overall in handoff, "overall decision absent from handoff")

    identity = {
        "Iteration ID": "iter014",
        "Status": "completed",
        "Work type": "implementation",
        "Overall acceptance result": "pass",
        "Decision": overall,
    }
    closeout_identity = "; ".join(f"{field} `{value}`" for field, value in identity.items())
    compact_report = " ".join(report.split())
    compact_handoff = " ".join(handoff.split())
    require(closeout_identity in compact_report, "iteration closeout identity mismatch")
    require(closeout_identity in compact_handoff, "handoff closeout identity mismatch")

    summary_root = COUPLING_ROOT / "summaries" / "iter014"
    for name in (
        "aggregate_result.json",
        "variant_table.csv",
        "rank_dominated_evaluation_result.json",
        "hybrid_high_l_maximin_evaluation_result.json",
    ):
        require((summary_root / name).is_file(), f"missing summary artifact {name}")

    print(
        "ITER014_HANDOFF_VALIDATE_PASS "
        f"overall={overall} "
        f"rank_dominated={variants['rank_dominated']['decision']} "
        f"hybrid_high_l_maximin={variants['hybrid_high_l_maximin']['decision']}"
    )


if __name__ == "__main__":
    main()
