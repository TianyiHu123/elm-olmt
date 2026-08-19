#!/usr/bin/env python3
"""Iter015 preflight: locked hashes, hybrid dry-checks, four targets, reuse smoke."""
from __future__ import annotations

import argparse
import hashlib
import json
import py_compile
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import (  # noqa: E402
    POOL_RULES,
    assert_pool_target_compatible,
    build_coupling_target,
    choose_candidate_pool,
    select_production_walkers,
)

EXPECTED = {
    "forcing": "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e",
    "spinup": "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023",
    "abby_obs": "e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2",
    "jerc_obs": "a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f",
    "abby_ledger": "ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b",
    "jerc_ledger": "25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d",
    "jerc_hybrid": "40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df",
    "abby_daily": "bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd",
    "jerc_hourly": "26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196",
}
CASES = {
    "ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC": "JERC_ppe6_I20TRCNPRDCTCBC",
}
LEDGER_RESOLUTION = {"ABBY": "daily", "JERC": "hourly"}
PARAMS = [
    "k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4", "k_frag",
    "rf_l1s1", "rf_l2s2", "rf_l3s3", "rf_s1s2", "rf_s2s3", "rf_s3s4", "sigma_SR",
]
COMPILE_TARGETS = (
    REPO_ROOT / "model_ELM" / "coupling_pipeline.py",
    REPO_ROOT / "initialize_pipeline.py",
    REPO_ROOT / "optimize_surrogate_forcing.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter015" / "preflight_iter015.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter015" / "analyze_iter015.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter015" / "validate_iter015_handoff.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools" / "plot_init_cloud_overlay.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools" / "fixed_length_mcmc_diagnostics.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools" / "plot_physical_corner.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--abby-observation", required=True, type=Path)
    parser.add_argument("--jerc-observation", required=True, type=Path)
    parser.add_argument("--abby-ledger", required=True, type=Path)
    parser.add_argument("--jerc-ledger", required=True, type=Path)
    parser.add_argument("--jerc-hybrid-reference", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--dependency-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    require(args.source_manifest.is_file(), "missing source manifest")
    require(args.dependency_manifest.is_file(), "missing dependency manifest")
    require(sha256(args.forcing_artifact) == EXPECTED["forcing"], "forcing hash mismatch")
    require(sha256(args.spinup_artifact) == EXPECTED["spinup"], "spinup hash mismatch")
    require(sha256(args.abby_observation) == EXPECTED["abby_obs"], "ABBY obs hash mismatch")
    require(sha256(args.jerc_observation) == EXPECTED["jerc_obs"], "JERC obs hash mismatch")
    require(sha256(args.abby_ledger) == EXPECTED["abby_ledger"], "ABBY ledger hash mismatch")
    require(sha256(args.jerc_ledger) == EXPECTED["jerc_ledger"], "JERC ledger hash mismatch")
    require(sha256(args.jerc_hybrid_reference) == EXPECTED["jerc_hybrid"], "JERC hybrid reference mismatch")
    require("hybrid_high_l_maximin" in POOL_RULES, "hybrid_high_l_maximin missing")
    for path in COMPILE_TARGETS:
        require(path.is_file(), f"missing compile target {path}")
        py_compile.compile(str(path), doraise=True)

    observations = {"ABBY": args.abby_observation, "JERC": args.jerc_observation}
    ledgers = {"ABBY": args.abby_ledger, "JERC": args.jerc_ledger}
    targets = {}
    dry_checks = {}
    reuse_checks = {}
    for site in ("ABBY", "JERC"):
        for resolution in ("hourly", "daily"):
            target = build_coupling_target(
                cases=[CASES[site]],
                resolution=resolution,
                forcing_artifact=args.forcing_artifact,
                spinup_artifact=args.spinup_artifact,
                observation_paths={site: observations[site]},
                expected_physical_parameter_count=14,
            )
            require(target["parameter_names"] == PARAMS, f"{site} {resolution} parameter names")
            midpoint = 0.5 * (target["pmin"] + target["pmax"])
            logp = float(target["log_posterior"](midpoint))
            require(np.isfinite(logp), f"{site} {resolution} midpoint logp")
            if resolution == "daily":
                require(site in target["daily_maps"], f"{site} daily map missing")
            key = f"{site.lower()}_{resolution}"
            targets[key] = {
                "sha256": target["identity"]["sha256"],
                "midpoint_log_posterior": logp,
                "daily_map_sha256": None if resolution != "daily" else target["daily_maps"][site]["sha256"],
            }
            if site == "ABBY" and resolution == "daily":
                require(target["identity"]["sha256"] == EXPECTED["abby_daily"], "ABBY daily target mismatch")
            if site == "JERC" and resolution == "hourly":
                require(target["identity"]["sha256"] == EXPECTED["jerc_hourly"], "JERC hourly target mismatch")

        ledger_resolution = LEDGER_RESOLUTION[site]
        ledger_target = build_coupling_target(
            cases=[CASES[site]],
            resolution=ledger_resolution,
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
            observation_paths={site: observations[site]},
            expected_physical_parameter_count=14,
        )
        ledger = np.load(ledgers[site], allow_pickle=False)
        states = np.asarray(ledger["states"], dtype=float)
        stored_logp = np.asarray(ledger["log_posterior"], dtype=float)
        pool, pool_logp, pool_strata, diagnostics = choose_candidate_pool(
            states,
            stored_logp,
            np.asarray(ledger_target["pmin"], dtype=float),
            np.asarray(ledger_target["pmax"], dtype=float),
            pool_size=640,
            seed=0,
            pool_rule="hybrid_high_l_maximin",
            high_l_quantile=0.90,
        )
        require(pool.shape == (640, 15), f"{site} hybrid pool shape")
        dry_checks[site.lower()] = {
            "status": "pass",
            "ledger_resolution": ledger_resolution,
            "normalized_rank": diagnostics.get("normalized_rank"),
            "normalized_condition_number": diagnostics.get("normalized_condition_number"),
            "high_l_quantile_applied": diagnostics.get("high_l_quantile_applied"),
            "high_l_universe_count": diagnostics.get("high_l_universe_count"),
        }
        fake_contract = {
            "site": site,
            "resolution": ledger_resolution,
            "cases": [CASES[site]],
            "target_identity": ledger_target["identity"],
        }
        for resolution in ("hourly", "daily"):
            campaign = build_coupling_target(
                cases=[CASES[site]],
                resolution=resolution,
                forcing_artifact=args.forcing_artifact,
                spinup_artifact=args.spinup_artifact,
                observation_paths={site: observations[site]},
                expected_physical_parameter_count=14,
            )
            reuse = assert_pool_target_compatible(
                fake_contract,
                campaign,
                resolution,
                pool_reuse_policy="site_hybrid_pool_reuse_v1",
            )
            indices, selected = select_production_walkers(
                pool,
                pool_logp,
                pool_strata,
                campaign["pmin"],
                campaign["pmax"],
                seed=0,
                log_posterior=campaign["log_posterior"],
                walker_count=64,
                require_stored_posterior_match=bool(reuse["require_stored_posterior_match"]),
            )
            require(selected.shape == (64, 15), f"{site} {resolution} walker shape")
            require(indices.shape == (64,), f"{site} {resolution} index shape")
            reuse_checks[f"{site.lower()}_{resolution}"] = {
                "resolutions_match": reuse["resolutions_match"],
                "require_stored_posterior_match": reuse["require_stored_posterior_match"],
                "pool_target_sha256": reuse["pool_target_sha256"],
                "campaign_target_sha256": reuse["campaign_target_sha256"],
                "n_walkers": 64,
            }

    payload = {
        "schema": "spinup-forcing-coupling-iter015-preflight-v1",
        "pool_rule": "hybrid_high_l_maximin",
        "pool_reuse_policy": "site_hybrid_pool_reuse_v1",
        "targets": targets,
        "ledger_dry_checks": dry_checks,
        "reuse_checks": reuse_checks,
        "source_manifest_sha256": sha256(args.source_manifest),
        "dependency_manifest_sha256": sha256(args.dependency_manifest),
        "status": "pass",
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("PREFLIGHT_PASS sites=ABBY,JERC pool_rule=hybrid_high_l_maximin")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
