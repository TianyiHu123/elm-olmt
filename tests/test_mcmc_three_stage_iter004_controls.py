from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from model_ELM.mcmc_three_stage_artifacts import (
    immutable_checkpoint_snapshot,
    validate_independent_review,
    validate_job_accounting,
)
from model_ELM.mcmc_three_stage_diagnostics import (
    ContinuationGate,
    continuation_outcome,
    proposal_rejection_rates,
)
from model_ELM.mcmc_three_stage_initialization import (
    validate_candidate_identity_arrays,
    validate_selection_ledger,
)
from development.mcmc_optimization.slurm.iter004.run_iter004 import (
    validate_failure_closeout_accounting,
)


def gate(*, fatal=(), limitation=(), passed=False):
    reasons = tuple(fatal) + tuple(limitation)
    return ContinuationGate(
        pass_gate=passed, reasons=reasons, fatal_reasons=tuple(fatal),
        limitation_reasons=tuple(limitation), iteration=128, unique_states=64,
        rank=18, condition_number=2.0, overall_numerical_rejection_rate=0.0,
        maximum_walker_numerical_rejection_rate=0.0, peak_rss_gib=1.0,
        projected_total_hours=1.0, projected_site_storage_gib=1.0,
        projected_total_storage_gib=2.0,
    )


class Iter004ControlTests(unittest.TestCase):
    def test_fatal_and_nonfatal_continuation_outcomes_are_distinct(self) -> None:
        self.assertEqual(continuation_outcome(gate(fatal=("current_state_rank_below_18",))),
                         "iter004_validation_failed")
        self.assertEqual(continuation_outcome(gate(limitation=("projected_runtime_above_5.5_hours",))),
                         "validated_with_nonfatal_limitation")
        self.assertEqual(continuation_outcome(gate(passed=True)), "continue")

    def test_proposal_rejection_rates_use_all_proposals_by_walker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            rows = []
            for walker in range(2):
                for proposal in range(2):
                    rows.append({"walker": walker, "blob": {"reason_code": int(walker == 1 and proposal == 0)}})
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            self.assertEqual(proposal_rejection_rates(path, nwalkers=2), (0.25, 0.5, 4))

    def test_candidate_identity_arrays_reject_reuse_drift(self) -> None:
        values = np.arange(4, dtype=np.int64)
        validate_candidate_identity_arrays(
            site_values=np.full(4, "ABBY"), target_values=np.full(4, "a" * 64),
            source_values=np.full(4, "b" * 64), candidate_indices=values,
            expected_site="ABBY", expected_target_sha256="a" * 64,
            expected_source_sha256="b" * 64,
        )
        with self.assertRaisesRegex(ValueError, "target identity"):
            validate_candidate_identity_arrays(
                site_values=np.full(4, "ABBY"), target_values=np.full(4, "c" * 64),
                source_values=np.full(4, "b" * 64), candidate_indices=values,
                expected_site="ABBY", expected_target_sha256="a" * 64,
                expected_source_sha256="b" * 64,
            )

    def test_selection_ledger_schema_and_positions_are_locked(self) -> None:
        payload = {
            "schema": "mcmc-iter004-walker-selection-ledger-v1", "site": "ABBY",
            "target_sha256": "a" * 64, "source_sha256": "b" * 64,
            "entries": [{"walker": value} for value in range(64)],
        }
        validate_selection_ledger(
            payload, schema="mcmc-iter004-walker-selection-ledger-v1", site="ABBY",
            count=64, target_sha256="a" * 64, source_sha256="b" * 64,
        )
        payload["entries"][1]["walker"] = 9
        with self.assertRaisesRegex(ValueError, "positions"):
            validate_selection_ledger(
                payload, schema="mcmc-iter004-walker-selection-ledger-v1", site="ABBY",
                count=64, target_sha256="a" * 64, source_sha256="b" * 64,
            )

    def test_accounting_enforces_terminal_scope_and_retry_ceiling(self) -> None:
        row = {
            "submission_sequence": 1, "job_id": "123", "planned_job": "preflight_iter004.slurm",
            "account": "chopinsong", "partition": "standard", "alloc_cpus": 2,
            "state": "COMPLETED", "exit_code": "0:0", "retry_class": "planned",
            "failure_classification": "none", "job_name": "mcmc_i004_wu1",
            "elapsed": "00:01:00", "total_cpu": "00:01:30", "max_rss": "1G",
            "req_mem": "10Gn", "node_list": "r1i0n1",
        }
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [row]},
            expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=1,
        )
        self.assertEqual(summary["attempt_count"], 1)
        bad = dict(row); bad["state"] = "RUNNING"
        with self.assertRaisesRegex(ValueError, "nonterminal"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [bad]},
                expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=1,
            )
        def attempt(sequence, job_id, retry_class, state, failure):
            value = dict(row)
            value.update(
                submission_sequence=sequence, job_id=str(job_id), retry_class=retry_class,
                state=state, exit_code="0:0" if state == "COMPLETED" else "1:0",
                failure_classification=failure,
            )
            return value
        two_corrections = [
            attempt(1, 201, "planned", "FAILED", "preflight_packaging"),
            attempt(2, 202, "preflight_correction", "FAILED", "preflight_application_compatibility"),
            attempt(3, 203, "preflight_correction", "COMPLETED", "none"),
        ]
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": two_corrections},
            expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=3,
        )
        self.assertEqual(summary["preflight_corrections"], 2)
        diagnostic_predecessor = attempt(
            3, 24825557, "preflight_correction", "FAILED", "preflight_numerical_parity",
        )
        diagnostic_attempt = attempt(4, 24825862, "preflight_diagnostic", "COMPLETED", "none")
        diagnostic_attempt["preceding_job_id"] = "24825557"
        diagnostic_attempt["diagnostic_outcome"] = "parity_fail"
        diagnostic = two_corrections[:2] + [diagnostic_predecessor, diagnostic_attempt]
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": diagnostic},
            expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=4,
        )
        self.assertEqual(summary["preflight_diagnostics"], 1)
        wrong_predecessor = [dict(value) for value in diagnostic]
        wrong_predecessor[-1]["preceding_job_id"] = "24825558"
        with self.assertRaisesRegex(ValueError, "predecessor job identity"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": wrong_predecessor},
                expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=4,
            )
        post_diagnostic_correction = attempt(5, 205, "preflight_correction", "COMPLETED", "none")
        post_diagnostic_correction["preceding_job_id"] = "24825862"
        corrected = diagnostic + [post_diagnostic_correction]
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": corrected},
            expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=5,
        )
        self.assertEqual(summary["preflight_corrections"], 3)
        wrong_correction_predecessor = [dict(value) for value in corrected]
        wrong_correction_predecessor[-1]["preceding_job_id"] = "24825863"
        with self.assertRaisesRegex(ValueError, "authorized preceding"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": wrong_correction_predecessor},
                expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=5,
            )
        four_corrections = [attempt(1, 211, "planned", "FAILED", "preflight_packaging")]
        four_corrections.extend(
            attempt(index, 210 + index, "preflight_correction",
                    "COMPLETED" if index == 5 else "FAILED",
                    "none" if index == 5 else "preflight_packaging")
            for index in range(2, 6)
        )
        with self.assertRaisesRegex(ValueError, "more than three"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": four_corrections},
                expected_jobs={"preflight_iter004.slurm": 2}, maximum_submissions=5,
            )
        def infrastructure_attempt(sequence, state):
            value = attempt(
                sequence, 300 + sequence,
                "planned" if sequence == 1 else "shared_infrastructure_retry",
                state, "none" if state == "COMPLETED" else "scheduler",
            )
            value.update(planned_job="pilot_abby_iter004.slurm", alloc_cpus=4)
            return value
        one_shared = [infrastructure_attempt(i, "COMPLETED" if i == 2 else "FAILED")
                      for i in range(1, 3)]
        with self.assertRaisesRegex(ValueError, "budget is exhausted"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": one_shared},
                expected_jobs={"pilot_abby_iter004.slurm": 4}, maximum_submissions=2,
            )
        pilot_failed = attempt(1, 24827059, "planned", "FAILED", "pilot_precreated_directory_compatibility")
        pilot_failed.update(planned_job="pilot_abby_iter004.slurm", alloc_cpus=4)
        pilot_fixed = attempt(2, 24827062, "pilot_startup_correction", "COMPLETED", "none")
        pilot_fixed.update(planned_job="pilot_abby_iter004.slurm", alloc_cpus=4, preceding_job_id="24827059")
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [pilot_failed, pilot_fixed]},
            expected_jobs={"pilot_abby_iter004.slurm": 4}, maximum_submissions=2,
        )
        self.assertEqual(summary["pilot_startup_corrections"], 1)
        pilot_fatal = dict(pilot_fixed)
        pilot_fatal.update(
            state="FAILED", exit_code="1:0",
            failure_classification="pilot_fatal_numerical_rejection",
        )
        failure_summary = validate_failure_closeout_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [pilot_failed, pilot_fatal]},
            expected_jobs={"pilot_abby_iter004.slurm": 4}, maximum_submissions=2,
        )
        self.assertFalse(failure_summary["all_required_jobs_successful"])
        self.assertTrue(failure_summary["fatal_pilot_closeout"])
        with self.assertRaisesRegex(ValueError, "lacks a successful terminal attempt"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [pilot_failed, pilot_fatal]},
                expected_jobs={"pilot_abby_iter004.slurm": 4}, maximum_submissions=2,
            )
        nonpilot_fatal = dict(pilot_fatal)
        nonpilot_fatal.update(
            submission_sequence=1, planned_job="diagnostics_iter004.slurm",
            retry_class="planned", failure_classification="scheduler",
        )
        nonpilot_fatal.pop("preceding_job_id", None)
        with self.assertRaisesRegex(RuntimeError, "non-pilot job lacks a successful"):
            validate_failure_closeout_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [nonpilot_fatal]},
                expected_jobs={"diagnostics_iter004.slurm": 4}, maximum_submissions=1,
            )
        jerc_failed = attempt(1, 24827061, "planned", "FAILED", "pilot_precreated_directory_compatibility")
        jerc_failed.update(planned_job="pilot_jerc_iter004.slurm", alloc_cpus=4)
        jerc_fixed = attempt(2, 24827063, "pilot_startup_correction", "COMPLETED", "none")
        jerc_fixed.update(planned_job="pilot_jerc_iter004.slurm", alloc_cpus=4, preceding_job_id="24827061")
        validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [jerc_failed, jerc_fixed]},
            expected_jobs={"pilot_jerc_iter004.slurm": 4}, maximum_submissions=2,
        )
        wrong_pilot_scope = dict(pilot_failed)
        wrong_pilot_scope.update(planned_job="search_abby_iter004.slurm")
        with self.assertRaisesRegex(ValueError, "pilot failure classification"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": [wrong_pilot_scope]},
                expected_jobs={"search_abby_iter004.slurm": 4}, maximum_submissions=1,
                require_all_successful=False,
            )
        wu3_planned = attempt(1, 24826641, "planned", "FAILED", "pool_replay_numerical_parity")
        wu3_planned.update(planned_job="pool_restart_iter004.slurm", alloc_cpus=4)
        wu3_corrected = attempt(
            2, 24826855, "wu3_correction", "FAILED", "wu3_target_identity_packaging",
        )
        wu3_corrected.update(
            planned_job="pool_restart_iter004.slurm", alloc_cpus=4,
            preceding_job_id="24826641",
        )
        wu3_identity_corrected = attempt(3, 24826856, "wu3_identity_correction", "COMPLETED", "none")
        wu3_identity_corrected.update(
            planned_job="pool_restart_iter004.slurm", alloc_cpus=4,
            preceding_job_id="24826855",
        )
        summary = validate_job_accounting(
            {"schema": "mcmc-iter004-job-accounting-v1",
             "attempts": [wu3_planned, wu3_corrected, wu3_identity_corrected]},
            expected_jobs={"pool_restart_iter004.slurm": 4}, maximum_submissions=3,
        )
        self.assertEqual(summary["wu3_corrections"], 1)
        self.assertEqual(summary["wu3_identity_corrections"], 1)
        wu3_wrong = [dict(wu3_planned), dict(wu3_corrected), dict(wu3_identity_corrected)]
        wu3_wrong[1]["preceding_job_id"] = "24826640"
        with self.assertRaisesRegex(ValueError, "WU3 correction predecessor"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": wu3_wrong},
                expected_jobs={"pool_restart_iter004.slurm": 4}, maximum_submissions=3,
            )
        wu3_identity_wrong = [dict(wu3_planned), dict(wu3_corrected), dict(wu3_identity_corrected)]
        wu3_identity_wrong[-1]["preceding_job_id"] = "24826854"
        with self.assertRaisesRegex(ValueError, "WU3 identity correction predecessor"):
            validate_job_accounting(
                {"schema": "mcmc-iter004-job-accounting-v1", "attempts": wu3_identity_wrong},
                expected_jobs={"pool_restart_iter004.slurm": 4}, maximum_submissions=3,
            )

    def test_independent_review_requires_exact_artifact_identity(self) -> None:
        artifacts = {"results/diagnostics_validation.json": "a" * 64}
        payload = {
            "schema": "mcmc-iter004-result-review-v1", "outcome": "pass",
            "reviewer": "independent-agent", "reviewed_artifacts": artifacts,
            "decision_candidate": "mcmc_pilot_validated",
        }
        validate_independent_review(
            payload, schema="mcmc-iter004-result-review-v1",
            reviewed_artifacts=artifacts, decision_candidate="mcmc_pilot_validated",
        )
        with self.assertRaisesRegex(ValueError, "identities"):
            validate_independent_review(
                payload, schema="mcmc-iter004-result-review-v1",
                reviewed_artifacts={"results/diagnostics_validation.json": "b" * 64},
                decision_candidate="mcmc_pilot_validated",
            )

    def test_checkpoint_snapshot_is_hashed_timed_and_nonoverwriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "active_backend.h5"
            source.write_bytes(b"checkpoint-fixture")
            manifest = immutable_checkpoint_snapshot(
                backend_path=source, checkpoint_root=Path(tmp) / "checkpoints",
                step=64, identity_sha256="d" * 64,
            )
            self.assertGreaterEqual(manifest["copy_seconds"], 0.0)
            self.assertEqual(manifest["backend_size_bytes"], len(b"checkpoint-fixture"))
            with self.assertRaises(FileExistsError):
                immutable_checkpoint_snapshot(
                    backend_path=source, checkpoint_root=Path(tmp) / "checkpoints",
                    step=64, identity_sha256="d" * 64,
                )


if __name__ == "__main__":
    unittest.main()
