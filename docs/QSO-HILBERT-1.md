# QSO-HILBERT-1

QSO-HILBERT-1 is a deterministic mathematical and visual-projection layer built on QSO-GLYPH-1. It represents finite-dimensional complex Hilbert spaces directly and infinite-dimensional spaces through an explicitly bounded displayed basis.

## Separation of truth and display

The canonical layer stores:

- a Hilbert-space name, dimension, field, and displayed orthonormal basis;
- complex state-vector coefficients;
- normalization state;
- square linear-operator matrices and operator classifications;
- exact inner products computed from canonical coefficients.

The visual layer stores nodes and edges derived from that data. Every exported scene declares:

```text
finite 2D projection; not the Hilbert space itself
```

A renderer must never reinterpret visual coordinates as canonical amplitudes, probabilities, distances, or semantic truth.

## Glyph mapping

| Mathematical object | QSO glyph root | Visual relation |
|---|---|---|
| Hilbert space | `existence` | enclosing origin node |
| basis vector | `state` | radial basis anchor |
| state vector | `observer` | situated state node |
| operator | `transform` | transformation node |
| coefficient | edge metadata | magnitude and complex phase |
| membership | edge | `contains` |
| superposition | edge | `superposition` |
| operator domain | edge | `acts_on` |

Zero coefficients are omitted from the visual edge set but remain present in canonical state data.

## Supported structures

The first implementation supports:

- finite and explicitly projected infinite-dimensional complex spaces;
- normalized and intentionally unnormalized state vectors;
- complex amplitudes, magnitude, phase, and inner products;
- orthogonality tests through zero inner product;
- linear, unitary, Hermitian, projector, and density operators;
- deterministic content-addressed scene manifests.

Tensor products, partial traces, eigensystems, spectral measures, projective-ray equivalence, and density-matrix validation are reserved for subsequent versions.

## Export demonstration

```bash
python -m qso_runtime.hilbert_manifest \
  --output artifacts/qso-hilbert-manifest.json
```

The demonstration contains the qubit basis states `|0>` and `|1>`, the equal superposition `|+>`, and the Hadamard operator.

## Verification

```bash
python -m unittest discover -s tests -p 'test_hilbert_glyphs.py' -v
```

Tests cover deterministic projection, coefficient magnitudes, orthogonality, normalization failure, bounded views of infinite spaces, operator dimensions, and rejection of non-finite numbers.

## Authority boundary

QSO-HILBERT-1 is a notation and interchange format. It does not perform physical experiments, certify a quantum state, infer that a represented system exists, or grant simulation, execution, publication, or deployment authority.
