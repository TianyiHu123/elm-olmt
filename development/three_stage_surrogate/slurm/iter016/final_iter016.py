"""Final validation and catalog-last publication for the Iter016 coupled release."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from netCDF4 import Dataset

from development.three_stage_surrogate.slurm.iter016.refit_iter016 import load_config
from model_ELM.three_stage_coupled_release import CoupledThreeStageInference, load_artifacts
from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_inventory(root: Path, manifest: Mapping[str, Any]) -> None:
    records = {str(item["path"]): item for item in manifest["files"]}
    actual = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and path.name != "release_manifest.json"}
    require(set(records) == actual, "final release inventory mismatch")
    for relative, record in records.items():
        path = root / relative
        require(path.stat().st_size == int(record["size_bytes"]), f"final release size mismatch: {relative}")
        require(sha256_file(path) == record["sha256"], f"final release hash mismatch: {relative}")


def tree_identity(left: Path, right: Path) -> None:
    left_files = {str(path.relative_to(left)): path for path in left.rglob("*") if path.is_file()}
    right_files = {str(path.relative_to(right)): path for path in right.rglob("*") if path.is_file()}
    require(set(left_files) == set(right_files), "published tree inventory mismatch")
    for relative in left_files:
        require(left_files[relative].stat().st_size == right_files[relative].stat().st_size, f"published tree size mismatch: {relative}")
        require(sha256_file(left_files[relative]) == sha256_file(right_files[relative]), f"published tree hash mismatch: {relative}")


def replay(root: Path, snapshot: Any) -> None:
    spinup, gpp, sr, manifest = load_artifacts(root / "artifact" / "coupled_artifacts", snapshot)
    engine = CoupledThreeStageInference(snapshot, spinup, gpp, sr, manifest)
    parameters = snapshot._parameter_values(snapshot.fixed_test_ranked[:2])
    for site in SITES:
        with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as source:
            forcing = {name: np.asarray(source.variables[name][:768], dtype=np.float64) for name in FORCING_NAMES}
            time = np.asarray(source.variables["time"][:768], dtype=np.int64)
        direct = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=1)
        chunked = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=2)
        for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
            require(np.allclose(getattr(direct, name), getattr(chunked, name), rtol=1e-6, atol=1e-6), f"final replay mismatch: {site}/{name}")
        require(np.array_equal(direct.gpp, np.maximum(direct.gpp_raw, 0.0)), f"final GPP gate mismatch: {site}")


def run(config_path: Path, output: Path) -> dict[str, Any]:
    config = read_json(config_path)
    require(config.get("schema") == "three-stage-iter016-final-config-v1", "final config schema mismatch")
    require(config.get("catalog_last_required") is True and config.get("historical_release_modification_allowed") is False, "final publication scope mismatch")
    require(not output.exists(), f"final output exists: {output}")
    candidate = Path(config["candidate_root"])
    candidate_manifest_path = candidate / "release_manifest.json"
    require(sha256_file(candidate_manifest_path) == config["candidate_manifest_sha256"], "candidate manifest mismatch")
    candidate_manifest = read_json(candidate_manifest_path)
    require(candidate_manifest.get("schema") == "three-stage-coupled-release-manifest-v1" and candidate_manifest.get("result") == "assembled", "candidate status mismatch")
    require(len(candidate_manifest.get("files", [])) == 26, "candidate file count mismatch")
    verify_inventory(candidate, candidate_manifest)
    require(sha256_file(Path(config["assembly_report"])) == config["assembly_report_sha256"], "assembly report mismatch")
    assembly = read_json(Path(config["assembly_report"]))
    require(assembly.get("result") == "pass" and assembly.get("stable_publication_performed") is False, "assembly eligibility mismatch")
    require(assembly.get("release_manifest_sha256") == config["candidate_manifest_sha256"], "assembly manifest identity mismatch")

    base_path = Path(config["base_config"])
    require(sha256_file(base_path) == config["base_config_sha256"], "final base config mismatch")
    base = load_config(base_path)
    snapshot = ThreeStageSnapshot(base["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == base["snapshot_sha256"], "final snapshot mismatch")
    require(sha256_file(snapshot.split_path) == base["global_split_sha256"], "final split mismatch")
    release_config_path = Path(config["release_config"])
    require(sha256_file(release_config_path) == config["release_config_sha256"], "final release config mismatch")
    release_config = read_json(release_config_path)
    historical_before = {}
    for record in release_config["historical_releases"]:
        require(sha256_file(Path(record["manifest"])) == record["manifest_sha256"], "historical manifest changed before final")
        require(sha256_file(Path(record["catalog"])) == record["catalog_sha256"], "historical catalog changed before final")
        historical_before[record["stage"]] = (record["manifest_sha256"], record["catalog_sha256"])

    staging_root = Path(config["staging_root"])
    stable_root = Path(config["stable_product_root"])
    release_name = str(config["release_name"])
    staging_release = staging_root / release_name
    stable_release = stable_root / release_name
    require(not (stable_root / "catalog.json").exists(), "stable catalog already exists")
    output.mkdir(parents=True)
    validated = output / "validation" / release_name
    shutil.copytree(candidate, validated)
    validated_manifest = dict(candidate_manifest)
    validated_manifest.update({
        "result": "validated",
        "validation": {
            "iteration": "iter016", "source_candidate_manifest_sha256": config["candidate_manifest_sha256"],
            "target_free_replay": True, "direct_chunk_consistency": True,
            "gpp_gate_equal_binary": True, "catalog_last": True,
        },
    })
    write_json(validated / "release_manifest.json", validated_manifest)
    verify_inventory(validated, validated_manifest)
    replay(validated, snapshot)

    staging_root.mkdir(parents=True, exist_ok=True)
    stable_root.mkdir(parents=True, exist_ok=True)
    job_id = os.environ.get("SLURM_JOB_ID", "unknown")
    staging_temp = staging_root / f".{release_name}_{job_id}"
    stable_temp = stable_root / f".{release_name}_{job_id}"
    require(not staging_temp.exists() and not stable_temp.exists(), "publication temp exists")
    empty_staging_placeholder_removed = False
    if staging_release.exists() and staging_release.is_dir() and not any(staging_release.iterdir()):
        staging_release.rmdir()
        empty_staging_placeholder_removed = True
    if staging_release.exists():
        tree_identity(validated, staging_release)
    else:
        shutil.copytree(validated, staging_temp)
        os.replace(staging_temp, staging_release)
    if stable_release.exists():
        tree_identity(staging_release, stable_release)
    else:
        shutil.copytree(staging_release, stable_temp)
        os.replace(stable_temp, stable_release)
    tree_identity(staging_release, stable_release)
    verify_inventory(stable_release, validated_manifest)
    replay(stable_release, snapshot)

    release_manifest_sha256 = sha256_file(stable_release / "release_manifest.json")
    catalog = {
        "schema": config["catalog_schema"],
        "current_release": release_name,
        "current_manifest": f"{release_name}/release_manifest.json",
        "current_manifest_sha256": release_manifest_sha256,
        "release_basis": "iter016_frozen_all_development_refit_and_fixed_test",
        "training_partition": "development_819",
        "evaluation_partition": "fixed_test_205",
        "gpp_output_policy": "hard_zero_v1",
        "performance_threshold_applied": False,
        "scientific_limitation": "128246 fixed-test SR predictions are negative; no post-hoc SR gate applied",
        "storage_note": "temporary unbacked /xdisk operational publication",
    }
    catalog_temp = stable_root / f".catalog_{job_id}.json"
    require(not catalog_temp.exists(), "catalog temp exists")
    write_json(catalog_temp, catalog)
    os.replace(catalog_temp, stable_root / "catalog.json")
    require(read_json(stable_root / "catalog.json") == catalog, "catalog publication mismatch")
    require(sha256_file(stable_release / "release_manifest.json") == release_manifest_sha256, "release changed after catalog")

    for record in release_config["historical_releases"]:
        require(sha256_file(Path(record["manifest"])) == historical_before[record["stage"]][0], "historical manifest changed after final")
        require(sha256_file(Path(record["catalog"])) == historical_before[record["stage"]][1], "historical catalog changed after final")
    report = {
        "schema": "three-stage-iter016-final-publication-report-v1", "result": "pass",
        "release": release_name, "validated_release_manifest_sha256": release_manifest_sha256,
        "catalog_sha256": sha256_file(stable_root / "catalog.json"), "file_count": 26,
        "staging_stable_byte_identical": True, "catalog_written_last": True,
        "target_free_replay": True, "direct_chunk_consistency": True,
        "gpp_gate_equal_binary": True, "historical_releases_modified": False,
        "uncertainty_refit": False, "performance_threshold_applied": False,
        "scientific_limitation_recorded": True,
        "empty_staging_placeholder_removed": empty_staging_placeholder_removed,
        "restart_safe_validated_tree_reuse": True,
    }
    write_json(output / "final_publication_report.json", report)
    print(f"ITER016_FINAL_PUBLISH_OK release={release_name} files=26 catalog_last=true", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return 0 if run(args.config, args.output)["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
