from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import xarray as xr

from model_ELM.load_obs_nc import (
    load_observations_strict_from_nc,
    load_observations_with_time_from_nc,
)


class StrictObservationLoaderTests(unittest.TestCase):
    def _write(self, path: Path, *, duplicate: bool = False, include_error: bool = True) -> None:
        time = np.array(
            ["2019-01-01T00:15", "2019-01-01T01:15", "2019-01-01T02:15"],
            dtype="datetime64[ns]",
        )
        if duplicate:
            time[2] = time[1]
        data_vars = {"SR": ("time", np.array([-1.0e-5, 0.0, 2.0e-5]))}
        if include_error:
            data_vars["SR_err"] = ("time", np.array([1.0e-6, np.nan, 2.0e-6]))
        ds = xr.Dataset(data_vars, coords={"time": time})
        ds["SR"].attrs["units"] = "gC/m^2/s"
        if include_error:
            ds["SR_err"].attrs["units"] = "gC/m^2/s"
        ds["time"].encoding.update({"calendar": "gregorian"})
        ds.to_netcdf(path)

    def test_strict_preserves_negative_and_uses_explicit_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obs.nc"
            self._write(path)
            payload = load_observations_strict_from_nc(
                str(path),
                ["SR"],
                {"SR": "SR_err"},
                error_fallback="relative_10_percent",
                absolute_floor=0.05,
                target_calendar="noleap",
                floor_to_hour=True,
            )
            self.assertLess(payload["obs"]["SR"][0], 0.0)
            self.assertEqual(payload["error_source"]["SR"][0], "configured")
            self.assertEqual(payload["error_source"]["SR"][1], "relative_10_percent")
            self.assertEqual(payload["obs_err"]["SR"][1], 0.05)
            self.assertEqual(len(payload["time"]), 3)

    def test_strict_missing_configured_error_fails_without_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obs.nc"
            self._write(path, include_error=False)
            with self.assertRaises(KeyError):
                load_observations_strict_from_nc(str(path), ["SR"], {"SR": "SR_err"})

    def test_strict_rejects_duplicate_normalized_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obs.nc"
            self._write(path, duplicate=True)
            with self.assertRaises(ValueError):
                load_observations_strict_from_nc(
                    str(path),
                    ["SR"],
                    {"SR": "SR_err"},
                    error_fallback="relative_10_percent",
                    absolute_floor=0.05,
                    floor_to_hour=True,
                )

    def test_legacy_loader_retains_historical_negative_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obs.nc"
            self._write(path)
            payload = load_observations_with_time_from_nc(
                str(path), ["SR"], {"SR": "SR_err"}
            )
            self.assertEqual(payload["obs"]["SR"][0], -9999.0)

    def test_strict_removes_february_29_during_noleap_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "leap.nc"
            time = np.array(["2020-02-28T23:00", "2020-02-29T00:00", "2020-03-01T00:00"], dtype="datetime64[ns]")
            ds = xr.Dataset({"SR": ("time", [1e-5, 2e-5, 3e-5])}, coords={"time": time})
            ds.SR.attrs["units"] = "gC/m^2/s"
            ds.time.encoding["calendar"] = "gregorian"
            ds.to_netcdf(path)
            payload = load_observations_strict_from_nc(str(path), ["SR"], target_calendar="noleap")
            self.assertEqual(len(payload["time"]), 2)

    def test_strict_rejects_unsorted_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsorted.nc"
            time = np.array(["2019-01-01T00:00", "2019-01-01T02:00", "2019-01-01T01:00"], dtype="datetime64[ns]")
            ds = xr.Dataset({"SR": ("time", [1e-5, 2e-5, 3e-5])}, coords={"time": time})
            ds.SR.attrs["units"] = "gC/m^2/s"
            ds.to_netcdf(path)
            with self.assertRaises(ValueError):
                load_observations_strict_from_nc(str(path), ["SR"], target_calendar=None)

    def test_strict_rejects_dimension_and_length_mismatch_without_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shape.nc"
            time = np.array(["2019-01-01T00:00", "2019-01-01T01:00", "2019-01-01T02:00"], dtype="datetime64[ns]")
            ds = xr.Dataset(
                {"SR": ("time", [1e-5, 2e-5, 3e-5]), "SR_err": ("err_time", [1e-6, 2e-6])},
                coords={"time": time, "err_time": [0, 1]},
            )
            ds.SR.attrs["units"] = "gC/m^2/s"
            ds.SR_err.attrs["units"] = "gC/m^2/s"
            ds.to_netcdf(path)
            with self.assertRaises(ValueError):
                load_observations_strict_from_nc(str(path), ["SR"], {"SR": "SR_err"}, target_calendar=None)

    def test_strict_rejects_unknown_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "units.nc"
            self._write(path)
            with xr.open_dataset(path) as opened:
                ds = opened.load()
            ds.SR.attrs["units"] = "bananas"
            ds.to_netcdf(path, mode="w")
            with self.assertRaises(ValueError):
                load_observations_strict_from_nc(str(path), ["SR"], target_calendar=None)

    def test_strict_rejects_undecodable_calendar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "calendar.nc"
            ds = xr.Dataset({"SR": ("time", [1e-5, 2e-5])}, coords={"time": [0.0, 1.0]})
            ds.SR.attrs["units"] = "gC/m^2/s"
            ds.to_netcdf(path)
            with self.assertRaises(ValueError):
                load_observations_strict_from_nc(str(path), ["SR"])


if __name__ == "__main__":
    unittest.main()
