"""Iter006 fixed-upstream GPP robustness, uncertainty, and release support."""
from __future__ import annotations

import csv
import json
import pickle
import shutil
import warnings
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence, Tuple

import numpy as np
from netCDF4 import Dataset
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler

from .three_stage_data import SITES, ThreeStageSnapshot, require, schema_sha256, sha256_file
from .three_stage_gpp import (
    FEATURE_COUNT,
    FORCING_FEATURE_NAMES,
    FORCING_NAMES,
    HOURS,
    MODEL_CONFIG,
    QUANTILES,
    SURFACE_NAMES,
    UPSTREAM_NAMES,
    _handoff,
    _metrics,
    _model,
    _site_static,
    engineer_forcing,
    feature_names,
    predict_artifact,
    write_json,
)

DEVELOPMENT_MEMBERS = 819
TRAIN_MEMBERS = 655
VALIDATION_MEMBERS = 164
SPLIT_COUNT = 20
DAY_COUNT = HOURS // 24
RESOLUTIONS: Tuple[str, ...] = ("hourly", "daily")
RELEASE_SCHEMA = "three-stage-gpp-release-artifact-v1"
RAW_SCHEMA = "three-stage-gpp-iter006-raw-v1"


def package_files(root: Path, *, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        rows.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def _load_split_manifest(config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(config["repeated_split_manifest"])
    require(sha256_file(path) == config["repeated_split_manifest_sha256"], "split manifest hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload["schema"] == "three-stage-spinup-iter004-splits-v1", "split schema mismatch")
    require(payload["seed"] == int(config.get("repeated_split_seed", 20261031)), "split seed mismatch")
    require(payload["split_design_sha256"] == config["split_design_sha256"], "split design mismatch")
    require(len(payload["splits"]) == SPLIT_COUNT, "split count mismatch")
    return payload


def validate_split_design(snapshot: ThreeStageSnapshot, payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {member: 0 for member in snapshot.development_ranked}
    for expected_id, item in enumerate(payload["splits"]):
        require(int(item["split_id"]) == expected_id, "split ID/order mismatch")
        train = list(item["train_member_ids"])
        validation = list(item["validation_member_ids"])
        require(len(train) == len(set(train)) == TRAIN_MEMBERS, "split training membership mismatch")
        require(len(validation) == len(set(validation)) == VALIDATION_MEMBERS, "split validation membership mismatch")
        require(not set(train).intersection(validation), "split overlap")
        require(set(train).union(validation) == snapshot.development_set, "split development coverage mismatch")
        require(not set(train).intersection(snapshot.fixed_test_set), "fixed-test training identity")
        require(not set(validation).intersection(snapshot.fixed_test_set), "fixed-test validation identity")
        for member in validation:
            counts[member] += 1
    require(counts == {str(k): int(v) for k, v in payload["validation_appearance_counts"].items()}, "appearance count mismatch")
    require(sum(value == 4 for value in counts.values()) == 815, "four-appearance balance mismatch")
    require(sum(value == 5 for value in counts.values()) == 4, "five-appearance balance mismatch")
    return counts


def preflight(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot identity mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split hash mismatch")
    require(sha256_file(Path(config["spinup_release_manifest"])) == config["spinup_release_manifest_sha256"], "spinup release hash mismatch")
    require(sha256_file(Path(config["predicted_cn_handoff"])) == config["predicted_cn_sha256"], "predicted-C/N hash mismatch")
    require(sha256_file(Path(config["gpp_configuration_file"])) == config["gpp_configuration_sha256"], "GPP configuration hash mismatch")
    splits = _load_split_manifest(config)
    counts = validate_split_design(snapshot, splits)
    frozen_configuration = json.loads(Path(config["gpp_configuration_file"]).read_text(encoding="utf-8"))
    require(config["model_config"] == frozen_configuration["model_config"], "model configuration mismatch")
    fixture = np.arange(96, dtype=np.float64).reshape(4, 24)
    require(np.allclose(fixture.mean(axis=1), fixture.reshape(4, 1, 24).mean(axis=2).ravel()), "daily fixture failed")
    report = {
        "schema": "three-stage-gpp-iter006-preflight-v1", "result": "pass", "no_training": True,
        "snapshot_sha256": snapshot.snapshot_sha256, "split_count": len(splits["splits"]),
        "four_appearance_members": sum(value == 4 for value in counts.values()),
        "five_appearance_members": sum(value == 5 for value in counts.values()),
        "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "preflight_report.json", report)
    return report


def prepare_raw(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"raw output exists: {output}")
    output.mkdir(parents=True)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split hash mismatch")
    splits = _load_split_manifest(config)
    validate_split_design(snapshot, splits)
    handoff_path = Path(config["predicted_cn_handoff"])
    require(sha256_file(handoff_path) == config["predicted_cn_sha256"], "predicted-C/N hash mismatch")
    upstream = _handoff(handoff_path, snapshot)
    names = feature_names(snapshot)
    x_path = output / "X_raw_float32.dat"
    y_path = output / "y_raw_float32.dat"
    time_path = output / "time_int64.dat"
    X = np.memmap(x_path, mode="w+", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS, FEATURE_COUNT))
    y = np.memmap(y_path, mode="w+", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS))
    times = np.memmap(time_path, mode="w+", dtype=np.int64, shape=(len(SITES), HOURS))
    params = snapshot._parameter_values(snapshot.development_ranked)
    require(params.shape == (DEVELOPMENT_MEMBERS, 18), "parameter matrix mismatch")
    with ExitStack() as stack:
        datasets = {
            site: stack.enter_context(Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r"))
            for site in SITES
        }
        for site_index, site in enumerate(SITES):
            dataset = datasets[site]
            time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
            require(time.shape == (HOURS,), f"{site} time mismatch")
            times[site_index] = time
            raw = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in FORCING_NAMES}
            forcing = engineer_forcing(raw, time).astype(np.float32)
            surface = _site_static(dataset).astype(np.float32)
            require(str(dataset.variables["GPP"].units) == "gC/m^2/day", f"{site} GPP units mismatch")
            for member_position, member in enumerate(snapshot.development_ranked):
                static = np.concatenate((params[member_position], surface, [upstream[name][site_index, member_position] for name in UPSTREAM_NAMES])).astype(np.float32)
                require(static.shape == (23,) and np.all(np.isfinite(static)), "static feature mismatch")
                X[site_index, member_position, :, :len(FORCING_FEATURE_NAMES)] = forcing
                X[site_index, member_position, :, len(FORCING_FEATURE_NAMES):] = static
                source_index = int(member[1:]) - 1
                target = np.asarray(dataset.variables["GPP"][source_index, :], dtype=np.float32)
                require(target.shape == (HOURS,) and np.all(np.isfinite(target)), f"{site} GPP target invalid")
                y[site_index, member_position] = target
    X.flush(); y.flush(); times.flush()
    layout = {
        "schema": RAW_SCHEMA, "sites": list(SITES), "development_member_ids": list(snapshot.development_ranked),
        "rows": len(SITES) * DEVELOPMENT_MEMBERS * HOURS, "features": FEATURE_COUNT,
        "hours_per_member": HOURS, "feature_names": list(names), "feature_schema_sha256": schema_sha256(names),
        "dtype": "float32", "x_file": x_path.name, "y_file": y_path.name, "time_file": time_path.name,
        "upstream_mode": "published_all819_in_sample", "validation_label": "fixed_upstream_gpp_stage",
        "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "layout.json", layout)
    manifest = {
        "schema": "three-stage-gpp-iter006-raw-manifest-v1", "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"], "predicted_cn_sha256": config["predicted_cn_sha256"],
        "split_manifest_sha256": config["repeated_split_manifest_sha256"],
        "layout_sha256": sha256_file(output / "layout.json"), "x_sha256": sha256_file(x_path),
        "y_sha256": sha256_file(y_path), "time_sha256": sha256_file(time_path),
        "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "raw_manifest.json", manifest)
    return manifest


def load_raw(path: Path) -> tuple[dict[str, Any], np.memmap, np.memmap, np.memmap]:
    layout = json.loads((path / "layout.json").read_text(encoding="utf-8"))
    require(layout["schema"] == RAW_SCHEMA, "raw layout schema mismatch")
    X = np.memmap(path / layout["x_file"], mode="r", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS, FEATURE_COUNT))
    y = np.memmap(path / layout["y_file"], mode="r", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS))
    times = np.memmap(path / layout["time_file"], mode="r", dtype=np.int64, shape=(len(SITES), HOURS))
    return layout, X, y, times


def validate_raw(config: Mapping[str, Any], path: Path, *, full_hashes: bool = True) -> dict[str, Any]:
    manifest = json.loads((path / "raw_manifest.json").read_text(encoding="utf-8"))
    layout, X, y, times = load_raw(path)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(manifest["snapshot_sha256"] == snapshot.snapshot_sha256 == config["snapshot_sha256"], "raw snapshot mismatch")
    require(manifest["global_split_sha256"] == config["global_split_sha256"], "raw global split mismatch")
    require(manifest["predicted_cn_sha256"] == config["predicted_cn_sha256"], "raw upstream mismatch")
    raw_source_split_sha256 = config.get(
        "raw_source_split_manifest_sha256", config["repeated_split_manifest_sha256"]
    )
    require(manifest["split_manifest_sha256"] == raw_source_split_sha256, "raw source split mismatch")
    require(layout["development_member_ids"] == list(snapshot.development_ranked), "raw member order mismatch")
    require(layout["feature_names"] == list(feature_names(snapshot)), "raw feature order mismatch")
    require(layout["feature_schema_sha256"] == schema_sha256(feature_names(snapshot)), "raw feature schema mismatch")
    require(layout["rows"] == 100442160 and layout["features"] == FEATURE_COUNT, "raw shape metadata mismatch")
    require(layout["fixed_test_access"] is False and layout["spinup_execution"] is False, "raw boundary mismatch")
    sample_members = (0, 409, 818)
    sample_hours = (0, 719, HOURS - 1)
    require(np.all(np.isfinite(X[:, sample_members][:, :, sample_hours])), "raw X samples invalid")
    require(np.all(np.isfinite(y[:, sample_members][:, :, sample_hours])), "raw y samples invalid")
    require(all(np.array_equal(times[index], np.arange(HOURS)) for index in range(len(SITES))), "raw time mismatch")
    upstream = _handoff(Path(config["predicted_cn_handoff"]), snapshot)
    params = snapshot._parameter_values(snapshot.development_ranked)
    reconstructed = 0
    with ExitStack() as stack:
        datasets = {
            site: stack.enter_context(Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r"))
            for site in SITES
        }
        for site_index, site in enumerate(SITES):
            dataset = datasets[site]
            source_time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
            raw_forcing = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in FORCING_NAMES}
            forcing = engineer_forcing(raw_forcing, source_time).astype(np.float32)
            surface = _site_static(dataset).astype(np.float32)
            for member_position in sample_members:
                member = snapshot.development_ranked[member_position]
                static = np.concatenate((params[member_position], surface, [upstream[name][site_index, member_position] for name in UPSTREAM_NAMES])).astype(np.float32)
                for hour in sample_hours:
                    expected_x = np.concatenate((forcing[hour], static)).astype(np.float32)
                    observed_x = np.asarray(X[site_index, member_position, hour], dtype=np.float32)
                    require(np.array_equal(observed_x, expected_x), f"raw source feature reconstruction mismatch: {site}/{member}/{hour}")
                    source_index = int(member[1:]) - 1
                    expected_y = np.float32(dataset.variables["GPP"][source_index, hour])
                    require(np.asarray(y[site_index, member_position, hour], dtype=np.float32) == expected_y, f"raw source target reconstruction mismatch: {site}/{member}/{hour}")
                    reconstructed += 1
    if full_hashes:
        require(sha256_file(path / layout["x_file"]) == manifest["x_sha256"], "raw X hash mismatch")
        require(sha256_file(path / layout["y_file"]) == manifest["y_sha256"], "raw y hash mismatch")
        require(sha256_file(path / layout["time_file"]) == manifest["time_sha256"], "raw time hash mismatch")
    report = {
        "schema": "three-stage-gpp-iter006-raw-validation-v1", "result": "pass",
        "rows": layout["rows"], "features": layout["features"], "full_hashes": full_hashes,
        "reconstructed_source_rows": reconstructed,
        "fixed_test_access": False, "spinup_execution": False,
    }
    return report


def _positions(layout: Mapping[str, Any], members: Sequence[str]) -> np.ndarray:
    mapping = {member: index for index, member in enumerate(layout["development_member_ids"])}
    require(len(mapping) == DEVELOPMENT_MEMBERS, "member-position map mismatch")
    result = np.asarray([mapping[str(member)] for member in members], dtype=np.int64)
    require(result.size == len(set(result.tolist())), "duplicate selected member position")
    return result


def _fit_scalers(X: np.memmap, y: np.memmap, positions: np.ndarray, chunk_rows: int) -> tuple[StandardScaler, StandardScaler]:
    x_scaler = StandardScaler(copy=True)
    y_scaler = StandardScaler(copy=True)
    member_chunk = max(1, chunk_rows // HOURS)
    for site_index in range(len(SITES)):
        for start in range(0, positions.size, member_chunk):
            selected = positions[start:start + member_chunk]
            x_block = np.asarray(X[site_index, selected], dtype=np.float32).reshape(-1, FEATURE_COUNT)
            y_block = np.asarray(y[site_index, selected], dtype=np.float32).reshape(-1, 1)
            x_scaler.partial_fit(x_block)
            y_scaler.partial_fit(y_block)
    return x_scaler, y_scaler


def _materialize_scaled(
    X: np.memmap, y: np.memmap, train_positions: np.ndarray, validation_positions: np.ndarray,
    x_scaler: StandardScaler, y_scaler: StandardScaler, output: Path,
) -> tuple[dict[str, Any], np.memmap, np.memmap]:
    total_rows = len(SITES) * DEVELOPMENT_MEMBERS * HOURS
    train_rows = len(SITES) * TRAIN_MEMBERS * HOURS
    x_path = output / "X_scaled_float32.dat"
    y_path = output / "y_scaled_float32.dat"
    scaled_x = np.memmap(x_path, mode="w+", dtype=np.float32, shape=(total_rows, FEATURE_COUNT))
    scaled_y = np.memmap(y_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    offsets: list[dict[str, Any]] = []
    cursor = 0
    for partition, positions in (("train", train_positions), ("validation", validation_positions)):
        for site_index, site in enumerate(SITES):
            start = cursor
            for position in positions:
                end = cursor + HOURS
                raw_x = np.asarray(X[site_index, position], dtype=np.float32)
                raw_y = np.asarray(y[site_index, position], dtype=np.float32).reshape(-1, 1)
                scaled_x[cursor:end] = x_scaler.transform(raw_x).astype(np.float32)
                scaled_y[cursor:end] = y_scaler.transform(raw_y).astype(np.float32).ravel()
                cursor = end
            offsets.append({"partition": partition, "site": site, "start": start, "end": cursor})
    require(cursor == total_rows and offsets[1]["end"] == train_rows, "scaled layout mismatch")
    scaled_x.flush(); scaled_y.flush()
    layout = {"rows": total_rows, "train_rows": train_rows, "validation_rows": total_rows - train_rows, "offsets": offsets}
    return layout, scaled_x, scaled_y


def _metric_rows(
    split_id: int, layout: Mapping[str, Any], y_scaled: np.ndarray, predictions: np.ndarray,
    y_mean: float, y_scale: float, iterations: int, warning_count: int,
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    moments: dict[str, np.ndarray] = {}
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    validation_member_count = VALIDATION_MEMBERS
    for partition in ("train", "validation"):
        pooled_truth: dict[str, list[np.ndarray]] = {resolution: [] for resolution in RESOLUTIONS}
        pooled_prediction: dict[str, list[np.ndarray]] = {resolution: [] for resolution in RESOLUTIONS}
        for site_index, site in enumerate(SITES):
            item = next(value for value in layout["offsets"] if value["partition"] == partition and value["site"] == site)
            start, end = int(item["start"]), int(item["end"])
            member_count = TRAIN_MEMBERS if partition == "train" else VALIDATION_MEMBERS
            truth = np.asarray(y_scaled[start:end], dtype=np.float64) * y_scale + y_mean
            predicted = np.asarray(predictions[start:end], dtype=np.float64)
            truth_daily = truth.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1)
            predicted_daily = predicted.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1)
            for resolution, observed, estimate in (("hourly", truth, predicted), ("daily", truth_daily, predicted_daily)):
                metrics = _metrics(observed, estimate)
                row = {"split_id": split_id, "partition": partition, "site": site, "resolution": resolution,
                       "expected_count": int(observed.size), "valid_count": int(observed.size), **metrics,
                       "model_iterations": iterations, "convergence_warning_count": warning_count,
                       "finite_prediction_pass": True, "reload_validation_pass": True}
                row["r2_train_validation_gap"] = ""
                row["rmse_validation_train_ratio"] = ""
                rows.append(row); by_key[(partition, site, resolution)] = row
                pooled_truth[resolution].append(observed); pooled_prediction[resolution].append(estimate)
                if partition == "validation":
                    residual = (estimate - observed).reshape(validation_member_count, -1)
                    prefix = f"{site}_{resolution}"
                    moments[f"{prefix}_count"] = np.full(validation_member_count, residual.shape[1], dtype=np.int64)
                    moments[f"{prefix}_sum"] = np.sum(residual, axis=1, dtype=np.float64)
                    moments[f"{prefix}_sumsq"] = np.sum(residual * residual, axis=1, dtype=np.float64)
        for resolution in RESOLUTIONS:
            observed = np.concatenate(pooled_truth[resolution]); estimate = np.concatenate(pooled_prediction[resolution])
            metrics = _metrics(observed, estimate)
            row = {"split_id": split_id, "partition": partition, "site": "pooled", "resolution": resolution,
                   "expected_count": int(observed.size), "valid_count": int(observed.size), **metrics,
                   "model_iterations": iterations, "convergence_warning_count": warning_count,
                   "finite_prediction_pass": True, "reload_validation_pass": True,
                   "r2_train_validation_gap": "", "rmse_validation_train_ratio": ""}
            rows.append(row); by_key[(partition, "pooled", resolution)] = row
    for site in (*SITES, "pooled"):
        for resolution in RESOLUTIONS:
            train = by_key[("train", site, resolution)]
            validation = by_key[("validation", site, resolution)]
            gap = float(train["r2"]) - float(validation["r2"])
            ratio = float(validation["rmse"]) / float(train["rmse"])
            train["r2_train_validation_gap"] = gap; validation["r2_train_validation_gap"] = gap
            train["rmse_validation_train_ratio"] = ratio; validation["rmse_validation_train_ratio"] = ratio
    return rows, moments


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path.name}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def fit_split(config: Mapping[str, Any], raw_path: Path, split_id: int, output: Path, *, smoke: bool = False) -> dict[str, Any]:
    require(not output.exists(), f"split output exists: {output}")
    output.mkdir(parents=True)
    layout, X, y, _ = load_raw(raw_path)
    splits = _load_split_manifest(config)
    item = splits["splits"][split_id]
    train_members = list(item["train_member_ids"])
    validation_members = list(item["validation_member_ids"])
    train_positions = _positions(layout, train_members)
    validation_positions = _positions(layout, validation_members)
    if smoke:
        train_positions = train_positions[:80]
        validation_positions = validation_positions[:20]
        rows_per_member = 1440
        x_train = np.concatenate([np.asarray(X[s, train_positions, :rows_per_member]).reshape(-1, FEATURE_COUNT) for s in range(len(SITES))])
        y_train = np.concatenate([np.asarray(y[s, train_positions, :rows_per_member]).reshape(-1) for s in range(len(SITES))])
        x_scaler = StandardScaler().fit(x_train); y_scaler = StandardScaler().fit(y_train.reshape(-1, 1))
        model = _model(config, smoke=True)
        model.fit(x_scaler.transform(x_train).astype(np.float32), y_scaler.transform(y_train.reshape(-1, 1)).astype(np.float32).ravel())
        x_val = np.concatenate([np.asarray(X[s, validation_positions, :rows_per_member]).reshape(-1, FEATURE_COUNT) for s in range(len(SITES))])
        prediction = model.predict(x_scaler.transform(x_val).astype(np.float32))
        require(np.all(np.isfinite(prediction)), "smoke prediction invalid")
        report = {"schema": "three-stage-gpp-iter006-smoke-v1", "result": "pass", "split_id": split_id,
                  "train_members": 80, "validation_members": 20, "hours": rows_per_member,
                  "fixed_test_access": False, "spinup_execution": False}
        write_json(output / "smoke_report.json", report)
        return report
    x_scaler, y_scaler = _fit_scalers(X, y, train_positions, int(config["scale_chunk_rows"]))
    scaled_layout, scaled_x, scaled_y = _materialize_scaled(X, y, train_positions, validation_positions, x_scaler, y_scaler, output)
    model = _model(config)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(scaled_x[:scaled_layout["train_rows"]], scaled_y[:scaled_layout["train_rows"]])
    warning_count = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    predictions_path = output / "predictions_physical_float32.dat"
    predictions = np.memmap(predictions_path, mode="w+", dtype=np.float32, shape=(scaled_layout["rows"],))
    chunk = int(config["prediction_chunk_rows"])
    y_mean, y_scale = float(y_scaler.mean_[0]), float(y_scaler.scale_[0])
    for start in range(0, scaled_layout["rows"], chunk):
        end = min(start + chunk, scaled_layout["rows"])
        estimate = model.predict(scaled_x[start:end]).astype(np.float64) * y_scale + y_mean
        require(np.all(np.isfinite(estimate)), "split prediction invalid")
        predictions[start:end] = estimate.astype(np.float32)
    predictions.flush()
    rows, moments = _metric_rows(split_id, scaled_layout, scaled_y, predictions, y_mean, y_scale, int(model.n_iter_), warning_count)
    metric_path = output / "metrics.csv"; _write_csv(metric_path, rows)
    moments["validation_member_ids"] = np.asarray(validation_members, dtype="U6")
    np.savez(output / "member_moments.npz", **moments)
    artifact = {
        "schema": "three-stage-gpp-iter006-robustness-artifact-v1", "model": model,
        "x_mean": x_scaler.mean_, "x_scale": x_scaler.scale_, "y_mean": y_mean, "y_scale": y_scale,
        "feature_names": layout["feature_names"], "feature_schema_sha256": layout["feature_schema_sha256"],
        "model_config": config["model_config"], "fit_scope": {"split_id": split_id,
        "train_member_ids": train_members, "validation_member_ids": validation_members, "fixed_test_access": False},
        "upstream_mode": layout["upstream_mode"], "validation_label": layout["validation_label"],
    }
    artifact_path = output / "gpp_robustness_artifact.pkl"
    with artifact_path.open("wb") as handle:
        pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
    np.savez(output / "scalers.npz", x_mean=x_scaler.mean_, x_scale=x_scaler.scale_, y_mean=y_scaler.mean_, y_scale=y_scaler.scale_)
    write_json(output / "scaled_layout.json", scaled_layout)
    report = {
        "schema": "three-stage-gpp-iter006-split-v1", "result": "pass", "split_id": split_id,
        "artifact_sha256": sha256_file(artifact_path), "predictions_sha256": sha256_file(predictions_path),
        "metrics_sha256": sha256_file(metric_path), "moments_sha256": sha256_file(output / "member_moments.npz"),
        "model_iterations": int(model.n_iter_), "convergence_warning_count": warning_count,
        "train_member_count": TRAIN_MEMBERS, "validation_member_count": VALIDATION_MEMBERS,
        "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "split_report.json", report)
    return report


def validate_split(config: Mapping[str, Any], raw_path: Path, split_path: Path) -> dict[str, Any]:
    report = json.loads((split_path / "split_report.json").read_text(encoding="utf-8"))
    split_id = int(report["split_id"])
    require(report["result"] == "pass" and report["fixed_test_access"] is False, "split report ineligible")
    require(sha256_file(split_path / "gpp_robustness_artifact.pkl") == report["artifact_sha256"], "split artifact hash mismatch")
    require(sha256_file(split_path / "predictions_physical_float32.dat") == report["predictions_sha256"], "split prediction hash mismatch")
    with (split_path / "gpp_robustness_artifact.pkl").open("rb") as handle:
        artifact = pickle.load(handle)
    require(artifact["schema"] == "three-stage-gpp-iter006-robustness-artifact-v1", "split artifact schema mismatch")
    raw_layout, X_raw, _, _ = load_raw(raw_path)
    scaled_layout = json.loads((split_path / "scaled_layout.json").read_text(encoding="utf-8"))
    X_scaled = np.memmap(split_path / "X_scaled_float32.dat", mode="r", dtype=np.float32, shape=(scaled_layout["rows"], FEATURE_COUNT))
    predictions = np.memmap(split_path / "predictions_physical_float32.dat", mode="r", dtype=np.float32, shape=(scaled_layout["rows"],))
    chunk = int(config["prediction_chunk_rows"])
    selected_chunks = (0, scaled_layout["train_rows"] // chunk, (scaled_layout["rows"] - 1) // chunk)
    maxima = []
    for chunk_index in selected_chunks:
        start = chunk_index * chunk; end = min(start + chunk, scaled_layout["rows"])
        replay = artifact["model"].predict(X_scaled[start:end]).astype(np.float64) * float(artifact["y_scale"]) + float(artifact["y_mean"])
        maxima.append(float(np.max(np.abs(replay - np.asarray(predictions[start:end], dtype=np.float64)))))
        require(np.allclose(replay, predictions[start:end], rtol=config["reload_rtol"], atol=config["reload_atol"]), "original-chunk replay mismatch")
    members = artifact["fit_scope"]["train_member_ids"][:1]
    position = _positions(raw_layout, members)[0]
    raw_sample = np.asarray(X_raw[0, position, :1000], dtype=np.float64)
    exact_repeat = {}
    cross = {}
    first = None
    for size in (1, 7, 1000):
        observed = predict_artifact(artifact, raw_sample[:size])
        repeated = predict_artifact(artifact, raw_sample[:size])
        require(np.array_equal(observed, repeated), "same-batch repeatability mismatch")
        exact_repeat[str(size)] = True
        if first is None:
            first = float(observed[0])
        cross[str(size)] = float(observed[0] - first)
    diagnostics = {"schema": "three-stage-gpp-iter006-split-reload-v1", "split_id": split_id,
                   "result": "pass", "chunk_max_absolute_differences": maxima,
                   "same_batch_exact_repeatability": exact_repeat, "cross_batch_first_prediction_difference": cross}
    write_json(split_path / "reload_validation.json", diagnostics)
    report["reload_validation_sha256"] = sha256_file(split_path / "reload_validation.json")
    write_json(split_path / "split_report.json", report)
    return diagnostics


def _read_metrics(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _independent_metric_values(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    """Recalculate metric evidence without calling the production metric helper."""
    observed = np.asarray(truth, dtype=np.float64).reshape(-1)
    estimated = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(observed.size == estimated.size and observed.size > 1, "independent metric inputs invalid")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(estimated)), "independent metric inputs nonfinite")
    residual = estimated - observed
    centered_truth = observed - float(np.mean(observed))
    denominator = float(np.sum(centered_truth * centered_truth))
    require(denominator > 0.0, "independent metric R2 denominator invalid")
    squared_residual = residual * residual
    values: dict[str, float | int] = {
        "expected_count": int(observed.size),
        "valid_count": int(observed.size),
        "r2": float(1.0 - float(np.sum(squared_residual)) / denominator),
        "rmse": float(np.sqrt(float(np.mean(squared_residual)))),
        "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)),
        "residual_std": float(np.sqrt(float(np.mean((residual - float(np.mean(residual))) ** 2)))),
        "gap_count": 0,
        "coverage_fraction": 1.0,
    }
    quantile_values = np.quantile(residual, np.asarray(QUANTILES, dtype=np.float64), method="linear")
    for quantile, value in zip(QUANTILES, quantile_values):
        values[f"q{str(quantile).replace('.', '_')}"] = float(value)
    return values


def _independently_validate_leaf_metrics(leaf: Path, split_id: int, recorded: Sequence[Mapping[str, str]]) -> None:
    """Rebuild all train/validation, site/pooled, hourly/daily leaf metrics from arrays."""
    scaled_layout = json.loads((leaf / "scaled_layout.json").read_text(encoding="utf-8"))
    rows = int(scaled_layout["rows"])
    y_scaled = np.memmap(leaf / "y_scaled_float32.dat", mode="r", dtype=np.float32, shape=(rows,))
    predictions = np.memmap(leaf / "predictions_physical_float32.dat", mode="r", dtype=np.float32, shape=(rows,))
    with (leaf / "gpp_robustness_artifact.pkl").open("rb") as handle:
        artifact = pickle.load(handle)
    y_mean = float(artifact["y_mean"]); y_scale = float(artifact["y_scale"])
    rebuilt: dict[tuple[str, str, str], dict[str, float | int]] = {}
    for partition in ("train", "validation"):
        member_count = TRAIN_MEMBERS if partition == "train" else VALIDATION_MEMBERS
        pooled: dict[str, list[np.ndarray]] = {"truth_hourly": [], "prediction_hourly": [], "truth_daily": [], "prediction_daily": []}
        for site in SITES:
            offset = next(item for item in scaled_layout["offsets"] if item["partition"] == partition and item["site"] == site)
            start, end = int(offset["start"]), int(offset["end"])
            truth_hourly = np.asarray(y_scaled[start:end], dtype=np.float64) * y_scale + y_mean
            prediction_hourly = np.asarray(predictions[start:end], dtype=np.float64)
            truth_daily = truth_hourly.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1)
            prediction_daily = prediction_hourly.reshape(member_count, DAY_COUNT, 24).mean(axis=2).reshape(-1)
            rebuilt[(partition, site, "hourly")] = _independent_metric_values(truth_hourly, prediction_hourly)
            rebuilt[(partition, site, "daily")] = _independent_metric_values(truth_daily, prediction_daily)
            pooled["truth_hourly"].append(truth_hourly); pooled["prediction_hourly"].append(prediction_hourly)
            pooled["truth_daily"].append(truth_daily); pooled["prediction_daily"].append(prediction_daily)
        for resolution in RESOLUTIONS:
            rebuilt[(partition, "pooled", resolution)] = _independent_metric_values(
                np.concatenate(pooled[f"truth_{resolution}"]), np.concatenate(pooled[f"prediction_{resolution}"])
            )
    for site in (*SITES, "pooled"):
        for resolution in RESOLUTIONS:
            train = rebuilt[("train", site, resolution)]; validation = rebuilt[("validation", site, resolution)]
            gap = float(train["r2"]) - float(validation["r2"])
            ratio = float(validation["rmse"]) / float(train["rmse"])
            train["r2_train_validation_gap"] = gap; validation["r2_train_validation_gap"] = gap
            train["rmse_validation_train_ratio"] = ratio; validation["rmse_validation_train_ratio"] = ratio
    require(len(recorded) == len(rebuilt) == 12, "independent leaf metric row count mismatch")
    integer_fields = ("expected_count", "valid_count", "gap_count")
    metric_fields = ("r2", "rmse", "mae", "bias", "residual_std", "coverage_fraction",
                     "q0_01", "q0_025", "q0_05", "q0_25", "q0_5", "q0_75", "q0_95", "q0_975", "q0_99")
    derived_fields = ("r2_train_validation_gap", "rmse_validation_train_ratio")
    for row in recorded:
        require(int(row["split_id"]) == split_id, "independent leaf split ID mismatch")
        key = (row["partition"], row["site"], row["resolution"])
        require(key in rebuilt, "independent leaf metric key mismatch")
        expected = rebuilt[key]
        for field in integer_fields:
            require(int(row[field]) == int(expected[field]), f"independent leaf {field} mismatch")
        for field in metric_fields:
            require(np.isclose(float(row[field]), float(expected[field]), rtol=1e-12, atol=1e-12), f"independent leaf {field} mismatch")
        # These two fields combine two independently accumulated metrics by subtraction or
        # division. Keep the direct metrics at 1e-12 above, while allowing only their bounded
        # compounded floating-point rounding in the derived comparison.
        for field in derived_fields:
            require(np.isclose(float(row[field]), float(expected[field]), rtol=1e-10, atol=1e-10), f"independent leaf {field} mismatch")


def aggregate(config: Mapping[str, Any], robustness_root: Path, output: Path) -> dict[str, Any]:
    require(not output.exists(), f"aggregate output exists: {output}")
    output.mkdir(parents=True)
    split_manifest = _load_split_manifest(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    appearance = validate_split_design(snapshot, split_manifest)
    metric_rows: list[dict[str, Any]] = []
    convergence_rows: list[dict[str, Any]] = []
    occurrence: dict[tuple[str, str, str], tuple[int, float, float]] = {}
    for split_id in range(SPLIT_COUNT):
        leaf = robustness_root / f"split_{split_id:02d}"
        report = json.loads((leaf / "split_report.json").read_text(encoding="utf-8"))
        require(report["result"] == "pass" and int(report["split_id"]) == split_id, "split result missing")
        reload_report = json.loads((leaf / "reload_validation.json").read_text(encoding="utf-8"))
        require(reload_report["result"] == "pass", "split reload validation missing")
        metric_rows.extend(_read_metrics(leaf / "metrics.csv"))
        convergence_rows.append({"split_id": split_id, "model_iterations": report["model_iterations"],
                                 "convergence_warning_count": report["convergence_warning_count"],
                                 "finite_prediction_pass": True, "reload_validation_pass": True})
        with np.load(leaf / "member_moments.npz", allow_pickle=False) as data:
            members = np.asarray(data["validation_member_ids"], dtype=str)
            for site in SITES:
                for resolution in RESOLUTIONS:
                    prefix = f"{site}_{resolution}"
                    for index, member in enumerate(members):
                        key = (site, resolution, member)
                        require(key not in occurrence or appearance[member] > 1, "unexpected duplicate occurrence")
                        count, total, sumsq = occurrence.get(key, (0, 0.0, 0.0))
                        occurrence[key] = (count + int(data[f"{prefix}_count"][index]),
                                           total + float(data[f"{prefix}_sum"][index]),
                                           sumsq + float(data[f"{prefix}_sumsq"][index]))
    require(len(metric_rows) == SPLIT_COUNT * 2 * 3 * 2, "metric row count mismatch")
    metric_path = output / "metric_distribution.csv"; _write_csv(metric_path, metric_rows)
    uncertainty_rows: list[dict[str, Any]] = []
    per_rep: dict[tuple[str, str], list[tuple[float, float]]] = {(site, resolution): [] for site in SITES for resolution in RESOLUTIONS}
    for row in metric_rows:
        if row["partition"] == "validation" and row["site"] in SITES:
            per_rep[(row["site"], row["resolution"])].append((float(row["bias"]), float(row["rmse"])))
            bias = float(row["bias"]); rmse = float(row["rmse"])
            uncertainty_rows.append({"estimate_scope": "per_repetition", "site": row["site"], "resolution": row["resolution"],
                                     "repetition": row["split_id"], "bias": bias, "rmse": rmse,
                                     "surrogate_error_variance": rmse * rmse,
                                     "centered_residual_variance": max(rmse * rmse - bias * bias, 0.0),
                                     "centered_residual_std": np.sqrt(max(rmse * rmse - bias * bias, 0.0)),
                                     "expected_count": row["expected_count"], "valid_count": row["valid_count"],
                                     "coverage_fraction": row["coverage_fraction"], "member_count": VALIDATION_MEMBERS,
                                     "occurrence_count": VALIDATION_MEMBERS, "member_balance_rule": "not_applicable_within_repetition",
                                     "residual_convention": "prediction minus ELM", "units": "gC/m^2/day",
                                     "snapshot_sha256": config["snapshot_sha256"], "split_design_sha256": config["split_design_sha256"],
                                     "gpp_configuration_sha256": config["gpp_configuration_sha256"],
                                     "upstream_release_manifest_sha256": config["spinup_release_manifest_sha256"]})
    aggregate_values: dict[tuple[str, str], tuple[float, float]] = {}
    for site in SITES:
        for resolution in RESOLUTIONS:
            member_means = []
            member_mean_squares = []
            total_count = 0
            for member in snapshot.development_ranked:
                count, total, sumsq = occurrence[(site, resolution, member)]
                expected_per_appearance = HOURS if resolution == "hourly" else DAY_COUNT
                require(count == appearance[member] * expected_per_appearance, "member moment count mismatch")
                member_means.append(total / count); member_mean_squares.append(sumsq / count); total_count += count
            bias = float(np.mean(member_means)); rmse = float(np.sqrt(np.mean(member_mean_squares)))
            aggregate_values[(site, resolution)] = (bias, rmse)
            uncertainty_rows.append({"estimate_scope": "member_balanced", "site": site, "resolution": resolution,
                                     "repetition": "", "bias": bias, "rmse": rmse,
                                     "surrogate_error_variance": rmse * rmse,
                                     "centered_residual_variance": max(rmse * rmse - bias * bias, 0.0),
                                     "centered_residual_std": np.sqrt(max(rmse * rmse - bias * bias, 0.0)),
                                     "expected_count": total_count, "valid_count": total_count, "coverage_fraction": 1.0,
                                     "member_count": DEVELOPMENT_MEMBERS, "occurrence_count": sum(appearance.values()),
                                     "member_balance_rule": "each member contributes equally after averaging its repeated held-out occurrences",
                                     "residual_convention": "prediction minus ELM", "units": "gC/m^2/day",
                                     "snapshot_sha256": config["snapshot_sha256"], "split_design_sha256": config["split_design_sha256"],
                                     "gpp_configuration_sha256": config["gpp_configuration_sha256"],
                                     "upstream_release_manifest_sha256": config["spinup_release_manifest_sha256"]})
    uncertainty_path = output / "uncertainty_estimates.csv"; _write_csv(uncertainty_path, uncertainty_rows)
    with (output / "convergence.json").open("x", encoding="utf-8") as handle:
        json.dump({"schema": "three-stage-gpp-iter006-convergence-v1", "splits": convergence_rows}, handle, indent=2, sort_keys=True); handle.write("\n")
    shutil.copy2(Path(config["repeated_split_manifest"]), output / "repeated_split_manifest.json")
    nc_path = output / "gpp_uncertainty.nc"
    with Dataset(str(nc_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-gpp-surrogate-uncertainty-v1"
        dataset.snapshot_sha256 = config["snapshot_sha256"]
        dataset.split_design_sha256 = config["split_design_sha256"]
        dataset.gpp_configuration_sha256 = config["gpp_configuration_sha256"]
        dataset.spinup_release_manifest_sha256 = config["spinup_release_manifest_sha256"]
        dataset.residual_convention = "prediction minus ELM in gC/m^2/day"
        dataset.pooling = "member-balanced: each member equal after averaging repeated held-out occurrences"
        dataset.daily_aggregation = "complete 24-hour mean of paired hourly target and prediction"
        dataset.validation_label = "fixed_upstream_gpp_stage"
        dataset.scope = "surrogate component only; excludes observations, fixed test, SR, and full-chain uncertainty"
        dataset.release_basis = config.get("release_basis", "performance_gate")
        dataset.performance_gate_applied = int(bool(config.get("performance_gate_applied", True)))
        dataset.createDimension("site", len(SITES)); dataset.createDimension("resolution", len(RESOLUTIONS)); dataset.createDimension("repetition", SPLIT_COUNT)
        dataset.createVariable("site", str, ("site",))[:] = np.asarray(SITES, dtype=object)
        dataset.createVariable("resolution", str, ("resolution",))[:] = np.asarray(RESOLUTIONS, dtype=object)
        dataset.createVariable("repetition", "i2", ("repetition",))[:] = np.arange(SPLIT_COUNT, dtype=np.int16)
        bias_var = dataset.createVariable("GPP_error_bias", "f8", ("site", "resolution"))
        rmse_var = dataset.createVariable("GPP_error_rmse", "f8", ("site", "resolution"))
        rep_bias_var = dataset.createVariable("GPP_per_repetition_error_bias", "f8", ("site", "resolution", "repetition"))
        rep_rmse_var = dataset.createVariable("GPP_per_repetition_error_rmse", "f8", ("site", "resolution", "repetition"))
        bias_var[:] = [[aggregate_values[(site, resolution)][0] for resolution in RESOLUTIONS] for site in SITES]
        rmse_var[:] = [[aggregate_values[(site, resolution)][1] for resolution in RESOLUTIONS] for site in SITES]
        rep_bias_var[:] = [[[value[0] for value in per_rep[(site, resolution)]] for resolution in RESOLUTIONS] for site in SITES]
        rep_rmse_var[:] = [[[value[1] for value in per_rep[(site, resolution)]] for resolution in RESOLUTIONS] for site in SITES]
        for variable in (bias_var, rmse_var, rep_bias_var, rep_rmse_var):
            variable.units = "gC/m^2/day"
    gate = (
        evaluate_gate(metric_rows)
        if bool(config.get("performance_gate_applied", True))
        else performance_assessment(metric_rows)
    )
    report = {
        "schema": "three-stage-gpp-iter006-uncertainty-report-v1", "result": "pass",
        "gate": gate, "snapshot_sha256": config["snapshot_sha256"],
        "split_design_sha256": config["split_design_sha256"], "fixed_test_access": False,
        "release_basis": config.get("release_basis", "performance_gate"),
        "performance_gate_applied": bool(config.get("performance_gate_applied", True)),
        "member_balance_rule": "equal member weight after within-member occurrence averaging",
        "files": package_files(output, exclude={"uncertainty_report.json"}),
    }
    write_json(output / "uncertainty_report.json", report)
    return report


def evaluate_gate(metric_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    results: dict[str, Any] = {}; passed = True
    for site in SITES:
        for resolution in RESOLUTIONS:
            selected = [row for row in metric_rows if row["partition"] == "validation" and row["site"] == site and row["resolution"] == resolution]
            require(len(selected) == SPLIT_COUNT, "gate metric count mismatch")
            r2 = np.asarray([float(row["r2"]) for row in selected]); rmse = np.asarray([float(row["rmse"]) for row in selected]); bias = np.asarray([float(row["bias"]) for row in selected])
            r2_q10 = float(np.quantile(r2, 0.10, method="linear")); rmse_q90 = float(np.quantile(rmse, 0.90, method="linear")); median_abs_bias = float(np.median(np.abs(bias)))
            r2_floor = 0.85 if resolution == "hourly" else 0.75
            rmse_ceiling = 5.0 if resolution == "hourly" else 3.0
            row_pass = r2_q10 >= r2_floor and rmse_q90 <= rmse_ceiling and median_abs_bias <= 0.35 and all(float(row["coverage_fraction"]) == 1.0 for row in selected)
            results[f"{site}_{resolution}"] = {"r2_q10": r2_q10, "r2_floor": r2_floor, "rmse_q90": rmse_q90,
                                                       "rmse_ceiling": rmse_ceiling, "median_absolute_bias": median_abs_bias,
                                                       "bias_ceiling": 0.35, "pass": bool(row_pass)}
            passed = passed and row_pass
    return {"result": "pass" if passed else "fail", "quantile_method": "linear", "by_site_resolution": results}


def performance_assessment(metric_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Record descriptive robustness quantiles without applying release thresholds."""
    results: dict[str, Any] = {}
    for site in SITES:
        for resolution in RESOLUTIONS:
            selected = [
                row for row in metric_rows
                if row["partition"] == "validation"
                and row["site"] == site
                and row["resolution"] == resolution
            ]
            require(len(selected) == SPLIT_COUNT, "assessment metric count mismatch")
            r2 = np.asarray([float(row["r2"]) for row in selected], dtype=np.float64)
            rmse = np.asarray([float(row["rmse"]) for row in selected], dtype=np.float64)
            bias = np.asarray([float(row["bias"]) for row in selected], dtype=np.float64)
            results[f"{site}_{resolution}"] = {
                "r2_q10": float(np.quantile(r2, 0.10, method="linear")),
                "rmse_q90": float(np.quantile(rmse, 0.90, method="linear")),
                "median_absolute_bias": float(np.median(np.abs(bias))),
                "coverage_complete": all(float(row["coverage_fraction"]) == 1.0 for row in selected),
            }
    return {
        "applied": False,
        "result": "not_applicable",
        "release_basis": "iter007_best_configuration",
        "quantile_method": "linear",
        "by_site_resolution": results,
    }


def validate_aggregate(config: Mapping[str, Any], robustness_root: Path, output: Path) -> dict[str, Any]:
    metrics = _read_metrics(output / "metric_distribution.csv")
    require(len(metrics) == SPLIT_COUNT * 2 * 3 * 2, "aggregate metric row count mismatch")
    require({int(row["split_id"]) for row in metrics} == set(range(SPLIT_COUNT)), "aggregate split coverage mismatch")
    rebuilt_metrics: list[dict[str, str]] = []
    for split_id in range(SPLIT_COUNT):
        leaf = robustness_root / f"split_{split_id:02d}"
        report = json.loads((leaf / "split_report.json").read_text(encoding="utf-8"))
        reload_report = json.loads((leaf / "reload_validation.json").read_text(encoding="utf-8"))
        require(report["result"] == reload_report["result"] == "pass", "independent split eligibility mismatch")
        require(int(report["split_id"]) == split_id, "independent split ID mismatch")
        require(sha256_file(leaf / "metrics.csv") == report["metrics_sha256"], "independent leaf metrics hash mismatch")
        require(sha256_file(leaf / "member_moments.npz") == report["moments_sha256"], "independent leaf moments hash mismatch")
        leaf_metrics = _read_metrics(leaf / "metrics.csv")
        _independently_validate_leaf_metrics(leaf, split_id, leaf_metrics)
        rebuilt_metrics.extend(leaf_metrics)
    require(rebuilt_metrics == metrics, "aggregate metric table differs from leaf evidence")
    for row in metrics:
        require(float(row["coverage_fraction"]) == 1.0 and int(row["gap_count"]) == 0, "aggregate coverage mismatch")
        for field in ("r2", "rmse", "mae", "bias", "residual_std", "q0_01", "q0_025", "q0_05", "q0_25", "q0_5", "q0_75", "q0_95", "q0_975", "q0_99"):
            require(np.isfinite(float(row[field])), f"aggregate nonfinite {field}")
    gate = (
        evaluate_gate(rebuilt_metrics)
        if bool(config.get("performance_gate_applied", True))
        else performance_assessment(rebuilt_metrics)
    )
    generated_report = json.loads((output / "uncertainty_report.json").read_text(encoding="utf-8"))
    require(generated_report["gate"] == gate, "independently recomputed gate mismatch")
    estimates = _read_metrics(output / "uncertainty_estimates.csv")
    require(len(estimates) == len(SITES) * len(RESOLUTIONS) * (SPLIT_COUNT + 1), "uncertainty table row count mismatch")
    identity_fields = ("snapshot_sha256", "split_design_sha256", "gpp_configuration_sha256", "upstream_release_manifest_sha256")
    for row in estimates:
        for field in identity_fields:
            expected = config["spinup_release_manifest_sha256"] if field == "upstream_release_manifest_sha256" else config[field]
            require(row[field] == expected, f"uncertainty table identity mismatch: {field}")
    split_manifest = _load_split_manifest(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    appearance = validate_split_design(snapshot, split_manifest)
    occurrence: dict[tuple[str, str, str], tuple[int, float, float]] = {}
    for split_id in range(SPLIT_COUNT):
        leaf = robustness_root / f"split_{split_id:02d}"
        with np.load(leaf / "member_moments.npz", allow_pickle=False) as data:
            members = np.asarray(data["validation_member_ids"], dtype=str)
            require(members.tolist() == list(split_manifest["splits"][split_id]["validation_member_ids"]), "independent moment member order mismatch")
            for site in SITES:
                for resolution in RESOLUTIONS:
                    prefix = f"{site}_{resolution}"
                    for index, member in enumerate(members):
                        key = (site, resolution, member); count, total, sumsq = occurrence.get(key, (0, 0.0, 0.0))
                        occurrence[key] = (count + int(data[f"{prefix}_count"][index]), total + float(data[f"{prefix}_sum"][index]), sumsq + float(data[f"{prefix}_sumsq"][index]))
    rebuilt_aggregate: dict[tuple[str, str], tuple[float, float]] = {}
    for site in SITES:
        for resolution in RESOLUTIONS:
            expected_per_appearance = HOURS if resolution == "hourly" else DAY_COUNT
            means = []; mean_squares = []
            for member in snapshot.development_ranked:
                count, total, sumsq = occurrence[(site, resolution, member)]
                require(count == appearance[member] * expected_per_appearance, "independent member moment count mismatch")
                means.append(total / count); mean_squares.append(sumsq / count)
            rebuilt_aggregate[(site, resolution)] = (float(np.mean(means)), float(np.sqrt(np.mean(mean_squares))))
    with Dataset(str(output / "gpp_uncertainty.nc"), "r") as dataset:
        require(dataset.getncattr("schema") == "three-stage-gpp-surrogate-uncertainty-v1", "uncertainty schema mismatch")
        require(set(dataset.dimensions) == {"site", "resolution", "repetition"}, "uncertainty dimensions mismatch")
        require(len(dataset.dimensions["site"]) == len(SITES) and len(dataset.dimensions["resolution"]) == len(RESOLUTIONS), "uncertainty dimension size mismatch")
        require(len(dataset.dimensions["repetition"]) == SPLIT_COUNT, "uncertainty repetition size mismatch")
        required = {"site", "resolution", "repetition", "GPP_error_bias", "GPP_error_rmse", "GPP_per_repetition_error_bias", "GPP_per_repetition_error_rmse"}
        require(set(dataset.variables) == required, "uncertainty variable scope mismatch")
        require(np.asarray(dataset.variables["site"][:], dtype=str).tolist() == list(SITES), "uncertainty site mismatch")
        require(np.asarray(dataset.variables["resolution"][:], dtype=str).tolist() == list(RESOLUTIONS), "uncertainty resolution mismatch")
        require(np.array_equal(np.asarray(dataset.variables["repetition"][:], dtype=np.int64), np.arange(SPLIT_COUNT, dtype=np.int64)), "uncertainty repetition coordinate mismatch")
        expected_attributes = {
            "snapshot_sha256": config["snapshot_sha256"],
            "split_design_sha256": config["split_design_sha256"],
            "gpp_configuration_sha256": config["gpp_configuration_sha256"],
            "spinup_release_manifest_sha256": config["spinup_release_manifest_sha256"],
            "residual_convention": "prediction minus ELM in gC/m^2/day",
            "pooling": "member-balanced: each member equal after averaging repeated held-out occurrences",
            "daily_aggregation": "complete 24-hour mean of paired hourly target and prediction",
            "validation_label": "fixed_upstream_gpp_stage",
            "scope": "surrogate component only; excludes observations, fixed test, SR, and full-chain uncertainty",
            "release_basis": config.get("release_basis", "performance_gate"),
            "performance_gate_applied": int(bool(config.get("performance_gate_applied", True))),
        }
        for attribute, expected in expected_attributes.items():
            require(dataset.getncattr(attribute) == expected, f"uncertainty provenance mismatch: {attribute}")
        for variable_name in required - {"site", "resolution", "repetition"}:
            require(dataset.variables[variable_name].getncattr("units") == "gC/m^2/day", f"uncertainty units mismatch: {variable_name}")
        for site_index, site in enumerate(SITES):
            for resolution_index, resolution in enumerate(RESOLUTIONS):
                aggregate_row = next(row for row in estimates if row["estimate_scope"] == "member_balanced" and row["site"] == site and row["resolution"] == resolution)
                rebuilt_bias, rebuilt_rmse = rebuilt_aggregate[(site, resolution)]
                require(np.isclose(float(aggregate_row["bias"]), rebuilt_bias, rtol=1e-12, atol=1e-12), "uncertainty table aggregate bias mismatch")
                require(np.isclose(float(aggregate_row["rmse"]), rebuilt_rmse, rtol=1e-12, atol=1e-12), "uncertainty table aggregate RMSE mismatch")
                require(np.isclose(float(dataset.variables["GPP_error_bias"][site_index, resolution_index]), rebuilt_bias, rtol=1e-12, atol=1e-12), "aggregate bias mismatch")
                require(np.isclose(float(dataset.variables["GPP_error_rmse"][site_index, resolution_index]), rebuilt_rmse, rtol=1e-12, atol=1e-12), "aggregate RMSE mismatch")
                repetition_rows = sorted((row for row in estimates if row["estimate_scope"] == "per_repetition" and row["site"] == site and row["resolution"] == resolution), key=lambda row: int(row["repetition"]))
                source_rows = sorted((row for row in rebuilt_metrics if row["partition"] == "validation" and row["site"] == site and row["resolution"] == resolution), key=lambda row: int(row["split_id"]))
                source_bias = [float(row["bias"]) for row in source_rows]; source_rmse = [float(row["rmse"]) for row in source_rows]
                require(np.allclose([float(row["bias"]) for row in repetition_rows], source_bias, rtol=1e-12, atol=1e-12), "uncertainty table per-repetition bias mismatch")
                require(np.allclose([float(row["rmse"]) for row in repetition_rows], source_rmse, rtol=1e-12, atol=1e-12), "uncertainty table per-repetition RMSE mismatch")
                require(np.allclose(dataset.variables["GPP_per_repetition_error_bias"][site_index, resolution_index], source_bias, rtol=1e-12, atol=1e-12), "per-repetition bias mismatch")
                require(np.allclose(dataset.variables["GPP_per_repetition_error_rmse"][site_index, resolution_index], source_rmse, rtol=1e-12, atol=1e-12), "per-repetition RMSE mismatch")
    report = {"schema": "three-stage-gpp-iter006-aggregate-validation-v1", "result": "pass",
              "gate": gate, "metric_rows": len(metrics), "uncertainty_rows": len(estimates),
              "fixed_test_access": False, "files": package_files(output, exclude={"aggregate_validation.json"})}
    write_json(output / "aggregate_validation.json", report)
    return report


def _release_artifact(config: Mapping[str, Any], raw_layout: Mapping[str, Any], model: Any, x_scaler: StandardScaler, y_scaler: StandardScaler, members: Sequence[str]) -> dict[str, Any]:
    return {"schema": RELEASE_SCHEMA, "model": model, "x_mean": x_scaler.mean_, "x_scale": x_scaler.scale_,
            "y_mean": float(y_scaler.mean_[0]), "y_scale": float(y_scaler.scale_[0]),
            "feature_names": raw_layout["feature_names"], "feature_schema_sha256": raw_layout["feature_schema_sha256"],
            "model_config": config["model_config"], "fit_scope": {"kind": "all_development",
            "development_member_ids": list(members), "fixed_test_access": False},
            "snapshot_sha256": config["snapshot_sha256"], "upstream_release_manifest_sha256": config["spinup_release_manifest_sha256"],
            "predicted_cn_sha256": config["predicted_cn_sha256"], "upstream_mode": "published_all819_in_sample",
            "validation_label": "fixed_upstream_gpp_stage", "target_units": "gC/m^2/day"}


def fit_release(
    config: Mapping[str, Any], raw_path: Path, aggregate_path: Path | None, output: Path
) -> dict[str, Any]:
    require(not output.exists(), f"release output exists: {output}")
    package = output / "release_0001"; (package / "artifact").mkdir(parents=True); (package / "uncertainty").mkdir(); (package / "handoff").mkdir(); (package / "validation").mkdir()
    if aggregate_path is not None:
        aggregate_validation = json.loads((aggregate_path / "aggregate_validation.json").read_text(encoding="utf-8"))
        require(aggregate_validation["result"] == "pass", "aggregate validation not passed")
        expected_result = "pass" if bool(config.get("performance_gate_applied", True)) else "not_applicable"
        require(aggregate_validation["gate"]["result"] == expected_result, "release assessment mismatch")
    raw_layout, X, y, times = load_raw(raw_path)
    all_positions = np.arange(DEVELOPMENT_MEMBERS, dtype=np.int64)
    x_scaler, y_scaler = _fit_scalers(X, y, all_positions, int(config["scale_chunk_rows"]))
    # Reuse the partition materializer with an empty validation tail through an explicit all-member layout.
    total_rows = len(SITES) * DEVELOPMENT_MEMBERS * HOURS
    x_path = output / "X_release_scaled_float32.dat"; y_path = output / "y_release_scaled_float32.dat"
    scaled_x = np.memmap(x_path, mode="w+", dtype=np.float32, shape=(total_rows, FEATURE_COUNT)); scaled_y = np.memmap(y_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    cursor = 0
    for site_index in range(len(SITES)):
        for position in all_positions:
            end = cursor + HOURS
            scaled_x[cursor:end] = x_scaler.transform(np.asarray(X[site_index, position], dtype=np.float32)).astype(np.float32)
            scaled_y[cursor:end] = y_scaler.transform(np.asarray(y[site_index, position], dtype=np.float32).reshape(-1, 1)).astype(np.float32).ravel()
            cursor = end
    require(cursor == total_rows, "release scaled row mismatch"); scaled_x.flush(); scaled_y.flush()
    model = _model(config)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning); model.fit(scaled_x, scaled_y)
    warning_count = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    artifact = _release_artifact(config, raw_layout, model, x_scaler, y_scaler, raw_layout["development_member_ids"])
    artifact_path = package / "artifact" / "gpp_surrogate_artifact.pkl"
    with artifact_path.open("wb") as handle:
        pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
    artifact_manifest = {"schema": "three-stage-gpp-release-artifact-manifest-v1", "artifact_sha256": sha256_file(artifact_path),
                         "feature_schema_sha256": artifact["feature_schema_sha256"], "model_config": config["model_config"],
                         "fit_member_count": DEVELOPMENT_MEMBERS, "fixed_test_access": False}
    write_json(package / "artifact" / "artifact_manifest.json", artifact_manifest)
    if aggregate_path is not None:
        for name in ("gpp_uncertainty.nc", "metric_distribution.csv", "uncertainty_estimates.csv", "repeated_split_manifest.json", "convergence.json", "uncertainty_report.json", "aggregate_validation.json"):
            shutil.copy2(aggregate_path / name, package / "uncertainty" / name)
    predictions_path = output / "release_predictions_physical_float32.dat"
    release_predictions = np.memmap(predictions_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    chunk = int(config["prediction_chunk_rows"])
    for start in range(0, total_rows, chunk):
        end = min(start + chunk, total_rows)
        prediction = model.predict(scaled_x[start:end]).astype(np.float64) * float(y_scaler.scale_[0]) + float(y_scaler.mean_[0])
        require(np.all(np.isfinite(prediction)), "release prediction invalid")
        release_predictions[start:end] = prediction.astype(np.float32)
    release_predictions.flush()
    handoff_path = package / "handoff" / "gpp_predicted_for_sr.nc"
    with Dataset(str(handoff_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-gpp-predicted-for-sr-handoff-v1"; dataset.artifact_sha256 = artifact_manifest["artifact_sha256"]
        dataset.snapshot_sha256 = config["snapshot_sha256"]; dataset.fit_scope = "all 819 development members; predictions are in-sample"
        dataset.createDimension("site", len(SITES)); dataset.createDimension("member", DEVELOPMENT_MEMBERS); dataset.createDimension("time", HOURS)
        dataset.createVariable("site", str, ("site",))[:] = np.asarray(SITES, dtype=object)
        dataset.createVariable("member_id", str, ("member",))[:] = np.asarray(raw_layout["development_member_ids"], dtype=object)
        dataset.createVariable("time", "i8", ("site", "time"))[:] = times
        prediction_var = dataset.createVariable("GPP_predicted", "f4", ("site", "member", "time"), zlib=True, complevel=4, chunksizes=(1, 1, min(HOURS, 8760)))
        prediction_var.units = "gC/m^2/day"; prediction_var.residual_convention = "not_applicable_release_prediction"
        cursor = 0
        for site_index in range(len(SITES)):
            for position in all_positions:
                prediction = np.asarray(release_predictions[cursor:cursor + HOURS], dtype=np.float32)
                prediction_var[site_index, position] = prediction; cursor += HOURS
        require(cursor == total_rows, "release handoff row mismatch")
    handoff_manifest = {"schema": "three-stage-gpp-predicted-for-sr-handoff-manifest-v1", "filename": handoff_path.name,
                        "sha256": sha256_file(handoff_path), "artifact_sha256": artifact_manifest["artifact_sha256"],
                        "snapshot_sha256": config["snapshot_sha256"], "site_order": list(SITES),
                        "development_member_ids": raw_layout["development_member_ids"], "variables": ["GPP_predicted"],
                        "contains_elm_truth": False, "contains_features_or_parameters": False, "fixed_test_access": False}
    write_json(package / "handoff" / "handoff_manifest.json", handoff_manifest)
    report = {"schema": "three-stage-gpp-iter006-release-fit-v1", "result": "pass",
              "artifact_sha256": artifact_manifest["artifact_sha256"], "handoff_sha256": handoff_manifest["sha256"],
              "predictions_sha256": sha256_file(predictions_path),
              "model_iterations": int(model.n_iter_), "convergence_warning_count": warning_count,
              "fit_member_count": DEVELOPMENT_MEMBERS, "fixed_test_access": False}
    write_json(package / "release_fit_report.json", report); write_json(output / "release_fit_report.json", report)
    return report


def load_release_artifact(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = json.loads((path / "artifact_manifest.json").read_text(encoding="utf-8"))
    artifact_path = path / "gpp_surrogate_artifact.pkl"
    require(sha256_file(artifact_path) == manifest["artifact_sha256"], "release artifact hash mismatch")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(artifact["schema"] == RELEASE_SCHEMA, "release artifact schema mismatch")
    return artifact, manifest


def validate_release(config: Mapping[str, Any], raw_path: Path, fit_package: Path, output: Path) -> dict[str, Any]:
    require(not output.exists(), f"release validation output exists: {output}")
    output.mkdir(parents=True); staging = output / "release_0001"; shutil.copytree(fit_package, staging)
    raw_layout, X, _, times = load_raw(raw_path)
    artifact, artifact_manifest = load_release_artifact(staging / "artifact")
    frozen_configuration = json.loads(Path(config["gpp_configuration_file"]).read_text(encoding="utf-8"))
    require(artifact["model_config"] == frozen_configuration["model_config"] == config["model_config"], "release model configuration mismatch")
    require(artifact["snapshot_sha256"] == config["snapshot_sha256"], "release artifact snapshot mismatch")
    require(artifact["upstream_release_manifest_sha256"] == config["spinup_release_manifest_sha256"], "release artifact upstream release mismatch")
    require(artifact["predicted_cn_sha256"] == config["predicted_cn_sha256"], "release artifact upstream handoff mismatch")
    require(artifact["feature_names"] == raw_layout["feature_names"], "release artifact feature names mismatch")
    require(artifact["feature_schema_sha256"] == raw_layout["feature_schema_sha256"] == artifact_manifest["feature_schema_sha256"], "release artifact feature schema mismatch")
    require(artifact["target_units"] == "gC/m^2/day", "release artifact target units mismatch")
    require(artifact["upstream_mode"] == "published_all819_in_sample" and artifact["validation_label"] == "fixed_upstream_gpp_stage", "release artifact interpretation mismatch")
    require(artifact["fit_scope"]["development_member_ids"] == raw_layout["development_member_ids"], "release fit scope mismatch")
    require(artifact["fit_scope"]["fixed_test_access"] is False, "release fixed-test mismatch")
    aggregate_validation = json.loads((staging / "uncertainty" / "aggregate_validation.json").read_text(encoding="utf-8"))
    require(aggregate_validation["result"] == "pass", "staged aggregate validation mismatch")
    expected_result = "pass" if bool(config.get("performance_gate_applied", True)) else "not_applicable"
    require(aggregate_validation["gate"]["result"] == expected_result, "staged performance assessment mismatch")
    uncertainty_report = json.loads((staging / "uncertainty" / "uncertainty_report.json").read_text(encoding="utf-8"))
    require(uncertainty_report["result"] == "pass" and uncertainty_report["gate"] == aggregate_validation["gate"], "staged uncertainty report mismatch")
    for item in aggregate_validation["files"]:
        candidate = staging / "uncertainty" / item["path"]
        require(candidate.is_file() and candidate.stat().st_size == int(item["size_bytes"]), f"staged uncertainty file missing: {item['path']}")
        require(sha256_file(candidate) == item["sha256"], f"staged uncertainty file hash mismatch: {item['path']}")
    staged_metrics = _read_metrics(staging / "uncertainty" / "metric_distribution.csv")
    release_gate = (
        evaluate_gate(staged_metrics)
        if bool(config.get("performance_gate_applied", True))
        else performance_assessment(staged_metrics)
    )
    require(release_gate == aggregate_validation["gate"], "release gate recomputation mismatch")
    handoff_path = staging / "handoff" / "gpp_predicted_for_sr.nc"
    with Dataset(str(handoff_path), "r") as handoff:
        require(handoff.getncattr("schema") == "three-stage-gpp-predicted-for-sr-handoff-v1", "handoff schema mismatch")
        require(handoff.getncattr("artifact_sha256") == artifact_manifest["artifact_sha256"], "handoff artifact attribute mismatch")
        require(handoff.getncattr("snapshot_sha256") == config["snapshot_sha256"], "handoff snapshot attribute mismatch")
        require(set(handoff.variables) == {"site", "member_id", "time", "GPP_predicted"}, "handoff variable scope mismatch")
        require(np.asarray(handoff.variables["site"][:], dtype=str).tolist() == list(SITES), "handoff site mismatch")
        require(np.asarray(handoff.variables["member_id"][:], dtype=str).tolist() == raw_layout["development_member_ids"], "handoff member mismatch")
        require(np.array_equal(handoff.variables["time"][:], times), "handoff time mismatch")
        require(str(handoff.variables["GPP_predicted"].units) == "gC/m^2/day", "handoff GPP units mismatch")
        all_observed = np.asarray(handoff.variables["GPP_predicted"][:], dtype=np.float32)
        require(all_observed.shape == (len(SITES), DEVELOPMENT_MEMBERS, HOURS), "handoff prediction shape mismatch")
        require(np.all(np.isfinite(all_observed)), "handoff full prediction coverage invalid")
        flat_raw = X.reshape(-1, FEATURE_COUNT)
        flat_observed = all_observed.reshape(-1)
        chunk = int(config["prediction_chunk_rows"])
        for chunk_index in (0, (flat_raw.shape[0] // chunk) // 2, (flat_raw.shape[0] - 1) // chunk):
            start = chunk_index * chunk; end = min(start + chunk, flat_raw.shape[0])
            expected = predict_artifact(artifact, np.asarray(flat_raw[start:end], dtype=np.float64))
            observed = np.asarray(flat_observed[start:end], dtype=np.float64)
            require(np.all(np.isfinite(observed)), "handoff nonfinite prediction")
            require(np.allclose(observed, expected, rtol=config["reload_rtol"], atol=config["reload_atol"]), "handoff prediction mismatch")
        for size in (1, 7, 1000):
            sample = np.asarray(X[0, 0, :size], dtype=np.float64)
            require(np.array_equal(predict_artifact(artifact, sample), predict_artifact(artifact, sample)), "release same-batch repeatability mismatch")
    handoff_manifest = json.loads((staging / "handoff" / "handoff_manifest.json").read_text(encoding="utf-8"))
    require(handoff_manifest["sha256"] == sha256_file(handoff_path), "handoff manifest hash mismatch")
    require(handoff_manifest["contains_elm_truth"] is False and handoff_manifest["contains_features_or_parameters"] is False, "handoff contents mismatch")
    validation_report = {"schema": "three-stage-gpp-iter006-release-validation-v1", "result": "pass",
                         "snapshot_sha256": config["snapshot_sha256"], "artifact_sha256": artifact_manifest["artifact_sha256"],
                         "handoff_sha256": handoff_manifest["sha256"], "fit_member_count": DEVELOPMENT_MEMBERS,
                         "fixed_test_access": False, "gate": release_gate,
                         "release_basis": config.get("release_basis", "performance_gate"),
                         "performance_gate_applied": bool(config.get("performance_gate_applied", True)),
                         "handoff_prediction_count": int(all_observed.size), "handoff_full_finite": True}
    write_json(output / "validation_report.json", validation_report); write_json(staging / "validation" / "validation_report.json", validation_report)
    release_manifest = {"schema": "three-stage-gpp-release-package-manifest-v1", "release": "release_0001",
                        "created_utc": datetime.now(timezone.utc).isoformat(), "result": "validated",
                        "snapshot_sha256": config["snapshot_sha256"], "artifact_sha256": artifact_manifest["artifact_sha256"],
                        "handoff_sha256": handoff_manifest["sha256"], "split_manifest_sha256": config["repeated_split_manifest_sha256"],
                        "fixed_test_access": False,
                        "release_basis": config.get("release_basis", "performance_gate"),
                        "performance_gate_applied": bool(config.get("performance_gate_applied", True)),
                        "files": package_files(staging, exclude={"release_manifest.json"})}
    write_json(staging / "release_manifest.json", release_manifest)
    return validation_report
