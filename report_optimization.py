#!/usr/bin/env python3
"""Independent, non-destructive reporting for a completed coupled MCMC path.

The optimizer owns its leaf products. This stage reads those products and writes a
portable report package below ``<path-root>/reports``; it never alters a chain,
backend, or leaf-level plot.

Best-parameter tables, CLM NetCDF exports, the aggregate physical corner, and the
SR MAP ensemble overlay include Tier-A seeds only. Full-seed inventory remains in
``all_seed_parameter_sets.csv`` and ``reports/per_seed/``.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_ELM.MCMC_forcing import run_forcing_surrogate_site
from model_ELM.coupling_pipeline import build_coupling_target
from model_ELM.mcmc_diagnostics import _valid_mask
from model_ELM.optimization_config import load_campaign, write_stage_manifest


SCHEMA = "coupled-optimization-report-v4"
TIER_A_MIN = 0.20
TIER_A_MAX = 0.50
SEED_COLORS = (
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
)
CORNER_SUBSAMPLE_PER_SEED = 1000
CORNER_RNG_SEED = 16016


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_file(source: Path, destination: Path) -> str | None:
    if not source.is_file():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def _leaf_records(
    root: Path, tier_min: float, tier_max: float, campaign_sha256: str,
) -> list[dict[str, Any]]:
    leaves = sorted((root / "optimization").glob("seed_*"))
    if not leaves:
        raise FileNotFoundError(f"no optimization leaves under {root / 'optimization'}")
    records: list[dict[str, Any]] = []
    for leaf in leaves:
        raw_path = leaf / "raw_chain.npz"
        result_path = leaf / "production_result.json"
        required = (
            "stage_manifest.json", "raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json",
            "backend.h5", "checkpoint_manifest.json", "selection_ledger.json",
            "production_result.json", "best_params.txt", "clm_params_best.nc",
            "plots/corner/corner_plot.png", "diagnostics/skill_table.csv",
            "diagnostics/walker_acceptance.csv", "diagnostics/parameter_chain_health.csv",
            "diagnostics/chain_health.json", "diagnostics/collocation_audit.csv",
            "diagnostics/residual_summary.csv", "diagnostics/delta_logL.csv",
        )
        missing = [name for name in required if not (leaf / name).is_file()]
        if missing:
            raise FileNotFoundError(f"incomplete optimization leaf {leaf}: {', '.join(missing)}")
        if not (leaf / "plots" / "predictions").is_dir():
            raise FileNotFoundError(f"missing site-specific posterior products: {leaf}")
        if not raw_path.is_file() or not result_path.is_file():
            raise FileNotFoundError(f"incomplete optimization leaf: {leaf}")
        receipt = _json(leaf / "stage_manifest.json")
        if receipt.get("stage") != "optimization":
            raise ValueError(f"leaf stage receipt is not optimization: {leaf}")
        if receipt.get("campaign_sha256") != campaign_sha256:
            raise ValueError(f"leaf campaign receipt does not match report campaign: {leaf}")
        if Path(str(receipt.get("output", ""))).resolve() != leaf.resolve():
            raise ValueError(f"leaf stage receipt output does not match its directory: {leaf}")
        raw = np.load(raw_path, allow_pickle=False)
        chain = np.asarray(raw["chain"], dtype=float)
        logp = np.asarray(raw.get("physical_log_prob", raw["log_prob"]), dtype=float)
        if chain.ndim != 3 or logp.shape != chain.shape[:2]:
            raise ValueError(f"invalid raw-chain dimensions in {raw_path}")
        flat_index = int(np.nanargmax(logp.reshape(-1)))
        parameter_names = [str(value) for value in raw["parameter_names"]]
        state = chain.reshape(-1, chain.shape[-1])[flat_index]
        result = _json(result_path)
        acceptance = float(result.get("result", {}).get("mean_acceptance_fraction", np.nan))
        checkpoint = _json(leaf / "checkpoint_manifest.json")
        if int(checkpoint.get("backend_iteration", -1)) != int(result["nsteps"]):
            raise ValueError(f"checkpoint is not terminal for {leaf}")
        if not np.all(np.isfinite(chain)) or not np.all(np.isfinite(logp)):
            raise ValueError(f"non-finite raw chain or posterior values in {leaf}")
        if np.any(chain < np.asarray(raw["pmin"], float)) or np.any(chain > np.asarray(raw["pmax"], float)):
            raise ValueError(f"out-of-bounds physical chain in {leaf}")
        tier_a = bool(np.isfinite(acceptance) and tier_min <= acceptance <= tier_max)
        records.append({
            "seed": leaf.name.removeprefix("seed_"), "leaf": leaf,
            "parameter_names": parameter_names, "map_state": state,
            "map_log_posterior": float(logp.reshape(-1)[flat_index]), "chain": chain,
            "mean_acceptance_fraction": acceptance, "tier_a": tier_a,
            "tier_a_reason": "tier_a_pass" if tier_a else "acceptance_outside_descriptive_range",
            "chain_health": _json(leaf / "diagnostics" / "chain_health.json"),
            "parameter_health": list(csv.DictReader((leaf / "diagnostics" / "parameter_chain_health.csv").open(encoding="utf-8"))),
            "skills": list(csv.DictReader((leaf / "diagnostics" / "skill_table.csv").open(encoding="utf-8"))),
            "delta_log_likelihood": list(csv.DictReader((leaf / "diagnostics" / "delta_logL.csv").open(encoding="utf-8"))),
        })
    first = records[0]["parameter_names"]
    if any(record["parameter_names"] != first for record in records[1:]):
        raise ValueError("parameter names differ across seeds; refusing aggregate report")
    return records


def _parameter_rows(records: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    if not records:
        return ["seed", "tier_a", "tier_a_reason", "mean_acceptance_fraction", "map_log_posterior"], []
    fields = ["seed", "tier_a", "tier_a_reason", "mean_acceptance_fraction", "map_log_posterior"]
    fields += list(records[0]["parameter_names"])
    rows: list[dict[str, Any]] = []
    for record in records:
        row = {key: record[key] for key in fields[:5]}
        row.update(zip(record["parameter_names"], np.asarray(record["map_state"], float).tolist()))
        rows.append(row)
    return fields, rows


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_parameter_tables(
    report_dir: Path, records: list[dict[str, Any]], retained: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_fields, all_rows = _parameter_rows(records)
    if retained:
        tier_fields, tier_rows = _parameter_rows(retained)
    else:
        tier_fields, tier_rows = all_fields, []
    _write_csv(report_dir / "all_seed_parameter_sets.csv", all_fields, all_rows)
    _write_csv(report_dir / "parameter_sets.csv", tier_fields, tier_rows)
    shutil.copy2(report_dir / "parameter_sets.csv", report_dir / "parameter_sets.txt")
    return all_rows, tier_rows


def _seed_color(seed: str | int) -> str:
    try:
        index = int(seed) - 9009
    except (TypeError, ValueError):
        index = 0
    return SEED_COLORS[index % len(SEED_COLORS)]


def _post_burn_samples(chain: np.ndarray, subsample: int, rng: np.random.Generator) -> np.ndarray:
    """Descriptive post-burn subsample in physical coordinates (all parameters)."""
    nsteps = int(chain.shape[0])
    discard = max(1, int(np.ceil(0.20 * nsteps)))
    if discard >= nsteps:
        discard = max(0, nsteps // 5)
    flat = chain[discard:].reshape(-1, chain.shape[-1])
    if len(flat) <= subsample:
        return flat
    return flat[rng.choice(len(flat), size=subsample, replace=False)]


def _write_corner(report_dir: Path, records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Write Iter016-style seed-colored physical corner for Tier-A seeds only."""
    if not records:
        return None
    names = list(records[0]["parameter_names"])
    rng = np.random.default_rng(CORNER_RNG_SEED)
    series: list[tuple[str, np.ndarray, str]] = []
    for record in records:
        seed = str(record["seed"])
        samples = _post_burn_samples(
            np.asarray(record["chain"], dtype=float),
            CORNER_SUBSAMPLE_PER_SEED,
            rng,
        )
        series.append((seed, samples, _seed_color(seed)))
    ndim = len(names)
    figure, axes = plt.subplots(ndim, ndim, figsize=(24, 24), squeeze=False)
    for row in range(ndim):
        for column in range(ndim):
            axis = axes[row, column]
            if row == column:
                for _, samples, color in series:
                    axis.hist(
                        samples[:, column],
                        bins=30,
                        color=color,
                        density=True,
                        alpha=0.45 if len(series) > 1 else 1.0,
                        histtype="stepfilled",
                    )
            elif row > column:
                for _, samples, color in series:
                    axis.scatter(
                        samples[:, column],
                        samples[:, row],
                        s=1,
                        alpha=0.15 if len(series) == 1 else 0.20,
                        linewidths=0,
                        color=color,
                    )
            else:
                axis.axis("off")
            if row == ndim - 1:
                axis.set_xlabel(names[column], rotation=45, ha="right", fontsize=6)
            if column == 0 and row > 0:
                axis.set_ylabel(names[row], fontsize=6)
            axis.tick_params(labelsize=5)
    if len(series) > 1:
        handles = [
            plt.Line2D(
                [0], [0], marker="o", color="none",
                markerfacecolor=color, markersize=6, label=label,
            )
            for label, _, color in series
        ]
        figure.legend(handles=handles, loc="upper right", fontsize=8)
    site_name = str(Path(records[0]["leaf"]).resolve().parent.parent.name).upper()
    figure.suptitle(
        f"{site_name} ensemble physical corner (Tier-A seed-colored post-burn)",
        fontsize=12,
    )
    figure.tight_layout()
    plots = report_dir.parent / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    path = plots / "physical_corner.png"
    by_seed = plots / "physical_corner_by_seed.png"
    figure.savefig(path, dpi=150)
    figure.savefig(by_seed, dpi=150)
    plt.close(figure)
    return {
        "physical_corner": str(path),
        "physical_corner_by_seed": str(by_seed),
        "seeds": [label for label, _, _ in series],
        "subsample_per_seed": CORNER_SUBSAMPLE_PER_SEED,
        "discard_fraction": 0.20,
    }


def _mask_to_nan(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    masked = np.asarray(values, dtype=float).copy().ravel()
    masked[~valid] = np.nan
    return masked


def _elm_baseline(target: dict[str, Any], site: str) -> np.ndarray:
    case = target["context"][site]["case"]
    raw = np.asarray(case.output["SR"], dtype=float)
    if raw.ndim == 2:
        series = raw.mean(axis=1)
    elif raw.ndim == 1:
        series = raw.ravel()
    else:
        raise ValueError(f"{site}: unexpected ELM output shape {raw.shape}")
    indices = np.asarray(target["context"][site]["overlap_indices"], dtype=int)
    aligned = series[indices].copy()
    aligned[aligned < -9000] = np.nan
    return aligned


def _write_sr_map_ensemble(
    report_dir: Path,
    contract: dict[str, Any],
    retained: list[dict[str, Any]],
    *,
    resolution: str,
) -> dict[str, Any] | None:
    if not retained:
        return None
    shared = contract["shared"]
    variables = [str(value) for value in shared["variables"]]
    if variables != ["SR"]:
        raise ValueError(f"SR MAP ensemble overlay currently supports variables=['SR']; got {variables}")
    if resolution not in {"hourly", "daily"}:
        raise ValueError(f"unsupported likelihood resolution for SR overlay: {resolution}")
    names = list(retained[0]["parameter_names"])
    n_physical = sum(1 for name in names if not name.startswith("sigma_"))
    observation_paths = {
        str(site).upper(): Path(path)
        for site, path in dict(shared.get("observations") or {}).items()
    }
    target = build_coupling_target(
        cases=[str(case) for case in shared["cases"]],
        resolution=resolution,
        forcing_artifact=Path(shared["forcing_artifact"]),
        spinup_artifact=Path(shared["spinup_artifact"]),
        observation_paths=observation_paths or None,
        expected_physical_parameter_count=n_physical,
    )
    sites = [str(site).upper() for site in shared["sites"]]
    plots: dict[str, Any] = {"schema": "coupled-sr-map-ensemble-overlay-v1", "sites": {}}
    for site in sites:
        context = target["context"][site]
        obs = np.asarray(target["obs"][site]["SR"], float).ravel()
        err = np.asarray(target["obs_err"][site]["SR"], float).ravel()
        valid = _valid_mask(obs, err)
        x = np.arange(len(obs))
        obs_plot = _mask_to_nan(obs, valid)
        err_plot = _mask_to_nan(err, valid)
        elm_plot = _mask_to_nan(_elm_baseline(target, site), valid)
        destination = report_dir / "plots" / "predictions" / site
        destination.mkdir(parents=True, exist_ok=True)
        plot_path = destination / "Predictions_SR_MAP_ensemble.png"
        plt.figure(figsize=(12, 4))
        series: list[dict[str, Any]] = []
        for record in retained:
            parms = np.asarray(record["map_state"], float).ravel()[:n_physical]
            pred = np.asarray(
                run_forcing_surrogate_site(context, parms, ["SR"])["SR"], float
            ).ravel()
            if pred.shape != obs.shape:
                raise ValueError(
                    f"{site} seed {record['seed']}: MAP prediction length {pred.shape} "
                    f"!= observation length {obs.shape}"
                )
            plt.plot(x, _mask_to_nan(pred, valid), linewidth=0.8, alpha=0.7, label=f"MAP seed {record['seed']}")
            series.append({
                "seed": record["seed"],
                "mean_acceptance_fraction": record["mean_acceptance_fraction"],
                "map_log_posterior": record["map_log_posterior"],
            })
        plt.plot(x, elm_plot, color="darkgreen", linewidth=0.8, linestyle="--", label="ELM precal", alpha=0.8)
        plt.plot(x, obs_plot, color="blue", linewidth=0.8, label="Observations", alpha=0.8)
        plt.fill_between(x, obs_plot - err_plot, obs_plot + err_plot, color="blue", alpha=0.2)
        plt.xlabel("Overlap index")
        plt.ylabel("SR")
        plt.title(f"{site} Tier-A MAP ensemble SR overlay")
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        site_manifest = {
            "site": site,
            "valid_mask": "(obs > -9000) & (err > 0) & finite",
            "n_total": int(len(obs)),
            "n_valid": int(np.count_nonzero(valid)),
            "series": series,
            "plot": str(plot_path),
        }
        (destination / "sr_overlay_manifest.json").write_text(
            json.dumps(site_manifest, indent=2) + "\n", encoding="utf-8",
        )
        plots["sites"][site] = site_manifest
    return plots


def _copy_leaf_products(
    root: Path, records: list[dict[str, Any]], retained: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    retained_seeds = {record["seed"] for record in retained}
    copied: list[dict[str, Any]] = []
    for record in records:
        seed, leaf = record["seed"], Path(record["leaf"])
        destination = root / "reports" / "per_seed" / f"seed_{seed}"
        entry: dict[str, Any] = {"seed": seed, "tier_a": seed in retained_seeds, "clm_params": None}
        if seed in retained_seeds:
            entry["clm_params"] = _copy_file(
                leaf / "clm_params_best.nc",
                root / "reports" / "best_parameters" / "clm_params" / f"clm_params_seed_{seed}.nc",
            )
        for relative in (
            "best_params.txt", "plots/corner/corner_plot.png", "diagnostics/skill_table.csv",
            "diagnostics/walker_acceptance.csv", "diagnostics/collocation_audit.csv",
            "diagnostics/residual_summary.csv", "diagnostics/delta_logL.csv",
        ):
            entry[relative] = _copy_file(leaf / relative, destination / Path(relative).name)
        predictions = leaf / "plots" / "predictions"
        if predictions.is_dir():
            shutil.copytree(predictions, destination / "predictions", dirs_exist_ok=False)
            entry["posterior_timeseries"] = str(destination / "predictions")
        copied.append(entry)
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--path-root", required=True, type=Path)
    args = parser.parse_args()
    contract = load_campaign(args.campaign, "reporting")
    optimization = load_campaign(args.campaign, "optimization")["optimization"]
    resolution = str(optimization["likelihood_resolution"])
    root = args.path_root.resolve()
    reports = root / "reports"
    # Allow a materializer scaffold (submit script + config + scheduler logs). Refuse only
    # when prior reporting products already exist under this path-root.
    if (
        (reports / "report_manifest.json").exists()
        or (reports / "best_parameters").exists()
        or (root / "postprocess" / "stage_manifest.json").exists()
    ):
        raise FileExistsError(f"refusing to overwrite reporting outputs under {root}")
    reporting = contract["reporting"]
    tier_range = reporting.get("tier_a_acceptance_range", [TIER_A_MIN, TIER_A_MAX])
    if not isinstance(tier_range, list) or len(tier_range) != 2:
        raise ValueError("reporting.tier_a_acceptance_range must contain two values")
    tier_min, tier_max = (float(value) for value in tier_range)
    records = _leaf_records(root, tier_min, tier_max, str(contract["campaign_sha256"]))
    retained = [record for record in records if record["tier_a"]]
    parameter_dir = reports / "best_parameters"
    parameter_dir.mkdir(parents=True)
    all_rows, tier_rows = _write_parameter_tables(parameter_dir, records, retained)
    copied = (
        _copy_leaf_products(root, records, retained)
        if bool(reporting.get("copy_leaf_products", True))
        else []
    )
    corner = _write_corner(parameter_dir, retained)
    overlay = _write_sr_map_ensemble(reports, contract, retained, resolution=resolution)
    status = "pass" if retained else "insufficient_retained"
    evidence = [{"seed": record["seed"], "mean_acceptance_fraction": record["mean_acceptance_fraction"],
                 "chain_health": record["chain_health"], "parameter_health": record["parameter_health"],
                 "skills": record["skills"], "delta_log_likelihood": record["delta_log_likelihood"]}
                for record in records]
    manifest = {
        "schema": SCHEMA,
        "status": status,
        "sites": contract["shared"]["sites"],
        "discovered_seeds": [record["seed"] for record in records],
        "retained_tier_a_seeds": [record["seed"] for record in retained],
        "all_seed_rows": all_rows,
        "tier_a_parameter_rows": tier_rows,
        "tier_a_acceptance_range": [tier_min, tier_max],
        "copied_leaf_products": copied,
        "physical_corner": None if corner is None else corner.get("physical_corner"),
        "physical_corner_by_seed": None if corner is None else corner.get("physical_corner_by_seed"),
        "physical_corner_detail": corner,
        "sr_map_ensemble_overlay": overlay,
        "per_seed_diagnostic_evidence": evidence,
    }
    (reports / "report_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_stage_manifest(
        root / "postprocess",
        {
            **contract,
            "path_root": str(root),
            "leaf_count": len(records),
            "retained_tier_a_count": len(retained),
            "status": status,
        },
    )
    print(
        f"REPORT_PASS status={status} leaves={len(records)} "
        f"tier_a={len(retained)} root={root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
