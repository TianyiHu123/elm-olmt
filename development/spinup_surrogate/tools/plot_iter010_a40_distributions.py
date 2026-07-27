#!/usr/bin/env python3
"""Plot Iter010 alpha-40 train/test metric distributions for three variants."""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output"
VARIANTS = [
    "s32_tanh_lbfgs_a40_lr1e3_full45",
    "s32_tanh_lbfgs_a40_lr1e3_corr080_prioritydrop",
    "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf",
]
TARGETS = ["TOTSOMC", "TOTSOMN"]
COLORS = {"Training": "tab:blue", "Testing": "tab:orange"}
def read_values(run_dir, target, metric):
    values = {"Training": [], "Testing": []}
    pattern = os.path.join(run_dir, "surrogate_spinup", "surrogate_spinup_stats_seed*.json")
    files = sorted(glob.glob(pattern))
    if len(files) != 100:
        raise RuntimeError(f"Expected 100 seed files in {run_dir}, found {len(files)}")
    for path in files:
        with open(path) as handle:
            item = json.load(handle)["by_variable"][target]
        values["Training"].append(float(item[f"{metric}_train"]))
        values["Testing"].append(float(item[f"{metric}_val"]))
    return values


def make_figure(variant, metric, xlabel, filename):
    run_dir = os.path.join(ROOT, f"spinup_surrogate_iter010_{variant}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    for ax, target in zip(axes, TARGETS):
        values = read_values(run_dir, target, metric)
        all_values = np.concatenate([values["Training"], values["Testing"]])
        bins = np.histogram_bin_edges(all_values, bins="auto")
        for label in ("Training", "Testing"):
            ax.hist(values[label], bins=bins, alpha=0.5, color=COLORS[label],
                    label=label, edgecolor="black", linewidth=0.35)
        ax.set_title(target)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Count")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
    fig.suptitle(f"Iter010 {variant}: {xlabel} distributions (100 seeds)")
    output = os.path.join(run_dir, filename)
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(output)


for variant in VARIANTS:
    make_figure(variant, "r2", "R²", "iter010_a40_r2_train_test_hist.png")
    make_figure(variant, "rmse", "RMSE", "iter010_a40_rmse_train_test_hist.png")
