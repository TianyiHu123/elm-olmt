from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from model_ELM.mcmc_coupled_adapter import OUTPUT_UNITS, load_ppe1_coupled_release
from model_ELM.mcmc_prior import PPE1, PPE2, Prior18
from model_ELM.three_stage_gpp import FORCING_NAMES

PPE1_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params")
PPE2_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe2_vertc/params")
SNAPSHOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data")
RELEASE = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc/release_0001")
SOURCE = Path("model_ELM/three_stage_coupled_release.py")
UNCERTAINTY = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/handoff")


def read_forcing(site: str, end: int):
    with Dataset(str(SNAPSHOT / "sites" / site / "input_data_v1.nc"), "r") as dataset:
        forcing = {name: np.asarray(dataset.variables[name][:end], dtype=np.float64) for name in FORCING_NAMES}
        time = np.asarray(dataset.variables["time"][:end], dtype=np.int64)
    return forcing, time


class CoupledInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded = load_ppe1_coupled_release(
            prior=Prior18.from_directory(PPE1, PPE1_ROOT), release_root=RELEASE,
            snapshot_root=SNAPSHOT, source_file=SOURCE, uncertainty_root=UNCERTAINTY,
        )

    def test_target_free_sequential_replay_and_shapes(self):
        engine = self.loaded.engine
        parameters = engine.snapshot._parameter_values(engine.snapshot.development_ranked[:2])
        for site in ("ABBY", "JERC"):
            with self.subTest(site=site):
                forcing, time = read_forcing(site, 768)
                first = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=1)
                repeat = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=1)
                chunked = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=2)
                self.assertEqual(first.totsomc.shape, (2,)); self.assertEqual(first.totsomn.shape, (2,))
                self.assertEqual(first.gpp.shape, (2, 48)); self.assertEqual(first.gpp_raw.shape, (2, 48)); self.assertEqual(first.sr.shape, (2, 48))
                for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
                    np.testing.assert_array_equal(getattr(first, name), getattr(repeat, name))
                np.testing.assert_array_equal(first.gpp, np.maximum(first.gpp_raw, 0.0))
                for name in ("gpp_raw", "gpp", "sr"):
                    np.testing.assert_allclose(getattr(first, name), getattr(chunked, name), rtol=1e-6, atol=1e-6)
                self.assertTrue(np.all(np.isfinite(first.sr)))
                self.assertFalse(first.provenance["contains_elm_truth"]); self.assertFalse(first.provenance["training_or_fitting"])
        self.assertEqual(self.loaded.output_units, OUTPUT_UNITS)
        self.assertEqual(OUTPUT_UNITS, {"TOTSOMC": "gC/m^2", "TOTSOMN": "gN/m^2", "GPP": "gC/m^2/day", "SR": "gC/m^2/day"})
        self.assertEqual(set(self.loaded.unit_provenance), {"three_stage_spinup.py", "three_stage_gpp.py", "three_stage_sr.py", "three_stage_inference.py"})

    def test_invalid_inputs_and_incompatible_prior_are_rejected(self):
        engine = self.loaded.engine
        parameters = engine.snapshot._parameter_values(engine.snapshot.development_ranked[:1])
        forcing, time = read_forcing("ABBY", 768)
        invalid = parameters.copy(); invalid[0, 17] = invalid[0, 16]
        invalid_values = (invalid, np.full((1, 18), np.nan), parameters[:, :-1], np.where(np.arange(18) == 0, 99.0, parameters))
        for value in invalid_values:
            with self.assertRaises(ValueError):
                engine.validate_parameters(value)
        with self.assertRaises(ValueError):
            engine.predict(parameters, site="ABBY", forcing=forcing, time=time[:-1], start=720, end=768)
        with self.assertRaises(ValueError):
            engine.predict(parameters, site="OSBS", forcing=forcing, time=time, start=720, end=768)
        missing = dict(forcing); missing.pop(next(iter(missing)))
        with self.assertRaises((KeyError, ValueError)):
            engine.predict(parameters, site="ABBY", forcing=missing, time=time, start=720, end=768)
        nonfinite = {name: values.copy() for name, values in forcing.items()}; nonfinite[next(iter(nonfinite))][0] = np.nan
        with self.assertRaises(ValueError):
            engine.predict(parameters, site="ABBY", forcing=nonfinite, time=time, start=720, end=768)
        nonconsecutive = time.copy(); nonconsecutive[1] = 9
        with self.assertRaises(ValueError):
            engine.predict(parameters, site="ABBY", forcing=forcing, time=nonconsecutive, start=720, end=768)
        with self.assertRaises(ValueError):
            engine.predict(parameters, site="ABBY", forcing=forcing, time=time, start=1, end=768)
        with self.assertRaisesRegex(ValueError, "prior/release incompatibility"):
            load_ppe1_coupled_release(
                prior=Prior18.from_directory(PPE2, PPE2_ROOT), release_root=RELEASE,
                snapshot_root=SNAPSHOT, source_file=SOURCE, uncertainty_root=UNCERTAINTY,
            )


if __name__ == "__main__":
    unittest.main()
