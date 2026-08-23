"""Versioned forcing-surrogate artifact loading and strict inference contracts."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

SUPPORTED_SCHEMA_VERSIONS = {"forcing-surrogate-v1"}
LEGACY_ARTIFACT_NAME = "surrogate_forcing_artifacts.pkl"


def _resolve_artifact_path(path_arg: Union[str, Path]) -> Path:
    path = Path(path_arg).expanduser().resolve()
    if path.is_file():
        return path
    if not path.is_dir():
        raise FileNotFoundError(f"Forcing-surrogate artifact path does not exist: {path}")
    manifest_path = path / "artifact_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        name = str(manifest.get("artifact_filename", "")).strip()
        if name:
            candidate = path / name
            if candidate.is_file():
                return candidate
            raise FileNotFoundError(
                f"Artifact manifest names missing file '{name}' in {path}"
            )
    legacy = path / LEGACY_ARTIFACT_NAME
    if legacy.is_file():
        return legacy
    candidates = sorted(path.glob("forcing_surrogate_*.pkl"))
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError(
        f"Unable to resolve one forcing artifact in {path}; "
        f"legacy={legacy.name}, versioned_candidates={[p.name for p in candidates]}"
    )


def _require_exact_keys(mapping: Mapping[str, Any], expected: Sequence[str], label: str) -> None:
    actual = list(mapping)
    expected_list = list(expected)
    if actual != expected_list:
        raise ValueError(
            f"{label} keys/order mismatch: supplied={actual}, required={expected_list}"
        )


def _feature_order_error(supplied: Sequence[str], required: Sequence[str]) -> ValueError:
    supplied_list = list(supplied)
    required_list = list(required)
    first_mismatch: Optional[int] = None
    for i, (left, right) in enumerate(zip(supplied_list, required_list)):
        if left != right:
            first_mismatch = i
            break
    if first_mismatch is None and len(supplied_list) != len(required_list):
        first_mismatch = min(len(supplied_list), len(required_list))
    missing = [name for name in required_list if name not in supplied_list]
    unexpected = [name for name in supplied_list if name not in required_list]
    return ValueError(
        "Feature order mismatch. "
        f"supplied={supplied_list}; required={required_list}; "
        f"first_mismatch={first_mismatch}; missing={missing}; unexpected={unexpected}"
    )


def require_exact_feature_order(
    supplied: Sequence[str],
    required: Sequence[str],
) -> None:
    if list(supplied) != list(required):
        raise _feature_order_error(supplied, required)


def validate_versioned_forcing_artifact(artifact: Mapping[str, Any]) -> None:
    schema_version = str(artifact.get("schema_version", ""))
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported forcing artifact schema_version={schema_version!r}; "
            f"supported={sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    if not str(artifact.get("release_version", "")).strip():
        raise ValueError("Artifact is missing release_version")
    targets = list(artifact.get("target_order", []))
    if targets != ["SR"]:
        raise ValueError(
            f"Artifact target_order mismatch: supplied={targets}, required=['SR']"
        )
    for key in ("models", "x_scaler", "y_scaler"):
        value = artifact.get(key)
        if not isinstance(value, Mapping):
            raise ValueError(f"Artifact is missing mapping '{key}'")
        _require_exact_keys(value, targets, f"artifact[{key!r}]")
    layout = artifact.get("training_layout")
    if not isinstance(layout, Mapping):
        raise ValueError("Artifact is missing training_layout mapping")
    ordered = list(layout.get("ordered_feature_names", []))
    if not ordered:
        raise ValueError("Artifact ordered_feature_names must not be empty")
    schema_hash = str(layout.get("ordered_feature_schema_sha256", "")).strip()
    if not schema_hash:
        raise ValueError("Artifact is missing ordered_feature_schema_sha256")
    fit_scope = artifact.get("fit_scope")
    if not isinstance(fit_scope, Mapping) or str(fit_scope.get("kind", "")) != "full_data":
        raise ValueError("Artifact fit_scope.kind must be 'full_data'")
    parameter_metadata = artifact.get("parameter_metadata")
    if not isinstance(parameter_metadata, Mapping):
        raise ValueError("Artifact is missing parameter_metadata")
    names = list(parameter_metadata.get("physical_names", []))
    aliases = list(parameter_metadata.get("aliases", []))
    pmin = list(parameter_metadata.get("ensemble_pmin", []))
    pmax = list(parameter_metadata.get("ensemble_pmax", []))
    if not names or not (len(names) == len(aliases) == len(pmin) == len(pmax)):
        raise ValueError("Artifact parameter metadata lengths are inconsistent")
    if len(set(names)) != len(names) or len(set(aliases)) != len(aliases):
        raise ValueError("Artifact parameter names/aliases must be unique")
    if aliases != [f"parm_{i}" for i in range(len(names))]:
        raise ValueError("Artifact parameter aliases are not canonical parm_N order")
    if np.any(np.asarray(pmin, dtype=float) > np.asarray(pmax, dtype=float)):
        raise ValueError("Artifact parameter bounds contain min > max")


def load_forcing_surrogate_artifact(
    artifact_path: Union[str, Path],
    *,
    allow_legacy: bool = False,
) -> Tuple[Dict[str, Any], Path]:
    """Load a trusted-source pickle and validate versioned artifacts.

    Pickle loading can execute code. Callers must only load artifacts from trusted sources.
    """
    path = _resolve_artifact_path(artifact_path)
    with path.open("rb") as fp:
        artifact = pickle.load(fp)
    if not isinstance(artifact, dict):
        raise ValueError(f"Forcing artifact is not a dictionary: {path}")
    if "schema_version" in artifact:
        validate_versioned_forcing_artifact(artifact)
    elif not allow_legacy:
        raise ValueError(f"Legacy unversioned artifact is not allowed: {path}")
    else:
        for key in ("models", "x_scaler", "y_scaler", "training_layout"):
            if key not in artifact:
                raise ValueError(f"Legacy forcing artifact missing required key '{key}': {path}")
    return artifact, path


def predict_versioned_forcing(
    artifact: Mapping[str, Any],
    X: np.ndarray,
) -> np.ndarray:
    validate_versioned_forcing_artifact(artifact)
    matrix = np.asarray(X, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError(f"X must be 2-D, got shape {matrix.shape}")
    required_cols = len(artifact["training_layout"]["ordered_feature_names"])
    if matrix.shape[1] != required_cols:
        raise ValueError(
            f"X must have {required_cols} columns in locked schema order, got {matrix.shape[1]}"
        )
    if np.any(~np.isfinite(matrix)):
        raise ValueError("X contains non-finite values")
    outputs = []
    for target in artifact["target_order"]:
        scaled = artifact["x_scaler"][target].transform(matrix)
        pred_scaled = artifact["models"][target].predict(scaled)
        pred = artifact["y_scaler"][target].inverse_transform(
            np.asarray(pred_scaled).reshape(-1, 1)
        ).ravel()
        if np.any(~np.isfinite(pred)):
            raise ValueError(f"Non-finite prediction for target {target}")
        outputs.append(pred)
    return np.column_stack(outputs)
