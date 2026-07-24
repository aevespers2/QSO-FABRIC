from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_interface_compatibility.py"
CORPUS_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "qso-interface-compatibility-v1.json"
SPEC = importlib.util.spec_from_file_location("validate_interface_compatibility", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


class InterfaceCompatibilityTests(unittest.TestCase):
    def test_canonical_corpus_validates(self) -> None:
        results = validator.validate_corpus(valid_corpus())
        self.assertEqual(len(results), 17)
        self.assertEqual(
            {r["interface"] for r in results if not r["reasons"]},
            validator.KNOWN_INTERFACES,
        )

    def test_duplicate_json_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate object key"):
            validator.load_json_bytes(b'{"a":1,"a":2}', "fixture")

    def test_nonfinite_number_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-finite"):
            validator.load_json_bytes(b'{"value":NaN}', "fixture")

    def test_overflowed_number_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-finite"):
            validator.load_json_bytes(b'{"value":1e999}', "fixture")

    def test_invalid_utf8_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "strict UTF-8"):
            validator.load_json_bytes(b'{"x":"\xff"}', "fixture")

    def test_unknown_top_level_field_rejected(self) -> None:
        data = valid_corpus()
        data["authority"] = "granted"
        with self.assertRaisesRegex(ValueError, "field mismatch"):
            validator.validate_corpus(data)

    def test_fact_order_drift_rejected(self) -> None:
        data = valid_corpus()
        data["fact_order"] = list(reversed(data["fact_order"]))
        with self.assertRaisesRegex(ValueError, "fact_order differs"):
            validator.validate_corpus(data)

    def test_reason_order_drift_rejected(self) -> None:
        data = valid_corpus()
        data["reason_order"] = list(reversed(data["reason_order"]))
        with self.assertRaisesRegex(ValueError, "reason_order differs"):
            validator.validate_corpus(data)

    def test_missing_fact_rejected(self) -> None:
        data = valid_corpus()
        del data["cases"][0]["facts"]["rollback_supported"]
        with self.assertRaisesRegex(ValueError, "field mismatch"):
            validator.validate_corpus(data)

    def test_nonboolean_fact_rejected(self) -> None:
        data = valid_corpus()
        data["cases"][0]["facts"]["evidence_bound"] = 1
        with self.assertRaisesRegex(ValueError, "must be boolean"):
            validator.validate_corpus(data)

    def test_duplicate_case_id_rejected(self) -> None:
        data = valid_corpus()
        duplicate = deepcopy(data["cases"][0])
        data["cases"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate case_id"):
            validator.validate_corpus(data)

    def test_known_interface_consistency_rejected(self) -> None:
        data = valid_corpus()
        data["cases"][0]["interface"] = "qso-unknown-interface"
        with self.assertRaisesRegex(ValueError, "unknown interface as known"):
            validator.validate_corpus(data)

    def test_disposition_drift_rejected(self) -> None:
        data = valid_corpus()
        data["cases"][2]["expected"]["disposition"] = "COMPATIBLE_PENDING_ARCHITECTURE_APPROVAL"
        with self.assertRaisesRegex(ValueError, "disposition drift"):
            validator.validate_corpus(data)

    def test_reason_drift_rejected(self) -> None:
        data = valid_corpus()
        data["cases"][2]["expected"]["reasons"] = ["PROTOCOL_MISMATCH"]
        with self.assertRaisesRegex(ValueError, "reason drift"):
            validator.validate_corpus(data)

    def test_reason_order_within_case_rejected(self) -> None:
        data = valid_corpus()
        data["cases"][-1]["expected"]["reasons"] = list(
            reversed(data["cases"][-1]["expected"]["reasons"])
        )
        with self.assertRaisesRegex(ValueError, "canonical order"):
            validator.validate_corpus(data)

    def test_missing_reason_coverage_rejected(self) -> None:
        data = valid_corpus()
        data["cases"] = [
            case
            for case in data["cases"]
            if case["case_id"] != "authority-promotion-detected"
        ]
        data["cases"][-1]["facts"]["authority_promotion_absent"] = True
        data["cases"][-1]["expected"]["reasons"].remove("AUTHORITY_PROMOTION_DETECTED")
        with self.assertRaisesRegex(ValueError, "lacks reason coverage"):
            validator.validate_corpus(data)

    def test_cli_failure_is_structured_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"version":NaN}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertIs(payload["valid"], False)
        self.assertIn("non-finite", payload["error"])


if __name__ == "__main__":
    unittest.main()
