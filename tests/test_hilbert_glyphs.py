from __future__ import annotations

import math
import unittest

from qso_runtime.hilbert_glyphs import (
    ComplexAmplitude,
    HilbertScene,
    HilbertSpace,
    LinearOperator,
    StateVector,
    qubit_scene,
)


class HilbertGlyphTests(unittest.TestCase):
    def test_equal_superposition_projection_is_deterministic(self) -> None:
        amplitude = 1.0 / math.sqrt(2.0)
        scene = qubit_scene()
        scene.add_state(StateVector("|+>", "H_qubit", (ComplexAmplitude(amplitude), ComplexAmplitude(amplitude))))
        first = scene.projection()
        second = scene.projection()
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
        superposition_edges = [edge for edge in first["edges"] if edge["relation"] == "superposition"]
        self.assertEqual(2, len(superposition_edges))
        self.assertTrue(all(math.isclose(edge["magnitude"], amplitude) for edge in superposition_edges))

    def test_inner_product_encodes_orthogonality(self) -> None:
        scene = qubit_scene()
        scene.add_state(StateVector("|0>", "H_qubit", (ComplexAmplitude(1.0), ComplexAmplitude(0.0))))
        scene.add_state(StateVector("|1>", "H_qubit", (ComplexAmplitude(0.0), ComplexAmplitude(1.0))))
        overlap = scene.inner_product("|0>", "|1>")
        self.assertEqual(0.0, overlap.magnitude_squared)

    def test_normalization_is_enforced(self) -> None:
        with self.assertRaises(ValueError):
            StateVector("bad", "H", (ComplexAmplitude(1.0), ComplexAmplitude(1.0)))

    def test_infinite_space_requires_explicit_displayed_basis_only(self) -> None:
        space = HilbertSpace("Fock", None, ("|0>", "|1>", "|2>"))
        scene = HilbertScene(space)
        result = scene.projection()
        self.assertIsNone(result["space"]["dimension"])
        self.assertIn("finite 2D projection", result["projection_notice"])

    def test_operator_shape_matches_space(self) -> None:
        scene = qubit_scene()
        identity = LinearOperator(
            "I",
            "H_qubit",
            (
                (ComplexAmplitude(1.0), ComplexAmplitude(0.0)),
                (ComplexAmplitude(0.0), ComplexAmplitude(1.0)),
            ),
            "unitary",
        )
        scene.add_operator(identity)
        result = scene.projection()
        self.assertEqual("unitary", result["operators"][0]["operator_type"])

    def test_nan_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ComplexAmplitude(float("nan"))


if __name__ == "__main__":
    unittest.main()
