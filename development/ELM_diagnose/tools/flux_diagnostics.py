#!/usr/bin/env python3
"""Direct-YAML, gap-preserving diagnostics for ELM carbon-flux outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pickle
import re
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import yaml

ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import model_ELM  # noqa: F401
from model_ELM.load_obs_nc import _convert_obs_to_daily, _to_hourly, collocate_obs_to_forcing_time, load_observations_with_time_from_nc
from model_ELM.surrogate_NN_Forcing import _load_forcing_matrix


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict) or not config.get("variable") or not config.get("sites"):
        raise ValueError("configuration requires variable and nonempty sites")
    return config


def member_matrix(case: object, variable: str) -> tuple[np.ndarray, np.ndarray]:
    if variable not in case.output or "taxis" not in case.output:
        raise ValueError(f"pickle lacks output[{variable!r}] or taxis")
    taxis = np.asarray(case.output["taxis"]).reshape(-1)
    values = np.asarray(case.output[variable], dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    elif values.ndim == 2 and values.shape[0] != taxis.size and values.shape[1] == taxis.size:
        values = values.T
    if values.ndim != 2 or values.shape[0] != taxis.size:
        raise ValueError(f"{variable} shape {values.shape} is incompatible with taxis {taxis.size}")
    return values, taxis


def load_series(spec: dict, variable: str) -> tuple[np.ndarray, np.ndarray, object, list[dict]]:
    matrices, taxis_ref, first_case, sources = [], None, None, []
    for raw_path in spec["pickle_paths"]:
        path = Path(raw_path)
        if not path.is_absolute() or not path.is_file():
            raise FileNotFoundError(f"series {spec['label']}: invalid pickle path {path}")
        with path.open("rb") as handle:
            case = pickle.load(handle)
        matrix, taxis = member_matrix(case, variable)
        if taxis_ref is None:
            taxis_ref, first_case = taxis, case
        elif not np.array_equal(taxis_ref, taxis):
            raise ValueError(f"series {spec['label']}: incompatible taxis in {path}")
        matrices.append(matrix)
        sources.append({"path": str(path), "sha256": digest(path), "members": int(matrix.shape[1])})
    return np.concatenate(matrices, axis=1), taxis_ref, first_case, sources


def safe_label(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_") or "series"


def as_datetime(time_values: np.ndarray) -> np.ndarray:
    return np.asarray([datetime(value.year, value.month, value.day, value.hour) for value in time_values])


def invalid_to_nan(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float).copy()
    values[~np.isfinite(values) | (values <= -9000)] = np.nan
    return values


def series_stats(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.nanmean(matrix, axis=1), np.nanstd(matrix, axis=1)


def metrics(prediction: np.ndarray, observation: np.ndarray) -> dict:
    valid = np.isfinite(prediction) & np.isfinite(observation)
    p, o = prediction[valid], observation[valid]
    if not len(o):
        return dict(n=0, rmse=np.nan, bias=np.nan, mae=np.nan, r2=np.nan, pearson_r=np.nan, kge=np.nan)
    residual = p - o
    corr = np.corrcoef(p, o)[0, 1] if np.std(p) and np.std(o) else np.nan
    denom = np.sum((o - o.mean()) ** 2)
    r2 = 1 - np.sum(residual ** 2) / denom if denom else np.nan
    kge = np.nan
    if np.isfinite(corr) and np.std(o) and np.mean(o):
        kge = 1 - np.sqrt((corr - 1) ** 2 + (np.std(p) / np.std(o) - 1) ** 2 + (np.mean(p) / np.mean(o) - 1) ** 2)
    return dict(n=int(len(o)), rmse=float(np.sqrt(np.mean(residual ** 2))), bias=float(np.mean(residual)), mae=float(np.mean(abs(residual))), r2=float(r2), pearson_r=float(corr), kge=float(kge))


def grouped(time_values: np.ndarray, values: np.ndarray, errors: np.ndarray | None, key) -> tuple[list, np.ndarray, np.ndarray | None]:
    buckets: dict[object, list[int]] = {}
    for index, stamp in enumerate(time_values):
        buckets.setdefault(key(stamp), []).append(index)
    keys, means, propagated = sorted(buckets), [], []
    for group_key in keys:
        indices = np.asarray(buckets[group_key])
        group = values[indices]
        means.append(np.nanmean(group) if np.any(np.isfinite(group)) else np.nan)
        if errors is not None:
            err = errors[indices]
            propagated.append(np.sqrt(np.sum(err ** 2)) / len(err) if np.all(np.isfinite(err)) else np.nan)
    return keys, np.asarray(means), np.asarray(propagated) if errors is not None else None


def daily_groups(time_values: np.ndarray) -> tuple[list, list[np.ndarray]]:
    buckets: dict[tuple[int, int, int], list[int]] = {}
    for index, stamp in enumerate(time_values):
        buckets.setdefault((stamp.year, stamp.month, stamp.day), []).append(index)
    keys = sorted(buckets)
    return keys, [np.asarray(buckets[key]) for key in keys]


def complete_daily_matrix(time_values: np.ndarray, matrix: np.ndarray) -> tuple[list, np.ndarray]:
    """Vectorize complete-day means across every member in a time-by-member matrix."""
    keys, groups = daily_groups(time_values)
    daily = np.full((len(keys), matrix.shape[1]), np.nan)
    for day_index, indices in enumerate(groups):
        hours = {time_values[index].hour for index in indices}
        if len(indices) != 24 or hours != set(range(24)):
            continue
        values = matrix[indices, :]
        valid = np.all(np.isfinite(values), axis=0)
        daily[day_index, valid] = np.mean(values[:, valid], axis=0)
    return keys, daily


def complete_daily(time_values: np.ndarray, values: np.ndarray, errors: np.ndarray | None) -> tuple[list, np.ndarray, np.ndarray | None]:
    """Return complete-day scalar means and propagated observation uncertainty."""
    keys, daily = complete_daily_matrix(time_values, values[:, None])
    propagated = None
    if errors is not None:
        _, groups = daily_groups(time_values)
        propagated = np.full(len(keys), np.nan)
        for day_index, indices in enumerate(groups):
            if np.isfinite(daily[day_index, 0]) and np.all(np.isfinite(errors[indices])):
                propagated[day_index] = np.sqrt(np.sum(errors[indices] ** 2)) / len(indices)
    return keys, daily[:, 0], propagated


def plot_lines(path: Path, x: np.ndarray, series: dict, observation: np.ndarray, error: np.ndarray | None, title: str, units: str) -> None:
    figure, axis = plt.subplots(figsize=(14, 4))
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(series), 1)))
    for (label, matrix), color in zip(series.items(), colors):
        mean, spread = series_stats(matrix)
        axis.plot(x, mean, label=label, color=color, lw=0.7)
        if matrix.shape[1] > 1:
            axis.fill_between(x, mean - spread, mean + spread, color=color, alpha=0.14, label=f"{label} ±1 SD")
    axis.plot(x, observation, color="black", lw=0.8, label="obs")
    if error is not None and np.any(np.isfinite(error)):
        axis.fill_between(x, observation - error, observation + error, color="black", alpha=0.15, label="obs ±1σ")
    axis.set(title=title, ylabel=units)
    axis.legend(ncol=4, fontsize=6)
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def run_site(site: str, spec: dict, variable: str, units: str, output: Path | None) -> tuple[list[dict], list[dict], dict]:
    labels = [entry["label"] for entry in spec["series"]]
    if len(labels) != len(set(labels)) or any(entry["role"] not in {"control", "optimized"} for entry in spec["series"]):
        raise ValueError(f"{site}: series labels must be unique and roles control/optimized")
    loaded = {entry["label"]: load_series(entry, variable) for entry in spec["series"]}
    controls = [entry["label"] for entry in spec["series"] if entry["role"] == "control"]
    if len(controls) != 1:
        raise ValueError(f"{site}: exactly one control series is required")
    control_label = controls[0]
    control, taxis, control_case, control_sources = loaded[control_label]
    for label, (matrix, member_taxis, _, _) in loaded.items():
        if matrix.shape[0] != control.shape[0] or not np.array_equal(member_taxis, taxis):
            raise ValueError(f"{site}/{label}: series taxis differs from control")
    _, _, forcing_time = _load_forcing_matrix(Path(control_case.metdir), ("FSDS",), control.shape[0])
    observation_spec = spec["observation"]
    observation_path = Path(observation_spec["path"])
    if not observation_path.is_file():
        raise FileNotFoundError(f"{site}: observation path missing")
    if observation_spec.get("label") != "obs" or observation_spec.get("value_variable") != variable:
        raise ValueError(f"{site}: observation label/value_variable disagrees with configuration")
    error_name = observation_spec.get("error_variable")
    with xr.open_dataset(observation_path) as dataset:
        error_available = bool(error_name and error_name in dataset.variables)
        raw_error = None
        if error_available:
            raw_error = np.asarray(_convert_obs_to_daily(_to_hourly(dataset[error_name]).squeeze(), error_name), dtype=float).reshape(-1)
    payload = load_observations_with_time_from_nc(str(observation_path), [variable])
    observed, errors, overlap = collocate_obs_to_forcing_time(forcing_time, payload["time"], payload["obs"], payload["obs_err"], [variable])
    indices = np.asarray(overlap["forcing_overlap_indices"], dtype=int)
    time_values, x = np.asarray(forcing_time)[indices], as_datetime(np.asarray(forcing_time)[indices])
    observation = invalid_to_nan(observed[variable])
    error = None
    error_status = "missing_in_file"
    if error_available and raw_error is not None and len(raw_error) == len(payload["time"]):
        lookup = {stamp: index for index, stamp in enumerate(np.asarray(payload["time"]))}
        raw_collocated = np.asarray([raw_error[lookup[stamp]] for stamp in np.asarray(forcing_time)[indices]], dtype=float)
        error = invalid_to_nan(raw_collocated)
        error[error <= 0] = np.nan
        error_status = "available" if np.any(np.isfinite(error)) else "invalid"
    elif error_available:
        error_status = "invalid"
    aligned = {label: invalid_to_nan(matrix[indices]) for label, (matrix, _, _, _) in loaded.items()}
    for label, matrix in aligned.items():
        paired = np.isfinite(observation) & np.any(np.isfinite(matrix), axis=1)
        if not np.any(paired):
            raise ValueError(f"{site}/{label}: no paired finite hourly support")
    _, complete_observation, _ = complete_daily(time_values, observation, error)
    common_complete_day = np.isfinite(complete_observation)
    for matrix in aligned.values():
        _, daily_members = complete_daily_matrix(time_values, matrix)
        common_complete_day &= np.isfinite(series_stats(daily_members)[0])
    if not np.any(common_complete_day):
        raise ValueError(f"{site}: no complete paired UTC day across configured series")
    manifest = dict(
        observation=dict(path=str(observation_path), sha256=digest(observation_path), error_variable=error_name, error_status=error_status, valid_observations=int(np.count_nonzero(np.isfinite(observation)))),
        series={label: sources for label, (_, _, _, sources) in loaded.items()},
        time_axis=dict(length=int(len(taxis)), first=str(taxis[0]), last=str(taxis[-1])),
        overlap=overlap,
    )
    if output is None:
        return [], [], manifest
    site_output = output / site
    site_output.mkdir(parents=True, exist_ok=True)
    plot_lines(site_output / f"{site}_{variable}_hourly_timeseries.png", x, aligned, observation, error, f"{site} hourly {variable}", units)
    day_keys, daily_obs, daily_err = complete_daily(time_values, observation, error)
    daily_series = {}
    for label, matrix in aligned.items():
        _, daily_series[label] = complete_daily_matrix(time_values, matrix)
    daily_x = np.asarray([datetime(*key) for key in day_keys])
    plot_lines(site_output / f"{site}_{variable}_daily_timeseries.png", daily_x, daily_series, daily_obs, daily_err, f"{site} complete-day {variable}", units)
    for suffix, key, xlabel in [("monthly_climatology", lambda stamp: stamp.month, "month"), ("utc_diurnal", lambda stamp: stamp.hour, "UTC hour")]:
        keys, obs_mean, obs_err = grouped(time_values, observation, error, key)
        grouped_series = {label: np.column_stack([grouped(time_values, matrix[:, member], None, key)[1] for member in range(matrix.shape[1])]) for label, matrix in aligned.items()}
        plot_lines(site_output / f"{site}_{variable}_{suffix}.png", np.asarray(keys), grouped_series, obs_mean, obs_err, f"{site} {suffix.replace('_', ' ')} {variable}", units)
    figure, axis = plt.subplots(figsize=(max(8, len(aligned)), 4))
    box_data = [series_stats(matrix)[0][np.isfinite(series_stats(matrix)[0])] for matrix in aligned.values()] + [observation[np.isfinite(observation)]]
    axis.boxplot(box_data, tick_labels=[*aligned.keys(), "obs"])
    axis.tick_params(axis="x", rotation=45)
    axis.set(title=f"{site} hourly {variable} distribution", ylabel=units)
    figure.tight_layout(); figure.savefig(site_output / f"{site}_{variable}_hourly_distribution.png", dpi=150); plt.close(figure)
    series_rows, member_rows = [], []
    for entry in spec["series"]:
        label, matrix = entry["label"], aligned[entry["label"]]
        mean, _ = series_stats(matrix)
        series_rows.append(dict(site=site, role=entry["role"], label=label, **metrics(mean, observation)))
        for member in range(matrix.shape[1]):
            member_rows.append(dict(site=site, role=entry["role"], label=label, member=member, **metrics(matrix[:, member], observation)))
    manifest["figures"] = sorted(str(path) for path in site_output.glob("*.png"))
    return series_rows, member_rows, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    config = read_config(args.config)
    if args.validate_only:
        for site, spec in config["sites"].items():
            run_site(site, spec, config["variable"], config["units"], None)
        print(f"FLUX_DIAGNOSTICS_CONFIG_PASS sites={len(config['sites'])}")
        return
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite output {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = args.output.with_name(f".{args.output.name}.staging")
    if staging.exists():
        raise FileExistsError(f"staging path already exists {staging}")
    staging.mkdir()
    series_rows, member_rows, manifest_sites = [], [], {}
    for site, spec in config["sites"].items():
        print(f"FLUX_DIAGNOSTICS site={site} stage=load_validate_plot", flush=True)
        rows, members, manifest = run_site(site, spec, config["variable"], config["units"], staging)
        series_rows.extend(rows); member_rows.extend(members); manifest_sites[site] = manifest
    for name, rows in [("series_metrics.csv", series_rows), ("member_metrics.csv", member_rows)]:
        with (staging / name).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    manifest = dict(config=str(args.config), config_sha256=digest(args.config), variable=config["variable"], sites=manifest_sites)
    receipt = dict(status="pass", config_sha256=digest(args.config), variable=config["variable"], sites=manifest_sites)
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n")
    (staging / "input_receipt.json").write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    staging.rename(args.output)
    print(f"FLUX_DIAGNOSTICS_PASS sites={len(manifest_sites)} series={len(series_rows)}", flush=True)


if __name__ == "__main__":
    main()
