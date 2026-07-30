#!/usr/bin/env python3
"""Plot cross-variant permutation importance from aggregate JSON artifacts."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TARGETS = ("TOTSOMC", "TOTSOMN")
COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")
REPO_ROOT = Path(__file__).resolve().parents[3]


class Placeholder:
    pass


class MetadataUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str) -> type:
        if module.startswith("model_ELM"):
            return Placeholder
        return super().find_class(module, name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration", required=True)
    parser.add_argument("--variant", action="append", required=True)
    parser.add_argument("--label", action="append")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--case-pickle",
        type=Path,
        default=REPO_ROOT / "pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl",
    )
    args = parser.parse_args()
    if args.label is not None and len(args.label) != len(args.variant):
        parser.error("--label must appear once per variant")
    if args.top < 1:
        parser.error("--top must be positive")
    return args


def parameter_labels(case_pickle: Path) -> dict[str, str]:
    with case_pickle.open("rb") as handle:
        case = MetadataUnpickler(handle).load()
    names = (
        getattr(case, "ensemble_parms", None)
        if not isinstance(case, dict)
        else case.get("ensemble_parms")
    )
    if names is None:
        raise RuntimeError(f"ensemble_parms not found in {case_pickle}")
    return {f"parm_{index}": str(name) for index, name in enumerate(list(names))}


def load_importance(
    repo: Path, iteration: str, variant: str, target: str
) -> dict[str, float]:
    path = (
        repo
        / "development/spinup_surrogate/summaries"
        / iteration
        / f"{variant}_importance_100seed.json"
    )
    rows = json.loads(path.read_text(encoding="utf-8"))["by_target"][target]
    return {row["feature"]: float(row["median_rmse_increase"]) for row in rows}


def main() -> None:
    args = parse_args()
    labels = args.label or args.variant
    label_map = parameter_labels(args.case_pickle)
    data = {
        (variant, target): load_importance(args.repo, args.iteration, variant, target)
        for variant in args.variant
        for target in TARGETS
    }
    all_features = set().union(*(values.keys() for values in data.values()))
    score = {
        feature: float(
            np.median(
                [
                    data[(variant, target)].get(feature, 0.0)
                    for variant in args.variant
                    for target in TARGETS
                ]
            )
        )
        for feature in all_features
    }
    top_features = sorted(all_features, key=lambda feature: score[feature], reverse=True)[
        : args.top
    ]
    display = [label_map.get(feature, feature) for feature in top_features]
    y_positions = np.arange(len(top_features))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(15, 9), sharey=True, constrained_layout=True)
    width = 0.8 / len(args.variant)
    for ax, target in zip(axes, TARGETS):
        for index, (variant, label) in enumerate(zip(args.variant, labels)):
            values = [data[(variant, target)].get(feature, 0.0) for feature in top_features]
            offset = (index - (len(args.variant) - 1) / 2) * width
            ax.barh(
                y_positions + offset,
                values,
                height=width,
                label=label,
                color=COLORS[index % len(COLORS)],
                alpha=0.8,
            )
        ax.set_yticks(y_positions)
        ax.set_yticklabels(display)
        ax.invert_yaxis()
        ax.set_title(target)
        ax.set_xlabel("Median RMSE increase")
        ax.grid(axis="x", alpha=0.25)
    axes[0].legend()
    fig.suptitle(f"{args.iteration} permutation importance")
    bar_path = args.output_dir / f"{args.iteration}_feature_importance_rmse_top{len(top_features)}.png"
    fig.savefig(bar_path, dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 9), constrained_layout=True)
    image = None
    for ax, target in zip(axes, TARGETS):
        matrix = np.array(
            [
                [data[(variant, target)].get(feature, 0.0) for variant in args.variant]
                for feature in top_features
            ]
        )
        image = ax.imshow(matrix, aspect="auto", cmap="viridis")
        ax.set_yticks(y_positions)
        ax.set_yticklabels(display)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_title(target)
    assert image is not None
    fig.colorbar(image, ax=axes, label="Median RMSE increase")
    fig.suptitle(f"{args.iteration} permutation importance")
    heatmap_path = args.output_dir / f"{args.iteration}_feature_importance_heatmap_top{len(top_features)}.png"
    fig.savefig(heatmap_path, dpi=180)
    plt.close(fig)
    print(bar_path)
    print(heatmap_path)


if __name__ == "__main__":
    main()
