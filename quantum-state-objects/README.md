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
