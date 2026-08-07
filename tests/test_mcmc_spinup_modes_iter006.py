"""Unit tests for Iter006 three-mode MCMC spinup wiring."""
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

from model_ELM import mcmc_spinup_modes as msm
from model_ELM.MCMC_forcing import run_forcing_surrogate_site


class ResolveSpinupModeTests(unittest.TestCase):
    def test_default_mean_spinup(self) -> None:
        self.assertEqual(
            msm.resolve_spinup_mode(spinup_mode=None, spinup_member=None),
            "mean_spinup",
        )

    def test_legacy_spinup_member_implies_member_restart(self) -> None:
        self.assertEqual(
            msm.resolve_spinup_mode(spinup_mode=None, spinup_member=1),
            "member_restart",
        )

    def test_explicit_modes(self) -> None:
        self.assertEqual(
            msm.resolve_spinup_mode(spinup_mode="mean_spinup", spinup_member=None),
            "mean_spinup",
        )
        self.assertEqual(
            msm.resolve_spinup_mode(spinup_mode="member_restart", spinup_member=2),
            "member_restart",
        )
        self.assertEqual(
            msm.resolve_spinup_mode(spinup_mode="coupled", spinup_member=None),
            "coupled",
        )

    def test_incompatible_flags_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            msm.resolve_spinup_mode(spinup_mode="mean_spinup", spinup_member=1)
        with self.assertRaises(ValueError):
            msm.resolve_spinup_mode(spinup_mode="member_restart", spinup_member=None)
        with self.assertRaises(ValueError):
            msm.resolve_spinup_mode(spinup_mode="coupled", spinup_member=1)
        with self.assertRaises(ValueError):
            msm.resolve_spinup_mode(spinup_mode="nope", spinup_member=None)

    def test_coupled_variant_default(self) -> None:
        self.assertEqual(msm.resolve_coupled_variant(None), "drop21_corr080")
        self.assertEqual(msm.resolve_coupled_variant("drop32"), "drop32")
        with self.assertRaises(ValueError):
            msm.resolve_coupled_variant("bad")


class PredictSrForModeTests(unittest.TestCase):
    def test_mean_spinup_delegates_to_offline(self) -> None:
        case = SimpleNamespace()
        params = np.arange(14, dtype=float)
        with mock.patch.object(
            msm,
            "predict_offline_sr",
            return_value={"SR": np.ones(3), "spinup_source": "elm_restart_mean"},
        ) as offline:
            out = msm.predict_sr_for_mode(
                case,
                mode="mean_spinup",
                forcing_artifact={"training_layout": {}},
                parameters=params,
            )
        offline.assert_called_once()
        self.assertEqual(out["spinup_mode"], "mean_spinup")

    def test_coupled_delegates_to_predict_coupled_sr(self) -> None:
        case = SimpleNamespace()
        params = np.arange(14, dtype=float)
        with mock.patch.object(
            msm,
            "predict_coupled_sr",
            return_value={
                "SR": np.ones(3),
                "spinup_source": "predicted",
                "spinup_variant": "drop21_corr080",
            },
        ) as coupled:
            out = msm.predict_sr_for_mode(
                case,
                mode="coupled",
                forcing_artifact={"training_layout": {}},
                parameters=params,
                spinup_artifact="/tmp/fake_spinup.pkl",
                coupled_variant="drop21_corr080",
            )
        coupled.assert_called_once()
        self.assertEqual(out["spinup_mode"], "coupled")


class CoupledForwardPathTests(unittest.TestCase):
    def test_run_forcing_surrogate_site_coupled_uses_predict_coupled_sr(self) -> None:
        case = SimpleNamespace(casename="FAKE")
        site_data = {
            "spinup_mode": "coupled",
            "case": case,
            "spinup_artifact": "/tmp/spinup.pkl",
            "forcing_artifact": "/tmp/forcing.pkl",
            "overlap_indices": np.asarray([0, 2]),
        }
        with mock.patch(
            "model_ELM.coupled_surrogate.predict_coupled_sr",
            return_value={"SR": np.asarray([10.0, 20.0, 30.0, 40.0])},
        ) as coupled:
            out = run_forcing_surrogate_site(site_data, np.arange(14, dtype=float), ["SR"])
        coupled.assert_called_once()
        np.testing.assert_allclose(out["SR"], [10.0, 30.0])

    def test_coupled_rejects_non_sr_vars(self) -> None:
        site_data = {
            "spinup_mode": "coupled",
            "case": SimpleNamespace(),
            "spinup_artifact": "/tmp/spinup.pkl",
            "forcing_artifact": "/tmp/forcing.pkl",
        }
        with self.assertRaises(ValueError):
            run_forcing_surrogate_site(site_data, np.arange(14, dtype=float), ["GPP", "SR"])


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
