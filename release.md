# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME AND UPSTREAM CONTRACTS`

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, three pytest cases, and a least-privilege GitHub Actions workflow. The task chain defines that runtime as a reproducible integration harness, but no release is eligible because P0 remains `READY`, `punchlist.md` is absent, candidate head `498d0035ad3b0a00aa1669691002b051942a6e7b` has no reported commit-status checks, and package, license, contract versioning, security, rollback, provenance, and upstream compatibility gates remain incomplete.

PR #1, which proposed scheduled owner-wide repository mutation, was closed on 2026-07-16. The scope conflict is therefore resolved for the current runtime candidate by exclusion, not by accepting the proposed capability. No repository-bootstrap automation is included, approved, scheduled, or deployed. Its security and reliability findings remain retained as evidence for any future independently chartered control-plane proposal.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, and report formats must be explicitly versioned and canonicalized.
- Any future repository-bootstrap or portfolio-governance automation must be versioned and released independently from the QSO-FABRIC runtime after separate approval.
- Do not tag until the immutable candidate commit satisfies every included gate.

## Release Scope

### Included runtime scope

- Bounded Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit resource limits.
- Append-only hash-chained event ledger, freeze-point hashes, messages, and final report.
- Package/environment definition and versioned event/ledger/freeze/report contracts.
- Positive, negative, boundary, timeout, tamper, interruption, determinism, and rollback fixtures.
- Read-only hash/version compatibility with QSO-GENOMES and QuantumStateObjects without importing execution authority.

### Explicitly excluded

- Owner-wide repository discovery, scheduled cross-repository mutation, generic planning-file installation, or portfolio-governance issue creation.
- Direct writes to other repositories' default branches.
- Broad owner token distribution or activation of live scheduled mutations.

## Selected Completed Work

- Selected as governance documentation: the product-boundary decision that QSO-FABRIC is the bounded four-QSO integration harness and not the portfolio control plane.
- Selected as scope-resolution evidence: closure of PR #1 and preservation of its security/reliability findings without accepting the proposed capability.
- No executable runtime work is selected for release. The runtime, tests, workflow, and README remain candidate inputs because no task is `DONE` and no complete evidence bundle verifies them at one immutable commit.

## Planned Changelog Entries

- `Added`: verified bounded four-QSO harness, package entry point, versioned output contracts, and fixture suite.
- `Security`: limits, timeout, untrusted input, path, command/network/credential, repository-write, dependency, workflow, and supply-chain findings.
- `Fixed`: determinism, ledger, freeze, timeout, message-cap, interruption, and rollback defects.
- `Documentation`: supported environment, contracts, limits, trust boundaries, commands, failures, recovery, and excluded control-plane scope.
- `Release`: package/source artifacts, reports, SBOM where applicable, checksums, provenance, and approval.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 is `DONE`; `punchlist.md` exists and included P1-P3 work has evidence. |
| Scope and authority | PASS | PR #1 is closed; no owner-wide mutation or portfolio-control capability is included in the runtime candidate. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | NO CURRENT EVIDENCE | Full pytest and CLI smoke checks pass with retained logs at one immutable candidate head. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, recovery, and rollback require evidence. |
| Security | FAIL | Secret, dependency, input/path, resource, command/network/credential, repository-write, workflow-token, and supply-chain checks pass. |
| Integration contracts | BLOCKED | Published QSO-GENOMES manifest and runnable QuantumStateObjects baseline are validated by version and hash. |
| Documentation | PARTIAL | Purpose and run command exist; install, contracts, supported matrix, failure modes, retention, rollback, and authority boundaries are unverified. |
| Provenance | NO EVIDENCE | Commit, Python/OS/tool versions, commands, results, fixture/output hashes, SBOM, and attestations are retained. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Artifact Requirements

- Reproducible source archive and Python package artifacts.
- Versioned event, ledger, freeze-point, limit, and report schemas/contracts.
- Positive, negative, boundary, timeout, tamper, determinism, interruption, and rollback fixture bundle.
- Complete test, CLI smoke, static, security, integration, and documentation reports.
- Representative report/ledger, SBOM where applicable, SHA-256 checksums, and provenance manifest.
- If portfolio bootstrap automation is proposed again in a separate product: opt-in repository manifest, dry-run evidence, per-repository pull-request flow, correct user/organization discovery, paginated duplicate detection, explicit write-error propagation, disabled-feature handling, mutation throttling/retry/checkpointing, least-privilege token matrix, audit/revocation/rollback design, duplicate-file prevention tests, and independent approval record.

## Rollback Criteria

Withdraw or roll back the runtime candidate if seeded runs diverge, ledger tampering is undetected, limits can be bypassed, timeout/interruption corrupts evidence, freeze hashes are unstable, untrusted input gains authority, upstream contracts drift, documented commands fail, severe security findings remain, or artifact hashes differ. If a future control-plane proposal is separately approved, disable and revoke it immediately after any unapproved write, non-opted-in target, protected/default-branch mutation, duplicate source of truth, silently skipped target, suppressed write failure, lost audit evidence, untracked partial run, or token-scope violation. Restore the prior verified state and preserve failed-candidate inputs, logs, reports, hashes, and affected-repository inventory.

## Unresolved Blockers

- P0 remains `READY`; `punchlist.md` and accepted Builder evidence are absent.
- Candidate head `498d0035ad3b0a00aa1669691002b051942a6e7b` has no reported commit-status checks, clean-environment pytest report, or CLI smoke report.
- No package/build definition, supported Python matrix, dependency baseline, or license is present.
- Adversarial, timeout, tamper, interruption, rollback, security, checksum, SBOM, and provenance evidence is absent.
- Upstream compatibility is blocked by the unaccepted QSO-GENOMES set and non-runnable QuantumStateObjects package.

## Archived Control-Plane Findings

PR #1 was closed and is not a current release blocker. Its retained findings cover broad-token/live-schedule/direct-write authority, duplicate planning files, incorrect organization discovery, non-paginated idempotency checks, swallowed write failures, disabled-Issues handling, and unsafe unthrottled partial mutation. Any successor requires a separate product charter and approval.

## Release Log

- 2026-07-16: Aligned the candidate with the bounded integration-harness directive; release remained blocked pending reproducible runtime and upstream-contract evidence.
- 2026-07-16: Reviewed PR #1, excluded owner-wide bootstrap automation from the runtime scope, and recorded its security and reliability findings.
- 2026-07-16: PR #1 was closed. Marked the runtime scope/authority gate `PASS` by exclusion; no automation capability was accepted, and the runtime release remains blocked by its original evidence and dependency gates.
