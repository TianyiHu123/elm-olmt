#!/usr/bin/env python3
"""Cross-validate Iter012 aggregate evidence and four durable closeout records."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ITER012_HANDOFF_VALIDATE_FAIL: {message}")


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--accounting", type=Path, required=True)
    args = parser.parse_args()
    with args.accounting.open(newline="", encoding="utf-8") as stream:
        accounting = list(csv.DictReader(stream))
    required_work_units = {
        *(f"legacy_production_{site}_{seed}" for site in ("abby", "jerc") for seed in (9009, 9010, 9011)),
        "v2_preflight",
        "v2_initialization_abby",
        "v2_initialization_jerc",
        "v2_pool_validation",
        *(f"v2_production_{site}_{seed}" for site in ("abby", "jerc") for seed in (9009, 9010, 9011)),
        "v2_evaluation_canonical_abby",
        "v2_evaluation_canonical_jerc",
        "v2_evaluation_legacy_abby",
        "v2_evaluation_legacy_jerc",
        "v2_aggregate",
    }
    allowed_v2_work_units = {
        work_unit for work_unit in required_work_units if work_unit.startswith("v2_")
    } | {"v2_handoff_validation"}
    terminal_states = {
        "COMPLETED",
        "FAILED",
        "TIMEOUT",
        "OUT_OF_MEMORY",
        "CANCELLED",
        "NODE_FAIL",
        "PREEMPTED",
    }
    require(accounting, "accounting ledger is empty")
    job_ids = [row.get("job_id") for row in accounting]
    require(
        all(job_ids) and len(job_ids) == len(set(job_ids)),
        "accounting job IDs are missing or duplicated",
    )
    require(
        all(row.get("state") in terminal_states for row in accounting),
        "accounting contains active, unknown, or malformed states",
    )
    v2_rows = [
        row for row in accounting if row.get("package_id") == "general_pipeline_v2"
    ]
    require(
        len(v2_rows) <= 31,
        "Package v2 exhausted the revised 32-task ceiling before handoff validation",
    )
    require(
        all(row.get("work_unit") in allowed_v2_work_units for row in v2_rows),
        "Package v2 accounting contains an unknown work unit",
    )
    preflight_attempts = [
        row for row in accounting if row.get("work_unit") == "v2_preflight"
    ]
    require(len(preflight_attempts) == 3, "preflight history must contain three attempts")
    historical_preflights = {
        row.get("job_id"): row for row in preflight_attempts if row.get("job_id")
    }
    for job_id in ("23574254", "23574301"):
        row = historical_preflights.get(job_id, {})
        require(
            row.get("state") == "OUT_OF_MEMORY"
            and row.get("exit_code") == "0:125"
            and row.get("classification") == "scheduler_resource"
            and row.get("run_dir", "").endswith(
                "spinup_forcing_coupling_iter012_general_pipeline_v2/preflight"
            ),
            f"historical preflight {job_id} evidence mismatch",
        )
    revised_preflights = [
        row
        for row in preflight_attempts
        if row.get("job_id") not in {"23574254", "23574301"}
    ]
    require(
        len(revised_preflights) == 1
        and revised_preflights[0].get("state") == "COMPLETED"
        and revised_preflights[0].get("exit_code") == "0:0"
        and revised_preflights[0].get("run_dir", "").endswith(
            "spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/preflight"
        ),
        "Revision1 preflight success evidence mismatch",
    )
    for work_unit in required_work_units:
        attempts = [row for row in accounting if row.get("work_unit") == work_unit]
        if work_unit.startswith("v2_"):
            require(
                all(
                    row.get("package_id") == "general_pipeline_v2"
                    for row in attempts
                ),
                f"{work_unit} has incorrect package ownership",
            )
            maximum_attempts = 3 if work_unit == "v2_preflight" else 2
            require(
                len(attempts) <= maximum_attempts,
                f"{work_unit} exceeds its approved attempt boundary",
            )
        else:
            require(
                all(row.get("package_id") == "legacy_v1" for row in attempts),
                f"{work_unit} has incorrect legacy package ownership",
            )
        for attempt in attempts:
            if attempt.get("state") != "COMPLETED" or attempt.get("exit_code") != "0:0":
                require(
                    bool(attempt.get("classification")),
                    f"{work_unit} has an unclassified unsuccessful attempt",
                )
                allowed_classifications = {"scheduler_resource"}
                if work_unit == "v2_preflight":
                    allowed_classifications.add("preflight_minimal_correction")
                require(
                    attempt.get("classification") in allowed_classifications,
                    f"{work_unit} has a non-retryable failure classification",
                )
    prior_handoff_attempts = [
        row for row in accounting if row.get("work_unit") == "v2_handoff_validation"
    ]
    require(
        len(prior_handoff_attempts) <= 1,
        "handoff validation exceeds its one-retry boundary",
    )
    for attempt in prior_handoff_attempts:
        require(
            attempt.get("package_id") == "general_pipeline_v2",
            "handoff validation has incorrect package ownership",
        )
        require(
            attempt.get("state")
            in {"TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "CANCELLED"}
            and attempt.get("classification") == "scheduler_resource"
            and attempt.get("exit_code") != "0:0",
            "handoff validation prior attempt is not a retryable scheduler/resource failure",
        )
    for work_unit in required_work_units:
        attempts = [row for row in accounting if row.get("work_unit") == work_unit]
        require(attempts, f"missing accounting for {work_unit}")
        require(
            any(
                row.get("state") == "COMPLETED" and row.get("exit_code") == "0:0"
                for row in attempts
            ),
            f"no successful terminal attempt for {work_unit}",
        )

    aggregate = json.loads(read(args.aggregate))
    require(
        aggregate.get("schema") == "spinup-forcing-coupling-iter012-aggregate-v2",
        "aggregate schema mismatch",
    )
    require(aggregate.get("status") == "pass", "aggregate status is not pass")
    canonical = aggregate.get("canonical_sites", [])
    legacy = aggregate.get("legacy_misconfigured_sampler_sites", [])
    require(len(canonical) == 2 and len(legacy) == 2, "aggregate site counts")
    require(all(row.get("move_matches_contract") for row in canonical), "canonical move gate")
    require(
        all(not row.get("move_matches_contract") for row in legacy),
        "legacy move-mismatch evidence",
    )
    labels = {row["site"]: row["label"] for row in canonical}
    require(set(labels) == {"ABBY", "JERC"}, "canonical site membership")
    decision = f"ABBY {labels['ABBY']}; JERC {labels['JERC']}"

    identity = {
        "Iteration ID": "iter012",
        "Status": "completed",
        "Work type": "implementation",
        "Objective": (
            "Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 "
            "and JERC hourly/0.75"
        ),
        "Bounded scope": (
            "Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical "
            "evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation"
        ),
        "Overall acceptance result": "pass",
        "Decision": decision,
    }
    closeout_identity = "; ".join(
        f"{field} `{value}`" for field, value in identity.items()
    )
    documents = {
        "iteration": read(COUPLING_ROOT / "iterations" / "iter012.md"),
        "handoff": read(COUPLING_ROOT / "handoff" / "CURRENT.md"),
        "summary": read(COUPLING_ROOT / "ITERATION_SUMMARY.md"),
        "report": read(
            COUPLING_ROOT / "summaries" / "iter012" / "ITER012_REPORT.md"
        ),
    }
    for label, document in documents.items():
        require(
            closeout_identity in " ".join(document.split()),
            f"{label} closeout identity mismatch",
        )

    with (COUPLING_ROOT / "registry.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    matches = [row for row in rows if row["iteration_id"] == "iter012"]
    require(len(matches) == 1, "registry must contain exactly one iter012 row")
    row = matches[0]
    expected_registry = {
        "iteration_id": "iter012",
        "status": "completed",
        "work_type": "implementation",
        "objective": identity["Objective"],
        "bounded_scope": identity["Bounded scope"],
        "acceptance_result": "pass",
        "decision": decision,
        "output_root": (
            "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
            "spinup_forcing_coupling/"
            "spinup_forcing_coupling_iter012_general_pipeline_v2/revision1"
        ),
        "summary_path": "development/spinup_forcing_coupling/summaries/iter012",
    }
    for field, value in expected_registry.items():
        require(row.get(field) == value, f"registry {field} mismatch")

    summary_root = COUPLING_ROOT / "summaries" / "iter012"
    for name in (
        "ITER012_REPORT.md",
        "aggregate_result.json",
        "abby_evaluation_result.json",
        "jerc_evaluation_result.json",
        "legacy_abby_evaluation_result.json",
        "legacy_jerc_evaluation_result.json",
        "accounting.csv",
    ):
        require((summary_root / name).is_file(), f"missing summary artifact {name}")
    print(
        "ITER012_HANDOFF_VALIDATE_PASS "
        f"abby={labels['ABBY']} jerc={labels['JERC']}"
    )


if __name__ == "__main__":
    main()
