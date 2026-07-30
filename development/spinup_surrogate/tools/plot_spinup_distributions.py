#!/usr/bin/env python3
"""Plot per-variant train/validation distributions and paired validation comparisons."""

from __future__ import annotations

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
COLORS = {"Training": "tab:blue", "Validation": "tab:orange"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration", required=True)
    parser.add_argument("--variant", action="append", required=True)
    parser.add_argument("--paired-control")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    if args.paired_control is not None and args.paired_control not in args.variant:
        parser.error("--paired-control must name one supplied --variant")
    return args


def stats_files(run_dir: Path) -> list[Path]:
    paths = [Path(path) for path in sorted(
        glob.glob(str(run_dir / "surrogate_spinup/surrogate_spinup_stats_seed*.json"))
    )]
    if not paths:
        raise RuntimeError(f"No stats files in {run_dir}")
    return paths


def read_values(run_dir: Path, target: str, metric: str) -> dict[str, list[float]]:
    values = {"Training": [], "Validation": []}
    for path in stats_files(run_dir):
        item = json.loads(path.read_text(encoding="utf-8"))["by_variable"][target]
        values["Training"].append(float(item[f"{metric}_train"]))
        values["Validation"].append(float(item[f"{metric}_val"]))
    return values


def make_distribution(
    iteration: str,
    variant: str,
    root: Path,
    output_dir: Path,
    metric: str,
    xlabel: str,
) -> None:
    run_dir = root / f"spinup_surrogate_{iteration}_{variant}"
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    seed_count = 0
    for ax, target in zip(axes, TARGETS):
        values = read_values(run_dir, target, metric)
        seed_count = len(values["Training"])
        bins = np.histogram_bin_edges(
            np.concatenate([values["Training"], values["Validation"]]), bins="auto"
        )
        for label in ("Training", "Validation"):
            ax.hist(
                values[label],
                bins=bins,
                alpha=0.5,
                color=COLORS[label],
                label=label,
                edgecolor="black",
                linewidth=0.35,
            )
        ax.set_title(target)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Count")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
    fig.suptitle(f"{iteration} {variant}: {xlabel} distributions ({seed_count} seeds)")
    output = output_dir / f"{iteration}_{variant}_{metric}_train_validation_hist.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(output)


def read_validation_by_seed(run_dir: Path, target: str, metric: str) -> dict[int, float]:
    values: dict[int, float] = {}
    for path in stats_files(run_dir):
        match = re.search(r"seed(\d+)", path.name)
        if match is None:
            raise RuntimeError(f"Cannot determine seed from {path}")
        item = json.loads(path.read_text(encoding="utf-8"))["by_variable"][target]
        values[int(match.group(1))] = float(item[f"{metric}_val"])
    return values


def make_paired(
    iteration: str,
    control: str,
    candidate: str,
    root: Path,
    output_dir: Path,
    metric: str,
    xlabel: str,
) -> None:
    control_dir = root / f"spinup_surrogate_{iteration}_{control}"
    candidate_dir = root / f"spinup_surrogate_{iteration}_{candidate}"
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    for ax, target in zip(axes, TARGETS):
        control_values = read_validation_by_seed(control_dir, target, metric)
        candidate_values = read_validation_by_seed(candidate_dir, target, metric)
        if set(control_values) != set(candidate_values):
            raise RuntimeError(f"Seed mismatch for {target}")
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
    fig.suptitle(f"{iteration}: paired validation {xlabel}")
    output = output_dir / f"{iteration}_{candidate}_vs_{control}_{metric}_validation_paired.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(output)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in args.variant:
        make_distribution(args.iteration, variant, args.root, args.output_dir, "r2", "R²")
        make_distribution(args.iteration, variant, args.root, args.output_dir, "rmse", "RMSE")
    if args.paired_control is not None:
        for variant in args.variant:
            if variant != args.paired_control:
                make_paired(
                    args.iteration,
                    args.paired_control,
                    variant,
                    args.root,
                    args.output_dir,
                    "r2",
                    "R²",
                )
                make_paired(
                    args.iteration,
                    args.paired_control,
                    variant,
                    args.root,
                    args.output_dir,
                    "rmse",
                    "RMSE",
                )


if __name__ == "__main__":
    main()
