"""Non-overwriting artifact helpers for three-stage MCMC workflows."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any

import numpy as np


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_json_exclusive(path: Path | str, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def write_npz_exclusive(path: Path | str, **arrays: np.ndarray) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            np.savez_compressed(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def require_matching_identity(path: Path | str, expected: dict[str, Any]) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise ValueError(f"missing identity manifest: {target}")
    observed = json.loads(target.read_text(encoding="utf-8"))
    if observed != expected:
        raise ValueError(f"identity manifest mismatch: {target}")
    return observed


def completed_backend_guard(run_directory: Path | str) -> None:
    root = Path(run_directory)
    completed = root / "COMPLETED.json"
    if completed.exists():
        raise FileExistsError(f"completed sampler run cannot be overwritten or resumed: {completed}")


def immutable_checkpoint_snapshot(
    *, backend_path: Path | str, checkpoint_root: Path | str, step: int,
    identity_sha256: str,
) -> dict[str, Any]:
    source = Path(backend_path)
    if not source.is_file() or step <= 0:
        raise ValueError("checkpoint source must exist and step must be positive")
    destination = Path(checkpoint_root) / f"step_{step:04d}"
    destination.mkdir(parents=True, exist_ok=False)
    snapshot = destination / "backend.h5"
    started = time.perf_counter()
    with source.open("rb") as reader:
        descriptor = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
        with os.fdopen(descriptor, "wb") as writer:
            for block in iter(lambda: reader.read(1024 * 1024), b""):
                writer.write(block)
            writer.flush()
            os.fsync(writer.fileno())
    copy_seconds = time.perf_counter() - started
    payload = {
        "schema": "mcmc-three-stage-checkpoint-v1",
        "step": int(step),
        "identity_sha256": str(identity_sha256),
        "backend_path": str(snapshot),
        "backend_sha256": sha256_file(snapshot),
        "backend_size_bytes": snapshot.stat().st_size,
        "copy_seconds": copy_seconds,
        "copy_mib_per_second": (
            snapshot.stat().st_size / (1024.0 * 1024.0) / copy_seconds
            if copy_seconds > 0.0 else None
        ),
    }
    write_json_exclusive(destination / "manifest.json", payload)
    return payload


def directory_size_bytes(path: Path | str) -> int:
    root = Path(path)
    return sum(item.stat().st_size for item in root.rglob("*") if item.is_file())


TERMINAL_SLURM_STATES = frozenset({
    "COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL",
    "PREEMPTED", "BOOT_FAIL", "DEADLINE", "REVOKED",
})
AUTHORIZED_PREFLIGHT_DIAGNOSTIC_PREDECESSOR = "24825557"
AUTHORIZED_POST_DIAGNOSTIC_CORRECTION_PREDECESSOR = "24825862"
AUTHORIZED_WU3_CORRECTION_PREDECESSOR = "24826641"
AUTHORIZED_WU3_IDENTITY_CORRECTION_PREDECESSOR = "24826855"
AUTHORIZED_PILOT_CORRECTION_PREDECESSORS = {
    "pilot_abby_iter004.slurm": "24827059",
    "pilot_jerc_iter004.slurm": "24827061",
}
AUTHORIZED_LATER_RETRY_JOBS = frozenset({
    "pilot_abby_iter004.slurm", "pilot_jerc_iter004.slurm",
    "diagnostics_iter004.slurm", "final_iter004.slurm",
})


def validate_job_accounting(
    payload: dict[str, Any], *, expected_jobs: dict[str, int], maximum_submissions: int,
    require_all_successful: bool = True,
) -> dict[str, Any]:
    """Validate the bounded Iter004 attempt/retry and terminal-accounting contract."""

    if payload.get("schema") != "mcmc-iter004-job-accounting-v1":
        raise ValueError("job accounting schema mismatch")
    attempts = payload.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("job accounting attempts must be a nonempty list")
    if len(attempts) > int(maximum_submissions):
        raise ValueError("job accounting exceeds the submission ceiling")
    sequences = [row.get("submission_sequence") for row in attempts]
    if sequences != list(range(1, len(attempts) + 1)):
        raise ValueError("job accounting submission sequence is not contiguous")
    job_ids = [str(row.get("job_id", "")) for row in attempts]
    if any(not value.isdigit() for value in job_ids) or len(set(job_ids)) != len(job_ids):
        raise ValueError("job accounting job IDs must be unique positive integers")
    allowed_retry = {
        "planned", "preflight_correction", "preflight_diagnostic",
        "wu3_correction", "wu3_identity_correction", "pilot_startup_correction",
        "shared_infrastructure_retry",
    }
    allowed_infrastructure = {"scheduler", "node", "preemption", "transport"}
    allowed_preflight = {
        "preflight_packaging", "preflight_application_compatibility",
        "preflight_numerical_parity",
    }
    allowed_wu3 = {"pool_replay_numerical_parity", "wu3_target_identity_packaging"}
    allowed_pilot = {"pilot_precreated_directory_compatibility", "pilot_fatal_numerical_rejection"}
    retry_counts = {name: 0 for name in allowed_retry}
    by_job: dict[str, list[dict[str, Any]]] = {name: [] for name in expected_jobs}
    for row in attempts:
        required_accounting = {"job_name", "elapsed", "total_cpu", "max_rss", "req_mem", "node_list"}
        if not required_accounting.issubset(row):
            raise ValueError("job accounting resource fields are incomplete")
        job = row.get("planned_job")
        if job not in expected_jobs:
            raise ValueError(f"unapproved planned job in accounting: {job}")
        if row.get("account") != "chopinsong" or row.get("partition") != "standard":
            raise ValueError("job accounting account/partition mismatch")
        if int(row.get("alloc_cpus", -1)) != int(expected_jobs[job]):
            raise ValueError(f"job accounting CPU allocation mismatch for {job}")
        state = str(row.get("state", "")).split("+")[0]
        if state not in TERMINAL_SLURM_STATES:
            raise ValueError(f"nonterminal or unsupported Slurm state for {job}: {state}")
        retry_class = row.get("retry_class")
        if retry_class not in allowed_retry:
            raise ValueError(f"unsupported retry class: {retry_class}")
        if retry_class in {"preflight_correction", "preflight_diagnostic"} and job != "preflight_iter004.slurm":
            raise ValueError("preflight correction or diagnostic is outside preflight scope")
        if retry_class in {"wu3_correction", "wu3_identity_correction"} and job != "pool_restart_iter004.slurm":
            raise ValueError("WU3 correction is outside pool/restart scope")
        if retry_class == "pilot_startup_correction" and job not in AUTHORIZED_PILOT_CORRECTION_PREDECESSORS:
            raise ValueError("pilot startup correction is outside site-pilot scope")
        retry_counts[retry_class] += 1
        failure = row.get("failure_classification")
        if state == "COMPLETED" and row.get("exit_code") == "0:0":
            if failure not in (None, "none"):
                raise ValueError("successful attempt has a failure classification")
        else:
            if failure not in allowed_infrastructure | allowed_preflight | allowed_wu3 | allowed_pilot:
                raise ValueError("failed attempt lacks an approved classification")
            if failure in allowed_preflight and job != "preflight_iter004.slurm":
                raise ValueError("preflight failure classification is outside preflight scope")
            if failure in allowed_wu3 and job != "pool_restart_iter004.slurm":
                raise ValueError("WU3 failure classification is outside pool/restart scope")
            if failure in allowed_pilot and job not in AUTHORIZED_PILOT_CORRECTION_PREDECESSORS:
                raise ValueError("pilot failure classification is outside site-pilot scope")
        by_job[job].append(row)
    if retry_counts["preflight_correction"] > 3:
        raise ValueError("more than three preflight corrections were used")
    if retry_counts["preflight_diagnostic"] > 1:
        raise ValueError("more than one preflight diagnostic was used")
    if retry_counts["wu3_correction"] > 1:
        raise ValueError("more than one WU3 correction was used")
    if retry_counts["wu3_identity_correction"] > 1:
        raise ValueError("more than one WU3 identity correction was used")
    if retry_counts["pilot_startup_correction"] > 2:
        raise ValueError("more than two pilot startup corrections were used")
    if retry_counts["shared_infrastructure_retry"] > 0:
        raise ValueError("shared infrastructure retry budget is exhausted")
    for job, rows in by_job.items():
        if not rows:
            raise ValueError(f"missing accounting for planned job: {job}")
        if rows[0]["retry_class"] != "planned":
            raise ValueError(f"first attempt is not planned for {job}")
        if any(row["retry_class"] == "planned" for row in rows[1:]):
            raise ValueError(f"duplicate planned attempt for {job}")
        for previous, current in zip(rows, rows[1:]):
            if current["retry_class"] == "preflight_correction":
                ordinary_correction = previous.get("failure_classification") in allowed_preflight
                post_diagnostic_correction = (
                    previous.get("retry_class") == "preflight_diagnostic"
                    and str(previous.get("job_id")) == AUTHORIZED_POST_DIAGNOSTIC_CORRECTION_PREDECESSOR
                    and previous.get("diagnostic_outcome") == "parity_fail"
                    and str(current.get("preceding_job_id")) == AUTHORIZED_POST_DIAGNOSTIC_CORRECTION_PREDECESSOR
                )
                if not (ordinary_correction or post_diagnostic_correction):
                    raise ValueError("preflight correction lacks an authorized preceding preflight failure")
            elif current["retry_class"] == "preflight_diagnostic":
                if previous.get("failure_classification") != "preflight_numerical_parity":
                    raise ValueError("preflight diagnostic lacks the authorized numerical-parity predecessor")
                if (str(previous.get("job_id")) != AUTHORIZED_PREFLIGHT_DIAGNOSTIC_PREDECESSOR
                        or str(current.get("preceding_job_id")) != AUTHORIZED_PREFLIGHT_DIAGNOSTIC_PREDECESSOR):
                    raise ValueError("preflight diagnostic predecessor job identity mismatch")
            elif current["retry_class"] == "wu3_correction":
                if (previous.get("failure_classification") != "pool_replay_numerical_parity"
                        or str(previous.get("job_id")) != AUTHORIZED_WU3_CORRECTION_PREDECESSOR
                        or str(current.get("preceding_job_id")) != AUTHORIZED_WU3_CORRECTION_PREDECESSOR):
                    raise ValueError("WU3 correction predecessor job identity mismatch")
            elif current["retry_class"] == "wu3_identity_correction":
                if (previous.get("failure_classification") != "wu3_target_identity_packaging"
                        or str(previous.get("job_id")) != AUTHORIZED_WU3_IDENTITY_CORRECTION_PREDECESSOR
                        or str(current.get("preceding_job_id")) != AUTHORIZED_WU3_IDENTITY_CORRECTION_PREDECESSOR):
                    raise ValueError("WU3 identity correction predecessor job identity mismatch")
            elif current["retry_class"] == "pilot_startup_correction":
                predecessor = AUTHORIZED_PILOT_CORRECTION_PREDECESSORS.get(job)
                if (previous.get("failure_classification") != "pilot_precreated_directory_compatibility"
                        or str(previous.get("job_id")) != predecessor
                        or str(current.get("preceding_job_id")) != predecessor):
                    raise ValueError("pilot startup correction predecessor job identity mismatch")
            elif current["retry_class"] == "shared_infrastructure_retry":
                if job not in AUTHORIZED_LATER_RETRY_JOBS:
                    raise ValueError("shared retry is outside authorized later-job scope")
                if previous.get("failure_classification") not in allowed_infrastructure:
                    raise ValueError("shared retry lacks a preceding infrastructure failure")
        if require_all_successful:
            final = rows[-1]
            if final["state"].split("+")[0] != "COMPLETED" or final["exit_code"] != "0:0":
                raise ValueError(f"planned job lacks a successful terminal attempt: {job}")
    return {
        "attempt_count": len(attempts),
        "planned_job_count": len(expected_jobs),
        "preflight_corrections": retry_counts["preflight_correction"],
        "preflight_diagnostics": retry_counts["preflight_diagnostic"],
        "wu3_corrections": retry_counts["wu3_correction"],
        "wu3_identity_corrections": retry_counts["wu3_identity_correction"],
        "pilot_startup_corrections": retry_counts["pilot_startup_correction"],
        "shared_infrastructure_retries": retry_counts["shared_infrastructure_retry"],
        "all_terminal": True,
        "all_required_jobs_successful": bool(require_all_successful),
    }


def validate_independent_review(
    payload: dict[str, Any], *, schema: str, reviewed_artifacts: dict[str, str],
    decision_candidate: str | None = None,
) -> dict[str, Any]:
    if payload.get("schema") != schema:
        raise ValueError("independent review schema mismatch")
    if payload.get("outcome") not in ("pass", "pass_with_concerns"):
        raise ValueError("independent review did not pass")
    if payload.get("reviewer") in (None, "", "primary"):
        raise ValueError("independent reviewer identity is invalid")
    key = "reviewed_artifacts" if schema.endswith("result-review-v1") else "reviewed_identities"
    if payload.get(key) != reviewed_artifacts:
        raise ValueError("independent review artifact identities mismatch")
    if decision_candidate is not None and payload.get("decision_candidate") != decision_candidate:
        raise ValueError("independent review decision mismatch")
    return payload
