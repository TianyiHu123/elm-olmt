from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from model_ELM.mcmc_prior import PPE1, PPE2, Prior18

PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")
PPE2_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe2_vertc/params")


class PriorContractTests(unittest.TestCase):
    def priors(self):
        return ((PPE1, Prior18.from_directory(PPE1, PPE1_ROOT)),
                (PPE2, Prior18.from_directory(PPE2, PPE2_ROOT)))

    def test_inverse_maps_reproduce_authoritative_matrices(self):
        for prior_id, prior in self.priors():
            with self.subTest(prior_id=prior_id):
                unit = np.loadtxt(prior.metadata_file.parent / "sobol18_1024_unit.txt")
                expected = np.loadtxt(prior.metadata_file.parent / "sobol18_1024.txt")
                self.assertEqual(unit.shape, (1024, 18)); self.assertEqual(expected.shape, (1024, 18))
                np.testing.assert_allclose(prior.inverse_unit(unit), expected, rtol=1e-10, atol=1e-12)

    def test_conditional_distributions_are_normalized(self):
        for prior_id, prior in self.priors():
            with self.subTest(prior_id=prior_id):
                for leafcn in (15.0, 25.0, 39.0):
                    low, high = prior.cn_bounds(leafcn)
                    integral = quad(lambda root: 1.0 / (high - float(low)), float(low), high, epsabs=1e-13)[0]
                    self.assertLessEqual(abs(integral - 1.0), 1e-10)
                for ks3 in (3.0e-4, 8.0e-4, 3.0e-3):
                    low, high = prior.ks4_bounds(ks3)
                    width = np.log(float(high) / float(low))
                    integral = quad(lambda ks4: 1.0 / (ks4 * width), float(low), float(high), epsabs=1e-13)[0]
                    self.assertLessEqual(abs(integral - 1.0), 1e-10)

    def test_physical_density_support_and_ratios(self):
        for prior_id, prior in self.priors():
            with self.subTest(prior_id=prior_id):
                physical = prior.inverse_unit(np.full(18, 0.5)); self.assertTrue(prior.support_mask(physical))
                changed = physical.copy(); changed[0] *= 1.2
                expected = -np.log(changed[0] / physical[0])
                self.assertTrue(np.isclose(prior.log_density(changed) - prior.log_density(physical), expected, atol=1e-12))
                invalid = physical.copy(); invalid[17] = invalid[16]; self.assertEqual(prior.log_density(invalid), -np.inf)
                invalid = physical.copy(); invalid[0] = np.nan; self.assertEqual(prior.log_density(invalid), -np.inf)

    def test_ppe2_density_contains_conditional_width(self):
        prior = Prior18.from_directory(PPE2, PPE2_ROOT)
        first = prior.inverse_unit(np.full(18, 0.5))
        second = first.copy(); second[5] = 1.5e-3; second[6] = np.sqrt(8e-5 * 1e-3)
        self.assertTrue(prior.support_mask(second))
        observed = prior.log_density(second) - prior.log_density(first)
        independent_terms = -np.log(second[5] / first[5]) - np.log(second[6] / first[6])
        _, first_high = prior.ks4_bounds(first[5]); _, second_high = prior.ks4_bounds(second[5])
        width_term = -np.log(np.log(float(second_high) / 8e-5) / np.log(float(first_high) / 8e-5))
        self.assertTrue(np.isclose(observed, independent_terms + width_term, atol=1e-12))

    def test_sampling_transform_roundtrip_and_jacobian(self):
        for prior_id, prior in self.priors():
            with self.subTest(prior_id=prior_id):
                physical = prior.inverse_unit(np.linspace(0.1, 0.9, 18)); transform = prior.coordinate_transform
                sampler = transform.physical_to_sampler(physical)
                np.testing.assert_allclose(transform.sampler_to_physical(sampler), physical, rtol=1e-12, atol=1e-14)
                epsilon = 1e-6; numerical = 0.0
                for index in range(18):
                    plus = sampler.copy(); plus[index] += epsilon
                    minus = sampler.copy(); minus[index] -= epsilon
                    derivative = (transform.sampler_to_physical(plus)[index] - transform.sampler_to_physical(minus)[index]) / (2 * epsilon)
                    numerical += np.log(abs(derivative))
                analytic = transform.log_abs_det_dphysical_dsampler(sampler)
                self.assertTrue(np.isclose(numerical, analytic, rtol=1e-6, atol=1e-8))
                self.assertTrue(np.isclose(prior.sampler_log_density(sampler), prior.log_density(physical) + analytic, atol=1e-12))

    def test_prior_release_compatibility_fails_closed(self):
        Prior18.from_directory(PPE1, PPE1_ROOT).require_release_compatibility(PPE1)
        with self.assertRaisesRegex(ValueError, "prior/release incompatibility"):
            Prior18.from_directory(PPE2, PPE2_ROOT).require_release_compatibility(PPE1)


if __name__ == "__main__":
    unittest.main()
