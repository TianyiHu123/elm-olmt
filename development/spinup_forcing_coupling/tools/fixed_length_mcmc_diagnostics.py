#!/usr/bin/env python3
"""Reusable fixed-length MCMC diagnostic helpers (Iter012/014 evaluation core).

Library functions are the contract. The CLI writes chain diagnostics JSON; it does
not apply iteration decision labels, provenance gates, or posterior promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from emcee.autocorr import integrated_time
from scipy.stats import norm, rankdata, wasserstein_distance

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import build_coupling_target

SCHEMA = "spinup-forcing-coupling-fixed-length-mcmc-diagnostics-v1"
DEFAULT_PARAMS = [
    "k_l1",
    "k_l2",
    "k_l3",
    "k_s1",
    "k_s2",
    "k_s3",
    "k_s4",
    "k_frag",
    "rf_l1s1",
    "rf_l2s2",
    "rf_l3s3",
    "rf_s1s2",
    "rf_s2s3",
    "rf_s3s4",
    "sigma_SR",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def skill(prediction: np.ndarray, observation: np.ndarray, error: np.ndarray) -> dict[str, Any]:
    mask = (
        (observation > -9000)
        & (error > 0)
        & np.isfinite(prediction)
        & np.isfinite(observation)
        & np.isfinite(error)
    )
    observed = observation[mask]
    predicted = prediction[mask]
    residual = predicted - observed
    total = np.sum((observed - np.mean(observed)) ** 2)
    correlation = (
        np.corrcoef(predicted, observed)[0, 1]
        if len(observed) > 1 and np.std(predicted) and np.std(observed)
        else np.nan
    )
    alpha = np.std(predicted) / np.std(observed) if np.std(observed) else np.nan
    beta = np.mean(predicted) / np.mean(observed) if np.mean(observed) else np.nan
    return {
        "valid_observations": int(mask.sum()),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "bias": float(np.mean(residual)),
        "r2": float(1 - np.sum(residual**2) / total) if total else np.nan,
        "kge": (
            float(
                1
                - np.sqrt(
                    (correlation - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2
                )
            )
            if np.isfinite(correlation) and np.isfinite(alpha) and np.isfinite(beta)
            else np.nan
        ),
    }


def rank_normalized_split_rhat(chains: np.ndarray) -> np.ndarray:
    nseed, nstep, nwalker, ndim = chains.shape
    half = nstep // 2
    split = (
        chains[:, : 2 * half]
        .reshape(nseed, 2, half, nwalker, ndim)
        .transpose(0, 1, 3, 2, 4)
        .reshape(-1, half, ndim)
    )
    ranked = np.empty_like(split)
    for parameter in range(ndim):
        values = split[:, :, parameter].reshape(-1)
        ranks = rankdata(values, method="average")
        ranked[:, :, parameter] = norm.ppf((ranks - 0.5) / len(values)).reshape(
            split.shape[0], half
        )
    means = np.mean(ranked, axis=1)
    variances = np.var(ranked, axis=1, ddof=1)
    between = half * np.var(means, axis=0, ddof=1)
    within = np.mean(variances, axis=0)
    return np.sqrt(((half - 1) / half * within + between / half) / within)


def split_seed_walker_chains(chains: np.ndarray) -> np.ndarray:
    nseed, nstep, nwalker, ndim = chains.shape
    half = nstep // 2
    return (
        chains[:, : 2 * half]
        .reshape(nseed, 2, half, nwalker, ndim)
        .transpose(0, 1, 3, 2, 4)
        .reshape(-1, half, ndim)
    )


def multi_chain_ess(values: np.ndarray) -> float:
    chains = np.asarray(values, dtype=float)
    chain_count, draw_count = chains.shape
    if chain_count < 2 or draw_count < 4 or not np.all(np.isfinite(chains)):
        return float("nan")
    within = float(np.mean(np.var(chains, axis=1, ddof=1)))
    between = float(draw_count * np.var(np.mean(chains, axis=1), ddof=1))
    variance_plus = (draw_count - 1) / draw_count * within + between / draw_count
    if not np.isfinite(variance_plus) or variance_plus <= 0:
        return float("nan")
    centered = chains - np.mean(chains, axis=1, keepdims=True)
    fft_length = 1 << (2 * draw_count - 1).bit_length()
    transformed = np.fft.rfft(centered, n=fft_length, axis=1)
    autocovariance = np.fft.irfft(
        transformed * np.conjugate(transformed), n=fft_length, axis=1
    )[:, :draw_count]
    autocovariance /= draw_count
    rho = np.empty(draw_count, dtype=float)
    rho[0] = 1.0
    rho[1:] = 1.0 - (within - np.mean(autocovariance[:, 1:], axis=0)) / variance_plus
    pair_sums: list[float] = []
    for start in range(0, draw_count - 1, 2):
        pair_sum = float(rho[start] + rho[start + 1])
        if pair_sum < 0:
            break
        if pair_sums and pair_sum > pair_sums[-1]:
            pair_sum = pair_sums[-1]
        pair_sums.append(pair_sum)
    tau_hat = -1.0 + 2.0 * float(np.sum(pair_sums))
    if not np.isfinite(tau_hat) or tau_hat <= 0:
        return float("nan")
    return float(min(chain_count * draw_count, chain_count * draw_count / tau_hat))


def rank_bulk_tail_ess(chains: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    split = split_seed_walker_chains(chains)
    bulk = np.empty(split.shape[-1], dtype=float)
    tail = np.empty(split.shape[-1], dtype=float)
    for parameter in range(split.shape[-1]):
        values = split[:, :, parameter]
        flat = values.reshape(-1)
        ranks = rankdata(flat, method="average")
        normalized = norm.ppf((ranks - 0.5) / len(flat)).reshape(values.shape)
        bulk[parameter] = multi_chain_ess(normalized)
        lower, upper = np.quantile(flat, [0.05, 0.95])
        lower_ess = multi_chain_ess((values <= lower).astype(float))
        upper_ess = multi_chain_ess((values >= upper).astype(float))
        tail[parameter] = min(lower_ess, upper_ess)
    return bulk, tail


def integrated_time_by_seed(chain: np.ndarray) -> tuple[np.ndarray, float | None, str | None]:
    """Return (tau, stability, error) for one (nsteps, nwalkers, ndim) physical chain."""
    nsteps = chain.shape[0]
    ndim = chain.shape[2]
    try:
        full = np.asarray(integrated_time(chain, tol=0, quiet=True), dtype=float)
        half = np.asarray(
            integrated_time(chain[: nsteps // 2], tol=0, quiet=True), dtype=float
        )
        if (
            full.shape != (ndim,)
            or half.shape != (ndim,)
            or not np.all(np.isfinite(full))
            or not np.all(np.isfinite(half))
            or np.any(full <= 0)
            or np.any(half <= 0)
        ):
            raise ValueError("non-finite or non-positive tau")
        return full, float(np.max(np.abs(full - half) / half)), None
    except Exception as exc:  # noqa: BLE001
        return np.full(ndim, np.nan), None, f"{type(exc).__name__}: {exc}"


def descriptive_discard(nsteps: int, tau_max: float | None) -> tuple[int, int | None, bool]:
    """Return (descriptive_discard, diagnostic_discard, diagnostic_window_valid)."""
    diagnostic_discard = (
        int(max(math.ceil(0.20 * nsteps), math.ceil(5 * tau_max)))
        if tau_max is not None and np.isfinite(tau_max)
        else None
    )
    diagnostic_window_valid = bool(
        diagnostic_discard is not None and diagnostic_discard < nsteps
    )
    discard = (
        diagnostic_discard if diagnostic_window_valid else int(math.ceil(0.20 * nsteps))
    )
    return int(discard), diagnostic_discard, diagnostic_window_valid


def max_cross_seed_normalized_wasserstein(
    post: np.ndarray, widths: np.ndarray
) -> float:
    nseed, _, _, ndim = post.shape
    require(nseed >= 2, "need at least two seeds for cross-seed Wasserstein")
    return max(
        wasserstein_distance(
            post[first, :, :, parameter].ravel(),
            post[second, :, :, parameter].ravel(),
        )
        / widths[parameter]
        for first in range(nseed)
        for second in range(first + 1, nseed)
        for parameter in range(ndim)
    )


def transformed_saturation(sampler_chains: list[np.ndarray], threshold: float = 10.0) -> float:
    stacked = np.concatenate(sampler_chains, axis=0)
    return float(np.max(np.mean(np.abs(stacked) >= threshold, axis=(0, 1))))


def physical_prior_edge_occupancy(
    post: np.ndarray, pmin: np.ndarray, pmax: np.ndarray, fraction: float = 0.01
) -> np.ndarray:
    widths = pmax - pmin
    return np.mean(
        (post <= pmin + fraction * widths) | (post >= pmax - fraction * widths),
        axis=(0, 1, 2),
    )


def load_raw_chain(path: Path) -> dict[str, np.ndarray]:
    payload = np.load(path, allow_pickle=False)
    require("chain" in payload.files, f"{path}: missing chain")
    chain = np.asarray(payload["chain"], dtype=float)
    sampler = (
        np.asarray(payload["sampler_chain"], dtype=float)
        if "sampler_chain" in payload.files
        else None
    )
    logp = None
    for key in ("physical_log_prob", "log_prob"):
        if key in payload.files:
            logp = np.asarray(payload[key], dtype=float)
            break
    require(chain.ndim == 3, f"{path}: chain must be (nsteps, nwalkers, ndim)")
    return {"chain": chain, "sampler_chain": sampler, "physical_log_prob": logp}


def summarize_chains(
    archives: list[dict[str, np.ndarray]],
    pmin: np.ndarray,
    pmax: np.ndarray,
    parameter_names: list[str],
) -> dict[str, Any]:
    chains = np.stack([item["chain"] for item in archives], axis=0)
    nseed, nsteps, nwalkers, ndim = chains.shape
    require(ndim == len(parameter_names), "parameter name count mismatch")
    tau_rows = []
    tau_stability = []
    tau_errors = []
    for item in archives:
        tau, stability, error = integrated_time_by_seed(item["chain"])
        tau_rows.append(tau)
        tau_stability.append(stability)
        tau_errors.append(error)
    tau = np.asarray(tau_rows)
    tau_available = bool(np.all(np.isfinite(tau)))
    tau_max = float(np.max(tau)) if tau_available else None
    discard, diagnostic_discard, window_valid = descriptive_discard(nsteps, tau_max)
    post = chains[:, discard:]
    widths = np.asarray(pmax, dtype=float) - np.asarray(pmin, dtype=float)
    wasserstein = max_cross_seed_normalized_wasserstein(post, widths)
    if window_valid:
        rhat = rank_normalized_split_rhat(post)
        bulk, tail = rank_bulk_tail_ess(post)
        steps_per_tau = post.shape[1] / tau
        diagnostics_finite = bool(
            np.all(np.isfinite(rhat))
            and np.all(np.isfinite(bulk))
            and np.all(np.isfinite(tail))
            and np.all(np.isfinite(steps_per_tau))
        )
    else:
        rhat = np.full(ndim, np.nan)
        bulk = np.full(ndim, np.nan)
        tail = np.full(ndim, np.nan)
        steps_per_tau = np.full_like(tau, np.nan)
        diagnostics_finite = False
    sampler_list = [
        item["sampler_chain"] for item in archives if item["sampler_chain"] is not None
    ]
    saturation = (
        transformed_saturation(sampler_list) if sampler_list else None
    )
    return {
        "schema": SCHEMA,
        "nseed": int(nseed),
        "nsteps": int(nsteps),
        "nwalkers": int(nwalkers),
        "ndim": int(ndim),
        "parameter_names": list(parameter_names),
        "tau_available": tau_available,
        "tau": tau.tolist(),
        "tau_stability_by_seed": tau_stability,
        "tau_errors": tau_errors,
        "descriptive_discard": int(discard),
        "diagnostic_discard": diagnostic_discard,
        "diagnostic_window_valid": window_valid,
        "diagnostics_finite": diagnostics_finite,
        "rank_normalized_split_rhat": rhat.tolist(),
        "rank_normalized_bulk_ess": bulk.tolist(),
        "quantile_tail_ess": tail.tolist(),
        "post_burn_steps_per_tau": steps_per_tau.tolist(),
        "max_cross_seed_normalized_wasserstein": float(wasserstein),
        "transformed_saturation": saturation,
        "physical_prior_edge_occupancy": physical_prior_edge_occupancy(
            post, np.asarray(pmin, dtype=float), np.asarray(pmax, dtype=float)
        ).tolist(),
        "status": "pass",
    }


def write_json(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    require(spec.get("schema") == SCHEMA, f"{args.spec}: schema mismatch")
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "mcmc_diagnostics.json"
    if result_path.exists() and not args.overwrite:
        raise FileExistsError(f"refusing to overwrite {result_path}; pass --overwrite")

    parameter_names = spec.get("parameter_names") or DEFAULT_PARAMS
    target = build_coupling_target(
        cases=[spec["case"]],
        resolution=spec["resolution"],
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    expected = spec.get("expected_target_sha256")
    if expected:
        require(target["identity"]["sha256"] == expected, "target fingerprint mismatch")
    require(target["parameter_names"] == parameter_names, "parameter order mismatch")

    archives = []
    provenance = []
    for member in spec["chains"]:
        path = Path(member["path"])
        loaded = load_raw_chain(path)
        require(np.all(np.isfinite(loaded["chain"])), f"{path}: non-finite chain")
        archives.append(loaded)
        provenance.append(
            {
                "label": member.get("label") or member.get("seed"),
                "path": str(path.resolve()),
                "sha256": sha256(path),
                "shape": list(loaded["chain"].shape),
            }
        )
    summary = summarize_chains(
        archives,
        np.asarray(target["pmin"], dtype=float),
        np.asarray(target["pmax"], dtype=float),
        parameter_names,
    )
    summary["spec_path"] = str(args.spec.resolve())
    summary["spec_sha256"] = sha256(args.spec)
    summary["target_sha256"] = target["identity"]["sha256"]
    summary["chains"] = provenance
    write_json(result_path, summary, overwrite=True)
    print(
        "FIXED_LENGTH_MCMC_DIAGNOSTICS_PASS "
        f"nseed={summary['nseed']} discard={summary['descriptive_discard']} "
        f"W={summary['max_cross_seed_normalized_wasserstein']:.4f} "
        f"output={result_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
