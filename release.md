# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME AND SCOPE-CONFLICT REVIEW`

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, three pytest cases, and a least-privilege GitHub Actions workflow. The task chain defines that runtime as a reproducible integration harness, but no release is eligible because P0 remains `READY`, `punchlist.md` is absent, candidate head `498d0035ad3b0a00aa1669691002b051942a6e7b` has no reported commit-status checks, and package, license, contract versioning, security, rollback, provenance, and upstream compatibility gates remain incomplete.

Draft PR #1 is not part of the runtime candidate. It proposes scheduled owner-wide repository mutation using a broad token and direct default-branch writes, defaults scheduled execution to live writes, and can create duplicate planning sources such as `TASK_CHAIN.md` beside `taskchain.md`. It requires redesign or relocation and explicit approval before it can enter any release scope.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, and report formats must be explicitly versioned and canonicalized.
- Repository-bootstrap or portfolio-governance automation must be versioned and released independently from the QSO-FABRIC runtime if approved.
- Do not tag until the immutable candidate commit satisfies every gate.

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

- Selected as governance documentation only: the product-boundary decision that QSO-FABRIC is the bounded four-QSO integration harness and not the portfolio control plane.
- Selected as review evidence only: the recorded security and scope findings for draft PR #1.
- No executable runtime work is selected for release. The runtime, tests, workflow, and README remain candidate inputs because no task is `DONE` and no complete evidence bundle verifies them at one immutable commit.

## Planned Changelog Entries

- `Added`: verified bounded four-QSO harness, package entry point, versioned output contracts, and fixture suite.
- `Security`: limits, timeout, untrusted input, path, command/network/credential, repository-write, dependency, workflow, and cross-repository authority findings.
- `Fixed`: determinism, ledger, freeze, timeout, message-cap, interruption, and rollback defects.
- `Documentation`: supported environment, contracts, limits, trust boundaries, commands, failures, recovery, and excluded control-plane scope.
- `Release`: package/source artifacts, reports, SBOM where applicable, checksums, provenance, and approval.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 is `DONE`; `punchlist.md` exists and included P1-P3 work has evidence. |
| Scope and authority | FAIL | Draft PR #1 is closed, relocated, or redesigned as an independently approved opt-in control-plane release; no owner-wide mutation capability is included in the runtime candidate. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | NO CURRENT EVIDENCE | Full pytest and CLI smoke checks pass with retained logs at candidate head `498d0035ad3b0a00aa1669691002b051942a6e7b`. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, recovery, and rollback require evidence. |
| Security | FAIL | Secret, dependency, input/path, resource, command/network/credential, repository-write, workflow-token, cross-repository, and supply-chain checks pass. |
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
- If portfolio bootstrap automation is pursued separately: opt-in repository manifest, dry-run evidence, per-repository pull-request flow, least-privilege token matrix, audit/retry/revocation/rollback design, duplicate-file prevention tests, and independent approval record.

## Rollback Criteria

Withdraw or roll back the runtime candidate if seeded runs diverge, ledger tampering is undetected, limits can be bypassed, timeout/interruption corrupts evidence, freeze hashes are unstable, untrusted input gains authority, upstream contracts drift, documented commands fail, severe security findings remain, or artifact hashes differ. Immediately disable and revoke any bootstrap automation if it performs an unapproved write, targets a non-opted-in repository, writes directly to a protected/default branch, creates a duplicate source of truth, loses audit evidence, or exceeds its declared token scope. Restore the prior verified state and preserve failed-candidate inputs, logs, reports, hashes, and affected-repository inventory.

## Unresolved Blockers

- P0 remains `READY`; `punchlist.md` and accepted Builder evidence are absent.
- Candidate head `498d0035ad3b0a00aa1669691002b051942a6e7b` has no reported commit-status checks, clean-environment pytest report, or CLI smoke report.
- No package/build definition, supported Python matrix, dependency baseline, or license is present.
- Adversarial, timeout, tamper, interruption, rollback, security, checksum, SBOM, and provenance evidence is absent.
- Upstream compatibility is blocked by the incomplete QSO-GENOMES set and non-runnable QuantumStateObjects package.
- Draft PR #1 conflicts with the approved product directive and currently presents broad-token, live-schedule, direct-write, duplicate-source, audit, and rollback risks.

## Decisions Requiring Approval

- Close or relocate draft PR #1 to a dedicated governance/control repository, or approve a redesigned independent control-plane product.
- Any approved redesign must be opt-in per repository, dry-run by default, pull-request based, least-privilege, non-duplicative, auditable, reversible, and excluded from the QSO-FABRIC runtime release.

## Release Log

- 2026-07-16: Aligned the candidate with the bounded integration-harness directive; release remained blocked pending reproducible runtime and upstream-contract evidence.
- 2026-07-16: Reviewed draft PR #1, excluded owner-wide bootstrap automation from the runtime scope, recorded its security blockers, and held the candidate `BLOCKED` pending redesign or relocation approval.
