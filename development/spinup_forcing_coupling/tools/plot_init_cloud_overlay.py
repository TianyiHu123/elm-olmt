#!/usr/bin/env python3
"""Reusable prior-normalized pool and walker initialization-cloud overlay plots."""
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
SCHEMA = "spinup-forcing-coupling-init-cloud-overlay-v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def normalize(states: np.ndarray, pmin: np.ndarray, pmax: np.ndarray) -> np.ndarray:
    return (states - pmin) / (pmax - pmin)


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
    parameter_names: list[str],
    overlap_radius: float,
) -> dict[str, Any]:
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
        "overlap_fraction_left_to_right": float(np.mean(left_nn <= overlap_radius)),
        "overlap_fraction_right_to_left": float(np.mean(right_nn <= overlap_radius)),
        "per_parameter_wasserstein": wasserstein,
        "max_per_parameter_wasserstein": float(np.max(wasserstein)),
        "wasserstein_by_parameter": {
            name: value for name, value in zip(parameter_names, wasserstein)
        },
    }


def plot_overlays(
    path: Path,
    clouds: dict[str, np.ndarray],
    parameter_names: list[str],
    highlight: list[str],
    title: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(5, 3, figsize=(max(14, 2.5 * len(clouds)), 16), constrained_layout=True)
    names = list(clouds.keys())
    for axis_index, (ax, param) in enumerate(zip(axes.ravel(), parameter_names)):
        series = [clouds[label][:, axis_index] for label in names]
        parts = ax.violinplot(series, showmeans=True, showextrema=False)
        for body in parts["bodies"]:
            body.set_alpha(0.55)
        ax.set_xticks(range(1, len(names) + 1))
        ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
        param_title = param
        if param in highlight:
            param_title = f"{param} *"
        ax.set_title(param_title)
        ax.set_ylim(0.0, 1.0)
    fig.suptitle(title)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def load_pool_npz(path: Path) -> np.ndarray:
    payload = np.load(path, allow_pickle=False)
    if "physical_states" in payload.files:
        states = np.asarray(payload["physical_states"], dtype=float)
    elif "physical_chain" in payload.files:
        states = np.asarray(payload["physical_chain"], dtype=float)
    else:
        raise RuntimeError(f"{path}: expected physical_states or physical_chain")
    require(states.ndim == 2 and states.shape[1] == 15, f"{path}: invalid pool shape {states.shape}")
    return states


def load_selection_ledger(path: Path) -> np.ndarray:
    payload = json.loads(path.read_text(encoding="utf-8"))
    states = np.asarray(payload["selected_physical_states"], dtype=float)
    require(states.shape == (64, 15), f"{path}: walker shape {states.shape}")
    return states


def load_tim_bundle(path: Path) -> np.ndarray:
    payload = np.load(path, allow_pickle=False)
    states = np.asarray(payload["initial_state"], dtype=float)
    require(states.shape == (64, 15), f"{path}: TIM bundle shape {states.shape}")
    return states


def load_cloud_member(member: dict[str, Any]) -> np.ndarray:
    kind = member["kind"]
    path = Path(member["path"])
    require(path.is_file(), f"missing cloud member {path}")
    if kind == "pool_npz":
        return load_pool_npz(path)
    if kind == "tim_pool_npz":
        return load_pool_npz(path)
    if kind == "selection_ledger":
        return load_selection_ledger(path)
    if kind == "tim_bundle":
        return load_tim_bundle(path)
    raise RuntimeError(f"unsupported cloud member kind {kind}")


def load_cloud(cloud: dict[str, Any]) -> tuple[np.ndarray, list[dict[str, Any]]]:
    kind = cloud["kind"]
    label = cloud["label"]
    provenance: list[dict[str, Any]] = []
    if kind in {"pool_npz", "tim_pool_npz"}:
        path = Path(cloud["path"])
        states = load_pool_npz(path)
        provenance.append({"label": label, "kind": kind, "path": str(path), "sha256": sha256(path)})
        return states, provenance
    if kind == "walker_union":
        members = cloud.get("members") or []
        require(members, f"{label}: walker_union requires members")
        parts = [load_cloud_member(member) for member in members]
        states = np.vstack(parts)
        for member in members:
            path = Path(member["path"])
            provenance.append(
                {
                    "label": label,
                    "kind": member["kind"],
                    "path": str(path),
                    "sha256": sha256(path),
                }
            )
        return states, provenance
    raise RuntimeError(f"unsupported cloud kind {kind}")


def load_spec(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == SCHEMA, f"{path}: schema mismatch")
    return payload


def write_json(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="JSON overlay specification")
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    spec = load_spec(args.spec)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_path = output_dir / "parameter_overlay.png"
    stats_path = output_dir / "cloud_stats.json"
    manifest_path = output_dir / "init_cloud_overlay_manifest.json"
    for path in (plot_path, stats_path, manifest_path):
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"refusing to overwrite {path}; pass --overwrite")

    parameter_names = spec.get("parameter_names") or DEFAULT_PARAMS
    highlight = spec.get("highlight_parameters") or []
    title = spec.get("title") or "Prior-normalized initialization clouds"
    overlap_radius = float(spec.get("overlap_radius", 0.05))
    expected_target_sha256 = spec.get("expected_target_sha256")

    target = build_coupling_target(
        cases=[spec["case"]],
        resolution=spec["resolution"],
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    if expected_target_sha256:
        require(
            target["identity"]["sha256"] == expected_target_sha256,
            "target fingerprint mismatch",
        )
    require(target["parameter_names"] == parameter_names, "parameter order mismatch")
    pmin = np.asarray(target["pmin"], dtype=float)
    pmax = np.asarray(target["pmax"], dtype=float)

    normalized: dict[str, np.ndarray] = {}
    provenance: list[dict[str, Any]] = []
    for cloud in spec["clouds"]:
        label = cloud["label"]
        states, cloud_provenance = load_cloud(cloud)
        require(np.all(np.isfinite(states)), f"{label}: non-finite states")
        require(
            np.all(states > pmin) and np.all(states < pmax),
            f"{label}: states outside physical bounds",
        )
        normalized[label] = normalize(states, pmin, pmax)
        provenance.extend(cloud_provenance)

    stats = {name: cloud_stats(name, values) for name, values in normalized.items()}
    comparisons: dict[str, Any] = {}
    for pair in spec.get("pairwise_comparisons") or []:
        left = pair["left"]
        right = pair["right"]
        key = f"{left}_vs_{right}"
        comparisons[key] = compare_clouds(
            left,
            normalized[left],
            right,
            normalized[right],
            parameter_names,
            overlap_radius,
        )

    plot_overlays(plot_path, normalized, parameter_names, highlight, title)
    write_json(
        stats_path,
        {
            "schema": "spinup-forcing-coupling-init-cloud-stats-v1",
            "parameter_names": parameter_names,
            "overlap_radius": overlap_radius,
            "cloud_stats": stats,
            "comparisons": comparisons,
            "status": "pass",
        },
        overwrite=True,
    )
    write_json(
        manifest_path,
        {
            "schema": SCHEMA,
            "spec_path": str(args.spec.resolve()),
            "spec_sha256": sha256(args.spec),
            "output_dir": str(output_dir.resolve()),
            "plot_path": str(plot_path.resolve()),
            "clouds": provenance,
            "target_sha256": target["identity"]["sha256"],
            "status": "pass",
        },
        overwrite=True,
    )
    print(
        "INIT_CLOUD_OVERLAY_PASS "
        f"clouds={len(normalized)} "
        f"plot={plot_path} "
        f"comparisons={len(comparisons)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
