"""MCMC campaign diagnostics for forcing-surrogate calibration (Iter007+)."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _valid_mask(obs: np.ndarray, err: np.ndarray) -> np.ndarray:
    obs_a = np.asarray(obs, dtype=float).ravel()
    err_a = np.asarray(err, dtype=float).ravel()
    return (obs_a > -9000) & (err_a > 0) & np.isfinite(obs_a) & np.isfinite(err_a)


def _skill_metrics(pred: np.ndarray, obs: np.ndarray, err: np.ndarray) -> Dict[str, float]:
    mask = _valid_mask(obs, err)
    y = np.asarray(obs, dtype=float).ravel()[mask]
    p = np.asarray(pred, dtype=float).ravel()[mask]
    if y.size == 0:
        return {
            "n": 0.0,
            "rmse": float("nan"),
            "bias": float("nan"),
            "r2": float("nan"),
            "kge": float("nan"),
        }
    resid = p - y
    rmse = float(np.sqrt(np.mean(resid**2)))
    bias = float(np.mean(resid))
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = float("nan") if ss_tot <= 0 else float(1.0 - ss_res / ss_tot)
    # Kling-Gupta efficiency (simplified)
    if np.std(y) == 0 or np.std(p) == 0:
        kge = float("nan")
    else:
        r = float(np.corrcoef(p, y)[0, 1])
        alpha = float(np.std(p) / np.std(y))
        beta = float(np.mean(p) / np.mean(y)) if np.mean(y) != 0 else float("nan")
        kge = float(1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2))
    return {"n": float(y.size), "rmse": rmse, "bias": bias, "r2": r2, "kge": kge}


def _gaussian_loglik(pred: np.ndarray, obs: np.ndarray, err: np.ndarray) -> float:
    mask = _valid_mask(obs, err)
    y = np.asarray(obs, dtype=float).ravel()[mask]
    p = np.asarray(pred, dtype=float).ravel()[mask]
    e = np.asarray(err, dtype=float).ravel()[mask]
    if y.size == 0:
        return float("nan")
    resid = p - y
    return float(np.sum(-0.5 * np.log(2.0 * np.pi) - np.log(e) - 0.5 * (resid / e) ** 2))


def write_mcmc_diagnostics(
    *,
    output_root: str | Path,
    sampler: Any,
    samples: np.ndarray,
    log_probs: np.ndarray,
    ensemble_parms: Sequence[str],
    n_model_parms: int,
    nerr_parms: int,
    pmin: np.ndarray,
    pmax: np.ndarray,
    sites: Sequence[str],
    myvars: Sequence[str],
    obs: Mapping[str, Mapping[str, np.ndarray]],
    obs_err: Mapping[str, Mapping[str, np.ndarray]],
    baseline_output: Optional[Mapping[str, Mapping[str, np.ndarray]]],
    forcing_context: Mapping[str, Mapping[str, Any]],
    predictive_cache: Mapping[str, Mapping[str, Any]],
    nwalkers: int,
    nsteps: int,
) -> Dict[str, Any]:
    root = Path(output_root)
    diag_dir = root / "diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)

    # --- Collocation audit ---
    collocation_rows = []
    for s in sites:
        od = forcing_context.get(s, {}).get("overlap_diagnostics", {})
        collocation_rows.append(
            {
                "site": s,
                "forcing_rows": od.get("n_forcing"),
                "obs_rows": od.get("n_obs"),
                "overlap_rows": od.get("n_overlap"),
                "first_overlap_time": od.get("first_overlap_time"),
                "last_overlap_time": od.get("last_overlap_time"),
                "spinup_mode": forcing_context.get(s, {}).get("spinup_mode"),
            }
        )
    with (diag_dir / "collocation_audit.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "site",
                "forcing_rows",
                "obs_rows",
                "overlap_rows",
                "first_overlap_time",
                "last_overlap_time",
                "spinup_mode",
            ],
        )
        writer.writeheader()
        writer.writerows(collocation_rows)

    # --- Chain health ---
    accept = np.asarray(sampler.acceptance_fraction, dtype=float)
    chain_health: Dict[str, Any] = {
        "nwalkers": int(nwalkers),
        "nsteps": int(nsteps),
        "mean_acceptance_fraction": float(np.mean(accept)),
        "min_acceptance_fraction": float(np.min(accept)),
        "max_acceptance_fraction": float(np.max(accept)),
        "flat_samples": int(samples.shape[0]),
        "n_model_parms": int(n_model_parms),
        "nerr_parms": int(nerr_parms),
    }
    try:
        tau = sampler.get_autocorr_time(tol=0)
        tau_a = np.asarray(tau, dtype=float)
        chain_health["mean_autocorr_time"] = float(np.nanmean(tau_a))
        chain_health["max_autocorr_time"] = float(np.nanmax(tau_a))
        # ESS approximation using thinned flat length / mean tau
        mean_tau = float(np.nanmean(tau_a))
        chain_health["approx_ess"] = (
            float("nan") if not np.isfinite(mean_tau) or mean_tau <= 0
            else float(samples.shape[0] / mean_tau)
        )
    except Exception as exc:  # noqa: BLE001 - characterization only
        chain_health["autocorr_error"] = str(exc)
        chain_health["mean_autocorr_time"] = float("nan")
        chain_health["max_autocorr_time"] = float("nan")
        chain_health["approx_ess"] = float("nan")

    log_prob_full = np.asarray(sampler.get_log_prob(discard=0, flat=False), dtype=float)
    np.savetxt(diag_dir / "log_prob_trace.txt", log_prob_full)
    plt.figure(figsize=(10, 4))
    for i in range(min(log_prob_full.shape[1], 8)):
        plt.plot(log_prob_full[:, i], alpha=0.4, linewidth=0.7)
    plt.xlabel("Step")
    plt.ylabel("log posterior")
    plt.title("Log-posterior traces (first walkers)")
    plt.tight_layout()
    plt.savefig(diag_dir / "log_prob_trace.png")
    plt.close()
    (diag_dir / "chain_health.json").write_text(
        json.dumps(chain_health, indent=2) + "\n", encoding="utf-8"
    )

    # --- Posterior summary + prior-edge occupancy ---
    edge_eps = 1e-6
    summary_rows = []
    edge_rows = []
    for i, name in enumerate(ensemble_parms):
        col = samples[:, i]
        lo = float(pmin[i])
        hi = float(pmax[i])
        width = max(hi - lo, edge_eps)
        near_lo = float(np.mean(col <= lo + edge_eps * width))
        near_hi = float(np.mean(col >= hi - edge_eps * width))
        summary_rows.append(
            {
                "parameter": name,
                "map": float(samples[int(np.argmax(log_probs)), i]),
                "mean": float(np.mean(col)),
                "std": float(np.std(col)),
                "p2.5": float(np.percentile(col, 2.5)),
                "p50": float(np.percentile(col, 50)),
                "p97.5": float(np.percentile(col, 97.5)),
                "prior_min": lo,
                "prior_max": hi,
            }
        )
        edge_rows.append(
            {
                "parameter": name,
                "frac_near_lower": near_lo,
                "frac_near_upper": near_hi,
            }
        )
    with (diag_dir / "posterior_summary.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "parameter",
                "map",
                "mean",
                "std",
                "p2.5",
                "p50",
                "p97.5",
                "prior_min",
                "prior_max",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)
    with (diag_dir / "prior_edge_occupancy.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=["parameter", "frac_near_lower", "frac_near_upper"]
        )
        writer.writeheader()
        writer.writerows(edge_rows)

    # --- Skill / residual / delta-logL ---
    skill_rows = []
    residual_rows = []
    delta_rows = []
    baseline_output = baseline_output or {}
    for s in sites:
        cache = predictive_cache.get(s, {})
        best = cache.get("best", {})
        for v in myvars:
            y = np.asarray(obs[s][v], dtype=float).ravel()
            e = np.asarray(obs_err[s][v], dtype=float).ravel()
            pred_best = np.asarray(best.get(v, []), dtype=float).ravel()
            if pred_best.size == 0:
                continue
            metrics_opt = _skill_metrics(pred_best, y, e)
            skill_rows.append(
                {"site": s, "var": v, "series": "optimized_best", **metrics_opt}
            )
            logl_opt = _gaussian_loglik(pred_best, y, e)
            elm = None
            if s in baseline_output and v in baseline_output[s]:
                elm = np.asarray(baseline_output[s][v], dtype=float).ravel()
                metrics_elm = _skill_metrics(elm, y, e)
                skill_rows.append(
                    {"site": s, "var": v, "series": "elm_precal", **metrics_elm}
                )
                logl_elm = _gaussian_loglik(elm, y, e)
                delta_rows.append(
                    {
                        "site": s,
                        "var": v,
                        "logL_optimized": logl_opt,
                        "logL_elm_precal": logl_elm,
                        "delta_logL_opt_minus_elm": (
                            float("nan")
                            if not (np.isfinite(logl_opt) and np.isfinite(logl_elm))
                            else float(logl_opt - logl_elm)
                        ),
                    }
                )
            else:
                delta_rows.append(
                    {
                        "site": s,
                        "var": v,
                        "logL_optimized": logl_opt,
                        "logL_elm_precal": float("nan"),
                        "delta_logL_opt_minus_elm": float("nan"),
                    }
                )

            mask = _valid_mask(y, e)
            resid = pred_best[mask] - y[mask]
            if resid.size:
                residual_rows.append(
                    {
                        "site": s,
                        "var": v,
                        "n": int(resid.size),
                        "resid_mean": float(np.mean(resid)),
                        "resid_std": float(np.std(resid)),
                        "resid_lag1_corr": (
                            float(np.corrcoef(resid[:-1], resid[1:])[0, 1])
                            if resid.size > 1
                            else float("nan")
                        ),
                    }
                )
                plt.figure(figsize=(10, 3))
                plt.plot(resid, linewidth=0.6, color="black")
                plt.axhline(0.0, color="gray", linewidth=0.8)
                plt.xlabel("Masked time index")
                plt.ylabel(f"Residual ({v})")
                plt.title(f"Optimized residual: {s} {v}")
                plt.tight_layout()
                plt.savefig(diag_dir / f"residual_{s}_{v}.png")
                plt.close()
                plt.figure()
                plt.hist(resid, bins=40, density=True, alpha=0.7)
                plt.xlabel(f"Residual ({v})")
                plt.ylabel("Density")
                plt.title(f"Residual histogram: {s} {v}")
                plt.tight_layout()
                plt.savefig(diag_dir / f"residual_hist_{s}_{v}.png")
                plt.close()

    with (diag_dir / "skill_table.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=["site", "var", "series", "n", "rmse", "bias", "r2", "kge"]
        )
        writer.writeheader()
        writer.writerows(skill_rows)
    with (diag_dir / "delta_logL.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "site",
                "var",
                "logL_optimized",
                "logL_elm_precal",
                "delta_logL_opt_minus_elm",
            ],
        )
        writer.writeheader()
        writer.writerows(delta_rows)
    with (diag_dir / "residual_summary.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "site",
                "var",
                "n",
                "resid_mean",
                "resid_std",
                "resid_lag1_corr",
            ],
        )
        writer.writeheader()
        writer.writerows(residual_rows)

    index = {
        "schema": "spinup-forcing-coupling-mcmc-diagnostics-v1",
        "diagnostics_dir": str(diag_dir),
        "files": sorted(p.name for p in diag_dir.iterdir()),
        "chain_health": chain_health,
        "n_collocation_rows": len(collocation_rows),
        "n_skill_rows": len(skill_rows),
    }
    (diag_dir / "diagnostics_index.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8"
    )
    print(f"DIAGNOSTICS_WRITTEN {diag_dir}")
    return index
