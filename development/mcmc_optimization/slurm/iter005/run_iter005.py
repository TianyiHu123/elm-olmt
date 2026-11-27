#!/usr/bin/env python3
"""Bounded Iter005 prior-unit sampler validation and site pilots on Puma compute nodes."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time
from typing import Any

import emcee
import numpy as np


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.mcmc_prior import PPE1, Prior18
from model_ELM.mcmc_three_stage_artifacts import (
    canonical_json_sha256, directory_size_bytes, sha256_file,
    write_json_exclusive, write_npz_exclusive,
)
from model_ELM.mcmc_three_stage_initialization import geometry_metrics
from model_ELM.mcmc_three_stage_observations import (
    CONFIG_SCHEMA as OBS_CONFIG_SCHEMA, ObservationReleaseConfig,
)
from model_ELM.mcmc_three_stage_posterior import load_three_stage_posterior
from model_ELM.mcmc_three_stage_release import (
    CONFIG_SCHEMA as RELEASE_CONFIG_SCHEMA, IMPLEMENTATION_ID, ThreeStageReleaseConfig,
)
from model_ELM.mcmc_three_stage_sampler import (
    REASON_CODES, finalize_sampler_run, random_state_equal, run_sampler_block,
)
from model_ELM.mcmc_three_stage_sampler_geometry import COORDINATE_SYSTEM_ID


SITES = ("ABBY", "JERC")
OLD_TARGET_FIELDS = (
    "site", "prior_id", "parameter_names", "prior_files", "full_window",
    "gpp_resolution", "sr_resolution", "include_cn", "cn_observation_cv",
    "release_manifest", "surrogate_catalog", "snapshot", "member_split",
    "observation_catalog", "observation_manifest", "observation_validation",
    "uncertainty_handoff", "uncertainty_manifest", "uncertainty_validation",
    "gpp_output_policy", "sr_output_policy",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    require(config["schema"] == "mcmc-optimization-iter005-config-v1", "configuration schema mismatch")
    require(config["repository_root"] == str(REPO_ROOT) and config["prior_id"] == PPE1,
            "repository or prior identity mismatch")
    require(config["coordinate_system_id"] == COORDINATE_SYSTEM_ID, "coordinate identity mismatch")
    require(config["emcee_version"] == emcee.__version__ and config["walker_count"] == 64,
            "sampler software or walker identity mismatch")
    require(config["pilot_steps"] == 128 and config["checkpoint_interval"] == 64,
            "pilot step or checkpoint contract mismatch")
    require(config["full_window_start"] == 720 and config["full_window_end"] == 61320
            and config["gpp_resolution"] == "daily" and config["sr_resolution"] == "daily"
            and config["include_cn"] is True and config["cn_observation_cv"] == 0.3,
            "scientific target drift")
    require(config["strict_tolerances"] == {"rtol": 1e-12, "atol": 1e-10, "component_sum_rtol": 0.0}
            and config["batch_tolerances"] == {"rtol": 1e-7, "atol": 1e-8},
            "locked numerical tolerances drift")
    require(config["planned_submissions"] == 5 and config["maximum_submissions"] == 10
            and config["preflight_correction_reruns"] == 1
            and config["shared_infrastructure_retries"] == 4
            and config["conditional_tolerance_correction_max"] == 1,
            "retry contract drift")
    return config


def release_config(config: dict[str, Any]) -> ThreeStageReleaseConfig:
    return ThreeStageReleaseConfig(
        schema=RELEASE_CONFIG_SCHEMA, implementation_id=IMPLEMENTATION_ID,
        prior_id=PPE1, release_id="release_0001",
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
        site=site, prior_id=PPE1, prior_root=config["ppe1_root"],
        surrogate_release=release_config(config),
        observation_release=observation_config(config),
        gpp_resolution="daily", sr_resolution="daily", cn_observation_cv=0.3,
        include_cn=True, start=720, end=61320, member_chunk=16,
        sampling_coordinate_system=COORDINATE_SYSTEM_ID,
    )


def rss_gib() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0**2


def preflight(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    prior = Prior18.from_directory(PPE1, config["ppe1_root"])
    checks = {
        "parameter": (prior.parameter_file, config["ppe1_parameter_sha256"]),
        "generator": (prior.generator_file, config["ppe1_generator_sha256"]),
        "metadata": (prior.metadata_file, config["ppe1_metadata_sha256"]),
        "release_constraints": (Path(config["surrogate_release_root"]) / "interface/parameter_constraints.json",
                                config["surrogate_parameter_constraints_sha256"]),
        "release_manifest": (Path(config["surrogate_release_root"]) / "release_manifest.json",
                             config["surrogate_release_manifest_sha256"]),
        "snapshot": (Path(config["snapshot_root"]) / "manifests/dataset_snapshot_r0001.json",
                     config["snapshot_sha256"]),
        "member_split": (Path(config["snapshot_root"]) / "splits/member_split_1024_v1.json",
                         config["member_split_sha256"]),
    }
    for label, (path, digest) in checks.items():
        require(sha256_file(path) == digest, f"{label} source identity mismatch")
    snapshot_payload = json.loads(checks["snapshot"][0].read_text())
    common_source_path = Path(config["snapshot_root"]) / "manifests/sources/common_v1.json"
    require(snapshot_payload["artifacts"]["manifests/sources/common_v1.json"]["sha256"]
            == config["snapshot_common_source_sha256"]
            and sha256_file(common_source_path) == config["snapshot_common_source_sha256"],
            "frozen surrogate snapshot common-source identity mismatch")
    env_root = Path(config["python"]).parent.parent
    site_packages = env_root / "lib/python3.11/site-packages/emcee"
    emcee_checks = {
        "metadata": (env_root / "conda-meta/emcee-3.1.6-pyhd8ed1ab_1.json",
                     config["emcee_conda_metadata_sha256"]),
        "de_move": (site_packages / "moves/de.py", config["emcee_de_move_sha256"]),
        "de_snooker": (site_packages / "moves/de_snooker.py", config["emcee_de_snooker_sha256"]),
        "hdf_backend": (site_packages / "backends/hdf.py", config["emcee_hdf_backend_sha256"]),
    }
    for label, (path, digest) in emcee_checks.items():
        require(sha256_file(path) == digest, f"emcee {label} identity mismatch")
    released = json.loads(checks["release_constraints"][0].read_text())
    metadata = json.loads(prior.metadata_file.read_text())
    snapshot_common = json.loads(common_source_path.read_text())
    snapshot_sampling = snapshot_common["sampling_metadata"]
    require(tuple(released["parameter_order"]) == prior.names and len(released["parameters"]) == 18,
            "development parameter order/dimension mismatch")
    require(tuple(snapshot_common["parameter_names"]) == prior.names
            and tuple(snapshot_sampling["parameter_names"]) == prior.names
            and len(snapshot_sampling["transforms"]) == 18,
            "development snapshot parameter order/dimension mismatch")
    for index, item in enumerate(released["parameters"]):
        require(item["name"] == prior.names[index]
                and float(item["lower"]) == float(prior.lower[index])
                and float(item["upper"]) == float(prior.upper[index])
                and float(metadata["transforms"][index]["lower"]) == float(prior.lower[index])
                and float(metadata["transforms"][index]["upper"]) == float(prior.upper[index])
                and snapshot_sampling["transforms"][index]["name"] == prior.names[index]
                and float(snapshot_sampling["transforms"][index]["lower"]) == float(prior.lower[index])
                and float(snapshot_sampling["transforms"][index]["upper"]) == float(prior.upper[index]),
                f"development bounds-equivalence mismatch at index {index}")
    cn = released["conditional_cn_constraint"]
    require(cn["enabled"] is True and cn["leafcn_index"] == 16 and cn["frootcn_index"] == 17
            and float(cn["gap"]) == 0.5 and float(cn["livewoodcn"]) == 50.0,
            "development conditional C:N metadata mismatch")
    snapshot_cn = snapshot_sampling["cn_constraint"]
    require(snapshot_cn["enabled"] is True and snapshot_cn["leafcn_index"] == cn["leafcn_index"]
            and snapshot_cn["frootcn_index"] == cn["frootcn_index"]
            and float(snapshot_cn["gap"]) == float(cn["gap"])
            and float(snapshot_cn["livewoodcn"]) == float(cn["livewoodcn"]),
            "development snapshot conditional C:N metadata mismatch")
    write_json_exclusive(runtime / "results/development_bounds_validation.json", {
        "schema": "mcmc-iter005-development-bounds-equivalence-v1",
        "result": "pass", "checks": {key: digest for key, (_, digest) in checks.items()},
        "snapshot_common_source_sha256": config["snapshot_common_source_sha256"],
        "emcee_checks": {key: digest for key, (_, digest) in emcee_checks.items()},
        "parameter_names": list(prior.names), "bounds_equal": True,
        "conditional_cn_equal": True, "scope": "development_validation_only",
    })
    write_json_exclusive(runtime / "results/preflight.json", {
        "schema": "mcmc-iter005-preflight-v1", "result": "pass",
        "coordinate_system_id": COORDINATE_SYSTEM_ID,
        "development_bounds_sha256": sha256_file(runtime / "results/development_bounds_validation.json"),
        "peak_rss_gib": rss_gib(),
    })
    print("MCMC_ITER005_PREFLIGHT_PASS")


def old_site_files(config: dict[str, Any], site: str) -> dict[str, Path]:
    root = Path(config["iter004_root"]) / "sites" / site
    return {
        "pool": root / "pool/pool.npz",
        "walkers": root / "walkers/walkers.npz",
        "ledger": root / "walkers/walker_selection_ledger.json",
        "target": root / "candidates/target_manifest.json",
        "source": root / "candidates/source_manifest.json",
        "old_identity": root / "pilot/identity.json",
    }


def new_target(config: dict[str, Any], site: str, posterior) -> dict[str, Any]:
    soil = posterior.observations.soil_cn
    return {
        "schema": "mcmc-iter005-physical-target-v1", "site": site,
        "prior_id": PPE1, "parameter_names": list(posterior.prior.names),
        "prior_files": {
            "parameter_file_sha256": config["ppe1_parameter_sha256"],
            "generator_file_sha256": config["ppe1_generator_sha256"],
            "metadata_file_sha256": config["ppe1_metadata_sha256"],
        },
        "full_window": [720, 61320], "gpp_resolution": "daily", "sr_resolution": "daily",
        "include_cn": True, "cn_observation_cv": 0.3,
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
        "fixed_cn_covariance": np.asarray(soil.covariance_by_cv[0.3], dtype=float).tolist(),
        "fixed_cn_bias_correction": np.asarray(soil.total_bias_correction, dtype=float).tolist(),
    }


def sampler_identity(config: dict[str, Any], site: str, *, seed: int,
                     target_sha: str, coordinate_sha: str) -> dict[str, Any]:
    site_config = config["sites"][site]
    prior = Prior18.from_directory(PPE1, config["ppe1_root"])
    return {
        "site": site, "prior_id": PPE1, "parameter_names": list(prior.names),
        "posterior_target_sha256": target_sha,
        "pool_sha256": site_config["old_pool_sha256"],
        "walker_sha256": site_config["old_walker_sha256"],
        "emcee_version": emcee.__version__,
        "move_configuration": config["move_configuration"],
        "seed": int(seed), "nwalkers": 64, "ndim": 18,
        "coordinate_system_id": COORDINATE_SYSTEM_ID,
        "geometry_source_sha256": sha256_file(REPO_ROOT / "model_ELM/mcmc_three_stage_sampler_geometry.py"),
        "sampler_source_sha256": sha256_file(REPO_ROOT / "model_ELM/mcmc_three_stage_sampler.py"),
        "posterior_source_sha256": sha256_file(REPO_ROOT / "model_ELM/mcmc_three_stage_posterior.py"),
        "execution_checksum_manifest_sha256": sha256_file(
            Path(config["runtime_root"]) / "manifests/execution_files.sha256"
        ),
        "release_manifest_sha256": config["surrogate_release_manifest_sha256"],
        "walker_coordinates_sha256": coordinate_sha,
    }


def component_array(results: list[Any], field: str) -> np.ndarray:
    return np.asarray([getattr(row, field) for row in results], dtype=np.float64)


def density(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    require(json.loads((runtime / "results/preflight.json").read_text())["result"] == "pass",
            "preflight gate missing")
    reference_root = Path(config["iter003_reference_root"])
    require(sha256_file(reference_root / "posterior_validation.json") == config["iter003_posterior_sha256"]
            and sha256_file(reference_root / "likelihood_reference_tests.json") == config["iter003_references_sha256"],
            "Iter003 independent reference identity mismatch")
    reference_cases = json.loads((reference_root / "likelihood_reference_tests.json").read_text())["cases"]
    reports = {}
    for site in SITES:
        started = time.perf_counter()
        source = old_site_files(config, site)
        site_config = config["sites"][site]
        for label, key in (("pool", "old_pool_sha256"), ("walkers", "old_walker_sha256"),
                           ("ledger", "old_walker_ledger_sha256"),
                           ("target", "old_target_manifest_sha256"),
                           ("source", "old_source_manifest_sha256")):
            require(sha256_file(source[label]) == site_config[key],
                    f"{site} Iter004 {label} identity mismatch")
        posterior = load_posterior(config, site)
        midpoint = posterior.prior.inverse_unit(np.full(18, 0.5))
        midpoint_result = posterior.evaluate(midpoint)
        reference_differences = {}
        for kind, field in (("GPP_daily", "log_likelihood_gpp"),
                            ("SR_daily", "log_likelihood_sr"),
                            ("joint_cn", "log_likelihood_cn")):
            matches = [row for row in reference_cases if row["site"] == site
                       and row["kind"] == kind
                       and (kind != "joint_cn" or row["cn_observation_cv"] == 0.3)]
            require(len(matches) == 1, f"{site} independent midpoint reference missing: {kind}")
            actual = float(getattr(midpoint_result, field))
            expected = float(matches[0]["reference"])
            require(np.isclose(actual, expected, rtol=1e-12, atol=1e-10),
                    f"{site} strict midpoint reference failure: {kind}")
            reference_differences[kind] = abs(actual - expected)
        require(np.isclose(midpoint_result.log_prior, posterior.prior.log_density(midpoint),
                           rtol=1e-12, atol=1e-10)
                and abs(midpoint_result.log_posterior - (
                    midpoint_result.log_prior + midpoint_result.log_likelihood_gpp
                    + midpoint_result.log_likelihood_sr + midpoint_result.log_likelihood_cn
                )) <= 1e-10,
                f"{site} strict midpoint prior/component sum failure")
        target = new_target(config, site, posterior)
        old_target = json.loads(source["target"].read_text())
        for key in OLD_TARGET_FIELDS:
            require(old_target[key] == target[key], f"{site} physical target changed: {key}")
        for key in ("site_uncertainty_product", "site_soil_product", "site_depth_source",
                    "fixed_cn_covariance", "fixed_cn_bias_correction"):
            require(old_target[key] == target[key], f"{site} fixed target product changed: {key}")
        old_ledger = json.loads(source["ledger"].read_text())
        require(old_ledger["site"] == site and len(old_ledger["entries"]) == 64,
                f"{site} old walker selection ledger invalid")
        with np.load(source["walkers"], allow_pickle=False) as saved:
            theta = np.asarray(saved["physical"], dtype=np.float64)
            saved_unit = np.asarray(saved["unit"], dtype=np.float64)
            saved_components = {key: np.asarray(saved[key], dtype=np.float64) for key in (
                "log_prior", "log_likelihood_gpp", "log_likelihood_sr",
                "log_likelihood_cn", "log_posterior")}
        require(theta.shape == (64, 18) and saved_unit.shape == (64, 18)
                and np.unique(np.asarray(theta, dtype="<f8"), axis=0).shape[0] == 64
                and np.all(posterior.prior.support_mask(theta)),
                f"{site} physical walkers invalid")
        geometry = posterior.sampling_geometry
        z = np.asarray(geometry.physical_to_sampler(theta), dtype=np.float64)
        unit = np.asarray(geometry.sampler_to_unit(z), dtype=np.float64)
        require(np.allclose(unit, saved_unit, rtol=0, atol=1e-12)
                and np.allclose(geometry.sampler_to_physical(z), theta, rtol=1e-12, atol=0),
                f"{site} strict walker mapping replay failed")
        physical_results = posterior.evaluate_batch(theta)
        sampling_results = posterior.evaluate_sampling_batch(z)
        for name, saved_values in saved_components.items():
            replay = component_array(physical_results, name)
            require(np.all(np.isfinite(replay))
                    and np.allclose(replay, saved_values, rtol=1e-7, atol=1e-8),
                    f"{site} stored physical target replay failed: {name}")
            sampled = component_array([row.physical for row in sampling_results], name)
            require(np.allclose(sampled, replay, rtol=1e-7, atol=1e-8),
                    f"{site} sampling physical component changed: {name}")
        numerical_residuals = {
            "prior_jacobian_cancellation": [],
            "physical_component_sum": [],
            "same_theta_normalized_density": [],
            "archived_vs_reconstructed_density": [],
            "full_jacobian_identity": [],
        }
        strict = config["strict_tolerances"]
        batch = config["batch_tolerances"]
        for index, row in enumerate(sampling_results):
            u = unit[index]
            unit_log_density = float(np.sum(np.log(u) + np.log1p(-u)))
            same_theta_components = (row.physical.log_prior
                                     + row.physical.log_likelihood_gpp
                                     + row.physical.log_likelihood_sr
                                     + row.physical.log_likelihood_cn)
            same_theta_alternative = (row.physical.log_likelihood_gpp
                                      + row.physical.log_likelihood_sr
                                      + row.physical.log_likelihood_cn
                                      + unit_log_density)
            archived_theta_alternative = (physical_results[index].log_likelihood_gpp
                                          + physical_results[index].log_likelihood_sr
                                          + physical_results[index].log_likelihood_cn
                                          + unit_log_density)
            residuals = {
                "prior_jacobian_cancellation": abs(row.physical.log_prior
                                                   + row.log_abs_det_jacobian
                                                   - unit_log_density),
                "physical_component_sum": abs(row.physical.log_posterior
                                              - same_theta_components),
                "same_theta_normalized_density": abs(row.log_sampling_posterior
                                                      - same_theta_alternative),
                "archived_vs_reconstructed_density": abs(row.log_sampling_posterior
                                                          - archived_theta_alternative),
                "full_jacobian_identity": abs(row.log_sampling_posterior
                                              - (row.physical.log_posterior
                                                 + row.log_abs_det_jacobian)),
            }
            for name, residual in residuals.items():
                require(np.isfinite(residual), f"{site} nonfinite {name}: walker {index}")
                numerical_residuals[name].append(residual)
            require(residuals["prior_jacobian_cancellation"] <= 1e-9,
                    f"{site} prior/Jacobian cancellation failed: walker {index}, "
                    f"residual={residuals['prior_jacobian_cancellation']}")
            require(np.isclose(row.physical.log_posterior, same_theta_components,
                               rtol=strict["rtol"], atol=strict["atol"]),
                    f"{site} physical component sum failed: walker {index}, "
                    f"residual={residuals['physical_component_sum']}")
            require(np.isclose(row.log_sampling_posterior, same_theta_alternative,
                               rtol=strict["rtol"], atol=strict["atol"]),
                    f"{site} same-theta normalized density failed: walker {index}, "
                    f"residual={residuals['same_theta_normalized_density']}")
            require(np.isclose(row.log_sampling_posterior, archived_theta_alternative,
                               rtol=batch["rtol"], atol=batch["atol"]),
                    f"{site} archived/reconstructed density parity failed: walker {index}, "
                    f"residual={residuals['archived_vs_reconstructed_density']}")
            require(residuals["full_jacobian_identity"] <= 1e-9,
                    f"{site} full-Jacobian identity failed: walker {index}, "
                    f"residual={residuals['full_jacobian_identity']}")
        numerical_residuals = {
            name: {"maximum_absolute": float(max(values)),
                   "worst_walker": int(np.argmax(values))}
            for name, values in numerical_residuals.items()
        }
        site_root = runtime / "sites" / site
        write_json_exclusive(site_root / "density_numerical_residuals.json", {
            "schema": "mcmc-iter005-density-numerical-residuals-v1",
            "site": site,
            "strict_reference_tolerances": strict,
            "archived_vs_reconstructed_tolerances": batch,
            "residuals": numerical_residuals,
        })
        coordinate_path = site_root / "walkers/iter005_coordinates.npz"
        write_npz_exclusive(coordinate_path, physical=theta, unit=unit, sampler=z)
        coordinate_sha = sha256_file(coordinate_path)
        target_path = site_root / "walkers/physical_target.json"
        write_json_exclusive(target_path, target)
        target_sha = sha256_file(target_path)
        identity = sampler_identity(config, site, seed=int(site_config["restart_seed"]),
                                    target_sha=target_sha, coordinate_sha=coordinate_sha)
        restart_root = site_root / "restart"
        full = restart_root / "uninterrupted"
        split = restart_root / "split"
        run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                          run_directory=full, identity=identity, target_iteration=16,
                          checkpoint_interval=8)
        run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                          run_directory=split, identity=identity, target_iteration=8,
                          checkpoint_interval=8)
        run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                          run_directory=split, identity=identity, target_iteration=16,
                          checkpoint_interval=8, resume=True)
        a = emcee.backends.HDFBackend(str(full / "active_backend.h5"), read_only=True)
        b = emcee.backends.HDFBackend(str(split / "active_backend.h5"), read_only=True)
        exact = (a.iteration == b.iteration == 16
                 and np.array_equal(a.get_chain(), b.get_chain())
                 and np.array_equal(a.get_log_prob(), b.get_log_prob())
                 and np.array_equal(a.get_blobs(), b.get_blobs())
                 and np.array_equal(a.accepted, b.accepted)
                 and random_state_equal(a.get_last_sample().random_state,
                                        b.get_last_sample().random_state)
                 and sha256_file(full / "proposal_ledger.jsonl")
                     == sha256_file(split / "proposal_ledger.jsonl")
                 and sha256_file(full / "identity.json") == sha256_file(split / "identity.json"))
        for path in (full, split):
            for step in (8, 16):
                checkpoint = json.loads((path / f"checkpoints/step_{step:04d}/manifest.json").read_text())
                require(checkpoint["step"] == step
                        and checkpoint["identity_sha256"] == canonical_json_sha256({
                            **identity, "schema": "mcmc-three-stage-sampler-identity-v2"})
                        and checkpoint["backend_sha256"] == sha256_file(
                            path / f"checkpoints/step_{step:04d}/backend.h5"),
                        f"{site} restart checkpoint identity mismatch")
        require(exact, f"{site} new coordinate split/restart failed")
        old_copy = restart_root / "incompatible_old"
        old_copy.mkdir()
        shutil.copy2(source["old_identity"], old_copy / "identity.json")
        try:
            run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                              run_directory=old_copy, identity=identity,
                              target_iteration=17, checkpoint_interval=8, resume=True)
        except ValueError as exc:
            require("identity mismatch" in str(exc), "old backend protection reason mismatch")
        else:
            raise RuntimeError("old coordinate identity was accepted for resume")
        finalize_sampler_run(full, decision="restart_equivalence_fixture")
        finalize_sampler_run(split, decision="restart_equivalence_pass")
        reports[site] = {
            "result": "pass", "site": site, "old_walker_sha256": site_config["old_walker_sha256"],
            "coordinates_sha256": coordinate_sha, "target_sha256": target_sha,
            "restart_identity_sha256": canonical_json_sha256({**identity, "schema": "mcmc-three-stage-sampler-identity-v2"}),
            "restart_exact": exact, "old_identity_rejected": True,
            "strict_reference_absolute_differences": reference_differences,
            "numerical_residuals": numerical_residuals,
            "elapsed_seconds": time.perf_counter() - started, "peak_rss_gib": rss_gib(),
        }
        write_json_exclusive(restart_root / "validation_report.json", reports[site])
    write_json_exclusive(runtime / "results/density_restart_validation.json", {
        "schema": "mcmc-iter005-density-restart-v1", "result": "pass", "sites": reports,
    })
    print("MCMC_ITER005_DENSITY_RESTART_PASS")


def pilot(config: dict[str, Any], site: str) -> None:
    runtime = Path(config["runtime_root"])
    gate = json.loads((runtime / "results/density_restart_validation.json").read_text())
    require(gate["result"] == "pass" and gate["sites"][site]["restart_exact"],
            "density/restart gate missing")
    posterior = load_posterior(config, site)
    site_root = runtime / "sites" / site
    coordinate_path = site_root / "walkers/iter005_coordinates.npz"
    require(sha256_file(coordinate_path) == gate["sites"][site]["coordinates_sha256"],
            "walker coordinate identity mismatch")
    with np.load(coordinate_path, allow_pickle=False) as saved:
        initial = np.asarray(saved["sampler"], dtype=np.float64)
        initial_unit = np.asarray(saved["unit"], dtype=np.float64)
    target_sha = sha256_file(site_root / "walkers/physical_target.json")
    require(target_sha == gate["sites"][site]["target_sha256"], "physical target identity mismatch")
    identity = sampler_identity(config, site,
                                seed=int(config["sites"][site]["pilot_seed"]),
                                target_sha=target_sha,
                                coordinate_sha=gate["sites"][site]["coordinates_sha256"])
    started = time.perf_counter()
    run_root = site_root / "pilot"
    block = run_sampler_block(posterior=posterior, initial_sampler_coordinates=initial,
                              run_directory=run_root, identity=identity, target_iteration=128,
                              checkpoint_interval=64)
    for step in (64, 128):
        checkpoint = json.loads((run_root / f"checkpoints/step_{step:04d}/manifest.json").read_text())
        require(checkpoint["step"] == step
                and checkpoint["identity_sha256"] == block["identity_sha256"]
                and checkpoint["backend_sha256"] == sha256_file(
                    run_root / f"checkpoints/step_{step:04d}/backend.h5"),
                f"{site} pilot checkpoint identity mismatch")
    backend = emcee.backends.HDFBackend(str(run_root / "active_backend.h5"), read_only=True)
    chain = np.asarray(backend.get_chain(), dtype=np.float64)
    final = np.asarray(backend.get_last_sample().coords, dtype=np.float64)
    final_physical = posterior.sampling_geometry.sampler_to_physical(final)
    final_unit = posterior.sampling_geometry.sampler_to_unit(final)
    geometry = geometry_metrics(final_unit)
    acceptance_by_walker = np.asarray(backend.accepted, dtype=np.int64) / 128.0
    accepted_moves = int(np.sum(backend.accepted))
    displacements = np.linalg.norm(final_unit - initial_unit, axis=1)
    reason_counts = {str(value): 0 for value in REASON_CODES.values()}
    per_walker_saturation = np.zeros(64, dtype=np.int64)
    ordinary_rejections = 0
    ledger_accepted = 0
    proposals = 0
    with (run_root / "proposal_ledger.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            code = int(row["blob"]["reason_code"])
            reason_counts[str(code)] = reason_counts.get(str(code), 0) + 1
            if code == REASON_CODES["coordinate_saturation"]:
                per_walker_saturation[int(row["walker"])] += 1
            if code == 0 and not row["accepted"]:
                ordinary_rejections += 1
            ledger_accepted += int(bool(row["accepted"]))
            proposals += 1
    require(proposals == 8192 and chain.shape == (128, 64, 18),
            "pilot proposal or chain count mismatch")
    require(accepted_moves == ledger_accepted,
            "pilot acceptance ledger/backend mismatch")
    chain_unit = posterior.sampling_geometry.sampler_to_unit(chain.reshape(-1, 18)).reshape(128, 64, 18)
    boundary = np.mean((chain_unit < 0.01) | (chain_unit > 0.99), axis=(0, 1))
    gates = config["pilot_gates"]
    fatal = []
    limitation = []
    if reason_counts.get("1", 0) != 0:
        fatal.append("ordinary_mapped_support_violation")
    if sum(reason_counts.get(str(i), 0) for i in (2, 3, 4)) != 0:
        fatal.append("parameter_dependent_surrogate_numerical_failure")
    if reason_counts.get("5", 0) > gates["max_saturation_site"] or np.max(per_walker_saturation) > gates["max_saturation_walker"]:
        fatal.append("coordinate_saturation_threshold_exceeded")
    if np.unique(np.asarray(final_physical, dtype="<f8"), axis=0).shape[0] < gates["minimum_distinct_states"]:
        limitation.append("insufficient_distinct_final_states")
    if geometry.rank < gates["minimum_rank"] or geometry.condition_number > gates["maximum_condition"]:
        limitation.append("poor_final_state_geometry")
    overall_acceptance = accepted_moves / 8192.0
    if not gates["minimum_acceptance"] <= overall_acceptance <= gates["maximum_acceptance"]:
        limitation.append("acceptance_outside_range")
    if np.count_nonzero(acceptance_by_walker == 0.0) > gates["maximum_zero_move_walkers"]:
        limitation.append("too_many_zero_move_walkers")
    if float(np.median(displacements)) < gates["minimum_median_unit_displacement"]:
        limitation.append("insufficient_median_unit_displacement")
    elapsed = time.perf_counter() - started
    report = {
        "schema": "mcmc-iter005-site-pilot-v1", "site": site,
        "result": "iter005_validation_failed" if fatal else "pass",
        "fatal_reasons": fatal, "mixing_limitations": limitation,
        "coordinate_system_id": COORDINATE_SYSTEM_ID,
        "identity_sha256": block["identity_sha256"],
        "backend_sha256": block["backend_sha256"],
        "proposal_ledger_sha256": block["proposal_ledger_sha256"],
        "checkpoint_steps": [64, 128], "iteration": int(backend.iteration),
        "reason_counts": reason_counts, "ordinary_metropolis_rejections": ordinary_rejections,
        "accepted_moves": accepted_moves, "overall_acceptance": overall_acceptance,
        "acceptance_by_walker": acceptance_by_walker.tolist(),
        "zero_move_walkers": int(np.count_nonzero(acceptance_by_walker == 0.0)),
        "median_unit_displacement": float(np.median(displacements)),
        "displacement_by_walker": displacements.tolist(),
        "unique_final_states": int(np.unique(np.asarray(final_physical, dtype="<f8"), axis=0).shape[0]),
        "final_state_rank": geometry.rank, "final_state_condition": geometry.condition_number,
        "boundary_occupancy_by_parameter": boundary.tolist(),
        "saturation_by_walker": per_walker_saturation.tolist(),
        "elapsed_seconds": elapsed, "throughput_proposals_per_second": proposals / elapsed,
        "peak_rss_gib": rss_gib(), "storage_bytes": directory_size_bytes(run_root),
        "convergence_claimed": False,
    }
    write_json_exclusive(site_root / "pilot_report.json", report)
    if fatal:
        raise RuntimeError(f"{site} fatal Iter005 pilot gate: {fatal}")
    finalize_sampler_run(run_root, decision=("bounded_pilot_with_mixing_limitations"
                                             if limitation else "bounded_pilot_validated"))
    print(f"MCMC_ITER005_{site}_PILOT_PASS acceptance={overall_acceptance:.6f}")


def diagnostics(config: dict[str, Any]) -> None:
    runtime = Path(config["runtime_root"])
    sites = {}
    for site in SITES:
        path = runtime / "sites" / site / "pilot_report.json"
        if not path.is_file():
            sites[site] = {"result": "missing_pilot_report"}
            continue
        report = json.loads(path.read_text())
        root = runtime / "sites" / site / "pilot"
        require(report["backend_sha256"] == sha256_file(root / "active_backend.h5")
                and report["proposal_ledger_sha256"] == sha256_file(root / "proposal_ledger.jsonl")
                and report["identity_sha256"] == canonical_json_sha256(
                    json.loads((root / "identity.json").read_text())),
                f"{site} pilot artifact integrity mismatch")
        if report["result"] == "pass":
            marker = root / "COMPLETED.json"
            if not marker.is_file():
                report["result"] = "iter005_validation_failed"
                report["fatal_reasons"] = ["missing_completed_backend_marker"]
            else:
                completed = json.loads(marker.read_text())
                require(completed["backend_sha256"] == report["backend_sha256"]
                        and completed["proposal_ledger_sha256"] == report["proposal_ledger_sha256"]
                        and completed["identity_sha256"] == sha256_file(root / "identity.json"),
                        f"{site} completed backend marker identity mismatch")
        sites[site] = report
    storage = directory_size_bytes(runtime)
    require(storage <= config["storage_cap_bytes"], "Iter005 storage cap exceeded")
    if any(value["result"] != "pass" for value in sites.values()):
        decision = "iter005_validation_failed"
    elif any(value["mixing_limitations"] for value in sites.values()):
        decision = "bounded_sampler_pilot_validated_with_mixing_limitations"
    else:
        decision = "bounded_sampler_pilot_validated"
    write_json_exclusive(runtime / "results/diagnostics_validation.json", {
        "schema": "mcmc-iter005-diagnostics-v1", "result": "pass",
        "decision_candidate": decision, "sites": sites, "storage_bytes": storage,
        "convergence_claimed": False,
    })
    print(f"MCMC_ITER005_DIAGNOSTICS_PASS decision={decision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "density", "pilot", "diagnostics"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--site", choices=SITES)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.mode == "preflight":
        preflight(config)
    elif args.mode == "density":
        density(config)
    elif args.mode == "pilot":
        require(args.site in SITES, "pilot requires a locked site")
        pilot(config, args.site)
    else:
        diagnostics(config)


if __name__ == "__main__":
    main()
