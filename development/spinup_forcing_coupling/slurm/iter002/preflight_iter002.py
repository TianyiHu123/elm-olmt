#!/usr/bin/env python
"""Bounded dependency/schema/import preflight for forcing-coupling Iter002.

No training, data generation, optimization, or iteration evaluation.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.forcing_surrogate_artifact import (  # noqa: E402
    load_forcing_surrogate_artifact,
    predict_versioned_forcing,
    validate_versioned_forcing_artifact,
)
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    _load_forcing_layout_dict,
    _resolve_forcing_memmap_paths,
    _schema_sha256,
)

LOCKED_MEMMAP_SIZE = 7148160000
LOCKED_MEMMAP_SHA256 = "01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6"
LOCKED_LAYOUT_SHA256 = "a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0"
LOCKED_SCHEMA_SHA256 = "cbe2daf49d74f5cc7b99caed138c8da314d42095cd8ea8a41cb762c903e93061"
LOCKED_PILOT_STATS_SHA256 = "bbe1b51ece8567b54a8437a01f907506bd11658ea029506b638674c9fba5f0e8"
LOCKED_PILOT_VALIDATION_SHA256 = "ef651685a8fbba6651a7b9fe465ef50b27a547d2fb1e3571a8f4a35241bdcc6f"
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_expected_hashes(path: Path) -> Dict[str, str]:
    expected: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split(maxsplit=1)
        expected[relative.strip()] = digest
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-hashes", required=True)
    parser.add_argument("--reuse-x-memmap", required=True)
    parser.add_argument("--reference-stats", required=True)
    parser.add_argument("--pilot-validation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    for rel in [
        "model_ELM/forcing_surrogate_artifact.py",
        "development/spinup_forcing_coupling/tools/release_forcing_surrogate.py",
        "development/spinup_forcing_coupling/tools/validate_iter002_release.py",
        "tests/test_forcing_surrogate_iter002.py",
    ]:
        path = REPO_ROOT / rel
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        print(f"AST_OK {rel}")

    expected = load_expected_hashes(Path(args.expected_hashes))
    for relative, digest in expected.items():
        path = REPO_ROOT / relative
        actual = sha256(path)
        if actual != digest:
            raise ValueError(f"Case hash mismatch for {relative}")
        print(f"CASE_HASH_OK {relative}")

    memmap_path, layout_path = _resolve_forcing_memmap_paths(Path(args.reuse_x_memmap))
    if memmap_path.stat().st_size != LOCKED_MEMMAP_SIZE:
        raise ValueError("Memmap size mismatch")
    if sha256(memmap_path) != LOCKED_MEMMAP_SHA256:
        raise ValueError("Memmap hash mismatch")
    if sha256(layout_path) != LOCKED_LAYOUT_SHA256:
        raise ValueError("Layout hash mismatch")
    layout = _load_forcing_layout_dict(layout_path)
    if list(layout["case_names"]) != CASES:
        raise ValueError("Layout case order mismatch")
    ordered = [
        *layout["forcing_feature_names"],
        *layout["parameter_names"],
        *layout["spinup_vars"],
    ]
    schema = _schema_sha256(ordered)
    if schema != LOCKED_SCHEMA_SHA256:
        raise ValueError(f"Schema hash mismatch: {schema}")
    print("MEMMAP_LAYOUT_SCHEMA_OK")

    stats_path = Path(args.reference_stats)
    validation_path = Path(args.pilot_validation)
    if sha256(stats_path) != LOCKED_PILOT_STATS_SHA256:
        raise ValueError("Pilot stats hash mismatch")
    if sha256(validation_path) != LOCKED_PILOT_VALIDATION_SHA256:
        raise ValueError("Pilot validation hash mismatch")
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    if stats.get("ordered_feature_schema_sha256") != LOCKED_SCHEMA_SHA256:
        raise ValueError("Pilot stats schema mismatch")
    print("PILOT_REFERENCE_OK")

    # Lightweight synthetic fixture for loader/predict only.
    rng = np.random.default_rng(1)
    X = rng.normal(size=(20, 3))
    y = X.sum(axis=1)
    x_scaler = StandardScaler().fit(X)
    y_scaler = StandardScaler().fit(y.reshape(-1, 1))
    model = LinearRegression().fit(
        x_scaler.transform(X), y_scaler.transform(y.reshape(-1, 1)).ravel()
    )
    artifact = {
        "release_version": "iter002-v1",
        "schema_version": "forcing-surrogate-v1",
        "target_order": ["SR"],
        "models": {"SR": model},
        "x_scaler": {"SR": x_scaler},
        "y_scaler": {"SR": y_scaler},
        "training_layout": {
            "ordered_feature_names": ["a", "b", "c"],
            "ordered_feature_schema_sha256": "fixture",
            "n_forcing_cols": 1,
            "n_params": 1,
            "n_spinup": 1,
        },
        "fit_scope": {"kind": "full_data", "rows": 20},
        "parameter_metadata": {
            "physical_names": ["p0"],
            "aliases": ["parm_0"],
            "ensemble_pmin": [0.0],
            "ensemble_pmax": [1.0],
        },
    }
    validate_versioned_forcing_artifact(artifact)
    pred = predict_versioned_forcing(artifact, np.ones((4, 3)))
    if pred.shape != (4, 1) or np.any(~np.isfinite(pred)):
        raise ValueError("Synthetic predict fixture failed")
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.pkl"
        with path.open("wb") as fp:
            pickle.dump(artifact, fp)
        loaded, _ = load_forcing_surrogate_artifact(path, allow_legacy=False)
        validate_versioned_forcing_artifact(loaded)
    print("SYNTHETIC_ARTIFACT_API_OK")

    payload: Dict[str, Any] = {
        "schema": "spinup-forcing-coupling-iter002-preflight-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cases": CASES,
        "memmap_sha256": LOCKED_MEMMAP_SHA256,
        "layout_sha256": LOCKED_LAYOUT_SHA256,
        "schema_sha256": LOCKED_SCHEMA_SHA256,
        "pilot_stats_sha256": LOCKED_PILOT_STATS_SHA256,
        "pilot_validation_sha256": LOCKED_PILOT_VALIDATION_SHA256,
        "python": sys.version.split()[0],
        "passed": True,
    }
    out = Path(args.output)
    out.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS cases=9 output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
