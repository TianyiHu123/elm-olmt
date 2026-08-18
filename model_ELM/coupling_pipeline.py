"""Reusable coupled-surrogate target and candidate-pool pipeline.

The public functions in this module are iteration-neutral.  Workflows provide their
case membership, artifacts, resolution, search budget, and provenance schema rather
than embedding those controls in the engine.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize
from scipy.stats import qmc

from .MCMC_forcing import MCMC_forcing, _init_mcmc_worker, log_posterior_forcing, run_forcing_surrogate_site
from .coupled_surrogate import prepare_coupled_site_arrays
from .load_obs_nc import collocate_obs_to_forcing_time, load_observations_with_time_from_nc
from .surrogate_NN_Forcing import build_forcing_inference_inputs, load_surrogate_forcing_artifacts

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OBS_ROOT = Path("/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json_atomic(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8"
    )
    temporary.replace(destination)


def _timestamp_components(stamp: Any) -> tuple[int, int, int, int]:
    """Return year, month, day, hour for cftime and NumPy datetime values."""
    if isinstance(stamp, np.datetime64):
        text = np.datetime_as_string(stamp, unit="h")
        date_text, time_text = text.split("T", 1)
        year, month, day = (int(part) for part in date_text.split("-"))
        return year, month, day, int(time_text[:2])
    if all(hasattr(stamp, attr) for attr in ("year", "month", "day", "hour")):
        return int(stamp.year), int(stamp.month), int(stamp.day), int(stamp.hour)
    raise ValueError("daily likelihood requires datetime-like forcing timestamps")


def build_daily_index_map(
    times: np.ndarray,
    observations: np.ndarray,
    observation_errors: np.ndarray,
    *,
    schema: str = "coupled-daily-map-v1",
) -> dict[str, Any]:
    by_day: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    for i, stamp in enumerate(np.asarray(times).reshape(-1)):
        year, month, day, hour = _timestamp_components(stamp)
        if not np.isfinite(observations[i]) or observations[i] <= -9000:
            continue
        if not np.isfinite(observation_errors[i]) or observation_errors[i] <= 0:
            continue
        key = (year, month, day)
        by_day.setdefault(key, []).append((hour, i))
    groups: list[list[int]] = []
    included: list[str] = []
    excluded: list[str] = []
    for key in sorted(by_day):
        rows = by_day[key]
        label = f"{key[0]:04d}-{key[1]:02d}-{key[2]:02d}"
        if len(rows) == 24 and sorted(hour for hour, _ in rows) == list(range(24)):
            groups.append([index for _, index in sorted(rows)])
            included.append(label)
        else:
            excluded.append(label)
    if not groups:
        raise ValueError("daily target has no complete valid 24-hour days")
    result = {
        "schema": schema,
        "aggregation": "arithmetic_mean_of_same_24_hourly_indices",
        "included_dates": included,
        "excluded_dates": excluded,
        "hourly_count": int(len(times)),
        "daily_count": int(len(groups)),
        "groups": groups,
    }
    result["sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def build_coupling_target(
    *,
    repo_root: str | Path = REPO_ROOT,
    cases: Sequence[str],
    resolution: str,
    forcing_artifact: str | Path,
    spinup_artifact: str | Path,
    observation_paths: Mapping[str, str | Path] | None = None,
    observation_root: str | Path | None = OBS_ROOT,
    fit_error: bool = True,
    expected_physical_parameter_count: int | None = None,
    target_schema: str = "coupled-target-v1",
    daily_map_schema: str = "coupled-daily-map-v1",
) -> dict[str, Any]:
    """Build one explicit-membership, single-resolution coupled target."""
    repo = Path(repo_root).resolve()
    supplied_case_names = tuple(str(case).strip() for case in cases if str(case).strip())
    case_names = tuple(sorted(supplied_case_names))
    if not case_names or len(set(case_names)) != len(case_names):
        raise ValueError("cases must contain one or more unique explicit case names")
    if resolution not in {"hourly", "daily"}:
        raise ValueError("resolution must be hourly or daily")
    forcing = Path(forcing_artifact).resolve()
    spinup = Path(spinup_artifact).resolve()
    if not forcing.is_file() or not spinup.is_file():
        raise FileNotFoundError(f"locked artifacts missing: {forcing}, {spinup}")
    obs_map = {
        str(key).upper(): Path(value).resolve()
        for key, value in (observation_paths or {}).items()
    }
    obs_root = Path(OBS_ROOT if observation_root is None else observation_root).resolve()

    loaded: list[tuple[str, Any]] = []
    for name in case_names:
        path = repo / "pklfiles" / f"{name}.pkl"
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("rb") as handle:
            loaded.append((name, pickle.load(handle)))
    sites: list[str] = []
    for name, case in loaded:
        site = str(getattr(case, "site", "")).strip().upper()
        if not site or site in sites:
            raise ValueError(f"case membership produced missing or duplicate site: {name}")
        sites.append(site)
    allowed_observation_keys = set(sites) | {name.upper() for name in case_names}
    extra_observation_keys = set(obs_map) - allowed_observation_keys
    if extra_observation_keys:
        raise ValueError(
            "observation_paths contains configuration outside selected cases/sites: "
            f"{sorted(extra_observation_keys)}"
        )

    layout = dict(load_surrogate_forcing_artifacts(loaded[0][1], str(forcing))["training_layout"])
    context: dict[str, dict[str, Any]] = {}
    observations: dict[str, dict[str, np.ndarray]] = {}
    errors: dict[str, dict[str, np.ndarray]] = {}
    daily_maps: dict[str, dict[str, Any]] = {}
    identity: dict[str, Any] = {
        "schema": target_schema,
        "cases": list(case_names),
        "sites": sites,
        "resolution": resolution,
        "forcing_artifact": str(forcing),
        "forcing_artifact_sha256": sha256_file(forcing),
        "spinup_artifact": str(spinup),
        "spinup_artifact_sha256": sha256_file(spinup),
        "fit_error": bool(fit_error),
    }

    for case_name, case in loaded:
        site = str(case.site).strip().upper()
        load_surrogate_forcing_artifacts(case, str(forcing))
        inputs = build_forcing_inference_inputs(case, training_layout=layout)
        obs_path = (
            obs_map.get(site)
            or obs_map.get(case_name.upper())
            or (obs_root / site / f"{site}_cdo_merge.nc")
        )
        if not obs_path.is_file():
            raise FileNotFoundError(obs_path)
        payload = load_observations_with_time_from_nc(
            obs_path=str(obs_path), myvars=["SR"], obs_err_vars={"SR": "SR_err"}
        )
        aligned, aligned_err, overlap = collocate_obs_to_forcing_time(
            forcing_time=inputs["forcing_time"], obs_time=payload["time"],
            obs=payload["obs"], obs_err=payload["obs_err"], myvars=["SR"]
        )
        prepared = prepare_coupled_site_arrays(case, spinup_artifact=spinup, forcing_artifact=forcing)
        overlap_indices = np.asarray(overlap["forcing_overlap_indices"], dtype=int)
        if resolution == "daily":
            daily_maps[site] = build_daily_index_map(
                np.asarray(inputs["forcing_time"])[overlap_indices], aligned["SR"], aligned_err["SR"], schema=daily_map_schema
            )
        observations[site] = {"SR": np.asarray(aligned["SR"], dtype=float)}
        errors[site] = {"SR": np.asarray(aligned_err["SR"], dtype=float)}
        context[site] = {
            "spinup_mode": "coupled",
            "spinup_artifact": str(prepared["spinup_artifact_path"] or spinup),
            "forcing_artifact": str(prepared["forcing_artifact_path"] or forcing),
            "surface": prepared["surface"], "climatology": prepared["climatology"],
            "forcing_engineered_full": prepared["forcing_engineered_full"],
            "overlap_indices": overlap_indices,
            "n_params": int(prepared["n_params"]), "n_forcing_cols": int(prepared["n_forcing_cols"]),
            "n_spinup": int(prepared["n_spinup"]), "case": case,
            "obs": observations[site], "obs_err": errors[site],
            "overlap_diagnostics": dict(overlap), "daily_index_map": daily_maps.get(site),
        }
        identity.setdefault("sites_detail", {})[site] = {
            "case": case_name, "case_pickle_sha256": sha256_file(repo / "pklfiles" / f"{case_name}.pkl"),
            "observation_path": str(obs_path), "observation_sha256": sha256_file(obs_path),
            "overlap_rows": int(overlap["n_overlap"]),
            "daily_map_sha256": daily_maps.get(site, {}).get("sha256"),
        }

    primary = loaded[0][1]
    for case_name, candidate in loaded[1:]:
        if (list(candidate.ensemble_parms) != list(primary.ensemble_parms)
                or not np.array_equal(np.asarray(candidate.ensemble_pmin), np.asarray(primary.ensemble_pmin))
                or not np.array_equal(np.asarray(candidate.ensemble_pmax), np.asarray(primary.ensemble_pmax))):
            raise ValueError(f"case parameter schema mismatch for {case_name}")
    pmin = np.asarray(primary.ensemble_pmin, dtype=float).copy()
    pmax = np.asarray(primary.ensemble_pmax, dtype=float).copy()
    names = list(primary.ensemble_parms)
    if expected_physical_parameter_count is not None and len(names) != expected_physical_parameter_count:
        raise ValueError(f"expected {expected_physical_parameter_count} physical parameters, got {len(names)}")
    if pmin.size != len(names) or pmax.size != len(names):
        raise ValueError("parameter names and bounds have different sizes")
    if fit_error:
        valid = [values["SR"][(values["SR"] > -9000) & np.isfinite(values["SR"])
                 & (errors[site]["SR"] > 0) & np.isfinite(errors[site]["SR"])] for site, values in observations.items()]
        max_observation = max((float(np.max(np.abs(values))) for values in valid if values.size), default=0.01)
        pmin = np.append(pmin, 0.0)
        pmax = np.append(pmax, 0.25 * max(max_observation, 0.01))
        names.append("sigma_SR")
    if np.any(~np.isfinite(pmin)) or np.any(~np.isfinite(pmax)) or np.any(pmax <= pmin):
        raise ValueError("target bounds are not finite and strictly ordered")
    identity["parameter_names"] = names
    identity["pmin"] = pmin.tolist()
    identity["pmax"] = pmax.tolist()
    identity["training_layout"] = layout
    identity["sha256"] = hashlib.sha256(json.dumps(identity, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()

    primary.all_sites = sites
    worker_state = {
        "sites": sites, "myvars": ["SR"], "pmin": pmin, "pmax": pmax,
        "obs": observations, "obs_err": errors, "nparms_ensemble": len(names),
        "nerr_parms": 1 if fit_error else 0, "site_data_by_site": context,
        "likelihood_resolution": resolution, "daily_index_maps": daily_maps,
    }

    def evaluate_log_posterior(state: np.ndarray) -> float:
        # MCMC_forcing keeps worker state at module scope. Reinstall this target's
        # immutable state before each parent-process evaluation so independently
        # built targets remain safe to interleave in one process.
        _init_mcmc_worker(worker_state)
        return float(log_posterior_forcing(np.asarray(state, dtype=float)))

    def evaluate_components(state: np.ndarray) -> dict[str, float]:
        values = np.asarray(state, dtype=float)
        inside = bool(np.all((values >= pmin) & (values <= pmax)))
        if not inside:
            return {
                "prior_component": float("-inf"),
                "log_likelihood": float("-inf"),
                "physical_log_posterior": float("-inf"),
            }
        posterior = evaluate_log_posterior(values)
        # The established forcing target contributes a constant 1.0 for its
        # bounded uniform prior before adding site likelihoods.
        prior_component = 1.0
        return {
            "prior_component": prior_component,
            "log_likelihood": float(posterior - prior_component),
            "physical_log_posterior": posterior,
        }

    return {
        "repo_root": repo,
        "case": primary, "cases": loaded, "sites": sites, "context": context,
        "obs": observations, "obs_err": errors, "daily_maps": daily_maps,
        "parameter_names": names, "pmin": pmin, "pmax": pmax, "identity": identity,
        "worker_state": worker_state,
        "log_posterior": evaluate_log_posterior,
        "log_components": evaluate_components,
        "predict": lambda site, state: run_forcing_surrogate_site(
            context[site], np.asarray(state, dtype=float)[:-1] if fit_error else np.asarray(state, dtype=float), ["SR"]
        )["SR"],
    }


def select_maximin(points: np.ndarray, count: int, seed: int) -> np.ndarray:
    if len(points) < count:
        raise ValueError(f"maximin requires {count} points, found {len(points)}")
    rng = np.random.default_rng(seed)
    selected = [int(rng.integers(len(points)))]
    distance = np.sum((points - points[selected[0]]) ** 2, axis=1)
    while len(selected) < count:
        best = np.flatnonzero(distance == np.max(distance))
        picked = int(best[rng.integers(len(best))])
        selected.append(picked)
        distance = np.minimum(distance, np.sum((points - points[picked]) ** 2, axis=1))
    return np.asarray(selected, dtype=int)


POOL_RULES = ("diversity_maximin", "rank_dominated", "hybrid_high_l_maximin")


def _diversity_maximin_indices(
    normalized: np.ndarray,
    logp: np.ndarray,
    *,
    pool_size: int,
    strata_bins: int,
    robust_quantile: float = 0.75,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Select pool indices by robust strata reps plus maximin fill."""
    strata = np.minimum((normalized * strata_bins).astype(int), strata_bins - 1)
    top_cut = float(np.quantile(logp, robust_quantile))
    robust_mask = logp >= top_cut
    robust_ids: list[list[int]] = []
    for axis in range(strata.shape[1]):
        for bin_id in range(strata_bins):
            if np.any(robust_mask & (strata[:, axis] == bin_id)):
                robust_ids.append([int(axis), int(bin_id)])
    if not robust_ids:
        raise RuntimeError("pool gate failed: no robust retained marginal stratum")
    ordered = np.argsort(logp)[::-1]
    required: list[int] = []
    for axis, bin_id in robust_ids:
        candidates = [int(i) for i in ordered if strata[i, axis] == bin_id and robust_mask[i]]
        if candidates:
            required.append(candidates[0])
    required = list(dict.fromkeys(required))
    if len(required) > pool_size:
        raise RuntimeError(
            f"pool gate failed: {len(required)} robust strata exceed pool size {pool_size}"
        )
    remaining = [i for i in ordered if i not in set(required)]
    selected = list(required)
    while len(selected) < pool_size:
        distances = np.min(
            np.sum(
                (normalized[remaining, None, :] - normalized[np.asarray(selected), :][None, :, :]) ** 2,
                axis=2,
            ),
            axis=1,
        )
        pick = int(remaining[int(np.argmax(distances))])
        selected.append(pick)
        remaining.remove(pick)
    return np.asarray(selected, dtype=int), {
        "robust_logp_cutoff": top_cut,
        "robust_quantile": float(robust_quantile),
        "strata_scheme": "marginal_parameter_bins_v1",
        "strata_bins": int(strata_bins),
        "robust_strata": robust_ids,
    }


def choose_candidate_pool(
    states: np.ndarray,
    logp: np.ndarray,
    pmin: np.ndarray,
    pmax: np.ndarray,
    *,
    pool_size: int = 640,
    strata_bins: int = 4,
    seed: int = 0,
    pool_rule: str = "diversity_maximin",
    high_l_quantile: float = 0.90,
):
    """Compress a search ledger into a candidate pool under a named pool rule.

    ``seed`` is retained for API compatibility; current rules are deterministic given
    the ledger contents and rule parameters.
    """
    del seed  # deterministic under the locked Iter014 pool rules
    if pool_rule not in POOL_RULES:
        raise ValueError(f"unsupported pool_rule={pool_rule!r}; expected one of {POOL_RULES}")
    if not (0.0 <= float(high_l_quantile) < 1.0):
        raise ValueError(f"high_l_quantile must be in [0, 1), got {high_l_quantile}")
    finite = np.isfinite(logp) & np.all(np.isfinite(states), axis=1)
    finite &= np.all((states > pmin) & (states < pmax), axis=1)
    unique_states, unique_indices = np.unique(states[finite], axis=0, return_index=True)
    finite_indices = np.flatnonzero(finite)[unique_indices]
    unique_logp = logp[finite_indices]
    if len(unique_states) < pool_size:
        raise RuntimeError(f"pool gate failed: only {len(unique_states)} finite exact-unique states")
    normalized = (unique_states - pmin) / (pmax - pmin)
    rule_diagnostics: dict[str, Any] = {
        "pool_rule": pool_rule,
        "high_l_quantile_requested": float(high_l_quantile),
    }
    if pool_rule == "rank_dominated":
        selected = np.argsort(unique_logp)[::-1][:pool_size]
        rule_diagnostics.update(
            {
                "robust_logp_cutoff": float(unique_logp[selected[-1]]),
                "strata_scheme": "marginal_parameter_bins_v1",
                "strata_bins": int(strata_bins),
                "robust_strata": [],
            }
        )
    elif pool_rule == "hybrid_high_l_maximin":
        quantile = float(high_l_quantile)
        universe = np.flatnonzero(unique_logp >= np.quantile(unique_logp, quantile))
        while len(universe) < pool_size and quantile > 0.0:
            quantile = max(0.0, quantile - 0.05)
            universe = np.flatnonzero(unique_logp >= np.quantile(unique_logp, quantile))
        if len(universe) < pool_size:
            raise RuntimeError(
                f"pool gate failed: high-L universe has only {len(universe)} states for pool_size {pool_size}"
            )
        local_selected, diversity_diag = _diversity_maximin_indices(
            normalized[universe],
            unique_logp[universe],
            pool_size=pool_size,
            strata_bins=strata_bins,
        )
        selected = universe[local_selected]
        rule_diagnostics.update(diversity_diag)
        rule_diagnostics["high_l_quantile_applied"] = float(quantile)
        rule_diagnostics["high_l_universe_count"] = int(len(universe))
    else:
        selected, diversity_diag = _diversity_maximin_indices(
            normalized,
            unique_logp,
            pool_size=pool_size,
            strata_bins=strata_bins,
        )
        rule_diagnostics.update(diversity_diag)
        rule_diagnostics["high_l_quantile_applied"] = None
    strata_all = np.minimum((normalized * strata_bins).astype(int), strata_bins - 1)
    selected = np.asarray(selected, dtype=int)
    selected_norm = normalized[selected]
    centered = selected_norm - np.mean(selected_norm, axis=0)
    rank = int(np.linalg.matrix_rank(centered))
    condition = float(np.linalg.cond(centered))
    if rank != pmin.size or not np.isfinite(condition) or condition > 1.0e6:
        raise RuntimeError(f"pool gate failed: rank={rank} condition={condition}")
    spread = np.ptp(selected_norm, axis=0)
    if np.any(spread <= 0):
        raise RuntimeError("pool gate failed: zero normalized spread")
    diagnostics = {
        "finite_exact_unique": int(len(unique_states)),
        "selected_count": int(len(selected)),
        "normalized_rank": rank,
        "normalized_condition_number": condition,
        "normalized_spread": spread.tolist(),
        **rule_diagnostics,
    }
    return unique_states[selected], unique_logp[selected], strata_all[selected], diagnostics


def select_production_walkers(
    pool: np.ndarray,
    logp: np.ndarray,
    strata: np.ndarray,
    pmin: np.ndarray,
    pmax: np.ndarray,
    seed: int,
    log_posterior,
    *,
    walker_count: int = 64,
) -> tuple[np.ndarray, np.ndarray]:
    """Select, validate, and re-evaluate one production walker's initial state."""
    normalized = (pool - pmin) / (pmax - pmin)
    rng = np.random.default_rng(seed)
    representatives: list[int] = []
    for axis in range(strata.shape[1]):
        for bin_id in sorted(set(int(x) for x in strata[:, axis])):
            candidates = np.flatnonzero(strata[:, axis] == bin_id)
            representatives.append(int(candidates[np.argmax(logp[candidates])]))
    representatives = list(dict.fromkeys(representatives))
    if len(representatives) > walker_count:
        selected_reps = [int(rng.integers(len(representatives)))]
        distance = np.sum((normalized[representatives] - normalized[representatives[selected_reps[0]]]) ** 2, axis=1)
        while len(selected_reps) < walker_count:
            available = np.asarray([i for i in range(len(representatives)) if i not in selected_reps], dtype=int)
            best = available[np.flatnonzero(distance[available] == np.max(distance[available]))]
            picked = int(best[rng.integers(len(best))])
            selected_reps.append(picked)
            distance = np.minimum(distance, np.sum((normalized[representatives] - normalized[representatives[picked]]) ** 2, axis=1))
        selected = [int(representatives[i]) for i in selected_reps]
    else:
        selected = list(representatives)
    while len(selected) < walker_count:
        available = np.asarray([i for i in range(len(pool)) if i not in set(selected)], dtype=int)
        distances = np.min(np.sum((normalized[available, None, :] - normalized[np.asarray(selected), :][None, :, :]) ** 2, axis=2), axis=1) if selected else np.ones(len(available))
        best = np.flatnonzero(distances == np.max(distances))
        selected.append(int(available[best[rng.integers(len(best))]]))
    selected_array = np.asarray(selected, dtype=int)
    states = pool[selected_array]
    stored_logp = logp[selected_array]
    reevaluated_logp = np.asarray([log_posterior(state) for state in states], dtype=float)
    if not np.all(np.isfinite(reevaluated_logp)) or not np.allclose(reevaluated_logp, stored_logp, rtol=0, atol=1e-8):
        raise RuntimeError("selected pool posterior values failed pre-backend re-evaluation")
    centered = ((states - pmin) / (pmax - pmin)) - np.mean((states - pmin) / (pmax - pmin), axis=0)
    if np.unique(states, axis=0).shape[0] != walker_count or np.linalg.matrix_rank(centered) != len(pmin):
        raise RuntimeError("selected walkers are not unique and full-rank")
    condition = float(np.linalg.cond(centered))
    if not np.isfinite(condition) or condition > 1e6 or np.any(np.ptp(states, axis=0) <= 0):
        raise RuntimeError(f"selected walkers fail geometry gate condition={condition}")
    return selected_array, states


def selection_validation_sha256(selection: Mapping[str, Any]) -> str:
    keys = (
        "pool_indices",
        "selected_physical_states",
        "stored_prior_component",
        "stored_log_likelihood",
        "stored_physical_log_posterior",
        "reevaluated_prior_component",
        "reevaluated_log_likelihood",
        "reevaluated_physical_log_posterior",
        "normalized_rank",
        "normalized_condition_number",
        "normalized_spread",
    )
    payload = {key: selection.get(key) for key in keys}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def run_fixed_production_chain(
    *,
    target: Mapping[str, Any],
    site: str,
    resolution: str,
    seed: int,
    pool_path: str | Path,
    output: str | Path,
    repository_commit: str,
    source_manifest: str | Path,
    dependency_manifest: str | Path,
    cases: Sequence[str],
    nwalkers: int = 64,
    nsteps: int = 32000,
    checkpoint_interval: int = 8000,
    n_processes: int = 1,
    sampler_coordinates: str = "transformed",
    move_configuration: str = "de_mixture",
    de_move_scale: float = 1.0,
    write_diagnostics: bool = True,
    selection_schema: str = "coupling-selection-ledger-v1",
    production_schema: str = "coupling-production-v1",
    daily_map_schema: str = "coupling-daily-maps-v1",
):
    """Run one fixed production chain from a frozen, provenance-checked pool."""
    output_path, pool_file = Path(output), Path(pool_path)
    scaffold = {
        "submission_config.env",
        "submit.sh",
        "submission_receipt.env",
        "submission_attempt.env",
        "retry_authorization.env",
        "backend.h5",
        "checkpoint_manifest.json",
        "checkpoint_manifest.json.tmp",
        "daily_index_maps.json",
        "selection_ledger.json",
        "selection_ledger.json.tmp",
        "production_result.json.tmp",
        "posterior_selection_ledger.json",
        "raw_chain.npz",
        "raw_chain_metadata.json",
        "raw_chain_hashes.json",
        "raw_chain.npz.tmp",
        "raw_chain_metadata.json.tmp",
        "raw_chain_hashes.json.tmp",
        "best_params.txt",
        "clm_params_best.nc",
        "diagnostic_report.md",
        "plots",
        "diagnostics",
    }
    existing = {path.name for path in output_path.iterdir()} if output_path.exists() else set()
    scheduler_logs = {name for name in existing if name.endswith((".out", ".err"))}
    submission_records = {
        name
        for name in existing
        if name.startswith("submission_") and name.endswith((".env", ".env.tmp"))
    }
    submitted_scripts = {
        name for name in existing if name.startswith("submit_") and name.endswith(".slurm")
    }
    if (
        "production_result.json" in existing
        or existing - scaffold - scheduler_logs - submitted_scripts - submission_records
    ):
        raise FileExistsError(f"refusing to overwrite production leaf: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    contract_path = pool_file.parent / "search_contract.json"
    if not contract_path.is_file():
        raise FileNotFoundError(f"missing frozen search contract: {contract_path}")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    canonical_cases = sorted(str(case).strip() for case in cases if str(case).strip())
    expected_site = target["sites"][0] if len(target["sites"]) == 1 else target["sites"]
    if (
        contract.get("site") != expected_site
        or contract.get("resolution") != resolution
        or contract.get("cases") != canonical_cases
    ):
        raise ValueError("candidate pool site/resolution/case membership does not match production target")
    if contract.get("target_identity") != target["identity"]:
        raise ValueError("candidate pool target identity differs from reconstructed production target")
    if contract.get("repository_commit") != repository_commit or contract.get("source_manifest_sha256") != sha256_file(source_manifest) or contract.get("dependency_manifest_sha256") != sha256_file(dependency_manifest):
        raise ValueError("candidate pool source/dependency provenance differs from locked production package")
    if contract.get("pool_sha256") != sha256_file(pool_file):
        raise ValueError("candidate pool hash differs from frozen search contract")
    pool = np.load(pool_file, allow_pickle=False)
    required = {
        "physical_states",
        "physical_log_posterior",
        "prior_component",
        "log_likelihood",
        "strata",
    }
    if required - set(pool.files):
        raise ValueError(f"pool missing arrays: {required - set(pool.files)}")
    pool_states = np.asarray(pool["physical_states"], dtype=float)
    strata = np.asarray(pool["strata"], dtype=int)
    pool_logp = np.asarray(pool["physical_log_posterior"], dtype=float)
    pool_prior = np.asarray(pool["prior_component"], dtype=float)
    pool_likelihood = np.asarray(pool["log_likelihood"], dtype=float)
    required_pool_size = int(contract.get("pool_gate", {}).get("selected_count", 0))
    if (
        required_pool_size < nwalkers
        or pool_states.shape[0] != required_pool_size
        or pool_states.shape[1] != len(target["pmin"])
        or strata.shape != pool_states.shape
        or pool_logp.shape != (required_pool_size,)
        or pool_prior.shape != (required_pool_size,)
        or pool_likelihood.shape != (required_pool_size,)
    ):
        raise ValueError("pool shape/size gate failed")
    selection_seed = int(hashlib.sha256(f"{seed}:{sha256_file(pool_file)}".encode()).hexdigest()[:8], 16)
    selection_path = output_path / "selection_ledger.json"
    if selection_path.exists():
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        expected_selection = {
            "schema": selection_schema,
            "site": site,
            "resolution": resolution,
            "production_seed": seed,
            "selection_seed": selection_seed,
            "pool": str(pool_file),
            "pool_sha256": sha256_file(pool_file),
            "target_identity": target["identity"],
            "search_contract_sha256": sha256_file(contract_path),
            "target_sha256": target["identity"]["sha256"],
        }
        for key, value in expected_selection.items():
            if selection.get(key) != value:
                raise ValueError(f"existing selection ledger mismatch for {key}")
        indices = np.asarray(selection.get("pool_indices"), dtype=int)
        states = np.asarray(selection.get("selected_physical_states"), dtype=float)
        if (
            indices.shape != (nwalkers,)
            or states.shape != (nwalkers, len(target["pmin"]))
            or not np.array_equal(states, pool_states[indices])
        ):
            raise ValueError("existing selection ledger state/index mismatch")
        reevaluated = np.asarray([target["log_posterior"](state) for state in states])
        if not np.allclose(reevaluated, pool_logp[indices], rtol=0, atol=1e-8):
            raise ValueError("existing selection ledger posterior mismatch")
        if selection.get("stored_prior_component") != pool_prior[indices].tolist():
            raise ValueError("existing selection ledger prior-component mismatch")
        if selection.get("stored_log_likelihood") != pool_likelihood[indices].tolist():
            raise ValueError("existing selection ledger likelihood-component mismatch")
        if selection.get("validation_sha256") != selection_validation_sha256(selection):
            raise ValueError("existing selection ledger validation hash mismatch")
    else:
        if (output_path / "backend.h5").exists():
            raise ValueError("backend exists without an immutable selection ledger")
        indices, states = select_production_walkers(
            pool_states,
            pool_logp,
            strata,
            target["pmin"],
            target["pmax"],
            selection_seed,
            target["log_posterior"],
            walker_count=nwalkers,
        )
        components = [target["log_components"](state) for state in states]
        reevaluated_prior = np.asarray(
            [item["prior_component"] for item in components], dtype=float
        )
        reevaluated_likelihood = np.asarray(
            [item["log_likelihood"] for item in components], dtype=float
        )
        reevaluated_posterior = np.asarray(
            [item["physical_log_posterior"] for item in components], dtype=float
        )
        if (
            not np.allclose(
                reevaluated_prior, pool_prior[indices], rtol=0, atol=1e-12
            )
            or not np.allclose(
                reevaluated_likelihood,
                pool_likelihood[indices],
                rtol=0,
                atol=1e-8,
            )
            or not np.allclose(
                reevaluated_posterior, pool_logp[indices], rtol=0, atol=1e-8
            )
        ):
            raise RuntimeError("selected pool posterior components failed re-evaluation")
        selected_normalized = (states - target["pmin"]) / (
            target["pmax"] - target["pmin"]
        )
        centered = selected_normalized - np.mean(selected_normalized, axis=0)
        selection = {
            "schema": selection_schema,
            "site": site,
            "resolution": resolution,
            "production_seed": seed,
            "selection_seed": selection_seed,
            "pool": str(pool_file),
            "pool_sha256": sha256_file(pool_file),
            "pool_indices": indices.tolist(),
            "selected_physical_states": states.tolist(),
            "stored_prior_component": pool_prior[indices].tolist(),
            "stored_log_likelihood": pool_likelihood[indices].tolist(),
            "stored_physical_log_posterior": pool_logp[indices].tolist(),
            "reevaluated_prior_component": reevaluated_prior.tolist(),
            "reevaluated_log_likelihood": reevaluated_likelihood.tolist(),
            "reevaluated_physical_log_posterior": reevaluated_posterior.tolist(),
            "normalized_rank": int(np.linalg.matrix_rank(centered)),
            "normalized_condition_number": float(np.linalg.cond(centered)),
            "normalized_spread": np.ptp(selected_normalized, axis=0).tolist(),
            "target_identity": target["identity"],
            "search_contract_sha256": sha256_file(contract_path),
            "target_sha256": target["identity"]["sha256"],
            "status": "validated_before_backend",
        }
        selection["validation_sha256"] = selection_validation_sha256(selection)
        write_json_atomic(selection_path, selection)
    result = MCMC_forcing(
        target["case"],
        myvars=["SR"],
        forcing_context=target["context"],
        workdir=target["repo_root"],
        nwalkers=nwalkers,
        nsteps=nsteps,
        fit_error=bool(target["identity"]["fit_error"]),
        n_processes=n_processes,
        output_root=str(output_path),
        write_diagnostics=write_diagnostics,
        seed=seed,
        sampler_coordinates=sampler_coordinates,
        move_configuration=move_configuration,
        initial_state=states,
        backend_path=output_path / "backend.h5",
        checkpoint_interval=checkpoint_interval,
        de_move_scale=de_move_scale,
        likelihood_resolution=resolution,
        daily_map_schema=daily_map_schema,
        posterior_selection_filename="posterior_selection_ledger.json",
        allow_existing_raw_chain=True,
    )
    metadata = {
        "schema": production_schema,
        "site": site,
        "sites": target["sites"],
        "cases": canonical_cases,
        "resolution": resolution,
        "seed": seed,
        "nwalkers": nwalkers,
        "nsteps": nsteps,
        "n_processes": n_processes,
        "sampler_coordinates": sampler_coordinates,
        "move_configuration": move_configuration,
        "de_move_scale": de_move_scale,
        "target_sha256": target["identity"]["sha256"],
        "pool_sha256": sha256_file(pool_file),
        "repository_commit": repository_commit,
        "source_manifest_sha256": sha256_file(source_manifest),
        "dependency_manifest_sha256": sha256_file(dependency_manifest),
        "result": result,
        "status": "pass",
    }
    selection["status"] = "production_complete"
    write_json_atomic(selection_path, selection)
    write_json_atomic(output_path / "production_result.json", metadata)
    return result


def _write_candidate_pool_artifacts(
    *,
    target: Mapping[str, Any],
    output_path: Path,
    pool: np.ndarray,
    pool_logp: np.ndarray,
    pool_strata: np.ndarray,
    diagnostics: Mapping[str, Any],
    states_array: np.ndarray,
    logp_array: np.ndarray,
    evaluations: Sequence[Mapping[str, Any]] | None,
    contract_fields: Mapping[str, Any],
    provenance: Mapping[str, Any] | None,
    contract_schema: str,
    candidate_metadata_schema: str,
) -> dict[str, Any]:
    """Persist pool, ledger, diagnostics, and search-contract artifacts."""
    pool_components = [target["log_components"](state) for state in pool]
    pool_prior = np.asarray(
        [item["prior_component"] for item in pool_components], dtype=float
    )
    pool_likelihood = np.asarray(
        [item["log_likelihood"] for item in pool_components], dtype=float
    )
    if not np.allclose(pool_prior + pool_likelihood, pool_logp, rtol=0, atol=1e-8):
        raise RuntimeError("candidate-pool posterior component decomposition failed")
    np.savez_compressed(
        output_path / "candidate_pool.npz",
        physical_states=pool,
        physical_log_posterior=pool_logp,
        prior_component=pool_prior,
        log_likelihood=pool_likelihood,
        strata=pool_strata,
    )
    np.savez_compressed(output_path / "candidate_ledger.npz", states=states_array, log_posterior=logp_array)
    candidate_metadata = {
        "schema": candidate_metadata_schema,
        "evaluations": list(evaluations or []),
        "target_sha256": target["identity"]["sha256"],
        "pool_sha256": sha256_file(output_path / "candidate_pool.npz"),
        "pool_rule": diagnostics.get("pool_rule"),
        "high_l_quantile_requested": diagnostics.get("high_l_quantile_requested"),
        "high_l_quantile_applied": diagnostics.get("high_l_quantile_applied"),
    }
    (output_path / "candidate_metadata.json").write_text(
        json.dumps(candidate_metadata, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    (output_path / "diversity_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    report = {
        "site": target["sites"][0] if len(target["sites"]) == 1 else target["sites"],
        "resolution": target["identity"]["resolution"],
        "parameter_names": target["parameter_names"],
        "pmin": np.asarray(target["pmin"], dtype=float).tolist(),
        "pmax": np.asarray(target["pmax"], dtype=float).tolist(),
        "diagnostics": diagnostics,
        "status": "pass",
    }
    (output_path / "initialization_report.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    contract = {
        "schema": contract_schema,
        "site": target["sites"][0] if len(target["sites"]) == 1 else target["sites"],
        "resolution": target["identity"]["resolution"],
        "cases": target["identity"]["cases"],
        "pool_gate": dict(diagnostics),
        "target_identity": target["identity"],
        "pool_sha256": sha256_file(output_path / "candidate_pool.npz"),
        "ledger_sha256": sha256_file(output_path / "candidate_ledger.npz"),
        "candidate_metadata_sha256": sha256_file(output_path / "candidate_metadata.json"),
        "diversity_diagnostics_sha256": sha256_file(
            output_path / "diversity_diagnostics.json"
        ),
        "initialization_report_sha256": sha256_file(
            output_path / "initialization_report.json"
        ),
        "status": "pass",
    }
    contract.update(dict(contract_fields))
    contract.update(dict(provenance or {}))
    (output_path / "search_contract.json").write_text(
        json.dumps(contract, indent=2, default=str) + "\n", encoding="utf-8"
    )
    artifact_names = (
        "candidate_pool.npz",
        "candidate_ledger.npz",
        "candidate_metadata.json",
        "diversity_diagnostics.json",
        "initialization_report.json",
        "search_contract.json",
    )
    artifact_manifest = {
        "schema": "coupling-initialization-artifact-manifest-v1",
        "artifacts": {
            name: sha256_file(output_path / name) for name in artifact_names
        },
        "status": "pass",
    }
    (output_path / "artifact_manifest.json").write_text(
        json.dumps(artifact_manifest, indent=2) + "\n", encoding="utf-8"
    )
    return {"pool": pool, "contract": contract, "diagnostics": diagnostics, "evaluations": int(len(states_array))}


def initialize_candidate_pool(
    *,
    target: Mapping[str, Any],
    output: str | Path,
    seed: int,
    sobol_counts: Sequence[int] = (8192, 16384, 32768, 65536),
    anchor_count: int = 32,
    anchor_max_evaluations: int = 512,
    pool_size: int = 640,
    pool_rule: str = "diversity_maximin",
    high_l_quantile: float = 0.90,
    provenance: Mapping[str, Any] | None = None,
    contract_schema: str = "coupling-search-contract-v1",
    candidate_metadata_schema: str = "coupling-candidate-metadata-v1",
):
    """Run a bounded Sobol/L-BFGS candidate search and freeze its artifacts."""
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    pmin, pmax = np.asarray(target["pmin"], dtype=float), np.asarray(target["pmax"], dtype=float)
    all_states: list[np.ndarray] = []
    all_logp: list[float] = []
    evaluations: list[dict[str, Any]] = []
    sampler = qmc.Sobol(d=len(pmin), scramble=True, seed=seed)
    normalized_full = sampler.random_base2(int(np.log2(max(sobol_counts))))
    evaluated_counts = []
    for count in sobol_counts:
        states = qmc.scale(normalized_full[:count], pmin, pmax)
        for row in states[len(all_states):count]:
            value = target["log_posterior"](row)
            all_states.append(np.asarray(row, dtype=float))
            all_logp.append(float(value))
            evaluations.append({"kind": "sobol", "state_index": int(len(all_states) - 1), "log_posterior": float(value)})
        evaluated_counts.append(int(len(all_states)))
        if np.sum(np.isfinite(np.asarray(all_logp))) >= pool_size:
            try:
                choose_candidate_pool(
                    np.asarray(all_states),
                    np.asarray(all_logp),
                    pmin,
                    pmax,
                    pool_size=pool_size,
                    seed=seed,
                    pool_rule=pool_rule,
                    high_l_quantile=high_l_quantile,
                )
                break
            except RuntimeError:
                pass
    states_array, logp_array = np.asarray(all_states, dtype=float), np.asarray(all_logp, dtype=float)
    finite_indices = np.flatnonzero(np.isfinite(logp_array))
    if len(finite_indices) < anchor_count:
        raise RuntimeError(f"fewer than {anchor_count} finite Sobol anchors")
    anchor_candidates = finite_indices[np.argsort(logp_array[finite_indices])[::-1][: min(512, len(finite_indices))]]
    normalized_candidates = (states_array[anchor_candidates] - pmin) / (pmax - pmin)
    anchor_indices = anchor_candidates[select_maximin(normalized_candidates, min(anchor_count, len(anchor_candidates)), seed + 100)]
    evaluations_count_before = int(len(all_states))
    for anchor in anchor_indices:
        target_evaluations = 0

        def objective(point: np.ndarray) -> float:
            nonlocal target_evaluations
            if target_evaluations >= anchor_max_evaluations:
                return 1.0e100
            target_evaluations += 1
            value = target["log_posterior"](point)
            all_states.append(np.asarray(point, dtype=float).copy())
            all_logp.append(float(value))
            evaluations.append({"kind": "lbfgs_eval", "state_index": int(len(all_states) - 1), "log_posterior": float(value)})
            return 1.0e100 if not np.isfinite(value) else -float(value)
        result = minimize(objective, states_array[anchor], method="L-BFGS-B", bounds=list(zip(pmin, pmax)), options={"maxiter": anchor_max_evaluations, "maxfun": anchor_max_evaluations, "ftol": 1e-12})
        if target_evaluations > anchor_max_evaluations:
            raise RuntimeError("L-BFGS-B anchor exceeded target-evaluation contract")
        evaluations.append(
            {
                "kind": "lbfgs_anchor",
                "source_index": int(anchor),
                "success": bool(result.success),
                "message": str(result.message),
                "optimizer_nfev": int(result.nfev),
                "target_evaluations": int(target_evaluations),
            }
        )
    states_array, logp_array = np.asarray(all_states, dtype=float), np.asarray(all_logp, dtype=float)
    pool, pool_logp, pool_strata, diagnostics = choose_candidate_pool(
        states_array,
        logp_array,
        pmin,
        pmax,
        pool_size=pool_size,
        seed=seed + 200,
        pool_rule=pool_rule,
        high_l_quantile=high_l_quantile,
    )
    return _write_candidate_pool_artifacts(
        target=target,
        output_path=output_path,
        pool=pool,
        pool_logp=pool_logp,
        pool_strata=pool_strata,
        diagnostics=diagnostics,
        states_array=states_array,
        logp_array=logp_array,
        evaluations=evaluations,
        contract_fields={
            "algorithm": "sobol_multistart_local_v1",
            "sobol_counts": [int(x) for x in sobol_counts],
            "evaluated_sobol_counts": evaluated_counts,
            "actual_evaluated_before_local": evaluations_count_before,
            "anchor_count": int(len(anchor_indices)),
            "anchor_max_posterior_evaluations": int(anchor_max_evaluations),
            "pool_rule": pool_rule,
            "high_l_quantile": float(high_l_quantile),
        },
        provenance=provenance,
        contract_schema=contract_schema,
        candidate_metadata_schema=candidate_metadata_schema,
    )


def rebuild_candidate_pool_from_ledger(
    *,
    target: Mapping[str, Any],
    ledger_path: str | Path,
    output: str | Path,
    pool_rule: str,
    high_l_quantile: float = 0.90,
    pool_size: int = 640,
    seed: int = 0,
    expected_ledger_sha256: str | None = None,
    provenance: Mapping[str, Any] | None = None,
    contract_schema: str = "coupling-search-contract-v1",
    candidate_metadata_schema: str = "coupling-candidate-metadata-v1",
):
    """Rebuild a candidate pool from a frozen search ledger without new search."""
    root = Path(output)
    ledger_file = Path(ledger_path)
    root.mkdir(parents=True, exist_ok=True)
    artifacts = root / "artifacts"
    staging = root / ".artifacts.build"
    if artifacts.exists():
        raise FileExistsError(f"refusing to overwrite rebuilt pool artifacts: {artifacts}")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=False)
    ledger_hash = sha256_file(ledger_file)
    if expected_ledger_sha256 is not None and ledger_hash != expected_ledger_sha256:
        raise ValueError(
            f"ledger hash mismatch: expected {expected_ledger_sha256}, found {ledger_hash}"
        )
    ledger = np.load(ledger_file, allow_pickle=False)
    if "states" not in ledger.files or "log_posterior" not in ledger.files:
        raise ValueError(f"ledger missing states/log_posterior arrays: {ledger_file}")
    states_array = np.asarray(ledger["states"], dtype=float)
    logp_array = np.asarray(ledger["log_posterior"], dtype=float)
    pmin = np.asarray(target["pmin"], dtype=float)
    pmax = np.asarray(target["pmax"], dtype=float)
    pool, pool_logp, pool_strata, diagnostics = choose_candidate_pool(
        states_array,
        logp_array,
        pmin,
        pmax,
        pool_size=pool_size,
        seed=seed,
        pool_rule=pool_rule,
        high_l_quantile=high_l_quantile,
    )
    result = _write_candidate_pool_artifacts(
        target=target,
        output_path=staging,
        pool=pool,
        pool_logp=pool_logp,
        pool_strata=pool_strata,
        diagnostics=diagnostics,
        states_array=states_array,
        logp_array=logp_array,
        evaluations=[
            {
                "kind": "ledger_rebuild",
                "source_ledger": str(ledger_file),
                "source_ledger_sha256": ledger_hash,
                "pool_rule": pool_rule,
                "high_l_quantile": float(high_l_quantile),
            }
        ],
        contract_fields={
            "algorithm": "ledger_pool_rebuild_v1",
            "source_ledger": str(ledger_file),
            "source_ledger_sha256": ledger_hash,
            "pool_rule": pool_rule,
            "high_l_quantile": float(high_l_quantile),
        },
        provenance=provenance,
        contract_schema=contract_schema,
        candidate_metadata_schema=candidate_metadata_schema,
    )
    staging.replace(artifacts)
    return result
