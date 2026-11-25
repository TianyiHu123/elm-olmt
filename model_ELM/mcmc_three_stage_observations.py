"""Strict loading and alignment of the immutable Iter002 observation release."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import numpy as np
import pandas as pd
import xarray as xr
from netCDF4 import Dataset

from .mcmc_coupled_adapter import EXPECTED_SNAPSHOT_SHA256


CONFIG_SCHEMA = "mcmc-three-stage-observation-config-v1"
EXPECTED_CATALOG_SHA256 = "cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8"
EXPECTED_MANIFEST_SHA256 = "460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2"
EXPECTED_VALIDATION_SHA256 = "19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef"
ORIGIN = pd.Timestamp("2018-01-01 00:00:00")
SITES = ("ABBY", "JERC")
RESOLUTIONS = ("hourly", "daily")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _readonly(array: np.ndarray, dtype: np.dtype | type | None = None) -> np.ndarray:
    result = np.asarray(array, dtype=dtype).copy()
    result.setflags(write=False)
    return result


def _noleap_hours(unix_ns: np.ndarray) -> np.ndarray:
    timestamps = pd.DatetimeIndex(np.asarray(unix_ns, dtype=np.int64).astype("datetime64[ns]"))
    hours = ((timestamps - ORIGIN) / pd.Timedelta(hours=1)).astype(np.int64).to_numpy()
    for year in range(ORIGIN.year, int(timestamps.year.max()) + 1):
        if pd.Timestamp(year=year, month=1, day=1).is_leap_year:
            hours -= 24 * (timestamps >= pd.Timestamp(year=year, month=3, day=1)).astype(np.int64)
    return hours


@dataclass(frozen=True)
class ObservationReleaseConfig:
    schema: str
    release_root: Path
    snapshot_root: Path
    catalog_sha256: str
    release_manifest_sha256: str
    validation_report_sha256: str
    snapshot_sha256: str

    def validate(self) -> None:
        if self.schema != CONFIG_SCHEMA:
            raise ValueError(f"unsupported observation config schema: {self.schema}")
        expected = (
            (self.catalog_sha256, EXPECTED_CATALOG_SHA256, "catalog"),
            (self.release_manifest_sha256, EXPECTED_MANIFEST_SHA256, "release manifest"),
            (self.validation_report_sha256, EXPECTED_VALIDATION_SHA256, "validation report"),
            (self.snapshot_sha256, EXPECTED_SNAPSHOT_SHA256, "snapshot"),
        )
        for observed, locked, label in expected:
            if observed != locked:
                raise ValueError(f"configured observation {label} identity mismatch")
        if not Path(self.release_root).expanduser().resolve().is_dir():
            raise ValueError(f"missing observation release root: {self.release_root}")
        if not Path(self.snapshot_root).expanduser().resolve().is_dir():
            raise ValueError(f"missing forcing snapshot root: {self.snapshot_root}")


@dataclass(frozen=True)
class FluxObservationOperator:
    variable: str
    resolution: str
    observed: np.ndarray
    observation_sigma: np.ndarray
    forcing_hour_groups: tuple[np.ndarray, ...]
    surrogate_rmse: float

    @property
    def count(self) -> int:
        return int(self.observed.size)

    def window(self, start: int, end: int) -> "FluxObservationOperator":
        keep = [index for index, group in enumerate(self.forcing_hour_groups)
                if group.size and int(group[0]) >= start and int(group[-1]) < end]
        if not keep:
            raise ValueError(f"{self.variable} {self.resolution} window has no observations")
        return FluxObservationOperator(
            variable=self.variable,
            resolution=self.resolution,
            observed=_readonly(self.observed[keep], np.float64),
            observation_sigma=_readonly(self.observation_sigma[keep], np.float64),
            forcing_hour_groups=tuple(_readonly(self.forcing_hour_groups[index], np.int64) for index in keep),
            surrogate_rmse=self.surrogate_rmse,
        )

    def aggregate_predictions(self, hourly_prediction: np.ndarray, start: int) -> np.ndarray:
        values = np.asarray(hourly_prediction, dtype=np.float64)
        if values.ndim != 1:
            raise ValueError("hourly prediction must be one-dimensional")
        aggregated = np.empty(self.count, dtype=np.float64)
        for index, group in enumerate(self.forcing_hour_groups):
            relative = group - int(start)
            if np.any(relative < 0) or np.any(relative >= values.size):
                raise ValueError("observation forcing-hour mapping is outside prediction window")
            aggregated[index] = float(np.mean(values[relative]))
        return aggregated


@dataclass(frozen=True)
class SoilCNContext:
    observed_stocks: np.ndarray
    depth_fraction: np.ndarray
    total_bias_correction: np.ndarray
    covariance_by_cv: Mapping[float, np.ndarray]


@dataclass(frozen=True)
class ThreeStageObservationContext:
    site: str
    flux: Mapping[tuple[str, str], FluxObservationOperator]
    soil_cn: SoilCNContext
    release_catalog_sha256: str
    release_manifest_sha256: str
    validation_report_sha256: str
    forcing_hours: int
    uncertainty_product_sha256: str
    soil_product_sha256: str
    depth_source_sha256: str

    def operator(self, variable: str, resolution: str) -> FluxObservationOperator:
        try:
            return self.flux[(variable.upper(), resolution)]
        except KeyError as exc:
            raise ValueError(f"unsupported flux operator: {variable}/{resolution}") from exc


def _verify_release(config: ObservationReleaseConfig) -> dict:
    config.validate()
    root = Path(config.release_root).expanduser().resolve()
    for name, expected in (
        ("catalog.json", config.catalog_sha256),
        ("release_manifest.json", config.release_manifest_sha256),
        ("validation_report.json", config.validation_report_sha256),
    ):
        path = root / name
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"observation release identity mismatch: {name}")
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
    if catalog.get("current_release") != "release_0001" or catalog.get("decision") != "observation_release_0001_published":
        raise ValueError("observation catalog contract mismatch")
    if catalog.get("release_manifest_sha256") != config.release_manifest_sha256:
        raise ValueError("observation catalog/manifest mismatch")
    if manifest.get("schema") != "mcmc-observation-release-manifest-v1" or manifest.get("result") != "validated":
        raise ValueError("observation manifest contract mismatch")
    if manifest.get("sites") != ["ABBY", "JERC"] or manifest.get("iter015_fixed_test_access") is not False:
        raise ValueError("observation site or fixed-test contract mismatch")
    for record in manifest.get("files", ()):
        path = root / record["path"]
        if (not path.is_file() or path.stat().st_size != int(record["size_bytes"])
                or _sha256(path) != record["sha256"]):
            raise ValueError(f"observation product identity mismatch: {record['path']}")
    return manifest


def _verify_forcing(config: ObservationReleaseConfig, site: str) -> int:
    snapshot_root = Path(config.snapshot_root).expanduser().resolve()
    snapshot_path = snapshot_root / "manifests" / "dataset_snapshot_r0001.json"
    if _sha256(snapshot_path) != config.snapshot_sha256:
        raise ValueError("forcing snapshot identity mismatch")
    with Dataset(str(snapshot_root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
        time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
        time_var = dataset.variables["time"]
        if str(getattr(time_var, "units", "")) != "hours since 2018-01-01 00:00:00":
            raise ValueError("forcing time units mismatch")
        if str(getattr(time_var, "calendar", "")) != "noleap":
            raise ValueError("forcing calendar mismatch")
    if time.shape != (61320,) or not np.array_equal(time, np.arange(61320, dtype=np.int64)):
        raise ValueError("forcing time axis mismatch")
    return int(time.size)


def _hourly_operator(hourly: xr.Dataset, variable: str, rmse: float) -> FluxObservationOperator:
    prefix = variable.upper()
    value_name = "GPP_gated" if prefix == "GPP" else "SR"
    dimension = "gpp_time" if prefix == "GPP" else "sr_time"
    valid = np.asarray(hourly[f"{prefix}_valid"].values, dtype=np.int8) == 1
    values = np.asarray(hourly[value_name].values, dtype=np.float64)
    sigma = np.asarray(hourly[f"{prefix}_obs_sigma"].values, dtype=np.float64)
    hours = np.asarray(hourly[dimension].values, dtype=np.int64)
    normalized = np.asarray(hourly[f"{prefix}_normalized_time_unix_ns"].values, dtype=np.int64)
    if not np.array_equal(_noleap_hours(normalized), hours):
        raise ValueError(f"{prefix} timestamp/canonical-hour mismatch")
    valid &= hours >= 720
    indices = np.flatnonzero(valid)
    if indices.size == 0 or not np.all(np.isfinite(values[indices])) or not np.all(np.isfinite(sigma[indices])):
        raise ValueError(f"{prefix} valid hourly observation mismatch")
    groups = tuple(_readonly(np.asarray([hours[index]]), np.int64) for index in indices)
    return FluxObservationOperator(
        prefix, "hourly", _readonly(values[indices], np.float64),
        _readonly(sigma[indices], np.float64), groups, float(rmse),
    )


def _daily_operator(
    hourly: xr.Dataset, daily: xr.Dataset, variable: str, rmse: float,
) -> FluxObservationOperator:
    prefix = variable.upper()
    value_name = "GPP_gated" if prefix == "GPP" else "SR"
    dimension = "gpp_time" if prefix == "GPP" else "sr_time"
    day_dimension = "gpp_day" if prefix == "GPP" else "sr_day"
    threshold = 18 if prefix == "GPP" else 22
    hourly_value = np.asarray(hourly[value_name].values, dtype=np.float64)
    hourly_sigma = np.asarray(hourly[f"{prefix}_obs_sigma"].values, dtype=np.float64)
    hourly_valid = np.asarray(hourly[f"{prefix}_valid"].values, dtype=np.int8) == 1
    hourly_hours = np.asarray(hourly[dimension].values, dtype=np.int64)
    day_values = np.asarray(daily[value_name].values, dtype=np.float64)
    day_sigma = np.asarray(daily[f"{prefix}_obs_sigma"].values, dtype=np.float64)
    day_count = np.asarray(daily[f"{prefix}_valid_hour_count"].values, dtype=np.int64)
    day_eligible = np.asarray(daily[f"{prefix}_eligible"].values, dtype=np.int8) == 1
    day_index = np.asarray(daily[f"{prefix}_source_hour_index"].values, dtype=np.int64)
    day_coordinate = np.asarray(daily[day_dimension].values, dtype=np.int64)
    observations: list[float] = []
    sigmas: list[float] = []
    groups: list[np.ndarray] = []
    for row in np.flatnonzero(day_eligible):
        source_indices = day_index[row]
        source_indices = source_indices[source_indices >= 0]
        if np.any(source_indices >= hourly_value.size):
            raise ValueError(f"{prefix} daily source index outside hourly product")
        source_indices = source_indices[hourly_valid[source_indices]]
        if source_indices.size != day_count[row] or source_indices.size < threshold:
            raise ValueError(f"{prefix} reconstructed daily valid-hour count mismatch")
        forcing_hours = hourly_hours[source_indices]
        if not np.all(forcing_hours // 24 == day_coordinate[row]):
            raise ValueError(f"{prefix} daily source hours map to the wrong canonical day")
        observed = float(np.mean(hourly_value[source_indices]))
        sigma = float(np.sqrt(np.mean(np.square(hourly_sigma[source_indices]))))
        if not np.isclose(observed, day_values[row], rtol=0.0, atol=1e-12):
            raise ValueError(f"{prefix} reconstructed daily observation mismatch")
        if not np.isclose(sigma, day_sigma[row], rtol=0.0, atol=1e-12):
            raise ValueError(f"{prefix} reconstructed daily sigma mismatch")
        observations.append(observed)
        sigmas.append(sigma)
        groups.append(_readonly(forcing_hours, np.int64))
    return FluxObservationOperator(
        prefix, "daily", _readonly(np.asarray(observations), np.float64),
        _readonly(np.asarray(sigmas), np.float64), tuple(groups), float(rmse),
    )


def load_three_stage_observations(
    *, site: str, config: ObservationReleaseConfig,
) -> ThreeStageObservationContext:
    if site not in SITES:
        raise ValueError(f"unsupported observation site: {site}")
    manifest = _verify_release(config)
    forcing_hours = _verify_forcing(config, site)
    root = Path(config.release_root).expanduser().resolve()
    site_root = root / "sites" / site
    with xr.open_dataset(site_root / "flux_hourly.nc") as opened:
        hourly = opened.load()
    with xr.open_dataset(site_root / "flux_daily.nc") as opened:
        daily = opened.load()
    with xr.open_dataset(site_root / "uncertainty.nc") as opened:
        uncertainty = opened.load()
    if hourly.attrs.get("schema") != "mcmc-observation-flux-hourly-v1" or hourly.attrs.get("site") != site:
        raise ValueError("hourly observation schema/site mismatch")
    if daily.attrs.get("schema") != "mcmc-observation-flux-daily-v1" or daily.attrs.get("site") != site:
        raise ValueError("daily observation schema/site mismatch")
    if uncertainty.attrs.get("schema") != "mcmc-fixed-uncertainty-v1" or uncertainty.attrs.get("site") != site:
        raise ValueError("uncertainty schema/site mismatch")
    if hourly.attrs.get("calendar") != "noleap" or daily.attrs.get("calendar") != "noleap":
        raise ValueError("observation calendar mismatch")
    if int(hourly.attrs.get("history_hours", -1)) != 720:
        raise ValueError("observation history gate mismatch")
    if int(daily.attrs.get("gpp_min_hours", -1)) != 18 or int(daily.attrs.get("sr_min_hours", -1)) != 22:
        raise ValueError("observation daily threshold mismatch")
    if hourly.attrs.get("flux_units") != "gC/m^2/day" or daily.attrs.get("flux_units") != "gC/m^2/day":
        raise ValueError("observation flux units mismatch")
    resolutions = tuple(str(value) for value in uncertainty.resolution.values.tolist())
    if resolutions != RESOLUTIONS:
        raise ValueError("uncertainty resolution order mismatch")
    rmse = {
        ("GPP", resolution): float(uncertainty.GPP_surrogate_rmse.values[index])
        for index, resolution in enumerate(resolutions)
    }
    rmse.update({
        ("SR", resolution): float(uncertainty.SR_surrogate_rmse.values[index])
        for index, resolution in enumerate(resolutions)
    })
    if not all(np.isfinite(value) and value > 0.0 for value in rmse.values()):
        raise ValueError("surrogate RMSE must be positive and finite")
    flux = {
        (variable, "hourly"): _hourly_operator(hourly, variable, rmse[(variable, "hourly")])
        for variable in ("GPP", "SR")
    }
    flux.update({
        (variable, "daily"): _daily_operator(hourly, daily, variable, rmse[(variable, "daily")])
        for variable in ("GPP", "SR")
    })
    soil_payload = json.loads((site_root / "soil_cn.json").read_text(encoding="utf-8"))
    if soil_payload.get("schema") != "mcmc-soil-cn-observation-v1" or soil_payload.get("site") != site:
        raise ValueError("soil C/N schema/site mismatch")
    observed_stocks = _readonly(np.asarray([
        soil_payload["TOTSOMC_gC_m2"], soil_payload["TOTSOMN_gN_m2"],
    ]), np.float64)
    depth_fraction = _readonly(uncertainty.depth_fraction.values, np.float64)
    total_bias = _readonly(uncertainty.total_log_bias_correction.values, np.float64)
    covariance_by_cv: dict[float, np.ndarray] = {}
    for index, cv_value in enumerate(np.asarray(uncertainty.cv.values, dtype=np.float64)):
        covariance = _readonly(uncertainty.total_log_covariance.values[index], np.float64)
        if covariance.shape != (2, 2) or not np.array_equal(covariance, covariance.T):
            raise ValueError("total C/N covariance symmetry mismatch")
        try:
            np.linalg.cholesky(covariance)
        except np.linalg.LinAlgError as exc:
            raise ValueError("total C/N covariance is not positive definite") from exc
        covariance_by_cv[float(cv_value)] = covariance
    if tuple(covariance_by_cv) != (0.2, 0.3, 0.5):
        raise ValueError("C/N observational CV contract mismatch")
    records = {item["path"]: item["sha256"] for item in manifest["files"]}
    sources = manifest["source_identities"]
    return ThreeStageObservationContext(
        site=site,
        flux=MappingProxyType(dict(flux)),
        soil_cn=SoilCNContext(
            observed_stocks, depth_fraction, total_bias,
            MappingProxyType(dict(covariance_by_cv)),
        ),
        release_catalog_sha256=config.catalog_sha256,
        release_manifest_sha256=config.release_manifest_sha256,
        validation_report_sha256=config.validation_report_sha256,
        forcing_hours=forcing_hours,
        uncertainty_product_sha256=records[f"sites/{site}/uncertainty.nc"],
        soil_product_sha256=records[f"sites/{site}/soil_cn.json"],
        depth_source_sha256=sources[f"{site}_depth"],
    )
