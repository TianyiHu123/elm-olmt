"""MCMC campaign diagnostics for forcing-surrogate calibration (Iter007+)."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def select_postburn_samples(
    *, chain: np.ndarray, log_prob: np.ndarray, pmin: np.ndarray, pmax: np.ndarray,
    n_model_parms: int, nsteps: int, tau_max: Optional[float],
) -> Dict[str, Any]:
    """Select finite in-bounds post-burn draws for derived diagnostics and plots."""
    del n_model_parms
    if tau_max is None or not np.isfinite(tau_max) or tau_max <= 0:
        discard, thin, tau_available = int(math.ceil(0.20 * nsteps)), 5, False
    else:
        discard = max(int(math.ceil(0.20 * nsteps)), int(math.ceil(5.0 * tau_max)))
        thin, tau_available = max(5, int(math.ceil(tau_max / 2.0))), True
    if discard >= chain.shape[0]:
        raise RuntimeError(f"Adaptive discard={discard} leaves no raw draws for nsteps={chain.shape[0]}")
    eligible_chain, eligible_lp = chain[discard::thin], log_prob[discard::thin]
    eligible = np.all((eligible_chain >= pmin) & (eligible_chain <= pmax), axis=2) & np.isfinite(eligible_lp)
    if not np.any(eligible):
        raise RuntimeError("No eligible raw-chain draws after bounds/log-prob filtering")
    records = []
    for walker in range(eligible.shape[1]):
        indices = np.flatnonzero(eligible[:, walker])
        if indices.size:
            chosen = indices if indices.size < 8 else indices[np.linspace(0, indices.size - 1, 8, dtype=int)]
            records.extend((int(step), int(walker)) for step in chosen)
    if len(records) < 512:
        records = [(step, walker) for step in range(eligible.shape[0]) for walker in range(eligible.shape[1]) if eligible[step, walker]]
    selected = np.asarray([eligible_chain[step, walker] for step, walker in records], float)
    selected_lp = np.asarray([eligible_lp[step, walker] for step, walker in records], float)
    return {
        "samples": eligible_chain[eligible], "log_probs": eligible_lp[eligible],
        "predictive_samples": selected, "predictive_log_probs": selected_lp,
        "discard": discard, "thin": thin, "tau_available": tau_available,
        "tau_max": None if tau_max is None else float(tau_max), "eligible_mask": eligible,
        "selected_ledger": [{"selected_draw_rank": rank, "walker": walker,
            "raw_step": int(discard + step * thin), "eligible_step": step,
            "log_probability": float(lp)} for rank, ((step, walker), lp) in enumerate(zip(records, selected_lp))],
        "per_walker": [{"walker": walker, "eligible": int(np.count_nonzero(eligible[:, walker])),
            "selected": sum(1 for _, chosen in records if chosen == walker)} for walker in range(eligible.shape[1])],
    }


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
    raw_chain: Optional[np.ndarray] = None,
    raw_log_probs: Optional[np.ndarray] = None,
    discard: Optional[int] = None,
    thin: Optional[int] = None,
    seed: Optional[int] = None,
    selection_payload: Optional[Mapping[str, Any]] = None,
    tau_values: Optional[np.ndarray] = None,
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
        tau = np.asarray(tau_values, dtype=float) if tau_values is not None else sampler.get_autocorr_time(tol=0)
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
        tau_a = np.full(len(ensemble_parms), np.nan, dtype=float)
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

    # Per-walker acceptance and per-parameter autocorrelation/stationarity evidence.
    with (diag_dir / "walker_acceptance.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["walker", "acceptance_fraction"])
        writer.writeheader()
        writer.writerows(
            {"walker": int(i), "acceptance_fraction": float(value)}
            for i, value in enumerate(accept)
        )
    with (diag_dir / "parameter_chain_health.csv").open("w", newline="", encoding="utf-8") as fp:
        fields = [
            "parameter", "autocorr_time", "steps_per_tau", "ess_approx",
            "first_half_mean", "second_half_mean", "stationarity_delta",
        ]
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        chain_for_health = np.asarray(raw_chain if raw_chain is not None else sampler.get_chain(), dtype=float)
        start = int(discard or 0)
        step = int(thin or 1)
        chain_for_health = chain_for_health[start::step]
        midpoint = max(1, chain_for_health.shape[0] // 2)
        for i, name in enumerate(ensemble_parms):
            values = chain_for_health[:, :, i] if chain_for_health.size else np.empty((0, nwalkers))
            first = float(np.mean(values[:midpoint])) if values.size else float("nan")
            second = float(np.mean(values[midpoint:])) if values.size else float("nan")
            tau_i = float(tau_a[i]) if i < tau_a.size else float("nan")
            writer.writerow(
                {
                    "parameter": name,
                    "autocorr_time": tau_i,
                    "steps_per_tau": (float(nsteps) / tau_i if np.isfinite(tau_i) and tau_i > 0 else float("nan")),
                    "ess_approx": (float(nwalkers * max(chain_for_health.shape[0], 0)) / tau_i if np.isfinite(tau_i) and tau_i > 0 else float("nan")),
                    "first_half_mean": first,
                    "second_half_mean": second,
                    "stationarity_delta": second - first if np.isfinite(first) and np.isfinite(second) else float("nan"),
                }
            )
    if selection_payload is not None:
        (diag_dir / "selection_summary.json").write_text(
            json.dumps(selection_payload, indent=2) + "\n", encoding="utf-8"
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

    # Human-readable, evidence-linked site report.  This is deliberately descriptive:
    # Iter008 has integrity gates, not scientific quality thresholds.
    report_lines = [
        "# Iter008 MCMC diagnostic report",
        "",
        "## Reproducible setup",
        f"- Sites: {', '.join(map(str, sites))}",
        f"- Variables: {', '.join(map(str, myvars))}",
        f"- Walkers x steps: {nwalkers} x {nsteps}",
        f"- Seed: {seed}",
        f"- Discard/thin: {discard}; {thin}",
        f"- Eligible draws: {samples.shape[0]}; predictive draws: {(selection_payload or {}).get('predictive_draws', 'unknown')}",
        "",
        "## Data and likelihood audit",
        "See `collocation_audit.csv`, `skill_table.csv`, `delta_logL.csv`, and `residual_summary.csv`.",
        "The fitted error parameter is site-specific under the locked `--fit-error` formulation.",
        "",
        "## Chain health and stationarity",
        "See `walker_acceptance.csv`, `parameter_chain_health.csv`, `chain_health.json`, and trace plots.",
        f"- Mean acceptance fraction: {chain_health.get('mean_acceptance_fraction')}",
        f"- Mean/max autocorrelation time: {chain_health.get('mean_autocorr_time')} / {chain_health.get('max_autocorr_time')}",
        f"- Approximate ESS: {chain_health.get('approx_ess')}",
        "",
        "## Posterior, identifiability, and prior edges",
        "See `posterior_summary.csv`, `prior_edge_occupancy.csv`, and the parameter posterior plots.",
        "",
        "## Predictive and residual diagnostics",
        "See prediction plots, residual plots, `skill_table.csv`, and `residual_summary.csv`.",
        "",
        "## Site conclusion",
        "Scientific quality is characterization only. The paired validator must classify the next direction as sampler-limited, likelihood-limited, site-specific model/data limitation, joint-calibration candidate, or inconclusive.",
    ]
    (root / "diagnostic_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    index = {
        "schema": "spinup-forcing-coupling-mcmc-diagnostics-v1",
        "diagnostics_dir": str(diag_dir),
        "files": sorted(p.name for p in diag_dir.iterdir()),
        "chain_health": chain_health,
        "n_collocation_rows": len(collocation_rows),
        "n_skill_rows": len(skill_rows),
        "raw_chain_shape": None if raw_chain is None else list(np.asarray(raw_chain).shape),
        "raw_log_prob_shape": None if raw_log_probs is None else list(np.asarray(raw_log_probs).shape),
        "discard": discard,
        "thin": thin,
        "seed": seed,
    }
    (diag_dir / "diagnostics_index.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8"
    )
    print(f"DIAGNOSTICS_WRITTEN {diag_dir}")
    return index
