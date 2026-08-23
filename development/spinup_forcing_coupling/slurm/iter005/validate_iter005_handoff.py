#!/usr/bin/env python3
"""Cross-validate Iter005 closeout records and non-circular commit identity."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING_ROOT = REPO_ROOT / "development" / "spinup_forcing_coupling"
REPORT = COUPLING_ROOT / "iterations" / "iter005.md"
CUMULATIVE = COUPLING_ROOT / "ITERATION_SUMMARY.md"
REGISTRY = COUPLING_ROOT / "registry.csv"
CURRENT = COUPLING_ROOT / "handoff" / "CURRENT.md"
SUMMARY_ROOT = COUPLING_ROOT / "summaries" / "iter005"
DECISION_PATH = SUMMARY_ROOT / "iter005_decision.json"
ACCOUNTING_PATH = SUMMARY_ROOT / "iter005_accounting.csv"
SITE_MEDIANS_PATH = SUMMARY_ROOT / "iter005_site_metric_medians.csv"
OUTPUT_ROOT = (
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
    "spinup_forcing_coupling"
)
SUMMARY_PATH = "development/spinup_forcing_coupling/summaries/iter005"
OBJECTIVE = "Mean-spinup offline forcing baseline versus Iter004 arms"
BOUNDED_SCOPE = (
    "Nine sites; mean-spinup offline 9×100 timeseries ON; overlay Iter004 "
    "three arms; two annotated plot types; joined medians CSV; no skill floor"
)
ACCEPTANCE_RESULT = "pass"
DECISION = (
    "Mean-spinup offline baseline compared with Iter004 arms under locked "
    "plot/summary contract; predictive scores characterized; production MCMC "
    "readiness not established"
)
FORCING_SHA = "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
REPOSITORY_PARENT = "9a125ef3a703e1169e831f77a04636c344359024"
EXPECTED_SUBJECT = "Close Iter005 mean-spinup offline baseline comparison"
NEXT_PLAN_MARKER = "Proposed iteration: `iter006`"
NEXT_PLAN_DETAIL_MARKERS = (
    "predict_coupled_sr",
    "MCMC",
    "without a PPE campaign",
    "optimize_surrogate_forcing.py",
)
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


def list_sha256(values: Iterable[str]) -> str:
    payload = json.dumps(sorted(values), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.rstrip("\n")


def validate_records(decision: dict[str, Any]) -> dict[str, str]:
    report = read_text(REPORT)
    cumulative = read_text(CUMULATIVE)
    current = read_text(CURRENT)
    require("- Iteration ID: `iter005`" in report, "report iteration ID drift")
    require("- Work type: `implementation`" in report, "report work type drift")
    require("- Status: `completed`" in report, "report status drift")
    require("- Phase: `closed`" in report, "report phase drift")
    require("- Active iteration: `iter005`" in current, "handoff iteration ID drift")
    require("- Status: `completed`" in current, "handoff status drift")
    require("- Phase: `closed`" in current, "handoff phase drift")
    require("- Active job IDs: none" in current, "handoff retains an active job")
    require("## iter005" in cumulative, "cumulative summary lacks Iter005")

    common_values = (
        OBJECTIVE,
        BOUNDED_SCOPE,
        ACCEPTANCE_RESULT,
        DECISION,
        OUTPUT_ROOT,
        SUMMARY_PATH,
        FORCING_SHA,
    )
    for label, text in (
        ("report", report),
        ("cumulative summary", cumulative),
        ("handoff", current),
    ):
        for value in common_values:
            require(value in text, f"{label} lacks consistent value: {value}")
        require(NEXT_PLAN_MARKER in text, f"{label} next-plan marker drift")
    for marker in NEXT_PLAN_DETAIL_MARKERS:
        require(marker in report, f"report next-plan detail drift: {marker}")
        require(marker in current, f"handoff next-plan detail drift: {marker}")

    with REGISTRY.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == REGISTRY_FIELDS, "registry schema drift")
        rows = list(reader)
    matches = [row for row in rows if row["iteration_id"] == "iter005"]
    require(len(matches) == 1, "registry must contain exactly one Iter005 row")
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
    require(FORCING_SHA in row["upstream_dependencies"], "registry dependency identity drift")
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


def validate_artifacts(decision: dict[str, Any]) -> None:
    require(ACCOUNTING_PATH.is_file(), "compact accounting evidence is missing")
    require(SITE_MEDIANS_PATH.is_file(), "site-median summary is missing")
    expected = {
        "schema": "spinup-forcing-coupling-iter005-decision-v1",
        "iteration_id": "iter005",
        "status": "completed",
        "work_type": "implementation",
        "objective": OBJECTIVE,
        "bounded_scope": BOUNDED_SCOPE,
        "acceptance_result": ACCEPTANCE_RESULT,
        "decision": DECISION,
        "forcing_artifact_sha256": FORCING_SHA,
        "output_root": OUTPUT_ROOT,
        "summary_path": SUMMARY_PATH,
        "authoritative_preflight_job": "23516340",
        "full_array_job": "23516376",
        "authoritative_validate_job": "23516504",
        "closed_at": "2026-08-06T19:42:02-0700",
    }
    for key, value in expected.items():
        require(decision.get(key) == value, f"decision evidence {key} drift")


def validate_git_identity(
    *,
    phase: str,
    expected_parent: str,
    expected_subject: str,
    controlled_paths: list[str],
) -> None:
    require(
        git("rev-parse", "HEAD") == expected_parent or phase == "postcommit",
        "parent HEAD drift",
    )
    if phase == "precommit":
        changed = set(git("status", "--porcelain=v1", "--untracked-files=all").splitlines())
        changed_paths = sorted(line[3:] for line in changed if line)
        require(changed_paths == controlled_paths, "precommit controlled path set drift")
        return
    require(git("rev-parse", "HEAD^") == expected_parent, "observed commit parent drift")
    require(git("log", "-1", "--pretty=%s") == expected_subject, "observed subject drift")
    committed = sorted(
        line
        for line in git(
            "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
        ).splitlines()
        if line
    )
    require(committed == controlled_paths, "observed commit controlled path set drift")
    dirty = git("status", "--porcelain=v1", "--", *controlled_paths)
    require(not dirty, "controlled paths are dirty after commit")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("precommit", "postcommit"), required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-subject", required=True)
    parser.add_argument("--active-iteration-job-count", type=int, required=True)
    args = parser.parse_args()
    require(args.active_iteration_job_count == 0, "active Iter005 jobs remain")
    require(args.expected_parent == REPOSITORY_PARENT, "expected-parent argument drift")
    require(args.expected_subject == EXPECTED_SUBJECT, "expected-subject argument drift")
    decision = read_json(DECISION_PATH)
    registry_row = validate_records(decision)
    require(
        registry_row["closeout_identity"].startswith("controlled_paths_manifest_sha256="),
        "registry closeout identity prefix drift",
    )
    validate_artifacts(decision)
    validate_git_identity(
        phase=args.phase,
        expected_parent=args.expected_parent,
        expected_subject=args.expected_subject,
        controlled_paths=decision["controlled_paths"],
    )
    print(
        "PASS: Iter005 records, artifacts, accounting, and "
        f"{args.phase} closeout identity validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
