#!/usr/bin/env python3
"""Plot cross-variant permutation importance from any iteration's aggregate JSON.

Example (after aggregation):
  development/spinup_surrogate/slurm/iter010/plot_iter010_a40_importance.py \
      --iteration iter011 --variant control --variant candidate \
      --label drop32 --label drop32_corr080 --output-dir /path/to/plots
"""
import argparse
import json
import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TARGETS = ("TOTSOMC", "TOTSOMN")
COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd")
REPO = Path(__file__).resolve().parents[3]


class Placeholder:
    pass


class MetadataUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith("model_ELM"):
            return Placeholder
        return super().find_class(module, name)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration", required=True, help="Iteration ID, for example iter011")
    parser.add_argument("--variant", action="append", required=True, help="Variant suffix; repeat")
    parser.add_argument("--label", action="append", help="Display label; repeat once per variant")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--case-pickle", type=Path,
                        default=REPO / "pklfiles" / "ABBY_ppe6_I20TRCNPRDCTCBC.pkl")
    args = parser.parse_args()
    if args.label is not None and len(args.label) != len(args.variant):
        parser.error("--label must appear once for every --variant")
    if args.top < 1:
        parser.error("--top must be positive")
    return args


def parameter_labels(case_pickle):
    with open(case_pickle, "rb") as handle:
        case = MetadataUnpickler(handle).load()
    names = getattr(case, "ensemble_parms", None) if not isinstance(case, dict) else case.get("ensemble_parms")
    if names is None:
        raise RuntimeError(f"ensemble_parms not found in {case_pickle}")
    return {f"parm_{index}": str(name) for index, name in enumerate(list(names))}


def load_importance(repo, iteration, variant, target):
    path = repo / "development" / "spinup_surrogate" / "summaries" / iteration / f"{variant}_importance_100seed.json"
    with open(path) as handle:
        rows = json.load(handle)["by_target"][target]
    return {row["feature"]: float(row["median_rmse_increase"]) for row in rows}


def main():
    args = parse_args()
    labels = args.label or args.variant
    label_map = parameter_labels(args.case_pickle)
    data = {(variant, target): load_importance(args.repo, args.iteration, variant, target)
            for variant in args.variant for target in TARGETS}
    all_features = set().union(*(values.keys() for values in data.values()))
    score = {feature: np.median([data[(variant, target)].get(feature, 0.0)
                                 for variant in args.variant for target in TARGETS])
             for feature in all_features}
    top = sorted(all_features, key=lambda feature: score[feature], reverse=True)[:args.top]
    display = [label_map.get(feature, feature) for feature in top]
    y = np.arange(len(top))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(15, 9), sharey=True, constrained_layout=True)
    width = 0.8 / len(args.variant)
    for ax, target in zip(axes, TARGETS):
        for index, (variant, label) in enumerate(zip(args.variant, labels)):
            values = [data[(variant, target)].get(feature, 0.0) for feature in top]
            offset = (index - (len(args.variant) - 1) / 2) * width
            ax.barh(y + offset, values, height=width, label=label,
                    color=COLORS[index % len(COLORS)], alpha=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(display)
        ax.invert_yaxis()
        ax.set_title(target)
        ax.set_xlabel("Median RMSE increase")
        ax.grid(axis="x", alpha=0.25)
    axes[0].legend()
    fig.suptitle(f"{args.iteration} permutation importance: top {len(top)} features")
    bar_path = args.output_dir / f"{args.iteration}_feature_importance_rmse_top{len(top)}.png"
    fig.savefig(bar_path, dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 9), constrained_layout=True)
    for ax, target in zip(axes, TARGETS):
        matrix = np.array([[data[(variant, target)].get(feature, 0.0) for variant in args.variant]
                           for feature in top])
        image = ax.imshow(matrix, aspect="auto", cmap="viridis")
        ax.set_yticks(y)
        ax.set_yticklabels(display)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_title(target)
        ax.set_xlabel("Feature policy")
        maximum = np.nanmax(matrix) if matrix.size else 0.0
        for row in range(len(top)):
            for column in range(len(args.variant)):
                color = "white" if maximum and matrix[row, column] > maximum * 0.45 else "black"
                ax.text(column, row, f"{matrix[row, column]:.0f}", ha="center", va="center",
                        fontsize=7, color=color)
    fig.colorbar(image, ax=axes, label="Median RMSE increase")
    fig.suptitle(f"{args.iteration} permutation importance: top {len(top)} features")
    heatmap_path = args.output_dir / f"{args.iteration}_feature_importance_heatmap_top{len(top)}.png"
    fig.savefig(heatmap_path, dpi=180)
    plt.close(fig)
    print(bar_path)
    print(heatmap_path)


if __name__ == "__main__":
    main()
