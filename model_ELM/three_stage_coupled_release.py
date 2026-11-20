"""Coupled all-development artifact and gated inference contract.

This module is intentionally distinct from the three historical stage-level release contracts and
from Iter015 fold artifacts.  It owns one coupled artifact set fitted on the immutable 819-member
development partition and never needs ELM targets for inference.
"""
from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .three_stage_data import ThreeStageSnapshot, require, sha256_file
from .three_stage_inference import FoldThreeStageInference


RELEASE_NAME = "release_0001"
PACKAGE_SCHEMA = "three-stage-coupled-artifact-package-v1"
SPINUP_SCHEMA = "three-stage-spinup-coupled-release-v1"
GPP_SCHEMA = "three-stage-gpp-coupled-release-v1"
SR_SCHEMA = "three-stage-sr-coupled-release-v1"
GPP_POLICY = "hard_zero_v1"
ARTIFACT_FILENAMES = {
    "spinup": "spinup_coupled_release.pkl",
    "gpp": "gpp_coupled_release.pkl",
    "sr": "sr_coupled_release.pkl",
}


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_one(
    artifact: Mapping[str, Any], *, schema: str, feature_count: int, snapshot: ThreeStageSnapshot
) -> None:
    require(artifact.get("schema") == schema, f"coupled artifact schema mismatch: {schema}")
    require(artifact.get("release_name") == RELEASE_NAME, "coupled release name mismatch")
    require(artifact.get("snapshot_sha256") == snapshot.snapshot_sha256, "coupled snapshot mismatch")
    require(artifact.get("global_split_sha256") == sha256_file(snapshot.split_path), "coupled split mismatch")
    members = list(artifact.get("training_member_ids", []))
    require(members == list(snapshot.development_ranked), "coupled training-member order mismatch")
    require(len(members) == 819 and len(set(members)) == 819, "coupled training scope mismatch")
    require(not set(members).intersection(snapshot.fixed_test_set), "coupled artifact contains fixed-test member")
    require(len(artifact.get("feature_names", [])) == feature_count, "coupled feature count mismatch")
    require(artifact.get("upstream_prediction_mode") == "direct_in_sample", "coupled upstream mode mismatch")
    require(artifact.get("fixed_test_fit_access") is False, "coupled fixed-test fit flag mismatch")


def validate_artifacts(
    snapshot: ThreeStageSnapshot,
    spinup: Mapping[str, Any],
    gpp: Mapping[str, Any],
    sr: Mapping[str, Any],
) -> None:
    _validate_one(spinup, schema=SPINUP_SCHEMA, feature_count=25, snapshot=snapshot)
    _validate_one(gpp, schema=GPP_SCHEMA, feature_count=43, snapshot=snapshot)
    _validate_one(sr, schema=SR_SCHEMA, feature_count=44, snapshot=snapshot)
    for artifact in (spinup, gpp, sr):
        require(artifact.get("training_member_ids") == spinup.get("training_member_ids"), "coupled fit scopes differ")
    require(gpp.get("gpp_output_policy") == GPP_POLICY, "coupled GPP policy mismatch")
    require(sr.get("gpp_output_policy") == GPP_POLICY, "coupled SR policy mismatch")


def validate_manifest(
    manifest: Mapping[str, Any],
    snapshot: ThreeStageSnapshot,
    artifacts: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    require(manifest.get("schema") == PACKAGE_SCHEMA, "coupled package schema mismatch")
    require(manifest.get("release_name") == RELEASE_NAME, "coupled package release mismatch")
    require(manifest.get("snapshot_sha256") == snapshot.snapshot_sha256, "coupled package snapshot mismatch")
    require(manifest.get("global_split_sha256") == sha256_file(snapshot.split_path), "coupled package split mismatch")
    require(manifest.get("training_partition") == "development", "coupled package training partition mismatch")
    require(int(manifest.get("training_member_count", -1)) == 819, "coupled package training count mismatch")
    members = list(manifest.get("training_member_ids", []))
    require(members == list(snapshot.development_ranked), "coupled package training members mismatch")
    require(not set(members).intersection(snapshot.fixed_test_set), "coupled package includes fixed-test member")
    require(manifest.get("fixed_test_fit_access") is False, "coupled package fixed-test flag mismatch")
    require(manifest.get("upstream_prediction_mode") == "direct_in_sample", "coupled package upstream mode mismatch")
    require(manifest.get("gpp_output_policy") == GPP_POLICY, "coupled package GPP policy mismatch")
    require(manifest.get("feature_counts") == {"spinup": 25, "gpp": 43, "sr": 44}, "coupled package feature counts mismatch")
    records = {str(item.get("stage")): item for item in manifest.get("files", [])}
    require(set(records) == set(ARTIFACT_FILENAMES), "coupled artifact inventory mismatch")
    expected_schemas = {"spinup": SPINUP_SCHEMA, "gpp": GPP_SCHEMA, "sr": SR_SCHEMA}
    for stage, filename in ARTIFACT_FILENAMES.items():
        record = records[stage]
        require(record.get("path") == filename, f"coupled {stage} filename mismatch")
        require(record.get("schema") == expected_schemas[stage], f"coupled {stage} record schema mismatch")
        require(isinstance(record.get("sha256"), str) and len(record["sha256"]) == 64, f"coupled {stage} record hash invalid")
        require(int(record.get("size_bytes", -1)) > 0, f"coupled {stage} record size invalid")
        if artifacts is not None:
            artifact = artifacts[stage]
            require(record["schema"] == artifact.get("schema"), f"coupled {stage} manifest/artifact schema mismatch")
            require(artifact.get("training_member_ids") == members, f"coupled {stage} manifest/artifact scope mismatch")
            require(len(artifact.get("feature_names", [])) == manifest["feature_counts"][stage], f"coupled {stage} manifest/artifact feature mismatch")


def save_artifacts(
    directory: Path | str,
    snapshot: ThreeStageSnapshot,
    spinup: Mapping[str, Any],
    gpp: Mapping[str, Any],
    sr: Mapping[str, Any],
    *,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    validate_artifacts(snapshot, spinup, gpp, sr)
    root = Path(directory)
    require(not root.exists(), f"coupled artifact directory exists: {root}")
    root.mkdir(parents=True)
    artifacts = {"spinup": dict(spinup), "gpp": dict(gpp), "sr": dict(sr)}
    files: list[dict[str, Any]] = []
    for stage, artifact in artifacts.items():
        path = root / ARTIFACT_FILENAMES[stage]
        with path.open("xb") as handle:
            pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
        files.append({
            "stage": stage,
            "path": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "schema": artifact["schema"],
        })
    manifest = {
        "schema": PACKAGE_SCHEMA,
        "release_name": RELEASE_NAME,
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": sha256_file(snapshot.split_path),
        "training_partition": "development",
        "training_member_count": 819,
        "training_member_ids": list(snapshot.development_ranked),
        "fixed_test_fit_access": False,
        "upstream_prediction_mode": "direct_in_sample",
        "gpp_output_policy": GPP_POLICY,
        "feature_counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "provenance": dict(provenance),
        "files": files,
    }
    validate_manifest(manifest, snapshot, artifacts)
    _write_json(root / "artifact_manifest.json", manifest)
    return manifest


def load_artifacts(
    directory: Path | str, snapshot: ThreeStageSnapshot
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = Path(directory)
    manifest_path = root / "artifact_manifest.json"
    require(manifest_path.is_file(), "coupled artifact manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, snapshot)
    records = {str(item["stage"]): item for item in manifest.get("files", [])}
    loaded: dict[str, dict[str, Any]] = {}
    for stage, filename in ARTIFACT_FILENAMES.items():
        record = records[stage]
        require(record.get("path") == filename, f"coupled {stage} filename mismatch")
        path = root / filename
        require(path.is_file(), f"coupled {stage} artifact missing")
        require(path.stat().st_size == int(record["size_bytes"]), f"coupled {stage} size mismatch")
        require(sha256_file(path) == record["sha256"], f"coupled {stage} hash mismatch")
        with path.open("rb") as handle:
            value = pickle.load(handle)
        require(isinstance(value, dict), f"coupled {stage} artifact type mismatch")
        loaded[stage] = value
    validate_artifacts(snapshot, loaded["spinup"], loaded["gpp"], loaded["sr"])
    validate_manifest(manifest, snapshot, loaded)
    return loaded["spinup"], loaded["gpp"], loaded["sr"], manifest


@dataclass(frozen=True)
class CoupledInferenceResult:
    site: str
    parameter_names: tuple[str, ...]
    parameters: np.ndarray
    time: np.ndarray
    totsomc: np.ndarray
    totsomn: np.ndarray
    gpp_raw: np.ndarray
    gpp: np.ndarray
    sr: np.ndarray
    provenance: dict[str, Any]


class CoupledThreeStageInference:
    """Target-free inference from one coupled all-development artifact set."""

    def __init__(
        self,
        snapshot: ThreeStageSnapshot,
        spinup: Mapping[str, Any],
        gpp: Mapping[str, Any],
        sr: Mapping[str, Any],
        manifest: Mapping[str, Any],
    ) -> None:
        validate_artifacts(snapshot, spinup, gpp, sr)
        validate_manifest(manifest, snapshot, {"spinup": spinup, "gpp": gpp, "sr": sr})
        self.snapshot = snapshot
        self.manifest = dict(manifest)
        adapted = []
        for stage, artifact in (("spinup", spinup), ("gpp", gpp), ("sr", sr)):
            value = dict(artifact)
            value["schema"] = f"three-stage-{stage}-fold-artifact-v1"
            value["split_id"] = -1
            value["train_member_ids"] = list(value["training_member_ids"])
            adapted.append(value)
        self._engine = FoldThreeStageInference(
            snapshot, adapted[0], adapted[1], adapted[2], split_id=-1,
            gpp_output_policy=GPP_POLICY,
        )

    def validate_parameters(self, parameters: Sequence[float] | np.ndarray) -> np.ndarray:
        return self._engine.validate_parameters(parameters)

    def predict_to_arrays(self, *args: Any, **kwargs: Any) -> np.ndarray:
        return self._engine.predict_to_arrays(*args, **kwargs)

    def predict(self, *args: Any, **kwargs: Any) -> CoupledInferenceResult:
        result = self._engine.predict(*args, **kwargs)
        provenance = {
            "schema": "three-stage-coupled-inference-v1",
            "release_name": RELEASE_NAME,
            "snapshot_sha256": self.snapshot.snapshot_sha256,
            "global_split_sha256": sha256_file(self.snapshot.split_path),
            "training_partition": "development",
            "training_member_count": 819,
            "upstream_prediction_mode": "direct_in_sample",
            "gpp_output_policy": GPP_POLICY,
            "site": result.site,
            "start": int(result.time[0]) if result.time.size else None,
            "end": int(result.time[-1]) + 1 if result.time.size else None,
            "contains_elm_truth": False,
            "training_or_fitting": False,
        }
        return CoupledInferenceResult(
            site=result.site,
            parameter_names=result.parameter_names,
            parameters=result.parameters,
            time=result.time,
            totsomc=result.totsomc,
            totsomn=result.totsomn,
            gpp_raw=result.gpp_raw,
            gpp=result.gpp,
            sr=result.sr,
            provenance=provenance,
        )
