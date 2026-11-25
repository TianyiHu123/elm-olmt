"""Pure numerical likelihood kernels for the three-stage MCMC posterior."""
from __future__ import annotations

import math

import numpy as np


def gaussian_log_likelihood(
    observed: np.ndarray,
    predicted: np.ndarray,
    observation_sigma: np.ndarray,
    surrogate_rmse: float,
) -> float:
    """Return a normalized independent Gaussian log likelihood."""

    obs = np.asarray(observed, dtype=np.float64)
    pred = np.asarray(predicted, dtype=np.float64)
    sigma = np.asarray(observation_sigma, dtype=np.float64)
    if obs.ndim != 1 or pred.shape != obs.shape or sigma.shape != obs.shape:
        raise ValueError("Gaussian inputs must be one-dimensional arrays with identical shape")
    if obs.size == 0:
        raise ValueError("Gaussian likelihood requires at least one observation")
    rmse = float(surrogate_rmse)
    if not np.all(np.isfinite(obs)) or not np.all(np.isfinite(pred)):
        raise ValueError("Gaussian observations and predictions must be finite")
    if not np.all(np.isfinite(sigma)) or np.any(sigma <= 0.0):
        raise ValueError("Gaussian observation sigma must be positive and finite")
    if not math.isfinite(rmse) or rmse <= 0.0:
        raise ValueError("Gaussian surrogate RMSE must be positive and finite")
    variance = np.square(sigma) + rmse * rmse
    residual = obs - pred
    terms = np.square(residual) / variance + np.log(2.0 * np.pi * variance)
    return float(-0.5 * np.sum(terms, dtype=np.float64))


def joint_cn_log_likelihood(
    observed_stocks: np.ndarray,
    predicted_full_profile_stocks: np.ndarray,
    depth_fraction: np.ndarray,
    total_bias_correction: np.ndarray,
    total_covariance: np.ndarray,
) -> float:
    """Return the normalized joint C/N log likelihood using stable solves."""

    observed = np.asarray(observed_stocks, dtype=np.float64)
    predicted = np.asarray(predicted_full_profile_stocks, dtype=np.float64)
    fraction = np.asarray(depth_fraction, dtype=np.float64)
    bias = np.asarray(total_bias_correction, dtype=np.float64)
    covariance = np.asarray(total_covariance, dtype=np.float64)
    for value, label in (
        (observed, "observed stocks"),
        (predicted, "predicted stocks"),
        (fraction, "depth fraction"),
        (bias, "bias correction"),
    ):
        if value.shape != (2,) or not np.all(np.isfinite(value)):
            raise ValueError(f"C/N {label} must be a finite length-two vector")
    if np.any(observed <= 0.0) or np.any(predicted <= 0.0) or np.any(fraction <= 0.0):
        raise ValueError("C/N observed, predicted, and depth-fraction values must be positive")
    if covariance.shape != (2, 2) or not np.all(np.isfinite(covariance)):
        raise ValueError("C/N covariance must be a finite 2x2 matrix")
    if not np.array_equal(covariance, covariance.T):
        raise ValueError("C/N covariance must be exactly symmetric")
    depth_prediction = fraction * predicted
    if not np.all(np.isfinite(depth_prediction)) or np.any(depth_prediction <= 0.0):
        raise ValueError("depth-adjusted C/N predictions must be positive and finite")
    try:
        cholesky = np.linalg.cholesky(covariance)
    except np.linalg.LinAlgError as exc:
        raise ValueError("C/N covariance must be positive definite") from exc
    residual = np.log(observed) - np.log(depth_prediction) + bias
    solved = np.linalg.solve(cholesky, residual)
    quadratic = float(np.dot(solved, solved))
    log_determinant = float(2.0 * np.sum(np.log(np.diag(cholesky))))
    return float(-0.5 * (quadratic + log_determinant + 2.0 * math.log(2.0 * math.pi)))
