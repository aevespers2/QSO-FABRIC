from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from qso_twins import (  # noqa: E402
    IntegrityProof,
    Observation,
    ObservationType,
    QualityScore,
    StateStatus,
    StateValue,
    Subject,
)

UTC_NOW = datetime(2026, 7, 24, 20, 0, tzinfo=timezone.utc)
VALID_HASH = "sha256:" + "a" * 64


def integrity() -> IntegrityProof:
    return IntegrityProof(
        content_hash=VALID_HASH,
        signature="test-signature",
        nonce="test-nonce",
        timestamp=UTC_NOW,
        authorized_source=True,
    )


def quality() -> QualityScore:
    return QualityScore(0.9, 0.8, 0.7)


def observation(**overrides: object) -> Observation:
    values: dict[str, object] = {
        "observation_id": "obs:1",
        "twin_id": "twin:alpha",
        "source_id": "source:sensor-1",
        "source_type": "sensor",
        "observation_type": ObservationType.STATE,
        "subject": Subject("device", "device-1"),
        "event_time": UTC_NOW,
        "ingestion_time": UTC_NOW + timedelta(seconds=1),
        "payload": {"nested": {"samples": [1, 2, 3]}},
        "provenance": {"collector": "fixture", "pipeline": ["normalize"]},
        "quality": quality(),
        "integrity": integrity(),
        "sequence": 0,
        "schema_ref": "schema:test:v1",
    }
    values.update(overrides)
    return Observation(**values)  # type: ignore[arg-type]


class DynamicTwinModelTests(unittest.TestCase):
    def test_positive_observation_is_deeply_immutable(self) -> None:
        record = observation()
        self.assertEqual(record.payload["nested"]["samples"], (1, 2, 3))
        with self.assertRaises(TypeError):
            record.payload["new"] = "value"  # type: ignore[index]
        with self.assertRaises(TypeError):
            record.payload["nested"]["new"] = "value"  # type: ignore[index]

    def test_boolean_probabilities_are_rejected(self) -> None:
        for field_name in ("completeness", "reliability", "clock_confidence"):
            values = {"completeness": 0.5, "reliability": 0.5, "clock_confidence": 0.5}
            values[field_name] = True
            with self.subTest(field=field_name), self.assertRaises(ValueError):
                QualityScore(**values)
        with self.assertRaises(ValueError):
            StateValue(
                value=1,
                status=StateStatus.OBSERVED,
                valid_from=UTC_NOW,
                observed_at=UTC_NOW,
                confidence=False,
                source_ids=("source:a",),
            )

    def test_non_finite_probabilities_are_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                QualityScore(value, 0.5, 0.5)

    def test_raw_enum_strings_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            observation(observation_type="state")
        with self.assertRaises(ValueError):
            StateValue(
                value=1,
                status="observed",  # type: ignore[arg-type]
                valid_from=UTC_NOW,
                observed_at=UTC_NOW,
                confidence=0.5,
                source_ids=("source:a",),
            )

    def test_malformed_hash_and_false_authorization_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            IntegrityProof("sha256:x", "sig", "nonce", UTC_NOW, True)
        with self.assertRaises(ValueError):
            IntegrityProof(VALID_HASH, "sig", "nonce", UTC_NOW, 1)  # type: ignore[arg-type]

    def test_boolean_sequence_and_empty_source_type_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            observation(sequence=True)
        with self.assertRaises(ValueError):
            observation(source_type=" ")

    def test_naive_timestamps_are_rejected_with_value_error(self) -> None:
        naive = datetime(2026, 7, 24, 20, 0)
        with self.assertRaises(ValueError):
            observation(event_time=naive)
        with self.assertRaises(ValueError):
            IntegrityProof(VALID_HASH, "sig", "nonce", naive, True)

    def test_invalid_nested_payload_types_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            observation(payload={"bad": {1, 2, 3}})
        with self.assertRaises(ValueError):
            observation(payload={1: "non-string-key"})

    def test_state_value_source_and_interval_boundaries(self) -> None:
        with self.assertRaises(ValueError):
            StateValue(
                value=1,
                status=StateStatus.OBSERVED,
                valid_from=UTC_NOW,
                observed_at=UTC_NOW,
                confidence=0.5,
                source_ids="source:a",
            )
        with self.assertRaises(ValueError):
            StateValue(
                value=1,
                status=StateStatus.OBSERVED,
                valid_from=UTC_NOW,
                observed_at=UTC_NOW,
                confidence=0.5,
                source_ids=("bad",),
            )
        with self.assertRaises(ValueError):
            StateValue(
                value=1,
                status=StateStatus.OBSERVED,
                valid_from=UTC_NOW,
                observed_at=UTC_NOW,
                confidence=0.5,
                source_ids=("source:a",),
                valid_to=UTC_NOW - timedelta(seconds=1),
            )


if __name__ == "__main__":
    unittest.main()
