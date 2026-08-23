#!/usr/bin/env python3
"""Fail-closed Iter011 campaign integrity, metric, and decision package."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from emcee import backends
from emcee.autocorr import integrated_time
from scipy.stats import wasserstein_distance

import model_ELM  # noqa: F401  # required for historical case pickle loading
from model_ELM.MCMC_forcing import _init_mcmc_worker, log_posterior_forcing, run_forcing_surrogate_site
from model_ELM.coupled_surrogate import prepare_coupled_site_arrays
from model_ELM.load_obs_nc import collocate_obs_to_forcing_time, load_observations_with_time_from_nc
from model_ELM.mcmc_geometry import CoordinateTransform
from model_ELM.surrogate_NN_Forcing import build_forcing_inference_inputs, load_surrogate_forcing_artifacts
from optimize_surrogate_forcing import _complete_day_groups

ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling")
FORCING = ROOT / "spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
SPINUP = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl")
OBS_ROOT = Path("/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4")
CASES = {"ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC", "JERC": "JERC_ppe6_I20TRCNPRDCTCBC"}
CONFIGS = [(resolution, scale) for resolution in ("hourly", "daily") for scale in ("0.50", "0.75", "1.00")]
SEEDS = (9009, 9010, 9011)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing empty table {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def parent(root: Path, resolution: str, scale: str) -> Path:
    return root / f"spinup_forcing_coupling_iter011_{resolution}_scale{scale.replace('.', '')}_campaign"


def leaf_name(site: str, seed: int) -> str:
    n = ("ABBY", "JERC").index(site) * 3 + SEEDS.index(seed) + 1
    return f"leaf_{n:02d}_{site.lower()}_seed{seed}"


def site_payload(repo: Path, site: str) -> tuple[dict, np.ndarray, np.ndarray, dict]:
    """Rebuild precisely the collocated hourly target and coupled predictor input."""
    with (repo / "pklfiles" / f"{CASES[site]}.pkl").open("rb") as handle:
        case = pickle.load(handle)
    artifact = load_surrogate_forcing_artifacts(case, FORCING)
    layout = dict(artifact["training_layout"])
    if dict(case.forcing_surrogate_training) != layout:
        raise ValueError(f"{site}: attached forcing layout differs from locked artifact layout")
    finputs = build_forcing_inference_inputs(case, training_layout=layout)
    obs_payload = load_observations_with_time_from_nc(
        obs_path=str(OBS_ROOT / site / f"{site}_cdo_merge.nc"), myvars=["SR"], obs_err_vars={"SR": "SR_err"}
    )
    obs, obs_err, overlap = collocate_obs_to_forcing_time(
        forcing_time=finputs["forcing_time"], obs_time=obs_payload["time"], obs=obs_payload["obs"],
        obs_err=obs_payload["obs_err"], myvars=["SR"]
    )
    prepared = prepare_coupled_site_arrays(case, spinup_artifact=SPINUP, forcing_artifact=FORCING)
    data = {
        "spinup_mode": "coupled", "spinup_artifact": str(prepared["spinup_artifact_path"]),
        "forcing_artifact": str(prepared["forcing_artifact_path"]), "surface": prepared["surface"],
        "climatology": prepared["climatology"], "forcing_engineered_full": prepared["forcing_engineered_full"],
        "overlap_indices": overlap["forcing_overlap_indices"], "n_params": int(prepared["n_params"]),
        "n_forcing_cols": int(prepared["n_forcing_cols"]), "n_spinup": int(prepared["n_spinup"]),
    }
    times = np.asarray(finputs["forcing_time"]).reshape(-1)[overlap["forcing_overlap_indices"]]
    return data, np.asarray(obs["SR"], float), np.asarray(obs_err["SR"], float), _complete_day_groups(times, obs, obs_err)


def tau(chain: np.ndarray) -> np.ndarray:
    answer = np.array([float(np.ravel(integrated_time(chain[:, :, i], tol=0, quiet=True))[0]) for i in range(15)])
    if not np.all(np.isfinite(answer)) or np.any(answer <= 0):
        raise ValueError("non-finite physical tau")
    return answer


def validate_leaf(repo: Path, root: Path, resolution: str, scale: str, site: str, seed: int, contexts: dict, reference: dict) -> dict:
    leaf = parent(root, resolution, scale) / leaf_name(site, seed)
    required = ("raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json", "backend.h5", "checkpoint_manifest.json")
    if any(not (leaf / name).is_file() for name in required):
        raise FileNotFoundError(f"{leaf}: incomplete immutable raw package")
    diagnostics = ("chain_health.json", "collocation_audit.csv", "log_prob_trace.png", "parameter_chain_health.csv", "posterior_summary.csv", "prior_edge_occupancy.csv", "residual_summary.csv", "skill_table.csv", "walker_acceptance.csv")
    plot_paths = ("plots/corner/corner_plot.png", f"plots/predictions/{site}/Predictions_SR_posterior.png")
    if any(not (leaf / "diagnostics" / name).is_file() for name in diagnostics) or any(not (leaf / name).is_file() for name in plot_paths):
        raise FileNotFoundError(f"{leaf}: required standard diagnostics/plots missing")
    raw = np.load(leaf / "raw_chain.npz", allow_pickle=False)
    required_arrays = {"chain", "sampler_chain", "log_prob", "physical_log_prob", "initial_state", "parameter_names", "pmin", "pmax"}
    if required_arrays - set(raw.files):
        raise ValueError(f"{leaf}: missing raw arrays")
    chain, sampler = np.asarray(raw["chain"], float), np.asarray(raw["sampler_chain"], float)
    logp, physical_logp = np.asarray(raw["log_prob"], float), np.asarray(raw["physical_log_prob"], float)
    pmin, pmax = np.asarray(raw["pmin"], float), np.asarray(raw["pmax"], float)
    names = [str(x) for x in raw["parameter_names"]]
    if names != reference["names"] or not np.array_equal(pmin, reference["pmin"]) or not np.array_equal(pmax, reference["pmax"]):
        raise ValueError(f"{leaf}: cross-package parameter/bounds contract mismatch")
    if any(not (leaf / "plots" / "pdfs" / f"{str(name)}.png").is_file() for name in raw["parameter_names"]) or not (leaf / "diagnostics" / f"residual_{site}_SR.png").is_file():
        raise FileNotFoundError(f"{leaf}: required parameter/residual plot missing")
    if chain.shape != (8000, 64, 15) or sampler.shape != chain.shape or logp.shape != (8000, 64) or physical_logp.shape != logp.shape:
        raise ValueError(f"{leaf}: chain shape contract failure")
    if not all(np.all(np.isfinite(x)) for x in (chain, sampler, logp, physical_logp)) or np.any(chain <= pmin) or np.any(chain >= pmax):
        raise ValueError(f"{leaf}: finite/bounds contract failure")
    metadata = json.loads((leaf / "raw_chain_metadata.json").read_text())
    hashes = json.loads((leaf / "raw_chain_hashes.json").read_text())
    checkpoint = json.loads((leaf / "checkpoint_manifest.json").read_text())
    if metadata.get("schema") != "spinup-forcing-coupling-raw-chain-v2" or metadata.get("sites") != [site] or metadata.get("seed") != seed:
        raise ValueError(f"{leaf}: metadata site/seed/schema mismatch")
    if metadata.get("nwalkers") != 64 or metadata.get("nsteps") != 8000 or metadata.get("move_configuration") != "de_mixture":
        raise ValueError(f"{leaf}: sampler contract mismatch")
    if metadata.get("transform", {}).get("coordinate_system") != "transformed" or metadata.get("parameter_names") != names or metadata.get("transform", {}).get("transform_kinds") != reference["transform_kinds"]:
        raise ValueError(f"{leaf}: transformed parameter-order mismatch")
    if not np.array_equal(np.asarray(metadata.get("pmin"), float), pmin) or not np.array_equal(np.asarray(metadata.get("pmax"), float), pmax):
        raise ValueError(f"{leaf}: metadata bounds mismatch")
    if metadata.get("likelihood_resolution") != resolution or float(metadata.get("de_move_scale")) != float(scale):
        raise ValueError(f"{leaf}: configuration provenance mismatch")
    if hashes.get("raw_chain_sha256") != digest(leaf / "raw_chain.npz") or hashes.get("metadata_sha256") != digest(leaf / "raw_chain_metadata.json") or checkpoint.get("backend_sha256") != digest(leaf / "backend.h5"):
        raise ValueError(f"{leaf}: raw/backend digest mismatch")
    if checkpoint.get("backend_iteration") != 8000 or checkpoint.get("required_steps") != [2000, 4000, 6000, 8000]:
        raise ValueError(f"{leaf}: checkpoint contract mismatch")
    transform = CoordinateTransform.from_parameters([str(x) for x in raw["parameter_names"]], pmin, pmax, enabled=True)
    if not np.allclose(logp - transform.log_abs_det_dphysical_dsampler(sampler), physical_logp, rtol=0, atol=1e-10):
        raise ValueError(f"{leaf}: Jacobian convention mismatch")
    backend = backends.HDFBackend(str(leaf / "backend.h5"), read_only=True)
    if backend.iteration != 8000 or not np.array_equal(backend.get_chain(), sampler) or not np.array_equal(backend.get_log_prob(), logp):
        raise ValueError(f"{leaf}: HDF/raw synchronization failure")
    initial = np.asarray(raw["initial_state"], float)
    bundle = root / "spinup_forcing_coupling_iter009_initialize" / f"{site.lower()}_high_seed{seed}.npz"
    if initial.shape != (64, 15) or not np.all(np.isfinite(initial)) or not bundle.is_file() or not np.array_equal(initial, np.load(bundle, allow_pickle=False)["initial_state"]):
        raise ValueError(f"{leaf}: immutable initialization-bundle mismatch")
    provenance = metadata.get("provenance", {})
    if provenance.get("ITERATION_ID") != "iter011" or provenance.get("SPINUP_MODE") != "coupled" or provenance.get("COUPLED_VARIANT") != "drop21_corr080" or provenance.get("MICROMAMBA_ENV") != "OLMT_puma":
        raise ValueError(f"{leaf}: source/environment provenance mismatch")
    preflight = root / "spinup_forcing_coupling_iter011_preflight"
    if provenance.get("SOURCE_MANIFEST_sha256") != digest(preflight / "source_manifest.sha256") or provenance.get("ARTIFACT_HASH_MANIFEST_sha256") != digest(preflight / "dependency_manifest.sha256") or provenance.get("SUBMISSION_CONFIG_sha256") != digest(parent(root, resolution, scale) / "submission_config.env"):
        raise ValueError(f"{leaf}: locked campaign manifest/config provenance mismatch")
    if resolution == "daily":
        saved = json.loads((leaf / "daily_index_maps.json").read_text()).get("maps", {}).get(site)
        if saved != contexts[site][3]:
            raise ValueError(f"{leaf}: daily map identity mismatch")
    accept = np.genfromtxt(leaf / "diagnostics" / "walker_acceptance.csv", delimiter=",", names=True)["acceptance_fraction"]
    with (leaf / "diagnostics" / "prior_edge_occupancy.csv").open(newline="", encoding="utf-8") as handle:
        sigma_rows = [row for row in csv.DictReader(handle) if row.get("parameter") == "sigma_SR"]
    if len(sigma_rows) != 1:
        raise ValueError(f"{leaf}: sigma_SR edge diagnostic missing or ambiguous")
    sigma_edge = float(sigma_rows[0]["frac_near_upper"])
    if np.asarray(accept).shape != (64,) or not np.all(np.isfinite(accept)) or np.any((accept < 0) | (accept > 1)) or not np.isfinite(sigma_edge) or not 0 <= sigma_edge <= 1:
        raise ValueError(f"{leaf}: acceptance/edge diagnostic malformed")
    best = chain.reshape(-1, 15)[int(np.argmax(physical_logp))]
    data, obs, obs_err, _ = contexts[site]
    _init_mcmc_worker({"sites": [site], "myvars": ["SR"], "pmin": pmin, "pmax": pmax,
                       "obs": {site: {"SR": obs}}, "obs_err": {site: {"SR": obs_err}},
                       "nparms_ensemble": 15, "nerr_parms": 1, "site_data_by_site": {site: data},
                       "likelihood_resolution": resolution,
                       "daily_index_maps": {site: contexts[site][3]} if resolution == "daily" else {}})
    reevaluated = float(log_posterior_forcing(best))
    if not np.isfinite(reevaluated) or not np.isclose(reevaluated, float(np.max(physical_logp)), rtol=0, atol=1e-8):
        raise ValueError(f"{leaf}: reconstructed locked physical target mismatch")
    pred = np.asarray(run_forcing_surrogate_site(data, best[:-1], ["SR"])["SR"], float)
    if pred.shape != obs.shape or not np.all(np.isfinite(pred)):
        raise ValueError(f"{leaf}: reconstructed prediction is non-finite or misaligned")
    mask = (obs > -9000) & (obs_err > 0)
    resid = pred[mask] - obs[mask]
    lag24 = float(np.corrcoef(resid[:-24], resid[24:])[0, 1]) if resid.size > 24 and np.std(resid[:-24]) and np.std(resid[24:]) else float("nan")
    if not np.isfinite(lag24):
        raise ValueError(f"{leaf}: non-finite hourly residual lag-24")
    t6000, t8000 = tau(chain[:6000]), tau(chain)
    return {"site": site, "seed": seed, "resolution": resolution, "de_scale": scale, "leaf": leaf.name,
            "mean_acceptance": float(np.mean(accept)), "saturation": float(np.max(np.mean(np.abs(sampler) >= 10, axis=(0, 1)))),
            "min_steps_per_tau": float(np.min(8000 / t8000)), "max_tau_change": float(np.max(np.abs(t8000 - t6000) / t6000)),
            "abs_resid_lag24": abs(lag24), "sigma_upper_edge": sigma_edge, "raw_chain_sha256": hashes["raw_chain_sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo", type=Path, required=True); parser.add_argument("--root", type=Path, default=ROOT); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False); args.summary.mkdir(parents=True, exist_ok=False)
    contexts = {site: site_payload(args.repo, site) for site in CASES}
    references = {}
    for site in CASES:
        reference_leaf = parent(args.root, "hourly", "1.00") / leaf_name(site, 9009)
        reference_archive = np.load(reference_leaf / "raw_chain.npz", allow_pickle=False)
        reference_metadata = json.loads((reference_leaf / "raw_chain_metadata.json").read_text())
        references[site] = {"names": [str(x) for x in reference_archive["parameter_names"]], "pmin": np.asarray(reference_archive["pmin"], float), "pmax": np.asarray(reference_archive["pmax"], float), "transform_kinds": reference_metadata.get("transform", {}).get("transform_kinds")}
    rows = [validate_leaf(args.repo, args.root, resolution, scale, site, seed, contexts, references[site]) for resolution, scale in CONFIGS for site in CASES for seed in SEEDS]
    if len(rows) != 36: raise ValueError("global 36-leaf completeness failure")
    if not all(np.isfinite(float(row[name])) for row in rows for name in ("mean_acceptance", "saturation", "min_steps_per_tau", "max_tau_change", "abs_resid_lag24", "sigma_upper_edge")):
        raise ValueError("non-finite aggregate decision input")
    # Cross-seed physical posterior distances are configuration/site properties.
    cross_rows = []
    for resolution, scale in CONFIGS:
        for site in CASES:
            archives = [np.load(parent(args.root, resolution, scale) / leaf_name(site, seed) / "raw_chain.npz", allow_pickle=False) for seed in SEEDS]
            chains = [np.asarray(a["chain"], float)[4000:] for a in archives]; widths = np.asarray(archives[0]["pmax"], float) - np.asarray(archives[0]["pmin"], float)
            distance = max(wasserstein_distance(a[:, :, k].ravel(), b[:, :, k].ravel()) / widths[k] for a in chains for b in chains for k in range(15))
            if not np.isfinite(distance): raise ValueError("non-finite cross-seed Wasserstein")
            cross_rows.append({"site": site, "resolution": resolution, "de_scale": scale, "max_cross_seed_width_fraction": float(distance)})
    write_csv(args.output / "leaf_metrics.csv", rows); write_csv(args.output / "cross_seed_wasserstein.csv", cross_rows)
    combined = []
    for row in rows:
        match = next(x for x in cross_rows if all(x[k] == row[k] for k in ("site", "resolution", "de_scale")))
        combined.append({**row, **match})
    write_csv(args.summary / "six_configuration_seed_metrics.csv", combined)
    decisions, report_details = [], []
    for site in CASES:
        site_rows = [row for row in combined if row["site"] == site]
        # Tau stability is candidate-specific interpretability evidence, never an iteration integrity gate.
        interpretable_configs = {(resolution, scale) for resolution, scale in CONFIGS if all(np.isfinite(row["max_tau_change"]) and row["max_tau_change"] <= .20 for row in site_rows if row["resolution"] == resolution and row["de_scale"] == scale)}
        by_config = {(resolution, scale): sorted([r for r in site_rows if r["resolution"] == resolution and r["de_scale"] == scale], key=lambda r: r["seed"]) for resolution, scale in CONFIGS}

        def directed_metric(left, right, name):
            """Return material direction: +1 left improves, -1 worsens, 0 equivalent."""
            a, b = np.asarray([r[name] for r in left], float), np.asarray([r[name] for r in right], float)
            if name == "mean_acceptance":
                a, b, threshold = np.maximum(.20 - a, 0) + np.maximum(a - .50, 0), np.maximum(.20 - b, 0) + np.maximum(b - .50, 0), .03
            elif name == "saturation":
                if np.max(a) <= .05 and np.max(b) <= .05: return 0
                threshold = .10
            elif name == "min_steps_per_tau":
                tiers_a, tiers_b = np.digitize(a, [20., 50.]), np.digitize(b, [20., 50.])
                signs = np.sign(a - b)
                relative = np.abs(a - b) / np.maximum(b, 1e-12)
                if np.all(signs == signs[0]) and signs[0] and (np.any(tiers_a != tiers_b) or np.median(relative) >= .20): return int(signs[0])
                return 0
            elif name == "abs_resid_lag24": threshold = .05
            elif name == "sigma_upper_edge":
                if np.max(a) <= .10 and np.max(b) <= .10: return 0
                threshold = .20
            else:  # cross-seed Wasserstein is a configuration property, not a paired seed statistic.
                av, bv = float(a[0]), float(b[0])
                if (av <= .05 and bv <= .05) or (av > .05 and bv > .05): return 0
                return 1 if av < bv else -1
            # Lower is better except the steps/tau branch above.  Require all paired seeds and material median.
            delta = b - a
            signs = np.sign(delta)
            if np.all(signs == signs[0]) and signs[0] and abs(float(np.median(delta))) >= threshold:
                return int(signs[0])
            return 0

        comparison_rows, audit_rows, dominates = [], [], {config: set() for config in CONFIGS}
        names = ("mean_acceptance", "saturation", "min_steps_per_tau", "max_cross_seed_width_fraction", "abs_resid_lag24", "sigma_upper_edge")
        for left in CONFIGS:
            for right in CONFIGS:
                if left == right: continue
                direction = {name: directed_metric(by_config[left], by_config[right], name) for name in names}
                better, worse = [name for name, value in direction.items() if value > 0], [name for name, value in direction.items() if value < 0]
                if better and not worse: dominates[left].add(right)
                comparison_rows.append({"site": site, "left": f"{left[0]}_{left[1]}", "right": f"{right[0]}_{right[1]}", "improves": ";".join(better), "worsens": ";".join(worse), "dominates": bool(better and not worse)})
                for name in names:
                    left_values, right_values = [float(r[name]) for r in by_config[left]], [float(r[name]) for r in by_config[right]]
                    audit_rows.append({"site": site, "left": f"{left[0]}_{left[1]}", "right": f"{right[0]}_{right[1]}", "metric": name, "seed9009_left_minus_right": left_values[0] - right_values[0], "seed9010_left_minus_right": left_values[1] - right_values[1], "seed9011_left_minus_right": left_values[2] - right_values[2], "median_left_minus_right": float(np.median(np.asarray(left_values) - np.asarray(right_values))), "material_direction": direction[name]})
        nondominated = [config for config in CONFIGS if not any(config in values for values in dominates.values())]
        if not interpretable_configs:
            decision, selected = "inconclusive_seed_instability", None
        elif len(nondominated) != 1:
            decision, selected = "inconclusive_metric_tradeoff", None
        elif nondominated[0] not in interpretable_configs:
            decision, selected = "inconclusive_seed_instability", None
        elif nondominated[0] == ("hourly", "1.00"):
            decision, selected = "default_configuration_retained", nondominated[0]
        elif ("hourly", "1.00") in dominates[nondominated[0]]:
            decision, selected = "preferred_configuration_supported", nondominated[0]
        else:
            decision, selected = "inconclusive_no_unique_preference", None
        write_csv(args.summary / f"{site.lower()}_paired_comparisons.csv", comparison_rows)
        write_csv(args.summary / f"{site.lower()}_paired_metric_audit.csv", audit_rows)
        payload = {"schema": "spinup-forcing-coupling-iter011-site-decision-v1", "site": site, "integrity_pass": True,
                   "interpretability_pass": bool(interpretable_configs), "eligible_configurations": [f"{x[0]}_{x[1]}" for x in sorted(interpretable_configs)], "decision": decision,
                   "unique_non_dominated": [f"{x[0]}_{x[1]}" for x in nondominated],
                   "selected_configuration": None if selected is None else f"{selected[0]}_{selected[1]}"}
        (args.summary / f"{site.lower()}_decision.json").write_text(json.dumps(payload, indent=2) + "\n")
        decisions.append(payload)
        report_details.append({"site": site, "eligible": sorted(interpretable_configs), "comparisons": comparison_rows, "audits": audit_rows, "decision": payload})
    # Compact, fixed-order comparison figures.  Per-chain standard plots remain with their raw leaves.
    for metric in ("mean_acceptance", "saturation", "min_steps_per_tau", "abs_resid_lag24", "sigma_upper_edge", "max_cross_seed_width_fraction"):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
        for axis, site in zip(axes, CASES, strict=True):
            values = [np.median([r[metric] for r in combined if r["site"] == site and r["resolution"] == resolution and r["de_scale"] == scale]) for resolution, scale in CONFIGS]
            axis.bar(range(6), values); axis.set_xticks(range(6), [f"{r[:1]}{s}" for r, s in CONFIGS]); axis.set_title(site); axis.set_ylabel(metric)
        fig.tight_layout(); fig.savefig(args.summary / f"comparison_{metric}.png"); plt.close(fig)
    write_csv(args.summary / "site_decisions.csv", decisions)
    config_rows = []
    for site in CASES:
        for resolution, scale in CONFIGS:
            selected = [row for row in combined if row["site"] == site and row["resolution"] == resolution and row["de_scale"] == scale]
            config_rows.append({"site": site, "resolution": resolution, "de_scale": scale, **{name: float(np.median([row[name] for row in selected])) for name in ("mean_acceptance", "saturation", "min_steps_per_tau", "abs_resid_lag24", "sigma_upper_edge", "max_cross_seed_width_fraction")}})
    write_csv(args.summary / "six_configuration_site_table.csv", config_rows)
    provenance = {"schema": "spinup-forcing-coupling-iter011-aggregation-provenance-v1", "campaign_root": str(args.root), "source_manifest": str(args.root / "spinup_forcing_coupling_iter011_preflight/source_manifest.sha256"), "dependency_manifest": str(args.root / "spinup_forcing_coupling_iter011_preflight/dependency_manifest.sha256"), "leaf_count": 36, "raw_hashes": [row["raw_chain_sha256"] for row in rows], "lag24_method": "locked-MAP coupled prediction minus collocated hourly SR, valid residual correlation at lag 24"}
    (args.summary / "aggregation_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    report = ["# Iter011 aggregate and decision report", "", "## Integrity and provenance", "", "All 36 immutable raw/HDF packages, checkpoint contracts, bundle identities, parameter/transform contracts, daily maps, MAP target re-evaluations, and required leaf diagnostics passed.", "", "## Six-configuration quantitative evidence", "", "| Site | Configuration | Acceptance | Saturation | Min steps/tau | Abs lag-24 | Sigma edge | Max Wasserstein |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    report += [f"| {row['site']} | {row['resolution']}/{row['de_scale']} | {row['mean_acceptance']:.5g} | {row['saturation']:.5g} | {row['min_steps_per_tau']:.5g} | {row['abs_resid_lag24']:.5g} | {row['sigma_upper_edge']:.5g} | {row['max_cross_seed_width_fraction']:.5g} |" for row in config_rows]
    report += ["", "The healthy/material thresholds are fixed in the approved plan: acceptance 0.20–0.50 (0.03 material), saturation ≤0.05 (0.10), steps/tau tier crossing or 20%, lag-24 0.05, sigma edge 0.20, and Wasserstein threshold crossing at 0.05. Seed-level signs, medians, and material directions are preserved in the paired audit CSVs.", "", "## Decisions and route", ""]
    report += [f"- {row['site']}: `{row['decision']}`; eligible configurations: {', '.join(row['eligible_configurations']) or 'none'}; non-dominated: {', '.join(row['unique_non_dominated']) or 'none'}; selected: {row['selected_configuration'] or 'none'}." for row in decisions]
    report += ["", "## Site-specific rationale", ""]
    for detail in report_details:
        site = detail["site"]; decision = detail["decision"]
        eligible = {f"{x[0]}_{x[1]}" for x in detail["eligible"]}
        unstable = [f"{r}_{s}" for r, s in CONFIGS if f"{r}_{s}" not in eligible]
        dominant = [f"{row['left']} dominates {row['right']} by {row['improves']}" for row in detail["comparisons"] if row["dominates"]]
        adverse = [f"{row['left']} vs {row['right']} worsens {row['worsens']}" for row in detail["comparisons"] if row["worsens"]]
        favorable = dominant[:6] or ["No material no-regression dominance relation was observed."]
        unfavorable = adverse[:6] or ["No material adverse relation was observed in the audited comparisons."]
        route = ("A supported configuration is evidence for a future site-specific production proposal only; no production run is authorized." if decision["decision"] == "preferred_configuration_supported" else "Retain the default only as the current bounded-pilot conclusion; any next diagnostic or production proposal requires fresh approval.")
        report += [f"### {site}", "", f"Tau-stable configurations: {', '.join(sorted(eligible)) or 'none'}.", f"Tau-unstable configurations: {', '.join(unstable) or 'none'}.", f"Outcome: `{decision['decision']}`. {route}", "", "Favorable evidence:"]
        report += [f"- {item}." for item in favorable]
        report += ["", "Adverse or limiting evidence:"]
        report += [f"- {item}." for item in unfavorable]
        report += ["", "The paired metric audit records every seed-level signed difference and median used for the all-three-seed/no-material-opposite rule.", ""]
    report += ["", "## Interpretation, limitations, and route", "", "Sampler metrics are interpretability evidence, not iteration-integrity gates. A lack of a supported unique non-dominated configuration is an inconclusive result rather than evidence of scientific equivalence. Residual lag-24 is evaluated on hourly predictions for both likelihood resolutions; it does not turn the daily target into an hourly target.", "", "## Next experiment", "", "No follow-up execution is authorized here. Any production or narrower diagnostic proposal requires a new consolidated kickoff approval."]
    (args.summary / "ITER011_REPORT.md").write_text("\n".join(report) + "\n")
    (args.output / "aggregate_result.json").write_text(json.dumps({"schema": "spinup-forcing-coupling-iter011-aggregate-v1", "leaves": rows, "decisions": decisions}, indent=2) + "\n")
    print("AGGREGATE_PASS leaves=36")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
