#!/usr/bin/env python3
"""Locked Iter003 validation and benchmark driver."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import resource
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from netCDF4 import Dataset

from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_likelihood import gaussian_log_likelihood, joint_cn_log_likelihood
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA as OBS_CONFIG_SCHEMA,
    ObservationReleaseConfig,
    load_three_stage_observations,
)
from model_ELM.mcmc_three_stage_posterior import ThreeStagePosterior
from model_ELM.mcmc_three_stage_release import (
    CONFIG_SCHEMA as RELEASE_CONFIG_SCHEMA,
    IMPLEMENTATION_ID,
    ThreeStageReleaseConfig,
    load_three_stage_release,
)
from model_ELM.three_stage_gpp import FORCING_NAMES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_config(path: Path) -> dict[str, Any]:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    require(cfg.get("schema") == "mcmc-optimization-iter003-config-v1", "config schema mismatch")
    require(cfg.get("maximum_submissions") == 10, "submission ceiling mismatch")
    require(cfg.get("shared_unchanged_scope_retries") == 4, "shared retry budget mismatch")
    require(cfg.get("prior_id") == PPE1, "active prior mismatch")
    return cfg


def release_config(cfg: dict[str, Any]) -> ThreeStageReleaseConfig:
    return ThreeStageReleaseConfig(
        schema=RELEASE_CONFIG_SCHEMA,
        implementation_id=IMPLEMENTATION_ID,
        prior_id=cfg["prior_id"],
        release_id="release_0001",
        release_root=Path(cfg["surrogate_release_root"]),
        snapshot_root=Path(cfg["snapshot_root"]),
        uncertainty_root=Path(cfg["uncertainty_root"]),
        uncertainty_handoff_sha256=cfg["uncertainty_handoff_sha256"],
        uncertainty_manifest_sha256=cfg["uncertainty_manifest_sha256"],
        uncertainty_validation_sha256=cfg["uncertainty_validation_sha256"],
        source_file=Path(cfg["surrogate_source_file"]),
        release_manifest_sha256=cfg["surrogate_release_manifest_sha256"],
        catalog_sha256=cfg["surrogate_catalog_sha256"],
        snapshot_sha256=cfg["snapshot_sha256"],
    )


def observation_config(cfg: dict[str, Any]) -> ObservationReleaseConfig:
    return ObservationReleaseConfig(
        schema=OBS_CONFIG_SCHEMA,
        release_root=Path(cfg["observation_release_root"]),
        snapshot_root=Path(cfg["snapshot_root"]),
        catalog_sha256=cfg["observation_catalog_sha256"],
        release_manifest_sha256=cfg["observation_manifest_sha256"],
        validation_report_sha256=cfg["observation_validation_sha256"],
        snapshot_sha256=cfg["snapshot_sha256"],
    )


def source_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def preflight(cfg: dict[str, Any], output: Path) -> None:
    runtime = Path(cfg["runtime_root"])
    require(Path(cfg["repository_root"]).resolve() == Path.cwd().resolve(), "repository root mismatch")
    require(source_bytes(runtime) <= int(cfg["storage_cap_bytes"]), "Iter003 storage cap exceeded")
    prior = Prior18.from_directory(PPE1, cfg["ppe1_root"])
    theta = prior.inverse_unit(np.full(18, 0.5))
    require(np.isfinite(prior.log_density(theta)), "PPE1 midpoint prior is invalid")
    gaussian = gaussian_log_likelihood(np.asarray([1.0]), np.asarray([1.1]), np.asarray([0.2]), 0.3)
    cn = joint_cn_log_likelihood(np.asarray([10.0, 1.0]), np.asarray([11.0, 1.1]),
                                 np.asarray([0.8, 0.8]), np.zeros(2), np.eye(2))
    require(np.isfinite(gaussian) and np.isfinite(cn), "pure-kernel preflight failed")
    dump_json(output, {
        "schema": "mcmc-iter003-preflight-v1", "result": "pass",
        "prior_id": PPE1, "parameter_count": 18,
        "pure_gaussian": gaussian, "pure_cn": cn,
        "storage_bytes": source_bytes(runtime),
    })
    print("MCMC_ITER003_PREFLIGHT_PASS")


def component(cfg: dict[str, Any], output: Path) -> None:
    prior = Prior18.from_directory(PPE1, cfg["ppe1_root"])
    before = time.perf_counter()
    loaded = load_three_stage_release(prior=prior, config=release_config(cfg))
    release_seconds = time.perf_counter() - before
    sites = {}
    for site in cfg["sites"]:
        started = time.perf_counter()
        observations = load_three_stage_observations(site=site, config=observation_config(cfg))
        sites[site] = {
            "context_seconds": time.perf_counter() - started,
            "counts": {
                f"{variable}_{resolution}": observations.operator(variable, resolution).count
                for variable in ("GPP", "SR") for resolution in ("hourly", "daily")
            },
        }
    dump_json(output, {
        "schema": "mcmc-iter003-component-v1", "result": "pass",
        "release_loading_seconds": release_seconds,
        "release_loading_components": loaded.loading_seconds,
        "compatibility_layer": loaded.compatibility_layer,
        "sites": sites,
    })
    print("MCMC_ITER003_COMPONENT_PASS")


def scalar_gaussian_reference(obs: np.ndarray, pred: np.ndarray, sigma: np.ndarray, rmse: float) -> float:
    terms = []
    for observed, predicted, uncertainty in zip(obs.tolist(), pred.tolist(), sigma.tolist()):
        variance = uncertainty * uncertainty + rmse * rmse
        terms.append(-0.5 * ((observed - predicted) ** 2 / variance + math.log(2.0 * math.pi * variance)))
    return math.fsum(terms)


def closed_form_cn_reference(obs: np.ndarray, pred: np.ndarray, fraction: np.ndarray,
                             bias: np.ndarray, covariance: np.ndarray) -> float:
    residual = np.log(obs) - np.log(fraction * pred) + bias
    a = float(covariance[0, 0]); b = float(covariance[0, 1]); d = float(covariance[1, 1])
    determinant = a * d - b * b
    require(determinant > 0.0, "reference C/N determinant is nonpositive")
    quadratic = (d * residual[0] ** 2 - 2.0 * b * residual[0] * residual[1]
                 + a * residual[1] ** 2) / determinant
    return float(-0.5 * (quadratic + math.log(determinant) + 2.0 * math.log(2.0 * math.pi)))


def forcing(cfg: dict[str, Any], site: str, end: int) -> tuple[dict[str, np.ndarray], np.ndarray]:
    path = Path(cfg["snapshot_root"]) / "sites" / site / "input_data_v1.nc"
    with Dataset(str(path), "r") as dataset:
        forcing_values = {name: np.asarray(dataset.variables[name][:end], dtype=np.float64) for name in FORCING_NAMES}
        time_values = np.asarray(dataset.variables["time"][:end], dtype=np.int64)
    return forcing_values, time_values


def integrated(cfg: dict[str, Any], output: Path) -> None:
    prior = Prior18.from_directory(PPE1, cfg["ppe1_root"])
    loaded = load_three_stage_release(prior=prior, config=release_config(cfg))
    theta = prior.inverse_unit(np.full(18, 0.5))
    second = prior.inverse_unit(np.linspace(0.2, 0.8, 18))
    rows: list[dict[str, Any]] = []
    reference_cases: list[dict[str, Any]] = []
    site_reports: dict[str, Any] = {}
    for site in cfg["sites"]:
        observations = load_three_stage_observations(site=site, config=observation_config(cfg))
        start = int(cfg["full_window_start"]); end = int(cfg["full_window_end"])
        forcing_values, time_values = forcing(cfg, site, end)
        first = loaded.engine.predict(theta, site=site, forcing=forcing_values, time=time_values,
                                      start=start, end=end, member_chunk=1)
        require(first.provenance["contains_elm_truth"] is False, "target leakage provenance")
        full_stocks = np.asarray([first.totsomc[0], first.totsomn[0]])
        soil = observations.soil_cn
        cv_results = {}
        for cv in (0.2, 0.3, 0.5):
            ll_value = joint_cn_log_likelihood(
                soil.observed_stocks, full_stocks, soil.depth_fraction,
                soil.total_bias_correction, soil.covariance_by_cv[cv],
            )
            cn_reference = closed_form_cn_reference(
                soil.observed_stocks, full_stocks, soil.depth_fraction,
                soil.total_bias_correction, soil.covariance_by_cv[cv],
            )
            require(np.isclose(ll_value, cn_reference, rtol=1e-12, atol=1e-10),
                    f"{site} C/N CV {cv} reference mismatch")
            cv_results[str(cv)] = ll_value
            reference_cases.append({
                "site": site, "kind": "joint_cn", "cn_observation_cv": cv,
                "actual": ll_value, "reference": cn_reference,
                "absolute_difference": abs(ll_value - cn_reference),
            })
        ll_cn = cv_results["0.3"]
        component_by_resolution: dict[tuple[str, str], float] = {}
        for variable, values in (("GPP", first.gpp[0]), ("SR", first.sr[0])):
            for resolution in ("hourly", "daily"):
                operator = observations.operator(variable, resolution).window(start, end)
                prediction = operator.aggregate_predictions(values, start)
                actual = gaussian_log_likelihood(operator.observed, prediction,
                                                 operator.observation_sigma, operator.surrogate_rmse)
                reference = scalar_gaussian_reference(operator.observed, prediction,
                                                      operator.observation_sigma, operator.surrogate_rmse)
                require(np.isclose(actual, reference, rtol=1e-12, atol=1e-10),
                        f"{site} {variable}/{resolution} reference mismatch")
                component_by_resolution[(variable, resolution)] = actual
                reference_cases.append({"site": site, "kind": f"{variable}_{resolution}",
                                        "actual": actual, "reference": reference,
                                        "absolute_difference": abs(actual-reference)})
        log_prior = float(prior.log_density(theta))
        for gpp_resolution, sr_resolution in cfg["resolution_combinations"]:
            ll_gpp = component_by_resolution[("GPP", gpp_resolution)]
            ll_sr = component_by_resolution[("SR", sr_resolution)]
            total = log_prior + ll_gpp + ll_sr + ll_cn
            rows.append({
                "site": site, "gpp_resolution": gpp_resolution, "sr_resolution": sr_resolution,
                "include_cn": True, "cn_observation_cv": 0.3, "log_prior": log_prior,
                "log_likelihood_gpp": ll_gpp, "log_likelihood_sr": ll_sr,
                "log_likelihood_cn": ll_cn, "log_posterior": total,
                "n_gpp": observations.operator("GPP", gpp_resolution).count,
                "n_sr": observations.operator("SR", sr_resolution).count,
            })
        smoke_start = int(cfg["benchmark"]["sites"][site]["start"])
        smoke_end = smoke_start + 48
        smoke_forcing, smoke_time = forcing(cfg, site, smoke_end)
        smoke_first = loaded.engine.predict(
            theta, site=site, forcing=smoke_forcing, time=smoke_time,
            start=smoke_start, end=smoke_end, member_chunk=1,
        )
        smoke_repeat = loaded.engine.predict(
            theta, site=site, forcing=smoke_forcing, time=smoke_time,
            start=smoke_start, end=smoke_end, member_chunk=1,
        )
        prediction_checksums = {}
        for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
            first_array = np.asarray(getattr(smoke_first, name))
            np.testing.assert_array_equal(first_array, getattr(smoke_repeat, name))
            prediction_checksums[name] = hashlib.sha256(first_array.tobytes()).hexdigest()
        smoke_results = []
        for gpp_resolution, sr_resolution in cfg["resolution_combinations"]:
            posterior = ThreeStagePosterior(
                site=site, prior=prior, release=loaded, observations=observations,
                gpp_resolution=gpp_resolution, sr_resolution=sr_resolution,
                cn_observation_cv=0.3, include_cn=True,
                start=smoke_start, end=smoke_end, member_chunk=2,
            )
            scalar = posterior.evaluate(theta)
            replay = posterior.evaluate(theta)
            invalid_for_batch = theta.copy(); invalid_for_batch[17] = invalid_for_batch[16]
            batch = posterior.evaluate_batch(np.vstack((theta, invalid_for_batch, second)))
            require(scalar.log_posterior == replay.log_posterior, "posterior replay mismatch")
            require(np.isclose(scalar.log_posterior, batch[0].log_posterior, rtol=1e-12, atol=1e-10),
                    "scalar/batch mismatch")
            require(len(batch) == 3 and batch[0].surrogate_evaluated
                    and not batch[1].surrogate_evaluated and batch[2].surrogate_evaluated,
                    "mixed-validity batch ordering mismatch")
            require(np.isclose(scalar.log_posterior, scalar.log_prior + scalar.log_likelihood_gpp
                               + scalar.log_likelihood_sr + scalar.log_likelihood_cn,
                               rtol=0.0, atol=1e-10), "posterior component sum mismatch")
            sampler = prior.coordinate_transform.physical_to_sampler(theta)
            sampling = posterior.evaluate_sampling(sampler)
            require(np.isclose(sampling.log_sampling_posterior,
                               scalar.log_posterior + sampling.log_abs_det_jacobian,
                               rtol=1e-12, atol=1e-10), "sampling Jacobian mismatch")
            smoke_results.append({
                "gpp_resolution": gpp_resolution, "sr_resolution": sr_resolution,
                "scalar_log_posterior": scalar.log_posterior,
                "batch_log_posterior": batch[0].log_posterior,
                "n_gpp": scalar.n_gpp, "n_sr": scalar.n_sr,
            })
        flux_only = ThreeStagePosterior(
            site=site, prior=prior, release=loaded, observations=observations,
            gpp_resolution="daily", sr_resolution="daily", cn_observation_cv=0.3,
            include_cn=False, start=smoke_start, end=smoke_end,
        ).evaluate(theta)
        require(flux_only.log_likelihood_cn == 0.0, "disabled C/N component is not zero")
        invalid = theta.copy(); invalid[17] = invalid[16]
        rejected = ThreeStagePosterior(
            site=site, prior=prior, release=loaded, observations=observations,
            gpp_resolution="daily", sr_resolution="daily", cn_observation_cv=0.3,
            include_cn=True, start=smoke_start, end=smoke_end,
        ).evaluate(invalid)
        require(rejected.log_posterior == -np.inf and not rejected.surrogate_evaluated,
                "invalid prior vector was not rejected before surrogate evaluation")
        site_reports[site] = {
            "full_prediction_reused_across_resolution_operators": True,
            "contains_elm_truth": False,
            "smoke_resolution_results": smoke_results,
            "flux_only_cn_component": flux_only.log_likelihood_cn,
            "invalid_support_rejected_before_surrogate": True,
            "mixed_validity_batch_ordering": True,
            "bounded_surrogate_replay_exact": True,
            "bounded_prediction_checksums": prediction_checksums,
            "cn_by_cv": cv_results,
        }
        site_rows = [row for row in rows if row["site"] == site]
        for resolution in ("hourly", "daily"):
            gpp_terms = {row["log_likelihood_gpp"] for row in site_rows
                         if row["gpp_resolution"] == resolution}
            sr_terms = {row["log_likelihood_sr"] for row in site_rows
                        if row["sr_resolution"] == resolution}
            require(len(gpp_terms) == 1, f"{site} GPP component changed with SR resolution")
            require(len(sr_terms) == 1, f"{site} SR component changed with GPP resolution")
        site_reports[site]["resolution_component_isolation"] = True
    results_root = Path(cfg["runtime_root"]) / "results"
    csv_path = results_root / "resolution_parity_summary.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    dump_json(results_root / "likelihood_reference_tests.json", {
        "schema": "mcmc-iter003-likelihood-reference-v1", "result": "pass",
        "rtol": 1e-12, "atol": 1e-10, "cases": reference_cases,
        "production_kernels_used_for_reference": False,
    })
    dump_json(output, {
        "schema": "mcmc-iter003-posterior-validation-v1", "result": "pass",
        "sites": site_reports,
        "resolution_rows": len(rows),
        "reference_case_count": len(reference_cases),
        "full_window": [cfg["full_window_start"], cfg["full_window_end"]],
        "full_window_surrogate_calls_per_site": 1,
        "note": "one full-window prediction per site reused across all resolution operators; deterministic replay is tested on bounded smoke windows",
        "gate_evidence": {
            "dependency_integrity": True,
            "observation_alignment": True,
            "all_resolution_combinations": True,
            "gaussian_reference": True,
            "joint_cn_reference": True,
            "prior_posterior_and_jacobian": True,
            "determinism_batching_and_no_leakage": True,
            "failure_handling_and_compatibility": True
        }
    })
    print("MCMC_ITER003_INTEGRATED_PASS")


def fixture_units(count: int = 16) -> np.ndarray:
    result = np.empty((count, 18), dtype=np.float64)
    for row in range(count):
        for column in range(18):
            result[row, column] = 0.2 + 0.6 * (((row * 37 + column * 17) % 97) / 96.0)
    return result


def benchmark(cfg: dict[str, Any], output: Path) -> None:
    benchmark_started = time.perf_counter()
    prior = Prior18.from_directory(PPE1, cfg["ppe1_root"])
    release_started = time.perf_counter()
    loaded = load_three_stage_release(prior=prior, config=release_config(cfg))
    release_seconds = time.perf_counter() - release_started
    parameters = prior.inverse_unit(fixture_units())
    cells: list[dict[str, Any]] = []
    cold_measurements: list[dict[str, Any]] = []
    context_seconds: dict[str, float] = {}
    for site in cfg["sites"]:
        observed_started = time.perf_counter()
        observations = load_three_stage_observations(site=site, config=observation_config(cfg))
        context_seconds[site] = time.perf_counter() - observed_started
        start = int(cfg["benchmark"]["sites"][site]["start"])
        for window in cfg["benchmark"]["sites"][site]["windows"]:
            end = start + int(window)
            for gpp_resolution, sr_resolution in cfg["resolution_combinations"]:
                context_started = time.perf_counter()
                posterior = ThreeStagePosterior(
                    site=site, prior=prior, release=loaded, observations=observations,
                    gpp_resolution=gpp_resolution, sr_resolution=sr_resolution,
                    cn_observation_cv=0.3, include_cn=True, start=start, end=end, member_chunk=16,
                )
                posterior_context_seconds = time.perf_counter() - context_started
                cold_results, cold_components = posterior.evaluate_batch_timed(parameters[:1])
                require(np.isfinite(cold_results[0].log_posterior), "cold posterior is nonfinite")
                cold_measurements.append({
                    "site": site, "window_hours": int(window),
                    "gpp_resolution": gpp_resolution, "sr_resolution": sr_resolution,
                    "context_initialization_seconds": posterior_context_seconds,
                    "first_posterior_call_seconds": cold_components["total_seconds"],
                    "component_seconds": cold_components,
                })
                for batch_size in cfg["benchmark"]["batch_sizes"]:
                    batch = parameters[:int(batch_size)]
                    warm = []
                    component_timings = []
                    checksums = []
                    for _ in range(int(cfg["benchmark"]["warm_repetitions"])):
                        results, measured = posterior.evaluate_batch_timed(batch)
                        warm.append(measured["total_seconds"])
                        component_timings.append(measured)
                        values = np.asarray([item.log_posterior for item in results], dtype=np.float64)
                        require(np.all(np.isfinite(values)), "benchmark posterior contains nonfinite values")
                        checksums.append(hashlib.sha256(values.tobytes()).hexdigest())
                    require(len(set(checksums)) == 1, "benchmark deterministic checksum mismatch")
                    median = float(np.median(warm))
                    cells.append({
                        "site": site, "window_hours": int(window),
                        "gpp_resolution": gpp_resolution, "sr_resolution": sr_resolution,
                        "batch_size": int(batch_size), "warm_seconds": warm,
                        "median_seconds": median,
                        "seconds_per_candidate": median / int(batch_size),
                        "component_median_seconds": {
                            name: float(np.median([item[name] for item in component_timings]))
                            for name in ("prior_seconds", "surrogate_seconds",
                                         "alignment_likelihood_seconds", "total_seconds")
                        },
                        "component_repeat_seconds": component_timings,
                        "checksum": checksums[0], "n_gpp": posterior.gpp_operator.count,
                        "n_sr": posterior.sr_operator.count,
                    })
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    thresholds = cfg["benchmark"]["material_thresholds"]
    blockers = []
    for site in cfg["sites"]:
        for gpp_resolution, sr_resolution in cfg["resolution_combinations"]:
            annual = [item for item in cells if item["site"] == site and item["window_hours"] == 8760
                      and item["gpp_resolution"] == gpp_resolution and item["sr_resolution"] == sr_resolution]
            scalar = next(item for item in annual if item["batch_size"] == 1)
            batch16 = next(item for item in annual if item["batch_size"] == 16)
            if scalar["median_seconds"] > float(thresholds["annual_scalar_median_seconds"]):
                blockers.append(f"{site}/{gpp_resolution}/{sr_resolution} annual scalar")
            if scalar["median_seconds"] * 1024 > float(thresholds["annual_1024_projection_seconds"]):
                blockers.append(f"{site}/{gpp_resolution}/{sr_resolution} 1024 projection")
            if batch16["seconds_per_candidate"] >= scalar["seconds_per_candidate"]:
                blockers.append(f"{site}/{gpp_resolution}/{sr_resolution} batch16 throughput")
    if peak > int(thresholds["peak_rss_kib"]):
        blockers.append("peak RSS")
    require(len(cells) == 72, "benchmark cell count mismatch")
    require(len(cold_measurements) == 24, "benchmark cold-measurement count mismatch")
    dump_json(output, {
        "schema": "mcmc-iter003-posterior-benchmark-v1", "result": "pass",
        "environment": {"python": sys.version, "numpy": np.__version__, "hostname": platform.node(),
                        "threads": {name: os.environ.get(name) for name in
                                    ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")}},
        "total_benchmark_seconds": time.perf_counter() - benchmark_started,
        "release_loading_seconds": release_seconds,
        "release_loading_components": loaded.loading_seconds,
        "observation_context_seconds": context_seconds,
        "fixture_sha256": hashlib.sha256(fixture_units().tobytes()).hexdigest(),
        "cold_measurements": cold_measurements,
        "expected_cold_measurements": 24,
        "observed_cold_measurements": len(cold_measurements),
        "cells": cells, "expected_cells": 72, "observed_cells": len(cells),
        "warm_repetitions": cfg["benchmark"]["warm_repetitions"],
        "peak_rss_kib": peak, "material_thresholds": thresholds,
        "material_performance_blockers": blockers,
        "future_projections_are_estimates_not_execution_budgets": True,
    })
    print(f"MCMC_ITER003_BENCHMARK_PASS blockers={len(blockers)}")


def final_validate(cfg: dict[str, Any], output: Path) -> None:
    runtime = Path(cfg["runtime_root"])
    required = {
        "preflight": runtime / "results" / "preflight.json",
        "component": runtime / "results" / "component_validation.json",
        "posterior": runtime / "results" / "posterior_validation.json",
        "resolution": runtime / "results" / "resolution_parity_summary.csv",
        "references": runtime / "results" / "likelihood_reference_tests.json",
        "benchmark": runtime / "results" / "posterior_benchmark.json",
        "package_review": runtime / "reviews" / "package_review.json",
        "result_review": runtime / "reviews" / "result_review.json",
        "pre_final_accounting": runtime / "manifests" / "pre_final_job_accounting.json",
    }
    for name, path in required.items():
        require(path.is_file(), f"missing final input: {name}")
    for name in ("preflight", "component", "posterior", "references"):
        payload = json.loads(required[name].read_text(encoding="utf-8"))
        require(payload.get("result") == "pass", f"{name} result is not pass")
    for name in ("package_review", "result_review"):
        payload = json.loads(required[name].read_text(encoding="utf-8"))
        require(payload.get("outcome") == "pass", f"{name} outcome is not pass")
    benchmark_payload = json.loads(required["benchmark"].read_text(encoding="utf-8"))
    require(benchmark_payload.get("schema") == "mcmc-iter003-posterior-benchmark-v1",
            "benchmark schema mismatch")
    require(benchmark_payload.get("result") == "pass", "benchmark result is not pass")
    require(benchmark_payload.get("observed_cells") == 72, "benchmark completeness mismatch")
    require(benchmark_payload.get("observed_cold_measurements") == 24,
            "benchmark cold-measurement completeness mismatch")
    cells = benchmark_payload.get("cells", [])
    cell_keys = {
        (item["site"], item["window_hours"], item["gpp_resolution"],
         item["sr_resolution"], item["batch_size"])
        for item in cells
    }
    require(len(cell_keys) == 72, "benchmark cell identities are not unique")
    for item in cells:
        require(len(item.get("warm_seconds", [])) == 5, "benchmark warm-repeat count mismatch")
        components = item.get("component_median_seconds", {})
        require(set(components) == {"prior_seconds", "surrogate_seconds",
                                   "alignment_likelihood_seconds", "total_seconds"},
                "benchmark component timing schema mismatch")
        require(all(np.isfinite(float(value)) and float(value) >= 0.0 for value in components.values()),
                "benchmark component timing invalid")
    cold = benchmark_payload.get("cold_measurements", [])
    require(len(cold) == 24 and all("component_seconds" in item for item in cold),
            "benchmark cold/component evidence incomplete")

    posterior_payload = json.loads(required["posterior"].read_text(encoding="utf-8"))
    require(posterior_payload.get("schema") == "mcmc-iter003-posterior-validation-v1",
            "posterior validation schema mismatch")
    require(posterior_payload.get("resolution_rows") == 8, "resolution validation row count mismatch")
    require(posterior_payload.get("reference_case_count") == 14, "likelihood reference count mismatch")
    require(posterior_payload.get("full_window_surrogate_calls_per_site") == 1,
            "full-window surrogate-call contract mismatch")
    require(all(posterior_payload.get("gate_evidence", {}).values())
            and len(posterior_payload.get("gate_evidence", {})) == 8,
            "posterior gate evidence incomplete")
    for site in cfg["sites"]:
        site_payload = posterior_payload["sites"][site]
        require(len(site_payload["smoke_resolution_results"]) == 4,
                f"{site} resolution-combination evidence incomplete")
        for name in ("full_prediction_reused_across_resolution_operators",
                     "invalid_support_rejected_before_surrogate", "mixed_validity_batch_ordering",
                     "bounded_surrogate_replay_exact", "resolution_component_isolation"):
            require(site_payload.get(name) is True, f"{site} missing evidence: {name}")
        require(set(site_payload["cn_by_cv"]) == {"0.2", "0.3", "0.5"},
                f"{site} C/N CV evidence mismatch")

    with required["resolution"].open(newline="", encoding="utf-8") as handle:
        resolution_rows = list(csv.DictReader(handle))
    require(len(resolution_rows) == 8, "resolution CSV row count mismatch")
    for site in cfg["sites"]:
        site_rows = [row for row in resolution_rows if row["site"] == site]
        require({(row["gpp_resolution"], row["sr_resolution"]) for row in site_rows}
                == {tuple(item) for item in cfg["resolution_combinations"]},
                f"{site} resolution CSV combinations mismatch")
        for resolution in ("hourly", "daily"):
            gpp_terms = {row["log_likelihood_gpp"] for row in site_rows
                         if row["gpp_resolution"] == resolution}
            sr_terms = {row["log_likelihood_sr"] for row in site_rows
                        if row["sr_resolution"] == resolution}
            require(len(gpp_terms) == 1 and len(sr_terms) == 1,
                    f"{site} resolution component isolation mismatch")

    reference_payload = json.loads(required["references"].read_text(encoding="utf-8"))
    require(reference_payload.get("schema") == "mcmc-iter003-likelihood-reference-v1",
            "likelihood reference schema mismatch")
    require(reference_payload.get("production_kernels_used_for_reference") is False,
            "likelihood references are not independent")
    reference_cases = reference_payload.get("cases", [])
    require(len(reference_cases) == 14, "likelihood reference cases incomplete")
    cn_reference_keys = {
        (case.get("site"), float(case["cn_observation_cv"]))
        for case in reference_cases if case.get("kind") == "joint_cn"
    }
    require(cn_reference_keys == {(site, cv) for site in cfg["sites"] for cv in (0.2, 0.3, 0.5)},
            "joint C/N site/CV reference coverage incomplete")
    require(sum(case.get("kind") != "joint_cn" for case in reference_cases) == 8,
            "flux likelihood reference coverage incomplete")
    for case in reference_cases:
        require(np.isclose(float(case["actual"]), float(case["reference"]), rtol=1e-12, atol=1e-10),
                "likelihood reference tolerance failure")

    execution_manifest = json.loads((runtime / "manifests" / "execution_manifest.json").read_text(encoding="utf-8"))
    require(execution_manifest["config_sha256"] == sha256(runtime / "submitted" / "iter003_config.json"),
            "submitted config identity mismatch")
    require(execution_manifest["checksum_manifest_sha256"]
            == sha256(runtime / "manifests" / "execution_files.sha256"),
            "submitted checksum manifest identity mismatch")

    accounting = json.loads(required["pre_final_accounting"].read_text(encoding="utf-8"))
    require(accounting.get("schema") == "mcmc-iter003-pre-final-accounting-v1",
            "pre-final accounting schema mismatch")
    attempts = accounting.get("attempts", [])
    require(len(attempts) <= 9, "pre-final submission ceiling exceeded")
    require(accounting.get("active_or_unaccounted") == 0, "pre-final job remains active or unaccounted")
    terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "PREEMPTED", "NODE_FAIL"}
    require(all(item.get("state") in terminal_states for item in attempts),
            "pre-final accounting contains nonterminal attempt")
    require(all(item.get("classification") for item in attempts if item.get("state") != "COMPLETED"),
            "failed pre-final attempt lacks classification")
    for work_unit in ("preflight", "component", "integrated", "benchmark"):
        require(any(item.get("work_unit") == work_unit and item.get("state") == "COMPLETED"
                    and item.get("exit_code") == "0:0" for item in attempts),
                f"missing successful terminal accounting for {work_unit}")
    require(int(accounting.get("shared_retries_consumed", 0)) <= 4,
            "shared retry budget exceeded")
    require(int(accounting.get("preflight_correction_reruns", 0)) <= 1,
            "preflight correction budget exceeded")

    blockers = benchmark_payload.get("material_performance_blockers", [])
    decision = ("four_observable_posterior_validated" if not blockers
                else "four_observable_posterior_validated_performance_blocker")
    require(source_bytes(runtime) <= int(cfg["storage_cap_bytes"]), "Iter003 storage cap exceeded")
    evidence = {name: {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}
                for name, path in required.items()}
    dump_json(output, {
        "schema": "mcmc-iter003-final-validation-v1", "result": "pass",
        "decision_candidate": decision, "gates_1_through_9_pass": True,
        "gate_10_requires_final_job_accounting_and_four_record_closeout": True,
        "material_performance_blockers": blockers, "evidence": evidence,
        "storage_bytes": source_bytes(runtime),
    })
    print(f"MCMC_ITER003_FINAL_PASS decision={decision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--step", choices=("preflight", "component", "integrated", "benchmark", "final"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    {"preflight": preflight, "component": component, "integrated": integrated,
     "benchmark": benchmark, "final": final_validate}[args.step](cfg, args.output)


if __name__ == "__main__":
    main()
