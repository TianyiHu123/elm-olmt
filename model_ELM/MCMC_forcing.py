import multiprocessing
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import emcee
import numpy as np

from .MCMC import _mcmc_write_outputs, sample_from_prior
from .mcmc_artifacts import write_raw_chain_artifact
from .mcmc_diagnostics import select_postburn_samples
from .mcmc_geometry import CoordinateTransform, make_move_configuration

# Populated in worker processes via Pool initializer (avoids re-pickling large static data).
_WORKER_STATE: Optional[Dict[str, Any]] = None


def _init_mcmc_worker(state: Dict[str, Any]) -> None:
    """Load static MCMC payloads once per worker process."""
    global _WORKER_STATE
    _WORKER_STATE = state
    # Warm artifact caches in each worker so first likelihood eval is not serialized.
    from .forcing_surrogate_artifact import load_forcing_surrogate_artifact
    from .spinup_surrogate_artifact import load_spinup_surrogate_artifact

    for _site, sd in state.get("site_data_by_site", {}).items():
        if str(sd.get("spinup_mode", "")) != "coupled":
            continue
        spinup_path = sd.get("spinup_artifact")
        forcing_path = sd.get("forcing_artifact")
        if spinup_path:
            load_spinup_surrogate_artifact(spinup_path, allow_legacy=False)
        if forcing_path:
            load_forcing_surrogate_artifact(forcing_path, allow_legacy=False)


def run_forcing_surrogate_site(
    site_data: Dict[str, Any],
    parms_model: np.ndarray,
    myvars: Sequence[str],
) -> Dict[str, np.ndarray]:
    """
    Forward model using a trained forcing surrogate for one site.

    This is a top-level function so it can be called in multiprocessing worker
    processes (emcee pool).

    When ``site_data["spinup_mode"] == "coupled"``, spinup is predicted from the
    current parameter vector via prepared coupled arrays (no ELM case object).
    Offline modes keep the historical fixed-spinup design-matrix path.
    """
    mode = str(site_data.get("spinup_mode", "mean_spinup"))
    pr = np.asarray(parms_model, dtype=np.float64).ravel()

    if mode == "coupled":
        from .coupled_surrogate import predict_coupled_sr_prepared

        if list(myvars) != ["SR"]:
            raise ValueError(
                "coupled spinup mode currently supports myvars=['SR'] only; "
                f"got {list(myvars)}"
            )
        # Legacy fallback: full case object (not multiprocessing-safe at scale).
        if "case" in site_data and "forcing_engineered_full" not in site_data:
            from .coupled_surrogate import predict_coupled_sr

            pred = predict_coupled_sr(
                site_data["case"],
                spinup_artifact=site_data["spinup_artifact"],
                forcing_artifact=site_data["forcing_artifact"],
                parameters=pr,
            )
            sr_full = np.asarray(pred["SR"], dtype=np.float64).ravel()
            overlap_idx = site_data.get("overlap_indices")
            if overlap_idx is None:
                return {"SR": sr_full}
            return {"SR": sr_full[np.asarray(overlap_idx, dtype=int)]}

        pred = predict_coupled_sr_prepared(
            spinup_artifact=site_data["spinup_artifact"],
            forcing_artifact=site_data["forcing_artifact"],
            parameters=pr,
            surface=site_data["surface"],
            climatology=site_data["climatology"],
            forcing_engineered=site_data["forcing_engineered_full"],
            overlap_indices=site_data.get("overlap_indices"),
        )
        return {"SR": np.asarray(pred["SR"], dtype=np.float64).ravel()}

    fe = np.asarray(site_data["forcing_engineered"], dtype=np.float64)
    sp = np.asarray(site_data["spinup"], dtype=np.float64).ravel()
    nf = int(site_data["n_forcing_cols"])
    nparam = int(site_data["n_params"])
    nsp = int(site_data["n_spinup"])
    ntime = int(fe.shape[0])

    if pr.size != nparam:
        raise ValueError(f"parms_model length mismatch: expected {nparam}, got {pr.size}")
    if sp.size != nsp:
        raise ValueError(f"spinup length mismatch: expected {nsp}, got {sp.size}")
    if fe.ndim != 2 or fe.shape[1] != nf:
        raise ValueError(f"forcing_engineered shape mismatch: expected (*,{nf}), got {fe.shape}")

    X = np.empty((ntime, nf + nparam + nsp), dtype=np.float64)
    X[:, :nf] = fe
    X[:, nf : nf + nparam] = pr
    X[:, nf + nparam :] = sp

    surrogate_forcing = site_data["surrogate_forcing"]
    x_scaler_forcing = site_data["x_scaler_forcing"]
    y_scaler_forcing = site_data["y_scaler_forcing"]

    out: Dict[str, np.ndarray] = {}
    for var in myvars:
        xn = x_scaler_forcing[var].transform(X)
        pred = surrogate_forcing[var].predict(xn)
        y = y_scaler_forcing[var].inverse_transform(np.asarray(pred).reshape(-1, 1))
        out[var] = y.ravel()
    return out


def log_posterior_forcing(
    parms,
    sites=None,
    myvars=None,
    pmin=None,
    pmax=None,
    obs=None,
    obs_err=None,
    nparms_ensemble=None,
    nerr_parms=None,
    site_data_by_site=None,
):
    # Prefer worker-local static state (Pool initializer) to avoid re-pickling large payloads.
    state = _WORKER_STATE
    if state is not None:
        sites = state["sites"]
        myvars = state["myvars"]
        pmin = state["pmin"]
        pmax = state["pmax"]
        obs = state["obs"]
        obs_err = state["obs_err"]
        nparms_ensemble = state["nparms_ensemble"]
        nerr_parms = state["nerr_parms"]
        site_data_by_site = state["site_data_by_site"]
        likelihood_resolution = state.get("likelihood_resolution", "hourly")
        daily_index_maps = state.get("daily_index_maps", {})
    else:
        likelihood_resolution = "hourly"
        daily_index_maps = {}

    prior = 1.0
    for j in range(nparms_ensemble):
        if parms[j] < pmin[j] or parms[j] > pmax[j]:
            prior = 0.0
    post = prior
    if prior > 0.0:
        parms_model = parms[0 : (nparms_ensemble - nerr_parms)]
        for s in sites:
            output = run_forcing_surrogate_site(site_data_by_site[s], parms_model, myvars)
            for v in myvars:
                myoutput = np.asarray(output[v]).flatten()
                myobs = np.asarray(obs[s][v]).flatten()
                myerr = np.asarray(obs_err[s][v]).flatten().copy()
                mask = (myobs > -9000) & (myerr > 0)
                if nerr_parms > 0:
                    myerr[mask] = parms[-len(myvars) + myvars.index(v)]
                if likelihood_resolution == "daily":
                    if v != "SR" or s not in daily_index_maps:
                        raise ValueError("daily likelihood is defined only for locked SR maps")
                    groups = daily_index_maps[s]["groups"]
                    daily_pred = np.asarray([np.mean(myoutput[group]) for group in groups], dtype=float)
                    daily_obs = np.asarray([np.mean(myobs[group]) for group in groups], dtype=float)
                    # The approved daily target uses fitted sigma_SR directly, without sqrt(24).
                    sigma = parms[-len(myvars) + myvars.index(v)] if nerr_parms > 0 else np.mean(myerr[mask])
                    resid = daily_pred - daily_obs
                    ri = (resid / sigma) ** 2
                    li = -0.5 * np.log(2.0 * np.pi) - np.log(sigma) - 0.5 * ri
                else:
                    resid = myoutput[mask] - myobs[mask]
                    ri = (resid / myerr[mask]) ** 2
                    li = -0.5 * np.log(2.0 * np.pi) - np.log(myerr[mask]) - 0.5 * ri
                post += np.sum(li)
    else:
        # Properly reject out-of-bounds proposals (finite sentinels can corrupt emcee chains).
        post = -np.inf
    return post


def log_posterior_forcing_sampler(sampler_coordinates):
    """Evaluate the physical target, including a Jacobian for transformed sampling."""
    state = _WORKER_STATE
    if state is None:
        raise RuntimeError("sampler log posterior requires initialized worker state")
    transform = state.get("coordinate_transform")
    if transform is None:
        return log_posterior_forcing(sampler_coordinates)
    try:
        physical = transform.sampler_to_physical(np.asarray(sampler_coordinates, dtype=float))
        physical_log_prob = log_posterior_forcing(physical)
        if not np.isfinite(physical_log_prob):
            return -np.inf
        return float(physical_log_prob + transform.log_abs_det_dphysical_dsampler(sampler_coordinates))
    except (ValueError, FloatingPointError, OverflowError):
        return -np.inf


def _attach_forcing_surrogate_from_primary(primary_case, target_case):
    if hasattr(target_case, "surrogate_forcing") and target_case.surrogate_forcing:
        return
    target_case.surrogate_forcing = primary_case.surrogate_forcing
    target_case.x_scaler_forcing = primary_case.x_scaler_forcing
    target_case.y_scaler_forcing = primary_case.y_scaler_forcing
    target_case.forcing_surrogate_training = primary_case.forcing_surrogate_training


def MCMC_forcing(
    self,
    myvars,
    forcing_context,
    workdir,
    nwalkers=32,
    nsteps=100,
    fit_error=True,
    n_processes: Optional[int] = None,
    smoke_likelihood_evals: int = 0,
    output_root: Optional[str] = None,
    write_diagnostics: bool = False,
    seed: Optional[int] = None,
    sampler_coordinates: str = "physical",
    move_configuration: str = "stretch",
    initial_state: Optional[np.ndarray] = None,
    backend_path: Optional[str | Path] = None,
    checkpoint_interval: int = 0,
    de_move_scale: float = 1.0,
    likelihood_resolution: str = "hourly",
    daily_map_schema: str = "spinup-forcing-coupling-iter011-daily-maps-v1",
    posterior_selection_filename: str = "selection_ledger.json",
    allow_existing_raw_chain: bool = False,
):
    sites = self.all_sites
    pmin = np.array(self.ensemble_pmin, dtype=float)
    pmax = np.array(self.ensemble_pmax, dtype=float)
    nparms_ensemble = int(self.nparms_ensemble)
    obs = {}
    obs_err = {}
    daily_index_maps = {}
    baseline_output: Dict[str, Dict[str, np.ndarray]] = {}
    site_data_by_site: Dict[str, Dict[str, Any]] = {}

    for s in sites:
        if s not in forcing_context:
            raise KeyError(f"Missing forcing_context for site '{s}'")
        fctx = forcing_context[s]
        mode = str(fctx.get("spinup_mode", "mean_spinup"))
        if mode != "coupled" and ("forcing_engineered" not in fctx or "spinup" not in fctx):
            raise KeyError(f"forcing_context[{s}] must include forcing_engineered and spinup")

        # Prefer explicit surrogate payload from forcing_context.
        surrogate_forcing = fctx.get("surrogate_forcing")
        x_scaler_forcing = fctx.get("x_scaler_forcing")
        y_scaler_forcing = fctx.get("y_scaler_forcing")
        meta = fctx.get("training_layout")
        case_obj = fctx.get("case")
        if (
            mode != "coupled"
            and (
                surrogate_forcing is None
                or x_scaler_forcing is None
                or y_scaler_forcing is None
                or meta is None
            )
        ):
            # Backward-compatible fallback: derive case object from the legacy primary-site workflow.
            if s == sites[0]:
                case_obj = self
            else:
                from model_ELM import ELMcase

                case_obj = ELMcase(casename=self.casename.replace(self.site, s))
                _attach_forcing_surrogate_from_primary(self, case_obj)
            surrogate_forcing = case_obj.surrogate_forcing
            x_scaler_forcing = case_obj.x_scaler_forcing
            y_scaler_forcing = case_obj.y_scaler_forcing
            meta = getattr(case_obj, "forcing_surrogate_training", None)
            if meta is None:
                raise ValueError(
                    f"Missing forcing_surrogate_training metadata on case for site '{s}'. Train forcing first."
                )

        if "obs" in fctx and "obs_err" in fctx:
            obs[s] = fctx["obs"]
            obs_err[s] = fctx["obs_err"]
        else:
            if case_obj is None:
                raise KeyError(
                    f"forcing_context[{s}] must include obs and obs_err when no case object is available."
                )
            if not hasattr(case_obj, "obs") or not hasattr(case_obj, "obs_err"):
                raise AttributeError(
                    f"Site {s} has no obs/obs_err; pass obs and obs_err in forcing_context."
                )
            obs[s] = case_obj.obs.copy()
            obs_err[s] = case_obj.obs_err.copy()
        if likelihood_resolution == "daily":
            if "daily_index_map" not in fctx:
                raise KeyError(f"forcing_context[{s}] is missing the locked daily index map")
            daily_index_maps[s] = fctx["daily_index_map"]

        if mode == "coupled":
            if case_obj is None:
                raise KeyError(f"forcing_context[{s}] must include case for coupled mode")
            if "spinup_artifact" not in fctx or "forcing_artifact" not in fctx:
                raise KeyError(
                    f"forcing_context[{s}] must include spinup_artifact and forcing_artifact "
                    "for coupled mode"
                )
            if meta is None:
                meta = fctx.get("training_layout") or {}
            n_params_expected = int(meta.get("n_params", self.nparms_ensemble))
            if n_params_expected != int(self.nparms_ensemble):
                raise ValueError(
                    f"Parameter count mismatch for site '{s}': "
                    f"case has {self.nparms_ensemble} parameters, surrogate expects {n_params_expected}."
                )
            from .coupled_surrogate import prepare_coupled_site_arrays

            prepared = prepare_coupled_site_arrays(
                case_obj,
                spinup_artifact=fctx["spinup_artifact"],
                forcing_artifact=fctx["forcing_artifact"],
            )
            if int(prepared["n_params"]) != n_params_expected:
                raise ValueError(
                    f"Prepared coupled n_params mismatch for site '{s}': "
                    f"{prepared['n_params']} vs {n_params_expected}"
                )
            # Multiprocessing-safe payload: arrays + artifact paths only (no ELM case).
            site_data_by_site[s] = {
                "spinup_mode": "coupled",
                "spinup_artifact": str(prepared["spinup_artifact_path"] or fctx["spinup_artifact"]),
                "forcing_artifact": str(
                    prepared["forcing_artifact_path"] or fctx["forcing_artifact"]
                ),
                "surface": prepared["surface"],
                "climatology": prepared["climatology"],
                "forcing_engineered_full": prepared["forcing_engineered_full"],
                "overlap_indices": fctx.get("overlap_diagnostics", {}).get(
                    "forcing_overlap_indices"
                ),
                "n_params": n_params_expected,
                "n_forcing_cols": int(prepared["n_forcing_cols"]),
                "n_spinup": int(prepared["n_spinup"]),
            }
            print(
                f"COUPLED_SITE_PREPARED site={s} "
                f"forcing_full={prepared['forcing_engineered_full'].shape} "
                f"surface={prepared['surface'].shape} clim={prepared['climatology'].shape}"
            )
        else:
            fe = np.asarray(fctx["forcing_engineered"], dtype=np.float64)
            sp = np.asarray(fctx["spinup"], dtype=np.float64).ravel()
            n_forcing_cols = int(meta.get("n_forcing_cols", -1))
            n_params_expected = int(meta.get("n_params", -1))
            n_spinup_expected = int(meta.get("n_spinup", -1))
            if n_forcing_cols <= 0 or n_params_expected <= 0 or n_spinup_expected <= 0:
                raise ValueError(
                    f"forcing metadata is incomplete for site '{s}': "
                    f"n_forcing_cols={n_forcing_cols}, n_params={n_params_expected}, n_spinup={n_spinup_expected}"
                )
            if n_params_expected != int(self.nparms_ensemble):
                raise ValueError(
                    f"Parameter count mismatch for site '{s}': "
                    f"case has {self.nparms_ensemble} parameters, surrogate expects {n_params_expected}."
                )
            if fe.ndim != 2 or fe.shape[1] != n_forcing_cols:
                raise ValueError(
                    f"forcing_engineered shape mismatch for site '{s}': "
                    f"expected (*, {n_forcing_cols}), got {fe.shape}"
                )
            if sp.size != n_spinup_expected:
                raise ValueError(
                    f"spinup length mismatch for site '{s}': "
                    f"expected {n_spinup_expected}, got {sp.size}"
                )

            expected_features = list(meta.get("forcing_feature_names", []))
            input_features = [str(x) for x in fctx.get("forcing_feature_names", [])]
            if expected_features and input_features and expected_features != input_features:
                raise ValueError(
                    f"Forcing feature names mismatch for site '{s}': "
                    f"expected {expected_features}, got {input_features}"
                )

            site_data_by_site[s] = {
                "spinup_mode": mode,
                "forcing_engineered": fe,
                "spinup": sp,
                "n_forcing_cols": n_forcing_cols,
                "n_params": n_params_expected,
                "n_spinup": n_spinup_expected,
                "surrogate_forcing": surrogate_forcing,
                "x_scaler_forcing": x_scaler_forcing,
                "y_scaler_forcing": y_scaler_forcing,
            }
        if "baseline_output" in fctx:
            baseline_keys = [
                str(var) for var in fctx["baseline_output"].keys() if var != "taxis"
            ]
            print(f"baseline_output site={s} vars={baseline_keys}")
            baseline_output[s] = {
                str(var): np.asarray(fctx["baseline_output"][var].mean(axis=1)).flatten()[
                    fctx["overlap_diagnostics"]["forcing_overlap_indices"]
                ]
                for var in fctx["baseline_output"]
                if var != "taxis"
            }

    # Add parameters to estimate observation error stddev
    nerr_parms = 0
    ensemble_parms = self.ensemble_parms.copy()
    if fit_error:
        print("Fitting observation error parameters")
        for v in myvars:
            mask = (obs[sites[0]][v] > -9000) & (obs_err[sites[0]][v] > 0)
            valid_maxima = [np.max(np.abs(obs[s][v][(obs[s][v] > -9000) & np.isfinite(obs[s][v]) & (obs_err[s][v] > 0) & np.isfinite(obs_err[s][v])])) for s in sites if np.any((obs[s][v] > -9000) & np.isfinite(obs[s][v]) & (obs_err[s][v] > 0) & np.isfinite(obs_err[s][v]))]
            max_obs = max(valid_maxima + [0.01])
            pmin = np.append(pmin, 0.0)
            pmax = np.append(pmax, 0.25 * max_obs)
            ensemble_parms = ensemble_parms + ["sigma_" + v]
            nparms_ensemble = len(ensemble_parms)
            nerr_parms = nerr_parms + 1

    smoke_n = int(smoke_likelihood_evals or 0)
    if smoke_n > 0:
        # Smoke calls must use the same locked hourly/daily target as production.  This state
        # deliberately omits a coordinate transform because the fixture evaluates physical states.
        _init_mcmc_worker({
            "sites": sites,
            "myvars": list(myvars),
            "pmin": np.asarray(pmin, dtype=float),
            "pmax": np.asarray(pmax, dtype=float),
            "obs": obs,
            "obs_err": obs_err,
            "nparms_ensemble": int(nparms_ensemble),
            "nerr_parms": int(nerr_parms),
            "site_data_by_site": site_data_by_site,
            "likelihood_resolution": likelihood_resolution,
            "daily_index_maps": daily_index_maps,
        })
        if initial_state is None:
            states = [0.5 * (pmin + pmax)]
        else:
            states = np.asarray(initial_state, dtype=float)
            if states.shape != (nwalkers, nparms_ensemble):
                raise ValueError(f"initial state must have shape {(nwalkers, nparms_ensemble)}, got {states.shape}")
            if not np.all(np.isfinite(states)) or np.any(states <= pmin) or np.any(states >= pmax):
                raise ValueError("smoke initial state is non-finite or outside strict physical bounds")
        logps = []
        for i, parms in enumerate(states):
            lp = log_posterior_forcing(
                parms,
                sites,
                myvars,
                pmin,
                pmax,
                obs,
                obs_err,
                nparms_ensemble,
                nerr_parms,
                site_data_by_site,
            )
            logps.append(float(lp))
            print(f"SMOKE_LIKELIHOOD_EVAL i={i} log_posterior={lp}")
        if not np.all(np.isfinite(logps)):
            raise RuntimeError("smoke likelihood produced a non-finite value")
        print(
            f"SMOKE_LIKELIHOOD_DONE n={len(logps)} "
            f"log_posterior_min={min(logps)} log_posterior_max={max(logps)}"
        )
        return {
            "smoke_likelihood_evals": len(logps),
            "log_posteriors": logps,
            "spinup_modes": {
                s: site_data_by_site[s].get("spinup_mode") for s in sites
            },
        }

    if seed is not None:
        np.random.seed(int(seed))
    transform = CoordinateTransform.from_parameters(
        ensemble_parms, pmin, pmax, enabled=(sampler_coordinates == "transformed")
    )
    if sampler_coordinates not in {"physical", "transformed"}:
        raise ValueError(f"unsupported sampler coordinate system: {sampler_coordinates}")
    if output_root is None:
        raise ValueError("raw-chain retention requires output_root")
    if likelihood_resolution not in {"hourly", "daily"}:
        raise ValueError(f"unsupported likelihood resolution: {likelihood_resolution}")
    if not np.isfinite(de_move_scale) or de_move_scale <= 0:
        raise ValueError("DEMove scale must be finite and positive")
    if likelihood_resolution == "daily":
        daily_path = Path(output_root) / "daily_index_maps.json"
        daily_payload = {"schema": daily_map_schema, "maps": daily_index_maps}
        if daily_path.exists():
            existing = json.loads(daily_path.read_text(encoding="utf-8"))
            if existing != daily_payload:
                raise ValueError("existing daily-map provenance differs from the locked target")
        else:
            daily_path.write_text(json.dumps(daily_payload, indent=2) + "\n", encoding="utf-8")
    if checkpoint_interval and (checkpoint_interval <= 0 or nsteps % checkpoint_interval):
        raise ValueError("checkpoint interval must be a positive divisor of nsteps")
    if initial_state is None:
        physical_initial = sample_from_prior(pmin, pmax, nwalkers)
    else:
        physical_initial = np.asarray(initial_state, dtype=float)
        if physical_initial.shape != (nwalkers, nparms_ensemble):
            raise ValueError(
                f"initial state must have shape {(nwalkers, nparms_ensemble)}, got {physical_initial.shape}"
            )
        # Enforce strict bounds, uniqueness, and full rank before an Iter009 chain starts.
        if not np.all(np.isfinite(physical_initial)) or np.any(physical_initial <= pmin) or np.any(physical_initial >= pmax):
            raise ValueError("initial state is non-finite or outside strict physical bounds")
        if np.unique(physical_initial, axis=0).shape[0] != nwalkers:
            raise ValueError("initial state must contain distinct walkers")
        if np.linalg.matrix_rank(physical_initial - physical_initial.mean(axis=0)) < nparms_ensemble:
            raise ValueError("initial state does not have full parameter rank")
    p0 = transform.physical_to_sampler(physical_initial)

    # Determine worker count (and cap it to available CPUs).
    avail = os.cpu_count() or 1
    slurm_cpus = os.environ.get("SLURM_CPUS_PER_TASK")
    default_workers = avail
    if slurm_cpus:
        try:
            default_workers = min(avail, int(slurm_cpus))
        except ValueError:
            default_workers = avail

    if n_processes is None:
        n_processes = default_workers
    else:
        n_processes = int(n_processes)
        n_processes = min(n_processes, avail)
    n_processes = max(1, int(n_processes))

    run_predict_fn = {
        s: (lambda parms_model, s=s: run_forcing_surrogate_site(site_data_by_site[s], parms_model, myvars))
        for s in sites
    }

    worker_state = {
        "sites": sites,
        "myvars": list(myvars),
        "pmin": np.asarray(pmin, dtype=float),
        "pmax": np.asarray(pmax, dtype=float),
        "obs": obs,
        "obs_err": obs_err,
        "nparms_ensemble": int(nparms_ensemble),
        "nerr_parms": int(nerr_parms),
        "site_data_by_site": site_data_by_site,
        "coordinate_transform": transform,
        "likelihood_resolution": likelihood_resolution,
        "daily_index_maps": daily_index_maps,
    }
    # Parent process also uses worker state so log_posterior_forcing has one code path.
    _init_mcmc_worker(worker_state)
    print(
        f"MCMC_WORKER_STATE_READY n_processes={n_processes} "
        f"sites={list(sites)} nwalkers={nwalkers} nsteps={nsteps} coordinates={sampler_coordinates}"
    )

    moves = make_move_configuration(move_configuration, de_move_scale=de_move_scale, ndim=nparms_ensemble)
    backend = None
    if backend_path is not None:
        backend_file = Path(backend_path)
        backend_file.parent.mkdir(parents=True, exist_ok=True)
        backend = emcee.backends.HDFBackend(str(backend_file))
        if not backend_file.exists():
            backend.reset(nwalkers, nparms_ensemble)
        else:
            backend_iteration = int(backend.iteration)
            if backend_iteration == 0:
                backend.reset(nwalkers, nparms_ensemble)
            elif backend_iteration > nsteps:
                raise ValueError(f"HDF backend has {backend_iteration} steps, exceeds locked {nsteps}")

    checkpoint_path = Path(output_root, "checkpoint_manifest.json") if checkpoint_interval else None

    def record_checkpoint() -> None:
        if checkpoint_path is None:
            return
        backend_hash = None
        if backend_path is not None and Path(backend_path).is_file():
            backend_hash = hashlib.sha256(Path(backend_path).read_bytes()).hexdigest()
        payload = {
            "schema": "spinup-forcing-coupling-iter009-checkpoints-v1",
            "backend": None if backend_path is None else str(backend_path),
            "backend_sha256": backend_hash,
            "backend_iteration": int(sampler.iteration),
            "required_steps": list(range(checkpoint_interval, nsteps + 1, checkpoint_interval)),
            "recorded_steps": list(range(checkpoint_interval, int(sampler.iteration) + 1, checkpoint_interval)),
        }
        temporary = checkpoint_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(checkpoint_path)

    def run_locked_chunks() -> None:
        while int(sampler.iteration) < nsteps:
            remaining = nsteps - int(sampler.iteration)
            chunk = min(remaining, checkpoint_interval if checkpoint_interval else remaining)
            sampler.run_mcmc(None if sampler.iteration else p0, chunk, progress=True)
            record_checkpoint()

    if n_processes > 1:
        with multiprocessing.Pool(
            processes=n_processes,
            initializer=_init_mcmc_worker,
            initargs=(worker_state,),
        ) as pool:
            sampler = emcee.EnsembleSampler(
                nwalkers,
                nparms_ensemble,
                log_posterior_forcing_sampler,
                args=(),
                pool=pool,
                moves=moves,
                backend=backend,
            )
            run_locked_chunks()
    else:
        sampler = emcee.EnsembleSampler(
            nwalkers,
            nparms_ensemble,
            log_posterior_forcing_sampler,
            args=(),
            moves=moves,
            backend=backend,
        )
        run_locked_chunks()
    
    print("run_mcmc done")
    sampler_chain = np.asarray(sampler.get_chain(discard=0, thin=1, flat=False), dtype=float)
    raw_chain = transform.sampler_to_physical(sampler_chain)
    raw_log_probs = np.asarray(sampler.get_log_prob(discard=0, thin=1, flat=False), dtype=float)
    raw_physical_log_probs = raw_log_probs - transform.log_abs_det_dphysical_dsampler(sampler_chain)
    if raw_chain.shape[0] != nsteps:
        raise RuntimeError(f"locked chain length mismatch: expected {nsteps}, got {raw_chain.shape[0]}")
    if checkpoint_interval:
        record_checkpoint()
    raw_metadata = write_raw_chain_artifact(
        output_root,
        chain=raw_chain,
        log_prob=raw_log_probs,
        initial_state=physical_initial,
        parameter_names=ensemble_parms,
        pmin=pmin,
        pmax=pmax,
        seed=int(seed) if seed is not None else -1,
        sites=sites,
        nwalkers=nwalkers,
        nsteps=nsteps,
        sampler_chain=sampler_chain,
        transform_metadata=transform.metadata(),
        move_configuration=move_configuration,
        de_move_scale=de_move_scale,
        likelihood_resolution=likelihood_resolution,
        backend_path=backend_path,
        physical_log_prob=raw_physical_log_probs,
        allow_existing=allow_existing_raw_chain,
    )
    try:
        acceptance_by_walker = np.asarray(sampler.acceptance_fraction, dtype=float)
        mean_acceptance = float(np.mean(acceptance_by_walker))
        print(
            "Mean acceptance fraction ",
            mean_acceptance,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Acceptance fraction unavailable: {exc}")
        acceptance_by_walker = np.full(nwalkers, np.nan)
        mean_acceptance = float("nan")

    n_model_parms = len(ensemble_parms) - nerr_parms
    try:
        tau_values = np.asarray(sampler.get_autocorr_time(tol=0), dtype=float)
        tau_max = float(np.nanmax(tau_values))
    except Exception as exc:  # characterization fallback is part of the contract
        print(f"AUTOCORR_UNAVAILABLE {exc}")
        tau_values = None
        tau_max = None
    selection = select_postburn_samples(
        chain=raw_chain,
        log_prob=raw_log_probs,
        pmin=np.asarray(pmin, dtype=float),
        pmax=np.asarray(pmax, dtype=float),
        n_model_parms=n_model_parms,
        nsteps=nsteps,
        tau_max=tau_max,
    )
    samples = selection["samples"]
    log_probs = selection["log_probs"]
    predictive_samples = selection["predictive_samples"]
    print(
        f"POSTPROCESS_FILTER eligible={samples.shape[0]} predictive={predictive_samples.shape[0]} "
        f"discard={selection['discard']} thin={selection['thin']}"
    )
    selection_payload = {
        "schema": "spinup-forcing-coupling-iter008-selection-v1",
        "raw_chain_sha256": raw_metadata["raw_chain_sha256"],
        "discard": selection["discard"],
        "thin": selection["thin"],
        "tau_available": selection["tau_available"],
        "tau_max": selection["tau_max"],
        "eligible_draws": int(samples.shape[0]),
        "predictive_draws": int(predictive_samples.shape[0]),
        "per_walker": selection["per_walker"],
        "ledger": selection["selected_ledger"],
    }
    Path(output_root, posterior_selection_filename).write_text(
        json.dumps(selection_payload, indent=2) + "\n", encoding="utf-8"
    )

    predictive_cache: Dict[str, Dict[str, Any]] = {}
    _mcmc_write_outputs(
        self,
        samples=samples,
        log_probs=log_probs,
        ensemble_parms=ensemble_parms,
        n_model_parms=n_model_parms,
        nerr_parms=nerr_parms,
        sites=sites,
        myvars=myvars,
        obs=obs,
        obs_err=obs_err,
        run_predict_fn=run_predict_fn,
        fit_error=fit_error,
        outdir_name="MCMC_forcing_output",
        baseline_output=baseline_output if baseline_output else None,
        olmtdir=workdir,
        output_root=output_root,
        predictive_cache=predictive_cache,
        predictive_samples=predictive_samples,
    )
    if write_diagnostics:
        if not output_root:
            raise ValueError("write_diagnostics=True requires output_root")
        from .mcmc_diagnostics import write_mcmc_diagnostics

        write_mcmc_diagnostics(
            output_root=output_root,
            sampler=sampler,
            samples=samples,
            log_probs=log_probs,
            ensemble_parms=ensemble_parms,
            n_model_parms=n_model_parms,
            nerr_parms=nerr_parms,
            pmin=pmin,
            pmax=pmax,
            sites=sites,
            myvars=myvars,
            obs=obs,
            obs_err=obs_err,
            baseline_output=baseline_output if baseline_output else None,
            forcing_context=forcing_context,
            predictive_cache=predictive_cache,
            nwalkers=nwalkers,
            nsteps=nsteps,
            raw_chain=raw_chain,
            raw_log_probs=raw_log_probs,
            discard=selection["discard"],
            thin=selection["thin"],
            seed=int(seed) if seed is not None else -1,
            selection_payload=selection_payload,
            tau_values=tau_values,
        )
    return {
        "mean_acceptance_fraction": mean_acceptance,
        "walker_acceptance_fraction": acceptance_by_walker.tolist(),
        "tau": None if tau_values is None else tau_values.tolist(),
        "posterior_selection": selection_payload,
    }
