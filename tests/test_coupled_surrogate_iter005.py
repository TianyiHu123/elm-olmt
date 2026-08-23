"""Synthetic unit tests for Iter005 mean-spinup offline path."""
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


class MeanSpinupOfflineTests(unittest.TestCase):
    def test_parameters_mode_uses_mean_spinup(self) -> None:
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
        params = np.arange(14, dtype=float)

        with mock.patch.object(
            cs,
            "build_forcing_inference_inputs",
            return_value={
                "ntime": 4,
                "forcing_engineered": np.ones((4, 1)),
                "spinup": np.asarray([10.0, 20.0]),
                "forcing_time": np.arange(4),
                "forcing_time_source": "test",
            },
        ) as bif, mock.patch.object(
            cs,
            "compose_forcing_surrogate_design_matrix",
            side_effect=lambda fe, p, spinup, layout: (
                captured.update({"spinup": np.asarray(spinup).copy(), "params": np.asarray(p).copy()})
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
                parameters=params,
            )

        bif.assert_called()
        kwargs = bif.call_args.kwargs
        self.assertNotIn("spinup_member", kwargs)
        # positional: case, training_layout only (no spinup_member)
        self.assertEqual(len(bif.call_args.args), 2)
        np.testing.assert_allclose(captured["spinup"], [10.0, 20.0])
        np.testing.assert_allclose(captured["params"], params)
        self.assertEqual(out["spinup_source"], "elm_restart_mean")
        self.assertIsNone(out["member"])
        self.assertEqual(out["SR"].shape, (4,))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
