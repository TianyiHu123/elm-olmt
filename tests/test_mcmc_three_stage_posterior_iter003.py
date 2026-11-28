from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

from model_ELM.mcmc_coupled_adapter import (
    CONSUMED_RELEASE_FILES,
    EXPECTED_CATALOG_SHA256 as SURROGATE_CATALOG,
    EXPECTED_RELEASE_MANIFEST_SHA256 as SURROGATE_MANIFEST,
    EXPECTED_SNAPSHOT_SHA256,
)
from model_ELM.mcmc_geometry import CoordinateTransform
from model_ELM.mcmc_prior import PPE1, PPE2, Prior18
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA as OBS_CONFIG_SCHEMA,
    ObservationReleaseConfig,
)
from model_ELM.mcmc_three_stage_posterior import load_three_stage_posterior
from model_ELM.mcmc_three_stage_release import (
    CONFIG_SCHEMA as RELEASE_CONFIG_SCHEMA,
    IMPLEMENTATION_ID,
    ThreeStageReleaseConfig,
    load_three_stage_release,
)


PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")
PPE2_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe2_vertc/params")
SNAPSHOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data")
RELEASE = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc/release_0001")
UNCERTAINTY = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/handoff")
OBSERVATIONS = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001")
OBS_CATALOG = "cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8"
OBS_MANIFEST = "460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2"
EXPECTED_VALIDATION_SHA256 = "19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef"
SOURCE = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc/model_ELM/three_stage_coupled_release.py")


def release_configuration(prior_id=PPE1):
    return ThreeStageReleaseConfig(
        schema=RELEASE_CONFIG_SCHEMA,
        implementation_id=IMPLEMENTATION_ID,
        prior_id=prior_id,
        release_id="release_0001",
        release_root=RELEASE,
        snapshot_root=SNAPSHOT,
        uncertainty_root=UNCERTAINTY,
        uncertainty_handoff_sha256=CONSUMED_RELEASE_FILES["uncertainty/uncertainty_handoff.json"][1],
        uncertainty_manifest_sha256=CONSUMED_RELEASE_FILES["uncertainty/products_manifest.json"][1],
        uncertainty_validation_sha256=CONSUMED_RELEASE_FILES["uncertainty/final_validation_report.json"][1],
        source_file=SOURCE,
        release_manifest_sha256=SURROGATE_MANIFEST,
        catalog_sha256=SURROGATE_CATALOG,
        snapshot_sha256=EXPECTED_SNAPSHOT_SHA256,
    )


def observation_configuration():
    return ObservationReleaseConfig(
        schema=OBS_CONFIG_SCHEMA,
        release_root=OBSERVATIONS,
        snapshot_root=SNAPSHOT,
        catalog_sha256=OBS_CATALOG,
        release_manifest_sha256=OBS_MANIFEST,
        validation_report_sha256=EXPECTED_VALIDATION_SHA256,
        snapshot_sha256=EXPECTED_SNAPSHOT_SHA256,
    )


class ThreeStagePosteriorTests(unittest.TestCase):
    def test_all_resolutions_components_batch_and_sampler(self):
        prior = Prior18.from_directory(PPE1, PPE1_ROOT)
        theta = prior.inverse_unit(np.full(18, 0.5))
        second = prior.inverse_unit(np.linspace(0.2, 0.8, 18))
        batch = np.vstack((theta, second))
        for site, start in (("ABBY", 24408), ("JERC", 2784)):
            for gpp_resolution, sr_resolution in (
                ("daily", "daily"), ("hourly", "hourly"),
                ("daily", "hourly"), ("hourly", "daily"),
            ):
                with self.subTest(site=site, gpp=gpp_resolution, sr=sr_resolution):
                    posterior = load_three_stage_posterior(
                        site=site, prior_id=PPE1, prior_root=PPE1_ROOT,
                        surrogate_release=release_configuration(),
                        observation_release=observation_configuration(),
                        gpp_resolution=gpp_resolution, sr_resolution=sr_resolution,
                        cn_observation_cv=0.30, include_cn=True,
                        start=start, end=start + 48, member_chunk=2,
                    )
                    scalar = posterior.evaluate(theta)
                    repeated = posterior.evaluate(theta)
                    batched = posterior.evaluate_batch(batch)
                    self.assertTrue(scalar.surrogate_evaluated)
                    self.assertEqual(scalar.log_posterior, repeated.log_posterior)
                    self.assertTrue(np.isclose(scalar.log_posterior,
                        scalar.log_prior + scalar.log_likelihood_gpp + scalar.log_likelihood_sr
                        + scalar.log_likelihood_cn, rtol=0.0, atol=1e-10))
                    self.assertTrue(np.isclose(scalar.log_posterior, batched[0].log_posterior,
                                               rtol=1e-12, atol=1e-10))
                    sampler = prior.coordinate_transform.physical_to_sampler(theta)
                    sampling = posterior.evaluate_sampling(sampler)
                    self.assertTrue(np.isclose(
                        sampling.log_sampling_posterior,
                        scalar.log_posterior + sampling.log_abs_det_jacobian,
                        rtol=1e-12, atol=1e-10,
                    ))

    def test_flux_only_invalid_support_and_malformed_input(self):
        prior = Prior18.from_directory(PPE1, PPE1_ROOT)
        posterior = load_three_stage_posterior(
            site="ABBY", prior_id=PPE1, prior_root=PPE1_ROOT,
            surrogate_release=release_configuration(), observation_release=observation_configuration(),
            include_cn=False, start=24408, end=24456,
        )
        theta = prior.inverse_unit(np.full(18, 0.5))
        valid = posterior.evaluate(theta)
        self.assertEqual(valid.log_likelihood_cn, 0.0)
        invalid = theta.copy(); invalid[17] = invalid[16]
        rejected = posterior.evaluate(invalid)
        self.assertEqual(rejected.log_posterior, -np.inf)
        self.assertFalse(rejected.surrogate_evaluated)
        self.assertEqual(rejected.log_likelihood_gpp, 0.0)
        mixed = posterior.evaluate_batch(np.vstack((theta, invalid, theta)))
        self.assertEqual(len(mixed), 3)
        self.assertTrue(mixed[0].surrogate_evaluated)
        self.assertFalse(mixed[1].surrogate_evaluated)
        self.assertTrue(mixed[2].surrogate_evaluated)
        self.assertEqual(mixed[0].log_posterior, mixed[2].log_posterior)
        with self.assertRaises(ValueError):
            posterior.evaluate(theta[:-1])

        original = posterior.release.engine.predict
        valid_inference = original(theta, site="ABBY", forcing=posterior.forcing,
                                   time=posterior.time, start=posterior.start, end=posterior.end,
                                   member_chunk=posterior.member_chunk)
        invalid_inference = SimpleNamespace(
            totsomc=np.asarray([-1.0]), totsomn=valid_inference.totsomn,
            gpp_raw=valid_inference.gpp_raw, gpp=valid_inference.gpp, sr=valid_inference.sr,
            provenance=valid_inference.provenance,
        )
        cn_posterior = load_three_stage_posterior(
            site="ABBY", prior_id=PPE1, prior_root=PPE1_ROOT,
            surrogate_release=release_configuration(), observation_release=observation_configuration(),
            include_cn=True, start=24408, end=24456,
        )
        with mock.patch.object(cn_posterior.release.engine, "predict", return_value=invalid_inference):
            nonpositive = cn_posterior.evaluate(theta)
        self.assertEqual(nonpositive.log_posterior, -np.inf)
        self.assertEqual(nonpositive.evaluation_error, "nonpositive_or_nonfinite_cn_prediction")
        self.assertTrue(nonpositive.surrogate_evaluated)

    def test_ppe2_and_incompatible_configuration_fail_before_prediction(self):
        ppe2 = Prior18.from_directory(PPE2, PPE2_ROOT)
        with self.assertRaises(ValueError):
            load_three_stage_release(prior=ppe2, config=release_configuration(prior_id=PPE2))
        with self.assertRaisesRegex(ValueError, "prior/release incompatibility"):
            load_three_stage_release(prior=ppe2, config=release_configuration())
        bad = release_configuration()
        bad = ThreeStageReleaseConfig(**{**bad.__dict__, "uncertainty_handoff_sha256": "0" * 64})
        with self.assertRaisesRegex(ValueError, "uncertainty handoff"):
            load_three_stage_release(prior=Prior18.from_directory(PPE1, PPE1_ROOT), config=bad)

    def test_legacy_coupling_pipeline_daily_map_remains_available(self):
        from model_ELM.coupling_pipeline import build_daily_index_map

        timestamps = np.arange("2020-01-01T00", "2020-01-03T00", dtype="datetime64[h]")
        observations = np.arange(48, dtype=np.float64)
        errors = np.full(48, 0.5)
        result = build_daily_index_map(timestamps, observations, errors)
        self.assertEqual(result["daily_count"], 2)
        self.assertEqual(len(result["groups"]), 2)

    def test_legacy_mcmc_forcing_geometry_and_jacobian_remain_available(self):
        transform = CoordinateTransform.from_parameters(
            ["k_l1", "rf_leaf", "parm_0", "sigma_SR"],
            [0.01, 0.0, -1.0, 0.0],
            [10.0, 1.0, 1.0, 5.0],
            enabled=True,
        )
        physical_batch = np.array([[0.1, 0.2, 0.0, 1.0], [2.0, 0.8, 0.7, 3.0]])
        recovered = transform.sampler_to_physical(transform.physical_to_sampler(physical_batch))
        np.testing.assert_allclose(recovered, physical_batch, rtol=0.0, atol=1.0e-12)
        self.assertEqual(transform.metadata()["transform_kinds"],
                         ["log", "logit", "physical", "logit"])
        with self.assertRaisesRegex(ValueError, "strictly within bounds"):
            transform.physical_to_sampler(np.array([0.01, 0.2, 0.0, 1.0]))
        with self.assertRaisesRegex(ValueError, "finite"):
            transform.sampler_to_physical(np.array([np.nan, 0.0, 0.0, 0.0]))

        physical = np.array([0.2, 0.3, 0.1, 2.0])
        sampler = transform.physical_to_sampler(physical)
        epsilon = 1.0e-6
        numerical = []
        for index in range(sampler.size):
            plus = sampler.copy()
            minus = sampler.copy()
            plus[index] += epsilon
            minus[index] -= epsilon
            derivative = (
                transform.sampler_to_physical(plus)[index]
                - transform.sampler_to_physical(minus)[index]
            ) / (2.0 * epsilon)
            numerical.append(np.log(abs(derivative)))
        analytic = transform.log_abs_det_dphysical_dsampler(sampler)
        self.assertTrue(np.isclose(sum(numerical), analytic, rtol=0.0, atol=1.0e-6))

        forcing_module = importlib.import_module("model_ELM.MCMC_forcing")
        with mock.patch.object(
            forcing_module,
            "log_posterior_forcing",
            side_effect=lambda values: -float(np.dot(values, values)),
        ), mock.patch.object(
            forcing_module,
            "_WORKER_STATE",
            {"coordinate_transform": transform},
        ):
            physical_target = forcing_module.log_posterior_forcing(physical)
            sampler_target = forcing_module.log_posterior_forcing_sampler(sampler)
        self.assertTrue(np.isclose(
            sampler_target - analytic,
            physical_target,
            rtol=0.0,
            atol=1.0e-12,
        ))


if __name__ == "__main__":
    unittest.main()
