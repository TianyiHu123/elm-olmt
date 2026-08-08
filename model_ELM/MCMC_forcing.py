import multiprocessing
import os
from typing import Any, Dict, Optional, Sequence

import emcee
import numpy as np

from .MCMC import _mcmc_write_outputs, sample_from_prior

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
                resid = myoutput[mask] - myobs[mask]
                ri = (resid / myerr[mask]) ** 2
                li = -0.5 * np.log(2.0 * np.pi) - np.log(myerr[mask]) - 0.5 * ri
                post += np.sum(li)
    else:
        # Properly reject out-of-bounds proposals (finite sentinels can corrupt emcee chains).
        post = -np.inf
    return post


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
):
    sites = self.all_sites
    pmin = np.array(self.ensemble_pmin, dtype=float)
    pmax = np.array(self.ensemble_pmax, dtype=float)
    nparms_ensemble = int(self.nparms_ensemble)
    obs = {}
    obs_err = {}
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
            max_obs = max([np.max(np.abs(obs[sites[0]][v][mask])), 0.01])
            pmin = np.append(pmin, 0.0)
            pmax = np.append(pmax, 0.25 * max_obs)
            ensemble_parms = ensemble_parms + ["sigma_" + v]
            nparms_ensemble = len(ensemble_parms)
            nerr_parms = nerr_parms + 1

    smoke_n = int(smoke_likelihood_evals or 0)
    if smoke_n > 0:
        mid = 0.5 * (pmin + pmax)
        logps = []
        for i in range(smoke_n):
            # Deterministic tiny budget around the prior midpoint.
            frac = float(i) / float(max(smoke_n - 1, 1))
            parms = pmin + frac * (pmax - pmin)
            if i == 0:
                parms = mid
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
        print(
            f"SMOKE_LIKELIHOOD_DONE n={smoke_n} "
            f"log_posterior_min={min(logps)} log_posterior_max={max(logps)}"
        )
        return {
            "smoke_likelihood_evals": smoke_n,
            "log_posteriors": logps,
            "spinup_modes": {
                s: site_data_by_site[s].get("spinup_mode") for s in sites
            },
        }

    p0 = sample_from_prior(pmin, pmax, nwalkers)

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
    }
    # Parent process also uses worker state so log_posterior_forcing has one code path.
    _init_mcmc_worker(worker_state)
    print(
        f"MCMC_WORKER_STATE_READY n_processes={n_processes} "
        f"sites={list(sites)} nwalkers={nwalkers} nsteps={nsteps}"
    )

    if n_processes > 1:
        with multiprocessing.Pool(
            processes=n_processes,
            initializer=_init_mcmc_worker,
            initargs=(worker_state,),
        ) as pool:
            sampler = emcee.EnsembleSampler(
                nwalkers,
                nparms_ensemble,
                log_posterior_forcing,
                args=(),
                pool=pool,
            )
            sampler.run_mcmc(p0, nsteps, progress=True)
    else:
        sampler = emcee.EnsembleSampler(
            nwalkers,
            nparms_ensemble,
            log_posterior_forcing,
            args=(),
        )
        sampler.run_mcmc(p0, nsteps, progress=True)
    
    print("run_mcmc done")
    samples = sampler.get_chain(discard=nsteps // 5, thin=5, flat=True)
    print("Flat samples size ", samples.shape)
    log_probs = sampler.get_log_prob(discard=nsteps // 5, thin=5, flat=True)
    print("Log probability size ", log_probs.shape)
    try:
        print(
            "Mean acceptance fraction ",
            float(np.mean(np.asarray(sampler.acceptance_fraction, dtype=float))),
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Acceptance fraction unavailable: {exc}")

    n_model_parms = len(ensemble_parms) - nerr_parms
    # Keep only prior-support samples for postprocess (coupled predict enforces bounds).
    pmin_m = np.asarray(pmin[:n_model_parms], dtype=float)
    pmax_m = np.asarray(pmax[:n_model_parms], dtype=float)
    in_bounds = np.all(
        (samples[:, :n_model_parms] >= pmin_m) & (samples[:, :n_model_parms] <= pmax_m),
        axis=1,
    )
    finite_lp = np.isfinite(log_probs)
    keep = in_bounds & finite_lp
    print(
        f"POSTPROCESS_FILTER kept={int(np.sum(keep))}/{samples.shape[0]} "
        f"in_bounds={int(np.sum(in_bounds))} finite_logp={int(np.sum(finite_lp))}"
    )
    if not np.any(keep):
        raise RuntimeError(
            "No prior-support posterior samples available for postprocess; "
            "MCMC chain did not retain in-bounds walkers."
        )
    samples = samples[keep]
    log_probs = log_probs[keep]

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
        )
