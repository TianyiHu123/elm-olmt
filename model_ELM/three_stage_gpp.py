"""Fixed-upstream ABBY/JERC GPP preparation, fitting, and inference."""
from __future__ import annotations

import csv
import json
import pickle
import warnings
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np
from netCDF4 import Dataset
from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler

from .three_stage_data import SITES, ThreeStageSnapshot, require, schema_sha256, sha256_file

FORCING_NAMES: Tuple[str, ...] = ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")
FORCING_FEATURE_NAMES: Tuple[str, ...] = (
    *FORCING_NAMES,
    "sin_hour", "cos_hour", "sin_doy", "cos_doy",
    "TBOT_mean_24h", "TBOT_mean_168h", "TBOT_mean_720h",
    "PRECTmms_sum_24h", "PRECTmms_sum_168h", "PRECTmms_sum_720h",
    "PRECTmms_anom_30d", "FSDS_anom_30d", "TBOT_anom_30d",
)
SURFACE_NAMES: Tuple[str, ...] = ("PCT_SAND", "PCT_CLAY", "ORGANIC")
UPSTREAM_NAMES: Tuple[str, ...] = ("TOTSOMC_predicted", "TOTSOMN_predicted")
HOURS = 61320
TRAIN_MEMBERS = 655
VALIDATION_MEMBERS = 164
FEATURE_COUNT = 43
QUANTILES: Tuple[float, ...] = (0.01, 0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975, 0.99)
MODEL_CONFIG: Dict[str, Any] = {
    "hidden_layer_sizes": [128], "activation": "relu", "solver": "adam", "alpha": 1.0e-4,
    "learning_rate": "adaptive", "learning_rate_init": 1.0e-3, "max_iter": 500,
    "early_stopping": True, "validation_fraction": 0.1, "n_iter_no_change": 10,
    "tol": 1.0e-4, "batch_size": "auto", "shuffle": True, "random_state": 42,
}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rolling(values: np.ndarray, window: int, *, total: bool) -> np.ndarray:
    source = np.asarray(values, dtype=np.float64).reshape(-1)
    csum = np.cumsum(np.insert(source, 0, 0.0))
    index = np.arange(source.size)
    start = np.maximum(0, index - window + 1)
    result = csum[index + 1] - csum[start]
    if not total:
        result = result / (index - start + 1)
    return result


def engineer_forcing(raw: Mapping[str, np.ndarray], time: np.ndarray) -> np.ndarray:
    """Build the locked 20-column timestamp-aware forcing matrix."""
    axis = np.asarray(time, dtype=np.int64).reshape(-1)
    require(axis.shape == (HOURS,) or axis.size < HOURS, "forcing time length invalid")
    require(np.array_equal(axis, np.arange(axis.size)), "forcing time must be consecutive no-leap hours")
    columns = []
    for name in FORCING_NAMES:
        require(name in raw, f"missing forcing {name}")
        values = np.asarray(raw[name], dtype=np.float64).reshape(-1)
        require(values.shape == axis.shape and np.all(np.isfinite(values)), f"forcing {name} invalid")
        columns.append(values)
    hour = axis % 24
    day = (axis // 24) % 365
    columns.extend((
        np.sin(2.0 * np.pi * hour / 24.0), np.cos(2.0 * np.pi * hour / 24.0),
        np.sin(2.0 * np.pi * day / 365.0), np.cos(2.0 * np.pi * day / 365.0),
    ))
    tbot = np.asarray(raw["TBOT"], dtype=np.float64)
    precip = np.asarray(raw["PRECTmms"], dtype=np.float64)
    for window in (24, 168, 720):
        columns.append(_rolling(tbot, window, total=False))
    for window in (24, 168, 720):
        columns.append(_rolling(precip, window, total=True))
    for name in ("PRECTmms", "FSDS", "TBOT"):
        values = np.asarray(raw[name], dtype=np.float64)
        columns.append(values - _rolling(values, 720, total=False))
    result = np.column_stack(columns)
    require(result.shape == (axis.size, len(FORCING_FEATURE_NAMES)), "forcing feature shape mismatch")
    require(np.all(np.isfinite(result)), "forcing features contain nonfinite values")
    return result


def engineer_forcing_window(
    raw_with_history: Mapping[str, np.ndarray], time_with_history: np.ndarray, start: int, end: int
) -> np.ndarray:
    """Engineer an arbitrary window when the caller supplies ordered history from hour zero."""
    axis = np.asarray(time_with_history, dtype=np.int64).reshape(-1)
    require(0 <= start < end <= axis.size, "forcing window bounds invalid")
    require(start == 0 or start >= 720, "nonzero forcing windows require at least 720 history hours")
    return engineer_forcing(raw_with_history, axis)[start:end]


def feature_names(snapshot: ThreeStageSnapshot) -> Tuple[str, ...]:
    names = (*FORCING_FEATURE_NAMES, *snapshot.parameter_names, *SURFACE_NAMES, *UPSTREAM_NAMES)
    require(len(names) == FEATURE_COUNT and len(set(names)) == FEATURE_COUNT, "GPP feature schema mismatch")
    return tuple(names)


def _handoff(path: Path, snapshot: ThreeStageSnapshot) -> Dict[str, np.ndarray]:
    with Dataset(str(path), "r") as dataset:
        require(dataset.getncattr("schema") == "three-stage-spinup-predicted-cn-handoff-v1", "handoff schema mismatch")
        require(np.asarray(dataset.variables["site"][:], dtype=str).tolist() == list(SITES), "handoff site order mismatch")
        require(np.asarray(dataset.variables["member_id"][:], dtype=str).tolist() == list(snapshot.development_ranked), "handoff member order mismatch")
        result = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in UPSTREAM_NAMES}
    for name, values in result.items():
        require(values.shape == (len(SITES), 819), f"{name} handoff shape mismatch")
        require(np.all(np.isfinite(values)) and np.all(values > 0.0), f"{name} handoff invalid")
    return result


def _site_static(dataset: Dataset) -> np.ndarray:
    values = np.asarray([float(np.asarray(dataset.variables[name][:])) for name in SURFACE_NAMES])
    require(np.all(np.isfinite(values)), "surface features invalid")
    return values


def _scale_in_place(path: Path, shape: Tuple[int, ...], scaler: StandardScaler, chunk_rows: int) -> None:
    values = np.memmap(path, mode="r+", dtype=np.float32, shape=shape)
    for start in range(0, shape[0], chunk_rows):
        end = min(start + chunk_rows, shape[0])
        values[start:end] = scaler.transform(values[start:end]).astype(np.float32)
    values.flush()


def prepare_contract(config: Mapping[str, Any], output: Path) -> Dict[str, Any]:
    """Materialize and scale the locked 819-member design in partition-major order."""
    require(not output.exists(), f"preparation output already exists: {output}")
    output.mkdir(parents=True)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    train, validation = snapshot.operational_split()
    require(list(train) == list(snapshot.development_ranked[:TRAIN_MEMBERS]), "training split mismatch")
    require(list(validation) == list(snapshot.development_ranked[TRAIN_MEMBERS:]), "validation split mismatch")
    handoff_path = Path(config["predicted_cn_handoff"])
    require(sha256_file(handoff_path) == config["predicted_cn_sha256"], "predicted-C/N hash mismatch")
    upstream = _handoff(handoff_path, snapshot)
    names = feature_names(snapshot)
    total_rows = len(SITES) * 819 * HOURS
    train_rows = len(SITES) * TRAIN_MEMBERS * HOURS
    require(total_rows == 100442160 and train_rows == 80329200, "row-count contract mismatch")
    x_path = output / "X_scaled_float32.dat"
    y_path = output / "y_scaled_float32.dat"
    X = np.memmap(x_path, mode="w+", dtype=np.float32, shape=(total_rows, FEATURE_COUNT))
    y = np.memmap(y_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    params = snapshot._parameter_values(snapshot.development_ranked)
    member_position = {member: index for index, member in enumerate(snapshot.development_ranked)}
    offsets: list[dict[str, Any]] = []
    row = 0
    with ExitStack() as stack:
        datasets = {
            site: stack.enter_context(Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r"))
            for site in SITES
        }
        forcing: Dict[str, np.ndarray] = {}
        surfaces: Dict[str, np.ndarray] = {}
        for site, dataset in datasets.items():
            time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
            require(time.shape == (HOURS,), f"{site} time shape mismatch")
            raw = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in FORCING_NAMES}
            forcing[site] = engineer_forcing(raw, time).astype(np.float32)
            surfaces[site] = _site_static(dataset)
            require(str(dataset.variables["GPP"].units) == "gC/m^2/day", f"{site} GPP units mismatch")
        for partition, members in (("train", train), ("validation", validation)):
            for site_index, site in enumerate(SITES):
                dataset = datasets[site]
                block_start = row
                for member in members:
                    position = member_position[member]
                    source_index = int(member[1:]) - 1
                    static = np.concatenate((params[position], surfaces[site], [upstream[name][site_index, position] for name in UPSTREAM_NAMES]))
                    require(static.shape == (23,) and np.all(np.isfinite(static)), "static feature block invalid")
                    end = row + HOURS
                    X[row:end, :len(FORCING_FEATURE_NAMES)] = forcing[site]
                    X[row:end, len(FORCING_FEATURE_NAMES):] = static.astype(np.float32)
                    target = np.asarray(dataset.variables["GPP"][source_index, :], dtype=np.float32)
                    require(target.shape == (HOURS,) and np.all(np.isfinite(target)), f"{site} GPP target invalid")
                    y[row:end] = target
                    row = end
                offsets.append({"partition": partition, "site": site, "start": block_start, "end": row, "members": list(members)})
    require(row == total_rows, "materialized row count mismatch")
    X.flush(); y.flush()
    chunk = int(config["scale_chunk_rows"])
    x_scaler = StandardScaler(copy=True)
    y_scaler = StandardScaler(copy=True)
    for start in range(0, train_rows, chunk):
        end = min(start + chunk, train_rows)
        x_scaler.partial_fit(X[start:end])
        y_scaler.partial_fit(np.asarray(y[start:end]).reshape(-1, 1))
    del X, y
    _scale_in_place(x_path, (total_rows, FEATURE_COUNT), x_scaler, chunk)
    _scale_in_place(y_path, (total_rows, 1), y_scaler, chunk)
    scaler_path = output / "scalers.npz"
    np.savez(
        scaler_path, x_mean=x_scaler.mean_, x_scale=x_scaler.scale_, y_mean=y_scaler.mean_,
        y_scale=y_scaler.scale_, feature_names=np.asarray(names, dtype="U64"),
    )
    layout = {
        "schema": "three-stage-gpp-iter005-prepared-v1", "feature_names": list(names),
        "feature_schema_sha256": schema_sha256(names), "dtype": "float32", "rows": total_rows,
        "features": FEATURE_COUNT, "hours_per_member": HOURS, "train_rows": train_rows,
        "validation_rows": total_rows - train_rows, "train_members": list(train),
        "validation_members": list(validation), "sites": list(SITES), "offsets": offsets,
        "fixed_test_access": False, "spinup_execution": False,
        "upstream_mode": "published_all819_in_sample", "validation_label": "fixed_upstream_gpp_stage",
        "x_file": x_path.name, "y_file": y_path.name, "scaler_file": scaler_path.name,
    }
    write_json(output / "layout.json", layout)
    manifest = {
        "schema": "three-stage-gpp-iter005-prepared-manifest-v1", "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"], "predicted_cn_sha256": config["predicted_cn_sha256"],
        "layout_sha256": sha256_file(output / "layout.json"), "x_sha256": sha256_file(x_path),
        "y_sha256": sha256_file(y_path), "scalers_sha256": sha256_file(scaler_path),
        "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "prepared_manifest.json", manifest)
    return manifest


def load_prepared(path: Path) -> Tuple[dict[str, Any], np.memmap, np.memmap, dict[str, np.ndarray]]:
    layout = json.loads((path / "layout.json").read_text(encoding="utf-8"))
    require(layout["schema"] == "three-stage-gpp-iter005-prepared-v1", "prepared schema mismatch")
    X = np.memmap(path / layout["x_file"], mode="r", dtype=np.float32, shape=(layout["rows"], layout["features"]))
    y = np.memmap(path / layout["y_file"], mode="r", dtype=np.float32, shape=(layout["rows"],))
    with np.load(path / layout["scaler_file"], allow_pickle=False) as data:
        scalers = {name: np.asarray(data[name]) for name in ("x_mean", "x_scale", "y_mean", "y_scale", "feature_names")}
    return layout, X, y, scalers


def validate_prepared(config: Mapping[str, Any], path: Path, *, full_hashes: bool = True) -> Dict[str, Any]:
    manifest = json.loads((path / "prepared_manifest.json").read_text(encoding="utf-8"))
    layout, X, y, scalers = load_prepared(path)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    expected_train, expected_validation = snapshot.operational_split()
    expected_names = feature_names(snapshot)
    require(manifest["schema"] == "three-stage-gpp-iter005-prepared-manifest-v1", "prepared manifest schema mismatch")
    require(manifest["snapshot_sha256"] == config["snapshot_sha256"], "prepared snapshot identity mismatch")
    require(manifest["global_split_sha256"] == config["global_split_sha256"], "prepared split identity mismatch")
    require(manifest["predicted_cn_sha256"] == config["predicted_cn_sha256"], "prepared handoff identity mismatch")
    require(sha256_file(path / "layout.json") == manifest["layout_sha256"], "prepared layout hash mismatch")
    require(layout["rows"] == 100442160 and layout["features"] == FEATURE_COUNT, "prepared dimensions mismatch")
    require(layout["train_rows"] == 80329200 and layout["validation_rows"] == 20112960, "prepared partition mismatch")
    require(layout["fixed_test_access"] is False and layout["spinup_execution"] is False, "prepared boundary mismatch")
    require(layout["train_members"] == list(expected_train), "prepared exact training split mismatch")
    require(layout["validation_members"] == list(expected_validation), "prepared exact validation split mismatch")
    require(set(layout["train_members"]).isdisjoint(layout["validation_members"]), "prepared split overlap")
    require(layout["feature_names"] == list(expected_names), "prepared feature names mismatch")
    require(layout["feature_schema_sha256"] == schema_sha256(expected_names), "prepared feature schema mismatch")
    require(np.asarray(scalers["feature_names"], dtype=str).tolist() == list(expected_names), "scaler feature names mismatch")
    expected_offsets = []
    cursor = 0
    for partition, members in (("train", expected_train), ("validation", expected_validation)):
        for site in SITES:
            end = cursor + len(members) * HOURS
            expected_offsets.append({"partition": partition, "site": site, "start": cursor, "end": end, "members": list(members)})
            cursor = end
    require(layout["offsets"] == expected_offsets and cursor == layout["rows"], "prepared offset/coverage mismatch")
    require(np.all(np.isfinite(scalers["x_mean"])) and np.all(scalers["x_scale"] > 0.0), "X scalers invalid")
    require(np.all(np.isfinite(scalers["y_mean"])) and np.all(scalers["y_scale"] > 0.0), "y scalers invalid")
    sample = np.asarray([0, HOURS - 1, layout["train_rows"] - 1, layout["train_rows"], layout["rows"] - 1], dtype=np.int64)
    require(np.all(np.isfinite(X[sample])) and np.all(np.isfinite(y[sample])), "prepared samples invalid")
    if full_hashes:
        require(sha256_file(path / layout["x_file"]) == manifest["x_sha256"], "prepared X hash mismatch")
        require(sha256_file(path / layout["y_file"]) == manifest["y_sha256"], "prepared y hash mismatch")
        require(sha256_file(path / layout["scaler_file"]) == manifest["scalers_sha256"], "prepared scaler hash mismatch")
    return {"schema": "three-stage-gpp-iter005-prepared-validation-v1", "result": "pass", "rows": layout["rows"], "features": layout["features"], "sample_rows": sample.tolist(), "full_hashes": full_hashes}


def _model(config: Mapping[str, Any], *, smoke: bool = False) -> MLPRegressor:
    model_config = dict(config["model_config"])
    model_config["hidden_layer_sizes"] = tuple(model_config["hidden_layer_sizes"])
    if smoke:
        model_config.update({"max_iter": 2, "early_stopping": False})
    return MLPRegressor(**model_config)


def smoke_fit(config: Mapping[str, Any], prepared: Path, output: Path) -> Dict[str, Any]:
    require(not output.exists(), f"smoke output exists: {output}")
    output.mkdir(parents=True)
    layout, X, y, _ = load_prepared(prepared)
    train_indices = []
    validation_indices = []
    for item in layout["offsets"]:
        count = 80 if item["partition"] == "train" else 20
        destination = train_indices if item["partition"] == "train" else validation_indices
        start = int(item["start"])
        for member in range(count):
            begin = start + member * HOURS
            destination.extend(range(begin, begin + 1440))
    train_selected = np.asarray(train_indices, dtype=np.int64)
    validation_selected = np.asarray(validation_indices, dtype=np.int64)
    model = _model(config, smoke=True)
    model.fit(X[train_selected], y[train_selected])
    train_prediction = model.predict(X[train_selected[:1000]])
    validation_prediction = model.predict(X[validation_selected])
    require(np.all(np.isfinite(train_prediction)) and np.all(np.isfinite(validation_prediction)), "smoke prediction invalid")
    report = {
        "schema": "three-stage-gpp-iter005-smoke-v1", "result": "pass",
        "train_rows": int(train_selected.size), "validation_rows": int(validation_selected.size),
        "train_members_per_site": 80, "validation_members_per_site": 20,
        "iterations": int(model.n_iter_), "fixed_test_access": False, "spinup_execution": False,
    }
    write_json(output / "smoke_report.json", report)
    return report


def _metrics(truth: np.ndarray, prediction: np.ndarray) -> Dict[str, float | int]:
    t = np.asarray(truth, dtype=np.float64).reshape(-1)
    p = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(t.size == p.size and t.size > 1, "metric inputs invalid")
    require(np.all(np.isfinite(t)) and np.all(np.isfinite(p)), "metric inputs nonfinite")
    residual = p - t
    centered = t - np.mean(t)
    denom = float(np.sum(centered * centered))
    result: Dict[str, float | int] = {
        "count": int(t.size), "r2": float(1.0 - np.sum(residual * residual) / denom),
        "rmse": float(np.sqrt(np.mean(residual * residual))), "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)), "residual_std": float(np.std(residual, ddof=0)),
        "gap_count": 0, "coverage_fraction": 1.0,
    }
    for quantile, value in zip(QUANTILES, np.quantile(residual, QUANTILES)):
        result[f"q{str(quantile).replace('.', '_')}"] = float(value)
    return result


def _offset(layout: Mapping[str, Any], partition: str, site: str) -> Tuple[int, int, int]:
    matches = [item for item in layout["offsets"] if item["partition"] == partition and item["site"] == site]
    require(len(matches) == 1, "offset lookup mismatch")
    item = matches[0]
    return int(item["start"]), int(item["end"]), len(item["members"])


def fit_baseline(config: Mapping[str, Any], prepared: Path, output: Path) -> Dict[str, Any]:
    require(not output.exists(), f"baseline output exists: {output}")
    output.mkdir(parents=True)
    layout, X, y, scalers = load_prepared(prepared)
    train_rows = int(layout["train_rows"])
    model = _model(config)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(X[:train_rows], y[:train_rows])
    convergence_warnings = sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    predictions_path = output / "predictions_physical_float32.dat"
    predictions = np.memmap(predictions_path, mode="w+", dtype=np.float32, shape=(layout["rows"],))
    chunk = int(config["prediction_chunk_rows"])
    y_mean = float(scalers["y_mean"][0]); y_scale = float(scalers["y_scale"][0])
    for start in range(0, layout["rows"], chunk):
        end = min(start + chunk, layout["rows"])
        pred = model.predict(X[start:end]).astype(np.float64) * y_scale + y_mean
        require(np.all(np.isfinite(pred)), "baseline prediction invalid")
        predictions[start:end] = pred.astype(np.float32)
    predictions.flush()
    metric_rows: list[dict[str, Any]] = []
    for partition in ("train", "validation"):
        pooled_truth = []
        pooled_prediction = []
        pooled_daily_truth = []
        pooled_daily_prediction = []
        for site in SITES:
            start, end, member_count = _offset(layout, partition, site)
            truth = np.asarray(y[start:end], dtype=np.float64) * y_scale + y_mean
            pred = np.asarray(predictions[start:end], dtype=np.float64)
            metric_rows.append({"partition": partition, "site": site, "resolution": "hourly", **_metrics(truth, pred)})
            truth_daily = truth.reshape(member_count, HOURS // 24, 24).mean(axis=2).reshape(-1)
            pred_daily = pred.reshape(member_count, HOURS // 24, 24).mean(axis=2).reshape(-1)
            metric_rows.append({"partition": partition, "site": site, "resolution": "daily", **_metrics(truth_daily, pred_daily)})
            pooled_truth.append(truth); pooled_prediction.append(pred)
            pooled_daily_truth.append(truth_daily); pooled_daily_prediction.append(pred_daily)
        metric_rows.append({"partition": partition, "site": "pooled", "resolution": "hourly", **_metrics(np.concatenate(pooled_truth), np.concatenate(pooled_prediction))})
        metric_rows.append({"partition": partition, "site": "pooled", "resolution": "daily", **_metrics(np.concatenate(pooled_daily_truth), np.concatenate(pooled_daily_prediction))})
    metric_path = output / "metrics.csv"
    with metric_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]))
        writer.writeheader(); writer.writerows(metric_rows)
    artifact = {
        "schema": "three-stage-gpp-iter005-artifact-v1", "model": model,
        "x_mean": scalers["x_mean"], "x_scale": scalers["x_scale"],
        "y_mean": y_mean, "y_scale": y_scale, "feature_names": layout["feature_names"],
        "feature_schema_sha256": layout["feature_schema_sha256"], "model_config": config["model_config"],
        "fit_scope": {"train_member_ids": layout["train_members"], "validation_member_ids": layout["validation_members"], "fixed_test_access": False},
        "upstream_mode": layout["upstream_mode"], "validation_label": layout["validation_label"],
    }
    artifact_path = output / "gpp_baseline_artifact.pkl"
    with artifact_path.open("wb") as handle:
        pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
    report = {
        "schema": "three-stage-gpp-iter005-baseline-v1", "result": "pass",
        "artifact_sha256": sha256_file(artifact_path), "predictions_sha256": sha256_file(predictions_path),
        "metrics_sha256": sha256_file(metric_path), "model_iterations": int(model.n_iter_),
        "convergence_warnings": int(convergence_warnings),
        "rows": layout["rows"], "train_rows": train_rows, "validation_rows": layout["validation_rows"],
        "fixed_test_access": False, "spinup_execution": False, "validation_label": "fixed_upstream_gpp_stage",
    }
    write_json(output / "baseline_report.json", report)
    return report


def load_artifact(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(artifact.get("schema") == "three-stage-gpp-iter005-artifact-v1", "GPP artifact schema mismatch")
    return artifact


def predict_artifact(artifact: Mapping[str, Any], raw_features: np.ndarray) -> np.ndarray:
    values = np.asarray(raw_features, dtype=np.float64)
    require(values.ndim == 2 and values.shape[1] == len(artifact["feature_names"]), "inference feature shape mismatch")
    require(np.all(np.isfinite(values)), "inference features nonfinite")
    # StandardScaler transformed the prepared float32 design in place after casting its fitted
    # statistics to the design dtype. Reproduce that dtype and rounding order exactly.
    scaled = values.astype(np.float32, copy=True)
    scaled -= np.asarray(artifact["x_mean"], dtype=scaled.dtype)
    scaled /= np.asarray(artifact["x_scale"], dtype=scaled.dtype)
    prediction = artifact["model"].predict(scaled) * float(artifact["y_scale"]) + float(artifact["y_mean"])
    require(np.all(np.isfinite(prediction)), "inference prediction nonfinite")
    return np.asarray(prediction, dtype=np.float64)

