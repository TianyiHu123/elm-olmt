#!/usr/bin/env python
"""Bounded no-preparation Iter001 compute-node preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import netCDF4
import numpy as np


EXPECTED_MONTHS = [f"{year:04d}-{month:02d}.nc" for year in range(2018, 2025) for month in range(1, 13)]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be initial 1 plus at most three correction/retries")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    root = Path(config["repository_root"]).resolve()
    sys.path.insert(0, str(root))
    import model_ELM  # noqa: F401
    from development.three_stage_surrogate.tools import prepare_surrogate_input_data as prep
    from development.three_stage_surrogate.tools import validate_surrogate_input_data as validator

    require(config["schema"] == "three-stage-surrogate-iter001-config-v1", "config schema mismatch")
    require(config["maximum_preflight_correction_retries"] == 3, "preflight retry contract mismatch")
    require(config["maximum_operational_correction_retries"] == 3, "operational retry contract mismatch")
    require(Path.cwd().resolve() == root, "preflight must run from locked repository root")
    plan = root / config["campaign_plan"]
    require(hashlib.sha256(plan.read_bytes()).hexdigest() == config["campaign_plan_sha256"], "campaign plan hash mismatch")
    names, values, _ = prep.load_parameters(config)
    require(len(names) == 18 and values.shape == (1024, 18), "parameter contract mismatch")
    for site in config["site_order"]:
        entry = config["sites"][site]
        for key in ("transient_pickle", "spinup_preprocessing", "surface_file"):
            require(Path(entry[key]).is_file(), f"missing {site} {key}: {entry[key]}")
        directory = Path(entry["forcing_directory"])
        require(directory.is_dir(), f"missing {site} forcing directory")
        require(sorted(path.name for path in directory.glob("*.nc")) == EXPECTED_MONTHS, f"{site} forcing inventory mismatch")
        with netCDF4.Dataset(entry["spinup_preprocessing"], "r") as dataset:
            require(len(dataset.dimensions["member"]) == 1024, f"{site} spinup member count mismatch")
            require(all(name in dataset.variables for name in ("member", "TOTSOMC", "TOTSOMN")), f"{site} spinup schema mismatch")
        with netCDF4.Dataset(entry["surface_file"], "r") as dataset:
            require(all(name in dataset.variables for name in prep.SURFACE_VARS), f"{site} surface schema mismatch")
        first_forcing = directory / EXPECTED_MONTHS[0]
        with netCDF4.Dataset(str(first_forcing), "r") as dataset:
            require("time" in dataset.variables, f"{site} forcing time missing")
            require(all(name in dataset.variables for name in prep.FORCING_VARS), f"{site} forcing schema mismatch")
    require(callable(validator.main), "validator import failed")
    require(np.__version__ and netCDF4.__version__, "dependency version unavailable")
    print(
        "ITER001_PREFLIGHT_OK no_training=true "
        f"attempt={args.attempt} sites=ABBY,JERC members=1024 parameters=18 forcing_months=84",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
