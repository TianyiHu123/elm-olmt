#!/usr/bin/env python3
"""Bounded Iter017 source/configuration preflight (compute-node only)."""
from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.optimization_config import load_campaign
from model_ELM.coupling_pipeline import build_coupling_target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-dir", type=Path, required=True)
    args = parser.parse_args()
    campaigns = sorted(args.campaign_dir.glob("*.yaml"))
    if len(campaigns) != 4:
        raise ValueError(f"expected four campaign YAML files, found {len(campaigns)}")
    for campaign in campaigns:
        for stage in ("initialization", "optimization", "reporting"):
            load_campaign(campaign, stage)
    for source in (
        REPO_ROOT / "initialize_pipeline.py", REPO_ROOT / "optimize_surrogate_forcing.py",
        REPO_ROOT / "run_optimization_campaign.py", REPO_ROOT / "report_optimization.py",
        REPO_ROOT / "model_ELM/MCMC_forcing.py", REPO_ROOT / "model_ELM/mcmc_artifacts.py",
        REPO_ROOT / "model_ELM/mcmc_diagnostics.py", REPO_ROOT / "model_ELM/optimization_config.py",
    ):
        py_compile.compile(str(source), doraise=True)
    # These imports cover the explicitly retained generic-MCMC, forcing-training,
    # and coupled-runtime public boundaries without starting a model calculation.
    import model_ELM.MCMC  # noqa: F401
    import model_ELM.MCMC_forcing  # noqa: F401
    import model_ELM.surrogate_NN_Forcing  # noqa: F401
    # The joint identity must be order-invariant, including the shared sigma_SR
    # bound that is derived across all valid sites. This is target construction,
    # not an MCMC/model run.
    for campaign in campaigns:
        contract = load_campaign(campaign, "optimization")
        shared = contract["shared"]
        if len(shared["sites"]) < 2:
            continue
        stage = contract["optimization"]
        forward = build_coupling_target(
            cases=shared["cases"], resolution=stage["likelihood_resolution"],
            forcing_artifact=shared["forcing_artifact"], spinup_artifact=shared["spinup_artifact"],
            observation_paths=shared["observations"], fit_error=True,
            expected_physical_parameter_count=14,
        )
        reverse = build_coupling_target(
            cases=list(reversed(shared["cases"])), resolution=stage["likelihood_resolution"],
            forcing_artifact=shared["forcing_artifact"], spinup_artifact=shared["spinup_artifact"],
            observation_paths=shared["observations"], fit_error=True,
            expected_physical_parameter_count=14,
        )
        if forward["identity"] != reverse["identity"]:
            raise ValueError(f"joint site-order invariance failed: {campaign}")
    print("ITER017_PREFLIGHT_PASS campaigns=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
