#!/usr/bin/env python3
"""Bounded compute-node configuration preflight for the Iter018 release."""
from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.optimization_config import load_campaign


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-dir", type=Path, required=True)
    args = parser.parse_args()
    campaigns = sorted(args.campaign_dir.glob("*.yaml"))
    if len(campaigns) != 9:
        raise ValueError(f"expected nine campaign YAML files, found {len(campaigns)}")
    observed: dict[str, tuple[str, float]] = {}
    for campaign in campaigns:
        for stage in ("initialization", "optimization", "reporting"):
            load_campaign(campaign, stage)
        contract = load_campaign(campaign, "optimization")
        shared = contract["shared"]
        if len(shared["sites"]) != 1 or len(shared["cases"]) != 1:
            raise ValueError(f"Iter018 must be single-site: {campaign}")
        observed[shared["sites"][0]] = (
            contract["optimization"]["likelihood_resolution"],
            contract["optimization"]["de_move_scale"],
        )
    expected = {
        "ABBY": ("daily", 0.50), "SOAP": ("daily", 0.50),
        "YELL": ("daily", 0.50), "WREF": ("daily", 0.50),
        "JERC": ("hourly", 0.75), "OSBS": ("hourly", 0.75),
        "RMNP": ("hourly", 0.75), "TALL": ("hourly", 0.75),
        "TEAK": ("hourly", 0.75),
    }
    if observed != expected:
        raise ValueError(f"unexpected Iter018 site configuration: {observed}")
    for source in (
        REPO_ROOT / "initialize_pipeline.py",
        REPO_ROOT / "run_optimization_campaign.py",
        REPO_ROOT / "report_optimization.py",
        REPO_ROOT / "model_ELM/optimization_config.py",
        REPO_ROOT / "model_ELM/mcmc_artifacts.py",
        REPO_ROOT / "model_ELM/mcmc_diagnostics.py",
    ):
        py_compile.compile(str(source), doraise=True)
    print("ITER018_PREFLIGHT_PASS campaigns=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
