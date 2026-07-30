import hashlib
import unittest
from pathlib import Path

from development.spinup_surrogate.tools.analyze_feature_stability import (
    _compact_output,
    _json_bytes,
)


class CompactFeatureStabilityTests(unittest.TestCase):
    def test_compact_output_preserves_decision_evidence(self):
        full = {
            "variant": "candidate",
            "stats_dir": "/scratch/candidate",
            "file_count": 5,
            "seeds": [1, 2, 3, 4, 5],
            "top_k": 10,
            "corr_thresholds_reported": [0.8],
            "by_target": {
                "TOTSOMC": {
                    "metrics": {"overfit_warning_fraction": 0.0},
                    "features": [
                        {
                            "feature": "parm_0",
                            "selected_frequency": 1.0,
                            "top_k_frequency": 0.8,
                            "median_rank": 2.0,
                            "rank_iqr": 1.0,
                            "mean_r2_drop": {"median": 0.1},
                            "mean_rmse_increase": {"median": 12.0},
                            "positive_r2_drop_fraction": 1.0,
                            "positive_rmse_increase_fraction": 1.0,
                            "strong_candidate": True,
                        }
                    ],
                }
            },
            "feature_selection_summary": {
                "selected_features": [
                    {
                        "feature": "parm_0",
                        "selected_count": 5,
                        "selected_frequency": 1.0,
                        "requested_count": 5,
                        "requested_frequency": 1.0,
                        "excluded_by_explicit_subset_count": 0,
                        "excluded_by_explicit_subset_frequency": 0.0,
                    }
                ],
                "requested_explicit_subset_features": [
                    {
                        "feature": "parm_0",
                        "requested_count": 5,
                        "requested_frequency": 1.0,
                    }
                ],
            },
            "correlation_summary": {
                "pairwise_abs_corr_summary": [{"pair": "parm_0|parm_1"}],
                "thresholded_pair_frequency": {
                    "0.80": [
                        {
                            "feature_i": "parm_0",
                            "feature_j": "parm_1",
                            "seed_count_meeting_threshold": 4,
                            "seed_frequency_meeting_threshold": 0.8,
                            "abs_corr_summary": {"median": 0.9},
                        }
                    ]
                },
                "surviving_representatives": [],
            },
            "cross_target_agreement": [
                {
                    "feature": "parm_0",
                    "target_agreement_strong_top_k": True,
                }
            ],
        }
        full_bytes = _json_bytes(full)
        backup = Path("/puma/backup/report.json")

        compact = _compact_output(full, full_bytes, backup)

        self.assertEqual(compact["schema_version"], "spinup-feature-stability-compact-v1")
        self.assertEqual(
            compact["full_report"]["sha256"],
            hashlib.sha256(full_bytes).hexdigest(),
        )
        self.assertEqual(compact["full_report"]["size_bytes"], len(full_bytes))
        self.assertEqual(compact["full_report"]["backup_path"], str(backup))
        self.assertNotIn(
            "pairwise_abs_corr_summary",
            compact["correlation_summary"],
        )
        feature = compact["by_target"]["TOTSOMC"]["features"][0]
        self.assertEqual(feature["median_r2_drop"], 0.1)
        self.assertEqual(feature["median_rmse_increase"], 12.0)
        self.assertEqual(
            compact["cross_target_strong_top_k_features"],
            ["parm_0"],
        )


if __name__ == "__main__":
    unittest.main()
