#!/usr/bin/env python3
"""Reusable physical-coordinate MCMC corner plots (pooled and optional per-seed).

Distinct from production `plots/corner/corner_plot.png` (14-param, thinned, `corner`
library). This tool matches the Iter012/014 evaluator style: physical coordinates,
optional `sigma_SR`, matplotlib histograms + scatter, pooled and/or seed-colored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
TOOLS_DIR = REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools"
for path in (REPO_ROOT, TOOLS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fixed_length_mcmc_diagnostics import (
    DEFAULT_PARAMS,
    descriptive_discard,
    integrated_time_by_seed,
    load_raw_chain,
)

SCHEMA = "spinup-forcing-coupling-physical-corner-v1"
SEED_COLORS = ("tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")


def subsample(states: np.ndarray, size: int, rng: np.random.Generator) -> np.ndarray:
    if len(states) <= size:
        return states
    return states[rng.choice(len(states), size=size, replace=False)]


def plot_corner(
    path: Path,
    series: list[tuple[str, np.ndarray, str]],
    parameter_names: list[str],
    title: str,
) -> None:
    ndim = len(parameter_names)
    figure, axes = plt.subplots(ndim, ndim, figsize=(24, 24))
    for row in range(ndim):
        for column in range(ndim):
            axis = axes[row, column]
            if row == column:
                for _, samples, color in series:
                    axis.hist(
                        samples[:, column],
                        bins=30,
                        color=color,
                        density=True,
                        alpha=0.45 if len(series) > 1 else 1.0,
                        histtype="stepfilled",
                    )
            elif row > column:
                for _, samples, color in series:
                    axis.scatter(
                        samples[:, column],
                        samples[:, row],
                        s=1,
                        alpha=0.15 if len(series) == 1 else 0.20,
                        linewidths=0,
                        color=color,
                    )
            else:
                axis.axis("off")
            if row == ndim - 1:
                axis.set_xlabel(
                    parameter_names[column], rotation=45, ha="right", fontsize=6
                )
            if column == 0 and row > 0:
                axis.set_ylabel(parameter_names[row], fontsize=6)
            axis.tick_params(labelsize=5)
    if len(series) > 1:
        handles = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=color,
                markersize=6,
                label=label,
            )
            for label, _, color in series
        ]
        figure.legend(handles=handles, loc="upper right", fontsize=8)
    figure.suptitle(title, fontsize=12)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def resolve_discard(nsteps: int, spec: dict[str, Any], chains: list[np.ndarray]) -> int:
    if spec.get("discard") is not None:
        return int(spec["discard"])
    tau_max = None
    for chain in chains:
        tau, _, error = integrated_time_by_seed(chain)
        if error is None:
            tau_max = float(np.max(tau) if tau_max is None else max(tau_max, np.max(tau)))
    discard, _, _ = descriptive_discard(nsteps, tau_max)
    return discard


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    require(spec.get("schema") == SCHEMA, f"{args.spec}: schema mismatch")
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    parameter_names = spec.get("parameter_names") or DEFAULT_PARAMS
    include_sigma = bool(spec.get("include_sigma_SR", True))
    if not include_sigma and parameter_names[-1] == "sigma_SR":
        parameter_names = parameter_names[:-1]
    subsample_size = int(spec.get("subsample", 2000))
    rng = np.random.default_rng(int(spec.get("rng_seed", 14014)))
    color_by_seed = bool(spec.get("color_by_seed", True))
    write_per_seed = bool(spec.get("write_per_seed", True))
    write_pooled = bool(spec.get("write_pooled", True))
    title = spec.get("title") or "Physical-coordinate MCMC corner"

    planned = []
    if write_pooled:
        planned.append(output_dir / "physical_corner.png")
        if color_by_seed:
            planned.append(output_dir / "physical_corner_by_seed.png")
    if write_per_seed:
        for member in spec["chains"]:
            label = str(member.get("label") or member.get("seed"))
            planned.append(output_dir / f"physical_corner_{label}.png")
    planned.append(output_dir / "physical_corner_manifest.json")
    for path in planned:
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"refusing to overwrite {path}; pass --overwrite")

    loaded = []
    provenance = []
    for member in spec["chains"]:
        path = Path(member["path"])
        payload = load_raw_chain(path)
        chain = payload["chain"]
        require(chain.shape[2] >= len(parameter_names), f"{path}: ndim {chain.shape[2]}")
        loaded.append((str(member.get("label") or member.get("seed")), chain))
        provenance.append(
            {
                "label": member.get("label") or member.get("seed"),
                "path": str(path.resolve()),
                "sha256": sha256(path),
                "shape": list(chain.shape),
            }
        )

    nsteps = loaded[0][1].shape[0]
    require(all(item[1].shape[0] == nsteps for item in loaded), "nsteps mismatch across chains")
    discard = resolve_discard(nsteps, spec, [item[1] for item in loaded])
    require(0 <= discard < nsteps, f"invalid discard {discard} for nsteps {nsteps}")

    post_by_label = []
    for index, (label, chain) in enumerate(loaded):
        post = chain[discard:, :, : len(parameter_names)].reshape(-1, len(parameter_names))
        color = SEED_COLORS[index % len(SEED_COLORS)]
        post_by_label.append((label, post, color))

    if write_pooled:
        pooled = np.concatenate([samples for _, samples, _ in post_by_label], axis=0)
        plot_corner(
            output_dir / "physical_corner.png",
            [("pooled", subsample(pooled, subsample_size, rng), "0.25")],
            parameter_names,
            f"{title} (pooled, discard={discard})",
        )
        if color_by_seed:
            colored = [
                (label, subsample(samples, max(1, subsample_size // len(post_by_label)), rng), color)
                for label, samples, color in post_by_label
            ]
            plot_corner(
                output_dir / "physical_corner_by_seed.png",
                colored,
                parameter_names,
                f"{title} (colored by seed, discard={discard})",
            )
    if write_per_seed:
        for label, samples, color in post_by_label:
            plot_corner(
                output_dir / f"physical_corner_{label}.png",
                [(label, subsample(samples, subsample_size, rng), color)],
                parameter_names,
                f"{title} ({label}, discard={discard})",
            )

    write_json(
        output_dir / "physical_corner_manifest.json",
        {
            "schema": SCHEMA,
            "spec_path": str(args.spec.resolve()),
            "spec_sha256": sha256(args.spec),
            "output_dir": str(output_dir.resolve()),
            "parameter_names": parameter_names,
            "discard": discard,
            "subsample": subsample_size,
            "color_by_seed": color_by_seed,
            "write_per_seed": write_per_seed,
            "write_pooled": write_pooled,
            "chains": provenance,
            "status": "pass",
        },
        overwrite=True,
    )
    print(
        "PHYSICAL_CORNER_PASS "
        f"nseed={len(loaded)} discard={discard} "
        f"pooled={write_pooled} per_seed={write_per_seed} output={output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
