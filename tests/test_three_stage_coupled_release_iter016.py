from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_coupled_release import (
    CoupledThreeStageInference,
    GPP_SCHEMA,
    SPINUP_SCHEMA,
    SR_SCHEMA,
    load_artifacts,
    save_artifacts,
)
from model_ELM.three_stage_data import TARGETS, ThreeStageSnapshot, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES, feature_names as gpp_feature_names
from model_ELM.three_stage_sr import feature_names as sr_feature_names


SNAPSHOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data")


class IdentityScaler:
    def transform(self, values: np.ndarray) -> np.ndarray:
        return np.asarray(values)

    def inverse_transform(self, values: np.ndarray) -> np.ndarray:
        return np.asarray(values)


class ConstantModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, values: np.ndarray) -> np.ndarray:
        return np.full(np.asarray(values).shape[0], self.value, dtype=np.float64)


class LastFeatureModel:
    def predict(self, values: np.ndarray) -> np.ndarray:
        return np.asarray(values, dtype=np.float64)[:, -1] + 0.5


class CoupledReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = ThreeStageSnapshot(SNAPSHOT, verify_component_hashes=False)
        members = list(cls.snapshot.development_ranked)
        common = {
            "release_name": "release_0001",
            "snapshot_sha256": cls.snapshot.snapshot_sha256,
            "global_split_sha256": sha256_file(cls.snapshot.split_path),
            "training_member_ids": members,
            "upstream_prediction_mode": "direct_in_sample",
            "fixed_test_fit_access": False,
        }
        cls.spinup = {
            **common,
            "schema": SPINUP_SCHEMA,
            "feature_names": list(cls.snapshot.feature_names),
            "models": {target: ConstantModel(np.log(100.0 if target == "TOTSOMC" else 10.0)) for target in TARGETS},
            "x_scalers": {target: IdentityScaler() for target in TARGETS},
            "y_scalers": {target: IdentityScaler() for target in TARGETS},
        }
        cls.gpp = {
            **common,
            "schema": GPP_SCHEMA,
            "feature_names": list(gpp_feature_names(cls.snapshot)),
            "model": ConstantModel(-0.25),
            "x_mean": np.zeros(43),
            "x_scale": np.ones(43),
            "y_mean": 0.0,
            "y_scale": 1.0,
            "gpp_output_policy": "hard_zero_v1",
        }
        cls.sr = {
            **common,
            "schema": SR_SCHEMA,
            "feature_names": list(sr_feature_names(cls.snapshot)),
            "model": LastFeatureModel(),
            "x_mean": np.zeros(44),
            "x_scale": np.ones(44),
            "y_mean": 0.0,
            "y_scale": 1.0,
            "gpp_output_policy": "hard_zero_v1",
        }

    def test_round_trip_gate_and_chunk_consistency(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "artifact"
            saved = save_artifacts(
                directory, self.snapshot, self.spinup, self.gpp, self.sr,
                provenance={"iteration": "iter016", "role": "unit_test_fixture"},
            )
            spinup, gpp, sr, loaded = load_artifacts(directory, self.snapshot)
            self.assertEqual(saved, loaded)
            engine = CoupledThreeStageInference(self.snapshot, spinup, gpp, sr, loaded)
            parameters = self.snapshot._parameter_values(self.snapshot.development_ranked[:2])
            with Dataset(str(SNAPSHOT / "sites" / "ABBY" / "input_data_v1.nc"), "r") as dataset:
                forcing = {name: np.asarray(dataset.variables[name][:768], dtype=np.float64) for name in FORCING_NAMES}
                time = np.asarray(dataset.variables["time"][:768], dtype=np.int64)
            first = engine.predict(parameters, site="ABBY", forcing=forcing, time=time, start=720, end=768, member_chunk=1)
            second = engine.predict(parameters, site="ABBY", forcing=forcing, time=time, start=720, end=768, member_chunk=2)
            np.testing.assert_allclose(first.gpp_raw, -0.25, rtol=0.0, atol=0.0)
            np.testing.assert_array_equal(first.gpp, 0.0)
            np.testing.assert_allclose(first.sr, 0.5, rtol=0.0, atol=0.0)
            np.testing.assert_allclose(first.gpp_raw, second.gpp_raw, rtol=1e-6, atol=1e-6)
            np.testing.assert_allclose(first.gpp, second.gpp, rtol=1e-6, atol=1e-6)
            np.testing.assert_allclose(first.sr, second.sr, rtol=1e-6, atol=1e-6)
            self.assertFalse(first.provenance["contains_elm_truth"])
            self.assertEqual(first.provenance["training_member_count"], 819)

    def test_parameter_and_training_scope_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "artifact"
            save_artifacts(
                directory, self.snapshot, self.spinup, self.gpp, self.sr,
                provenance={"iteration": "iter016", "role": "unit_test_fixture"},
            )
            spinup, gpp, sr, manifest = load_artifacts(directory, self.snapshot)
            engine = CoupledThreeStageInference(self.snapshot, spinup, gpp, sr, manifest)
            values = self.snapshot._parameter_values(self.snapshot.development_ranked[:1])
            invalid = values.copy()
            invalid[0, 17] = invalid[0, 16]
            with self.assertRaises(ValueError):
                engine.validate_parameters(invalid)
            altered = dict(sr)
            altered["training_member_ids"] = list(self.snapshot.development_ranked[:-1]) + [self.snapshot.fixed_test_ranked[0]]
            with self.assertRaises(ValueError):
                CoupledThreeStageInference(self.snapshot, spinup, gpp, altered, manifest)
            for key, bad_value in (
                ("global_split_sha256", "0" * 64),
                ("training_partition", "fixed_test"),
                ("fixed_test_fit_access", True),
                ("gpp_output_policy", "raw"),
            ):
                corrupted = dict(manifest)
                corrupted[key] = bad_value
                with self.assertRaises(ValueError, msg=key):
                    CoupledThreeStageInference(self.snapshot, spinup, gpp, sr, corrupted)


if __name__ == "__main__":
    unittest.main()
