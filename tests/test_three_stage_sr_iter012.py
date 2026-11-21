import unittest

import numpy as np

from development.three_stage_surrogate.slurm.iter012.iter012_common import (
    BASE_FEATURE_COUNT,
    FEATURE_COUNT,
    feature_block,
)


class Iter012FeatureBlockTests(unittest.TestCase):
    def setUp(self):
        self.x = np.arange(2 * 3 * 4 * FEATURE_COUNT, dtype=np.float32).reshape(2, 3, 4, FEATURE_COUNT)
        self.true_gpp = (100000 + np.arange(2 * 3 * 4, dtype=np.float32)).reshape(2, 3, 4)
        self.positions = np.asarray([0, 2], dtype=np.int64)

    def test_arm_a_removes_gpp_column(self):
        observed = feature_block(self.x, self.true_gpp, "A", 0, self.positions)
        expected = self.x[0, self.positions, :, :BASE_FEATURE_COUNT].reshape(-1, BASE_FEATURE_COUNT)
        self.assertEqual(observed.shape, (8, 43))
        np.testing.assert_array_equal(observed, expected)

    def test_arm_b_preserves_predicted_gpp_column(self):
        observed = feature_block(self.x, self.true_gpp, "B", 1, self.positions)
        expected = self.x[1, self.positions].reshape(-1, FEATURE_COUNT)
        self.assertEqual(observed.shape, (8, 44))
        np.testing.assert_array_equal(observed, expected)

    def test_arm_c_replaces_only_gpp_column(self):
        observed = feature_block(self.x, self.true_gpp, "C", 1, self.positions)
        expected_base = self.x[1, self.positions, :, :BASE_FEATURE_COUNT].reshape(-1, BASE_FEATURE_COUNT)
        expected_gpp = self.true_gpp[1, self.positions].reshape(-1)
        self.assertEqual(observed.shape, (8, 44))
        np.testing.assert_array_equal(observed[:, :BASE_FEATURE_COUNT], expected_base)
        np.testing.assert_array_equal(observed[:, -1], expected_gpp)

    def test_invalid_arm_rejected(self):
        with self.assertRaises(ValueError):
            feature_block(self.x, self.true_gpp, "D", 0, self.positions)


if __name__ == "__main__":
    unittest.main()
