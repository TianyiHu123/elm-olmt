"""Validated snapshot loading for the staged three-stage-surrogate campaign."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
from netCDF4 import Dataset


SITES: Tuple[str, ...] = ("ABBY", "JERC")
TARGETS: Tuple[str, ...] = ("TOTSOMC", "TOTSOMN")
PARAMETER_COUNT = 18
MEMBER_COUNT = 1024
DEVELOPMENT_COUNT = 819
FIXED_TEST_COUNT = 205
CLIMATOLOGY_HOURS = 5 * 365 * 24
FEATURE_NAMES_STATIC: Tuple[str, ...] = (
    "PCT_SAND",
    "ORGANIC",
    "PRECTmms_clim_mean",
    "PRECTmms_clim_std",
    "FSDS_clim_mean",
    "TBOT_clim_std",
    "RH_clim_seasonal_amp",
)
MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def schema_sha256(names: Sequence[str]) -> str:
    encoded = json.dumps(list(names), separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _member_number(member_id: str) -> int:
    text = str(member_id)
    require(len(text) == 6 and text.startswith("g") and text[1:].isdigit(), f"invalid member ID: {text}")
    number = int(text[1:])
    require(1 <= number <= MEMBER_COUNT, f"member outside 1..{MEMBER_COUNT}: {text}")
    return number


def _monthly_index(nyears: int = 5) -> np.ndarray:
    values: List[int] = []
    for _ in range(nyears):
        for month, days in enumerate(MONTH_LENGTHS, start=1):
            values.extend([month] * (days * 24))
    result = np.asarray(values, dtype=np.int16)
    require(result.size == CLIMATOLOGY_HOURS, "internal no-leap monthly index length mismatch")
    return result


def compact_climatology(forcing: Mapping[str, np.ndarray]) -> Dict[str, float]:
    """Return the locked five-feature climatology from exactly five no-leap years."""
    needed = ("PRECTmms", "FSDS", "TBOT", "RH")
    for name in needed:
        require(name in forcing, f"missing forcing variable {name}")
        values = np.asarray(forcing[name], dtype=np.float64).reshape(-1)
        require(values.shape == (CLIMATOLOGY_HOURS,), f"{name} climatology length mismatch")
        require(np.all(np.isfinite(values)), f"{name} climatology contains nonfinite values")
    rh = np.asarray(forcing["RH"], dtype=np.float64)
    months = _monthly_index()
    monthly_means = np.asarray([np.mean(rh[months == month]) for month in range(1, 13)])
    return {
        "PRECTmms_clim_mean": float(np.mean(forcing["PRECTmms"])),
        "PRECTmms_clim_std": float(np.std(forcing["PRECTmms"], ddof=0)),
        "FSDS_clim_mean": float(np.mean(forcing["FSDS"])),
        "TBOT_clim_std": float(np.std(forcing["TBOT"], ddof=0)),
        "RH_clim_seasonal_amp": float(np.max(monthly_means) - np.min(monthly_means)),
    }


@dataclass(frozen=True)
class LoadedRows:
    X: np.ndarray
    y: np.ndarray | None
    site: np.ndarray
    member_id: np.ndarray
    parameter_names: Tuple[str, ...]
    feature_names: Tuple[str, ...]


class ThreeStageSnapshot:
    """Strict, development-only reader for the immutable Iter001 snapshot."""

    def __init__(self, root: Path | str, *, verify_component_hashes: bool = True) -> None:
        self.root = Path(root).expanduser().resolve()
        catalog_path = self.root / "catalog.json"
        require(catalog_path.is_file(), f"catalog missing: {catalog_path}")
        self.catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        require(self.catalog.get("schema") == "three-stage-surrogate-catalog-v1", "catalog schema mismatch")
        snapshot_relative = Path(str(self.catalog.get("current_snapshot", "")))
        self.snapshot_path = self.root / snapshot_relative
        require(self.snapshot_path.is_file(), f"snapshot missing: {self.snapshot_path}")
        expected_snapshot_hash = str(self.catalog.get("current_snapshot_sha256", ""))
        observed_snapshot_hash = sha256_file(self.snapshot_path)
        require(observed_snapshot_hash == expected_snapshot_hash, "catalog snapshot hash mismatch")
        self.snapshot_sha256 = observed_snapshot_hash
        self.snapshot = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
        require(self.snapshot.get("schema") == "three-stage-surrogate-snapshot-v1", "snapshot schema mismatch")
        require(self.snapshot.get("revision") == "r0001", "unexpected snapshot revision")
        require(tuple(self.snapshot.get("sites", [])) == SITES, "snapshot site/order mismatch")
        require(int(self.snapshot.get("member_count", -1)) == MEMBER_COUNT, "snapshot member count mismatch")
        self.artifacts = dict(self.snapshot.get("artifacts", {}))
        if verify_component_hashes:
            self.verify_components()

        self.parameter_path = self.root / "common" / "parameters_v1.nc"
        self.split_path = self.root / "splits" / "member_split_1024_v1.json"
        self.common_manifest_path = self.root / "manifests" / "sources" / "common_v1.json"
        self.split = json.loads(self.split_path.read_text(encoding="utf-8"))
        require(self.split.get("schema") == "three-stage-surrogate-member-split-v1", "split schema mismatch")
        require(int(self.split.get("development_count", -1)) == DEVELOPMENT_COUNT, "development count mismatch")
        require(int(self.split.get("fixed_test_count", -1)) == FIXED_TEST_COUNT, "fixed-test count mismatch")
        self.development_ranked = tuple(str(v) for v in self.split["development_member_ids_ranked"])
        self.fixed_test_ranked = tuple(str(v) for v in self.split["fixed_test_member_ids_ranked"])
        require(len(set(self.development_ranked)) == DEVELOPMENT_COUNT, "duplicate development identity")
        require(not set(self.development_ranked).intersection(self.fixed_test_ranked), "split overlap")
        self.development_set = frozenset(self.development_ranked)
        self.fixed_test_set = frozenset(self.fixed_test_ranked)
        self.common_manifest = json.loads(self.common_manifest_path.read_text(encoding="utf-8"))
        self.parameter_names = tuple(str(v) for v in self.common_manifest["parameter_names"])
        require(len(self.parameter_names) == PARAMETER_COUNT, "parameter count mismatch")
        transforms = self.common_manifest["sampling_metadata"]["transforms"]
        require([str(v["name"]) for v in transforms] == list(self.parameter_names), "parameter transform order mismatch")
        self.parameter_metadata = {
            "physical_names": list(self.parameter_names),
            "aliases": [f"parm_{index}" for index in range(PARAMETER_COUNT)],
            "ensemble_pmin": [float(v["lower"]) for v in transforms],
            "ensemble_pmax": [float(v["upper"]) for v in transforms],
        }
        self.feature_names = tuple(self.parameter_names) + FEATURE_NAMES_STATIC
        require(len(self.feature_names) == 25 and len(set(self.feature_names)) == 25, "feature schema mismatch")

    def verify_components(self) -> None:
        for relative, identity in sorted(self.artifacts.items()):
            path = self.root / relative
            require(path.is_file(), f"snapshot component missing: {relative}")
            require(path.stat().st_size == int(identity["size_bytes"]), f"component size mismatch: {relative}")
            require(sha256_file(path) == str(identity["sha256"]), f"component hash mismatch: {relative}")

    def resolve_development_members(self, members: Sequence[str]) -> Tuple[str, ...]:
        ordered = tuple(str(v) for v in members)
        require(bool(ordered), "member selection is empty")
        require(len(set(ordered)) == len(ordered), "member selection contains duplicates")
        forbidden = [member for member in ordered if member not in self.development_set]
        require(not forbidden, f"member selection is outside development partition: {forbidden}")
        return ordered

    def operational_split(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        train = self.development_ranked[:655]
        validation = self.development_ranked[655:]
        require(len(train) == 655 and len(validation) == 164, "operational split size mismatch")
        return train, validation

    def smoke_split(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        train, validation = self.operational_split()
        return train[:80], validation[:20]

    def _parameter_values(self, members: Sequence[str]) -> np.ndarray:
        indices = np.asarray([_member_number(member) - 1 for member in members], dtype=np.int64)
        with Dataset(str(self.parameter_path), "r") as dataset:
            require(dataset.getncattr("parameter_order").split(",") == list(self.parameter_names), "parameter NetCDF order mismatch")
            observed_member = np.asarray(dataset.variables["member"][:], dtype=np.int32)
            require(np.array_equal(observed_member, np.arange(1, MEMBER_COUNT + 1)), "parameter member coordinate mismatch")
            values = np.column_stack(
                [np.asarray(dataset.variables[name][indices], dtype=np.float64) for name in self.parameter_names]
            )
        require(values.shape == (len(members), PARAMETER_COUNT), "parameter selection shape mismatch")
        require(np.all(np.isfinite(values)), "parameter selection contains nonfinite values")
        return values

    def _site_context_and_targets(
        self, site: str, members: Sequence[str], *, include_targets: bool
    ) -> Tuple[np.ndarray, np.ndarray | None]:
        require(site in SITES, f"unsupported site: {site}")
        indices = np.asarray([_member_number(member) - 1 for member in members], dtype=np.int64)
        path = self.root / "sites" / site / "input_data_v1.nc"
        with Dataset(str(path), "r") as dataset:
            require(str(dataset.getncattr("site")) == site, f"site attribute mismatch: {site}")
            time = np.asarray(dataset.variables["time"][:CLIMATOLOGY_HOURS], dtype=np.int64)
            require(np.array_equal(time, np.arange(CLIMATOLOGY_HOURS)), f"{site} first-five-year time axis mismatch")
            time_var = dataset.variables["time"]
            require(str(getattr(time_var, "units", "")) == "hours since 2018-01-01 00:00:00", f"{site} time units mismatch")
            require(str(getattr(time_var, "calendar", "")) == "noleap", f"{site} calendar mismatch")
            forcing = {
                name: np.asarray(dataset.variables[name][:CLIMATOLOGY_HOURS], dtype=np.float64)
                for name in ("PRECTmms", "FSDS", "TBOT", "RH")
            }
            climatology = compact_climatology(forcing)
            context_values = [
                float(np.asarray(dataset.variables["PCT_SAND"][:])),
                float(np.asarray(dataset.variables["ORGANIC"][:])),
                *[float(climatology[name]) for name in FEATURE_NAMES_STATIC[2:]],
            ]
            context = np.tile(np.asarray(context_values, dtype=np.float64), (len(members), 1))
            targets: np.ndarray | None = None
            if include_targets:
                targets = np.column_stack(
                    [np.asarray(dataset.variables[name][indices], dtype=np.float64) for name in TARGETS]
                )
        require(context.shape == (len(members), len(FEATURE_NAMES_STATIC)), "site context shape mismatch")
        require(np.all(np.isfinite(context)), f"{site} context contains nonfinite values")
        if targets is not None:
            require(targets.shape == (len(members), len(TARGETS)), "target selection shape mismatch")
            require(np.all(np.isfinite(targets)) and np.all(targets > 0.0), f"{site} targets must be positive finite")
        return context, targets

    def load_rows(
        self,
        members: Sequence[str],
        *,
        sites: Sequence[str] = SITES,
        include_targets: bool = True,
    ) -> LoadedRows:
        ordered_members = self.resolve_development_members(members)
        ordered_sites = tuple(str(v) for v in sites)
        require(bool(ordered_sites) and len(set(ordered_sites)) == len(ordered_sites), "invalid site selection")
        require(all(site in SITES for site in ordered_sites), "site selection contains unsupported site")
        parameters = self._parameter_values(ordered_members)
        x_blocks: List[np.ndarray] = []
        y_blocks: List[np.ndarray] = []
        site_labels: List[str] = []
        member_labels: List[str] = []
        for site in ordered_sites:
            context, targets = self._site_context_and_targets(site, ordered_members, include_targets=include_targets)
            x_blocks.append(np.column_stack((parameters, context)))
            if targets is not None:
                y_blocks.append(targets)
            site_labels.extend([site] * len(ordered_members))
            member_labels.extend(ordered_members)
        X = np.vstack(x_blocks)
        y = np.vstack(y_blocks) if include_targets else None
        require(X.shape == (len(ordered_sites) * len(ordered_members), 25), "design matrix shape mismatch")
        require(np.all(np.isfinite(X)), "design matrix contains nonfinite values")
        return LoadedRows(
            X=X,
            y=y,
            site=np.asarray(site_labels, dtype="U4"),
            member_id=np.asarray(member_labels, dtype="U6"),
            parameter_names=self.parameter_names,
            feature_names=self.feature_names,
        )


def read_member_file(path: Path | str) -> Tuple[str, ...]:
    values = tuple(line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip())
    require(bool(values), f"member file is empty: {path}")
    return values


def write_member_file(path: Path | str, members: Iterable[str]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(f"{member}\n" for member in members), encoding="utf-8")
