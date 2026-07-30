#!/usr/bin/env python3
"""Plot per-variant train/test R2 and RMSE distributions for any iteration.

Example (after an iteration has produced its stats files):
  development/spinup_surrogate/slurm/iter010/plot_iter010_a40_distributions.py \
      --iteration iter011 --variant control --variant candidate \
      --output-dir /path/to/plots
"""
import argparse
import glob
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DEFAULT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")
TARGETS = ("TOTSOMC", "TOTSOMN")
COLORS = {"Training": "tab:blue", "Testing": "tab:orange"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration", required=True, help="Iteration ID, for example iter011")
    parser.add_argument("--variant", action="append", required=True, help="Variant suffix; repeat")
    parser.add_argument("--paired-control", help="Control variant for paired validation plots")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    if args.paired_control is not None and args.paired_control not in args.variant:
        parser.error("--paired-control must name one supplied --variant")
    return args


def read_values(run_dir, target, metric):
    values = {"Training": [], "Testing": []}
    pattern = run_dir / "surrogate_spinup" / "surrogate_spinup_stats_seed*.json"
    files = sorted(glob.glob(str(pattern)))
    if not files:
        raise RuntimeError(f"No stats files in {run_dir}")
    for path in files:
        with open(path) as handle:
            item = json.load(handle)["by_variable"][target]
        values["Training"].append(float(item[f"{metric}_train"]))
        values["Testing"].append(float(item[f"{metric}_val"]))
    return values


def make_figure(iteration, variant, root, output_dir, metric, xlabel):
    run_dir = root / f"spinup_surrogate_{iteration}_{variant}"
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    for ax, target in zip(axes, TARGETS):
        values = read_values(run_dir, target, metric)
        all_values = np.concatenate([values["Training"], values["Testing"]])
        bins = np.histogram_bin_edges(all_values, bins="auto")
        for label in ("Training", "Testing"):
            ax.hist(values[label], bins=bins, alpha=0.5, color=COLORS[label], label=label,
                    edgecolor="black", linewidth=0.35)
        ax.set_title(target)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Count")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
    fig.suptitle(f"{iteration} {variant}: {xlabel} distributions ({len(values['Training'])} seeds)")
    output = output_dir / f"{iteration}_{variant}_{metric}_train_test_hist.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(output)


def read_validation_by_seed(run_dir, target, metric):
    pattern = run_dir / "surrogate_spinup" / "surrogate_spinup_stats_seed*.json"
    values = {}
    for path in sorted(glob.glob(str(pattern))):
        match = re.search(r"seed(\d+)", Path(path).name)
        if match is None:
            raise RuntimeError(f"Cannot determine seed from {path}")
        with open(path) as handle:
            values[int(match.group(1))] = float(json.load(handle)["by_variable"][target][f"{metric}_val"])
    if not values:
        raise RuntimeError(f"No stats files in {run_dir}")
    return values


def make_paired_figure(iteration, control, candidate, root, output_dir, metric, xlabel):
    control_dir = root / f"spinup_surrogate_{iteration}_{control}"
    candidate_dir = root / f"spinup_surrogate_{iteration}_{candidate}"
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    for ax, target in zip(axes, TARGETS):
        control_values = read_validation_by_seed(control_dir, target, metric)
        candidate_values = read_validation_by_seed(candidate_dir, target, metric)
        if set(control_values) != set(candidate_values):
            raise RuntimeError(f"Seed mismatch for {target}: {control} vs {candidate}")
        seeds = sorted(control_values)
        x_values = np.array([control_values[seed] for seed in seeds])
        y_values = np.array([candidate_values[seed] for seed in seeds])
        limits = (min(x_values.min(), y_values.min()), max(x_values.max(), y_values.max()))
        ax.scatter(x_values, y_values, alpha=0.7, edgecolors="black", linewidths=0.25)
        ax.plot(limits, limits, color="black", linestyle="--", linewidth=1)
        ax.set_title(target)
        ax.set_xlabel(f"Control validation {xlabel}")
        ax.set_ylabel(f"Candidate validation {xlabel}")
        ax.grid(alpha=0.25)
        ax.set_aspect("equal", adjustable="box")
    fig.suptitle(f"{iteration}: paired validation {xlabel}, {candidate} vs {control}")
    output = output_dir / f"{iteration}_{candidate}_vs_{control}_{metric}_val_paired.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(output)


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in args.variant:
        make_figure(args.iteration, variant, args.root, args.output_dir, "r2", "R²")
        make_figure(args.iteration, variant, args.root, args.output_dir, "rmse", "RMSE")
    if args.paired_control is not None:
        for variant in args.variant:
            if variant == args.paired_control:
                continue
            make_paired_figure(args.iteration, args.paired_control, variant, args.root,
                               args.output_dir, "r2", "R²")
            make_paired_figure(args.iteration, args.paired_control, variant, args.root,
                               args.output_dir, "rmse", "RMSE")


if __name__ == "__main__":
    main()
