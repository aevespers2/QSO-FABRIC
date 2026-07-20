# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME AND UPSTREAM CONTRACTS`

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, three pytest cases, and GitHub Actions workflows. The task chain defines that runtime as a reproducible integration harness, but no release is eligible because P0 remains `READY`, `punchlist.md` is absent, current `main` head `eaf70fe46910387c9253c2600d0c1a34088b8296` has no reported combined commit-status checks, and package, license, contract versioning, deterministic security/failure fixtures, rollback, provenance, and upstream compatibility gates remain incomplete.

The repository now also contains a consent-capacity policy and enforcement workflow. Their presence is not a completed security gate. An open repair candidate documents exact-head improvements, but no unmerged branch is selected for release and every final candidate must be revalidated after reconciliation.

PR #1, which proposed scheduled owner-wide repository mutation, was closed on 2026-07-16. The scope conflict is therefore resolved for the current runtime candidate by exclusion, not by accepting the proposed capability. No repository-bootstrap automation is included, approved, scheduled, or deployed. Its security and reliability findings remain retained as evidence for any future independently chartered control-plane proposal.

## A.L.I.S.T.A.I.R.E. release boundary

A.L.I.S.T.A.I.R.E. is the canonical system; QSO-FABRIC is its bounded collaboration, experiment, and evidence subsystem. This release plan does not authorize QSO-FABRIC to become the autonomous-development control plane.

Repository discovery, portfolio planning, branch and pull-request preparation, merge/deployment policy, credentials, audit, incident response, and cross-repository rollback require a separate product owner, versioned contracts, independent security review, and independent release approval. QSO-FABRIC may provide reports and integrity evidence to that future boundary without inheriting its authority.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, and report formats must be explicitly versioned and canonicalized.
- Integration-adapter, expanded-runtime, and control-plane capabilities must not be folded into the first runtime version merely because candidate pull requests exist.
- Any future repository-bootstrap or portfolio-governance automation must be versioned and released independently from the QSO-FABRIC runtime after separate approval.
- Do not tag until the immutable candidate commit satisfies every included gate.

## Release Scope

### Included runtime scope

- Bounded Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit resource limits.
- Append-only hash-chained event ledger, freeze-point hashes, messages, and final report.
- Package/environment definition and versioned event/ledger/freeze/report contracts.
- Positive, negative, boundary, timeout, tamper, interruption, determinism, and rollback fixtures.
- Read-only hash/version compatibility with QSO-GENOMES and QuantumStateObjects without importing execution authority.
- Documentation of QSO-FABRIC's role, architecture, onboarding, candidate semantics, release gates, and A.L.I.S.T.A.I.R.E. boundary.

### Explicitly excluded

- Owner-wide repository discovery, scheduled cross-repository mutation, generic planning-file installation, or portfolio-governance issue creation.
- Direct writes to other repositories' default branches.
- Broad owner token distribution or activation of live scheduled mutations.
- Merge, release, deployment, wallet, payment-settlement, unrestricted network-learning, or self-governance authority.
- Automatic inclusion of expanded collectives, Seeker networking, self-learning scaffolds, sprite policy, QSIO adapters, or other open candidate branches.

## Selected Completed Work

- Selected as governance documentation: the product-boundary decision that QSO-FABRIC is the bounded four-QSO integration harness and not the portfolio control plane.
- Selected as architecture documentation: QSO-FABRIC's role as the deterministic collaboration and evidence subsystem inside A.L.I.S.T.A.I.R.E., including a capability ladder and explicit control-plane separation.
- Selected as candidate governance: admission, conflict, sequencing, status-language, and exact-head evidence rules for concurrent pull requests.
- Selected as developer documentation: Pages overview, runtime architecture, trust boundaries, onboarding, output-contract notes, failure behavior, and contribution discipline.
- Selected as scope-resolution evidence: closure of PR #1 and preservation of its security/reliability findings without accepting the proposed capability.
- No executable runtime work is selected for release. The runtime, tests, workflows, consent policy, and open candidates remain candidate inputs because no task is `DONE` and no complete evidence bundle verifies an accepted immutable head.

## Planned Changelog Entries

- `Added`: verified bounded four-QSO harness, package entry point, versioned output contracts, and fixture suite.
- `Security`: limits, timeout, consent, untrusted input, path, command/network/credential, repository-write, dependency, workflow, and supply-chain findings.
- `Fixed`: determinism, ledger, freeze, timeout, message-cap, interruption, and rollback defects.
- `Documentation`: supported environment, contracts, limits, trust boundaries, A.L.I.S.T.A.I.R.E. subsystem role, candidate governance, commands, failures, recovery, and excluded control-plane scope.
- `Release`: package/source artifacts, reports, SBOM where applicable, checksums, provenance, and approval.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 is `DONE`; `punchlist.md` exists and included P1-P3 work has evidence. |
| Scope and authority | PASS | PR #1 is closed; no owner-wide mutation or portfolio-control capability is included in the runtime candidate. |
| System-role clarity | PASS | QSO-FABRIC is documented as a bounded A.L.I.S.T.A.I.R.E. subsystem; autonomous-development control-plane authority remains separate and unassigned. |
| Candidate sequencing | PARTIAL | Admission and conflict rules are documented; open candidates still require explicit selection, reconciliation, and exact-head evidence. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | NO CURRENT EVIDENCE | Full pytest and CLI smoke checks pass with retained logs at one immutable candidate head. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, recovery, and rollback require evidence. |
| Security and consent | FAIL | Consent policy semantics, secret, dependency, input/path, resource, command/network/credential, repository-write, workflow-token, and supply-chain checks pass on the accepted exact head. |
| Integration contracts | BLOCKED | Published QSO-GENOMES manifest and runnable QuantumStateObjects baseline are validated by version and hash. |
| Documentation | PARTIAL | Architecture, onboarding, candidate output semantics, system role, and candidate governance are documented; supported matrix, accepted contracts, retained validation, operational recovery, and released artifact instructions remain incomplete. |
| Provenance | NO EVIDENCE | Commit, Python/OS/tool versions, commands, results, fixture/output hashes, SBOM, and attestations are retained. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Candidate Admission Gate

An open pull request is not a release input until it:

1. fits the current product directive or has a recorded independent charter;
2. identifies contract, dependency, permission, and authority changes;
3. rebases and reconciles every shared invariant;
4. produces exact-head deterministic, security, failure, rollback, and provenance evidence;
5. updates task, release, changelog, and public documentation;
6. receives explicit acceptance.

After combining accepted candidates, all evidence must be regenerated at the final immutable head. Evidence from an earlier branch head cannot be carried forward by assertion.

## Artifact Requirements

- Reproducible source archive and Python package artifacts.
- Versioned event, ledger, freeze-point, limit, and report schemas/contracts.
- Positive, negative, boundary, timeout, tamper, determinism, interruption, and rollback fixture bundle.
- Complete test, CLI smoke, static, security, consent, integration, and documentation reports.
- Representative report/ledger, SBOM where applicable, SHA-256 checksums, and provenance manifest.
- Candidate reconciliation record showing accepted, rejected, deferred, and superseded pull requests and their contract effects.
- If portfolio bootstrap automation is proposed again in a separate product: opt-in repository manifest, dry-run evidence, per-repository pull-request flow, correct user/organization discovery, paginated duplicate detection, explicit write-error propagation, disabled-feature handling, mutation throttling/retry/checkpointing, least-privilege token matrix, audit/revocation/rollback design, duplicate-file prevention tests, and independent approval record.

## Rollback Criteria

Withdraw or roll back the runtime candidate if seeded runs diverge, ledger tampering is undetected, limits can be bypassed, timeout/interruption corrupts evidence, freeze hashes are unstable, consent or authority constraints can be bypassed, untrusted input gains authority, upstream contracts drift, documented commands fail, severe security findings remain, candidate assumptions conflict, or artifact hashes differ. If a future control-plane proposal is separately approved, disable and revoke it immediately after any unapproved write, non-opted-in target, protected/default-branch mutation, duplicate source of truth, silently skipped target, suppressed write failure, lost audit evidence, untracked partial run, or token-scope violation. Restore the prior verified state and preserve failed-candidate inputs, logs, reports, hashes, and affected-repository inventory.

## Unresolved Blockers

- P0 remains `READY`; `punchlist.md` and accepted Builder evidence are absent.
- Current `main` head `eaf70fe46910387c9253c2600d0c1a34088b8296` has no reported combined commit-status checks, clean-environment pytest report, or CLI smoke report.
- No package/build definition, supported Python matrix, dependency baseline, or license is accepted.
- Adversarial, timeout, tamper, interruption, rollback, security, consent, checksum, SBOM, and provenance evidence is incomplete or absent on an accepted exact head.
- Upstream compatibility is blocked by the unaccepted QSO-GENOMES set and non-runnable QuantumStateObjects package.
- Multiple open architecture candidates require sequencing and reconciliation; none is implicitly selected.
- The wider portfolio has not identified and approved the dedicated autonomous-development control-plane owner.

## Archived Control-Plane Findings

PR #1 was closed and is not a current release blocker. Its retained findings cover broad-token/live-schedule/direct-write authority, duplicate planning files, incorrect organization discovery, non-paginated idempotency checks, swallowed write failures, disabled-Issues handling, and unsafe unthrottled partial mutation. Any successor requires a separate product charter and approval.

## Release Log

- 2026-07-19: Documented QSO-FABRIC's A.L.I.S.T.A.I.R.E. subsystem role, autonomous-development boundary, and concurrent-candidate governance; release remained blocked and no candidate was accepted.
- 2026-07-19: Updated the baseline reference to current `main` head and retained `NO CURRENT EVIDENCE` for combined commit-status checks.
- 2026-07-16: Aligned the candidate with the bounded integration-harness directive; release remained blocked pending reproducible runtime and upstream-contract evidence.
- 2026-07-16: Reviewed PR #1, excluded owner-wide bootstrap automation from the runtime scope, and recorded its security and reliability findings.
- 2026-07-16: PR #1 was closed. Marked the runtime scope/authority gate `PASS` by exclusion; no automation capability was accepted, and the runtime release remains blocked by its original evidence and dependency gates.
