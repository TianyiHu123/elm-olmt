"""Deterministic geometry helpers for the Iter009 coupled-MCMC pilot.

The sampler may operate in either physical coordinates or a one-to-one transformed
coordinate system.  The physical likelihood/prior remains authoritative; transformed
sampling includes the analytic change-of-variables Jacobian.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


_LOG_PARAMETERS = frozenset({"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag"})


@dataclass(frozen=True)
class CoordinateTransform:
    """Strict physical/sampler coordinate mapping with an analytic Jacobian."""

    names: tuple[str, ...]
    pmin: np.ndarray
    pmax: np.ndarray
    transformed: np.ndarray
    kinds: tuple[str, ...]

    @classmethod
    def from_parameters(
        cls, names: Sequence[str], pmin: Sequence[float], pmax: Sequence[float], *, enabled: bool
    ) -> "CoordinateTransform":
        lower = np.asarray(pmin, dtype=float)
        upper = np.asarray(pmax, dtype=float)
        labels = tuple(str(name) for name in names)
        if lower.ndim != 1 or lower.shape != upper.shape or len(labels) != lower.size:
            raise ValueError("coordinate names and bounds must be aligned one-dimensional arrays")
        if not np.all(np.isfinite(lower)) or not np.all(np.isfinite(upper)) or np.any(upper <= lower):
            raise ValueError("coordinate bounds must be finite and strictly ordered")
        kinds = []
        transformed = np.zeros(lower.size, dtype=bool)
        for i, name in enumerate(labels):
            if not enabled:
                kinds.append("physical")
            elif name in _LOG_PARAMETERS:
                if lower[i] <= 0:
                    raise ValueError(f"log-transformed parameter {name} must have positive lower bound")
                kinds.append("log")
                transformed[i] = True
            elif name.startswith("rf_") or name.startswith("sigma_"):
                kinds.append("logit")
                transformed[i] = True
            else:
                kinds.append("physical")
        return cls(labels, lower, upper, transformed, tuple(kinds))

    def physical_to_sampler(self, physical: np.ndarray) -> np.ndarray:
        value = np.asarray(physical, dtype=float)
        if value.shape[-1] != self.pmin.size:
            raise ValueError("physical coordinate width does not match bounds")
        if not np.all(np.isfinite(value)) or np.any(value <= self.pmin) or np.any(value >= self.pmax):
            raise ValueError("physical coordinates must be finite and strictly within bounds")
        result = value.copy()
        for i, kind in enumerate(self.kinds):
            if kind == "log":
                result[..., i] = np.log(value[..., i])
            elif kind == "logit":
                scaled = (value[..., i] - self.pmin[i]) / (self.pmax[i] - self.pmin[i])
                result[..., i] = np.log(scaled) - np.log1p(-scaled)
        return result

    def sampler_to_physical(self, sampler: np.ndarray) -> np.ndarray:
        value = np.asarray(sampler, dtype=float)
        if value.shape[-1] != self.pmin.size:
            raise ValueError("sampler coordinate width does not match bounds")
        if not np.all(np.isfinite(value)):
            raise ValueError("sampler coordinates must be finite")
        result = value.copy()
        for i, kind in enumerate(self.kinds):
            if kind == "log":
                result[..., i] = np.exp(value[..., i])
            elif kind == "logit":
                sigmoid = np.empty_like(value[..., i])
                positive = value[..., i] >= 0
                sigmoid[positive] = 1.0 / (1.0 + np.exp(-value[..., i][positive]))
                exp_value = np.exp(value[..., i][~positive])
                sigmoid[~positive] = exp_value / (1.0 + exp_value)
                result[..., i] = self.pmin[i] + (self.pmax[i] - self.pmin[i]) * sigmoid
        if np.any(result <= self.pmin) or np.any(result >= self.pmax):
            raise ValueError("sampler coordinates map outside strict physical bounds")
        return result

    def log_abs_det_dphysical_dsampler(self, sampler: np.ndarray) -> np.ndarray:
        """Return log |d physical / d sampler| for the final coordinate axis."""
        value = np.asarray(sampler, dtype=float)
        physical = self.sampler_to_physical(value)
        out = np.zeros(value.shape[:-1], dtype=float)
        for i, kind in enumerate(self.kinds):
            if kind == "log":
                out += np.log(physical[..., i])
            elif kind == "logit":
                span = self.pmax[i] - self.pmin[i]
                scaled = (physical[..., i] - self.pmin[i]) / span
                out += np.log(span) + np.log(scaled) + np.log1p(-scaled)
        return out

    def metadata(self) -> dict[str, object]:
        return {
            "coordinate_system": "transformed" if bool(np.any(self.transformed)) else "physical",
            "parameter_names": list(self.names),
            "transform_kinds": list(self.kinds),
            "pmin": self.pmin.tolist(),
            "pmax": self.pmax.tolist(),
            "jacobian": "log_abs_det_dphysical_dsampler added to physical log posterior",
        }


def make_move_configuration(name: str, *, de_move_scale: float = 1.0, ndim: int | None = None):
    """Return the locked Iter009/Iter011 proposal mechanisms.

    A unit Iter011 multiplier deliberately constructs the same default DEMove object; lower
    multipliers only change DEMove's gamma and leave DESnookerMove unchanged.
    """
    import emcee

    if name == "stretch":
        return emcee.moves.StretchMove(a=2.0)
    if name == "de_mixture":
        if de_move_scale <= 0:
            raise ValueError("de_move_scale must be positive")
        if de_move_scale == 1.0:
            de_move = emcee.moves.DEMove()
        else:
            if ndim is None or ndim <= 0:
                raise ValueError("ndim is required for a non-default DEMove scale")
            de_move = emcee.moves.DEMove(gamma0=float(de_move_scale) * 2.38 / np.sqrt(2.0 * ndim))
        return [(de_move, 0.8), (emcee.moves.DESnookerMove(), 0.2)]
    raise ValueError(f"unsupported Iter009 move configuration: {name}")
