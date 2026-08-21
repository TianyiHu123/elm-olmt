"""Immutable artifact writers shared by coupled MCMC execution and reporting."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_raw_chain_artifact(
    output_root: str | Path,
    *,
    chain: np.ndarray,
    log_prob: np.ndarray,
    initial_state: np.ndarray,
    parameter_names: Sequence[str],
    pmin: np.ndarray,
    pmax: np.ndarray,
    seed: int,
    sites: Sequence[str],
    nwalkers: int,
    nsteps: int,
    sampler_chain: Optional[np.ndarray] = None,
    transform_metadata: Optional[Dict[str, Any]] = None,
    move_configuration: Optional[str] = None,
    de_move_scale: float = 1.0,
    likelihood_resolution: str = "hourly",
    backend_path: Optional[str | Path] = None,
    physical_log_prob: Optional[np.ndarray] = None,
    allow_existing: bool = False,
) -> Dict[str, Any]:
    """Write or verify the raw-chain package before derived post-processing."""
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    raw_path, meta_path, hashes_path = (
        root / "raw_chain.npz", root / "raw_chain_metadata.json", root / "raw_chain_hashes.json"
    )
    payload: Dict[str, np.ndarray] = {
        "chain": np.asarray(chain, dtype=np.float64),
        "log_prob": np.asarray(log_prob, dtype=np.float64),
        "initial_state": np.asarray(initial_state, dtype=np.float64),
        "parameter_names": np.asarray(list(parameter_names), dtype="U"),
        "pmin": np.asarray(pmin, dtype=np.float64),
        "pmax": np.asarray(pmax, dtype=np.float64),
    }
    if sampler_chain is not None:
        payload["sampler_chain"] = np.asarray(sampler_chain, dtype=np.float64)
    if physical_log_prob is not None:
        payload["physical_log_prob"] = np.asarray(physical_log_prob, dtype=np.float64)
    if raw_path.exists():
        if not allow_existing or not meta_path.is_file() or not hashes_path.is_file():
            raise FileExistsError("raw-chain package already exists; refusing overwrite")
        existing = np.load(raw_path, allow_pickle=False)
        if set(existing.files) != set(payload) or any(
            not np.array_equal(np.asarray(existing[key]), value) for key, value in payload.items()
        ):
            raise ValueError("existing raw-chain package differs from recovered backend")
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        raw_hash = _sha256(raw_path)
        if metadata.get("raw_chain_sha256") != raw_hash:
            raise ValueError("existing raw-chain metadata hash mismatch on recovery")
        return metadata
    if meta_path.exists() or hashes_path.exists():
        raise ValueError("raw-chain metadata exists without the raw chain")
    temporary = root / "raw_chain.npz.tmp"
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **payload)
    temporary.replace(raw_path)
    provenance = {key: value for key in (
        "ITERATION_ID", "REPOSITORY_COMMIT", "SITE_NAME", "CASE_NAME", "OBS_PATH",
        "FORCING_ARTIFACT", "SPINUP_ARTIFACT", "SPINUP_MODE", "COUPLED_VARIANT",
        "N_WALKERS", "N_STEPS", "N_PROCESSES", "SEED", "SOURCE_MANIFEST",
        "DEPENDENCY_MANIFEST", "SUBMISSION_CONFIG", "MICROMAMBA_ENV",
    ) if (value := os.environ.get(key))}
    metadata: Dict[str, Any] = {
        "schema": "coupled-mcmc-raw-chain-v3",
        "chain_shape": list(payload["chain"].shape), "log_prob_shape": list(payload["log_prob"].shape),
        "initial_state_shape": list(payload["initial_state"].shape), "parameter_names": list(parameter_names),
        "pmin": np.asarray(pmin, float).tolist(), "pmax": np.asarray(pmax, float).tolist(),
        "seed": int(seed), "sites": list(sites), "nwalkers": int(nwalkers), "nsteps": int(nsteps),
        "transform": transform_metadata, "move_configuration": move_configuration,
        "de_move_scale": float(de_move_scale), "likelihood_resolution": likelihood_resolution,
        "backend_path": None if backend_path is None else str(backend_path),
        "provenance": provenance, "raw_chain_sha256": _sha256(raw_path),
    }
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    hashes_path.write_text(json.dumps({
        "schema": "coupled-mcmc-raw-chain-hashes-v2", "raw_chain": str(raw_path),
        "raw_chain_sha256": metadata["raw_chain_sha256"], "metadata": str(meta_path),
        "metadata_sha256": _sha256(meta_path),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"RAW_CHAIN_WRITTEN path={raw_path} sha256={metadata['raw_chain_sha256']}")
    return metadata
