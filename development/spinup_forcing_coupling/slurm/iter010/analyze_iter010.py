#!/usr/bin/env python3
"""Deterministic Iter010 TIM topology analysis.

This utility is intentionally self-contained: it reads only the six locked Iter009
archives, writes compact evidence to the requested output directory, and never changes
the source archives or evaluates a constructed parameter vector.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import linalg, stats

PARAMS = ["k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag",
          "rf_l1s1", "rf_l2s2", "rf_l3s3", "rf_s1s2", "rf_s2s3", "rf_s3s4", "sigma_SR"]
SITES = ("ABBY", "JERC")
SEEDS = (9009, 9010, 9011)
WINDOWS = (500, 1000, 2000, 4000)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def assign_two(values: np.ndarray) -> np.ndarray:
    """Deterministic two-means assignment, labels always lower then higher."""
    x = np.asarray(values, dtype=float)
    c = np.array([np.min(x), np.max(x)], dtype=float)
    for _ in range(100):
        lab = np.abs(x[:, None] - c[None, :]).argmin(axis=1)
        new = np.array([x[lab == j].mean() if np.any(lab == j) else c[j] for j in range(2)])
        if np.allclose(new, c, rtol=0, atol=1e-14):
            break
        c = new
    order = np.argsort(c)
    return np.where(lab == order[0], 0, 1).astype(int)


def load_source(path: Path, expected: dict) -> dict:
    meta_path = Path(expected["metadata"])
    meta = json.loads(meta_path.read_text())
    z = np.load(path, allow_pickle=False)
    chain = np.asarray(z["chain"], dtype=float)
    physical_logp = np.asarray(z["physical_log_prob"], dtype=float)
    names = [str(x) for x in z["parameter_names"].tolist()]
    if chain.shape != (8000, 64, 15) or physical_logp.shape != (8000, 64):
        raise ValueError(f"wrong source shape {path}: {chain.shape} {physical_logp.shape}")
    if names != PARAMS or not np.isfinite(chain).all() or not np.isfinite(physical_logp).all():
        raise ValueError(f"source schema/finiteness failure: {path}")
    pmin, pmax = np.asarray(z["pmin"], float), np.asarray(z["pmax"], float)
    if not np.all(chain >= pmin) or not np.all(chain <= pmax):
        raise ValueError(f"source bounds failure: {path}")
    for key, hash_key in (("raw_chain", "raw_sha256"), ("backend", "backend_sha256"), ("metadata", "metadata_sha256"), ("checkpoint", "checkpoint_sha256"), ("selection", "selection_sha256")):
        if sha256(Path(expected[key])) != expected[hash_key]:
            raise ValueError(f"locked provenance hash changed: {expected[key]}")
    if sha256(path) != expected["raw_sha256"]:
        raise ValueError(f"locked raw archive hash changed: {path}")
    if meta["seed"] != expected["seed"] or meta["sites"] != [expected["site"]]:
        raise ValueError(f"locked site/seed provenance changed: {path}")
    return {"path": str(path), "chain": chain, "logp": physical_logp,
            "pmin": pmin, "pmax": pmax, "meta": meta,
            "raw_sha256": sha256(path), "meta_sha256": sha256(meta_path)}


def draws(chain: np.ndarray) -> np.ndarray:
    idx = np.linspace(4000, 7999, 32, dtype=int)
    return chain[idx, :, :].reshape(-1, chain.shape[-1])


def pca_xy(x: np.ndarray) -> np.ndarray:
    y = x - np.mean(x, axis=0)
    u, _, _ = linalg.svd(y, full_matrices=False)
    return u[:, :2] * np.sqrt(max(y.shape[0] - 1, 1))


def gmm_bic(x: np.ndarray, k: int) -> float:
    x = np.asarray(x, float).reshape(-1, 1)
    if k == 1:
        mu, var = float(x.mean()), float(x.var() + 1e-12)
        ll = np.sum(stats.norm.logpdf(x[:, 0], mu, math.sqrt(var)))
        npar = 2
    else:
        labels = assign_two(x[:, 0])
        mus = np.array([x[labels == j].mean() for j in (0, 1)])
        vars_ = np.array([x[labels == j].var() + 1e-12 for j in (0, 1)])
        weights = np.array([(labels == j).mean() for j in (0, 1)])
        dens = sum(weights[j] * stats.norm.pdf(x[:, 0], mus[j], np.sqrt(vars_[j])) for j in (0, 1))
        ll = np.log(np.maximum(dens, 1e-300)).sum()
        npar = 5
    return float(npar * np.log(len(x)) - 2 * ll)


def chain_metrics(src: dict, site: str, seed: int, out: Path) -> dict:
    chain, logp = src["chain"], src["logp"]
    medians = np.median(logp[7000:8000], axis=0)
    ref = assign_two(medians)
    metrics = {"site": site, "seed": seed, "source": src["path"],
               "raw_sha256": src["raw_sha256"], "metadata_sha256": src["meta_sha256"],
               "shape": list(chain.shape), "windows": {}, "reference_group_sizes": [int((ref == j).sum()) for j in (0, 1)]}
    for w in WINDOWS:
        m = np.median(logp[-w:], axis=0)
        lab = assign_two(m)
        metrics["windows"][str(w)] = {"group_sizes": [int((lab == j).sum()) for j in (0, 1)],
                                       "assignment_agreement_reference": float((lab == ref).mean()),
                                       "centers": [float(m[lab == j].mean()) for j in (0, 1)],
                                       "gap": float(m[lab == 1].min() - m[lab == 0].max())}
    lab2, lab4 = assign_two(np.median(logp[-2000:], axis=0)), ref
    late_a, late_b = chain[4000:6000].reshape(-1, 15), chain[6000:8000].reshape(-1, 15)
    x = draws(chain)
    norm = (x - src["pmin"]) / (src["pmax"] - src["pmin"])
    grp_x = chain[7000:8000].mean(axis=0)
    gmeans = np.array([grp_x[ref == j].mean(axis=0) for j in (0, 1)])
    gmeans_n = (gmeans - src["pmin"]) / (src["pmax"] - src["pmin"])
    centroid_distance = float(np.linalg.norm(gmeans_n[1] - gmeans_n[0]))
    all_terminal = chain[7000:8000].reshape(-1, 15)
    all_norm = (all_terminal - src["pmin"]) / (src["pmax"] - src["pmin"])
    # Fixed, predeclared supporting classifications; these are routing evidence, not vetoes.
    scalar = metrics["windows"]["2000"]
    scalar_support = bool(gmm_bic(medians, 2) + 10 < gmm_bic(medians, 1) and scalar["gap"] > 0)
    classifier_labels = np.tile(ref, 1000)
    classifier_acc = float(np.mean((((all_norm - gmeans_n[0]) ** 2).sum(1) < ((all_norm - gmeans_n[1]) ** 2).sum(1)) == classifier_labels))
    multivariate_support = bool(centroid_distance >= 1.0 and classifier_acc >= 0.90)
    temporal_agreement = float((lab2 == lab4).mean())
    occ_delta = abs(float((lab2 == 1).mean()) - float((assign_two(np.median(logp[4000:6000], axis=0)) == 1).mean()))
    temporal_support = bool(temporal_agreement >= 0.90 and occ_delta <= 0.10)
    metrics.update({"gmm_bic_1": gmm_bic(medians, 1), "gmm_bic_2": gmm_bic(medians, 2),
                    "classifier_accuracy": classifier_acc, "centroid_distance_prior_normalized": centroid_distance,
                    "temporal_assignment_agreement_2000_4000": temporal_agreement,
                    "late_occupancy_delta": occ_delta,
                    "requirements": {"scalar_separation": "support" if scalar_support else "oppose",
                                      "multivariate_separation": "support" if multivariate_support else "oppose",
                                      "temporal_persistence": "support" if temporal_support else "oppose",
                                      "reproducible_group_locations": "ambiguous"},
                    "reference_assignment": ref.tolist(), "group_means_normalized": gmeans_n.tolist(),
                    "standardized_group_differences": ((gmeans_n[1] - gmeans_n[0]) / (np.std(norm, axis=0) + 1e-12)).tolist(),
                    "kde_bandwidth_sensitivity": {"0.5x": float(stats.gaussian_kde(medians, bw_method=0.5).factor), "1.0x": float(stats.gaussian_kde(medians).factor), "2.0x": float(stats.gaussian_kde(medians, bw_method=2.0).factor)}})
    np.savez_compressed(out / f"{site.lower()}_seed{seed}_metrics.npz", reference_assignment=ref,
                        terminal_medians=medians, normalized_draws=norm)

    fig, ax = plt.subplots(figsize=(10, 4)); ax.plot(logp, lw=.15, alpha=.45, color="0.35")
    for j, c in enumerate(("tab:blue", "tab:orange")):
        ax.plot(logp[:, ref == j], lw=.15, alpha=.55, color=c)
    ax.set(title=f"{site} seed {seed}: physical log-posterior traces", xlabel="step", ylabel="log posterior"); fig.tight_layout(); fig.savefig(out / f"{site.lower()}_seed{seed}_01_traces.png", dpi=150); plt.close(fig)
    order = np.argsort(medians); fig, (ax, rug) = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw={"height_ratios":[3,1]}); ax.plot(medians[order], ".-", ms=2); ax.axvline((ref[order] == 0).sum() - .5, color="k", ls="--"); ax.set(title="Sorted terminal walker medians; forced threshold and density", ylabel="median physical log posterior"); rug.hist(medians[ref == 0], bins=20, alpha=.5, color="tab:blue", density=True); rug.hist(medians[ref == 1], bins=20, alpha=.5, color="tab:orange", density=True); rug.set_xlabel("terminal median; histogram/rug density"); fig.tight_layout(); fig.savefig(out / f"{site.lower()}_seed{seed}_02_terminal.png", dpi=150); plt.close(fig)
    sample = draws(chain); sample_lab = np.tile(ref, 32); fig, axes = plt.subplots(15, 15, figsize=(18, 18));
    for i in range(15):
        for j in range(15):
            ax = axes[i, j]
            if i == j:
                for g, c in enumerate(("tab:blue", "tab:orange")): ax.hist(sample[sample_lab == g, i], bins=18, density=True, alpha=.45, color=c)
            elif i > j:
                for g, c in enumerate(("tab:blue", "tab:orange")): ax.scatter(sample[sample_lab == g, j], sample[sample_lab == g, i], s=.2, alpha=.12, color=c)
            else: ax.axis("off")
            if i == 14: ax.set_xlabel(PARAMS[j], fontsize=5, rotation=90)
            if j == 0 and i > 0: ax.set_ylabel(PARAMS[i], fontsize=5)
            ax.tick_params(labelsize=3)
    fig.suptitle(f"{site} seed {seed}: physical-parameter corner, terminal colors"); fig.tight_layout(); fig.savefig(out / f"{site.lower()}_seed{seed}_03_corner.png", dpi=120); plt.close(fig)
    xy = pca_xy(norm); fig, ax = plt.subplots(figsize=(7, 5)); colors = np.where(np.tile(ref, 32), "tab:orange", "tab:blue"); ax.scatter(xy[:, 0], xy[:, 1], s=1, alpha=.18, c=colors)
    for wkr in range(64):
        wi = np.arange(wkr, len(sample), 64); ax.plot(xy[wi, 0], xy[wi, 1], color=colors[wkr], alpha=.18, lw=.35)
    ax.set(title="Prior-width-normalized PCA; 2048 draws and intermediate trajectories", xlabel="PC1", ylabel="PC2"); fig.tight_layout(); fig.savefig(out / f"{site.lower()}_seed{seed}_04_pca.png", dpi=150); plt.close(fig)
    starts = list(range(4000, 8000 - 1000 + 1, 250)); rolling = np.vstack([assign_two(np.median(logp[s:s+1000], axis=0)) for s in starts]); occ = [float((a == 1).mean()) for a in rolling]; transitions = [int(np.count_nonzero(a[1:] != a[:-1])) for a in rolling]
    runs=[]
    for wkr in range(64):
        seq=rolling[:,wkr]; lengths=[]; run=1
        for prev, cur in zip(seq[:-1], seq[1:]):
            if cur == prev: run += 1
            else: lengths.append(run); run=1
        lengths.append(run); runs.extend(lengths)
    metrics.update({"transition_count": int(np.sum(np.abs(np.diff(rolling, axis=0)))), "residence_time_max_windows": int(max(runs)), "residence_time_median_windows": float(np.median(runs))})
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(8, 6), sharex=False); ax.plot(starts, occ, "o-", label="high-group occupancy"); ax2=ax.twinx(); ax2.plot(starts, transitions, "s--", color="tab:red", label="transitions/window"); ax.set_ylabel("occupancy"); ax2.set_ylabel("transitions"); ax.set_title("Rolling assignments, transitions, and occupancy (1000-step, stride 250)"); axr.hist(runs, bins=np.arange(.5, max(runs)+1.5), color="tab:purple", alpha=.7); axr.set(xlabel="residence length in rolling windows", ylabel="walker runs"); fig.tight_layout(); fig.savefig(out / f"{site.lower()}_seed{seed}_05_rolling.png", dpi=150); plt.close(fig)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", type=Path, required=True); ap.add_argument("--output", type=Path, required=True); args = ap.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text()); all_metrics = []
    for item in manifest["sources"]:
        src = load_source(Path(item["raw_chain"]), item)
        site, seed = item["site"], int(item["seed"]); all_metrics.append(chain_metrics(src, site, seed, args.output))
    by_site = {}
    for m in all_metrics: by_site.setdefault(m["site"], []).append(m)
    site_results = {}
    for site, rows in by_site.items():
        req = {k: [r["requirements"][k] for r in rows] for k in ("scalar_separation", "multivariate_separation", "temporal_persistence", "reproducible_group_locations")}
        # Cross-seed location consistency is deliberately conservative and predeclared.
        means = {r["seed"]: np.asarray(r["group_means_normalized"], float) for r in rows}
        pairwise = [float(np.linalg.norm(means[a][g] - means[b][g])) for a in SEEDS for b in SEEDS if a < b for g in (0, 1)]
        loc = "support" if max(pairwise) <= 0.5 else "oppose"
        for r in rows: r["requirements"]["reproducible_group_locations"] = loc
        site_results[site] = {"max_cross_seed_group_location_distance": max(pairwise)}
        req["reproducible_group_locations"] = [loc] * 3
        if all(v == "support" for vals in req.values() for v in vals): result = "two_basin_supported"
        elif all(v == "oppose" for v in req["scalar_separation"] + req["multivariate_separation"] + req["temporal_persistence"]): result = "two_basin_declined"
        elif all(req[k].count("support") >= 2 for k in req): result = "connected_ridge_supported"
        else: result = "inconclusive"
        site_results[site].update({"requirements": req, "topology": result, "n_chains": len(rows)})
        fig, ax = plt.subplots(figsize=(8, 4)); x = np.arange(3); width=.18
        for i, key in enumerate(("gmm_bic_1", "gmm_bic_2", "centroid_distance_prior_normalized", "temporal_assignment_agreement_2000_4000")):
            ax.bar(x + (i-1.5)*width, [r[key] for r in rows], width, label=key)
        ax.set_xticks(x, [f"seed {r['seed']}" for r in rows]); ax.set_title(f"{site}: three-seed topology support metrics"); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(args.output / f"{site.lower()}_three_seed_comparison.png", dpi=150); plt.close(fig)
    decision = {"schema": "spinup-forcing-coupling-iter010-decision-v1", "sources": all_metrics, "sites": site_results, "prediction_required": any(v["topology"] == "two_basin_supported" for v in site_results.values())}
    (args.output / "topology_decision.json").write_text(json.dumps(decision, indent=2, sort_keys=True))
    with (args.output / "topology_table.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["site", "topology", "seed", "scalar", "multivariate", "temporal", "location"])
        for site, rows in by_site.items():
            for r in rows: w.writerow([site, site_results[site]["topology"], r["seed"], r["requirements"]["scalar_separation"], r["requirements"]["multivariate_separation"], r["requirements"]["temporal_persistence"], r["requirements"]["reproducible_group_locations"]])
    print(json.dumps({"status": "TOPOLOGY_PASS", "sites": site_results, "prediction_required": decision["prediction_required"]}, sort_keys=True))


if __name__ == "__main__": main()
