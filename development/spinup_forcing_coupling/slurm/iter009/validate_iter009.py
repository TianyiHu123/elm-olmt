#!/usr/bin/env python3
"""Fail-closed integrity validator for the 30 locked Iter009 campaign leaves."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm, rankdata, wasserstein_distance
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_ELM.mcmc_geometry import CoordinateTransform


ARMS = {
    "B": ("physical", "uniform", "stretch"),
    "T": ("transformed", "uniform", "stretch"),
    "I": ("physical", "high", "stretch"),
    "M": ("physical", "uniform", "de_mixture"),
    "TIM": ("transformed", "high", "de_mixture"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(matrix: Path):
    lines = matrix.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"), strict=True)) for line in lines[1:]]


def _tau(chain: np.ndarray) -> np.ndarray:
    """Return physical-coordinate integrated times, failing closed when unavailable."""
    from emcee.autocorr import integrated_time

    values = []
    for index in range(chain.shape[-1]):
        result = np.asarray(integrated_time(chain[:, :, index], tol=0, quiet=True), dtype=float)
        values.append(float(np.ravel(result)[0]))
    answer = np.asarray(values, dtype=float)
    if answer.shape != (15,) or not np.all(np.isfinite(answer)) or np.any(answer <= 0):
        raise ValueError("non-finite physical-coordinate autocorrelation time")
    return answer


def _split_rhat(values: np.ndarray) -> float:
    """Rank-normalized split R-hat screening statistic for walker trajectories."""
    nstep, nwalker = values.shape
    half = nstep // 2
    if half < 4:
        raise ValueError("too few steps for split R-hat")
    split = np.concatenate((values[:half].T, values[-half:].T), axis=0)
    ranked = rankdata(split, method="average").reshape(split.shape)
    normalized = norm.ppf((ranked - 0.375) / (ranked.size + 0.25))
    means = normalized.mean(axis=1)
    within = normalized.var(axis=1, ddof=1).mean()
    between = half * means.var(ddof=1)
    variance = (half - 1.0) * within / half + between / half
    return float(np.sqrt(variance / within)) if within > 0 else float("inf")


def _terminal_bands(log_prob: np.ndarray) -> tuple[int, float]:
    """Deterministic 1-D two-means terminal-band screen over walker medians."""
    points = np.median(log_prob[-1000:], axis=0)
    lower, upper = float(np.min(points)), float(np.max(points))
    for _ in range(32):
        midpoint = 0.5 * (lower + upper)
        labels = points > midpoint
        if not labels.any() or labels.all():
            return 0, 0.0
        lower_next, upper_next = float(points[~labels].mean()), float(points[labels].mean())
        if np.isclose(lower, lower_next) and np.isclose(upper, upper_next):
            break
        lower, upper = lower_next, upper_next
    labels = points > 0.5 * (lower + upper)
    counts = min(int((~labels).sum()), int(labels.sum()))
    if counts == 0:
        return 0, 0.0
    distances_same = np.where(labels, np.abs(points - upper), np.abs(points - lower))
    distances_other = np.where(labels, np.abs(points - lower), np.abs(points - upper))
    denominator = np.maximum(np.maximum(distances_same, distances_other), 1e-12)
    silhouette = float(np.mean((distances_other - distances_same) / denominator))
    return counts, silhouette


def _write_csv(path: Path, fieldnames: list[str], entries: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)


def validate_leaf(parent: Path, row: dict[str, str], arm: str) -> dict[str, object]:
    leaf = parent / row["leaf_id"]
    expected_coordinates, expected_initialization, expected_move = ARMS[arm]
    if (row["arm"], row["coordinates"], row["initialization"], row["move"]) != (
        arm, expected_coordinates, expected_initialization, expected_move
    ):
        raise ValueError(f"{leaf}: matrix arm contract mismatch")
    for name in ("raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json", "backend.h5", "checkpoint_manifest.json"):
        if not (leaf / name).is_file():
            raise FileNotFoundError(f"{leaf}: missing {name}")
    for name in ("chain_health.json", "walker_acceptance.csv", "parameter_chain_health.csv", "log_prob_trace.txt", "log_prob_trace.png", "prior_edge_occupancy.csv"):
        if not (leaf / "diagnostics" / name).is_file():
            raise FileNotFoundError(f"{leaf}: missing diagnostics/{name}")
    archive = np.load(leaf / "raw_chain.npz", allow_pickle=False)
    required = {"chain", "sampler_chain", "log_prob", "physical_log_prob", "initial_state", "parameter_names", "pmin", "pmax"}
    if required - set(archive.files):
        raise ValueError(f"{leaf}: raw archive lacks {sorted(required - set(archive.files))}")
    physical = np.asarray(archive["chain"], dtype=float)
    sampler = np.asarray(archive["sampler_chain"], dtype=float)
    sampler_logp = np.asarray(archive["log_prob"], dtype=float)
    physical_logp = np.asarray(archive["physical_log_prob"], dtype=float)
    initial = np.asarray(archive["initial_state"], dtype=float)
    pmin = np.asarray(archive["pmin"], dtype=float)
    pmax = np.asarray(archive["pmax"], dtype=float)
    if physical.shape != (8000, 64, 15) or sampler.shape != physical.shape:
        raise ValueError(f"{leaf}: locked chain shape mismatch: {physical.shape}, {sampler.shape}")
    if sampler_logp.shape != (8000, 64) or physical_logp.shape != sampler_logp.shape:
        raise ValueError(f"{leaf}: locked log-probability shape mismatch")
    if initial.shape != (64, 15) or pmin.shape != (15,) or pmax.shape != (15,):
        raise ValueError(f"{leaf}: initialization or bounds shape mismatch")
    if not all(np.all(np.isfinite(value)) for value in (physical, sampler, sampler_logp, physical_logp, initial)):
        raise ValueError(f"{leaf}: non-finite chain evidence")
    if np.any(physical <= pmin) or np.any(physical >= pmax):
        raise ValueError(f"{leaf}: physical chain violates strict bounds")
    names = [str(name) for name in archive["parameter_names"]]
    transform = CoordinateTransform.from_parameters(names, pmin, pmax, enabled=(row["coordinates"] == "transformed"))
    if not np.allclose(
        sampler_logp - transform.log_abs_det_dphysical_dsampler(sampler), physical_logp, rtol=0, atol=1.0e-10
    ):
        raise ValueError(f"{leaf}: sampler/physical log-probability Jacobian mismatch")
    bundle = parent.parent / "spinup_forcing_coupling_iter009_initialize" / f"{row['site'].lower()}_{row['initialization']}_seed{row['mcmc_seed']}.npz"
    if not bundle.is_file() or not np.array_equal(initial, np.load(bundle, allow_pickle=False)["initial_state"]):
        raise ValueError(f"{leaf}: initial state does not match immutable initialization bundle")
    metadata = json.loads((leaf / "raw_chain_metadata.json").read_text(encoding="utf-8"))
    hashes = json.loads((leaf / "raw_chain_hashes.json").read_text(encoding="utf-8"))
    checkpoint = json.loads((leaf / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    if metadata.get("schema") != "spinup-forcing-coupling-raw-chain-v2":
        raise ValueError(f"{leaf}: unexpected raw metadata schema")
    if metadata.get("sites") != [row["site"]] or metadata.get("seed") != int(row["mcmc_seed"]):
        raise ValueError(f"{leaf}: site/seed provenance mismatch")
    if metadata.get("move_configuration") != row["move"]:
        raise ValueError(f"{leaf}: move provenance mismatch")
    if metadata.get("transform", {}).get("coordinate_system") != row["coordinates"]:
        raise ValueError(f"{leaf}: coordinate provenance mismatch")
    if hashes.get("raw_chain_sha256") != sha256(leaf / "raw_chain.npz"):
        raise ValueError(f"{leaf}: raw archive checksum mismatch")
    if checkpoint.get("backend_iteration") != 8000 or checkpoint.get("required_steps") != [2000, 4000, 6000, 8000]:
        raise ValueError(f"{leaf}: checkpoint contract mismatch")
    if checkpoint.get("backend_sha256") != sha256(leaf / "backend.h5"):
        raise ValueError(f"{leaf}: HDF checksum mismatch")
    return {"arm": arm, "leaf": row["leaf_id"], "site": row["site"], "seed": int(row["mcmc_seed"]), "status": "pass"}


def evaluate_site_arm(root: Path, arm: str, site: str, entries: list[dict[str, object]], output: Path) -> dict[str, object]:
    """Build the declared three-seed package and its immutable qualification result."""
    parent = root / f"spinup_forcing_coupling_iter009_{arm.lower()}_campaign"
    leaves = [parent / str(entry["leaf"]) for entry in entries]
    archives = [np.load(leaf / "raw_chain.npz", allow_pickle=False) for leaf in leaves]
    chains = [np.asarray(archive["chain"], dtype=float) for archive in archives]
    sampler_chains = [np.asarray(archive["sampler_chain"], dtype=float) for archive in archives]
    physical_log_probs = [np.asarray(archive["physical_log_prob"], dtype=float) for archive in archives]
    names = [str(name) for name in archives[0]["parameter_names"]]
    widths = np.asarray(archives[0]["pmax"], dtype=float) - np.asarray(archives[0]["pmin"], dtype=float)
    taus_6000 = [_tau(chain[:6000]) for chain in chains]
    taus_8000 = [_tau(chain) for chain in chains]
    tau_relative_change = [np.abs(final - earlier) / earlier for earlier, final in zip(taus_6000, taus_8000, strict=True)]
    rhat = np.asarray([[_split_rhat(chain[:, :, index]) for index in range(15)] + [_split_rhat(logp)] for chain, logp in zip(chains, physical_log_probs, strict=True)], dtype=float)
    terminal = [_terminal_bands(logp) for logp in physical_log_probs]
    acceptance = []
    low_acceptance = []
    for leaf in leaves:
        values = np.genfromtxt(leaf / "diagnostics" / "walker_acceptance.csv", delimiter=",", names=True)
        fractions = np.atleast_1d(values["acceptance_fraction"]).astype(float)
        acceptance.append(float(np.mean(fractions)))
        low_acceptance.append(int(np.count_nonzero(fractions < 0.10)))
    distances = np.zeros((3, 3, 15), dtype=float)
    for left in range(3):
        for right in range(left + 1, 3):
            for index in range(15):
                distances[left, right, index] = distances[right, left, index] = wasserstein_distance(
                    chains[left][4000:, :, index].ravel(), chains[right][4000:, :, index].ravel()
                )
    max_distance_ratio = float(np.max(distances / widths[None, None, :]))
    parameter_rows = []
    for index, name in enumerate(names):
        parameter_rows.append({
            "parameter": name,
            "max_tau_8000": float(max(tau[index] for tau in taus_8000)),
            "max_relative_tau_change": float(max(change[index] for change in tau_relative_change)),
            "min_steps_per_tau": float(min(8000.0 / tau[index] for tau in taus_8000)),
            "max_split_rhat": float(np.max(rhat[:, index])),
            "max_cross_seed_wasserstein": float(np.max(distances[:, :, index])),
            "max_cross_seed_width_fraction": float(np.max(distances[:, :, index]) / widths[index]),
        })
    _write_csv(output / "parameter_metrics.csv", list(parameter_rows[0]), parameter_rows)
    saturation_rows = []
    for index, name in enumerate(names):
        saturation_rows.append({
            "parameter": name,
            "max_abs_sampler_coordinate": float(max(np.max(np.abs(chain[:, :, index])) for chain in sampler_chains)),
            "max_fraction_abs_coordinate_ge_10": float(max(np.mean(np.abs(chain[:, :, index]) >= 10.0) for chain in sampler_chains)),
        })
    _write_csv(output / "transformed_coordinate_saturation.csv", list(saturation_rows[0]), saturation_rows)
    np.savez_compressed(output / "tau_trajectories.npz", tau_6000=np.asarray(taus_6000), tau_8000=np.asarray(taus_8000))
    np.savez_compressed(output / "cross_seed_wasserstein.npz", distance=distances, parameter_names=np.asarray(names))
    plt.figure(figsize=(9, 4))
    for chain, entry in zip(chains, entries, strict=True):
        plt.plot(np.median(chain[:, :, 0], axis=1), linewidth=0.7, label=f"seed {entry['seed']}")
    plt.legend(); plt.xlabel("step"); plt.ylabel(names[0]); plt.tight_layout()
    plt.savefig(output / "overlaid_seed_trace.png"); plt.close()
    plt.figure(figsize=(9, 4))
    for chain, entry in zip(chains, entries, strict=True):
        plt.hist(chain[4000:, :, 0].ravel(), bins=60, density=True, histtype="step", label=f"seed {entry['seed']}")
    plt.legend(); plt.xlabel(names[0]); plt.ylabel("density"); plt.tight_layout()
    plt.savefig(output / "overlaid_seed_marginal.png"); plt.close()
    qualified = (
        all(0.20 <= value <= 0.50 for value in acceptance)
        and max(low_acceptance) <= 6
        and np.all(np.isfinite(taus_8000))
        and max(float(np.max(change)) for change in tau_relative_change) <= 0.20
        and min(float(np.min(8000.0 / tau)) for tau in taus_8000) >= 20.0
        and float(np.max(rhat)) <= 1.05
        and not any(count >= 7 and silhouette >= 0.5 for count, silhouette in terminal)
        and max_distance_ratio <= 0.05
    )
    payload = {
        "schema": "spinup-forcing-coupling-iter009-site-arm-v1", "arm": arm, "site": site,
        "seeds": [int(entry["seed"]) for entry in entries], "mean_acceptance": acceptance,
        "low_acceptance_walkers": low_acceptance, "tau_6000": [tau.tolist() for tau in taus_6000],
        "tau_8000": [tau.tolist() for tau in taus_8000], "max_split_rhat": float(np.max(rhat)),
        "terminal_bands": [{"smallest_band": count, "silhouette": silhouette} for count, silhouette in terminal],
        "max_cross_seed_width_fraction": max_distance_ratio, "geometry_qualified": qualified,
    }
    (output / "site_arm_decision.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"arm": arm, "site": site, **payload}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--summary-root", required=True, type=Path)
    args = parser.parse_args()
    results = []
    for arm in ARMS:
        parent = args.root / f"spinup_forcing_coupling_iter009_{arm.lower()}_campaign"
        matrix = parent / "matrix.tsv"
        if not matrix.is_file():
            raise FileNotFoundError(f"missing {matrix}")
        arm_rows = rows(matrix)
        if len(arm_rows) != 6:
            raise ValueError(f"{matrix}: expected six leaves")
        results.extend(validate_leaf(parent, row, arm) for row in arm_rows)
    if len(results) != 30 or len({entry["leaf"] + entry["arm"] for entry in results}) != 30:
        raise ValueError("global Iter009 leaf completeness/uniqueness failure")
    validate_root = args.root / "spinup_forcing_coupling_iter009_validate"
    package_root = validate_root / "site_arm_packages"
    package_root.mkdir(parents=True, exist_ok=False)
    packages = []
    for arm in ARMS:
        for site in ("ABBY", "JERC"):
            selected = [entry for entry in results if entry["arm"] == arm and entry["site"] == site]
            if len(selected) != 3:
                raise ValueError(f"{arm}/{site}: expected three seed results")
            package = package_root / f"{arm.lower()}_{site.lower()}"
            package.mkdir()
            packages.append(evaluate_site_arm(args.root, arm, site, selected, package))
    # The kickoff materializes the repository-owned summary directory.  It is
    # safe to reuse only when it is empty; never overwrite a prior evaluation.
    if args.summary_root.exists():
        if not args.summary_root.is_dir() or any(args.summary_root.iterdir()):
            raise FileExistsError(f"refusing to overwrite nonempty {args.summary_root}")
    else:
        args.summary_root.mkdir(parents=True)
    matrix_rows = [{"arm": package["arm"], "site": package["site"], "geometry_qualified": package["geometry_qualified"], "max_split_rhat": package["max_split_rhat"], "max_cross_seed_width_fraction": package["max_cross_seed_width_fraction"]} for package in packages]
    _write_csv(args.summary_root / "qualification_matrix.csv", list(matrix_rows[0]), matrix_rows)
    arm_packages = {arm: [package for package in packages if package["arm"] == arm] for arm in ARMS}
    arm_qualified = {arm: all(package["geometry_qualified"] for package in arm_packages[arm]) for arm in ARMS}
    candidates = [arm for arm in ARMS if arm_qualified[arm]]
    simplicity = {arm: index for index, arm in enumerate(("B", "M", "T", "I", "TIM"))}
    def arm_key(arm: str) -> tuple[float, float, float, int]:
        group = arm_packages[arm]
        worst_tau = max(max(max(row) for row in package["tau_8000"]) for package in group)
        worst_rhat = max(float(package["max_split_rhat"]) for package in group)
        worst_distance = max(float(package["max_cross_seed_width_fraction"]) for package in group)
        return (float(worst_tau), worst_rhat, worst_distance, simplicity[arm])
    selected = None
    selection_key = None
    if candidates:
        best_tau = min(arm_key(arm)[0] for arm in candidates)
        tau_tied = [arm for arm in candidates if arm_key(arm)[0] < 1.10 * best_tau]
        selected = min(tau_tied, key=lambda arm: arm_key(arm)[1:])
        selection_key = arm_key(selected)
    route = "geometry-qualified-arm-selected" if selected else "investigate_multimodality_nonidentifiability_likelihood_or_model_structure"
    decision = {
        "schema": "spinup-forcing-coupling-iter009-decision-v1", "packages": packages,
        "arm_qualified": arm_qualified, "selected_arm": selected, "route": route,
        "selection_key": selection_key,
        "attribution": None if selected is None else {
            "B": "default_geometry_or_run_length", "T": "scaling_or_bound_geometry", "I": "initialization_or_burn_in", "M": "proposal_limitation", "TIM": "interaction"
        }[selected],
    }
    selection_rows = []
    for arm in ARMS:
        key = arm_key(arm)
        selection_rows.append({
            "arm": arm, "geometry_qualified": arm_qualified[arm], "worst_tau": key[0],
            "worst_split_rhat": key[1], "worst_wasserstein_width_fraction": key[2],
            "simplicity_rank": key[3], "selected": arm == selected,
        })
    _write_csv(args.summary_root / "worst_case_selection.csv", list(selection_rows[0]), selection_rows)
    report = [
        "# Iter009 sampler-geometry qualification report", "",
        f"Decision route: `{route}`", f"Selected arm: `{selected or 'none'}`", "",
        "## Immutable qualification matrix", "",
        "| Arm | Site | Qualified | Worst split R-hat | Worst cross-seed width fraction |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for package in packages:
        report.append(
            f"| {package['arm']} | {package['site']} | {package['geometry_qualified']} | "
            f"{package['max_split_rhat']:.6g} | {package['max_cross_seed_width_fraction']:.6g} |"
        )
    report.extend([
        "", "## Interpretation", "",
        "All geometry statistics use the physical posterior. Split R-hat is a screening statistic "
        "because ensemble walkers interact; nominal unthinned ESS is reported per leaf and is not "
        "an independent qualification gate. Boundary and transformed-coordinate saturation are "
        "report-only evidence. No likelihood, skill, or predictive metric participates in selection.",
        "",
    ])
    (args.summary_root / "ITER009_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    (validate_root / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    (args.summary_root / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    output = validate_root / "validation_result.json"
    output.write_text(json.dumps({"schema": "spinup-forcing-coupling-iter009-validation-v1", "leaves": results, "packages": packages}, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATE_PASS leaves={len(results)} packages={len(packages)} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
