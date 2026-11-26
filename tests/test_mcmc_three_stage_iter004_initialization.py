from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_initialization import (
    assess_stage_one,
    physical_to_unit,
    prior_aware_candidates,
    scrambled_sobol_prefix,
    select_candidate_pool,
    select_walkers,
    validate_pool_geometry,
    validate_walker_geometry,
)


PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")


class Iter004InitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prior = Prior18.from_directory(PPE1, PPE1_ROOT)

    def test_nested_scrambled_sobol_and_exact_prior_mapping(self) -> None:
        stage_one = scrambled_sobol_prefix(dimension=18, count=1024, seed=420041)
        maximum = scrambled_sobol_prefix(dimension=18, count=2048, seed=420041)
        np.testing.assert_array_equal(stage_one, maximum[:1024])
        self.assertFalse(np.array_equal(
            stage_one, scrambled_sobol_prefix(dimension=18, count=1024, seed=420042)
        ))
        physical = prior_aware_candidates(self.prior, stage_one)
        replay = physical_to_unit(self.prior, physical)
        np.testing.assert_allclose(replay, stage_one, rtol=1.0e-12, atol=1.0e-12)
        self.assertTrue(np.all(np.asarray(self.prior.support_mask(physical), dtype=bool)))
        root_low, root_high = self.prior.cn_bounds(physical[:, 16])
        self.assertTrue(np.all(physical[:, 17] >= root_low))
        self.assertTrue(np.all(physical[:, 17] <= root_high))

    def test_stage_pool_and_walker_rules_are_deterministic(self) -> None:
        unit = scrambled_sobol_prefix(dimension=18, count=1024, seed=420041)
        physical = prior_aware_candidates(self.prior, unit)
        eligible = np.ones(1024, dtype=bool)
        assessment = assess_stage_one(unit, eligible)
        self.assertTrue(assessment.stage_pass, assessment.failure_reasons)
        scores = -np.square(unit - 0.5).sum(axis=1)
        candidate_indices = np.arange(1024, dtype=np.int64)
        first_pool = select_candidate_pool(
            unit=unit, physical=physical, log_posterior=scores,
            eligible=eligible, candidate_indices=candidate_indices,
        )
        second_pool = select_candidate_pool(
            unit=unit, physical=physical, log_posterior=scores,
            eligible=eligible, candidate_indices=candidate_indices,
        )
        np.testing.assert_array_equal(first_pool, second_pool)
        validate_pool_geometry(unit[first_pool])
        walkers = select_walkers(
            unit=unit[first_pool], log_posterior=scores[first_pool],
            candidate_indices=candidate_indices[first_pool], seed=430041,
        )
        replay = select_walkers(
            unit=unit[first_pool], log_posterior=scores[first_pool],
            candidate_indices=candidate_indices[first_pool], seed=430041,
        )
        np.testing.assert_array_equal(walkers, replay)
        validate_walker_geometry(unit[first_pool][walkers])
        self.assertEqual(np.unique(physical[first_pool][walkers], axis=0).shape[0], 64)

    def test_stage_two_triggers_are_not_score_based(self) -> None:
        unit = scrambled_sobol_prefix(dimension=18, count=1024, seed=420041)
        eligible = np.ones(1024, dtype=bool)
        eligible[:600] = False
        assessment = assess_stage_one(unit, eligible)
        self.assertFalse(assessment.stage_pass)
        self.assertIn("fewer_than_512_finite_unique_eligible", assessment.failure_reasons)
        self.assertIn("finite_rate_below_0.90", assessment.failure_reasons)
        with self.assertRaises(ValueError):
            scrambled_sobol_prefix(dimension=18, count=1000, seed=420041)


if __name__ == "__main__":
    unittest.main()
