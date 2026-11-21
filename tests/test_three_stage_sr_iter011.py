import hashlib
import unittest
from pathlib import Path
from unittest.mock import Mock

from development.three_stage_surrogate.slurm.iter010.iter010_common import FROZEN_OPTIMIZER
from development.three_stage_surrogate.slurm.iter011.iter011_common import PARAMETER_COUNTS, load_candidates
from model_ELM.three_stage_sr import FEATURE_COUNT, GPP_FEATURE_NAME, feature_names


class Iter011ContractTests(unittest.TestCase):
    def test_exact_candidate_inventory(self):
        path = Path("development/three_stage_surrogate/slurm/iter011/candidate_manifest.json").resolve()
        config = {"candidate_manifest": str(path), "candidate_manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        payload = load_candidates(config)
        self.assertEqual([row["candidate_id"] for row in payload["candidates"]], list("ABCDE"))
        self.assertEqual(payload["frozen_optimizer"], FROZEN_OPTIMIZER)
        self.assertEqual(PARAMETER_COUNTS, {"A": 9025, "B": 9025, "C": 14081, "D": 14081, "E": 14081})
        self.assertEqual(payload["production_fit_count"], 100)

    def test_feature_schema_appends_same_hour_gpp(self):
        snapshot = Mock(parameter_names=tuple(f"p{i}" for i in range(18)))
        names = feature_names(snapshot)
        self.assertEqual(len(names), FEATURE_COUNT)
        self.assertEqual(names[-1], GPP_FEATURE_NAME)
        self.assertEqual(len(set(names)), FEATURE_COUNT)


if __name__ == "__main__":
    unittest.main()
