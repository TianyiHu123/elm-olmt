#!/usr/bin/env python3
"""Iter014 preflight and bounded integration entry point."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_data import SITES, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES
from model_ELM.three_stage_inference import FrozenThreeStageInference, read_result, write_result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload["schema"] == "three-stage-inference-iter014-config-v1", "configuration schema mismatch")
    return payload


def preflight(config: dict[str, Any], output: Path) -> None:
    require(not output.exists(), "preflight output exists")
    output.mkdir(parents=True)
    engine = FrozenThreeStageInference(config)
    require(list(engine.snapshot.development_ranked[index] for index in config["sample_positions"]) == config["sample_members"], "sample mapping mismatch")
    lower = engine.lower.copy()
    lower[17] = max(lower[17], lower[16] + 0.5)
    middle = (engine.lower + engine.upper) / 2.0
    middle[17] = min(49.5, max(40.0, middle[16] + 0.5))
    upper = engine.upper.copy()
    upper[17] = 49.5
    engine.validate_parameters(np.vstack((lower, middle, upper)))
    report = {
        "schema": "three-stage-inference-iter014-preflight-v1",
        "result": "pass",
        "artifact_deserialization": True,
        "parameter_vectors_checked": 3,
        "parameter_names": list(engine.parameter_names),
        "sample_positions": config["sample_positions"],
        "sample_members": config["sample_members"],
        "windows": config["windows"],
        "spinup_features": len(engine.spinup["feature_names"]),
        "gpp_features": len(engine.gpp["feature_names"]),
        "sr_features": len(engine.sr["feature_names"]),
        "fixed_test_access": False,
        "training_or_fitting": False,
        "full_819_engine": False,
    }
    write_json(output / "preflight_report.json", report)
    print("ITER014_PREFLIGHT_OK artifacts=3 synthetic_vectors=3 fixed_test=false")


def integration(config: dict[str, Any], output: Path) -> None:
    require(not output.exists(), "integration output exists")
    output.mkdir(parents=True)
    engine = FrozenThreeStageInference(config)
    positions = np.asarray(config["sample_positions"], dtype=np.int64)
    members = list(config["sample_members"])
    require([engine.snapshot.development_ranked[index] for index in positions] == members, "integration sample mismatch")
    parameters = engine.snapshot._parameter_values(members)
    maxima = {
        "TOTSOMC": 0.0, "TOTSOMN": 0.0, "GPP": 0.0, "SR": 0.0,
        "chunk_TOTSOMC": 0.0, "chunk_TOTSOMN": 0.0,
        "chunk_GPP": 0.0, "chunk_SR": 0.0,
        "reload_GPP": 0.0, "reload_SR": 0.0,
    }
    counts = {"TOTSOMC": 0, "TOTSOMN": 0, "GPP": 0, "SR": 0}
    rows: list[dict[str, Any]] = []
    replay_rows: list[dict[str, Any]] = []
    replay_failures = 0
    verified_handoffs = {
        "C/N": sha256_file(Path(config["predicted_cn_handoff"])),
        "GPP": sha256_file(Path(config["predicted_gpp_handoff"])),
        "SR": sha256_file(Path(config["predicted_sr_handoff"])),
    }
    require(verified_handoffs["C/N"] == config["predicted_cn_sha256"], "C/N handoff identity mismatch")
    require(verified_handoffs["GPP"] == config["predicted_gpp_sha256"], "GPP handoff identity mismatch")
    require(verified_handoffs["SR"] == config["predicted_sr_sha256"], "SR handoff identity mismatch")
    with Dataset(config["predicted_cn_handoff"], "r") as cn_handoff, Dataset(
        config["predicted_gpp_handoff"], "r"
    ) as gpp_handoff, Dataset(config["predicted_sr_handoff"], "r") as sr_handoff:
        require(np.asarray(cn_handoff.variables["member_id"][:], dtype=str).tolist() == list(engine.snapshot.development_ranked), "C/N handoff member mismatch")
        require(np.asarray(gpp_handoff.variables["member_id"][:], dtype=str).tolist() == list(engine.snapshot.development_ranked), "GPP handoff member mismatch")
        require(np.asarray(sr_handoff.variables["member_id"][:], dtype=str).tolist() == list(engine.snapshot.development_ranked), "SR handoff member mismatch")
        for site_index, site in enumerate(SITES):
            site_path = engine.snapshot.root / "sites" / site / "input_data_v1.nc"
            with Dataset(str(site_path), "r") as source:
                for start, end in config["windows"]:
                    forcing = {name: np.asarray(source.variables[name][:end], dtype=np.float64) for name in FORCING_NAMES}
                    time = np.asarray(source.variables["time"][:end], dtype=np.int64)
                    direct = engine.predict(parameters, site=site, forcing=forcing, time=time, start=start, end=end)
                    chunked = engine.predict(parameters, site=site, forcing=forcing, time=time, start=start, end=end, chunk_rows=17)
                    expected_c = np.asarray(cn_handoff.variables["TOTSOMC_predicted"][site_index, positions], dtype=np.float64)
                    expected_n = np.asarray(cn_handoff.variables["TOTSOMN_predicted"][site_index, positions], dtype=np.float64)
                    expected_gpp = np.asarray(gpp_handoff.variables["GPP_predicted"][site_index, positions, start:end], dtype=np.float64)
                    expected_sr = np.asarray(sr_handoff.variables["SR_predicted"][site_index, positions, start:end], dtype=np.float64)
                    observed = {"TOTSOMC": direct.totsomc, "TOTSOMN": direct.totsomn, "GPP": direct.gpp, "SR": direct.sr}
                    expected = {"TOTSOMC": expected_c, "TOTSOMN": expected_n, "GPP": expected_gpp, "SR": expected_sr}
                    comparison_names = ("TOTSOMC", "TOTSOMN", "GPP", "SR") if start == config["windows"][0][0] else ("GPP", "SR")
                    for name in comparison_names:
                        require(np.all(np.isfinite(observed[name])), f"nonfinite {name}")
                        difference = np.abs(observed[name] - expected[name])
                        allowed = config["handoff_replay_atol"] + config["handoff_replay_rtol"] * np.abs(expected[name])
                        close = difference <= allowed
                        nonzero = expected[name] != 0.0
                        relative = difference[nonzero] / np.abs(expected[name][nonzero])
                        mismatch_count = int(np.count_nonzero(~close))
                        replay_failures += int(mismatch_count > 0)
                        replay_rows.append({
                            "site": site,
                            "start": start,
                            "end": end,
                            "stage": name,
                            "count": int(difference.size),
                            "mismatch_count": mismatch_count,
                            "zero_reference_count": int(np.count_nonzero(~nonzero)),
                            "max_absolute_difference": float(np.max(difference)),
                            "max_relative_difference_nonzero_reference": float(np.max(relative)) if relative.size else None,
                            "max_normalized_tolerance_ratio": float(np.max(difference / allowed)),
                        })
                        maximum = float(np.max(difference))
                        maxima[name] = max(maxima[name], maximum)
                        if name in ("GPP", "SR"):
                            counts[name] += int(observed[name].size)
                    if start == config["windows"][0][0]:
                        counts["TOTSOMC"] += int(direct.totsomc.size)
                        counts["TOTSOMN"] += int(direct.totsomn.size)
                    for name, first, second in (
                        ("TOTSOMC", direct.totsomc, chunked.totsomc),
                        ("TOTSOMN", direct.totsomn, chunked.totsomn),
                        ("GPP", direct.gpp, chunked.gpp),
                        ("SR", direct.sr, chunked.sr),
                    ):
                        require(np.allclose(first, second, rtol=config["reload_rtol"], atol=config["reload_atol"]), f"chunk replay mismatch: {name}")
                        maxima[f"chunk_{name}"] = max(maxima[f"chunk_{name}"], float(np.max(np.abs(first - second))))
                    serialized = output / f"{site.lower()}_{start}_{end}.nc"
                    write_result(serialized, direct)
                    reloaded = read_result(serialized)
                    for name, first, second in (
                        ("parameters", direct.parameters, reloaded.parameters),
                        ("time", direct.time, reloaded.time),
                        ("TOTSOMC", direct.totsomc, reloaded.totsomc),
                        ("TOTSOMN", direct.totsomn, reloaded.totsomn),
                        ("GPP", direct.gpp, reloaded.gpp),
                        ("SR", direct.sr, reloaded.sr),
                    ):
                        require(np.array_equal(first, second), f"serialization mismatch: {name}")
                        if name in ("GPP", "SR"):
                            maxima[f"reload_{name}"] = max(maxima[f"reload_{name}"], float(np.max(np.abs(first - second))))
                    require(reloaded.parameter_names == direct.parameter_names, "serialization mismatch: parameter_names")
                    require(reloaded.site == direct.site, "serialization mismatch: site")
                    require(reloaded.provenance == direct.provenance, "serialization mismatch: provenance")
                    rows.append({"site": site, "start": start, "end": end, "members": members, "hours": end - start, "output": serialized.name, "output_sha256": sha256_file(serialized)})
    require(counts == {"TOTSOMC": 18, "TOTSOMN": 18, "GPP": 2592, "SR": 2592}, f"comparison denominator mismatch: {counts}")
    report = {
        "schema": "three-stage-inference-iter014-integration-v1",
        "result": "pass" if replay_failures == 0 else "fail_published_handoff_replay",
        "sample_positions": config["sample_positions"],
        "sample_members": members,
        "sites": list(SITES),
        "windows": config["windows"],
        "comparison_counts": counts,
        "maximum_absolute_differences": maxima,
        "handoff_replay_rtol": config["handoff_replay_rtol"],
        "handoff_replay_atol": config["handoff_replay_atol"],
        "direct_chunk_rtol": config["reload_rtol"],
        "direct_chunk_atol": config["reload_atol"],
        "verified_handoff_sha256": verified_handoffs,
        "published_replay_comparisons": replay_rows,
        "published_replay_failed_comparisons": replay_failures,
        "serialized_outputs": rows,
        "contains_elm_truth_in_engine": False,
        "fixed_test_access": False,
        "training_or_fitting": False,
        "full_819_engine": False,
    }
    if replay_failures:
        report["schema"] = "three-stage-inference-iter014-integration-failure-v1"
        write_json(output / "integration_failure_report.json", report)
        raise ValueError(f"published replay mismatches in {replay_failures}/{len(replay_rows)} bounded comparisons")
    write_json(output / "integration_report.json", report)
    print("ITER014_INTEGRATION_OK spinup=18 gpp=2592 sr=2592 fixed_test=false")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "integration"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.mode == "preflight":
        preflight(config, args.output)
    else:
        integration(config, args.output)


if __name__ == "__main__":
    main()
