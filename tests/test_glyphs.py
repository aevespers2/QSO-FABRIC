from __future__ import annotations

import unittest

from qso_runtime.glyphs import Glyph, GlyphRegistry, Stroke, core_registry, glyph_from_mapping


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
        decoded = glyph_from_mapping(
            {
                "name": "signal",
                "meaning": "transmitted state",
                "family": "computational",
                "strokes": [{"primitive": "arc", "points": [[1, 3], [3, 1], [5, 3]]}],
            }
        )
        self.assertEqual("signal", decoded.name)
        self.assertEqual("qg:", decoded.glyph_id[:3])


if __name__ == "__main__":
    unittest.main()
