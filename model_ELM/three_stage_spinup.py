"""Training, evaluation, and output helpers for the staged spinup baseline."""
from __future__ import annotations

import csv
import json
import math
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from .three_stage_data import SITES, TARGETS, LoadedRows, ThreeStageSnapshot, require, schema_sha256
from .three_stage_spinup_artifact import predict_matrix, save_artifact


MODEL_CONFIG = {
    "hidden_layer_sizes": [32],
    "activation": "tanh",
    "solver": "lbfgs",
    "alpha": 40.0,
    "max_iter": 800,
    "random_state": 42,
}
METRIC_FIELDS = ("n", "r2", "rmse", "mae", "bias", "residual_std")
GAP_METRIC_FIELDS = ("r2", "rmse", "mae", "bias", "residual_std")


def normalize_mlp_config(config: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the explicit MLP configuration supplied by a driver."""
    layers = tuple(int(value) for value in config.get("hidden_layer_sizes", ()))
    require(bool(layers) and len(layers) <= 2, "hidden layers must contain one or two sizes")
    require(all(value in {8, 16, 32, 64, 128} for value in layers), "unsupported hidden layer size")
    activation = str(config.get("activation", ""))
    require(activation in {"tanh", "relu"}, "unsupported activation")
    solver = str(config.get("solver", ""))
    require(solver == "lbfgs", "unsupported solver")
    alpha = float(config.get("alpha", float("nan")))
    require(math.isfinite(alpha) and alpha >= 0.0, "alpha must be finite and nonnegative")
    max_iter = int(config.get("max_iter", 0))
    require(max_iter == 800, "max_iter must be 800")
    random_state = int(config.get("random_state", -1))
    require(random_state == 42, "random_state must be 42")
    return {
        "hidden_layer_sizes": list(layers),
        "activation": activation,
        "solver": solver,
        "alpha": alpha,
        "max_iter": max_iter,
        "random_state": random_state,
    }


def fit_compact_models(train: LoadedRows, model_config: Mapping[str, Any]) -> Dict[str, Any]:
    """Fit the two locked targets without producing a persistent artifact."""
    require(train.y is not None, "training targets missing")
    normalized = normalize_mlp_config(model_config)
    models: Dict[str, Any] = {}
    x_scalers: Dict[str, StandardScaler] = {}
    y_scalers: Dict[str, StandardScaler] = {}
    convergence: Dict[str, Any] = {}
    for target_index, target in enumerate(TARGETS):
        x_scaler = StandardScaler().fit(train.X)
        log_target = np.log(train.y[:, target_index]).reshape(-1, 1)
        y_scaler = StandardScaler().fit(log_target)
        model = MLPRegressor(
            hidden_layer_sizes=tuple(normalized["hidden_layer_sizes"]),
            activation=normalized["activation"],
            solver=normalized["solver"],
            alpha=normalized["alpha"],
            max_iter=normalized["max_iter"],
            random_state=normalized["random_state"],
        )
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            model.fit(x_scaler.transform(train.X), y_scaler.transform(log_target).ravel())
        convergence[target] = {
            "n_iter": int(getattr(model, "n_iter_", -1)),
            "loss": float(getattr(model, "loss_", float("nan"))),
            "warnings": [
                {"category": item.category.__name__, "message": str(item.message)} for item in captured
            ],
            "has_convergence_warning": any(
                issubclass(item.category, ConvergenceWarning) for item in captured
            ),
        }
        models[target] = model
        x_scalers[target] = x_scaler
        y_scalers[target] = y_scaler
    return {
        "model_config": normalized,
        "models": models,
        "x_scalers": x_scalers,
        "y_scalers": y_scalers,
        "convergence": convergence,
    }


def predict_compact_models(fitted: Mapping[str, Any], X: np.ndarray) -> np.ndarray:
    """Predict positive physical C/N values from an in-memory compact fit."""
    matrix = np.asarray(X, dtype=np.float64)
    require(matrix.ndim == 2 and matrix.shape[1] == 25, "prediction matrix shape mismatch")
    require(np.all(np.isfinite(matrix)), "prediction matrix contains nonfinite values")
    outputs = []
    for target in TARGETS:
        scaled = fitted["x_scalers"][target].transform(matrix)
        scaled_prediction = fitted["models"][target].predict(scaled)
        log_prediction = fitted["y_scalers"][target].inverse_transform(
            np.asarray(scaled_prediction, dtype=np.float64).reshape(-1, 1)
        ).ravel()
        require(np.all(np.isfinite(log_prediction)), f"{target} log prediction contains nonfinite values")
        prediction = np.exp(log_prediction)
        require(np.all(np.isfinite(prediction)) and np.all(prediction > 0.0), f"{target} prediction invalid")
        outputs.append(prediction)
    return np.column_stack(outputs)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        result = float(value)
        return result if math.isfinite(result) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if value is None or isinstance(value, str):
        return value
    return str(value)


def regression_metrics(truth: np.ndarray, prediction: np.ndarray) -> Dict[str, float | int]:
    observed = np.asarray(truth, dtype=np.float64).ravel()
    predicted = np.asarray(prediction, dtype=np.float64).ravel()
    require(observed.size == predicted.size and observed.size >= 2, "metric arrays must match and contain at least two rows")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(predicted)), "metric arrays contain nonfinite values")
    residual = predicted - observed
    return {
        "n": int(observed.size),
        "r2": float(r2_score(observed, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(observed, predicted))),
        "mae": float(mean_absolute_error(observed, predicted)),
        "bias": float(np.mean(residual)),
        "residual_std": float(np.std(residual, ddof=0)),
    }


def metric_rows(
    run_kind: str,
    train: LoadedRows,
    train_prediction: np.ndarray,
    validation: LoadedRows,
    validation_prediction: np.ndarray,
) -> List[Dict[str, Any]]:
    require(train.y is not None and validation.y is not None, "metric rows require targets")
    rows: List[Dict[str, Any]] = []
    for partition, loaded, prediction in (
        ("training", train, train_prediction),
        ("validation", validation, validation_prediction),
    ):
        for site in ("pooled", *SITES):
            mask = np.ones(loaded.site.shape, dtype=bool) if site == "pooled" else loaded.site == site
            for target_index, target in enumerate(TARGETS):
                truth_values = loaded.y[mask, target_index]
                predicted_values = prediction[mask, target_index]
                for scale in ("physical", "log"):
                    if scale == "log":
                        require(np.all(truth_values > 0.0) and np.all(predicted_values > 0.0), "log metrics require positive values")
                        metric_truth = np.log(truth_values)
                        metric_prediction = np.log(predicted_values)
                    else:
                        metric_truth = truth_values
                        metric_prediction = predicted_values
                    row: Dict[str, Any] = {
                        "run_kind": run_kind,
                        "partition": partition,
                        "site": site,
                        "target": target,
                        "scale": scale,
                    }
                    row.update(regression_metrics(metric_truth, metric_prediction))
                    rows.append(row)
    return rows


def metric_gap_rows(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Return validation-minus-training gaps for every reporting stratum."""
    gaps: List[Dict[str, Any]] = []
    for site in ("pooled", *SITES):
        for target in TARGETS:
            for scale in ("physical", "log"):
                selected = {
                    str(row["partition"]): row
                    for row in rows
                    if row["site"] == site and row["target"] == target and row["scale"] == scale
                }
                require(set(selected) == {"training", "validation"}, "metric-gap partition mismatch")
                training = selected["training"]
                validation = selected["validation"]
                record: Dict[str, Any] = {
                    "site": site,
                    "target": target,
                    "scale": scale,
                    "definition": "validation minus training",
                    "training_n": int(training["n"]),
                    "validation_n": int(validation["n"]),
                }
                for field in GAP_METRIC_FIELDS:
                    record[f"{field}_gap"] = float(validation[field]) - float(training[field])
                gaps.append(record)
    return gaps


def _metric_lookup(rows: Sequence[Mapping[str, Any]], target: str, scale: str, partition: str) -> Mapping[str, Any]:
    matches = [
        row
        for row in rows
        if row["target"] == target
        and row["scale"] == scale
        and row["partition"] == partition
        and row["site"] == "pooled"
    ]
    require(len(matches) == 1, "pooled metric lookup mismatch")
    return matches[0]


def save_scatter_plots(
    directory: Path,
    train: LoadedRows,
    train_prediction: np.ndarray,
    validation: LoadedRows,
    validation_prediction: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
) -> List[Path]:
    require(train.y is not None and validation.y is not None, "scatter plots require targets")
    directory.mkdir(parents=True, exist_ok=False)
    colors = {"ABBY": "#1f77b4", "JERC": "#d62728"}
    outputs: List[Path] = []
    for target_index, target in enumerate(TARGETS):
        for scale in ("physical", "log"):
            figure, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
            for axis, partition, loaded, prediction in (
                (axes[0], "training", train, train_prediction),
                (axes[1], "validation", validation, validation_prediction),
            ):
                all_truth = loaded.y[:, target_index]
                all_prediction = prediction[:, target_index]
                if scale == "log":
                    all_truth = np.log(all_truth)
                    all_prediction = np.log(all_prediction)
                for site in SITES:
                    mask = loaded.site == site
                    axis.scatter(
                        all_truth[mask],
                        all_prediction[mask],
                        s=18,
                        alpha=0.7,
                        color=colors[site],
                        label=site,
                        edgecolors="none",
                    )
                lower = float(min(np.min(all_truth), np.min(all_prediction)))
                upper = float(max(np.max(all_truth), np.max(all_prediction)))
                axis.plot([lower, upper], [lower, upper], color="black", linewidth=1.0, linestyle="--")
                metric = _metric_lookup(rows, target, scale, partition)
                axis.set_title(
                    f"{partition.capitalize()}\nR2={metric['r2']:.3f} RMSE={metric['rmse']:.3g}"
                )
                unit = "ln(stock)" if scale == "log" else ("gC m-2" if target == "TOTSOMC" else "gN m-2")
                axis.set_xlabel(f"ELM {target} ({unit})")
                axis.set_ylabel(f"Predicted {target} ({unit})")
                axis.legend(frameon=False)
            output = directory / f"{target}_{scale}_scatter.png"
            figure.savefig(output, dpi=180)
            plt.close(figure)
            outputs.append(output)
    return outputs


def permutation_importance_rmse(
    artifact: Mapping[str, Any], validation: LoadedRows, *, repeats: int = 8
) -> Dict[str, Any]:
    require(validation.y is not None, "permutation importance requires targets")
    result: Dict[str, Any] = {"repeats": int(repeats), "random_state": 42, "by_target": {}}
    for target_index, target in enumerate(TARGETS):
        x_scaler = artifact["x_scalers"][target]
        y_scaler = artifact["y_scalers"][target]
        model = artifact["models"][target]
        scaled = x_scaler.transform(validation.X)
        base_scaled = model.predict(scaled)
        base_log_prediction = y_scaler.inverse_transform(np.asarray(base_scaled).reshape(-1, 1)).ravel()
        base_prediction = np.exp(base_log_prediction)
        truth = validation.y[:, target_index]
        base_rmse = float(np.sqrt(mean_squared_error(truth, base_prediction)))
        rng = np.random.default_rng(42 + target_index)
        records = []
        for feature_index, feature_name in enumerate(artifact["feature_names"]):
            increases = []
            for _ in range(repeats):
                permuted = scaled.copy()
                permuted[:, feature_index] = permuted[rng.permutation(permuted.shape[0]), feature_index]
                perm_scaled = model.predict(permuted)
                perm_log_prediction = y_scaler.inverse_transform(np.asarray(perm_scaled).reshape(-1, 1)).ravel()
                perm_prediction = np.exp(perm_log_prediction)
                perm_rmse = float(np.sqrt(mean_squared_error(truth, perm_prediction)))
                increases.append(perm_rmse - base_rmse)
            records.append(
                {
                    "feature": feature_name,
                    "rmse_increase_mean": float(np.mean(increases)),
                    "rmse_increase_std": float(np.std(increases, ddof=0)),
                }
            )
        result["by_target"][target] = {"baseline_rmse": base_rmse, "features": records}
    return result


def write_metrics(
    directory: Path,
    rows: Sequence[Mapping[str, Any]],
    gaps: Sequence[Mapping[str, Any]],
    payload: Mapping[str, Any],
) -> Tuple[Path, Path, Path]:
    json_path = directory / "metrics.json"
    json_path.write_text(json.dumps(_json_safe(dict(payload)), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    csv_path = directory / "metrics.csv"
    fieldnames = ["run_kind", "partition", "site", "target", "scale", *METRIC_FIELDS]
    with csv_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fieldnames})
    gaps_path = directory / "metric_gaps.csv"
    gap_fieldnames = [
        "site", "target", "scale", "definition", "training_n", "validation_n",
        *[f"{field}_gap" for field in GAP_METRIC_FIELDS],
    ]
    with gaps_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=gap_fieldnames)
        writer.writeheader()
        for row in gaps:
            writer.writerow({field: row[field] for field in gap_fieldnames})
    return json_path, csv_path, gaps_path


def write_validation_predictions(
    path: Path,
    loaded: LoadedRows,
    prediction: np.ndarray,
    *,
    artifact_sha256: str,
    snapshot_sha256: str,
    run_kind: str,
) -> None:
    require(loaded.y is not None, "validation output requires targets")
    members = []
    for member in loaded.member_id.tolist():
        if member not in members:
            members.append(member)
    nmember = len(members)
    require(loaded.X.shape[0] == len(SITES) * nmember, "validation output row layout mismatch")
    truth = loaded.y.reshape(len(SITES), nmember, len(TARGETS))
    predicted = prediction.reshape(len(SITES), nmember, len(TARGETS))
    with Dataset(str(path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-spinup-validation-predictions-v1"
        dataset.run_kind = run_kind
        dataset.artifact_sha256 = artifact_sha256
        dataset.snapshot_sha256 = snapshot_sha256
        dataset.residual_convention = "prediction minus ELM"
        dataset.createDimension("site", len(SITES))
        dataset.createDimension("member", nmember)
        site_var = dataset.createVariable("site", str, ("site",))
        site_var[:] = np.asarray(SITES, dtype=object)
        member_var = dataset.createVariable("member_id", str, ("member",))
        member_var[:] = np.asarray(members, dtype=object)
        for target_index, target in enumerate(TARGETS):
            units = "gC/m^2" if target == "TOTSOMC" else "gN/m^2"
            for suffix, values in (
                ("elm", truth[:, :, target_index]),
                ("pred", predicted[:, :, target_index]),
                ("residual", predicted[:, :, target_index] - truth[:, :, target_index]),
                ("log_elm", np.log(truth[:, :, target_index])),
                ("log_pred", np.log(predicted[:, :, target_index])),
                ("log_residual", np.log(predicted[:, :, target_index]) - np.log(truth[:, :, target_index])),
            ):
                variable = dataset.createVariable(f"{target}_{suffix}", "f8", ("site", "member"), zlib=True, complevel=4)
                variable[:] = values
                variable.units = "1" if suffix.startswith("log_") else units


def fit_baseline(
    snapshot: ThreeStageSnapshot,
    train_members: Sequence[str],
    validation_members: Sequence[str],
    *,
    run_kind: str,
    output_directory: Path,
    source_identity: Mapping[str, Any],
) -> Dict[str, Any]:
    require(run_kind in {"smoke", "operational"}, "unsupported run kind")
    train = snapshot.load_rows(train_members, include_targets=True)
    validation = snapshot.load_rows(validation_members, include_targets=True)
    require(train.y is not None and validation.y is not None, "training targets missing")
    compact = fit_compact_models(train, MODEL_CONFIG)
    normalized_model_config = compact["model_config"]
    models = compact["models"]
    x_scalers = compact["x_scalers"]
    y_scalers = compact["y_scalers"]
    convergence = compact["convergence"]

    artifact: Dict[str, Any] = {
        "schema": "three-stage-spinup-development-v1",
        "artifact_role": "non_release_smoke" if run_kind == "smoke" else "non_release_validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "target_order": list(TARGETS),
        "target_transform": "natural_log",
        "target_metadata": {
            "TOTSOMC": {"units": "gC/m^2", "definition": "soil1-soil4 full-profile integral over 10 active decomposition layers"},
            "TOTSOMN": {"units": "gN/m^2", "definition": "soil1-soil4 full-profile integral over 10 active decomposition layers"},
        },
        "models": models,
        "x_scalers": x_scalers,
        "y_scalers": y_scalers,
        "model_config": normalized_model_config,
        "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": schema_sha256(snapshot.feature_names),
        "parameter_metadata": snapshot.parameter_metadata,
        "sites": list(SITES),
        "site_identity_is_feature": False,
        "climatology": {
            "start": "2018-01-01T00:00:00",
            "end": "2022-12-31T23:00:00",
            "calendar": "noleap",
            "hours": 43800,
            "std_ddof": 0,
            "rh_seasonal_amplitude": "max minus min of 12 monthly climatological means",
        },
        "fit_scope": {
            "kind": run_kind,
            "train_member_ids": list(train_members),
            "validation_member_ids": list(validation_members),
            "training_rows": int(train.X.shape[0]),
            "validation_rows": int(validation.X.shape[0]),
        },
        "snapshot_revision": "r0001",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "source_identity": dict(source_identity),
        "convergence": convergence,
    }
    train_prediction = predict_matrix(artifact, train.X)
    validation_prediction = predict_matrix(artifact, validation.X)
    rows = metric_rows(run_kind, train, train_prediction, validation, validation_prediction)
    gaps = metric_gap_rows(rows)
    importance = permutation_importance_rmse(artifact, validation, repeats=8)

    output_directory.mkdir(parents=True, exist_ok=False)
    artifact_directory = output_directory / "artifact"
    artifact_path, manifest_path = save_artifact(artifact, artifact_directory)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plots = save_scatter_plots(
        output_directory / "plots", train, train_prediction, validation, validation_prediction, rows
    )
    payload = {
        "schema": "three-stage-spinup-metrics-v1",
        "run_kind": run_kind,
        "artifact_role": artifact["artifact_role"],
        "snapshot_revision": "r0001",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": artifact["feature_schema_sha256"],
        "model_config": normalized_model_config,
        "target_transform": "natural_log",
        "fit_scope": artifact["fit_scope"],
        "metric_definition": {
            "r2": "sklearn.metrics.r2_score",
            "bias": "mean(prediction - ELM)",
            "residual_std": "population SD of prediction - ELM",
            "log": "natural logarithm",
        },
        "convergence": convergence,
        "rows": rows,
        "validation_minus_training_gaps": gaps,
        "permutation_importance": importance,
    }
    metrics_json, metrics_csv, metric_gaps_csv = write_metrics(output_directory, rows, gaps, payload)
    prediction_path = output_directory / "validation_predictions.nc"
    write_validation_predictions(
        prediction_path,
        validation,
        validation_prediction,
        artifact_sha256=str(manifest["artifact_sha256"]),
        snapshot_sha256=snapshot.snapshot_sha256,
        run_kind=run_kind,
    )
    package_manifest = {
        "schema": "three-stage-spinup-development-package-v1",
        "run_kind": run_kind,
        "artifact_role": artifact["artifact_role"],
        "files": {},
    }
    for path in [artifact_path, manifest_path, metrics_json, metrics_csv, metric_gaps_csv, prediction_path, *plots]:
        relative = path.relative_to(output_directory)
        package_manifest["files"][str(relative)] = {
            "size_bytes": path.stat().st_size,
            "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        }
    (output_directory / "package_manifest.json").write_text(
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "artifact_directory": str(artifact_directory),
        "artifact_sha256": manifest["artifact_sha256"],
        "metrics_json": str(metrics_json),
        "validation_predictions": str(prediction_path),
        "package_manifest": str(output_directory / "package_manifest.json"),
    }
