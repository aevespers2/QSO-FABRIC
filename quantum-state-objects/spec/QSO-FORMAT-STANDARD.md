# QSO Format Standard 0.1

## Naming

Normative family name: `QSO-<CATEGORY>[-<SUBTYPE>]`.

## Required envelope

Every serialized QSO family object contains `qso` metadata and a `payload`. Required metadata: `format`, `format_version`, `schema`, `object_id`, `created_at`, `content_hash`, `mutation_class`, and `payload_encoding`.

## Serialization

- JSON: human-readable authoring and diagnostics.
- Canonical CBOR: normative binary interchange.
- QSO Package: compressed multi-resource deployment container.
- QSO Stream: framed append-only event transport.

## Integrity

Hashes cover canonical metadata and payload while excluding the `qso.content_hash` field itself and transport-only fields. Excluding the digest field prevents a circular hash definition. Signatures bind the object identifier, schema identifier, canonicalization algorithm, hash algorithm, and content hash.

For the version 0.1 JSON authoring profile, the SHA-256 preimage is UTF-8 JSON serialized with lexicographically sorted keys, no insignificant whitespace, preserved Unicode, no non-finite numbers, and the top-level `qso.content_hash` field omitted. A validator must fail closed on malformed, placeholder, mismatched, or unsupported root digests. Canonical CBOR remains the planned normative binary profile and requires a separately reviewed canonicalization implementation.

## Composition

A `.qso` composition root references specialized objects by immutable object identifier and content hash. Implementations must reject unresolved required references and hash mismatches before bundle acceptance. A structural authoring validator may check reference shape and digest syntax without claiming that external objects have been resolved; that limitation must be explicit.

## Evolution

Breaking schema changes increment the major version. Readers must preserve unknown non-critical fields and reject unknown critical fields.
