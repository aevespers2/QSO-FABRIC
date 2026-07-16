# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME BASELINE`

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, three pytest cases, and a least-privilege GitHub Actions workflow. The task chain now formally defines the runtime as a reproducible integration harness, but no release is eligible because P0 remains `READY`, `punchlist.md` is absent, candidate head `cb624f246c75c888fc2949694ccd892564502258` lacks current CI/test evidence, and package, license, contract versioning, security, rollback, provenance, and upstream compatibility gates remain incomplete.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, and report formats must be explicitly versioned and canonicalized.
- Do not tag until the immutable candidate commit satisfies every gate.

## Release Scope

- Bounded Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit resource limits.
- Append-only hash-chained event ledger, freeze-point hashes, messages, and final report.
- Package/environment definition and versioned event/ledger/freeze/report contracts.
- Positive, negative, boundary, timeout, tamper, interruption, determinism, and rollback fixtures.
- Read-only hash/version compatibility with QSO-GENOMES and QuantumStateObjects without importing execution authority.

## Selected Completed Work

None selected. The runtime, tests, workflow, and README are candidate implementation inputs, but no task is `DONE` and no complete evidence bundle verifies them at one immutable commit.

## Planned Changelog Entries

- `Added`: verified bounded four-QSO harness, package entry point, versioned output contracts, and fixture suite.
- `Security`: limits, timeout, untrusted input, path, command/network/credential, repository-write, dependency, and workflow findings.
- `Fixed`: determinism, ledger, freeze, timeout, message-cap, interruption, and rollback defects.
- `Documentation`: supported environment, contracts, limits, trust boundaries, commands, failures, and recovery.
- `Release`: package/source artifacts, reports, SBOM where applicable, checksums, provenance, and approval.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 is `DONE`; `punchlist.md` exists and included P1-P3 work has evidence. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | NO CURRENT EVIDENCE | Full pytest and CLI smoke checks pass with retained logs at the candidate commit. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, recovery, and rollback require evidence. |
| Security | NO EVIDENCE | Secret, dependency, input/path, resource, command/network/credential, repository-write, and supply-chain checks pass. |
| Integration contracts | BLOCKED | Published QSO-GENOMES manifest and runnable QuantumStateObjects baseline are validated by version and hash. |
| Documentation | PARTIAL | Purpose and run command exist; install, contracts, supported matrix, failure modes, retention, and rollback are unverified. |
| Provenance | NO EVIDENCE | Commit, Python/OS/tool versions, commands, results, fixture/output hashes, SBOM, and attestations are retained. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Artifact Requirements

- Reproducible source archive and Python package artifacts.
- Versioned event, ledger, freeze-point, limit, and report schemas/contracts.
- Positive, negative, boundary, timeout, tamper, determinism, interruption, and rollback fixture bundle.
- Complete test, CLI smoke, static, security, integration, and documentation reports.
- Representative report/ledger, SBOM where applicable, SHA-256 checksums, and provenance manifest.

## Rollback Criteria

Withdraw or roll back if seeded runs diverge, ledger tampering is undetected, limits can be bypassed, timeout/interruption corrupts evidence, freeze hashes are unstable, untrusted input gains authority, upstream contracts drift, documented commands fail, severe security findings remain, or artifact hashes differ. Restore the prior verified state and preserve failed-candidate inputs, logs, reports, and hashes.

## Unresolved Blockers

- P0 remains `READY`; `punchlist.md` and accepted Builder evidence are absent.
- No current CI, clean-environment pytest, or CLI smoke report is attached.
- No package/build definition, supported Python matrix, dependency baseline, or license is present.
- Adversarial, timeout, tamper, interruption, rollback, security, checksum, SBOM, and provenance evidence is absent.
- Upstream compatibility is blocked by the incomplete QSO-GENOMES set and non-runnable QuantumStateObjects package.

## Release Log

- 2026-07-16: Aligned the candidate with the bounded integration-harness directive; release remains blocked pending reproducible runtime and upstream-contract evidence.