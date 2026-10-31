"""Frozen-candidate robustness, uncertainty, and release contracts for spinup C/N."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pickle
import shutil
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
from netCDF4 import Dataset
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .three_stage_data import LoadedRows, SITES, TARGETS, ThreeStageSnapshot, require, schema_sha256, sha256_file
from .three_stage_spinup import fit_compact_models, predict_compact_models
from .three_stage_spinup_screen import subset_rows


RELEASE_SCHEMA = "three-stage-spinup-release-v1"
ARTIFACT_MANIFEST_SCHEMA = "three-stage-spinup-release-artifact-manifest-v1"
MODEL_CONFIG: Dict[str, Any] = {
    "hidden_layer_sizes": [64, 32],
    "activation": "tanh",
    "solver": "lbfgs",
    "alpha": 10.0,
    "max_iter": 800,
    "random_state": 42,
}
SPLIT_SEED = 20261031
SPLIT_COUNT = 20
QUANTILES = (0.01, 0.025, 0.05, 0.25, 0.50, 0.75, 0.95, 0.975, 0.99)
PHYSICAL_UNITS = {"TOTSOMC": "gC/m^2", "TOTSOMN": "gN/m^2"}


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def split_design_sha256(value: Mapping[str, Any]) -> str:
    """Hash the split payload with its identity field excluded."""
    payload = {key: item for key, item in value.items() if key != "split_design_sha256"}
    return canonical_hash(payload)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def package_files(root: Path, *, exclude: Iterable[str] = ()) -> List[Dict[str, Any]]:
    omitted = set(exclude)
    records: List[Dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in omitted:
            continue
        records.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return records


def balanced_split_manifest(development_members: Sequence[str]) -> Dict[str, Any]:
    """Create the fresh locked 20-fold balanced repeated-split design."""
    members = tuple(str(value) for value in development_members)
    require(len(members) == 819 and len(set(members)) == 819, "development population mismatch")
    rng = np.random.default_rng(SPLIT_SEED)
    used_extras: set[str] = set()
    splits: List[Dict[str, Any]] = []
    member_array = np.asarray(members, dtype="U6")
    for round_index in range(4):
        permuted = member_array[rng.permutation(member_array.size)].tolist()
        groups = [permuted[index * 164:(index + 1) * 164] for index in range(4)]
        groups.append(permuted[656:])
        extra = next(member for member in permuted[:656] if member not in used_extras)
        used_extras.add(extra)
        groups[4].append(extra)
        for fold_index, validation in enumerate(groups):
            selected = set(validation)
            train = [member for member in members if member not in selected]
            require(len(validation) == len(selected) == 164 and len(train) == 655, "split size mismatch")
            splits.append({
                "split_id": len(splits), "round": round_index, "fold": fold_index,
                "train_member_ids": train, "validation_member_ids": validation,
            })
    counts = {member: 0 for member in members}
    for split in splits:
        for member in split["validation_member_ids"]:
            counts[member] += 1
    require(len(splits) == SPLIT_COUNT, "split count mismatch")
    require(sum(value == 4 for value in counts.values()) == 815, "four-appearance count mismatch")
    require(sum(value == 5 for value in counts.values()) == 4, "five-appearance count mismatch")
    result = {
        "schema": "three-stage-spinup-iter004-splits-v1", "seed": SPLIT_SEED,
        "development_count": 819, "train_count": 655, "validation_count": 164,
        "splits": splits, "validation_appearance_counts": counts,
    }
    result["split_design_sha256"] = split_design_sha256(result)
    return result


def _metrics(truth: np.ndarray, prediction: np.ndarray) -> Dict[str, float | int]:
    observed = np.asarray(truth, dtype=np.float64)
    predicted = np.asarray(prediction, dtype=np.float64)
    require(observed.shape == predicted.shape and observed.size >= 2, "metric shape mismatch")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(predicted)), "nonfinite metric input")
    residual = predicted - observed
    return {
        "n": int(observed.size), "r2": float(r2_score(observed, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(observed, predicted))),
        "mae": float(mean_absolute_error(observed, predicted)), "bias": float(np.mean(residual)),
        "residual_std": float(np.std(residual, ddof=0)),
    }


def _write_metric_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    fields = list(rows[0])
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _source_preprocessing(snapshot: ThreeStageSnapshot, site: str) -> Tuple[Path, str]:
    source_path = snapshot.root / "manifests" / "sources" / f"{site}_v1.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))["sources"]["spinup_preprocessing"]
    path = Path(source["path"])
    require(path.is_file(), f"missing {site} preprocessing source")
    require(path.stat().st_size == int(source["size_bytes"]), f"{site} preprocessing size mismatch")
    require(sha256_file(path) == str(source["sha256"]), f"{site} preprocessing hash mismatch")
    return path, str(source["sha256"])


def _depth_log_errors(
    snapshot: ThreeStageSnapshot, loaded: LoadedRows
) -> Tuple[Dict[str, Dict[str, np.ndarray]], Dict[str, str]]:
    """Read the validated preprocessing source for the optional same-member diagnostic."""
    result: Dict[str, Dict[str, np.ndarray]] = {}
    hashes: Dict[str, str] = {}
    for site in SITES:
        path, identity = _source_preprocessing(snapshot, site)
        hashes[site] = identity
        with Dataset(str(path), "r") as dataset:
            require("member" in dataset.variables, f"{site} preprocessing member coordinate missing")
            member_variable = dataset.variables["member"]
            require(member_variable.dimensions == ("member",), f"{site} member coordinate dimensions mismatch")
            require(len(dataset.dimensions["member"]) == 1024, f"{site} preprocessing member dimension mismatch")
            selected_indices = np.asarray([int(member[1:]) - 1 for member in snapshot.development_ranked], dtype=np.int64)
            selected_coordinate = np.asarray(member_variable[selected_indices], dtype=np.int64)
            require(
                np.array_equal(selected_coordinate, selected_indices + 1),
                f"{site} preprocessing member identity mismatch",
            )
            by_target: Dict[str, np.ndarray] = {}
            for target, depth_name in (("TOTSOMC", "TOTSOMC_NEONDEPTH"), ("TOTSOMN", "TOTSOMN_NEONDEPTH")):
                require(target in dataset.variables and depth_name in dataset.variables, f"{site} depth variables missing")
                require(dataset.variables[target].dimensions == ("member",), f"{site} {target} dimensions mismatch")
                require(dataset.variables[depth_name].dimensions == ("member",), f"{site} {depth_name} dimensions mismatch")
                total = np.asarray(dataset.variables[target][selected_indices], dtype=np.float64).reshape(-1)
                depth = np.asarray(dataset.variables[depth_name][selected_indices], dtype=np.float64).reshape(-1)
                require(total.size == depth.size == 819, f"{site} selected depth variable size mismatch")
                require(np.all(np.isfinite(total)) and np.all(total > 0.0), f"{site} total invalid")
                require(np.all(np.isfinite(depth)) and np.all(depth > 0.0), f"{site} depth total invalid")
                loaded_mask = loaded.site == site
                target_index = TARGETS.index(target)
                require(
                    np.asarray(loaded.member_id[loaded_mask], dtype=str).tolist() == list(snapshot.development_ranked),
                    f"{site} immutable snapshot member order mismatch",
                )
                require(
                    np.allclose(total, loaded.y[loaded_mask, target_index], rtol=1e-12, atol=1e-10),
                    f"{site} {target} preprocessing/snapshot target mismatch",
                )
                by_target[target] = np.log(depth) - np.log(total)
            result[site] = by_target
    return result, hashes


def run_robustness(snapshot: ThreeStageSnapshot, split_manifest: Mapping[str, Any], output: Path) -> Dict[str, Any]:
    require(split_manifest.get("schema") == "three-stage-spinup-iter004-splits-v1", "split schema mismatch")
    require(int(split_manifest.get("seed", -1)) == SPLIT_SEED, "split seed mismatch")
    require(dict(split_manifest.get("validation_appearance_counts", {})) == {
        member: int(split_manifest["validation_appearance_counts"][member]) for member in snapshot.development_ranked
    }, "split population/order mismatch")
    loaded = snapshot.load_rows(snapshot.development_ranked, include_targets=True)
    require(loaded.y is not None, "robustness targets missing")
    depth_errors, depth_hashes = _depth_log_errors(snapshot, loaded)
    development_position = {
        member: index for index, member in enumerate(snapshot.development_ranked)
    }
    require(
        len(development_position) == 819
        and set(development_position) == snapshot.development_set,
        "development-position map mismatch",
    )
    output.mkdir(parents=True, exist_ok=False)
    evidence_path = output / "paired_robustness_evidence.nc"
    split_rows: List[Dict[str, Any]] = []
    convergence: List[Dict[str, Any]] = []
    observations: List[Dict[str, Any]] = []
    depth_rows: List[Dict[str, Any]] = []
    for split in split_manifest["splits"]:
        split_id = int(split["split_id"])
        train = subset_rows(loaded, split["train_member_ids"])
        validation = subset_rows(loaded, split["validation_member_ids"])
        fitted = fit_compact_models(train, MODEL_CONFIG)
        prediction = predict_compact_models(fitted, validation.X)
        require(np.all(np.isfinite(prediction)) and np.all(prediction > 0.0), "invalid robustness prediction")
        for target in TARGETS:
            convergence.append({"split_id": split_id, "target": target, **fitted["convergence"][target]})
        for site_index, site in enumerate(SITES):
            mask = validation.site == site
            for target_index, target in enumerate(TARGETS):
                truth = validation.y[mask, target_index]
                predicted = prediction[mask, target_index]
                for scale, observed, modeled in (
                    ("physical", truth, predicted), ("log", np.log(truth), np.log(predicted))
                ):
                    split_rows.append({
                        "record_type": "repetition", "split_id": split_id, "site": site,
                        "target": target, "scale": scale, **_metrics(observed, modeled),
                        **{f"q{str(q).replace('.', '_')}": float(np.quantile(modeled - observed, q)) for q in QUANTILES},
                    })
                selected_members = [str(value) for value in validation.member_id[mask]]
                require(
                    all(member in development_position for member in selected_members),
                    "diagnostic member is outside development-position map",
                )
                member_positions = np.asarray(
                    [development_position[member] for member in selected_members], dtype=np.int64
                )
                surrogate_error = np.log(predicted) - np.log(truth)
                depth_error = depth_errors[site][target][member_positions]
                depth_rows.append({
                    "split_id": split_id, "site": site, "target": target, "n": int(surrogate_error.size),
                    "pearson_correlation": float(np.corrcoef(surrogate_error, depth_error)[0, 1]),
                    "surrogate_log_error_mean": float(np.mean(surrogate_error)),
                    "depth_log_error_mean": float(np.mean(depth_error)),
                    "depth_error_definition": "log(NEON-depth ELM stock) minus log(full-profile ELM stock)",
                })
        for row_index in range(validation.X.shape[0]):
            observations.append({
                "split_id": split_id, "site": str(validation.site[row_index]),
                "member_id": str(validation.member_id[row_index]),
                "truth": validation.y[row_index].copy(), "prediction": prediction[row_index].copy(),
            })
    require(len(observations) == SPLIT_COUNT * len(SITES) * 164, "observation coverage mismatch")
    require(len(split_rows) == SPLIT_COUNT * len(SITES) * len(TARGETS) * 2, "metric coverage mismatch")
    for site in SITES:
        for target_index, target in enumerate(TARGETS):
            selected = [row for row in observations if row["site"] == site]
            truth = np.asarray([row["truth"][target_index] for row in selected])
            prediction = np.asarray([row["prediction"][target_index] for row in selected])
            for scale, observed, modeled in (
                ("physical", truth, prediction), ("log", np.log(truth), np.log(prediction))
            ):
                split_rows.append({
                    "record_type": "cross_repetition", "split_id": -1, "site": site,
                    "target": target, "scale": scale, **_metrics(observed, modeled),
                    **{f"q{str(q).replace('.', '_')}": float(np.quantile(modeled - observed, q)) for q in QUANTILES},
                })
    with Dataset(str(evidence_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-spinup-iter004-robustness-v1"
        dataset.snapshot_sha256 = snapshot.snapshot_sha256
        require(split_manifest["split_design_sha256"] == split_design_sha256(split_manifest), "split design identity mismatch")
        dataset.split_design_sha256 = split_manifest["split_design_sha256"]
        dataset.model_config_sha256 = canonical_hash(MODEL_CONFIG)
        dataset.residual_convention = "prediction minus ELM"
        dataset.target_transform = "natural_log"
        dataset.ABBY_spinup_preprocessing_sha256 = depth_hashes["ABBY"]
        dataset.JERC_spinup_preprocessing_sha256 = depth_hashes["JERC"]
        dataset.target_definitions = json.dumps({
            target: "soil1-soil4 full-profile integral over 10 active decomposition layers" for target in TARGETS
        }, sort_keys=True)
        dataset.createDimension("observation", len(observations))
        split_var = dataset.createVariable("split_id", "i2", ("observation",))
        site_var = dataset.createVariable("site", str, ("observation",))
        member_var = dataset.createVariable("member_id", str, ("observation",))
        split_var[:] = [row["split_id"] for row in observations]
        site_var[:] = np.asarray([row["site"] for row in observations], dtype=object)
        member_var[:] = np.asarray([row["member_id"] for row in observations], dtype=object)
        for target_index, target in enumerate(TARGETS):
            truth = np.asarray([row["truth"][target_index] for row in observations])
            prediction = np.asarray([row["prediction"][target_index] for row in observations])
            for suffix, values, units in (
                ("elm", truth, PHYSICAL_UNITS[target]), ("predicted", prediction, PHYSICAL_UNITS[target]),
                ("residual", prediction - truth, PHYSICAL_UNITS[target]), ("log_elm", np.log(truth), "1"),
                ("log_predicted", np.log(prediction), "1"),
                ("log_residual", np.log(prediction) - np.log(truth), "1"),
            ):
                variable = dataset.createVariable(f"{target}_{suffix}", "f8", ("observation",), zlib=True, complevel=4)
                variable[:] = values
                variable.units = units
                variable.target_definition = "soil1-soil4 full-profile integral over 10 active decomposition layers"
                variable.residual_convention = "prediction minus ELM" if "residual" in suffix else "not applicable"
    _write_metric_csv(output / "metric_distribution.csv", split_rows)
    _write_metric_csv(output / "depth_error_dependence.csv", depth_rows)
    write_json(output / "convergence.json", convergence)
    report = {
        "schema": "three-stage-spinup-iter004-robustness-report-v1", "result": "pass",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "split_design_sha256": split_manifest["split_design_sha256"], "model_config": MODEL_CONFIG,
        "model_config_sha256": canonical_hash(MODEL_CONFIG), "observation_count": len(observations),
        "metric_row_count": len(split_rows), "depth_diagnostic_row_count": len(depth_rows),
        "preprocessing_sha256": depth_hashes,
        "convergence_warning_count": sum(bool(item["has_convergence_warning"]) for item in convergence),
        "files": package_files(output, exclude={"robustness_report.json"}),
    }
    write_json(output / "robustness_report.json", report)
    return report


def _weighted_moments(values: np.ndarray, weights: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    normalized = np.asarray(weights, dtype=np.float64) / float(np.sum(weights))
    mean = np.sum(values * normalized[:, None], axis=0)
    centered = values - mean
    covariance = (centered * normalized[:, None]).T @ centered
    return mean, covariance


def aggregate_uncertainty(evidence_path: Path, split_manifest: Mapping[str, Any], output: Path) -> Dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    with Dataset(str(evidence_path), "r") as source:
        require(source.getncattr("schema") == "three-stage-spinup-iter004-robustness-v1", "evidence schema mismatch")
        sites = np.asarray(source.variables["site"][:], dtype=str)
        members = np.asarray(source.variables["member_id"][:], dtype=str)
        split_ids = np.asarray(source.variables["split_id"][:], dtype=np.int16)
        errors = np.column_stack([
            np.asarray(source.variables["TOTSOMC_log_residual"][:], dtype=np.float64),
            np.asarray(source.variables["TOTSOMN_log_residual"][:], dtype=np.float64),
        ])
        snapshot_sha256 = str(source.getncattr("snapshot_sha256"))
        split_sha256 = str(source.getncattr("split_design_sha256"))
    require(split_sha256 == split_manifest["split_design_sha256"], "evidence/split hash mismatch")
    require(split_sha256 == split_design_sha256(split_manifest), "split design identity invalid")
    counts = {str(key): int(value) for key, value in split_manifest["validation_appearance_counts"].items()}
    summary: Dict[str, Any] = {}
    per_rep: Dict[str, Dict[str, List[Any]]] = {}
    for site in SITES:
        mask = sites == site
        selected_errors = errors[mask]
        selected_members = members[mask]
        weights = np.asarray([1.0 / counts[member] for member in selected_members])
        bias, covariance = _weighted_moments(selected_errors, weights)
        require(np.all(np.isfinite(bias)) and np.all(np.isfinite(covariance)), "nonfinite uncertainty summary")
        require(np.allclose(covariance, covariance.T, rtol=0.0, atol=1e-12), "covariance asymmetric")
        eigenvalues = np.linalg.eigvalsh(covariance)
        require(float(np.min(eigenvalues)) >= -1e-12, "covariance not positive semidefinite")
        standard = np.sqrt(np.diag(covariance))
        correlation = covariance / np.outer(standard, standard)
        summary[site] = {
            "bias": bias.tolist(), "covariance": covariance.tolist(), "correlation": correlation.tolist(),
            "eigenvalues": eigenvalues.tolist(), "normalized_weight_sum": 1.0,
            "effective_member_count": 819, "occurrence_count": int(mask.sum()),
        }
        per_rep[site] = {"bias": [], "covariance": [], "correlation": []}
        for split_id in range(SPLIT_COUNT):
            rep_values = errors[mask & (split_ids == split_id)]
            rep_bias = np.mean(rep_values, axis=0)
            rep_covariance = np.cov(rep_values, rowvar=False, ddof=0)
            rep_standard = np.sqrt(np.diag(rep_covariance))
            per_rep[site]["bias"].append(rep_bias.tolist())
            per_rep[site]["covariance"].append(rep_covariance.tolist())
            per_rep[site]["correlation"].append((rep_covariance / np.outer(rep_standard, rep_standard)).tolist())
    nc_path = output / "surrogate_uncertainty.nc"
    with Dataset(str(nc_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-spinup-surrogate-uncertainty-v1"
        dataset.snapshot_sha256 = snapshot_sha256
        dataset.split_design_sha256 = split_sha256
        dataset.residual_convention = "prediction minus ELM in natural-log space"
        dataset.pooling = "member-balanced: occurrence weight 1/k, normalized over 819 members, ddof=0"
        dataset.scope = "surrogate component only; excludes observation, depth, and total likelihood uncertainty"
        dataset.target_definitions = json.dumps({
            target: "soil1-soil4 full-profile integral over 10 active decomposition layers" for target in TARGETS
        }, sort_keys=True)
        dataset.createDimension("site", len(SITES))
        dataset.createDimension("repetition", SPLIT_COUNT)
        site_var = dataset.createVariable("site", str, ("site",))
        site_var[:] = np.asarray(SITES, dtype=object)
        for target_index, target in enumerate(TARGETS):
            bias_var = dataset.createVariable(f"{target}_log_error_bias", "f8", ("site",))
            variance_var = dataset.createVariable(f"{target}_log_error_variance", "f8", ("site",))
            rep_bias_var = dataset.createVariable(f"{target}_per_repetition_log_error_bias", "f8", ("site", "repetition"))
            rep_variance_var = dataset.createVariable(f"{target}_per_repetition_log_error_variance", "f8", ("site", "repetition"))
            bias_var[:] = [summary[site]["bias"][target_index] for site in SITES]
            variance_var[:] = [summary[site]["covariance"][target_index][target_index] for site in SITES]
            rep_bias_var[:] = [[per_rep[site]["bias"][rep][target_index] for rep in range(SPLIT_COUNT)] for site in SITES]
            rep_variance_var[:] = [[per_rep[site]["covariance"][rep][target_index][target_index] for rep in range(SPLIT_COUNT)] for site in SITES]
            for variable in (bias_var, variance_var, rep_bias_var, rep_variance_var):
                variable.units = "1"
                variable.target_definition = "soil1-soil4 full-profile integral over 10 active decomposition layers"
        covariance_var = dataset.createVariable("TOTSOMC_TOTSOMN_log_error_covariance", "f8", ("site",))
        correlation_var = dataset.createVariable("TOTSOMC_TOTSOMN_log_error_correlation", "f8", ("site",))
        rep_covariance_var = dataset.createVariable("TOTSOMC_TOTSOMN_per_repetition_log_error_covariance", "f8", ("site", "repetition"))
        rep_correlation_var = dataset.createVariable("TOTSOMC_TOTSOMN_per_repetition_log_error_correlation", "f8", ("site", "repetition"))
        covariance_var[:] = [summary[site]["covariance"][0][1] for site in SITES]
        correlation_var[:] = [summary[site]["correlation"][0][1] for site in SITES]
        rep_covariance_var[:] = [[per_rep[site]["covariance"][rep][0][1] for rep in range(SPLIT_COUNT)] for site in SITES]
        rep_correlation_var[:] = [[per_rep[site]["correlation"][rep][0][1] for rep in range(SPLIT_COUNT)] for site in SITES]
        covariance_var.units = rep_covariance_var.units = "1"
        correlation_var.units = rep_correlation_var.units = "1"
    report = {
        "schema": "three-stage-spinup-surrogate-uncertainty-report-v1", "result": "pass",
        "snapshot_sha256": snapshot_sha256, "split_design_sha256": split_sha256,
        "member_balance_rule": "each occurrence weight 1/k; normalized; population ddof=0",
        "sites": summary, "files": package_files(output, exclude={"uncertainty_report.json"}),
    }
    write_json(output / "uncertainty_report.json", report)
    return report


def validate_release_artifact(artifact: Mapping[str, Any]) -> None:
    require(artifact.get("schema") == RELEASE_SCHEMA, "release artifact schema mismatch")
    require(artifact.get("artifact_role") == "published_spinup_inference", "artifact role mismatch")
    require(list(artifact.get("target_order", [])) == list(TARGETS), "target order mismatch")
    require(artifact.get("target_transform") == "natural_log", "target transform mismatch")
    require(dict(artifact.get("model_config", {})) == MODEL_CONFIG, "frozen model configuration mismatch")
    require(list(artifact.get("sites", [])) == list(SITES), "site order mismatch")
    features = list(artifact.get("feature_names", []))
    require(len(features) == 25 and schema_sha256(features) == artifact.get("feature_schema_sha256"), "feature schema mismatch")
    for name in ("models", "x_scalers", "y_scalers"):
        require(list(artifact.get(name, {})) == list(TARGETS), f"{name} target mapping mismatch")
    fit_scope = artifact.get("fit_scope", {})
    members = list(fit_scope.get("development_member_ids", []))
    require(len(members) == len(set(members)) == 819, "release fit member scope mismatch")
    require(int(fit_scope.get("training_rows", -1)) == 1638, "release fit row count mismatch")
    require(fit_scope.get("fixed_test_access") is False, "fixed-test access mismatch")
    require(len(str(artifact.get("snapshot_sha256", ""))) == 64, "snapshot identity missing")


def predict_release(artifact: Mapping[str, Any], X: np.ndarray) -> np.ndarray:
    validate_release_artifact(artifact)
    matrix = np.asarray(X, dtype=np.float64)
    require(matrix.ndim == 2 and matrix.shape[1] == 25 and matrix.shape[0] >= 1, "prediction matrix shape mismatch")
    require(np.all(np.isfinite(matrix)), "prediction matrix contains nonfinite values")
    result = []
    for target in TARGETS:
        scaled = artifact["x_scalers"][target].transform(matrix)
        scaled_prediction = artifact["models"][target].predict(scaled)
        log_prediction = artifact["y_scalers"][target].inverse_transform(np.asarray(scaled_prediction).reshape(-1, 1)).ravel()
        prediction = np.exp(log_prediction)
        require(np.all(np.isfinite(prediction)) and np.all(prediction > 0.0), f"{target} prediction invalid")
        result.append(prediction)
    return np.column_stack(result)


def load_release_artifact(directory: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    manifest = json.loads((directory / "artifact_manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("schema") == ARTIFACT_MANIFEST_SCHEMA, "artifact manifest schema mismatch")
    artifact_path = directory / str(manifest["artifact_filename"])
    require(artifact_path.stat().st_size == int(manifest["artifact_size_bytes"]), "artifact size mismatch")
    require(sha256_file(artifact_path) == manifest["artifact_sha256"], "artifact hash mismatch")
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    require(isinstance(artifact, dict), "release pickle is not a dictionary")
    validate_release_artifact(artifact)
    return artifact, manifest


def fit_release(snapshot: ThreeStageSnapshot, staging: Path, source_identity: Mapping[str, Any]) -> Dict[str, Any]:
    artifact_directory = staging / "artifact"
    handoff_directory = staging / "handoff"
    require(not staging.exists(), "attempt-local release package already exists")
    artifact_directory.mkdir(parents=True)
    handoff_directory.mkdir(parents=True)
    (staging / "uncertainty").mkdir()
    (staging / "validation").mkdir()
    loaded = snapshot.load_rows(snapshot.development_ranked, include_targets=True)
    fitted = fit_compact_models(loaded, MODEL_CONFIG)
    artifact: Dict[str, Any] = {
        "schema": RELEASE_SCHEMA, "artifact_role": "published_spinup_inference",
        "created_utc": datetime.now(timezone.utc).isoformat(), "target_order": list(TARGETS),
        "target_transform": "natural_log", "target_metadata": {
            target: {"units": PHYSICAL_UNITS[target], "definition": "soil1-soil4 full-profile integral over 10 active decomposition layers"}
            for target in TARGETS
        },
        "models": fitted["models"], "x_scalers": fitted["x_scalers"], "y_scalers": fitted["y_scalers"],
        "model_config": MODEL_CONFIG, "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": schema_sha256(snapshot.feature_names),
        "parameter_metadata": snapshot.parameter_metadata, "sites": list(SITES),
        "site_identity_is_feature": False,
        "fit_scope": {"kind": "all_development", "development_member_ids": list(snapshot.development_ranked),
                      "training_rows": int(loaded.X.shape[0]), "fixed_test_access": False},
        "snapshot_revision": "r0001", "snapshot_sha256": snapshot.snapshot_sha256,
        "source_identity": dict(source_identity), "convergence": fitted["convergence"],
    }
    validate_release_artifact(artifact)
    artifact_path = artifact_directory / "spinup_release_artifact.pkl"
    with artifact_path.open("xb") as handle:
        pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
    manifest = {
        "schema": ARTIFACT_MANIFEST_SCHEMA, "artifact_filename": artifact_path.name,
        "artifact_sha256": sha256_file(artifact_path), "artifact_size_bytes": artifact_path.stat().st_size,
        "artifact_schema": RELEASE_SCHEMA, "snapshot_sha256": snapshot.snapshot_sha256,
        "feature_schema_sha256": artifact["feature_schema_sha256"], "model_config": MODEL_CONFIG,
        "model_config_sha256": canonical_hash(MODEL_CONFIG), "fit_scope": artifact["fit_scope"],
    }
    write_json(artifact_directory / "artifact_manifest.json", manifest)
    prediction = predict_release(artifact, loaded.X).reshape(len(SITES), 819, len(TARGETS))
    handoff_path = handoff_directory / "spinup_predicted_cn.nc"
    with Dataset(str(handoff_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.schema = "three-stage-spinup-predicted-cn-handoff-v1"
        dataset.artifact_sha256 = manifest["artifact_sha256"]
        dataset.snapshot_sha256 = snapshot.snapshot_sha256
        dataset.fit_scope = "all 819 development members; predictions are in-sample"
        dataset.target_transform = "natural_log fit; physical positive output; no clipping"
        dataset.createDimension("site", len(SITES))
        dataset.createDimension("member", 819)
        site_var = dataset.createVariable("site", str, ("site",))
        member_var = dataset.createVariable("member_id", str, ("member",))
        site_var[:] = np.asarray(SITES, dtype=object)
        member_var[:] = np.asarray(snapshot.development_ranked, dtype=object)
        for target_index, target in enumerate(TARGETS):
            variable = dataset.createVariable(f"{target}_predicted", "f8", ("site", "member"), zlib=True, complevel=4)
            variable[:] = prediction[:, :, target_index]
            variable.units = PHYSICAL_UNITS[target]
            variable.definition = artifact["target_metadata"][target]["definition"]
    handoff_manifest = {
        "schema": "three-stage-spinup-predicted-cn-handoff-manifest-v1",
        "filename": handoff_path.name, "sha256": sha256_file(handoff_path),
        "size_bytes": handoff_path.stat().st_size, "artifact_sha256": manifest["artifact_sha256"],
        "snapshot_sha256": snapshot.snapshot_sha256, "site_order": list(SITES),
        "development_member_ids": list(snapshot.development_ranked),
        "variables": [f"{target}_predicted" for target in TARGETS],
        "contains_elm_truth": False, "contains_features_or_parameters": False,
    }
    write_json(handoff_directory / "handoff_manifest.json", handoff_manifest)
    report = {
        "schema": "three-stage-spinup-iter004-release-fit-report-v1", "result": "pass",
        "artifact_sha256": manifest["artifact_sha256"], "handoff_sha256": handoff_manifest["sha256"],
        "snapshot_sha256": snapshot.snapshot_sha256, "fit_scope": artifact["fit_scope"],
        "convergence": fitted["convergence"],
    }
    write_json(staging / "release_fit_report.json", report)
    return report


def copy_uncertainty_to_staging(uncertainty_directory: Path, staging: Path) -> None:
    target = staging / "uncertainty"
    require(target.is_dir() and not any(target.iterdir()), "uncertainty staging is not empty")
    for path in sorted(item for item in uncertainty_directory.iterdir() if item.is_file()):
        shutil.copy2(path, target / path.name)
