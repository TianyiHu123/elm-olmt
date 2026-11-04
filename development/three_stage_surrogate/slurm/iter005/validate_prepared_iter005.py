#!/usr/bin/env python
"""Fresh-process validation of Iter005 prepared data."""
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

from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_gpp import HOURS, SURFACE_NAMES, UPSTREAM_NAMES, load_prepared, validate_prepared, write_json


FORCING = ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")


def rolling(values: np.ndarray, hour: int, window: int, total: bool) -> float:
    start = max(0, hour - window + 1)
    selected = np.asarray(values[start:hour + 1], dtype=np.float64)
    return float(np.sum(selected) if total else np.mean(selected))


def direct_row(dataset: Dataset, hour: int) -> list[float]:
    raw = {name: np.asarray(dataset.variables[name][:], dtype=np.float64) for name in FORCING}
    day = (hour // 24) % 365
    hod = hour % 24
    values = [float(raw[name][hour]) for name in FORCING]
    values.extend((
        float(np.sin(2.0 * np.pi * hod / 24.0)), float(np.cos(2.0 * np.pi * hod / 24.0)),
        float(np.sin(2.0 * np.pi * day / 365.0)), float(np.cos(2.0 * np.pi * day / 365.0)),
    ))
    values.extend(rolling(raw["TBOT"], hour, window, False) for window in (24, 168, 720))
    values.extend(rolling(raw["PRECTmms"], hour, window, True) for window in (24, 168, 720))
    values.extend(float(raw[name][hour] - rolling(raw[name], hour, 720, False)) for name in ("PRECTmms", "FSDS", "TBOT"))
    return values


def validate_source_rows(config: dict, prepared: Path) -> dict:
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(sha256_file(Path(config["predicted_cn_handoff"])) == config["predicted_cn_sha256"], "source handoff hash mismatch")
    layout, X, y, scalers = load_prepared(prepared)
    params = snapshot._parameter_values(snapshot.development_ranked)
    position = {member: index for index, member in enumerate(snapshot.development_ranked)}
    with Dataset(config["predicted_cn_handoff"], "r") as handoff:
        require(handoff.getncattr("schema") == "three-stage-spinup-predicted-cn-handoff-v1", "source handoff schema mismatch")
        require(np.asarray(handoff.variables["site"][:], dtype=str).tolist() == list(SITES), "source handoff site order mismatch")
        require(np.asarray(handoff.variables["member_id"][:], dtype=str).tolist() == list(snapshot.development_ranked), "source handoff member order mismatch")
        upstream = {name: np.asarray(handoff.variables[name][:], dtype=np.float64) for name in UPSTREAM_NAMES}
    for name, values in upstream.items():
        require(values.shape == (2, 819) and np.all(np.isfinite(values)) and np.all(values > 0.0), f"source handoff {name} invalid")
    checked = []
    for offset in layout["offsets"]:
        site = str(offset["site"])
        site_index = list(layout["sites"]).index(site)
        members = list(offset["members"])
        with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            surface = [float(np.asarray(dataset.variables[name][:])) for name in SURFACE_NAMES]
            cases = ((0, 0), (0, 23), (0, 24), (len(members) // 2, 719), (len(members) - 1, HOURS - 1))
            for member_index, hour in cases:
                member = members[member_index]
                global_row = int(offset["start"]) + member_index * HOURS + hour
                member_position = position[member]
                raw = np.asarray(
                    direct_row(dataset, hour) + params[member_position].tolist() + surface
                    + [float(upstream[name][site_index, member_position]) for name in UPSTREAM_NAMES],
                    dtype=np.float64,
                )
                expected_x = (raw - scalers["x_mean"]) / scalers["x_scale"]
                expected_y = (float(dataset.variables["GPP"][int(member[1:]) - 1, hour]) - float(scalers["y_mean"][0])) / float(scalers["y_scale"][0])
                require(np.allclose(np.asarray(X[global_row], dtype=np.float64), expected_x, rtol=2e-5, atol=2e-5), f"source feature mismatch at row {global_row}")
                require(np.isclose(float(y[global_row]), expected_y, rtol=2e-5, atol=2e-5), f"source target mismatch at row {global_row}")
                checked.append({"row": global_row, "partition": offset["partition"], "site": site, "member_id": member, "hour": hour})
    require(len(checked) == 20, "source validation coverage mismatch")
    return {"source_rows": checked, "source_rows_reconstructed": len(checked)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared-directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = validate_prepared(config, args.prepared_directory, full_hashes=True)
    report.update(validate_source_rows(config, args.prepared_directory))
    write_json(args.output, report)
    print(f"ITER005_PREPARED_VALIDATE_OK rows={report['rows']} features={report['features']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
