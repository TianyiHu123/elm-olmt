#!/usr/bin/env python3
"""Iter013 Stage A: TIM vs Iter012 initialization-cloud comparison for one site."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wasserstein_distance

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import build_coupling_target

PARAMS = [
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
OVERLAP_RADIUS = 0.05
SEEDS = (9009, 9010, 9011)

SITE_CONFIG = {
    "ABBY": {
        "resolution": "daily",
        "case": "ABBY_ppe6_I20TRCNPRDCTCBC",
        "target_sha256": "bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd",
        "pool_sha256": "982350b16e17202acb4f2b82ab40c26e24c31dff159bb68dafbd6d8cc69a2d19",
        "ledger_sha256": "ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b",
        "tim_pool_sha256": "b19cbe90bdc746a4c2bf577fc2dc4877a32d89ee6bf77d76b6058c3f9085ad4a",
        "tim_bundle_sha256": {
            9009: "37f51011638e93ef1420d092d7f97bbd8e6bfa24342d205fcc09b9d5a9d8716a",
            9010: "49a32268e72a183414e2ba684717b1b7675c84f4ebf12b2ffd23df850c9f69cb",
            9011: "8c30198df99da7225f9c3235866c3020fef8d1e7a9349494149ddcfa11d14e0c",
        },
        "highlight": ["sigma_SR"],
    },
    "JERC": {
        "resolution": "hourly",
        "case": "JERC_ppe6_I20TRCNPRDCTCBC",
        "target_sha256": "26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196",
        "pool_sha256": "32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96",
        "ledger_sha256": "25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d",
        "tim_pool_sha256": "fcd909188789ab97b222773fc21f2a60e401a730f16e95edeee1e7aac49140e8",
        "tim_bundle_sha256": {
            9009: "394902f2c2378a6793196f226c7cf136872a2631012f559ba857c989c47bd8fe",
            9010: "86fa8a3a732be080454bb451ab025cf604c1c8c0a98ffbdce26ed2b46d3870d6",
            9011: "fa19ed47a533f540e88992c1eac6346f46478192ed85b1132222ac08599f063e",
        },
        "highlight": ["k_s1", "k_s2", "k_s3", "k_s4", "k_l1", "rf_l3s3"],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")


def normalize(states: np.ndarray, pmin: np.ndarray, pmax: np.ndarray) -> np.ndarray:
    return (states - pmin) / (pmax - pmin)


def row_keys(states: np.ndarray) -> list[bytes]:
    return [np.asarray(row, dtype=np.float64).tobytes() for row in states]


def unique_topk(
    states: np.ndarray, logp: np.ndarray, count: int
) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(logp)[::-1]
    selected_states: list[np.ndarray] = []
    selected_logp: list[float] = []
    seen: set[bytes] = set()
    for index in order:
        key = np.asarray(states[index], dtype=np.float64).tobytes()
        if key in seen:
            continue
        seen.add(key)
        selected_states.append(np.asarray(states[index], dtype=float))
        selected_logp.append(float(logp[index]))
        if len(selected_states) >= count:
            break
    require(len(selected_states) == count, f"unable to collect {count} unique top states")
    return np.asarray(selected_states, dtype=float), np.asarray(selected_logp, dtype=float)


def intersection_fraction(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    a_keys = set(row_keys(a))
    b_keys = set(row_keys(b))
    overlap = a_keys & b_keys
    return {
        "count_a": float(len(a_keys)),
        "count_b": float(len(b_keys)),
        "intersection_count": float(len(overlap)),
        "intersection_fraction_of_a": float(len(overlap) / max(len(a_keys), 1)),
    }


def pairwise_mean_distance(points: np.ndarray) -> float:
    if len(points) < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(len(points)):
        deltas = points[i + 1 :] - points[i]
        if len(deltas) == 0:
            continue
        dists = np.sqrt(np.sum(deltas * deltas, axis=1))
        total += float(np.sum(dists))
        count += int(len(dists))
    return total / max(count, 1)


def nearest_neighbor_distances(query: np.ndarray, reference: np.ndarray) -> np.ndarray:
    if len(query) == 0:
        return np.asarray([], dtype=float)
    if len(reference) == 0:
        return np.full(len(query), np.inf, dtype=float)
    distances = np.empty(len(query), dtype=float)
    for i, row in enumerate(query):
        deltas = reference - row
        distances[i] = float(np.sqrt(np.min(np.sum(deltas * deltas, axis=1))))
    return distances


def within_cloud_mean_nn(points: np.ndarray) -> float:
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i, row in enumerate(points):
        others = np.concatenate([points[:i], points[i + 1 :]], axis=0)
        total += float(np.min(np.sqrt(np.sum((others - row) ** 2, axis=1))))
    return total / len(points)


def cloud_stats(name: str, normalized: np.ndarray) -> dict[str, Any]:
    return {
        "name": name,
        "n": int(len(normalized)),
        "mean": normalized.mean(axis=0).tolist(),
        "std": normalized.std(axis=0, ddof=0).tolist(),
        "range": np.ptp(normalized, axis=0).tolist(),
        "p05": np.quantile(normalized, 0.05, axis=0).tolist(),
        "p95": np.quantile(normalized, 0.95, axis=0).tolist(),
        "width_05_95": (
            np.quantile(normalized, 0.95, axis=0) - np.quantile(normalized, 0.05, axis=0)
        ).tolist(),
        "centroid": normalized.mean(axis=0).tolist(),
        "mean_pairwise_distance": pairwise_mean_distance(normalized),
        "mean_nearest_neighbor_distance": within_cloud_mean_nn(normalized),
        "mean_spread": float(np.mean(np.ptp(normalized, axis=0))),
        "max_spread": float(np.max(np.ptp(normalized, axis=0))),
    }


def compare_clouds(
    left_name: str,
    left: np.ndarray,
    right_name: str,
    right: np.ndarray,
) -> dict[str, Any]:
    left_nn = nearest_neighbor_distances(left, right)
    right_nn = nearest_neighbor_distances(right, left)
    wasserstein = [
        float(wasserstein_distance(left[:, j], right[:, j])) for j in range(left.shape[1])
    ]
    return {
        "left": left_name,
        "right": right_name,
        "centroid_euclidean_distance": float(
            np.linalg.norm(left.mean(axis=0) - right.mean(axis=0))
        ),
        "mean_pairwise_distance_left": pairwise_mean_distance(left),
        "mean_pairwise_distance_right": pairwise_mean_distance(right),
        "mean_nearest_neighbor_left_to_right": float(np.mean(left_nn)),
        "mean_nearest_neighbor_right_to_left": float(np.mean(right_nn)),
        "overlap_fraction_left_to_right": float(np.mean(left_nn <= OVERLAP_RADIUS)),
        "overlap_fraction_right_to_left": float(np.mean(right_nn <= OVERLAP_RADIUS)),
        "per_parameter_wasserstein": wasserstein,
        "max_per_parameter_wasserstein": float(np.max(wasserstein)),
        "wasserstein_by_parameter": {
            name: value for name, value in zip(PARAMS, wasserstein)
        },
    }


def classify_geometry(
    walker_comparison: dict[str, Any],
    pool_comparison: dict[str, Any],
) -> str:
    max_w = walker_comparison["max_per_parameter_wasserstein"]
    walker_overlap = walker_comparison["overlap_fraction_left_to_right"]
    pool_overlap = pool_comparison["overlap_fraction_left_to_right"]
    left_mpd = walker_comparison["mean_pairwise_distance_left"]
    right_mpd = walker_comparison["mean_pairwise_distance_right"]
    if max_w <= OVERLAP_RADIUS and walker_overlap >= 0.80:
        return "coincide"
    if pool_overlap >= 0.80 and right_mpd >= 2.0 * left_mpd:
        return "tim_nested_in_iter012_pool"
    if walker_overlap < 0.20 and max_w > OVERLAP_RADIUS:
        return "separated"
    return "inconclusive_geometry"


def classify_selection(fraction: float) -> str:
    if fraction >= 0.80:
        return "rank_dominated"
    if fraction < 0.50:
        return "diversity_dominated"
    return "mixed_rank_and_diversity"


def load_site_arrays(site: str, cfg: dict[str, Any], args: argparse.Namespace):
    site_l = site.lower()
    pool_path = Path(getattr(args, f"{site_l}_pool"))
    ledger_path = Path(getattr(args, f"{site_l}_ledger"))
    tim_pool_path = Path(getattr(args, f"{site_l}_tim_pool"))
    require(sha256(pool_path) == cfg["pool_sha256"], f"{site} pool hash mismatch")
    require(sha256(ledger_path) == cfg["ledger_sha256"], f"{site} ledger hash mismatch")
    require(sha256(tim_pool_path) == cfg["tim_pool_sha256"], f"{site} TIM pool hash mismatch")

    pool = np.load(pool_path, allow_pickle=False)
    ledger = np.load(ledger_path, allow_pickle=False)
    tim_pool = np.load(tim_pool_path, allow_pickle=False)
    pool_states = np.asarray(pool["physical_states"], dtype=float)
    pool_logp = np.asarray(pool["physical_log_posterior"], dtype=float)
    ledger_states = np.asarray(ledger["states"], dtype=float)
    ledger_logp = np.asarray(ledger["log_posterior"], dtype=float)
    tim_pool_states = np.asarray(tim_pool["physical_chain"], dtype=float)

    walker_by_seed: dict[int, np.ndarray] = {}
    for seed in SEEDS:
        ledger_json = Path(getattr(args, f"{site_l}_selection_{seed}"))
        require(ledger_json.is_file(), f"missing selection ledger {ledger_json}")
        payload = json.loads(ledger_json.read_text(encoding="utf-8"))
        states = np.asarray(payload["selected_physical_states"], dtype=float)
        require(states.shape == (64, 15), f"{site} seed {seed} walker shape {states.shape}")
        walker_by_seed[seed] = states

    tim_walkers: dict[int, np.ndarray] = {}
    for seed in SEEDS:
        bundle = Path(getattr(args, f"{site_l}_tim_bundle_{seed}"))
        require(sha256(bundle) == cfg["tim_bundle_sha256"][seed], f"{site} TIM bundle {seed} hash")
        arr = np.asarray(np.load(bundle, allow_pickle=False)["initial_state"], dtype=float)
        require(arr.shape == (64, 15), f"{site} TIM bundle {seed} shape {arr.shape}")
        tim_walkers[seed] = arr

    return {
        "pool_states": pool_states,
        "pool_logp": pool_logp,
        "ledger_states": ledger_states,
        "ledger_logp": ledger_logp,
        "tim_pool_states": tim_pool_states,
        "walker_by_seed": walker_by_seed,
        "tim_walkers": tim_walkers,
    }


def plot_overlays(
    path: Path,
    clouds: dict[str, np.ndarray],
    highlight: list[str],
) -> None:
    if path.exists():
        raise FileExistsError(path)
    fig, axes = plt.subplots(5, 3, figsize=(14, 16), constrained_layout=True)
    names = list(clouds.keys())
    for axis_index, (ax, name) in enumerate(zip(axes.ravel(), PARAMS)):
        series = [clouds[label][:, axis_index] for label in names]
        parts = ax.violinplot(series, showmeans=True, showextrema=False)
        for body in parts["bodies"]:
            body.set_alpha(0.55)
        ax.set_xticks(range(1, len(names) + 1))
        ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
        title = name
        if name in highlight:
            title = f"{name} *"
        ax.set_title(title)
        ax.set_ylim(0.0, 1.0)
    fig.suptitle("Prior-normalized initialization clouds")
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, choices=["ABBY", "JERC"])
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    for site in ("abby", "jerc"):
        parser.add_argument(f"--{site}-pool", type=Path)
        parser.add_argument(f"--{site}-ledger", type=Path)
        parser.add_argument(f"--{site}-tim-pool", type=Path)
        for seed in SEEDS:
            parser.add_argument(f"--{site}-selection-{seed}", type=Path)
            parser.add_argument(f"--{site}-tim-bundle-{seed}", type=Path)
    args = parser.parse_args()
    site = args.site
    cfg = SITE_CONFIG[site]
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    for name in (
        "geometry.json",
        "common_target_logp.json",
        "topk_counterfactual.json",
        "classification.json",
        "parameter_overlay.png",
    ):
        if (out / name).exists():
            raise FileExistsError(out / name)

    arrays = load_site_arrays(site, cfg, args)
    target = build_coupling_target(
        cases=[cfg["case"]],
        resolution=cfg["resolution"],
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    require(
        target["identity"]["sha256"] == cfg["target_sha256"],
        f"{site} target fingerprint mismatch",
    )
    require(target["parameter_names"] == PARAMS, f"{site} parameter order mismatch")
    pmin = np.asarray(target["pmin"], dtype=float)
    pmax = np.asarray(target["pmax"], dtype=float)

    for label, states in (
        ("pool", arrays["pool_states"]),
        ("tim_pool", arrays["tim_pool_states"]),
        *[(f"walker_{seed}", arrays["walker_by_seed"][seed]) for seed in SEEDS],
        *[(f"tim_walker_{seed}", arrays["tim_walkers"][seed]) for seed in SEEDS],
    ):
        require(np.all(np.isfinite(states)), f"{site} {label} non-finite")
        require(np.all(states > pmin) and np.all(states < pmax), f"{site} {label} OOB")

    tim_pool_keys = set(row_keys(arrays["tim_pool_states"]))
    for seed, states in arrays["tim_walkers"].items():
        missing = [i for i, key in enumerate(row_keys(states)) if key not in tim_pool_keys]
        require(not missing, f"{site} TIM seed {seed} walkers not in TIM pool: {missing[:5]}")

    walker_union = np.vstack([arrays["walker_by_seed"][seed] for seed in SEEDS])
    tim_walker_union = np.vstack([arrays["tim_walkers"][seed] for seed in SEEDS])

    norm = {
        "tim_pool": normalize(arrays["tim_pool_states"], pmin, pmax),
        "tim_walkers": normalize(tim_walker_union, pmin, pmax),
        "iter012_pool": normalize(arrays["pool_states"], pmin, pmax),
        "iter012_walkers": normalize(walker_union, pmin, pmax),
    }
    for seed in SEEDS:
        norm[f"tim_walkers_{seed}"] = normalize(arrays["tim_walkers"][seed], pmin, pmax)
        norm[f"iter012_walkers_{seed}"] = normalize(
            arrays["walker_by_seed"][seed], pmin, pmax
        )

    stats = {name: cloud_stats(name, values) for name, values in norm.items()}
    walker_cmp = compare_clouds(
        "tim_walkers", norm["tim_walkers"], "iter012_walkers", norm["iter012_walkers"]
    )
    pool_cmp = compare_clouds(
        "tim_walkers", norm["tim_walkers"], "iter012_pool", norm["iter012_pool"]
    )
    pool_to_pool = compare_clouds(
        "tim_pool", norm["tim_pool"], "iter012_pool", norm["iter012_pool"]
    )
    tim_pool_to_iter012_walkers = compare_clouds(
        "tim_pool", norm["tim_pool"], "iter012_walkers", norm["iter012_walkers"]
    )
    geometry = {
        "schema": "spinup-forcing-coupling-iter013-geometry-v1",
        "site": site,
        "resolution": cfg["resolution"],
        "parameter_names": PARAMS,
        "overlap_radius": OVERLAP_RADIUS,
        "highlight_parameters": cfg["highlight"],
        "cloud_stats": stats,
        "comparisons": {
            "tim_walkers_vs_iter012_walkers": walker_cmp,
            "tim_walkers_vs_iter012_pool": pool_cmp,
            "tim_pool_vs_iter012_pool": pool_to_pool,
            "tim_pool_vs_iter012_walkers": tim_pool_to_iter012_walkers,
        },
        "status": "pass",
    }
    write_json(out / "geometry.json", geometry)

    def evaluate_logp(states: np.ndarray) -> np.ndarray:
        values = np.empty(len(states), dtype=float)
        for i, row in enumerate(states):
            values[i] = float(target["log_posterior"](row))
        require(np.all(np.isfinite(values)), "common-target logp non-finite")
        return values

    tim_pool_logp = evaluate_logp(arrays["tim_pool_states"])
    tim_walker_logp = evaluate_logp(tim_walker_union)
    stored_pool_logp = arrays["pool_logp"]
    stored_walker_logp_parts: list[np.ndarray] = []
    for seed in SEEDS:
        ledger_json = Path(getattr(args, f"{site.lower()}_selection_{seed}"))
        payload = json.loads(ledger_json.read_text(encoding="utf-8"))
        if "stored_physical_log_posterior" in payload:
            values = np.asarray(payload["stored_physical_log_posterior"], dtype=float)
        elif "reevaluated_physical_log_posterior" in payload:
            values = np.asarray(payload["reevaluated_physical_log_posterior"], dtype=float)
        else:
            raise RuntimeError(f"{site} seed {seed} selection ledger lacks stored logp")
        require(values.shape == (64,), f"{site} seed {seed} stored logp shape")
        require(np.all(np.isfinite(values)), f"{site} seed {seed} stored logp non-finite")
        stored_walker_logp_parts.append(values)
    stored_walker_logp = np.concatenate(stored_walker_logp_parts)

    def percentiles(values: np.ndarray) -> dict[str, float]:
        return {
            "p05": float(np.quantile(values, 0.05)),
            "p50": float(np.quantile(values, 0.50)),
            "p95": float(np.quantile(values, 0.95)),
            "mean": float(np.mean(values)),
            "n": int(len(values)),
        }

    common_target = {
        "schema": "spinup-forcing-coupling-iter013-common-target-logp-v1",
        "site": site,
        "resolution": cfg["resolution"],
        "target_sha256": target["identity"]["sha256"],
        "clouds": {
            "tim_pool_under_iter012_target": percentiles(tim_pool_logp),
            "tim_walkers_under_iter012_target": percentiles(tim_walker_logp),
            "iter012_pool_stored": percentiles(stored_pool_logp),
            "iter012_walkers_stored": percentiles(stored_walker_logp),
        },
        "median_difference_tim_walkers_minus_iter012_walkers": float(
            np.median(tim_walker_logp) - np.median(stored_walker_logp)
        ),
        "status": "pass",
    }
    write_json(out / "common_target_logp.json", common_target)

    top640_states, top640_logp = unique_topk(
        arrays["ledger_states"], arrays["ledger_logp"], 640
    )
    top64_states, top64_logp = unique_topk(
        arrays["ledger_states"], arrays["ledger_logp"], 64
    )
    pool_vs_top640 = intersection_fraction(arrays["pool_states"], top640_states)
    walker_vs_top64 = {
        str(seed): intersection_fraction(arrays["walker_by_seed"][seed], top64_states)
        for seed in SEEDS
    }
    selection_fraction = pool_vs_top640["intersection_fraction_of_a"]
    topk = {
        "schema": "spinup-forcing-coupling-iter013-topk-counterfactual-v1",
        "site": site,
        "pool_vs_ledger_top640": pool_vs_top640,
        "walkers_vs_ledger_top64": walker_vs_top64,
        "actual_pool_spread": {
            "mean": float(np.mean(np.ptp(norm["iter012_pool"], axis=0))),
            "max": float(np.max(np.ptp(norm["iter012_pool"], axis=0))),
        },
        "top640_spread": {
            "mean": float(np.mean(np.ptp(normalize(top640_states, pmin, pmax), axis=0))),
            "max": float(np.max(np.ptp(normalize(top640_states, pmin, pmax), axis=0))),
        },
        "top64_spread": {
            "mean": float(np.mean(np.ptp(normalize(top64_states, pmin, pmax), axis=0))),
            "max": float(np.max(np.ptp(normalize(top64_states, pmin, pmax), axis=0))),
        },
        "top640_logp_percentiles": percentiles(top640_logp),
        "top64_logp_percentiles": percentiles(top64_logp),
        "status": "pass",
    }
    write_json(out / "topk_counterfactual.json", topk)

    geometry_class = classify_geometry(walker_cmp, pool_cmp)
    selection_class = classify_selection(selection_fraction)
    classification = {
        "schema": "spinup-forcing-coupling-iter013-classification-v1",
        "site": site,
        "geometry_class": geometry_class,
        "selection_class": selection_class,
        "geometry_inputs": {
            "max_per_parameter_wasserstein_walkers": walker_cmp[
                "max_per_parameter_wasserstein"
            ],
            "overlap_tim_walkers_to_iter012_walkers": walker_cmp[
                "overlap_fraction_left_to_right"
            ],
            "overlap_tim_walkers_to_iter012_pool": pool_cmp[
                "overlap_fraction_left_to_right"
            ],
            "mean_pairwise_distance_tim_walkers": walker_cmp[
                "mean_pairwise_distance_left"
            ],
            "mean_pairwise_distance_iter012_walkers": walker_cmp[
                "mean_pairwise_distance_right"
            ],
        },
        "selection_inputs": {
            "pool_intersection_fraction_of_actual_640": selection_fraction,
            "walker_intersection_fractions": {
                seed: walker_vs_top64[seed]["intersection_fraction_of_a"]
                for seed in walker_vs_top64
            },
        },
        "status": "pass",
    }
    write_json(out / "classification.json", classification)

    plot_overlays(
        out / "parameter_overlay.png",
        {
            "TIM pool": norm["tim_pool"],
            "TIM walk": norm["tim_walkers"],
            "I012 pool": norm["iter012_pool"],
            "I012 walk": norm["iter012_walkers"],
        },
        cfg["highlight"],
    )
    print(
        f"ANALYZE_PASS site={site} geometry={geometry_class} selection={selection_class}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
