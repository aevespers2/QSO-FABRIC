import json
import math
import unittest
from dataclasses import FrozenInstanceError, replace

from qso_runtime.emergence_garden import (
    EmergenceGarden,
    Evidence,
    GardenEvent,
    GrowthStage,
)


def supporting(index: int, *, reproducible: bool = False) -> Evidence:
    return Evidence(
        source=f"experiment-{index}",
        summary=f"supporting observation {index}",
        confidence=0.9,
        supports=True,
        reproducible=reproducible,
        evidence_id=f"e-{index}",
    )


class EmergenceGardenTests(unittest.TestCase):
    def test_growth_lifecycle_reaches_flower(self) -> None:
        garden = EmergenceGarden()
        idea = garden.plant(
            "Adaptive resonance",
            "Bounded resonance improves repair.",
            idea_id="idea-1",
        )
        self.assertIs(idea.stage, GrowthStage.SEED)

        for index in range(1, 9):
            idea = garden.add_evidence("idea-1", supporting(index, reproducible=index <= 3))

        self.assertIs(idea.stage, GrowthStage.FLOWER)
        self.assertGreater(idea.support_score, 0.8)
        self.assertTrue(garden.verify_ledger())

    def test_failed_path_is_preserved_and_can_be_revived(self) -> None:
        garden = EmergenceGarden()
        garden.plant("Rejected path", "A deliberately uncertain proposal.", idea_id="idea-2")
        garden.add_evidence(
            "idea-2",
            Evidence(
                source="falsification-run",
                summary="The predicted effect was absent.",
                confidence=0.95,
                supports=False,
                reproducible=True,
                evidence_id="negative-1",
            ),
        )

        idea = garden.mark_dead_branch("idea-2", "Falsified under the current protocol")
        self.assertIs(idea.stage, GrowthStage.DEAD_BRANCH)
        self.assertIsNotNone(idea.archived_reason)
        self.assertIn("idea-2", garden.ideas)
        self.assertEqual(garden.snapshot()["event_count"], 3)

        idea = garden.add_evidence("idea-2", supporting(2, reproducible=True))
        self.assertIs(idea.stage, GrowthStage.DEAD_BRANCH)

        idea = garden.revive("idea-2", "New instrumentation justifies retesting")
        self.assertIs(idea.stage, GrowthStage.SEED)
        self.assertIsNone(idea.archived_reason)
        self.assertTrue(garden.verify_ledger())

    def test_snapshot_is_deterministically_ordered_and_strict_json(self) -> None:
        garden = EmergenceGarden()
        garden.plant("Second", "Second hypothesis", idea_id="b")
        garden.plant("First", "First hypothesis", idea_id="a")
        snapshot = garden.snapshot()

        self.assertEqual(snapshot["schema"], "qso.emergence-garden/v1")
        self.assertEqual(snapshot["clock"], "deterministic-logical-sequence")
        self.assertEqual([item["idea_id"] for item in snapshot["ideas"]], ["a", "b"])
        self.assertNotEqual(snapshot["ledger_head"], "GENESIS")
        json.dumps(snapshot, allow_nan=False)

    def test_replay_without_explicit_ids_is_deterministic(self) -> None:
        def build() -> EmergenceGarden:
            garden = EmergenceGarden()
            idea = garden.plant(
                "Deterministic idea",
                "The same operation sequence yields the same state.",
                tags=("replay", "provenance"),
            )
            garden.add_evidence(
                idea.idea_id,
                Evidence(
                    source="fixture-1",
                    summary="The fixture was reproduced.",
                    confidence=0.8,
                    reproducible=True,
                ),
            )
            garden.add_note(idea.idea_id, "Retain this note in the ledger.")
            return garden

        first = build()
        second = build()
        self.assertEqual(first.snapshot(), second.snapshot())
        self.assertEqual(first.events, second.events)
        self.assertTrue(first.verify_ledger())
        self.assertTrue(second.verify_ledger())

    def test_returned_state_cannot_bypass_the_ledger(self) -> None:
        garden = EmergenceGarden()
        idea = garden.plant("Immutable idea", "External mutation must fail.", idea_id="immutable")
        with self.assertRaises(FrozenInstanceError):
            idea.stage = GrowthStage.FLOWER  # type: ignore[misc]
        with self.assertRaises(TypeError):
            garden.ideas["other"] = idea  # type: ignore[index]
        with self.assertRaises(TypeError):
            garden.events[0].payload["stage"] = "flower"  # type: ignore[index]
        self.assertIs(garden.ideas["immutable"].stage, GrowthStage.SEED)
        self.assertTrue(garden.verify_ledger())

    def test_evidence_identity_is_content_deterministic_and_duplicate_safe(self) -> None:
        first = Evidence("source", "summary", 0.75, reproducible=True)
        second = Evidence("source", "summary", 0.75, reproducible=True)
        self.assertEqual(first.evidence_id, second.evidence_id)

        garden = EmergenceGarden()
        idea = garden.plant("Duplicate evidence", "Duplicates must be rejected.")
        garden.add_evidence(idea.idea_id, first)
        with self.assertRaises(ValueError):
            garden.add_evidence(idea.idea_id, second)

    def test_invalid_types_and_non_finite_confidence_fail_closed(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Evidence("source", "summary", value)
        with self.assertRaises(TypeError):
            Evidence("source", "summary", True)
        with self.assertRaises(TypeError):
            Evidence("source", "summary", 0.5, supports=1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            EmergenceGarden().plant("title", "hypothesis", tags="not-a-tag-list")

    def test_revival_requires_a_reason(self) -> None:
        garden = EmergenceGarden()
        idea = garden.plant("Dormant", "Reasoned revival is required.")
        garden.set_dormant(idea.idea_id, "Paused")
        with self.assertRaises(ValueError):
            garden.revive(idea.idea_id, "   ")

    def test_ledger_detects_substitution(self) -> None:
        garden = EmergenceGarden()
        garden.plant("Ledger", "Substitution should invalidate the chain.", idea_id="ledger")
        event = garden.events[0]
        garden._events[0] = replace(event, event_hash="0" * 64)  # noqa: SLF001
        self.assertFalse(garden.verify_ledger())


if __name__ == "__main__":
    unittest.main()
