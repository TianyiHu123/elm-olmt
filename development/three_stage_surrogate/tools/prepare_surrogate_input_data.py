#!/usr/bin/env python
"""Prepare the versioned ABBY/JERC three-stage-surrogate input package.

This utility is deliberately data-only: it performs no fitting, scaling, feature selection, or
target-based partition analysis. It writes an attempt-local staging package that must be checked
and published by ``validate_surrogate_input_data.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np
from netCDF4 import Dataset, num2date


SCHEMA = "three-stage-surrogate-input-v1"
SOURCE_SCHEMA = "three-stage-surrogate-source-v1"
SNAPSHOT_SCHEMA = "three-stage-surrogate-snapshot-v1"
SPLIT_SCHEMA = "three-stage-surrogate-member-split-v1"
FORCING_VARS = ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")
SURFACE_VARS = ("PCT_SAND", "PCT_CLAY", "ORGANIC")
TARGET_VARS = ("GPP", "SR")
SPINUP_VARS = ("TOTSOMC", "TOTSOMN")
N_MEMBERS = 1024
N_HOURS = 7 * 365 * 24
START_YEAR = 2018
END_YEAR = 2024


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
    temporary.replace(path)


def normalized_attribute(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    require(config.get("schema") == "three-stage-surrogate-iter001-config-v1", "config schema mismatch")
    return config


def expected_month_names() -> list[str]:
    return [f"{year:04d}-{month:02d}.nc" for year in range(START_YEAR, END_YEAR + 1) for month in range(1, 13)]


def canonical_time_keys() -> list[Tuple[int, int, int, int]]:
    month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    keys: list[Tuple[int, int, int, int]] = []
    for year in range(START_YEAR, END_YEAR + 1):
        for month, ndays in enumerate(month_days, start=1):
            for day in range(1, ndays + 1):
                for hour in range(24):
                    keys.append((year, month, day, hour))
    require(len(keys) == N_HOURS, f"internal canonical time count mismatch: {len(keys)}")
    return keys


def load_parameters(config: Mapping[str, Any]) -> Tuple[list[str], np.ndarray, Dict[str, Any]]:
    common = config["common_sources"]
    names_path = Path(common["parameter_names"])
    matrix_path = Path(common["parameter_values"])
    metadata_path = Path(common["parameter_metadata"])
    parmfile_path = Path(common["parameter_list"])
    names = names_path.read_text(encoding="utf-8").split()
    parm_names = [line.split()[0] for line in parmfile_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    values = np.loadtxt(matrix_path, dtype=np.float64)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    require(len(names) == 18 and parm_names == names, "parameter names/list must contain the same 18 ordered names")
    require(values.shape == (N_MEMBERS, len(names)), f"parameter matrix shape mismatch: {values.shape}")
    require(np.all(np.isfinite(values)), "parameter matrix contains nonfinite values")
    require(list(metadata.get("parameter_names", [])) == names, "metadata parameter order mismatch")
    leaf = values[:, names.index("leafcn")]
    froot = values[:, names.index("frootcn")]
    constraint = metadata.get("cn_constraint", {})
    gap = float(constraint.get("gap", 0.5))
    livewood = float(constraint.get("livewoodcn", 50.0))
    require(np.all(froot >= leaf + gap), "parameter matrix violates frootcn >= leafcn + gap")
    require(np.all(froot <= livewood - gap), "parameter matrix violates livewoodcn-gap upper support")
    return names, values, metadata


def normalize_member_parameter_matrix(case: Any, n_parameters: int) -> np.ndarray:
    values = np.asarray(case.samples, dtype=np.float64)
    if values.shape == (n_parameters, N_MEMBERS):
        values = values.T
    require(values.shape == (N_MEMBERS, n_parameters), f"pickle samples shape mismatch: {values.shape}")
    return values


def normalize_target(values: Any, name: str) -> np.ndarray:
    array = np.asarray(values)
    if array.shape == (N_HOURS, N_MEMBERS):
        array = array.T
    require(array.shape == (N_MEMBERS, N_HOURS), f"{name} shape mismatch after normalization: {array.shape}")
    require(np.issubdtype(array.dtype, np.number), f"{name} must be numeric")
    require(np.all(np.isfinite(array)), f"{name} contains nonfinite values")
    return array


def validate_case(case: Any, site: str, names: Sequence[str], parameters: np.ndarray) -> Dict[str, np.ndarray]:
    case_names = [str(value) for value in list(getattr(case, "ensemble_parms", []))]
    require(case_names == list(names), f"{site} pickle parameter order mismatch")
    case_parameters = normalize_member_parameter_matrix(case, len(names))
    require(np.array_equal(case_parameters, parameters), f"{site} pickle parameter values differ from shared design")
    require(hasattr(case, "output") and isinstance(case.output, dict), f"{site} pickle missing output dictionary")
    targets = {name: normalize_target(case.output[name], f"{site} {name}") for name in TARGET_VARS if name in case.output}
    require(set(targets) == set(TARGET_VARS), f"{site} pickle lacks GPP or SR")
    taxis = np.asarray(case.output.get("taxis", []), dtype=np.float64).reshape(-1)
    expected = START_YEAR + np.arange(N_HOURS, dtype=np.float64) / 8760.0
    require(taxis.shape == (N_HOURS,), f"{site} taxis shape mismatch: {taxis.shape}")
    require(np.allclose(taxis, expected, rtol=0.0, atol=5e-12), f"{site} taxis is not the expected no-leap hourly axis")
    stored_site = str(getattr(case, "site", ""))
    require(not stored_site or stored_site == site, f"{site} pickle stores unexpected site={stored_site!r}")
    return targets


def _time_vector(dataset: Dataset, path: Path) -> Tuple[str, np.ndarray]:
    require("time" in dataset.variables, f"forcing file lacks time coordinate: {path}")
    var = dataset.variables["time"]
    units = getattr(var, "units", None)
    calendar = getattr(var, "calendar", "standard")
    require(bool(units), f"forcing time lacks units: {path}")
    decoded = np.asarray(num2date(var[:], units=units, calendar=calendar, only_use_cftime_datetimes=True), dtype=object)
    return calendar, decoded.reshape(-1)


def _forcing_vector(dataset: Dataset, name: str, ntime: int, path: Path) -> Tuple[np.ndarray, Dict[str, Any]]:
    require(name in dataset.variables, f"forcing variable {name} missing from {path}")
    var = dataset.variables[name]
    require("time" in var.dimensions, f"forcing variable {name} has no time dimension in {path}")
    array = np.ma.asarray(var[:])
    require(not np.any(np.ma.getmaskarray(array)), f"forcing variable {name} has masked values in {path}")
    values = np.asarray(array)
    time_axis = var.dimensions.index("time")
    values = np.moveaxis(values, time_axis, 0)
    require(values.shape[0] == ntime, f"forcing {name} time length mismatch in {path}")
    require(int(np.prod(values.shape[1:], dtype=np.int64)) == 1, f"forcing {name} has non-singleton spatial dimensions {values.shape}")
    values = values.reshape(ntime)
    require(np.all(np.isfinite(values)), f"forcing {name} contains nonfinite values in {path}")
    attrs = {
        key: normalized_attribute(getattr(var, key))
        for key in var.ncattrs()
        if key not in {"_FillValue", "missing_value"}
    }
    return values, attrs


def aggregate_hourly_values(
    observed_hour_keys: Sequence[Tuple[int, int, int, int]],
    observed_full_keys: Sequence[Tuple[int, int, int, int, int, int]],
    raw: Mapping[str, np.ndarray],
    expected_keys: Sequence[Tuple[int, int, int, int]],
) -> Dict[str, np.ndarray]:
    require(list(observed_full_keys) == sorted(observed_full_keys), "forcing timestamps are not monotonically ordered")
    require(len(observed_full_keys) == len(set(observed_full_keys)), "forcing contains duplicate exact timestamps")
    require(all(values.shape == (len(observed_hour_keys),) for values in raw.values()), "forcing raw vector length mismatch")
    combined = {name: np.empty(len(expected_keys), dtype=np.float64) for name in raw}
    position = 0
    for hour_index, expected_key in enumerate(expected_keys):
        start = position
        while position < len(observed_hour_keys) and observed_hour_keys[position] == expected_key:
            position += 1
        count = position - start
        require(count in (1, 2), f"forcing hour {expected_key} has {count} source records, expected 1 or 2")
        for name, values in raw.items():
            combined[name][hour_index] = float(np.mean(values[start:position]))
    require(position == len(observed_hour_keys), "forcing has timestamps outside the canonical no-leap axis")
    return combined


def load_forcing(directory: Path) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]], list[Path]]:
    expected_names = expected_month_names()
    files = [directory / name for name in expected_names]
    observed_names = sorted(path.name for path in directory.glob("*.nc") if path.is_file())
    require(observed_names == expected_names, f"forcing inventory mismatch under {directory}")
    canonical = canonical_time_keys()
    values_by_var: Dict[str, list[np.ndarray]] = {name: [] for name in FORCING_VARS}
    attrs_by_var: Dict[str, Dict[str, Any]] = {}
    observed_hour_keys: list[Tuple[int, int, int, int]] = []
    observed_full_keys: list[Tuple[int, int, int, int, int, int]] = []
    for path in files:
        with Dataset(str(path), "r") as dataset:
            _, times = _time_vector(dataset, path)
            keep = np.asarray([not (int(t.month) == 2 and int(t.day) == 29) for t in times], dtype=bool)
            kept_times = times[keep]
            observed_hour_keys.extend((int(t.year), int(t.month), int(t.day), int(t.hour)) for t in kept_times)
            observed_full_keys.extend(
                (int(t.year), int(t.month), int(t.day), int(t.hour), int(t.minute), int(t.second))
                for t in kept_times
            )
            for name in FORCING_VARS:
                vector, attrs = _forcing_vector(dataset, name, times.size, path)
                values_by_var[name].append(vector[keep])
                if name in attrs_by_var:
                    require(attrs_by_var[name] == attrs, f"forcing attributes for {name} vary across months")
                else:
                    attrs_by_var[name] = attrs
    raw = {name: np.concatenate(parts) for name, parts in values_by_var.items()}
    combined = aggregate_hourly_values(observed_hour_keys, observed_full_keys, raw, canonical)
    for name, values in combined.items():
        require(values.shape == (N_HOURS,), f"forcing {name} prepared length mismatch")
        require(np.all(np.isfinite(values)), f"forcing {name} contains nonfinite prepared values")
    return combined, attrs_by_var, files


def load_surface(path: Path) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]]]:
    values: Dict[str, float] = {}
    attrs: Dict[str, Dict[str, Any]] = {}
    with Dataset(str(path), "r") as dataset:
        for name in SURFACE_VARS:
            require(name in dataset.variables, f"surface variable {name} missing from {path}")
            var = dataset.variables[name]
            array = np.ma.asarray(var[:], dtype=np.float64)
            require(not np.any(np.ma.getmaskarray(array)), f"surface variable {name} contains masked values")
            raw = np.asarray(array, dtype=np.float64)
            require(np.all(np.isfinite(raw)), f"surface variable {name} contains nonfinite values")
            values[name] = float(np.sum(raw) if name == "ORGANIC" else np.mean(raw))
            attrs[name] = {
                key: normalized_attribute(getattr(var, key))
                for key in var.ncattrs()
                if key not in {"_FillValue", "missing_value"}
            }
    return values, attrs


def load_spinup(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    with Dataset(str(path), "r") as dataset:
        members = np.asarray(dataset.variables["member"][:], dtype=np.int32)
        require(np.array_equal(members, np.arange(1, N_MEMBERS + 1, dtype=np.int32)), "spinup member identity mismatch")
        arrays = []
        for name in SPINUP_VARS:
            var = dataset.variables[name]
            values = np.asarray(var[:])
            require(values.shape == (N_MEMBERS,), f"spinup {name} shape mismatch")
            require(np.all(np.isfinite(values)) and np.all(values > 0.0), f"spinup {name} must be positive finite")
            arrays.append(values)
    return arrays[0], arrays[1]


def _copy_attrs(variable: Any, attrs: Mapping[str, Any]) -> None:
    for key, value in attrs.items():
        if key not in {"_FillValue", "missing_value", "scale_factor", "add_offset"}:
            setattr(variable, key, value)


def _create_member_coordinates(dataset: Dataset) -> None:
    dataset.createDimension("member", N_MEMBERS)
    member = dataset.createVariable("member", "i4", ("member",))
    member[:] = np.arange(1, N_MEMBERS + 1, dtype=np.int32)
    member.long_name = "canonical PPE member identity (1-based)"
    sample = dataset.createVariable("sample_index", "i4", ("member",))
    sample[:] = np.arange(N_MEMBERS, dtype=np.int32)
    sample.long_name = "zero-based row index in the shared Sobol parameter matrix"
    ensemble = dataset.createVariable("ensemble_id", str, ("member",))
    ensemble[:] = np.asarray([f"g{i:05d}" for i in range(1, N_MEMBERS + 1)], dtype=object)
    ensemble.long_name = "ELM PPE ensemble directory identity"


def write_parameters(path: Path, names: Sequence[str], values: np.ndarray, source_hashes: Mapping[str, str]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with Dataset(str(temporary), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = SCHEMA
        dataset.role = "shared PPE parameter values"
        dataset.parameter_order = ",".join(names)
        dataset.created_utc = now_utc()
        dataset.source_hashes_json = json.dumps(dict(source_hashes), sort_keys=True)
        _create_member_coordinates(dataset)
        for index, name in enumerate(names):
            variable = dataset.createVariable(name, values.dtype, ("member",), zlib=True, complevel=4, shuffle=True, chunksizes=(256,))
            variable[:] = values[:, index]
            variable.long_name = f"PPE parameter {name}"
    temporary.replace(path)


def write_site(
    path: Path,
    site: str,
    targets: Mapping[str, np.ndarray],
    forcing: Mapping[str, np.ndarray],
    forcing_attrs: Mapping[str, Mapping[str, Any]],
    spinup: Tuple[np.ndarray, np.ndarray],
    surface: Mapping[str, float],
    surface_attrs: Mapping[str, Mapping[str, Any]],
    source_hashes: Mapping[str, Any],
) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with Dataset(str(temporary), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = SCHEMA
        dataset.site = site
        dataset.created_utc = now_utc()
        dataset.calendar_alignment = "Gregorian forcing hourly means with February 29 removed, exact timestamp join to ELM no-leap target axis"
        dataset.source_hashes_json = json.dumps(dict(source_hashes), sort_keys=True)
        _create_member_coordinates(dataset)
        dataset.createDimension("time", N_HOURS)
        time = dataset.createVariable("time", "i4", ("time",), chunksizes=(8760,))
        time[:] = np.arange(N_HOURS, dtype=np.int32)
        time.units = "hours since 2018-01-01 00:00:00"
        time.calendar = "noleap"
        time.long_name = "validated ELM no-leap hourly timestamp"
        for name in FORCING_VARS:
            values = forcing[name]
            variable = dataset.createVariable(name, values.dtype, ("time",), zlib=True, complevel=4, shuffle=True, chunksizes=(8760,))
            variable[:] = values
            _copy_attrs(variable, forcing_attrs[name])
            variable.temporal_aggregation = "arithmetic mean of one or two source records within each hour"
        for name in TARGET_VARS:
            values = targets[name]
            variable = dataset.createVariable(name, values.dtype, ("member", "time"), zlib=True, complevel=4, shuffle=True, chunksizes=(1, 8760))
            variable[:] = values
            variable.units = "gC/m^2/day"
            variable.source_value_policy = "serialized OLMT postprocessed values, unchanged"
        for name, values, units in (
            ("TOTSOMC", spinup[0], "gC/m^2"),
            ("TOTSOMN", spinup[1], "gN/m^2"),
        ):
            variable = dataset.createVariable(name, values.dtype, ("member",), zlib=True, complevel=4, shuffle=True, chunksizes=(256,))
            variable[:] = values
            variable.units = units
            variable.target_definition = "soil1-soil4 full-profile integral over 10 active decomposition layers"
        for name in SURFACE_VARS:
            variable = dataset.createVariable(name, "f8")
            variable.assignValue(surface[name])
            _copy_attrs(variable, surface_attrs[name])
            variable.feature_reduction = "sum over source values" if name == "ORGANIC" else "mean over source values"
    temporary.replace(path)


def make_split(seed: int) -> Dict[str, Any]:
    namespace = "three-stage-surrogate-v1"
    ranked = []
    for member in range(1, N_MEMBERS + 1):
        ensemble = f"g{member:05d}"
        digest = hashlib.sha256(f"{namespace}|{seed}|{ensemble}".encode("utf-8")).hexdigest()
        ranked.append((digest, ensemble))
    ranked.sort(key=lambda item: (item[0], item[1]))
    fixed_ranked = [ensemble for _, ensemble in ranked[:205]]
    development_ranked = [ensemble for _, ensemble in ranked[205:]]
    return {
        "schema": SPLIT_SCHEMA,
        "namespace": namespace,
        "seed": seed,
        "algorithm": "SHA256(namespace|seed|ensemble_id), ascending digest then ensemble_id",
        "eligible_member_count": N_MEMBERS,
        "development_count": len(development_ranked),
        "fixed_test_count": len(fixed_ranked),
        "development_member_ids_ranked": development_ranked,
        "fixed_test_member_ids_ranked": fixed_ranked,
        "development_member_ids_numeric": sorted(development_ranked),
        "fixed_test_member_ids_numeric": sorted(fixed_ranked),
    }


def source_identity(path: Path) -> Dict[str, Any]:
    return {"path": str(path.resolve()), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def prepare(config_path: Path, run_dir: Path, attempt: int) -> Path:
    require(1 <= attempt <= 4, "attempt must be in 1..4 (initial plus three correction/retry chances)")
    config = load_config(config_path)
    repository_root = Path(config["repository_root"]).resolve()
    sys.path.insert(0, str(repository_root))
    import model_ELM  # noqa: F401  # register ELMcase for pickle loading

    package = run_dir / "staging" / f"prepare_attempt_{attempt}" / "package"
    require(not package.exists(), f"attempt package already exists: {package}")
    package.mkdir(parents=True)
    names, parameters, metadata = load_parameters(config)
    common_sources = {key: source_identity(Path(value)) for key, value in config["common_sources"].items()}
    write_parameters(package / "common" / "parameters_v1.nc", names, parameters, {k: v["sha256"] for k, v in common_sources.items()})

    site_source_manifests: Dict[str, Any] = {}
    for site in config["site_order"]:
        entry = config["sites"][site]
        pickle_path = Path(entry["transient_pickle"])
        spinup_path = Path(entry["spinup_preprocessing"])
        forcing_dir = Path(entry["forcing_directory"])
        surface_path = Path(entry["surface_file"])
        forcing_files = [forcing_dir / name for name in expected_month_names()]
        site_sources = {
            "transient_pickle": source_identity(pickle_path),
            "spinup_preprocessing": source_identity(spinup_path),
            "surface_file": source_identity(surface_path),
            "forcing_files": [source_identity(path) for path in forcing_files],
        }
        with pickle_path.open("rb") as handle:
            case = pickle.load(handle)
        targets = validate_case(case, site, names, parameters)
        forcing, forcing_attrs, _ = load_forcing(forcing_dir)
        spinup = load_spinup(spinup_path)
        surface, surface_attrs = load_surface(surface_path)
        output_path = package / "sites" / site / "input_data_v1.nc"
        write_site(output_path, site, targets, forcing, forcing_attrs, spinup, surface, surface_attrs, {
            "transient_pickle": site_sources["transient_pickle"]["sha256"],
            "spinup_preprocessing": site_sources["spinup_preprocessing"]["sha256"],
            "surface_file": site_sources["surface_file"]["sha256"],
            "forcing_files": [item["sha256"] for item in site_sources["forcing_files"]],
        })
        site_source_manifests[site] = {"schema": SOURCE_SCHEMA, "site": site, "sources": site_sources}
        atomic_json(package / "manifests" / "sources" / f"{site}_v1.json", site_source_manifests[site])
        del case, targets, forcing, spinup

    common_manifest = {"schema": SOURCE_SCHEMA, "role": "common", "sources": common_sources, "parameter_names": names, "sampling_metadata": metadata}
    atomic_json(package / "manifests" / "sources" / "common_v1.json", common_manifest)
    split = make_split(int(config["split_seed"]))
    atomic_json(package / "splits" / "member_split_1024_v1.json", split)

    artifact_paths = [
        Path("common/parameters_v1.nc"),
        Path("sites/ABBY/input_data_v1.nc"),
        Path("sites/JERC/input_data_v1.nc"),
        Path("splits/member_split_1024_v1.json"),
        Path("manifests/sources/common_v1.json"),
        Path("manifests/sources/ABBY_v1.json"),
        Path("manifests/sources/JERC_v1.json"),
    ]
    artifacts = {}
    for relative in artifact_paths:
        identity = source_identity(package / relative)
        identity["path"] = str(relative)
        artifacts[str(relative)] = identity
    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "revision": "r0001",
        "created_utc": now_utc(),
        "sites": list(config["site_order"]),
        "member_count": N_MEMBERS,
        "hour_count_by_site": {site: N_HOURS for site in config["site_order"]},
        "artifacts": artifacts,
        "preparation": {"config": str(config_path.resolve()), "attempt": attempt, "repository_commit": config["repository_commit"]},
    }
    atomic_json(package / "manifests" / "dataset_snapshot_r0001.json", snapshot)
    snapshot_hash = sha256_file(package / "manifests" / "dataset_snapshot_r0001.json")
    atomic_json(package / "catalog.json", {"schema": "three-stage-surrogate-catalog-v1", "current_snapshot": "manifests/dataset_snapshot_r0001.json", "current_snapshot_sha256": snapshot_hash})
    readme = package / "README.md"
    readme.write_text(
        "# Three-stage surrogate input data\n\n"
        "This collection contains immutable component artifacts and appendable snapshot revisions.\n"
        "A snapshot is published only when catalog.json exists and identifies its manifest; ignore\n"
        "component files in the absence of that catalog commit marker.\n"
        "The original transferred sources remain authoritative and unchanged. Derived feature or\n"
        "training-matrix caches may be added only by later authorized iterations with explicit\n"
        "source, feature-schema, split, and upstream-artifact identities.\n",
        encoding="utf-8",
    )
    print(f"PREPARE_SURROGATE_INPUT_OK package={package} attempt={attempt}", flush=True)
    return package


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    prepare(args.config.resolve(), args.run_dir.resolve(), args.attempt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
