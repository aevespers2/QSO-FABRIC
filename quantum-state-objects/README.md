# Quantum State Object File Formats

This directory defines the QSO container family, schemas, registries, lifecycle rules, reference tooling, examples, and conformance tests.

## Layout

- `spec/` normative format and lifecycle specifications
- `registry/` machine-readable format, media-type, extension, and mutation registries
- `schemas/` shared and family-specific JSON Schemas
- `profiles/` interoperable implementation profiles
- `examples/` valid reference objects and bundles
- `tools/` reference validation, packing, unpacking, hashing, and migration utilities
- `tests/` conformance and negative-test fixtures
- `docs/` architecture, security, governance, and implementation guidance

The canonical `.qso` object is a cryptographically bound composition root. Specialized family files remain independently versioned and content-addressed.

## Current validator boundary

`tools/qso_validate.py` is a fail-closed, dependency-free validator for the JSON authoring profile. It validates required metadata types and formats, QSO-CORE reference structure, non-placeholder SHA-256 digests, and the top-level canonical JSON content hash. It deliberately rejects BLAKE3 roots until a reviewed dependency or implementation is available.

The validator does **not** resolve external references, validate signatures, authorize mutations, or establish that referenced manifest and identity objects exist. Those remain release-blocking bundle, registry, and governance checks rather than implicit claims of this scaffold.
