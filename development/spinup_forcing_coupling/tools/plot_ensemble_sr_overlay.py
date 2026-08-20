#!/usr/bin/env python3
"""Overlay MAP SR predictions for a Tier-A MAP ensemble."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
TOOLS_DIR = REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools"
for path in (REPO_ROOT, TOOLS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ensemble_common import DEFAULT_SEEDS, SITE_CONFIG, load_leaf, tier_a_result  # noqa: E402
from model_ELM.coupling_pipeline import build_coupling_target  # noqa: E402
from model_ELM.MCMC_forcing import run_forcing_surrogate_site  # noqa: E402

CASES = {"ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC", "JERC": "JERC_ppe6_I20TRCNPRDCTCBC"}
SCHEMA = "spinup-forcing-coupling-ensemble-sr-overlay-v1"


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
    aligned = aligned.copy()
    aligned[aligned < -9000] = np.nan
    return aligned


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", choices=sorted(SITE_CONFIG), required=True)
    parser.add_argument("--forcing-artifact", type=Path, required=True)
    parser.add_argument("--spinup-artifact", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    cfg = SITE_CONFIG[args.site]
    target = build_coupling_target(
        cases=[CASES[args.site]],
        resolution=cfg["resolution"],
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    context = target["context"][args.site]
    obs = np.asarray(target["obs"][args.site]["SR"], float)
    err = np.asarray(target["obs_err"][args.site]["SR"], float)
    elm = elm_baseline(target, args.site)
    x = np.arange(len(obs))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = args.output_dir / "Predictions_SR_MAP_ensemble.png"
    manifest_path = args.output_dir / "sr_overlay_manifest.json"
    if plot_path.exists() and not args.overwrite:
        raise FileExistsError(plot_path)

    plt.figure(figsize=(12, 4))
    series = []
    for seed in args.seeds:
        leaf = load_leaf(args.root, args.site, seed)
        passed, _ = tier_a_result(leaf["mean_acceptance"], leaf["campaign_pass"])
        if not passed:
            continue
        pred = np.asarray(
            run_forcing_surrogate_site(context, leaf["map_state"][:-1], ["SR"])["SR"], float
        ).ravel()
        label = f"MAP seed {seed}"
        plt.plot(x, pred, linewidth=0.8, alpha=0.7, label=label)
        series.append({"seed": seed, "rmse": leaf["map_rmse"]})
    plt.plot(x, elm, color="darkgreen", linewidth=0.8, linestyle="--", label="ELM precal", alpha=0.8)
    plt.plot(x, obs, color="blue", linewidth=0.8, label="Observations", alpha=0.8)
    plt.fill_between(x, obs - err, obs + err, color="blue", alpha=0.2)
    plt.xlabel("Overlap index")
    plt.ylabel("SR")
    plt.title(f"{args.site} MAP ensemble SR overlay")
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()

    manifest = {"schema": SCHEMA, "site": args.site, "series": series, "plot": str(plot_path)}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"SR_OVERLAY_PASS site={args.site} series={len(series)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
