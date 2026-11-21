"""Iter016 all-development direct-sequential refit and Unit1 preflight."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from development.three_stage_surrogate.slurm.iter015.full_chain_iter015 import (
    _fit_hourly_stage,
    _forcing_and_surface,
    _offsets,
    write_json,
)
from development.three_stage_surrogate.slurm.iter015.full_chain_iter015 import preflight as iter015_preflight
from model_ELM.three_stage_coupled_release import (
    CoupledThreeStageInference,
    GPP_SCHEMA,
    SPINUP_SCHEMA,
    SR_SCHEMA,
    load_artifacts,
    save_artifacts,
)
from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, schema_sha256, sha256_file
from model_ELM.three_stage_gpp import HOURS, feature_names as gpp_feature_names
from model_ELM.three_stage_spinup import fit_compact_models, predict_compact_models
from model_ELM.three_stage_spinup_release import MODEL_CONFIG as SPINUP_MODEL_CONFIG
from model_ELM.three_stage_sr import feature_names as sr_feature_names


SCHEMA = "three-stage-iter016-config-v1"
PLAN_SHA256 = "6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d"


def load_config(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(value.get("schema") == SCHEMA, "Iter016 configuration schema mismatch")
    return value


def validate_config(config: Mapping[str, Any], *, verify_snapshot_components: bool) -> ThreeStageSnapshot:
    require(config.get("plan_sha256") == PLAN_SHA256, "Iter016 plan mismatch")
    require(config.get("gpp_output_policy") == "hard_zero_v1", "Iter016 GPP policy mismatch")
    for key in (
        "fixed_test_fit_allowed", "hyperparameter_tuning_allowed", "cross_fitting_allowed",
        "historical_release_modification_allowed",
    ):
        require(config.get(key) is False, f"Iter016 scope mismatch: {key}")
    for path_key, hash_key in (
        ("iter015_config_file", "iter015_config_sha256"),
        ("gpp_configuration_file", "gpp_configuration_sha256"),
        ("sr_configuration_file", "sr_configuration_sha256"),
        ("spinup_release_manifest", "spinup_release_manifest_sha256"),
        ("gpp_release_manifest", "gpp_release_manifest_sha256"),
        ("sr_release_manifest", "sr_release_manifest_sha256"),
        ("uncertainty_handoff", "uncertainty_handoff_sha256"),
        ("uncertainty_products_manifest", "uncertainty_products_manifest_sha256"),
        ("uncertainty_validation", "uncertainty_validation_sha256"),
    ):
        path = Path(str(config[path_key]))
        require(path.is_file(), f"Iter016 dependency missing: {path_key}")
        require(sha256_file(path) == config[hash_key], f"Iter016 dependency mismatch: {path_key}")
    gpp_configuration = json.loads(Path(config["gpp_configuration_file"]).read_text(encoding="utf-8"))
    sr_configuration = json.loads(Path(config["sr_configuration_file"]).read_text(encoding="utf-8"))
    require(config["gpp_model_config"] == gpp_configuration["model_config"], "Iter016 GPP model mismatch")
    require(config["sr_model_config"] == sr_configuration["model_config"], "Iter016 SR model mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=verify_snapshot_components)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "Iter016 snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "Iter016 split mismatch")
    require(len(snapshot.development_ranked) == 819 and len(snapshot.fixed_test_ranked) == 205, "Iter016 population mismatch")
    require(not snapshot.development_set.intersection(snapshot.fixed_test_set), "Iter016 partition overlap")
    require(Path(config["stable_product_root"]).exists() is False, "Iter016 stable product family already exists")
    return snapshot


def _release_artifact(
    artifact: Mapping[str, Any], *, stage: str, snapshot: ThreeStageSnapshot, config: Mapping[str, Any]
) -> dict[str, Any]:
    value = dict(artifact)
    value.pop("split_id", None)
    value.pop("train_member_ids", None)
    value.update({
        "schema": {"spinup": SPINUP_SCHEMA, "gpp": GPP_SCHEMA, "sr": SR_SCHEMA}[stage],
        "release_name": config["stable_release_name"],
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"],
        "training_member_ids": list(snapshot.development_ranked),
        "training_partition": "development",
        "upstream_prediction_mode": "direct_in_sample",
        "fixed_test_fit_access": False,
    })
    if stage in {"gpp", "sr"}:
        value["gpp_output_policy"] = "hard_zero_v1"
    return value


def preflight(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"Iter016 Unit1 output exists: {output}")
    output.mkdir(parents=True)
    snapshot = validate_config(config, verify_snapshot_components=True)
    iter015_config = json.loads(Path(config["iter015_config_file"]).read_text(encoding="utf-8"))
    smoke = iter015_preflight(iter015_config, output / "iter015_smoke")
    report = {
        "schema": "three-stage-iter016-preflight-report-v1",
        "result": "pass",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"],
        "development_member_count": len(snapshot.development_ranked),
        "fixed_test_member_count": len(snapshot.fixed_test_ranked),
        "fixed_test_target_access": False,
        "all_development_fit_performed": False,
        "historical_release_modified": False,
        "gpp_output_policy": "hard_zero_v1",
        "feature_counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "iter015_smoke_report_sha256": sha256_file(output / "iter015_smoke" / "preflight_report.json"),
        "release_interface_tested": True,
    }
    write_json(output / "preflight_report.json", report)
    return report


def refit(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"Iter016 refit output exists: {output}")
    output.mkdir(parents=True)
    snapshot = validate_config(config, verify_snapshot_components=True)
    members = list(snapshot.development_ranked)
    loaded = snapshot.load_rows(members, include_targets=True)
    fitted_spinup = fit_compact_models(loaded, SPINUP_MODEL_CONFIG)
    spinup = {
        **fitted_spinup,
        "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": schema_sha256(snapshot.feature_names),
    }
    cn_prediction = predict_compact_models(spinup, loaded.X)
    require(cn_prediction.shape == (len(SITES) * 819, 2), "Iter016 C/N prediction shape mismatch")
    parameters = {"training": snapshot._parameter_values(members)}
    cn_values: dict[tuple[str, str], np.ndarray] = {}
    for site_index, site in enumerate(SITES):
        begin = site_index * len(members)
        cn_values[("training", site)] = cn_prediction[begin : begin + len(members)]
    forcing_raw: dict[str, dict[str, np.ndarray]] = {}
    times: dict[str, np.ndarray] = {}
    forcing_features: dict[str, np.ndarray] = {}
    surfaces: dict[str, np.ndarray] = {}
    for site in SITES:
        raw, axis, engineered, surface = _forcing_and_surface(snapshot, site, HOURS)
        forcing_raw[site] = raw
        times[site] = axis
        forcing_features[site] = engineered
        surfaces[site] = surface
    partitions = [("training", members)]
    offsets, total_rows = _offsets(partitions, HOURS)
    active_config = dict(config)
    active_config["active_split_id"] = -1
    gpp, gpp_raw, gpp_raw_rw, gpp_warnings = _fit_hourly_stage(
        stage="GPP", config=active_config, snapshot=snapshot, partitions=partitions,
        parameters=parameters, cn_values=cn_values, forcing_features=forcing_features,
        surfaces=surfaces, offsets=offsets, total_rows=total_rows, hours=HOURS, output=output,
        gpp_gated=None, smoke=False,
    )
    gated_path = output / "gpp_gated_physical_float32.dat"
    gated = np.memmap(gated_path, mode="w+", dtype=np.float32, shape=(total_rows,))
    chunk = int(config["prediction_chunk_rows"])
    for start in range(0, total_rows, chunk):
        end = min(start + chunk, total_rows)
        gated[start:end] = np.maximum(np.asarray(gpp_raw_rw[start:end], dtype=np.float32), np.float32(0.0))
    gated.flush()
    sr, sr_prediction, sr_rw, sr_warnings = _fit_hourly_stage(
        stage="SR", config=active_config, snapshot=snapshot, partitions=partitions,
        parameters=parameters, cn_values=cn_values, forcing_features=forcing_features,
        surfaces=surfaces, offsets=offsets, total_rows=total_rows, hours=HOURS, output=output,
        gpp_gated=gated, smoke=False,
    )
    spinup = _release_artifact(spinup, stage="spinup", snapshot=snapshot, config=config)
    gpp = _release_artifact(gpp, stage="gpp", snapshot=snapshot, config=config)
    sr = _release_artifact(sr, stage="sr", snapshot=snapshot, config=config)
    manifest = save_artifacts(
        output / "artifact_package", snapshot, spinup, gpp, sr,
        provenance={
            "iteration": "iter016",
            "repository_base_commit": config["repository_base_commit"],
            "plan_sha256": config["plan_sha256"],
            "configuration_sha256": sha256_file(Path(config["repository_root"]) / "development/three_stage_surrogate/slurm/iter016/iter016_config.json"),
            "training_target_access": "development_only",
            "fixed_test_target_access": False,
        },
    )
    reloaded_spinup, reloaded_gpp, reloaded_sr, reloaded_manifest = load_artifacts(
        output / "artifact_package", snapshot
    )
    require(manifest == reloaded_manifest, "Iter016 artifact manifest reload mismatch")
    engine = CoupledThreeStageInference(snapshot, reloaded_spinup, reloaded_gpp, reloaded_sr, reloaded_manifest)
    sample = parameters["training"][:2]
    replay_end = 768
    replay_forcing = {name: values[:replay_end] for name, values in forcing_raw["ABBY"].items()}
    replay_time = times["ABBY"][:replay_end]
    first = engine.predict(
        sample, site="ABBY", forcing=replay_forcing, time=replay_time,
        start=720, end=768, member_chunk=1,
    )
    second = engine.predict(
        sample, site="ABBY", forcing=replay_forcing, time=replay_time,
        start=720, end=768, member_chunk=2,
    )
    for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
        require(np.allclose(getattr(first, name), getattr(second, name), rtol=1e-6, atol=1e-6), f"Iter016 chunk mismatch: {name}")
    require(np.array_equal(first.gpp, np.maximum(first.gpp_raw, 0.0)), "Iter016 inference gate mismatch")
    require(np.array_equal(np.asarray(gated), np.maximum(np.asarray(gpp_raw_rw), 0.0)), "Iter016 full gate mismatch")
    prediction_files = {
        "gpp_raw": Path(gpp_raw_rw.filename),
        "gpp_gated": gated_path,
        "sr": Path(sr_rw.filename),
    }
    write_json(output / "development_layout.json", {
        "schema": "three-stage-iter016-development-layout-v1",
        "sites": list(SITES),
        "member_ids": members,
        "hours": HOURS,
        "offsets": offsets,
        "total_rows": total_rows,
        "files": {
            name: {"path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for name, path in prediction_files.items()
        },
    })
    report = {
        "schema": "three-stage-iter016-refit-report-v1",
        "result": "pass",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": config["global_split_sha256"],
        "training_partition": "development",
        "training_member_count": 819,
        "fixed_test_fit_access": False,
        "fixed_test_target_access": False,
        "feature_counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "feature_schema_sha256": {
            "spinup": schema_sha256(snapshot.feature_names),
            "gpp": schema_sha256(gpp_feature_names(snapshot)),
            "sr": schema_sha256(sr_feature_names(snapshot)),
        },
        "gpp_output_policy": "hard_zero_v1",
        "gpp_gate_equal_full_binary": True,
        "artifact_reload_complete": True,
        "direct_chunk_consistency": True,
        "artifact_manifest_sha256": sha256_file(output / "artifact_package" / "artifact_manifest.json"),
        "development_layout_sha256": sha256_file(output / "development_layout.json"),
        "development_prediction_sha256": {
            name: sha256_file(path) for name, path in prediction_files.items()
        },
        "convergence": {"spinup": spinup["convergence"], "gpp": gpp_warnings, "sr": sr_warnings},
        "historical_release_modified": False,
        "fixed_test_evaluation_performed": False,
    }
    write_json(output / "refit_report.json", report)
    gpp_raw_rw.flush()
    gated.flush()
    sr_rw.flush()
    return report
