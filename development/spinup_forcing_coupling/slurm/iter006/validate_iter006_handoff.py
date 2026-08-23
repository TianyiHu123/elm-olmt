#!/usr/bin/env python3
"""Cross-validate Iter006 closeout records and non-circular commit identity."""

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
REPORT = COUPLING_ROOT / "iterations" / "iter006.md"
CUMULATIVE = COUPLING_ROOT / "ITERATION_SUMMARY.md"
REGISTRY = COUPLING_ROOT / "registry.csv"
CURRENT = COUPLING_ROOT / "handoff" / "CURRENT.md"
SUMMARY_ROOT = COUPLING_ROOT / "summaries" / "iter006"
DECISION_PATH = SUMMARY_ROOT / "iter006_decision.json"
ACCOUNTING_PATH = SUMMARY_ROOT / "iter006_accounting.csv"
SMOKE_IDENTITY_PATH = SUMMARY_ROOT / "iter006_smoke_identity.json"
OUTPUT_ROOT = (
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/"
    "spinup_forcing_coupling"
)
SUMMARY_PATH = "development/spinup_forcing_coupling/summaries/iter006"
OBJECTIVE = "MCMC three-mode spinup wiring (mean / member-restart / coupled)"
BOUNDED_SCOPE = (
    "ABBY smoke; three MCMC spinup modes; coupled drop32/drop21_corr080; "
    "<=10 likelihood evals/mode; no production campaign"
)
ACCEPTANCE_RESULT = "pass"
DECISION = (
    "MCMC can select and call locked coupling/offline primitives under each "
    "declared spinup mode; mean/member-restart paths still work; production "
    "campaign readiness not established"
)
FORCING_SHA = "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
REPOSITORY_PARENT = "542b7d3ce74bd3baa23c48b5b4638270be12cf86"
EXPECTED_SUBJECT = "Close Iter006 three-mode MCMC spinup wiring"
NEXT_PLAN_MARKER = "Proposed iteration: `iter007`"
NEXT_PLAN_DETAIL_MARKERS = (
    "production MCMC",
    "campaign",
    "spinup-mode",
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
    require("- Iteration ID: `iter006`" in report, "report iteration ID drift")
    require("- Work type: `implementation`" in report, "report work type drift")
    require("- Status: `completed`" in report, "report status drift")
    require("- Phase: `closed`" in report, "report phase drift")
    require("- Active iteration: `iter006`" in current, "handoff iteration ID drift")
    require("- Status: `completed`" in current, "handoff status drift")
    require("- Phase: `closed`" in current, "handoff phase drift")
    require("- Active job IDs: none" in current, "handoff retains an active job")
    require("## iter006" in cumulative, "cumulative summary lacks Iter006")

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
    matches = [row for row in rows if row["iteration_id"] == "iter006"]
    require(len(matches) == 1, "registry must contain exactly one Iter006 row")
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
    require(SMOKE_IDENTITY_PATH.is_file(), "smoke identity summary is missing")
    smoke = read_json(SMOKE_IDENTITY_PATH)
    require(smoke.get("passed") is True, "smoke identity not passed")
    require(smoke.get("site") == "ABBY", "smoke site drift")
    for mode in ("mean_spinup", "member_restart", "coupled"):
        require(mode in smoke.get("modes_exercised", []), f"smoke missing mode {mode}")
    expected = {
        "schema": "spinup-forcing-coupling-iter006-decision-v1",
        "iteration_id": "iter006",
        "forcing_artifact_sha256": FORCING_SHA,
        "passed": True,
    }
    for key, value in expected.items():
        require(decision.get(key) == value, f"decision evidence {key} drift")


def validate_git_identity(
    *,
    phase: str,
    expected_parent: str,
    expected_subject: str,
) -> None:
    head = git("rev-parse", "HEAD")
    if phase == "precommit":
        require(head == expected_parent, f"precommit HEAD drift: {head} != {expected_parent}")
        status = git("status", "--porcelain")
        require(status.strip(), "precommit expected a dirty controlled worktree")
        return
    if phase == "postcommit":
        parent = git("rev-parse", "HEAD^")
        subject = git("log", "-1", "--format=%s")
        require(parent == expected_parent, f"postcommit parent drift: {parent}")
        require(subject == expected_subject, f"postcommit subject drift: {subject}")
        status = git("status", "--porcelain")
        require(not status.strip(), "postcommit worktree must be clean for controlled paths")
        return
    raise ValueError(f"unknown phase {phase}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-iteration-job-count", type=int, required=True)
    parser.add_argument("--phase", choices=("precommit", "postcommit"), required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-subject", required=True)
    args = parser.parse_args()
    require(args.active_iteration_job_count == 0, "active jobs remain")
    decision = read_json(DECISION_PATH)
    validate_records(decision)
    validate_artifacts(decision)
    validate_git_identity(
        phase=args.phase,
        expected_parent=args.expected_parent,
        expected_subject=args.expected_subject,
    )
    print(
        "PASS: Iter006 records, artifacts, accounting, and "
        f"{args.phase} closeout identity validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
