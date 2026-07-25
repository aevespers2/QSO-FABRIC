from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from qso_twins import (
    AppendOnlyLedger,
    DuplicateObservationError,
    IntegrityProof,
    Observation,
    ObservationType,
    QualityScore,
    StateMaterializer,
    Subject,
)


NOW = datetime(2026, 7, 24, 23, 59, tzinfo=timezone.utc)


def observation(observation_id: str, value: float, sequence: int) -> Observation:
    return Observation(
        observation_id=observation_id,
        twin_id="twin:checkout",
        source_id="source:otel-prod",
        source_type="telemetry",
        observation_type=ObservationType.STATE,
        subject=Subject(entity_type="service", entity_id="checkout-api"),
        event_time=NOW,
        ingestion_time=NOW,
        sequence=sequence,
        schema_ref="schema:qso.state.v1",
        payload={"field": "latency_p95_ms", "value": value, "unit": "ms"},
        provenance={"collector": "otel-gateway", "pipeline": ["validate"]},
        quality=QualityScore(1.0, 0.97, 0.99),
        integrity=IntegrityProof(
            content_hash="sha256:" + str(sequence).zfill(64),
            signature=f"signature-{sequence}",
            nonce=f"nonce-{sequence}",
            timestamp=NOW,
            authorized_source=True,
        ),
    )


class LedgerTests(unittest.TestCase):
    def test_append_builds_valid_hash_chain(self) -> None:
        ledger = AppendOnlyLedger()
        first = ledger.append(observation("obs-1", 100.0, 1))
        second = ledger.append(observation("obs-2", 125.0, 2))

        self.assertEqual(first.index, 0)
        self.assertEqual(second.index, 1)
        self.assertEqual(second.previous_hash, first.entry_hash)
        self.assertTrue(ledger.verify())

    def test_duplicate_observations_are_rejected(self) -> None:
        ledger = AppendOnlyLedger()
        item = observation("obs-1", 100.0, 1)
        ledger.append(item)
        with self.assertRaises(DuplicateObservationError):
            ledger.append(item)

    def test_observations_are_immutable(self) -> None:
        item = observation("obs-1", 100.0, 1)
        with self.assertRaises(FrozenInstanceError):
            item.twin_id = "twin:other"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            item.payload["value"] = 999.0  # type: ignore[index]


class MaterializerTests(unittest.TestCase):
    def test_replay_produces_latest_state(self) -> None:
        ledger = AppendOnlyLedger()
        ledger.extend(
            (
                observation("obs-1", 100.0, 1),
                observation("obs-2", 125.0, 2),
            )
        )

        state = StateMaterializer().materialize(ledger)
        entity = state[("twin:checkout", "service", "checkout-api")]

        self.assertEqual(entity.fields["latency_p95_ms"].value, 125.0)
        self.assertEqual(entity.last_ledger_index, 1)
        self.assertEqual(entity.fields["latency_p95_ms"].source_ids, ("source:otel-prod",))

    def test_replay_is_deterministic(self) -> None:
        ledger = AppendOnlyLedger()
        ledger.extend((observation("obs-1", 100.0, 1), observation("obs-2", 125.0, 2)))
        materializer = StateMaterializer()

        first = materializer.materialize(ledger)
        second = materializer.materialize(ledger)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
