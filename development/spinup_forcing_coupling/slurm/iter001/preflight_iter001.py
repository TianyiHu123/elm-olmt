#!/usr/bin/env python
"""Bounded dependency/schema preflight for forcing-coupling Iter001.

This inspects identities and metadata only. It does not build the feature matrix, fit a model,
or evaluate iteration results.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import pickle
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401 - required for trusted local pickle classes
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    SPINUP_VAR_SUM,
    _collect_forcing_files,
    _restart_file,
)

CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]
FORCING_VARS = ["PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF"]
TARGET = "SR"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_identity(path: Path, *, include_hash: bool = True) -> Dict[str, Any]:
    resolved = path.resolve(strict=True)
    stat = resolved.stat()
    return {
        "path": str(resolved),
        "size": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
        "sha256": sha256(resolved) if include_hash else None,
    }


def load_expected_hashes(path: Path) -> Dict[str, str]:
    expected: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split(maxsplit=1)
        expected[relative.strip()] = digest
    return expected


def validate_forcing_files(paths: Iterable[Path]) -> Dict[str, Any]:
    identities = [file_identity(path) for path in paths]
    available = set()
    for identity in identities:
        with Dataset(identity["path"], "r") as dataset:
            available.update(str(name) for name in dataset.variables)
    missing = sorted(set(FORCING_VARS) - available)
    if missing:
        raise ValueError(f"Forcing files do not expose required variables: {missing}")
    return {"files": identities, "available_variables": sorted(available)}


def validate_restarts(case: Any, nsamples: int) -> List[Dict[str, Any]]:
    records = []
    required_components = sorted({name for names in SPINUP_VAR_SUM.values() for name in names})
    for member in range(1, nsamples + 1):
        path = _restart_file(case, member)
        identity = file_identity(path)
        with Dataset(identity["path"], "r") as dataset:
            missing = [name for name in required_components if name not in dataset.variables]
            if missing:
                raise ValueError(
                    f"Restart {identity['path']} missing required components: {missing}"
                )
            identity["components"] = {
                name: {
                    "dtype": str(dataset.variables[name].dtype),
                    "dimensions": list(dataset.variables[name].dimensions),
                    "shape": list(dataset.variables[name].shape),
                }
                for name in required_components
            }
        identity["member"] = member
        records.append(identity)
    return records


def inspect_case(case_name: str, expected_hash: str) -> Dict[str, Any]:
    path = REPO_ROOT / "pklfiles" / f"{case_name}.pkl"
    # The submitted Slurm wrapper has already run sha256sum -c over every case pickle.
    # Reuse that locked digest here rather than reading another ~19 GB inside the preflight.
    identity = file_identity(path, include_hash=False)
    identity["sha256"] = expected_hash
    with path.open("rb") as handle:
        case = pickle.load(handle)
    actual_case_name = str(getattr(case, "casename", ""))
    if actual_case_name != case_name:
        raise ValueError(f"Case identity mismatch: expected {case_name}, loaded {actual_case_name}")
    samples = np.asarray(case.samples)
    if samples.ndim != 2:
        raise ValueError(f"{case_name} samples must be 2-D, got {samples.shape}")
    nsamples = int(samples.shape[1])
    parameter_names = [str(name) for name in list(case.ensemble_parms)]
    if len(parameter_names) != samples.shape[0] or len(set(parameter_names)) != len(parameter_names):
        raise ValueError(f"{case_name} ensemble_parms is not a unique ordered samples schema")
    if TARGET not in case.output:
        raise ValueError(f"{case_name} is missing target {TARGET}")
    target = np.asarray(case.output[TARGET])
    if target.ndim != 2 or target.shape[1] != nsamples:
        raise ValueError(f"{case_name} target shape {target.shape} is incompatible with samples")
    if np.any(~np.isfinite(target)):
        raise ValueError(f"{case_name} target {TARGET} contains non-finite values")
    forcing_paths = _collect_forcing_files(Path(case.metdir))
    record = {
        "case": case_name,
        "pickle": identity,
        "samples_shape": list(samples.shape),
        "target": TARGET,
        "target_shape": list(target.shape),
        "ensemble_parms": parameter_names,
        "metdir": str(Path(case.metdir).resolve(strict=True)),
        "forcing": validate_forcing_files(forcing_paths),
        "runroot": str(Path(case.runroot).resolve(strict=True)),
        "dependcase": str(case.dependcase),
        "finidat": str(case.finidat),
        "restarts": validate_restarts(case, nsamples),
    }
    del target, samples, case
    gc.collect()
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-hashes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--micromamba-module", required=True)
    parser.add_argument("--environment-yaml", type=Path, required=True)
    args = parser.parse_args()
    if Path.cwd().resolve() != REPO_ROOT:
        raise RuntimeError(f"Preflight must run from {REPO_ROOT}")
    expected = load_expected_hashes(args.expected_hashes)
    if "/" not in args.micromamba_module:
        raise ValueError("The full preflight requires a pinned micromamba/<version> module")
    records = []
    reference_parameters: Optional[List[str]] = None
    for case_name in CASES:
        relative = f"pklfiles/{case_name}.pkl"
        if relative not in expected:
            raise ValueError(f"Missing expected pickle hash for {relative}")
        record = inspect_case(case_name, expected[relative])
        if reference_parameters is None:
            reference_parameters = record["ensemble_parms"]
        elif record["ensemble_parms"] != reference_parameters:
            raise ValueError(f"{case_name} ensemble_parms names/order differs from ABBY")
        records.append(record)
    payload = {
        "schema": "spinup-forcing-coupling-iter001-dependencies-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(REPO_ROOT),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "micromamba_module": args.micromamba_module,
        "environment_name": "OLMT_puma",
        "environment_yaml": file_identity(args.environment_yaml),
        "installed_python_distributions": {
            distribution.metadata["Name"]: distribution.version
            for distribution in sorted(
                importlib.metadata.distributions(),
                key=lambda item: str(item.metadata["Name"]).lower(),
            )
            if distribution.metadata["Name"]
        },
        "cases": records,
        "case_order": CASES,
        "target": TARGET,
        "forcing_vars": FORCING_VARS,
        "spinup_vars": list(SPINUP_VAR_SUM),
        "parameter_names": reference_parameters,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(f"PREFLIGHT_PASS cases={len(records)} output={args.output} sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
