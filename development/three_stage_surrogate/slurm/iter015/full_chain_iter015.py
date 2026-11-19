"""Fold-specific ABBY/JERC spinup -> gated GPP -> SR fitting for Iter015."""
from __future__ import annotations

import csv
import json
import pickle
import shutil
import warnings
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from netCDF4 import Dataset
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler

from model_ELM.three_stage_data import SITES, TARGETS, ThreeStageSnapshot, require, schema_sha256, sha256_file
from model_ELM.three_stage_gpp import (
    FEATURE_COUNT as GPP_FEATURE_COUNT,
    FORCING_FEATURE_NAMES,
    FORCING_NAMES,
    HOURS,
    SURFACE_NAMES,
    _model as gpp_model,
    _site_static,
    engineer_forcing,
    feature_names as gpp_feature_names,
    predict_artifact as predict_gpp_artifact,
)
from model_ELM.three_stage_gpp_release import validate_split_design
from model_ELM.three_stage_inference import FoldThreeStageInference
from model_ELM.three_stage_spinup import fit_compact_models, predict_compact_models
from model_ELM.three_stage_spinup_release import MODEL_CONFIG as SPINUP_MODEL_CONFIG, _depth_log_errors
from model_ELM.three_stage_sr import (
    FEATURE_COUNT as SR_FEATURE_COUNT,
    _model as sr_model,
    feature_names as sr_feature_names,
    predict_artifact as predict_sr_artifact,
)


SCHEMA = "three-stage-full-chain-iter015-v1"
QUANTILES = (0.01, 0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975, 0.99)
RESOLUTIONS = ("hourly", "daily")
GPP_POLICY = "hard_zero_v1"


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path.name}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "three-stage-iter015-config-v1", "Iter015 config schema mismatch")
    return payload


def load_splits(config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(config["repeated_split_manifest"])
    require(sha256_file(path) == config["repeated_split_manifest_sha256"], "Iter015 split manifest mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "three-stage-spinup-iter004-splits-v1", "Iter015 split schema mismatch")
    require(int(payload.get("seed", -1)) == int(config["repeated_split_seed"]), "Iter015 split seed mismatch")
    require(payload.get("split_design_sha256") == config["split_design_sha256"], "Iter015 split design mismatch")
    require(len(payload.get("splits", [])) == 20, "Iter015 requires twenty splits")
    return payload


def validate_config(config: Mapping[str, Any], *, verify_snapshot_components: bool) -> tuple[ThreeStageSnapshot, dict[str, Any]]:
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=verify_snapshot_components)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "Iter015 snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "Iter015 global split mismatch")
    require(config.get("plan_sha256") == "6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d", "Iter015 plan mismatch")
    require(config.get("gpp_output_policy") == GPP_POLICY, "Iter015 GPP policy mismatch")
    for key in (
        "fixed_test_allowed", "all_development_fit_allowed", "cross_fitting_allowed",
        "release_modification_allowed",
    ):
        require(config.get(key) is False, f"Iter015 scope boundary mismatch: {key}")
    for path_key, hash_key in (
        ("gpp_configuration_file", "gpp_configuration_sha256"),
        ("sr_configuration_file", "sr_configuration_sha256"),
    ):
        require(sha256_file(Path(config[path_key])) == config[hash_key], f"Iter015 dependency mismatch: {path_key}")
    gpp_configuration = json.loads(Path(config["gpp_configuration_file"]).read_text(encoding="utf-8"))
    sr_configuration = json.loads(Path(config["sr_configuration_file"]).read_text(encoding="utf-8"))
    require(config["gpp_model_config"] == gpp_configuration["model_config"], "Iter015 GPP model mismatch")
    require(config["sr_model_config"] == sr_configuration["model_config"], "Iter015 SR model mismatch")
    splits = load_splits(config)
    validate_split_design(snapshot, splits)
    return snapshot, splits


def _member_number(member: str) -> int:
    require(len(member) == 6 and member.startswith("g") and member[1:].isdigit(), "invalid member ID")
    return int(member[1:])


def _forcing_and_surface(snapshot: ThreeStageSnapshot, site: str, hours: int) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
        time = np.asarray(dataset.variables["time"][:hours], dtype=np.int64)
        require(np.array_equal(time, np.arange(hours)), f"{site} time mismatch")
        forcing = {name: np.asarray(dataset.variables[name][:hours], dtype=np.float64) for name in FORCING_NAMES}
        engineered = engineer_forcing(forcing, time).astype(np.float32)
        surface = _site_static(dataset).astype(np.float32)
    return forcing, time, engineered, surface


def _feature_block(
    forcing_features: np.ndarray,
    parameters: np.ndarray,
    surface: np.ndarray,
    cn: np.ndarray,
) -> np.ndarray:
    count = parameters.shape[0]
    hours = forcing_features.shape[0]
    block = np.empty((count, hours, GPP_FEATURE_COUNT), dtype=np.float32)
    block[:, :, : len(FORCING_FEATURE_NAMES)] = forcing_features[None, :, :]
    static = np.column_stack((parameters, np.tile(surface, (count, 1)), cn)).astype(np.float32)
    require(static.shape == (count, 23), "Iter015 static feature mismatch")
    block[:, :, len(FORCING_FEATURE_NAMES) :] = static[:, None, :]
    return block


def _target(snapshot: ThreeStageSnapshot, site: str, target: str, members: Sequence[str], hours: int) -> np.ndarray:
    path = snapshot.root / "sites" / site / "input_data_v1.nc"
    values = np.empty((len(members), hours), dtype=np.float32)
    with Dataset(str(path), "r") as dataset:
        require(str(dataset.variables[target].units) == "gC/m^2/day", f"{site} {target} units mismatch")
        for index, member in enumerate(members):
            values[index] = np.asarray(dataset.variables[target][_member_number(member) - 1, :hours], dtype=np.float32)
    require(np.all(np.isfinite(values)), f"{site} {target} target invalid")
    return values


def _metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    observed = np.asarray(truth, dtype=np.float64).reshape(-1)
    estimated = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(observed.size == estimated.size and observed.size > 1, "Iter015 metric size mismatch")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(estimated)), "Iter015 metric nonfinite")
    residual = estimated - observed
    denominator = float(np.sum((observed - float(np.mean(observed))) ** 2))
    require(denominator > 0.0, "Iter015 R2 denominator invalid")
    result: dict[str, float | int] = {
        "expected_count": int(observed.size),
        "valid_count": int(observed.size),
        "r2": float(1.0 - float(np.sum(residual * residual)) / denominator),
        "rmse": float(np.sqrt(float(np.mean(residual * residual)))),
        "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)),
        "residual_std": float(np.std(residual, ddof=0)),
        "coverage_fraction": 1.0,
    }
    for quantile, value in zip(QUANTILES, np.quantile(residual, QUANTILES, method="linear")):
        result[f"q{str(quantile).replace('.', '_')}"] = float(value)
    return result


def _artifact_paths(output: Path) -> tuple[Path, Path, Path]:
    directory = output / "artifacts"
    directory.mkdir()
    return directory / "spinup_fold.pkl", directory / "gpp_fold.pkl", directory / "sr_fold.pkl"


def _pickle(path: Path, value: Any) -> str:
    with path.open("xb") as handle:
        pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return sha256_file(path)


def _reload_pickle(path: Path, expected_sha256: str) -> Any:
    require(sha256_file(path) == expected_sha256, f"Iter015 artifact identity mismatch: {path.name}")
    with path.open("rb") as handle:
        return pickle.load(handle)


def _offsets(partitions: Sequence[tuple[str, Sequence[str]]], hours: int) -> tuple[list[dict[str, Any]], int]:
    cursor = 0
    rows: list[dict[str, Any]] = []
    for partition, members in partitions:
        for site in SITES:
            start = cursor
            cursor += len(members) * hours
            rows.append({"partition": partition, "site": site, "start": start, "end": cursor, "members": list(members)})
    return rows, cursor


def _offset(offsets: Sequence[Mapping[str, Any]], partition: str, site: str) -> Mapping[str, Any]:
    return next(item for item in offsets if item["partition"] == partition and item["site"] == site)


def _fit_hourly_stage(
    *,
    stage: str,
    config: Mapping[str, Any],
    snapshot: ThreeStageSnapshot,
    partitions: Sequence[tuple[str, Sequence[str]]],
    parameters: Mapping[str, np.ndarray],
    cn_values: Mapping[tuple[str, str], np.ndarray],
    forcing_features: Mapping[str, np.ndarray],
    surfaces: Mapping[str, np.ndarray],
    offsets: Sequence[Mapping[str, Any]],
    total_rows: int,
    hours: int,
    output: Path,
    gpp_gated: np.memmap | None,
    smoke: bool,
) -> tuple[dict[str, Any], np.memmap, np.memmap, list[dict[str, Any]]]:
    feature_count = GPP_FEATURE_COUNT if stage == "GPP" else SR_FEATURE_COUNT
    target_name = stage
    x_path = output / f"{stage.lower()}_X_scaled_float32.dat"
    y_path = output / f"{stage.lower()}_y_scaled_float32.dat"
    prediction_path = output / f"{stage.lower()}_predictions_physical_float32.dat"
    x_scaler = StandardScaler(copy=True)
    y_scaler = StandardScaler(copy=True)
    train_members = partitions[0][1]
    for site in SITES:
        truth = _target(snapshot, site, target_name, train_members, hours)
        for index, member in enumerate(train_members):
            base = _feature_block(
                forcing_features[site], parameters["training"][index : index + 1], surfaces[site],
                cn_values[("training", site)][index : index + 1],
            ).reshape(hours, GPP_FEATURE_COUNT)
            if stage == "SR":
                item = _offset(offsets, "training", site)
                start = int(item["start"]) + index * hours
                block = np.column_stack((base, np.asarray(gpp_gated[start : start + hours], dtype=np.float32)))
            else:
                block = base
            x_scaler.partial_fit(block)
            y_scaler.partial_fit(truth[index].reshape(-1, 1))
    scaled_x = np.memmap(x_path, mode="w+", dtype=np.float32, shape=(total_rows, feature_count))
    scaled_y = np.memmap(y_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    for partition, members in partitions:
        for site in SITES:
            truth = _target(snapshot, site, target_name, members, hours)
            item = _offset(offsets, partition, site)
            cursor = int(item["start"])
            for index, member in enumerate(members):
                base = _feature_block(
                    forcing_features[site], parameters[partition][index : index + 1], surfaces[site],
                    cn_values[(partition, site)][index : index + 1],
                ).reshape(hours, GPP_FEATURE_COUNT)
                if stage == "SR":
                    block = np.column_stack((base, np.asarray(gpp_gated[cursor : cursor + hours], dtype=np.float32)))
                else:
                    block = base
                scaled_x[cursor : cursor + hours] = x_scaler.transform(block).astype(np.float32)
                scaled_y[cursor : cursor + hours] = y_scaler.transform(truth[index].reshape(-1, 1)).astype(np.float32).ravel()
                cursor += hours
            require(cursor == int(item["end"]), f"Iter015 {stage} partition layout mismatch")
    scaled_x.flush()
    scaled_y.flush()
    model_config = config["gpp_model_config"] if stage == "GPP" else config["sr_model_config"]
    model_factory = gpp_model if stage == "GPP" else sr_model
    model = model_factory({"model_config": model_config}, smoke=smoke)
    training_rows = len(SITES) * len(train_members) * hours
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(scaled_x[:training_rows], scaled_y[:training_rows])
    warning_rows = [
        {"stage": stage, "category": item.category.__name__, "message": str(item.message)} for item in captured
    ]
    y_mean = float(y_scaler.mean_[0])
    y_scale = float(y_scaler.scale_[0])
    artifact = {
        "schema": f"three-stage-{stage.lower()}-fold-artifact-v1",
        "split_id": int(config["active_split_id"]),
        "model": model,
        "x_mean": x_scaler.mean_,
        "x_scale": x_scaler.scale_,
        "y_mean": y_mean,
        "y_scale": y_scale,
        "feature_names": list(gpp_feature_names(snapshot) if stage == "GPP" else sr_feature_names(snapshot)),
        "feature_schema_sha256": schema_sha256(gpp_feature_names(snapshot) if stage == "GPP" else sr_feature_names(snapshot)),
        "model_config": model_config,
        "train_member_ids": list(train_members),
        "fixed_test_access": False,
        "gpp_output_policy": GPP_POLICY if stage == "SR" else "applied_after_physical_reconstruction",
    }
    predictions = np.memmap(prediction_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    predictor = predict_gpp_artifact if stage == "GPP" else predict_sr_artifact
    first_raw: np.ndarray | None = None
    for partition, members in partitions:
        for site in SITES:
            item = _offset(offsets, partition, site)
            cursor = int(item["start"])
            for index, member in enumerate(members):
                base = _feature_block(
                    forcing_features[site], parameters[partition][index : index + 1], surfaces[site],
                    cn_values[(partition, site)][index : index + 1],
                ).reshape(hours, GPP_FEATURE_COUNT)
                if stage == "SR":
                    raw_block = np.column_stack((base, np.asarray(gpp_gated[cursor : cursor + hours], dtype=np.float32)))
                else:
                    raw_block = base
                estimate = predictor(artifact, raw_block)
                require(np.all(np.isfinite(estimate)), f"Iter015 {stage} prediction invalid")
                predictions[cursor : cursor + hours] = estimate.astype(np.float32)
                if first_raw is None:
                    first_raw = raw_block[: min(hours, 48)].copy()
                cursor += hours
            require(cursor == int(item["end"]), f"Iter015 {stage} prediction layout mismatch")
    predictions.flush()
    require(first_raw is not None, f"Iter015 {stage} replay fixture missing")
    replay = predictor(artifact, first_raw)
    require(np.allclose(replay, predictions[: replay.size], rtol=1e-6, atol=1e-6), f"Iter015 {stage} raw replay mismatch")
    del scaled_x, scaled_y
    x_path.unlink()
    y_path.unlink()
    return artifact, predictions, np.memmap(prediction_path, mode="r+", dtype=np.float32, shape=(total_rows,)), warning_rows


def _spinup_metrics(
    partitions: Sequence[tuple[str, Sequence[str]]],
    loaded: Mapping[str, Any],
    predicted: Mapping[str, np.ndarray],
    split_id: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for partition, members in partitions:
        truth = loaded[partition].y
        estimate = predicted[partition]
        require(truth is not None, "Iter015 spinup truth missing")
        for site in (*SITES, "pooled"):
            mask = np.ones(loaded[partition].site.shape, dtype=bool) if site == "pooled" else loaded[partition].site == site
            for target_index, target in enumerate(TARGETS):
                for scale, observed, modeled in (
                    ("physical", truth[mask, target_index], estimate[mask, target_index]),
                    ("log", np.log(truth[mask, target_index]), np.log(estimate[mask, target_index])),
                ):
                    rows.append({
                        "split_id": split_id, "stage": "spinup", "partition": partition,
                        "site": site, "target": target, "scale": scale, "resolution": "member",
                        **_metrics(observed, modeled),
                    })
    return rows


def _flux_metrics(
    snapshot: ThreeStageSnapshot,
    partitions: Sequence[tuple[str, Sequence[str]]],
    offsets: Sequence[Mapping[str, Any]],
    predictions: Mapping[str, np.memmap],
    hours: int,
    split_id: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for partition, members in partitions:
        by_target: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {"GPP": {}, "SR": {}}
        for target in ("GPP", "SR"):
            for site in SITES:
                item = _offset(offsets, partition, site)
                observed = _target(snapshot, site, target, members, hours)
                modeled = np.asarray(predictions[target][int(item["start"]) : int(item["end"])], dtype=np.float32).reshape(len(members), hours)
                by_target[target][site] = (observed, modeled)
            for site in (*SITES, "pooled"):
                if site == "pooled":
                    observed = np.concatenate([by_target[target][value][0].reshape(-1) for value in SITES])
                    modeled = np.concatenate([by_target[target][value][1].reshape(-1) for value in SITES])
                else:
                    observed, modeled = by_target[target][site]
                    observed = observed.reshape(-1)
                    modeled = modeled.reshape(-1)
                for resolution in RESOLUTIONS:
                    if resolution == "daily":
                        require(hours % 24 == 0, "Iter015 daily coverage mismatch")
                        observed_values = observed.reshape(-1, 24).mean(axis=1)
                        modeled_values = modeled.reshape(-1, 24).mean(axis=1)
                    else:
                        observed_values = observed
                        modeled_values = modeled
                    rows.append({
                        "split_id": split_id, "stage": target.lower(), "partition": partition,
                        "site": site, "target": target, "scale": "physical", "resolution": resolution,
                        **_metrics(observed_values, modeled_values),
                    })
    return rows


def _gate_comparison(
    snapshot: ThreeStageSnapshot,
    validation_members: Sequence[str],
    offsets: Sequence[Mapping[str, Any]],
    raw: np.memmap,
    gated: np.memmap,
    hours: int,
    split_id: int,
) -> list[dict[str, Any]]:
    by_site: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for site in SITES:
        item = _offset(offsets, "validation", site)
        truth = _target(snapshot, site, "GPP", validation_members, hours).reshape(-1)
        raw_values = np.asarray(raw[int(item["start"]) : int(item["end"])], dtype=np.float32)
        gated_values = np.asarray(gated[int(item["start"]) : int(item["end"])], dtype=np.float32)
        require(np.array_equal(gated_values, np.maximum(raw_values, np.float32(0.0))), "Iter015 GPP gate mismatch")
        by_site[site] = truth, raw_values, gated_values
    rows: list[dict[str, Any]] = []
    for site in (*SITES, "pooled"):
        if site == "pooled":
            truth = np.concatenate([by_site[value][0] for value in SITES])
            raw_values = np.concatenate([by_site[value][1] for value in SITES])
            gated_values = np.concatenate([by_site[value][2] for value in SITES])
        else:
            truth, raw_values, gated_values = by_site[site]
        for resolution in RESOLUTIONS:
            if resolution == "daily":
                observed = truth.reshape(-1, 24).mean(axis=1)
                raw_use = raw_values.reshape(-1, 24).mean(axis=1)
                gated_use = gated_values.reshape(-1, 24).mean(axis=1)
            else:
                observed, raw_use, gated_use = truth, raw_values, gated_values
            raw_metrics = _metrics(observed, raw_use)
            gated_metrics = _metrics(observed, gated_use)
            rows.append({
                "split_id": split_id, "site": site, "resolution": resolution,
                "raw_r2": raw_metrics["r2"], "gated_r2": gated_metrics["r2"],
                "gated_minus_raw_r2": float(gated_metrics["r2"]) - float(raw_metrics["r2"]),
                "raw_rmse": raw_metrics["rmse"], "gated_rmse": gated_metrics["rmse"],
                "raw_minus_gated_rmse": float(raw_metrics["rmse"]) - float(gated_metrics["rmse"]),
                "negative_raw_count": int(np.count_nonzero(raw_use < 0.0)),
                "same_target_count": int(observed.size),
            })
    require(len(rows) == 6, "Iter015 per-split GPP gate row count mismatch")
    return rows


def _propagation_and_depth(
    snapshot: ThreeStageSnapshot,
    validation_members: Sequence[str],
    validation_loaded: Any,
    validation_cn: np.ndarray,
    offsets: Sequence[Mapping[str, Any]],
    predictions: Mapping[str, np.memmap],
    hours: int,
    split_id: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    propagation: list[dict[str, Any]] = []
    truth_cn = validation_loaded.y
    require(truth_cn is not None, "Iter015 propagation truth missing")
    for site_index, site in enumerate(SITES):
        cn_start = site_index * len(validation_members)
        item = _offset(offsets, "validation", site)
        gpp_truth = _target(snapshot, site, "GPP", validation_members, hours)
        sr_truth = _target(snapshot, site, "SR", validation_members, hours)
        gpp_pred = np.asarray(predictions["GPP"][int(item["start"]) : int(item["end"])], dtype=np.float64).reshape(len(validation_members), hours)
        sr_pred = np.asarray(predictions["SR"][int(item["start"]) : int(item["end"])], dtype=np.float64).reshape(len(validation_members), hours)
        for member_index, member in enumerate(validation_members):
            cn_error = np.log(validation_cn[cn_start + member_index]) - np.log(truth_cn[cn_start + member_index])
            propagation.append({
                "split_id": split_id, "site": site, "member_id": member,
                "cn_rms_log_error": float(np.sqrt(np.mean(cn_error * cn_error))),
                "gpp_hourly_rmse": float(np.sqrt(np.mean((gpp_pred[member_index] - gpp_truth[member_index]) ** 2))),
                "sr_hourly_rmse": float(np.sqrt(np.mean((sr_pred[member_index] - sr_truth[member_index]) ** 2))),
            })
    all_loaded = snapshot.load_rows(snapshot.development_ranked, include_targets=True)
    depth_errors, depth_hashes = _depth_log_errors(snapshot, all_loaded)
    development_position = {member: index for index, member in enumerate(snapshot.development_ranked)}
    depth_rows: list[dict[str, Any]] = []
    for site_index, site in enumerate(SITES):
        begin = site_index * len(validation_members)
        finish = begin + len(validation_members)
        surrogate = np.log(validation_cn[begin:finish]) - np.log(truth_cn[begin:finish])
        positions = np.asarray([development_position[member] for member in validation_members], dtype=np.int64)
        depth = np.column_stack([depth_errors[site][target][positions] for target in TARGETS])
        combined = np.column_stack((surrogate, depth))
        covariance = np.cov(combined, rowvar=False, ddof=0)
        correlation = np.corrcoef(combined, rowvar=False)
        labels = ("surrogate_C", "surrogate_N", "depth_C", "depth_N")
        for row_index, row_name in enumerate(labels):
            for column_index, column_name in enumerate(labels):
                depth_rows.append({
                    "split_id": split_id, "site": site, "row": row_name, "column": column_name,
                    "covariance": float(covariance[row_index, column_index]),
                    "correlation": float(correlation[row_index, column_index]),
                    "count": len(validation_members),
                    "preprocessing_sha256": depth_hashes[site],
                })
    return propagation, depth_rows


def _write_validation_predictions(
    path: Path,
    split_id: int,
    validation_members: Sequence[str],
    validation_loaded: Any,
    validation_cn: np.ndarray,
    offsets: Sequence[Mapping[str, Any]],
    raw: np.memmap,
    gated: np.memmap,
    sr: np.memmap,
    hours: int,
) -> None:
    with Dataset(str(path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-iter015-heldout-predictions-v1"
        dataset.split_id = split_id
        dataset.gpp_output_policy = GPP_POLICY
        dataset.residual_convention = "prediction minus ELM"
        dataset.fixed_test_access = 0
        dataset.createDimension("site", len(SITES))
        dataset.createDimension("member", len(validation_members))
        dataset.createDimension("target", len(TARGETS))
        dataset.createDimension("time", hours)
        dataset.createVariable("site", str, ("site",))[:] = np.asarray(SITES, dtype=object)
        dataset.createVariable("member_id", str, ("member",))[:] = np.asarray(validation_members, dtype=object)
        dataset.createVariable("target", str, ("target",))[:] = np.asarray(TARGETS, dtype=object)
        dataset.createVariable("time", "i8", ("time",))[:] = np.arange(hours, dtype=np.int64)
        truth_cn = validation_loaded.y.reshape(len(SITES), len(validation_members), len(TARGETS))
        pred_cn = validation_cn.reshape(len(SITES), len(validation_members), len(TARGETS))
        dataset.createVariable("CN_elm", "f8", ("site", "member", "target"), zlib=True)[:] = truth_cn
        dataset.createVariable("CN_predicted", "f8", ("site", "member", "target"), zlib=True)[:] = pred_cn
        for name, source in (("GPP_raw", raw), ("GPP_gated", gated), ("SR_predicted", sr)):
            variable = dataset.createVariable(name, "f4", ("site", "member", "time"), zlib=True, complevel=4, chunksizes=(1, 1, min(hours, 8760)))
            for site_index, site in enumerate(SITES):
                item = _offset(offsets, "validation", site)
                variable[site_index] = np.asarray(source[int(item["start"]) : int(item["end"])], dtype=np.float32).reshape(len(validation_members), hours)


def run_split(config: Mapping[str, Any], split_id: int, output: Path, *, smoke: bool = False) -> dict[str, Any]:
    require(not output.exists(), f"Iter015 split output exists: {output}")
    output.mkdir(parents=True)
    snapshot, splits = validate_config(config, verify_snapshot_components=True)
    item = splits["splits"][split_id]
    train_members = list(item["train_member_ids"])
    validation_members = list(item["validation_member_ids"])
    hours = HOURS
    if smoke:
        train_members = train_members[:8]
        validation_members = validation_members[:2]
        hours = int(config["smoke_hours"])
    partitions: list[tuple[str, Sequence[str]]] = [("training", train_members), ("validation", validation_members)]
    active_config = dict(config)
    active_config["active_split_id"] = split_id
    loaded = {
        partition: snapshot.load_rows(members, include_targets=True) for partition, members in partitions
    }
    fitted_spinup = fit_compact_models(loaded["training"], SPINUP_MODEL_CONFIG)
    spinup_artifact = {
        **fitted_spinup,
        "schema": "three-stage-spinup-fold-artifact-v1",
        "split_id": split_id,
        "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": schema_sha256(snapshot.feature_names),
        "train_member_ids": train_members,
        "fixed_test_access": False,
    }
    cn_predictions = {
        partition: predict_compact_models(spinup_artifact, loaded[partition].X) for partition, _ in partitions
    }
    parameters = {partition: snapshot._parameter_values(members) for partition, members in partitions}
    cn_values: dict[tuple[str, str], np.ndarray] = {}
    for partition, members in partitions:
        for site_index, site in enumerate(SITES):
            begin = site_index * len(members)
            cn_values[(partition, site)] = cn_predictions[partition][begin : begin + len(members)]
    forcing_raw: dict[str, dict[str, np.ndarray]] = {}
    times: dict[str, np.ndarray] = {}
    forcing_features: dict[str, np.ndarray] = {}
    surfaces: dict[str, np.ndarray] = {}
    for site in SITES:
        raw, axis, engineered, surface = _forcing_and_surface(snapshot, site, hours)
        forcing_raw[site] = raw
        times[site] = axis
        forcing_features[site] = engineered
        surfaces[site] = surface
    offsets, total_rows = _offsets(partitions, hours)
    spinup_path, gpp_path, sr_path = _artifact_paths(output)
    spinup_sha256 = _pickle(spinup_path, spinup_artifact)
    gpp_artifact, gpp_raw, gpp_raw_rw, gpp_warnings = _fit_hourly_stage(
        stage="GPP", config=active_config, snapshot=snapshot, partitions=partitions,
        parameters=parameters, cn_values=cn_values, forcing_features=forcing_features,
        surfaces=surfaces, offsets=offsets, total_rows=total_rows, hours=hours, output=output,
        gpp_gated=None, smoke=smoke,
    )
    gpp_gated_path = output / "gpp_gated_physical_float32.dat"
    gpp_gated = np.memmap(gpp_gated_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    chunk = int(config["prediction_chunk_rows"])
    for start in range(0, total_rows, chunk):
        end = min(start + chunk, total_rows)
        gpp_gated[start:end] = np.maximum(np.asarray(gpp_raw_rw[start:end], dtype=np.float32), np.float32(0.0))
    gpp_gated.flush()
    gpp_sha256 = _pickle(gpp_path, gpp_artifact)
    sr_artifact, sr_predictions, sr_rw, sr_warnings = _fit_hourly_stage(
        stage="SR", config=active_config, snapshot=snapshot, partitions=partitions,
        parameters=parameters, cn_values=cn_values, forcing_features=forcing_features,
        surfaces=surfaces, offsets=offsets, total_rows=total_rows, hours=hours, output=output,
        gpp_gated=gpp_gated, smoke=smoke,
    )
    sr_sha256 = _pickle(sr_path, sr_artifact)
    reloaded_spinup = _reload_pickle(spinup_path, spinup_sha256)
    reloaded_gpp = _reload_pickle(gpp_path, gpp_sha256)
    reloaded_sr = _reload_pickle(sr_path, sr_sha256)
    engine = FoldThreeStageInference(
        snapshot, reloaded_spinup, reloaded_gpp, reloaded_sr, split_id=split_id,
        gpp_output_policy=GPP_POLICY,
    )
    validation_cn_from_engine: list[np.ndarray] = []
    for site_index, site in enumerate(SITES):
        item_offset = _offset(offsets, "validation", site)
        shape = (len(validation_members), hours)
        start_row = int(item_offset["start"])
        end_row = int(item_offset["end"])
        cn = engine.predict_to_arrays(
            parameters["validation"], site=site, forcing=forcing_raw[site], time=times[site],
            start=0, end=hours,
            gpp_raw_output=gpp_raw_rw[start_row:end_row].reshape(shape),
            gpp_output=gpp_gated[start_row:end_row].reshape(shape),
            sr_output=sr_rw[start_row:end_row].reshape(shape), member_chunk=int(config["inference_member_chunk"]),
        )
        validation_cn_from_engine.append(cn)
        expected_cn = cn_values[("validation", site)]
        require(np.allclose(cn, expected_cn, rtol=1e-12, atol=1e-10), "Iter015 engine C/N mismatch")
        sample_count = min(2, len(validation_members))
        replay = engine.predict(
            parameters["validation"][:sample_count], site=site, forcing=forcing_raw[site], time=times[site],
            start=0, end=hours, member_chunk=int(config["inference_member_chunk"]),
        )
        require(np.allclose(replay.gpp_raw, gpp_raw_rw[start_row : start_row + sample_count * hours].reshape(sample_count, hours), rtol=1e-6, atol=1e-6), "Iter015 streamed raw-GPP replay mismatch")
        require(np.allclose(replay.gpp, gpp_gated[start_row : start_row + sample_count * hours].reshape(sample_count, hours), rtol=1e-6, atol=1e-6), "Iter015 streamed gated-GPP replay mismatch")
        require(np.allclose(replay.sr, sr_rw[start_row : start_row + sample_count * hours].reshape(sample_count, hours), rtol=1e-6, atol=1e-6), "Iter015 streamed SR replay mismatch")
    gpp_raw_rw.flush()
    gpp_gated.flush()
    sr_rw.flush()
    validation_cn = np.vstack(validation_cn_from_engine)
    metric_rows = _spinup_metrics(partitions, loaded, cn_predictions, split_id)
    metric_rows.extend(_flux_metrics(snapshot, partitions, offsets, {"GPP": gpp_gated, "SR": sr_rw}, hours, split_id))
    gate_rows = _gate_comparison(snapshot, validation_members, offsets, gpp_raw_rw, gpp_gated, hours, split_id)
    propagation_rows, depth_rows = _propagation_and_depth(
        snapshot, validation_members, loaded["validation"], validation_cn, offsets,
        {"GPP": gpp_gated, "SR": sr_rw}, hours, split_id,
    )
    write_csv(output / "metrics.csv", metric_rows)
    write_csv(output / "gpp_gate_comparison.csv", gate_rows)
    write_csv(output / "error_propagation.csv", propagation_rows)
    write_csv(output / "depth_error_dependence.csv", depth_rows)
    write_json(output / "convergence.json", {
        "schema": "three-stage-iter015-convergence-v1",
        "spinup": spinup_artifact["convergence"], "gpp": gpp_warnings, "sr": sr_warnings,
    })
    write_json(output / "layout.json", {
        "schema": "three-stage-iter015-layout-v1", "split_id": split_id, "smoke": smoke,
        "hours": hours, "offsets": offsets, "total_rows": total_rows,
        "train_member_ids": train_members, "validation_member_ids": validation_members,
        "gpp_raw_file": Path(gpp_raw_rw.filename).name,
        "gpp_gated_file": gpp_gated_path.name,
        "sr_file": Path(sr_rw.filename).name,
    })
    prediction_path = output / "heldout_predictions.nc"
    _write_validation_predictions(
        prediction_path, split_id, validation_members, loaded["validation"], validation_cn,
        offsets, gpp_raw_rw, gpp_gated, sr_rw, hours,
    )
    artifact_hashes = {"spinup": spinup_sha256, "gpp": gpp_sha256, "sr": sr_sha256}
    file_hashes = {
        name: sha256_file(output / name) for name in (
            "metrics.csv", "gpp_gate_comparison.csv", "error_propagation.csv",
            "depth_error_dependence.csv", "convergence.json", "layout.json", "heldout_predictions.nc",
            "gpp_predictions_physical_float32.dat", "gpp_gated_physical_float32.dat",
            "sr_predictions_physical_float32.dat",
        )
    }
    report = {
        "schema": "three-stage-iter015-split-report-v1",
        "result": "pass", "split_id": split_id, "smoke": smoke, "hours": hours,
        "train_member_count": len(train_members), "validation_member_count": len(validation_members),
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"],
        "repeated_split_manifest_sha256": config["repeated_split_manifest_sha256"],
        "split_design_sha256": config["split_design_sha256"],
        "gpp_output_policy": GPP_POLICY,
        "artifact_sha256": artifact_hashes, "file_sha256": file_hashes,
        "artifact_reload_complete": True,
        "metric_row_count": len(metric_rows), "gate_row_count": len(gate_rows),
        "propagation_row_count": len(propagation_rows), "depth_row_count": len(depth_rows),
        "fixed_test_access": False, "all_development_fit": False, "cross_fitting": False,
        "published_upstream_training_inputs": False, "release_modified": False,
        "scaled_scratch_removed": True,
    }
    write_json(output / "split_report.json", report)
    return report


def preflight(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"Iter015 preflight output exists: {output}")
    output.mkdir(parents=True)
    snapshot, splits = validate_config(config, verify_snapshot_components=True)
    counts = validate_split_design(snapshot, splits)
    fixture = np.asarray((-1.0, -0.0, 0.25), dtype=np.float64)
    require(np.array_equal(np.maximum(fixture, 0.0), np.asarray((0.0, 0.0, 0.25))), "hard-zero fixture mismatch")
    smoke_report = run_split(config, 0, output / "smoke", smoke=True)
    report = {
        "schema": "three-stage-iter015-preflight-report-v1", "result": "pass",
        "snapshot_sha256": snapshot.snapshot_sha256, "split_count": len(splits["splits"]),
        "four_appearance_members": sum(value == 4 for value in counts.values()),
        "five_appearance_members": sum(value == 5 for value in counts.values()),
        "smoke_report_sha256": sha256_file(output / "smoke" / "split_report.json"),
        "gpp_output_policy": GPP_POLICY, "fixed_test_access": False,
    }
    write_json(output / "preflight_report.json", report)
    return report
