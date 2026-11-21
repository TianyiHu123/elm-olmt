"""Validate and accept the completed Iter016 attempt-1 fit without refitting."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from netCDF4 import Dataset


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter016.refit_iter016 import load_config, validate_config
from model_ELM.three_stage_coupled_release import CoupledThreeStageInference, load_artifacts
from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES, HOURS


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_file(path: Path, record: Mapping[str, Any]) -> None:
    require(path.is_file(), f"recovery input missing: {path}")
    if "size_bytes" in record:
        require(path.stat().st_size == int(record["size_bytes"]), f"recovery size mismatch: {path.name}")
    require(sha256_file(path) == record["sha256"], f"recovery hash mismatch: {path.name}")


def recover(
    recovery_config_path: Path,
    execution_manifest_path: Path,
    output: Path,
) -> dict[str, Any]:
    recovery = read_json(recovery_config_path)
    require(recovery.get("schema") == "three-stage-iter016-recovery-config-v1", "recovery schema mismatch")
    require(not output.exists(), f"recovery output exists: {output}")
    require(recovery.get("additional_fitting_allowed") is False, "recovery fitting boundary mismatch")
    require(recovery.get("fixed_test_access_allowed") is False, "recovery fixed-test boundary mismatch")
    require(recovery.get("attempt_1_mutation_allowed") is False, "recovery mutation boundary mismatch")
    require(recovery.get("release_publication_allowed") is False, "recovery release boundary mismatch")
    require(execution_manifest_path.is_file(), "recovery execution manifest missing")
    recovery_config_sha256 = sha256_file(recovery_config_path)
    execution_manifest_sha256 = sha256_file(execution_manifest_path)
    base_path = Path(recovery["base_config"])
    require(sha256_file(base_path) == recovery["base_config_sha256"], "recovery base config mismatch")
    config = load_config(base_path)
    snapshot = validate_config(config, verify_snapshot_components=True)
    require(str(recovery.get("failed_job_id")) == "24725445", "recovery failed job mismatch")
    require(recovery.get("failed_state") == "FAILED" and recovery.get("failed_exit_code") == "1:0", "recovery failure identity mismatch")
    for path_key, hash_key in (("failed_stdout", "failed_stdout_sha256"), ("failed_stderr", "failed_stderr_sha256")):
        path = Path(recovery[path_key])
        require(path.is_file() and sha256_file(path) == recovery[hash_key], f"recovery log mismatch: {path_key}")
    source = Path(recovery["source_root"])
    require(source.is_dir() and source.name == "attempt_1", "recovery source mismatch")
    manifest_path = Path(recovery["artifact_manifest"])
    require(sha256_file(manifest_path) == recovery["artifact_manifest_sha256"], "recovery artifact manifest mismatch")
    spinup, gpp, sr, manifest = load_artifacts(source / "artifact_package", snapshot)
    require(sha256_file(manifest_path) == recovery["artifact_manifest_sha256"], "recovery manifest changed during load")
    prediction_records = recovery["prediction_files"]
    prediction_paths = {name: Path(record["path"]) for name, record in prediction_records.items()}
    for name, path in prediction_paths.items():
        validate_file(path, prediction_records[name])
    total_rows = int(recovery["total_rows"])
    require(total_rows == 2 * 819 * HOURS, "recovery row count mismatch")
    arrays = {
        name: np.memmap(path, mode="r", dtype=np.float32, shape=(total_rows,))
        for name, path in prediction_paths.items()
    }
    chunk_rows = int(config["prediction_chunk_rows"])
    for start in range(0, total_rows, chunk_rows):
        end = min(start + chunk_rows, total_rows)
        raw = np.asarray(arrays["gpp_raw"][start:end])
        gated = np.asarray(arrays["gpp_gated"][start:end])
        respiration = np.asarray(arrays["sr"][start:end])
        require(np.all(np.isfinite(raw)) and np.all(np.isfinite(gated)) and np.all(np.isfinite(respiration)), "recovery nonfinite prediction")
        require(np.array_equal(gated, np.maximum(raw, np.float32(0.0))), "recovery full gate mismatch")
    engine = CoupledThreeStageInference(snapshot, spinup, gpp, sr, manifest)
    member_count = int(recovery["replay_member_count"])
    replay_start = int(recovery["replay_start"])
    replay_end = int(recovery["replay_end"])
    parameters = snapshot._parameter_values(snapshot.development_ranked[:member_count])
    site_path = snapshot.root / "sites" / str(recovery["replay_site"]) / "input_data_v1.nc"
    with Dataset(str(site_path), "r") as dataset:
        forcing = {
            name: np.asarray(dataset.variables[name][:replay_end], dtype=np.float64)
            for name in FORCING_NAMES
        }
        time = np.asarray(dataset.variables["time"][:replay_end], dtype=np.int64)
    direct = engine.predict(
        parameters, site=str(recovery["replay_site"]), forcing=forcing, time=time,
        start=replay_start, end=replay_end, member_chunk=1,
    )
    chunked = engine.predict(
        parameters, site=str(recovery["replay_site"]), forcing=forcing, time=time,
        start=replay_start, end=replay_end, member_chunk=2,
    )
    for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
        require(np.allclose(getattr(direct, name), getattr(chunked, name), rtol=1e-6, atol=1e-6), f"recovery chunk mismatch: {name}")
    require(np.array_equal(direct.gpp, np.maximum(direct.gpp_raw, 0.0)), "recovery replay gate mismatch")
    invalid = parameters[:1].copy()
    invalid[0, 17] = invalid[0, 16]
    rejected = False
    try:
        engine.validate_parameters(invalid)
    except ValueError:
        rejected = True
    require(rejected, "recovery conditional C:N rejection missing")
    site_rows = 819 * HOURS
    for member in range(member_count):
        source_slice = slice(member * HOURS + replay_start, member * HOURS + replay_end)
        require(np.allclose(direct.gpp_raw[member], arrays["gpp_raw"][source_slice], rtol=1e-6, atol=1e-6), "recovery stored raw-GPP replay mismatch")
        require(np.allclose(direct.gpp[member], arrays["gpp_gated"][source_slice], rtol=1e-6, atol=1e-6), "recovery stored gated-GPP replay mismatch")
        require(np.allclose(direct.sr[member], arrays["sr"][source_slice], rtol=1e-6, atol=1e-6), "recovery stored SR replay mismatch")
    require(site_rows * 2 == total_rows, "recovery site layout mismatch")
    output.mkdir(parents=True)
    layout = {
        "schema": "three-stage-iter016-recovered-development-layout-v1",
        "fit_attempt": 1,
        "validation_attempt": 2,
        "source_root": str(source),
        "sites": ["ABBY", "JERC"],
        "member_ids": list(snapshot.development_ranked),
        "hours": HOURS,
        "total_rows": total_rows,
        "artifact_manifest": {"path": str(manifest_path), "sha256": recovery["artifact_manifest_sha256"]},
        "prediction_files": prediction_records,
    }
    write_json(output / "development_layout.json", layout)
    report = {
        "schema": "three-stage-iter016-refit-recovery-report-v1",
        "result": "pass",
        "fit_attempt": 1,
        "validation_attempt": 2,
        "additional_fitting": False,
        "failed_job_id": "24725445",
        "failed_state": "FAILED 1:0",
        "failed_logs": {
            "stdout": {
                "path": recovery["failed_stdout"],
                "sha256": recovery["failed_stdout_sha256"],
            },
            "stderr": {
                "path": recovery["failed_stderr"],
                "sha256": recovery["failed_stderr_sha256"],
            },
        },
        "recovery_config": {
            "path": str(recovery_config_path),
            "sha256": recovery_config_sha256,
        },
        "execution_manifest": {
            "path": str(execution_manifest_path),
            "sha256": execution_manifest_sha256,
        },
        "correction": recovery["correction"],
        "accepted_artifact_root": str(source / "artifact_package"),
        "artifact_manifest_sha256": recovery["artifact_manifest_sha256"],
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"],
        "training_partition": "development",
        "training_member_count": 819,
        "fixed_test_fit_access": False,
        "fixed_test_target_access": False,
        "feature_counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "gpp_output_policy": "hard_zero_v1",
        "artifact_reload_complete": True,
        "full_prediction_finite": True,
        "gpp_gate_equal_full_binary": True,
        "direct_chunk_consistency": True,
        "stored_prediction_replay": True,
        "conditional_cn_rejection": True,
        "prediction_files": prediction_records,
        "development_layout_sha256": "pending",
        "attempt_1_mutated": False,
        "historical_release_modified": False,
        "fixed_test_evaluation_performed": False,
        "release_published": False,
    }
    report["development_layout_sha256"] = sha256_file(output / "development_layout.json")
    write_json(output / "refit_recovery_report.json", report)
    print("ITER016_REFIT_RECOVERY_OK fit_attempt=1 validation_attempt=2 additional_fitting=false fixed_test=false", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery-config", type=Path, required=True)
    parser.add_argument("--execution-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = recover(args.recovery_config, args.execution_manifest, args.output)
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
