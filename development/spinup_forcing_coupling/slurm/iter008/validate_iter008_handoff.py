#!/usr/bin/env python3
"""Cross-validate Iter008 closeout records and the non-circular closeout commit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
COUPLING = ROOT / "development/spinup_forcing_coupling"
REPORT = COUPLING / "iterations/iter008.md"
CURRENT = COUPLING / "handoff/CURRENT.md"
SUMMARY = COUPLING / "ITERATION_SUMMARY.md"
REGISTRY = COUPLING / "registry.csv"
SUMMARY_ROOT = COUPLING / "summaries/iter008"
DECISION = SUMMARY_ROOT / "iter008_decision.json"
ACCOUNTING = SUMMARY_ROOT / "iter008_accounting.csv"
OUTPUT_ROOT = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling"
SUMMARY_PATH = "development/spinup_forcing_coupling/summaries/iter008"
OBJECTIVE = "Single-site ABBY and JERC coupled/drop21_corr080 SR MCMC diagnostic campaign"
BOUNDED = "ABBY and JERC separately; coupled drop21_corr080; SR; 64x4000; seed 8008; raw-chain diagnostics; integrity-only"
FORCING_SHA = "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
SPINUP_SHA = "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023"
FIELDS = ["iteration_id", "closed_at", "status", "work_type", "objective", "bounded_scope", "acceptance_result", "decision", "upstream_dependencies", "output_root", "summary_path", "closeout_mode", "closeout_identity", "notes"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def text(path: Path) -> str:
    require(path.is_file(), f"missing {path}")
    return path.read_text(encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout.rstrip("\n")


def list_hash(paths: list[str]) -> str:
    return hashlib.sha256(json.dumps(sorted(set(paths)), separators=(",", ":")).encode()).hexdigest()


def validate_records() -> dict:
    report, current, summary = text(REPORT), text(CURRENT), text(SUMMARY)
    decision = json.loads(text(DECISION))
    require("- Iteration ID: `iter008`" in report and "- Status: `completed`" in report and "- Phase: `closed`" in report, "report state mismatch")
    require("- Active iteration: `iter008`" in current and "- Status: `completed`" in current and "- Phase: `closed`" in current, "handoff state mismatch")
    require("- Active job IDs: none" in current, "active job remains in handoff")
    for doc_name, doc in (("report", report), ("handoff", current), ("summary", summary)):
        for value in (OBJECTIVE, BOUNDED, OUTPUT_ROOT, SUMMARY_PATH, FORCING_SHA, SPINUP_SHA):
            require(value in doc, f"{doc_name} lacks {value}")
    require(decision.get("iteration_id") == "iter008", "decision iteration mismatch")
    require(decision.get("status") == "completed", "decision status mismatch")
    require(decision.get("acceptance_result") == "pass", "decision acceptance mismatch")
    require(decision.get("passed") is True, "decision not passed")
    require(ACCOUNTING.is_file(), "accounting missing")
    with REGISTRY.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        require(reader.fieldnames == FIELDS, "registry schema mismatch")
        rows = [row for row in reader if row["iteration_id"] == "iter008"]
    require(len(rows) == 1, "registry Iter008 row count")
    row = rows[0]
    for key, value in {"status": "completed", "work_type": "implementation", "objective": OBJECTIVE, "bounded_scope": BOUNDED, "acceptance_result": "pass", "output_root": OUTPUT_ROOT, "summary_path": SUMMARY_PATH, "closeout_mode": "committed"}.items():
        require(row[key] == value, f"registry {key} mismatch")
    require(FORCING_SHA in row["upstream_dependencies"] and SPINUP_SHA in row["upstream_dependencies"], "registry dependency mismatch")
    return decision


def validate_git(phase: str, parent: str, subject: str) -> None:
    head = git("rev-parse", "HEAD")
    if phase == "precommit":
        require(head == parent, f"precommit parent mismatch: {head}")
        require(bool(git("status", "--porcelain").strip()), "expected bounded dirty worktree")
    else:
        require(git("rev-parse", "HEAD^") == parent, "postcommit parent mismatch")
        require(git("log", "-1", "--format=%s") == subject, "postcommit subject mismatch")
        require(not git("status", "--porcelain").strip(), "postcommit worktree dirty")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("precommit", "postcommit"), required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-subject", required=True)
    parser.add_argument("--active-job-count", type=int, required=True)
    args = parser.parse_args()
    require(args.active_job_count == 0, "active jobs remain")
    decision = validate_records()
    controlled = decision.get("controlled_paths", [])
    if controlled:
        require(controlled == sorted(set(controlled)), "controlled paths not sorted/unique")
        require(decision.get("controlled_paths_manifest_sha256") == list_hash(controlled), "controlled paths hash mismatch")
    validate_git(args.phase, args.expected_parent, args.expected_subject)
    print(f"ITER008_HANDOFF_VALIDATE_PASS phase={args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
