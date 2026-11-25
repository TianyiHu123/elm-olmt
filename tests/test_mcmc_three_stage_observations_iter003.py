from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import xarray as xr

from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA,
    EXPECTED_CATALOG_SHA256,
    EXPECTED_MANIFEST_SHA256,
    EXPECTED_VALIDATION_SHA256,
    ObservationReleaseConfig,
    _daily_operator,
    load_three_stage_observations,
)
from model_ELM.mcmc_coupled_adapter import EXPECTED_SNAPSHOT_SHA256


OBSERVATIONS = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001")
SNAPSHOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data")


def configuration(**changes):
    values = dict(
        schema=CONFIG_SCHEMA,
        release_root=OBSERVATIONS,
        snapshot_root=SNAPSHOT,
        catalog_sha256=EXPECTED_CATALOG_SHA256,
        release_manifest_sha256=EXPECTED_MANIFEST_SHA256,
        validation_report_sha256=EXPECTED_VALIDATION_SHA256,
        snapshot_sha256=EXPECTED_SNAPSHOT_SHA256,
    )
    values.update(changes)
    return ObservationReleaseConfig(**values)


class ThreeStageObservationTests(unittest.TestCase):
    def test_counts_alignment_units_and_read_only_arrays(self):
        expected = {
            "ABBY": {("GPP", "hourly"): 15437, ("GPP", "daily"): 514,
                     ("SR", "hourly"): 26264, ("SR", "daily"): 1095},
            "JERC": {("GPP", "hourly"): 19844, ("GPP", "daily"): 699,
                     ("SR", "hourly"): 51162, ("SR", "daily"): 2114},
        }
        for site in ("ABBY", "JERC"):
            with self.subTest(site=site):
                context = load_three_stage_observations(site=site, config=configuration())
                self.assertEqual(context.forcing_hours, 61320)
                for key, count in expected[site].items():
                    operator = context.operator(*key)
                    self.assertEqual(operator.count, count)
                    self.assertFalse(operator.observed.flags.writeable)
                    self.assertFalse(operator.observation_sigma.flags.writeable)
                    self.assertTrue(np.all(operator.observation_sigma > 0.0))
                self.assertEqual(tuple(context.soil_cn.covariance_by_cv), (0.2, 0.3, 0.5))
                self.assertTrue(np.all(context.soil_cn.observed_stocks > 0.0))
                with self.assertRaises(TypeError):
                    context.flux[("GPP", "hourly")] = context.operator("GPP", "hourly")
                with self.assertRaises(TypeError):
                    context.soil_cn.covariance_by_cv[0.3] = np.eye(2)

    def test_locked_benchmark_window_counts(self):
        windows = {
            "ABBY": (24408, {48: (36, 48, 1, 2), 720: (409, 718, 11, 30), 8760: (5124, 8756, 179, 365)}),
            "JERC": (2784, {48: (42, 48, 2, 2), 720: (294, 720, 10, 30), 8760: (573, 8711, 19, 362)}),
        }
        for site, (start, by_window) in windows.items():
            context = load_three_stage_observations(site=site, config=configuration())
            for hours, expected in by_window.items():
                end = start + hours
                observed = (
                    context.operator("GPP", "hourly").window(start, end).count,
                    context.operator("SR", "hourly").window(start, end).count,
                    context.operator("GPP", "daily").window(start, end).count,
                    context.operator("SR", "daily").window(start, end).count,
                )
                self.assertEqual(observed, expected)

    def test_invalid_configuration_and_site_fail_closed(self):
        with self.assertRaises(ValueError):
            load_three_stage_observations(site="OSBS", config=configuration())
        with self.assertRaisesRegex(ValueError, "configured observation catalog"):
            load_three_stage_observations(site="ABBY", config=configuration(catalog_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "configured observation validation"):
            load_three_stage_observations(site="ABBY", config=configuration(validation_report_sha256="0" * 64))

        site_root = OBSERVATIONS / "sites" / "ABBY"
        with xr.open_dataset(site_root / "flux_hourly.nc") as opened:
            hourly = opened.load()
        with xr.open_dataset(site_root / "flux_daily.nc") as opened:
            daily = opened.load()
        corrupted = daily.copy(deep=True)
        eligible = np.flatnonzero(corrupted.GPP_eligible.values == 1)[0]
        corrupted.GPP_valid_hour_count.values[eligible] += 1
        with self.assertRaisesRegex(ValueError, "valid-hour count"):
            _daily_operator(hourly, corrupted, "GPP", 0.5)


if __name__ == "__main__":
    unittest.main()
