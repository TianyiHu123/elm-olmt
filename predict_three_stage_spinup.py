#!/usr/bin/env python
"""Predict C/N from one trusted Iter002 development artifact for an exact member subset."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import SITES, TARGETS, ThreeStageSnapshot, read_member_file, require
from model_ELM.three_stage_spinup_artifact import load_artifact, predict_matrix


def resolve_members(args: argparse.Namespace, snapshot: ThreeStageSnapshot) -> tuple[str, ...]:
    if args.members_file is not None:
        return snapshot.resolve_development_members(read_member_file(args.members_file))
    require(args.member_set == "development", "only development member-set is authorized")
    if args.member_count == "all":
        count = len(snapshot.development_ranked)
    else:
        require(str(args.member_count).isdigit(), "member-count must be a positive integer or all")
        count = int(args.member_count)
    require(1 <= count <= len(snapshot.development_ranked), "member-count outside development range")
    return snapshot.development_ranked[:count]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--snapshot-root", required=True, type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--members-file", type=Path)
    selection.add_argument("--member-set", choices=("development",))
    parser.add_argument("--member-count", default="all")
    parser.add_argument("--sites", default="ABBY,JERC")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.members_file is not None:
        require(args.member_count == "all", "member-count cannot accompany members-file")
    snapshot = ThreeStageSnapshot(args.snapshot_root, verify_component_hashes=True)
    artifact, artifact_path, manifest = load_artifact(args.artifact_dir)
    require(artifact["snapshot_sha256"] == snapshot.snapshot_sha256, "artifact/snapshot identity mismatch")
    sites = tuple(value.strip() for value in args.sites.split(",") if value.strip())
    require(bool(sites) and all(site in SITES for site in sites), "invalid site selection")
    members = resolve_members(args, snapshot)
    loaded = snapshot.load_rows(members, sites=sites, include_targets=False)
    require(list(loaded.feature_names) == list(artifact["feature_names"]), "artifact/input feature order mismatch")
    prediction = predict_matrix(artifact, loaded.X).reshape(len(sites), len(members), len(TARGETS))
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with Dataset(str(output), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-spinup-predictions-v1"
        dataset.artifact_role = artifact["artifact_role"]
        dataset.target_transform = artifact["target_transform"]
        dataset.artifact_sha256 = manifest["artifact_sha256"]
        dataset.snapshot_sha256 = snapshot.snapshot_sha256
        dataset.feature_schema_sha256 = artifact["feature_schema_sha256"]
        dataset.member_selection_json = json.dumps(list(members), separators=(",", ":"))
        dataset.createDimension("site", len(sites))
        dataset.createDimension("member", len(members))
        site_var = dataset.createVariable("site", str, ("site",))
        site_var[:] = np.asarray(sites, dtype=object)
        member_var = dataset.createVariable("member_id", str, ("member",))
        member_var[:] = np.asarray(members, dtype=object)
        train_set = set(artifact["fit_scope"]["train_member_ids"])
        was_training = dataset.createVariable("was_training_member", "i1", ("member",))
        was_training[:] = np.asarray([member in train_set for member in members], dtype=np.int8)
        for target_index, target in enumerate(TARGETS):
            variable = dataset.createVariable(target, "f8", ("site", "member"), zlib=True, complevel=4)
            variable[:] = prediction[:, :, target_index]
            variable.units = "gC/m^2" if target == "TOTSOMC" else "gN/m^2"
            variable.target_definition = "soil1-soil4 full-profile integral over 10 active decomposition layers"
    print(
        f"ITER002_PREDICT_OK members={len(members)} sites={','.join(sites)} "
        f"artifact_sha256={manifest['artifact_sha256']} output={output}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
