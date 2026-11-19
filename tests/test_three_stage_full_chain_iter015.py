from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_data import TARGETS, ThreeStageSnapshot
from model_ELM.three_stage_gpp import FEATURE_COUNT as GPP_FEATURE_COUNT, FORCING_NAMES, feature_names as gpp_feature_names
from model_ELM.three_stage_inference import FoldThreeStageInference
from model_ELM.three_stage_sr import FEATURE_COUNT as SR_FEATURE_COUNT, feature_names as sr_feature_names


ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
CONFIG = ROOT / "development/three_stage_surrogate/slurm/iter015/iter015_config.json"


class IdentityScaler:
    def transform(self, values):
        return np.asarray(values)

    def inverse_transform(self, values):
        return np.asarray(values)


class ConstantModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, values):
        return np.full(np.asarray(values).shape[0], self.value, dtype=np.float64)


class GPPFixtureModel:
    def predict(self, values):
        matrix = np.asarray(values, dtype=np.float64)
        return matrix[:, 1] - 100.0


class SRFixtureModel:
    def predict(self, values):
        return np.asarray(values, dtype=np.float64)[:, -1]


class Iter015InferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.snapshot = ThreeStageSnapshot(cls.config["snapshot_root"], verify_component_hashes=False)
        cls.members = list(cls.snapshot.development_ranked[:2])
        cls.parameters = cls.snapshot._parameter_values(cls.members)
        cls.spinup = {
            "schema": "three-stage-spinup-fold-artifact-v1",
            "split_id": 0,
            "feature_names": list(cls.snapshot.feature_names),
            "train_member_ids": cls.members,
            "fixed_test_access": False,
            "models": {target: ConstantModel(np.log(100.0 + index)) for index, target in enumerate(TARGETS)},
            "x_scalers": {target: IdentityScaler() for target in TARGETS},
            "y_scalers": {target: IdentityScaler() for target in TARGETS},
        }
        cls.gpp = {
            "schema": "three-stage-gpp-fold-artifact-v1",
            "split_id": 0,
            "feature_names": list(gpp_feature_names(cls.snapshot)),
            "train_member_ids": cls.members,
            "fixed_test_access": False,
            "model": GPPFixtureModel(),
            "x_mean": np.zeros(GPP_FEATURE_COUNT),
            "x_scale": np.ones(GPP_FEATURE_COUNT),
            "y_mean": 0.0,
            "y_scale": 1.0,
        }
        cls.sr = {
            "schema": "three-stage-sr-fold-artifact-v1",
            "split_id": 0,
            "feature_names": list(sr_feature_names(cls.snapshot)),
            "train_member_ids": cls.members,
            "fixed_test_access": False,
            "gpp_output_policy": "hard_zero_v1",
            "model": SRFixtureModel(),
            "x_mean": np.zeros(SR_FEATURE_COUNT),
            "x_scale": np.ones(SR_FEATURE_COUNT),
            "y_mean": 0.0,
            "y_scale": 1.0,
        }
        cls.engine = FoldThreeStageInference(
            cls.snapshot, cls.spinup, cls.gpp, cls.sr, split_id=0,
            gpp_output_policy="hard_zero_v1",
        )

    def forcing(self, hours: int):
        with Dataset(str(self.snapshot.root / "sites/ABBY/input_data_v1.nc"), "r") as dataset:
            values = {name: np.asarray(dataset.variables[name][:hours], dtype=np.float64) for name in FORCING_NAMES}
            time = np.asarray(dataset.variables["time"][:hours], dtype=np.int64)
        return values, time

    def test_config_and_feature_contract(self) -> None:
        self.assertEqual(self.config["gpp_output_policy"], "hard_zero_v1")
        self.assertFalse(self.config["fixed_test_allowed"])
        self.assertEqual(len(self.gpp["feature_names"]), 43)
        self.assertEqual(len(self.sr["feature_names"]), 44)

    def test_gate_precedes_sr(self) -> None:
        forcing, time = self.forcing(48)
        result = self.engine.predict(
            self.parameters[:1], site="ABBY", forcing=forcing, time=time,
            start=0, end=48, member_chunk=1,
        )
        np.testing.assert_array_equal(result.gpp, np.maximum(result.gpp_raw, 0.0))
        np.testing.assert_allclose(result.sr, result.gpp, rtol=0.0, atol=0.0)
        self.assertTrue(np.any(result.gpp_raw < 0.0))
        self.assertTrue(np.all(result.gpp >= 0.0))
        self.assertEqual(result.provenance["gpp_output_policy"], "hard_zero_v1")

    def test_memory_bounded_chunk_replay(self) -> None:
        forcing, time = self.forcing(48)
        one = self.engine.predict(
            self.parameters, site="ABBY", forcing=forcing, time=time,
            start=0, end=48, member_chunk=1,
        )
        two = self.engine.predict(
            self.parameters, site="ABBY", forcing=forcing, time=time,
            start=0, end=48, member_chunk=2,
        )
        np.testing.assert_allclose(one.gpp_raw, two.gpp_raw, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(one.gpp, two.gpp, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(one.sr, two.sr, rtol=1e-6, atol=1e-6)


if __name__ == "__main__":
    unittest.main()
