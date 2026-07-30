from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from predict_surrogate_spinup import _load_parameter_json_file


class ParameterJsonFileTests(unittest.TestCase):
    def test_loads_named_parameter_object(self) -> None:
        payload = {"k_l1": 0.5, "k_l2": 0.6}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "params.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(_load_parameter_json_file(str(path)), payload)

    def test_loads_positional_batch(self) -> None:
        payload = [[0.1, 0.2], [0.3, 0.4]]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "params_batch.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(_load_parameter_json_file(str(path)), payload)

    def test_rejects_inline_json_with_clear_error(self) -> None:
        inline = json.dumps({f"parameter_{i}": 0.123456789 for i in range(20)})
        with self.assertRaisesRegex(ValueError, "file path, not inline JSON"):
            _load_parameter_json_file(inline)

    def test_rejects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            with self.assertRaisesRegex(FileNotFoundError, "not found"):
                _load_parameter_json_file(str(missing))

    def test_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"k_l1": 0.5, "k_l1": 0.6}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate parameter"):
                _load_parameter_json_file(str(path))


if __name__ == "__main__":
    unittest.main()
