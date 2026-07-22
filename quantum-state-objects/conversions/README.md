# QSO Compatibility Conversions

This directory contains **additive, source-preserving conversion adapters** for legacy or repository-local QSO-FABRIC artifacts. The adapters emit candidate QSO family objects and provenance records without rewriting or deleting the source.

Read [`../docs/CONVERSION-BOUNDARY.md`](../docs/CONVERSION-BOUNDARY.md) for the architecture, trust model, review checklist, and current hardening gaps.

## Core rules

1. Preserve the exact source artifact unchanged.
2. Record the source path and SHA-256 digest.
3. Give every source, conversion attempt, derived report, and provenance object a distinct identity.
4. Emit a family-specific derived object with a deterministic content hash for the complete conversion input tuple.
5. Emit append-only `QSO-PROVENANCE` for every conversion.
6. Queue ambiguous artifacts instead of guessing their semantic family.
7. Treat conversion as representation migration, not source validation, runtime admission, or authority.
8. Preserve correction, revocation, supersession, and rollback references when those contracts are introduced.

## Current adapter

`four-qso-report-to-qso-report-v1` converts a bounded four-QSO experiment report into:

- `QSO-REPORT` — objective, per-QSO observations, inferences, contradictions, proposals, freeze points, and source/provenance references;
- `QSO-PROVENANCE` — source events, source-declared ledger state, limits, seed, final event hash, and source binding.

The adapter requires an explicit `--created-at` value. Output bytes and hashes are therefore reproducible only when the source bytes, source-path string, timestamp, converter version, and serialization rules are all unchanged.

## Example

From the repository root:

```bash
python quantum-state-objects/tools/convert_four_qso_report.py \
  artifacts/four_qso_report.json \
  --created-at 2026-07-23T00:00:00Z \
  --report-output artifacts/converted/four-qso.qreport.json \
  --provenance-output artifacts/converted/four-qso.qprov.json
```

Review the source and both outputs together. Do not move only the derived report while discarding the source or provenance record.

## Registry semantics

`conversion-registry.json` distinguishes:

- completed conversions tied to exact source and target digests;
- locally available adapters and their expected source pattern;
- target family names;
- source-preservation and reversibility claims; and
- the tests covering the adapter.

A registry status such as `ready` means that the local adapter and tests are present for review. It does **not** mean accepted portfolio compatibility, production readiness, or authority to migrate external data.

## Layout

| Path | Meaning |
|---|---|
| `output/` | Derived QSO family objects |
| `provenance/` | Conversion events and lineage records |
| `conversion-registry.json` | Completed conversions and locally available adapters |
| `conversion-queue.json` | Artifacts awaiting classification, mapping, or ownership decisions |

## Fail closed when

- source bytes or expected digest differ;
- required source fields are missing or inconsistent;
- the semantic family is ambiguous;
- the conversion timestamp or source identity is absent;
- output identities collide;
- the adapter or mapping version is unsupported;
- privacy, licensing, retention, or publication treatment is unknown;
- a consumer would lose source, provenance, correction, or revocation references; or
- conversion is being used as a substitute for approval, admission, or canonical disposition.

## Non-authority statement

```text
conversion success
!= source authenticity
!= independent ledger verification
!= accepted QSO standard
!= runtime admission
!= mutation or capability authority
!= source deletion permission
!= release, publication, or deployment approval
```