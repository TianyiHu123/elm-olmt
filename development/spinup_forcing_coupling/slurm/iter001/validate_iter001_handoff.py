#!/usr/bin/env python3
"""Cross-validate Iter001 closeout records and non-circular commit identity."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"
REPORT = COUPLING_ROOT / "iterations" / "iter001.md"
CUMULATIVE = COUPLING_ROOT / "ITERATION_SUMMARY.md"
REGISTRY = COUPLING_ROOT / "registry.csv"
CURRENT = COUPLING_ROOT / "handoff" / "CURRENT.md"
SUMMARY_ROOT = COUPLING_ROOT / "summaries" / "iter001"
DECISION_PATH = SUMMARY_ROOT / "iter001_decision.json"
ACCOUNTING_PATH = SUMMARY_ROOT / "iter001_accounting.csv"
BASELINE_STATS = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
    "spinup_forcing_coupling/spinup_forcing_coupling_iter001_baseline/"
    "surrogate_forcing"
)
AGGREGATE_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
    "spinup_forcing_coupling/spinup_forcing_coupling_iter001_aggregate"
)
OUTPUT_ROOT = (
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
    "spinup_forcing_coupling"
)
SUMMARY_PATH = "development/spinup_forcing_coupling/summaries/iter001"
OBJECTIVE = "Historical nine-site SR forcing-surrogate offline baseline"
BOUNDED_SCOPE = (
    "Nine sites; SR; random_time_window; seeds 10001-10100; pooled/per-site metrics; "
    "eight-repeat pooled permutation importance; no coupling or saved-artifact inference"
)
ACCEPTANCE_RESULT = "pass"
DECISION = (
    "Technical offline baseline validated; predictive quality characterized; "
    "coupling readiness not established"
)
SOURCE_SHA = "1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6"
DEPENDENCY_SHA = "e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9"
PRODUCTION_CONFIG_SHA = (
    "ef9b837bcdeb85ea96438ac6e9321a37623aa13ac9156d9ed96d5c942c104246"
)
REPOSITORY_COMMIT = "2648998d4ceb08ecf72859a7d5200c0e3a5eb41d"
CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]
REGISTRY_FIELDS = [
    "iteration_id",
    "closed_at",
    "status",
    "work_type",
    "objective",
    "bounded_scope",
    "acceptance_result",
    "decision",
    "upstream_dependencies",
    "output_root",
    "summary_path",
    "closeout_mode",
    "closeout_identity",
    "notes",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing required record: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_sha256(values: Iterable[str]) -> str:
    payload = json.dumps(sorted(values), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def schema_sha256(names: list[str]) -> str:
    payload = json.dumps(names, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def finite_number(value: Any, label: str) -> float:
    require(
        not isinstance(value, bool) and isinstance(value, (int, float)),
        f"{label} must be numeric",
    )
    result = float(value)
    require(math.isfinite(result), f"{label} must be finite")
    return result


def validate_diagnostics(value: dict[str, Any], label: str) -> None:
    for population in ("train", "test"):
        metrics = value[population]
        finite_number(metrics["r2"], f"{label}.{population}.r2")
        finite_number(metrics["rmse"], f"{label}.{population}.rmse")
        require(int(metrics["n_rows"]) > 0, f"{label}.{population}.n_rows must be positive")
    finite_number(value["r2_gap"], f"{label}.r2_gap")
    finite_number(value["rmse_ratio"], f"{label}.rmse_ratio")
    require(
        isinstance(value["overfitting_warning"], bool),
        f"{label}.overfitting_warning must be boolean",
    )


def git(*args: str) -> str:
    # Preserve leading spaces in porcelain status lines; only trim the trailing newline.
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.rstrip("\n")


def validate_production_records() -> None:
    paths = sorted(BASELINE_STATS.glob("surrogate_forcing_stats_seed*_rs*.json"))
    require(len(paths) == 100, f"expected 100 production records, found {len(paths)}")
    seeds: list[int] = []
    reference_schema: list[str] | None = None
    for path in paths:
        match = re.fullmatch(
            r"surrogate_forcing_stats_seed(?P<seed>\d+)_rs(?P=seed)\.json",
            path.name,
        )
        require(match is not None, f"unexpected production filename: {path.name}")
        payload = read_json(path)
        seed = int(match.group("seed"))
        require(payload["split_random_state"] == seed, f"seed mismatch: {path.name}")
        require(payload["schema"] == "olmt-forcing-surrogate-stats-v2", "schema drift")
        require(payload["split_mode"] == "random_time_window", f"seed {seed} split drift")
        require(payload["train_fraction"] == 0.8, f"seed {seed} train fraction drift")
        require(
            payload["output_label"] == "spinup_forcing_coupling_iter001_baseline",
            f"seed {seed} output label drift",
        )
        require(payload["case_names"] == CASES, f"seed {seed} case order drift")
        require(payload["outvars"] == ["SR"], f"seed {seed} target drift")
        provenance = payload["provenance"]
        require(provenance["source_manifest_sha256"] == SOURCE_SHA, "source drift")
        require(provenance["dependency_manifest_sha256"] == DEPENDENCY_SHA, "dependency drift")
        require(
            provenance["submission_config_sha256"] == PRODUCTION_CONFIG_SHA,
            "production config drift",
        )
        require(
            provenance["repository_commit"] == REPOSITORY_COMMIT,
            f"seed {seed} repository commit drift",
        )
        ordered = [str(name) for name in payload["ordered_feature_names"]]
        require(ordered and len(ordered) == len(set(ordered)), f"seed {seed} schema invalid")
        require(
            payload["ordered_feature_schema_sha256"] == schema_sha256(ordered),
            f"seed {seed} schema hash drift",
        )
        if reference_schema is None:
            reference_schema = ordered
        else:
            require(ordered == reference_schema, f"seed {seed} ordered schema drift")

        stats = payload["by_variable"]["SR"]
        validate_diagnostics(stats["pooled"], f"seed{seed}.pooled")
        require(list(stats["by_site"]) == CASES, f"seed {seed} site order drift")
        for case in CASES:
            validate_diagnostics(stats["by_site"][case], f"seed{seed}.{case}")
        importance = stats["permutation_importance"]
        require(importance["n_repeats"] == 8, f"seed {seed} repeat count drift")
        require(importance["random_state"] == seed, f"seed {seed} importance seed drift")
        features = importance["features"]
        require(importance["feature_count"] == len(ordered), f"seed {seed} feature count drift")
        require(
            [str(row["feature"]) for row in features] == ordered,
            f"seed {seed} importance schema drift",
        )
        for row in features:
            for metric in ("test_r2_decrease", "test_rmse_increase"):
                values = row[metric]
                require(len(values) == 8, f"seed {seed} {row['feature']} {metric} count drift")
                for index, value in enumerate(values):
                    finite_number(value, f"seed{seed}.{row['feature']}.{metric}[{index}]")
            finite_number(
                row["test_r2_decrease_mean"],
                f"seed{seed}.{row['feature']}.test_r2_decrease_mean",
            )
            finite_number(
                row["test_rmse_increase_mean"],
                f"seed{seed}.{row['feature']}.test_rmse_increase_mean",
            )
        seeds.append(seed)
    require(seeds == list(range(10001, 10101)), "production seed set drift")


def validate_records(decision: dict[str, Any]) -> dict[str, str]:
    report = read_text(REPORT)
    cumulative = read_text(CUMULATIVE)
    current = read_text(CURRENT)
    require("- Iteration ID: `iter001`" in report, "report iteration ID drift")
    require("- Work type: `implementation`" in report, "report work type drift")
    require("- Status: `completed`" in report, "report status drift")
    require("- Phase: `closed`" in report, "report phase drift")
    require("- Active iteration: `iter001`" in current, "handoff iteration ID drift")
    require("- Status: `completed`" in current, "handoff status drift")
    require("- Phase: `closed`" in current, "handoff phase drift")
    require("- Active job IDs: none" in current, "handoff retains an active job")
    require("## iter001" in cumulative, "cumulative summary lacks Iter001")

    common_values = (
        OBJECTIVE,
        BOUNDED_SCOPE,
        ACCEPTANCE_RESULT,
        DECISION,
        OUTPUT_ROOT,
        SUMMARY_PATH,
        SOURCE_SHA,
        DEPENDENCY_SHA,
        PRODUCTION_CONFIG_SHA,
    )
    for label, text in (
        ("report", report),
        ("cumulative summary", cumulative),
        ("handoff", current),
    ):
        for value in common_values:
            require(value in text, f"{label} lacks consistent value: {value}")
        require("No next iteration is proposed" in text, f"{label} next-state drift")

    with REGISTRY.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == REGISTRY_FIELDS, "registry schema drift")
        rows = list(reader)
    matches = [row for row in rows if row["iteration_id"] == "iter001"]
    require(len(matches) == 1, "registry must contain exactly one Iter001 row")
    row = matches[0]
    expected = {
        "status": "completed",
        "work_type": "implementation",
        "objective": OBJECTIVE,
        "bounded_scope": BOUNDED_SCOPE,
        "acceptance_result": ACCEPTANCE_RESULT,
        "decision": DECISION,
        "output_root": OUTPUT_ROOT,
        "summary_path": SUMMARY_PATH,
        "closeout_mode": "committed",
    }
    for key, value in expected.items():
        require(row[key] == value, f"registry {key} drift")
    for value in (SOURCE_SHA, DEPENDENCY_SHA, PRODUCTION_CONFIG_SHA):
        require(value in row["upstream_dependencies"], "registry dependency identity drift")
    require(row["closed_at"], "registry close time is empty")

    controlled_paths = decision["controlled_paths"]
    require(
        controlled_paths == sorted(set(controlled_paths)),
        "decision controlled paths must be sorted and unique",
    )
    controlled_hash = list_sha256(controlled_paths)
    require(
        decision["controlled_paths_manifest_sha256"] == controlled_hash,
        "decision controlled-path manifest hash drift",
    )
    require(controlled_hash in row["closeout_identity"], "registry closeout identity drift")
    return row


def validate_summary_evidence(decision: dict[str, Any]) -> None:
    expected = {
        "schema": "spinup-forcing-coupling-iter001-decision-v1",
        "iteration_id": "iter001",
        "status": "completed",
        "work_type": "implementation",
        "objective": OBJECTIVE,
        "bounded_scope": BOUNDED_SCOPE,
        "acceptance_result": ACCEPTANCE_RESULT,
        "decision": DECISION,
        "eligible_seed_count": 100,
        "source_manifest_sha256": SOURCE_SHA,
        "dependency_manifest_sha256": DEPENDENCY_SHA,
        "production_config_sha256": PRODUCTION_CONFIG_SHA,
        "output_root": OUTPUT_ROOT,
        "summary_path": SUMMARY_PATH,
    }
    for key, value in expected.items():
        require(decision.get(key) == value, f"decision evidence {key} drift")
    require(ACCOUNTING_PATH.is_file(), "compact accounting evidence is missing")
    with ACCOUNTING_PATH.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 100, "compact accounting must contain 100 replacement leaves")
    require(
        [int(row["array_task_id"]) for row in rows] == list(range(1, 101)),
        "compact accounting array-task set drift",
    )
    require(
        all(row["state"] == "COMPLETED" and row["exit_code"] == "0:0" for row in rows),
        "compact accounting contains an ineligible replacement leaf",
    )

    aggregate = AGGREGATE_ROOT / "iter001_aggregate.json"
    aggregate_validation = AGGREGATE_ROOT / "iter001_aggregate_validation.json"
    require(sha256(aggregate) == decision["aggregate_sha256"], "aggregate hash drift")
    require(
        sha256(aggregate_validation) == decision["aggregate_validation_sha256"],
        "aggregate-validation hash drift",
    )
    validation = read_json(aggregate_validation)
    require(validation["gate"] == "pass", "aggregate validation did not pass")


def validate_git_identity(
    *,
    phase: str,
    expected_parent: str,
    expected_subject: str,
    controlled_paths: list[str],
) -> None:
    require(git("rev-parse", "HEAD") == expected_parent or phase == "postcommit", "parent HEAD drift")
    if phase == "precommit":
        changed = set(git("status", "--porcelain=v1", "--untracked-files=all").splitlines())
        changed_paths = sorted(line[3:] for line in changed if line)
        require(changed_paths == controlled_paths, "precommit controlled path set drift")
        return
    require(git("rev-parse", "HEAD^") == expected_parent, "observed commit parent drift")
    require(git("log", "-1", "--pretty=%s") == expected_subject, "observed subject drift")
    committed = sorted(
        line for line in git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines()
        if line
    )
    require(committed == controlled_paths, "observed commit controlled path set drift")
    dirty = git("status", "--porcelain=v1", "--", *controlled_paths)
    require(not dirty, "controlled paths are dirty after commit")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-iteration-job-count", type=int, required=True)
    parser.add_argument("--phase", choices=("precommit", "postcommit"), required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-subject", required=True)
    args = parser.parse_args()
    require(args.active_iteration_job_count == 0, "active Iter001 jobs remain")
    decision = read_json(DECISION_PATH)
    validate_records(decision)
    validate_summary_evidence(decision)
    validate_production_records()
    validate_git_identity(
        phase=args.phase,
        expected_parent=args.expected_parent,
        expected_subject=args.expected_subject,
        controlled_paths=decision["controlled_paths"],
    )
    print(
        "PASS: Iter001 records, artifacts, accounting, and "
        f"{args.phase} closeout identity validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
