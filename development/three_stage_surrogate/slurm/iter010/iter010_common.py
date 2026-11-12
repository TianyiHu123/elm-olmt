#!/usr/bin/env python
"""Shared Iter010 SR-refinement fit and contract utilities."""
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

RESOLUTIONS = ("hourly", "daily")
SCREEN_SPLITS = (1, 3, 7, 10, 12, 13, 14, 16)
FINALIST_SPLITS = (0, 2, 4, 5, 6, 8, 9, 11, 15, 17, 18, 19)
FROZEN_OPTIMIZER = {
    "solver": "adam",
    "learning_rate": "adaptive",
    "learning_rate_init": 0.001,
    "max_iter": 500,
    "early_stopping": True,
    "validation_fraction": 0.1,
    "n_iter_no_change": 10,
    "tol": 0.0001,
    "batch_size": "auto",
    "shuffle": True,
    "random_state": 42,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_candidates(config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(config["candidate_manifest"])
    require(sha256_file(path) == config["candidate_manifest_sha256"], "candidate manifest hash mismatch")
    payload = read_json(path)
    require(payload["schema"] == "three-stage-sr-iter010-candidates-v1", "candidate schema mismatch")
    require(payload["candidate_count"] == len(payload["candidates"]) == 33, "candidate count mismatch")
    require([int(row["candidate_id"]) for row in payload["candidates"]] == list(range(33)), "candidate ID mismatch")
    require(tuple(payload["screen_split_ids"]) == SCREEN_SPLITS, "screen split mismatch")
    require(tuple(payload["finalist_split_ids"]) == FINALIST_SPLITS, "finalist split mismatch")
    require(payload["finalist_count"] == 6, "finalist count mismatch")
    require(payload["frozen_optimizer"] == FROZEN_OPTIMIZER, "optimizer contract mismatch")
    require(payload["fixed_test_allowed"] is False, "candidate fixed-test scope mismatch")
    require(payload["spinup_execution_allowed"] is False, "candidate spinup scope mismatch")
    require(payload["gpp_execution_allowed"] is False, "candidate GPP scope mismatch")
    require(payload["all_development_fit_allowed"] is False, "candidate all-development scope mismatch")
    require(payload["release_allowed"] is False, "candidate release scope mismatch")
    expected = [
        ((64, 32), "tanh", 1.0e-4),
    ]
    expected.extend(
        (hidden, "tanh", alpha)
        for hidden in ((32, 16), (64, 16))
        for alpha in (1.0e-6, 1.0e-4, 1.0e-2, 1.0)
    )
    expected.extend(((64, 32), "tanh", alpha) for alpha in (1.0e-6, 1.0e-2, 1.0))
    expected.extend(
        (hidden, "tanh", alpha)
        for hidden in ((64, 64), (96, 48), (128, 32), (128, 64), (64, 32, 16))
        for alpha in (1.0e-6, 1.0e-4, 1.0e-2, 1.0)
    )
    expected.append(((128,), "relu", 10.0))
    observed = [
        (tuple(row["hidden_layer_sizes"]), row["activation"], float(row["alpha"]))
        for row in payload["candidates"]
    ]
    require(observed == expected, "candidate matrix mismatch")
    baseline = payload["candidates"][0]
    require(
        baseline["hidden_layer_sizes"] == [64, 32]
        and baseline["activation"] == "tanh"
        and float(baseline["alpha"]) == 0.0001,
        "candidate 0 baseline mismatch",
    )
    return payload


def model_config(candidate: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(FROZEN_OPTIMIZER)
    result.update(
        hidden_layer_sizes=tuple(int(value) for value in candidate["hidden_layer_sizes"]),
        activation=str(candidate["activation"]),
        alpha=float(candidate["alpha"]),
    )
    return result


def candidate_by_id(payload: Mapping[str, Any], candidate_id: int) -> dict[str, Any]:
    require(0 <= candidate_id < 33, "candidate ID out of range")
    row = dict(payload["candidates"][candidate_id])
    require(int(row["candidate_id"]) == candidate_id, "candidate lookup mismatch")
    return row


def validate_contract(config: Mapping[str, Any], *, full_raw_hashes: bool) -> dict[str, Any]:
    require(config["schema"] == "three-stage-sr-iter010-config-v1", "Iter010 config schema mismatch")
    require(config["fixed_test_allowed"] is False, "fixed-test permission mismatch")
    require(config["spinup_execution_allowed"] is False, "spinup permission mismatch")
    require(config["gpp_execution_allowed"] is False, "GPP permission mismatch")
    require(config["all_development_fit_allowed"] is False, "all-development permission mismatch")
    require(config["release_allowed"] is False, "release permission mismatch")
    require(sha256_file(REPO_ROOT / "development/three_stage_surrogate/PLAN.md") == config["plan_sha256"], "plan hash mismatch")
    require(sha256_file(Path(config["spinup_release_manifest"])) == config["spinup_release_manifest_sha256"], "spinup release hash mismatch")
    require(sha256_file(Path(config["predicted_cn_handoff"])) == config["predicted_cn_sha256"], "predicted C/N hash mismatch")
    require(sha256_file(Path(config["gpp_release_manifest"])) == config["gpp_release_manifest_sha256"], "GPP release hash mismatch")
    require(sha256_file(Path(config["predicted_gpp_handoff"])) == config["predicted_gpp_sha256"], "predicted GPP hash mismatch")
    candidates = load_candidates(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot identity mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split hash mismatch")
    splits = _load_split_manifest(config)
    validate_split_design(snapshot, splits)
    require(set(SCREEN_SPLITS).isdisjoint(FINALIST_SPLITS), "stage split overlap")
    require(set(SCREEN_SPLITS).union(FINALIST_SPLITS) == set(range(20)), "stage split coverage mismatch")
    raw_report = validate_raw(config, Path(config["raw_directory"]), full_hashes=full_raw_hashes)
    raw_manifest = read_json(Path(config["raw_directory"]) / "raw_manifest.json")
    require(raw_manifest["layout_sha256"] == config["raw_layout_sha256"], "raw layout identity mismatch")
    require(raw_manifest["x_sha256"] == config["raw_x_sha256"], "raw X identity mismatch")
    require(raw_manifest["y_sha256"] == config["raw_y_sha256"], "raw y identity mismatch")
    require(raw_manifest["time_sha256"] == config["raw_time_sha256"], "raw time identity mismatch")
    return {
        "schema": "three-stage-sr-iter010-contract-validation-v1",
        "result": "pass",
        "candidate_count": len(candidates["candidates"]),
        "screen_fit_count": 33 * len(SCREEN_SPLITS),
        "finalist_fit_count": 6 * len(FINALIST_SPLITS),
        "raw_full_hashes": bool(full_raw_hashes),
        "raw_validation": raw_report,
        "fixed_test_access": False,
        "spinup_execution": False,
    }


def _selected_members(config: Mapping[str, Any], raw_layout: Mapping[str, Any], split_id: int) -> tuple[list[str], list[str], np.ndarray, np.ndarray]:
    splits = _load_split_manifest(config)
    item = splits["splits"][split_id]
    train_members = list(item["train_member_ids"])
    validation_members = list(item["validation_member_ids"])
    return train_members, validation_members, _positions(raw_layout, train_members), _positions(raw_layout, validation_members)


def smoke(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"smoke output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    raw_layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    _, _, train_positions, validation_positions = _selected_members(config, raw_layout, SCREEN_SPLITS[0])
    train_positions = train_positions[:80]
    validation_positions = validation_positions[:20]
    hours = 1440
    x_train = np.concatenate(
        [np.asarray(X[site, train_positions, :hours], dtype=np.float32).reshape(-1, FEATURE_COUNT) for site in range(len(SITES))]
    )
    y_train = np.concatenate(
        [np.asarray(y[site, train_positions, :hours], dtype=np.float32).reshape(-1) for site in range(len(SITES))]
    )
    x_validation = np.concatenate(
        [np.asarray(X[site, validation_positions, :hours], dtype=np.float32).reshape(-1, FEATURE_COUNT) for site in range(len(SITES))]
    )
    x_scaler = StandardScaler().fit(x_train)
    y_scaler = StandardScaler().fit(y_train.reshape(-1, 1))
    rows = []
    for candidate_id in (0, 27, 32):
        candidate = candidate_by_id(candidates, candidate_id)
        settings = model_config(candidate)
        settings.update(max_iter=2, early_stopping=False)
        model = MLPRegressor(**settings)
        model.fit(
            x_scaler.transform(x_train).astype(np.float32),
            y_scaler.transform(y_train.reshape(-1, 1)).astype(np.float32).ravel(),
        )
        observed = model.predict(x_scaler.transform(x_validation).astype(np.float32))
        roundtrip = pickle.loads(pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL))
        replay = roundtrip.predict(x_scaler.transform(x_validation[:1000]).astype(np.float32))
        require(np.all(np.isfinite(observed)), "smoke prediction invalid")
        require(np.allclose(replay, observed[:1000], rtol=1e-6, atol=1e-6), "smoke serialization mismatch")
        rows.append({"candidate_id": candidate_id, "iterations": int(model.n_iter_), "finite": True, "roundtrip": True})
    report = {
        "schema": "three-stage-sr-iter010-smoke-v1",
        "result": "pass",
        "split_id": SCREEN_SPLITS[0],
        "train_members": 80,
        "validation_members": 20,
        "hours": hours,
        "candidates": rows,
        "fixed_test_access": False,
        "spinup_execution": False,
    }
    write_json(output / "smoke_report.json", report)
    return report


def _materialize_train(
    X: np.memmap,
    y: np.memmap,
    positions: np.ndarray,
    x_scaler: StandardScaler,
    y_scaler: StandardScaler,
    output: Path,
) -> tuple[np.memmap, np.memmap]:
    rows = len(SITES) * TRAIN_MEMBERS * HOURS
    scaled_x = np.memmap(output / "X_train_scaled_float32.dat", mode="w+", dtype=np.float32, shape=(rows, FEATURE_COUNT))
    scaled_y = np.memmap(output / "y_train_scaled_float32.dat", mode="w+", dtype=np.float32, shape=(rows,))
    cursor = 0
    for site_index in range(len(SITES)):
        for position in positions:
            end = cursor + HOURS
            raw_x = np.asarray(X[site_index, position], dtype=np.float32)
            raw_y = np.asarray(y[site_index, position], dtype=np.float32).reshape(-1, 1)
            scaled_x[cursor:end] = x_scaler.transform(raw_x).astype(np.float32)
            scaled_y[cursor:end] = y_scaler.transform(raw_y).astype(np.float32).ravel()
            cursor = end
    require(cursor == rows, "scaled training coverage mismatch")
    scaled_x.flush()
    scaled_y.flush()
    return scaled_x, scaled_y


def _predict_partitions(
    X: np.memmap,
    train_positions: np.ndarray,
    validation_positions: np.ndarray,
    model: MLPRegressor,
    x_scaler: StandardScaler,
    y_scaler: StandardScaler,
    output: Path,
) -> tuple[dict[str, Any], np.memmap, list[np.ndarray]]:
    validation_rows = len(SITES) * VALIDATION_MEMBERS * HOURS
    predictions_path = output / "predictions_physical_float32.dat"
    predictions = np.memmap(predictions_path, mode="w+", dtype=np.float32, shape=(validation_rows,))
    offsets = []
    train_predictions = []
    y_mean = float(y_scaler.mean_[0])
    y_scale = float(y_scaler.scale_[0])
    for site_index in range(len(SITES)):
        site_values = np.empty(TRAIN_MEMBERS * HOURS, dtype=np.float32)
        site_cursor = 0
        for position in train_positions:
            end = site_cursor + HOURS
            design = x_scaler.transform(np.asarray(X[site_index, position], dtype=np.float32)).astype(np.float32)
            estimate = model.predict(design).astype(np.float64) * y_scale + y_mean
            require(np.all(np.isfinite(estimate)), "training prediction invalid")
            site_values[site_cursor:end] = estimate.astype(np.float32)
            site_cursor = end
        require(site_cursor == site_values.size, "training prediction coverage mismatch")
        train_predictions.append(site_values)
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
    require(cursor == validation_rows, "validation prediction coverage mismatch")
    predictions.flush()
    layout = {"schema": "three-stage-sr-iter010-prediction-layout-v1", "rows": validation_rows, "offsets": offsets}
    write_json(output / "prediction_layout.json", layout)
    return layout, predictions, train_predictions


def _pooled_metric_rows(
    candidate_id: int,
    split_id: int,
    y: np.memmap,
    train_positions: np.ndarray,
    validation_positions: np.ndarray,
    prediction_layout: Mapping[str, Any],
    predictions: np.ndarray,
    train_predictions: Sequence[np.ndarray],
    iterations: int,
    warning_count: int,
) -> list[dict[str, Any]]:
    rows = []
    for partition, positions in (("train", train_positions), ("validation", validation_positions)):
        member_count = TRAIN_MEMBERS if partition == "train" else VALIDATION_MEMBERS
        truth_hourly = []
        prediction_hourly = []
        truth_daily = []
        prediction_daily = []
        for site_index, site in enumerate(SITES):
            observed = np.asarray(y[site_index, positions], dtype=np.float64).reshape(-1)
            if partition == "train":
                estimated = np.asarray(train_predictions[site_index], dtype=np.float64)
            else:
                offset = next(item for item in prediction_layout["offsets"] if item["site"] == site)
                estimated = np.asarray(predictions[int(offset["start"]):int(offset["end"])], dtype=np.float64)
            require(observed.size == estimated.size == member_count * HOURS, "metric coverage mismatch")
            truth_hourly.append(observed)
            prediction_hourly.append(estimated)
            truth_daily.append(observed.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1))
            prediction_daily.append(estimated.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1))
        for resolution, observed_parts, estimated_parts in (
            ("hourly", truth_hourly, prediction_hourly),
            ("daily", truth_daily, prediction_daily),
        ):
            observed = np.concatenate(observed_parts)
            estimated = np.concatenate(estimated_parts)
            metrics = _metrics(observed, estimated)
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "split_id": split_id,
                    "partition": partition,
                    "resolution": resolution,
                    "expected_count": int(observed.size),
                    "valid_count": int(observed.size),
                    **metrics,
                    "model_iterations": iterations,
                    "convergence_warning_count": warning_count,
                    "finite_prediction_pass": True,
                    "serialization_validation_pass": True,
                }
            )
    return rows


def fit_leaf(config: Mapping[str, Any], candidate_id: int, split_id: int, output: Path) -> dict[str, Any]:
    require(not output.exists(), f"leaf output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    candidate = candidate_by_id(candidates, candidate_id)
    raw_layout, X, y, _ = load_raw(Path(config["raw_directory"]))
    train_members, validation_members, train_positions, validation_positions = _selected_members(config, raw_layout, split_id)
    x_scaler, y_scaler = _fit_scalers(X, y, train_positions, int(config["scale_chunk_rows"]))
    scaled_x, scaled_y = _materialize_train(X, y, train_positions, x_scaler, y_scaler, output)
    model = MLPRegressor(**model_config(candidate))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(scaled_x, scaled_y)
    warning_count = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    prediction_layout, predictions, train_predictions = _predict_partitions(
        X, train_positions, validation_positions, model, x_scaler, y_scaler, output
    )
    artifact = {"schema": "three-stage-sr-iter010-leaf-artifact-v1", "model": model,
                "x_mean": x_scaler.mean_, "x_scale": x_scaler.scale_,
                "y_mean": y_scaler.mean_, "y_scale": y_scaler.scale_,
                "candidate": candidate, "candidate_id": candidate_id, "split_id": split_id}
    serialized = pickle.dumps(artifact, protocol=pickle.HIGHEST_PROTOCOL)
    artifact_path = output / "sr_leaf_artifact.pkl"
    artifact_path.write_bytes(serialized)
    restored = pickle.loads(serialized)
    sample_raw = np.asarray(X[0, train_positions[0], :1000], dtype=np.float32)
    sample_scaled = x_scaler.transform(sample_raw).astype(np.float32)
    original = model.predict(sample_scaled)
    replay = restored["model"].predict(sample_scaled)
    require(np.allclose(original, replay, rtol=config["reload_rtol"], atol=config["reload_atol"]), "serialization replay mismatch")
    metric_rows = _pooled_metric_rows(
        candidate_id,
        split_id,
        y,
        train_positions,
        validation_positions,
        prediction_layout,
        predictions,
        train_predictions,
        int(model.n_iter_),
        warning_count,
    )
    write_csv(output / "pooled_metrics.csv", metric_rows)
    np.savez(
        output / "scalers.npz",
        x_mean=x_scaler.mean_,
        x_scale=x_scaler.scale_,
        y_mean=y_scaler.mean_,
        y_scale=y_scaler.scale_,
    )
    write_json(output / "candidate.json", candidate)
    reload_report = {
        "schema": "three-stage-sr-iter010-serialization-validation-v1",
        "result": "pass",
        "candidate_id": candidate_id,
        "split_id": split_id,
        "sample_rows": 1000,
        "maximum_absolute_difference": float(np.max(np.abs(original - replay))),
    }
    write_json(output / "serialization_validation.json", reload_report)
    report = {
        "schema": "three-stage-sr-iter010-leaf-v1",
        "result": "pass",
        "candidate_id": candidate_id,
        "split_id": split_id,
        "candidate": candidate,
        "model_iterations": int(model.n_iter_),
        "convergence_warning_count": warning_count,
        "train_member_count": len(train_members),
        "validation_member_count": len(validation_members),
        "prediction_rows": int(prediction_layout["rows"]),
        "predictions_sha256": sha256_file(output / "predictions_physical_float32.dat"),
        "artifact_sha256": sha256_file(artifact_path),
        "metrics_sha256": sha256_file(output / "pooled_metrics.csv"),
        "scalers_sha256": sha256_file(output / "scalers.npz"),
        "serialization_validation_sha256": sha256_file(output / "serialization_validation.json"),
        "fixed_test_access": False,
        "spinup_execution": False,
        "all_development_fit": False,
        "release_created": False,
    }
    write_json(output / "leaf_report.json", report)
    del scaled_x, scaled_y
    (output / "X_train_scaled_float32.dat").unlink()
    (output / "y_train_scaled_float32.dat").unlink()
    report["successful_scaled_scratch_removed"] = True
    write_json(output / "leaf_report.json", report)
    return report


def leaf_directory(root: Path, candidate_id: int, split_id: int) -> Path:
    return root / f"candidate_{candidate_id:02d}" / f"split_{split_id:02d}"
