from __future__ import annotations

import unittest

import numpy as np

from development.mcmc_optimization.slurm.iter007.run_iter007 import gap_lengths, interpolate_eligible


class Iter007InterpolationFixtures(unittest.TestCase):
    def test_physical_gap_crosses_midnight(self):
        support = np.ones(48, dtype=bool)
        support[23:25] = False
        lengths = gap_lengths(support)
        np.testing.assert_array_equal(lengths[23:25], [2, 2])
        self.assertEqual(int(lengths[:24].max()), 2)
        self.assertEqual(int(lengths[24:].max()), 2)
        support[25] = False
        self.assertEqual(int(gap_lengths(support)[23]), 3)

    def test_unbracketed_run_is_ineligible(self):
        support = np.ones(24, dtype=bool)
        support[:2] = False
        np.testing.assert_array_equal(gap_lengths(support)[:2], [32767, 32767])
        support[:] = True
        support[-1] = False
        self.assertEqual(int(gap_lengths(support)[-1]), 32767)

    def test_fill_only_eligible_hours_and_preserve_supported_values(self):
        values = np.array([2.0, np.nan, np.nan, 8.0, np.nan, 10.0])
        support = np.isfinite(values)
        eligible = np.array([True, True, True, True, False, False])
        result, flag = interpolate_eligible(values, support, eligible)
        np.testing.assert_allclose(result[:4], [2.0, 4.0, 6.0, 8.0])
        self.assertTrue(np.isnan(result[4]))
        np.testing.assert_array_equal(flag, [False, True, True, False, False, False])
        np.testing.assert_array_equal(result[support], values[support])

    def test_no_extrapolation(self):
        values = np.array([np.nan, 2.0, 3.0])
        with self.assertRaisesRegex(RuntimeError, "extrapolate"):
            interpolate_eligible(values, np.isfinite(values), np.array([True, True, True]))


if __name__ == "__main__":
    unittest.main()
