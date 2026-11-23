"""Fail-closed loader for the published PPE1 coupled three-stage release."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from .mcmc_prior import PPE1, Prior18
from .three_stage_coupled_release import CoupledThreeStageInference, load_artifacts
from .three_stage_data import ThreeStageSnapshot, sha256_file


EXPECTED_RELEASE_MANIFEST_SHA256 = "4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a"
EXPECTED_CATALOG_SHA256 = "89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da"
EXPECTED_SNAPSHOT_SHA256 = "39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a"
EXPECTED_SPLIT_SHA256 = "99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce"
EXPECTED_SOURCE_SHA256 = "9483e27eefe23f553c68ee9b174cbb2b5975efd1c631c1d5e453594987b45fc2"
EXPECTED_ENGINE_SOURCE_SHA256 = "733483741533c38ffab26d8a6378d64d19f0691646018b3afbc8861087403dda"
EXPECTED_UNIT_SOURCE_HASHES = {
    "three_stage_spinup.py": "841b162ebc08e4cb4df26f2c183d7fa3f9eb9ec4c008187c0698d9a4f7616c56",
    "three_stage_gpp.py": "e2c22e556a2b23901dc6ca38feadcac9b8c7a7d96032c8de07f37d486bc3a818",
    "three_stage_sr.py": "b1db611c3fa3592623f7fdddf515b67331a42fb210001461a11bee511fb38710",
    "three_stage_inference.py": EXPECTED_ENGINE_SOURCE_SHA256,
}
OUTPUT_UNITS = {"TOTSOMC": "gC/m^2", "TOTSOMN": "gN/m^2", "GPP": "gC/m^2/day", "SR": "gC/m^2/day"}
CONSUMED_RELEASE_FILES = {
    "interface/feature_schema.json": (2495, "67f5b43acf7c08ff021d65ffd42e57a1b74b77f438071bdbc9af4f788c7612cb"),
    "interface/inference_contract.json": (741, "306b8090378e47eb7f08ead62721f146ba102c8d67acd4da210276e1ad45f728"),
    "interface/parameter_constraints.json": (4235, "29af5ac158761baea828868d1a259f1f295e279c6178b2dd93650c0c2864a6b6"),
    "uncertainty/final_validation_report.json": (1006, "fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6"),
    "uncertainty/products_manifest.json": (4545, "293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9"),
    "uncertainty/uncertainty_handoff.json": (6453, "c9282bbad9abc2d6519329018ca9be026171f071e6e689a44fb2af102784f436"),
}


@dataclass(frozen=True)
class LoadedCoupledRelease:
    engine: CoupledThreeStageInference
    release_manifest: dict
    inference_contract: dict
    feature_schema: dict
    parameter_constraints: dict
    output_units: dict[str, str]
    unit_provenance: dict[str, str]
    loading_seconds: dict[str, float]


def _json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"missing release dependency: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_ppe1_coupled_release(
    *, prior: Prior18, release_root: Path | str, snapshot_root: Path | str, source_file: Path | str,
    uncertainty_root: Path | str,
) -> LoadedCoupledRelease:
    prior.require_release_compatibility(PPE1)
    release = Path(release_root).resolve()
    snapshot_path = Path(snapshot_root).resolve()
    source = Path(source_file).resolve()
    validation_start = time.perf_counter()
    outer_manifest_path = release / "release_manifest.json"
    catalog_path = release.parent / "catalog.json"
    if sha256_file(outer_manifest_path) != EXPECTED_RELEASE_MANIFEST_SHA256:
        raise ValueError("coupled release manifest identity mismatch")
    if sha256_file(catalog_path) != EXPECTED_CATALOG_SHA256:
        raise ValueError("coupled catalog identity mismatch")
    if sha256_file(source) != EXPECTED_SOURCE_SHA256:
        raise ValueError("coupled inference source identity mismatch")
    if sha256_file(source.parent / "three_stage_inference.py") != EXPECTED_ENGINE_SOURCE_SHA256:
        raise ValueError("coupled inference engine source identity mismatch")
    for name, digest in EXPECTED_UNIT_SOURCE_HASHES.items():
        if sha256_file(source.parent / name) != digest:
            raise ValueError(f"output-unit source identity mismatch: {name}")
    unit_source = (source.parent / "three_stage_inference.py").read_text(encoding="utf-8")
    for literal in ('("TOTSOMC", result.totsomc, "gC/m^2")',
                    '("TOTSOMN", result.totsomn, "gN/m^2")',
                    'variable.units = "gC/m^2/day"'):
        if literal not in unit_source:
            raise ValueError(f"output-unit source contract missing: {literal}")
    outer_manifest = _json(outer_manifest_path)
    records = {item["path"]: item for item in outer_manifest.get("files", ())}
    for relative, (size, digest) in CONSUMED_RELEASE_FILES.items():
        record = records.get(relative)
        path = release / relative
        if record is None or int(record.get("size_bytes", -1)) != size or record.get("sha256") != digest:
            raise ValueError(f"release payload record mismatch: {relative}")
        if path.stat().st_size != size or sha256_file(path) != digest:
            raise ValueError(f"release payload identity mismatch: {relative}")
    uncertainty = Path(uncertainty_root).resolve()
    for name, digest in (
        ("uncertainty_handoff.json", CONSUMED_RELEASE_FILES["uncertainty/uncertainty_handoff.json"][1]),
        ("products_manifest.json", CONSUMED_RELEASE_FILES["uncertainty/products_manifest.json"][1]),
        ("final_validation_report.json", CONSUMED_RELEASE_FILES["uncertainty/final_validation_report.json"][1]),
    ):
        if sha256_file(uncertainty / name) != digest:
            raise ValueError(f"external uncertainty identity mismatch: {name}")
    catalog = _json(catalog_path)
    if catalog.get("current_release") != "release_0001" or catalog.get("gpp_output_policy") != "hard_zero_v1":
        raise ValueError("coupled catalog contract mismatch")
    if catalog.get("training_partition") != "development_819":
        raise ValueError("coupled training partition mismatch")
    inference_contract = _json(release / "interface" / "inference_contract.json")
    feature_schema = _json(release / "interface" / "feature_schema.json")
    constraints = _json(release / "interface" / "parameter_constraints.json")
    if inference_contract.get("contains_elm_targets") is not False or inference_contract.get("training_or_fitting") is not False:
        raise ValueError("release is not target-free inference")
    if inference_contract.get("gpp_output_policy") != "hard_zero_v1":
        raise ValueError("release GPP output policy mismatch")
    if inference_contract.get("sites") != ["ABBY", "JERC"]:
        raise ValueError("release site contract mismatch")
    if inference_contract.get("calendar") != "noleap" or int(inference_contract.get("nonzero_window_history_hours", -1)) != 720:
        raise ValueError("release time contract mismatch")
    if feature_schema.get("counts") != {"spinup": 25, "gpp": 43, "sr": 44}:
        raise ValueError("release feature schema mismatch")
    if tuple(constraints.get("parameter_order", ())) != prior.names:
        raise ValueError("release parameter order mismatch")
    validation_seconds = time.perf_counter() - validation_start
    snapshot_start = time.perf_counter()
    snapshot = ThreeStageSnapshot(snapshot_path, verify_component_hashes=True)
    snapshot_seconds = time.perf_counter() - snapshot_start
    if snapshot.snapshot_sha256 != EXPECTED_SNAPSHOT_SHA256:
        raise ValueError("snapshot identity mismatch")
    if sha256_file(snapshot.split_path) != EXPECTED_SPLIT_SHA256:
        raise ValueError("global split identity mismatch")
    artifact_root = release / "artifact" / "coupled_artifacts"
    artifact_start = time.perf_counter()
    spinup, gpp, sr, manifest = load_artifacts(artifact_root, snapshot)
    artifact_seconds = time.perf_counter() - artifact_start
    engine_start = time.perf_counter()
    engine = CoupledThreeStageInference(snapshot, spinup, gpp, sr, manifest)
    engine_seconds = time.perf_counter() - engine_start
    return LoadedCoupledRelease(
        engine, outer_manifest, inference_contract, feature_schema, constraints, dict(OUTPUT_UNITS),
        dict(EXPECTED_UNIT_SOURCE_HASHES),
        {"identity_validation": validation_seconds, "snapshot": snapshot_seconds,
         "artifacts": artifact_seconds, "engine_construction": engine_seconds},
    )
