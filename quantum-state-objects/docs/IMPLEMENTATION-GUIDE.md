# QSO Format Implementation Guide

## Audience

This guide is for developers and reviewers working on the QSO format subsystem in QSO-FABRIC PR #19. The included Python utilities are development references, not a hardened production SDK.

## Development setup

From `quantum-state-objects/`:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pytest -q
```

Use an isolated environment. Do not install the development package into a privileged system interpreter or a production runtime.

## Validation pipeline

Implementations should process an object in this order:

1. **Read bounded bytes.** Enforce maximum source, nesting, collection, string, and attachment sizes before deep processing.
2. **Decode strict UTF-8.** Reject invalid byte sequences.
3. **Parse strict JSON.** Reject duplicate keys, non-finite numbers, unsupported critical fields, and ambiguous number representations.
4. **Validate the common envelope.** Check format, version, schema, object identity, timestamp, encoding, mutation classification, and hash fields.
5. **Validate the family payload.** Apply the exact family schema and profile.
6. **Check registries.** Verify supported format, media type, extension, algorithm, mutation class, and conversion identifiers.
7. **Canonicalize and verify content hashes.** Use the exact declared canonicalization generation.
8. **Resolve required references.** Bind target identity, expected digest, version, and allowed relationship.
9. **Build and validate the composition graph.** Reject missing targets, forbidden cycles, conflicting identities, or unsupported mappings.
10. **Verify signatures when required.** Signature validity is separate from signer authorization and current trust.
11. **Apply governance and admission policy.** Keep proposal, review, capability, execution, and disposition records separate.
12. **Expose only bounded results.** Validation must not execute embedded resources or silently activate capabilities.
13. **Record provenance.** Bind source, tool version, mapping, timestamps, inputs, outputs, failures, corrections, and rollback.

## Repository layout workflow

When adding a format family:

1. add or update its registry entry;
2. add a closed schema and explicit version;
3. document semantic ownership and non-ownership;
4. provide a minimal valid example;
5. add malformed, boundary, stale, unsupported-version, and hostile fixtures;
6. update applicable profiles;
7. add canonicalization vectors and expected hashes;
8. document migration, correction, revocation, and rollback;
9. update architecture, governance, security, roadmap, task chain, release plan, and changelog; and
10. obtain independent review at one immutable head.

Do not add a family merely because a filename or concept appears elsewhere in the portfolio. Shared names require explicit mappings and ownership.

## Adding a conversion adapter

A conversion adapter must:

- preserve source bytes;
- bind exact source path and digest;
- define a stable conversion identifier and version;
- state whether the mapping is lossless, lossy, reversible, or partial;
- require explicit conversion time rather than inventing trusted time;
- emit separate target and provenance identities;
- fail closed on ambiguous family selection;
- provide deterministic fixtures for the complete input tuple;
- include correction, revocation, supersession, and rollback treatment; and
- avoid claims of source authenticity, runtime admission, or canonical acceptance.

See [`CONVERSION-BOUNDARY.md`](CONVERSION-BOUNDARY.md).

## Packaging workflow

Before packing:

- validate every source file and expected media type;
- reject symlinks and unsafe or non-normalized paths;
- keep the output outside the source tree;
- generate a deterministic manifest with size and digest bindings; and
- enforce member and aggregate size ceilings.

Before unpacking:

- inspect the complete central directory;
- reject traversal, absolute, drive-qualified, backslash, collision, encryption, unsupported compression, symlink, special-file, and oversized entries;
- parse and validate the manifest before creating the destination;
- verify archive/member set, size, media type, and digest equality;
- require a safe, empty destination with no symlink parents; and
- extract manually only after every preflight check passes.

Package validation does not make embedded resources safe to execute.

## Error and result design

Use stable error classes and reason codes. Avoid collapsing these conditions:

- malformed input;
- unsupported version;
- unresolved reference;
- integrity mismatch;
- signature invalid;
- signer unauthorized;
- stale or replayed record;
- policy denied;
- partial or unknown evidence;
- privacy or licensing hold;
- correction or revocation pending;
- rollback required; and
- internal implementation error.

A tool error is not a policy failure, and a policy denial is not evidence corruption.

## Test expectations

Every changed surface should include:

- positive fixtures;
- duplicate-key and non-finite-number rejection;
- size and nesting boundaries;
- wrong digest and wrong identity cases;
- unsupported versions and algorithms;
- stale, replay, correction, revocation, and supersession cases;
- archive traversal, collision, symlink, special-file, and decompression-limit cases where applicable;
- conversion source-preservation and deterministic-input-tuple cases;
- partial-write, interruption, retry, and rollback cases; and
- public-output safety checks.

## Documentation checklist

Before review, align:

- root and subsystem READMEs;
- architecture and diagrams with prose alternatives;
- governance and ownership boundaries;
- security and privacy assumptions;
- onboarding and exact commands;
- `taskchain.md` priorities;
- `release.md` gates;
- `changelog.md` evidence; and
- PR #15/#19 reconciliation notes.

## Prohibited shortcuts

Do not:

- treat locally implemented canonical JSON as portfolio-approved canonical bytes;
- infer authority from a governance or capability object;
- execute resources during validation;
- silently ignore unsupported fields or versions;
- discard source artifacts after conversion;
- equate test success with architecture acceptance;
- weaken package preflight to improve compatibility; or
- publish or release from an unreconciled documentation/implementation lineage.

## Completion meaning

A change is ready for repository review when its semantics, source identity, negative fixtures, documentation, security effects, rollback path, and exact-head evidence are complete. It is not production-ready until neutral ownership, signatures, key custody, cross-language compatibility, independent security review, release approval, and deployment policy are separately satisfied.