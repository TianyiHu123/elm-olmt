from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from model_ELM.three_stage_data import CLIMATOLOGY_HOURS, compact_climatology, schema_sha256
from model_ELM.three_stage_spinup import metric_gap_rows, normalize_mlp_config, regression_metrics
from model_ELM.three_stage_spinup_screen import balanced_split_manifest, candidate_manifest
from model_ELM.three_stage_spinup_artifact import load_artifact, predict_matrix, save_artifact


class ThreeStageSpinupTests(unittest.TestCase):
    def test_iter003_candidate_matrix(self) -> None:
        manifest = candidate_manifest()
        self.assertEqual(len(manifest["candidates"]), 96)
        self.assertEqual(sum(item["is_iter002_baseline"] for item in manifest["candidates"]), 1)
        configs = {item["config_sha256"] for item in manifest["candidates"]}
        self.assertEqual(len(configs), 96)

    def test_iter003_balanced_splits(self) -> None:
        members = [f"g{index:05d}" for index in range(1, 820)]
        manifest = balanced_split_manifest(members)
        self.assertEqual(len(manifest["splits"]), 20)
        counts = list(manifest["validation_appearance_counts"].values())
        self.assertEqual(counts.count(4), 815)
        self.assertEqual(counts.count(5), 4)
        self.assertTrue(all(len(split["train_member_ids"]) == 655 for split in manifest["splits"]))
        self.assertTrue(all(len(split["validation_member_ids"]) == 164 for split in manifest["splits"]))

    def test_explicit_mlp_config_validation(self) -> None:
        observed = normalize_mlp_config({
            "hidden_layer_sizes": [64, 32],
            "activation": "relu",
            "solver": "lbfgs",
            "alpha": 10,
            "max_iter": 800,
            "random_state": 42,
        })
        self.assertEqual(observed["hidden_layer_sizes"], [64, 32])
        self.assertEqual(observed["alpha"], 10.0)

    def test_compact_climatology_exact_values(self) -> None:
        forcing = {
            "PRECTmms": np.full(CLIMATOLOGY_HOURS, 2.0),
            "FSDS": np.full(CLIMATOLOGY_HOURS, 3.0),
            "TBOT": np.arange(CLIMATOLOGY_HOURS, dtype=np.float64),
            "RH": np.tile(np.arange(1, 13, dtype=np.float64).repeat(
                np.asarray([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]) * 24
            ), 5),
        }
        observed = compact_climatology(forcing)
        self.assertEqual(observed["PRECTmms_clim_mean"], 2.0)
        self.assertEqual(observed["PRECTmms_clim_std"], 0.0)
        self.assertEqual(observed["FSDS_clim_mean"], 3.0)
        self.assertGreater(observed["TBOT_clim_std"], 0.0)
        self.assertEqual(observed["RH_clim_seasonal_amp"], 11.0)

    def test_metrics_use_predictive_r2(self) -> None:
        truth = np.asarray([1.0, 2.0, 3.0])
        prediction = np.asarray([2.0, 3.0, 4.0])
        metrics = regression_metrics(truth, prediction)
        self.assertAlmostEqual(metrics["r2"], -0.5)
        self.assertAlmostEqual(metrics["bias"], 1.0)

    def test_metric_gaps_are_validation_minus_training(self) -> None:
        rows = []
        for partition, offset in (("training", 1.0), ("validation", 3.0)):
            for site in ("pooled", "ABBY", "JERC"):
                for target in ("TOTSOMC", "TOTSOMN"):
                    for scale in ("physical", "log"):
                        rows.append({
                            "partition": partition,
                            "site": site,
                            "target": target,
                            "scale": scale,
                            "n": 10,
                            "r2": offset,
                            "rmse": offset,
                            "mae": offset,
                            "bias": offset,
                            "residual_std": offset,
                        })
        gaps = metric_gap_rows(rows)
        self.assertEqual(len(gaps), 12)
        self.assertTrue(all(row["rmse_gap"] == 2.0 for row in gaps))

    def test_artifact_round_trip_and_positive_predictions(self) -> None:
        rng = np.random.default_rng(42)
        X = rng.normal(size=(40, 25))
        feature_names = [f"feature_{index}" for index in range(25)]
        models = {}
        x_scalers = {}
        y_scalers = {}
        for target, offset in (("TOTSOMC", 1000.0), ("TOTSOMN", 100.0)):
            y = offset + np.sum(X, axis=1)
            x_scaler = StandardScaler().fit(X)
            log_y = np.log(y).reshape(-1, 1)
            y_scaler = StandardScaler().fit(log_y)
            model = LinearRegression().fit(
                x_scaler.transform(X), y_scaler.transform(log_y).ravel()
            )
            models[target] = model
            x_scalers[target] = x_scaler
            y_scalers[target] = y_scaler
        artifact = {
            "schema": "three-stage-spinup-development-v1",
            "artifact_role": "non_release_smoke",
            "target_order": ["TOTSOMC", "TOTSOMN"],
            "target_transform": "natural_log",
            "models": models,
            "x_scalers": x_scalers,
            "y_scalers": y_scalers,
            "model_config": {
                "hidden_layer_sizes": [32],
                "activation": "tanh",
                "solver": "lbfgs",
                "alpha": 40.0,
                "max_iter": 800,
                "random_state": 42,
            },
            "feature_names": feature_names,
            "feature_schema_sha256": schema_sha256(feature_names),
            "parameter_metadata": {
                "physical_names": [f"p{index}" for index in range(18)],
                "aliases": [f"parm_{index}" for index in range(18)],
                "ensemble_pmin": [0.0] * 18,
                "ensemble_pmax": [1.0] * 18,
            },
            "fit_scope": {
                "train_member_ids": ["g00001"],
                "validation_member_ids": ["g00002"],
            },
            "snapshot_revision": "r0001",
            "snapshot_sha256": "0" * 64,
        }
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "artifact"
            save_artifact(artifact, directory)
            loaded, _, _ = load_artifact(directory)
            prediction = predict_matrix(loaded, X[:3])
            self.assertEqual(prediction.shape, (3, 2))
            self.assertTrue(np.all(prediction > 0.0))


if __name__ == "__main__":
    unittest.main()
