"""PPE1 prior-unit/logit coordinates for the three-stage sampler only.

The authoritative prior is ``Prior18``.  This module does not change its
physical density or the legacy SR-only coordinate transform.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .mcmc_prior import LOG_PARAMETERS, PPE1, Prior18


COORDINATE_SYSTEM_ID = "ppe1_prior_unit_logit_v1"


class CoordinateSaturation(ValueError):
    """Finite proposed z rounded to a unit or physical boundary."""


def _matrix(values: np.ndarray, *, name: str) -> tuple[np.ndarray, bool]:
    array = np.asarray(values, dtype=np.float64)
    scalar = array.ndim == 1
    if scalar:
        array = array[None, :]
    if array.ndim != 2 or array.shape[1] != 18:
        raise ValueError(f"{name} must have shape (18,) or (n,18)")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array, scalar


def _sigmoid(z: np.ndarray) -> np.ndarray:
    result = np.empty_like(z)
    positive = z >= 0
    with np.errstate(under="ignore"):
        result[positive] = 1.0 / (1.0 + np.exp(-z[positive]))
        exponential = np.exp(z[~positive])
    result[~positive] = exponential / (1.0 + exponential)
    return result


@dataclass(frozen=True)
class PriorUnitLogitGeometry:
    prior: Prior18

    def __post_init__(self) -> None:
        if self.prior.prior_id != PPE1 or len(self.prior.names) != 18:
            raise ValueError("prior-unit/logit geometry requires the PPE1 18-D prior")

    @property
    def coordinate_system_id(self) -> str:
        return COORDINATE_SYSTEM_ID

    def sampler_to_unit(self, sampler: np.ndarray) -> np.ndarray:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        u = _sigmoid(z)
        if np.any((u <= 0.0) | (u >= 1.0)):
            raise CoordinateSaturation("finite sampler coordinate saturated a unit boundary")
        return u[0] if scalar else u

    def sampler_to_physical(self, sampler: np.ndarray) -> np.ndarray:
        unit = self.sampler_to_unit(sampler)
        physical = self.prior.inverse_unit(unit)
        theta, _ = _matrix(physical, name="mapped physical parameters")
        if np.any((theta < self.prior.lower) | (theta > self.prior.upper)):
            raise RuntimeError("prior inverse unit mapping escaped PPE1 marginal bounds")
        if np.any((theta == self.prior.lower) | (theta == self.prior.upper)):
            raise CoordinateSaturation("interior unit coordinate rounded to a physical bound")
        root_low, root_high = self.prior.cn_bounds(theta[:, 16])
        if np.any((theta[:, 17] < root_low) | (theta[:, 17] > root_high)):
            raise RuntimeError("prior inverse unit mapping escaped conditional C:N support")
        if np.any((theta[:, 17] == root_low) | (theta[:, 17] == root_high)):
            raise CoordinateSaturation("conditional C:N coordinate rounded to a bound")
        if not np.all(np.asarray(self.prior.support_mask(physical), dtype=bool)):
            raise RuntimeError("prior inverse unit mapping escaped PPE1 physical support")
        return physical

    def physical_to_unit(self, physical: np.ndarray) -> np.ndarray:
        theta, scalar = _matrix(physical, name="physical parameters")
        if not np.all(np.asarray(self.prior.support_mask(theta), dtype=bool)):
            raise ValueError("physical parameters are outside PPE1 support")
        unit = (theta - self.prior.lower) / (self.prior.upper - self.prior.lower)
        for index, name in enumerate(self.prior.names):
            if name in LOG_PARAMETERS:
                unit[:, index] = np.log(theta[:, index] / self.prior.lower[index]) / np.log(
                    self.prior.upper[index] / self.prior.lower[index]
                )
        root_low, root_high = self.prior.cn_bounds(theta[:, 16])
        unit[:, 17] = (theta[:, 17] - root_low) / (root_high - root_low)
        if np.any((unit <= 0.0) | (unit >= 1.0)):
            raise CoordinateSaturation("physical parameters map to a unit boundary")
        replay = np.asarray(self.prior.inverse_unit(unit), dtype=np.float64)
        if not np.allclose(replay, theta, rtol=1.0e-12, atol=0.0):
            raise RuntimeError("physical-to-unit prior inverse replay failed")
        return unit[0] if scalar else unit

    def physical_to_sampler(self, physical: np.ndarray) -> np.ndarray:
        unit = self.physical_to_unit(physical)
        return np.log(unit) - np.log1p(-unit)

    def log_abs_det_dphysical_dsampler(self, sampler: np.ndarray) -> np.ndarray | float:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        unit = np.asarray(self.sampler_to_unit(z), dtype=np.float64)
        theta = np.asarray(self.prior.inverse_unit(unit), dtype=np.float64)
        log_dtheta_du = np.zeros(z.shape[0], dtype=np.float64)
        for index, name in enumerate(self.prior.names):
            if index == 17:
                root_low, root_high = self.prior.cn_bounds(theta[:, 16])
                term = np.log(root_high - root_low)
            elif name in LOG_PARAMETERS:
                term = np.log(theta[:, index]) + np.log(
                    np.log(self.prior.upper[index] / self.prior.lower[index])
                )
            else:
                term = np.log(self.prior.upper[index] - self.prior.lower[index])
            log_dtheta_du += term
        log_du_dz = -np.logaddexp(0.0, -z) - np.logaddexp(0.0, z)
        result = log_dtheta_du + np.sum(log_du_dz, axis=1)
        if not np.all(np.isfinite(result)):
            raise RuntimeError("prior-unit/logit Jacobian is nonfinite")
        return float(result[0]) if scalar else result
