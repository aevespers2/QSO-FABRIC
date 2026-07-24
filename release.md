# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME AND UPSTREAM CONTRACTS`

Trusted base before this repair: `main@bd0ac7af3b34602082db03e71055b652707c9b18`.

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, tests, and repository workflows. It is not release eligible because the runtime has not been reproduced at one immutable candidate with clean installation, deterministic hashes, adversarial fixtures, rollback evidence, package identity, license, provenance, accepted upstream contracts, security review, and explicit approval.

The repository previously claimed that owner-wide bootstrap automation was excluded while a trusted-base workflow still ran every six hours with `contents: write`, `issues: write`, a broad repository secret, persisted checkout credentials, and direct cross-repository mutation behavior. That contradiction is now addressed by a focused repair candidate: the schedule and automatic live-write path are removed, the retained workflow is manual and read-only, generated evidence is isolated and retained, and the script fails closed unless a separately authorized direct execution explicitly enables writes. No such execution or credential is approved.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, message, contradiction, repair, training-trace, probe-log, and report formats must be explicitly versioned and canonicalized.
- Any repository-bootstrap or portfolio-governance automation must be independently chartered, reviewed, versioned, and released outside the runtime product boundary.
- Do not tag until the immutable candidate commit satisfies every included gate.

## Release Scope

### Included runtime scope

- Bounded Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit resource limits.
- Append-only hash-chained event ledger, freeze-point hashes, messages, and final report.
- Package/environment definition and versioned event, ledger, freeze-point, limit, and report contracts.
- Positive, negative, boundary, malformed, replay, timeout, tamper, interruption, determinism, and rollback fixtures.
- Read-only hash/version compatibility with QSO-GENOMES and QuantumStateObjects without importing execution authority.

### Explicitly excluded

- Scheduled owner-wide repository discovery or mutation.
- Generic planning-file installation and portfolio-governance issue creation.
- Direct writes to other repositories' default branches.
- Broad owner token distribution or activation of live mutation.
- Package publication, deployment, credentials, payments, infrastructure applies, or production control without separate approval.

## Selected Completed Work

- Product boundary: QSO-FABRIC remains the bounded four-QSO integration harness, not the portfolio control plane.
- Consent boundary: repository-wide consent-capacity validation is exact-head, read-only, pinned, and evidence retaining.
- Bootstrap safety candidate: scheduled and automatic live-write behavior is retired; manual audit coverage is public-repository and read-only; unauthorized mutation fails before network writes; GET-only `404` handling and issue pagination are corrected; focused regressions and retained exact-head evidence are required.
- Planning alignment: `taskchain.md`, `punchlist.md`, `release.md`, and `changelog.md` distinguish completed safety repair from unverified runtime and future research work.

No executable runtime work is selected for release solely because these governance controls exist.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 runtime reproduction is `DONE`; included P1-P3 work has evidence. |
| Scope and authority | REVIEW | The bootstrap safety repair must pass exact-head validation and merge without restoring scheduled writes or privileged permissions. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | PARTIAL | Safety workflows exist; full runtime pytest and CLI smoke checks require retained logs at one immutable candidate head. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, recovery, and rollback require evidence. |
| Security | FAIL | Secret, dependency, input/path, resource, command/network/credential, repository-write, workflow-token, and supply-chain checks pass. |
| Integration contracts | BLOCKED | Published QSO-GENOMES manifest and runnable QuantumStateObjects baseline are accepted and validated by version and hash. |
| Documentation | PARTIAL | Purpose, boundaries, and planning records exist; install, contracts, supported matrix, failure modes, retention, and recovery remain incomplete. |
| Provenance | PARTIAL | Safety evidence is retained; complete runtime commit, environment, command, fixture/output hash, SBOM, and attestation evidence is absent. |
| Approval | PENDING | Explicit release approval after every blocking gate passes. |

## Artifact Requirements

- Reproducible source archive and Python package artifacts.
- Versioned event, ledger, freeze-point, limit, contradiction, repair, training-trace, probe-log, and report schemas.
- Positive, negative, boundary, malformed, replay, timeout, tamper, determinism, interruption, and rollback fixtures.
- Complete test, CLI smoke, static, security, integration, documentation, and exact-head workflow reports.
- Representative report and ledger, SBOM where applicable, SHA-256 checksums, and provenance manifest.
- For any future independently approved control plane: opt-in target manifest, dry-run evidence, per-repository pull-request flow, correct user/organization discovery, paginated idempotency checks, explicit write-error propagation, disabled-feature handling, mutation throttling/retry/checkpointing, least-privilege token matrix, audit/revocation/rollback design, duplicate-file prevention tests, and an independent approval record.

## Rollback Criteria

Withdraw or roll back the runtime candidate if seeded runs diverge, ledger tampering is undetected, limits can be bypassed, timeout or interruption corrupts evidence, freeze hashes are unstable, untrusted input gains authority, upstream contracts drift, documented commands fail, severe security findings remain, or artifact hashes differ.

Withdraw the bootstrap safety repair if any schedule, automatic write permission, broad secret, persisted checkout credential, unapproved mutation path, misleading dry-run report, missing failure artifact, or source-integrity defect reappears. Preserve the failed candidate, workflow run, report, hashes, and affected repository inventory.

## Unresolved Blockers

- P0 runtime reproduction remains `READY` rather than `DONE`.
- No package/build definition, supported Python matrix, dependency baseline, or license is verified.
- Adversarial, timeout, tamper, interruption, rollback, security, checksum, SBOM, and complete provenance evidence is absent.
- Upstream compatibility is blocked by the unaccepted QSO-GENOMES set and QuantumStateObjects runtime candidate.
- Contradiction/repair records, canonical training traces, and Planck-probe logs remain proposals without accepted schemas or independent consumers.
- Any live control-plane write path remains unauthorized.

## Release Log

- 2026-07-16: Aligned the candidate with the bounded integration-harness directive and excluded the original bootstrap proposal.
- 2026-07-24: Verified that the trusted base contradicted that exclusion through a scheduled privileged bootstrap workflow whose live mutation step failed.
- 2026-07-24: Prepared a reversible repair that removes the schedule and write permissions, eliminates the workflow's broad secret, enforces dry-run and explicit write authorization, adds exact-head safety validation, and synchronizes the planning records. Release remains blocked.
