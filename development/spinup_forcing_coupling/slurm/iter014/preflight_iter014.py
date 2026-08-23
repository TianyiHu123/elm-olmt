#!/usr/bin/env python3
"""Iter014 preflight: locked hashes, POOL_RULES, ledger dry-check, target sha, py_compile."""
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
    build_coupling_target,
    choose_candidate_pool,
)

EXPECTED_FORCING = "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
EXPECTED_SPINUP = "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023"
EXPECTED_OBS = "a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f"
EXPECTED_LEDGER = "25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d"
EXPECTED_CONTROL_POOL = "32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96"
EXPECTED_TARGET = "26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196"
REQUIRED_POOL_RULES = ("rank_dominated", "hybrid_high_l_maximin")
PARAMS = [
    "k_l1",
    "k_l2",
    "k_l3",
    "k_s1",
    "k_s2",
    "k_s3",
    "k_s4",
    "k_frag",
    "rf_l1s1",
    "rf_l2s2",
    "rf_l3s3",
    "rf_s1s2",
    "rf_s2s3",
    "rf_s3s4",
    "sigma_SR",
]
COMPILE_TARGETS = (
    REPO_ROOT / "model_ELM" / "coupling_pipeline.py",
    REPO_ROOT / "initialize_pipeline.py",
    REPO_ROOT / "optimize_surrogate_forcing.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter014" / "preflight_iter014.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter014" / "evaluate_iter014.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter014" / "aggregate_iter014.py",
    REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter014" / "validate_iter014_handoff.py",
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
    parser.add_argument("--observation", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--control-pool", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--dependency-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    require(args.source_manifest.is_file(), "missing source manifest")
    require(args.dependency_manifest.is_file(), "missing dependency manifest")
    require(sha256(args.forcing_artifact) == EXPECTED_FORCING, "forcing hash mismatch")
    require(sha256(args.spinup_artifact) == EXPECTED_SPINUP, "spinup hash mismatch")
    require(sha256(args.observation) == EXPECTED_OBS, "JERC obs hash mismatch")
    require(sha256(args.ledger) == EXPECTED_LEDGER, "ledger hash mismatch")
    require(sha256(args.control_pool) == EXPECTED_CONTROL_POOL, "control pool hash mismatch")

    require(set(REQUIRED_POOL_RULES).issubset(set(POOL_RULES)), "POOL_RULES missing Iter014 rules")
    require("diversity_maximin" in POOL_RULES, "default diversity_maximin missing from POOL_RULES")

    for path in COMPILE_TARGETS:
        require(path.is_file(), f"missing compile target {path}")
        py_compile.compile(str(path), doraise=True)

    target = build_coupling_target(
        cases=["JERC_ppe6_I20TRCNPRDCTCBC"],
        resolution="hourly",
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        observation_paths={"JERC": args.observation},
        expected_physical_parameter_count=14,
    )
    require(target["parameter_names"] == PARAMS, "parameter names mismatch")
    require(target["identity"]["sha256"] == EXPECTED_TARGET, "target sha256 mismatch")
    midpoint = 0.5 * (target["pmin"] + target["pmax"])
    logp = float(target["log_posterior"](midpoint))
    require(np.isfinite(logp), "midpoint log posterior is not finite")

    ledger = np.load(args.ledger, allow_pickle=False)
    require("states" in ledger.files and "log_posterior" in ledger.files, "ledger arrays missing")
    states = np.asarray(ledger["states"], dtype=float)
    stored_logp = np.asarray(ledger["log_posterior"], dtype=float)
    require(states.ndim == 2 and states.shape[1] == 15, "ledger state shape")
    require(stored_logp.shape[0] == states.shape[0], "ledger logp length")
    dry_checks = {}
    eligible_rules = []
    for rule in REQUIRED_POOL_RULES:
        try:
            pool, pool_logp, pool_strata, diagnostics = choose_candidate_pool(
                states,
                stored_logp,
                np.asarray(target["pmin"], dtype=float),
                np.asarray(target["pmax"], dtype=float),
                pool_size=640,
                seed=0,
                pool_rule=rule,
                high_l_quantile=0.90,
            )
        except RuntimeError as exc:
            message = str(exc)
            if "pool gate failed" not in message:
                raise
            dry_checks[rule] = {
                "status": "geometry_gate_failed",
                "error": message,
                "pool_rule": rule,
            }
            continue
        require(pool.shape == (640, 15), f"{rule} pool shape")
        require(pool_logp.shape == (640,), f"{rule} pool logp shape")
        require(pool_strata.shape[0] == 640, f"{rule} strata length")
        dry_checks[rule] = {
            "status": "pass",
            "pool_size": int(pool.shape[0]),
            "pool_rule": diagnostics.get("pool_rule", rule),
            "finite_exact_unique": int(diagnostics.get("finite_exact_unique", -1)),
            "normalized_rank": diagnostics.get("normalized_rank"),
            "normalized_condition_number": diagnostics.get("normalized_condition_number"),
            "high_l_quantile_requested": diagnostics.get("high_l_quantile_requested"),
            "high_l_quantile_applied": diagnostics.get("high_l_quantile_applied"),
            "high_l_universe_count": diagnostics.get("high_l_universe_count"),
            "median_pool_logp": float(np.median(pool_logp)),
            "min_pool_logp": float(np.min(pool_logp)),
        }
        eligible_rules.append(rule)

    require(
        dry_checks.get("hybrid_high_l_maximin", {}).get("status") == "pass",
        "hybrid_high_l_maximin must pass pool geometry gates",
    )
    require(eligible_rules, "no eligible pool rules after geometry gates")

    payload = {
        "schema": "spinup-forcing-coupling-iter014-preflight-v1",
        "site": "JERC",
        "resolution": "hourly",
        "target_sha256": target["identity"]["sha256"],
        "ledger_sha256": EXPECTED_LEDGER,
        "control_pool_sha256": EXPECTED_CONTROL_POOL,
        "forcing_sha256": EXPECTED_FORCING,
        "spinup_sha256": EXPECTED_SPINUP,
        "observation_sha256": EXPECTED_OBS,
        "pool_rules": list(POOL_RULES),
        "required_pool_rules": list(REQUIRED_POOL_RULES),
        "eligible_pool_rules": eligible_rules,
        "midpoint_log_posterior": logp,
        "ledger_dry_checks": dry_checks,
        "source_manifest_sha256": sha256(args.source_manifest),
        "dependency_manifest_sha256": sha256(args.dependency_manifest),
        "revision": "geometry_gate_scientific_v1",
        "status": "pass",
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        "PREFLIGHT_PASS eligible="
        + ",".join(eligible_rules)
        + " geometry_failed="
        + ",".join(
            rule
            for rule, item in dry_checks.items()
            if item.get("status") == "geometry_gate_failed"
        )
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
