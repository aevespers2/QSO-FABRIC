# QSO-GLYPH-1

QSO-GLYPH-1 is a deterministic semantic writing layer for QSO Fabric. It represents a glyph as validated geometric data rather than as an opaque image, allowing runtimes, ledgers, renderers, and analysis tools to exchange the same canonical object.

## Geometry

Every stroke is anchored to a 7×7 integer grid and uses one of eight primitives:

| Primitive | Semantic root |
|---|---|
| circle | existence or bounded object |
| vertical | time or ordered change |
| horizontal | stability or state |
| curve | continuous change |
| triangle | intent or direction |
| diamond | discrete transformation |
| dot | origin or observation |
| arc | recursion or memory |

A stroke also carries bounded weight and 45-degree rotation. A glyph adds a family, optional phoneme, certainty, abstraction level, semantic tags, and component references.

## Canonical identity

Each glyph is serialized as sorted compact JSON and assigned a content-derived identifier:

```text
qg:<first 24 hexadecimal digits of SHA-256>
```

A registry exports a `QSO-GLYPH-1` manifest with an independent SHA-256 digest. Equivalent glyph sets therefore produce equivalent identifiers and manifests across runs.

## Composition

Composition joins two or more registered glyphs, removes duplicate strokes, preserves component order, merges tags, carries the lowest component certainty, and advances the abstraction level by one. Examples included by the CLI are:

- `observer + memory -> historian`
- `observer + memory + change -> self-awareness`
- `observer + intent + state -> collective-intelligence`

Composition is descriptive only. It does not execute capabilities or alter QSO runtime authority.

## Export

```bash
python -m qso_runtime.glyph_manifest \
  --output artifacts/qso-glyph-manifest.json
```

Use `--roots-only` to emit only the eight canonical roots.

## Tests

```bash
python -m unittest discover -s tests -p 'test_glyphs.py' -v
```

The tests cover deterministic manifests, semantic composition, registry conflicts, grid boundaries, and external mapping validation.

## Future renderer contract

A renderer should consume only the manifest and map primitives to SVG, OpenType, canvas, or terminal output. Rendering must not modify semantic identity; presentation-specific animation, color, or interpolation belongs in a separate non-canonical layer.
