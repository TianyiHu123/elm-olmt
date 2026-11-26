from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import emcee
import numpy as np

from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_initialization import scrambled_sobol_prefix
from model_ELM.mcmc_three_stage_posterior import PosteriorResult, SamplingPosteriorResult
from model_ELM.mcmc_three_stage_sampler import (
    BLOB_DTYPE,
    AuditedDEMove,
    AuditedDESnookerMove,
    ProposalAuditLedger,
    finalize_sampler_run,
    random_state_equal,
    run_sampler_block,
)


PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")


class FakePosterior:
    def __init__(self, prior: Prior18) -> None:
        self.prior = prior

    def evaluate_sampling_batch(self, coordinates):
        values = np.asarray(coordinates, dtype=np.float64)
        results = []
        for sampler_row in values:
            try:
                physical_row = self.prior.coordinate_transform.sampler_to_physical(sampler_row)
            except (ValueError, FloatingPointError):
                invalid = PosteriorResult(
                    site="ABBY", prior_id="ppe1", gpp_resolution="daily", sr_resolution="daily",
                    cn_observation_cv=0.30, include_cn=True, log_prior=-np.inf,
                    log_likelihood_gpp=0.0, log_likelihood_sr=0.0,
                    log_likelihood_cn=0.0, log_posterior=-np.inf,
                    n_gpp=1, n_sr=1, surrogate_evaluated=False, gpp_raw_min=None,
                    evaluation_error="outside_prior_support", provenance={},
                )
                results.append(SamplingPosteriorResult(
                    physical=invalid, log_abs_det_jacobian=-np.inf,
                    log_sampling_posterior=-np.inf,
                ))
                continue
            log_prior = float(self.prior.log_density(physical_row))
            jacobian = float(self.prior.coordinate_transform.log_abs_det_dphysical_dsampler(sampler_row))
            likelihood = -0.5 * float(np.dot(sampler_row, sampler_row))
            posterior = PosteriorResult(
                site="ABBY", prior_id="ppe1", gpp_resolution="daily", sr_resolution="daily",
                cn_observation_cv=0.30, include_cn=True, log_prior=log_prior,
                log_likelihood_gpp=likelihood, log_likelihood_sr=0.0,
                log_likelihood_cn=0.0, log_posterior=log_prior + likelihood,
                n_gpp=1, n_sr=1, surrogate_evaluated=True, gpp_raw_min=0.0,
                evaluation_error=None, provenance={},
            )
            results.append(SamplingPosteriorResult(
                physical=posterior, log_abs_det_jacobian=jacobian,
                log_sampling_posterior=posterior.log_posterior + jacobian,
            ))
        return results


def identity(seed: int) -> dict[str, object]:
    return {
        "site": "ABBY", "prior_id": "ppe1", "parameter_names": [f"p{i}" for i in range(18)],
        "posterior_target_sha256": "1" * 64, "pool_sha256": "2" * 64,
        "walker_sha256": "3" * 64, "emcee_version": emcee.__version__,
        "move_configuration": {"DEMove": 0.8, "DESnookerMove": 0.2},
        "seed": seed, "nwalkers": 64, "ndim": 18,
    }


class Iter004SamplerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prior = Prior18.from_directory(PPE1, PPE1_ROOT)
        unit = scrambled_sobol_prefix(dimension=18, count=64, seed=440041)
        physical = cls.prior.inverse_unit(unit)
        cls.initial = cls.prior.coordinate_transform.physical_to_sampler(physical)

    def _gaussian(self, values):
        return -0.5 * np.sum(np.square(values), axis=1)

    def test_audited_moves_preserve_installed_move_math(self) -> None:
        for installed, audited_factory in (
            (emcee.moves.DEMove(sigma=1.0e-5, gamma0=None), AuditedDEMove),
            (emcee.moves.DESnookerMove(gammas=1.7), AuditedDESnookerMove),
        ):
            with self.subTest(move=type(installed).__name__), tempfile.TemporaryDirectory() as tmp:
                state = np.random.RandomState(777).get_state()
                base = emcee.EnsembleSampler(64, 18, self._gaussian, vectorize=True, moves=installed)
                base.random_state = state
                base.run_mcmc(self.initial, 1, progress=False)
                ledger = ProposalAuditLedger(
                    Path(tmp) / "ledger.jsonl",
                    sampler_to_physical=self.prior.coordinate_transform.sampler_to_physical,
                )
                ledger.current_step = 1
                audited = emcee.EnsembleSampler(
                    64, 18, self._gaussian, vectorize=True, moves=audited_factory(ledger)
                )
                audited.random_state = state
                audited.run_mcmc(self.initial, 1, progress=False)
                np.testing.assert_array_equal(base.get_chain(), audited.get_chain())
                np.testing.assert_array_equal(base.get_log_prob(), audited.get_log_prob())
                np.testing.assert_array_equal(base.acceptance_fraction, audited.acceptance_fraction)
                rows = [json.loads(line) for line in (Path(tmp) / "ledger.jsonl").read_text().splitlines()]
                self.assertEqual(len(rows), 64)
                self.assertEqual({row["walker"] for row in rows}, set(range(64)))

    def test_split_restart_is_identical_and_completed_run_is_protected(self) -> None:
        fake = FakePosterior(self.prior)
        with tempfile.TemporaryDirectory() as tmp:
            uninterrupted = Path(tmp) / "uninterrupted"
            split = Path(tmp) / "split"
            uninterrupted.mkdir()
            run_sampler_block(
                posterior=fake, initial_sampler_coordinates=self.initial,
                run_directory=uninterrupted, identity=identity(440041),
                target_iteration=16, checkpoint_interval=8,
            )
            run_sampler_block(
                posterior=fake, initial_sampler_coordinates=self.initial,
                run_directory=split, identity=identity(440041),
                target_iteration=8, checkpoint_interval=8,
            )
            run_sampler_block(
                posterior=fake, initial_sampler_coordinates=self.initial,
                run_directory=split, identity=identity(440041),
                target_iteration=16, checkpoint_interval=8, resume=True,
            )
            first = emcee.backends.HDFBackend(str(uninterrupted / "active_backend.h5"), read_only=True)
            second = emcee.backends.HDFBackend(str(split / "active_backend.h5"), read_only=True)
            np.testing.assert_array_equal(first.get_chain(), second.get_chain())
            np.testing.assert_array_equal(first.get_log_prob(), second.get_log_prob())
            np.testing.assert_array_equal(first.get_blobs(), second.get_blobs())
            np.testing.assert_array_equal(first.accepted, second.accepted)
            self.assertTrue(random_state_equal(
                first.get_last_sample().random_state, second.get_last_sample().random_state
            ))
            finalize_sampler_run(split, decision="restart_test_pass")
            with self.assertRaises(FileExistsError):
                run_sampler_block(
                    posterior=fake, initial_sampler_coordinates=self.initial,
                    run_directory=split, identity=identity(440041),
                    target_iteration=24, checkpoint_interval=8, resume=True,
                )
            occupied = Path(tmp) / "occupied"
            occupied.mkdir(); (occupied / "unexpected.txt").write_text("protected")
            with self.assertRaises(FileExistsError):
                run_sampler_block(
                    posterior=fake, initial_sampler_coordinates=self.initial,
                    run_directory=occupied, identity=identity(440041),
                    target_iteration=8, checkpoint_interval=8,
                )

    def test_blob_dtype_is_fixed(self) -> None:
        self.assertEqual(BLOB_DTYPE.names, (
            "log_physical_posterior", "log_prior", "log_likelihood_gpp",
            "log_likelihood_sr", "log_likelihood_cn", "log_abs_det_jacobian", "reason_code",
        ))
        state = np.random.RandomState(123).get_state()
        self.assertTrue(random_state_equal(list(state), tuple(state)))
        changed = list(state); changed[-1] = float(changed[-1]) + 1.0
        self.assertFalse(random_state_equal(list(state), changed))


if __name__ == "__main__":
    unittest.main()
