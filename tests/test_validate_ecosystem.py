from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_ecosystem.py"
SPEC = importlib.util.spec_from_file_location("validate_ecosystem", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_manifest() -> dict:
    return {
        "schema_version": "1.0.0",
        "component": "QSO-FABRIC",
        "version": "0.1.0",
        "purpose": "Provide a deterministic bounded coordination fabric with retained evidence.",
        "conformance": {
            "claimed_level": 1,
            "evidence_path": "artifacts/conformance",
        },
        "runtime_bounds": {
            "max_seconds": 300,
            "max_rounds": 16,
            "max_messages": 256,
            "max_memory_mb": 2048,
            "network_default": "deny",
        },
        "capabilities": [
            {
                "name": "bounded-message-exchange",
                "authority": "execute",
                "default": "allow",
                "constraints": ["round limit", "deterministic seed"],
            }
        ],
        "interfaces": [
            {
                "name": "qso-event-ledger",
                "role": "producer",
                "protocol": "append-only-json",
                "schema_version": "1.0.0",
                "idempotent": True,
                "retry_limit": 0,
            }
        ],
        "governance": {
            "review_component": "Jacob Redmond",
            "deprecated_aliases": ["Aequitas"],
            "human_override": True,
            "audit_log": True,
        },
    }


def valid_schema() -> dict:
    path = Path(__file__).resolve().parents[1] / "schemas" / "qso-manifest.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


class EcosystemValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "README.md").write_text("# Test\n", encoding="utf-8")
        workflow = self.root / ".github" / "workflows"
        workflow.mkdir(parents=True)
        (workflow / "ecosystem-conformance.yml").write_text("name: test\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def validate(self, data: dict) -> list[str]:
        return validator.validate(data, repository_root=self.root)

    def test_valid_manifest_and_schema(self) -> None:
        validator.validate_schema_contract(valid_schema())
        checks = self.validate(valid_manifest())
        self.assertIn("interface-declarations", checks)
        self.assertIn("l1-reproducibility-artifacts", checks)

    def test_duplicate_json_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate object key"):
            validator.load_json_bytes(b'{"a":1,"a":2}', "fixture")

    def test_nonfinite_number_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-finite"):
            validator.load_json_bytes(b'{"value":NaN}', "fixture")

    def test_unknown_top_level_field_rejected(self) -> None:
        data = valid_manifest()
        data["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            self.validate(data)

    def test_unknown_nested_field_rejected(self) -> None:
        data = valid_manifest()
        data["runtime_bounds"]["unexpected"] = 1
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            self.validate(data)

    def test_boolean_claimed_level_rejected(self) -> None:
        data = valid_manifest()
        data["conformance"]["claimed_level"] = True
        with self.assertRaisesRegex(ValueError, "integer 0..5"):
            self.validate(data)

    def test_boolean_runtime_bound_rejected(self) -> None:
        data = valid_manifest()
        data["runtime_bounds"]["max_seconds"] = True
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.validate(data)

    def test_unsafe_evidence_path_rejected(self) -> None:
        data = valid_manifest()
        data["conformance"]["evidence_path"] = "../outside"
        with self.assertRaisesRegex(ValueError, "safe repository-relative"):
            self.validate(data)

    def test_duplicate_capability_name_rejected(self) -> None:
        data = valid_manifest()
        data["capabilities"].append(deepcopy(data["capabilities"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate capability"):
            self.validate(data)

    def test_non_object_capability_rejected(self) -> None:
        data = valid_manifest()
        data["capabilities"] = ["execute-everything"]
        with self.assertRaisesRegex(ValueError, "must be an object"):
            self.validate(data)

    def test_unbounded_default_allow_execute_rejected(self) -> None:
        data = valid_manifest()
        data["capabilities"][0]["constraints"] = ["human review"]
        with self.assertRaisesRegex(ValueError, "lacks a bounded constraint"):
            self.validate(data)

    def test_empty_interfaces_rejected(self) -> None:
        data = valid_manifest()
        data["interfaces"] = []
        with self.assertRaisesRegex(ValueError, "non-empty array"):
            self.validate(data)

    def test_duplicate_interface_name_rejected(self) -> None:
        data = valid_manifest()
        data["interfaces"].append(deepcopy(data["interfaces"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate interface"):
            self.validate(data)

    def test_boolean_retry_limit_rejected(self) -> None:
        data = valid_manifest()
        data["interfaces"][0]["retry_limit"] = False
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            self.validate(data)

    def test_nonboolean_idempotent_rejected(self) -> None:
        data = valid_manifest()
        data["interfaces"][0]["idempotent"] = 1
        with self.assertRaisesRegex(ValueError, "must be boolean"):
            self.validate(data)

    def test_weakened_governance_rejected(self) -> None:
        data = valid_manifest()
        data["governance"]["human_override"] = False
        with self.assertRaisesRegex(ValueError, "human override"):
            self.validate(data)

    def test_schema_required_field_drift_rejected(self) -> None:
        schema = valid_schema()
        schema["required"].remove("interfaces")
        with self.assertRaisesRegex(ValueError, "required-field set differs"):
            validator.validate_schema_contract(schema)

    def test_invalid_utf8_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "strict UTF-8"):
            validator.load_json_bytes(b'{"x":"\xff"}', "fixture")

    def test_missing_l1_workflow_rejected(self) -> None:
        (self.root / ".github" / "workflows" / "ecosystem-conformance.yml").unlink()
        with self.assertRaisesRegex(ValueError, "L1 requires ecosystem-conformance"):
            self.validate(valid_manifest())

    def test_cli_failure_is_structured_json(self) -> None:
        manifest_path = self.root / "qso.manifest.json"
        schema_path = self.root / "schema.json"
        manifest_path.write_text('{"schema_version":NaN}', encoding="utf-8")
        schema_path.write_text(json.dumps(valid_schema()), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), str(manifest_path), str(schema_path)],
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
