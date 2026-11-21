#!/usr/bin/env python
"""Independent fresh-process validation of the Iter005 GPP baseline."""
from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES, HOURS, MODEL_CONFIG, QUANTILES, SURFACE_NAMES, UPSTREAM_NAMES, engineer_forcing, load_prepared, predict_artifact, write_json


def source_raw_rows(config: dict, layout: dict, selected_rows: np.ndarray) -> np.ndarray:
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    params = snapshot._parameter_values(snapshot.development_ranked)
    position = {member: index for index, member in enumerate(snapshot.development_ranked)}
    with Dataset(config["predicted_cn_handoff"], "r") as handoff:
        upstream = {name: np.asarray(handoff.variables[name][:], dtype=np.float64) for name in UPSTREAM_NAMES}
    datasets = {site: Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") for site in SITES}
    try:
        forcing = {}
        for site, dataset in datasets.items():
            time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
            raw_forcing = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in FORCING_NAMES}
            forcing[site] = engineer_forcing(raw_forcing, time)
        result = []
        for global_row in selected_rows.tolist():
            matches = [item for item in layout["offsets"] if int(item["start"]) <= global_row < int(item["end"])]
            require(len(matches) == 1, f"source sample offset mismatch: {global_row}")
            item = matches[0]
            local = global_row - int(item["start"])
            member = item["members"][local // HOURS]
            hour = local % HOURS
            site = item["site"]
            site_index = list(SITES).index(site)
            member_position = position[member]
            surface = [float(np.asarray(datasets[site].variables[name][:])) for name in SURFACE_NAMES]
            result.append(
                forcing[site][hour].tolist() + params[member_position].tolist() + surface
                + [float(upstream[name][site_index, member_position]) for name in UPSTREAM_NAMES]
            )
    finally:
        for dataset in datasets.values():
            dataset.close()
    values = np.asarray(result, dtype=np.float64)
    require(values.shape == (selected_rows.size, layout["features"]) and np.all(np.isfinite(values)), "source sample reconstruction invalid")
    return values


def independent_metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    truth64 = np.asarray(truth, dtype=np.float64).reshape(-1)
    pred64 = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(truth64.size == pred64.size and truth64.size > 1, "invalid validation metric rows")
    finite = np.isfinite(truth64) & np.isfinite(pred64)
    require(np.all(finite), "validation metric rows contain gaps")
    residual = pred64 - truth64
    ss_res = float(np.dot(residual, residual))
    centered = truth64 - float(np.mean(truth64))
    ss_tot = float(np.dot(centered, centered))
    result: dict[str, float | int] = {
        "count": int(truth64.size),
        "r2": float(1.0 - ss_res / ss_tot),
        "rmse": float(np.sqrt(ss_res / truth64.size)),
        "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)),
        "residual_std": float(np.sqrt(np.mean((residual - np.mean(residual)) ** 2))),
        "gap_count": int(truth64.size - np.count_nonzero(finite)),
        "coverage_fraction": float(np.mean(finite)),
    }
    for quantile, value in zip(QUANTILES, np.percentile(residual, np.asarray(QUANTILES) * 100.0)):
        result[f"q{str(quantile).replace('.', '_')}"] = float(value)
    return result


def offset(layout: dict, partition: str, site: str) -> tuple[int, int, int]:
    rows = [item for item in layout["offsets"] if item["partition"] == partition and item["site"] == site]
    require(len(rows) == 1, "validation offset lookup mismatch")
    return int(rows[0]["start"]), int(rows[0]["end"]), len(rows[0]["members"])


def recompute_metrics(layout: dict, y: np.ndarray, predictions: np.ndarray, y_mean: float, y_scale: float) -> list[dict]:
    rows: list[dict] = []
    for partition in ("train", "validation"):
        pooled_truth: list[np.ndarray] = []
        pooled_pred: list[np.ndarray] = []
        pooled_daily_truth: list[np.ndarray] = []
        pooled_daily_pred: list[np.ndarray] = []
        for site in ("ABBY", "JERC"):
            start, end, members = offset(layout, partition, site)
            truth = np.asarray(y[start:end], dtype=np.float64) * y_scale + y_mean
            pred = np.asarray(predictions[start:end], dtype=np.float64)
            daily_truth = np.sum(truth.reshape(members, HOURS // 24, 24), axis=2).reshape(-1) / 24.0
            daily_pred = np.sum(pred.reshape(members, HOURS // 24, 24), axis=2).reshape(-1) / 24.0
            rows.append({"partition": partition, "site": site, "resolution": "hourly", **independent_metrics(truth, pred)})
            rows.append({"partition": partition, "site": site, "resolution": "daily", **independent_metrics(daily_truth, daily_pred)})
            pooled_truth.append(truth); pooled_pred.append(pred)
            pooled_daily_truth.append(daily_truth); pooled_daily_pred.append(daily_pred)
        rows.append({"partition": partition, "site": "pooled", "resolution": "hourly", **independent_metrics(np.concatenate(pooled_truth), np.concatenate(pooled_pred))})
        rows.append({"partition": partition, "site": "pooled", "resolution": "daily", **independent_metrics(np.concatenate(pooled_daily_truth), np.concatenate(pooled_daily_pred))})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared-directory", required=True, type=Path)
    parser.add_argument("--baseline-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output_directory.exists(), f"validation output exists: {args.output_directory}")
    args.output_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["model_config"] == MODEL_CONFIG, "validation model configuration drift")
    layout, X, y, scalers = load_prepared(args.prepared_directory)
    artifact_path = args.baseline_directory / "gpp_baseline_artifact.pkl"
    predictions_path = args.baseline_directory / "predictions_physical_float32.dat"
    metrics_path = args.baseline_directory / "metrics.csv"
    baseline_report = json.loads((args.baseline_directory / "baseline_report.json").read_text(encoding="utf-8"))
    require(sha256_file(artifact_path) == baseline_report["artifact_sha256"], "artifact hash mismatch")
    require(sha256_file(predictions_path) == baseline_report["predictions_sha256"], "prediction hash mismatch")
    require(sha256_file(metrics_path) == baseline_report["metrics_sha256"], "metric hash mismatch")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(artifact["schema"] == "three-stage-gpp-iter005-artifact-v1", "artifact schema mismatch")
    require(artifact["model_config"] == config["model_config"], "artifact model configuration mismatch")
    require(artifact["fit_scope"]["train_member_ids"] == layout["train_members"], "artifact training members mismatch")
    require(artifact["fit_scope"]["validation_member_ids"] == layout["validation_members"], "artifact validation members mismatch")
    require(artifact["fit_scope"]["fixed_test_access"] is False, "artifact fixed-test boundary mismatch")
    require(artifact["feature_names"] == layout["feature_names"], "artifact feature names mismatch")
    require(artifact["feature_schema_sha256"] == layout["feature_schema_sha256"], "artifact feature schema mismatch")
    require(np.array_equal(np.asarray(artifact["x_mean"]), scalers["x_mean"]), "artifact X means mismatch")
    require(np.array_equal(np.asarray(artifact["x_scale"]), scalers["x_scale"]), "artifact X scales mismatch")
    require(float(artifact["y_mean"]) == float(scalers["y_mean"][0]), "artifact y mean mismatch")
    require(float(artifact["y_scale"]) == float(scalers["y_scale"][0]), "artifact y scale mismatch")
    require(artifact["upstream_mode"] == "published_all819_in_sample", "artifact upstream mode mismatch")
    require(artifact["validation_label"] == "fixed_upstream_gpp_stage", "artifact validation label mismatch")
    predictions = np.memmap(predictions_path, mode="r", dtype=np.float32, shape=(layout["rows"],))
    sample = np.asarray([0, 23, 24, 719, HOURS - 1, layout["train_rows"] - 1, layout["train_rows"], layout["rows"] - 1], dtype=np.int64)
    raw = source_raw_rows(config, layout, sample)
    batch_first_predictions = {}
    batch_diagnostics = {}
    for batch_size in (1, 7, 1000):
        repeated = np.resize(raw, (batch_size, raw.shape[1]))
        inferred_first = predict_artifact(artifact, repeated)
        inferred_second = predict_artifact(artifact, repeated)
        batch_first_predictions[str(batch_size)] = float(inferred_first[0])
        batch_diagnostics[str(batch_size)] = {
            "observed_shape": list(inferred_first.shape),
            "shape_valid": bool(inferred_first.shape == (batch_size,)),
            "finite": bool(np.all(np.isfinite(inferred_first))),
            "repeatable": bool(np.array_equal(inferred_first, inferred_second)),
            "first_prediction": float(inferred_first[0]),
        }
    reloaded_prediction = predict_artifact(artifact, raw)
    direct_reload = artifact["model"].predict(X[sample]) * float(artifact["y_scale"]) + float(artifact["y_mean"])
    stored_prediction = np.asarray(predictions[sample], dtype=np.float64)
    independently_scaled = raw.astype(np.float32, copy=True)
    independently_scaled -= np.asarray(artifact["x_mean"])
    independently_scaled /= np.asarray(artifact["x_scale"])
    reload_diagnostics = {
        "schema": "three-stage-gpp-iter005-reload-diagnostic-v1",
        "sample_rows": sample.tolist(),
        "scaled_array_equal": bool(np.array_equal(independently_scaled, np.asarray(X[sample]))),
        "scaled_max_abs_difference": float(np.max(np.abs(independently_scaled.astype(np.float64) - np.asarray(X[sample], dtype=np.float64)))),
        "public_max_abs_prediction_difference": float(np.max(np.abs(reloaded_prediction - stored_prediction))),
        "direct_max_abs_prediction_difference": float(np.max(np.abs(direct_reload - stored_prediction))),
        "public_predictions": reloaded_prediction.tolist(),
        "direct_predictions": np.asarray(direct_reload, dtype=np.float64).tolist(),
        "stored_predictions": stored_prediction.tolist(),
        "flexible_batch_gate": config["flexible_batch_gate"],
        "flexible_batch_diagnostics": batch_diagnostics,
    }
    write_json(args.output_directory / "reload_diagnostics.json", reload_diagnostics)
    for batch_size, diagnostic in batch_diagnostics.items():
        require(diagnostic["shape_valid"] and diagnostic["finite"], f"batch-{batch_size} inference failed")
        require(diagnostic["repeatable"], f"batch-{batch_size} repeatability failed")
    chunk = int(config["prediction_chunk_rows"])
    replayed_rows = 0
    replay_max_abs_difference = 0.0
    replay_chunks = []
    for chunk_start in sorted(set((int(row) // chunk) * chunk for row in sample)):
        chunk_end = min(chunk_start + chunk, int(layout["rows"]))
        replay = artifact["model"].predict(X[chunk_start:chunk_end]).astype(np.float64) * float(artifact["y_scale"]) + float(artifact["y_mean"])
        stored = np.asarray(predictions[chunk_start:chunk_end], dtype=np.float64)
        difference = float(np.max(np.abs(np.asarray(replay, dtype=np.float64) - stored)))
        replayed_rows += chunk_end - chunk_start
        replay_max_abs_difference = max(replay_max_abs_difference, difference)
        replay_chunks.append({
            "start": chunk_start, "end": chunk_end, "max_abs_difference": difference,
            "passes_tolerance": bool(np.allclose(replay, stored, rtol=config["reload_rtol"], atol=config["reload_atol"])),
        })
        reload_diagnostics.update({
            "reload_equivalence_mode": config["reload_equivalence_mode"],
            "replay_chunks": replay_chunks,
            "replayed_rows": replayed_rows,
            "replay_max_abs_prediction_difference": replay_max_abs_difference,
        })
        write_json(args.output_directory / "reload_diagnostics.json", reload_diagnostics)
        require(replay_chunks[-1]["passes_tolerance"], f"chunk replay mismatch: {chunk_start}")
    batch_values = np.asarray(list(batch_first_predictions.values()), dtype=np.float64)
    reload_diagnostics.update({
        "reload_equivalence_mode": config["reload_equivalence_mode"],
        "replay_chunks": replay_chunks,
        "replayed_rows": replayed_rows,
        "replay_max_abs_prediction_difference": replay_max_abs_difference,
        "flexible_batch_gate": config["flexible_batch_gate"],
        "batch_first_predictions": batch_first_predictions,
        "cross_batch_max_abs_difference": float(np.max(batch_values) - np.min(batch_values)),
        "cross_batch_policy": config["cross_batch_policy"],
    })
    write_json(args.output_directory / "reload_diagnostics.json", reload_diagnostics)
    recomputed = recompute_metrics(layout, y, predictions, float(scalers["y_mean"][0]), float(scalers["y_scale"][0]))
    with metrics_path.open("r", encoding="utf-8", newline="") as handle:
        recorded = list(csv.DictReader(handle))
    require(len(recorded) == len(recomputed) == 12, "metric row count mismatch")
    for expected, observed in zip(recomputed, recorded):
        for key in ("partition", "site", "resolution"):
            require(str(expected[key]) == observed[key], f"metric identity mismatch: {key}")
        for key, value in expected.items():
            if key in {"partition", "site", "resolution"}:
                continue
            require(np.isclose(float(value), float(observed[key]), rtol=1e-10, atol=1e-10), f"metric mismatch: {expected['partition']}/{expected['site']}/{expected['resolution']}/{key}")
    report = {
        "schema": "three-stage-gpp-iter005-final-validation-v1", "result": "pass",
        "artifact_sha256": baseline_report["artifact_sha256"], "predictions_sha256": baseline_report["predictions_sha256"],
        "metrics_sha256": baseline_report["metrics_sha256"], "metric_rows_recomputed": len(recomputed),
        "sample_rows": sample.tolist(), "batch_sizes": [1, 7, 1000], "reload_equivalence": True,
        "reload_equivalence_mode": config["reload_equivalence_mode"],
        "replay_chunks": len(replay_chunks), "replayed_rows": replayed_rows,
        "replay_max_abs_prediction_difference": replay_max_abs_difference,
        "cross_batch_max_abs_difference": reload_diagnostics["cross_batch_max_abs_difference"],
        "fixed_test_access": False, "spinup_execution": False, "validation_label": "fixed_upstream_gpp_stage",
    }
    write_json(args.output_directory / "validation_report.json", report)
    with (args.output_directory / "recomputed_metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(recomputed, handle, indent=2, sort_keys=True); handle.write("\n")
    print("ITER005_VALIDATE_OK metric_rows=12 reload_equivalence=true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
