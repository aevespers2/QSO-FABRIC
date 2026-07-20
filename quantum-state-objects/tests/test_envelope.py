from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "qso_validate.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("qso_validate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_validator()
        self.example = json.loads((ROOT / "examples" / "minimal" / "minimal.qso.json").read_text())

    def test_minimal_example_is_valid(self):
        self.assertEqual([], self.validator.validate(self.example))

    def test_missing_format_fails(self):
        del self.example["qso"]["format"]
        self.assertIn("missing qso.format", self.validator.validate(self.example))

    def test_invalid_mutation_class_fails(self):
        self.example["qso"]["mutation_class"] = "unbounded"
        self.assertIn("invalid qso.mutation_class", self.validator.validate(self.example))


if __name__ == "__main__":
    unittest.main()
