from __future__ import annotations

import math
import unittest

import numpy as np

from model_ELM.mcmc_three_stage_likelihood import (
    gaussian_log_likelihood,
    joint_cn_log_likelihood,
)


class ThreeStageLikelihoodTests(unittest.TestCase):
    def test_gaussian_matches_scalar_reference(self):
        observed = np.asarray([0.0, 1.5, -0.2, 4.0], dtype=np.float64)
        predicted = np.asarray([0.1, 1.1, 0.3, 3.7], dtype=np.float64)
        sigma = np.asarray([0.05, 0.2, 0.3, 0.8], dtype=np.float64)
        rmse = 0.4
        terms = []
        for obs, pred, obs_sigma in zip(observed, predicted, sigma):
            variance = obs_sigma * obs_sigma + rmse * rmse
            terms.append(-0.5 * ((obs - pred) ** 2 / variance + math.log(2.0 * math.pi * variance)))
        expected = math.fsum(terms)
        actual = gaussian_log_likelihood(observed, predicted, sigma, rmse)
        self.assertTrue(np.isclose(actual, expected, rtol=1e-12, atol=1e-10))

    def test_joint_cn_matches_closed_form_reference(self):
        observed = np.asarray([100.0, 12.0])
        predicted = np.asarray([110.0, 10.5])
        fraction = np.asarray([0.7, 0.72])
        bias = np.asarray([0.01, -0.02])
        covariance = np.asarray([[0.15, 0.04], [0.04, 0.11]])
        residual = np.log(observed) - np.log(fraction * predicted) + bias
        a, b, d = covariance[0, 0], covariance[0, 1], covariance[1, 1]
        determinant = a * d - b * b
        quadratic = (d * residual[0] ** 2 - 2.0 * b * residual[0] * residual[1]
                     + a * residual[1] ** 2) / determinant
        expected = -0.5 * (quadratic + math.log(determinant) + 2.0 * math.log(2.0 * math.pi))
        actual = joint_cn_log_likelihood(observed, predicted, fraction, bias, covariance)
        self.assertTrue(np.isclose(actual, expected, rtol=1e-12, atol=1e-10))

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            gaussian_log_likelihood(np.ones(2), np.ones(3), np.ones(2), 0.1)
        with self.assertRaises(ValueError):
            gaussian_log_likelihood(np.ones(2), np.ones(2), np.zeros(2), 0.1)
        with self.assertRaises(ValueError):
            gaussian_log_likelihood(np.ones(2), np.ones(2), np.ones(2), 0.0)
        args = (np.ones(2), np.ones(2), np.ones(2), np.zeros(2))
        with self.assertRaises(ValueError):
            joint_cn_log_likelihood(*args, np.asarray([[1.0, 2.0], [2.0, 1.0]]))
        with self.assertRaisesRegex(ValueError, "exactly symmetric"):
            joint_cn_log_likelihood(*args, np.asarray([[1.0, 0.2], [0.1, 1.0]]))
        with self.assertRaises(ValueError):
            joint_cn_log_likelihood(np.ones(2), np.asarray([0.0, 1.0]), np.ones(2), np.zeros(2), np.eye(2))


if __name__ == "__main__":
    unittest.main()
