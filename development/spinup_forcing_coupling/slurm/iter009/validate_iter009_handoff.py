#!/usr/bin/env python3
"""Fail closed on Iter009 cross-record and closeout-commit drift."""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path


ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING = ROOT / "development/spinup_forcing_coupling"
REPORT = COUPLING / "iterations" / "iter009.md"
CURRENT = COUPLING / "handoff" / "CURRENT.md"
SUMMARY = COUPLING / "ITERATION_SUMMARY.md"
REGISTRY = COUPLING / "registry.csv"
SUMMARY_ROOT = COUPLING / "summaries" / "iter009"
FIELDS = ["iteration_id", "closed_at", "status", "work_type", "objective", "bounded_scope", "acceptance_result", "decision", "upstream_dependencies", "output_root", "summary_path", "closeout_mode", "closeout_identity", "notes"]
OBJECTIVE = "ABBY and JERC sampler-geometry pilot"
BOUNDED = "ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011"
OUTPUT_ROOT = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling"
SUMMARY_PATH = "development/spinup_forcing_coupling/summaries/iter009"
DEPENDENCIES = (
    "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e",
    "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023",
    "e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2",
    "a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path}")
    return path.read_text(encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout.rstrip()


def field(document: str, label: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(label)}: `([^`]+)`$", document)
    require(match is not None, f"missing standardized {label} field")
    return match.group(1)


def changed_paths(parent: str, phase: str) -> set[str]:
    if phase == "postcommit":
        return {line for line in git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines() if line}
    tracked = {line for line in git("diff", "--name-only", parent).splitlines() if line}
    untracked = {line for line in git("ls-files", "--others", "--exclude-standard").splitlines() if line}
    return tracked | untracked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("precommit", "postcommit"), required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-subject", required=True)
    parser.add_argument("--active-job-count", type=int, required=True)
    parser.add_argument("--controlled-path", action="append", required=True)
    args = parser.parse_args()
    require(args.active_job_count == 0, "active jobs remain")
    report, current, summary = read(REPORT), read(CURRENT), read(SUMMARY)
    documents = {"report": report, "handoff": current, "summary": summary}
    for name, document in documents.items():
        for value in ("iter009", OBJECTIVE, BOUNDED, OUTPUT_ROOT, SUMMARY_PATH):
            require(value in document, f"{name} lacks {value}")
    require("- Status: `completed`" in report and "- Phase: `closed`" in report, "report not closed")
    require("- Status: `completed`" in current and "- Phase: `closed`" in current, "handoff not closed")
    require("- Active job IDs: none" in current, "handoff retains active jobs")
    standardized = ("Iteration ID", "Status", "Work type", "Objective", "Bounded scope", "Overall acceptance result", "Decision", "Next state")
    extracted = {name: {label: field(document, label) for label in standardized} for name, document in documents.items()}
    reference = extracted["report"]
    for name, values in extracted.items():
        require(values == reference, f"{name} standardized closeout fields disagree")
    require(reference == {
        "Iteration ID": "iter009", "Status": "completed", "Work type": "implementation",
        "Objective": OBJECTIVE, "Bounded scope": BOUNDED,
        "Overall acceptance result": reference["Overall acceptance result"],
        "Decision": reference["Decision"], "Next state": reference["Next state"],
    }, "standardized Iter009 identity fields drift")
    require(reference["Overall acceptance result"] in {"pass", "fail"}, "acceptance result invalid")
    for name in ("qualification_matrix.csv", "worst_case_selection.csv", "ITER009_REPORT.md", "decision.json", "iter009_accounting.csv"):
        require((SUMMARY_ROOT / name).is_file(), f"missing summary artifact {name}")
    decision = json.loads(read(SUMMARY_ROOT / "decision.json"))
    require(decision.get("schema") == "spinup-forcing-coupling-iter009-decision-v1", "decision schema drift")
    require(decision.get("route"), "decision route missing")
    require(decision.get("route") == reference["Decision"], "decision route record mismatch")
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        require(rows and list(rows[0]) == FIELDS, "registry schema drift")
    matches = [row for row in rows if row["iteration_id"] == "iter009"]
    require(len(matches) == 1, "registry Iter009 row count")
    row = matches[0]
    for key, value in {"status": "completed", "work_type": "implementation", "objective": OBJECTIVE, "bounded_scope": BOUNDED, "output_root": OUTPUT_ROOT, "summary_path": SUMMARY_PATH, "closeout_mode": "committed"}.items():
        require(row[key] == value, f"registry {key} drift")
    require(row["acceptance_result"] in {"pass", "fail"}, "registry acceptance result invalid")
    require(row["acceptance_result"] == reference["Overall acceptance result"], "registry acceptance mismatch")
    require(row["decision"] == reference["Decision"], "registry decision mismatch")
    require(reference["Next state"] in row["notes"], "registry next state mismatch")
    for dependency in DEPENDENCIES:
        require(dependency in row["upstream_dependencies"], "registry dependency mismatch")
        for name, document in documents.items():
            require(dependency in document, f"{name} dependency mismatch")
    head = git("rev-parse", "HEAD")
    expected_paths = set(args.controlled_path)
    require(len(expected_paths) == len(args.controlled_path), "duplicate controlled path")
    actual_paths = changed_paths(args.expected_parent, args.phase)
    require(actual_paths == expected_paths, f"controlled path drift: {sorted(actual_paths ^ expected_paths)}")
    if args.phase == "precommit":
        require(head == args.expected_parent, "precommit parent mismatch")
        require(git("status", "--porcelain"), "expected dirty controlled worktree")
    else:
        require(git("rev-parse", "HEAD^") == args.expected_parent, "postcommit parent mismatch")
        require(git("log", "-1", "--format=%s") == args.expected_subject, "postcommit subject mismatch")
        require(not git("status", "--porcelain"), "postcommit worktree dirty")
    print(f"ITER009_HANDOFF_VALIDATE_PASS phase={args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
