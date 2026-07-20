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

Hashes cover canonical metadata and payload, excluding transport-only fields. Signatures bind the object identifier, schema identifier, canonicalization algorithm, hash algorithm, and content hash.

## Composition

A `.qso` composition root references specialized objects by immutable object identifier and content hash. Implementations must reject unresolved required references and hash mismatches.

## Evolution

Breaking schema changes increment the major version. Readers must preserve unknown non-critical fields and reject unknown critical fields.
