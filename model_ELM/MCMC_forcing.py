import multiprocessing
import os
from typing import Any, Dict, Optional, Sequence

import emcee
import numpy as np

from .MCMC import _mcmc_write_outputs, sample_from_prior


def run_forcing_surrogate_site(
    site_data: Dict[str, Any],
    parms_model: np.ndarray,
    myvars: Sequence[str],
) -> Dict[str, np.ndarray]:
    """
    Forward model using a trained forcing surrogate for one site.

    This is a top-level function so it can be called in multiprocessing worker
    processes (emcee pool).
    """
    fe = np.asarray(site_data["forcing_engineered"], dtype=np.float64)
    sp = np.asarray(site_data["spinup"], dtype=np.float64).ravel()
    nf = int(site_data["n_forcing_cols"])
    nparam = int(site_data["n_params"])
    nsp = int(site_data["n_spinup"])
    ntime = int(fe.shape[0])

    pr = np.asarray(parms_model, dtype=np.float64).ravel()
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
    sites,
    myvars,
    pmin,
    pmax,
    obs,
    obs_err,
    nparms_ensemble,
    nerr_parms,
    site_data_by_site,
):
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
        post = -9999999
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
    nwalkers=32,
    nsteps=100,
    fit_error=True,
    n_processes: Optional[int] = None,
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
        if "forcing_engineered" not in fctx or "spinup" not in fctx:
            raise KeyError(f"forcing_context[{s}] must include forcing_engineered and spinup")

        # Prefer explicit surrogate payload from forcing_context.
        surrogate_forcing = fctx.get("surrogate_forcing")
        x_scaler_forcing = fctx.get("x_scaler_forcing")
        y_scaler_forcing = fctx.get("y_scaler_forcing")
        meta = fctx.get("training_layout")
        case_obj = None
        if (
            surrogate_forcing is None
            or x_scaler_forcing is None
            or y_scaler_forcing is None
            or meta is None
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
            baseline_output[s] = {
                str(var): np.asarray(fctx["baseline_output"][var]).flatten()
                for var in fctx["baseline_output"]
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

    if n_processes > 1:
        with multiprocessing.Pool(processes=n_processes) as pool:
            sampler = emcee.EnsembleSampler(
                nwalkers,
                nparms_ensemble,
                log_posterior_forcing,
                args=(
                    sites,
                    myvars,
                    pmin,
                    pmax,
                    obs,
                    obs_err,
                    nparms_ensemble,
                    nerr_parms,
                    site_data_by_site,
                ),
                pool=pool,
            )
            sampler.run_mcmc(p0, nsteps, progress=True)
    else:
        sampler = emcee.EnsembleSampler(
            nwalkers,
            nparms_ensemble,
            log_posterior_forcing,
            args=(
                sites,
                myvars,
                pmin,
                pmax,
                obs,
                obs_err,
                nparms_ensemble,
                nerr_parms,
                site_data_by_site,
            ),
        )
        sampler.run_mcmc(p0, nsteps, progress=True)

    samples = sampler.get_chain(discard=nsteps // 5, thin=5, flat=True)
    log_probs = sampler.get_log_prob(discard=nsteps // 5, thin=5, flat=True)
    n_model_parms = len(ensemble_parms) - nerr_parms
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
    )
