# QSO Legacy Conversions

This directory contains additive, reversible conversions of legacy QSO-FABRIC artifacts into the QSO Format Standard 0.1 family envelopes.

## Rules

1. Preserve the source artifact unchanged.
2. Record the exact source path and SHA-256 digest.
3. Emit a family-specific QSO object with a deterministic content hash.
4. Emit append-only QSO-PROVENANCE for every conversion.
5. Queue ambiguous artifacts instead of guessing their semantic family.
6. Treat conversion as representation migration, not authorization to activate capabilities or modify source policy.

## Layout

- `output/` converted QSO family objects
- `provenance/` conversion events and lineage
- `conversion-registry.json` completed and queued conversions
- `conversion-queue.json` artifacts awaiting classification or mapping
