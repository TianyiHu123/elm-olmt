#!/usr/bin/env python3
"""Run the bounded Iter009 sampler/HDF smoke contract on a compute node.

This deliberately uses a deterministic synthetic physical posterior.  It validates the
actual sampler-target adapter and persistence mechanics without evaluating the coupled
scientific model or making any scientific inference.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path

import emcee
import numpy as np

from model_ELM.mcmc_geometry import CoordinateTransform, make_move_configuration


N_WALKERS = 32
N_STEPS = 2
PARAMETER_NAMES = (
    "k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag",
    "rf_leaf", "rf_stem", "rf_root", "parm_11", "parm_12", "parm_13", "sigma_SR",
)
PMIN = np.array([0.01] * 8 + [0.0] * 3 + [-1.0] * 3 + [0.0], dtype=float)
PMAX = np.array([10.0] * 8 + [1.0] * 3 + [1.0] * 3 + [5.0], dtype=float)
MECHANISMS = (
    ("physical_stretch", "physical", "stretch"),
    ("transformed_stretch", "transformed", "stretch"),
    ("physical_de_mixture", "physical", "de_mixture"),
    ("transformed_de_mixture", "transformed", "de_mixture"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initial_physical(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Keep every walker comfortably inside strict bounds and use independent jitter.
    centre = (PMIN + PMAX) / 2.0
    spread = (PMAX - PMIN) * 0.2
    return centre + rng.uniform(-1.0, 1.0, size=(N_WALKERS, PMIN.size)) * spread


def verify_geometry_adapter(forcing, transform: CoordinateTransform, physical: np.ndarray) -> None:
    """Exercise the production sampler adapter and its analytic Jacobian directly."""
    sampler = transform.physical_to_sampler(physical)
    physical_log_prob = forcing.log_posterior_forcing(physical)
    sampler_log_prob = forcing.log_posterior_forcing_sampler(sampler)
    jacobian = transform.log_abs_det_dphysical_dsampler(sampler)
    if not np.isclose(sampler_log_prob - jacobian, physical_log_prob, rtol=0, atol=1.0e-12):
        raise RuntimeError("sampler target does not recover the physical target after Jacobian removal")
    numerical = []
    epsilon = 1.0e-6
    for index in range(sampler.size):
        plus = sampler.copy(); plus[index] += epsilon
        minus = sampler.copy(); minus[index] -= epsilon
        numerical.append(np.log(abs((transform.sampler_to_physical(plus)[index] - transform.sampler_to_physical(minus)[index]) / (2.0 * epsilon))))
    if not np.isclose(sum(numerical), jacobian, rtol=0, atol=1.0e-6):
        raise RuntimeError("analytic Jacobian does not match finite-difference geometry")


def run_one(root: Path, *, site: str, label: str, coordinates: str, move: str, seed: int) -> dict:
    forcing = importlib.import_module("model_ELM.MCMC_forcing")
    transform = CoordinateTransform.from_parameters(
        PARAMETER_NAMES, PMIN, PMAX, enabled=(coordinates == "transformed")
    )
    physical_initial = initial_physical(seed)
    sampler_initial = transform.physical_to_sampler(physical_initial)
    centre = (PMIN + PMAX) / 2.0
    scale = PMAX - PMIN
    original_target = forcing.log_posterior_forcing
    original_state = forcing._WORKER_STATE
    forcing.log_posterior_forcing = lambda values: -float(np.sum(((values - centre) / scale) ** 2))
    forcing._WORKER_STATE = {"coordinate_transform": transform}
    run_dir = root / f"{site.lower()}_{label}"
    run_dir.mkdir(parents=True, exist_ok=False)
    backend_path = run_dir / "backend.h5"
    try:
        verify_geometry_adapter(forcing, transform, physical_initial[0])
        backend = emcee.backends.HDFBackend(str(backend_path))
        backend.reset(N_WALKERS, PMIN.size)
        first = emcee.EnsembleSampler(
            N_WALKERS, PMIN.size, forcing.log_posterior_forcing_sampler,
            moves=make_move_configuration(move), backend=backend,
        )
        first.run_mcmc(sampler_initial, 1, progress=False)
        if backend.iteration != 1:
            raise RuntimeError(f"{site}/{label}: HDF creation did not retain one step")
        # New backend/sampler objects prove reopen and continuation rather than reusing memory.
        reopened_backend = emcee.backends.HDFBackend(str(backend_path))
        second = emcee.EnsembleSampler(
            N_WALKERS, PMIN.size, forcing.log_posterior_forcing_sampler,
            moves=make_move_configuration(move), backend=reopened_backend,
        )
        second.run_mcmc(None, 1, progress=False)
        sampler_chain = np.asarray(second.get_chain(), dtype=float)
        sampler_log_prob = np.asarray(second.get_log_prob(), dtype=float)
        physical_chain = transform.sampler_to_physical(sampler_chain)
        physical_log_prob = sampler_log_prob - transform.log_abs_det_dphysical_dsampler(sampler_chain)
        if second.iteration != N_STEPS or sampler_chain.shape != (N_STEPS, N_WALKERS, PMIN.size):
            raise RuntimeError(f"{site}/{label}: HDF continuation/finalization shape mismatch")
        if not np.all(np.isfinite(physical_chain)) or not np.all(np.isfinite(physical_log_prob)):
            raise RuntimeError(f"{site}/{label}: non-finite finalized smoke output")
        np.savez_compressed(
            run_dir / "raw_chain.npz", chain=physical_chain, sampler_chain=sampler_chain,
            log_prob=sampler_log_prob, physical_log_prob=physical_log_prob,
            initial_state=physical_initial, parameter_names=np.asarray(PARAMETER_NAMES, dtype="U"),
        )
        result = {
            "site": site, "mechanism": label, "coordinates": coordinates, "move": move,
            "nwalkers": N_WALKERS, "nsteps": N_STEPS, "backend_sha256": sha256(backend_path),
            "raw_chain_sha256": sha256(run_dir / "raw_chain.npz"), "status": "pass",
        }
        (run_dir / "finalization.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        forcing.log_posterior_forcing = original_target
        forcing._WORKER_STATE = original_state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(f"refusing to overwrite preflight output: {args.output_root}")
    args.output_root.mkdir(parents=True)
    results = []
    for site_index, site in enumerate(("ABBY", "JERC")):
        for mechanism_index, (label, coordinates, move) in enumerate(MECHANISMS):
            results.append(run_one(
                args.output_root, site=site, label=label, coordinates=coordinates, move=move,
                seed=900900 + site_index * 100 + mechanism_index,
            ))
    payload = {
        "schema": "spinup-forcing-coupling-iter009-preflight-v1",
        "mechanisms": len(MECHANISMS), "sites": ["ABBY", "JERC"],
        "nwalkers": N_WALKERS, "nsteps": N_STEPS,
        "smoke_proposals": len(results) * N_WALKERS * N_STEPS,
        "results": results,
    }
    (args.output_root / "preflight_result.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_SMOKE_PASS proposals={payload['smoke_proposals']} output={args.output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
