#!/usr/bin/env python
"""Run one Iter003 MLP candidate from explicit CLI configuration."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require
from model_ELM.three_stage_spinup import normalize_mlp_config
from model_ELM.three_stage_spinup_screen import canonical_hash, run_candidate, write_candidate_result


def parse_layers(value: str) -> list[int]:
    try:
        layers = [int(item) for item in value.split(",") if item]
    except ValueError as error:
        raise argparse.ArgumentTypeError("invalid hidden-layer list") from error
    if not layers:
        raise argparse.ArgumentTypeError("hidden-layer list is empty")
    return layers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--candidate-manifest", required=True, type=Path)
    parser.add_argument("--split-manifest", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True, type=int)
    parser.add_argument("--hidden-layers", required=True, type=parse_layers)
    parser.add_argument("--activation", required=True, choices=("tanh", "relu"))
    parser.add_argument("--solver", required=True, choices=("lbfgs",))
    parser.add_argument("--alpha", required=True, type=float)
    parser.add_argument("--max-iter", required=True, type=int)
    parser.add_argument("--random-state", required=True, type=int)
    parser.add_argument("--attempt", required=True, type=int)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--split-limit", type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be in 1..4")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-spinup-iter003-config-v1", "config schema mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    candidates = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
    splits = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    require(candidates["schema"] == "three-stage-spinup-iter003-candidates-v1", "candidate schema mismatch")
    require(splits["schema"] == "three-stage-spinup-iter003-splits-v1", "split schema mismatch")
    require(0 <= args.candidate_id < len(candidates["candidates"]), "candidate ID out of range")
    candidate = candidates["candidates"][args.candidate_id]
    supplied = normalize_mlp_config({
        "hidden_layer_sizes": args.hidden_layers,
        "activation": args.activation,
        "solver": args.solver,
        "alpha": args.alpha,
        "max_iter": args.max_iter,
        "random_state": args.random_state,
    })
    require(candidate["config"] == supplied, "CLI and candidate-manifest config mismatch")
    require(candidate["config_sha256"] == canonical_hash(supplied), "candidate config hash mismatch")
    loaded = snapshot.load_rows(snapshot.development_ranked, include_targets=True)
    result = run_candidate(loaded, candidate, splits, split_limit=args.split_limit)
    write_candidate_result(args.output_directory, result, {
        "repository_base_commit": config["repository_base_commit"],
        "execution_manifest_sha256": os.environ.get("ITER003_EXECUTION_MANIFEST_SHA256"),
        "config_sha256": os.environ.get("ITER003_CONFIG_SHA256"),
        "candidate_manifest_sha256": os.environ.get("ITER003_CANDIDATE_MANIFEST_SHA256"),
        "split_manifest_sha256": os.environ.get("ITER003_SPLIT_MANIFEST_SHA256"),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "attempt": args.attempt,
    })
    print(f"ITER003_CANDIDATE_OK candidate={args.candidate_id} splits={result['split_count']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
