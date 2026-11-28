#!/usr/bin/env python3
"""Exercise both published observations through the inference-facing entry point."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

from development.mcmc_optimization.slurm.iter003.run_iter003 import release_config
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA, ObservationReleaseConfig, _daily_operator,
)
from model_ELM.mcmc_three_stage_posterior import load_three_stage_posterior


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def config(path: Path) -> ObservationReleaseConfig:
    values = json.loads(path.read_text())
    require(values["schema"] == CONFIG_SCHEMA, "selection schema")
    return ObservationReleaseConfig(**values)


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_reference(frozen, site: str, variable: str):
    prefix = f"{site}_{variable}"
    eligible = np.asarray(frozen[f"{prefix}_daily_eligible"], dtype=bool)
    hour_valid = np.asarray(frozen[f"{prefix}_hourly_valid"], dtype=bool)
    hour_values = np.asarray(frozen[f"{prefix}_hourly_values"], dtype=np.float64)
    hour_sigma = np.asarray(frozen[f"{prefix}_hourly_sigma"], dtype=np.float64)
    hour_axis = np.asarray(frozen[f"{prefix}_hourly_hours"], dtype=np.int64)
    groups, means, sigmas = [], [], []
    for row in np.flatnonzero(eligible):
        indices = np.asarray(frozen[f"{prefix}_daily_source_index"][row], dtype=np.int64)
        indices = indices[indices >= 0]
        indices = indices[hour_valid[indices]]
        groups.append(hour_axis[indices])
        means.append(float(np.mean(hour_values[indices])))
        sigmas.append(float(np.sqrt(np.mean(np.square(hour_sigma[indices])))))
    np.testing.assert_allclose(means, np.asarray(frozen[f"{prefix}_daily_mean"])[eligible], rtol=0, atol=1e-12)
    np.testing.assert_allclose(sigmas, np.asarray(frozen[f"{prefix}_daily_sigma"])[eligible], rtol=0, atol=1e-12)
    return groups, np.asarray(means), np.asarray(sigmas)


def check_posterior(posterior, selected: ObservationReleaseConfig, site: str, expected_min: int, frozen) -> dict:
    context = posterior.observations
    require(context.release_id == selected.release_id, "selected release context identity")
    require(context.release_catalog_sha256 == selected.catalog_sha256, "selected catalog context identity")
    require(context.release_manifest_sha256 == selected.release_manifest_sha256, "selected manifest context identity")
    require(posterior._provenance()["observation_release_id"] == selected.release_id, "target provenance identity")
    counts = {}
    for variable in ("GPP", "SR"):
        with xr.open_dataset(Path(selected.release_root) / "sites" / site / "flux_hourly.nc") as ds:
            hourly = ds.load()
        hour_dim = "gpp_time" if variable == "GPP" else "sr_time"
        value_name = "GPP_gated" if variable == "GPP" else "SR"
        hour_mask = np.asarray(hourly[f"{variable}_valid"].values, dtype=bool)
        hour_mask &= np.asarray(hourly[hour_dim].values, dtype=np.int64) >= 720
        if selected.release_id == "release_0001":
            prefix = f"{site}_{variable}"
            np.testing.assert_array_equal(hourly[f"{variable}_valid"].values, frozen[f"{prefix}_hourly_valid"])
            np.testing.assert_allclose(hourly[value_name].values, frozen[f"{prefix}_hourly_values"], rtol=0, atol=0, equal_nan=True)
            np.testing.assert_allclose(hourly[f"{variable}_obs_sigma"].values, frozen[f"{prefix}_hourly_sigma"], rtol=0, atol=0, equal_nan=True)
        hour_operator = context.operator(variable, "hourly")
        expected_hours = np.asarray(hourly[hour_dim].values[hour_mask], dtype=np.int64)
        require(hour_operator.count == len(expected_hours), f"{site} {variable} hourly mask count")
        require(np.array_equal(np.asarray([group[0] for group in hour_operator.forcing_hour_groups]), expected_hours),
                f"{site} {variable} hourly groups")
        np.testing.assert_allclose(hour_operator.observed, hourly[value_name].values[hour_mask], rtol=0, atol=0)
        np.testing.assert_allclose(hour_operator.observation_sigma,
                                   hourly[f"{variable}_obs_sigma"].values[hour_mask], rtol=0, atol=0)
        if selected.release_id == "release_0001":
            reference_groups, means, sigmas = frozen_reference(frozen, site, variable)
        else:
            reference_groups, means, sigmas = independent_new_reference(Path(selected.release_root), site, variable)
        operator = context.operator(variable, "daily")
        require(operator.count == len(reference_groups), f"{site} {variable} daily count")
        np.testing.assert_allclose(operator.observed, means, rtol=0, atol=1e-12)
        np.testing.assert_allclose(operator.observation_sigma, sigmas, rtol=0, atol=1e-12)
        for actual, expected in zip(operator.forcing_hour_groups, reference_groups):
            require(np.array_equal(actual, expected), f"{site} {variable} forcing group mismatch")
            require(len(actual) >= expected_min and len(np.unique(actual)) == len(actual), f"{site} {variable} support mismatch")
        if expected_min == 24:
            require(all(len(group) == 24 for group in reference_groups), f"{site} {variable} not full day")
        counts[variable] = operator.count
    with xr.open_dataset(Path(selected.release_root) / "sites" / site / "uncertainty.nc") as ds:
        uncertainty = ds.load()
    np.testing.assert_array_equal(context.soil_cn.depth_fraction, uncertainty.depth_fraction.values)
    np.testing.assert_array_equal(context.soil_cn.total_bias_correction, uncertainty.total_log_bias_correction.values)
    for name in uncertainty.data_vars:
        np.testing.assert_array_equal(uncertainty[name].values, frozen[f"{site}_uncertainty_{name}"])
    soil = json.loads((Path(selected.release_root) / "sites" / site / "soil_cn.json").read_text())
    require(file_sha(Path(selected.release_root) / "sites" / site / "soil_cn.json") == str(frozen[f"{site}_soil_json_sha256"]),
            f"{site} inherited soil bytes")
    np.testing.assert_allclose(context.soil_cn.observed_stocks,
                               [soil["TOTSOMC_gC_m2"], soil["TOTSOMN_gN_m2"]], rtol=0, atol=0)
    return counts


def independent_new_reference(root: Path, site: str, variable: str):
    with xr.open_dataset(root / "sites" / site / "flux_hourly.nc") as ds: hourly = ds.load()
    with xr.open_dataset(root / "sites" / site / "flux_daily.nc") as ds: daily = ds.load()
    value = "GPP_gated" if variable == "GPP" else "SR"
    hour_dim = "gpp_time" if variable == "GPP" else "sr_time"
    groups, means, sigmas = [], [], []
    for row in np.flatnonzero(daily[f"{variable}_eligible"].values):
        indices = np.asarray(daily[f"{variable}_source_hour_index"].values[row], dtype=np.int64)
        indices = indices[indices >= 0]
        indices = indices[np.asarray(hourly[f"{variable}_valid"].values[indices], dtype=bool)]
        groups.append(np.asarray(hourly[hour_dim].values[indices], dtype=np.int64))
        means.append(float(np.mean(hourly[value].values[indices])))
        sigmas.append(float(np.sqrt(np.mean(np.square(hourly[f"{variable}_obs_sigma"].values[indices])))))
    return groups, np.asarray(means), np.asarray(sigmas)


def rejections(old_config: ObservationReleaseConfig, old_root: Path) -> dict:
    from dataclasses import replace
    cases = {}
    for label, changed in (("catalog_hash", {"catalog_sha256": "0"*64}),
                           ("manifest_hash", {"release_manifest_sha256": "0"*64}),
                           ("schema", {"schema": "unsupported"}),
                           ("forcing_compatibility", {"snapshot_sha256": "0"*64}),
                           ("release_identity", {"release_id": "incorrect"})):
        try:
            replace(old_config, **changed).validate()
            if label in ("catalog_hash", "manifest_hash"):
                from model_ELM.mcmc_three_stage_observations import load_three_stage_observations
                load_three_stage_observations(site="ABBY", config=replace(old_config, **changed))
        except (ValueError, FileNotFoundError):
            cases[label] = "rejected"
        else:
            raise RuntimeError(f"{label} fixture accepted")
    with tempfile.TemporaryDirectory(prefix="iter007_release_schema_") as temporary:
        fixture = Path(temporary) / old_config.release_id
        shutil.copytree(old_root, fixture)
        manifest_path = fixture / "release_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["schema"] = "unsupported-release-manifest"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        catalog_path = fixture / "catalog.json"
        catalog = json.loads(catalog_path.read_text())
        catalog["release_path"] = str(fixture)
        catalog["release_manifest_sha256"] = file_sha(manifest_path)
        catalog_path.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n")
        from model_ELM.mcmc_three_stage_observations import load_three_stage_observations
        fixture_config = replace(old_config, release_root=fixture, catalog_sha256=file_sha(catalog_path),
                                 release_manifest_sha256=file_sha(manifest_path))
        try:
            load_three_stage_observations(site="ABBY", config=fixture_config)
        except ValueError as exc:
            require("manifest contract mismatch" in str(exc), "wrong unsupported-schema rejection")
            cases["release_schema"] = "rejected"
        else:
            raise RuntimeError("unsupported release schema accepted")
    with xr.open_dataset(old_root / "sites/ABBY/flux_hourly.nc") as ds: hourly = ds.load()
    with xr.open_dataset(old_root / "sites/ABBY/flux_daily.nc") as ds: daily = ds.load()
    row = int(np.flatnonzero(daily.GPP_eligible.values)[0])
    for label, edit in (("coverage", "count"), ("hourly_index", "index")):
        broken = daily.copy(deep=True)
        if edit == "count": broken.GPP_valid_hour_count.values[row] += 1
        else: broken.GPP_source_hour_index.values[row, 0] = hourly.sizes["gpp_time"] + 1
        try:
            _daily_operator(hourly, broken, "GPP", 0.5)
        except ValueError:
            cases[label] = "rejected"
        else:
            raise RuntimeError(f"{label} fixture accepted")
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection-a", type=Path, required=True)
    parser.add_argument("--selection-b", type=Path, required=True)
    parser.add_argument("--iter004-config", type=Path, required=True)
    parser.add_argument("--frozen-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    old_selection = config(args.selection_a)
    new_selection = config(args.selection_b)
    require(old_selection.release_id == "release_0001" and new_selection.release_id == "release_0002", "selection order")
    base = json.loads(args.iter004_config.read_text())
    surrogate = release_config(base)
    audit = json.loads((args.frozen_reference.parent / "source_audit.json").read_text())
    require(file_sha(args.frozen_reference) == audit["frozen_reference_sha256"], "frozen reference hash mismatch")
    frozen = np.load(args.frozen_reference, allow_pickle=False)
    result = {"schema":"mcmc-iter007-integration-v1", "result":"pass", "selections":{}, "rejections":{}}
    for selected, min_count in ((old_selection, 18), (new_selection, 24), (old_selection, 18)):
        one = {}
        for site in ("ABBY", "JERC"):
            posterior = load_three_stage_posterior(site=site, prior_id="ppe1", prior_root=base["ppe1_root"],
                                                   surrogate_release=surrogate, observation_release=selected,
                                                   gpp_resolution="daily", sr_resolution="daily", cn_observation_cv=.3,
                                                   include_cn=True, start=720, end=61320)
            one[site] = check_posterior(posterior, selected, site, min_count, frozen)
        result["selections"][selected.release_id] = one
    result["rejections"] = rejections(old_selection, Path(old_selection.release_root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("MCMC_ITER007_DUAL_RELEASE_INTEGRATION_PASS")


if __name__ == "__main__": main()
