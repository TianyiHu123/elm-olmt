#!/usr/bin/env python
"""Build one locked Iter002 full-data forcing-surrogate-v1 release artifact."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.forcing_surrogate_artifact import (  # noqa: E402
    predict_versioned_forcing,
    validate_versioned_forcing_artifact,
)
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    _complete_regression_diagnostics,
    _flatten_targets_for_blocks,
    _load_forcing_layout_dict,
    _permutation_importance_payload,
    _prepare_case_training_block_targets_only,
    _resolve_forcing_memmap_paths,
    _schema_sha256,
)

SCHEMA_VERSION = "forcing-surrogate-v1"
RELEASE_VERSION = "iter002-v1"
TARGET_ORDER = ["SR"]
FORCING_VARS = ["PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF"]
SPINUP_VARS = ["TOTSOMC", "TOTSOMN"]
DEFAULT_CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]
LOCKED_MEMMAP_SIZE = 7148160000
LOCKED_MEMMAP_SHA256 = "01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6"
LOCKED_LAYOUT_SHA256 = "a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0"
LOCKED_SCHEMA_SHA256 = "cbe2daf49d74f5cc7b99caed138c8da314d42095cd8ea8a41cb762c903e93061"
METRIC_KEYS = ["r2_train", "r2_test", "rmse_train", "rmse_test", "r2_gap", "rmse_ratio"]
RTOL = 1.0e-10
ATOL = 1.0e-8
SPLIT_SEED = 10001
CV_FOLDS = 3
PERMUTATION_REPEATS = 8
LOCKED_BASELINE_AGGREGATE_SHA256 = (
    "b75510b4f1fc64109d5be942e93d4af1662bd1c7a2a07c565f065245ce69f0a3"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-list", required=True)
    parser.add_argument("--reuse-x-memmap", required=True)
    parser.add_argument(
        "--baseline-aggregate",
        required=True,
        help="Iter001 100-seed aggregate JSON used only for characterization comparison",
    )
    parser.add_argument("--output-artifact", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--submission-config", required=True)
    parser.add_argument("--importance-outdir", required=True)
    parser.add_argument("--n-jobs", required=True, type=int)
    parser.add_argument("--memmap-sha256", default=LOCKED_MEMMAP_SHA256)
    parser.add_argument("--layout-sha256", default=LOCKED_LAYOUT_SHA256)
    parser.add_argument("--schema-sha256", default=LOCKED_SCHEMA_SHA256)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_dtype(dtype_str: str) -> np.dtype:
    text = str(dtype_str).strip()
    if text in {"float32", "np.float32", "<class 'numpy.float32'>", "numpy.float32"}:
        return np.dtype(np.float32)
    if text in {"float64", "np.float64", "<class 'numpy.float64'>", "numpy.float64"}:
        return np.dtype(np.float64)
    return np.dtype(text)


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
            f"Physical parameter names invalid: count={len(names)}, n_params={n_params}"
        )
    pmin = np.asarray(case.ensemble_pmin, dtype=np.float64).reshape(-1)
    pmax = np.asarray(case.ensemble_pmax, dtype=np.float64).reshape(-1)
    if pmin.size != n_params or pmax.size != n_params:
        raise ValueError("ensemble_pmin/pmax lengths do not match nparms_ensemble")
    if np.any(~np.isfinite(pmin)) or np.any(~np.isfinite(pmax)) or np.any(pmin > pmax):
        raise ValueError("Parameter bounds are non-finite or inverted")
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


def _quick_grid() -> Dict[str, Any]:
    return {
        "hidden_layer_sizes": [(64,), (128,)],
        "activation": ["relu"],
        "solver": ["adam"],
        "alpha": [1e-4, 1e-3],
        "learning_rate": ["adaptive"],
    }


def _fit_grid(
    X: np.ndarray,
    y: np.ndarray,
    *,
    n_jobs: int,
) -> Tuple[Any, Any, Any, Dict[str, Any]]:
    x_scaler = preprocessing.StandardScaler().fit(X)
    y_scaler = preprocessing.StandardScaler().fit(y.reshape(-1, 1))
    X_scaled = x_scaler.transform(X)
    y_scaled = y_scaler.transform(y.reshape(-1, 1)).ravel()
    clf = MLPRegressor(
        max_iter=500,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10,
        random_state=42,
    )
    grid = GridSearchCV(
        clf,
        _quick_grid(),
        n_jobs=n_jobs,
        cv=CV_FOLDS,
        pre_dispatch=n_jobs,
    )
    grid.fit(X_scaled, y_scaled)
    pred = y_scaler.inverse_transform(grid.predict(X_scaled).reshape(-1, 1)).ravel()
    return grid, x_scaler, y_scaler, {"best_params": dict(grid.best_params_), "pred": pred}


def _percentile_rank(value: float, dist: Mapping[str, Any]) -> float:
    """Approximate percentile using five-number summary when raw samples are unavailable."""
    points = [
        float(dist["min"]),
        float(dist["q25"]),
        float(dist["median"]),
        float(dist["q75"]),
        float(dist["max"]),
    ]
    percentiles = [0.0, 25.0, 50.0, 75.0, 100.0]
    if value <= points[0]:
        return 0.0
    if value >= points[-1]:
        return 100.0
    for left, right, p_left, p_right in zip(
        points, points[1:], percentiles, percentiles[1:]
    ):
        if left <= value <= right:
            if right == left:
                return float(p_left)
            frac = (value - left) / (right - left)
            return float(p_left + frac * (p_right - p_left))
    return 100.0


def _baseline_comparison_characterization(
    full_diag: Mapping[str, Any],
    best_params: Mapping[str, Any],
    baseline_aggregate: Mapping[str, Any],
    baseline_path: Path,
) -> Dict[str, Any]:
    """Record full-data in-sample metrics vs Iter001 100-seed distributions.

    Characterization only: never a pass/fail gate. Full-data in-sample metrics are not
    held-out split metrics; comparison to the 100-seed held-out distribution is diagnostic.
    """
    distributions = baseline_aggregate.get("metric_distributions")
    if not isinstance(distributions, Mapping):
        raise ValueError("Baseline aggregate missing metric_distributions")
    for key in METRIC_KEYS:
        if key not in distributions:
            raise ValueError(f"Baseline aggregate missing metric_distributions[{key}]")

    in_sample_r2 = float(full_diag["train"]["r2"])
    in_sample_rmse = float(full_diag["train"]["rmse"])
    # Full-data fit has no holdout; map in-sample analogs for distribution comparison.
    observed = {
        "r2_train": in_sample_r2,
        "r2_test": in_sample_r2,
        "rmse_train": in_sample_rmse,
        "rmse_test": in_sample_rmse,
        "r2_gap": 0.0,
        "rmse_ratio": 1.0,
    }
    comparisons = {}
    for key in METRIC_KEYS:
        dist = distributions[key]
        value = float(observed[key])
        comparisons[key] = {
            "observed_full_data_in_sample_analog": value,
            "baseline_100seed": {
                "mean": float(dist["mean"]),
                "median": float(dist["median"]),
                "std": float(dist["std"]),
                "min": float(dist["min"]),
                "q25": float(dist["q25"]),
                "q75": float(dist["q75"]),
                "max": float(dist["max"]),
            },
            "delta_vs_mean": value - float(dist["mean"]),
            "delta_vs_median": value - float(dist["median"]),
            "approx_percentile_vs_five_number": _percentile_rank(value, dist),
        }
    return {
        "role": "characterization_only_not_a_gate",
        "note": (
            "Full-data in-sample metrics are compared to Iter001 100-seed held-out "
            "metric distributions for diagnosis only. r2_test/rmse_test/r2_gap/rmse_ratio "
            "analogs are filled from in-sample values (gap=0, ratio=1) because there is "
            "no holdout in the full-data fit."
        ),
        "baseline_aggregate_path": str(baseline_path),
        "baseline_aggregate_sha256": _sha256(baseline_path),
        "eligible_seed_count": int(baseline_aggregate.get("eligible_seed_count", -1)),
        "best_params": dict(best_params),
        "full_data_in_sample": {
            "r2": in_sample_r2,
            "rmse": in_sample_rmse,
            "rows": int(full_diag["train"].get("n_rows", -1)),
        },
        "comparisons": comparisons,
    }


def _write_importance_products(
    importance: Mapping[str, Any],
    outdir: Path,
    ordered_feature_names: Sequence[str],
) -> Dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / "full_data_permutation_importance.json"
    csv_path = outdir / "full_data_permutation_importance.csv"
    plot_path = outdir / "full_data_permutation_importance_rmse.png"
    payload = {
        "schema": "spinup-forcing-coupling-iter002-full-data-importance-v1",
        "kind": "full_data_in_sample",
        "n_repeats": importance["n_repeats"],
        "random_state": importance["random_state"],
        "ordered_feature_names": list(ordered_feature_names),
        "features": importance["features"],
    }
    json_path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "feature",
                "test_rmse_increase_mean",
                "test_rmse_increase_std",
                "test_r2_decrease_mean",
                "test_r2_decrease_std",
            ],
        )
        writer.writeheader()
        for row in importance["features"]:
            writer.writerow(
                {
                    "feature": row["feature"],
                    "test_rmse_increase_mean": row["test_rmse_increase_mean"],
                    "test_rmse_increase_std": row["test_rmse_increase_std"],
                    "test_r2_decrease_mean": row["test_r2_decrease_mean"],
                    "test_r2_decrease_std": row["test_r2_decrease_std"],
                }
            )
    names = [row["feature"] for row in importance["features"]]
    means = [float(row["test_rmse_increase_mean"]) for row in importance["features"]]
    order = np.argsort(means)[::-1]
    fig, ax = plt.subplots(figsize=(10, max(6, 0.28 * len(names))))
    ax.barh(
        [names[i] for i in order][::-1],
        [means[i] for i in order][::-1],
        color="#4c78a8",
    )
    ax.set_xlabel("Mean in-sample RMSE increase")
    ax.set_title("Iter002 full-data permutation importance (SR)")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    return {
        "json": str(json_path),
        "csv": str(csv_path),
        "plot": str(plot_path),
        "json_sha256": _sha256(json_path),
        "csv_sha256": _sha256(csv_path),
        "plot_sha256": _sha256(plot_path),
    }


def _package_versions() -> Dict[str, str]:
    result = {}
    for name in ("numpy", "scikit-learn", "netCDF4", "joblib", "matplotlib"):
        result[name] = importlib.metadata.version(name)
    result["python"] = sys.version.split()[0]
    return result


def main() -> int:
    args = _parser().parse_args()
    if args.n_jobs != 4:
        raise ValueError(f"Locked worker controls require n_jobs=4, got {args.n_jobs}")
    case_names = [v.strip() for v in args.case_list.split(",") if v.strip()]
    if case_names != DEFAULT_CASES:
        raise ValueError(f"Case list/order mismatch: {case_names}")

    memmap_dir = Path(args.reuse_x_memmap).resolve()
    memmap_path, layout_path = _resolve_forcing_memmap_paths(memmap_dir)
    if memmap_path.stat().st_size != LOCKED_MEMMAP_SIZE:
        raise ValueError(f"Memmap size mismatch: {memmap_path.stat().st_size}")
    memmap_sha = _sha256(memmap_path)
    layout_sha = _sha256(layout_path)
    if memmap_sha != args.memmap_sha256:
        raise ValueError(f"Memmap hash mismatch: {memmap_sha}")
    if layout_sha != args.layout_sha256:
        raise ValueError(f"Layout hash mismatch: {layout_sha}")

    layout = _load_forcing_layout_dict(layout_path)
    dtype_np = _normalize_dtype(layout["dtype_str"])
    if list(layout["case_names"]) != case_names:
        raise ValueError("Layout case order mismatch")
    if list(layout["forcing_vars_used"]) != FORCING_VARS:
        raise ValueError("Layout forcing vars mismatch")
    if list(layout["spinup_vars"]) != SPINUP_VARS:
        raise ValueError("Layout spinup vars mismatch")

    cases = _load_cases(case_names)
    blocks = [
        _prepare_case_training_block_targets_only(
            case,
            TARGET_ORDER,
            SPINUP_VARS,
            layout["n_forcing"],
            layout["forcing_vars_used"],
            layout["forcing_feature_names"],
            layout["n_spinup"],
        )
        for case in cases
    ]
    rows = int(layout["rows"])
    nfeatures = int(layout["nfeatures"])
    X = np.memmap(memmap_path, mode="r", dtype=dtype_np, shape=(rows, nfeatures))
    y = _flatten_targets_for_blocks(blocks, "SR", dtype_np).ravel().astype(np.float64)

    ordered_feature_names = [
        *layout["forcing_feature_names"],
        *layout["parameter_names"],
        *layout["spinup_vars"],
    ]
    schema_sha = _schema_sha256(ordered_feature_names)
    if schema_sha != args.schema_sha256 or schema_sha != LOCKED_SCHEMA_SHA256:
        raise ValueError(f"Schema hash mismatch: {schema_sha}")

    baseline_path = Path(args.baseline_aggregate).resolve()
    baseline_sha = _sha256(baseline_path)
    if baseline_sha != LOCKED_BASELINE_AGGREGATE_SHA256:
        raise ValueError(
            f"Baseline aggregate hash mismatch: {baseline_sha} != "
            f"{LOCKED_BASELINE_AGGREGATE_SHA256}"
        )
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if int(baseline.get("eligible_seed_count", -1)) != 100:
        raise ValueError("Baseline aggregate must be the Iter001 exact-100 seed distribution")
    if baseline.get("ordered_feature_schema_sha256") != LOCKED_SCHEMA_SHA256:
        raise ValueError("Baseline aggregate schema hash mismatch")
    if list(baseline.get("case_order", [])) != case_names:
        raise ValueError("Baseline aggregate case order mismatch")

    print("Starting full-data fit...")
    model, x_scaler, y_scaler, fit_info = _fit_grid(X, y, n_jobs=args.n_jobs)
    pred_full = fit_info["pred"]
    full_diag = _complete_regression_diagnostics(y, pred_full, y, pred_full)
    print(
        "FULL_DATA_FIT_OK "
        f"r2={full_diag['train']['r2']:.6f} rmse={full_diag['train']['rmse']:.6f}"
    )
    baseline_comparison = _baseline_comparison_characterization(
        full_diag,
        fit_info["best_params"],
        baseline,
        baseline_path,
    )
    comparison_path = Path(args.importance_outdir).resolve() / "full_data_vs_baseline100seed.json"
    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_path.write_text(
        json.dumps(baseline_comparison, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"BASELINE_COMPARISON_RECORDED path={comparison_path}")

    X_scaled = x_scaler.transform(X)
    y_scaled = y_scaler.transform(y.reshape(-1, 1)).ravel()
    importance = _permutation_importance_payload(
        model,
        X_scaled,
        y_scaled,
        float(y_scaler.scale_[0]),
        ordered_feature_names,
        n_repeats=PERMUTATION_REPEATS,
        random_state=SPLIT_SEED,
    )
    if [row["feature"] for row in importance["features"]] != list(ordered_feature_names):
        raise ValueError("Importance feature order mismatch")
    importance_paths = _write_importance_products(
        importance,
        Path(args.importance_outdir).resolve(),
        ordered_feature_names,
    )
    print("FULL_DATA_IMPORTANCE_PASS")

    source_manifest = Path(args.source_manifest).resolve()
    submission_config = Path(args.submission_config).resolve()
    created = datetime.now(timezone.utc).isoformat()
    parameter_metadata = _physical_parameter_metadata(cases[0])
    training_layout = {
        "forcing_feature_names": list(layout["forcing_feature_names"]),
        "forcing_vars_used": list(layout["forcing_vars_used"]),
        "parameter_names": list(layout["parameter_names"]),
        "spinup_vars": list(layout["spinup_vars"]),
        "ordered_feature_names": list(ordered_feature_names),
        "ordered_feature_schema_sha256": schema_sha,
        "n_forcing_cols": int(layout["n_forcing"]),
        "n_params": int(layout["n_params"]),
        "n_spinup": int(layout["n_spinup"]),
        "case_names": list(case_names),
        "tair_var": "TBOT",
        "precip_var": "PRECTmms",
        "hyperparameters": {
            "quick_grid": True,
            "cv_folds": CV_FOLDS,
            "n_jobs": args.n_jobs,
            "estimator_random_state": 42,
        },
    }
    detail_configuration = {
        "schema_version": SCHEMA_VERSION,
        "release_version": RELEASE_VERSION,
        "cases": list(case_names),
        "target": "SR",
        "forcing_families": FORCING_VARS,
        "spinup_state_inputs": SPINUP_VARS,
        "parameters": list(layout["parameter_names"]),
        "feature_schema_sha256": schema_sha,
        "hyperparameters": "historical --quick-grid",
        "cv_folds": CV_FOLDS,
        "n_jobs": args.n_jobs,
        "fit_scope": "full_data",
        "importance": {
            "kind": "full_data_in_sample",
            "n_repeats": PERMUTATION_REPEATS,
            "random_state": SPLIT_SEED,
        },
        "inference_tolerances": {"rtol": RTOL, "atol": ATOL},
        "metric_comparison_role": "characterization_only_vs_iter001_100seed_distribution",
    }
    artifact: Dict[str, Any] = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "created_utc": created,
        "trusted_source_only": True,
        "environment_version_sensitive": True,
        "target_order": TARGET_ORDER,
        "detail_configuration": detail_configuration,
        "models": {"SR": model},
        "x_scaler": {"SR": x_scaler},
        "y_scaler": {"SR": y_scaler},
        "training_layout": training_layout,
        "parameter_metadata": parameter_metadata,
        "fit_scope": {
            "kind": "full_data",
            "rows": int(rows),
            "cases": list(case_names),
            "estimator_seed": 42,
            "validation_evidence_kind": "operational load/inference validation only",
        },
        "validation_evidence": {
            "iter001_baseline_aggregate": str(baseline_path),
            "iter001_baseline_aggregate_sha256": baseline_sha,
            "baseline_comparison_characterization": baseline_comparison,
            "baseline_comparison_path": str(comparison_path),
            "baseline_comparison_sha256": _sha256(comparison_path),
            "memmap_path": str(memmap_path),
            "memmap_sha256": memmap_sha,
            "layout_path": str(layout_path),
            "layout_sha256": layout_sha,
            "full_fit_diagnostics": {
                "SR": {
                    "rows": int(rows),
                    "training_r2": float(full_diag["train"]["r2"]),
                    "training_rmse": float(full_diag["train"]["rmse"]),
                    "best_params": fit_info["best_params"],
                    "note": (
                        "full-data training diagnostic; not validation evidence; "
                        "baseline comparison is characterization only"
                    ),
                }
            },
            "full_data_importance": importance_paths,
        },
        "package_versions": _package_versions(),
        "worker_controls": {
            "n_jobs": args.n_jobs,
            "pre_dispatch": "n_jobs",
            "numerical_library_threads": 1,
        },
        "source_provenance": {
            "repo_root": str(REPO_ROOT),
            "source_manifest": str(source_manifest),
            "source_manifest_sha256": _sha256(source_manifest),
            "submission_config": str(submission_config),
            "submission_config_sha256": _sha256(submission_config),
        },
    }
    validate_versioned_forcing_artifact(artifact)
    sample = np.asarray(X[:32, :], dtype=np.float64)
    pre_save_prediction = predict_versioned_forcing(artifact, sample)

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
    validate_versioned_forcing_artifact(loaded)
    post_load_prediction = predict_versioned_forcing(loaded, sample)
    if not np.allclose(pre_save_prediction, post_load_prediction, rtol=RTOL, atol=ATOL):
        raise ValueError("Pre-save/post-load predictions differ beyond locked tolerance")
    os.replace(temporary_path, output_path)
    artifact_sha = _sha256(output_path)
    manifest = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "artifact_filename": output_path.name,
        "artifact_size_bytes": output_path.stat().st_size,
        "artifact_sha256": artifact_sha,
        "created_utc": created,
        "source_manifest_sha256": _sha256(source_manifest),
        "submission_config_sha256": _sha256(submission_config),
        "memmap_sha256": memmap_sha,
        "layout_sha256": layout_sha,
        "schema_sha256": schema_sha,
        "importance": importance_paths,
    }
    validation = {
        "release_version": RELEASE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "passed": True,
        "pass_criteria": (
            "artifact_write_and_pre_save_post_load_identity; "
            "metric/baseline comparison is characterization only"
        ),
        "baseline_comparison_characterization": {
            "path": str(comparison_path),
            "sha256": _sha256(comparison_path),
            "role": "characterization_only_not_a_gate",
        },
        "pre_save_post_load": {
            "rtol": RTOL,
            "atol": ATOL,
            "max_abs_difference": float(
                np.max(np.abs(pre_save_prediction - post_load_prediction))
            ),
            "prediction_shape": list(pre_save_prediction.shape),
            "prediction_sha256": hashlib.sha256(post_load_prediction.tobytes()).hexdigest(),
        },
        "full_data_importance": importance_paths,
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
        f"ITER002_RELEASE_OK artifact={output_path} sha256={artifact_sha} "
        f"rows={rows} features={nfeatures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
