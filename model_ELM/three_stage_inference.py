"""Frozen ABBY/JERC spinup -> GPP -> SR inference from published releases."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from netCDF4 import Dataset

from .three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from .three_stage_gpp import (
    FEATURE_COUNT as GPP_FEATURE_COUNT,
    FORCING_FEATURE_NAMES,
    FORCING_NAMES,
    SURFACE_NAMES,
    engineer_forcing_window,
    feature_names as gpp_feature_names,
    predict_artifact as predict_gpp_artifact,
)
from .three_stage_gpp_release import load_release_artifact as load_gpp_release
from .three_stage_spinup_release import (
    load_release_artifact as load_spinup_release,
    predict_release as predict_spinup_release,
)
from .three_stage_sr import (
    FEATURE_COUNT as SR_FEATURE_COUNT,
    feature_names as sr_feature_names,
    predict_artifact as predict_sr_artifact,
)
from .three_stage_sr_release import load_release_artifact as load_sr_release
from .three_stage_spinup import predict_compact_models


SCHEMA = "three-stage-frozen-inference-v1"
OUTPUT_SCHEMA = "three-stage-frozen-inference-output-v1"
PARAMETER_COUNT = 18
CN_GAP = 0.5
LIVEWOOD_CN = 50.0


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deterministic_predict(
    function: Any, artifact: Mapping[str, Any], values: np.ndarray, chunk_rows: int | None
) -> np.ndarray:
    """Evaluate with a fixed one-row numerical kernel inside optional outer chunks.

    sklearn's dense MLP prediction can choose different BLAS reductions for different batch
    shapes.  The frozen artifacts are small enough that a one-row kernel is the clearest stable
    inference contract.  ``chunk_rows`` still bounds traversal and intermediate retention, but
    cannot change the floating-point operation shape used for an individual prediction.
    """
    matrix = np.asarray(values)
    step = matrix.shape[0] if chunk_rows is None else chunk_rows
    require(isinstance(step, int) and step > 0, "chunk_rows must be a positive integer")
    blocks: list[np.ndarray] = []
    for start in range(0, matrix.shape[0], step):
        stop = min(start + step, matrix.shape[0])
        rows = [
            np.asarray(function(artifact, matrix[index : index + 1]), dtype=np.float64).reshape(-1)
            for index in range(start, stop)
        ]
        blocks.append(np.concatenate(rows))
    return np.concatenate(blocks)


def _deterministic_spinup(artifact: Mapping[str, Any], values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values)
    rows = [
        np.asarray(predict_spinup_release(artifact, matrix[index : index + 1]), dtype=np.float64)
        for index in range(matrix.shape[0])
    ]
    return np.vstack(rows)


@dataclass(frozen=True)
class InferenceResult:
    site: str
    parameter_names: tuple[str, ...]
    parameters: np.ndarray
    time: np.ndarray
    totsomc: np.ndarray
    totsomn: np.ndarray
    gpp: np.ndarray
    sr: np.ndarray
    provenance: dict[str, Any]


@dataclass(frozen=True)
class FoldInferenceResult:
    """Fold-specific full-chain result with both raw and policy-gated GPP."""

    site: str
    parameter_names: tuple[str, ...]
    parameters: np.ndarray
    time: np.ndarray
    totsomc: np.ndarray
    totsomn: np.ndarray
    gpp_raw: np.ndarray
    gpp: np.ndarray
    sr: np.ndarray
    provenance: dict[str, Any]


class FoldThreeStageInference:
    """Memory-bounded inference for one fitted development fold.

    This interface is deliberately separate from :class:`FrozenThreeStageInference`: the latter
    remains the historical published-release contract, while this class consumes fold-local
    artifacts and applies the prospective physical GPP output policy before every SR call.
    """

    def __init__(
        self,
        snapshot: ThreeStageSnapshot,
        spinup_artifact: Mapping[str, Any],
        gpp_artifact: Mapping[str, Any],
        sr_artifact: Mapping[str, Any],
        *,
        split_id: int,
        gpp_output_policy: str = "hard_zero_v1",
    ) -> None:
        require(gpp_output_policy == "hard_zero_v1", "unsupported GPP output policy")
        self.snapshot = snapshot
        self.spinup = spinup_artifact
        self.gpp = gpp_artifact
        self.sr = sr_artifact
        self.split_id = int(split_id)
        self.gpp_output_policy = gpp_output_policy
        require(self.spinup.get("schema") == "three-stage-spinup-fold-artifact-v1", "fold spinup schema mismatch")
        require(self.gpp.get("schema") == "three-stage-gpp-fold-artifact-v1", "fold GPP schema mismatch")
        require(self.sr.get("schema") == "three-stage-sr-fold-artifact-v1", "fold SR schema mismatch")
        require(int(self.spinup.get("split_id", -1)) == self.split_id, "spinup split mismatch")
        require(int(self.gpp.get("split_id", -1)) == self.split_id, "GPP split mismatch")
        require(int(self.sr.get("split_id", -1)) == self.split_id, "SR split mismatch")
        require(self.spinup.get("feature_names") == list(snapshot.feature_names), "fold spinup feature mismatch")
        require(self.gpp.get("feature_names") == list(gpp_feature_names(snapshot)), "fold GPP feature mismatch")
        require(self.sr.get("feature_names") == list(sr_feature_names(snapshot)), "fold SR feature mismatch")
        require(len(self.spinup.get("feature_names", [])) == 25, "fold spinup feature count mismatch")
        require(len(self.gpp.get("feature_names", [])) == GPP_FEATURE_COUNT == 43, "fold GPP feature count mismatch")
        require(len(self.sr.get("feature_names", [])) == SR_FEATURE_COUNT == 44, "fold SR feature count mismatch")
        require(self.sr.get("gpp_output_policy") == gpp_output_policy, "fold SR GPP policy mismatch")
        spinup_members = list(self.spinup.get("train_member_ids", []))
        require(spinup_members == list(self.gpp.get("train_member_ids", [])), "spinup/GPP scope mismatch")
        require(spinup_members == list(self.sr.get("train_member_ids", [])), "spinup/SR scope mismatch")
        require(len(spinup_members) == len(set(spinup_members)) and bool(spinup_members), "fold training scope invalid")
        require(set(spinup_members).issubset(snapshot.development_set), "fold artifact scope is outside development")
        require(not set(spinup_members).intersection(snapshot.fixed_test_set), "fold artifact contains fixed-test member")
        self.parameter_names = tuple(snapshot.parameter_names)
        transforms = snapshot.common_manifest["sampling_metadata"]["transforms"]
        self.lower = np.asarray([float(item["lower"]) for item in transforms], dtype=np.float64)
        self.upper = np.asarray([float(item["upper"]) for item in transforms], dtype=np.float64)
        constraint = snapshot.common_manifest["sampling_metadata"]["cn_constraint"]
        require(constraint["enabled"] is True, "fold conditional C:N support is not enabled")
        require(int(constraint["leafcn_index"]) == 16 and int(constraint["frootcn_index"]) == 17, "fold conditional C:N indices mismatch")
        require(float(constraint["gap"]) == CN_GAP and float(constraint["livewoodcn"]) == LIVEWOOD_CN, "fold conditional C:N constants mismatch")

    def validate_parameters(self, parameters: Sequence[float] | np.ndarray) -> np.ndarray:
        matrix = np.asarray(parameters, dtype=np.float64)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        require(matrix.ndim == 2 and matrix.shape[1] == PARAMETER_COUNT and matrix.shape[0] >= 1, "parameters must have shape (n,18)")
        require(np.all(np.isfinite(matrix)), "parameters contain nonfinite values")
        require(np.all(matrix >= self.lower) and np.all(matrix <= self.upper), "parameters violate physical bounds")
        require(np.all(matrix[:, 17] >= matrix[:, 16] + CN_GAP), "parameters violate leafcn/frootcn gap")
        require(np.all(matrix[:, 17] <= min(self.upper[17], LIVEWOOD_CN - CN_GAP)), "parameters violate livewood C:N support")
        return matrix

    def _site_context(self, site: str) -> tuple[np.ndarray, np.ndarray]:
        require(site in SITES, f"unsupported site: {site}")
        context, _ = self.snapshot._site_context_and_targets(
            site, (self.snapshot.development_ranked[0],), include_targets=False
        )
        with Dataset(str(self.snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            surface = np.asarray(
                [float(np.asarray(dataset.variables[name][:])) for name in SURFACE_NAMES], dtype=np.float64
            )
        require(context.shape == (1, 7) and surface.shape == (3,), "fold site context shape mismatch")
        return context[0], surface

    def predict_to_arrays(
        self,
        parameters: Sequence[float] | np.ndarray,
        *,
        site: str,
        forcing: Mapping[str, np.ndarray],
        time: np.ndarray,
        start: int,
        end: int,
        gpp_raw_output: np.ndarray,
        gpp_output: np.ndarray,
        sr_output: np.ndarray,
        member_chunk: int = 2,
    ) -> np.ndarray:
        """Write a complete fold prediction into caller-owned arrays or memmaps."""
        matrix = self.validate_parameters(parameters)
        require(isinstance(member_chunk, int) and member_chunk > 0, "member_chunk must be positive")
        axis = np.asarray(time, dtype=np.int64).reshape(-1)
        require(axis.size == end and np.array_equal(axis, np.arange(axis.size)), "fold time axis invalid")
        require(0 <= start < end <= 61320, "fold window bounds invalid")
        require(start == 0 or start >= 720, "fold nonzero window requires 720-hour history")
        hours = end - start
        expected_shape = (matrix.shape[0], hours)
        for name, values in (("raw GPP", gpp_raw_output), ("gated GPP", gpp_output), ("SR", sr_output)):
            require(values.shape == expected_shape, f"{name} output shape mismatch")
        raw = {name: np.asarray(forcing[name], dtype=np.float64).reshape(-1) for name in FORCING_NAMES}
        require(all(values.shape == axis.shape and np.all(np.isfinite(values)) for values in raw.values()), "fold forcing invalid")
        forcing_features = engineer_forcing_window(raw, axis, start, end).astype(np.float32)
        spinup_context, surface = self._site_context(site)
        spinup_x = np.column_stack((matrix, np.tile(spinup_context, (matrix.shape[0], 1))))
        cn = predict_compact_models(self.spinup, spinup_x)
        require(cn.shape == (matrix.shape[0], 2) and np.all(cn > 0.0), "fold C/N output invalid")
        for first in range(0, matrix.shape[0], member_chunk):
            last = min(first + member_chunk, matrix.shape[0])
            count = last - first
            block = np.empty((count, hours, GPP_FEATURE_COUNT), dtype=np.float32)
            block[:, :, : len(FORCING_FEATURE_NAMES)] = forcing_features[None, :, :]
            static = np.column_stack((matrix[first:last], np.tile(surface, (count, 1)), cn[first:last]))
            block[:, :, len(FORCING_FEATURE_NAMES) :] = static[:, None, :].astype(np.float32)
            flat_gpp = predict_gpp_artifact(self.gpp, block.reshape(-1, GPP_FEATURE_COUNT)).reshape(count, hours)
            gated = np.maximum(flat_gpp, 0.0)
            require(np.all(np.isfinite(flat_gpp)) and np.all(gated >= 0.0), "fold GPP output invalid")
            sr_features = np.empty((count, hours, SR_FEATURE_COUNT), dtype=np.float32)
            sr_features[:, :, :-1] = block
            sr_features[:, :, -1] = gated.astype(np.float32)
            sr = predict_sr_artifact(self.sr, sr_features.reshape(-1, SR_FEATURE_COUNT)).reshape(count, hours)
            require(np.all(np.isfinite(sr)), "fold SR output invalid")
            gpp_raw_output[first:last] = flat_gpp
            gpp_output[first:last] = gated
            sr_output[first:last] = sr
        return cn

    def predict(
        self,
        parameters: Sequence[float] | np.ndarray,
        *,
        site: str,
        forcing: Mapping[str, np.ndarray],
        time: np.ndarray,
        start: int,
        end: int,
        member_chunk: int = 2,
    ) -> FoldInferenceResult:
        matrix = self.validate_parameters(parameters)
        hours = end - start
        gpp_raw = np.empty((matrix.shape[0], hours), dtype=np.float64)
        gpp = np.empty_like(gpp_raw)
        sr = np.empty_like(gpp_raw)
        cn = self.predict_to_arrays(
            matrix, site=site, forcing=forcing, time=time, start=start, end=end,
            gpp_raw_output=gpp_raw, gpp_output=gpp, sr_output=sr, member_chunk=member_chunk,
        )
        provenance = {
            "schema": "three-stage-fold-inference-v1",
            "snapshot_sha256": self.snapshot.snapshot_sha256,
            "split_id": self.split_id,
            "parameter_names": list(self.parameter_names),
            "site": site,
            "start": start,
            "end": end,
            "upstream_mode": "fold_predicted_cn_and_gated_predicted_same_hour_gpp",
            "gpp_output_policy": self.gpp_output_policy,
            "contains_elm_truth": False,
            "fixed_test_access": False,
            "training_or_fitting": False,
        }
        return FoldInferenceResult(
            site=site, parameter_names=self.parameter_names, parameters=matrix.copy(),
            time=np.asarray(time, dtype=np.int64)[start:end].copy(), totsomc=cn[:, 0].copy(),
            totsomn=cn[:, 1].copy(), gpp_raw=gpp_raw, gpp=gpp, sr=sr, provenance=provenance,
        )


class FrozenThreeStageInference:
    """Strict inference-only interface for the three published ABBY/JERC releases."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        require(self.config.get("schema") == "three-stage-inference-iter014-config-v1", "configuration schema mismatch")
        self.snapshot = ThreeStageSnapshot(self.config["snapshot_root"], verify_component_hashes=False)
        require(self.snapshot.snapshot_sha256 == self.config["snapshot_sha256"], "snapshot identity mismatch")
        require(sha256_file(self.snapshot.split_path) == self.config["global_split_sha256"], "split identity mismatch")
        self._verify_path("spinup_release_manifest", "spinup_release_manifest_sha256")
        self._verify_path("gpp_release_manifest", "gpp_release_manifest_sha256")
        self._verify_path("sr_release_manifest", "sr_release_manifest_sha256")
        self.spinup, self.spinup_manifest = load_spinup_release(Path(self.config["spinup_artifact_directory"]))
        self.gpp, self.gpp_manifest = load_gpp_release(Path(self.config["gpp_artifact_directory"]))
        self.sr, self.sr_manifest = load_sr_release(Path(self.config["sr_artifact_directory"]))
        require(self.spinup_manifest["artifact_sha256"] == self.config["spinup_artifact_sha256"], "spinup artifact mismatch")
        require(self.gpp_manifest["artifact_sha256"] == self.config["gpp_artifact_sha256"], "GPP artifact mismatch")
        require(self.sr_manifest["artifact_sha256"] == self.config["sr_artifact_sha256"], "SR artifact mismatch")
        require(self.spinup["feature_names"] == list(self.snapshot.feature_names), "spinup feature order mismatch")
        require(self.gpp["feature_names"] == list(gpp_feature_names(self.snapshot)), "GPP feature order mismatch")
        require(self.sr["feature_names"] == list(sr_feature_names(self.snapshot)), "SR feature order mismatch")
        require(len(self.gpp["feature_names"]) == GPP_FEATURE_COUNT, "GPP feature count mismatch")
        require(len(self.sr["feature_names"]) == SR_FEATURE_COUNT, "SR feature count mismatch")
        self.parameter_names = tuple(self.snapshot.parameter_names)
        transforms = self.snapshot.common_manifest["sampling_metadata"]["transforms"]
        self.lower = np.asarray([float(item["lower"]) for item in transforms], dtype=np.float64)
        self.upper = np.asarray([float(item["upper"]) for item in transforms], dtype=np.float64)
        constraint = self.snapshot.common_manifest["sampling_metadata"]["cn_constraint"]
        require(constraint["enabled"] is True, "conditional C:N support is not enabled")
        require(int(constraint["leafcn_index"]) == 16 and int(constraint["frootcn_index"]) == 17, "conditional C:N indices mismatch")
        require(float(constraint["gap"]) == CN_GAP and float(constraint["livewoodcn"]) == LIVEWOOD_CN, "conditional C:N constants mismatch")

    @classmethod
    def from_json(cls, path: Path | str) -> "FrozenThreeStageInference":
        return cls(_read_json(Path(path)))

    def _verify_path(self, path_key: str, hash_key: str) -> None:
        path = Path(self.config[path_key])
        require(path.is_file(), f"missing dependency: {path_key}")
        require(sha256_file(path) == self.config[hash_key], f"dependency identity mismatch: {path_key}")

    def validate_parameters(self, parameters: Sequence[float] | np.ndarray) -> np.ndarray:
        matrix = np.asarray(parameters, dtype=np.float64)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        require(matrix.ndim == 2 and matrix.shape[1] == PARAMETER_COUNT and matrix.shape[0] >= 1, "parameters must have shape (n,18)")
        require(np.all(np.isfinite(matrix)), "parameters contain nonfinite values")
        require(np.all(matrix >= self.lower) and np.all(matrix <= self.upper), "parameters violate physical bounds")
        leafcn = matrix[:, 16]
        frootcn = matrix[:, 17]
        require(np.all(frootcn >= leafcn + CN_GAP), "parameters violate leafcn/frootcn gap")
        require(np.all(frootcn <= min(self.upper[17], LIVEWOOD_CN - CN_GAP)), "parameters violate livewood C:N support")
        return matrix

    def _site_context(self, site: str) -> tuple[np.ndarray, np.ndarray]:
        require(site in SITES, f"unsupported site: {site}")
        context, _ = self.snapshot._site_context_and_targets(
            site, (self.snapshot.development_ranked[0],), include_targets=False
        )
        with Dataset(str(self.snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            surface = np.asarray([float(np.asarray(dataset.variables[name][:])) for name in SURFACE_NAMES], dtype=np.float64)
        require(context.shape == (1, 7) and surface.shape == (3,), "site context shape mismatch")
        require(np.all(np.isfinite(context)) and np.all(np.isfinite(surface)), "site context contains nonfinite values")
        return context[0], surface

    def predict(
        self,
        parameters: Sequence[float] | np.ndarray,
        *,
        site: str,
        forcing: Mapping[str, np.ndarray],
        time: np.ndarray,
        start: int,
        end: int,
        chunk_rows: int | None = None,
    ) -> InferenceResult:
        matrix = self.validate_parameters(parameters)
        require(site in SITES, f"unsupported site: {site}")
        axis = np.asarray(time, dtype=np.int64).reshape(-1)
        require(axis.size == end, "forcing input must be the ordered prefix through end")
        require(np.array_equal(axis, np.arange(axis.size)), "time must be consecutive no-leap hours from the canonical origin")
        require(0 <= start < end <= 61320, "window bounds invalid")
        require(start == 0 or start >= 720, "nonzero windows require 720-hour history")
        raw = {name: np.asarray(forcing[name], dtype=np.float64).reshape(-1) for name in FORCING_NAMES}
        require(all(values.shape == axis.shape and np.all(np.isfinite(values)) for values in raw.values()), "forcing values invalid")

        spinup_context, surface = self._site_context(site)
        spinup_x = np.column_stack((matrix, np.tile(spinup_context, (matrix.shape[0], 1))))
        cn = _deterministic_spinup(self.spinup, spinup_x)
        forcing_features = engineer_forcing_window(raw, axis, start, end)
        hours = end - start
        gpp_blocks: list[np.ndarray] = []
        sr_blocks: list[np.ndarray] = []
        for row in range(matrix.shape[0]):
            static = np.concatenate((matrix[row], surface, cn[row]))
            require(static.shape == (23,), "hourly static feature shape mismatch")
            gpp_x = np.column_stack((forcing_features, np.tile(static, (hours, 1))))
            gpp = _deterministic_predict(predict_gpp_artifact, self.gpp, gpp_x, chunk_rows)
            sr_x = np.column_stack((gpp_x, gpp))
            sr = _deterministic_predict(predict_sr_artifact, self.sr, sr_x, chunk_rows)
            require(gpp.shape == (hours,) and sr.shape == (hours,), "hourly output shape mismatch")
            require(np.all(np.isfinite(gpp)) and np.all(np.isfinite(sr)), "hourly output contains nonfinite values")
            gpp_blocks.append(gpp)
            sr_blocks.append(sr)
        provenance = {
            "schema": SCHEMA,
            "snapshot_sha256": self.config["snapshot_sha256"],
            "global_split_sha256": self.config["global_split_sha256"],
            "spinup_release_manifest_sha256": self.config["spinup_release_manifest_sha256"],
            "spinup_artifact_sha256": self.config["spinup_artifact_sha256"],
            "gpp_release_manifest_sha256": self.config["gpp_release_manifest_sha256"],
            "gpp_artifact_sha256": self.config["gpp_artifact_sha256"],
            "sr_release_manifest_sha256": self.config["sr_release_manifest_sha256"],
            "sr_artifact_sha256": self.config["sr_artifact_sha256"],
            "parameter_names": list(self.parameter_names),
            "site": site,
            "start": start,
            "end": end,
            "upstream_mode": "predicted_cn_and_predicted_same_hour_gpp",
            "contains_elm_truth": False,
            "fixed_test_access": False,
            "training_or_fitting": False,
        }
        return InferenceResult(
            site=site,
            parameter_names=self.parameter_names,
            parameters=matrix.copy(),
            time=axis[start:end].copy(),
            totsomc=cn[:, 0].copy(),
            totsomn=cn[:, 1].copy(),
            gpp=np.vstack(gpp_blocks),
            sr=np.vstack(sr_blocks),
            provenance=provenance,
        )


def write_result(path: Path | str, result: InferenceResult) -> None:
    target = Path(path)
    require(not target.exists(), f"output already exists: {target}")
    with Dataset(str(target), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = OUTPUT_SCHEMA
        dataset.provenance_json = json.dumps(result.provenance, sort_keys=True, separators=(",", ":"))
        dataset.createDimension("sample", result.parameters.shape[0])
        dataset.createDimension("parameter", result.parameters.shape[1])
        dataset.createDimension("time", result.time.size)
        dataset.createVariable("parameter_name", str, ("parameter",))[:] = np.asarray(result.parameter_names, dtype=object)
        dataset.createVariable("parameters", "f8", ("sample", "parameter"))[:] = result.parameters
        dataset.createVariable("time", "i8", ("time",))[:] = result.time
        dataset.variables["time"].units = "hours since 2018-01-01 00:00:00"
        dataset.variables["time"].calendar = "noleap"
        for name, values, units in (
            ("TOTSOMC", result.totsomc, "gC/m^2"),
            ("TOTSOMN", result.totsomn, "gN/m^2"),
        ):
            variable = dataset.createVariable(name, "f8", ("sample",))
            variable[:] = values
            variable.units = units
        for name, values in (("GPP", result.gpp), ("SR", result.sr)):
            variable = dataset.createVariable(name, "f8", ("sample", "time"))
            variable[:] = values
            variable.units = "gC/m^2/day"


def read_result(path: Path | str) -> InferenceResult:
    with Dataset(str(path), "r") as dataset:
        require(dataset.getncattr("schema") == OUTPUT_SCHEMA, "output schema mismatch")
        provenance = json.loads(dataset.getncattr("provenance_json"))
        names = tuple(np.asarray(dataset.variables["parameter_name"][:], dtype=str).tolist())
        return InferenceResult(
            site=str(provenance["site"]),
            parameter_names=names,
            parameters=np.asarray(dataset.variables["parameters"][:], dtype=np.float64),
            time=np.asarray(dataset.variables["time"][:], dtype=np.int64),
            totsomc=np.asarray(dataset.variables["TOTSOMC"][:], dtype=np.float64),
            totsomn=np.asarray(dataset.variables["TOTSOMN"][:], dtype=np.float64),
            gpp=np.asarray(dataset.variables["GPP"][:], dtype=np.float64),
            sr=np.asarray(dataset.variables["SR"][:], dtype=np.float64),
            provenance=provenance,
        )


def _cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--parameters-json", type=Path, required=True)
    parser.add_argument("--forcing-npz", type=Path, required=True)
    parser.add_argument("--site", choices=SITES, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--chunk-rows", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    parameters = np.asarray(_read_json(args.parameters_json)["parameters"], dtype=np.float64)
    with np.load(args.forcing_npz, allow_pickle=False) as data:
        forcing = {name: np.asarray(data[name]) for name in FORCING_NAMES}
        time = np.asarray(data["time"])
    engine = FrozenThreeStageInference.from_json(args.config)
    result = engine.predict(
        parameters, site=args.site, forcing=forcing, time=time, start=args.start, end=args.end,
        chunk_rows=args.chunk_rows,
    )
    write_result(args.output, result)


if __name__ == "__main__":
    _cli()
