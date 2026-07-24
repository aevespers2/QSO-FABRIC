"""Export a deterministic QSO-HILBERT-1 demonstration scene."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .hilbert_glyphs import ComplexAmplitude, LinearOperator, StateVector, qubit_scene


def build_manifest() -> dict[str, object]:
    scene = qubit_scene()
    amplitude = 1.0 / math.sqrt(2.0)
    scene.add_state(StateVector("|0>", "H_qubit", (ComplexAmplitude(1.0), ComplexAmplitude(0.0))))
    scene.add_state(StateVector("|1>", "H_qubit", (ComplexAmplitude(0.0), ComplexAmplitude(1.0))))
    scene.add_state(StateVector("|+>", "H_qubit", (ComplexAmplitude(amplitude), ComplexAmplitude(amplitude))))
    scene.add_operator(
        LinearOperator(
            "Hadamard",
            "H_qubit",
            (
                (ComplexAmplitude(amplitude), ComplexAmplitude(amplitude)),
                (ComplexAmplitude(amplitude), ComplexAmplitude(-amplitude)),
            ),
            "unitary",
        )
    )
    return scene.projection()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a QSO-HILBERT-1 visual projection manifest")
    parser.add_argument("--output", type=Path, default=Path("artifacts/qso-hilbert-manifest.json"))
    args = parser.parse_args()
    manifest = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "manifest_sha256": manifest["manifest_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
