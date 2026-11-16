import json
import pickle
import unittest
from pathlib import Path

import numpy as np

from model_ELM.three_stage_sr import FEATURE_COUNT, predict_artifact


ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")


class ConstantModel:
    def predict(self, values):
        return np.sum(values, axis=1)


class TestIter013Contract(unittest.TestCase):
    def test_frozen_configuration(self):
        payload = json.loads((ROOT / "development/three_stage_surrogate/slurm/iter013/sr_configuration.json").read_text())
        self.assertEqual(payload["selection_decision"], "deployable_arm_B_selected")
        self.assertEqual(payload["feature_count"], FEATURE_COUNT)
        self.assertEqual(payload["gpp_input"], "published_predicted_same_hour")
        self.assertEqual(payload["model_config"]["hidden_layer_sizes"], [96, 48])
        self.assertEqual(payload["model_config"]["activation"], "tanh")
        self.assertEqual(payload["model_config"]["alpha"], 0.01)

    def test_float32_standalone_scaler_arithmetic(self):
        artifact = {
            "model": ConstantModel(),
            "x_mean": np.linspace(-1, 1, FEATURE_COUNT, dtype=np.float64),
            "x_scale": np.linspace(1, 2, FEATURE_COUNT, dtype=np.float64),
            "y_mean": 2.0,
            "y_scale": 3.0,
        }
        raw = np.arange(FEATURE_COUNT * 3, dtype=np.float32).reshape(3, FEATURE_COUNT)
        scaled = raw.copy()
        scaled -= artifact["x_mean"].astype(np.float32)
        scaled /= artifact["x_scale"].astype(np.float32)
        expected = artifact["model"].predict(scaled) * 3.0 + 2.0
        np.testing.assert_array_equal(predict_artifact(artifact, raw), expected.astype(np.float64))
        restored = pickle.loads(pickle.dumps(artifact))
        np.testing.assert_array_equal(predict_artifact(restored, raw), expected.astype(np.float64))


if __name__ == "__main__":
    unittest.main()
