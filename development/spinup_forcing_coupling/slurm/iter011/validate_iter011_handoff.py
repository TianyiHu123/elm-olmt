#!/usr/bin/env python3
"""Validate Iter011 durable closeout records against the completed aggregate package."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
COUPLING = REPO_ROOT / "development" / "spinup_forcing_coupling"
OUTPUT_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling"
)
RESULT = OUTPUT_ROOT / "spinup_forcing_coupling_iter011_aggregate" / "result"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER011_HANDOFF_VALIDATE_FAIL: {message}")


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-job-count", type=int, required=True)
    args = parser.parse_args()
    require(args.active_job_count == 0, "active Iter011 job count is not zero")

    identity = {
        "Iteration ID": "iter011",
        "Status": "completed",
        "Work type": "implementation",
        "Objective": "Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC",
        "Bounded scope": "ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains",
        "Overall acceptance result": "pass",
        "Decision": "ABBY preferred_configuration_supported daily_0.75; JERC inconclusive_metric_tradeoff with no selected configuration",
    }
    closeout_identity = "; ".join(f"{field} `{value}`" for field, value in identity.items())
    iteration = read(COUPLING / "iterations" / "iter011.md")
    handoff = read(COUPLING / "handoff" / "CURRENT.md")
    summary = read(COUPLING / "ITERATION_SUMMARY.md")
    for label, document in {
        "iteration": iteration,
        "handoff": handoff,
        "summary": summary,
    }.items():
        normalized = " ".join(document.split())
        require(closeout_identity in normalized, f"{label} closeout identity mismatch")

    with (COUPLING / "registry.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    matches = [item for item in rows if item["iteration_id"] == "iter011"]
    require(len(matches) == 1, "registry must contain exactly one iter011 row")
    row = matches[0]
    expected = {
        "iteration_id": identity["Iteration ID"],
        "status": "completed",
        "work_type": "implementation",
        "objective": identity["Objective"],
        "bounded_scope": identity["Bounded scope"],
        "acceptance_result": "pass",
        "decision": identity["Decision"],
        "output_root": str(OUTPUT_ROOT),
        "summary_path": "development/spinup_forcing_coupling/summaries/iter011",
    }
    for field, value in expected.items():
        require(row[field] == value, f"registry {field} mismatch")

    required_result_artifacts = (
        "aggregate_result.json",
        "cross_seed_wasserstein.csv",
        "leaf_metrics.csv",
    )
    required_summary_artifacts = (
        "abby_decision.json",
        "jerc_decision.json",
        "six_configuration_seed_metrics.csv",
        "six_configuration_site_table.csv",
        "ITER011_REPORT.md",
    )
    for name in required_result_artifacts:
        require((RESULT / name).is_file(), f"missing final artifact {name}")
    for name in required_summary_artifacts:
        require((COUPLING / "summaries" / "iter011" / name).is_file(), f"missing summary {name}")

    report = " ".join(read(COUPLING / "summaries" / "iter011" / "ITER011_REPORT.md").split())
    for field, value in identity.items():
        require(f"{field}: `{value}`" in report, f"report {field} mismatch")
    validation_record = " ".join(iteration.split())
    for required in (
        "slurm/iter011/validate_iter011_handoff.py",
        "--active-job-count 0",
        "ITER011_HANDOFF_VALIDATE_PASS leaves=36 decision=site_specific",
        "result `pass`",
    ):
        require(required in validation_record, f"iteration lacks validator evidence {required!r}")

    aggregate = json.loads(read(RESULT / "aggregate_result.json"))
    require(aggregate.get("schema") == "spinup-forcing-coupling-iter011-aggregate-v1", "aggregate schema")
    require(len(aggregate.get("leaves", [])) == 36, "aggregate leaf count")
    abby = json.loads(read(COUPLING / "summaries" / "iter011" / "abby_decision.json"))
    jerc = json.loads(read(COUPLING / "summaries" / "iter011" / "jerc_decision.json"))
    require(abby.get("decision") == "preferred_configuration_supported", "ABBY decision")
    require(abby.get("selected_configuration") == "daily_0.75", "ABBY selection")
    require(jerc.get("decision") == "inconclusive_metric_tradeoff", "JERC decision")
    require(jerc.get("selected_configuration") is None, "JERC must not have a selection")
    print("ITER011_HANDOFF_VALIDATE_PASS leaves=36 decision=site_specific")


if __name__ == "__main__":
    main()
