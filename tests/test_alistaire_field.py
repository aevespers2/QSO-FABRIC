from __future__ import annotations

import math
import unittest

from qso_runtime.alistaire_field import (
    AlistaireField,
    AlistaireLimits,
    ConstitutionalViolation,
    ConstitutionalWeights,
    Possibility,
)


class AlistaireFieldTests(unittest.TestCase):
    def test_observation_is_bounded_and_hash_chained(self) -> None:
        field = AlistaireField()
        first_hash = field.state.state_hash
        memory = field.observe("A bounded observation", semantic_tags=("qso", "field"))
        self.assertTrue(memory.memory_id.startswith("mem-"))
        self.assertNotEqual(first_hash, field.state.state_hash)
        self.assertEqual(first_hash, field.state.previous_hash)
        self.assertEqual(1, len(field.state.memories))

    def test_memory_affinity_rewards_shared_structure(self) -> None:
        field = AlistaireField()
        left = field.observe("first", semantic_tags=("truth", "repair"), relational_relevance=0.8)
        right = field.observe("second", semantic_tags=("truth", "repair"), relational_relevance=0.8)
        unrelated = field.observe("third", semantic_tags=("noise",), relational_relevance=0.0)
        self.assertGreater(field.memory_affinity(left, right), field.memory_affinity(left, unrelated))

    def test_constitutional_values_cannot_be_adapted_as_laws(self) -> None:
        field = AlistaireField()
        with self.assertRaises(ConstitutionalViolation):
            field.adapt_laws({"constitutional_truth": -1.0})

    def test_constitutional_weights_cannot_be_replaced(self) -> None:
        with self.assertRaises(ConstitutionalViolation):
            AlistaireField(weights=ConstitutionalWeights(truth=0.0))

    def test_coercion_ceiling_can_only_be_tightened(self) -> None:
        stricter = AlistaireField(limits=AlistaireLimits(coercion_ceiling=0.01))
        self.assertEqual(0.01, stricter.limits.coercion_ceiling)
        with self.assertRaises(ConstitutionalViolation):
            AlistaireField(limits=AlistaireLimits(coercion_ceiling=0.5))

    def test_unknown_adaptive_law_is_rejected(self) -> None:
        field = AlistaireField()
        with self.assertRaises(ConstitutionalViolation):
            field.adapt_laws({"coercion_discount": 1.0})

    def test_coercive_action_is_rejected(self) -> None:
        field = AlistaireField()
        field.set_possibilities(
            [
                Possibility(
                    action_id="support",
                    description="Offer a reversible, evidence-labelled proposal",
                    truth=0.9,
                    clarity=0.9,
                    autonomy=1.0,
                    repair=0.7,
                ),
                Possibility(
                    action_id="control",
                    description="Force the preferred outcome",
                    truth=1.0,
                    clarity=1.0,
                    autonomy=0.0,
                    coercion=0.8,
                ),
            ]
        )
        decision = field.decide()
        self.assertEqual("support", decision.selected_action_id)
        self.assertEqual("coercion ceiling exceeded", decision.rejected["control"])

    def test_out_of_range_scoring_input_is_rejected(self) -> None:
        field = AlistaireField()
        for possibility in (
            Possibility(action_id="negative-harm", description="invalid", harm=-1.0),
            Possibility(action_id="inflated-truth", description="invalid", truth=2.0),
            Possibility(action_id="nan-risk", description="invalid", risk=math.nan),
        ):
            with self.subTest(possibility=possibility.action_id):
                with self.assertRaises(ValueError):
                    field.set_possibilities([possibility])

    def test_non_json_metadata_is_rejected(self) -> None:
        field = AlistaireField()
        with self.assertRaises(ValueError):
            field.set_possibilities(
                [
                    Possibility(
                        action_id="bad-metadata",
                        description="invalid",
                        metadata={"opaque": object()},
                    )
                ]
            )

    def test_possibility_overflow_fails_instead_of_truncating(self) -> None:
        limits = AlistaireLimits(max_possibilities=2)
        field = AlistaireField(limits=limits)
        possibilities = [
            Possibility(action_id=f"action-{index}", description="bounded")
            for index in range(3)
        ]
        with self.assertRaises(ValueError):
            field.set_possibilities(possibilities)
        self.assertEqual([], field.state.possibilities)

    def test_decision_is_deterministic_under_ties(self) -> None:
        field = AlistaireField()
        field.set_possibilities(
            [
                Possibility(action_id="beta", description="B", truth=0.5, autonomy=0.5),
                Possibility(action_id="alpha", description="A", truth=0.5, autonomy=0.5),
            ]
        )
        self.assertEqual("alpha", field.decide().selected_action_id)

    def test_contradictions_are_preserved_not_erased(self) -> None:
        field = AlistaireField()
        field.register_contradiction(
            "claim-a",
            "claim-b",
            degree=0.8,
            distortion_risk=0.4,
            suppression_risk=0.6,
        )
        self.assertGreater(field.contradiction_energy(), 0.0)
        self.assertEqual(1, len(field.state.contradictions))

    def test_non_finite_intent_and_law_updates_are_rejected(self) -> None:
        field = AlistaireField()
        with self.assertRaises(ValueError):
            field.update_intent({"repair": math.inf})
        with self.assertRaises(ValueError):
            field.adapt_laws({"repair_preference": math.nan})


if __name__ == "__main__":
    unittest.main()
