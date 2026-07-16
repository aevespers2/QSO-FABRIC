# Changelog

## Unreleased

### Product
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.

### Architecture
- Added a formal task chain that preserves QSO-GENOMES and QuantumStateObjects as schema/hash-validated dependencies without importing executable authority.

### Implementation
- Existing runtime, tests, and CI are recorded as candidate assets; this entry does not claim they have passed current release gates.

### Release
- The first candidate remains blocked until the runtime is reproducible, packaged, licensed, security-tested, checksummed, and tied to provenance.

### Deployment
- No networked or production deployment is in MVP scope.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable