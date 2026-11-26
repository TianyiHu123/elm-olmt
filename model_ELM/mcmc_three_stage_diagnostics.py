"""Pilot diagnostics and immutable continuation gates for three-stage MCMC."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import emcee
import numpy as np

from .mcmc_prior import Prior18
from .mcmc_three_stage_initialization import geometry_metrics, physical_to_unit
from .mcmc_three_stage_sampler import BLOB_DTYPE


@dataclass(frozen=True)
class ContinuationGate:
    pass_gate: bool
    reasons: tuple[str, ...]
    fatal_reasons: tuple[str, ...]
    limitation_reasons: tuple[str, ...]
    iteration: int
    unique_states: int
    rank: int
    condition_number: float
    overall_numerical_rejection_rate: float
    maximum_walker_numerical_rejection_rate: float
    peak_rss_gib: float
    projected_total_hours: float
    projected_site_storage_gib: float
    projected_total_storage_gib: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def continuation_outcome(gate: ContinuationGate) -> str:
    """Map the immutable continuation gate without weakening fatal failures."""

    if gate.fatal_reasons:
        return "iter004_validation_failed"
    if gate.limitation_reasons:
        return "validated_with_nonfatal_limitation"
    if gate.pass_gate and not gate.reasons:
        return "continue"
    raise ValueError("continuation gate classification is internally inconsistent")


def _numerical_rejection_rates(blobs: np.ndarray) -> tuple[float, float]:
    if blobs.dtype != BLOB_DTYPE or blobs.ndim != 2:
        raise ValueError("sampler blobs must use the locked structured dtype and shape")
    rejected = blobs["reason_code"] != 0
    return float(np.mean(rejected)), float(np.max(np.mean(rejected, axis=0)))


def _proposal_rejection_rates(path: Path | str, *, nwalkers: int = 64) -> tuple[float, float, int]:
    counts = np.zeros(nwalkers, dtype=np.int64)
    rejected = np.zeros(nwalkers, dtype=np.int64)
    total = 0
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            walker = int(row["walker"])
            if walker < 0 or walker >= nwalkers:
                raise ValueError("proposal ledger walker index is out of range")
            counts[walker] += 1
            total += 1
            blob = row.get("blob")
            if blob is not None and int(blob["reason_code"]) != 0:
                rejected[walker] += 1
    if total == 0 or np.any(counts == 0):
        raise ValueError("proposal ledger is empty or incomplete")
    rates = rejected / counts
    return float(rejected.sum() / total), float(np.max(rates)), int(total)


def proposal_rejection_rates(path: Path | str, *, nwalkers: int = 64) -> tuple[float, float, int]:
    """Public validated proposal-ledger rejection accounting."""

    return _proposal_rejection_rates(path, nwalkers=nwalkers)


def evaluate_continuation_gate(
    *, prior: Prior18, backend_path: Path | str, proposal_ledger_path: Path | str,
    peak_rss_gib: float,
    projected_total_hours: float, projected_site_storage_gib: float,
    projected_total_storage_gib: float,
) -> ContinuationGate:
    backend = emcee.backends.HDFBackend(str(backend_path), read_only=True)
    if int(backend.iteration) != 128:
        raise ValueError("continuation gate requires exactly 128 completed steps")
    sampler_state = np.asarray(backend.get_last_sample().coords, dtype=np.float64)
    physical = prior.coordinate_transform.sampler_to_physical(sampler_state)
    if not np.all(np.asarray(prior.support_mask(physical), dtype=bool)):
        raise ValueError("continuation state left exact physical prior support")
    unit = physical_to_unit(prior, physical)
    geometry = geometry_metrics(unit)
    unique_states = int(np.unique(np.asarray(physical, dtype="<f8"), axis=0).shape[0])
    overall_rejection, maximum_walker_rejection, _ = _proposal_rejection_rates(
        proposal_ledger_path, nwalkers=sampler_state.shape[0]
    )
    fatal_reasons = []
    limitation_reasons = []
    if unique_states < 19:
        fatal_reasons.append("fewer_than_19_unique_current_states")
    if geometry.rank < 18:
        fatal_reasons.append("current_state_rank_below_18")
    if geometry.condition_number > 1.0e12:
        fatal_reasons.append("current_state_condition_above_1e12")
    if overall_rejection > 0.50:
        fatal_reasons.append("overall_numerical_rejection_above_0.50")
    if maximum_walker_rejection > 0.90:
        fatal_reasons.append("walker_numerical_rejection_above_0.90")
    if peak_rss_gib > 18.0:
        fatal_reasons.append("peak_rss_above_18_gib")
    if projected_total_hours > 5.5:
        limitation_reasons.append("projected_runtime_above_5.5_hours")
    if projected_site_storage_gib > 4.0:
        limitation_reasons.append("projected_site_storage_above_4_gib")
    if projected_total_storage_gib > 9.0:
        limitation_reasons.append("projected_total_storage_above_9_gib")
    reasons = fatal_reasons + limitation_reasons
    return ContinuationGate(
        pass_gate=not reasons,
        reasons=tuple(reasons),
        fatal_reasons=tuple(fatal_reasons),
        limitation_reasons=tuple(limitation_reasons),
        iteration=128,
        unique_states=unique_states,
        rank=geometry.rank,
        condition_number=geometry.condition_number,
        overall_numerical_rejection_rate=overall_rejection,
        maximum_walker_numerical_rejection_rate=maximum_walker_rejection,
        peak_rss_gib=float(peak_rss_gib),
        projected_total_hours=float(projected_total_hours),
        projected_site_storage_gib=float(projected_site_storage_gib),
        projected_total_storage_gib=float(projected_total_storage_gib),
    )


def summarize_pilot(
    *, prior: Prior18, backend_path: Path | str, proposal_ledger_path: Path | str,
) -> dict[str, Any]:
    backend = emcee.backends.HDFBackend(str(backend_path), read_only=True)
    chain = np.asarray(backend.get_chain(flat=False), dtype=np.float64)
    log_prob = np.asarray(backend.get_log_prob(flat=False), dtype=np.float64)
    blobs = np.asarray(backend.get_blobs(flat=False))
    physical = prior.coordinate_transform.sampler_to_physical(chain)
    acceptance = np.asarray(backend.accepted, dtype=np.float64) / float(backend.iteration)
    overall_rejection, maximum_walker_rejection, proposal_count = _proposal_rejection_rates(
        proposal_ledger_path, nwalkers=chain.shape[1]
    )
    if proposal_count != int(backend.iteration) * int(chain.shape[1]):
        raise ValueError("proposal ledger does not contain exactly one row per walker-step proposal")
    moved = np.any(np.any(chain[1:] != chain[:-1], axis=2), axis=0) if chain.shape[0] > 1 else np.zeros(chain.shape[1], dtype=bool)
    limitations = []
    if float(np.median(acceptance)) < 0.05 or float(np.median(acceptance)) > 0.80:
        limitations.append("median_acceptance_outside_0.05_0.80")
    if float(np.mean(acceptance == 0.0)) > 0.25:
        limitations.append("more_than_25_percent_zero_acceptance_walkers")
    if int(np.sum(moved)) < 48:
        limitations.append("fewer_than_48_walkers_moved")
    autocorrelation = None
    preliminary_ess = None
    autocorrelation_error = None
    try:
        tau = np.asarray(emcee.autocorr.integrated_time(chain, quiet=False), dtype=float)
        autocorrelation = tau.tolist()
        preliminary_ess = (chain.shape[0] * chain.shape[1] / tau).tolist()
    except emcee.autocorr.AutocorrError as exc:
        autocorrelation_error = str(exc)
    return {
        "schema": "mcmc-three-stage-pilot-summary-v1",
        "iteration": int(backend.iteration),
        "chain_shape": list(chain.shape),
        "physical_shape": list(physical.shape),
        "log_probability_shape": list(log_prob.shape),
        "acceptance_fraction": acceptance.tolist(),
        "acceptance_median": float(np.median(acceptance)),
        "walkers_moved": int(np.sum(moved)),
        "overall_numerical_rejection_rate": overall_rejection,
        "maximum_walker_numerical_rejection_rate": maximum_walker_rejection,
        "proposal_count": proposal_count,
        "autocorrelation_time": autocorrelation,
        "preliminary_ess": preliminary_ess,
        "autocorrelation_error": autocorrelation_error,
        "mixing_limitations": limitations,
        "convergence_claimed": False,
    }
