#!/usr/bin/env python
"""Inspect, transactionally repath, or recover the nine Puma case pickles.

Run this utility only on a Puma compute node under the migration runtime contract
recorded in ``handoff/CURRENT.md``.  It intentionally loads one pickle at a time.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import pickle
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np


REPOSITORY_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

EXPECTED_SITES = ("ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL")
EXPECTED_MONTHLY_FILES = {
    "ABBY": 84,
    "JERC": 84,
    "OSBS": 84,
    "SOAP": 84,
    "RMNP": 84,
    "TALL": 84,
    "TEAK": 72,
    "WREF": 72,
    "YELL": 72,
}
FORCING_VARIABLES = ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")
SURFACE_VARIABLES = ("PCT_SAND", "PCT_CLAY", "ORGANIC")
PERLMUTTER_PATH_MARKERS = ("/pscratch/", "/global/cfs/", "/global/homes/")
STAGED_SUFFIX = ".puma.staged"
BACKUP_SUFFIX = ".perlmutter.bak"
MONTHLY_NAME = re.compile(r"^(\d{4})-(\d{2})\.nc$")


class MigrationError(RuntimeError):
    """A migration precondition, validation, or transaction failed."""


@dataclass(frozen=True)
class CasePaths:
    name: str
    site: str
    original: Path
    staged: Path
    backup: Path
    metdir: Path


@dataclass(frozen=True)
class CompactInvariants:
    class_name: str
    case_name: str
    site: str
    nsamples: int
    dependcase: str
    finidat: str
    top_level_keys: tuple[str, ...]
    array_shapes: tuple[tuple[str, tuple[int, ...], str], ...]
    dictionary_keys: tuple[tuple[str, tuple[str, ...]], ...]
    compact_digest: str


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and transactionally repath the nine transferred OLMT case pickles."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true", help="Read-only full Puma preflight")
    mode.add_argument("--apply", action="store_true", help="Preflight, stage, validate, and activate all nine")
    mode.add_argument(
        "--recover",
        action="store_true",
        help="Restore every original path from preserved backups after interrupted activation",
    )
    parser.add_argument("--pickle-dir", required=True, type=Path)
    parser.add_argument(
        "--cases",
        required=True,
        help="Comma-separated nine case names, without the .pkl suffix",
    )
    parser.add_argument("--run-root", required=True, type=Path, help="Puma NEON_ppe run root")
    parser.add_argument("--met-root", required=True, type=Path, help="Puma CTSM_NEON meteorology root")
    return parser


def _parse_cases(raw: str, pickle_dir: Path, met_root: Path) -> list[CasePaths]:
    names = [value.strip() for value in raw.split(",") if value.strip()]
    if len(names) != len(set(names)):
        raise MigrationError("--cases contains duplicate case names")
    sites = [name.split("_", 1)[0] for name in names]
    if len(names) != 9 or set(sites) != set(EXPECTED_SITES):
        raise MigrationError(
            "--cases must contain exactly one case for each migration site: "
            + ",".join(EXPECTED_SITES)
        )

    resolved: list[CasePaths] = []
    for name, site in zip(names, sites):
        original = pickle_dir / f"{name}.pkl"
        resolved.append(
            CasePaths(
                name=name,
                site=site,
                original=original,
                staged=Path(f"{original}{STAGED_SUFFIX}"),
                backup=Path(f"{original}{BACKUP_SUFFIX}"),
                metdir=met_root / site / f"1x1pt_{site}" / "CLM1PT_data",
            )
        )
    return resolved


def _load_case(path: Path) -> Any:
    # Register ELMcase only when deserializing the trusted repository pickles.
    import model_ELM  # noqa: F401

    with path.open("rb") as stream:
        return pickle.load(stream)


def _assert_repository_root() -> None:
    required = (
        REPOSITORY_ROOT / "train_surrogate_spinup.py",
        REPOSITORY_ROOT / "development" / "spinup_surrogate" / "WORKFLOW.md",
        REPOSITORY_ROOT / "development" / "hpc" / "puma.md",
        REPOSITORY_ROOT / "conda_envs" / "OLMT_puma.yml",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise MigrationError(
            "Fixed repository root is missing required tracked artifact(s): " + ", ".join(missing)
        )


def _canonical_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return {"float": value.hex()}
    if isinstance(value, np.generic):
        return _canonical_scalar(value.item())
    if isinstance(value, Path):
        return {"path": str(value)}
    return None


def _collect_compact_structure(
    value: Any,
    path: str,
    *,
    digest: "hashlib._Hash",
    arrays: list[tuple[str, tuple[int, ...], str]],
    dictionaries: list[tuple[str, tuple[str, ...]]],
    seen: set[int],
) -> None:
    scalar = _canonical_scalar(value)
    if scalar is not None or value is None:
        digest.update(json.dumps([path, scalar], sort_keys=True, separators=(",", ":")).encode())
        return

    if isinstance(value, np.ndarray):
        item = (path, tuple(int(dim) for dim in value.shape), str(value.dtype))
        arrays.append(item)
        digest.update(json.dumps(["array", *item], separators=(",", ":")).encode())
        return

    identity = id(value)
    if identity in seen:
        digest.update(json.dumps([path, "cycle"], separators=(",", ":")).encode())
        return
    seen.add(identity)
    try:
        if isinstance(value, dict):
            keys = tuple(sorted(str(key) for key in value.keys()))
            dictionaries.append((path, keys))
            digest.update(json.dumps([path, "dict", keys], separators=(",", ":")).encode())
            for key in sorted(value.keys(), key=lambda item: str(item)):
                _collect_compact_structure(
                    value[key],
                    f"{path}[{key!r}]",
                    digest=digest,
                    arrays=arrays,
                    dictionaries=dictionaries,
                    seen=seen,
                )
            return
        if isinstance(value, (list, tuple)):
            digest.update(
                json.dumps([path, type(value).__name__, len(value)], separators=(",", ":")).encode()
            )
            for index, item in enumerate(value):
                _collect_compact_structure(
                    item,
                    f"{path}[{index}]",
                    digest=digest,
                    arrays=arrays,
                    dictionaries=dictionaries,
                    seen=seen,
                )
            return
        if isinstance(value, set):
            normalized = sorted(repr(item) for item in value)
            digest.update(json.dumps([path, "set", normalized], separators=(",", ":")).encode())
            return
        digest.update(
            json.dumps(
                [path, "object", f"{type(value).__module__}.{type(value).__qualname__}"],
                separators=(",", ":"),
            ).encode()
        )
    finally:
        seen.remove(identity)


def _snapshot_case(case: Any) -> CompactInvariants:
    if not hasattr(case, "__dict__"):
        raise MigrationError(f"Loaded object has no __dict__: {type(case)!r}")
    state = vars(case)
    required = ("casename", "site", "nsamples", "dependcase", "finidat", "runroot", "metdir")
    missing = [key for key in required if key not in state]
    if missing:
        raise MigrationError(f"Case is missing required attribute(s): {missing}")

    arrays: list[tuple[str, tuple[int, ...], str]] = []
    dictionaries: list[tuple[str, tuple[str, ...]]] = []
    digest = hashlib.sha256()
    for key in sorted(state):
        if key in {"runroot", "metdir"}:
            digest.update(json.dumps([key, "migration-field"], separators=(",", ":")).encode())
            continue
        _collect_compact_structure(
            state[key],
            key,
            digest=digest,
            arrays=arrays,
            dictionaries=dictionaries,
            seen=set(),
        )
    return CompactInvariants(
        class_name=f"{type(case).__module__}.{type(case).__qualname__}",
        case_name=str(case.casename),
        site=str(case.site),
        nsamples=int(case.nsamples),
        dependcase=str(case.dependcase),
        finidat=str(case.finidat),
        top_level_keys=tuple(sorted(str(key) for key in state)),
        array_shapes=tuple(sorted(arrays)),
        dictionary_keys=tuple(sorted(dictionaries)),
        compact_digest=digest.hexdigest(),
    )


def _assert_same_invariants(before: CompactInvariants, after: CompactInvariants, name: str) -> None:
    if before != after:
        changed = [
            field
            for field in before.__dataclass_fields__
            if getattr(before, field) != getattr(after, field)
        ]
        raise MigrationError(f"Staged pickle changed compact invariant(s) for {name}: {changed}")


def _assert_expected_case(case: Any, paths: CasePaths) -> CompactInvariants:
    invariants = _snapshot_case(case)
    if invariants.case_name != paths.name:
        raise MigrationError(
            f"Pickle/name mismatch: requested {paths.name}, stored casename={invariants.case_name}"
        )
    if invariants.site != paths.site:
        raise MigrationError(
            f"Case/site mismatch for {paths.name}: expected {paths.site}, stored site={invariants.site}"
        )
    if invariants.nsamples != 100:
        raise MigrationError(f"Expected nsamples=100 for {paths.name}, found {invariants.nsamples}")
    return invariants


def _contains_perlmutter_path(value: Path | str) -> bool:
    normalized = f"/{str(value).strip('/')}"
    return any(marker in f"{normalized}/" for marker in PERLMUTTER_PATH_MARKERS)


def _assert_puma_roots(run_root: Path, met_root: Path) -> None:
    expected_run = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe")
    expected_met = Path("/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON")
    if run_root != expected_run:
        raise MigrationError(f"--run-root must be {expected_run}, got {run_root}")
    if met_root != expected_met:
        raise MigrationError(f"--met-root must be {expected_met}, got {met_root}")
    for label, root in (("run root", run_root), ("meteorology root", met_root)):
        if _contains_perlmutter_path(root):
            raise MigrationError(f"{label} retains a Perlmutter path dependency: {root}")
        if not root.is_dir():
            raise MigrationError(f"{label} does not exist: {root}")


def _month_index(year: int, month: int) -> int:
    return year * 12 + month - 1


def _validate_monthly_sequence(site: str, files: Sequence[Path]) -> None:
    expected_count = EXPECTED_MONTHLY_FILES[site]
    if len(files) != expected_count:
        raise MigrationError(
            f"{site} forcing file count is {len(files)}, expected {expected_count}: {files[0].parent if files else ''}"
        )
    parsed: list[tuple[int, int]] = []
    for path in files:
        match = MONTHLY_NAME.match(path.name)
        if not match:
            raise MigrationError(f"Unexpected forcing filename for {site}: {path.name}")
        year, month = (int(value) for value in match.groups())
        if not 1 <= month <= 12:
            raise MigrationError(f"Invalid month in forcing filename: {path.name}")
        parsed.append((year, month))
    indices = [_month_index(year, month) for year, month in parsed]
    expected = list(range(indices[0], indices[0] + expected_count))
    if indices != expected:
        raise MigrationError(f"{site} forcing files are not one complete contiguous monthly sequence")


def _validate_forcing_netcdf(case: Any, paths: CasePaths) -> None:
    from netCDF4 import Dataset, num2date

    forcing_files = sorted(path for path in paths.metdir.glob("*.nc") if path.is_file())
    _validate_monthly_sequence(paths.site, forcing_files)
    covered_years: set[int] = set()
    for forcing_file in forcing_files:
        try:
            with Dataset(str(forcing_file), "r") as dataset:
                missing = [name for name in FORCING_VARIABLES if name not in dataset.variables]
                if missing:
                    raise MigrationError(f"{forcing_file} is missing forcing variables: {missing}")
                if "time" not in dataset.variables:
                    raise MigrationError(f"{forcing_file} has no time variable")
                time_var = dataset.variables["time"]
                if time_var.size == 0 or not hasattr(time_var, "units"):
                    raise MigrationError(f"{forcing_file} has an empty or unitless time variable")
                calendar = getattr(time_var, "calendar", "standard")
                time_values = np.asarray(time_var[:]).reshape(-1)
                timestamps = num2date(
                    time_values,
                    units=time_var.units,
                    calendar=calendar,
                    only_use_cftime_datetimes=True,
                )
                covered_years.update(
                    int(timestamp.year)
                    for timestamp in np.asarray(timestamps, dtype=object).reshape(-1)
                )
        except MigrationError:
            raise
        except Exception as exc:
            raise MigrationError(f"Unable to open or inspect forcing NetCDF {forcing_file}: {exc}") from exc

    start_year = int(getattr(case, "met_startyear"))
    end_year = int(getattr(case, "met_endyear_spinup"))
    if end_year < start_year:
        raise MigrationError(
            f"Invalid stored spinup-cycle years for {paths.name}: {start_year}-{end_year}"
        )
    missing_years = [year for year in range(start_year, end_year + 1) if year not in covered_years]
    if missing_years:
        raise MigrationError(
            f"{paths.name} forcing coverage does not contain stored spinup-cycle years: {missing_years}"
        )


def _open_netcdf(path: Path, label: str) -> None:
    from netCDF4 import Dataset

    try:
        with Dataset(str(path), "r"):
            pass
    except Exception as exc:
        raise MigrationError(f"Unable to open {label} NetCDF {path}: {exc}") from exc


def _resolved_restart(case: Any, run_root: Path, ens_num: int) -> Path:
    group = f"g{ens_num:05d}"
    return run_root / "UQ" / str(case.dependcase) / group / Path(str(case.finidat)).name


def _validate_resolved_data(case: Any, paths: CasePaths, run_root: Path) -> None:
    if not paths.metdir.is_dir():
        raise MigrationError(f"Meteorology directory does not exist for {paths.name}: {paths.metdir}")
    restart_files: list[Path] = []
    surface_files: list[Path] = []
    for ens_num in range(1, 101):
        restart = _resolved_restart(case, run_root, ens_num)
        if not restart.is_file():
            raise MigrationError(f"Missing restart for {paths.name} ensemble {ens_num}: {restart}")
        matches = sorted(restart.parent.glob("surfdata*.nc"))
        if len(matches) != 1:
            raise MigrationError(
                f"Expected one ensemble surface file for {paths.name} ensemble {ens_num}, found {len(matches)}"
            )
        restart_files.append(restart)
        surface_files.append(matches[0])

    if len(set(restart_files)) != 100 or len(set(surface_files)) != 100:
        raise MigrationError(f"{paths.name} did not resolve to 100 distinct restart and surface files")
    for path in restart_files:
        _open_netcdf(path, "restart")
    for path in surface_files:
        _open_netcdf(path, "surface")
        from netCDF4 import Dataset

        with Dataset(str(path), "r") as dataset:
            missing = [name for name in SURFACE_VARIABLES if name not in dataset.variables]
            if missing:
                raise MigrationError(f"{path} is missing surface variables: {missing}")
    _validate_forcing_netcdf(case, paths)


def _inspect_inputs(case_paths: Sequence[CasePaths], run_root: Path) -> dict[str, CompactInvariants]:
    snapshots: dict[str, CompactInvariants] = {}
    for paths in case_paths:
        if not paths.original.is_file():
            raise MigrationError(f"Case pickle does not exist: {paths.original}")
        print(f"Inspecting {paths.name} from {paths.original}", flush=True)
        case = _load_case(paths.original)
        try:
            snapshot = _assert_expected_case(case, paths)
            _validate_resolved_data(case, paths, run_root)
            proposed_runroot = str(run_root)
            proposed_metdir = str(paths.metdir)
            if _contains_perlmutter_path(proposed_runroot) or _contains_perlmutter_path(proposed_metdir):
                raise MigrationError(f"Proposed Puma paths retain Perlmutter dependency for {paths.name}")
            print(
                f"  runroot: {case.runroot} -> {proposed_runroot}\n"
                f"  metdir:  {case.metdir} -> {proposed_metdir}\n"
                f"  resolved: 100 restarts, 100 surfaces, "
                f"{EXPECTED_MONTHLY_FILES[paths.site]} forcing months",
                flush=True,
            )
            snapshots[paths.name] = snapshot
        finally:
            del case
            gc.collect()
    return snapshots


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _dump_staged(case: Any, staged: Path) -> None:
    temporary = staged.with_name(f".{staged.name}.tmp.{os.getpid()}")
    try:
        with temporary.open("xb") as stream:
            pickle.dump(case, stream, protocol=pickle.HIGHEST_PROTOCOL)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, staged)
        _fsync_directory(staged.parent)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _assert_clean_transaction_paths(case_paths: Sequence[CasePaths]) -> None:
    conflicts: list[str] = []
    for paths in case_paths:
        if paths.staged.exists():
            conflicts.append(str(paths.staged))
        if paths.backup.exists():
            conflicts.append(str(paths.backup))
    if conflicts:
        raise MigrationError(
            "Existing staged/backup migration artifacts require inspection or --recover: "
            + ", ".join(conflicts)
        )


def _assert_staging_capacity(case_paths: Sequence[CasePaths]) -> None:
    required = sum(paths.original.stat().st_size for paths in case_paths)
    available = shutil.disk_usage(case_paths[0].original.parent).free
    headroom = 1024**3
    if available < required + headroom:
        raise MigrationError(
            f"Insufficient free space to stage all pickles: need {required + headroom} bytes "
            f"including 1 GiB headroom, have {available}"
        )


def _stage_all(
    case_paths: Sequence[CasePaths],
    run_root: Path,
    snapshots: dict[str, CompactInvariants],
) -> None:
    for paths in case_paths:
        print(f"Staging {paths.name} beside its original", flush=True)
        case = _load_case(paths.original)
        try:
            _assert_same_invariants(snapshots[paths.name], _assert_expected_case(case, paths), paths.name)
            case.runroot = str(run_root)
            case.metdir = str(paths.metdir)
            _dump_staged(case, paths.staged)
        finally:
            del case
            gc.collect()

    for paths in case_paths:
        print(f"Reloading and validating staged {paths.name}", flush=True)
        case = _load_case(paths.staged)
        try:
            staged_snapshot = _assert_expected_case(case, paths)
            _assert_same_invariants(snapshots[paths.name], staged_snapshot, paths.name)
            if str(case.runroot) != str(run_root) or str(case.metdir) != str(paths.metdir):
                raise MigrationError(f"Staged Puma paths are incorrect for {paths.name}")
            if _contains_perlmutter_path(case.runroot) or _contains_perlmutter_path(case.metdir):
                raise MigrationError(f"Staged operational paths retain Perlmutter dependency for {paths.name}")
        finally:
            del case
            gc.collect()


def _restore_backup_link(paths: CasePaths) -> None:
    if paths.original.exists():
        if paths.staged.exists():
            raise MigrationError(
                f"Cannot preserve activated file because staged path already exists: {paths.staged}"
            )
        os.replace(paths.original, paths.staged)
    os.link(paths.backup, paths.original)
    _fsync_directory(paths.original.parent)


def _rollback_activation(case_paths: Sequence[CasePaths]) -> list[str]:
    errors: list[str] = []
    for paths in case_paths:
        try:
            if not paths.backup.exists():
                continue
            if paths.original.exists() and os.path.samefile(paths.original, paths.backup):
                continue
            _restore_backup_link(paths)
        except Exception as exc:
            errors.append(f"{paths.name}: {exc}")
    return errors


def _activate_all(case_paths: Sequence[CasePaths]) -> None:
    try:
        for paths in case_paths:
            os.replace(paths.original, paths.backup)
            _fsync_directory(paths.original.parent)
        for paths in case_paths:
            os.replace(paths.staged, paths.original)
            _fsync_directory(paths.original.parent)
    except Exception as exc:
        rollback_errors = _rollback_activation(case_paths)
        detail = f"; rollback errors: {rollback_errors}" if rollback_errors else "; rollback completed"
        raise MigrationError(f"Activation was interrupted: {exc}{detail}") from exc


def _recover_all(case_paths: Sequence[CasePaths]) -> None:
    unrecoverable = [
        paths.name
        for paths in case_paths
        if not paths.original.is_file() and not paths.backup.is_file()
    ]
    if unrecoverable:
        raise MigrationError(
            "Recovery found case(s) with neither original nor backup: " + ", ".join(unrecoverable)
        )
    errors = _rollback_activation(case_paths)
    if errors:
        raise MigrationError("Recovery was incomplete: " + "; ".join(errors))
    for paths in case_paths:
        if not paths.original.is_file():
            raise MigrationError(f"Recovery verification failed for {paths.name}")
        if paths.backup.is_file() and not os.path.samefile(paths.original, paths.backup):
            raise MigrationError(f"Recovered original does not match its backup for {paths.name}")
    print("Recovery complete. Backups were preserved; staged Puma pickles were not deleted.")


def _apply(case_paths: Sequence[CasePaths], run_root: Path) -> None:
    _assert_clean_transaction_paths(case_paths)
    _assert_staging_capacity(case_paths)
    snapshots = _inspect_inputs(case_paths, run_root)
    _stage_all(case_paths, run_root, snapshots)
    _activate_all(case_paths)
    for paths in case_paths:
        if not paths.original.is_file() or not paths.backup.is_file():
            raise MigrationError(f"Post-activation file verification failed for {paths.name}")
    print("Applied all nine Puma pickle rewrites. Perlmutter backups were preserved.")


def main() -> int:
    args = _build_parser().parse_args()
    pickle_dir = args.pickle_dir.resolve()
    run_root = args.run_root.resolve()
    met_root = args.met_root.resolve()
    try:
        _assert_repository_root()
        if not pickle_dir.is_dir():
            raise MigrationError(f"--pickle-dir does not exist: {pickle_dir}")
        _assert_puma_roots(run_root, met_root)
        case_paths = _parse_cases(args.cases, pickle_dir, met_root)
        if args.inspect:
            _inspect_inputs(case_paths, run_root)
            print("All nine case pickles and resolved Puma data paths passed inspection.")
        elif args.apply:
            _apply(case_paths, run_root)
        else:
            _recover_all(case_paths)
    except Exception as exc:
        print(f"Migration error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
