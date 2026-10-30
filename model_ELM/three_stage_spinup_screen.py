"""Compact repeated-split screening helpers for three-stage spinup Iter003."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import numpy as np

from .three_stage_data import LoadedRows, SITES, TARGETS, require
from .three_stage_spinup import fit_compact_models, metric_rows, predict_compact_models


LAYER_CHOICES = ((16,), (32,), (64,), (128,), (16, 8), (32, 16), (64, 32), (128, 64))
ACTIVATIONS = ("tanh", "relu")
ALPHAS = (0.0, 1.0, 10.0, 40.0, 100.0, 300.0)
SPLIT_SEED = 20261030


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def candidate_manifest() -> Dict[str, Any]:
    candidates: List[Dict[str, Any]] = []
    for layers in LAYER_CHOICES:
        for activation in ACTIVATIONS:
            for alpha in ALPHAS:
                config = {
                    "hidden_layer_sizes": list(layers),
                    "activation": activation,
                    "solver": "lbfgs",
                    "alpha": alpha,
                    "max_iter": 800,
                    "random_state": 42,
                }
                candidates.append({
                    "candidate_id": len(candidates),
                    "config": config,
                    "config_sha256": canonical_hash(config),
                    "is_iter002_baseline": config == {
                        "hidden_layer_sizes": [32], "activation": "tanh", "solver": "lbfgs",
                        "alpha": 40.0, "max_iter": 800, "random_state": 42,
                    },
                })
    require(len(candidates) == 96, "candidate count mismatch")
    require(sum(bool(item["is_iter002_baseline"]) for item in candidates) == 1, "baseline count mismatch")
    return {"schema": "three-stage-spinup-iter003-candidates-v1", "candidates": candidates}


def balanced_split_manifest(development_members: Sequence[str]) -> Dict[str, Any]:
    members = tuple(str(value) for value in development_members)
    require(len(members) == 819 and len(set(members)) == 819, "development population mismatch")
    rng = np.random.default_rng(SPLIT_SEED)
    used_extras: set[str] = set()
    splits: List[Dict[str, Any]] = []
    member_array = np.asarray(members, dtype="U6")
    for round_index in range(4):
        permuted = member_array[rng.permutation(member_array.size)].tolist()
        groups = [permuted[index * 164:(index + 1) * 164] for index in range(4)]
        groups.append(permuted[656:])
        extra = next(member for member in permuted[:656] if member not in used_extras)
        used_extras.add(extra)
        groups[4].append(extra)
        for fold_index, validation in enumerate(groups):
            validation_set = set(validation)
            train = [member for member in members if member not in validation_set]
            require(len(validation) == 164 and len(validation_set) == 164, "validation split mismatch")
            require(len(train) == 655, "training split mismatch")
            splits.append({
                "split_id": len(splits),
                "round": round_index,
                "fold": fold_index,
                "train_member_ids": train,
                "validation_member_ids": validation,
            })
    counts = {member: 0 for member in members}
    for split in splits:
        for member in split["validation_member_ids"]:
            counts[member] += 1
    require(len(splits) == 20, "split count mismatch")
    require(sorted(counts.values()).count(4) == 815, "four-appearance count mismatch")
    require(sorted(counts.values()).count(5) == 4, "five-appearance count mismatch")
    return {
        "schema": "three-stage-spinup-iter003-splits-v1",
        "seed": SPLIT_SEED,
        "development_count": 819,
        "train_count": 655,
        "validation_count": 164,
        "splits": splits,
        "validation_appearance_counts": counts,
    }


def subset_rows(loaded: LoadedRows, members: Sequence[str]) -> LoadedRows:
    selected = set(str(value) for value in members)
    mask = np.asarray([str(value) in selected for value in loaded.member_id], dtype=bool)
    require(int(mask.sum()) == len(SITES) * len(selected), "row subset coverage mismatch")
    return LoadedRows(
        X=loaded.X[mask],
        y=None if loaded.y is None else loaded.y[mask],
        site=loaded.site[mask],
        member_id=loaded.member_id[mask],
        parameter_names=loaded.parameter_names,
        feature_names=loaded.feature_names,
    )


def run_candidate(
    loaded: LoadedRows,
    candidate: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    *,
    split_limit: int | None = None,
) -> Dict[str, Any]:
    splits = list(split_manifest["splits"])
    if split_limit is not None:
        require(split_limit >= 1, "split limit must be positive")
        splits = splits[:split_limit]
    metrics: List[Dict[str, Any]] = []
    convergence: List[Dict[str, Any]] = []
    timings: List[Dict[str, Any]] = []
    for split in splits:
        start = time.monotonic()
        train = subset_rows(loaded, split["train_member_ids"])
        validation = subset_rows(loaded, split["validation_member_ids"])
        fitted = fit_compact_models(train, candidate["config"])
        train_prediction = predict_compact_models(fitted, train.X)
        validation_prediction = predict_compact_models(fitted, validation.X)
        split_rows = metric_rows("iter003_screen", train, train_prediction, validation, validation_prediction)
        for row in split_rows:
            metrics.append({"candidate_id": int(candidate["candidate_id"]), "split_id": int(split["split_id"]), **row})
        for target in TARGETS:
            convergence.append({
                "candidate_id": int(candidate["candidate_id"]),
                "split_id": int(split["split_id"]),
                "target": target,
                **fitted["convergence"][target],
            })
        timings.append({"split_id": int(split["split_id"]), "elapsed_seconds": time.monotonic() - start})
    require(len(metrics) == len(splits) * 24, "metric row count mismatch")
    require(len(convergence) == len(splits) * len(TARGETS), "convergence row count mismatch")
    return {
        "schema": "three-stage-spinup-iter003-candidate-result-v1",
        "candidate_id": int(candidate["candidate_id"]),
        "config": dict(candidate["config"]),
        "config_sha256": str(candidate["config_sha256"]),
        "is_iter002_baseline": bool(candidate["is_iter002_baseline"]),
        "split_count": len(splits),
        "metrics": metrics,
        "convergence": convergence,
        "timings": timings,
    }


def write_candidate_result(directory: Path, result: Mapping[str, Any], source_identity: Mapping[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    payload = {**dict(result), "source_identity": dict(source_identity), "status": "complete"}
    json_path = directory / "result.json"
    temporary = directory / ".result.json.tmp"
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, json_path)
    metrics_path = directory / "metrics.csv"
    rows = list(result["metrics"])
    fieldnames = [
        "candidate_id", "split_id", "run_kind", "partition", "site", "target", "scale",
        "n", "r2", "rmse", "mae", "bias", "residual_std",
    ]
    with metrics_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fieldnames} for row in rows)
