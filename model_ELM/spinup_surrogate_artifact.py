"""Versioned spinup-surrogate artifact loading and strict inference contracts."""
from __future__ import annotations

import json
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from .surrogate_NN_Spinup import build_spinup_inference_features

SUPPORTED_SCHEMA_VERSIONS = {"spinup-surrogate-v1"}
LEGACY_ARTIFACT_NAME = "surrogate_spinup_artifacts.pkl"


def _resolve_artifact_path(path_arg: Union[str, Path]) -> Path:
    path = Path(path_arg).expanduser().resolve()
    if path.is_file():
        return path
    if not path.is_dir():
        raise FileNotFoundError(f"Spinup-surrogate artifact path does not exist: {path}")
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
    candidates = sorted(path.glob("spinup_surrogate_*.pkl"))
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError(
        f"Unable to resolve one spinup artifact in {path}; "
        f"legacy={legacy.name}, versioned_candidates={[p.name for p in candidates]}"
    )


def _require_exact_keys(mapping: Mapping[str, Any], expected: Sequence[str], label: str) -> None:
    actual = list(mapping)
    expected_list = list(expected)
    if actual != expected_list:
        raise ValueError(
            f"{label} keys/order mismatch: supplied={actual}, required={expected_list}"
        )


def validate_versioned_artifact(artifact: Mapping[str, Any]) -> None:
    schema_version = str(artifact.get("schema_version", ""))
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported spinup artifact schema_version={schema_version!r}; "
            f"supported={sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    targets = list(artifact.get("target_order", []))
    if targets != ["TOTSOMC", "TOTSOMN"]:
        raise ValueError(
            f"Artifact target_order mismatch: supplied={targets}, "
            "required=['TOTSOMC', 'TOTSOMN']"
        )
    for key in ("models", "x_scaler", "y_scaler"):
        value = artifact.get(key)
        if not isinstance(value, Mapping):
            raise ValueError(f"Artifact is missing mapping '{key}'")
        _require_exact_keys(value, targets, f"artifact[{key!r}]")
    layout = artifact.get("training_layout")
    if not isinstance(layout, Mapping):
        raise ValueError("Artifact is missing training_layout mapping")
    selected = list(layout.get("input_feature_names", []))
    complete = list(layout.get("input_feature_names_all", []))
    if not selected or not complete:
        raise ValueError("Artifact feature orders must not be empty")
    indices = [int(v) for v in layout.get("selected_feature_indices", [])]
    if [complete[i] for i in indices] != selected:
        raise ValueError("Artifact selected-feature indices do not reproduce selected order")
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


def load_spinup_surrogate_artifact(
    artifact_path: Union[str, Path],
    *,
    allow_legacy: bool = True,
) -> Tuple[Dict[str, Any], Path]:
    """Load a trusted-source pickle and validate versioned artifacts.

    Pickle loading can execute code. Callers must only load artifacts from trusted sources.
    """
    path = _resolve_artifact_path(artifact_path)
    with path.open("rb") as fp:
        artifact = pickle.load(fp)
    if not isinstance(artifact, dict):
        raise ValueError(f"Spinup artifact is not a dictionary: {path}")
    if "schema_version" in artifact:
        validate_versioned_artifact(artifact)
    elif not allow_legacy:
        raise ValueError(f"Legacy unversioned artifact is not allowed: {path}")
    else:
        for key in ("models", "x_scaler", "y_scaler", "training_layout"):
            if key not in artifact:
                raise ValueError(f"Legacy spinup artifact missing required key '{key}': {path}")
    return artifact, path


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
        f"first_mismatch={first_mismatch}; missing={missing}; unexpected={unexpected}; "
        f"correct --feature-subset value={','.join(required_list)}"
    )


def require_exact_feature_order(
    supplied: Sequence[str],
    required: Sequence[str],
) -> None:
    if list(supplied) != list(required):
        raise _feature_order_error(supplied, required)


def normalize_physical_parameters(
    artifact: Mapping[str, Any],
    values: Union[Sequence[float], Mapping[str, float], np.ndarray],
) -> np.ndarray:
    metadata = artifact["parameter_metadata"]
    names = list(metadata["physical_names"])
    if isinstance(values, Mapping):
        supplied_names = list(values)
        missing = [name for name in names if name not in values]
        extra = [name for name in supplied_names if name not in names]
        if missing or extra:
            raise ValueError(
                f"Named parameters mismatch: required={names}; supplied={supplied_names}; "
                f"missing={missing}; extra={extra}"
            )
        arr = np.asarray([[float(values[name]) for name in names]], dtype=np.float64)
    else:
        arr = np.asarray(values, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.ndim != 2 or arr.shape[1] != len(names):
            raise ValueError(
                f"Positional parameters must have shape (n, {len(names)}) in physical order "
                f"{names}; got {arr.shape}"
            )
    if np.any(~np.isfinite(arr)):
        raise ValueError("Parameters contain non-finite values")
    pmin = np.asarray(metadata["ensemble_pmin"], dtype=np.float64)
    pmax = np.asarray(metadata["ensemble_pmax"], dtype=np.float64)
    low = np.argwhere(arr < pmin.reshape(1, -1))
    high = np.argwhere(arr > pmax.reshape(1, -1))
    if low.size or high.size:
        violations = []
        for row, col in np.vstack([low, high]).tolist():
            violations.append(
                {
                    "row": int(row),
                    "parameter": names[int(col)],
                    "value": float(arr[row, col]),
                    "min": float(pmin[col]),
                    "max": float(pmax[col]),
                }
            )
        raise ValueError(f"Parameters outside ensemble_pmin/pmax: {violations}")
    return arr


def parse_physical_parameter_json(text: str) -> Any:
    """Parse JSON while rejecting duplicate object keys before mapping normalization."""
    def reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        duplicates = []
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        if duplicates:
            raise ValueError(f"Duplicate parameter name(s) in JSON: {duplicates}")
        return result

    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def _warn_empirical_ranges(
    artifact: Mapping[str, Any],
    X_selected: np.ndarray,
) -> Sequence[str]:
    selected_names = list(artifact["training_layout"]["input_feature_names"])
    ranges = artifact.get("feature_ranges", {}).get("selected", {})
    messages = []
    for col, name in enumerate(selected_names):
        bounds = ranges.get(name)
        if not isinstance(bounds, Mapping):
            continue
        lo = float(bounds["min"])
        hi = float(bounds["max"])
        values = X_selected[:, col]
        if np.any(values < lo) or np.any(values > hi):
            message = (
                f"Feature '{name}' is within declared parameter bounds where applicable but "
                f"outside empirical training range [{lo}, {hi}]: "
                f"observed=[{float(np.min(values))}, {float(np.max(values))}]"
            )
            warnings.warn(message, UserWarning, stacklevel=3)
            messages.append(message)
    return messages


def build_selected_inference_matrix(
    artifact: Mapping[str, Any],
    parameters: Union[Sequence[float], Mapping[str, float], np.ndarray],
    surface: Sequence[float],
    climatology: Sequence[float],
    feature_subset: Sequence[str],
) -> Tuple[np.ndarray, Sequence[str]]:
    validate_versioned_artifact(artifact)
    layout = artifact["training_layout"]
    required = list(layout["input_feature_names"])
    require_exact_feature_order(feature_subset, required)
    params = normalize_physical_parameters(artifact, parameters)
    surface_arr = np.asarray(surface, dtype=np.float64)
    clim_arr = np.asarray(climatology, dtype=np.float64)
    n_surface = int(layout["n_surface"])
    n_clim = int(layout["n_climatology"])
    if surface_arr.ndim == 1:
        if surface_arr.size != n_surface:
            raise ValueError(f"surface must have length {n_surface}, got {surface_arr.size}")
        surface_rows = np.tile(surface_arr.reshape(1, -1), (params.shape[0], 1))
    elif surface_arr.ndim == 2 and surface_arr.shape == (params.shape[0], n_surface):
        surface_rows = surface_arr
    else:
        raise ValueError(
            f"surface must have shape ({n_surface},) or ({params.shape[0]}, {n_surface}), "
            f"got {surface_arr.shape}"
        )
    if clim_arr.ndim == 1:
        if clim_arr.size != n_clim:
            raise ValueError(f"climatology must have length {n_clim}, got {clim_arr.size}")
        clim_rows = np.tile(clim_arr.reshape(1, -1), (params.shape[0], 1))
    elif clim_arr.ndim == 2 and clim_arr.shape == (params.shape[0], n_clim):
        clim_rows = clim_arr
    else:
        raise ValueError(
            f"climatology must have shape ({n_clim},) or ({params.shape[0]}, {n_clim}), "
            f"got {clim_arr.shape}"
        )
    if np.any(~np.isfinite(surface_rows)) or np.any(~np.isfinite(clim_rows)):
        raise ValueError("Surface/climatology inputs contain non-finite values")
    complete = np.empty((params.shape[0], params.shape[1] + n_surface + n_clim), dtype=np.float64)
    complete[:, : params.shape[1]] = params
    complete[:, params.shape[1] : params.shape[1] + n_surface] = surface_rows
    complete[:, params.shape[1] + n_surface :] = clim_rows
    indices = np.asarray(layout["selected_feature_indices"], dtype=np.int64)
    selected = complete[:, indices]
    messages = _warn_empirical_ranges(artifact, selected)
    return selected, messages


def predict_versioned_spinup(
    artifact: Mapping[str, Any],
    X_selected: np.ndarray,
) -> np.ndarray:
    validate_versioned_artifact(artifact)
    X = np.asarray(X_selected, dtype=np.float64)
    if X.ndim != 2:
        raise ValueError(f"X_selected must be 2-D, got {X.shape}")
    required_cols = len(artifact["training_layout"]["input_feature_names"])
    if X.shape[1] != required_cols:
        raise ValueError(f"X_selected must have {required_cols} columns, got {X.shape[1]}")
    outputs = []
    for target in artifact["target_order"]:
        scaled = artifact["x_scaler"][target].transform(X)
        pred_scaled = artifact["models"][target].predict(scaled)
        pred = artifact["y_scaler"][target].inverse_transform(
            np.asarray(pred_scaled).reshape(-1, 1)
        ).ravel()
        if np.any(~np.isfinite(pred)):
            raise ValueError(f"Non-finite prediction for target {target}")
        outputs.append(pred)
    return np.column_stack(outputs)


def case_inference_components(
    case: Any,
    artifact: Mapping[str, Any],
    *,
    spinup_case: Optional[Any] = None,
    surface_member: Optional[int] = None,
) -> Dict[str, Any]:
    return build_spinup_inference_features(
        case,
        dict(artifact["training_layout"]),
        spinup_case=spinup_case,
        surface_member=surface_member,
    )
