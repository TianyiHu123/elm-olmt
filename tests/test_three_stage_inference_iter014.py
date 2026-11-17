from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_gpp import FORCING_NAMES
from model_ELM.three_stage_inference import FrozenThreeStageInference, read_result, write_result


class FrozenInferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = os.environ.get(
            "ITER014_CONFIG",
            "/xdisk/chopinsong/tianyihu/elm-olmt/development/three_stage_surrogate/slurm/iter014/iter014_config.json",
        )
        cls.engine = FrozenThreeStageInference.from_json(config)
        cls.config = cls.engine.config
        cls.parameters = cls.engine.snapshot._parameter_values(("g00314",))
        cls.site_path = cls.engine.snapshot.root / "sites" / "ABBY" / "input_data_v1.nc"

    def _forcing(self, end: int) -> tuple[dict[str, np.ndarray], np.ndarray]:
        with Dataset(str(self.site_path), "r") as dataset:
            forcing = {name: np.asarray(dataset.variables[name][:end], dtype=np.float64) for name in FORCING_NAMES}
            time = np.asarray(dataset.variables["time"][:end], dtype=np.int64)
        return forcing, time

    def test_parameter_and_site_contract_rejects_invalid_inputs(self) -> None:
        valid = self.engine.validate_parameters(self.parameters)
        self.assertEqual(valid.shape, (1, 18))
        with self.assertRaises(ValueError):
            self.engine.validate_parameters(np.zeros(17))
        invalid = valid.copy()
        invalid[0, 0] = self.engine.lower[0] / 2.0
        with self.assertRaises(ValueError):
            self.engine.validate_parameters(invalid)
        invalid = valid.copy()
        invalid[0, 16] = 40.0
        invalid[0, 17] = 40.0
        with self.assertRaises(ValueError):
            self.engine.validate_parameters(invalid)
        forcing, time = self._forcing(768)
        with self.assertRaises(ValueError):
            self.engine.predict(self.parameters, site="OSBS", forcing=forcing, time=time, start=720, end=768)
        with self.assertRaises(ValueError):
            self.engine.predict(self.parameters, site="ABBY", forcing=forcing, time=time, start=719, end=768)

    def test_published_replay_chunking_and_serialization(self) -> None:
        forcing, time = self._forcing(768)
        direct = self.engine.predict(self.parameters, site="ABBY", forcing=forcing, time=time, start=720, end=768)
        chunked = self.engine.predict(
            self.parameters, site="ABBY", forcing=forcing, time=time, start=720, end=768, chunk_rows=7
        )
        np.testing.assert_allclose(chunked.totsomc, direct.totsomc, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(chunked.totsomn, direct.totsomn, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(chunked.gpp, direct.gpp, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(chunked.sr, direct.sr, rtol=1e-6, atol=1e-6)
        with Dataset(self.config["predicted_cn_handoff"], "r") as dataset:
            np.testing.assert_allclose(direct.totsomc, dataset.variables["TOTSOMC_predicted"][0, 0], rtol=self.config["handoff_replay_rtol"], atol=self.config["handoff_replay_atol"])
            np.testing.assert_allclose(direct.totsomn, dataset.variables["TOTSOMN_predicted"][0, 0], rtol=self.config["handoff_replay_rtol"], atol=self.config["handoff_replay_atol"])
        with Dataset(self.config["predicted_gpp_handoff"], "r") as dataset:
            np.testing.assert_allclose(direct.gpp[0], dataset.variables["GPP_predicted"][0, 0, 720:768], rtol=self.config["handoff_replay_rtol"], atol=self.config["handoff_replay_atol"])
        with Dataset(self.config["predicted_sr_handoff"], "r") as dataset:
            np.testing.assert_allclose(direct.sr[0], dataset.variables["SR_predicted"][0, 0, 720:768], rtol=self.config["handoff_replay_rtol"], atol=self.config["handoff_replay_atol"])
        self.assertFalse(direct.provenance["contains_elm_truth"])
        self.assertFalse(direct.provenance["fixed_test_access"])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.nc"
            write_result(path, direct)
            loaded = read_result(path)
            np.testing.assert_allclose(loaded.parameters, direct.parameters, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(loaded.time, direct.time, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(loaded.totsomc, direct.totsomc, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(loaded.totsomn, direct.totsomn, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(loaded.gpp, direct.gpp, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(loaded.sr, direct.sr, rtol=0.0, atol=0.0)
            self.assertEqual(loaded.parameter_names, direct.parameter_names)
            self.assertEqual(loaded.site, direct.site)
            self.assertEqual(loaded.provenance, direct.provenance)


if __name__ == "__main__":
    unittest.main()
