#!/usr/bin/env python3
"""Build immutable Iter009 physical-space initialization bundles from Iter008 chains."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maximin_indices(points: np.ndarray, count: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Deterministically select dispersed rows in normalized prior coordinates."""
    if points.shape[0] < count:
        raise ValueError(f"need {count} candidate states, found {points.shape[0]}")
    rng = np.random.default_rng(seed)
    first = int(rng.integers(points.shape[0]))
    selected = [first]
    selected_distance = [float("inf")]
    distance = np.sum((points - points[first]) ** 2, axis=1)
    while len(selected) < count:
        best = np.flatnonzero(distance == np.max(distance))
        choice = int(best[rng.integers(best.size)])
        selected.append(choice)
        selected_distance.append(float(np.sqrt(distance[choice])))
        distance = np.minimum(distance, np.sum((points - points[choice]) ** 2, axis=1))
    return np.asarray(selected, dtype=int), np.asarray(selected_distance, dtype=float)


def require_initial_state(state: np.ndarray, pmin: np.ndarray, pmax: np.ndarray) -> None:
    if state.shape != (64, pmin.size):
        raise ValueError(f"expected (64, {pmin.size}) initialization state, got {state.shape}")
    if not np.all(np.isfinite(state)) or np.any(state <= pmin) or np.any(state >= pmax):
        raise ValueError("initial state is non-finite or not strictly in bounds")
    if np.unique(state, axis=0).shape[0] != 64:
        raise ValueError("initial state contains repeated physical rows")
    centered = state - state.mean(axis=0)
    if np.linalg.matrix_rank(centered) != pmin.size:
        raise ValueError("initial state is rank deficient")
    condition = float(np.linalg.cond(centered))
    if not np.isfinite(condition) or condition > 1.0e12:
        raise ValueError(f"initial state has unacceptable condition number: {condition}")


def write_bundle(path: Path, *, state: np.ndarray, metadata: dict) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite immutable bundle: {path}")
    np.savez_compressed(path, initial_state=state)
    bundle_hash = sha256(path)
    metadata["bundle"] = str(path)
    metadata["bundle_sha256"] = bundle_hash
    path.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def build_site(raw_path: Path, outdir: Path, site: str) -> None:
    raw = np.load(raw_path, allow_pickle=False)
    chain = np.asarray(raw["chain"], dtype=float)
    log_prob = np.asarray(raw["log_prob"], dtype=float)
    pmin = np.asarray(raw["pmin"], dtype=float)
    pmax = np.asarray(raw["pmax"], dtype=float)
    if chain.shape != (4000, 64, 15) or log_prob.shape != (4000, 64):
        raise ValueError(f"unexpected Iter008 raw shape for {site}: {chain.shape}, {log_prob.shape}")
    final_chain = chain[2000:].reshape(-1, 15)
    final_logp = log_prob[2000:].reshape(-1)
    finite = np.isfinite(final_logp) & np.all(np.isfinite(final_chain), axis=1)
    finite &= np.all(final_chain > pmin, axis=1) & np.all(final_chain < pmax, axis=1)
    candidates = final_chain[finite]
    candidate_logp = final_logp[finite]
    source_indices = np.flatnonzero(finite)
    unique, unique_rows = np.unique(candidates, axis=0, return_index=True)
    unique_logp = candidate_logp[unique_rows]
    unique_source = source_indices[unique_rows]
    if unique.shape[0] < 640:
        raise ValueError(f"{site}: only {unique.shape[0]} unique finite in-bounds states")
    cutoff = np.quantile(unique_logp, 0.90)
    keep = unique_logp >= cutoff
    pool = unique[keep]
    pool_logp = unique_logp[keep]
    pool_source = unique_source[keep]
    if pool.shape[0] < 640 or np.any(np.ptp(pool, axis=0) <= 0):
        raise ValueError(f"{site}: high-likelihood pool is insufficient or has zero spread")
    normalized_pool = (pool - pmin) / (pmax - pmin)
    outdir.mkdir(parents=True, exist_ok=True)
    pool_path = outdir / f"{site.lower()}_high_likelihood_pool.npz"
    if pool_path.exists():
        raise FileExistsError(f"refusing to overwrite immutable pool: {pool_path}")
    np.savez_compressed(pool_path, physical_chain=pool, log_prob=pool_logp, source_index=pool_source)
    pool_meta = {
        "schema": "spinup-forcing-coupling-iter009-initialization-pool-v1",
        "site": site,
        "source_raw_chain": str(raw_path),
        "source_raw_chain_sha256": sha256(raw_path),
        "pool_sha256": sha256(pool_path),
        "unique_finite_in_bounds": int(unique.shape[0]),
        "top_decile_cutoff": float(cutoff),
        "pool_size": int(pool.shape[0]),
    }
    pool_path.with_suffix(".json").write_text(json.dumps(pool_meta, indent=2) + "\n", encoding="utf-8")
    for seed in (9009, 9010, 9011):
        uniform_rng = np.random.default_rng(10000 + seed)
        uniform = pmin + uniform_rng.uniform(size=(64, pmin.size)) * (pmax - pmin)
        require_initial_state(uniform, pmin, pmax)
        write_bundle(outdir / f"{site.lower()}_uniform_seed{seed}.npz", state=uniform, metadata={
            "schema": "spinup-forcing-coupling-iter009-initialization-bundle-v1", "site": site,
            "kind": "uniform-prior", "mcmc_seed": seed, "uniform_init_seed": 10000 + seed,
            "pmin": pmin.tolist(), "pmax": pmax.tolist(),
        })
        picked, distances = maximin_indices(normalized_pool, 64, 20000 + seed)
        high = pool[picked]
        require_initial_state(high, pmin, pmax)
        write_bundle(outdir / f"{site.lower()}_high_seed{seed}.npz", state=high, metadata={
            "schema": "spinup-forcing-coupling-iter009-initialization-bundle-v1", "site": site,
            "kind": "high-likelihood-maximin", "mcmc_seed": seed, "maximin_seed": 20000 + seed,
            "source_raw_flat_indices": pool_source[picked].tolist(),
            "source_log_prob": pool_logp[picked].tolist(), "pmin": pmin.tolist(), "pmax": pmax.tolist(),
            "selection_rank": list(range(1, 65)), "maximin_distance": distances.tolist(),
        })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abby-raw", required=True, type=Path)
    parser.add_argument("--jerc-raw", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    build_site(args.abby_raw, args.outdir, "ABBY")
    build_site(args.jerc_raw, args.outdir, "JERC")
    print(f"INITIALIZE_PASS outdir={args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
