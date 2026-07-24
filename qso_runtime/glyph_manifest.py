"""Command-line export for the canonical QSO glyph manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .glyphs import core_registry


def build_manifest(include_examples: bool = True) -> dict[str, object]:
    registry = core_registry()
    if include_examples:
        registry.compose("historian", "observer joined with memory", ("observer", "memory"))
        registry.compose("self-awareness", "observer recursively related to retained state", ("observer", "memory", "change"))
        registry.compose("collective-intelligence", "observing agents joined through directed exchange", ("observer", "intent", "state"))
    return registry.manifest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the deterministic QSO-GLYPH-1 manifest")
    parser.add_argument("--output", type=Path, default=Path("artifacts/qso-glyph-manifest.json"))
    parser.add_argument("--roots-only", action="store_true", help="omit composed demonstration glyphs")
    args = parser.parse_args()

    manifest = build_manifest(include_examples=not args.roots_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "glyph_count": len(manifest["glyphs"]), "manifest_sha256": manifest["manifest_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
