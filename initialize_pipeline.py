"""General adapter for the reusable coupled candidate-pool initializer.

Workflow launchers should provide a plain configuration to
``initialize_candidate_pool_from_config``.  Scientific search behavior lives in
``model_ELM.coupling_pipeline``; this module owns only configuration translation,
provenance wiring, and the optional command-line interface.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from typing import Any, Mapping

from model_ELM.coupling_pipeline import (
    POOL_RULES,
    build_coupling_target,
    initialize_candidate_pool,
    rebuild_candidate_pool_from_ledger,
)


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def initialize_candidate_pool_from_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Build a configured target and run the reusable candidate-pool initializer."""
    cases = [str(case).strip() for case in config["cases"] if str(case).strip()]
    output = Path(config["output"])
    existing = {path.name for path in output.iterdir()} if output.exists() else set()
    staging = output / ".artifacts.build"
    artifacts = output / "artifacts"
    allowed = {
        "submission_config.env",
        "submit.sh",
        "submission_receipt.env",
        "submission_attempt.env",
        "retry_authorization.env",
    }
    allowed |= {name for name in existing if name.endswith((".out", ".err"))}
    allowed |= {
        name
        for name in existing
        if name.startswith("submission_") and name.endswith((".env", ".env.tmp"))
    }
    allowed |= {
        name for name in existing if name.startswith("submit_") and name.endswith(".slurm")
    }
    allowed.add(staging.name)
    if existing - allowed:
        raise FileExistsError(f"refusing to overwrite initialized pool: {output}")
    output.mkdir(parents=True, exist_ok=True)
    if artifacts.exists():
        raise FileExistsError(f"refusing to overwrite completed pool artifacts: {artifacts}")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    target = build_coupling_target(
        cases=cases,
        resolution=str(config["resolution"]),
        forcing_artifact=config["forcing_artifact"],
        spinup_artifact=config["spinup_artifact"],
        observation_paths=config.get("observation_paths"),
        observation_root=config.get("observation_root"),
        fit_error=bool(config.get("fit_error", True)),
        expected_physical_parameter_count=config.get("expected_physical_parameter_count"),
        target_schema=str(config.get("target_schema", "coupled-target-v1")),
        daily_map_schema=str(config.get("daily_map_schema", "coupled-daily-map-v1")),
    )
    if config.get("site") is not None and target["sites"] != [str(config["site"]).upper()]:
        raise ValueError(f"configured site does not match target membership: {target['sites']}")
    result = initialize_candidate_pool(
        target=target,
        output=staging,
        seed=int(config["seed"]),
        sobol_counts=tuple(int(value) for value in config.get("sobol_counts", (8192, 16384, 32768, 65536))),
        anchor_count=int(config.get("anchor_count", 32)),
        anchor_max_evaluations=int(config.get("anchor_max_evaluations", 512)),
        pool_size=int(config.get("pool_size", 640)),
        pool_rule=str(config.get("pool_rule", "diversity_maximin")),
        high_l_quantile=float(config.get("high_l_quantile", 0.90)),
        provenance={
            "repository_commit": str(config["repository_commit"]),
            "source_manifest_sha256": _sha256(config["source_manifest"]),
            "dependency_manifest_sha256": _sha256(config["dependency_manifest"]),
        },
        contract_schema=str(config.get("contract_schema", "coupling-search-contract-v1")),
        candidate_metadata_schema=str(config.get("candidate_metadata_schema", "coupling-candidate-metadata-v1")),
    )
    staging.replace(artifacts)
    result["artifact_root"] = str(artifacts)
    result["target_identity"] = target["identity"]
    return result


def rebuild_candidate_pool_from_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Rebuild a candidate pool from a frozen ledger under a selected pool rule."""
    cases = [str(case).strip() for case in config["cases"] if str(case).strip()]
    output = Path(config["output"])
    target = build_coupling_target(
        cases=cases,
        resolution=str(config["resolution"]),
        forcing_artifact=config["forcing_artifact"],
        spinup_artifact=config["spinup_artifact"],
        observation_paths=config.get("observation_paths"),
        observation_root=config.get("observation_root"),
        fit_error=bool(config.get("fit_error", True)),
        expected_physical_parameter_count=config.get("expected_physical_parameter_count"),
        target_schema=str(config.get("target_schema", "coupled-target-v1")),
        daily_map_schema=str(config.get("daily_map_schema", "coupled-daily-map-v1")),
    )
    if config.get("site") is not None and target["sites"] != [str(config["site"]).upper()]:
        raise ValueError(f"configured site does not match target membership: {target['sites']}")
    result = rebuild_candidate_pool_from_ledger(
        target=target,
        ledger_path=config["ledger_path"],
        output=output,
        pool_rule=str(config["pool_rule"]),
        high_l_quantile=float(config.get("high_l_quantile", 0.90)),
        pool_size=int(config.get("pool_size", 640)),
        seed=int(config.get("seed", 0)),
        expected_ledger_sha256=config.get("expected_ledger_sha256"),
        provenance={
            "repository_commit": str(config["repository_commit"]),
            "source_manifest_sha256": _sha256(config["source_manifest"]),
            "dependency_manifest_sha256": _sha256(config["dependency_manifest"]),
        },
        contract_schema=str(config.get("contract_schema", "coupling-search-contract-v1")),
        candidate_metadata_schema=str(config.get("candidate_metadata_schema", "coupling-candidate-metadata-v1")),
    )
    result["artifact_root"] = str(Path(output) / "artifacts")
    result["target_identity"] = target["identity"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site")
    parser.add_argument("--resolution", required=True, choices=["hourly", "daily"])
    parser.add_argument("--cases", required=True, help="comma-separated explicit case names")
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument(
        "--observation",
        action="append",
        default=[],
        help="optional SITE=/path/to/observations.nc mapping; repeat per selected site",
    )
    parser.add_argument("--observation-root", type=Path)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--dependency-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--expected-physical-parameter-count", type=int)
    parser.add_argument("--target-schema", default="coupled-target-v1")
    parser.add_argument("--daily-map-schema", default="coupled-daily-map-v1")
    parser.add_argument("--contract-schema", default="coupling-search-contract-v1")
    parser.add_argument("--candidate-metadata-schema", default="coupling-candidate-metadata-v1")
    parser.add_argument("--pool-rule", default="diversity_maximin", choices=list(POOL_RULES))
    parser.add_argument("--high-l-quantile", type=float, default=0.90)
    parser.add_argument("--pool-size", type=int, default=640)
    parser.add_argument("--rebuild-from-ledger", type=Path)
    parser.add_argument("--expected-ledger-sha256")
    args = parser.parse_args()
    observation_paths = {}
    for item in args.observation:
        if "=" not in item:
            raise ValueError(f"invalid --observation mapping: {item}")
        key, value = item.split("=", 1)
        observation_paths[key.strip()] = Path(value).expanduser().resolve()
    config = {
        "site": args.site, "resolution": args.resolution,
        "cases": args.cases.split(","), "forcing_artifact": args.forcing_artifact,
        "spinup_artifact": args.spinup_artifact, "repository_commit": args.repository_commit,
        "source_manifest": args.source_manifest, "dependency_manifest": args.dependency_manifest,
        "output": args.output,
        "expected_physical_parameter_count": args.expected_physical_parameter_count,
        "observation_paths": observation_paths,
        "observation_root": args.observation_root,
        "target_schema": args.target_schema,
        "daily_map_schema": args.daily_map_schema,
        "contract_schema": args.contract_schema,
        "candidate_metadata_schema": args.candidate_metadata_schema,
        "pool_rule": args.pool_rule,
        "high_l_quantile": args.high_l_quantile,
        "pool_size": args.pool_size,
    }
    if args.rebuild_from_ledger is not None:
        config["seed"] = int(args.seed if args.seed is not None else 0)
        config["ledger_path"] = args.rebuild_from_ledger
        config["expected_ledger_sha256"] = args.expected_ledger_sha256
        rebuild_candidate_pool_from_config(config)
        print(
            f"REBUILD_PASS site={args.site or 'configured'} pool_rule={args.pool_rule}"
        )
        return 0
    if args.seed is None:
        raise ValueError("--seed is required for full initialization")
    config["seed"] = int(args.seed)
    initialize_candidate_pool_from_config(config)
    print(f"INITIALIZE_PASS site={args.site or 'configured'} pool_rule={args.pool_rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
