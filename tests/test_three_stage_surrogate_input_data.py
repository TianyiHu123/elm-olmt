from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from development.three_stage_surrogate.tools import prepare_surrogate_input_data as prep


class ThreeStageSurrogateInputDataTests(unittest.TestCase):
    def test_canonical_no_leap_axis(self) -> None:
        keys = prep.canonical_time_keys()
        self.assertEqual(len(keys), 61320)
        self.assertEqual(keys[0], (2018, 1, 1, 0))
        self.assertEqual(keys[-1], (2024, 12, 31, 23))
        self.assertNotIn((2020, 2, 29, 0), keys)
        self.assertNotIn((2024, 2, 29, 0), keys)

    def test_month_inventory(self) -> None:
        names = prep.expected_month_names()
        self.assertEqual(len(names), 84)
        self.assertEqual(names[0], "2018-01.nc")
        self.assertEqual(names[-1], "2024-12.nc")

    def test_split_is_locked_and_complete(self) -> None:
        split = prep.make_split(2026)
        development = split["development_member_ids_numeric"]
        fixed = split["fixed_test_member_ids_numeric"]
        self.assertEqual(len(development), 819)
        self.assertEqual(len(fixed), 205)
        self.assertFalse(set(development) & set(fixed))
        self.assertEqual(set(development) | set(fixed), {f"g{i:05d}" for i in range(1, 1025)})
        expected_first = min(
            (hashlib.sha256(f"three-stage-surrogate-v1|2026|g{i:05d}".encode()).hexdigest(), f"g{i:05d}")
            for i in range(1, 1025)
        )[1]
        self.assertEqual(split["fixed_test_member_ids_ranked"][0], expected_first)

    def test_hourly_aggregation_uses_exact_timestamp_groups(self) -> None:
        hour_keys = [(2018, 1, 1, 0), (2018, 1, 1, 0), (2018, 1, 1, 1)]
        full_keys = [(2018, 1, 1, 0, 0, 0), (2018, 1, 1, 0, 30, 0), (2018, 1, 1, 1, 0, 0)]
        raw = {"TBOT": np.asarray([2.0, 4.0, 8.0], dtype=np.float32)}
        result = prep.aggregate_hourly_values(hour_keys, full_keys, raw, [(2018, 1, 1, 0), (2018, 1, 1, 1)])
        np.testing.assert_array_equal(result["TBOT"], np.asarray([3.0, 8.0], dtype=np.float64))

    def test_publication_link_is_idempotent_only_for_same_artifact(self) -> None:
        from development.three_stage_surrogate.tools import validate_surrogate_input_data as validator

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            source.write_text("locked\n", encoding="utf-8")
            self.assertEqual(validator.link_atomically_or_accept(source, destination), "linked")
            self.assertEqual(validator.link_atomically_or_accept(source, destination), "accepted_existing_hardlink")
            replacement = root / "replacement"
            replacement.write_text("different\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validator.link_atomically_or_accept(replacement, destination)

    def test_parameter_netcdf_named_variables_and_storage_contract(self) -> None:
        names = [f"p{i}" for i in range(18)]
        values = np.arange(1024 * 18, dtype=np.float64).reshape(1024, 18)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "parameters.nc"
            prep.write_parameters(path, names, values, {"fixture": "0" * 64})
            with Dataset(str(path), "r") as dataset:
                self.assertEqual(dataset.parameter_order.split(","), names)
                self.assertNotIn("parameter", dataset.dimensions)
                self.assertEqual(len(dataset.dimensions["member"]), 1024)
                for index, name in enumerate(names):
                    self.assertEqual(dataset.variables[name].dimensions, ("member",))
                    self.assertEqual(dataset.variables[name].chunking(), [256])
                    filters = dataset.variables[name].filters()
                    self.assertTrue(filters["zlib"])
                    self.assertTrue(filters["shuffle"])
                    self.assertEqual(filters["complevel"], 4)
                    np.testing.assert_array_equal(dataset.variables[name][:], values[:, index])


if __name__ == "__main__":
    unittest.main()
