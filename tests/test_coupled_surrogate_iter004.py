"""Synthetic unit tests for Iter004 offline + coupled comparison primitives."""
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


class OfflinePredictTests(unittest.TestCase):
    def test_predict_uses_elm_restart_spinup(self) -> None:
        case = SimpleNamespace(
            samples=np.arange(14 * 3, dtype=float).reshape(14, 3),
            casename="FAKE",
            nsamples=3,
        )
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
            "build_forcing_inference_inputs",
            return_value={
                "ntime": 4,
                "forcing_engineered": np.ones((4, 1)),
                "spinup": np.asarray([999.0, 888.0]),
                "forcing_time": np.arange(4),
                "forcing_time_source": "test",
            },
        ) as bif, mock.patch.object(
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
            out = cs.predict_offline_sr(
                case,
                forcing_artifact=forcing_art,
                member=1,
            )

        bif.assert_called()
        kwargs = bif.call_args.kwargs
        self.assertEqual(kwargs.get("spinup_member"), 1)
        np.testing.assert_allclose(captured["spinup"], [999.0, 888.0])
        self.assertEqual(out["TOTSOMC"], 999.0)
        self.assertEqual(out["TOTSOMN"], 888.0)
        self.assertEqual(out["spinup_source"], "elm_restart")
        self.assertEqual(out["SR"].shape, (4,))

    def test_requires_exactly_one_of_member_or_parameters(self) -> None:
        with self.assertRaises(ValueError):
            cs.predict_offline_sr(SimpleNamespace(), forcing_artifact={})


class CoupledStillUsesPredictedSpinup(unittest.TestCase):
    def test_coupled_not_elm_spinup(self) -> None:
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
        self.assertEqual(out["spinup_source"], "predicted")


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
