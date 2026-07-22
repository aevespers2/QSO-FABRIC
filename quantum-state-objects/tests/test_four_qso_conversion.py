from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from convert_four_qso_report import canonical_bytes, convert  # noqa: E402


class FourQSOConversionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = {
            "objective": "Test deterministic conversion",
            "base_seed": 2987,
            "limits": {
                "max_rounds": 1,
                "max_messages_per_qso": 2,
                "max_message_chars": 600,
                "max_runtime_seconds": 10.0,
            },
            "ledger_valid": True,
            "event_count": 1,
            "final_event_hash": "abc123",
            "qsos": {
                "atlas": {
                    "role": "mathematical structure",
                    "observations": ["objective received"],
                    "inferences": ["use invariants"],
                    "contradictions": [],
                    "final_proposal": "bounded graph",
                    "freeze_points": ["final:def456"],
                }
            },
            "events": [
                {
                    "seq": 0,
                    "kind": "experiment_started",
                    "actor": "fabric",
                    "payload": {"objective": "Test deterministic conversion"},
                    "previous_hash": "GENESIS",
                    "event_hash": "abc123",
                }
            ],
        }

    def test_conversion_splits_report_and_provenance(self) -> None:
        qreport, qprov = convert(
            self.report,
            source_path="artifacts/four_qso_report.json",
            source_hash="sha256:" + "1" * 64,
            created_at="2026-07-22T00:00:00Z",
        )
        self.assertEqual("QSO-REPORT", qreport["qso"]["format"])
        self.assertEqual("QSO-PROVENANCE", qprov["qso"]["format"])
        self.assertEqual(self.report["events"], qprov["payload"]["events"])
        self.assertNotIn("events", qreport["payload"])

    def test_conversion_is_deterministic(self) -> None:
        arguments = {
            "source_path": "artifacts/four_qso_report.json",
            "source_hash": "sha256:" + "2" * 64,
            "created_at": "2026-07-22T00:00:00Z",
        }
        first = convert(copy.deepcopy(self.report), **arguments)
        second = convert(copy.deepcopy(self.report), **arguments)
        self.assertEqual(first, second)

    def test_content_hashes_bind_canonical_objects(self) -> None:
        qreport, qprov = convert(
            self.report,
            source_path="artifacts/four_qso_report.json",
            source_hash="sha256:" + "3" * 64,
            created_at="2026-07-22T00:00:00Z",
        )
        for value in (qreport, qprov):
            expected = value["qso"]["content_hash"]
            clone = copy.deepcopy(value)
            clone["qso"].pop("content_hash")
            actual = "sha256:" + hashlib.sha256(canonical_bytes(clone)).hexdigest()
            self.assertEqual(expected, actual)

    def test_rejects_incomplete_or_inconsistent_reports(self) -> None:
        incomplete = dict(self.report)
        incomplete.pop("events")
        with self.assertRaises(ValueError):
            convert(
                incomplete,
                source_path="missing.json",
                source_hash="sha256:" + "4" * 64,
                created_at="2026-07-22T00:00:00Z",
            )

        inconsistent = copy.deepcopy(self.report)
        inconsistent["event_count"] = 2
        with self.assertRaises(ValueError):
            convert(
                inconsistent,
                source_path="bad.json",
                source_hash="sha256:" + "5" * 64,
                created_at="2026-07-22T00:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
