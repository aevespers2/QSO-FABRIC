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
        self.example = json.loads(
            (ROOT / "examples" / "minimal" / "minimal.qso.json").read_text(
                encoding="utf-8"
            )
        )

    def rehash(self):
        self.example["qso"]["content_hash"] = (
            self.validator.compute_sha256_content_hash(self.example)
        )

    def test_minimal_example_is_valid(self):
        self.assertEqual([], self.validator.validate(self.example))

    def test_mutation_example_is_valid(self):
        mutation = json.loads(
            (ROOT / "examples" / "mutation" / "state-change.qmut.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual([], self.validator.validate(mutation))

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: qso"):
            self.validator.strict_object([("qso", {}), ("qso", {})])

    def test_missing_format_fails(self):
        del self.example["qso"]["format"]
        self.rehash()
        self.assertIn("missing qso.format", self.validator.validate(self.example))

    def test_invalid_mutation_class_fails(self):
        self.example["qso"]["mutation_class"] = "unbounded"
        self.rehash()
        self.assertIn(
            "invalid qso.mutation_class", self.validator.validate(self.example)
        )

    def test_wrong_format_type_fails_closed(self):
        self.example["qso"]["format"] = 7
        self.rehash()
        self.assertIn(
            "qso.format must be a string", self.validator.validate(self.example)
        )

    def test_invalid_timestamp_fails(self):
        self.example["qso"]["created_at"] = "not-a-time"
        self.rehash()
        self.assertIn("invalid qso.created_at", self.validator.validate(self.example))

    def test_placeholder_hash_fails(self):
        self.example["qso"]["content_hash"] = "sha256:" + ("0" * 64)
        self.assertIn(
            "qso.content_hash must not be a placeholder digest",
            self.validator.validate(self.example),
        )

    def test_payload_tampering_fails_integrity(self):
        self.example["payload"]["entrypoints"].append("bootstrap")
        self.assertIn(
            "qso.content_hash does not match canonical content",
            self.validator.validate(self.example),
        )

    def test_core_manifest_is_required(self):
        del self.example["payload"]["manifest"]
        self.rehash()
        self.assertIn(
            "missing payload.manifest", self.validator.validate(self.example)
        )

    def test_reference_hash_placeholder_fails(self):
        self.example["payload"]["identity"]["content_hash"] = "sha256:" + ("0" * 64)
        self.rehash()
        self.assertIn(
            "payload.identity.content_hash must not be a placeholder digest",
            self.validator.validate(self.example),
        )

    def test_duplicate_reference_ids_fail(self):
        duplicate = dict(self.example["payload"]["identity"])
        self.example["payload"]["components"] = [duplicate]
        self.rehash()
        self.assertIn(
            "duplicate QSO reference object_id: qso:identity:example-minimal",
            self.validator.validate(self.example),
        )

    def test_unsupported_hash_algorithm_fails_closed(self):
        self.example["qso"]["content_hash"] = "blake3:" + ("1" * 64)
        self.assertIn(
            "unsupported qso.content_hash algorithm: blake3",
            self.validator.validate(self.example),
        )


if __name__ == "__main__":
    unittest.main()
