#!/usr/bin/env python3
"""Evaluate Iter014 JERC 64x8000 productions for both high-L pool rules."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from emcee.autocorr import integrated_time
from emcee.backends import HDFBackend
from scipy.stats import norm, rankdata, wasserstein_distance

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import (  # noqa: E402
    build_coupling_target,
    selection_validation_sha256,
)

SEEDS = (9009, 9010, 9011)
NSTEPS = 8000
NWALKERS = 64
NPARAMETERS = 15
POOL_RULES = ("rank_dominated", "hybrid_high_l_maximin")
EXPECTED_TARGET = "26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill(prediction: np.ndarray, observation: np.ndarray, error: np.ndarray) -> dict:
    mask = (
        (observation > -9000)
        & (error > 0)
        & np.isfinite(prediction)
        & np.isfinite(observation)
        & np.isfinite(error)
    )
    observed = observation[mask]
    predicted = prediction[mask]
    residual = predicted - observed
    total = np.sum((observed - np.mean(observed)) ** 2)
    correlation = (
        np.corrcoef(predicted, observed)[0, 1]
        if len(observed) > 1 and np.std(predicted) and np.std(observed)
        else np.nan
    )
    alpha = np.std(predicted) / np.std(observed) if np.std(observed) else np.nan
    beta = np.mean(predicted) / np.mean(observed) if np.mean(observed) else np.nan
    return {
        "valid_observations": int(mask.sum()),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "bias": float(np.mean(residual)),
        "r2": float(1 - np.sum(residual**2) / total) if total else np.nan,
        "kge": (
            float(
                1
                - np.sqrt(
                    (correlation - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2
                )
            )
            if np.isfinite(correlation) and np.isfinite(alpha) and np.isfinite(beta)
            else np.nan
        ),
    }


def rank_normalized_split_rhat(chains: np.ndarray) -> np.ndarray:
    nseed, nstep, nwalker, ndim = chains.shape
    half = nstep // 2
    split = (
        chains[:, : 2 * half]
        .reshape(nseed, 2, half, nwalker, ndim)
        .transpose(0, 1, 3, 2, 4)
        .reshape(-1, half, ndim)
    )
    ranked = np.empty_like(split)
    for parameter in range(ndim):
        values = split[:, :, parameter].reshape(-1)
        ranks = rankdata(values, method="average")
        ranked[:, :, parameter] = norm.ppf((ranks - 0.5) / len(values)).reshape(
            split.shape[0], half
        )
    means = np.mean(ranked, axis=1)
    variances = np.var(ranked, axis=1, ddof=1)
    between = half * np.var(means, axis=0, ddof=1)
    within = np.mean(variances, axis=0)
    return np.sqrt(((half - 1) / half * within + between / half) / within)


def split_seed_walker_chains(chains: np.ndarray) -> np.ndarray:
    nseed, nstep, nwalker, ndim = chains.shape
    half = nstep // 2
    return (
        chains[:, : 2 * half]
        .reshape(nseed, 2, half, nwalker, ndim)
        .transpose(0, 1, 3, 2, 4)
        .reshape(-1, half, ndim)
    )


def multi_chain_ess(values: np.ndarray) -> float:
    chains = np.asarray(values, dtype=float)
    chain_count, draw_count = chains.shape
    if chain_count < 2 or draw_count < 4 or not np.all(np.isfinite(chains)):
        return float("nan")
    within = float(np.mean(np.var(chains, axis=1, ddof=1)))
    between = float(draw_count * np.var(np.mean(chains, axis=1), ddof=1))
    variance_plus = (draw_count - 1) / draw_count * within + between / draw_count
    if not np.isfinite(variance_plus) or variance_plus <= 0:
        return float("nan")
    centered = chains - np.mean(chains, axis=1, keepdims=True)
    fft_length = 1 << (2 * draw_count - 1).bit_length()
    transformed = np.fft.rfft(centered, n=fft_length, axis=1)
    autocovariance = np.fft.irfft(
        transformed * np.conjugate(transformed), n=fft_length, axis=1
    )[:, :draw_count]
    autocovariance /= draw_count
    rho = np.empty(draw_count, dtype=float)
    rho[0] = 1.0
    rho[1:] = 1.0 - (
        within - np.mean(autocovariance[:, 1:], axis=0)
    ) / variance_plus
    pair_sums = []
    for start in range(0, draw_count - 1, 2):
        pair_sum = float(rho[start] + rho[start + 1])
        if pair_sum < 0:
            break
        if pair_sums and pair_sum > pair_sums[-1]:
            pair_sum = pair_sums[-1]
        pair_sums.append(pair_sum)
    tau_hat = -1.0 + 2.0 * float(np.sum(pair_sums))
    if not np.isfinite(tau_hat) or tau_hat <= 0:
        return float("nan")
    return float(min(chain_count * draw_count, chain_count * draw_count / tau_hat))


def rank_bulk_tail_ess(chains: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    split = split_seed_walker_chains(chains)
    bulk = np.empty(split.shape[-1], dtype=float)
    tail = np.empty(split.shape[-1], dtype=float)
    for parameter in range(split.shape[-1]):
        values = split[:, :, parameter]
        flat = values.reshape(-1)
        ranks = rankdata(flat, method="average")
        normalized = norm.ppf((ranks - 0.5) / len(flat)).reshape(values.shape)
        bulk[parameter] = multi_chain_ess(normalized)
        lower, upper = np.quantile(flat, [0.05, 0.95])
        lower_ess = multi_chain_ess((values <= lower).astype(float))
        upper_ess = multi_chain_ess((values >= upper).astype(float))
        tail[parameter] = min(lower_ess, upper_ess)
    return bulk, tail


def evaluate_pool_rule(
    *,
    pool_rule: str,
    production_root: Path,
    pool_path: Path,
    output_root: Path,
    forcing_artifact: Path,
    spinup_artifact: Path,
    observation_path: Path,
    repository_commit: str,
    source_manifest: Path,
    dependency_manifest: Path,
    control: dict,
) -> dict:
    site = "JERC"
    resolution = "hourly"
    cases = ["JERC_ppe6_I20TRCNPRDCTCBC"]
    rule_output = output_root / pool_rule
    final_output = rule_output / "artifacts"
    staging_output = rule_output / ".artifacts.build"
    if final_output.exists():
        raise FileExistsError(f"refusing to overwrite completed evaluation: {final_output}")
    if staging_output.exists():
        shutil.rmtree(staging_output)
    rule_output.mkdir(parents=True, exist_ok=True)
    staging_output.mkdir()

    target = build_coupling_target(
        cases=cases,
        resolution=resolution,
        forcing_artifact=forcing_artifact,
        spinup_artifact=spinup_artifact,
        observation_paths={"JERC": observation_path},
        expected_physical_parameter_count=14,
    )
    if target["identity"]["sha256"] != EXPECTED_TARGET:
        raise ValueError("target sha256 mismatch against locked Iter014 contract")
    expected_pool_sha256 = sha256(pool_path)
    expected_source_sha256 = sha256(source_manifest)
    expected_dependency_sha256 = sha256(dependency_manifest)
    archives = []
    acceptance = []
    observed_moves = []

    for seed in SEEDS:
        leaf = production_root / pool_rule / f"seed_{seed}"
        raw_path = leaf / "raw_chain.npz"
        metadata_path = leaf / "raw_chain_metadata.json"
        hashes = json.loads((leaf / "raw_chain_hashes.json").read_text())
        if (
            hashes.get("raw_chain") != str(raw_path)
            or hashes.get("metadata") != str(metadata_path)
            or hashes.get("raw_chain_sha256") != sha256(raw_path)
            or hashes.get("metadata_sha256") != sha256(metadata_path)
        ):
            raise ValueError(f"{leaf}: raw-chain hash manifest mismatch")

        raw = np.load(raw_path, allow_pickle=False)
        chain = np.asarray(raw["chain"], dtype=float)
        sampler = np.asarray(raw["sampler_chain"], dtype=float)
        log_probability = np.asarray(raw["physical_log_prob"], dtype=float)
        if (
            chain.shape != (NSTEPS, NWALKERS, NPARAMETERS)
            or sampler.shape != chain.shape
            or log_probability.shape != (NSTEPS, NWALKERS)
            or not np.all(np.isfinite(chain))
            or not np.all(np.isfinite(sampler))
            or not np.all(np.isfinite(log_probability))
            or np.any(chain < target["pmin"])
            or np.any(chain > target["pmax"])
        ):
            raise ValueError(f"{leaf}: fixed-length raw package gate failed")

        production = json.loads((leaf / "production_result.json").read_text())
        selection = json.loads((leaf / "selection_ledger.json").read_text())
        raw_metadata = json.loads(metadata_path.read_text())
        backend_path = leaf / "backend.h5"
        checkpoint = json.loads((leaf / "checkpoint_manifest.json").read_text())
        required_steps = [8000]
        if (
            checkpoint.get("backend_iteration") != NSTEPS
            or checkpoint.get("required_steps") != required_steps
            or checkpoint.get("recorded_steps") != required_steps
            or checkpoint.get("backend") != str(backend_path)
            or checkpoint.get("backend_sha256") != sha256(backend_path)
        ):
            raise ValueError(f"{leaf}: checkpoint manifest mismatch")
        if (
            production.get("status") != "pass"
            or production.get("site") != site
            or production.get("resolution") != resolution
            or production.get("seed") != seed
            or production.get("target_sha256") != target["identity"]["sha256"]
            or production.get("pool_sha256") != expected_pool_sha256
            or production.get("repository_commit") != repository_commit
            or production.get("source_manifest_sha256") != expected_source_sha256
            or production.get("dependency_manifest_sha256")
            != expected_dependency_sha256
            or production.get(
                "sampler_coordinates",
                raw_metadata.get("transform", {}).get("coordinate_system"),
            )
            != "transformed"
            or float(production.get("de_move_scale", raw_metadata.get("de_move_scale", np.nan)))
            != 0.75
        ):
            raise ValueError(f"{leaf}: production provenance mismatch")
        if (
            selection.get("site") != site
            or selection.get("resolution") != resolution
            or selection.get("production_seed") != seed
            or selection.get("target_sha256") != target["identity"]["sha256"]
            or selection.get("pool_sha256") != expected_pool_sha256
            or selection.get("status") != "production_complete"
        ):
            raise ValueError(f"{leaf}: selection-ledger provenance mismatch")
        selection_spread = np.asarray(selection.get("normalized_spread"), dtype=float)
        if (
            selection.get("schema") != "coupling-selection-ledger-v1"
            or selection.get("normalized_rank") != NPARAMETERS
            or float(selection.get("normalized_condition_number", np.inf)) > 1.0e6
            or selection_spread.shape != (NPARAMETERS,)
            or np.any(selection_spread <= 0)
            or len(selection.get("stored_prior_component", [])) != NWALKERS
            or len(selection.get("stored_log_likelihood", [])) != NWALKERS
            or len(selection.get("reevaluated_prior_component", [])) != NWALKERS
            or len(selection.get("reevaluated_log_likelihood", [])) != NWALKERS
            or selection.get("validation_sha256") != selection_validation_sha256(selection)
        ):
            raise ValueError(f"{leaf}: selection validation incomplete")
        provenance = raw_metadata.get("provenance", {})
        if (
            raw_metadata.get("seed") != seed
            or raw_metadata.get("sites") != [site]
            or raw_metadata.get("nwalkers") != NWALKERS
            or raw_metadata.get("nsteps") != NSTEPS
            or provenance.get("REPOSITORY_COMMIT") != repository_commit
            or provenance.get("SOURCE_MANIFEST_sha256") != expected_source_sha256
            or provenance.get("DEPENDENCY_MANIFEST_sha256")
            != expected_dependency_sha256
            or raw_metadata.get("transform", {}).get("coordinate_system") != "transformed"
            or float(raw_metadata.get("de_move_scale", np.nan)) != 0.75
        ):
            raise ValueError(f"{leaf}: raw-chain provenance mismatch")
        observed_moves.append(raw_metadata.get("move_configuration"))
        backend = HDFBackend(str(backend_path), read_only=True)
        walker_acceptance = np.asarray(backend.accepted, dtype=float) / float(
            backend.iteration
        )
        if walker_acceptance.shape != (NWALKERS,) or not np.all(
            np.isfinite(walker_acceptance)
        ):
            raise ValueError(f"{leaf}: walker acceptance unavailable")
        acceptance.append(walker_acceptance)
        archives.append((chain, sampler, log_probability))

    move_matches_contract = all(move == "de_mixture" for move in observed_moves)
    if not move_matches_contract:
        raise ValueError(
            f"{pool_rule}: production move mismatch: observed={observed_moves}"
        )

    chains = np.stack([archive[0] for archive in archives], axis=0)
    acceptance_array = np.stack(acceptance, axis=0)
    tau_rows = []
    tau_stability = []
    tau_errors = []
    for chain, _, _ in archives:
        try:
            full = np.asarray(integrated_time(chain, tol=0, quiet=True), dtype=float)
            half = np.asarray(
                integrated_time(chain[: NSTEPS // 2], tol=0, quiet=True), dtype=float
            )
            if (
                full.shape != (NPARAMETERS,)
                or half.shape != (NPARAMETERS,)
                or not np.all(np.isfinite(full))
                or not np.all(np.isfinite(half))
                or np.any(full <= 0)
                or np.any(half <= 0)
            ):
                raise ValueError("non-finite or non-positive tau")
            tau_rows.append(full)
            tau_stability.append(float(np.max(np.abs(full - half) / half)))
            tau_errors.append(None)
        except Exception as exc:  # noqa: BLE001
            tau_rows.append(np.full(NPARAMETERS, np.nan))
            tau_stability.append(np.nan)
            tau_errors.append(f"{type(exc).__name__}: {exc}")
    tau = np.asarray(tau_rows)
    tau_available = bool(np.all(np.isfinite(tau)))
    tau_max = float(np.max(tau)) if tau_available else None
    diagnostic_discard = (
        int(max(np.ceil(0.20 * NSTEPS), np.ceil(5 * tau_max)))
        if tau_max is not None
        else None
    )
    diagnostic_window_valid = bool(
        diagnostic_discard is not None and diagnostic_discard < NSTEPS
    )
    descriptive_discard = (
        diagnostic_discard if diagnostic_window_valid else int(np.ceil(0.20 * NSTEPS))
    )
    post = chains[:, descriptive_discard:]
    flat = post.reshape(-1, NPARAMETERS)
    flat_log_probability = np.concatenate(
        [archive[2][descriptive_discard:].reshape(-1) for archive in archives]
    )

    if diagnostic_window_valid:
        rhat_values = rank_normalized_split_rhat(post)
        bulk_ess, tail_ess = rank_bulk_tail_ess(post)
        tail_tau = np.full((len(SEEDS), NPARAMETERS), np.nan)
        post_burn_steps_per_tau = post.shape[1] / tau
        diagnostics_finite = bool(
            np.all(np.isfinite(rhat_values))
            and np.all(np.isfinite(bulk_ess))
            and np.all(np.isfinite(tail_ess))
            and np.all(np.isfinite(post_burn_steps_per_tau))
        )
    else:
        rhat_values = np.full(NPARAMETERS, np.nan)
        bulk_ess = np.full(NPARAMETERS, np.nan)
        tail_tau = np.full((len(SEEDS), NPARAMETERS), np.nan)
        tail_ess = np.full(NPARAMETERS, np.nan)
        post_burn_steps_per_tau = np.full_like(tau, np.nan)
        diagnostics_finite = False

    widths = target["pmax"] - target["pmin"]
    wasserstein_max = max(
        wasserstein_distance(
            post[first, :, :, parameter].ravel(),
            post[second, :, :, parameter].ravel(),
        )
        / widths[parameter]
        for first in range(3)
        for second in range(first + 1, 3)
        for parameter in range(NPARAMETERS)
    )
    saturation = float(
        np.max(
            np.mean(
                np.abs(np.concatenate([archive[1] for archive in archives], axis=0))
                >= 10,
                axis=(0, 1),
            )
        )
    )
    edge = np.mean(
        (post <= target["pmin"] + 0.01 * widths)
        | (post >= target["pmax"] - 0.01 * widths),
        axis=(0, 1, 2),
    )
    median_state = np.median(flat, axis=0)
    map_state = flat[int(np.nanargmax(flat_log_probability))]
    rng = np.random.default_rng(14014)
    sampled_states = flat[rng.choice(len(flat), size=min(64, len(flat)), replace=False)]
    observation = target["obs"][site]["SR"]
    error = target["obs_err"][site]["SR"]
    median_prediction = target["predict"](site, median_state)
    map_prediction = target["predict"](site, map_state)
    predictions = np.asarray([target["predict"](site, state) for state in sampled_states])
    predictive = {
        "count": int(len(predictions)),
        "lower_025": np.percentile(predictions, 2.5, axis=0).tolist(),
        "median": np.percentile(predictions, 50, axis=0).tolist(),
        "upper_975": np.percentile(predictions, 97.5, axis=0).tolist(),
    }
    metrics = {
        "posterior_median": skill(median_prediction, observation, error),
        "map_descriptive": skill(map_prediction, observation, error),
        "posterior_predictive_sample": predictive,
        "fitted_sigma_SR_median": float(median_state[-1]),
        "fitted_sigma_SR_map": float(map_state[-1]),
    }
    mean_acceptance_by_seed = np.mean(acceptance_array, axis=1)
    mean_acceptance = float(np.mean(mean_acceptance_by_seed))
    control_mean_acceptance = float(np.mean(control["mean_acceptance_by_seed"]))
    control_wasserstein = float(control["max_cross_seed_normalized_wasserstein"])
    stable_tau = bool(
        tau_available
        and np.all(np.isfinite(tau_stability))
        and np.all(np.asarray(tau_stability) <= 0.20)
    )
    integrity_pass = bool(
        move_matches_contract
        and np.all(np.isfinite(acceptance_array))
        and np.isfinite(wasserstein_max)
    )
    qualified = bool(
        integrity_pass
        and diagnostic_window_valid
        and diagnostics_finite
        and stable_tau
        and np.all(post_burn_steps_per_tau >= 50)
        and np.all(rhat_values <= 1.05)
        and np.all(bulk_ess >= 400)
        and np.all(tail_ess >= 400)
        and wasserstein_max <= 0.05
    )
    label = "diagnostically_qualified" if qualified else "fixed_length_inconclusive"
    result = {
        "schema": "spinup-forcing-coupling-iter014-evaluation-v1",
        "site": site,
        "resolution": resolution,
        "pool_rule": pool_rule,
        "seeds": list(SEEDS),
        "nsteps": NSTEPS,
        "chain_shape": list(chains.shape),
        "required_move_configuration": "de_mixture",
        "observed_move_configurations": observed_moves,
        "move_matches_contract": move_matches_contract,
        "integrity_pass": integrity_pass,
        "mean_acceptance_by_seed": mean_acceptance_by_seed.tolist(),
        "mean_acceptance": mean_acceptance,
        "walker_acceptance_by_seed": acceptance_array.tolist(),
        "tau_available": tau_available,
        "tau_errors": tau_errors,
        "tau": tau.tolist(),
        "tail_tau": tail_tau.tolist(),
        "tau_stability_by_seed": tau_stability,
        "diagnostic_discard": diagnostic_discard,
        "diagnostic_window_valid": diagnostic_window_valid,
        "descriptive_discard": descriptive_discard,
        "post_burn_steps_per_tau": post_burn_steps_per_tau.tolist(),
        "rank_normalized_split_rhat": rhat_values.tolist(),
        "rank_normalized_bulk_ess": bulk_ess.tolist(),
        "quantile_tail_ess": tail_ess.tolist(),
        "max_cross_seed_normalized_wasserstein": float(wasserstein_max),
        "transformed_saturation": saturation,
        "physical_prior_edge_occupancy": edge.tolist(),
        "metrics": metrics,
        "label": label,
        "target_sha256": target["identity"]["sha256"],
        "pool_sha256": expected_pool_sha256,
        "control_comparison": {
            "control_path": control.get("_path"),
            "control_mean_acceptance": control_mean_acceptance,
            "control_max_cross_seed_normalized_wasserstein": control_wasserstein,
            "acceptance_delta": mean_acceptance - control_mean_acceptance,
            "wasserstein_delta": float(wasserstein_max) - control_wasserstein,
            "acceptance_improved": mean_acceptance > control_mean_acceptance,
            "wasserstein_improved": float(wasserstein_max) < control_wasserstein,
            "acceptance_clearly_above": mean_acceptance >= 0.25,
            "wasserstein_meets_gate": float(wasserstein_max) <= 0.05,
        },
        "production_repository_commit": repository_commit,
        "production_source_manifest_sha256": expected_source_sha256,
        "production_dependency_manifest_sha256": expected_dependency_sha256,
        "status": "pass",
    }
    np.savez_compressed(
        staging_output / "physical_traces.npz",
        traces=post,
        log_posterior=flat_log_probability,
    )
    corner_rng = np.random.default_rng(14014)
    corner = flat[corner_rng.choice(len(flat), size=min(2000, len(flat)), replace=False)]
    figure, axes = plt.subplots(NPARAMETERS, NPARAMETERS, figsize=(24, 24))
    for row in range(NPARAMETERS):
        for column in range(NPARAMETERS):
            axis = axes[row, column]
            if row == column:
                axis.hist(corner[:, column], bins=30, color="0.25", density=True)
            elif row > column:
                axis.scatter(
                    corner[:, column],
                    corner[:, row],
                    s=1,
                    alpha=0.15,
                    linewidths=0,
                    color="tab:blue",
                )
            else:
                axis.axis("off")
            if row == NPARAMETERS - 1:
                axis.set_xlabel(
                    target["parameter_names"][column],
                    rotation=45,
                    ha="right",
                    fontsize=6,
                )
            if column == 0 and row > 0:
                axis.set_ylabel(target["parameter_names"][row], fontsize=6)
            axis.tick_params(labelsize=5)
    figure.tight_layout()
    figure.savefig(staging_output / "physical_corner.png", dpi=150)
    plt.close(figure)
    with (staging_output / "hourly_predictions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "index",
                "observation",
                "posterior_median",
                "map",
                "pp_lower",
                "pp_median",
                "pp_upper",
            ]
        )
        for index in range(len(observation)):
            writer.writerow(
                [
                    index,
                    observation[index],
                    median_prediction[index],
                    map_prediction[index],
                    predictive["lower_025"][index],
                    predictive["median"][index],
                    predictive["upper_975"][index],
                ]
            )
    (staging_output / "evaluation_result.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    staging_output.replace(final_output)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--observation", required=True, type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--pool-rebuild-root", required=True, type=Path)
    parser.add_argument("--evaluation-root", required=True, type=Path)
    parser.add_argument("--control-evaluation", required=True, type=Path)
    parser.add_argument("--preflight-result", required=True, type=Path)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--dependency-manifest", required=True, type=Path)
    args = parser.parse_args()

    control = json.loads(args.control_evaluation.read_text(encoding="utf-8"))
    if control.get("site") != "JERC":
        raise ValueError("control evaluation is not JERC")
    control["_path"] = str(args.control_evaluation)
    preflight = json.loads(args.preflight_result.read_text(encoding="utf-8"))
    if preflight.get("status") != "pass":
        raise ValueError("preflight result status is not pass")
    eligible = [
        str(rule)
        for rule in preflight.get("eligible_pool_rules", [])
        if str(rule) in POOL_RULES
    ]
    if not eligible:
        raise ValueError("preflight lists no eligible pool rules")
    dry_checks = preflight.get("ledger_dry_checks", {})

    summary = {
        "schema": "spinup-forcing-coupling-iter014-evaluation-summary-v1",
        "site": "JERC",
        "pool_rules": [],
        "geometry_gate_failed": [],
        "control": {
            "path": str(args.control_evaluation),
            "mean_acceptance": float(np.mean(control["mean_acceptance_by_seed"])),
            "max_cross_seed_normalized_wasserstein": float(
                control["max_cross_seed_normalized_wasserstein"]
            ),
        },
        "status": "pass",
    }
    for pool_rule in POOL_RULES:
        check = dry_checks.get(pool_rule, {})
        if check.get("status") == "geometry_gate_failed":
            stub = {
                "schema": "spinup-forcing-coupling-iter014-evaluation-v1",
                "site": "JERC",
                "pool_rule": pool_rule,
                "status": "geometry_gate_failed",
                "label": "geometry_gate_failed",
                "integrity_pass": False,
                "nsteps": 8000,
                "seeds": list(SEEDS),
                "mean_acceptance": float("nan"),
                "mean_acceptance_by_seed": [float("nan")] * len(SEEDS),
                "max_cross_seed_normalized_wasserstein": float("nan"),
                "control_comparison": {
                    "acceptance_improved": False,
                    "wasserstein_improved": False,
                },
                "preflight_error": check.get("error"),
                "target_sha256": EXPECTED_TARGET,
                "pool_sha256": None,
            }
            rule_dir = args.evaluation_root / pool_rule / "artifacts"
            if rule_dir.exists():
                raise FileExistsError(f"refusing to overwrite {rule_dir}")
            rule_dir.mkdir(parents=True, exist_ok=True)
            (rule_dir / "evaluation_result.json").write_text(
                json.dumps(stub, indent=2) + "\n", encoding="utf-8"
            )
            summary["geometry_gate_failed"].append(pool_rule)
            summary["pool_rules"].append(
                {
                    "pool_rule": pool_rule,
                    "label": "geometry_gate_failed",
                    "integrity_pass": False,
                    "mean_acceptance": None,
                    "max_cross_seed_normalized_wasserstein": None,
                    "control_comparison": stub["control_comparison"],
                }
            )
            print(f"EVALUATION_SKIP pool_rule={pool_rule} label=geometry_gate_failed")
            continue
        if pool_rule not in eligible:
            raise ValueError(
                f"pool rule {pool_rule} is neither eligible nor geometry-failed"
            )
        result = evaluate_pool_rule(
            pool_rule=pool_rule,
            production_root=args.production_root,
            pool_path=args.pool_rebuild_root
            / pool_rule
            / "artifacts"
            / "candidate_pool.npz",
            output_root=args.evaluation_root,
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
            observation_path=args.observation,
            repository_commit=args.repository_commit,
            source_manifest=args.source_manifest,
            dependency_manifest=args.dependency_manifest,
            control=control,
        )
        summary["pool_rules"].append(
            {
                "pool_rule": pool_rule,
                "label": result["label"],
                "integrity_pass": result["integrity_pass"],
                "mean_acceptance": result["mean_acceptance"],
                "max_cross_seed_normalized_wasserstein": result[
                    "max_cross_seed_normalized_wasserstein"
                ],
                "control_comparison": result["control_comparison"],
            }
        )
        print(
            f"EVALUATION_PASS pool_rule={pool_rule} label={result['label']} "
            f"mean_acc={result['mean_acceptance']:.4f} "
            f"W={result['max_cross_seed_normalized_wasserstein']:.4f}"
        )

    summary_path = args.evaluation_root / "evaluation_summary.json"
    if summary_path.exists():
        raise FileExistsError(summary_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        "EVALUATION_PASS eligible="
        + ",".join(eligible)
        + " geometry_failed="
        + ",".join(summary["geometry_gate_failed"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
