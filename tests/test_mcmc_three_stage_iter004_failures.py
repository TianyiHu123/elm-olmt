from __future__ import annotations

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
from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA as OBS_CONFIG_SCHEMA,
    ObservationReleaseConfig,
)
from model_ELM.mcmc_three_stage_posterior import load_three_stage_posterior
from model_ELM.mcmc_three_stage_release import (
    CONFIG_SCHEMA as RELEASE_CONFIG_SCHEMA,
    IMPLEMENTATION_ID,
    ThreeStageReleaseConfig,
)


PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")
SNAPSHOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data")
RELEASE = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc/release_0001")
UNCERTAINTY = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/handoff")
OBSERVATIONS = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001")
OBS_CATALOG = "cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8"
OBS_MANIFEST = "460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2"
EXPECTED_VALIDATION_SHA256 = "19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef"
SOURCE = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc/model_ELM/three_stage_coupled_release.py")


def release_configuration():
    return ThreeStageReleaseConfig(
        schema=RELEASE_CONFIG_SCHEMA, implementation_id=IMPLEMENTATION_ID, prior_id=PPE1,
        release_id="release_0001", release_root=RELEASE, snapshot_root=SNAPSHOT,
        uncertainty_root=UNCERTAINTY,
        uncertainty_handoff_sha256=CONSUMED_RELEASE_FILES["uncertainty/uncertainty_handoff.json"][1],
        uncertainty_manifest_sha256=CONSUMED_RELEASE_FILES["uncertainty/products_manifest.json"][1],
        uncertainty_validation_sha256=CONSUMED_RELEASE_FILES["uncertainty/final_validation_report.json"][1],
        source_file=SOURCE, release_manifest_sha256=SURROGATE_MANIFEST,
        catalog_sha256=SURROGATE_CATALOG, snapshot_sha256=EXPECTED_SNAPSHOT_SHA256,
    )


def observation_configuration():
    return ObservationReleaseConfig(
        schema=OBS_CONFIG_SCHEMA, release_root=OBSERVATIONS, snapshot_root=SNAPSHOT,
        catalog_sha256=OBS_CATALOG, release_manifest_sha256=OBS_MANIFEST,
        validation_report_sha256=EXPECTED_VALIDATION_SHA256,
        snapshot_sha256=EXPECTED_SNAPSHOT_SHA256,
    )


class Iter004FailureClassificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prior = Prior18.from_directory(PPE1, PPE1_ROOT)
        self.theta = self.prior.inverse_unit(np.full(18, 0.5))
        self.posterior = load_three_stage_posterior(
            site="ABBY", prior_id=PPE1, prior_root=PPE1_ROOT,
            surrogate_release=release_configuration(), observation_release=observation_configuration(),
            include_cn=True, start=24408, end=24456, member_chunk=2,
        )
        self.valid = self.posterior.release.engine.predict(
            self.theta, site="ABBY", forcing=self.posterior.forcing, time=self.posterior.time,
            start=self.posterior.start, end=self.posterior.end,
            member_chunk=self.posterior.member_chunk,
        )

    def _inference(self, **overrides):
        payload = {
            "totsomc": self.valid.totsomc.copy(), "totsomn": self.valid.totsomn.copy(),
            "gpp_raw": self.valid.gpp_raw.copy(), "gpp": self.valid.gpp.copy(),
            "sr": self.valid.sr.copy(), "provenance": self.valid.provenance,
        }
        payload.update(overrides)
        return SimpleNamespace(**payload)

    def test_recognized_nonfinite_flux_predictions_are_row_local_rejections(self) -> None:
        gpp = self.valid.gpp.copy(); gpp[0, 0] = np.nan
        with mock.patch.object(self.posterior.release.engine, "predict", return_value=self._inference(gpp=gpp)):
            result = self.posterior.evaluate(self.theta)
        self.assertEqual(result.log_posterior, -np.inf)
        self.assertEqual(result.evaluation_error, "nonfinite_gpp_prediction")
        sr = self.valid.sr.copy(); sr[0, 0] = np.inf
        with mock.patch.object(self.posterior.release.engine, "predict", return_value=self._inference(sr=sr)):
            result = self.posterior.evaluate(self.theta)
        self.assertEqual(result.log_posterior, -np.inf)
        self.assertEqual(result.evaluation_error, "nonfinite_sr_prediction")

    def test_unexpected_surrogate_errors_fail_closed(self) -> None:
        with mock.patch.object(self.posterior.release.engine, "predict", side_effect=RuntimeError("injected")):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                self.posterior.evaluate(self.theta)
        with mock.patch.object(self.posterior.release.engine, "predict", side_effect=ValueError("injected")):
            with self.assertRaisesRegex(ValueError, "injected"):
                self.posterior.evaluate_batch(np.vstack((self.theta, self.theta)))

    def test_sampling_batch_matches_scalar_and_preserves_invalid_row(self) -> None:
        second = self.prior.inverse_unit(np.linspace(0.2, 0.8, 18))
        physical = np.vstack((self.theta, second))
        sampler = self.prior.coordinate_transform.physical_to_sampler(physical)
        sampler_with_invalid = np.vstack((sampler[0], sampler[1], sampler[0]))
        sampler_with_invalid[1, 0] = 1000.0
        isolated = self.posterior.evaluate_sampling_batch(sampler_with_invalid)
        self.assertTrue(np.isfinite(isolated[0].log_sampling_posterior))
        self.assertEqual(isolated[1].log_sampling_posterior, -np.inf)
        self.assertEqual(isolated[1].physical.evaluation_error, "outside_prior_support")
        self.assertFalse(isolated[1].physical.surrogate_evaluated)
        self.assertEqual(isolated[0].log_sampling_posterior, isolated[2].log_sampling_posterior)
        batch = self.posterior.evaluate_sampling_batch(sampler)
        scalar = [self.posterior.evaluate_sampling(row) for row in sampler]
        self.assertEqual([item.log_sampling_posterior for item in batch],
                         [item.log_sampling_posterior for item in scalar])


if __name__ == "__main__":
    unittest.main()
