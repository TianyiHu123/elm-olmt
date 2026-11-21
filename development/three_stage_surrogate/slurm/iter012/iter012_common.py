#!/usr/bin/env python
"""Shared Iter012 SR GPP-input ablation utilities."""
from __future__ import annotations

import csv
import json
import pickle
import sys
import warnings
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, schema_sha256, sha256_file
from model_ELM.three_stage_sr import FEATURE_COUNT, HOURS, _metrics, feature_names, write_json
from model_ELM.three_stage_sr_release import (
    DAY_COUNT,
    DEVELOPMENT_MEMBERS,
    TRAIN_MEMBERS,
    VALIDATION_MEMBERS,
    _load_split_manifest,
    _positions,
    load_raw,
    validate_raw,
    validate_split_design,
)

ARM_IDS = ("A", "B", "C")
BASE_FEATURE_COUNT = FEATURE_COUNT - 1
TRUE_GPP_NAME = "GPP_ELM_true_diagnostic"
MODEL_PARAMETER_COUNTS = {"A": 8929, "B": 9025, "C": 9025}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_arms(config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(config["arm_manifest"])
    require(sha256_file(path) == config["arm_manifest_sha256"], "arm manifest hash mismatch")
    payload = read_json(path)
    require(payload["schema"] == "three-stage-sr-iter012-arms-v1", "arm schema mismatch")
    require(payload["arm_count"] == len(payload["arms"]) == 3, "arm count mismatch")
    require(tuple(item["arm_id"] for item in payload["arms"]) == ARM_IDS, "arm IDs mismatch")
    expected = [
        ("A", "none", 43, True),
        ("B", "published_predicted_same_hour", 44, True),
        ("C", "true_elm_same_hour", 44, False),
    ]
    observed = [
        (item["arm_id"], item["gpp_input"], int(item["feature_count"]), bool(item["deployable"]))
        for item in payload["arms"]
    ]
    require(observed == expected, "arm matrix mismatch")
    model = payload["model_config"]
    require(model["hidden_layer_sizes"] == [96, 48], "hidden layers mismatch")
    require(model["activation"] == "tanh" and float(model["alpha"]) == 0.01, "model mismatch")
    require(payload["split_ids"] == list(range(20)) and payload["production_fit_count"] == 60, "fit design mismatch")
    for key in ("fixed_test_allowed", "spinup_execution_allowed", "gpp_execution_allowed", "all_development_fit_allowed", "release_allowed"):
        require(payload[key] is False, f"arm boundary mismatch: {key}")
    return payload


def arm_by_id(payload: Mapping[str, Any], arm_id: str) -> dict[str, Any]:
    require(arm_id in ARM_IDS, "arm ID invalid")
    result = dict(payload["arms"][ARM_IDS.index(arm_id)])
    require(result["arm_id"] == arm_id, "arm lookup mismatch")
    return result


def model_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload["model_config"])
    result["hidden_layer_sizes"] = tuple(result["hidden_layer_sizes"])
    return result


def expected_feature_schemas(snapshot: ThreeStageSnapshot) -> dict[str, Any]:
    established = list(feature_names(snapshot))
    base = established[:BASE_FEATURE_COUNT]
    schemas = {
        "A": base,
        "B": established,
        "C": [*base, TRUE_GPP_NAME],
    }
    return {
        "schema": "three-stage-sr-iter012-feature-schemas-v1",
        "arms": {
            arm_id: {
                "feature_count": len(names),
                "feature_names": names,
                "feature_schema_sha256": schema_sha256(names),
                "gpp_input": {"A": "none", "B": "published_predicted_same_hour", "C": "true_elm_same_hour"}[arm_id],
                "deployable": arm_id in ("A", "B"),
            }
            for arm_id, names in schemas.items()
        },
    }


def load_true_gpp(path: Path) -> np.memmap:
    return np.memmap(path, mode="r", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS))


def feature_block(X: np.memmap, true_gpp: np.memmap, arm_id: str, site_index: int, positions: np.ndarray) -> np.ndarray:
    require(arm_id in ARM_IDS, "arm invalid")
    if arm_id == "A":
        return np.asarray(X[site_index, positions, :, :BASE_FEATURE_COUNT], dtype=np.float32).reshape(-1, BASE_FEATURE_COUNT)
    if arm_id == "B":
        return np.asarray(X[site_index, positions], dtype=np.float32).reshape(-1, FEATURE_COUNT)
    base = np.asarray(X[site_index, positions, :, :BASE_FEATURE_COUNT], dtype=np.float32).reshape(-1, BASE_FEATURE_COUNT)
    gpp = np.asarray(true_gpp[site_index, positions], dtype=np.float32).reshape(-1)
    result = np.empty((base.shape[0], FEATURE_COUNT), dtype=np.float32)
    result[:, :BASE_FEATURE_COUNT] = base
    result[:, -1] = gpp
    return result


def selected_members(config: Mapping[str, Any], layout: Mapping[str, Any], split_id: int):
    item = _load_split_manifest(config)["splits"][split_id]
    train = list(item["train_member_ids"])
    validation = list(item["validation_member_ids"])
    return train, validation, _positions(layout, train), _positions(layout, validation)


def validate_contract(config: Mapping[str, Any], *, full_raw_hashes: bool, full_true_gpp_hash: bool) -> dict[str, Any]:
    require(config["schema"] == "three-stage-sr-iter012-config-v1", "config schema mismatch")
    for key in ("fixed_test_allowed", "spinup_execution_allowed", "gpp_execution_allowed", "all_development_fit_allowed", "release_allowed"):
        require(config[key] is False, f"config boundary mismatch: {key}")
    repo = Path(config["repository_root"])
    require(sha256_file(repo / "development/three_stage_surrogate/PLAN.md") == config["plan_sha256"], "plan mismatch")
    for path_key, hash_key in (
        ("spinup_release_manifest", "spinup_release_manifest_sha256"),
        ("predicted_cn_handoff", "predicted_cn_sha256"),
        ("gpp_release_manifest", "gpp_release_manifest_sha256"),
        ("predicted_gpp_handoff", "predicted_gpp_sha256"),
    ):
        require(sha256_file(Path(config[path_key])) == config[hash_key], f"dependency mismatch: {path_key}")
    load_arms(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split mismatch")
    validate_split_design(snapshot, _load_split_manifest(config))
    raw_report = validate_raw(config, Path(config["raw_directory"]), full_hashes=full_raw_hashes)
    raw_manifest = read_json(Path(config["raw_directory"]) / "raw_manifest.json")
    for field, key in (("layout_sha256", "raw_layout_sha256"), ("x_sha256", "raw_x_sha256"), ("y_sha256", "raw_y_sha256"), ("time_sha256", "raw_time_sha256")):
        require(raw_manifest[field] == config[key], f"raw identity mismatch: {field}")
    schema_path = Path(config["feature_schemas"])
    require(sha256_file(schema_path) == config["feature_schemas_sha256"], "feature schema hash mismatch")
    require(read_json(schema_path) == expected_feature_schemas(snapshot), "feature schemas mismatch")
    true_gpp_path = Path(config["true_gpp_file"])
    require(true_gpp_path.stat().st_size == len(SITES) * DEVELOPMENT_MEMBERS * HOURS * 4, "true GPP size mismatch")
    if full_true_gpp_hash:
        require(sha256_file(true_gpp_path) == config["true_gpp_sha256"], "true GPP hash mismatch")
    true_gpp = load_true_gpp(true_gpp_path)
    require(np.all(np.isfinite(true_gpp[:, (0, 409, 818)][:, :, (0, 719, HOURS - 1)])), "true GPP sample invalid")
    return {
        "schema": "three-stage-sr-iter012-contract-validation-v1",
        "result": "pass",
        "arm_count": 3,
        "production_fit_count": 60,
        "raw_full_hashes": bool(full_raw_hashes),
        "true_gpp_full_hash": bool(full_true_gpp_hash),
        "raw_validation": raw_report,
        "fixed_test_access": False,
    }


def fit_scalers(X, y, true_gpp, arm_id, positions, chunk_rows):
    x_scaler = StandardScaler(copy=True)
    y_scaler = StandardScaler(copy=True)
    member_chunk = max(1, int(chunk_rows) // HOURS)
    for site_index in range(len(SITES)):
        for start in range(0, positions.size, member_chunk):
            selected = positions[start:start + member_chunk]
            x_scaler.partial_fit(feature_block(X, true_gpp, arm_id, site_index, selected))
            y_scaler.partial_fit(np.asarray(y[site_index, selected], dtype=np.float32).reshape(-1, 1))
    return x_scaler, y_scaler


def materialize_train(X, y, true_gpp, arm_id, positions, x_scaler, y_scaler, output):
    width = int(x_scaler.n_features_in_)
    rows = len(SITES) * TRAIN_MEMBERS * HOURS
    scaled_x = np.memmap(output / "X_train_scaled_float32.dat", mode="w+", dtype=np.float32, shape=(rows, width))
    scaled_y = np.memmap(output / "y_train_scaled_float32.dat", mode="w+", dtype=np.float32, shape=(rows,))
    cursor = 0
    for site_index in range(len(SITES)):
        for position in positions:
            end = cursor + HOURS
            block = feature_block(X, true_gpp, arm_id, site_index, np.asarray([position], dtype=np.int64))
            scaled_x[cursor:end] = x_scaler.transform(block).astype(np.float32)
            raw_y = np.asarray(y[site_index, position], dtype=np.float32).reshape(-1, 1)
            scaled_y[cursor:end] = y_scaler.transform(raw_y).astype(np.float32).ravel()
            cursor = end
    require(cursor == rows, "scaled training coverage mismatch")
    scaled_x.flush()
    scaled_y.flush()
    return scaled_x, scaled_y


def predict_partitions(X, true_gpp, arm_id, train_positions, validation_positions, model, x_scaler, y_scaler, output):
    rows = len(SITES) * VALIDATION_MEMBERS * HOURS
    predictions = np.memmap(output / "predictions_physical_float32.dat", mode="w+", dtype=np.float32, shape=(rows,))
    y_mean, y_scale = float(y_scaler.mean_[0]), float(y_scaler.scale_[0])
    train_predictions, offsets = [], []
    for site_index in range(len(SITES)):
        values = np.empty(TRAIN_MEMBERS * HOURS, dtype=np.float32)
        cursor = 0
        for position in train_positions:
            end = cursor + HOURS
            block = feature_block(X, true_gpp, arm_id, site_index, np.asarray([position], dtype=np.int64))
            estimate = model.predict(x_scaler.transform(block).astype(np.float32)).astype(np.float64) * y_scale + y_mean
            require(np.all(np.isfinite(estimate)), "training prediction invalid")
            values[cursor:end] = estimate.astype(np.float32)
            cursor = end
        train_predictions.append(values)
    cursor = 0
    for site_index, site in enumerate(SITES):
        start = cursor
        for position in validation_positions:
            end = cursor + HOURS
            block = feature_block(X, true_gpp, arm_id, site_index, np.asarray([position], dtype=np.int64))
            estimate = model.predict(x_scaler.transform(block).astype(np.float32)).astype(np.float64) * y_scale + y_mean
            require(np.all(np.isfinite(estimate)), "validation prediction invalid")
            predictions[cursor:end] = estimate.astype(np.float32)
            cursor = end
        offsets.append({"partition": "validation", "site": site, "start": start, "end": cursor})
    require(cursor == rows, "validation prediction coverage mismatch")
    predictions.flush()
    layout = {"schema": "three-stage-sr-iter012-prediction-layout-v1", "rows": rows, "offsets": offsets}
    write_json(output / "prediction_layout.json", layout)
    return layout, predictions, train_predictions


def metric_rows(arm_id, split_id, y, train_positions, validation_positions, layout, predictions, train_predictions, iterations, warnings_count):
    rows = []
    for partition, positions, member_count in (("train", train_positions, TRAIN_MEMBERS), ("validation", validation_positions, VALIDATION_MEMBERS)):
        site_values = {}
        for site_index, site in enumerate(SITES):
            observed = np.asarray(y[site_index, positions], dtype=np.float64).reshape(-1)
            if partition == "train":
                estimated = np.asarray(train_predictions[site_index], dtype=np.float64)
            else:
                offset = next(item for item in layout["offsets"] if item["site"] == site)
                estimated = np.asarray(predictions[int(offset["start"]):int(offset["end"])], dtype=np.float64)
            require(observed.size == estimated.size == member_count * HOURS, "metric coverage mismatch")
            site_values[site] = {
                "hourly": (observed, estimated),
                "daily": (observed.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1), estimated.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1)),
            }
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                if scope == "pooled":
                    observed = np.concatenate([site_values[site][resolution][0] for site in SITES])
                    estimated = np.concatenate([site_values[site][resolution][1] for site in SITES])
                else:
                    observed, estimated = site_values[scope][resolution]
                metrics = _metrics(observed, estimated)
                rows.append({"arm_id": arm_id, "split_id": split_id, "partition": partition, "scope": scope, "resolution": resolution, "expected_count": int(observed.size), "valid_count": int(observed.size), "r2": metrics["r2"], "rmse": metrics["rmse"], "mae": metrics["mae"], "bias": metrics["bias"], "model_iterations": iterations, "convergence_warning_count": warnings_count, "finite_prediction_pass": True, "serialization_validation_pass": True})
    return rows


def smoke(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"smoke output exists: {output}")
    output.mkdir(parents=True)
    arms = load_arms(config)
    layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    true_gpp = load_true_gpp(Path(config["true_gpp_file"]))
    _, _, train_pos, validation_pos = selected_members(config, layout, 0)
    train_pos, validation_pos = train_pos[:40], validation_pos[:10]
    hours = 240
    rows = []
    for arm_id in ARM_IDS:
        x_train = np.concatenate([feature_block(X, true_gpp, arm_id, site, train_pos)[:, :][np.arange(train_pos.size * HOURS).reshape(train_pos.size, HOURS)[:, :hours].ravel()] for site in range(len(SITES))])
        y_train = np.concatenate([np.asarray(y[site, train_pos, :hours], dtype=np.float32).reshape(-1) for site in range(len(SITES))])
        x_validation = np.concatenate([feature_block(X, true_gpp, arm_id, site, validation_pos)[np.arange(validation_pos.size * HOURS).reshape(validation_pos.size, HOURS)[:, :hours].ravel()] for site in range(len(SITES))])
        xs = StandardScaler().fit(x_train)
        ys = StandardScaler().fit(y_train.reshape(-1, 1))
        settings = model_config(arms)
        settings.update(max_iter=2, early_stopping=False)
        model = MLPRegressor(**settings)
        model.fit(xs.transform(x_train).astype(np.float32), ys.transform(y_train.reshape(-1, 1)).astype(np.float32).ravel())
        prediction = model.predict(xs.transform(x_validation).astype(np.float32))
        replay = pickle.loads(pickle.dumps(model)).predict(xs.transform(x_validation[:1000]).astype(np.float32))
        require(np.all(np.isfinite(prediction)) and np.allclose(replay, prediction[:1000], rtol=1e-6, atol=1e-6), "smoke failure")
        rows.append({"arm_id": arm_id, "feature_count": int(xs.n_features_in_), "iterations": int(model.n_iter_), "finite": True, "roundtrip": True})
    report = {"schema": "three-stage-sr-iter012-smoke-v1", "result": "pass", "production": False, "max_iter": 2, "train_members": 40, "validation_members": 10, "hours": hours, "arms": rows, "fixed_test_access": False}
    write_json(output / "smoke_report.json", report)
    return report


def fit_leaf(config: Mapping[str, Any], arm_id: str, split_id: int, output: Path) -> dict[str, Any]:
    require(not output.exists(), f"leaf output exists: {output}")
    output.mkdir(parents=True)
    arms = load_arms(config)
    arm = arm_by_id(arms, arm_id)
    raw_layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    true_gpp = load_true_gpp(Path(config["true_gpp_file"]))
    train_members, validation_members, train_positions, validation_positions = selected_members(config, raw_layout, split_id)
    x_scaler, y_scaler = fit_scalers(X, y, true_gpp, arm_id, train_positions, int(config["scale_chunk_rows"]))
    require(int(x_scaler.n_features_in_) == int(arm["feature_count"]), "scaler feature count mismatch")
    scaled_x, scaled_y = materialize_train(X, y, true_gpp, arm_id, train_positions, x_scaler, y_scaler, output)
    model = MLPRegressor(**model_config(arms))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(scaled_x, scaled_y)
    warning_count = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    prediction_layout, predictions, train_predictions = predict_partitions(X, true_gpp, arm_id, train_positions, validation_positions, model, x_scaler, y_scaler, output)
    artifact = {"schema": "three-stage-sr-iter012-leaf-artifact-v1", "model": model, "x_mean": x_scaler.mean_, "x_scale": x_scaler.scale_, "y_mean": y_scaler.mean_, "y_scale": y_scaler.scale_, "arm": arm, "arm_id": arm_id, "split_id": split_id}
    artifact_path = output / "sr_leaf_artifact.pkl"
    serialized = pickle.dumps(artifact, protocol=pickle.HIGHEST_PROTOCOL)
    artifact_path.write_bytes(serialized)
    restored = pickle.loads(serialized)
    sample_raw = feature_block(X, true_gpp, arm_id, 0, np.asarray([train_positions[0]], dtype=np.int64))[:1000]
    sample = x_scaler.transform(sample_raw).astype(np.float32)
    original, replay = model.predict(sample), restored["model"].predict(sample)
    require(np.allclose(original, replay, rtol=config["reload_rtol"], atol=config["reload_atol"]), "serialization replay mismatch")
    rows = metric_rows(arm_id, split_id, y, train_positions, validation_positions, prediction_layout, predictions, train_predictions, int(model.n_iter_), warning_count)
    write_csv(output / "metrics.csv", rows)
    np.savez(output / "scalers.npz", x_mean=x_scaler.mean_, x_scale=x_scaler.scale_, y_mean=y_scaler.mean_, y_scale=y_scaler.scale_)
    write_json(output / "arm.json", arm)
    write_json(output / "serialization_validation.json", {"schema": "three-stage-sr-iter012-serialization-validation-v1", "result": "pass", "arm_id": arm_id, "split_id": split_id, "sample_rows": 1000, "maximum_absolute_difference": float(np.max(np.abs(original - replay)))})
    report = {"schema": "three-stage-sr-iter012-leaf-v1", "result": "pass", "arm_id": arm_id, "split_id": split_id, "arm": arm, "parameter_count": MODEL_PARAMETER_COUNTS[arm_id], "model_iterations": int(model.n_iter_), "convergence_warning_count": warning_count, "train_member_count": len(train_members), "validation_member_count": len(validation_members), "metric_rows": len(rows), "prediction_rows": int(prediction_layout["rows"]), "predictions_sha256": sha256_file(output / "predictions_physical_float32.dat"), "artifact_sha256": sha256_file(artifact_path), "metrics_sha256": sha256_file(output / "metrics.csv"), "scalers_sha256": sha256_file(output / "scalers.npz"), "serialization_validation_sha256": sha256_file(output / "serialization_validation.json"), "fixed_test_access": False, "spinup_execution": False, "gpp_execution": False, "all_development_fit": False, "release_created": False}
    del scaled_x, scaled_y
    (output / "X_train_scaled_float32.dat").unlink()
    (output / "y_train_scaled_float32.dat").unlink()
    report["successful_scaled_scratch_removed"] = True
    write_json(output / "leaf_report.json", report)
    return report
