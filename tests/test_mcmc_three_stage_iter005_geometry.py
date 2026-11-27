from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_posterior import PosteriorResult, ThreeStagePosterior
from model_ELM.mcmc_three_stage_sampler import sampler_identity, run_sampler_block
from model_ELM.mcmc_three_stage_sampler_geometry import (
    COORDINATE_SYSTEM_ID, CoordinateSaturation, PriorUnitLogitGeometry,
)


PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")


class Iter005GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prior = Prior18.from_directory(PPE1, PPE1_ROOT)
        cls.geometry = PriorUnitLogitGeometry(cls.prior)

    def test_scalar_batch_prior_inverse_and_conditional_support(self) -> None:
        unit = np.array([np.linspace(0.1, 0.9, 18), np.linspace(0.9, 0.1, 18)])
        theta = self.prior.inverse_unit(unit)
        z = self.geometry.physical_to_sampler(theta)
        np.testing.assert_allclose(self.geometry.sampler_to_unit(z), unit, rtol=0, atol=1e-12)
        np.testing.assert_allclose(self.geometry.sampler_to_physical(z), theta, rtol=1e-12, atol=0)
        for index in range(2):
            np.testing.assert_array_equal(self.geometry.sampler_to_physical(z[index]),
                                          self.geometry.sampler_to_physical(z[index:index + 1])[0])
        self.assertTrue(np.all(self.prior.support_mask(theta)))
        lower, upper = self.prior.cn_bounds(theta[:, 16])
        self.assertTrue(np.all((theta[:, 17] > lower) & (theta[:, 17] < upper)))
        invalid = theta[0].copy(); invalid[17] = invalid[16]
        with self.assertRaises(ValueError):
            self.geometry.physical_to_sampler(invalid)

    def test_independent_analytical_full_jacobian_and_prior_cancellation(self) -> None:
        z = np.linspace(-1.6, 1.7, 18)
        theta = self.geometry.sampler_to_physical(z)
        u = self.geometry.sampler_to_unit(z)
        root_low, root_high = self.prior.cn_bounds(theta[16])
        terms = []
        for i in range(18):
            if i == 17:
                terms.append(np.log(root_high - root_low))
            elif i < 8:
                terms.append(np.log(theta[i]) + np.log(np.log(self.prior.upper[i] / self.prior.lower[i])))
            else:
                terms.append(np.log(self.prior.upper[i] - self.prior.lower[i]))
        expected = sum(terms) + np.sum(np.log(u) + np.log1p(-u))
        observed = self.geometry.log_abs_det_dphysical_dsampler(z)
        self.assertTrue(np.isclose(observed, expected, rtol=1e-12, atol=1e-10))
        self.assertLessEqual(abs(float(self.prior.log_density(theta)) + observed
                                 - np.sum(np.log(u) + np.log1p(-u))), 1e-9)
        # The C:N Jacobian is triangular: derivative of frootcn w.r.t. leafcn
        # does not change the determinant's diagonal product.
        eps = 1e-6
        numerical = np.zeros((18, 18))
        for i in range(18):
            plus = z.copy(); plus[i] += eps
            minus = z.copy(); minus[i] -= eps
            numerical[:, i] = (self.geometry.sampler_to_physical(plus)
                               - self.geometry.sampler_to_physical(minus)) / (2 * eps)
        self.assertAlmostEqual(float(np.linalg.slogdet(numerical)[1]), observed, delta=1e-6)

    def test_active_conditional_cn_branch_and_triangular_jacobian(self) -> None:
        unit = np.full(18, 0.5)
        unit[16] = 0.996
        theta = self.prior.inverse_unit(unit)
        self.assertGreater(theta[16], 39.5)
        low, high = self.prior.cn_bounds(theta[16])
        self.assertEqual(float(low), theta[16] + 0.5)
        self.assertLess(theta[17], high)
        z = self.geometry.physical_to_sampler(theta)
        np.testing.assert_allclose(self.geometry.sampler_to_physical(z), theta, rtol=1e-12, atol=0)
        observed = float(self.geometry.log_abs_det_dphysical_dsampler(z))
        u = self.geometry.sampler_to_unit(z)
        self.assertLessEqual(abs(self.prior.log_density(theta) + observed
                                 - float(np.sum(np.log(u) + np.log1p(-u)))), 1e-9)
        eps = 1e-6
        plus = z.copy(); plus[16] += eps
        minus = z.copy(); minus[16] -= eps
        derivative = (self.geometry.sampler_to_physical(plus)
                      - self.geometry.sampler_to_physical(minus)) / (2 * eps)
        self.assertAlmostEqual(float(derivative[17] / derivative[16]), 0.5, delta=1e-8)

    def test_boundary_saturation_and_no_clipping(self) -> None:
        with self.assertRaises(CoordinateSaturation):
            self.geometry.sampler_to_physical(np.full(18, 1000.0))
        with self.assertRaises(CoordinateSaturation):
            self.geometry.sampler_to_physical(np.full(18, -1000.0))
        # Exact physical endpoints are outside the open PPE1 support. Saturation
        # refers to an interior unit coordinate rounding onto an endpoint.
        with self.assertRaisesRegex(ValueError, "outside PPE1 support"):
            self.geometry.physical_to_sampler(self.prior.inverse_unit(np.zeros(18)))
        with self.assertRaises(ValueError):
            self.geometry.sampler_to_physical(np.full(18, np.nan))
        original = self.prior.inverse_unit
        def bad_map(_prior, unit):
            mapped = np.asarray(original(unit), dtype=float).copy()
            mapped[0] = self.prior.lower[0] - 0.01
            return mapped
        with patch.object(Prior18, "inverse_unit", bad_map):
            with self.assertRaisesRegex(RuntimeError, "escaped PPE1 marginal bounds"):
                self.geometry.sampler_to_physical(np.zeros(18))
        def rounded_map(_prior, unit):
            mapped = np.asarray(original(unit), dtype=float).copy()
            mapped[0] = self.prior.lower[0]
            return mapped
        with patch.object(Prior18, "inverse_unit", rounded_map):
            with self.assertRaises(CoordinateSaturation):
                self.geometry.sampler_to_physical(np.zeros(18))

    def test_density_components_scalar_batch_and_invalid_row_isolation(self) -> None:
        geometry = self.geometry
        prior = self.prior
        class Fixture:
            sampling_geometry = geometry
            sampling_coordinate_system = COORDINATE_SYSTEM_ID
            def __init__(self):
                self.prior = prior
            def evaluate_batch(self, theta):
                values = []
                for row in theta:
                    lp = float(prior.log_density(row))
                    values.append(PosteriorResult(
                        site="ABBY", prior_id=PPE1, gpp_resolution="daily", sr_resolution="daily",
                        cn_observation_cv=0.3, include_cn=True, log_prior=lp,
                        log_likelihood_gpp=-3., log_likelihood_sr=-5., log_likelihood_cn=-7.,
                        log_posterior=lp-15., n_gpp=1, n_sr=1, surrogate_evaluated=True,
                        gpp_raw_min=0., evaluation_error=None, provenance={},
                    ))
                return values
            def evaluate(self, theta):
                return self.evaluate_batch(np.asarray(theta, dtype=float)[None, :])[0]
            def _invalid_result(self, log_prior, *, reason="outside_prior_support"):
                return PosteriorResult(
                    site="ABBY", prior_id=PPE1, gpp_resolution="daily", sr_resolution="daily",
                    cn_observation_cv=0.3, include_cn=True, log_prior=log_prior,
                    log_likelihood_gpp=0., log_likelihood_sr=0., log_likelihood_cn=0.,
                    log_posterior=-np.inf, n_gpp=1, n_sr=1, surrogate_evaluated=False,
                    gpp_raw_min=None, evaluation_error=reason, provenance={},
                )
        fixture = Fixture()
        z = np.array([np.zeros(18), np.full(18, 1000.), np.linspace(-1, 1, 18)])
        batch = ThreeStagePosterior.evaluate_sampling_batch(fixture, z)
        self.assertEqual(batch[1].physical.evaluation_error, "coordinate_saturation")
        for index in (0, 2):
            scalar = ThreeStagePosterior.evaluate_sampling(fixture, z[index])
            self.assertEqual(scalar.log_sampling_posterior, batch[index].log_sampling_posterior)
            u = geometry.sampler_to_unit(z[index])
            self.assertLessEqual(abs(batch[index].log_sampling_posterior
                                     - (-15. + float(np.sum(np.log(u) + np.log1p(-u))))), 1e-9)
        class BadGeometry:
            def sampler_to_physical(self, _):
                raise RuntimeError("unexpected implementation failure")
        fixture.sampling_geometry = BadGeometry()
        with self.assertRaisesRegex(RuntimeError, "unexpected implementation failure"):
            ThreeStagePosterior.evaluate_sampling_batch(fixture, z[:1])

    def test_new_sampler_identity_cannot_use_legacy_posterior(self) -> None:
        payload = {
            "site": "ABBY", "prior_id": PPE1, "parameter_names": list(self.prior.names),
            "posterior_target_sha256": "1" * 64, "pool_sha256": "2" * 64,
            "walker_sha256": "3" * 64, "emcee_version": "3.1.6",
            "move_configuration": {}, "seed": 1, "nwalkers": 64, "ndim": 18,
            "coordinate_system_id": COORDINATE_SYSTEM_ID,
            "geometry_source_sha256": "4" * 64, "release_manifest_sha256": "5" * 64,
            "walker_coordinates_sha256": "6" * 64,
            "sampler_source_sha256": "7" * 64, "posterior_source_sha256": "8" * 64,
            "execution_checksum_manifest_sha256": "9" * 64,
        }
        normalized, _ = sampler_identity(payload)
        self.assertEqual(normalized["schema"], "mcmc-three-stage-sampler-identity-v2")
        with tempfile.TemporaryDirectory() as tmp:
            fake = SimpleNamespace(prior=self.prior)
            with self.assertRaisesRegex(ValueError, "coordinate identity"):
                run_sampler_block(posterior=fake,
                                  initial_sampler_coordinates=np.zeros((64, 18)),
                                  run_directory=Path(tmp) / "old", identity=payload,
                                  target_iteration=1)
        changed = dict(payload)
        changed["sampler_source_sha256"] = "a" * 64
        self.assertNotEqual(sampler_identity(payload)[1], sampler_identity(changed)[1])


if __name__ == "__main__":
    unittest.main()
