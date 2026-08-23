#!/usr/bin/env python
"""Validate Iter001 pilot files before production is eligible."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.surrogate_NN_Forcing import _load_forcing_layout_dict  # noqa: E402

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
REPOSITORY_COMMIT = "2648998d4ceb08ecf72859a7d5200c0e3a5eb41d"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_sha256(names: Any) -> str:
    encoded = json.dumps(list(names), ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_layout_dtype(value: Any) -> np.dtype:
    """Return a dtype for both NumPy names and legacy class-style strings."""
    raw = str(value)
    try:
        return np.dtype(raw)
    except TypeError as original_error:
        prefix = "<class 'numpy."
        suffix = "'>"
        if raw.startswith(prefix) and raw.endswith(suffix):
            name = raw[len(prefix) : -len(suffix)]
            try:
                return np.dtype(name)
            except TypeError:
                pass
        raise ValueError(f"Unsupported pilot memmap dtype representation: {raw!r}") from original_error


def finite(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{label} must be finite")


def validate_diagnostics(value: Mapping[str, Any], label: str) -> None:
    for population in ("train", "test"):
        finite(value[population]["r2"], f"{label}.{population}.r2")
        finite(value[population]["rmse"], f"{label}.{population}.rmse")
        if int(value[population]["n_rows"]) <= 0:
            raise ValueError(f"{label}.{population}.n_rows must be positive")
    finite(value["r2_gap"], f"{label}.r2_gap")
    finite(value["rmse_ratio"], f"{label}.rmse_ratio")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-dir", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--validation-source-manifest", type=Path)
    parser.add_argument("--dependency-manifest", type=Path, required=True)
    parser.add_argument("--pilot-config", type=Path, required=True)
    args = parser.parse_args()
    stats_files = list(args.pilot_dir.glob("surrogate_forcing_stats_*.json"))
    if len(stats_files) != 1:
        raise ValueError(f"Expected exactly one pilot stats JSON, found {len(stats_files)}")
    payload = json.loads(stats_files[0].read_text(encoding="utf-8"))
    if payload.get("schema") != "olmt-forcing-surrogate-stats-v2":
        raise ValueError("Unexpected pilot stats schema")
    if payload["case_names"] != CASES or payload["outvars"] != ["SR"]:
        raise ValueError("Pilot cases/target mismatch")
    if payload["split_mode"] != "random_time_window" or payload["train_fraction"] != 0.8:
        raise ValueError("Pilot split mismatch")
    if payload["split_random_state"] != 10001:
        raise ValueError("Pilot seed mismatch")
    if payload["output_label"] != "spinup_forcing_coupling_iter001_pilot":
        raise ValueError("Pilot output label mismatch")
    expected = {
        "source_manifest_sha256": sha256(args.source_manifest),
        "dependency_manifest_sha256": sha256(args.dependency_manifest),
        "submission_config_sha256": sha256(args.pilot_config),
    }
    for key, value in expected.items():
        if payload["provenance"].get(key) != value:
            raise ValueError(f"Pilot provenance mismatch for {key}")
    if payload["provenance"].get("repository_commit") != REPOSITORY_COMMIT:
        raise ValueError("Pilot repository commit mismatch")
    ordered = payload["ordered_feature_names"]
    if not ordered or len(set(ordered)) != len(ordered):
        raise ValueError("Pilot ordered schema is empty or duplicated")
    recomputed_schema_sha = schema_sha256(ordered)
    if payload["ordered_feature_schema_sha256"] != recomputed_schema_sha:
        raise ValueError("Pilot ordered schema hash mismatch")
    stats = payload["by_variable"]["SR"]
    validate_diagnostics(stats["pooled"], "pilot.pooled")
    if list(stats["by_site"]) != CASES:
        raise ValueError("Pilot per-site order mismatch")
    for case in CASES:
        validate_diagnostics(stats["by_site"][case], f"pilot.{case}")
    importance = stats["permutation_importance"]
    if importance["n_repeats"] != 8 or importance["random_state"] != 10001:
        raise ValueError("Pilot permutation configuration mismatch")
    if [row["feature"] for row in importance["features"]] != ordered:
        raise ValueError("Pilot importance feature order mismatch")
    for row in importance["features"]:
        for metric in ("test_r2_decrease", "test_rmse_increase"):
            if len(row[metric]) != 8:
                raise ValueError(f"Pilot {row['feature']} {metric} is incomplete")
            for value in row[metric]:
                finite(value, f"pilot.{row['feature']}.{metric}")
    memmap = args.pilot_dir / "X_forcing_memmap.dat"
    layout_path = args.pilot_dir / "X_forcing_memmap_layout.npz"
    artifact_path = args.pilot_dir / "surrogate_forcing_artifacts.pkl"
    for path in (memmap, layout_path, artifact_path):
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"Missing or empty pilot artifact: {path}")
    layout = _load_forcing_layout_dict(layout_path)
    if layout["case_names"] != CASES or layout["ordered_feature_names"] != ordered:
        raise ValueError("Pilot memmap layout identity/schema mismatch")
    if layout["ordered_feature_schema_sha256"] != recomputed_schema_sha:
        raise ValueError("Pilot memmap layout schema hash mismatch")
    expected_bytes = (
        int(layout["rows"])
        * int(layout["nfeatures"])
        * normalize_layout_dtype(layout["dtype_str"]).itemsize
    )
    if memmap.stat().st_size != expected_bytes:
        raise ValueError("Pilot memmap byte size does not match layout")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    if artifact["case_names"] != CASES or artifact["outvars"] != ["SR"]:
        raise ValueError("Pilot artifact identity mismatch")
    if artifact["ordered_feature_names"] != ordered:
        raise ValueError("Pilot artifact schema mismatch")
    if artifact["ordered_feature_schema_sha256"] != recomputed_schema_sha:
        raise ValueError("Pilot artifact schema hash mismatch")
    if set(artifact["models"]) != {"SR"} or set(artifact["x_scaler"]) != {"SR"} or set(artifact["y_scaler"]) != {"SR"}:
        raise ValueError("Pilot model/scaler artifact is incomplete")
    report = {
        "schema": "spinup-forcing-coupling-iter001-pilot-validation-v1",
        "gate": "pass",
        "stats_path": str(stats_files[0]),
        "stats_sha256": sha256(stats_files[0]),
        "artifact_path": str(artifact_path),
        "artifact_sha256": sha256(artifact_path),
        "memmap_path": str(memmap),
        "memmap_size": memmap.stat().st_size,
        "layout_path": str(layout_path),
        "layout_sha256": sha256(layout_path),
        "ordered_feature_schema_sha256": payload["ordered_feature_schema_sha256"],
        "training_source_manifest_path": str(args.source_manifest),
        "training_source_manifest_sha256": sha256(args.source_manifest),
        "validation_source_manifest_path": str(
            args.validation_source_manifest or args.source_manifest
        ),
        "validation_source_manifest_sha256": sha256(
            args.validation_source_manifest or args.source_manifest
        ),
    }
    output = args.pilot_dir.parent / "pilot_validation.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"PILOT_VALIDATION_PASS output={output} sha256={sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
