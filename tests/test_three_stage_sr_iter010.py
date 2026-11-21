import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from development.three_stage_surrogate.slurm.iter010.iter010_common import FROZEN_OPTIMIZER, load_candidates
from model_ELM.three_stage_sr import FEATURE_COUNT, GPP_FEATURE_NAME, feature_names


class Iter010ContractTests(unittest.TestCase):
    def test_candidate_inventory_and_control(self):
        path = Path("development/three_stage_surrogate/slurm/iter010/candidate_manifest.json").resolve()
        config = {"candidate_manifest": str(path), "candidate_manifest_sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}
        payload = load_candidates(config)
        self.assertEqual(len(payload["candidates"]), 33)
        self.assertEqual(payload["candidates"][0], {"candidate_id": 0, "hidden_layer_sizes": [64, 32], "activation": "tanh", "alpha": 0.0001})
        self.assertEqual(payload["candidates"][32], {"candidate_id": 32, "hidden_layer_sizes": [128], "activation": "relu", "alpha": 10.0})
        self.assertEqual(payload["frozen_optimizer"], FROZEN_OPTIMIZER)

    def test_feature_schema_appends_same_hour_gpp(self):
        snapshot = Mock(parameter_names=tuple(f"p{i}" for i in range(18)))
        names = feature_names(snapshot)
        self.assertEqual(len(names), FEATURE_COUNT)
        self.assertEqual(names[-1], GPP_FEATURE_NAME)
        self.assertEqual(len(set(names)), FEATURE_COUNT)


if __name__ == "__main__":
    unittest.main()
