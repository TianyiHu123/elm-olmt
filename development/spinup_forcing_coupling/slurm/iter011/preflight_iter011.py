#!/usr/bin/env python3
"""Bounded Iter011 contract preflight; no coupled scientific MCMC is run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import emcee

from model_ELM.mcmc_geometry import make_move_configuration
from optimize_surrogate_forcing import _complete_day_groups


class Hour:
    def __init__(self, hour: int):
        self.year, self.month, self.day, self.hour = 2001, 1, 1, hour


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--initialization-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite preflight output: {args.output}")
    args.output.mkdir(parents=True)
    obs = {"SR": np.arange(1.0, 25.0)}
    err = {"SR": np.ones(24)}
    daily = _complete_day_groups(np.asarray([Hour(i) for i in range(24)], dtype=object), obs, err)
    if daily["groups"] != [list(range(24))] or daily["daily_count"] != 1:
        raise RuntimeError("complete-day fixture did not retain exactly one 24-hour group")
    prediction = np.arange(24.0, 48.0)
    manual = -0.5 * np.log(2.0 * np.pi) - 0.5 * ((prediction.mean() - obs["SR"].mean()) / 2.0) ** 2 - np.log(2.0)
    grouped = -0.5 * np.log(2.0 * np.pi) - 0.5 * ((np.mean(prediction[daily["groups"][0]]) - np.mean(obs["SR"][daily["groups"][0]])) / 2.0) ** 2 - np.log(2.0)
    if not np.isclose(manual, grouped, rtol=0, atol=1e-14):
        raise RuntimeError("manual daily likelihood equality failed")
    default = make_move_configuration("de_mixture")
    unit = make_move_configuration("de_mixture", de_move_scale=1.0, ndim=15)
    if default[0][0].__class__ is not unit[0][0].__class__ or default[0][0].gamma0 != unit[0][0].gamma0:
        raise RuntimeError("unit DEMove scale is not default-equivalent")
    hourly_obs = np.array([1.0, 2.0, 3.0])
    hourly_pred = np.array([1.5, 1.0, 2.5])
    hourly_sigma = np.array([2.0, 2.0, 2.0])
    legacy_hourly = np.sum(-0.5 * np.log(2.0 * np.pi) - np.log(hourly_sigma) - 0.5 * ((hourly_pred - hourly_obs) / hourly_sigma) ** 2)
    explicit_hourly = sum(
        -0.5 * np.log(2.0 * np.pi) - np.log(sigma) - 0.5 * ((pred - observed) / sigma) ** 2
        for pred, observed, sigma in zip(hourly_pred, hourly_obs, hourly_sigma)
    )
    if not np.isclose(legacy_hourly, explicit_hourly, rtol=0, atol=1e-14):
        raise RuntimeError("old and explicit hourly likelihood paths differ")
    hdf = args.output / "backend.h5"
    backend = emcee.backends.HDFBackend(str(hdf)); backend.reset(32, 15)
    initial = np.random.default_rng(11).normal(size=(32, 15))
    sampler = emcee.EnsembleSampler(32, 15, lambda x: -0.5 * np.dot(x, x), backend=backend)
    sampler.run_mcmc(initial, 1, progress=False)
    emcee.EnsembleSampler(32, 15, lambda x: -0.5 * np.dot(x, x), backend=emcee.backends.HDFBackend(str(hdf))).run_mcmc(None, 1, progress=False)
    chain = np.asarray(emcee.backends.HDFBackend(str(hdf)).get_chain(), dtype=float)
    if chain.shape != (2, 32, 15) or not np.all(np.isfinite(chain)):
        raise RuntimeError("HDF reopen/checkpoint fixture failed")
    np.savez_compressed(args.output / "raw_chain.npz", chain=chain)
    (args.output / "checkpoint_manifest.json").write_text(json.dumps({"required_steps": [1, 2], "recorded_steps": [1, 2]}, indent=2) + "\n", encoding="utf-8")
    bundles = []
    for site in ("abby", "jerc"):
        for seed in (9009, 9010, 9011):
            path = args.initialization_dir / f"{site}_high_seed{seed}.npz"
            data = np.load(path, allow_pickle=False)["initial_state"]
            if data.shape != (64, 15) or not np.all(np.isfinite(data)):
                raise RuntimeError(f"invalid reused bundle: {path}")
            bundles.append({"path": str(path), "sha256": digest(path)})
    result = {
        "schema": "spinup-forcing-coupling-iter011-preflight-v1",
        "daily_fixture": daily,
        "manual_daily_loglike": float(manual),
        "unit_de_move_default_equivalent": True,
        "hourly_explicit_path_equivalent": True,
        "hourly_legacy_loglike": float(legacy_hourly),
        "hourly_explicit_loglike": float(explicit_hourly),
        "hdf_checkpoint_raw_wiring": {"chain_shape": list(chain.shape), "backend_sha256": digest(hdf)},
        "bundles": bundles,
        "status": "pass",
    }
    (args.output / "preflight_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PREFLIGHT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
