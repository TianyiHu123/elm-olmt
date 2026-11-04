#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_gpp import FEATURE_COUNT, predict_artifact
from model_ELM.three_stage_gpp_release import DEVELOPMENT_MEMBERS, HOURS, SITES, load_raw
from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_spinup_release import write_json


def comparison(
    left: np.ndarray,
    right: np.ndarray,
    rtol: float,
    atol: float,
    global_start: int,
    elements_per_row: int = 1,
) -> dict[str, object]:
    delta = np.abs(np.asarray(left, dtype=np.float64) - np.asarray(right, dtype=np.float64))
    close = np.isclose(left, right, rtol=rtol, atol=atol)
    worst = int(np.argmax(delta))
    row_offset, element_offset = divmod(worst, elements_per_row)
    global_offset = global_start + row_offset
    rows_per_site = DEVELOPMENT_MEMBERS * HOURS
    site_index, within_site = divmod(global_offset, rows_per_site)
    member_position, time_index = divmod(within_site, HOURS)
    return {
        "allclose": bool(np.all(close)),
        "failing_count": int(np.count_nonzero(~close)),
        "max_abs_difference": float(delta.reshape(-1)[worst]),
        "worst_offset": worst,
        "left_at_worst": float(np.asarray(left).reshape(-1)[worst]),
        "right_at_worst": float(np.asarray(right).reshape(-1)[worst]),
        "worst_coordinate": {
            "global_offset": global_offset,
            "site_index": site_index,
            "site": SITES[site_index],
            "member_position": member_position,
            "time_index": time_index,
            "feature_index": element_offset if elements_per_row > 1 else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--release-attempt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["fixed_test_allowed"] is False, "diagnostic fixed-test boundary mismatch")
    require(config["development_members"] == DEVELOPMENT_MEMBERS, "diagnostic development count mismatch")
    args.output.mkdir(parents=True, exist_ok=False)
    raw_layout, raw_x, _, raw_times = load_raw(Path(config["raw_directory"]))
    require(len(raw_layout["development_member_ids"]) == DEVELOPMENT_MEMBERS, "raw development scope mismatch")
    require(raw_layout["fixed_test_access"] is False, "raw fixed-test access mismatch")
    total_rows = len(SITES) * DEVELOPMENT_MEMBERS * HOURS
    scaled_x = np.memmap(
        args.release_attempt / "X_release_scaled_float32.dat",
        mode="r",
        dtype=np.float32,
        shape=(total_rows, FEATURE_COUNT),
    )
    stored = np.memmap(
        args.release_attempt / "release_predictions_physical_float32.dat",
        mode="r",
        dtype=np.float32,
        shape=(total_rows,),
    )
    package = args.release_attempt / "release_0001"
    artifact_path = package / "artifact" / "gpp_surrogate_artifact.pkl"
    artifact_manifest = json.loads((package / "artifact" / "artifact_manifest.json").read_text(encoding="utf-8"))
    require(sha256_file(artifact_path) == artifact_manifest["artifact_sha256"], "artifact hash mismatch")
    require(artifact_manifest["fit_member_count"] == DEVELOPMENT_MEMBERS, "artifact member count mismatch")
    require(artifact_manifest["fixed_test_access"] is False, "artifact fixed-test access mismatch")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(artifact["fit_scope"]["kind"] == "all_development", "artifact fit scope mismatch")
    require(artifact["fit_scope"]["development_member_ids"] == raw_layout["development_member_ids"], "artifact member order mismatch")
    require(artifact["fit_scope"]["fixed_test_access"] is False, "artifact fit fixed-test mismatch")
    handoff_path = package / "handoff" / "gpp_predicted_for_sr.nc"
    handoff_manifest = json.loads((package / "handoff" / "handoff_manifest.json").read_text(encoding="utf-8"))
    require(sha256_file(handoff_path) == handoff_manifest["sha256"], "handoff hash mismatch")
    require(handoff_manifest["artifact_sha256"] == artifact_manifest["artifact_sha256"], "handoff artifact mismatch")
    require(handoff_manifest["development_member_ids"] == raw_layout["development_member_ids"], "handoff manifest member order mismatch")
    require(handoff_manifest["site_order"] == list(SITES), "handoff manifest site order mismatch")
    require(handoff_manifest["fixed_test_access"] is False, "handoff fixed-test access mismatch")
    with Dataset(str(handoff_path), "r") as dataset:
        require(tuple(dataset.variables["GPP_predicted"].dimensions) == ("site", "member", "time"), "handoff dimensions mismatch")
        require(np.asarray(dataset.variables["site"][:], dtype=str).tolist() == list(SITES), "handoff site coordinate mismatch")
        require(np.asarray(dataset.variables["member_id"][:], dtype=str).tolist() == raw_layout["development_member_ids"], "handoff member coordinate mismatch")
        require(np.array_equal(dataset.variables["time"][:], raw_times), "handoff time coordinate mismatch")
        handoff = np.asarray(dataset.variables["GPP_predicted"][:], dtype=np.float32).reshape(-1)

    chunk = int(config["prediction_chunk_rows"])
    chunk_indices = (0, (total_rows // chunk) // 2, (total_rows - 1) // chunk)
    rows = []
    flat_raw = raw_x.reshape(-1, FEATURE_COUNT)
    for chunk_index in chunk_indices:
        start = chunk_index * chunk
        end = min(start + chunk, total_rows)
        original_scaled = np.asarray(scaled_x[start:end], dtype=np.float32)
        raw = np.asarray(flat_raw[start:end], dtype=np.float64)
        manual_scaled = raw.astype(np.float32, copy=True)
        manual_scaled -= np.asarray(artifact["x_mean"])
        manual_scaled /= np.asarray(artifact["x_scale"])
        replay_scaled = (
            artifact["model"].predict(original_scaled).astype(np.float64)
            * float(artifact["y_scale"])
            + float(artifact["y_mean"])
        )
        replay_raw = predict_artifact(artifact, raw)
        rows.append(
            {
                "chunk_index": chunk_index,
                "start": start,
                "end": end,
                "handoff_vs_stored": comparison(handoff[start:end], stored[start:end], 0.0, 0.0, start),
                "scaled_replay_vs_stored": comparison(
                    replay_scaled, stored[start:end], config["reload_rtol"], config["reload_atol"], start
                ),
                "raw_replay_vs_stored": comparison(
                    replay_raw, stored[start:end], config["reload_rtol"], config["reload_atol"], start
                ),
                "manual_vs_original_scaled": comparison(
                    manual_scaled, original_scaled, 0.0, 0.0, start, FEATURE_COUNT
                ),
                "raw_vs_scaled_replay": comparison(
                    replay_raw, replay_scaled, config["reload_rtol"], config["reload_atol"], start
                ),
            }
        )
    report = {
        "schema": "three-stage-gpp-iter008-handoff-replay-diagnostic-v1",
        "result": "diagnostic_complete",
        "reload_rtol": config["reload_rtol"],
        "reload_atol": config["reload_atol"],
        "chunks": rows,
    }
    write_json(args.output / "diagnostic_report.json", report)
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
