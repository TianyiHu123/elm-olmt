#!/usr/bin/env python3
"""Execute the locked Iter004 work units on a Puma compute node."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
from typing import Any

import emcee
import numpy as np


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.mcmc_coupled_adapter import CONSUMED_RELEASE_FILES
from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_artifacts import (
    canonical_json_sha256,
    directory_size_bytes,
    sha256_file,
    validate_independent_review,
    validate_job_accounting,
    write_json_exclusive,
    write_npz_exclusive,
)
from model_ELM.mcmc_three_stage_diagnostics import continuation_outcome, evaluate_continuation_gate, summarize_pilot
from model_ELM.mcmc_three_stage_initialization import (
    assess_stage_one,
    geometry_metrics,
    physical_to_unit,
    prior_aware_candidates,
    sampling_eligibility,
    scrambled_sobol_prefix,
    select_candidate_pool,
    select_walkers,
    validate_candidate_identity_arrays,
    validate_pool_geometry,
    validate_selection_ledger,
    validate_walker_geometry,
)
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA as OBS_CONFIG_SCHEMA,
    ObservationReleaseConfig,
)
from model_ELM.mcmc_three_stage_posterior import PosteriorResult, load_three_stage_posterior
from model_ELM.mcmc_three_stage_release import (
    CONFIG_SCHEMA as RELEASE_CONFIG_SCHEMA,
    IMPLEMENTATION_ID,
    ThreeStageReleaseConfig,
)
from model_ELM.mcmc_three_stage_sampler import finalize_sampler_run, random_state_equal, run_sampler_block


SOURCE_FILES = (
    "model_ELM/mcmc_prior.py",
    "model_ELM/mcmc_geometry.py",
    "model_ELM/mcmc_three_stage_release.py",
    "model_ELM/mcmc_three_stage_observations.py",
    "model_ELM/mcmc_three_stage_likelihood.py",
    "model_ELM/mcmc_three_stage_posterior.py",
    "model_ELM/mcmc_three_stage_initialization.py",
    "model_ELM/mcmc_three_stage_sampler.py",
    "model_ELM/mcmc_three_stage_artifacts.py",
    "model_ELM/mcmc_three_stage_diagnostics.py",
)

PLANNED_JOB_CPUS = {
    "preflight_iter004.slurm": 2,
    "search_abby_iter004.slurm": 4,
    "search_jerc_iter004.slurm": 4,
    "pool_restart_iter004.slurm": 4,
    "pilot_abby_iter004.slurm": 4,
    "pilot_jerc_iter004.slurm": 4,
    "diagnostics_iter004.slurm": 4,
    "final_iter004.slurm": 2,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_failure_closeout_accounting(
    payload: dict[str, Any], *, expected_jobs: dict[str, int], maximum_submissions: int,
) -> dict[str, Any]:
    """Permit only the two locked fatal pilot outcomes in an otherwise successful ledger."""
    summary = validate_job_accounting(
        payload, expected_jobs=expected_jobs, maximum_submissions=maximum_submissions,
        require_all_successful=False,
    )
    by_job = {name: [] for name in expected_jobs}
    for row in payload["attempts"]:
        by_job[row["planned_job"]].append(row)
    fatal_pilots = {"pilot_abby_iter004.slurm", "pilot_jerc_iter004.slurm"}
    for job, rows in by_job.items():
        final_attempt = rows[-1]
        if job in fatal_pilots:
            require(
                final_attempt["state"].split("+")[0] == "FAILED"
                and final_attempt["exit_code"] == "1:0"
                and final_attempt.get("failure_classification") == "pilot_fatal_numerical_rejection",
                f"pilot job lacks the exact fatal closeout attempt: {job}",
            )
        else:
            require(
                final_attempt["state"].split("+")[0] == "COMPLETED"
                and final_attempt["exit_code"] == "0:0",
                f"non-pilot job lacks a successful terminal attempt: {job}",
            )
    return {**summary, "fatal_pilot_closeout": True}


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload.get("schema") == "mcmc-optimization-iter004-config-v1", "config schema mismatch")
    require(Path(payload["repository_root"]).resolve() == REPO_ROOT, "repository root mismatch")
    require(payload["branch"] == "feature/mcmc-optimization", "branch mismatch")
    require(payload["prior_id"] == PPE1, "Iter004 supports PPE1 only")
    require(payload["emcee_version"] == emcee.__version__, "emcee version mismatch")
    require(payload["candidate_stage_one"] == 1024 and payload["candidate_maximum"] == 2048,
            "candidate budget mismatch")
    require(payload["walker_count"] == 64 and payload["pilot_maximum_steps"] == 256,
            "pilot geometry mismatch")
    require(payload.get("tolerances") == {
        "rtol": 1e-12, "atol": 1e-10, "component_sum_rtol": 0.0,
    }, "strict reference tolerance contract mismatch")
    require(payload.get("batch_equivalence_tolerances") == {
        "rtol": 1e-7, "atol": 1e-8,
    }, "batch-equivalence tolerance contract mismatch")
    require(payload.get("preflight_diagnostic_only") is False,
            "correction package must not remain diagnostic-only")
    require(payload.get("preflight_correction_reruns") == 3
            and payload.get("preflight_diagnostic_reruns") == 1
            and payload.get("wu3_correction_reruns") == 1
            and payload.get("wu3_identity_correction_reruns") == 1
            and payload.get("pilot_startup_correction_reruns") == 2
            and payload.get("shared_unchanged_scope_retries") == 0
            and payload.get("maximum_submissions") == 16,
            "authorized retry allocation mismatch")
    return payload


def source_hashes() -> dict[str, str]:
    return {path: sha256_file(REPO_ROOT / path) for path in SOURCE_FILES}


def release_config(config: dict[str, Any]) -> ThreeStageReleaseConfig:
    return ThreeStageReleaseConfig(
        schema=RELEASE_CONFIG_SCHEMA,
        implementation_id=IMPLEMENTATION_ID,
        prior_id=PPE1,
        release_id="release_0001",
        release_root=Path(config["surrogate_release_root"]),
        snapshot_root=Path(config["snapshot_root"]),
        uncertainty_root=Path(config["uncertainty_root"]),
        uncertainty_handoff_sha256=config["uncertainty_handoff_sha256"],
        uncertainty_manifest_sha256=config["uncertainty_manifest_sha256"],
        uncertainty_validation_sha256=config["uncertainty_validation_sha256"],
        source_file=Path(config["surrogate_source_file"]),
        release_manifest_sha256=config["surrogate_release_manifest_sha256"],
        catalog_sha256=config["surrogate_catalog_sha256"],
        snapshot_sha256=config["snapshot_sha256"],
    )


def observation_config(config: dict[str, Any]) -> ObservationReleaseConfig:
    return ObservationReleaseConfig(
        schema=OBS_CONFIG_SCHEMA,
        release_root=Path(config["observation_release_root"]),
        snapshot_root=Path(config["snapshot_root"]),
        catalog_sha256=config["observation_catalog_sha256"],
        release_manifest_sha256=config["observation_manifest_sha256"],
        validation_report_sha256=config["observation_validation_sha256"],
        snapshot_sha256=config["snapshot_sha256"],
    )


def load_posterior(config: dict[str, Any], site: str):
    return load_three_stage_posterior(
        site=site,
        prior_id=PPE1,
        prior_root=Path(config["ppe1_root"]),
        surrogate_release=release_config(config),
        observation_release=observation_config(config),
        gpp_resolution=config["gpp_resolution"],
        sr_resolution=config["sr_resolution"],
        cn_observation_cv=float(config["cn_observation_cv"]),
        include_cn=bool(config["include_cn"]),
        start=int(config["full_window_start"]),
        end=int(config["full_window_end"]),
        member_chunk=16,
    )


def peak_rss_gib() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / (1024.0 * 1024.0)


def json_number(value: float) -> float | str:
    number = float(value)
    if np.isneginf(number):
        return "-Infinity"
    if np.isposinf(number):
        return "Infinity"
    require(np.isfinite(number), "NaN is prohibited in Iter004 evidence")
    return number


def result_payload(result: PosteriorResult) -> dict[str, Any]:
    return {
        "site": result.site,
        "log_prior": json_number(result.log_prior),
        "log_likelihood_gpp": json_number(result.log_likelihood_gpp),
        "log_likelihood_sr": json_number(result.log_likelihood_sr),
        "log_likelihood_cn": json_number(result.log_likelihood_cn),
        "log_posterior": json_number(result.log_posterior),
        "evaluation_error": result.evaluation_error,
        "surrogate_evaluated": result.surrogate_evaluated,
        "n_gpp": result.n_gpp,
        "n_sr": result.n_sr,
    }


def reference_row(path: Path, site: str) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matches = [row for row in rows if row["site"] == site and row["gpp_resolution"] == "daily"
               and row["sr_resolution"] == "daily" and row["include_cn"] == "True"
               and float(row["cn_observation_cv"]) == 0.3]
    require(len(matches) == 1, f"missing unique Iter003 full-window reference for {site}")
    return matches[0]


def close_values(observed: float, expected: float, config: dict[str, Any], *, component_sum=False) -> bool:
    tolerance = config["tolerances"]
    return bool(np.isclose(
        observed, expected,
        rtol=float(tolerance["component_sum_rtol"] if component_sum else tolerance["rtol"]),
        atol=float(tolerance["atol"]),
    ))


def batch_close_values(observed: float, expected: float, config: dict[str, Any]) -> bool:
    tolerance = config["batch_equivalence_tolerances"]
    return bool(np.isclose(
        observed, expected, rtol=float(tolerance["rtol"]), atol=float(tolerance["atol"]),
    ))


def sampling_parity_diagnostic(
    *, config: dict[str, Any], site: str, label: str, coordinate: np.ndarray,
    batch_result: Any, scalar_result: Any,
) -> dict[str, Any]:
    """Return complete, JSON-safe evidence for one transformed-target parity comparison."""

    tolerance = config["batch_equivalence_tolerances"]
    comparisons = {}
    for field in (
        "log_prior", "log_likelihood_gpp", "log_likelihood_sr",
        "log_likelihood_cn", "log_posterior",
    ):
        batch_value = float(getattr(batch_result.physical, field))
        scalar_value = float(getattr(scalar_result.physical, field))
        equal_nonfinite = batch_value == scalar_value
        absolute_delta = 0.0 if equal_nonfinite else abs(batch_value - scalar_value)
        allowed_delta = (
            float(tolerance["atol"]) + float(tolerance["rtol"]) * abs(scalar_value)
            if np.isfinite(scalar_value) else 0.0
        )
        relative_delta = (
            absolute_delta / abs(scalar_value) if scalar_value != 0.0
            else (0.0 if absolute_delta == 0.0 else float("inf"))
        )
        comparisons[field] = {
            "batch": json_number(batch_value), "scalar": json_number(scalar_value),
            "absolute_delta": json_number(absolute_delta),
            "relative_delta": json_number(relative_delta),
            "allowed_delta": allowed_delta,
            "normalized_tolerance_usage": json_number(
                absolute_delta / allowed_delta if allowed_delta > 0.0
                else (0.0 if absolute_delta == 0.0 else float("inf"))
            ),
            "within_tolerance": batch_close_values(batch_value, scalar_value, config),
        }
    batch_sampling = float(batch_result.log_sampling_posterior)
    scalar_sampling = float(scalar_result.log_sampling_posterior)
    equal_nonfinite = batch_sampling == scalar_sampling
    absolute_delta = 0.0 if equal_nonfinite else abs(batch_sampling - scalar_sampling)
    allowed_delta = (
        float(tolerance["atol"]) + float(tolerance["rtol"]) * abs(scalar_sampling)
        if np.isfinite(scalar_sampling) else 0.0
    )
    relative_delta = (
        absolute_delta / abs(scalar_sampling) if scalar_sampling != 0.0
        else (0.0 if absolute_delta == 0.0 else float("inf"))
    )
    comparisons["log_sampling_posterior"] = {
        "batch": json_number(batch_sampling), "scalar": json_number(scalar_sampling),
        "absolute_delta": json_number(absolute_delta), "relative_delta": json_number(relative_delta),
        "allowed_delta": allowed_delta,
        "normalized_tolerance_usage": json_number(
            absolute_delta / allowed_delta if allowed_delta > 0.0
            else (0.0 if absolute_delta == 0.0 else float("inf"))
        ),
        "within_tolerance": batch_close_values(batch_sampling, scalar_sampling, config),
    }
    batch_jacobian = float(batch_result.log_abs_det_jacobian)
    scalar_jacobian = float(scalar_result.log_abs_det_jacobian)
    jacobian_absolute_delta = (
        0.0 if batch_jacobian == scalar_jacobian else abs(batch_jacobian - scalar_jacobian)
    )
    jacobian_allowed_delta = (
        float(tolerance["atol"]) + float(tolerance["rtol"]) * abs(scalar_jacobian)
        if np.isfinite(scalar_jacobian) else 0.0
    )
    jacobian_relative_delta = (
        jacobian_absolute_delta / abs(scalar_jacobian) if scalar_jacobian != 0.0
        else (0.0 if jacobian_absolute_delta == 0.0 else float("inf"))
    )
    comparisons["log_abs_det_jacobian"] = {
        "batch": json_number(batch_jacobian), "scalar": json_number(scalar_jacobian),
        "absolute_delta": json_number(jacobian_absolute_delta),
        "relative_delta": json_number(jacobian_relative_delta),
        "allowed_delta": jacobian_allowed_delta,
        "normalized_tolerance_usage": json_number(
            jacobian_absolute_delta / jacobian_allowed_delta if jacobian_allowed_delta > 0.0
            else (0.0 if jacobian_absolute_delta == 0.0 else float("inf"))
        ),
        "within_tolerance": batch_close_values(batch_jacobian, scalar_jacobian, config),
    }
    return {
        "label": label,
        "sampler_coordinate": np.asarray(coordinate, dtype=np.float64).tolist(),
        "batch_physical": result_payload(batch_result.physical),
        "scalar_physical": result_payload(scalar_result.physical),
        "comparisons": comparisons,
        "sampling_target_within_tolerance": comparisons["log_sampling_posterior"]["within_tolerance"],
        "site": site,
    }


def physical_parity_diagnostic(
    *, config: dict[str, Any], index: int, theta: np.ndarray,
    batch_result: PosteriorResult, scalar_result: PosteriorResult,
) -> dict[str, Any]:
    """Return component-level scalar/batch evidence for one physical candidate."""

    tolerance = config["batch_equivalence_tolerances"]
    comparisons = {}
    for field in (
        "log_prior", "log_likelihood_gpp", "log_likelihood_sr",
        "log_likelihood_cn", "log_posterior",
    ):
        batch_value = float(getattr(batch_result, field))
        scalar_value = float(getattr(scalar_result, field))
        absolute_delta = 0.0 if batch_value == scalar_value else abs(batch_value - scalar_value)
        allowed_delta = (
            float(tolerance["atol"]) + float(tolerance["rtol"]) * abs(scalar_value)
            if np.isfinite(scalar_value) else 0.0
        )
        relative_delta = (
            absolute_delta / abs(scalar_value) if scalar_value != 0.0
            else (0.0 if absolute_delta == 0.0 else float("inf"))
        )
        comparisons[field] = {
            "batch": json_number(batch_value), "scalar": json_number(scalar_value),
            "absolute_delta": json_number(absolute_delta),
            "relative_delta": json_number(relative_delta), "allowed_delta": allowed_delta,
            "normalized_tolerance_usage": json_number(
                absolute_delta / allowed_delta if allowed_delta > 0.0
                else (0.0 if absolute_delta == 0.0 else float("inf"))
            ),
            "within_tolerance": batch_close_values(batch_value, scalar_value, config),
        }
    return {
        "candidate_index": int(index), "physical_parameters": np.asarray(theta).tolist(),
        "batch": result_payload(batch_result), "scalar": result_payload(scalar_result),
        "comparisons": comparisons,
        "posterior_within_tolerance": comparisons["log_posterior"]["within_tolerance"],
    }


def preflight(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    output = runtime / "results" / "wu1_readiness.json"
    require(not output.exists(), "WU1 evidence already exists")
    diagnostic_only = bool(config.get("preflight_diagnostic_only", False))
    if diagnostic_only:
        require(os.environ.get("SLURM_JOB_ID") is not None,
                "diagnostic-only preflight requires a Slurm job identity")
        require(config.get("preflight_diagnostic_predecessor_job_id") == "24825557",
                "diagnostic-only predecessor identity mismatch")
    package_review_path = runtime / "reviews" / "package_review.json"
    require(package_review_path.is_file(), "independent package review artifact missing")
    package_review = json.loads(package_review_path.read_text(encoding="utf-8"))
    package_root = REPO_ROOT / "development/mcmc_optimization/slurm/iter004"
    expected_reviewed = {
        "config_sha256": sha256_file(package_root / "iter004_config.json"),
        "checksum_manifest_sha256": sha256_file(package_root / "execution_files.sha256"),
        "execution_manifest_sha256": sha256_file(package_root / "execution_manifest.json"),
        "driver_sha256": sha256_file(package_root / "run_iter004.py"),
        "test_runner_sha256": sha256_file(package_root / "run_iter004_tests.py"),
    }
    validate_independent_review(
        package_review, schema="mcmc-iter004-package-review-v1",
        reviewed_artifacts=expected_reviewed,
    )
    dependencies = {
        "plan": sha256_file(REPO_ROOT / "development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md"),
        "release_manifest": sha256_file(Path(config["surrogate_release_root"]) / "release_manifest.json"),
        "surrogate_catalog": sha256_file(Path(config["surrogate_release_root"]).parent / "catalog.json"),
        "snapshot": sha256_file(Path(config["snapshot_root"]) / "manifests/dataset_snapshot_r0001.json"),
        "member_split": sha256_file(Path(config["snapshot_root"]) / "splits/member_split_1024_v1.json"),
        "uncertainty_handoff": sha256_file(Path(config["uncertainty_root"]) / "uncertainty_handoff.json"),
        "uncertainty_manifest": sha256_file(Path(config["uncertainty_root"]) / "products_manifest.json"),
        "uncertainty_validation": sha256_file(Path(config["uncertainty_root"]) / "final_validation_report.json"),
        "observation_catalog": sha256_file(Path(config["observation_release_root"]) / "catalog.json"),
        "observation_manifest": sha256_file(Path(config["observation_release_root"]) / "release_manifest.json"),
        "observation_validation": sha256_file(Path(config["observation_release_root"]) / "validation_report.json"),
        "iter003_posterior": sha256_file(Path(config["runtime_root"]).parent / "iter003_four_observable_posterior/results/posterior_validation.json"),
        "iter003_references": sha256_file(Path(config["runtime_root"]).parent / "iter003_four_observable_posterior/results/likelihood_reference_tests.json"),
        "iter003_benchmark": sha256_file(Path(config["runtime_root"]).parent / "iter003_four_observable_posterior/results/posterior_benchmark.json"),
        "iter003_resolution_parity": sha256_file(Path(config["runtime_root"]).parent / "iter003_four_observable_posterior/results/resolution_parity_summary.csv"),
        "emcee_conda_metadata": sha256_file(Path(config["emcee_conda_metadata"])),
        "emcee_de_move": sha256_file(Path(config["emcee_de_move_source"])),
        "emcee_de_snooker": sha256_file(Path(config["emcee_de_snooker_source"])),
        "emcee_hdf_backend": sha256_file(Path(config["emcee_hdf_backend_source"])),
    }
    expected = {
        "plan": config["plan_sha256"], "release_manifest": config["surrogate_release_manifest_sha256"],
        "surrogate_catalog": config["surrogate_catalog_sha256"],
        "snapshot": config["snapshot_sha256"], "member_split": config["member_split_sha256"],
        "uncertainty_handoff": config["uncertainty_handoff_sha256"],
        "uncertainty_manifest": config["uncertainty_manifest_sha256"],
        "uncertainty_validation": config["uncertainty_validation_sha256"],
        "observation_catalog": config["observation_catalog_sha256"],
        "observation_manifest": config["observation_manifest_sha256"],
        "observation_validation": config["observation_validation_sha256"],
        "iter003_posterior": config["iter003_posterior_sha256"],
        "iter003_references": config["iter003_references_sha256"],
        "iter003_benchmark": config["iter003_benchmark_sha256"],
        "iter003_resolution_parity": config["iter003_resolution_parity_sha256"],
        "emcee_conda_metadata": config["emcee_conda_metadata_sha256"],
        "emcee_de_move": config["emcee_de_move_sha256"],
        "emcee_de_snooker": config["emcee_de_snooker_sha256"],
        "emcee_hdf_backend": config["emcee_hdf_backend_sha256"],
    }
    require(dependencies == expected, "WU1 dependency identity mismatch")
    reference_path = Path(config["runtime_root"]).parent / "iter003_four_observable_posterior/results/resolution_parity_summary.csv"
    prior = Prior18.from_directory(PPE1, Path(config["ppe1_root"]))
    midpoint = prior.inverse_unit(np.full(18, 0.5))
    second = prior.inverse_unit(np.linspace(0.2, 0.8, 18))
    invalid = midpoint.copy(); invalid[17] = invalid[16]
    site_reports = {}
    diagnostic_site_reports = {}
    for site in config["sites"]:
        started = time.perf_counter()
        posterior = load_posterior(config, site)
        initialization_seconds = time.perf_counter() - started
        scalar_seconds = []
        scalar_results = []
        for _ in range(3):
            begun = time.perf_counter(); scalar_results.append(posterior.evaluate(midpoint)); scalar_seconds.append(time.perf_counter() - begun)
        first = scalar_results[0]
        require(all(result_payload(value) == result_payload(first) for value in scalar_results[1:]),
                f"{site} deterministic scalar replay failed")
        expected_row = reference_row(reference_path, site)
        for field, reference_field in (
            ("log_prior", "log_prior"), ("log_likelihood_gpp", "log_likelihood_gpp"),
            ("log_likelihood_sr", "log_likelihood_sr"), ("log_likelihood_cn", "log_likelihood_cn"),
            ("log_posterior", "log_posterior"),
        ):
            require(close_values(float(getattr(first, field)), float(expected_row[reference_field]), config),
                    f"{site} full-window {field} parity failed")
        require(close_values(
            first.log_posterior,
            first.log_prior + first.log_likelihood_gpp + first.log_likelihood_sr + first.log_likelihood_cn,
            config, component_sum=True,
        ), f"{site} component sum failed")
        mixed = posterior.evaluate_batch(np.vstack((midpoint, invalid, second)))
        require(mixed[1].evaluation_error == "outside_prior_support" and not mixed[1].surrogate_evaluated,
                f"{site} mixed invalid row classification failed")
        require(batch_close_values(mixed[0].log_posterior, first.log_posterior, config),
                f"{site} mixed batch changed valid result")
        sampler = prior.coordinate_transform.physical_to_sampler(np.vstack((midpoint, second)))
        sampling_batch = posterior.evaluate_sampling_batch(sampler)
        sampling_scalars = [posterior.evaluate_sampling(coordinate) for coordinate in sampler]
        parity_rows = [
            sampling_parity_diagnostic(
                config=config, site=site, label=label, coordinate=coordinate,
                batch_result=batch_result, scalar_result=scalar_result,
            )
            for label, coordinate, batch_result, scalar_result in zip(
                ("midpoint", "second"), sampler, sampling_batch, sampling_scalars,
            )
        ]
        parity_payload = {
            "schema": "mcmc-iter004-wu1-sampling-parity-diagnostic-v1",
            "job_id": os.environ.get("SLURM_JOB_ID", "unknown"),
            "site": site,
            "gate": "transformed_coordinate_scalar_batch_parity",
            "rtol": float(config["batch_equivalence_tolerances"]["rtol"]),
            "atol": float(config["batch_equivalence_tolerances"]["atol"]),
            "rows": parity_rows,
            "result": "pass" if all(row["sampling_target_within_tolerance"] for row in parity_rows) else "fail",
            "source_hashes": source_hashes(),
        }
        parity_path = runtime / "results" / (
            f"wu1_sampling_parity_{parity_payload['job_id']}_{site}.json"
        )
        write_json_exclusive(parity_path, parity_payload)
        if parity_payload["result"] != "pass":
            print(
                "MCMC_ITER004_WU1_PARITY_FAILURE "
                + json.dumps({
                    "site": site, "gate": parity_payload["gate"],
                    "artifact": str(parity_path), "rows": parity_rows,
                }, sort_keys=True, allow_nan=False),
                file=sys.stderr, flush=True,
            )
        diagnostic_site_reports[site] = {
            "result": parity_payload["result"],
            "artifact": str(parity_path),
            "artifact_sha256": sha256_file(parity_path),
        }
        if diagnostic_only:
            continue
        require(parity_payload["result"] == "pass",
                f"{site} sampling batch parity failed; diagnostic={parity_path}")
        batch_reports = {}
        for batch_size in (16, 64):
            unit = scrambled_sobol_prefix(dimension=18, count=batch_size, seed=410000 + batch_size)
            physical = prior_aware_candidates(prior, unit)
            begun = time.perf_counter(); batch_results, timing = posterior.evaluate_batch_timed(physical); elapsed = time.perf_counter() - begun
            scalar_results = [posterior.evaluate(theta) for theta in physical]
            physical_parity_rows = [
                physical_parity_diagnostic(
                    config=config, index=index, theta=theta,
                    batch_result=batch_result, scalar_result=scalar_result,
                )
                for index, (theta, batch_result, scalar_result) in enumerate(
                    zip(physical, batch_results, scalar_results)
                )
            ]
            physical_parity_payload = {
                "schema": "mcmc-iter004-wu1-physical-batch-parity-v1",
                "job_id": os.environ.get("SLURM_JOB_ID", "unknown"),
                "site": site, "batch_size": batch_size,
                "rtol": float(config["batch_equivalence_tolerances"]["rtol"]),
                "atol": float(config["batch_equivalence_tolerances"]["atol"]),
                "rows": physical_parity_rows,
                "result": "pass" if all(
                    value["posterior_within_tolerance"] for value in physical_parity_rows
                ) else "fail",
                "source_hashes": source_hashes(),
            }
            physical_parity_path = runtime / "results" / (
                f"wu1_physical_parity_{physical_parity_payload['job_id']}_{site}_{batch_size}.json"
            )
            write_json_exclusive(physical_parity_path, physical_parity_payload)
            if physical_parity_payload["result"] != "pass":
                failed_rows = [
                    value for value in physical_parity_rows
                    if not value["posterior_within_tolerance"]
                ]
                print(
                    "MCMC_ITER004_WU1_PHYSICAL_PARITY_FAILURE "
                    + json.dumps({
                        "site": site, "batch_size": batch_size,
                        "artifact": str(physical_parity_path), "failed_rows": failed_rows,
                    }, sort_keys=True, allow_nan=False),
                    file=sys.stderr, flush=True,
                )
            require(physical_parity_payload["result"] == "pass",
                    f"{site} scalar/batch-{batch_size} parity failed; diagnostic={physical_parity_path}")
            batch_reports[str(batch_size)] = {
                "elapsed_seconds": elapsed, "seconds_per_candidate": elapsed / batch_size,
                "timing": timing, "parity_artifact": str(physical_parity_path),
                "parity_artifact_sha256": sha256_file(physical_parity_path),
                "numerical_rejections": {
                    reason: sum(value.evaluation_error == reason for value in batch_results)
                    for reason in sorted({value.evaluation_error for value in batch_results if value.evaluation_error})
                },
            }
        warm_scalar = float(np.median(scalar_seconds))
        stage_one_projection = batch_reports["64"]["seconds_per_candidate"] * 1024.0
        maximum_projection = batch_reports["64"]["seconds_per_candidate"] * 2048.0
        gates = config["resource_gates"]
        require(initialization_seconds <= float(gates["initialization_seconds"]), f"{site} initialization gate failed")
        require(warm_scalar <= float(gates["warm_scalar_seconds"]), f"{site} scalar latency gate failed")
        require(batch_reports["16"]["seconds_per_candidate"] < warm_scalar, f"{site} batch-16 improvement failed")
        require(stage_one_projection <= float(gates["stage_one_projection_seconds"]), f"{site} Stage-1 projection failed")
        require(maximum_projection <= float(gates["maximum_search_projection_seconds"]), f"{site} max search projection failed")
        site_reports[site] = {
            "initialization_seconds": initialization_seconds,
            "warm_scalar_seconds": scalar_seconds,
            "reference": result_payload(first),
            "mixed_batch": [result_payload(value) for value in mixed],
            "batch": batch_reports,
            "stage_one_projection_seconds": stage_one_projection,
            "maximum_projection_seconds": maximum_projection,
        }
    if diagnostic_only:
        diagnostic_result = (
            "parity_pass" if all(value["result"] == "pass" for value in diagnostic_site_reports.values())
            else "parity_fail"
        )
        diagnostic_path = runtime / "results" / f"wu1_diagnostic_{os.environ['SLURM_JOB_ID']}.json"
        write_json_exclusive(diagnostic_path, {
            "schema": "mcmc-iter004-wu1-diagnostic-completion-v1",
            "result": "diagnostic_complete",
            "parity_result": diagnostic_result,
            "job_id": os.environ["SLURM_JOB_ID"],
            "authorized_predecessor_job_id": config["preflight_diagnostic_predecessor_job_id"],
            "sites": diagnostic_site_reports,
            "readiness_artifact_written": False,
            "candidate_search_authorized": False,
            "rtol": float(config["batch_equivalence_tolerances"]["rtol"]),
            "atol": float(config["batch_equivalence_tolerances"]["atol"]),
            "source_hashes": source_hashes(),
            "peak_rss_gib": peak_rss_gib(),
        })
        require(not output.exists(), "diagnostic-only mode created a prohibited readiness artifact")
        print(
            f"MCMC_ITER004_WU1_DIAGNOSTIC_COMPLETE parity={diagnostic_result} "
            f"artifact={diagnostic_path} readiness_written=false"
        )
        return
    peak = peak_rss_gib()
    require(peak <= float(config["resource_gates"]["wu1_peak_rss_gib"]), "WU1 peak RSS gate failed")
    write_json_exclusive(output, {
        "schema": "mcmc-iter004-wu1-readiness-v1", "result": "pass",
        "dependencies": dependencies, "source_hashes": source_hashes(),
        "sites": site_reports, "peak_rss_gib": peak,
        "emcee_version": emcee.__version__, "full_window": [720, 61320],
    })
    print("MCMC_ITER004_WU1_PASS")


def score_candidates(posterior, physical: np.ndarray, batch_size: int) -> dict[str, np.ndarray]:
    rows = []
    for start in range(0, physical.shape[0], batch_size):
        rows.extend(posterior.evaluate_batch(physical[start:start + batch_size]))
    return {
        "log_prior": np.asarray([row.log_prior for row in rows], dtype=np.float64),
        "log_likelihood_gpp": np.asarray([row.log_likelihood_gpp for row in rows], dtype=np.float64),
        "log_likelihood_sr": np.asarray([row.log_likelihood_sr for row in rows], dtype=np.float64),
        "log_likelihood_cn": np.asarray([row.log_likelihood_cn for row in rows], dtype=np.float64),
        "log_posterior": np.asarray([row.log_posterior for row in rows], dtype=np.float64),
        "reason": np.asarray([row.evaluation_error or "valid" for row in rows], dtype="U64"),
        "surrogate_evaluated": np.asarray([row.surrogate_evaluated for row in rows], dtype=bool),
    }


def search(config: dict[str, Any], site: str) -> None:
    require(site in config["sites"], "unsupported search site")
    readiness_path = Path(config["runtime_root"]) / "results" / "wu1_readiness.json"
    require(readiness_path.is_file(), "WU1 readiness evidence missing")
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    require(readiness.get("schema") == "mcmc-iter004-wu1-readiness-v1"
            and readiness.get("result") == "pass"
            and readiness.get("source_hashes") == source_hashes(),
            "WU1 readiness identity/result mismatch")
    root = Path(config["runtime_root"]) / "sites" / site / "candidates"
    output = root / "candidate_scores.npz"
    require(not output.exists(), f"{site} candidate output already exists")
    posterior = load_posterior(config, site)
    prior = posterior.prior
    seed = int(config["sites"][site]["candidate_seed"])
    require(seed != int(config["ppe_design_seed"]), "candidate seed duplicates PPE design seed")
    target_payload = posterior_target_payload(config, site, posterior)
    target_sha = canonical_json_sha256(target_payload)
    source_payload = {
        "schema": "mcmc-iter004-source-manifest-v1", "site": site,
        "repository_start_commit": config["repository_start_commit"],
        "plan_sha256": config["plan_sha256"], "source_hashes": source_hashes(),
        "emcee_version": config["emcee_version"],
        "emcee_de_move_sha256": config["emcee_de_move_sha256"],
        "emcee_de_snooker_sha256": config["emcee_de_snooker_sha256"],
        "emcee_hdf_backend_sha256": config["emcee_hdf_backend_sha256"],
    }
    source_sha = canonical_json_sha256(source_payload)
    search_contract = {
        "schema": "mcmc-iter004-candidate-search-contract-v1", "site": site,
        "seed": seed, "ppe_design_seed": config["ppe_design_seed"], "dimension": 18,
        "stage_one": 1024, "optional_stage_two": 1024, "maximum": 2048,
        "mapping": "Prior18.inverse_unit", "ranking_target": "physical_log_posterior_no_jacobian",
        "stage_two_triggers": [
            "fewer_than_512_finite_unique_eligible", "finite_rate_below_0.90",
            "eligible_rank_below_18", "eligible_condition_above_1000",
            "eligible_percentile_span_below_0.75", "eligible_decile_occupancy_below_8",
            "provisional_pool_gate_failure",
        ],
        "target_sha256": target_sha, "source_sha256": source_sha,
    }
    write_json_exclusive(root / "target_manifest.json", target_payload)
    write_json_exclusive(root / "source_manifest.json", source_payload)
    write_json_exclusive(root / "candidate_search_contract.json", search_contract)
    started = time.perf_counter()
    unit = scrambled_sobol_prefix(dimension=18, count=1024, seed=seed)
    physical = prior_aware_candidates(prior, unit)
    scored = score_candidates(posterior, physical, int(config["candidate_batch_size"]))
    transform_eligible, transform_reasons = sampling_eligibility(prior, physical)
    eligible = np.isfinite(scored["log_posterior"]) & transform_eligible
    assessment = assess_stage_one(unit, eligible)
    provisional_failure = None
    if assessment.stage_pass:
        try:
            provisional = select_candidate_pool(
                unit=unit, physical=physical, log_posterior=scored["log_posterior"], eligible=eligible,
            )
            validate_pool_geometry(unit[provisional])
        except ValueError as exc:
            provisional_failure = str(exc)
    stage_two_used = not assessment.stage_pass or provisional_failure is not None
    if stage_two_used:
        maximum_unit = scrambled_sobol_prefix(dimension=18, count=2048, seed=seed)
        np.testing.assert_array_equal(unit, maximum_unit[:1024])
        extra_physical = prior_aware_candidates(prior, maximum_unit[1024:])
        extra_scored = score_candidates(posterior, extra_physical, int(config["candidate_batch_size"]))
        unit = maximum_unit
        physical = np.vstack((physical, extra_physical))
        for key in scored:
            scored[key] = np.concatenate((scored[key], extra_scored[key]))
        transform_eligible, transform_reasons = sampling_eligibility(prior, physical)
        eligible = np.isfinite(scored["log_posterior"]) & transform_eligible
    final_assessment = assess_stage_one(unit, eligible)
    require(final_assessment.stage_pass, f"{site} maximum candidate prefix failed coverage gates: {final_assessment.failure_reasons}")
    pool = select_candidate_pool(
        unit=unit, physical=physical, log_posterior=scored["log_posterior"], eligible=eligible,
    )
    pool_geometry = validate_pool_geometry(unit[pool])
    elapsed = time.perf_counter() - started
    write_npz_exclusive(
        output, unit=unit, physical=physical, candidate_index=np.arange(unit.shape[0], dtype=np.int64),
        site=np.full(unit.shape[0], site, dtype="U4"),
        target_sha256=np.full(unit.shape[0], target_sha, dtype="U64"),
        source_sha256=np.full(unit.shape[0], source_sha, dtype="U64"),
        eligible=eligible, transform_reason=np.asarray([reason or "valid" for reason in transform_reasons], dtype="U64"),
        **scored,
    )
    write_json_exclusive(root / "search_report.json", {
        "schema": "mcmc-iter004-candidate-search-v1", "site": site, "result": "pass",
        "seed": seed, "ppe_design_seed": config["ppe_design_seed"], "stage_two_used": stage_two_used,
        "stage_one_assessment": assessment.to_dict(), "provisional_pool_failure": provisional_failure,
        "final_assessment": final_assessment.to_dict(), "pool_geometry": pool_geometry.to_dict(),
        "generated": int(unit.shape[0]), "finite_eligible": int(np.sum(eligible)),
        "elapsed_seconds": elapsed, "throughput_per_second": unit.shape[0] / elapsed,
        "peak_rss_gib": peak_rss_gib(),
        "numerical_rejections": {reason: int(np.sum(scored["reason"] == reason)) for reason in np.unique(scored["reason"])},
        "candidate_scores_sha256": sha256_file(output),
        "target_manifest_sha256": sha256_file(root / "target_manifest.json"),
        "source_manifest_sha256": sha256_file(root / "source_manifest.json"),
        "search_contract_sha256": sha256_file(root / "candidate_search_contract.json"),
        "posterior_target_sha256": target_sha, "source_identity_sha256": source_sha,
        "source_hashes": source_hashes(),
    })
    print(f"MCMC_ITER004_SEARCH_PASS site={site} stage_two={stage_two_used}")


def posterior_target_payload(config: dict[str, Any], site: str, posterior=None) -> dict[str, Any]:
    if posterior is None:
        posterior = load_posterior(config, site)
    soil = posterior.observations.soil_cn
    return {
        "schema": "mcmc-iter004-target-v1", "site": site, "prior_id": PPE1,
        "parameter_names": list(posterior.prior.names),
        "prior_files": {
            "parameter_file_sha256": sha256_file(posterior.prior.parameter_file),
            "generator_file_sha256": sha256_file(posterior.prior.generator_file),
            "metadata_file_sha256": sha256_file(posterior.prior.metadata_file),
        },
        "full_window": [config["full_window_start"], config["full_window_end"]],
        "gpp_resolution": config["gpp_resolution"], "sr_resolution": config["sr_resolution"],
        "include_cn": config["include_cn"], "cn_observation_cv": config["cn_observation_cv"],
        "release_manifest": config["surrogate_release_manifest_sha256"],
        "surrogate_catalog": config["surrogate_catalog_sha256"],
        "snapshot": config["snapshot_sha256"], "member_split": config["member_split_sha256"],
        "observation_catalog": config["observation_catalog_sha256"],
        "observation_manifest": config["observation_manifest_sha256"],
        "observation_validation": config["observation_validation_sha256"],
        "uncertainty_handoff": config["uncertainty_handoff_sha256"],
        "uncertainty_manifest": config["uncertainty_manifest_sha256"],
        "uncertainty_validation": config["uncertainty_validation_sha256"],
        "site_uncertainty_product": posterior.observations.uncertainty_product_sha256,
        "site_soil_product": posterior.observations.soil_product_sha256,
        "site_depth_source": posterior.observations.depth_source_sha256,
        "gpp_output_policy": "hard_zero_v1", "sr_output_policy": "unclipped",
        "fixed_cn_covariance": np.asarray(soil.covariance_by_cv[float(config["cn_observation_cv"])], dtype=float).tolist(),
        "fixed_cn_bias_correction": np.asarray(soil.total_bias_correction, dtype=float).tolist(),
        "coordinate_transform": posterior.prior.coordinate_transform.metadata(),
        "source_hashes": source_hashes(),
    }


def validate_accounting_only_source_transition(
    *, stored: dict[str, str], current: dict[str, str], compatibility: dict[str, str], label: str,
) -> None:
    differences = sorted(
        path for path in set(stored) | set(current) if stored.get(path) != current.get(path)
    )
    require(differences == [compatibility["path"]]
            and stored[compatibility["path"]] == compatibility["search_sha256"]
            and current[compatibility["path"]] == compatibility["current_sha256"]
            and compatibility["classification"] == "accounting_only_no_posterior_change",
            f"{label} accounting-only source compatibility mismatch: {differences}")


def _sampler_identity(config: dict[str, Any], site: str, *, seed: int, pool_path: Path, walker_path: Path) -> dict[str, Any]:
    target_sha = canonical_json_sha256(posterior_target_payload(config, site))
    prior = Prior18.from_directory(PPE1, config["ppe1_root"])
    return {
        "site": site, "prior_id": PPE1, "parameter_names": list(prior.names),
        "posterior_target_sha256": target_sha, "pool_sha256": sha256_file(pool_path),
        "walker_sha256": sha256_file(walker_path), "emcee_version": emcee.__version__,
        "move_configuration": config["move_configuration"], "seed": int(seed),
        "nwalkers": 64, "ndim": 18,
    }


def pool_restart(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    package_root = REPO_ROOT / "development/mcmc_optimization/slurm/iter004"
    package_review_path = runtime / "reviews" / "package_review.json"
    require(package_review_path.is_file(), "independent correction-package review artifact missing")
    validate_independent_review(
        json.loads(package_review_path.read_text(encoding="utf-8")),
        schema="mcmc-iter004-package-review-v1",
        reviewed_artifacts={
            "config_sha256": sha256_file(package_root / "iter004_config.json"),
            "checksum_manifest_sha256": sha256_file(package_root / "execution_files.sha256"),
            "execution_manifest_sha256": sha256_file(package_root / "execution_manifest.json"),
            "driver_sha256": sha256_file(package_root / "run_iter004.py"),
            "test_runner_sha256": sha256_file(package_root / "run_iter004_tests.py"),
        },
    )
    combined = {}
    for site in config["sites"]:
        candidate_root = runtime / "sites" / site / "candidates"
        candidate_path = candidate_root / "candidate_scores.npz"
        require(candidate_path.is_file(), f"missing {site} candidate evidence")
        search_report = json.loads((candidate_root / "search_report.json").read_text(encoding="utf-8"))
        require(search_report.get("schema") == "mcmc-iter004-candidate-search-v1"
                and search_report.get("result") == "pass", f"{site} search report gate failed")
        require(search_report["candidate_scores_sha256"] == sha256_file(candidate_path),
                f"{site} candidate artifact hash mismatch")
        target_path = candidate_root / "target_manifest.json"
        source_path = candidate_root / "source_manifest.json"
        contract_path = candidate_root / "candidate_search_contract.json"
        require(search_report["target_manifest_sha256"] == sha256_file(target_path)
                and search_report["source_manifest_sha256"] == sha256_file(source_path)
                and search_report["search_contract_sha256"] == sha256_file(contract_path),
                f"{site} candidate manifest hash mismatch")
        target_payload = json.loads(target_path.read_text(encoding="utf-8"))
        source_payload = json.loads(source_path.read_text(encoding="utf-8"))
        target_sha = canonical_json_sha256(target_payload)
        source_sha = canonical_json_sha256(source_payload)
        current_target = posterior_target_payload(config, site)
        stored_target_sources = target_payload["source_hashes"]
        current_target_sources = current_target["source_hashes"]
        stored_target_scientific = {key: value for key, value in target_payload.items() if key != "source_hashes"}
        current_target_scientific = {key: value for key, value in current_target.items() if key != "source_hashes"}
        require(stored_target_scientific == current_target_scientific,
                f"{site} scientific target manifest mismatch")
        compatibility = config["candidate_source_compatibility"]
        validate_accounting_only_source_transition(
            stored=stored_target_sources, current=current_target_sources,
            compatibility=compatibility, label=f"{site} target manifest",
        )
        stored_sources = source_payload["source_hashes"]
        current_sources = source_hashes()
        require(stored_target_sources == stored_sources,
                f"{site} target/source stored source maps differ")
        validate_accounting_only_source_transition(
            stored=stored_sources, current=current_sources,
            compatibility=compatibility, label=f"{site} source manifest",
        )
        require(search_report["posterior_target_sha256"] == target_sha
                and search_report["source_identity_sha256"] == source_sha,
                f"{site} target/source identity mismatch")
        values = np.load(candidate_path, allow_pickle=False)
        validate_candidate_identity_arrays(
            site_values=values["site"], target_values=values["target_sha256"],
            source_values=values["source_sha256"], candidate_indices=values["candidate_index"],
            expected_site=site, expected_target_sha256=target_sha,
            expected_source_sha256=source_sha,
        )
        pool_positions = select_candidate_pool(
            unit=values["unit"], physical=values["physical"], log_posterior=values["log_posterior"],
            eligible=values["eligible"], candidate_indices=values["candidate_index"],
        )
        pool_unit = values["unit"][pool_positions]
        pool_physical = values["physical"][pool_positions]
        pool_indices = values["candidate_index"][pool_positions]
        selection_scores = values["log_posterior"][pool_positions]
        pool_geometry = validate_pool_geometry(pool_unit)
        posterior = load_posterior(config, site)
        require(np.all(np.asarray(posterior.prior.support_mask(pool_physical), dtype=bool)),
                f"{site} pool prior support failed")
        require(np.unique(np.asarray(pool_physical, dtype="<f8"), axis=0).shape[0] == 256,
                f"{site} pool physical uniqueness failed")
        np.testing.assert_allclose(physical_to_unit(posterior.prior, pool_physical), pool_unit,
                                   rtol=1e-12, atol=1e-12)
        replay = score_candidates(posterior, pool_physical, 64)
        pool_root = runtime / "sites" / site / "pool"
        tolerance = config["batch_equivalence_tolerances"]
        replay_components = (
            "log_prior", "log_likelihood_gpp", "log_likelihood_sr",
            "log_likelihood_cn", "log_posterior",
        )
        parity_rows = []
        parity_maxima = {}
        failing = {}
        for component in replay_components:
            stored = np.asarray(values[component][pool_positions], dtype=float)
            current = np.asarray(replay[component], dtype=float)
            finite_pair = np.isfinite(current) & np.isfinite(stored)
            absolute = np.where(finite_pair, np.abs(current - stored), np.inf)
            relative = np.where(
                finite_pair,
                absolute / np.maximum(np.maximum(np.abs(stored), np.abs(current)), np.finfo(float).tiny),
                np.inf,
            )
            allowed = float(tolerance["atol"]) + float(tolerance["rtol"]) * np.abs(stored)
            normalized = np.where(
                finite_pair & np.isfinite(allowed),
                absolute / np.maximum(allowed, np.finfo(float).tiny),
                np.inf,
            )
            within = finite_pair & np.isfinite(allowed) & (absolute <= allowed)
            parity_maxima[component] = {
                "maximum_absolute_delta": json_number(np.max(absolute)),
                "maximum_relative_delta": json_number(np.max(relative)),
                "maximum_normalized_tolerance_use": json_number(np.max(normalized)),
            }
            failing[component] = np.flatnonzero(~within).astype(int).tolist()
            for position in range(256):
                if component == replay_components[0]:
                    parity_rows.append({
                        "pool_position": position,
                        "candidate_index": int(pool_indices[position]),
                        "physical_parameters": pool_physical[position].tolist(),
                        "replay_reason": str(replay["reason"][position]),
                        "surrogate_evaluated": bool(replay["surrogate_evaluated"][position]),
                        "components": {},
                    })
                parity_rows[position]["components"][component] = {
                    "stored": json_number(stored[position]),
                    "replayed": "NaN" if np.isnan(current[position]) else json_number(current[position]),
                    "absolute_delta": json_number(absolute[position]),
                    "relative_delta": json_number(relative[position]),
                    "allowed_delta": json_number(allowed[position]),
                    "normalized_tolerance_use": json_number(normalized[position]),
                    "within_tolerance": bool(within[position]),
                }
        parity_pass = not any(failing.values())
        job_id = os.environ.get("SLURM_JOB_ID", "no_slurm_job")
        parity_path = pool_root / f"pool_replay_parity_{job_id}.json"
        write_json_exclusive(parity_path, {
            "schema": "mcmc-iter004-pool-replay-parity-v1",
            "site": site,
            "job_id": job_id,
            "batch_size": 64,
            "tolerances": tolerance,
            "target_sha256": target_sha,
            "source_sha256": source_sha,
            "component_maxima": parity_maxima,
            "failing_pool_positions": failing,
            "rows": parity_rows,
            "result": "pass" if parity_pass else "fail",
        })
        print(f"{site} pool replay parity artifact: {parity_path}")
        print(json.dumps({"site": site, "result": "pass" if parity_pass else "fail",
                          "component_maxima": parity_maxima, "failing_pool_positions": failing},
                         sort_keys=True))
        require(parity_pass, f"{site} pool replay numerical parity failed; evidence={parity_path}")
        pool_path = pool_root / "pool.npz"
        write_npz_exclusive(
            pool_path, unit=pool_unit, physical=pool_physical, candidate_index=pool_indices,
            log_posterior=replay["log_posterior"], selection_log_posterior=selection_scores,
            log_prior=replay["log_prior"], log_likelihood_gpp=replay["log_likelihood_gpp"],
            log_likelihood_sr=replay["log_likelihood_sr"], log_likelihood_cn=replay["log_likelihood_cn"],
            target_sha256=np.asarray(target_sha), source_sha256=np.asarray(source_sha),
        )
        pool_ledger_path = pool_root / "pool_selection_ledger.json"
        pool_ledger = {
            "schema": "mcmc-iter004-pool-selection-ledger-v1", "site": site,
            "target_sha256": target_sha, "source_sha256": source_sha,
            "rule": "96 descending physical posterior then 160 greedy maximin in prior-unit coordinates",
            "entries": [
                {"pool_position": int(position), "candidate_index": int(pool_indices[position]),
                 "selection_component": "score" if position < 96 else "diversity",
                 "selection_log_posterior": float(selection_scores[position]),
                 "replayed_log_posterior": float(replay["log_posterior"][position])}
                for position in range(256)
            ],
        }
        validate_selection_ledger(
            pool_ledger, schema="mcmc-iter004-pool-selection-ledger-v1", site=site,
            count=256, target_sha256=target_sha, source_sha256=source_sha,
        )
        write_json_exclusive(pool_ledger_path, pool_ledger)
        walker_positions = select_walkers(
            unit=pool_unit, log_posterior=selection_scores, candidate_indices=pool_indices,
            seed=int(config["sites"][site]["walker_seed"]),
        )
        walker_unit = pool_unit[walker_positions]
        walker_physical = pool_physical[walker_positions]
        walker_sampler = posterior.prior.coordinate_transform.physical_to_sampler(walker_physical)
        walker_jacobian = posterior.prior.coordinate_transform.log_abs_det_dphysical_dsampler(walker_sampler)
        walker_geometry = validate_walker_geometry(walker_unit)
        require(np.all(np.isfinite(walker_sampler)) and np.all(np.isfinite(walker_jacobian))
                and np.unique(np.asarray(walker_physical, dtype="<f8"), axis=0).shape[0] == 64,
                f"{site} walker transformation/uniqueness failed")
        require(np.all(np.asarray(posterior.prior.support_mask(walker_physical), dtype=bool)),
                f"{site} walker prior support failed")
        walker_replay = score_candidates(posterior, walker_physical, 64)
        require(np.all(np.isfinite(walker_replay["log_posterior"])), f"{site} walker posterior is nonfinite")
        walker_root = runtime / "sites" / site / "walkers"
        walker_path = walker_root / "walkers.npz"
        write_npz_exclusive(
            walker_path, unit=walker_unit, physical=walker_physical, sampler=walker_sampler,
            pool_position=walker_positions, candidate_index=pool_indices[walker_positions],
            log_prior=walker_replay["log_prior"],
            log_likelihood_gpp=walker_replay["log_likelihood_gpp"],
            log_likelihood_sr=walker_replay["log_likelihood_sr"],
            log_likelihood_cn=walker_replay["log_likelihood_cn"],
            log_posterior=walker_replay["log_posterior"],
            log_abs_det_jacobian=walker_jacobian,
            target_sha256=np.asarray(target_sha), source_sha256=np.asarray(source_sha),
        )
        walker_ledger_path = walker_root / "walker_selection_ledger.json"
        walker_ledger = {
            "schema": "mcmc-iter004-walker-selection-ledger-v1", "site": site,
            "seed": int(config["sites"][site]["walker_seed"]),
            "target_sha256": target_sha, "source_sha256": source_sha,
            "rule": "16 score-focused then 48 greedy maximin in prior-unit coordinates",
            "entries": [
                {"walker": int(position), "pool_position": int(walker_positions[position]),
                 "candidate_index": int(pool_indices[walker_positions[position]]),
                 "selection_component": "score" if position < 16 else "diversity"}
                for position in range(64)
            ],
        }
        validate_selection_ledger(
            walker_ledger, schema="mcmc-iter004-walker-selection-ledger-v1", site=site,
            count=64, target_sha256=target_sha, source_sha256=source_sha,
        )
        write_json_exclusive(walker_ledger_path, walker_ledger)
        restart_root = runtime / "sites" / site / "restart"
        restart_identity = _sampler_identity(
            config, site, seed=int(config["sites"][site]["restart_seed"]),
            pool_path=pool_path, walker_path=walker_path,
        )
        uninterrupted = restart_root / "uninterrupted"
        split = restart_root / "split"
        run_sampler_block(
            posterior=posterior, initial_sampler_coordinates=walker_sampler,
            run_directory=uninterrupted, identity=restart_identity, target_iteration=16,
            checkpoint_interval=8,
        )
        run_sampler_block(
            posterior=posterior, initial_sampler_coordinates=walker_sampler,
            run_directory=split, identity=restart_identity, target_iteration=8,
            checkpoint_interval=8,
        )
        run_sampler_block(
            posterior=posterior, initial_sampler_coordinates=walker_sampler,
            run_directory=split, identity=restart_identity, target_iteration=16,
            checkpoint_interval=8, resume=True,
        )
        first = emcee.backends.HDFBackend(str(uninterrupted / "active_backend.h5"), read_only=True)
        second = emcee.backends.HDFBackend(str(split / "active_backend.h5"), read_only=True)
        exact = (
            np.array_equal(first.get_chain(), second.get_chain())
            and np.array_equal(first.get_log_prob(), second.get_log_prob())
            and np.array_equal(first.get_blobs(), second.get_blobs())
            and np.array_equal(first.accepted, second.accepted)
            and random_state_equal(first.get_last_sample().random_state, second.get_last_sample().random_state)
        )
        require(exact, f"{site} split/restart equivalence failed")
        uninterrupted_completed = finalize_sampler_run(uninterrupted, decision="restart_equivalence_fixture")
        split_completed = finalize_sampler_run(split, decision="restart_equivalence_pass")
        site_report = {
            "schema": "mcmc-iter004-pool-walker-restart-v1", "site": site, "result": "pass",
            "pool_geometry": pool_geometry.to_dict(), "walker_geometry": walker_geometry.to_dict(),
            "pool_sha256": sha256_file(pool_path), "walker_sha256": sha256_file(walker_path),
            "pool_selection_ledger_sha256": sha256_file(pool_ledger_path),
            "pool_replay_parity_sha256": sha256_file(parity_path),
            "walker_selection_ledger_sha256": sha256_file(walker_ledger_path),
            "target_manifest_sha256": sha256_file(target_path),
            "source_manifest_sha256": sha256_file(source_path),
            "posterior_target_sha256": target_sha, "source_identity_sha256": source_sha,
            "pool_selection_rule": "96 score + 160 diversity", "walker_selection_rule": "16 score + 48 diversity",
            "walker_seed": int(config["sites"][site]["walker_seed"]),
            "restart_seed": int(config["sites"][site]["restart_seed"]),
            "restart_exact": exact, "restart_identity": restart_identity,
            "uninterrupted_completed": uninterrupted_completed, "split_completed": split_completed,
            "peak_rss_gib": peak_rss_gib(),
        }
        write_json_exclusive(runtime / "sites" / site / "restart" / "validation_report.json", site_report)
        combined[site] = site_report
    write_json_exclusive(runtime / "results" / "pool_walker_restart_validation.json", {
        "schema": "mcmc-iter004-pool-walker-restart-combined-v1", "result": "pass", "sites": combined,
    })
    print("MCMC_ITER004_POOL_RESTART_PASS")


def pilot(config: dict[str, Any], site: str) -> None:
    runtime = Path(config["runtime_root"])
    pool_path = runtime / "sites" / site / "pool" / "pool.npz"
    walker_path = runtime / "sites" / site / "walkers" / "walkers.npz"
    require(pool_path.is_file() and walker_path.is_file(), f"{site} pool/walker gate missing")
    gate_path = runtime / "results" / "pool_walker_restart_validation.json"
    require(gate_path.is_file(), "common restart gate missing")
    gate_payload = json.loads(gate_path.read_text(encoding="utf-8"))
    require(gate_payload.get("schema") == "mcmc-iter004-pool-walker-restart-combined-v1"
            and gate_payload.get("result") == "pass", "common restart gate is invalid")
    site_gate = gate_payload["sites"][site]
    require(site_gate["pool_sha256"] == sha256_file(pool_path)
            and site_gate["walker_sha256"] == sha256_file(walker_path),
            f"{site} pool/walker identity drift")
    require(site_gate["pool_selection_ledger_sha256"] == sha256_file(runtime / "sites" / site / "pool/pool_selection_ledger.json")
            and site_gate["walker_selection_ledger_sha256"] == sha256_file(runtime / "sites" / site / "walkers/walker_selection_ledger.json"),
            f"{site} selection ledger identity drift")
    for run_name, completed_key in (("uninterrupted", "uninterrupted_completed"),
                                    ("split", "split_completed")):
        completed_path = runtime / "sites" / site / "restart" / run_name / "COMPLETED.json"
        completed_payload = json.loads(completed_path.read_text(encoding="utf-8"))
        require(completed_payload == site_gate[completed_key], f"{site} restart completed identity mismatch")
        run_root_check = completed_path.parent
        require(completed_payload["backend_sha256"] == sha256_file(run_root_check / "active_backend.h5")
                and completed_payload["proposal_ledger_sha256"] == sha256_file(run_root_check / "proposal_ledger.jsonl")
                and completed_payload["identity_sha256"] == sha256_file(run_root_check / "identity.json"),
                f"{site} restart artifact drift")
    walkers = np.load(walker_path, allow_pickle=False)
    posterior = load_posterior(config, site)
    identity = _sampler_identity(
        config, site, seed=int(config["sites"][site]["pilot_seed"]),
        pool_path=pool_path, walker_path=walker_path,
    )
    run_root = runtime / "sites" / site / "pilot"
    started = time.perf_counter()
    block = run_sampler_block(
        posterior=posterior, initial_sampler_coordinates=walkers["sampler"], run_directory=run_root,
        identity=identity, target_iteration=128, checkpoint_interval=64,
    )
    elapsed_128 = time.perf_counter() - started
    site_size_gib = directory_size_bytes(runtime / "sites" / site) / (1024.0 ** 3)
    total_size_gib = directory_size_bytes(runtime) / (1024.0 ** 3)
    gate = evaluate_continuation_gate(
        prior=posterior.prior, backend_path=run_root / "active_backend.h5",
        proposal_ledger_path=run_root / "proposal_ledger.jsonl",
        peak_rss_gib=peak_rss_gib(), projected_total_hours=(2.0 * elapsed_128 / 3600.0),
        projected_site_storage_gib=2.0 * site_size_gib,
        projected_total_storage_gib=2.0 * total_size_gib,
    )
    gate_outcome = continuation_outcome(gate)
    if gate_outcome == "iter004_validation_failed":
        failure_path = runtime / "sites" / site / "pilot_validation_failure.json"
        write_json_exclusive(failure_path, {
            "schema": "mcmc-iter004-site-pilot-failure-v1", "site": site,
            "result": "iter004_validation_failed", "continuation_gate": gate.to_dict(),
            "block": block, "elapsed_seconds": time.perf_counter() - started,
            "peak_rss_gib": peak_rss_gib(),
        })
        raise RuntimeError(f"{site} fatal pilot continuation gate failed: {gate.fatal_reasons}")
    continued = False
    if gate_outcome == "continue":
        block = run_sampler_block(
            posterior=posterior, initial_sampler_coordinates=walkers["sampler"], run_directory=run_root,
            identity=identity, target_iteration=256, checkpoint_interval=64, resume=True,
        )
        continued = True
    summary = summarize_pilot(
        prior=posterior.prior, backend_path=run_root / "active_backend.h5",
        proposal_ledger_path=run_root / "proposal_ledger.jsonl",
    )
    elapsed_total = time.perf_counter() - started
    limitation = bool(gate_outcome == "validated_with_nonfatal_limitation" or summary["mixing_limitations"])
    decision = "pilot_complete_with_limitations" if limitation else "pilot_complete"
    completed = finalize_sampler_run(run_root, decision=decision)
    report = {
        "schema": "mcmc-iter004-site-pilot-v1", "site": site, "result": "pass",
        "continued_to_256": continued, "continuation_gate": gate.to_dict(),
        "summary": summary, "block": block, "completed": completed,
        "elapsed_128_seconds": elapsed_128, "elapsed_total_seconds": elapsed_total,
        "steps_per_second": summary["iteration"] / elapsed_total,
        "estimated_1024_step_hours": elapsed_total / summary["iteration"] * 1024.0 / 3600.0,
        "peak_rss_gib": peak_rss_gib(),
        "decision": decision,
    }
    write_json_exclusive(runtime / "sites" / site / "pilot_report.json", report)
    print(f"MCMC_ITER004_PILOT_PASS site={site} steps={summary['iteration']} decision={decision}")


def diagnostics(config: dict[str, Any]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    runtime = Path(config["runtime_root"])
    combined = {}
    fatal_pilot = False
    for site in config["sites"]:
        report_path = runtime / "sites" / site / "pilot_report.json"
        run_root = runtime / "sites" / site / "pilot"
        failure_path = runtime / "sites" / site / "pilot_validation_failure.json"
        require(report_path.is_file() != failure_path.is_file(),
                f"{site} must have exactly one terminal pilot evidence type")
        if report_path.is_file():
            pilot_report = json.loads(report_path.read_text(encoding="utf-8"))
            require(pilot_report.get("schema") == "mcmc-iter004-site-pilot-v1"
                    and pilot_report.get("result") == "pass", f"{site} pilot report gate failed")
            completed_payload = json.loads((run_root / "COMPLETED.json").read_text(encoding="utf-8"))
            require(completed_payload == pilot_report["completed"], f"{site} completed-run manifest mismatch")
            require(completed_payload["backend_sha256"] == sha256_file(run_root / "active_backend.h5")
                    and completed_payload["proposal_ledger_sha256"] == sha256_file(run_root / "proposal_ledger.jsonl")
                    and completed_payload["identity_sha256"] == sha256_file(run_root / "identity.json"),
                    f"{site} completed pilot artifact drift")
        else:
            require(failure_path.is_file() and not (run_root / "COMPLETED.json").exists(),
                    f"missing exclusive {site} pilot failure evidence")
            pilot_report = json.loads(failure_path.read_text(encoding="utf-8"))
            require(pilot_report.get("schema") == "mcmc-iter004-site-pilot-failure-v1"
                    and pilot_report.get("result") == "iter004_validation_failed"
                    and pilot_report["continuation_gate"]["iteration"] == 128
                    and pilot_report["block"]["iteration"] == 128
                    and pilot_report["continuation_gate"]["fatal_reasons"],
                    f"{site} fatal pilot evidence gate failed")
            fatal_pilot = True
        expected_identity = _sampler_identity(
            config, site, seed=int(config["sites"][site]["pilot_seed"]),
            pool_path=runtime / "sites" / site / "pool/pool.npz",
            walker_path=runtime / "sites" / site / "walkers/walkers.npz",
        )
        expected_identity["posterior_target_sha256"] = config["sites"][site]["pilot_posterior_target_sha256"]
        expected_identity["schema"] = "mcmc-three-stage-sampler-identity-v1"
        observed_identity = json.loads((run_root / "identity.json").read_text(encoding="utf-8"))
        require(observed_identity == expected_identity,
                f"{site} pilot sampler identity mismatch")
        posterior = load_posterior(config, site)
        backend = emcee.backends.HDFBackend(str(runtime / "sites" / site / "pilot/active_backend.h5"), read_only=True)
        expected_iteration = 128 if pilot_report.get("result") == "iter004_validation_failed" else None
        require(int(backend.iteration) == expected_iteration if expected_iteration is not None
                else int(backend.iteration) in (128, 256), f"{site} pilot iteration is unsupported")
        if expected_iteration is not None:
            require(
                pilot_report["block"]["backend_sha256"] == sha256_file(run_root / "active_backend.h5")
                and pilot_report["block"]["proposal_ledger_sha256"] == sha256_file(run_root / "proposal_ledger.jsonl")
                and pilot_report["block"]["identity_sha256"] == canonical_json_sha256(observed_identity),
                f"{site} fatal pilot artifact identity mismatch",
            )
        chain = np.asarray(backend.get_chain(), dtype=np.float64)
        log_prob = np.asarray(backend.get_log_prob(), dtype=np.float64)
        blobs = np.asarray(backend.get_blobs())
        physical = posterior.prior.coordinate_transform.sampler_to_physical(chain)
        walker = np.load(runtime / "sites" / site / "walkers/walkers.npz", allow_pickle=False)
        best_flat = int(np.argmax(log_prob))
        best_step, best_walker = np.unravel_index(best_flat, log_prob.shape)
        initial_physical = walker["physical"][best_walker]
        final_physical = physical[best_step, best_walker]
        representative = []
        for label, theta in (("initial", initial_physical), ("best", final_physical)):
            result = posterior.evaluate(theta)
            inference = posterior.release.engine.predict(
                theta, site=site, forcing=posterior.forcing, time=posterior.time,
                start=posterior.start, end=posterior.end, member_chunk=1,
            )
            gpp_prediction = posterior.gpp_operator.aggregate_predictions(inference.gpp[0], posterior.start)
            sr_prediction = posterior.sr_operator.aggregate_predictions(inference.sr[0], posterior.start)
            depth_stocks = posterior.observations.soil_cn.depth_fraction * np.asarray(
                [inference.totsomc[0], inference.totsomn[0]], dtype=float
            )
            diagnostic_path = runtime / "sites" / site / "diagnostics" / f"representative_{label}.npz"
            write_npz_exclusive(
                diagnostic_path, parameters=theta, gpp_observed=posterior.gpp_operator.observed,
                gpp_predicted=gpp_prediction, sr_observed=posterior.sr_operator.observed,
                sr_predicted=sr_prediction, depth_adjusted_cn=depth_stocks,
                gpp_residual=posterior.gpp_operator.observed - gpp_prediction,
                sr_residual=posterior.sr_operator.observed - sr_prediction,
                observed_cn=posterior.observations.soil_cn.observed_stocks,
            )
            representative.append({"label": label, "posterior": result_payload(result),
                                   "artifact_sha256": sha256_file(diagnostic_path)})
        diag_root = runtime / "sites" / site / "diagnostics"
        diag_root.mkdir(parents=True, exist_ok=True)
        figure, axes = plt.subplots(3, 1, figsize=(10, 9), constrained_layout=True)
        axes[0].plot(log_prob, alpha=0.25); axes[0].set_title(f"{site} sampling log posterior")
        axes[1].hist(np.asarray(blobs["log_likelihood_gpp"]).ravel(), bins=40, alpha=0.6, label="GPP")
        axes[1].hist(np.asarray(blobs["log_likelihood_sr"]).ravel(), bins=40, alpha=0.6, label="SR")
        axes[1].hist(np.asarray(blobs["log_likelihood_cn"]).ravel(), bins=40, alpha=0.6, label="C/N")
        axes[1].legend(); axes[1].set_title("Likelihood components")
        axes[2].bar(np.arange(64), np.asarray(backend.accepted) / float(backend.iteration))
        axes[2].set_title("Acceptance fraction by walker"); axes[2].set_xlabel("walker")
        trace_path = diag_root / "pilot_diagnostics.png"
        figure.savefig(trace_path, dpi=160); plt.close(figure)
        parameter_figure, parameter_axes = plt.subplots(6, 3, figsize=(15, 18), constrained_layout=True)
        for index, axis in enumerate(parameter_axes.ravel()):
            axis.plot(physical[:, :, index], alpha=0.18, linewidth=0.6)
            axis.set_title(posterior.prior.names[index])
            axis.set_xlabel("step")
        parameter_trace_path = diag_root / "physical_parameter_traces.png"
        parameter_figure.savefig(parameter_trace_path, dpi=150); plt.close(parameter_figure)
        candidate = np.load(runtime / "sites" / site / "candidates/candidate_scores.npz", allow_pickle=False)
        pool = np.load(runtime / "sites" / site / "pool/pool.npz", allow_pickle=False)
        flat_unit = physical_to_unit(posterior.prior, physical.reshape(-1, 18))
        bound_occupancy = {
            name: {
                "lower_5pct": float(np.mean(flat_unit[:, index] <= 0.05)),
                "upper_5pct": float(np.mean(flat_unit[:, index] >= 0.95)),
            }
            for index, name in enumerate(posterior.prior.names)
        }
        eligible_positions = np.flatnonzero(candidate["eligible"])
        score_order = eligible_positions[np.lexsort((candidate["candidate_index"][eligible_positions],
                                                      -candidate["log_posterior"][eligible_positions]))]
        high_score_positions = score_order[:min(96, score_order.size)]
        candidate_component_quantiles = {
            component: np.quantile(candidate[component][eligible_positions], [0, .05, .25, .5, .75, .95, 1]).tolist()
            for component in ("log_prior", "log_likelihood_gpp", "log_likelihood_sr",
                              "log_likelihood_cn", "log_posterior")
        }
        final_component_quantiles = {
            component: np.quantile(np.asarray(blobs[component])[-1], [0, .25, .5, .75, 1]).tolist()
            for component in ("log_prior", "log_likelihood_gpp", "log_likelihood_sr", "log_likelihood_cn")
        }
        checkpoint_manifests = []
        for manifest_path in sorted((run_root / "checkpoints").glob("step_*/manifest.json")):
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            require(payload["backend_sha256"] == sha256_file(manifest_path.parent / "backend.h5"),
                    f"{site} checkpoint snapshot drift")
            checkpoint_manifests.append(payload)
        require(checkpoint_manifests, f"{site} checkpoint evidence missing")
        if expected_iteration is not None:
            require([item["step"] for item in checkpoint_manifests] == [64, 128],
                    f"{site} fatal pilot checkpoint sequence mismatch")
            final_checkpoint = checkpoint_manifests[-1]
            require(
                final_checkpoint["backend_sha256"] == pilot_report["block"]["backend_sha256"]
                and final_checkpoint["identity_sha256"] == pilot_report["block"]["identity_sha256"],
                f"{site} fatal pilot final checkpoint identity mismatch",
            )
        soil = posterior.observations.soil_cn
        combined[site] = {
            "pilot": pilot_report,
            "fatal_pilot": pilot_report.get("result") == "iter004_validation_failed",
            "candidate_generated": int(candidate["unit"].shape[0]),
            "candidate_finite": int(np.sum(candidate["eligible"])),
            "candidate_score_quantiles": np.quantile(candidate["log_posterior"][candidate["eligible"]], [0, .25, .5, .75, 1]).tolist(),
            "candidate_component_quantiles": candidate_component_quantiles,
            "high_score_region_count": int(high_score_positions.size),
            "high_score_region_geometry": geometry_metrics(candidate["unit"][high_score_positions]).to_dict(),
            "pool_geometry": geometry_metrics(pool["unit"]).to_dict(),
            "walker_geometry": geometry_metrics(walker["unit"]).to_dict(),
            "initial_physical_log_posterior_quantiles": np.quantile(
                walker["log_posterior"], [0, .25, .5, .75, 1]
            ).tolist(),
            "initial_component_quantiles": {
                component: np.quantile(walker[component], [0, .25, .5, .75, 1]).tolist()
                for component in ("log_prior", "log_likelihood_gpp", "log_likelihood_sr", "log_likelihood_cn")
            },
            "final_sampling_log_posterior_quantiles": np.quantile(
                log_prob[-1], [0, .25, .5, .75, 1]
            ).tolist(),
            "final_physical_log_posterior_quantiles": np.quantile(
                np.asarray(blobs["log_physical_posterior"])[-1], [0, .25, .5, .75, 1]
            ).tolist(),
            "final_component_quantiles": final_component_quantiles,
            "bound_occupancy": bound_occupancy,
            "representative": representative,
            "fixed_cn_provenance": {
                "observation_catalog_sha256": posterior.observations.release_catalog_sha256,
                "soil_product_sha256": posterior.observations.soil_product_sha256,
                "depth_source_sha256": posterior.observations.depth_source_sha256,
                "cv": float(config["cn_observation_cv"]),
                "covariance": np.asarray(soil.covariance_by_cv[float(config["cn_observation_cv"])], dtype=float).tolist(),
                "total_bias_correction": np.asarray(soil.total_bias_correction, dtype=float).tolist(),
            },
            "checkpoint_io": checkpoint_manifests,
            "diagnostic_figure_sha256": sha256_file(trace_path),
            "parameter_trace_figure_sha256": sha256_file(parameter_trace_path),
            "interpretation": "exploratory engineering pilot; no posterior convergence or calibrated interval claim",
        }
    storage = directory_size_bytes(runtime)
    require(storage <= int(config["storage_cap_bytes"]), "Iter004 storage cap exceeded")
    any_limitations = any(
        value["pilot"].get("decision") == "pilot_complete_with_limitations" for value in combined.values()
    )
    decision_candidate = (
        "iter004_validation_failed" if fatal_pilot else
        "mcmc_pilot_validated_with_limitations" if any_limitations else "mcmc_pilot_validated"
    )
    write_json_exclusive(runtime / "results" / "diagnostics_validation.json", {
        "schema": "mcmc-iter004-diagnostics-v1", "result": "pass", "sites": combined,
        "storage_bytes": storage, "storage_cap_bytes": config["storage_cap_bytes"],
        "decision_candidate": decision_candidate, "convergence_claimed": False,
        "peak_rss_gib": peak_rss_gib(),
    })
    print(f"MCMC_ITER004_DIAGNOSTICS_PASS decision_candidate={decision_candidate}")


def final(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    diagnostics_payload = json.loads((runtime / "results/diagnostics_validation.json").read_text())
    failure_closeout = diagnostics_payload["decision_candidate"] == "iter004_validation_failed"
    pilot_evidence = [
        runtime / "sites" / site / ("pilot_validation_failure.json" if failure_closeout else "pilot_report.json")
        for site in config["sites"]
    ]
    required = [
        runtime / "results/wu1_readiness.json",
        runtime / "results/pool_walker_restart_validation.json",
        runtime / "results/diagnostics_validation.json",
        runtime / "sites/ABBY/candidates/search_report.json",
        runtime / "sites/JERC/candidates/search_report.json",
        runtime / "manifests/pre_final_job_accounting.json",
        runtime / "reviews/result_review.json",
    ] + pilot_evidence
    missing = [str(path) for path in required if not path.is_file()]
    require(not missing, f"final verification missing evidence: {missing}")
    require(diagnostics_payload["result"] == "pass", "diagnostics gate did not pass")
    accounting_payload = json.loads((runtime / "manifests/pre_final_job_accounting.json").read_text(encoding="utf-8"))
    require(len(accounting_payload.get("attempts", [])) <= 15,
            "pre-final accounting leaves no capacity for the final planned job")
    expected_jobs = {name: cpus for name, cpus in PLANNED_JOB_CPUS.items() if name != "final_iter004.slurm"}
    accounting_validation = (
        validate_failure_closeout_accounting(
            accounting_payload, expected_jobs=expected_jobs,
            maximum_submissions=int(config["maximum_submissions"]),
        ) if failure_closeout else validate_job_accounting(
            accounting_payload, expected_jobs=expected_jobs,
            maximum_submissions=int(config["maximum_submissions"]), require_all_successful=True,
        )
    )
    review_path = runtime / "reviews/result_review.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_required = {
        "results/diagnostics_validation.json": sha256_file(runtime / "results/diagnostics_validation.json"),
        str(pilot_evidence[0].relative_to(runtime)): sha256_file(pilot_evidence[0]),
        str(pilot_evidence[1].relative_to(runtime)): sha256_file(pilot_evidence[1]),
        "manifests/pre_final_job_accounting.json": sha256_file(runtime / "manifests/pre_final_job_accounting.json"),
    }
    validate_independent_review(
        review_payload, schema="mcmc-iter004-result-review-v1",
        reviewed_artifacts=review_required,
        decision_candidate=diagnostics_payload["decision_candidate"],
    )
    require(directory_size_bytes(runtime) <= int(config["storage_cap_bytes"]), "storage cap exceeded")
    payload = {
        "schema": "mcmc-iter004-final-validation-v1", "result": "pass",
        "decision_candidate": diagnostics_payload["decision_candidate"],
        "required_evidence": {str(path.relative_to(runtime)): sha256_file(path) for path in required},
        "source_hashes": source_hashes(), "storage_bytes": directory_size_bytes(runtime),
        "submitted_job_count_before_final": len(accounting_payload["attempts"]),
        "accounting_validation": accounting_validation,
        "result_review_sha256": sha256_file(review_path),
    }
    write_json_exclusive(runtime / "results/final_validation.json", payload)
    print(f"MCMC_ITER004_FINAL_PASS decision={payload['decision_candidate']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "search", "pool-restart", "pilot", "diagnostics", "final"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--site", choices=("ABBY", "JERC"))
    args = parser.parse_args()
    config = load_config(args.config)
    if args.mode in ("search", "pilot"):
        require(args.site is not None, f"{args.mode} requires --site")
    if args.mode == "preflight": preflight(config)
    elif args.mode == "search": search(config, args.site)
    elif args.mode == "pool-restart": pool_restart(config)
    elif args.mode == "pilot": pilot(config, args.site)
    elif args.mode == "diagnostics": diagnostics(config)
    elif args.mode == "final": final(config)


if __name__ == "__main__":
    main()
