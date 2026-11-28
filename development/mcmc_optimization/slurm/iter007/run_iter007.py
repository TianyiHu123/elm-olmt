#!/usr/bin/env python3
"""Build and validate the ABBY/JERC observation release_0002."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from development.mcmc_optimization.slurm.iter002 import run_iter002 as old

REPO = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc")
BASE = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization")
TASK = BASE / "observation_diagnostics/gpp_qc_coverage_001"
REFERENCE = BASE / "observation_products/release_0001"
NATIVE = Path("/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4")
SITES = ("ABBY", "JERC")
DAY_UNITS = "gC/m^2/day"
NATIVE_FACTOR = 12e-6 * 86400.0
SRC_START = "2018-01-01 00:00:00"
SRC_END = "2025-01-01 00:00:00"
EXPECTED_GPP = {"ABBY": 333, "JERC": 463}
EXPECTED_SR = {"ABBY": 1083, "JERC": 2046}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return old.sha256(path)


def write_json(path: Path, obj: object) -> None:
    old.dump_json(path, obj)


def cfg_load(path: Path) -> tuple[dict, dict]:
    cfg = json.loads(path.read_text())
    require(cfg.get("schema") == "mcmc-optimization-iter007-config-v1", "Iter007 config schema")
    require(Path.cwd().resolve() == REPO, "wrong checkout")
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == cfg["repository_commit"], "HEAD drift")
    require(subprocess.check_output(["git", "branch", "--show-current"], text=True).strip() == cfg["branch"], "branch drift")
    require(sha(REPO / "development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md") == cfg["plan_sha256"], "plan drift")
    require(sha(Path(cfg["iter002_config"])) == cfg["iter002_config_sha256"], "Iter002 config drift")
    require(sha(TASK / "manifests/raw_sha256.txt") == cfg["task_a_raw_manifest_sha256"], "Task A inventory drift")
    require(sha(TASK / "manifests/results_sha256.txt") == cfg["task_a_results_manifest_sha256"], "Task A results manifest drift")
    require(sha(REFERENCE / "catalog.json") == cfg["reference_catalog_sha256"], "old catalog drift")
    require(sha(REFERENCE / "release_manifest.json") == cfg["reference_manifest_sha256"], "old manifest drift")
    require(sha(REFERENCE / "validation_report.json") == cfg["reference_validation_sha256"], "old validation drift")
    base_cfg = json.loads(Path(cfg["iter002_config"]).read_text())
    require(base_cfg["sites"] == list(SITES), "site drift")
    return cfg, base_cfg


def paths(cfg: dict) -> tuple[Path, Path, Path]:
    return Path(cfg["runtime_root"]), Path(cfg["staging_root"]), Path(cfg["publication_root"])


def size_gate(cfg: dict) -> None:
    runtime, _, release = paths(cfg)
    require(old.tree_size(runtime) <= cfg["runtime_cap_bytes"], "runtime size cap")
    require(old.tree_size(release) <= cfg["release_cap_bytes"], "release size cap")


def verify_native_inventory() -> dict:
    entries = []
    for row in (TASK / "manifests/raw_sha256.txt").read_text().splitlines():
        digest, filename = row.split("  ", 1)
        path = Path(filename)
        require(path.is_file() and sha(path) == digest, f"native source drift {path}")
        entries.append((digest, path))
    require(len(entries) == 168, "expected 84 monthly files for each of two sites")
    for site in SITES:
        names = [p for _, p in entries if p.parent.name == site]
        require(len(names) == 84, f"{site} native month count")
        require(names == [NATIVE / site / f"{site}_eval_{year:04d}-{month:02d}.nc"
                          for year in range(2018, 2025) for month in range(1, 13)], f"{site} native inventory order")
    return {"file_count": len(entries), "manifest_sha256": sha(TASK / "manifests/raw_sha256.txt")}


def audit(cfg: dict, base_cfg: dict) -> None:
    runtime, _, _ = paths(cfg)
    native = verify_native_inventory()
    task_results = []
    for line in (TASK / "manifests/results_sha256.txt").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        result_path = TASK / relative
        require(result_path.is_file() and sha(result_path) == digest, f"Task A result drift {relative}")
        task_results.append(relative)
    sources = old.verify_sources(base_cfg)
    manifest = json.loads((REFERENCE / "release_manifest.json").read_text())
    for entry in manifest["files"]:
        path = REFERENCE / entry["path"]
        require(path.stat().st_size == entry["size_bytes"] and sha(path) == entry["sha256"], f"old product drift {path}")
    coverage = pd.read_csv(REFERENCE / "diagnostics/coverage_threshold_summary.csv")
    for site in SITES:
        row = coverage[(coverage.site == site) & (coverage.variable == "SR") & (coverage.threshold == 24)]
        require(len(row) == 1 and int(row.eligible_days_after_history.iloc[0]) == EXPECTED_SR[site], f"{site} SR 24-hour count")
    frozen = {}
    frozen_counts = {}
    for site in SITES:
        with xr.open_dataset(REFERENCE / "sites" / site / "flux_hourly.nc") as ds: hourly = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "flux_daily.nc") as ds: daily = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "uncertainty.nc") as ds: uncertainty = ds.load()
        frozen[f"{site}_soil_json_sha256"] = np.asarray(sha(REFERENCE / "sites" / site / "soil_cn.json"))
        for name in uncertainty.data_vars:
            frozen[f"{site}_uncertainty_{name}"] = uncertainty[name].values
        for variable in ("GPP", "SR"):
            day = "gpp_day" if variable == "GPP" else "sr_day"
            hour = "gpp_time" if variable == "GPP" else "sr_time"
            value = "GPP_gated" if variable == "GPP" else "SR"
            prefix = f"{site}_{variable}"
            frozen[f"{prefix}_daily_eligible"] = daily[f"{variable}_eligible"].values
            frozen[f"{prefix}_daily_mean"] = daily[value].values
            frozen[f"{prefix}_daily_sigma"] = daily[f"{variable}_obs_sigma"].values
            frozen[f"{prefix}_daily_count"] = daily[f"{variable}_valid_hour_count"].values
            frozen[f"{prefix}_daily_source_index"] = daily[f"{variable}_source_hour_index"].values
            frozen[f"{prefix}_daily_day"] = daily[day].values
            frozen[f"{prefix}_hourly_valid"] = hourly[f"{variable}_valid"].values
            frozen[f"{prefix}_hourly_hours"] = hourly[hour].values
            frozen[f"{prefix}_hourly_values"] = hourly[value].values
            frozen[f"{prefix}_hourly_sigma"] = hourly[f"{variable}_obs_sigma"].values
            frozen_counts[prefix] = int(np.asarray(daily[f"{variable}_eligible"].values).sum())
    require(frozen_counts == {"ABBY_GPP":514, "ABBY_SR":1095, "JERC_GPP":699, "JERC_SR":2114}, "frozen old daily count drift")
    frozen_path = runtime / "results/frozen_release_0001.npz"
    temporary = frozen_path.with_suffix(".npz.tmp")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **frozen)
    os.replace(temporary, frozen_path)
    report = {"schema": "mcmc-iter007-source-audit-v1", "result": "pass", "native": native,
              "iter002_sources": sources, "reference_catalog_sha256": sha(REFERENCE / "catalog.json"),
              "reference_manifest_sha256": sha(REFERENCE / "release_manifest.json"),
              "task_a_validation_sha256": sha(TASK / "outputs/validation.json"),
              "task_a_results_manifest_sha256": cfg["task_a_results_manifest_sha256"],
              "task_a_verified_result_files": task_results,
              "sr_24_after_history": EXPECTED_SR, "frozen_daily_counts": frozen_counts,
              "frozen_reference_sha256": sha(frozen_path),
              "task_a_daily_sha256": {site:sha(TASK / "outputs/daily" / f"{site}_eligibility.nc") for site in SITES}}
    write_json(runtime / "results/source_audit.json", report)
    size_gate(cfg)


def native_site(site: str) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = []
    fields = {name: [] for name in ("GPP_DT", "GPP", "qfNEE", "NEE_fqc", "GPP_fqc")}
    for year in range(2018, 2025):
        for month in range(1, 13):
            path = NATIVE / site / f"{site}_eval_{year:04d}-{month:02d}.nc"
            with xr.open_dataset(path) as ds:
                require(ds.sizes.get("lat") == ds.sizes.get("lon") == 1, f"{site} native spatial schema")
                times.append(pd.DatetimeIndex(ds.time.values))
                for name in fields:
                    require(ds[name].dims == ("time", "lat", "lon"), f"{site} native {name} schema")
                    fields[name].append(np.asarray(ds[name].values[:, 0, 0], dtype=np.float64))
    index = pd.DatetimeIndex(np.concatenate([v.asi8 for v in times]).astype("datetime64[ns]"))
    grid = pd.date_range(SRC_START, SRC_END, freq="30min", inclusive="left")
    require(index.equals(grid) and len(index) == 122736, f"{site} native time grid")
    values = {name: np.concatenate(parts) for name, parts in fields.items()}
    accepted = ((values["qfNEE"] == 0) & np.isin(values["NEE_fqc"], (0, 2))
                & np.isin(values["GPP_fqc"], (0, 2)))
    dt = values["GPP_DT"]
    nt = values["GPP"]
    def aggregate(v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        good = (accepted & np.isfinite(v)).reshape(-1, 2)
        pair = v.reshape(-1, 2)
        count = good.sum(axis=1).astype(np.int8)
        out = np.full(count.size, np.nan)
        np.divide(np.where(good, pair, 0).sum(axis=1), count, out=out, where=count > 0)
        return out, count
    dt_hour, dt_count = aggregate(dt)
    nt_hour, nt_count = aggregate(nt)
    return pd.date_range(SRC_START, SRC_END, freq="h", inclusive="left"), dt_hour, nt_hour, dt_count, nt_count


def gap_lengths(valid: np.ndarray) -> np.ndarray:
    missing = ~valid
    edges = np.diff(np.r_[False, missing, False].astype(np.int8))
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    lengths = np.zeros(valid.size, dtype=np.int32)
    for start, end in zip(starts, ends):
        lengths[start:end] = end - start if start > 0 and end < valid.size and valid[start - 1] and valid[end] else 32767
    return lengths


def interpolate_eligible(values: np.ndarray, support: np.ndarray, eligible_hours: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fill only qualifying physical hours; supported input is never overwritten."""
    filled = np.asarray(eligible_hours, dtype=bool) & ~np.asarray(support, dtype=bool)
    result = np.asarray(values, dtype=np.float64).copy()
    positions = np.arange(len(result))
    if np.any(filled):
        require(np.any(support), "cannot interpolate without source support")
        require(np.all(positions[filled] > positions[support][0]) and
                np.all(positions[filled] < positions[support][-1]), "interpolation would extrapolate")
        result[filled] = np.interp(positions[filled], positions[support], result[support])
    return result, filled


def build_gpp(site: str) -> dict:
    chronology, dt, nt, dt_count, nt_count = native_site(site)
    nday = len(chronology) // 24
    require(len(chronology) == 61368 and nday * 24 == len(chronology), "physical hourly grid")
    dt_ok, nt_ok = dt_count > 0, nt_count > 0
    dt_gap, nt_gap = gap_lengths(dt_ok), gap_lengths(nt_ok)
    dt_daily = (dt_ok.reshape(nday, 24).sum(axis=1) >= 20) & (dt_gap.reshape(nday, 24).max(axis=1) <= 2)
    nt_daily = (nt_ok.reshape(nday, 24).sum(axis=1) >= 20) & (nt_gap.reshape(nday, 24).max(axis=1) <= 2)
    paired_daily = dt_daily & nt_daily
    eligible_hours = np.repeat(paired_daily, 24)
    dt, dt_fill = interpolate_eligible(dt, dt_ok, eligible_hours)
    nt, nt_fill = interpolate_eligible(nt, nt_ok, eligible_hours)
    require(np.all(np.isfinite(dt.reshape(nday, 24)[paired_daily])) and
            np.all(np.isfinite(nt.reshape(nday, 24)[paired_daily])), f"{site} unfilled eligible day")
    keep = ~((chronology.month == 2) & (chronology.day == 29))
    normalized, hours, _ = old.normalized_noleap_time(chronology.values, SRC_START)
    require(len(hours) == 61320 and np.array_equal(hours, np.arange(61320)), f"{site} canonical hours")
    retained_day = ~((chronology[::24].month == 2) & (chronology[::24].day == 29))
    pre_eligible = paired_daily[retained_day]
    require(int(pre_eligible[30:].sum()) == EXPECTED_GPP[site], f"{site} Task A paired count drift: {int(pre_eligible[30:].sum())}")
    dt, nt = dt[keep] * NATIVE_FACTOR, nt[keep] * NATIVE_FACTOR
    dt_count, nt_count = dt_count[keep], nt_count[keep]
    dt_fill, nt_fill = dt_fill[keep], nt_fill[keep]
    raw = (dt + nt) / 2
    half = (dt - nt) / 2
    valid_source = (dt_count > 0) & (nt_count > 0)
    valid = np.isfinite(raw) & (hours >= 720)
    sigma = np.maximum.reduce([np.abs(half), 0.1 * np.abs(raw), np.full(len(raw), 0.05)])
    sigma[~np.isfinite(raw)] = np.nan
    daily = old.daily_groups(hours, valid, {"GPP_raw": raw, "GPP_gated": np.maximum(raw, 0),
                                            "GPP_gate_after": np.maximum(raw, 0)}, sigma, 24)
    daily["GPP_gate_after"] = np.maximum(daily["GPP_raw"], 0)
    require(int(daily["eligible"].sum()) == EXPECTED_GPP[site], f"{site} reconstructed eligible count")
    require(np.array_equal(daily["eligible"], pre_eligible & (daily["day"] * 24 >= 720)), f"{site} eligibility changed after fill")
    return {"time": normalized, "hours": hours, "excluded": chronology[~keep], "dt": dt, "nt": nt,
            "dt_count": dt_count, "nt_count": nt_count, "dt_fill": dt_fill, "nt_fill": nt_fill,
            "raw": raw, "half": half, "gated": np.maximum(raw, 0), "sigma": sigma,
            "valid_source": valid_source, "valid": valid, "daily": daily,
            "pre_eligible": pre_eligible, "dt_support": dt_ok[keep], "nt_support": nt_ok[keep]}


def rebuild_site(cfg: dict, base_cfg: dict, site: str) -> dict:
    _, staging, _ = paths(cfg)
    # Iter002's established SR processing is reused byte-for-byte in numerical logic.
    base_copy = dict(base_cfg)
    base_copy["staging_root"] = str(staging)
    _, arrays = old.prepare_flux_site(base_copy, site)
    site_root = staging / "sites" / site
    with xr.open_dataset(site_root / "flux_hourly.nc") as ds:
        hourly = ds.load()
    with xr.open_dataset(site_root / "flux_daily.nc") as ds:
        daily = ds.load()
    g = build_gpp(site)
    for name, value in (("GPP_DT", g["dt"]), ("GPP_NT", g["nt"]), ("GPP_raw", g["raw"]),
                        ("GPP_halfdiff", g["half"]), ("GPP_gated", g["gated"]), ("GPP_obs_sigma", g["sigma"])):
        hourly[name].values[:] = value
    for name, value in (("GPP_valid_source", g["valid_source"]), ("GPP_valid", g["valid"]),
                        ("GPP_error_source", np.where(np.isfinite(g["raw"]), 1, 0))):
        hourly[name].values[:] = value.astype(np.int8)
    hourly["GPP_source_time_unix_ns"].values[:] = g["time"].asi8
    hourly["GPP_normalized_time_unix_ns"].values[:] = g["time"].asi8
    hourly["GPP_excluded_source_time_unix_ns"].values[:] = g["excluded"].asi8
    for name, value in (("GPP_DT_accepted_half_count", g["dt_count"]),
                        ("GPP_NT_accepted_half_count", g["nt_count"]),
                        ("GPP_DT_pre_fill_support", g["dt_support"]),
                        ("GPP_NT_pre_fill_support", g["nt_support"]),
                        ("GPP_DT_interpolated", g["dt_fill"]), ("GPP_NT_interpolated", g["nt_fill"])):
        hourly[name] = (("gpp_time",), np.asarray(value, dtype=np.int8))
    hourly.attrs["gpp_qc_policy"] = "q0_n02_g02"
    hourly.attrs["gpp_interpolation_policy"] = "linear_bracketed_v1"
    hourly.attrs["gpp_interpolation_chronology"] = "Gregorian physical hourly grid before leap-day exclusion"
    gd = g["daily"]
    for name, key in (("GPP_raw", "GPP_raw"), ("GPP_gated", "GPP_gated"),
                      ("GPP_gate_after_daily", "GPP_gate_after"), ("GPP_obs_sigma", "sigma"),
                      ("GPP_valid_hour_count", "count"), ("GPP_eligible", "eligible"),
                      ("GPP_source_hour_index", "hour_index")):
        daily[name].values[:] = gd[key]
    daily["GPP_pre_fill_eligible"] = (("gpp_day",), g["pre_eligible"].astype(np.int8))
    daily["GPP_DT_pre_fill_hour_count"] = (("gpp_day",), g["dt_count"].reshape(-1, 24).astype(bool).sum(axis=1).astype(np.int8))
    daily["GPP_NT_pre_fill_hour_count"] = (("gpp_day",), g["nt_count"].reshape(-1, 24).astype(bool).sum(axis=1).astype(np.int8))
    daily.attrs.update({"gpp_min_hours": 24, "sr_min_hours": 24, "gpp_pre_fill_min_hours": 20,
                        "gpp_reconstructed_hours": 24, "gpp_max_physical_gap_hours": 2,
                        "gpp_reconstruction_policy": "linear_bracketed_v1",
                        "gpp_qc_policy": "q0_n02_g02"})
    sd = old.daily_groups(arrays["sh"], arrays["svalid"], {"SR": np.asarray(hourly.SR.values)},
                          np.asarray(hourly.SR_obs_sigma.values), 24)
    require(np.array_equal(sd["day"], daily.sr_day.values), f"{site} SR day coordinate")
    for name, key in (("SR", "SR"), ("SR_obs_sigma", "sigma"), ("SR_valid_hour_count", "count"),
                      ("SR_eligible", "eligible"), ("SR_source_hour_index", "hour_index")):
        daily[name].values[:] = sd[key]
    require(int(sd["eligible"].sum()) == EXPECTED_SR[site], f"{site} SR 24-day count")
    old.write_netcdf(site_root / "flux_hourly.nc", hourly)
    old.write_netcdf(site_root / "flux_daily.nc", daily)
    shutil.copyfile(REFERENCE / "sites" / site / "soil_cn.json", site_root / "soil_cn.json")
    with xr.open_dataset(REFERENCE / "sites" / site / "uncertainty.nc") as ds:
        uncertainty = ds.load()
    uncertainty.attrs["flux_daily_approximation"] = "fixed Iter015 full-day RMSE applied to reconstructed 24-hour GPP and fully observed 24-hour SR means"
    uncertainty.attrs["inherited_numerical_product_sha256"] = sha(REFERENCE / "sites" / site / "uncertainty.nc")
    old.write_netcdf(site_root / "uncertainty.nc", uncertainty)
    qc = {"schema": "mcmc-observation-qc-v1", "site": site, "gpp_qc_policy": "q0_n02_g02",
          "gpp_pre_fill_eligible_days": int(g["pre_eligible"].sum()), "gpp_eligible_days": int(gd["eligible"].sum()),
          "sr_eligible_days": int(sd["eligible"].sum()), "gpp_dt_interpolated_hours": int(g["dt_fill"].sum()),
          "gpp_nt_interpolated_hours": int(g["nt_fill"].sum()), "sr_interpolated_hours": 0,
          "gpp_threshold": 24, "sr_threshold": 24, "gpp_pre_fill_threshold_per_method": 20,
          "gpp_max_physical_gap_hours": 2, "gpp_calendar_excluded_hours": len(g["excluded"]),
          "sr_calendar_excluded_hours": int(hourly.SR_excluded_source_time_unix_ns.size),
          "jerc_sr_fallback_only": site == "JERC"}
    write_json(site_root / "qc_report.json", qc)
    return qc


def combined_sigma(obs: np.ndarray, surrogate: float) -> np.ndarray:
    return np.sqrt(np.square(obs) + surrogate * surrogate)


def diagnostics(cfg: dict) -> None:
    _, staging, _ = paths(cfg)
    out = staging / "diagnostics"
    out.mkdir(parents=True, exist_ok=True)
    coverage_rows, gate_rows, comparison_rows, attribution_rows, membership_rows = [], [], [], [], []
    fig_cov, axes_cov = plt.subplots(2, 2, figsize=(13, 8))
    fig_gate, axes_gate = plt.subplots(2, 2, figsize=(13, 8))
    fig_unc, axes_unc = plt.subplots(2, 3, figsize=(16, 8))
    fig_cmp, axes_cmp = plt.subplots(2, 2, figsize=(13, 8))
    fig_attr, axes_attr = plt.subplots(2, 2, figsize=(13, 8))
    fig_mem, axes_mem = plt.subplots(2, 2, figsize=(13, 8))
    fig_dist, axes_dist = plt.subplots(2, 2, figsize=(13, 8))
    fig_season, axes_season = plt.subplots(2, 2, figsize=(13, 8))
    for row, site in enumerate(SITES):
        with xr.open_dataset(staging / "sites" / site / "flux_hourly.nc") as ds:
            h = ds.load()
        with xr.open_dataset(staging / "sites" / site / "flux_daily.nc") as ds:
            d = ds.load()
        with xr.open_dataset(staging / "sites" / site / "uncertainty.nc") as ds:
            u = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "flux_hourly.nc") as ds:
            oh = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "flux_daily.nc") as ds:
            od = ds.load()
        for col, variable in enumerate(("GPP", "SR")):
            day = "gpp_day" if variable == "GPP" else "sr_day"
            value = "GPP_gated" if variable == "GPP" else "SR"
            eligible = np.asarray(d[f"{variable}_eligible"].values, dtype=bool)
            old_eligible = np.asarray(od[f"{variable}_eligible"].values, dtype=bool)
            require(np.array_equal(d[day].values, od[day].values), f"{site} {variable} day-axis mismatch")
            days = np.asarray(d[day].values, dtype=np.int64)
            shared, new, excluded = eligible & old_eligible, eligible & ~old_eligible, ~eligible & old_eligible
            for kind, mask in (("shared", shared), ("new", new), ("excluded", excluded)):
                for index in np.flatnonzero(mask):
                    physical_date = pd.Timestamp(np.asarray(h.GPP_normalized_time_unix_ns.values)[int(days[index])*24], unit="ns")
                    membership_rows.append({"site": site, "variable": variable, "canonical_day": int(days[index]),
                                            "membership": kind, "new_value": float(d[value].values[index]) if eligible[index] else np.nan,
                                            "new_sigma": float(d[f"{variable}_obs_sigma"].values[index]) if eligible[index] else np.nan,
                                            "old_value": float(od[value].values[index]) if old_eligible[index] else np.nan,
                                            "old_sigma": float(od[f"{variable}_obs_sigma"].values[index]) if old_eligible[index] else np.nan,
                                            "month": physical_date.month})
            rmse = float(u[f"{variable}_surrogate_rmse"].sel(resolution="daily"))
            for index in np.flatnonzero(shared):
                old_value, new_value = float(od[value].values[index]), float(d[value].values[index])
                old_sigma, new_sigma = float(od[f"{variable}_obs_sigma"].values[index]), float(d[f"{variable}_obs_sigma"].values[index])
                comparison_rows.append({"site": site, "variable": variable, "canonical_day": int(days[index]),
                                        "old_value": old_value, "new_value": new_value, "difference": new_value-old_value,
                                        "old_obs_sigma": old_sigma, "new_obs_sigma": new_sigma,
                                        "obs_sigma_ratio": new_sigma/old_sigma,
                                        "old_combined_sigma": float(combined_sigma(old_sigma, rmse)),
                                        "new_combined_sigma": float(combined_sigma(new_sigma, rmse)),
                                        "combined_sigma_ratio": float(combined_sigma(new_sigma, rmse)/combined_sigma(old_sigma, rmse))})
                old_indices = np.asarray(od[f"{variable}_source_hour_index"].values[index], dtype=np.int64)
                old_indices = old_indices[old_indices >= 0]
                old_valid = np.asarray(oh[f"{variable}_valid"].values[old_indices], dtype=bool)
                old_hours = np.asarray(oh[f"{day[:-4]}_time"].values[old_indices[old_valid]], dtype=np.int64)
                new_hour_axis = np.asarray(h[f"{day[:-4]}_time"].values, dtype=np.int64)
                loc = np.searchsorted(new_hour_axis, old_hours)
                require(np.array_equal(new_hour_axis[loc], old_hours), f"{site} {variable} exact old hours absent")
                new_old_hours = float(np.mean(h[value].values[loc]))
                attribution_rows.append({"site": site, "variable": variable, "canonical_day": int(days[index]),
                                         "old_release_mean": old_value, "new_exact_old_hours_mean": new_old_hours,
                                         "new_full_24_mean": new_value, "source_processing_delta": new_old_hours-old_value,
                                         "coverage_delta": new_value-new_old_hours, "total_delta": new_value-old_value,
                                         "old_retained_hours": int(len(old_hours))})
                if variable == "SR":
                    require(np.isclose(new_old_hours, old_value, rtol=0, atol=1e-12)
                            and np.isclose(new_value, old_value, rtol=0, atol=1e-12)
                            and np.isclose(new_sigma, old_sigma, rtol=0, atol=1e-12), f"{site} SR shared-date mismatch")
            coverage_rows.append({"site": site, "variable": variable, "old_days": int(old_eligible.sum()),
                                  "new_days": int(eligible.sum()), "shared": int(shared.sum()),
                                  "new_only": int(new.sum()), "excluded": int(excluded.sum())})
            axes_cov[row, col].plot(days, old_eligible.astype(int), lw=.6, label="release_0001")
            axes_cov[row, col].plot(days, eligible.astype(int), lw=.6, label="release_0002")
            axes_cov[row, col].set(title=f"{site} {variable} daily coverage", xlabel="canonical day", ylabel="eligible")
            axes_cmp[row, col].scatter([r["old_value"] for r in comparison_rows if r["site"] == site and r["variable"] == variable],
                                      [r["new_value"] for r in comparison_rows if r["site"] == site and r["variable"] == variable], s=5)
            axes_cmp[row, col].set(title=f"{site} {variable} shared-date means", xlabel="old gC m^-2 day^-1", ylabel="new gC m^-2 day^-1")
            subset_attr = [r for r in attribution_rows if r["site"] == site and r["variable"] == variable]
            axes_attr[row, col].scatter([r["source_processing_delta"] for r in subset_attr],
                                        [r["coverage_delta"] for r in subset_attr], s=5)
            axes_attr[row, col].axhline(0, color="grey", lw=.5)
            axes_attr[row, col].axvline(0, color="grey", lw=.5)
            axes_attr[row, col].set(title=f"{site} {variable} shared-date attribution",
                                     xlabel="source processing delta, gC m^-2 day^-1",
                                     ylabel="coverage delta, gC m^-2 day^-1")
            axes_mem[row, col].bar(("shared", "new", "excluded"), (int(shared.sum()), int(new.sum()), int(excluded.sum())))
            axes_mem[row, col].set(title=f"{site} {variable} date membership", ylabel="days")
        raw = np.asarray(d.GPP_raw.values)
        gated = np.asarray(d.GPP_gated.values)
        for index in np.flatnonzero(d.GPP_eligible.values):
            gate_rows.append({"site": site, "canonical_day": int(d.gpp_day.values[index]),
                              "mean_raw": float(raw[index]), "hourly_gate_then_mean": float(gated[index]),
                              "mean_then_gate": float(d.GPP_gate_after_daily.values[index]),
                              "impact": float(gated[index] - max(0, raw[index]))})
        axes_gate[row, 0].scatter(raw[np.isfinite(raw)], gated[np.isfinite(raw)], s=5)
        axes_gate[row, 0].set(title=f"{site} hourly gate then mean", xlabel="raw daily mean", ylabel="gated daily mean")
        axes_gate[row, 1].hist([r["impact"] for r in gate_rows if r["site"] == site], bins=25)
        axes_gate[row, 1].set(title=f"{site} gate impact", xlabel="gC m^-2 day^-1")
        cv_index = int(np.flatnonzero(np.isclose(u.cv.values, .3))[0])
        flux_obs = [float(np.nanmedian(d.GPP_obs_sigma.values)), float(np.nanmedian(d.SR_obs_sigma.values))]
        gpp_sur = float(u.GPP_surrogate_rmse.sel(resolution="daily"))
        sr_sur = float(u.SR_surrogate_rmse.sel(resolution="daily"))
        axes_unc[row, 0].bar(("GPP obs", "GPP sur", "SR obs", "SR sur"),
                             (flux_obs[0], gpp_sur, flux_obs[1], sr_sur))
        axes_unc[row, 0].tick_params(axis="x", rotation=35)
        axes_unc[row, 0].set(title=f"{site} daily flux uncertainty", ylabel="gC m^-2 day^-1")
        obs_cov = np.asarray(u.observation_log_covariance.values[cv_index], dtype=np.float64)
        sur_cov = np.asarray(u.surrogate_log_covariance.values, dtype=np.float64)
        depth_cov = np.asarray(u.depth_log_covariance.values, dtype=np.float64)
        total_cov = np.asarray(u.total_log_covariance.values[cv_index], dtype=np.float64)
        image = axes_unc[row, 1].imshow(np.block([[sur_cov, depth_cov], [obs_cov, total_cov]]), cmap="viridis")
        axes_unc[row, 1].set(title=f"{site} C/N: surrogate | depth / observation | total",
                             xticks=(.5, 2.5), yticks=(.5, 2.5), xticklabels=("sur", "depth"),
                             yticklabels=("sur/depth", "obs/total"))
        fig_unc.colorbar(image, ax=axes_unc[row, 1])
        axes_unc[row, 2].bar(("obs C", "obs N", "sur C", "sur N", "depth C", "depth N", "total C", "total N"),
                             np.r_[np.diag(obs_cov), np.diag(sur_cov), np.diag(depth_cov), np.diag(total_cov)])
        axes_unc[row, 2].tick_params(axis="x", rotation=45)
        axes_unc[row, 2].set(title=f"{site} C/N variance, CV 0.30", ylabel="log variance")
    pd.DataFrame(coverage_rows).to_csv(out / "observation_coverage.csv", index=False)
    pd.DataFrame([{"site": r["site"], "variable": r["variable"], "threshold": 24,
                   "eligible_days_after_history": r["new_days"]} for r in coverage_rows]).to_csv(
                       out / "coverage_threshold_summary.csv", index=False)
    pd.DataFrame(gate_rows).to_csv(out / "gpp_zero_gate_impact.csv", index=False)
    pd.DataFrame(comparison_rows).to_csv(out / "release_comparison_shared_dates.csv", index=False)
    pd.DataFrame(attribution_rows).to_csv(out / "release_comparison_attribution.csv", index=False)
    members = pd.DataFrame(membership_rows)
    members["season"] = members.month.map({12:"DJF",1:"DJF",2:"DJF",3:"MAM",4:"MAM",5:"MAM",6:"JJA",7:"JJA",8:"JJA",9:"SON",10:"SON",11:"SON"})
    members.to_csv(out / "release_comparison_membership.csv", index=False)
    for row, site in enumerate(SITES):
        for col, variable in enumerate(("GPP", "SR")):
            subset = members[(members.site == site) & (members.variable == variable)]
            categories = ("shared", "new", "excluded")
            sigmas = [subset.loc[subset.membership == category,
                                 "old_sigma" if category == "excluded" else "new_sigma"].dropna().to_numpy()
                      for category in categories]
            axes_dist[row, col].boxplot(sigmas, tick_labels=categories, showfliers=False)
            axes_dist[row, col].set(title=f"{site} {variable} daily observation sigma by date class",
                                     ylabel="gC m^-2 day^-1")
            bottoms = np.zeros(4)
            for category in categories:
                values = np.asarray([((subset.season == season) & (subset.membership == category)).sum()
                                     for season in ("DJF", "MAM", "JJA", "SON")], dtype=int)
                axes_season[row, col].bar(("DJF", "MAM", "JJA", "SON"), values, bottom=bottoms, label=category)
                bottoms += values
            axes_season[row, col].set(title=f"{site} {variable} dates by season and class", ylabel="days")
            axes_season[row, col].legend(fontsize=7)
    members.groupby(["site", "variable", "membership", "season"], dropna=False).agg(
        days=("canonical_day", "size"), median_new_sigma=("new_sigma", "median"),
        median_old_sigma=("old_sigma", "median")).reset_index().to_csv(out / "release_comparison_seasonal.csv", index=False)
    uncertainty_audit = json.loads((REFERENCE / "diagnostics/uncertainty_audit.json").read_text())
    uncertainty_audit["schema"] = "mcmc-iter007-uncertainty-audit-v1"
    uncertainty_audit["inherited_from_release"] = "release_0001"
    uncertainty_audit["inheritance"] = "all numerical uncertainty arrays identical; flux daily description updated for full 24-hour means"
    write_json(out / "uncertainty_audit.json", uncertainty_audit)
    for fig, name in ((fig_cov,"flux_coverage_alignment.png"), (fig_gate,"gpp_zero_gate_impact.png"),
                      (fig_unc,"uncertainty_components.png"), (fig_cmp,"release_comparison_shared_dates.png"),
                      (fig_attr,"release_comparison_attribution.png"), (fig_mem,"release_comparison_membership.png"),
                      (fig_dist,"release_comparison_uncertainty.png"), (fig_season,"release_comparison_seasonal.png")):
        fig.tight_layout(); fig.savefig(out / name, dpi=160); plt.close(fig)


def rebuild(cfg: dict, base_cfg: dict) -> None:
    runtime, staging, _ = paths(cfg)
    require((runtime / "results/source_audit.json").is_file(), "source audit missing")
    results = {site: rebuild_site(cfg, base_cfg, site) for site in SITES}
    diagnostics(cfg)
    write_json(runtime / "results/rebuild.json", {"schema":"mcmc-iter007-rebuild-v1", "result":"pass", "sites":results})
    size_gate(cfg)


def validate(cfg: dict, root: Path) -> dict:
    from model_ELM.mcmc_three_stage_observations import _daily_operator
    runtime, _, _ = paths(cfg)
    source_audit = json.loads((runtime / "results/source_audit.json").read_text())
    required = ("flux_coverage_alignment.png", "gpp_zero_gate_impact.png", "uncertainty_components.png",
                "release_comparison_shared_dates.png", "release_comparison_attribution.png", "release_comparison_membership.png",
                "release_comparison_uncertainty.png", "release_comparison_seasonal.png",
                "release_comparison_shared_dates.csv", "release_comparison_attribution.csv", "release_comparison_membership.csv",
                "release_comparison_seasonal.csv")
    for name in required:
        require((root / "diagnostics" / name).stat().st_size > 0, f"missing diagnostic {name}")
    checks = {}
    for site in SITES:
        require(sha(TASK / "outputs/daily" / f"{site}_eligibility.nc") ==
                source_audit["task_a_daily_sha256"][site], f"{site} Task A daily identity drift")
        site_root = root / "sites" / site
        require(sha(site_root / "soil_cn.json") == sha(REFERENCE / "sites" / site / "soil_cn.json"), f"{site} soil byte drift")
        with xr.open_dataset(site_root / "uncertainty.nc") as ds: new_u = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "uncertainty.nc") as ds: old_u = ds.load()
        for name in old_u.data_vars:
            require(np.array_equal(new_u[name].values, old_u[name].values), f"{site} fixed array drift {name}")
        with xr.open_dataset(site_root / "flux_hourly.nc") as ds: h = ds.load()
        with xr.open_dataset(site_root / "flux_daily.nc") as ds: d = ds.load()
        with xr.open_dataset(REFERENCE / "sites" / site / "flux_daily.nc") as ds: old_d = ds.load()
        qc = json.loads((site_root / "qc_report.json").read_text())
        for count_name, mask_name in (("gpp_pre_fill_eligible_days", "GPP_pre_fill_eligible"),
                                      ("gpp_eligible_days", "GPP_eligible"),
                                      ("sr_eligible_days", "SR_eligible")):
            require(qc[count_name] == int(np.asarray(d[mask_name].values, dtype=bool).sum()),
                    f"{site} QC count mismatch {count_name}")
        with xr.open_dataset(TASK / "outputs/daily" / f"{site}_eligibility.nc") as ds: task_daily = ds.load()
        with xr.open_dataset(TASK / "outputs/masks" / f"{site}_hourly_support.nc") as ds: task_hourly = ds.load()
        task_noleap = np.asarray(task_daily.noleap_day.values, dtype=bool)
        task_dates = pd.DatetimeIndex(task_daily.day.values)[task_noleap]
        product_dates = pd.DatetimeIndex(np.asarray(h.GPP_normalized_time_unix_ns.values[::24], dtype=np.int64).astype("datetime64[ns]"))
        require(task_dates.equals(product_dates), f"{site} Task A physical day alignment")
        task_eligible = np.asarray(task_daily.eligible.sel({"policy": "q0_n02_g02", "minimum_hours": 20,
                                                            "maximum_gap_hours": 2, "method": "paired"}).values, dtype=bool)[task_noleap]
        task_history = np.asarray(task_daily.mcmc_history_eligible_day.values, dtype=bool)[task_noleap]
        require(np.array_equal(np.asarray(d.GPP_pre_fill_eligible.values, dtype=bool), task_eligible), f"{site} Task A pre-fill daily mask mismatch")
        require(np.array_equal(np.asarray(d.GPP_eligible.values, dtype=bool), task_eligible & task_history), f"{site} Task A release daily mask mismatch")
        for method in ("DT", "NT"):
            task_count = np.asarray(task_daily[f"{method}_available_hours"].sel(policy="q0_n02_g02").values, dtype=np.int64)[task_noleap]
            task_gap = np.asarray(task_daily[f"{method}_max_physical_missing_run_hours"].sel(policy="q0_n02_g02").values, dtype=np.int64)[task_noleap]
            require(np.array_equal(d[f"GPP_{method}_pre_fill_hour_count"].values, task_count), f"{site} {method} Task A support count")
            physical_eligible = (task_count >= 20) & (task_gap <= 2)
            method_mask = np.asarray(task_daily.eligible.sel({"policy": "q0_n02_g02", "minimum_hours": 20,
                                                              "maximum_gap_hours": 2, "method": method}).values, dtype=bool)[task_noleap]
            require(np.array_equal(physical_eligible, method_mask), f"{site} {method} Task A physical eligibility")
            task_half = np.asarray(task_hourly[f"{method}_half_count"].sel(policy="q0_n02_g02").values, dtype=np.int64)
            task_estimate = np.asarray(task_hourly[f"{method}_estimate_native"].sel(policy="q0_n02_g02").values, dtype=np.float64)
            physical_hours = pd.date_range(SRC_START, SRC_END, freq="h", inclusive="left")
            noleap_hours = ~((physical_hours.month == 2) & (physical_hours.day == 29))
            require(np.array_equal(h[f"GPP_{method}_accepted_half_count"].values, task_half[noleap_hours]), f"{site} {method} Task A hourly halves")
            supported = task_half[noleap_hours] > 0
            np.testing.assert_allclose(h[f"GPP_{method}"].values[supported],
                                       task_estimate[noleap_hours][supported] * NATIVE_FACTOR,
                                       rtol=0, atol=1e-12)
        require(d.attrs["gpp_reconstruction_policy"] == "linear_bracketed_v1", "GPP policy metadata")
        require(int(d.attrs["gpp_pre_fill_min_hours"]) == 20 and int(d.attrs["gpp_min_hours"]) == 24 and int(d.attrs["sr_min_hours"]) == 24, "coverage metadata")
        require(np.array_equal(d.GPP_eligible.values, d.GPP_pre_fill_eligible.values * (d.gpp_day.values >= 30)), "pre-fill eligibility drift")
        for variable, expected in (("GPP", EXPECTED_GPP[site]), ("SR", EXPECTED_SR[site])):
            operator = _daily_operator(h, d, variable, float(new_u[f"{variable}_surrogate_rmse"].sel(resolution="daily")), 24)
            require(operator.count == expected and all(len(group) == 24 and len(np.unique(group)) == 24 for group in operator.forcing_hour_groups), f"{site} {variable} 24-hour reconstruction")
            checks[f"{site}_{variable}"] = expected
        shared_sr = (np.asarray(d.SR_eligible.values, dtype=bool)
                     & np.asarray(old_d.SR_eligible.values, dtype=bool))
        require(np.array_equal(d.sr_day.values, old_d.sr_day.values), f"{site} SR day axis drift")
        np.testing.assert_allclose(d.SR.values[shared_sr], old_d.SR.values[shared_sr], rtol=0, atol=1e-12)
        np.testing.assert_allclose(d.SR_obs_sigma.values[shared_sr], old_d.SR_obs_sigma.values[shared_sr], rtol=0, atol=1e-12)
        np.testing.assert_allclose(h.GPP_raw.values, (h.GPP_DT.values+h.GPP_NT.values)/2, rtol=0, atol=1e-12, equal_nan=True)
        np.testing.assert_allclose(h.GPP_halfdiff.values, (h.GPP_DT.values-h.GPP_NT.values)/2, rtol=0, atol=1e-12, equal_nan=True)
        np.testing.assert_allclose(h.GPP_gated.values, np.maximum(h.GPP_raw.values, 0), rtol=0, atol=1e-12, equal_nan=True)
        expected_sigma = np.maximum.reduce([np.abs(h.GPP_halfdiff.values), .1*np.abs(h.GPP_raw.values), np.full(h.sizes["gpp_time"], .05)])
        np.testing.assert_allclose(h.GPP_obs_sigma.values, expected_sigma, rtol=0, atol=1e-12, equal_nan=True)
    return {"schema":"mcmc-iter007-staged-validation-v1", "result":"pass", "daily_counts":checks,
            "required_diagnostics":list(required)}


def publish(cfg: dict, config_path: Path) -> None:
    runtime, staging, destination = paths(cfg)
    require(not destination.exists(), "publication root already exists")
    staged_report = runtime / "results/staged_validation.json"
    require(staged_report.is_file() and json.loads(staged_report.read_text()).get("result") == "pass",
            "reviewable staged validation missing")
    review_path = runtime / "reviews/staged_review.json"
    require(review_path.is_file() and json.loads(review_path.read_text()).get("outcome") == "pass",
            "independent staged result review missing")
    result = validate(cfg, staging)
    result["validated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(staging / "validation_report.json", result)
    base_cfg = json.loads(Path(cfg["iter002_config"]).read_text())
    source_ids = {}
    for name, _, digest in old.iter_sources(base_cfg):
        label = f"{name}_processed_reference" if name.endswith("_gpp") else name
        source_ids[label] = digest
    source_ids["native_gpp_168_file_manifest"] = cfg["task_a_raw_manifest_sha256"]
    source_ids["inherited_observation_reference_manifest"] = cfg["reference_manifest_sha256"]
    manifest = {"schema":"mcmc-observation-release-manifest-v1", "release":"release_0002", "result":"validated",
                "sites":list(SITES), "plan_sha256":cfg["plan_sha256"], "repository_commit":cfg["repository_commit"],
                "config_sha256":sha(config_path), "source_identities":source_ids, "iter015_fixed_test_access":False,
                "catalog_last":True, "files":old.file_manifest(staging, {"release_manifest.json", "catalog.json"})}
    write_json(staging / "release_manifest.json", manifest)
    temporary = destination.parent / f".{destination.name}.iter007_tmp_{os.getpid()}"
    require(not temporary.exists(), "publication temporary root exists")
    shutil.copytree(staging, temporary)
    require(sha(temporary / "release_manifest.json") == sha(staging / "release_manifest.json"), "staging copy mismatch")
    validate(cfg, temporary)
    os.replace(temporary, destination)
    catalog = {"schema":"mcmc-observation-release-catalog-v1", "current_release":"release_0002",
               "release_path":str(destination), "release_manifest_sha256":sha(destination / "release_manifest.json"),
               "published_at_utc":datetime.now(timezone.utc).isoformat(), "decision":"observation_release_0002_published"}
    write_json(destination / "catalog.json", catalog)
    write_json(runtime / "results/publication.json", {"schema":"mcmc-iter007-publication-v1", "result":"pass",
                                                   "catalog_sha256":sha(destination / "catalog.json"),
                                                   "manifest_sha256":sha(destination / "release_manifest.json")})
    size_gate(cfg)


def final_reload(cfg: dict) -> None:
    runtime, _, destination = paths(cfg)
    require(destination.is_dir(), "published release missing")
    manifest = json.loads((destination / "release_manifest.json").read_text())
    require(json.loads((destination / "catalog.json").read_text())["release_manifest_sha256"] == sha(destination / "release_manifest.json"), "catalog manifest mismatch")
    for item in manifest["files"]:
        path = destination / item["path"]
        require(path.is_file() and path.stat().st_size == item["size_bytes"] and sha(path) == item["sha256"], f"published hash mismatch {path}")
    result = validate(cfg, destination)
    write_json(runtime / "results/final_reload.json", {"schema":"mcmc-iter007-final-reload-v1", "result":"pass",
                                                   "catalog_sha256":sha(destination / "catalog.json"),
                                                   "manifest_sha256":sha(destination / "release_manifest.json"), "validation":result})
    size_gate(cfg)


def preflight(cfg: dict, base_cfg: dict) -> None:
    runtime, _, destination = paths(cfg)
    require(not destination.exists(), "publication root exists at preflight")
    require(sha(Path(base_cfg["sources"]["forcing_snapshot"]["path"])) == base_cfg["sources"]["forcing_snapshot"]["sha256"], "forcing snapshot drift")
    require(sha(TASK / "outputs/validation.json") == cfg["task_a_validation_sha256"], "Task A validation drift")
    require(json.loads((TASK / "outputs/validation.json").read_text())["result"] == "pass", "Task A validation failed")
    write_json(runtime / "results/preflight.json", {"schema":"mcmc-iter007-preflight-v1", "result":"pass"})
    size_gate(cfg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--step", required=True, choices=("preflight","source-audit","rebuild","staged-validate","publish","final-reload"))
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    cfg, base_cfg = cfg_load(config_path)
    runtime, staging, _ = paths(cfg)
    if args.step == "preflight": preflight(cfg, base_cfg)
    elif args.step == "source-audit": audit(cfg, base_cfg)
    elif args.step == "rebuild": rebuild(cfg, base_cfg)
    elif args.step == "staged-validate": write_json(runtime / "results/staged_validation.json", validate(cfg, staging))
    elif args.step == "publish": publish(cfg, config_path)
    else: final_reload(cfg)
    print(f"MCMC_ITER007_{args.step.upper().replace('-', '_')}_PASS")


if __name__ == "__main__": main()
