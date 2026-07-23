# QSO-ECOSYSTEM-001: Ecosystem Conformance Foundation

Status: Draft 0.1

## Purpose

This specification defines the minimum evidence required for a repository to participate in the QSO ecosystem. It converts architectural claims into machine-checkable contracts while preserving bounded autonomy and human review.

## Conformance levels

- **L0 — Identified:** valid ecosystem manifest, ownership, purpose, version, and declared interfaces.
- **L1 — Reproducible:** deterministic build or execution instructions and pinned runtime assumptions.
- **L2 — Verified:** automated schema, unit, and invariant tests with stored evidence.
- **L3 — Integrated:** contract tests against at least one other QSO component and versioned interface compatibility.
- **L4 — Resilient:** threat model, failure injection, recovery tests, and bounded-resource enforcement.
- **L5 — Governed:** provenance, audit ledger, human override, migration policy, and release attestation.

A repository MUST NOT claim a level unless every requirement at that level and below is satisfied.

## Required repository artifacts

1. `qso.manifest.json`
2. `README.md` with deterministic run instructions
3. `SECURITY.md` or an explicit security-boundary section
4. `tests/` containing executable checks
5. `artifacts/conformance/` for generated evidence
6. A CI workflow invoking the ecosystem validator

## Core invariants

Every runtime component MUST declare and test:

- bounded execution time, rounds, messages, memory, and external authority;
- deterministic replay when a seed and input set are fixed;
- append-only provenance for state transitions;
- explicit freeze, stop, and human-override behavior;
- schema-versioned inputs, outputs, and migrations;
- denial by default for undeclared capabilities;
- separation of proposal generation from consequential execution.

## Interface contract

Interfaces MUST identify:

- protocol and schema version;
- producer and consumer roles;
- authentication and authorization assumptions;
- idempotency and replay behavior;
- failure semantics and retry limits;
- provenance fields and integrity hashes;
- deprecation and migration windows.

## Evidence bundle

A conformance run SHOULD emit one JSON document containing:

- repository and commit identity;
- validator version;
- claimed and achieved level;
- test names, outcomes, and durations;
- invariant results;
- dependency and interface versions;
- generated artifact hashes;
- unresolved exceptions and approving human reviewer.

## Governance compatibility

The governance/review component is canonically named **Jacob Redmond**. Historical identifiers such as `Aequitas` MAY remain only as deprecated aliases with explicit migration metadata; silent identifier replacement is prohibited.

## Scoring mapping

The ecosystem benchmark is computed from weighted evidence rather than aspiration:

- architecture and interfaces: 15%
- implementation completeness: 15%
- verification and reproducibility: 20%
- security and resilience: 15%
- governance and provenance: 10%
- interoperability: 10%
- documentation and usability: 10%
- operational evidence: 5%

Missing evidence scores zero for the corresponding criterion. Self-attestation without executable evidence is capped at 50% of that criterion.
