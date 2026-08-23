#!/usr/bin/env python3
"""MAP and cloud geometry diagnostics for equifinality vs convergence."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wasserstein_distance

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from ensemble_common import (  # noqa: E402
    DECOMP_W_EQUIFINAL,
    DEFAULT_SEEDS,
    K_PARAMS,
    MAP_W_CONVERGED,
    RF_PARAMS,
    SITE_CONFIG,
    SR_RMSE_EQUIVALENCE,
    load_leaf,
    normalize_states,
    param_indices,
    post_burn_physical_samples,
    tier_a_result,
)

SCHEMA = "spinup-forcing-coupling-ensemble-equifinality-diagnostics-v1"


def pairwise_wasserstein(states_a: np.ndarray, states_b: np.ndarray, pmin: np.ndarray, pmax: np.ndarray) -> float:
    norm_a = normalize_states(states_a, pmin, pmax)
    norm_b = normalize_states(states_b, pmin, pmax)
    values = []
    for dim in range(norm_a.shape[1]):
        values.append(wasserstein_distance(norm_a[:, dim], norm_b[:, dim]))
    return float(np.mean(values))


def classify_map_label(max_map_w: float, sr_spread: float, max_decomp_w: float, retained: int) -> str:
    if retained < 2:
        return "insufficient_retained"
    if sr_spread <= SR_RMSE_EQUIVALENCE and max_map_w < MAP_W_CONVERGED:
        return "converged"
    if sr_spread <= SR_RMSE_EQUIVALENCE and max_decomp_w >= DECOMP_W_EQUIFINAL:
        return "equifinal_candidate"
    if sr_spread <= SR_RMSE_EQUIVALENCE:
        return "mixed"
    return "mixed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", choices=sorted(SITE_CONFIG), required=True)
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--subsample", type=int, default=1000)
    parser.add_argument("--rng-seed", type=int, default=16016)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    rng = np.random.default_rng(args.rng_seed)
    healthy: list[dict[str, Any]] = []
    for seed in args.seeds:
        leaf = load_leaf(args.root, args.site, seed)
        passed, _ = tier_a_result(leaf["mean_acceptance"], leaf["campaign_pass"])
        if passed:
            healthy.append(leaf)

    map_rows: list[dict[str, Any]] = []
    cloud_rows: list[dict[str, Any]] = []
    max_map_w = 0.0
    max_decomp_w = 0.0
    if healthy:
        pmin, pmax = healthy[0]["pmin"], healthy[0]["pmax"]
        names = healthy[0]["parameter_names"]
        k_idx = param_indices(names, K_PARAMS)
        rf_idx = param_indices(names, RF_PARAMS)
        map_states = np.stack([leaf["map_state"] for leaf in healthy])
        norm_maps = normalize_states(map_states, pmin, pmax)
        for i, left in enumerate(healthy):
            for j, right in enumerate(healthy):
                if j <= i:
                    continue
                full_w = pairwise_wasserstein(
                    left["map_state"][None, :],
                    right["map_state"][None, :],
                    pmin,
                    pmax,
                )
                decomp_left = np.concatenate([left["map_state"][k_idx], left["map_state"][rf_idx]])[None, :]
                decomp_right = np.concatenate([right["map_state"][k_idx], right["map_state"][rf_idx]])[None, :]
                decomp_pmin = np.concatenate([pmin[k_idx], pmin[rf_idx]])
                decomp_pmax = np.concatenate([pmax[k_idx], pmax[rf_idx]])
                decomp_w = pairwise_wasserstein(decomp_left, decomp_right, decomp_pmin, decomp_pmax)
                max_map_w = max(max_map_w, full_w)
                max_decomp_w = max(max_decomp_w, decomp_w)
                map_rows.append(
                    {
                        "site": args.site,
                        "seed_left": left["seed"],
                        "seed_right": right["seed"],
                        "map_wasserstein_full": full_w,
                        "map_wasserstein_decomposition": decomp_w,
                        "map_rmse_delta": abs(left["map_rmse"] - right["map_rmse"]),
                    }
                )
        cloud_cache = {
            leaf["seed"]: post_burn_physical_samples(leaf, args.subsample, rng) for leaf in healthy
        }
        within = []
        for leaf in healthy:
            cloud = cloud_cache[leaf["seed"]]
            norm = normalize_states(cloud, pmin, pmax)
            spread = float(np.mean(np.std(norm, axis=0)))
            within.append(spread)
        mean_within = float(np.mean(within)) if within else 0.0
        for i, left in enumerate(healthy):
            for j, right in enumerate(healthy):
                if j <= i:
                    continue
                cloud_w = pairwise_wasserstein(cloud_cache[left["seed"]], cloud_cache[right["seed"]], pmin, pmax)
                cloud_rows.append(
                    {
                        "site": args.site,
                        "seed_left": left["seed"],
                        "seed_right": right["seed"],
                        "cloud_wasserstein_full": cloud_w,
                        "between_within_ratio": cloud_w / max(mean_within, 1e-12),
                    }
                )

    rmse_values = [leaf["map_rmse"] for leaf in healthy]
    sr_spread = float(max(rmse_values) - min(rmse_values)) if rmse_values else float("nan")
    map_label = classify_map_label(max_map_w, sr_spread, max_decomp_w, len(healthy))
    cloud_label = map_label
    if healthy and map_rows:
        if max_map_w >= MAP_W_CONVERGED and sr_spread <= SR_RMSE_EQUIVALENCE and max_decomp_w >= DECOMP_W_EQUIFINAL:
            cloud_label = "equifinal_candidate" if map_label != "converged" else map_label
        elif max_map_w < MAP_W_CONVERGED:
            cloud_label = "confirmed" if map_label == "converged" else "unconfirmed"
        else:
            cloud_label = "confirmed" if map_label == cloud_label else "revised"

    args.output_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = args.output_dir / "map_cross_seed_matrix.csv"
    cloud_path = args.output_dir / "seed_cloud_geometry.json"
    diagnosis_path = args.output_dir / "equifinality_diagnosis.json"
    if diagnosis_path.exists() and not args.overwrite:
        raise FileExistsError(diagnosis_path)
    if map_rows:
        with matrix_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(map_rows[0].keys()))
            writer.writeheader()
            writer.writerows(map_rows)
    diagnosis = {
        "schema": SCHEMA,
        "site": args.site,
        "retained_tier_a_seeds": [leaf["seed"] for leaf in healthy],
        "map_sr_rmse_spread": sr_spread,
        "max_pairwise_map_wasserstein": max_map_w,
        "max_pairwise_decomposition_wasserstein": max_decomp_w,
        "map_label": map_label,
        "cloud_confirmation": cloud_label,
        "thresholds": {
            "map_w_converged": MAP_W_CONVERGED,
            "sr_rmse_equivalence": SR_RMSE_EQUIVALENCE,
            "decomposition_w_equifinal": DECOMP_W_EQUIFINAL,
        },
        "cloud_pairs": cloud_rows,
    }
    cloud_path.write_text(json.dumps({"pairs": cloud_rows}, indent=2) + "\n", encoding="utf-8")
    diagnosis_path.write_text(json.dumps(diagnosis, indent=2) + "\n", encoding="utf-8")
    print(
        f"EQUIFINALITY_DIAG_PASS site={args.site} label={map_label} retained={len(healthy)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
