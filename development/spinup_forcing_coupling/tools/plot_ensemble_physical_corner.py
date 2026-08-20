#!/usr/bin/env python3
"""Seed-colored physical corner for MAP ensemble post-burn samples."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
TOOLS_DIR = REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools"
for path in (REPO_ROOT, TOOLS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ensemble_common import DEFAULT_SEEDS, SITE_CONFIG, load_leaf, post_burn_physical_samples, tier_a_result  # noqa: E402
from plot_physical_corner import SCHEMA as CORNER_SCHEMA  # noqa: E402
from plot_physical_corner import plot_corner, subsample, write_json  # noqa: E402

SCHEMA = "spinup-forcing-coupling-ensemble-physical-corner-v1"
COLORS = (
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", choices=sorted(SITE_CONFIG), required=True)
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--subsample", type=int, default=1000)
    parser.add_argument("--rng-seed", type=int, default=16016)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    rng = np.random.default_rng(args.rng_seed)
    series = []
    parameter_names = None
    for index, seed in enumerate(args.seeds):
        leaf = load_leaf(args.root, args.site, seed)
        passed, _ = tier_a_result(leaf["mean_acceptance"], leaf["campaign_pass"])
        if not passed:
            continue
        parameter_names = leaf["parameter_names"]
        samples = post_burn_physical_samples(leaf, args.subsample, rng)
        samples = subsample(samples, args.subsample, rng)
        series.append((str(seed), samples, COLORS[index % len(COLORS)]))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = args.output_dir / "physical_corner_by_seed.png"
    manifest_path = args.output_dir / "physical_corner_manifest.json"
    if plot_path.exists() and not args.overwrite:
        raise FileExistsError(plot_path)
    if not series or parameter_names is None:
        manifest = {
            "schema": SCHEMA,
            "site": args.site,
            "status": "skipped_no_tier_a_seeds",
            "seeds": [],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"ENSEMBLE_CORNER_SKIP site={args.site} reason=no_tier_a_seeds")
        return 0
    plot_corner(
        plot_path,
        series,
        parameter_names,
        title=f"{args.site} ensemble physical corner (seed-colored post-burn)",
    )
    write_json(
        manifest_path,
        {
            "schema": SCHEMA,
            "corner_schema": CORNER_SCHEMA,
            "site": args.site,
            "seeds": [int(label) for label, _, _ in series],
            "plot": str(plot_path),
        },
        overwrite=True,
    )
    print(f"ENSEMBLE_CORNER_PASS site={args.site} seeds={len(series)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
