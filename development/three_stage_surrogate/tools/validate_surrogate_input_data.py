#!/usr/bin/env python
"""Validate and optionally publish an Iter001 surrogate-input staging package."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np
from netCDF4 import Dataset
import xarray as xr


def _load_prepare_module(repository_root: Path):
    sys.path.insert(0, str(repository_root))
    from development.three_stage_surrogate.tools import prepare_surrogate_input_data as prep

    return prep


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def json_load(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _timestamp_parts(value: Any) -> tuple[int, int, int, int]:
    if hasattr(value, "year"):
        return int(value.year), int(value.month), int(value.day), int(value.hour)
    text = np.datetime_as_string(np.datetime64(value), unit="h")
    return int(text[0:4]), int(text[5:7]), int(text[8:10]), int(text[11:13])


def load_forcing_independently(directory: Path, prep: Any) -> tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]], list[Path]]:
    files = [directory / name for name in prep.expected_month_names()]
    require(all(path.is_file() for path in files), f"independent forcing inventory has missing files: {directory}")
    with xr.open_mfdataset([str(path) for path in files], combine="by_coords") as dataset:
        results: Dict[str, np.ndarray] = {}
        attrs: Dict[str, Dict[str, Any]] = {}
        expected_keys = prep.canonical_time_keys()
        for name in prep.FORCING_VARS:
            require(name in dataset.variables, f"independent forcing variable missing: {name}")
            hourly = dataset[name].resample(time="1h").mean()
            times = np.asarray(hourly["time"].values).reshape(-1)
            keep = np.asarray([not (_timestamp_parts(value)[1:3] == (2, 29)) for value in times], dtype=bool)
            kept_times = times[keep]
            keys = [_timestamp_parts(value) for value in kept_times]
            require(keys == expected_keys, f"independent hourly forcing timestamps mismatch: {name}")
            values = np.ma.asarray(hourly.values)[keep]
            require(not np.any(np.ma.getmaskarray(values)), f"independent forcing has masked values: {name}")
            values = np.asarray(values)
            require(values.shape[0] == prep.N_HOURS, f"independent forcing time length mismatch: {name}")
            require(int(np.prod(values.shape[1:], dtype=np.int64)) == 1, f"independent forcing has non-singleton spatial dimensions: {name}")
            values = values.reshape(prep.N_HOURS).astype(np.float64, copy=False)
            require(np.all(np.isfinite(values)), f"independent forcing has nonfinite values: {name}")
            results[name] = values
            attrs[name] = dict(dataset[name].attrs)
    return results, attrs, files


def validate_parameters(path: Path, names: list[str], values: np.ndarray) -> None:
    with Dataset(str(path), "r") as dataset:
        require(dataset.getncattr("schema") == "three-stage-surrogate-input-v1", "parameter schema mismatch")
        require(len(dataset.dimensions["member"]) == 1024, "parameter member dimension mismatch")
        require(dataset.getncattr("parameter_order").split(",") == names, "parameter order attribute mismatch")
        require(np.array_equal(dataset.variables["member"][:], np.arange(1, 1025)), "parameter member coordinate mismatch")
        require(np.array_equal(dataset.variables["sample_index"][:], np.arange(1024)), "parameter sample coordinate mismatch")
        require(list(dataset.variables["ensemble_id"][:]) == [f"g{i:05d}" for i in range(1, 1025)], "parameter ensemble coordinate mismatch")
        for index, name in enumerate(names):
            require(name in dataset.variables, f"prepared parameter missing: {name}")
            require(np.dtype(dataset.variables[name].dtype) == values[:, index].dtype, f"prepared parameter dtype differs: {name}")
            require(dataset.variables[name].chunking() == [256], f"prepared parameter chunks differ: {name}")
            filters = dataset.variables[name].filters()
            require(filters["zlib"] and filters["shuffle"] and filters["complevel"] == 4, f"prepared parameter compression differs: {name}")
            require(np.array_equal(np.asarray(dataset.variables[name][:]), values[:, index]), f"prepared parameter differs: {name}")


def validate_site(
    prep: Any,
    config: Mapping[str, Any],
    package: Path,
    site: str,
    names: list[str],
    parameters: np.ndarray,
) -> Dict[str, Any]:
    entry = config["sites"][site]
    pickle_path = Path(entry["transient_pickle"])
    spinup_path = Path(entry["spinup_preprocessing"])
    forcing_dir = Path(entry["forcing_directory"])
    surface_path = Path(entry["surface_file"])
    with pickle_path.open("rb") as handle:
        case = pickle.load(handle)
    targets = prep.validate_case(case, site, names, parameters)
    forcing, forcing_attrs, forcing_files = load_forcing_independently(forcing_dir, prep)
    spinup = prep.load_spinup(spinup_path)
    surface, _ = prep.load_surface(surface_path)
    prepared_path = package / "sites" / site / "input_data_v1.nc"
    with Dataset(str(prepared_path), "r") as dataset:
        require(dataset.getncattr("schema") == prep.SCHEMA, f"{site} schema mismatch")
        require(dataset.getncattr("site") == site, f"{site} site attribute mismatch")
        require(len(dataset.dimensions["member"]) == prep.N_MEMBERS, f"{site} member dimension mismatch")
        require(len(dataset.dimensions["time"]) == prep.N_HOURS, f"{site} time dimension mismatch")
        require(np.array_equal(dataset.variables["member"][:], np.arange(1, prep.N_MEMBERS + 1)), f"{site} member coordinate mismatch")
        require(np.array_equal(dataset.variables["sample_index"][:], np.arange(prep.N_MEMBERS)), f"{site} sample coordinate mismatch")
        require(list(dataset.variables["ensemble_id"][:]) == [f"g{i:05d}" for i in range(1, prep.N_MEMBERS + 1)], f"{site} ensemble coordinate mismatch")
        require(np.array_equal(dataset.variables["time"][:], np.arange(prep.N_HOURS)), f"{site} time coordinate mismatch")
        require(dataset.variables["time"].getncattr("calendar") == "noleap", f"{site} calendar mismatch")
        for name in prep.FORCING_VARS:
            require(np.dtype(dataset.variables[name].dtype) == np.dtype("float64"), f"{site} forcing dtype differs: {name}")
            require(dataset.variables[name].chunking() == [8760], f"{site} forcing chunks differ: {name}")
            require(np.array_equal(np.asarray(dataset.variables[name][:]), forcing[name]), f"{site} forcing differs: {name}")
            require(getattr(dataset.variables[name], "units", None) == forcing_attrs[name].get("units"), f"{site} forcing units differ: {name}")
        for name in prep.TARGET_VARS:
            require(np.dtype(dataset.variables[name].dtype) == targets[name].dtype, f"{site} target dtype differs: {name}")
            require(dataset.variables[name].chunking() == [1, 8760], f"{site} target chunks differ: {name}")
            require(np.array_equal(np.asarray(dataset.variables[name][:]), targets[name]), f"{site} target differs: {name}")
            require(dataset.variables[name].getncattr("units") == "gC/m^2/day", f"{site} target units mismatch: {name}")
        for index, name in enumerate(prep.SPINUP_VARS):
            require(np.dtype(dataset.variables[name].dtype) == spinup[index].dtype, f"{site} spinup dtype differs: {name}")
            require(dataset.variables[name].chunking() == [256], f"{site} spinup chunks differ: {name}")
            require(np.array_equal(np.asarray(dataset.variables[name][:]), spinup[index]), f"{site} spinup target differs: {name}")
        for name in prep.SURFACE_VARS:
            require(float(dataset.variables[name].getValue()) == surface[name], f"{site} surface feature differs: {name}")
    source_manifest = json_load(package / "manifests" / "sources" / f"{site}_v1.json")
    sources = source_manifest["sources"]
    require(sources["transient_pickle"]["sha256"] == prep.sha256_file(pickle_path), f"{site} pickle hash mismatch")
    require(sources["spinup_preprocessing"]["sha256"] == prep.sha256_file(spinup_path), f"{site} spinup hash mismatch")
    require(sources["surface_file"]["sha256"] == prep.sha256_file(surface_path), f"{site} surface hash mismatch")
    require([item["sha256"] for item in sources["forcing_files"]] == [prep.sha256_file(path) for path in forcing_files], f"{site} forcing hash mismatch")
    return {
        "site": site,
        "members": prep.N_MEMBERS,
        "hours": prep.N_HOURS,
        "prepared_path": f"sites/{site}/input_data_v1.nc",
        "prepared_sha256": prep.sha256_file(prepared_path),
    }


def validate_snapshot(prep: Any, package: Path) -> Dict[str, Any]:
    snapshot_path = package / "manifests" / "dataset_snapshot_r0001.json"
    snapshot = json_load(snapshot_path)
    require(snapshot.get("schema") == prep.SNAPSHOT_SCHEMA, "snapshot schema mismatch")
    for relative, identity in snapshot["artifacts"].items():
        path = package / relative
        require(path.is_file(), f"snapshot artifact missing: {relative}")
        require(path.stat().st_size == identity["size_bytes"], f"snapshot artifact size mismatch: {relative}")
        require(prep.sha256_file(path) == identity["sha256"], f"snapshot artifact hash mismatch: {relative}")
    catalog = json_load(package / "catalog.json")
    require(catalog["current_snapshot_sha256"] == prep.sha256_file(snapshot_path), "catalog snapshot hash mismatch")
    return snapshot


def validate_common_sources(prep: Any, config: Mapping[str, Any], package: Path) -> None:
    manifest = json_load(package / "manifests" / "sources" / "common_v1.json")
    require(manifest.get("schema") == prep.SOURCE_SCHEMA and manifest.get("role") == "common", "common source manifest schema mismatch")
    for key, configured in config["common_sources"].items():
        identity = manifest["sources"][key]
        path = Path(configured).resolve()
        require(identity["path"] == str(path), f"common source path mismatch: {key}")
        require(identity["size_bytes"] == path.stat().st_size, f"common source size mismatch: {key}")
        require(identity["sha256"] == prep.sha256_file(path), f"common source hash mismatch: {key}")


def validate_split(prep: Any, package: Path, seed: int) -> Dict[str, Any]:
    path = package / "splits" / "member_split_1024_v1.json"
    observed = json_load(path)
    ranked = []
    for member in range(1, prep.N_MEMBERS + 1):
        ensemble = f"g{member:05d}"
        digest = hashlib.sha256(f"three-stage-surrogate-v1|{seed}|{ensemble}".encode("utf-8")).hexdigest()
        ranked.append((digest, ensemble))
    ranked.sort(key=lambda item: (item[0], item[1]))
    fixed_ranked = [ensemble for _, ensemble in ranked[:205]]
    development_ranked = [ensemble for _, ensemble in ranked[205:]]
    require(observed["fixed_test_member_ids_ranked"] == fixed_ranked, "fixed-test ranking mismatch")
    require(observed["development_member_ids_ranked"] == development_ranked, "development ranking mismatch")
    require(observed["fixed_test_member_ids_numeric"] == sorted(fixed_ranked), "fixed-test numeric order mismatch")
    require(observed["development_member_ids_numeric"] == sorted(development_ranked), "development numeric order mismatch")
    development = set(observed["development_member_ids_numeric"])
    fixed = set(observed["fixed_test_member_ids_numeric"])
    universe = {f"g{i:05d}" for i in range(1, prep.N_MEMBERS + 1)}
    require(len(development) == 819 and len(fixed) == 205, "split counts mismatch")
    require(not development.intersection(fixed) and development.union(fixed) == universe, "split overlap/completeness failure")
    return observed


def link_atomically_or_accept(source: Path, destination: Path) -> str:
    if destination.exists():
        require(os.path.samefile(source, destination), f"preexisting publication is not the reviewed staging artifact: {destination}")
        return "accepted_existing_hardlink"
    temporary = destination.with_name(f".{destination.name}.publish-tmp")
    require(not temporary.exists(), f"publication temporary exists: {temporary}")
    os.link(source, temporary)
    os.replace(temporary, destination)
    return "linked"


def publish(package: Path, output_root: Path, validation_report: Path) -> None:
    relative_files = [
        Path("README.md"),
        Path("common/parameters_v1.nc"),
        Path("sites/ABBY/input_data_v1.nc"),
        Path("sites/JERC/input_data_v1.nc"),
        Path("splits/member_split_1024_v1.json"),
        Path("manifests/sources/common_v1.json"),
        Path("manifests/sources/ABBY_v1.json"),
        Path("manifests/sources/JERC_v1.json"),
        Path("manifests/dataset_snapshot_r0001.json"),
    ]
    for relative in relative_files:
        source = package / relative
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        link_atomically_or_accept(source, destination)
    report_destination = output_root / "validation" / "iter001_validation_report.json"
    report_destination.parent.mkdir(parents=True, exist_ok=True)
    if report_destination.exists():
        previous_report = json_load(report_destination)
        current_report = json_load(validation_report)
        require(previous_report.get("result") == "pass", "preexisting validation report is not passing")
        require(previous_report.get("prepare_attempt") == current_report.get("prepare_attempt"), "preexisting validation report belongs to another prepared attempt")
        require(previous_report.get("sites") == current_report.get("sites"), "preexisting validation report has different artifact identities")
        require(previous_report.get("snapshot_revision") == current_report.get("snapshot_revision"), "preexisting validation report has different snapshot revision")
    else:
        link_atomically_or_accept(validation_report, report_destination)
    # The catalog is the single commit marker. Consumers must ignore component files when it is
    # absent. Reaching this step is retry-safe because every earlier artifact is either the exact
    # reviewed staging hardlink or a previously recorded passing validation report.
    link_atomically_or_accept(package / "catalog.json", output_root / "catalog.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--prepare-attempt", required=True, type=int)
    parser.add_argument("--validation-attempt", required=True, type=int)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    require(1 <= args.validation_attempt <= 4, "validation attempt must be in 1..4")
    config = json_load(args.config.resolve())
    repository_root = Path(config["repository_root"]).resolve()
    prep = _load_prepare_module(repository_root)
    import model_ELM  # noqa: F401

    package = args.run_dir.resolve() / "staging" / f"prepare_attempt_{args.prepare_attempt}" / "package"
    require(package.is_dir(), f"prepared package missing: {package}")
    report_path = args.run_dir.resolve() / "validation_attempts" / f"attempt_{args.validation_attempt}" / "validation_report.json"
    require(not report_path.exists(), f"validation report already exists: {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    names, parameters, _ = prep.load_parameters(config)
    validate_common_sources(prep, config, package)
    validate_parameters(package / "common" / "parameters_v1.nc", names, parameters)
    site_results = [validate_site(prep, config, package, site, names, parameters) for site in config["site_order"]]
    split = validate_split(prep, package, int(config["split_seed"]))
    snapshot = validate_snapshot(prep, package)
    report = {
        "schema": "three-stage-surrogate-validation-report-v1",
        "result": "pass",
        "prepare_attempt": args.prepare_attempt,
        "validation_attempt": args.validation_attempt,
        "sites": site_results,
        "parameter_count": len(names),
        "member_count": prep.N_MEMBERS,
        "development_count": split["development_count"],
        "fixed_test_count": split["fixed_test_count"],
        "snapshot_revision": snapshot["revision"],
        "no_training": True,
    }
    prep.atomic_json(report_path, report)
    if args.publish:
        publish(package, Path(config["output_root"]).resolve(), report_path)
    print(
        "VALIDATE_SURROGATE_INPUT_OK "
        f"sites={','.join(config['site_order'])} members={prep.N_MEMBERS} hours={prep.N_HOURS} "
        f"development=819 fixed_test=205 publish={str(args.publish).lower()}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
