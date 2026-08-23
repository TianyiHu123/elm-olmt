"""Synthetic checks for forcing-coupling Iter002 versioned artifact contracts."""
from __future__ import annotations

import pickle
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.forcing_surrogate_artifact import (
    load_forcing_surrogate_artifact,
    predict_versioned_forcing,
    require_exact_feature_order,
    validate_versioned_forcing_artifact,
)


def _minimal_artifact() -> dict:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 3))
    y = X.sum(axis=1)
    x_scaler = StandardScaler().fit(X)
    y_scaler = StandardScaler().fit(y.reshape(-1, 1))
    model = LinearRegression().fit(x_scaler.transform(X), y_scaler.transform(y.reshape(-1, 1)).ravel())
    names = ["f0", "f1", "f2"]
    return {
        "release_version": "iter002-v1",
        "schema_version": "forcing-surrogate-v1",
        "target_order": ["SR"],
        "models": {"SR": model},
        "x_scaler": {"SR": x_scaler},
        "y_scaler": {"SR": y_scaler},
        "training_layout": {
            "ordered_feature_names": names,
            "ordered_feature_schema_sha256": "abc",
            "n_forcing_cols": 1,
            "n_params": 1,
            "n_spinup": 1,
        },
        "fit_scope": {"kind": "full_data", "rows": 40},
        "parameter_metadata": {
            "physical_names": ["p0"],
            "aliases": ["parm_0"],
            "ensemble_pmin": [0.0],
            "ensemble_pmax": [1.0],
        },
    }


class Iter002ForcingArtifactTest(unittest.TestCase):
    def test_validate_accepts_minimal_and_rejects_bad_schema(self) -> None:
        artifact = _minimal_artifact()
        validate_versioned_forcing_artifact(artifact)
        bad = dict(artifact)
        bad["schema_version"] = "spinup-surrogate-v1"
        with self.assertRaises(ValueError):
            validate_versioned_forcing_artifact(bad)

    def test_feature_order_and_predict(self) -> None:
        artifact = _minimal_artifact()
        require_exact_feature_order(["f0", "f1", "f2"], ["f0", "f1", "f2"])
        with self.assertRaises(ValueError):
            require_exact_feature_order(["f1", "f0", "f2"], ["f0", "f1", "f2"])
        pred = predict_versioned_forcing(artifact, np.ones((5, 3)))
        self.assertEqual(pred.shape, (5, 1))
        self.assertTrue(np.all(np.isfinite(pred)))

    def test_legacy_reject_and_manifest_resolve(self) -> None:
        artifact = _minimal_artifact()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "forcing_surrogate_iter002_sr.pkl"
            with path.open("wb") as fp:
                pickle.dump(artifact, fp)
            (root / "artifact_manifest.json").write_text(
                '{"artifact_filename":"forcing_surrogate_iter002_sr.pkl"}\n',
                encoding="utf-8",
            )
            loaded, resolved = load_forcing_surrogate_artifact(root, allow_legacy=False)
            self.assertEqual(resolved, path.resolve())
            self.assertEqual(loaded["schema_version"], "forcing-surrogate-v1")

            legacy = root / "legacy.pkl"
            with legacy.open("wb") as fp:
                pickle.dump(
                    {
                        "models": artifact["models"],
                        "x_scaler": artifact["x_scaler"],
                        "y_scaler": artifact["y_scaler"],
                        "training_layout": artifact["training_layout"],
                    },
                    fp,
                )
            with self.assertRaises(ValueError):
                load_forcing_surrogate_artifact(legacy, allow_legacy=False)


if __name__ == "__main__":
    unittest.main()
