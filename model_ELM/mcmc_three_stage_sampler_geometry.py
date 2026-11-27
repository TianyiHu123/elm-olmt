"""PPE1 prior-unit/logit coordinates for the three-stage sampler only.

The authoritative prior is ``Prior18``.  This module does not change its
physical density or the legacy SR-only coordinate transform.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .mcmc_prior import LOG_PARAMETERS, PPE1, Prior18


COORDINATE_SYSTEM_ID = "ppe1_prior_unit_logit_v1"
BOUNDARY_COORDINATE_SYSTEM_ID = "ppe1_prior_unit_logit_boundary_v2"
NUMERICAL_POLICY_SHA256 = "931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e"


class CoordinateSaturation(ValueError):
    """Finite proposed z rounded to a unit or physical boundary."""


class PhysicalMappingError(RuntimeError):
    """A finite proposed coordinate has an ineligible physical mapping."""

    def __init__(self, message: str, details: dict[str, object]):
        super().__init__(message)
        self.details = details


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


@dataclass(frozen=True)
class BoundaryMapResult:
    physical: np.ndarray
    unit: np.ndarray
    log_abs_det_jacobian: float
    events: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class PriorUnitLogitBoundaryGeometry:
    """Finite-precision PPE1 evaluation at the original finite logit state.

    Repairs are an evaluated physical-input policy.  They do not define a
    literally clipped change-of-variables map; the analytic smooth-map
    Jacobian remains evaluated at the original z.
    """

    prior: Prior18

    def __post_init__(self) -> None:
        if self.prior.prior_id != PPE1 or len(self.prior.names) != 18:
            raise ValueError("boundary geometry requires PPE1 and 18 parameters")
        policy_path = Path(__file__).resolve().parents[1] / "development/mcmc_optimization/slurm/iter006/numerical_policy.json"
        raw = policy_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != NUMERICAL_POLICY_SHA256:
            raise ValueError("Iter006 numerical policy identity mismatch")
        policy = json.loads(raw)
        if policy["coordinate_system_id"] != BOUNDARY_COORDINATE_SYSTEM_ID or policy["directional_ulp_ceiling"] != 8:
            raise ValueError("Iter006 numerical policy schema mismatch")
        object.__setattr__(self, "policy", policy)

    @property
    def coordinate_system_id(self) -> str:
        return BOUNDARY_COORDINATE_SYSTEM_ID

    def sampler_to_unit(self, sampler: np.ndarray) -> np.ndarray:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        u = _sigmoid(z)
        if np.any((u <= 0.0) | (u >= 1.0)):
            error = CoordinateSaturation("finite sampler coordinate saturated an exact unit boundary")
            error.details = {"z": z.tolist(), "u": u.tolist(), "kind": "unit_saturation"}  # type: ignore[attr-defined]
            raise error
        return u[0] if scalar else u

    @staticmethod
    def _reference_row(prior: Prior18, u: np.ndarray) -> tuple[list[Decimal], list[tuple[Decimal, Decimal]]]:
        with localcontext() as context:
            context.prec = 800
            values: list[Decimal] = []
            intervals: list[tuple[Decimal, Decimal]] = []
            for index, name in enumerate(prior.names):
                low = Decimal.from_float(float(prior.lower[index]))
                high = Decimal.from_float(float(prior.upper[index]))
                if index == 17:
                    low = max(low, values[16] + Decimal("0.5"))
                    high = min(high, Decimal("49.5"))
                unit = Decimal.from_float(float(u[index]))
                if name in LOG_PARAMETERS:
                    value = (low.ln() + unit * (high / low).ln()).exp()
                else:
                    value = low + unit * (high - low)
                values.append(value)
                intervals.append((low, high))
            return values, intervals

    @staticmethod
    def _branch(name: str, index: int, side: str) -> str:
        if index == 17:
            return "conditional_root_" + side
        return ("log_uniform_" if name in LOG_PARAMETERS else "linear_") + side

    @staticmethod
    def _raw_component(name: str, low: float, high: float, u: float) -> float:
        if name in LOG_PARAMETERS:
            ratio_log = math.log(high / low)
            return (low * math.exp(u * ratio_log) if u <= 0.5
                    else high * math.exp((u - 1.0) * ratio_log))
        span = high - low
        return low + u * span if u <= 0.5 else high - (1.0 - u) * span

    @staticmethod
    def _directional_ulp(bound: float, side: str) -> float:
        direction = -math.inf if side == "lower" else math.inf
        return abs(math.nextafter(bound, direction) - bound)

    @staticmethod
    def _regime_displacement(name: str, low: float, high: float, u: float, side: str) -> float:
        if name in LOG_PARAMETERS:
            ratio_log = math.log(high / low)
            if side == "lower":
                return abs(low * math.expm1(u * ratio_log))
            return abs(high * math.expm1((u - 1.0) * ratio_log))
        return (u if side == "lower" else 1.0 - u) * (high - low)

    def _check_boundary(
        self, *, index: int, name: str, z: float, u: float, raw: float,
        low: float, high: float, side: str, reference: Decimal,
        reference_interval: tuple[Decimal, Decimal],
    ) -> dict[str, object]:
        bound = low if side == "lower" else high
        ulp = self._directional_ulp(bound, side)
        branch = self._branch(name, index, side)
        allowance = int(self.policy["allowance_by_branch_and_side"][branch])
        outward = max(0.0, (bound - raw if side == "lower" else raw - bound) / ulp)
        input_displacement = self._regime_displacement(name, low, high, u, side)
        with localcontext() as context:
            context.prec = 800
            unit_ulp = Decimal.from_float(ulp)
            full_error = abs(Decimal.from_float(raw) - reference) / unit_ulp
            reference_distance = abs(reference - Decimal.from_float(bound)) / unit_ulp
            true_low, true_high = reference_interval
            reference_supported = true_low <= reference <= true_high
            eligible = (outward <= allowance and input_displacement <= 8.0 * ulp
                        and reference_distance <= Decimal(8)
                        and full_error <= Decimal(allowance) and reference_supported)
            details: dict[str, object] = {
                "parameter": name, "index": index, "side": side,
                "bound_type": "conditional" if index == 17 else "marginal",
                "branch": branch, "z": z, "u": u, "raw": raw,
                "lower": low, "upper": high, "bound": bound,
                "directional_ulp": ulp, "outward_ulp_excursion": outward,
                "absolute_excursion": abs(raw - bound) if outward else 0.0,
                "relative_excursion": abs(raw-bound) / abs(bound) if outward else 0.0,
                "input_displacement_ulp": input_displacement / ulp,
                "reference_physical": str(reference),
                "reference_distance_from_bound_ulp": str(reference_distance),
                "full_mapping_error_ulp": str(full_error),
                "allowance_ulp": allowance, "eligible": bool(eligible),
                "kind": "physical_repair" if outward else "natural_physical_endpoint",
            }
        if not eligible:
            raise PhysicalMappingError("physical mapping boundary event fails locked policy", details)
        details["repaired"] = bound
        return details

    def map_with_jacobian(self, sampler: np.ndarray) -> BoundaryMapResult:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        if not scalar:
            raise ValueError("map_with_jacobian requires one 18-parameter vector")
        row = z[0]
        unit = np.asarray(self.sampler_to_unit(row), dtype=np.float64)
        theta = np.empty(18, dtype=np.float64)
        events: list[dict[str, object]] = []
        reference_values = None
        reference_intervals = None
        for index, name in enumerate(self.prior.names):
            low = float(self.prior.lower[index])
            high = float(self.prior.upper[index])
            if index == 17:
                root_low, root_high = self.prior.cn_bounds(theta[16])
                low, high = float(root_low), float(root_high)
            if not (math.isfinite(low) and math.isfinite(high) and low < high):
                raise PhysicalMappingError("invalid ordered physical interval", {"index": index, "lower": low, "upper": high})
            raw = self._raw_component(name, low, high, float(unit[index]))
            if not math.isfinite(raw):
                raise PhysicalMappingError("nonfinite physical component", {"index": index, "raw": raw})
            side = "lower" if raw <= low else "upper" if raw >= high else None
            if side is not None:
                if reference_values is None:
                    reference_values, reference_intervals = self._reference_row(self.prior, unit)
                assert reference_intervals is not None
                event = self._check_boundary(
                    index=index, name=name, z=float(row[index]), u=float(unit[index]),
                    raw=raw, low=low, high=high, side=side,
                    reference=reference_values[index], reference_interval=reference_intervals[index],
                )
                events.append(event)
                raw = min(max(raw, low), high)
            theta[index] = raw
        if not bool(self.prior.support_mask(theta)):
            raise PhysicalMappingError("complete repaired physical vector lacks PPE1 support", {"physical": theta.tolist()})
        log_dtheta_du = 0.0
        for index, name in enumerate(self.prior.names):
            if index == 17:
                low, high = self.prior.cn_bounds(theta[16])
                term = math.log(float(high - low))
            elif name in LOG_PARAMETERS:
                term = math.log(float(theta[index])) + math.log(math.log(float(self.prior.upper[index] / self.prior.lower[index])))
            else:
                term = math.log(float(self.prior.upper[index] - self.prior.lower[index]))
            log_dtheta_du += term
        log_du_dz = -np.logaddexp(0.0, -row) - np.logaddexp(0.0, row)
        jacobian = float(log_dtheta_du + np.sum(log_du_dz))
        if not math.isfinite(jacobian):
            raise PhysicalMappingError("nonfinite analytic Jacobian", {"z": row.tolist()})
        return BoundaryMapResult(theta, unit, jacobian, tuple(events))

    def sampler_to_physical(self, sampler: np.ndarray) -> np.ndarray:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        physical = np.asarray([self.map_with_jacobian(row).physical for row in z], dtype=np.float64)
        return physical[0] if scalar else physical

    def log_abs_det_dphysical_dsampler(self, sampler: np.ndarray) -> np.ndarray | float:
        z, scalar = _matrix(sampler, name="sampler coordinates")
        values = np.asarray([self.map_with_jacobian(row).log_abs_det_jacobian for row in z], dtype=np.float64)
        return float(values[0]) if scalar else values

    def physical_to_sampler(self, physical: np.ndarray) -> np.ndarray:
        return PriorUnitLogitGeometry(self.prior).physical_to_sampler(physical)
