#!/usr/bin/env python3
"""Iter015 makeup: redraw Predictions_SR_posterior.png with overlap-aligned ELM precal."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import build_coupling_target  # noqa: E402
from model_ELM.mcmc_diagnostics import _gaussian_loglik, _skill_metrics  # noqa: E402
from model_ELM.MCMC_forcing import run_forcing_surrogate_site  # noqa: E402

CASES = {"ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC", "JERC": "JERC_ppe6_I20TRCNPRDCTCBC"}
CONFIGS = [(resolution, scale) for resolution in ("hourly", "daily") for scale in ("0.50", "0.75", "1.00")]
SEEDS = (9009, 9010, 9011)


def elm_baseline(target: dict, site: str) -> np.ndarray:
    case = target["context"][site]["case"]
    raw = np.asarray(case.output["SR"], dtype=float)
    if raw.ndim == 2:
        series = raw.mean(axis=1)
    elif raw.ndim == 1:
        series = raw.ravel()
    else:
        raise ValueError(f"{site}: unexpected ELM output shape {raw.shape}")
    indices = np.asarray(target["context"][site]["overlap_indices"], dtype=int)
    aligned = series[indices]
    if aligned.shape != (len(indices),):
        raise ValueError(f"{site}: aligned ELM shape {aligned.shape}")
    aligned = aligned.copy()
    aligned[aligned < -9000] = np.nan
    return aligned


def reconstruct_draws(leaf: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = np.load(leaf / "raw_chain.npz", allow_pickle=False)
    chain = np.asarray(raw["chain"], float)
    physical_logp = np.asarray(raw["physical_log_prob"], float)
    selection = json.loads((leaf / "posterior_selection_ledger.json").read_text(encoding="utf-8"))
    discard = int(selection["discard"])
    thin = int(selection["thin"])
    eligible = chain[discard::thin]
    eligible_lp = physical_logp[discard::thin]
    finite = np.isfinite(eligible_lp)
    samples = eligible[finite]
    log_probs = eligible_lp[finite]
    if samples.size == 0:
        raise ValueError(f"{leaf}: no eligible samples")
    predictive = np.asarray(
        [chain[int(row["raw_step"]), int(row["walker"])] for row in selection["ledger"]],
        dtype=float,
    )
    return samples, log_probs, predictive


def rewrite_skill(path: Path, site: str, elm: np.ndarray, obs: np.ndarray, err: np.ndarray, pred_best: np.ndarray) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fieldnames = list(rows[0]) if rows else ["site", "var", "series", "n", "rmse", "bias", "r2", "kge"]
    rows = [row for row in rows if row.get("series") != "elm_precal"]
    metrics = _skill_metrics(elm, obs, err)
    rows.append({"site": site, "var": "SR", "series": "elm_precal", **{key: metrics[key] for key in ("n", "rmse", "bias", "r2", "kge")}})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    delta_path = path.parent / "delta_logL.csv"
    logl_opt = _gaussian_loglik(pred_best, obs, err)
    logl_elm = _gaussian_loglik(elm, obs, err)
    payload = [
        {
            "site": site,
            "var": "SR",
            "logL_optimized": logl_opt,
            "logL_elm_precal": logl_elm,
            "delta_logL_opt_minus_elm": (
                float("nan")
                if not (np.isfinite(logl_opt) and np.isfinite(logl_elm))
                else float(logl_opt - logl_elm)
            ),
        }
    ]
    with delta_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["site", "var", "logL_optimized", "logL_elm_precal", "delta_logL_opt_minus_elm"],
        )
        writer.writeheader()
        writer.writerows(payload)


def plot_prediction(
    path: Path,
    posterior: np.ndarray,
    best: np.ndarray,
    elm: np.ndarray,
    obs: np.ndarray,
    err: np.ndarray,
    sigma: float,
) -> None:
    lower = np.percentile(posterior, 2.5, axis=0)
    upper = np.percentile(posterior, 97.5, axis=0)
    median = np.percentile(posterior, 50, axis=0)
    x = np.arange(len(median))
    obs_plot = np.asarray(obs, float).copy()
    obs_plot[obs_plot < -9000] = np.nan
    err_plot = np.asarray(err, float).copy()
    err_plot[err_plot < -9000] = np.nan
    err_plot[err_plot > -9000] = sigma
    backup = path.with_name(path.stem + ".pre_elm_makeup.png")
    if path.is_file() and not backup.is_file():
        shutil.copy2(path, backup)
    plt.figure(figsize=(15, 3))
    plt.fill_between(x, lower, upper, color="gray", alpha=0.3, label="95% CI")
    plt.plot(x, median, color="red", linewidth=0.5, alpha=0.3, label="Model median")
    plt.plot(x, best, color="darkred", linewidth=0.5, label="Best fit", alpha=0.5)
    plt.plot(x, elm, color="darkgreen", linewidth=0.5, linestyle="--", label="ELM (pre-calibration)", alpha=0.5)
    plt.plot(x, obs_plot, color="blue", linewidth=0.5, label="Observations", alpha=0.5)
    plt.fill_between(x, obs_plot - err_plot, obs_plot + err_plot, color="blue", alpha=0.3)
    plt.xlabel("Time")
    plt.ylabel("SR")
    plt.title("Posterior predictive for SR")
    plt.legend()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path)
    plt.close()


def replot_leaf(root: Path, forcing, spinup, site: str, resolution: str, scale: str, seed: int, cache: dict) -> dict:
    leaf = root / "production" / site.lower() / f"{resolution}_{scale}" / f"seed_{seed}"
    key = (site, resolution)
    if key not in cache:
        cache[key] = build_coupling_target(
            cases=[CASES[site]],
            resolution=resolution,
            forcing_artifact=forcing,
            spinup_artifact=spinup,
            expected_physical_parameter_count=14,
        )
    target = cache[key]
    samples, log_probs, predictive = reconstruct_draws(leaf)
    best_state = samples[int(np.argmax(log_probs))]
    context = target["context"][site]
    elm = elm_baseline(target, site)
    obs = np.asarray(target["obs"][site]["SR"], float)
    err = np.asarray(target["obs_err"][site]["SR"], float)
    posterior = []
    for state in predictive:
        pred = run_forcing_surrogate_site(context, state[:-1], ["SR"])["SR"]
        posterior.append(np.asarray(pred, float).ravel())
    posterior = np.asarray(posterior, float)
    best = np.asarray(run_forcing_surrogate_site(context, best_state[:-1], ["SR"])["SR"], float).ravel()
    if elm.shape != best.shape or posterior.shape[1] != best.shape[0]:
        raise ValueError(
            f"{leaf}: length mismatch elm={elm.shape} best={best.shape} posterior={posterior.shape}"
        )
    if not np.any(np.isfinite(elm)):
        raise ValueError(f"{leaf}: aligned ELM baseline is non-finite")
    plot_path = leaf / "plots" / "predictions" / site / "Predictions_SR_posterior.png"
    plot_prediction(plot_path, posterior, best, elm, obs, err, float(best_state[-1]))
    rewrite_skill(leaf / "diagnostics" / "skill_table.csv", site, elm, obs, err, best)
    payload = {
        "leaf": str(leaf),
        "site": site,
        "resolution": resolution,
        "de_scale": scale,
        "seed": seed,
        "predictive_draws": int(posterior.shape[0]),
        "series_length": int(best.shape[0]),
        "elm_finite_frac": float(np.mean(np.isfinite(elm))),
        "plot": str(plot_path),
        "status": "pass",
    }
    (leaf / "diagnostics" / "elm_precal_makeup.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"REPLOT_PASS site={site} resolution={resolution} de_scale={scale} "
        f"seed={seed} n={best.shape[0]}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    cache = {}
    results = [
        replot_leaf(args.root, args.forcing_artifact, args.spinup_artifact, site, resolution, scale, seed, cache)
        for resolution, scale in CONFIGS
        for site in CASES
        for seed in SEEDS
    ]
    if len(results) != 36:
        raise ValueError("expected 36 makeup leaves")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"schema": "spinup-forcing-coupling-iter015-elm-precal-makeup-v1", "status": "pass", "leaves": results}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print("REPLOT_ELM_PRECAL_PASS leaves=36")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
