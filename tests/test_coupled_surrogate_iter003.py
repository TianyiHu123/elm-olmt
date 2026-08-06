"""Synthetic unit tests for Iter003 coupled-surrogate primitives."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM import coupled_surrogate as cs
from model_ELM.surrogate_NN_Forcing import compose_forcing_surrogate_design_matrix


class MetricTests(unittest.TestCase):
    def test_perfect_metrics(self) -> None:
        obs = np.linspace(0.0, 1.0, 50)
        pred = obs.copy()
        m = cs.compute_sr_metrics(obs, pred)
        self.assertAlmostEqual(m["r2"], 1.0, places=12)
        self.assertAlmostEqual(m["rmse"], 0.0, places=12)
        self.assertAlmostEqual(m["bias"], 0.0, places=12)
        self.assertAlmostEqual(m["mae"], 0.0, places=12)
        self.assertAlmostEqual(m["pearson_r"], 1.0, places=12)
        self.assertAlmostEqual(m["kge"], 1.0, places=12)

    def test_kge_penalizes_bias(self) -> None:
        obs = np.linspace(1.0, 2.0, 40)
        pred = obs + 0.5
        kge = cs.metric_kge(obs, pred)
        self.assertLess(kge, 1.0)
        self.assertTrue(np.isfinite(kge))


class DesignMatrixTests(unittest.TestCase):
    def test_compose_tiles_params_and_spinup(self) -> None:
        layout = {"n_forcing_cols": 3, "n_params": 2, "n_spinup": 2}
        fe = np.arange(12, dtype=float).reshape(4, 3)
        params = np.asarray([10.0, 20.0])
        spinup = np.asarray([100.0, 200.0])
        X = compose_forcing_surrogate_design_matrix(fe, params, spinup, layout)
        self.assertEqual(X.shape, (4, 7))
        np.testing.assert_allclose(X[:, :3], fe)
        np.testing.assert_allclose(X[:, 3:5], np.tile(params, (4, 1)))
        np.testing.assert_allclose(X[:, 5:], np.tile(spinup, (4, 1)))


class CoupledPredictTests(unittest.TestCase):
    def test_predict_uses_predicted_spinup_not_elm(self) -> None:
        case = SimpleNamespace(
            samples=np.arange(14 * 3, dtype=float).reshape(14, 3),
            casename="FAKE",
            nsamples=3,
        )
        spinup_art = {
            "variant": "drop32",
            "training_layout": {"input_feature_names": ["f0", "f1"]},
        }
        forcing_art = {
            "training_layout": {
                "n_forcing_cols": 1,
                "n_params": 14,
                "n_spinup": 2,
                "ordered_feature_names": [f"c{i}" for i in range(17)],
            }
        }
        captured = {}

        with mock.patch.object(
            cs,
            "case_inference_components",
            return_value={"surface": np.zeros(1), "climatology": np.zeros(1)},
        ), mock.patch.object(
            cs, "build_selected_inference_matrix", return_value=(np.zeros((1, 2)), [])
        ), mock.patch.object(
            cs, "predict_versioned_spinup", return_value=np.asarray([[111.0, 222.0]])
        ), mock.patch.object(
            cs,
            "build_forcing_inference_inputs",
            return_value={
                "ntime": 4,
                "forcing_engineered": np.ones((4, 1)),
                "spinup": np.asarray([999.0, 888.0]),
                "forcing_time": np.arange(4),
                "forcing_time_source": "test",
            },
        ), mock.patch.object(
            cs,
            "compose_forcing_surrogate_design_matrix",
            side_effect=lambda fe, params, spinup, layout: (
                captured.update({"spinup": np.asarray(spinup).copy()})
                or np.ones((4, 17))
            ),
        ), mock.patch.object(
            cs,
            "predict_versioned_forcing",
            side_effect=lambda _a, X: np.linspace(0.0, 1.0, X.shape[0]).reshape(-1, 1),
        ):
            out = cs.predict_coupled_sr(
                case,
                spinup_artifact=spinup_art,
                forcing_artifact=forcing_art,
                member=1,
            )

        np.testing.assert_allclose(captured["spinup"], [111.0, 222.0])
        self.assertEqual(out["TOTSOMC"], 111.0)
        self.assertEqual(out["TOTSOMN"], 222.0)
        self.assertEqual(out["ntime"], 4)
        self.assertEqual(out["SR"].shape, (4,))

    def test_requires_exactly_one_of_member_or_parameters(self) -> None:
        with self.assertRaises(ValueError):
            cs.predict_coupled_sr(
                SimpleNamespace(),
                spinup_artifact={},
                forcing_artifact={},
            )


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
