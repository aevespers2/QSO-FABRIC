from __future__ import annotations

import math
import unittest

from qso_runtime.glyphs import Glyph, GlyphRegistry, Stroke, core_registry, glyph_from_mapping


VALID_GLYPH = {
    "name": "signal",
    "meaning": "transmitted state",
    "family": "computational",
    "strokes": [{"primitive": "arc", "points": [[1, 3], [3, 1], [5, 3]]}],
}


class GlyphTests(unittest.TestCase):
    def test_core_registry_is_deterministic(self) -> None:
        first = core_registry().manifest()
        second = core_registry().manifest()
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
        self.assertEqual(8, len(first["glyphs"]))

    def test_composition_carries_semantics(self) -> None:
        registry = core_registry()
        historian = registry.compose("historian", "observer joined with memory", ("observer", "memory"))
        self.assertEqual(("observer", "memory"), historian.components)
        self.assertIn("agent", historian.tags)
        self.assertGreater(historian.abstraction, registry.get("observer").abstraction)
        self.assertTrue(historian.glyph_id.startswith("qg:"))

    def test_conflicting_registration_fails(self) -> None:
        registry = GlyphRegistry()
        original = Glyph("x", "first", "mathematical", (Stroke("dot", ((3, 3),)),))
        changed = Glyph("x", "second", "mathematical", (Stroke("dot", ((3, 3),)),))
        registry.register(original)
        with self.assertRaises(ValueError):
            registry.register(changed)

    def test_grid_boundary_is_enforced(self) -> None:
        with self.assertRaises(ValueError):
            Stroke("dot", ((7, 0),))

    def test_mapping_decoder_validates(self) -> None:
        decoded = glyph_from_mapping(VALID_GLYPH)
        self.assertEqual("signal", decoded.name)
        self.assertEqual("qg:", decoded.glyph_id[:3])

    def test_non_finite_certainty_is_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                glyph_from_mapping(VALID_GLYPH | {"certainty": value})

    def test_boolean_numeric_fields_are_rejected(self) -> None:
        cases = (
            VALID_GLYPH | {"abstraction": True},
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": [[True, 3]]}]},
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": [[3, 3]], "weight": True}]},
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": [[3, 3]], "rotation": False}]},
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                glyph_from_mapping(case)

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            glyph_from_mapping(VALID_GLYPH | {"authority": "execute"})
        with self.assertRaises(ValueError):
            glyph_from_mapping(
                VALID_GLYPH
                | {"strokes": [{"primitive": "dot", "points": [[3, 3]], "execute": True}]}
            )

    def test_non_mapping_strokes_are_not_silently_dropped(self) -> None:
        with self.assertRaises(ValueError):
            glyph_from_mapping(VALID_GLYPH | {"strokes": ["not-a-stroke"]})

    def test_string_collections_are_rejected(self) -> None:
        for field in ("tags", "components"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                glyph_from_mapping(VALID_GLYPH | {field: "abc"})
        with self.assertRaises(ValueError):
            core_registry().compose("bad", "bad composition", "observer")

    def test_scalar_fields_are_not_coerced_to_strings(self) -> None:
        for field, value in (("name", 1), ("meaning", object()), ("family", 7), ("phoneme", 2)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                glyph_from_mapping(VALID_GLYPH | {field: value})

    def test_malformed_points_fail_closed(self) -> None:
        cases = (
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": [[3]]}]},
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": ["33"]}]},
            VALID_GLYPH | {"strokes": [{"primitive": "dot", "points": []}]},
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                glyph_from_mapping(case)

    def test_duplicate_labels_and_components_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            glyph_from_mapping(VALID_GLYPH | {"tags": ["signal", "signal"]})
        with self.assertRaises(ValueError):
            core_registry().compose("duplicate", "duplicate source", ("observer", "observer"))

    def test_direct_dataclass_inputs_preserve_strict_types(self) -> None:
        with self.assertRaises(ValueError):
            Stroke("dot", ((3, 3),), weight=True)
        with self.assertRaises(ValueError):
            Glyph("bad", "non-finite", "computational", (Stroke("dot", ((3, 3),)),), certainty=math.nan)
        with self.assertRaises(ValueError):
            Glyph("bad", "boolean abstraction", "computational", (Stroke("dot", ((3, 3),)),), abstraction=False)


if __name__ == "__main__":
    unittest.main()
