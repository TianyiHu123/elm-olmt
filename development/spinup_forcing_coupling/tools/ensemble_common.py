"""Shared helpers for spinup-forcing-coupling MAP ensemble tools."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from emcee.autocorr import integrated_time

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")

DEFAULT_SEEDS = (9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017)

SITE_CONFIG = {
    "ABBY": {"resolution": "daily", "de_scale": "0.50", "config_dir": "daily_0.50"},
    "JERC": {"resolution": "hourly", "de_scale": "0.75", "config_dir": "hourly_0.75"},
}

K_PARAMS = ("k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag")
RF_PARAMS = ("rf_l1s1", "rf_l2s2", "rf_l3s3", "rf_s1s2", "rf_s2s3", "rf_s3s4")

ACCEPTANCE_MIN = 0.20
ACCEPTANCE_MAX = 0.50

MAP_W_CONVERGED = 0.05
SR_RMSE_EQUIVALENCE = 0.01
DECOMP_W_EQUIFINAL = 0.05


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def leaf_dir(root: Path, site: str, seed: int) -> Path:
    cfg = SITE_CONFIG[site]
    return root / "production" / site.lower() / cfg["config_dir"] / f"seed_{seed}"


def tau(chain: np.ndarray) -> np.ndarray:
    answer = np.array(
        [float(np.ravel(integrated_time(chain[:, :, i], tol=0, quiet=True))[0]) for i in range(15)]
    )
    if not np.all(np.isfinite(answer)) or np.any(answer <= 0):
        raise ValueError("non-finite physical tau")
    return answer


def skill_from_table(path: Path, series: str) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("series") == series]
    if not rows:
        raise ValueError(f"{path}: missing series {series}")
    row = rows[0]
    return {key: float(row[key]) for key in ("rmse", "bias", "r2") if key in row}


def load_leaf(root: Path, site: str, seed: int) -> dict[str, Any]:
    leaf = leaf_dir(root, site, seed)
    cfg = SITE_CONFIG[site]
    required = (
        "raw_chain.npz",
        "raw_chain_metadata.json",
        "raw_chain_hashes.json",
        "backend.h5",
        "checkpoint_manifest.json",
        "selection_ledger.json",
        "production_result.json",
        "diagnostics/walker_acceptance.csv",
        "diagnostics/skill_table.csv",
    )
    if any(not (leaf / name).is_file() for name in required):
        raise FileNotFoundError(f"{leaf}: incomplete production leaf")
    raw = np.load(leaf / "raw_chain.npz", allow_pickle=False)
    chain = np.asarray(raw["chain"], float)
    sampler = np.asarray(raw["sampler_chain"], float)
    physical_logp = np.asarray(raw["physical_log_prob"], float)
    names = [str(x) for x in raw["parameter_names"]]
    accept = np.genfromtxt(
        leaf / "diagnostics" / "walker_acceptance.csv", delimiter=",", names=True
    )["acceptance_fraction"]
    production = json.loads((leaf / "production_result.json").read_text(encoding="utf-8"))
    metadata = json.loads((leaf / "raw_chain_metadata.json").read_text(encoding="utf-8"))
    map_skill = skill_from_table(leaf / "diagnostics" / "skill_table.csv", "optimized_best")
    elm_skill = skill_from_table(leaf / "diagnostics" / "skill_table.csv", "elm_precal")
    t6000, t8000 = tau(chain[:6000]), tau(chain)
    if "best_physical_state" in production:
        map_state = np.asarray(production["best_physical_state"], float)
        map_log_posterior = float(production.get("best_physical_log_posterior", np.nan))
    else:
        flat_idx = int(np.nanargmax(physical_logp.reshape(-1)))
        map_state = chain.reshape(-1, chain.shape[-1])[flat_idx].copy()
        map_log_posterior = float(physical_logp.reshape(-1)[flat_idx])
    return {
        "site": site,
        "seed": seed,
        "resolution": cfg["resolution"],
        "de_scale": cfg["de_scale"],
        "leaf": leaf,
        "parameter_names": names,
        "pmin": np.asarray(raw["pmin"], float),
        "pmax": np.asarray(raw["pmax"], float),
        "chain": chain,
        "sampler_chain": sampler,
        "mean_acceptance": float(np.mean(accept)),
        "saturation": float(np.max(np.mean(np.abs(sampler) >= 10, axis=(0, 1)))),
        "min_steps_per_tau": float(np.min(8000 / t8000)),
        "max_tau_change": float(np.max(np.abs(t8000 - t6000) / t6000)),
        "map_state": map_state,
        "map_log_posterior": map_log_posterior,
        "map_rmse": map_skill.get("rmse", float("nan")),
        "map_bias": map_skill.get("bias", float("nan")),
        "map_r2": map_skill.get("r2", float("nan")),
        "elm_rmse": elm_skill.get("rmse", float("nan")),
        "elm_bias": elm_skill.get("bias", float("nan")),
        "elm_r2": elm_skill.get("r2", float("nan")),
        "campaign_pass": (leaf / "production_result.json").is_file()
        and metadata.get("nsteps") == 8000,
        "metadata": metadata,
        "production": production,
    }


def tier_a_result(mean_acceptance: float, campaign_pass: bool) -> tuple[bool, str]:
    if not campaign_pass:
        return False, "missing_or_incomplete_production_artifacts"
    if mean_acceptance < ACCEPTANCE_MIN:
        return False, f"acceptance_below_floor:{mean_acceptance:.6f}"
    if mean_acceptance > ACCEPTANCE_MAX:
        return False, f"acceptance_above_ceiling:{mean_acceptance:.6f}"
    return True, "tier_a_pass"


def param_indices(names: list[str], params: tuple[str, ...]) -> list[int]:
    index = {name: i for i, name in enumerate(names)}
    return [index[name] for name in params]


def normalized_widths(pmin: np.ndarray, pmax: np.ndarray) -> np.ndarray:
    return np.maximum(pmax - pmin, 1e-12)


def normalize_states(states: np.ndarray, pmin: np.ndarray, pmax: np.ndarray) -> np.ndarray:
    return (states - pmin) / normalized_widths(pmin, pmax)


def post_burn_physical_samples(leaf_data: dict[str, Any], subsample_size: int, rng: np.random.Generator) -> np.ndarray:
    chain = leaf_data["chain"]
    discard = max(int(np.ceil(np.max(integrated_time(chain, tol=0, quiet=True)) / 20)), 1)
    flat = chain[discard:].reshape(-1, chain.shape[-1])
    if len(flat) <= subsample_size:
        return flat
    return flat[rng.choice(len(flat), size=subsample_size, replace=False)]
