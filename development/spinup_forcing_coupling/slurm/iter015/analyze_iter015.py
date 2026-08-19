#!/usr/bin/env python3
"""Iter015 analysis: 36-leaf integrity, Iter011 decisions, reusable overlay/corner/diagnostics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from emcee.autocorr import integrated_time
from scipy.stats import wasserstein_distance

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import build_coupling_target  # noqa: E402
from model_ELM.MCMC_forcing import run_forcing_surrogate_site  # noqa: E402
from model_ELM.mcmc_geometry import CoordinateTransform  # noqa: E402

CASES = {"ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC", "JERC": "JERC_ppe6_I20TRCNPRDCTCBC"}
CONFIGS = [(resolution, scale) for resolution in ("hourly", "daily") for scale in ("0.50", "0.75", "1.00")]
SEEDS = (9009, 9010, 9011)
LEDGER_RESOLUTION = {"ABBY": "daily", "JERC": "hourly"}
TOOLS = REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing empty table {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def leaf_dir(root: Path, site: str, resolution: str, scale: str, seed: int) -> Path:
    return root / "production" / site.lower() / f"{resolution}_{scale}" / f"seed_{seed}"


def experiment_dir(analysis_root: Path, site: str, resolution: str, scale: str) -> Path:
    return analysis_root / site.lower() / f"{resolution}_{scale}"


def tau(chain: np.ndarray) -> np.ndarray:
    answer = np.array(
        [float(np.ravel(integrated_time(chain[:, :, i], tol=0, quiet=True))[0]) for i in range(15)]
    )
    if not np.all(np.isfinite(answer)) or np.any(answer <= 0):
        raise ValueError("non-finite physical tau")
    return answer


def skill_from_table(path: Path, series: str) -> dict:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("series") == series]
    if not rows:
        raise ValueError(f"{path}: missing series {series}")
    row = rows[0]
    return {key: float(row[key]) for key in ("rmse", "bias", "r2") if key in row}


def validate_leaf(root: Path, site: str, resolution: str, scale: str, seed: int, reference: dict) -> dict:
    leaf = leaf_dir(root, site, resolution, scale, seed)
    required = (
        "raw_chain.npz",
        "raw_chain_metadata.json",
        "raw_chain_hashes.json",
        "backend.h5",
        "checkpoint_manifest.json",
        "selection_ledger.json",
        "production_result.json",
    )
    if any(not (leaf / name).is_file() for name in required):
        raise FileNotFoundError(f"{leaf}: incomplete immutable package")
    diagnostics = (
        "chain_health.json",
        "walker_acceptance.csv",
        "prior_edge_occupancy.csv",
        "skill_table.csv",
    )
    plot_paths = (
        "plots/corner/corner_plot.png",
        f"plots/predictions/{site}/Predictions_SR_posterior.png",
    )
    if any(not (leaf / "diagnostics" / name).is_file() for name in diagnostics):
        raise FileNotFoundError(f"{leaf}: required diagnostics missing")
    if any(not (leaf / name).is_file() for name in plot_paths):
        raise FileNotFoundError(f"{leaf}: required standard plots missing")
    raw = np.load(leaf / "raw_chain.npz", allow_pickle=False)
    chain = np.asarray(raw["chain"], float)
    sampler = np.asarray(raw["sampler_chain"], float)
    logp = np.asarray(raw["log_prob"], float)
    physical_logp = np.asarray(raw["physical_log_prob"], float)
    pmin = np.asarray(raw["pmin"], float)
    pmax = np.asarray(raw["pmax"], float)
    names = [str(x) for x in raw["parameter_names"]]
    if names != reference["names"] or not np.array_equal(pmin, reference["pmin"]) or not np.array_equal(pmax, reference["pmax"]):
        raise ValueError(f"{leaf}: parameter/bounds contract mismatch")
    if any(not (leaf / "plots" / "pdfs" / f"{name}.png").is_file() for name in names):
        raise FileNotFoundError(f"{leaf}: parameter PDF missing")
    if chain.shape != (8000, 64, 15) or sampler.shape != chain.shape:
        raise ValueError(f"{leaf}: chain shape contract failure")
    if not all(np.all(np.isfinite(x)) for x in (chain, sampler, logp, physical_logp)):
        raise ValueError(f"{leaf}: non-finite chain")
    if np.any(chain <= pmin) or np.any(chain >= pmax):
        raise ValueError(f"{leaf}: bounds contract failure")
    metadata = json.loads((leaf / "raw_chain_metadata.json").read_text(encoding="utf-8"))
    hashes = json.loads((leaf / "raw_chain_hashes.json").read_text(encoding="utf-8"))
    checkpoint = json.loads((leaf / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    selection = json.loads((leaf / "selection_ledger.json").read_text(encoding="utf-8"))
    production = json.loads((leaf / "production_result.json").read_text(encoding="utf-8"))
    if metadata.get("nwalkers") != 64 or metadata.get("nsteps") != 8000:
        raise ValueError(f"{leaf}: sampler contract mismatch")
    if metadata.get("move_configuration") != "de_mixture":
        raise ValueError(f"{leaf}: move_configuration mismatch")
    if metadata.get("likelihood_resolution") != resolution:
        raise ValueError(f"{leaf}: likelihood resolution mismatch")
    if float(metadata.get("de_move_scale")) != float(scale):
        raise ValueError(f"{leaf}: DEMove scale mismatch")
    if hashes.get("raw_chain_sha256") != digest(leaf / "raw_chain.npz"):
        raise ValueError(f"{leaf}: raw digest mismatch")
    if checkpoint.get("backend_iteration") != 8000:
        raise ValueError(f"{leaf}: checkpoint iteration mismatch")
    if checkpoint.get("required_steps") != [2000, 4000, 6000, 8000]:
        raise ValueError(f"{leaf}: checkpoint required_steps mismatch")
    if selection.get("pool_reuse_policy") != "site_hybrid_pool_reuse_v1":
        raise ValueError(f"{leaf}: pool_reuse_policy missing")
    if production.get("pool_reuse_policy") != "site_hybrid_pool_reuse_v1":
        raise ValueError(f"{leaf}: production reuse policy missing")
    transform = CoordinateTransform.from_parameters(names, pmin, pmax, enabled=True)
    if not np.allclose(
        logp - transform.log_abs_det_dphysical_dsampler(sampler),
        physical_logp,
        rtol=0,
        atol=1e-10,
    ):
        raise ValueError(f"{leaf}: Jacobian convention mismatch")
    accept = np.genfromtxt(leaf / "diagnostics" / "walker_acceptance.csv", delimiter=",", names=True)["acceptance_fraction"]
    with (leaf / "diagnostics" / "prior_edge_occupancy.csv").open(newline="", encoding="utf-8") as handle:
        sigma_rows = [row for row in csv.DictReader(handle) if row.get("parameter") == "sigma_SR"]
    if len(sigma_rows) != 1:
        raise ValueError(f"{leaf}: sigma_SR edge diagnostic missing")
    sigma_edge = float(sigma_rows[0]["frac_near_upper"])
    t6000, t8000 = tau(chain[:6000]), tau(chain)
    skill_path = leaf / "diagnostics" / "skill_table.csv"
    map_skill = skill_from_table(skill_path, "optimized_best")
    elm_skill = skill_from_table(skill_path, "elm_precal")
    return {
        "site": site,
        "seed": seed,
        "resolution": resolution,
        "de_scale": scale,
        "leaf": str(leaf),
        "mean_acceptance": float(np.mean(accept)),
        "saturation": float(np.max(np.mean(np.abs(sampler) >= 10, axis=(0, 1)))),
        "min_steps_per_tau": float(np.min(8000 / t8000)),
        "max_tau_change": float(np.max(np.abs(t8000 - t6000) / t6000)),
        "abs_resid_lag24": float("nan"),
        "sigma_upper_edge": sigma_edge,
        "raw_chain_sha256": hashes["raw_chain_sha256"],
        "map_rmse": map_skill.get("rmse", float("nan")),
        "map_bias": map_skill.get("bias", float("nan")),
        "map_r2": map_skill.get("r2", float("nan")),
        "elm_rmse": elm_skill.get("rmse", float("nan")),
        "elm_bias": elm_skill.get("bias", float("nan")),
        "elm_r2": elm_skill.get("r2", float("nan")),
        "pool_target_sha256": selection.get("pool_target_sha256"),
        "campaign_target_sha256": selection.get("campaign_target_sha256"),
    }


def directed_metric(left, right, name):
    a = np.asarray([r[name] for r in left], float)
    b = np.asarray([r[name] for r in right], float)
    if name == "mean_acceptance":
        a, b, threshold = (
            np.maximum(0.20 - a, 0) + np.maximum(a - 0.50, 0),
            np.maximum(0.20 - b, 0) + np.maximum(b - 0.50, 0),
            0.03,
        )
    elif name == "saturation":
        if np.max(a) <= 0.05 and np.max(b) <= 0.05:
            return 0
        threshold = 0.10
    elif name == "min_steps_per_tau":
        tiers_a, tiers_b = np.digitize(a, [20.0, 50.0]), np.digitize(b, [20.0, 50.0])
        signs = np.sign(a - b)
        relative = np.abs(a - b) / np.maximum(b, 1e-12)
        if np.all(signs == signs[0]) and signs[0] and (np.any(tiers_a != tiers_b) or np.median(relative) >= 0.20):
            return int(signs[0])
        return 0
    elif name == "abs_resid_lag24":
        threshold = 0.05
    elif name == "sigma_upper_edge":
        if np.max(a) <= 0.10 and np.max(b) <= 0.10:
            return 0
        threshold = 0.20
    else:
        av, bv = float(a[0]), float(b[0])
        if (av <= 0.05 and bv <= 0.05) or (av > 0.05 and bv > 0.05):
            return 0
        return 1 if av < bv else -1
    delta = b - a
    signs = np.sign(delta)
    if np.all(signs == signs[0]) and signs[0] and abs(float(np.median(delta))) >= threshold:
        return int(signs[0])
    return 0


def run_tool(script: Path, extra: list[str]) -> None:
    command = [sys.executable, str(script), *extra]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{script.name} failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def write_specs_and_plots(
    root: Path,
    analysis_root: Path,
    forcing: Path,
    spinup: Path,
    site: str,
    resolution: str,
    scale: str,
) -> None:
    out = experiment_dir(analysis_root, site, resolution, scale)
    out.mkdir(parents=True, exist_ok=True)
    chains = []
    members = []
    for seed in SEEDS:
        leaf = leaf_dir(root, site, resolution, scale, seed)
        chains.append({"label": str(seed), "path": str(leaf / "raw_chain.npz")})
        members.append({"kind": "selection_ledger", "path": str(leaf / "selection_ledger.json")})
    pool = root / "pool_rebuild" / site.lower() / "artifacts" / "candidate_pool.npz"
    overlay_spec = {
        "schema": "spinup-forcing-coupling-init-cloud-overlay-v1",
        "case": CASES[site],
        "resolution": resolution,
        "title": f"{site} {resolution}/{scale} hybrid starts",
        "clouds": [
            {"label": "hybrid_pool", "kind": "pool_npz", "path": str(pool)},
            {"label": "walkers", "kind": "walker_union", "members": members},
        ],
        "pairwise_comparisons": [{"left": "hybrid_pool", "right": "walkers"}],
    }
    overlay_path = out / "init_cloud_overlay.spec.json"
    overlay_path.write_text(json.dumps(overlay_spec, indent=2) + "\n", encoding="utf-8")
    diag_spec = {
        "schema": "spinup-forcing-coupling-fixed-length-mcmc-diagnostics-v1",
        "case": CASES[site],
        "resolution": resolution,
        "chains": chains,
    }
    diag_path = out / "mcmc_diagnostics.spec.json"
    diag_path.write_text(json.dumps(diag_spec, indent=2) + "\n", encoding="utf-8")
    corner_spec = {
        "schema": "spinup-forcing-coupling-physical-corner-v1",
        "title": f"{site} {resolution}/{scale} physical corner",
        "include_sigma_SR": True,
        "color_by_seed": False,
        "write_pooled": True,
        "write_per_seed": False,
        "subsample": 2000,
        "rng_seed": 14014,
        "chains": chains,
    }
    corner_path = out / "physical_corner.spec.json"
    corner_path.write_text(json.dumps(corner_spec, indent=2) + "\n", encoding="utf-8")
    run_tool(
        TOOLS / "plot_init_cloud_overlay.py",
        [
            "--spec", str(overlay_path),
            "--forcing-artifact", str(forcing),
            "--spinup-artifact", str(spinup),
            "--output-dir", str(out),
            "--overwrite",
        ],
    )
    run_tool(
        TOOLS / "fixed_length_mcmc_diagnostics.py",
        [
            "--spec", str(diag_path),
            "--forcing-artifact", str(forcing),
            "--spinup-artifact", str(spinup),
            "--output-dir", str(out),
            "--overwrite",
        ],
    )
    run_tool(
        TOOLS / "plot_physical_corner.py",
        [
            "--spec", str(corner_path),
            "--output-dir", str(out),
            "--overwrite",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--analysis-output", required=True, type=Path)
    parser.add_argument("--summary-dir", required=True, type=Path)
    args = parser.parse_args()
    analysis_root = args.analysis_output
    analysis_root.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)

    references = {}
    for site in CASES:
        reference_leaf = leaf_dir(args.root, site, "hourly", "1.00", 9009)
        archive = np.load(reference_leaf / "raw_chain.npz", allow_pickle=False)
        metadata = json.loads((reference_leaf / "raw_chain_metadata.json").read_text(encoding="utf-8"))
        references[site] = {
            "names": [str(x) for x in archive["parameter_names"]],
            "pmin": np.asarray(archive["pmin"], float),
            "pmax": np.asarray(archive["pmax"], float),
            "transform_kinds": metadata.get("transform", {}).get("transform_kinds"),
        }
    rows = [
        validate_leaf(args.root, site, resolution, scale, seed, references[site])
        for resolution, scale in CONFIGS
        for site in CASES
        for seed in SEEDS
    ]
    if len(rows) != 36:
        raise ValueError("global 36-leaf completeness failure")
    hourly_targets = {}
    for row in rows:
        site = row["site"]
        if site not in hourly_targets:
            hourly_targets[site] = build_coupling_target(
                cases=[CASES[site]],
                resolution="hourly",
                forcing_artifact=args.forcing_artifact,
                spinup_artifact=args.spinup_artifact,
                expected_physical_parameter_count=14,
            )
        leaf = Path(row["leaf"])
        raw = np.load(leaf / "raw_chain.npz", allow_pickle=False)
        chain = np.asarray(raw["chain"], float)
        physical_logp = np.asarray(raw["physical_log_prob"], float)
        best = chain.reshape(-1, 15)[int(np.argmax(physical_logp))]
        target = hourly_targets[site]
        obs = np.asarray(target["obs"][site]["SR"], float)
        err = np.asarray(target["obs_err"][site]["SR"], float)
        pred = np.asarray(
            run_forcing_surrogate_site(target["context"][site], best[:-1], ["SR"])["SR"],
            float,
        )
        mask = (obs > -9000) & (err > 0) & np.isfinite(pred)
        resid = pred[mask] - obs[mask]
        if resid.size > 24 and np.std(resid[:-24]) and np.std(resid[24:]):
            lag24 = abs(float(np.corrcoef(resid[:-24], resid[24:])[0, 1]))
        else:
            lag24 = float("nan")
        if not np.isfinite(lag24):
            raise ValueError(f"{leaf}: non-finite hourly residual lag-24")
        row["abs_resid_lag24"] = lag24

    cross_rows = []
    for resolution, scale in CONFIGS:
        for site in CASES:
            archives = [
                np.load(leaf_dir(args.root, site, resolution, scale, seed) / "raw_chain.npz", allow_pickle=False)
                for seed in SEEDS
            ]
            chains = [np.asarray(item["chain"], float)[4000:] for item in archives]
            widths = np.asarray(archives[0]["pmax"], float) - np.asarray(archives[0]["pmin"], float)
            distance = max(
                wasserstein_distance(a[:, :, k].ravel(), b[:, :, k].ravel()) / widths[k]
                for a in chains
                for b in chains
                for k in range(15)
            )
            cross_rows.append(
                {
                    "site": site,
                    "resolution": resolution,
                    "de_scale": scale,
                    "max_cross_seed_width_fraction": float(distance),
                }
            )
    write_csv(analysis_root / "leaf_metrics.csv", rows)
    write_csv(analysis_root / "cross_seed_wasserstein.csv", cross_rows)
    combined = []
    for row in rows:
        match = next(
            item
            for item in cross_rows
            if all(item[k] == row[k] for k in ("site", "resolution", "de_scale"))
        )
        combined.append({**row, **match})
    write_csv(args.summary_dir / "six_configuration_seed_metrics.csv", combined)

    decisions = []
    names = (
        "mean_acceptance",
        "saturation",
        "min_steps_per_tau",
        "max_cross_seed_width_fraction",
        "abs_resid_lag24",
        "sigma_upper_edge",
    )
    for site in CASES:
        site_rows = [row for row in combined if row["site"] == site]
        interpretable = {
            (resolution, scale)
            for resolution, scale in CONFIGS
            if all(
                np.isfinite(row["max_tau_change"]) and row["max_tau_change"] <= 0.20
                for row in site_rows
                if row["resolution"] == resolution and row["de_scale"] == scale
            )
        }
        by_config = {
            (resolution, scale): sorted(
                [row for row in site_rows if row["resolution"] == resolution and row["de_scale"] == scale],
                key=lambda item: item["seed"],
            )
            for resolution, scale in CONFIGS
        }
        comparison_rows = []
        audit_rows = []
        dominates = {config: set() for config in CONFIGS}
        for left in CONFIGS:
            for right in CONFIGS:
                if left == right:
                    continue
                direction = {name: directed_metric(by_config[left], by_config[right], name) for name in names}
                better = [name for name, value in direction.items() if value > 0]
                worse = [name for name, value in direction.items() if value < 0]
                if better and not worse:
                    dominates[left].add(right)
                comparison_rows.append(
                    {
                        "site": site,
                        "left": f"{left[0]}_{left[1]}",
                        "right": f"{right[0]}_{right[1]}",
                        "improves": ";".join(better),
                        "worsens": ";".join(worse),
                        "dominates": bool(better and not worse),
                    }
                )
                for name in names:
                    left_values = [float(row[name]) for row in by_config[left]]
                    right_values = [float(row[name]) for row in by_config[right]]
                    audit_rows.append(
                        {
                            "site": site,
                            "left": f"{left[0]}_{left[1]}",
                            "right": f"{right[0]}_{right[1]}",
                            "metric": name,
                            "seed9009_left_minus_right": left_values[0] - right_values[0],
                            "seed9010_left_minus_right": left_values[1] - right_values[1],
                            "seed9011_left_minus_right": left_values[2] - right_values[2],
                            "median_left_minus_right": float(np.median(np.asarray(left_values) - np.asarray(right_values))),
                            "material_direction": direction[name],
                        }
                    )
        nondominated = [config for config in CONFIGS if not any(config in values for values in dominates.values())]
        if not interpretable:
            decision, selected = "inconclusive_seed_instability", None
        elif len(nondominated) != 1:
            decision, selected = "inconclusive_metric_tradeoff", None
        elif nondominated[0] not in interpretable:
            decision, selected = "inconclusive_seed_instability", None
        elif nondominated[0] == ("hourly", "1.00"):
            decision, selected = "default_configuration_retained", nondominated[0]
        elif ("hourly", "1.00") in dominates[nondominated[0]]:
            decision, selected = "preferred_configuration_supported", nondominated[0]
        else:
            decision, selected = "inconclusive_no_unique_preference", None
        write_csv(args.summary_dir / f"{site.lower()}_paired_comparisons.csv", comparison_rows)
        write_csv(args.summary_dir / f"{site.lower()}_paired_metric_audit.csv", audit_rows)
        payload = {
            "schema": "spinup-forcing-coupling-iter015-site-decision-v1",
            "site": site,
            "integrity_pass": True,
            "interpretability_pass": bool(interpretable),
            "eligible_configurations": [f"{item[0]}_{item[1]}" for item in sorted(interpretable)],
            "decision": decision,
            "unique_non_dominated": [f"{item[0]}_{item[1]}" for item in nondominated],
            "selected_configuration": None if selected is None else f"{selected[0]}_{selected[1]}",
        }
        (args.summary_dir / f"{site.lower()}_decision.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        decisions.append(payload)

    write_csv(args.summary_dir / "site_decisions.csv", decisions)
    config_rows = []
    for site in CASES:
        for resolution, scale in CONFIGS:
            selected = [
                row
                for row in combined
                if row["site"] == site and row["resolution"] == resolution and row["de_scale"] == scale
            ]
            config_rows.append(
                {
                    "site": site,
                    "resolution": resolution,
                    "de_scale": scale,
                    **{
                        name: float(np.median([row[name] for row in selected]))
                        for name in (
                            "mean_acceptance",
                            "saturation",
                            "min_steps_per_tau",
                            "abs_resid_lag24",
                            "sigma_upper_edge",
                            "max_cross_seed_width_fraction",
                            "map_rmse",
                            "elm_rmse",
                        )
                    },
                }
            )
    write_csv(args.summary_dir / "six_configuration_site_table.csv", config_rows)

    reported = {}
    for resolution, scale in CONFIGS:
        for site in CASES:
            write_specs_and_plots(
                args.root,
                analysis_root,
                args.forcing_artifact,
                args.spinup_artifact,
                site,
                resolution,
                scale,
            )
            diag = json.loads(
                (experiment_dir(analysis_root, site, resolution, scale) / "mcmc_diagnostics.json").read_text(
                    encoding="utf-8"
                )
            )
            reported[f"{site}_{resolution}_{scale}"] = {
                "max_cross_seed_normalized_wasserstein": diag.get("max_cross_seed_normalized_wasserstein"),
                "max_rank_normalized_split_rhat": diag.get("max_rank_normalized_split_rhat"),
                "min_bulk_ess": diag.get("min_bulk_ess"),
                "min_tail_ess": diag.get("min_tail_ess"),
                "label": diag.get("label"),
            }

    aggregate = {
        "schema": "spinup-forcing-coupling-iter015-aggregate-v1",
        "status": "pass",
        "leaves": 36,
        "decisions": decisions,
        "reported_diagnostics": reported,
        "pool_reuse_policy": "site_hybrid_pool_reuse_v1",
    }
    (analysis_root / "aggregate_result.json").write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    (args.summary_dir / "aggregate_result.json").write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    (analysis_root / "site_decisions.json").write_text(json.dumps(decisions, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Iter015 hybrid-init configuration matrix",
        "",
        "## Integrity",
        "",
        "All 36 immutable packages passed selection-ledger, chain, Jacobian, and plot gates.",
        "",
        "## Site decisions",
        "",
    ]
    for payload in decisions:
        report.append(
            f"- {payload['site']}: `{payload['decision']}`; selected: "
            f"{payload['selected_configuration'] or 'none'}; eligible: "
            f"{', '.join(payload['eligible_configurations']) or 'none'}."
        )
    report += [
        "",
        "## Six-configuration medians",
        "",
        "| Site | Configuration | Acceptance | Saturation | Min steps/tau | Abs lag-24 | Sigma edge | Width | MAP RMSE | ELM RMSE |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in config_rows:
        report.append(
            f"| {row['site']} | {row['resolution']}/{row['de_scale']} | "
            f"{row['mean_acceptance']:.5g} | {row['saturation']:.5g} | "
            f"{row['min_steps_per_tau']:.5g} | {row['abs_resid_lag24']:.5g} | "
            f"{row['sigma_upper_edge']:.5g} | {row['max_cross_seed_width_fraction']:.5g} | "
            f"{row['map_rmse']:.5g} | {row['elm_rmse']:.5g} |"
        )
    report_text = "\n".join(report) + "\n"
    (analysis_root / "ITER015_REPORT.md").write_text(report_text, encoding="utf-8")
    (args.summary_dir / "ITER015_REPORT.md").write_text(report_text, encoding="utf-8")
    print("ANALYSIS_PASS leaves=36")
    for payload in decisions:
        print(
            f"SITE {payload['site']} decision={payload['decision']} "
            f"selected={payload['selected_configuration'] or 'none'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
