#!/usr/bin/env python
"""Shared Iter011 SR capacity/regularization utilities."""
from __future__ import annotations

import json
import pickle
import warnings
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from development.three_stage_surrogate.slurm.iter010.iter010_common import (
    FROZEN_OPTIMIZER,
    _materialize_train,
    read_csv,
    read_json,
    write_csv,
)
from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_sr import FEATURE_COUNT, HOURS, _metrics, write_json
from model_ELM.three_stage_sr_release import (
    DAY_COUNT,
    TRAIN_MEMBERS,
    VALIDATION_MEMBERS,
    _fit_scalers,
    _load_split_manifest,
    _positions,
    load_raw,
    validate_raw,
    validate_split_design,
)

CANDIDATE_IDS = tuple("ABCDE")
PARAMETER_COUNTS = {"A": 9025, "B": 9025, "C": 14081, "D": 14081, "E": 14081}


def load_candidates(config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(config["candidate_manifest"])
    require(sha256_file(path) == config["candidate_manifest_sha256"], "candidate manifest hash mismatch")
    payload = read_json(path)
    require(payload["schema"] == "three-stage-sr-iter011-candidates-v1", "candidate schema mismatch")
    require(payload["candidate_count"] == len(payload["candidates"]) == 5, "candidate count mismatch")
    require(tuple(row["candidate_id"] for row in payload["candidates"]) == CANDIDATE_IDS, "candidate IDs mismatch")
    observed = [
        (tuple(row["hidden_layer_sizes"]), row["activation"], float(row["alpha"]))
        for row in payload["candidates"]
    ]
    expected = [
        ((96, 48), "tanh", 1.0),
        ((96, 48), "tanh", 0.01),
        ((128, 64), "tanh", 1.0),
        ((128, 64), "tanh", 0.01),
        ((128, 64), "tanh", 0.1),
    ]
    require(observed == expected, "candidate matrix mismatch")
    require(payload["frozen_optimizer"] == FROZEN_OPTIMIZER, "optimizer mismatch")
    require(payload["split_ids"] == list(range(20)), "split IDs mismatch")
    require(payload["production_fit_count"] == 100, "fit count mismatch")
    for key in ("fixed_test_allowed", "spinup_execution_allowed", "gpp_execution_allowed", "all_development_fit_allowed", "release_allowed"):
        require(payload[key] is False, f"candidate boundary mismatch: {key}")
    return payload


def candidate_by_id(payload: Mapping[str, Any], candidate_id: str) -> dict[str, Any]:
    require(candidate_id in CANDIDATE_IDS, "candidate ID invalid")
    row = dict(payload["candidates"][CANDIDATE_IDS.index(candidate_id)])
    require(row["candidate_id"] == candidate_id, "candidate lookup mismatch")
    return row


def model_config(candidate: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(FROZEN_OPTIMIZER)
    result.update(
        hidden_layer_sizes=tuple(int(x) for x in candidate["hidden_layer_sizes"]),
        activation=str(candidate["activation"]),
        alpha=float(candidate["alpha"]),
    )
    return result


def selected_members(config: Mapping[str, Any], layout: Mapping[str, Any], split_id: int):
    item = _load_split_manifest(config)["splits"][split_id]
    train = list(item["train_member_ids"])
    validation = list(item["validation_member_ids"])
    return train, validation, _positions(layout, train), _positions(layout, validation)


def validate_contract(config: Mapping[str, Any], *, full_raw_hashes: bool) -> dict[str, Any]:
    require(config["schema"] == "three-stage-sr-iter011-config-v1", "config schema mismatch")
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
    load_candidates(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split mismatch")
    validate_split_design(snapshot, _load_split_manifest(config))
    raw_report = validate_raw(config, Path(config["raw_directory"]), full_hashes=full_raw_hashes)
    raw_manifest = read_json(Path(config["raw_directory"]) / "raw_manifest.json")
    for field, key in (("layout_sha256", "raw_layout_sha256"), ("x_sha256", "raw_x_sha256"), ("y_sha256", "raw_y_sha256"), ("time_sha256", "raw_time_sha256")):
        require(raw_manifest[field] == config[key], f"raw identity mismatch: {field}")
    return {"schema": "three-stage-sr-iter011-contract-validation-v1", "result": "pass", "candidate_count": 5, "production_fit_count": 100, "raw_full_hashes": bool(full_raw_hashes), "raw_validation": raw_report, "fixed_test_access": False}


def smoke(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"smoke output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    _, _, train_pos, validation_pos = selected_members(config, layout, 0)
    train_pos, validation_pos = train_pos[:40], validation_pos[:10]
    hours = 240
    x_train = np.concatenate([np.asarray(X[s, train_pos, :hours], dtype=np.float32).reshape(-1, FEATURE_COUNT) for s in range(len(SITES))])
    y_train = np.concatenate([np.asarray(y[s, train_pos, :hours], dtype=np.float32).reshape(-1) for s in range(len(SITES))])
    x_validation = np.concatenate([np.asarray(X[s, validation_pos, :hours], dtype=np.float32).reshape(-1, FEATURE_COUNT) for s in range(len(SITES))])
    xs = StandardScaler().fit(x_train)
    ys = StandardScaler().fit(y_train.reshape(-1, 1))
    rows = []
    for candidate_id in CANDIDATE_IDS:
        settings = model_config(candidate_by_id(candidates, candidate_id))
        settings.update(max_iter=2, early_stopping=False)
        model = MLPRegressor(**settings)
        model.fit(xs.transform(x_train).astype(np.float32), ys.transform(y_train.reshape(-1, 1)).astype(np.float32).ravel())
        prediction = model.predict(xs.transform(x_validation).astype(np.float32))
        replay = pickle.loads(pickle.dumps(model)).predict(xs.transform(x_validation[:1000]).astype(np.float32))
        require(np.all(np.isfinite(prediction)) and np.allclose(replay, prediction[:1000], rtol=1e-6, atol=1e-6), "smoke failure")
        rows.append({"candidate_id": candidate_id, "iterations": int(model.n_iter_), "finite": True, "roundtrip": True})
    report = {"schema": "three-stage-sr-iter011-smoke-v1", "result": "pass", "production": False, "max_iter": 2, "train_members": 40, "validation_members": 10, "hours": hours, "candidates": rows, "fixed_test_access": False}
    write_json(output / "smoke_report.json", report)
    return report


def _predict_partitions(X, train_positions, validation_positions, model, x_scaler, y_scaler, output):
    rows = len(SITES) * VALIDATION_MEMBERS * HOURS
    path = output / "predictions_physical_float32.dat"
    predictions = np.memmap(path, mode="w+", dtype=np.float32, shape=(rows,))
    train_predictions, offsets = [], []
    y_mean, y_scale = float(y_scaler.mean_[0]), float(y_scaler.scale_[0])
    for site_index in range(len(SITES)):
        values = np.empty(TRAIN_MEMBERS * HOURS, dtype=np.float32)
        cursor = 0
        for position in train_positions:
            end = cursor + HOURS
            design = x_scaler.transform(np.asarray(X[site_index, position], dtype=np.float32)).astype(np.float32)
            estimate = model.predict(design).astype(np.float64) * y_scale + y_mean
            require(np.all(np.isfinite(estimate)), "training prediction invalid")
            values[cursor:end] = estimate.astype(np.float32)
            cursor = end
        require(cursor == values.size, "training prediction coverage mismatch")
        train_predictions.append(values)
    cursor = 0
    for site_index, site in enumerate(SITES):
        start = cursor
        for position in validation_positions:
            end = cursor + HOURS
            design = x_scaler.transform(np.asarray(X[site_index, position], dtype=np.float32)).astype(np.float32)
            estimate = model.predict(design).astype(np.float64) * y_scale + y_mean
            require(np.all(np.isfinite(estimate)), "validation prediction invalid")
            predictions[cursor:end] = estimate.astype(np.float32)
            cursor = end
        offsets.append({"partition": "validation", "site": site, "start": start, "end": cursor})
    require(cursor == rows, "validation prediction coverage mismatch")
    predictions.flush()
    layout = {"schema": "three-stage-sr-iter011-prediction-layout-v1", "rows": rows, "offsets": offsets}
    write_json(output / "prediction_layout.json", layout)
    return layout, predictions, train_predictions


def metric_rows(candidate_id, split_id, y, train_positions, validation_positions, layout, predictions, train_predictions, iterations, warnings_count):
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
                    observed = np.concatenate([site_values[s][resolution][0] for s in SITES])
                    estimated = np.concatenate([site_values[s][resolution][1] for s in SITES])
                else:
                    observed, estimated = site_values[scope][resolution]
                metrics = _metrics(observed, estimated)
                rows.append({"candidate_id": candidate_id, "split_id": split_id, "partition": partition, "scope": scope, "resolution": resolution, "expected_count": int(observed.size), "valid_count": int(observed.size), "r2": metrics["r2"], "rmse": metrics["rmse"], "mae": metrics["mae"], "bias": metrics["bias"], "model_iterations": iterations, "convergence_warning_count": warnings_count, "finite_prediction_pass": True, "serialization_validation_pass": True})
    return rows


def fit_leaf(config: Mapping[str, Any], candidate_id: str, split_id: int, output: Path) -> dict[str, Any]:
    require(not output.exists(), f"leaf output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    candidate = candidate_by_id(candidates, candidate_id)
    raw_layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    train_members, validation_members, train_positions, validation_positions = selected_members(config, raw_layout, split_id)
    x_scaler, y_scaler = _fit_scalers(X, y, train_positions, int(config["scale_chunk_rows"]))
    scaled_x, scaled_y = _materialize_train(X, y, train_positions, x_scaler, y_scaler, output)
    model = MLPRegressor(**model_config(candidate))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(scaled_x, scaled_y)
    warning_count = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    prediction_layout, predictions, train_predictions = _predict_partitions(X, train_positions, validation_positions, model, x_scaler, y_scaler, output)
    artifact = {"schema": "three-stage-sr-iter011-leaf-artifact-v1", "model": model, "x_mean": x_scaler.mean_, "x_scale": x_scaler.scale_, "y_mean": y_scaler.mean_, "y_scale": y_scaler.scale_, "candidate": candidate, "candidate_id": candidate_id, "split_id": split_id}
    artifact_path = output / "sr_leaf_artifact.pkl"
    serialized = pickle.dumps(artifact, protocol=pickle.HIGHEST_PROTOCOL)
    artifact_path.write_bytes(serialized)
    restored = pickle.loads(serialized)
    sample = x_scaler.transform(np.asarray(X[0, train_positions[0], :1000], dtype=np.float32)).astype(np.float32)
    original, replay = model.predict(sample), restored["model"].predict(sample)
    require(np.allclose(original, replay, rtol=config["reload_rtol"], atol=config["reload_atol"]), "serialization replay mismatch")
    rows = metric_rows(candidate_id, split_id, y, train_positions, validation_positions, prediction_layout, predictions, train_predictions, int(model.n_iter_), warning_count)
    write_csv(output / "metrics.csv", rows)
    np.savez(output / "scalers.npz", x_mean=x_scaler.mean_, x_scale=x_scaler.scale_, y_mean=y_scaler.mean_, y_scale=y_scaler.scale_)
    write_json(output / "candidate.json", candidate)
    write_json(output / "serialization_validation.json", {"schema": "three-stage-sr-iter011-serialization-validation-v1", "result": "pass", "candidate_id": candidate_id, "split_id": split_id, "sample_rows": 1000, "maximum_absolute_difference": float(np.max(np.abs(original - replay)))})
    report = {"schema": "three-stage-sr-iter011-leaf-v1", "result": "pass", "candidate_id": candidate_id, "split_id": split_id, "candidate": candidate, "parameter_count": PARAMETER_COUNTS[candidate_id], "model_iterations": int(model.n_iter_), "convergence_warning_count": warning_count, "train_member_count": len(train_members), "validation_member_count": len(validation_members), "metric_rows": len(rows), "prediction_rows": int(prediction_layout["rows"]), "predictions_sha256": sha256_file(output / "predictions_physical_float32.dat"), "artifact_sha256": sha256_file(artifact_path), "metrics_sha256": sha256_file(output / "metrics.csv"), "scalers_sha256": sha256_file(output / "scalers.npz"), "serialization_validation_sha256": sha256_file(output / "serialization_validation.json"), "fixed_test_access": False, "spinup_execution": False, "gpp_execution": False, "all_development_fit": False, "release_created": False}
    del scaled_x, scaled_y
    (output / "X_train_scaled_float32.dat").unlink()
    (output / "y_train_scaled_float32.dat").unlink()
    report["successful_scaled_scratch_removed"] = True
    write_json(output / "leaf_report.json", report)
    return report
