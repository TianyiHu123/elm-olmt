"""Targeted synthetic checks for forcing-coupling Iter001 contracts."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from sklearn.linear_model import LinearRegression

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.surrogate_NN_Forcing import (
    _build_split_indices,
    _complete_regression_diagnostics,
    _forcing_output_path,
    _load_forcing_layout_dict,
    _permutation_importance_payload,
    _save_forcing_layout_npz,
    _schema_sha256,
)

ITER001_SLURM = REPO_ROOT / "development/spinup_forcing_coupling/slurm/iter001"
if str(ITER001_SLURM) not in sys.path:
    sys.path.insert(0, str(ITER001_SLURM))
from aggregate_iter001 import (  # noqa: E402
    CASES as AGGREGATE_CASES,
    REPOSITORY_COMMIT,
    distribution,
    main as aggregate_main,
    schema_sha256,
    sha256 as file_sha256,
    validate_seed_set,
)
from validate_iter001_aggregate import validate_aggregate  # noqa: E402
from validate_iter001_pilot import normalize_layout_dtype  # noqa: E402


class Iter001ForcingContractsTest(unittest.TestCase):
    def test_direct_output_contract_has_no_implicit_uq_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            expected = Path(tmp).resolve() / "run_a" / "surrogate_forcing"
            self.assertEqual(_forcing_output_path(tmp, "run_a"), expected)
            self.assertNotIn("UQ_output", expected.parts)
        for invalid in ("", ".", "..", "a/b"):
            with self.assertRaises(ValueError):
                _forcing_output_path("/tmp", invalid)

    def test_random_time_window_is_seeded_contiguous_and_nonempty(self) -> None:
        case_ids = np.repeat(np.arange(2), 20)
        member_ids = np.tile(np.repeat(np.arange(2), 10), 2)
        time_ids = np.tile(np.arange(10), 4)
        site_ids = case_ids.copy()
        first = _build_split_indices(
            case_ids, member_ids, time_ids, site_ids, "random_time_window", 0.8, 10001
        )
        second = _build_split_indices(
            case_ids, member_ids, time_ids, site_ids, "random_time_window", 0.8, 10001
        )
        self.assertTrue(np.array_equal(first[0], second[0]))
        self.assertTrue(np.array_equal(first[1], second[1]))
        self.assertGreater(first[0].size, 0)
        self.assertGreater(first[1].size, 0)
        for case_id in range(2):
            selected_times = np.unique(time_ids[first[0]][case_ids[first[0]] == case_id])
            self.assertEqual(selected_times.size, 8)
            self.assertTrue(np.all(np.diff(selected_times) == 1))

    def test_metric_and_overfitting_formulas(self) -> None:
        result = _complete_regression_diagnostics(
            np.array([0.0, 1.0, 2.0]),
            np.array([0.0, 1.0, 2.0]),
            np.array([0.0, 1.0, 2.0]),
            np.array([0.0, 2.0, 4.0]),
        )
        self.assertAlmostEqual(result["train"]["rmse"], 0.0)
        self.assertAlmostEqual(result["test"]["rmse"], np.sqrt(5.0 / 3.0))
        self.assertTrue(np.isinf(result["rmse_ratio"]))
        self.assertTrue(result["rmse_warning"])
        self.assertTrue(result["overfitting_warning"])

    def test_layout_round_trip_locks_complete_ordered_schema(self) -> None:
        forcing = ["FSDS", "TBOT_roll24"]
        params = ["leafcn", "frootcn"]
        spinup = ["TOTSOMC", "TOTSOMN"]
        ordered = forcing + params + spinup
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "layout.npz"
            _save_forcing_layout_npz(
                path,
                rows=4,
                nfeatures=6,
                dtype_np=np.dtype("float32"),
                row_case_ids=np.array([0, 0, 1, 1]),
                row_member_ids=np.array([0, 0, 0, 0]),
                row_time_ids=np.array([0, 1, 0, 1]),
                row_site_ids=np.array([0, 0, 1, 1]),
                site_names=["A", "B"],
                forcing_feature_names=forcing,
                forcing_vars_used=["FSDS", "TBOT"],
                parameter_names=params,
                spinup_vars=spinup,
                case_names=["A", "B"],
                n_forcing=2,
                n_params=2,
                n_spinup=2,
            )
            loaded = _load_forcing_layout_dict(path)
        self.assertEqual(loaded["parameter_names"], params)
        self.assertEqual(loaded["ordered_feature_names"], ordered)
        self.assertEqual(loaded["ordered_feature_schema_sha256"], _schema_sha256(ordered))

    def test_layout_dtype_normalizes_class_style_numpy_value(self) -> None:
        self.assertEqual(normalize_layout_dtype("float32"), np.dtype("float32"))
        self.assertEqual(
            normalize_layout_dtype("<class 'numpy.float32'>"), np.dtype("float32")
        )
        with self.assertRaisesRegex(ValueError, "Unsupported pilot memmap dtype"):
            normalize_layout_dtype("<class 'numpy.not_a_dtype'>")

    def test_permutation_importance_is_complete_finite_and_reproducible(self) -> None:
        X = np.array(
            [[0.0, 0.0], [1.0, 0.0], [2.0, 1.0], [3.0, 1.0], [4.0, 2.0], [5.0, 2.0]]
        )
        y = 3.0 * X[:, 0] - X[:, 1]
        estimator = LinearRegression().fit(X, y)
        first = _permutation_importance_payload(
            estimator, X, y, 2.0, ["x0", "x1"], n_repeats=8, random_state=10001
        )
        second = _permutation_importance_payload(
            estimator, X, y, 2.0, ["x0", "x1"], n_repeats=8, random_state=10001
        )
        self.assertEqual(first, second)
        self.assertEqual(first["feature_count"], 2)
        for feature in first["features"]:
            self.assertEqual(len(feature["test_r2_decrease"]), 8)
            self.assertEqual(len(feature["test_rmse_increase"]), 8)
            self.assertTrue(np.all(np.isfinite(feature["test_r2_decrease"])))
            self.assertTrue(np.all(np.isfinite(feature["test_rmse_increase"])))

    def test_aggregation_distribution_and_seed_invariants(self) -> None:
        summary = distribution([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(summary["min"], 1.0)
        self.assertEqual(summary["median"], 2.5)
        self.assertEqual(summary["max"], 4.0)
        validate_seed_set(list(range(10001, 10101)))
        with self.assertRaises(ValueError):
            validate_seed_set(list(range(10001, 10100)) + [10099])

    def test_synthetic_end_to_end_aggregation_and_output_validation(self) -> None:
        ordered = ["forcing_a", "parameter_a"]
        diagnostics = {
            "train": {"r2": 0.8, "rmse": 1.0, "n_rows": 80},
            "test": {"r2": 0.7, "rmse": 1.2, "n_rows": 20},
            "r2_gap": 0.1,
            "rmse_ratio": 1.2,
            "r2_warning": False,
            "rmse_warning": False,
            "overfitting_warning": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            source = root / "source.sha256"
            dependency = root / "dependency.json"
            config = root / "production.env"
            source.write_text("source\n", encoding="utf-8")
            dependency.write_text("{}\n", encoding="utf-8")
            config.write_text("STAGE=production\n", encoding="utf-8")
            provenance = {
                "repository_commit": REPOSITORY_COMMIT,
                "source_manifest_sha256": file_sha256(source),
                "dependency_manifest_sha256": file_sha256(dependency),
                "submission_config_sha256": file_sha256(config),
            }
            for seed in range(10001, 10101):
                importance = []
                for index, name in enumerate(ordered):
                    r2_values = [0.01 * (index + 1)] * 8
                    rmse_values = [0.1 * (index + 1)] * 8
                    importance.append(
                        {
                            "feature": name,
                            "test_r2_decrease": r2_values,
                            "test_r2_decrease_mean": r2_values[0],
                            "test_r2_decrease_std": 0.0,
                            "test_rmse_increase": rmse_values,
                            "test_rmse_increase_mean": rmse_values[0],
                            "test_rmse_increase_std": 0.0,
                        }
                    )
                payload = {
                    "schema": "olmt-forcing-surrogate-stats-v2",
                    "split_random_state": seed,
                    "split_mode": "random_time_window",
                    "train_fraction": 0.8,
                    "output_label": "spinup_forcing_coupling_iter001_baseline",
                    "case_names": AGGREGATE_CASES,
                    "outvars": ["SR"],
                    "ordered_feature_names": ordered,
                    "ordered_feature_schema_sha256": schema_sha256(ordered),
                    "provenance": provenance,
                    "by_variable": {
                        "SR": {
                            "pooled": diagnostics,
                            "by_site": {case: diagnostics for case in AGGREGATE_CASES},
                            "permutation_importance": {
                                "n_repeats": 8,
                                "random_state": seed,
                                "feature_count": len(ordered),
                                "features": importance,
                            },
                        }
                    },
                }
                (input_dir / f"surrogate_forcing_stats_seed{seed}.json").write_text(
                    json.dumps(payload), encoding="utf-8"
                )
            argv = [
                "aggregate_iter001.py",
                "--input-dir",
                str(input_dir),
                "--output-dir",
                str(output_dir),
                "--source-manifest",
                str(source),
                "--dependency-manifest",
                str(dependency),
                "--production-config",
                str(config),
            ]
            with patch.object(sys, "argv", argv):
                self.assertEqual(aggregate_main(), 0)
            report = validate_aggregate(
                output_dir,
                source_manifest=source,
                dependency_manifest=dependency,
                production_config=config,
            )
            self.assertEqual(report["gate"], "pass")


if __name__ == "__main__":
    unittest.main()
