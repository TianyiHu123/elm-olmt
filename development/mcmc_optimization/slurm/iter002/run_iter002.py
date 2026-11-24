#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from model_ELM.load_obs_nc import load_observations_strict_from_nc


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def tree_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file()) if path.exists() else 0


def enforce_storage(cfg: dict[str, Any]) -> int:
    used = tree_size(Path(cfg["runtime_root"])) + tree_size(Path(cfg["publication_root"]))
    require(used <= int(cfg["storage_cap_bytes"]), f"Iter002 storage cap exceeded: {used}")
    return used


def load_config(path: str) -> tuple[dict[str, Any], Path]:
    config_path = Path(path).resolve()
    cfg = json.loads(config_path.read_text())
    require(cfg["schema"] == "mcmc-optimization-iter002-config-v1", "wrong config schema")
    return cfg, config_path


def verify_identity(cfg: dict[str, Any], config_path: Path) -> None:
    root = Path(cfg["repository_root"]).resolve()
    require(Path.cwd().resolve() == root, f"wrong repository root: {Path.cwd().resolve()}")
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    require(branch == cfg["branch"], f"wrong branch: {branch}")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    require(head == cfg["repository_commit"], f"wrong repository commit: {head}")
    plan = root / "development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md"
    require(sha256(plan) == cfg["plan_sha256"], "campaign plan hash mismatch")
    require(config_path.is_file(), "config missing")


def iter_sources(cfg: dict[str, Any]):
    for name, item in cfg["sources"].items():
        yield name, Path(item["path"]), item["sha256"]
    for site, items in cfg["site_sources"].items():
        for name, pair in items.items():
            yield f"{site}_{name}", Path(pair[0]), pair[1]


def verify_sources(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, path, expected in iter_sources(cfg):
        require(path.is_file(), f"missing source {name}: {path}")
        actual = sha256(path)
        require(actual == expected, f"source hash mismatch for {name}: {actual}")
        rows.append({"name": name, "path": str(path), "sha256": actual, "size_bytes": path.stat().st_size})
    return rows


def verify_iter015_products(cfg: dict[str, Any]) -> dict[str, str]:
    handoff_manifest = json.loads(Path(cfg["sources"]["uncertainty_manifest"]["path"]).read_text())
    expected = handoff_manifest["files"]
    required = ("metric_summary.csv", "cn_member_balanced_summary.csv", "cn_member_balanced_covariance.csv")
    verified = {}
    for name in required:
        require(name in expected, f"Iter015 manifest lacks {name}")
        path = Path(cfg["iter015_products_root"]) / name
        require(path.is_file(), f"Iter015 product missing: {path}")
        actual = sha256(path)
        require(actual == expected[name]["sha256"], f"Iter015 product hash mismatch: {name}")
        require(path.stat().st_size == expected[name]["size_bytes"], f"Iter015 product size mismatch: {name}")
        verified[name] = actual
    return verified


def normalized_noleap_time(values: np.ndarray, origin_text: str) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray]:
    source = pd.DatetimeIndex(pd.to_datetime(values))
    normalized = source.floor("h")
    require(normalized.is_monotonic_increasing, "timestamps are not sorted")
    require(not normalized.has_duplicates, "normalized timestamps contain duplicates")
    keep = ~((normalized.month == 2) & (normalized.day == 29))
    normalized = normalized[keep]
    origin = pd.Timestamp(origin_text)
    hours = ((normalized - origin) / pd.Timedelta(hours=1)).astype(np.int64).to_numpy()
    for year in range(origin.year, int(normalized.year.max()) + 1):
        if pd.Timestamp(year=year, month=1, day=1).is_leap_year:
            hours -= 24 * (normalized >= pd.Timestamp(year=year, month=3, day=1)).astype(np.int64)
    require(np.unique(hours).size == hours.size, "noleap timestamps are not unique")
    require(np.all(np.diff(hours) > 0), "noleap timestamps are not increasing")
    return normalized, hours, np.asarray(keep)


def daily_groups(time_hour: np.ndarray, valid: np.ndarray, values: dict[str, np.ndarray], sigma: np.ndarray, threshold: int) -> dict[str, Any]:
    days = np.unique(time_hour // 24)
    indices = np.full((days.size, 24), -1, dtype=np.int64)
    count = np.zeros(days.size, dtype=np.int16)
    result = {name: np.full(days.size, np.nan, dtype=np.float64) for name in values}
    daily_sigma = np.full(days.size, np.nan, dtype=np.float64)
    for row, day in enumerate(days):
        loc = np.flatnonzero(time_hour // 24 == day)
        slots = time_hour[loc] % 24
        require(np.unique(slots).size == slots.size, f"duplicate hourly slots on noleap day {day}")
        indices[row, slots] = loc
        use = loc[valid[loc]]
        count[row] = use.size
        if use.size >= threshold:
            for name, array in values.items():
                result[name][row] = float(np.mean(array[use]))
            daily_sigma[row] = float(np.sqrt(np.mean(np.square(sigma[use]))))
    return {"day": days, "hour_index": indices, "count": count, "eligible": count >= threshold,
            "sigma": daily_sigma, **result}


def source_coverage(time_hour: np.ndarray, valid: np.ndarray) -> dict[str, int]:
    counts = []
    for day in np.unique(time_hour // 24):
        loc = time_hour // 24 == day
        counts.append(int(np.count_nonzero(valid[loc])))
    return {str(level): int(np.count_nonzero(np.asarray(counts) >= level)) for level in (18, 20, 22, 24)}


def validate_annual_stats(gpp_path: Path, annual_path: Path) -> int:
    with xr.open_dataset(gpp_path) as opened:
        ds = opened.load()
    time = pd.DatetimeIndex(pd.to_datetime(ds.time.values))
    published = pd.read_csv(annual_path)
    checked = 0
    for var, partition in (("GPP_DT", "DT"), ("GPP_NT", "NT")):
        values = np.asarray(ds[var].values, dtype=np.float64) * 86400.0
        frame = pd.DataFrame({"time": time, "value": values}).set_index("time")
        daily = frame["value"].resample("1D").agg(["mean", "count"])
        daily.loc[daily["count"] < 18, "mean"] = np.nan
        for year, group in daily.groupby(daily.index.year):
            values_y = group["mean"].dropna().to_numpy()
            row = published[(published.year == year) & (published.variable == "GPP") & (published.partition == partition)]
            require(len(row) == 1, f"missing annual GPP row for {year} {partition}")
            expected_n = int(row.iloc[0]["n_valid_days"])
            require(values_y.size == expected_n, f"annual valid-day mismatch for {year} {partition}")
            if values_y.size:
                stats = {"mean": np.mean(values_y), "median": np.median(values_y), "min": np.min(values_y),
                         "max": np.max(values_y), **{f"q{int(q*100):02d}": np.quantile(values_y, q) for q in (.05, .25, .50, .75, .95)}}
                for name, value in stats.items():
                    require(np.isclose(value, float(row.iloc[0][name]), rtol=1e-12, atol=1e-12),
                            f"annual statistic mismatch {year} {partition} {name}")
            checked += 1
    return checked


def source_audit(cfg: dict[str, Any]) -> dict[str, Any]:
    sources = verify_sources(cfg)
    iter015_products = verify_iter015_products(cfg)
    forcing = json.loads(Path(cfg["sources"]["forcing_snapshot"]["path"]).read_text())
    require(forcing["hour_count_by_site"] == {site: 61320 for site in cfg["sites"]}, "forcing hour-count mismatch")
    coverage = {}
    annual_rows = 0
    for site in cfg["sites"]:
        item = cfg["site_sources"][site]
        with xr.open_dataset(item["gpp"][0]) as opened:
            gpp = opened.load()
        require(set(("GPP_DT", "GPP_NT", "time")).issubset(gpp.variables), f"{site} GPP schema")
        require(gpp.GPP_DT.attrs.get("units") == "gC/m^2/s", f"{site} GPP units")
        require(gpp.GPP_NT.attrs.get("units") == "gC/m^2/s", f"{site} GPP_NT units")
        require(gpp.GPP_DT.dims == ("time",) and gpp.GPP_NT.dims == ("time",), f"{site} GPP dimensions")
        source_time = pd.DatetimeIndex(pd.to_datetime(gpp.time.values))
        require(np.all(source_time.minute == 15), f"{site} GPP timestamps are not HH:15")
        _, g_hours, keep = normalized_noleap_time(gpp.time.values, cfg["canonical_origin"])
        paired = np.isfinite(gpp.GPP_DT.values[keep]) & np.isfinite(gpp.GPP_NT.values[keep])
        coverage.setdefault(site, {})["GPP"] = source_coverage(g_hours, paired)
        annual_rows += validate_annual_stats(Path(item["gpp"][0]), Path(item["annual"][0]))
        strict_gpp = load_observations_strict_from_nc(
            item["gpp"][0], ["GPP_DT", "GPP_NT"], target_calendar="noleap", floor_to_hour=True
        )
        require(len(strict_gpp["time"]) == 61320, f"{site} strict GPP noleap length")

        with xr.open_dataset(item["sr"][0]) as opened:
            sr = opened.load()
        require("SR" in sr and sr.SR.attrs.get("units") == "gC/m^2/s", f"{site} SR schema/units")
        require(sr.SR.dims == ("time",), f"{site} SR dimensions")
        require(("SR_err" in sr) == (site == "ABBY"), f"{site} SR_err availability mismatch")
        if "SR_err" in sr:
            require(sr.SR_err.attrs.get("units") == "gC/m^2/s" and sr.SR_err.dims == ("time",), f"{site} SR_err schema/units")
        strict_sr = load_observations_strict_from_nc(
            item["sr"][0], ["SR"], {"SR": "SR_err"}, error_fallback="relative_10_percent",
            absolute_floor=cfg["sr_absolute_floor"], target_calendar="noleap", floor_to_hour=True
        )
        _, sr_hours, sr_keep = normalized_noleap_time(sr.time.values, cfg["canonical_origin"])
        require(len(strict_sr["time"]) == len(sr_hours), f"{site} strict SR noleap length")
        coverage[site]["SR"] = source_coverage(sr_hours, np.isfinite(sr.SR.values[sr_keep]))
        expected_coverage = cfg["expected_source_coverage_noleap"][site]
        require(
            coverage[site] == expected_coverage,
            f"{site} coverage drift: observed={coverage[site]!r}, expected={expected_coverage!r}",
        )

    soil = pd.read_csv(cfg["sources"]["soil_csv"]["path"])
    require(list(soil.columns) == ["siteID", "totalSoilC_gC_m2", "totalSoilN_gN_m2", "CN_ratio", "effectiveDepth_m"], "soil CSV schema")
    for site in cfg["sites"]:
        row = soil[soil.siteID == site]
        require(len(row) == 1, f"soil row count for {site}")
        require(float(row.totalSoilC_gC_m2.iloc[0]) > 0 and float(row.totalSoilN_gN_m2.iloc[0]) > 0, f"nonpositive soil stock {site}")
        require(float(row.effectiveDepth_m.iloc[0]) == 2.0, f"unexpected soil depth {site}")

    report = {
        "schema": "mcmc-iter002-source-audit-v1", "result": "pass", "sources": sources,
        "coverage_noleap_before_history": coverage, "annual_gpp_rows_recomputed": annual_rows,
        "iter015_products": iter015_products, "forcing_hour_count_by_site": forcing["hour_count_by_site"],
        "gpp_qc": "NEE qfNEE==0 and NEE_fqc==0; GPP additionally GPP_fqc==0; lenient 30min-to-hourly mean",
        "remaining_uncertainties": [
            "Perlmutter execution logs are not on Puma; transferred processed products and scripts are hash-locked",
            "Iter015 daily surrogate uncertainty uses full model days while partial observed-hour means are retained"
        ],
    }
    report["storage_bytes_after_audit"] = enforce_storage(cfg)
    dump_json(Path(cfg["runtime_root"]) / "results/source_audit.json", report)
    return report


def write_netcdf(path: Path, ds: xr.Dataset) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    encoding = {name: {"zlib": True, "complevel": 4} for name in ds.data_vars if ds[name].dtype.kind in "fiu"}
    ds.to_netcdf(tmp, encoding=encoding)
    os.replace(tmp, path)


def prepare_flux_site(cfg: dict[str, Any], site: str) -> tuple[dict[str, Any], dict[str, Any]]:
    item = cfg["site_sources"][site]
    with xr.open_dataset(item["gpp"][0]) as opened:
        gpp = opened.load()
    gdates, gh, keep = normalized_noleap_time(gpp.time.values, cfg["canonical_origin"])
    gsource_all = pd.DatetimeIndex(pd.to_datetime(gpp.time.values))
    gsource = gsource_all[keep]
    gexcluded = gsource_all[~keep]
    dt = np.asarray(gpp.GPP_DT.values[keep], dtype=np.float64) * 86400.0
    nt = np.asarray(gpp.GPP_NT.values[keep], dtype=np.float64) * 86400.0
    raw = (dt + nt) / 2.0
    half = (dt - nt) / 2.0
    gated = np.maximum(0.0, raw)
    source_valid = np.isfinite(dt) & np.isfinite(nt)
    history_ready = gh >= int(cfg["history_hours"])
    gvalid = source_valid & history_ready
    gsigma = np.maximum.reduce([np.abs(half), 0.10 * np.abs(raw), np.full(raw.size, cfg["gpp_absolute_floor"])])
    gsigma[~source_valid] = np.nan
    gd = daily_groups(gh, gvalid, {"GPP_raw": raw, "GPP_gated": gated, "GPP_gate_after": np.maximum(0.0, raw)}, gsigma, cfg["gpp_min_hours"])
    gd["GPP_gate_after"] = np.maximum(0.0, gd["GPP_raw"])

    with xr.open_dataset(item["sr"][0]) as opened:
        srds = opened.load()
    sdates, sh, sk = normalized_noleap_time(srds.time.values, cfg["canonical_origin"])
    ssource_all = pd.DatetimeIndex(pd.to_datetime(srds.time.values))
    ssource = ssource_all[sk]
    sexcluded = ssource_all[~sk]
    sr = np.asarray(srds.SR.values[sk], dtype=np.float64) * 86400.0
    svalid_source = np.isfinite(sr)
    svalid = svalid_source & (sh >= int(cfg["history_hours"]))
    fallback = np.maximum(0.10 * np.abs(sr), cfg["sr_absolute_floor"])
    if "SR_err" in srds:
        configured = np.asarray(srds.SR_err.values[sk], dtype=np.float64) * 86400.0
        use_configured = np.isfinite(configured) & (configured > 0)
        ssigma = np.where(use_configured, configured, fallback)
        sflag = np.where(use_configured, 2, 3).astype(np.int8)
    else:
        ssigma = fallback
        sflag = np.full(sr.size, 3, dtype=np.int8)
    ssigma[~svalid_source] = np.nan
    sflag[~svalid_source] = 0
    sd = daily_groups(sh, svalid, {"SR": sr}, ssigma, cfg["sr_min_hours"])

    hourly = xr.Dataset(
        data_vars={
            "GPP_DT": ("gpp_time", dt), "GPP_NT": ("gpp_time", nt), "GPP_raw": ("gpp_time", raw),
            "GPP_halfdiff": ("gpp_time", half), "GPP_gated": ("gpp_time", gated),
            "GPP_obs_sigma": ("gpp_time", gsigma), "GPP_valid_source": ("gpp_time", source_valid.astype(np.int8)),
            "GPP_valid": ("gpp_time", gvalid.astype(np.int8)), "GPP_error_source": ("gpp_time", np.where(source_valid, 1, 0).astype(np.int8)),
            "SR": ("sr_time", sr), "SR_obs_sigma": ("sr_time", ssigma), "SR_valid_source": ("sr_time", svalid_source.astype(np.int8)),
            "SR_valid": ("sr_time", svalid.astype(np.int8)), "SR_error_source": ("sr_time", sflag),
            "GPP_source_time_unix_ns": ("gpp_time", gsource.asi8),
            "GPP_normalized_time_unix_ns": ("gpp_time", gdates.asi8),
            "GPP_excluded_source_time_unix_ns": ("gpp_excluded_time", gexcluded.asi8),
            "SR_source_time_unix_ns": ("sr_time", ssource.asi8),
            "SR_normalized_time_unix_ns": ("sr_time", sdates.asi8),
            "SR_excluded_source_time_unix_ns": ("sr_excluded_time", sexcluded.asi8),
        },
        coords={"gpp_time": gh, "sr_time": sh, "gpp_excluded_time": np.arange(gexcluded.size),
                "sr_excluded_time": np.arange(sexcluded.size)},
        attrs={"schema": "mcmc-observation-flux-hourly-v1", "site": site, "calendar": "noleap",
               "time_units": f"hours since {cfg['canonical_origin']}", "flux_units": "gC/m^2/day", "history_hours": cfg["history_hours"]},
    )
    for name in ("GPP_DT", "GPP_NT", "GPP_raw", "GPP_halfdiff", "GPP_gated", "GPP_obs_sigma", "SR", "SR_obs_sigma"):
        hourly[name].attrs["units"] = "gC/m^2/day"
    for name in ("GPP_source_time_unix_ns", "GPP_normalized_time_unix_ns", "GPP_excluded_source_time_unix_ns",
                 "SR_source_time_unix_ns", "SR_normalized_time_unix_ns", "SR_excluded_source_time_unix_ns"):
        hourly[name].attrs["units"] = "nanoseconds since 1970-01-01 00:00:00 UTC"
    hourly.GPP_error_source.attrs.update({"flag_values": [0, 1], "flag_meanings": "missing halfdiff_relative_floor"})
    hourly.SR_error_source.attrs.update({"flag_values": [0, 2, 3], "flag_meanings": "missing configured relative_floor_fallback"})

    daily = xr.Dataset(
        data_vars={
            "GPP_raw": ("gpp_day", gd["GPP_raw"]), "GPP_gated": ("gpp_day", gd["GPP_gated"]),
            "GPP_gate_after_daily": ("gpp_day", gd["GPP_gate_after"]), "GPP_obs_sigma": ("gpp_day", gd["sigma"]),
            "GPP_valid_hour_count": ("gpp_day", gd["count"]), "GPP_eligible": ("gpp_day", gd["eligible"].astype(np.int8)),
            "GPP_source_hour_index": (("gpp_day", "hour_slot"), gd["hour_index"]),
            "SR": ("sr_day", sd["SR"]), "SR_obs_sigma": ("sr_day", sd["sigma"]),
            "SR_valid_hour_count": ("sr_day", sd["count"]), "SR_eligible": ("sr_day", sd["eligible"].astype(np.int8)),
            "SR_source_hour_index": (("sr_day", "hour_slot"), sd["hour_index"]),
        },
        coords={"gpp_day": gd["day"], "sr_day": sd["day"], "hour_slot": np.arange(24)},
        attrs={"schema": "mcmc-observation-flux-daily-v1", "site": site, "calendar": "noleap",
               "day_units": f"days since {cfg['canonical_origin']}", "flux_units": "gC/m^2/day",
               "gpp_min_hours": cfg["gpp_min_hours"], "sr_min_hours": cfg["sr_min_hours"],
               "daily_sigma_rule": "sqrt(mean(hourly_sigma^2)); no sqrt(n) reduction"},
    )
    for name in ("GPP_raw", "GPP_gated", "GPP_gate_after_daily", "GPP_obs_sigma", "SR", "SR_obs_sigma"):
        daily[name].attrs["units"] = "gC/m^2/day"

    site_dir = Path(cfg["staging_root"]) / "sites" / site
    write_netcdf(site_dir / "flux_hourly.nc", hourly)
    write_netcdf(site_dir / "flux_daily.nc", daily)
    qc = {
        "schema": "mcmc-observation-qc-v1", "site": site,
        "gpp_source_hours": int(source_valid.sum()), "gpp_history_eligible_hours": int(gvalid.sum()),
        "gpp_eligible_days": int(gd["eligible"].sum()), "sr_source_hours": int(svalid_source.sum()),
        "sr_history_eligible_hours": int(svalid.sum()), "sr_eligible_days": int(sd["eligible"].sum()),
        "gpp_threshold": cfg["gpp_min_hours"], "sr_threshold": cfg["sr_min_hours"],
        "gpp_negative_raw_hours": int(np.count_nonzero(source_valid & (raw < 0))),
        "gpp_gate_changed_hours": int(np.count_nonzero(source_valid & (raw < 0))),
        "gpp_calendar_excluded_hours": int(gexcluded.size), "sr_calendar_excluded_hours": int(sexcluded.size),
        "jerc_sr_fallback_only": bool(site == "JERC"),
    }
    dump_json(site_dir / "qc_report.json", qc)
    arrays = {"site": site, "gh": gh, "gdates": gdates, "gvalid": gvalid, "raw": raw, "gated": gated, "gd": gd,
              "sh": sh, "sdates": sdates, "svalid": svalid, "sd": sd, "gexcluded": gexcluded, "sexcluded": sexcluded}
    return qc, arrays


def prepare_flux(cfg: dict[str, Any]) -> dict[str, Any]:
    require((Path(cfg["runtime_root"]) / "results/source_audit.json").is_file(), "source audit missing")
    diagnostics = Path(cfg["staging_root"]) / "diagnostics"
    diagnostics.mkdir(parents=True, exist_ok=True)
    qcs, arrays = {}, {}
    coverage_rows, threshold_rows, gate_rows = [], [], []
    for site in cfg["sites"]:
        qcs[site], arrays[site] = prepare_flux_site(cfg, site)
        for variable, day, count, eligible in (
            [("GPP", d, c, e) for d, c, e in zip(arrays[site]["gd"]["day"], arrays[site]["gd"]["count"], arrays[site]["gd"]["eligible"])] +
            [("SR", d, c, e) for d, c, e in zip(arrays[site]["sd"]["day"], arrays[site]["sd"]["count"], arrays[site]["sd"]["eligible"])]
        ):
            coverage_rows.append({"site": site, "variable": variable, "noleap_day": int(day), "valid_hours": int(count), "eligible": int(eligible)})
        for variable, daily in (("GPP", arrays[site]["gd"]), ("SR", arrays[site]["sd"])):
            for level in (18, 20, 22, 24):
                threshold_rows.append({"site": site, "variable": variable, "threshold": level,
                                       "eligible_days_after_history": int(np.count_nonzero(daily["count"] >= level))})
        gd = arrays[site]["gd"]
        for day, raw, gated, after, count in zip(gd["day"], gd["GPP_raw"], gd["GPP_gated"], gd["GPP_gate_after"], gd["count"]):
            if np.isfinite(raw):
                gate_rows.append({"site": site, "noleap_day": int(day), "valid_hours": int(count), "raw": raw,
                                  "hourly_gate_then_mean": gated, "mean_then_gate": after, "impact": gated - raw})
    pd.DataFrame(coverage_rows).to_csv(diagnostics / "observation_coverage.csv", index=False)
    pd.DataFrame(threshold_rows).to_csv(diagnostics / "coverage_threshold_summary.csv", index=False)
    pd.DataFrame(gate_rows).to_csv(diagnostics / "gpp_zero_gate_impact.csv", index=False)

    fig, axes = plt.subplots(4, 2, figsize=(13, 12), constrained_layout=True)
    for col, site in enumerate(cfg["sites"]):
        gmat = arrays[site]["gvalid"].reshape(-1, 24).T
        smat = arrays[site]["svalid"].reshape(-1, 24).T
        axes[0, col].imshow(gmat, aspect="auto", interpolation="nearest", cmap="Greys", vmin=0, vmax=1)
        axes[0, col].set(title=f"{site} GPP paired-hour availability", xlabel="noleap day", ylabel="hour")
        axes[1, col].imshow(smat, aspect="auto", interpolation="nearest", cmap="Greys", vmin=0, vmax=1)
        axes[1, col].set(title=f"{site} SR-hour availability", xlabel="noleap day in SR window", ylabel="hour")
        axes[2, col].hist(arrays[site]["gd"]["count"], bins=np.arange(-.5, 25.6), alpha=.65, label="GPP", color="#2c7fb8")
        axes[2, col].hist(arrays[site]["sd"]["count"], bins=np.arange(-.5, 25.6), alpha=.45, label="SR", color="#f03b20")
        axes[2, col].axvline(cfg["gpp_min_hours"], color="#2c7fb8", linestyle="--")
        axes[2, col].axvline(cfg["sr_min_hours"], color="#f03b20", linestyle="--")
        axes[2, col].set(title=f"{site} daily coverage thresholds", xlabel="valid hours", ylabel="days")
        axes[2, col].legend()
        gdays = arrays[site]["gd"]["day"]
        sdays = arrays[site]["sd"]["day"]
        common, gi, si = np.intersect1d(gdays, sdays, return_indices=True)
        overlap = (arrays[site]["gd"]["eligible"][gi] & arrays[site]["sd"]["eligible"][si]).astype(int)
        axes[3, col].plot(common, arrays[site]["gd"]["count"][gi], label="GPP hours", linewidth=.8)
        axes[3, col].plot(common, arrays[site]["sd"]["count"][si], label="SR hours", linewidth=.8)
        axes[3, col].fill_between(common, 0, 24, where=overlap.astype(bool), alpha=.12, label="both eligible")
        text_note = (f"both eligible={overlap.sum()}\n"
                     f"Feb29 exclusions: GPP={len(arrays[site]['gexcluded'])}, SR={len(arrays[site]['sexcluded'])}\n"
                     f"GPP source HH:15 -> HH:00; history={cfg['history_hours']} h")
        axes[3, col].text(.01, .98, text_note, transform=axes[3, col].transAxes, va="top", fontsize=8,
                          bbox={"facecolor": "white", "alpha": .8, "edgecolor": "none"})
        axes[3, col].set(title=f"{site} GPP/SR overlap and exclusions", xlabel="noleap day", ylabel="valid hours", ylim=(0, 24.5))
        axes[3, col].legend(fontsize=7, loc="lower right")
    fig.savefig(diagnostics / "flux_coverage_alignment.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(12, 11), constrained_layout=True)
    for col, site in enumerate(cfg["sites"]):
        valid = arrays[site]["gvalid"]
        axes[0, col].hist(arrays[site]["raw"][valid], bins=60, alpha=.55, label="raw")
        axes[0, col].hist(arrays[site]["gated"][valid], bins=60, alpha=.55, label="gated")
        axes[0, col].set(title=f"{site} hourly GPP", xlabel="gC m$^{-2}$ day$^{-1}$", ylabel="hours")
        axes[0, col].legend()
        gd = arrays[site]["gd"]
        use = np.isfinite(gd["GPP_raw"])
        axes[1, col].scatter(gd["GPP_raw"][use], gd["GPP_gated"][use], s=8, alpha=.5, label="hourly gate first")
        axes[1, col].scatter(gd["GPP_raw"][use], gd["GPP_gate_after"][use], s=8, alpha=.5, label="daily gate")
        axes[1, col].set(title=f"{site} eligible daily comparison", xlabel="raw daily mean", ylabel="gated daily mean")
        axes[1, col].legend(fontsize=8)
        monthly = pd.DataFrame({"month": arrays[site]["gdates"].month, "impact": arrays[site]["gated"] - arrays[site]["raw"],
                                "valid": arrays[site]["gvalid"]})
        monthly = monthly[monthly.valid].groupby("month")["impact"].agg(["mean", "count"])
        axes[2, col].bar(monthly.index, monthly["mean"], color="#31a354")
        for month, row in monthly.iterrows():
            axes[2, col].text(month, row["mean"], str(int(row["count"])), ha="center", va="bottom", fontsize=6, rotation=90)
        axes[2, col].set(title=f"{site} gate impact by month (labels=hours)", xlabel="month", ylabel="mean gated - raw")
    fig.savefig(diagnostics / "gpp_zero_gate_impact.png", dpi=180)
    plt.close(fig)

    report = {"schema": "mcmc-iter002-flux-preparation-v1", "result": "pass", "sites": qcs,
              "figures": ["flux_coverage_alignment.png", "gpp_zero_gate_impact.png"]}
    report["storage_bytes_after_flux"] = enforce_storage(cfg)
    dump_json(Path(cfg["runtime_root"]) / "results/flux_preparation.json", report)
    return report


def select_metric(frame: pd.DataFrame, site: str, stage: str, resolution: str, metric: str) -> float:
    row = frame[(frame.stage == stage) & (frame.partition == "validation") & (frame.site == site) &
                (frame.scale == "physical") & (frame.resolution == resolution) & (frame.metric == metric)]
    require(len(row) == 1, f"missing Iter015 metric {site} {stage} {resolution} {metric}")
    return float(row.iloc[0]["mean"])


def prepare_uncertainty(cfg: dict[str, Any]) -> dict[str, Any]:
    require((Path(cfg["runtime_root"]) / "results/flux_preparation.json").is_file(), "flux result missing")
    verified_iter015 = verify_iter015_products(cfg)
    products = Path(cfg["iter015_products_root"])
    metric = pd.read_csv(products / "metric_summary.csv")
    cn_summary = pd.read_csv(products / "cn_member_balanced_summary.csv")
    cn_cov = pd.read_csv(products / "cn_member_balanced_covariance.csv")
    soil = pd.read_csv(cfg["sources"]["soil_csv"]["path"])
    audit: dict[str, Any] = {"schema": "mcmc-iter002-uncertainty-audit-v1", "sites": {}}
    figure_data = {}
    for site in cfg["sites"]:
        soil_row = soil[soil.siteID == site].iloc[0]
        depth_path = Path(cfg["site_sources"][site]["depth"][0])
        with xr.open_dataset(depth_path) as opened:
            depth = opened.load()
        require(depth.sizes.get("member") == 1024, f"{site} depth member count")
        full = np.column_stack([depth.TOTSOMC.values, depth.TOTSOMN.values]).astype(np.float64)
        shallow = np.column_stack([depth.TOTSOMC_NEONDEPTH.values, depth.TOTSOMN_NEONDEPTH.values]).astype(np.float64)
        fractions = np.array([np.mean(depth.SOC_DEPTH_FRACTION.values), np.mean(depth.SON_DEPTH_FRACTION.values)])
        residual = np.log(fractions[None, :] * full / shallow)
        depth_bias = np.mean(residual, axis=0)
        depth_cov = np.cov(residual, rowvar=False, ddof=1)
        require(np.all(np.isfinite(depth_cov)), f"{site} nonfinite depth covariance")
        expected_depth = cfg["expected_depth_statistics"][site]
        np.testing.assert_allclose(fractions, expected_depth["fractions"], rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(depth_bias, expected_depth["mean_log_residual"], rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(depth_cov, expected_depth["sample_covariance"], rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(np.sqrt(np.diag(depth_cov)), expected_depth["printed_sd"], rtol=0, atol=5e-7)
        depth_corr = depth_cov[0, 1] / np.sqrt(depth_cov[0, 0] * depth_cov[1, 1])
        require(abs(depth_corr - expected_depth["printed_correlation"]) <= 5e-7, f"{site} printed depth correlation mismatch")

        ordered = ["TOTSOMC", "TOTSOMN"]
        surrogate_bias = np.array([
            float(cn_summary[(cn_summary.site == site) & (cn_summary.target == target) &
                             (cn_summary.member_balanced_metric == "mean_log_error")].iloc[0]["mean"])
            for target in ordered
        ])
        surrogate_cov = np.empty((2, 2), dtype=np.float64)
        for i, row_target in enumerate(ordered):
            for j, col_target in enumerate(ordered):
                row = cn_cov[(cn_cov.site == site) & (cn_cov.row_target == row_target) & (cn_cov.column_target == col_target)]
                require(len(row) == 1, f"{site} missing surrogate covariance {row_target}/{col_target}")
                surrogate_cov[i, j] = float(row.iloc[0]["member_balanced_log_error_covariance"])
        require(np.max(np.abs(surrogate_cov - surrogate_cov.T)) <= 1e-14, f"{site} asymmetric surrogate covariance")

        cvs = np.asarray(cfg["cn_observation_cv"], dtype=np.float64)
        observation_cov = np.zeros((cvs.size, 2, 2), dtype=np.float64)
        total_cov = np.zeros_like(observation_cov)
        for idx, cv in enumerate(cvs):
            observation_cov[idx] = np.eye(2) * np.log1p(cv * cv)
            total_cov[idx] = observation_cov[idx] + surrogate_cov + depth_cov
            require(np.max(np.abs(total_cov[idx] - total_cov[idx].T)) <= 1e-14, f"{site} asymmetric total covariance")
            np.linalg.cholesky(total_cov[idx])

        resolutions = ["hourly", "daily"]
        gpp_rmse = np.array([select_metric(metric, site, "gpp", r, "rmse") for r in resolutions])
        gpp_bias = np.array([select_metric(metric, site, "gpp", r, "bias") for r in resolutions])
        sr_rmse = np.array([select_metric(metric, site, "sr", r, "rmse") for r in resolutions])
        sr_bias = np.array([select_metric(metric, site, "sr", r, "bias") for r in resolutions])
        uds = xr.Dataset(
            data_vars={
                "GPP_surrogate_rmse": ("resolution", gpp_rmse), "GPP_surrogate_bias": ("resolution", gpp_bias),
                "SR_surrogate_rmse": ("resolution", sr_rmse), "SR_surrogate_bias": ("resolution", sr_bias),
                "depth_fraction": ("cn_target", fractions), "surrogate_log_bias": ("cn_target", surrogate_bias),
                "depth_log_bias": ("cn_target", depth_bias), "total_log_bias_correction": ("cn_target", surrogate_bias + depth_bias),
                "surrogate_log_covariance": (("cn_target", "cn_target_2"), surrogate_cov),
                "depth_log_covariance": (("cn_target", "cn_target_2"), depth_cov),
                "observation_log_covariance": (("cv", "cn_target", "cn_target_2"), observation_cov),
                "total_log_covariance": (("cv", "cn_target", "cn_target_2"), total_cov),
            },
            coords={"resolution": resolutions, "cn_target": ordered, "cn_target_2": ordered, "cv": cvs},
            attrs={"schema": "mcmc-fixed-uncertainty-v1", "site": site, "baseline_cv": cfg["cn_baseline_cv"],
                   "surrogate_population": "819 development members, Iter015 member-balanced held-out errors",
                   "depth_population": "complete 1024-member PPE1 preprocessing ensemble",
                   "depth_covariance_estimator": "sample covariance, divisor N-1",
                   "flux_daily_approximation": "Iter015 full-day RMSE applied to exact partial observed-hour means",
                   "flux_bias_policy": "report only; no correction", "cn_bias_policy": "surrogate plus depth fixed mean log error"},
        )
        for name in ("GPP_surrogate_rmse", "GPP_surrogate_bias", "SR_surrogate_rmse", "SR_surrogate_bias"):
            uds[name].attrs["units"] = "gC/m^2/day"
        site_dir = Path(cfg["staging_root"]) / "sites" / site
        write_netcdf(site_dir / "uncertainty.nc", uds)
        soil_payload = {
            "schema": "mcmc-soil-cn-observation-v1", "site": site,
            "TOTSOMC_gC_m2": float(soil_row.totalSoilC_gC_m2), "TOTSOMN_gN_m2": float(soil_row.totalSoilN_gN_m2),
            "CN_ratio": float(soil_row.CN_ratio), "effective_depth_m": float(soil_row.effectiveDepth_m),
            "source": cfg["sources"]["soil_csv"], "processing_script": cfg["sources"]["soil_script"],
            "definition": "processed NEON soil horizon stocks integrated to effective depth; no Iter002 rederivation",
        }
        dump_json(site_dir / "soil_cn.json", soil_payload)
        audit["sites"][site] = {
            "fractions": fractions.tolist(), "depth_bias": depth_bias.tolist(), "depth_covariance": depth_cov.tolist(),
            "surrogate_bias": surrogate_bias.tolist(), "surrogate_covariance": surrogate_cov.tolist(),
            "total_bias_correction": (surrogate_bias + depth_bias).tolist(),
            "total_covariance_by_cv": {str(cv): total_cov[i].tolist() for i, cv in enumerate(cvs)},
            "gpp_surrogate_rmse": dict(zip(resolutions, gpp_rmse.tolist())),
            "sr_surrogate_rmse": dict(zip(resolutions, sr_rmse.tolist())),
        }
        with xr.open_dataset(Path(cfg["staging_root"]) / "sites" / site / "flux_daily.nc") as flux_daily:
            obs_error = np.array([float(np.nanmedian(flux_daily.GPP_obs_sigma.values)),
                                  float(np.nanmedian(flux_daily.SR_obs_sigma.values))])
        figure_data[site] = (gpp_rmse, sr_rmse, obs_error, observation_cov, surrogate_cov, depth_cov, total_cov)

    diagnostics = Path(cfg["staging_root"]) / "diagnostics"
    dump_json(diagnostics / "uncertainty_audit.json", audit)
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    for row, site in enumerate(cfg["sites"]):
        gpp, sr, flux_obs, obs, sur, dep, total = figure_data[site]
        axes[row, 0].bar(["GPP obs d", "GPP sur d", "SR obs d", "SR sur d"],
                         [flux_obs[0], gpp[1], flux_obs[1], sr[1]], color=["#9ecae1", "#2c7fb8", "#fcae91", "#f03b20"])
        axes[row, 0].tick_params(axis="x", rotation=35)
        axes[row, 0].set(title=f"{site} flux observation and surrogate errors", ylabel="gC m$^{-2}$ day$^{-1}$")
        axes[row, 0].text(.02, .98, "obs: hourly precedence + floor; daily RMS\nsur: Iter015 fixed full-day RMSE",
                          transform=axes[row, 0].transAxes, va="top", fontsize=7)
        im1 = axes[row, 1].imshow(np.block([[sur, dep], [obs[1], total[1]]]), cmap="viridis")
        axes[row, 1].set(title=f"{site} C/N covariance components", xticks=[], yticks=[])
        fig.colorbar(im1, ax=axes[row, 1], fraction=.046)
        axes[row, 2].bar(["obs C", "obs N", "sur C", "sur N", "depth C", "depth N", "total C", "total N"],
                         np.r_[np.diag(obs[1]), np.diag(sur), np.diag(dep), np.diag(total[1])])
        axes[row, 2].tick_params(axis="x", rotation=45)
        axes[row, 2].set(title=f"{site} baseline CV=0.30 variances", ylabel="log variance")
    fig.savefig(diagnostics / "uncertainty_components.png", dpi=180)
    plt.close(fig)
    audit["result"] = "pass"
    audit["iter015_verified_products"] = verified_iter015
    audit["storage_bytes_after_uncertainty"] = enforce_storage(cfg)
    dump_json(Path(cfg["runtime_root"]) / "results/uncertainty_integration.json", audit)
    return audit


def file_manifest(root: Path, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    exclude = exclude or set()
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        rows.append({"path": rel, "sha256": sha256(path), "size_bytes": path.stat().st_size})
    return rows


def validate_daily_reconstruction(site: str, hourly: xr.Dataset, daily: xr.Dataset, variable: str, threshold: int) -> None:
    prefix = "GPP" if variable == "GPP" else "SR"
    time = hourly[f"{prefix.lower()}_time"].values
    valid = hourly[f"{prefix}_valid"].values.astype(bool)
    sigma = hourly[f"{prefix}_obs_sigma"].values
    day_values = daily[f"{prefix.lower()}_day"].values
    index = daily[f"{prefix}_source_hour_index"].values
    counts = daily[f"{prefix}_valid_hour_count"].values
    eligible = daily[f"{prefix}_eligible"].values.astype(bool)
    for row, day in enumerate(day_values):
        loc = index[row]
        loc = loc[loc >= 0]
        require(np.all(time[loc] // 24 == day), f"{site} {prefix} source-hour day mismatch")
        use = loc[valid[loc]]
        require(use.size == counts[row], f"{site} {prefix} daily count mismatch")
        require(eligible[row] == (use.size >= threshold), f"{site} {prefix} eligibility mismatch")
        if eligible[row]:
            expected_sigma = np.sqrt(np.mean(np.square(sigma[use])))
            np.testing.assert_allclose(daily[f"{prefix}_obs_sigma"].values[row], expected_sigma, rtol=1e-12, atol=1e-12)
            if prefix == "GPP":
                raw = hourly.GPP_raw.values[use]
                gated = hourly.GPP_gated.values[use]
                np.testing.assert_allclose(daily.GPP_raw.values[row], np.mean(raw), rtol=1e-12, atol=1e-12)
                np.testing.assert_allclose(daily.GPP_gated.values[row], np.mean(gated), rtol=1e-12, atol=1e-12)
                np.testing.assert_allclose(daily.GPP_gate_after_daily.values[row], max(0.0, np.mean(raw)), rtol=1e-12, atol=1e-12)
            else:
                np.testing.assert_allclose(daily.SR.values[row], np.mean(hourly.SR.values[use]), rtol=1e-12, atol=1e-12)
        else:
            require(not np.isfinite(daily[f"{prefix}_obs_sigma"].values[row]), f"{site} {prefix} ineligible sigma is finite")


def validate_staged(cfg: dict[str, Any], root: Path) -> dict[str, Any]:
    required = ["diagnostics/flux_coverage_alignment.png", "diagnostics/gpp_zero_gate_impact.png",
                "diagnostics/uncertainty_components.png", "diagnostics/observation_coverage.csv",
                "diagnostics/uncertainty_audit.json"]
    for site in cfg["sites"]:
        required += [f"sites/{site}/flux_hourly.nc", f"sites/{site}/flux_daily.nc", f"sites/{site}/soil_cn.json",
                     f"sites/{site}/uncertainty.nc", f"sites/{site}/qc_report.json"]
    for rel in required:
        require((root / rel).is_file(), f"missing staged product {rel}")
    for site in cfg["sites"]:
        with xr.open_dataset(root / f"sites/{site}/flux_hourly.nc") as opened:
            hourly = opened.load()
        require(hourly.attrs.get("schema") == "mcmc-observation-flux-hourly-v1", f"{site} hourly schema")
        require(np.any(hourly.GPP_raw.values < 0), f"{site} raw negative GPP was not retained")
        np.testing.assert_allclose(hourly.GPP_gated.values, np.maximum(0, hourly.GPP_raw.values), rtol=1e-12, atol=1e-12, equal_nan=True)
        np.testing.assert_allclose(hourly.GPP_raw.values, (hourly.GPP_DT.values + hourly.GPP_NT.values)/2, rtol=1e-12, atol=1e-12, equal_nan=True)
        np.testing.assert_allclose(hourly.GPP_halfdiff.values, (hourly.GPP_DT.values - hourly.GPP_NT.values)/2, rtol=1e-12, atol=1e-12, equal_nan=True)
        source_ns = hourly.GPP_source_time_unix_ns.values
        normalized_ns = hourly.GPP_normalized_time_unix_ns.values
        require(np.all(source_ns - normalized_ns == np.timedelta64(15, "m")), f"{site} GPP source timestamp offset")
        require(hourly.GPP_excluded_source_time_unix_ns.size == 48, f"{site} GPP calendar exclusion count")
        expected_gpp_sigma = np.maximum.reduce([np.abs(hourly.GPP_halfdiff.values), 0.10*np.abs(hourly.GPP_raw.values),
                                                np.full(hourly.sizes["gpp_time"], cfg["gpp_absolute_floor"])])
        np.testing.assert_allclose(hourly.GPP_obs_sigma.values, expected_gpp_sigma, rtol=1e-12, atol=1e-12, equal_nan=True)
        require(np.all(hourly.SR_source_time_unix_ns.values == hourly.SR_normalized_time_unix_ns.values), f"{site} SR time normalization")
        with xr.open_dataset(root / f"sites/{site}/flux_daily.nc") as opened:
            daily = opened.load()
        require(daily.attrs.get("daily_sigma_rule", "").startswith("sqrt(mean"), f"{site} daily sigma rule")
        require(np.all(daily.GPP_source_hour_index.values >= -1), f"{site} invalid GPP indices")
        require(np.all(daily.SR_source_hour_index.values >= -1), f"{site} invalid SR indices")
        validate_daily_reconstruction(site, hourly, daily, "GPP", cfg["gpp_min_hours"])
        validate_daily_reconstruction(site, hourly, daily, "SR", cfg["sr_min_hours"])
        with xr.open_dataset(root / f"sites/{site}/uncertainty.nc") as ds:
            for matrix in ds.total_log_covariance.values:
                require(np.max(np.abs(matrix-matrix.T)) <= 1e-14, f"{site} total covariance symmetry")
                np.linalg.cholesky(matrix)
    thresholds = pd.read_csv(root / "diagnostics/coverage_threshold_summary.csv")
    for site in cfg["sites"]:
        with xr.open_dataset(root / f"sites/{site}/flux_daily.nc") as opened:
            daily = opened.load()
        for variable in ("GPP", "SR"):
            counts = daily[f"{variable}_valid_hour_count"].values
            for level in (18, 20, 22, 24):
                row = thresholds[(thresholds.site == site) & (thresholds.variable == variable) & (thresholds.threshold == level)]
                require(len(row) == 1 and int(row.iloc[0].eligible_days_after_history) == int(np.count_nonzero(counts >= level)),
                        f"{site} {variable} threshold table mismatch at {level}")
    return {"schema": "mcmc-iter002-staged-validation-v1", "result": "pass", "required_file_count": len(required)}


def publish(cfg: dict[str, Any], config_path: Path) -> dict[str, Any]:
    root = Path(cfg["staging_root"])
    destination = Path(cfg["publication_root"])
    require(root.is_dir(), "staging root missing")
    require(not destination.exists(), f"publication root already exists: {destination}")
    validation = validate_staged(cfg, root)
    validation["validated_at_utc"] = datetime.now(timezone.utc).isoformat()
    dump_json(root / "validation_report.json", validation)
    manifest = {
        "schema": "mcmc-observation-release-manifest-v1", "release": "release_0001",
        "result": "validated", "sites": cfg["sites"], "plan_sha256": cfg["plan_sha256"],
        "repository_commit": cfg["repository_commit"], "config_sha256": sha256(config_path),
        "source_identities": {name: digest for name, _, digest in iter_sources(cfg)},
        "iter015_fixed_test_access": False, "catalog_last": True,
        "files": file_manifest(root, {"release_manifest.json", "catalog.json"}),
    }
    dump_json(root / "release_manifest.json", manifest)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / f".{destination.name}.iter002_tmp_{os.getpid()}"
    require(not temporary.exists(), f"temporary publication path exists: {temporary}")
    shutil.copytree(root, temporary)
    require(sha256(temporary / "release_manifest.json") == sha256(root / "release_manifest.json"), "temporary publication copy mismatch")
    validate_staged(cfg, temporary)
    os.replace(temporary, destination)
    catalog = {
        "schema": "mcmc-observation-release-catalog-v1", "current_release": "release_0001",
        "release_path": str(destination), "release_manifest_sha256": sha256(destination / "release_manifest.json"),
        "published_at_utc": datetime.now(timezone.utc).isoformat(), "decision": "observation_release_0001_published",
    }
    dump_json(destination / "catalog.json", catalog)
    result = {"schema": "mcmc-iter002-publication-v1", "result": "pass", "catalog": catalog,
              "published_file_count": len(file_manifest(destination)), "atomic_promotion": True}
    result["storage_bytes_after_publication"] = enforce_storage(cfg)
    dump_json(Path(cfg["runtime_root"]) / "results/publication.json", result)
    return result


def final_validate(cfg: dict[str, Any]) -> dict[str, Any]:
    root = Path(cfg["publication_root"])
    require(root.is_dir(), "published release missing")
    catalog = json.loads((root / "catalog.json").read_text())
    require(catalog["release_manifest_sha256"] == sha256(root / "release_manifest.json"), "catalog manifest hash mismatch")
    manifest = json.loads((root / "release_manifest.json").read_text())
    for item in manifest["files"]:
        path = root / item["path"]
        require(path.is_file() and path.stat().st_size == item["size_bytes"] and sha256(path) == item["sha256"],
                f"published product mismatch: {item['path']}")
    staged = validate_staged(cfg, root)
    require(manifest["iter015_fixed_test_access"] is False, "fixed-test uncertainty contamination")
    result = {
        "schema": "mcmc-iter002-final-validation-v1", "result": "pass",
        "decision": "observation_release_0001_published", "release_manifest_sha256": sha256(root / "release_manifest.json"),
        "catalog_sha256": sha256(root / "catalog.json"), "validated_product_count": len(manifest["files"]),
        "staged_validation": staged,
    }
    result["storage_bytes_final"] = enforce_storage(cfg)
    dump_json(Path(cfg["runtime_root"]) / "results/final_validation.json", result)
    print("MCMC_ITER002_FINAL_PASS decision=observation_release_0001_published")
    return result


def preflight(cfg: dict[str, Any]) -> dict[str, Any]:
    rows = verify_sources(cfg)
    root = Path(cfg["runtime_root"])
    require(root.is_dir() and os.access(root, os.W_OK), "runtime root is not writable")
    require(not Path(cfg["publication_root"]).exists(), "publication root collision")
    result = {"schema": "mcmc-iter002-preflight-v1", "result": "pass", "source_count": len(rows),
              "python": sys.version, "xarray": xr.__version__, "numpy": np.__version__, "pandas": pd.__version__}
    result["storage_bytes"] = enforce_storage(cfg)
    dump_json(root / "results/preflight.json", result)
    print("MCMC_ITER002_PREFLIGHT_PASS")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--step", required=True, choices=["preflight", "source-audit", "flux", "uncertainty", "publish", "final-validate"])
    args = parser.parse_args()
    cfg, config_path = load_config(args.config)
    verify_identity(cfg, config_path)
    if args.step == "preflight":
        preflight(cfg)
    elif args.step == "source-audit":
        source_audit(cfg)
        print("MCMC_ITER002_SOURCE_AUDIT_PASS")
    elif args.step == "flux":
        prepare_flux(cfg)
        print("MCMC_ITER002_FLUX_PASS")
    elif args.step == "uncertainty":
        prepare_uncertainty(cfg)
        print("MCMC_ITER002_UNCERTAINTY_PASS")
    elif args.step == "publish":
        publish(cfg, config_path)
        print("MCMC_ITER002_PUBLICATION_PASS")
    else:
        final_validate(cfg)


if __name__ == "__main__":
    main()
