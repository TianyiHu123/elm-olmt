"""Strict development-artifact contract for the staged ABBY/JERC spinup surrogate."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence, Tuple

import numpy as np

from .three_stage_data import TARGETS, require, schema_sha256, sha256_file


SCHEMA = "three-stage-spinup-development-v1"
ARTIFACT_FILENAME = "spinup_development_artifact.pkl"
MANIFEST_FILENAME = "artifact_manifest.json"


def validate_artifact(artifact: Mapping[str, Any]) -> None:
    require(str(artifact.get("schema")) == SCHEMA, "artifact schema mismatch")
    require(str(artifact.get("artifact_role")) in {"non_release_smoke", "non_release_validation"}, "artifact role mismatch")
    require(list(artifact.get("target_order", [])) == list(TARGETS), "artifact target order mismatch")
    require(str(artifact.get("target_transform")) == "natural_log", "artifact target transform mismatch")
    for key in ("models", "x_scalers", "y_scalers"):
        value = artifact.get(key)
        require(isinstance(value, Mapping), f"artifact missing mapping {key}")
        require(list(value) == list(TARGETS), f"artifact {key} key/order mismatch")
    feature_names = list(artifact.get("feature_names", []))
    require(len(feature_names) == 25 and len(set(feature_names)) == 25, "artifact feature schema mismatch")
    require(schema_sha256(feature_names) == str(artifact.get("feature_schema_sha256", "")), "artifact feature hash mismatch")
    parameter_metadata = artifact.get("parameter_metadata")
    require(isinstance(parameter_metadata, Mapping), "artifact parameter metadata missing")
    names = list(parameter_metadata.get("physical_names", []))
    aliases = list(parameter_metadata.get("aliases", []))
    lower = np.asarray(parameter_metadata.get("ensemble_pmin", []), dtype=np.float64)
    upper = np.asarray(parameter_metadata.get("ensemble_pmax", []), dtype=np.float64)
    require(len(names) == len(aliases) == lower.size == upper.size == 18, "artifact parameter metadata length mismatch")
    require(aliases == [f"parm_{index}" for index in range(18)], "artifact parameter aliases mismatch")
    require(np.all(np.isfinite(lower)) and np.all(np.isfinite(upper)) and np.all(lower <= upper), "artifact parameter bounds invalid")
    fit_scope = artifact.get("fit_scope")
    require(isinstance(fit_scope, Mapping), "artifact fit scope missing")
    train_members = list(fit_scope.get("train_member_ids", []))
    validation_members = list(fit_scope.get("validation_member_ids", []))
    require(bool(train_members) and bool(validation_members), "artifact member scopes empty")
    require(not set(train_members).intersection(validation_members), "artifact train/validation overlap")
    require(str(artifact.get("snapshot_revision")) == "r0001", "artifact snapshot revision mismatch")
    require(len(str(artifact.get("snapshot_sha256", ""))) == 64, "artifact snapshot hash missing")
    model_config = artifact.get("model_config")
    require(isinstance(model_config, Mapping), "artifact model config missing")
    expected_config = {
        "hidden_layer_sizes": [32],
        "activation": "tanh",
        "solver": "lbfgs",
        "alpha": 40.0,
        "max_iter": 800,
        "random_state": 42,
    }
    require(dict(model_config) == expected_config, "artifact model config mismatch")


def save_artifact(artifact: Mapping[str, Any], directory: Path | str) -> Tuple[Path, Path]:
    validate_artifact(artifact)
    root = Path(directory).resolve()
    root.mkdir(parents=True, exist_ok=False)
    artifact_path = root / ARTIFACT_FILENAME
    with artifact_path.open("xb") as handle:
        pickle.dump(dict(artifact), handle, protocol=pickle.HIGHEST_PROTOCOL)
    identity = {
        "schema": "three-stage-spinup-artifact-manifest-v1",
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_sha256": sha256_file(artifact_path),
        "artifact_size_bytes": artifact_path.stat().st_size,
        "artifact_schema": SCHEMA,
        "artifact_role": artifact["artifact_role"],
        "target_transform": artifact["target_transform"],
        "snapshot_revision": artifact["snapshot_revision"],
        "snapshot_sha256": artifact["snapshot_sha256"],
        "feature_schema_sha256": artifact["feature_schema_sha256"],
        "fit_scope": artifact["fit_scope"],
    }
    manifest_path = root / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact_path, manifest_path


def load_artifact(directory: Path | str) -> Tuple[Dict[str, Any], Path, Dict[str, Any]]:
    root = Path(directory).expanduser().resolve()
    manifest_path = root / MANIFEST_FILENAME
    require(manifest_path.is_file(), f"artifact manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schema") == "three-stage-spinup-artifact-manifest-v1", "artifact manifest schema mismatch")
    artifact_path = root / str(manifest.get("artifact_filename", ""))
    require(artifact_path.is_file(), f"artifact pickle missing: {artifact_path}")
    require(artifact_path.stat().st_size == int(manifest["artifact_size_bytes"]), "artifact size mismatch")
    require(sha256_file(artifact_path) == str(manifest["artifact_sha256"]), "artifact hash mismatch")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(isinstance(artifact, dict), "artifact pickle is not a dictionary")
    validate_artifact(artifact)
    require(str(manifest["feature_schema_sha256"]) == artifact["feature_schema_sha256"], "manifest feature hash mismatch")
    require(str(manifest["target_transform"]) == artifact["target_transform"], "manifest target transform mismatch")
    require(str(manifest["snapshot_sha256"]) == artifact["snapshot_sha256"], "manifest snapshot hash mismatch")
    return artifact, artifact_path, manifest


def predict_matrix(artifact: Mapping[str, Any], X: np.ndarray) -> np.ndarray:
    validate_artifact(artifact)
    matrix = np.asarray(X, dtype=np.float64)
    require(matrix.ndim == 2 and matrix.shape[1] == len(artifact["feature_names"]), "prediction matrix shape mismatch")
    require(np.all(np.isfinite(matrix)), "prediction matrix contains nonfinite values")
    outputs = []
    for target in TARGETS:
        scaled_x = artifact["x_scalers"][target].transform(matrix)
        scaled_prediction = artifact["models"][target].predict(scaled_x)
        log_prediction = artifact["y_scalers"][target].inverse_transform(
            np.asarray(scaled_prediction, dtype=np.float64).reshape(-1, 1)
        ).ravel()
        require(np.all(np.isfinite(log_prediction)), f"{target} log prediction contains nonfinite values")
        prediction = np.exp(log_prediction)
        require(np.all(np.isfinite(prediction)), f"{target} prediction contains nonfinite values")
        require(np.all(prediction > 0.0), f"{target} prediction contains nonpositive values")
        outputs.append(prediction)
    return np.column_stack(outputs)
