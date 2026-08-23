#!/usr/bin/env python3
"""Stage adapter for the universal coupled-optimization YAML contract.

This adapter deliberately does not submit jobs. Slurm wrappers select one stage
and one external output directory, while this module translates only that YAML
section to the established initializer or optimizer CLI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from initialize_pipeline import (
    initialize_candidate_pool_from_config,
    rebuild_candidate_pool_from_config,
)
from model_ELM.optimization_config import load_campaign, write_stage_manifest


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
_INITIALIZATION_ARTIFACTS = (
    "candidate_pool.npz",
    "candidate_ledger.npz",
    "candidate_metadata.json",
    "diversity_diagnostics.json",
    "initialization_report.json",
    "search_contract.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _reuse_complete_initialization_artifacts(
    output: Path, shared: dict, stage: dict, *, repository_commit: str,
    source_manifest: Path, dependency_manifest: Path,
) -> dict | None:
    """Recover only a missing stage receipt after verified immutable artifacts exist."""
    artifacts = output / "artifacts"
    if not artifacts.exists():
        return None
    if (output / "stage_manifest.json").exists():
        raise FileExistsError(f"existing stage receipt requires a new output directory: {output}")
    manifest_path = artifacts / "artifact_manifest.json"
    manifest = _read_json(manifest_path)
    if manifest.get("schema") != "coupling-initialization-artifact-manifest-v1" or manifest.get("status") != "pass":
        raise ValueError(f"unverified initialization artifact manifest: {manifest_path}")
    recorded = manifest.get("artifacts")
    if not isinstance(recorded, dict) or set(recorded) != set(_INITIALIZATION_ARTIFACTS):
        raise ValueError(f"incomplete initialization artifact manifest: {manifest_path}")
    for name in _INITIALIZATION_ARTIFACTS:
        artifact = artifacts / name
        if not artifact.is_file() or recorded[name] != _sha256(artifact):
            raise ValueError(f"initialization artifact hash mismatch: {artifact}")
    metadata = _read_json(artifacts / "candidate_metadata.json")
    diagnostics = _read_json(artifacts / "diversity_diagnostics.json")
    report = _read_json(artifacts / "initialization_report.json")
    search_contract = _read_json(artifacts / "search_contract.json")
    identity = search_contract.get("target_identity")
    if not isinstance(identity, dict):
        raise ValueError("initialization search contract lacks target identity")
    if identity.get("cases") != list(shared["cases"]) or identity.get("sites") != list(shared["sites"]):
        raise ValueError("existing initialization artifacts do not match campaign membership")
    if identity.get("resolution") != stage["resolution"] or search_contract.get("resolution") != stage["resolution"]:
        raise ValueError("existing initialization artifacts do not match campaign resolution")
    if search_contract.get("pool_gate", {}).get("pool_rule") != stage["pool_rule"]:
        raise ValueError("existing initialization artifacts do not match campaign pool rule")
    if metadata.get("pool_sha256") != recorded["candidate_pool.npz"]:
        raise ValueError("candidate metadata does not attest the recorded pool")
    if diagnostics.get("selected_count") != stage["pool_size"] or report.get("status") != "pass":
        raise ValueError("existing initialization artifacts do not satisfy the candidate-pool gate")
    contract_hashes = {
        "pool_sha256": "candidate_pool.npz",
        "ledger_sha256": "candidate_ledger.npz",
        "candidate_metadata_sha256": "candidate_metadata.json",
        "diversity_diagnostics_sha256": "diversity_diagnostics.json",
        "initialization_report_sha256": "initialization_report.json",
    }
    for field, name in contract_hashes.items():
        if search_contract.get(field) != recorded[name]:
            raise ValueError(f"initialization search contract hash mismatch: {field}")
    if identity.get("sha256") != metadata.get("target_sha256"):
        raise ValueError("candidate metadata does not attest the search-contract target")
    for path_key, hash_key in (("forcing_artifact", "forcing_artifact_sha256"),
                               ("spinup_artifact", "spinup_artifact_sha256")):
        path = Path(identity.get(path_key, ""))
        if not path.is_file() or identity.get(hash_key) != _sha256(path):
            raise ValueError(f"search-contract dependency identity mismatch: {path_key}")
    for detail in identity.get("sites_detail", {}).values():
        observation = Path(detail.get("observation_path", ""))
        if not observation.is_file() or detail.get("observation_sha256") != _sha256(observation):
            raise ValueError("search-contract observation identity mismatch")
    if stage["mode"] == "ledger_rebuild":
        evaluations = metadata.get("evaluations")
        if not isinstance(evaluations, list) or len(evaluations) != 1:
            raise ValueError("ledger-rebuild artifacts lack their single source-ledger receipt")
        evaluation = evaluations[0]
        ledger = Path(stage["ledger_path"])
        if (evaluation.get("kind") != "ledger_rebuild"
                or evaluation.get("source_ledger") != str(ledger)
                or evaluation.get("source_ledger_sha256") != _sha256(ledger)):
            raise ValueError("ledger-rebuild artifacts do not match the configured source ledger")
    predecessor = {
        "repository_commit": search_contract.get("repository_commit"),
        "source_manifest_sha256": search_contract.get("source_manifest_sha256"),
        "dependency_manifest_sha256": search_contract.get("dependency_manifest_sha256"),
    }
    if not all(isinstance(value, str) and value for value in predecessor.values()):
        raise ValueError("initialization search contract lacks complete package provenance")
    successor = {
        "repository_commit": repository_commit,
        "source_manifest_sha256": _sha256(source_manifest),
        "dependency_manifest_sha256": _sha256(dependency_manifest),
    }
    transition = {
        "schema": "coupling-pool-provenance-transition-v1",
        "reason": "initialization_stage_receipt_serialization_recovery",
        "predecessor": predecessor,
        "successor": successor,
        "artifact_manifest_sha256": _sha256(manifest_path),
        "target_identity_sha256": identity["sha256"],
        "artifact_hashes": {field: search_contract[field] for field in contract_hashes},
    }
    transition_path = output / "pool_provenance_transition.json"
    encoded = json.dumps(transition, indent=2, sort_keys=True) + "\n"
    if transition_path.exists():
        if transition_path.read_text(encoding="utf-8") != encoded:
            raise FileExistsError(f"existing pool provenance transition differs: {transition_path}")
    else:
        transition_path.write_text(encoded, encoding="utf-8")
    return {
        "reused_complete_artifacts": True,
        "artifact_root": str(artifacts.resolve()),
        "artifact_manifest_sha256": _sha256(manifest_path),
        "candidate_pool_sha256": recorded["candidate_pool.npz"],
        "candidate_ledger_sha256": recorded["candidate_ledger.npz"],
        "pool_provenance_transition": str(transition_path.resolve()),
        "pool_provenance_transition_sha256": _sha256(transition_path),
        "artifact_predecessor": predecessor,
        "production_successor": successor,
    }


def _observation_pairs(shared: dict) -> list[str]:
    observations = shared.get("observations", {})
    return [f"{site}:{observations[site]}" for site in shared["sites"]]


def _initialize(args: argparse.Namespace) -> int:
    contract = load_campaign(args.campaign, "initialization")
    shared, stage = contract["shared"], contract["initialization"]
    reused = _reuse_complete_initialization_artifacts(
        Path(args.output), shared, stage, repository_commit=args.repository_commit,
        source_manifest=args.source_manifest, dependency_manifest=args.dependency_manifest,
    )
    if reused is not None:
        write_stage_manifest(args.output, {**contract, "output": str(Path(args.output).resolve()), "result": reused})
        print(f"INITIALIZATION_PASS sites={','.join(shared['sites'])} mode={stage['mode']} reused_artifacts=true")
        return 0
    config = {
        "cases": shared["cases"], "resolution": stage["resolution"],
        "forcing_artifact": shared["forcing_artifact"], "spinup_artifact": shared["spinup_artifact"],
        "observation_paths": shared.get("observations", {}), "fit_error": True,
        "repository_commit": args.repository_commit, "source_manifest": args.source_manifest,
        "dependency_manifest": args.dependency_manifest, "output": args.output,
        "seed": stage["seed"], "pool_rule": stage["pool_rule"], "pool_size": stage["pool_size"],
        "high_l_quantile": stage.get("high_l_quantile", 0.90),
        "expected_physical_parameter_count": 14,
    }
    if stage["mode"] == "ledger_rebuild":
        config["ledger_path"] = stage["ledger_path"]
        result = rebuild_candidate_pool_from_config(config)
    elif stage["mode"] == "fresh":
        result = initialize_candidate_pool_from_config(config)
    else:
        raise ValueError(f"unsupported initialization.mode: {stage['mode']}")
    write_stage_manifest(args.output, {**contract, "output": str(Path(args.output).resolve()), "result": result})
    print(f"INITIALIZATION_PASS sites={','.join(shared['sites'])} mode={stage['mode']}")
    return 0


def _optimize(args: argparse.Namespace) -> int:
    contract = load_campaign(args.campaign, "optimization")
    shared, stage = contract["shared"], contract["optimization"]
    command = [
        sys.executable, str(REPO_ROOT / "optimize_surrogate_forcing.py"),
        "--case", ",".join(shared["cases"]), "--artifact", shared["forcing_artifact"],
        "--vars", ",".join(shared["variables"]), "--obs", ",".join(_observation_pairs(shared)),
        "--spinup-mode", "coupled", "--spinup-artifact", shared["spinup_artifact"],
        "--nwalkers", str(stage["nwalkers"]), "--nsteps", str(stage["nsteps"]),
        "--n-processes", str(args.n_processes), "--seed", str(args.seed),
        "--sampler-coordinates", stage["sampler_coordinates"],
        "--move-configuration", stage["move_configuration"], "--de-move-scale", str(stage["de_move_scale"]),
        "--likelihood-resolution", stage["likelihood_resolution"], "--candidate-pool", str(args.pool),
        "--repository-commit", args.repository_commit, "--source-manifest", str(args.source_manifest),
        "--dependency-manifest", str(args.dependency_manifest), "--expected-physical-parameter-count", "14",
        "--checkpoint-interval", str(stage["checkpoint_interval"]), "--backend", str(Path(args.output) / "backend.h5"),
        "--workdir", str(REPO_ROOT), "--outputdir", str(args.output), "--flat-output", "--write-diagnostics",
    ]
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        return completed.returncode
    write_stage_manifest(args.output, {**contract, "output": str(Path(args.output).resolve()), "seed": args.seed, "pool": str(Path(args.pool).resolve())})
    print(f"OPTIMIZATION_PASS sites={','.join(shared['sites'])} seed={args.seed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=["initialization", "optimization"])
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--dependency-manifest", type=Path, required=True)
    parser.add_argument("--pool", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--n-processes", type=int, default=1)
    args = parser.parse_args()
    if args.stage == "initialization":
        return _initialize(args)
    if args.pool is None or args.seed is None:
        parser.error("optimization requires --pool and --seed")
    return _optimize(args)


if __name__ == "__main__":
    raise SystemExit(main())
