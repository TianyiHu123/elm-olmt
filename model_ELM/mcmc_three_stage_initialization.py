"""Deterministic prior-aware initialization for three-stage MCMC pilots."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from typing import Any, Sequence

import numpy as np

from .mcmc_prior import Prior18


@dataclass(frozen=True)
class GeometryMetrics:
    count: int
    dimension: int
    rank: int
    condition_number: float
    range_by_dimension: tuple[float, ...]
    std_by_dimension: tuple[float, ...]
    minimum_pairwise_distance: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SearchAssessment:
    generated: int
    finite_unique_eligible: int
    finite_rate: float
    geometry: GeometryMetrics
    percentile_span_05_95: tuple[float, ...]
    occupied_deciles: tuple[int, ...]
    stage_pass: bool
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _require_matrix(values: np.ndarray | Sequence[Sequence[float]], *, columns: int) -> np.ndarray:
    matrix = np.asarray(values, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] != columns or matrix.shape[0] == 0:
        raise ValueError(f"values must have shape (n,{columns}) with n > 0")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("values must be finite")
    return matrix


def scrambled_sobol_prefix(*, dimension: int, count: int, seed: int) -> np.ndarray:
    """Return one Owen-scrambled power-of-two Sobol prefix."""

    if dimension <= 0 or count <= 0 or count & (count - 1):
        raise ValueError("dimension must be positive and count must be a power of two")
    from scipy.stats import qmc

    sampler = qmc.Sobol(d=int(dimension), scramble=True, seed=int(seed))
    unit = np.asarray(sampler.random_base2(m=int(log2(count))), dtype=np.float64)
    if unit.shape != (count, dimension) or np.any(unit < 0.0) or np.any(unit > 1.0):
        raise RuntimeError("Sobol generator returned an invalid unit-space array")
    return unit


def prior_aware_candidates(prior: Prior18, unit: np.ndarray) -> np.ndarray:
    matrix = _require_matrix(unit, columns=18)
    if np.any(matrix < 0.0) or np.any(matrix > 1.0):
        raise ValueError("candidate unit coordinates must lie in [0,1]")
    physical = np.asarray(prior.inverse_unit(matrix), dtype=np.float64)
    if physical.shape != matrix.shape:
        raise RuntimeError("prior inverse map changed candidate shape")
    return physical


def physical_to_unit(prior: Prior18, physical: np.ndarray) -> np.ndarray:
    """Invert ``Prior18.inverse_unit`` without approximating conditional support."""

    matrix = _require_matrix(physical, columns=18)
    support = np.asarray(prior.support_mask(matrix), dtype=bool)
    if not np.all(support):
        raise ValueError("physical values must satisfy exact prior support")
    unit = (matrix - prior.lower) / (prior.upper - prior.lower)
    for index, name in enumerate(prior.names):
        if name in {"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag"}:
            low, high = prior.ks4_bounds(matrix[:, 5]) if index == 6 else (
                np.full(matrix.shape[0], prior.lower[index]),
                np.full(matrix.shape[0], prior.upper[index]),
            )
            unit[:, index] = np.log(matrix[:, index] / low) / np.log(high / low)
    root_low, root_high = prior.cn_bounds(matrix[:, 16])
    unit[:, 17] = (matrix[:, 17] - root_low) / (root_high - root_low)
    if np.any(unit < -1.0e-14) or np.any(unit > 1.0 + 1.0e-14):
        raise RuntimeError("physical-to-unit inverse escaped the unit interval")
    unit = np.minimum(1.0, np.maximum(0.0, unit))
    replay = np.asarray(prior.inverse_unit(unit), dtype=np.float64)
    if not np.allclose(replay, matrix, rtol=1.0e-12, atol=1.0e-12):
        raise RuntimeError("physical-to-unit inverse failed exact prior-aware replay")
    return unit


def sampling_eligibility(prior: Prior18, physical: np.ndarray) -> tuple[np.ndarray, tuple[str | None, ...]]:
    matrix = _require_matrix(physical, columns=18)
    eligible = np.zeros(matrix.shape[0], dtype=bool)
    reasons: list[str | None] = []
    for index, row in enumerate(matrix):
        try:
            sampler = np.asarray(prior.coordinate_transform.physical_to_sampler(row), dtype=np.float64)
        except ValueError:
            reasons.append("sampling_transform_boundary")
            continue
        if not np.all(np.isfinite(sampler)):
            reasons.append("sampling_transform_boundary")
            continue
        eligible[index] = True
        reasons.append(None)
    return eligible, tuple(reasons)


def geometry_metrics(unit: np.ndarray) -> GeometryMetrics:
    matrix = _require_matrix(unit, columns=18)
    centered = matrix - matrix.mean(axis=0)
    singular = np.linalg.svd(centered, compute_uv=False)
    tolerance = max(centered.shape) * np.finfo(np.float64).eps * singular[0]
    rank = int(np.sum(singular > tolerance))
    condition = float("inf") if rank < matrix.shape[1] else float(singular[0] / singular[-1])
    if matrix.shape[0] < 2:
        minimum_distance = float("inf")
    else:
        minimum_distance = float("inf")
        for index in range(matrix.shape[0] - 1):
            distances = np.linalg.norm(matrix[index + 1 :] - matrix[index], axis=1)
            minimum_distance = min(minimum_distance, float(np.min(distances)))
    return GeometryMetrics(
        count=int(matrix.shape[0]),
        dimension=int(matrix.shape[1]),
        rank=rank,
        condition_number=condition,
        range_by_dimension=tuple(float(v) for v in np.ptp(matrix, axis=0)),
        std_by_dimension=tuple(float(v) for v in np.std(matrix, axis=0, ddof=0)),
        minimum_pairwise_distance=minimum_distance,
    )


def assess_stage_one(unit: np.ndarray, eligible: np.ndarray) -> SearchAssessment:
    matrix = _require_matrix(unit, columns=18)
    mask = np.asarray(eligible, dtype=bool)
    if mask.shape != (matrix.shape[0],):
        raise ValueError("eligible mask shape mismatch")
    selected = matrix[mask]
    if selected.shape[0] == 0:
        empty_geometry = GeometryMetrics(0, 18, 0, float("inf"), (0.0,) * 18, (0.0,) * 18, 0.0)
        return SearchAssessment(
            generated=matrix.shape[0], finite_unique_eligible=0, finite_rate=0.0,
            geometry=empty_geometry, percentile_span_05_95=(0.0,) * 18,
            occupied_deciles=(0,) * 18, stage_pass=False,
            failure_reasons=("fewer_than_512_finite_unique_eligible", "finite_rate_below_0.90"),
        )
    selected = np.unique(selected, axis=0)
    geometry = geometry_metrics(selected)
    spans = np.percentile(selected, 95.0, axis=0) - np.percentile(selected, 5.0, axis=0)
    occupied = []
    for column in range(18):
        bins = np.minimum((selected[:, column] * 10.0).astype(np.int64), 9)
        occupied.append(int(np.unique(bins).size))
    reasons = []
    finite_rate = float(mask.mean())
    if selected.shape[0] < 512:
        reasons.append("fewer_than_512_finite_unique_eligible")
    if finite_rate < 0.90:
        reasons.append("finite_rate_below_0.90")
    if geometry.rank < 18:
        reasons.append("eligible_rank_below_18")
    if geometry.condition_number > 1000.0:
        reasons.append("eligible_condition_above_1000")
    if np.any(spans < 0.75):
        reasons.append("eligible_percentile_span_below_0.75")
    if any(value < 8 for value in occupied):
        reasons.append("eligible_decile_occupancy_below_8")
    return SearchAssessment(
        generated=int(matrix.shape[0]),
        finite_unique_eligible=int(selected.shape[0]),
        finite_rate=finite_rate,
        geometry=geometry,
        percentile_span_05_95=tuple(float(v) for v in spans),
        occupied_deciles=tuple(occupied),
        stage_pass=not reasons,
        failure_reasons=tuple(reasons),
    )


def _ordered_unique_indices(physical: np.ndarray, candidate_indices: np.ndarray) -> np.ndarray:
    keep: list[int] = []
    seen: set[bytes] = set()
    for position in np.argsort(candidate_indices, kind="stable"):
        key = np.asarray(physical[position], dtype="<f8").tobytes()
        if key not in seen:
            seen.add(key)
            keep.append(int(position))
    return np.asarray(keep, dtype=np.int64)


def select_candidate_pool(
    *,
    unit: np.ndarray,
    physical: np.ndarray,
    log_posterior: np.ndarray,
    eligible: np.ndarray,
    candidate_indices: np.ndarray | None = None,
    score_count: int = 96,
    diversity_count: int = 160,
) -> np.ndarray:
    unit_matrix = _require_matrix(unit, columns=18)
    physical_matrix = _require_matrix(physical, columns=18)
    if physical_matrix.shape != unit_matrix.shape:
        raise ValueError("unit and physical candidate shapes differ")
    scores = np.asarray(log_posterior, dtype=np.float64)
    mask = np.asarray(eligible, dtype=bool) & np.isfinite(scores)
    if scores.shape != (unit_matrix.shape[0],) or mask.shape != scores.shape:
        raise ValueError("candidate score or eligibility shape mismatch")
    indices = np.arange(unit_matrix.shape[0], dtype=np.int64) if candidate_indices is None else np.asarray(candidate_indices, dtype=np.int64)
    if indices.shape != scores.shape or np.unique(indices).size != indices.size:
        raise ValueError("candidate indices must be unique and aligned")
    positions = np.flatnonzero(mask)
    positions = positions[_ordered_unique_indices(physical_matrix[positions], indices[positions])]
    total = int(score_count + diversity_count)
    if positions.size < total:
        raise ValueError(f"at least {total} unique finite eligible candidates are required")
    score_order = positions[np.lexsort((indices[positions], -scores[positions]))]
    selected = list(map(int, score_order[:score_count]))
    remaining = set(map(int, positions)) - set(selected)
    while len(selected) < total:
        selected_unit = unit_matrix[np.asarray(selected)]
        best = None
        best_key = None
        for position in remaining:
            distance = float(np.min(np.linalg.norm(selected_unit - unit_matrix[position], axis=1)))
            key = (distance, float(scores[position]), -int(indices[position]))
            if best_key is None or key > best_key:
                best_key = key
                best = position
        if best is None:
            raise RuntimeError("deterministic diversity fill exhausted unexpectedly")
        selected.append(int(best))
        remaining.remove(int(best))
    return np.asarray(selected, dtype=np.int64)


def validate_pool_geometry(unit: np.ndarray) -> GeometryMetrics:
    metrics = geometry_metrics(unit)
    if metrics.count != 256 or metrics.rank != 18 or metrics.condition_number > 100.0:
        raise ValueError("candidate pool count/rank/condition gate failed")
    if min(metrics.range_by_dimension) < 0.50 or min(metrics.std_by_dimension) < 0.10:
        raise ValueError("candidate pool range/spread gate failed")
    return metrics


def select_walkers(
    *, unit: np.ndarray, log_posterior: np.ndarray, candidate_indices: np.ndarray,
    seed: int, score_focused: int = 16, walker_count: int = 64,
) -> np.ndarray:
    matrix = _require_matrix(unit, columns=18)
    scores = np.asarray(log_posterior, dtype=np.float64)
    indices = np.asarray(candidate_indices, dtype=np.int64)
    if matrix.shape[0] != 256 or scores.shape != (256,) or indices.shape != (256,):
        raise ValueError("walker selection requires one aligned 256-member pool")
    if not np.all(np.isfinite(scores)) or np.unique(indices).size != 256:
        raise ValueError("pool scores and candidate indices must be finite and unique")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    permutation = rng.permutation(256)
    tie_rank = np.empty(256, dtype=np.int64)
    tie_rank[permutation] = np.arange(256, dtype=np.int64)
    score_order = np.lexsort((tie_rank, indices, -scores))
    selected = list(map(int, score_order[:score_focused]))
    remaining = set(range(256)) - set(selected)
    while len(selected) < walker_count:
        selected_unit = matrix[np.asarray(selected)]
        best = None
        best_key = None
        for position in remaining:
            distance = float(np.min(np.linalg.norm(selected_unit - matrix[position], axis=1)))
            key = (distance, float(scores[position]), -int(tie_rank[position]), -int(indices[position]))
            if best_key is None or key > best_key:
                best_key = key
                best = position
        if best is None:
            raise RuntimeError("walker diversity fill exhausted unexpectedly")
        selected.append(int(best))
        remaining.remove(int(best))
    return np.asarray(selected, dtype=np.int64)


def validate_walker_geometry(unit: np.ndarray) -> GeometryMetrics:
    metrics = geometry_metrics(unit)
    if metrics.count != 64 or metrics.rank != 18 or metrics.condition_number > 100.0:
        raise ValueError("walker count/rank/condition gate failed")
    if min(metrics.range_by_dimension) < 0.25 or min(metrics.std_by_dimension) < 0.05:
        raise ValueError("walker range/spread gate failed")
    if metrics.minimum_pairwise_distance < 0.20:
        raise ValueError("walker minimum-distance gate failed")
    return metrics


def validate_candidate_identity_arrays(
    *, site_values: np.ndarray, target_values: np.ndarray, source_values: np.ndarray,
    candidate_indices: np.ndarray, expected_site: str, expected_target_sha256: str,
    expected_source_sha256: str,
) -> None:
    indices = np.asarray(candidate_indices, dtype=np.int64)
    if indices.ndim != 1 or not np.array_equal(indices, np.arange(indices.size, dtype=np.int64)):
        raise ValueError("candidate indices are not the exact deterministic sequence")
    if np.asarray(site_values).shape != indices.shape or not np.all(np.asarray(site_values) == expected_site):
        raise ValueError("candidate site identity mismatch")
    if np.asarray(target_values).shape != indices.shape or not np.all(
        np.asarray(target_values) == expected_target_sha256
    ):
        raise ValueError("candidate target identity mismatch")
    if np.asarray(source_values).shape != indices.shape or not np.all(
        np.asarray(source_values) == expected_source_sha256
    ):
        raise ValueError("candidate source identity mismatch")


def validate_selection_ledger(
    payload: dict[str, Any], *, schema: str, site: str, count: int,
    target_sha256: str, source_sha256: str,
) -> None:
    if payload.get("schema") != schema or payload.get("site") != site:
        raise ValueError("selection ledger schema/site mismatch")
    if payload.get("target_sha256") != target_sha256 or payload.get("source_sha256") != source_sha256:
        raise ValueError("selection ledger target/source mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) != count:
        raise ValueError("selection ledger entry count mismatch")
    position_key = "pool_position" if schema.endswith("pool-selection-ledger-v1") else "walker"
    if [row.get(position_key) for row in entries] != list(range(count)):
        raise ValueError("selection ledger positions are not deterministic")
