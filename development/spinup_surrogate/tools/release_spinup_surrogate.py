#!/usr/bin/env python
"""Build one locked Iter012 full-data spinup-surrogate release artifact."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
from netCDF4 import Dataset
from sklearn import preprocessing

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401 - register ELMcase for trusted case pickles
from model_ELM.spinup_surrogate_artifact import (  # noqa: E402
    predict_versioned_spinup,
    validate_versioned_artifact,
)
from model_ELM.surrogate_NN_Forcing import SPINUP_VAR_SUM, _restart_file  # noqa: E402
from model_ELM.surrogate_NN_Spinup import (  # noqa: E402
    _build_design_matrix,
    _build_split_indices,
    _compute_overfitting_diagnostics,
    _normalize_fixed_mlp_params,
    _prepare_case_spinup_block,
    _rmse,
    _safe_r2,
    _validate_spinup_blocks,
    _build_spinup_estimator_and_grid,
)

SCHEMA_VERSION = "spinup-surrogate-v1"
RELEASE_VERSION = "iter012-v1"
TARGET_ORDER = ["TOTSOMC", "TOTSOMN"]
SURFACE_VARS = ["PCT_SAND", "PCT_CLAY", "ORGANIC"]
FORCING_VARS = ["PRECTmms", "FSDS", "TBOT", "RH"]
FIXED_MLP = {
    "hidden_layer_sizes": (32,),
    "activation": "tanh",
    "solver": "lbfgs",
    "alpha": 40.0,
    "learning_rate_init": 1.0e-3,
}
METRIC_KEYS = ["r2_train", "r2_val", "rmse_train", "rmse_val", "r2_gap", "rmse_ratio"]
RTOL = 1.0e-10
ATOL = 1.0e-8
TARGET_METADATA_DIAGNOSTIC = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
    "spinup_surrogate_iter012_metadata_diagnostic/target_metadata_diagnostic.json"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True, choices=["drop32", "drop21_corr080"])
    parser.add_argument("--case-list", required=True)
    parser.add_argument("--spinup-case-list", required=True)
    parser.add_argument("--feature-subset", required=True)
    parser.add_argument("--reference-stats", required=True)
    parser.add_argument("--output-artifact", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--submission-config", required=True)
    parser.add_argument("--n-jobs", required=True, type=int)
    parser.add_argument("--pre-dispatch", required=True)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(blob).hexdigest()


def _load_cases(names: Sequence[str]) -> List[Any]:
    cases = []
    for name in names:
        path = REPO_ROOT / "pklfiles" / f"{name}.pkl"
        if not path.is_file():
            raise FileNotFoundError(f"Missing case pickle: {path}")
        with path.open("rb") as fp:
            cases.append(pickle.load(fp))
    return cases


def _physical_parameter_metadata(case: Any) -> Dict[str, Any]:
    names = [str(v) for v in list(case.ensemble_parms)]
    n_params = int(case.nparms_ensemble)
    if len(names) != n_params or len(set(names)) != n_params:
        raise ValueError(
            f"ABBY physical parameter names invalid: count={len(names)}, n_params={n_params}"
        )
    pmin = np.asarray(case.ensemble_pmin, dtype=np.float64).reshape(-1)
    pmax = np.asarray(case.ensemble_pmax, dtype=np.float64).reshape(-1)
    if pmin.size != n_params or pmax.size != n_params:
        raise ValueError("ABBY ensemble_pmin/pmax lengths do not match nparms_ensemble")
    if np.any(~np.isfinite(pmin)) or np.any(~np.isfinite(pmax)) or np.any(pmin > pmax):
        raise ValueError("ABBY parameter bounds are non-finite or inverted")
    aliases = [f"parm_{i}" for i in range(n_params)]
    return {
        "physical_names": names,
        "aliases": aliases,
        "alias_to_physical": dict(zip(aliases, names)),
        "physical_to_alias": dict(zip(names, aliases)),
        "ensemble_pmin": pmin.tolist(),
        "ensemble_pmax": pmax.tolist(),
        "reference_case": str(case.casename),
    }


def _audit_target_metadata(cases: Sequence[Any]) -> Dict[str, Any]:
    diagnostic = json.loads(TARGET_METADATA_DIAGNOSTIC.read_text(encoding="utf-8"))
    if diagnostic.get("diagnostic") != "iter012-target-metadata-no-fitting":
        raise ValueError("Unexpected target-metadata diagnostic identity")
    if diagnostic.get("training_or_fitting_performed") is not False:
        raise ValueError("Target-metadata evidence must be from the no-fitting diagnostic")
    diagnostic_cases = diagnostic.get("case_records", [])
    expected_case_names = [str(case.casename) for case in cases]
    if [record.get("case") for record in diagnostic_cases] != expected_case_names:
        raise ValueError("Target-metadata diagnostic case identity/order mismatch")
    mapping_source = diagnostic.get("mapping_source", {})
    mapping_path = REPO_ROOT / "model_ELM/surrogate_NN_Forcing.py"
    if (
        mapping_source.get("path") != str(mapping_path)
        or mapping_source.get("sha256") != _sha256(mapping_path)
        or mapping_source.get("target_components") != {
            target: list(SPINUP_VAR_SUM[target]) for target in TARGET_ORDER
        }
    ):
        raise ValueError("Target-metadata diagnostic component mapping provenance mismatch")
    diagnostic_by_case = {record["case"]: record for record in diagnostic_cases}

    audit: Dict[str, Any] = {}
    for target in TARGET_ORDER:
        components = list(SPINUP_VAR_SUM.get(target, [target]))
        records = []
        target_units = set()
        target_long_names = set()
        history_records = []
        for case in cases:
            diagnostic_case = diagnostic_by_case[str(case.casename)]
            restart = _restart_file(case, 1)
            if not restart.is_file():
                raise FileNotFoundError(f"Missing restart for target audit: {restart}")
            diagnostic_restart = diagnostic_case.get("restart", {})
            if (
                diagnostic_restart.get("path") != str(restart)
                or diagnostic_restart.get("sha256") != _sha256(restart)
            ):
                raise ValueError(
                    f"Live restart does not match locked diagnostic evidence: {restart}"
                )
            with Dataset(str(restart), "r") as nc:
                restart_version = str(getattr(nc, "version", "")).strip()
                restart_source = str(getattr(nc, "source", "")).strip()
                if not restart_version or restart_source != "E3SM Land Model":
                    raise ValueError(
                        f"Unexpected restart source/version for target audit: {restart}"
                    )
                for component in components:
                    if component not in nc.variables:
                        raise KeyError(f"Missing target component {component} in {restart}")
                    var = nc.variables[component]
                    units = str(getattr(var, "units", "")).strip()
                    long_name = str(getattr(var, "long_name", "")).strip()
                    if "units" not in var.ncattrs() or "long_name" not in var.ncattrs():
                        raise ValueError(
                            f"Target component {component} lacks units/long_name attributes in "
                            f"{restart}"
                        )
                    values = np.asarray(
                        np.ma.asarray(var[:]).filled(np.nan), dtype=np.float64
                    )
                    if np.any(~np.isfinite(values)):
                        raise ValueError(f"Target component {component} is non-finite in {restart}")
                    diagnostic_component = diagnostic_restart["targets"][target][component]
                    if (
                        diagnostic_component.get("dimensions") != list(var.dimensions)
                        or diagnostic_component.get("shape") != list(values.shape)
                        or diagnostic_component.get("attributes", {}).get("units") != units
                        or diagnostic_component.get("attributes", {}).get("long_name")
                        != long_name
                        or diagnostic_component.get("numpy_nansum")
                        != float(np.nansum(values))
                    ):
                        raise ValueError(
                            f"Live component metadata/value differs from locked evidence: "
                            f"{restart}:{component}"
                        )
                    records.append(
                        {
                            "case": str(case.casename),
                            "restart": str(restart),
                            "component": component,
                            "units": units,
                            "long_name": long_name,
                            "dimensions": list(var.dimensions),
                            "shape": list(values.shape),
                            "numpy_nansum": float(np.nansum(values)),
                            "aggregation": "numpy.nansum over every stored element",
                        }
                    )

            history_candidates = sorted(restart.parent.glob("*.elm.h*.nc"))
            if len(history_candidates) < 3:
                raise ValueError(
                    f"Need at least three colocated ELM history files for {restart}"
                )
            diagnostic_history = diagnostic_case.get("history_evidence", {})
            selected_history = history_candidates[:3]
            if (
                diagnostic_history.get("candidate_count") != len(history_candidates)
                or diagnostic_history.get("omitted_count")
                != len(history_candidates) - len(selected_history)
                or diagnostic_history.get("searched")
                != [str(path) for path in selected_history]
            ):
                raise ValueError(
                    f"Live history selection differs from locked evidence for {restart}"
                )
            diagnostic_history_by_path = {
                record["path"]: record
                for record in diagnostic_history.get("matches", [])
            }
            if set(diagnostic_history_by_path) != {
                str(path) for path in selected_history
            }:
                raise ValueError(
                    f"Locked history-match set is incomplete for {restart}"
                )
            for history_path in selected_history:
                locked_history = diagnostic_history_by_path[str(history_path)]
                if locked_history.get("sha256") != _sha256(history_path):
                    raise ValueError(
                        f"Live history file differs from locked evidence: {history_path}"
                    )
                with Dataset(str(history_path), "r") as history:
                    history_version = str(
                        getattr(history, "git_version", getattr(history, "source_id", ""))
                    ).strip()
                    if (
                        str(getattr(history, "source", "")).strip() != "E3SM Land Model"
                        or history_version != restart_version
                    ):
                        raise ValueError(
                            f"History/restart model provenance mismatch: {history_path}"
                        )
                    if target not in history.variables:
                        raise KeyError(
                            f"Native history target {target} missing in {history_path}"
                        )
                    history_var = history.variables[target]
                    history_units = str(getattr(history_var, "units", "")).strip()
                    history_long_name = str(
                        getattr(history_var, "long_name", "")
                    ).strip()
                    if not history_units or not history_long_name:
                        raise ValueError(
                            f"Native history target {target} lacks units/long_name in "
                            f"{history_path}"
                        )
                    if tuple(history_var.dimensions) != ("time", "lndgrid"):
                        raise ValueError(
                            f"Unexpected native history dimensions for {target}: "
                            f"{history_var.dimensions}"
                        )
                    history_values = np.asarray(
                        np.ma.asarray(history_var[:]).filled(np.nan), dtype=np.float64
                    )
                    if np.any(~np.isfinite(history_values)):
                        raise ValueError(
                            f"Native history target {target} is non-finite in {history_path}"
                        )
                    locked_global = locked_history.get("global_attributes", {})
                    locked_target = locked_history.get("targets", {}).get(target, {})
                    if (
                        locked_global.get("source") != "E3SM Land Model"
                        or locked_global.get("git_version") != history_version
                        or locked_target.get("attributes", {}).get("units")
                        != history_units
                        or locked_target.get("attributes", {}).get("long_name")
                        != history_long_name
                        or locked_target.get("dimensions")
                        != list(history_var.dimensions)
                        or locked_target.get("shape") != list(history_values.shape)
                        or locked_target.get("numpy_nansum")
                        != float(np.nansum(history_values))
                    ):
                        raise ValueError(
                            f"Live history metadata/value differs from locked evidence: "
                            f"{history_path}:{target}"
                        )
                    target_units.add(history_units)
                    target_long_names.add(history_long_name)
                    history_records.append(
                        {
                            "case": str(case.casename),
                            "path": str(history_path),
                            "sha256": _sha256(history_path),
                            "model_source": "E3SM Land Model",
                            "model_version": history_version,
                            "target": target,
                            "units": history_units,
                            "long_name": history_long_name,
                            "dimensions": list(history_var.dimensions),
                            "shape": list(history_values.shape),
                        }
                    )
        if len(target_units) != 1:
            raise ValueError(f"Inconsistent units for {target}: {sorted(target_units)}")
        if len(target_long_names) != 1:
            raise ValueError(
                f"Inconsistent long_name values for {target}: {sorted(target_long_names)}"
            )
        audit[target] = {
            "components": components,
            "units": next(iter(target_units)),
            "long_name": next(iter(target_long_names)),
            "scalar_definition": (
                "sum numpy.nansum(component[:]) across listed components"
                if len(components) > 1
                else "numpy.nansum(component[:])"
            ),
            "unit_definition_provenance": (
                "units and long_name are taken from three colocated native ELM history "
                "diagnostics per case after exact E3SM Land Model version equality with each "
                "restart; restart component units/long_name are recorded verbatim and may be "
                "empty"
            ),
            "diagnostic_evidence": {
                "path": str(TARGET_METADATA_DIAGNOSTIC),
                "sha256": _sha256(TARGET_METADATA_DIAGNOSTIC),
            },
            "records": records,
            "native_history_records": history_records,
        }
    return audit


def _feature_ranges(names: Sequence[str], X: np.ndarray) -> Dict[str, Dict[str, float]]:
    if X.shape[1] != len(names):
        raise ValueError("Feature range name/column mismatch")
    result = {}
    for i, name in enumerate(names):
        col = np.asarray(X[:, i], dtype=np.float64)
        if np.any(~np.isfinite(col)):
            raise ValueError(f"Feature {name} contains non-finite values")
        result[str(name)] = {"min": float(np.min(col)), "max": float(np.max(col))}
    return result


def _fit_model(X: np.ndarray, y: np.ndarray) -> tuple[Any, Any, Any]:
    x_scaler = preprocessing.StandardScaler().fit(X)
    y_scaler = preprocessing.StandardScaler().fit(y.reshape(-1, 1))
    estimator, _ = _build_spinup_estimator_and_grid("nn", False)
    model = estimator.set_params(**_normalize_fixed_mlp_params(FIXED_MLP))
    model.fit(x_scaler.transform(X), y_scaler.transform(y.reshape(-1, 1)).ravel())
    return model, x_scaler, y_scaler


def _reproduction_gate(
    X: np.ndarray,
    blocks: Sequence[Any],
    row_case_ids: np.ndarray,
    row_member_ids: np.ndarray,
    row_site_ids: np.ndarray,
    reference: Mapping[str, Any],
) -> Dict[str, Any]:
    train_idx, val_idx, split_details = _build_split_indices(
        row_case_ids=row_case_ids,
        row_member_ids=row_member_ids,
        row_site_ids=row_site_ids,
        split_mode="by_member",
        train_fraction=0.8,
        split_random_state=10001,
    )
    if split_details != reference["split_details"]:
        raise ValueError("Reproduction split_details do not exactly match Iter011 seed10001")
    observed: Dict[str, Any] = {}
    for target_index, target in enumerate(TARGET_ORDER):
        y = np.concatenate(
            [block.spinup_targets[:, target_index] for block in blocks]
        ).astype(np.float64)
        model, x_scaler, y_scaler = _fit_model(X[train_idx, :], y[train_idx])
        train_pred = y_scaler.inverse_transform(
            model.predict(x_scaler.transform(X[train_idx, :])).reshape(-1, 1)
        ).ravel()
        val_pred = y_scaler.inverse_transform(
            model.predict(x_scaler.transform(X[val_idx, :])).reshape(-1, 1)
        ).ravel()
        train_r2 = _safe_r2(y[train_idx], train_pred)
        val_r2 = _safe_r2(y[val_idx], val_pred)
        train_rmse = _rmse(y[train_idx], train_pred)
        val_rmse = _rmse(y[val_idx], val_pred)
        diagnostics = _compute_overfitting_diagnostics(
            train_r2, val_r2, train_rmse, val_rmse
        )
        values = {
            "r2_train": train_r2,
            "r2_val": val_r2,
            "rmse_train": train_rmse,
            "rmse_val": val_rmse,
            "r2_gap": diagnostics["r2_gap"],
            "rmse_ratio": diagnostics["rmse_ratio"],
        }
        expected = reference["by_variable"][target]
        comparisons = {}
        for key in METRIC_KEYS:
            passed = bool(np.isclose(values[key], expected[key], rtol=RTOL, atol=ATOL))
            comparisons[key] = {
                "observed": float(values[key]),
                "expected": float(expected[key]),
                "passed": passed,
            }
            if not passed:
                raise ValueError(
                    f"Reproduction mismatch {target}.{key}: "
                    f"observed={values[key]!r}, expected={expected[key]!r}"
                )
        observed[target] = comparisons
    return {
        "passed": True,
        "rtol": RTOL,
        "atol": ATOL,
        "split_details_sha256": _json_sha(split_details),
        "metrics": observed,
    }


def _package_versions() -> Dict[str, str]:
    result = {}
    for name in ("numpy", "scikit-learn", "netCDF4", "joblib"):
        result[name] = importlib.metadata.version(name)
    result["python"] = sys.version.split()[0]
    return result


def main() -> int:
    args = _parser().parse_args()
    if args.n_jobs != 4 or args.pre_dispatch != "n_jobs":
        raise ValueError(
            f"Locked worker controls require n_jobs=4/pre_dispatch=n_jobs, "
            f"got {args.n_jobs}/{args.pre_dispatch}"
        )
    case_names = [v.strip() for v in args.case_list.split(",") if v.strip()]
    spinup_case_names = [v.strip() for v in args.spinup_case_list.split(",") if v.strip()]
    selected_names = [v.strip() for v in args.feature_subset.split(",") if v.strip()]
    if len(case_names) != 9 or len(spinup_case_names) != 9:
        raise ValueError("Iter012 requires exactly nine ordered case and spinup-case names")
    cases = _load_cases(case_names)
    spinup_cases = _load_cases(spinup_case_names)
    blocks = [
        _prepare_case_spinup_block(
            case=case,
            spinup_vars=TARGET_ORDER,
            surface_vars=SURFACE_VARS,
            forcing_vars=FORCING_VARS,
            clim_feature_mode="compact",
            spinup_case=spinup_case,
        )
        for case, spinup_case in zip(cases, spinup_cases)
    ]
    _validate_spinup_blocks(blocks)
    if [block.nsamples for block in blocks] != [100] * 9:
        raise ValueError(f"Expected 100 members per case, got {[b.nsamples for b in blocks]}")
    X_all, row_case_ids, row_member_ids, row_site_ids = _build_design_matrix(blocks)
    ref = blocks[0]
    complete_names = (
        [f"parm_{i}" for i in range(ref.params.shape[1])]
        + list(ref.surface_feature_names)
        + list(ref.climatology_feature_names)
    )
    if len(set(selected_names)) != len(selected_names):
        raise ValueError("Frozen feature subset contains duplicates")
    missing = [name for name in selected_names if name not in complete_names]
    if missing:
        raise ValueError(f"Frozen feature subset contains unknown names: {missing}")
    indices = [complete_names.index(name) for name in selected_names]
    expected_count = 32 if args.variant == "drop32" else 21
    if len(indices) != expected_count:
        raise ValueError(
            f"Variant {args.variant} requires {expected_count} features, got {len(indices)}"
        )
    X = X_all[:, indices]
    reference_path = Path(args.reference_stats).resolve()
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    if reference["input_feature_names"] != selected_names:
        raise ValueError("Reference stats feature order does not match locked release order")
    if reference["case_names"] != case_names:
        raise ValueError("Reference stats case order does not match locked release order")
    reproduction = _reproduction_gate(
        X, blocks, row_case_ids, row_member_ids, row_site_ids, reference
    )
    parameter_metadata = _physical_parameter_metadata(cases[0])
    target_metadata = _audit_target_metadata(cases)
    models: Dict[str, Any] = {}
    x_scalers: Dict[str, Any] = {}
    y_scalers: Dict[str, Any] = {}
    full_fit_diagnostics: Dict[str, Any] = {}
    for target_index, target in enumerate(TARGET_ORDER):
        y = np.concatenate(
            [block.spinup_targets[:, target_index] for block in blocks]
        ).astype(np.float64)
        model, x_scaler, y_scaler = _fit_model(X, y)
        pred = y_scaler.inverse_transform(
            model.predict(x_scaler.transform(X)).reshape(-1, 1)
        ).ravel()
        models[target] = model
        x_scalers[target] = x_scaler
        y_scalers[target] = y_scaler
        full_fit_diagnostics[target] = {
            "rows": int(y.size),
            "training_r2": float(_safe_r2(y, pred)),
            "training_rmse": float(_rmse(y, pred)),
            "prediction_sha256": hashlib.sha256(pred.tobytes()).hexdigest(),
            "note": "full-data training diagnostic; not validation evidence",
        }
    source_manifest = Path(args.source_manifest).resolve()
    submission_config = Path(args.submission_config).resolve()
    created = datetime.now(timezone.utc).isoformat()
    training_layout = {
        "input_feature_names": selected_names,
        "input_feature_names_all": complete_names,
        "selected_feature_indices": indices,
        "surface_feature_names": SURFACE_VARS,
        "climatology_feature_names": list(ref.climatology_feature_names),
        "spinup_vars": TARGET_ORDER,
        "model_type": "nn",
        "fixed_mlp_params": {
            **FIXED_MLP,
            "hidden_layer_sizes": list(FIXED_MLP["hidden_layer_sizes"]),
            "max_iter": 800,
            "random_state": 42,
        },
        "feature_set": "all",
        "explicit_feature_subset": selected_names,
        "feature_subset_policy": "strict",
        "apply_variance_filter": False,
        "apply_corr_filter": False,
        "forcing_vars_for_climatology": FORCING_VARS,
        "clim_feature_mode": "compact",
        "n_params": int(ref.params.shape[1]),
        "n_surface": int(ref.surface.shape[1]),
        "n_climatology": int(ref.climatology.shape[1]),
        "case_names": case_names,
        "spinup_case_names": spinup_case_names,
        "nsamples_per_case": {str(b.case_name): int(b.nsamples) for b in blocks},
    }
    artifact: Dict[str, Any] = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "variant": args.variant,
        "created_utc": created,
        "trusted_source_only": True,
        "environment_version_sensitive": True,
        "target_order": TARGET_ORDER,
        "target_metadata": target_metadata,
        "models": models,
        "x_scaler": x_scalers,
        "y_scaler": y_scalers,
        "training_layout": training_layout,
        "parameter_metadata": parameter_metadata,
        "feature_ranges": {
            "complete": _feature_ranges(complete_names, X_all),
            "selected": _feature_ranges(selected_names, X),
        },
        "fit_scope": {
            "kind": "full_data",
            "rows": int(X.shape[0]),
            "cases": case_names,
            "members_per_case": 100,
            "estimator_seed": 42,
            "validation_evidence_kind": "Iter011 100-seed summaries",
        },
        "validation_evidence": {
            "iter011_reference_stats": str(reference_path),
            "iter011_reference_stats_sha256": _sha256(reference_path),
            "iter011_summary_root": str(
                REPO_ROOT / "development/spinup_surrogate/summaries/iter011"
            ),
            "reproduction": reproduction,
            "full_fit_diagnostics": full_fit_diagnostics,
        },
        "package_versions": _package_versions(),
        "worker_controls": {
            "n_jobs": args.n_jobs,
            "pre_dispatch": args.pre_dispatch,
            "numerical_library_threads": 1,
            "fixed_lbfgs_note": (
                "Direct fixed-parameter MLPRegressor fitting has no n_jobs parameter; "
                "controls are locked for workflow compatibility and any reusable parallel stage"
            ),
        },
        "source_provenance": {
            "repo_root": str(REPO_ROOT),
            "source_manifest": str(source_manifest),
            "source_manifest_sha256": _sha256(source_manifest),
            "submission_config": str(submission_config),
            "submission_config_sha256": _sha256(submission_config),
        },
    }
    validate_versioned_artifact(artifact)
    pre_save_prediction = predict_versioned_spinup(artifact, X[:12, :])
    output_path = Path(args.output_artifact).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp.{os.environ.get('SLURM_JOB_ID', 'manual')}"
    )
    if temporary_path.exists():
        raise FileExistsError(f"Refusing to overwrite stale temporary artifact: {temporary_path}")
    with temporary_path.open("wb") as fp:
        pickle.dump(artifact, fp, protocol=pickle.HIGHEST_PROTOCOL)
    with temporary_path.open("rb") as fp:
        loaded = pickle.load(fp)
    validate_versioned_artifact(loaded)
    post_load_prediction = predict_versioned_spinup(loaded, X[:12, :])
    if not np.allclose(pre_save_prediction, post_load_prediction, rtol=RTOL, atol=ATOL):
        raise ValueError("Pre-save/post-load predictions differ beyond locked tolerance")
    os.replace(temporary_path, output_path)
    artifact_sha = _sha256(output_path)
    manifest = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "variant": args.variant,
        "artifact_filename": output_path.name,
        "artifact_size_bytes": output_path.stat().st_size,
        "artifact_sha256": artifact_sha,
        "created_utc": created,
        "source_manifest_sha256": _sha256(source_manifest),
        "submission_config_sha256": _sha256(submission_config),
    }
    validation = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "variant": args.variant,
        "passed": True,
        "reproduction_gate": reproduction,
        "pre_save_post_load": {
            "rtol": RTOL,
            "atol": ATOL,
            "max_abs_difference": float(
                np.max(np.abs(pre_save_prediction - post_load_prediction))
            ),
            "prediction_shape": list(pre_save_prediction.shape),
            "prediction_sha256": hashlib.sha256(
                post_load_prediction.tobytes()
            ).hexdigest(),
        },
        "target_metadata_audit": target_metadata,
        "full_fit_diagnostics": full_fit_diagnostics,
        "artifact_sha256": artifact_sha,
        "artifact_size_bytes": output_path.stat().st_size,
    }
    (output_path.parent / "artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (output_path.parent / "validation_report.json").write_text(
        json.dumps(validation, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        f"ITER012_RELEASE_OK variant={args.variant} artifact={output_path} "
        f"sha256={artifact_sha} rows={X.shape[0]} features={X.shape[1]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
