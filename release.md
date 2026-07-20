# Release Plan

## Current Decision

Status: `BLOCKED — UNVERIFIED RUNTIME, UPSTREAM CONTRACTS, AND GLUING OWNERSHIP`

QSO-FABRIC contains a bounded four-QSO Python runtime, a CLI-style experiment runner, tests, and GitHub Actions workflows. The task chain defines that runtime as a reproducible integration harness, but no runtime release is eligible because P0 remains `READY`; package, license, output-contract versioning, deterministic security/failure fixtures, rollback, provenance, and upstream compatibility gates remain incomplete.

A detailed [`punchlist.md`](punchlist.md) now exists and records the required evidence. Its existence advances planning only; it does not complete any executable release gate.

The repository also has concurrent candidates for a disabled QSIO adapter (PR #16) and a QSO file-format subsystem (PR #17). These introduce unresolved ownership across QSO-FABRIC, QSO-GENOMES, QuantumStateObjects, `qsio-kernel`, and Repository `1`. The [obstruction and gluing analysis](docs/OBSTRUCTION_AND_GLUING.md) records fifteen material incompatibilities and the pairwise and triple-overlap witnesses required before composition.

PR #1, which proposed scheduled owner-wide repository mutation, was closed on 2026-07-16. No repository-bootstrap automation is included, approved, scheduled, or deployed. Its security and reliability findings remain retained as evidence for any future independently chartered control-plane proposal.

## A.L.I.S.T.A.I.R.E. release boundary

A.L.I.S.T.A.I.R.E. is the canonical system; QSO-FABRIC is its bounded collaboration, experiment, and evidence subsystem. This release plan does not authorize QSO-FABRIC to become:

- the autonomous-development control plane;
- the portfolio capability or canonical-state authority;
- the canonical owner of all QSO file formats, genomes, runtime lifecycle, or kernel semantics;
- a credential, signing-key, deployment, payment, or publication authority.

Repository discovery, portfolio planning, branch and pull-request preparation, merge/deployment policy, credentials, capabilities, canonical-state decisions, audit, incident response, signing-key custody, and cross-repository rollback require separate owners, versioned contracts, independent security review, and independent release approval. QSO-FABRIC may provide reports and integrity evidence without inheriting those authorities.

## Versioning

- Scheme: Semantic Versioning after package identity, supported Python versions, license, and contract boundaries are defined.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Event, ledger, freeze-point, limit, and report formats must be explicitly versioned and canonicalized.
- The QSO file-format proposal requires its own owner and versioning decision; its `0.1` label is not an accepted portfolio standard.
- Integration-adapter, expanded-runtime, file-format, and control-plane capabilities must not be folded into the first runtime version merely because candidate pull requests exist.
- Do not tag until the immutable candidate commit satisfies every included gate.

## Release Scope

### Included runtime scope

- Bounded Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit resource limits.
- Append-only hash-chained local event ledger, freeze-point hashes, messages, and final report.
- Package/environment definition and versioned event/ledger/freeze/report contracts.
- Positive, negative, boundary, timeout, tamper, interruption, determinism, consent, and rollback fixtures.
- Read-only hash/version compatibility with accepted QSO-GENOMES and QuantumStateObjects contracts without importing execution authority.
- Documentation of QSO-FABRIC's role, architecture, onboarding, candidate semantics, obstruction ledger, release punch list, release gates, and A.L.I.S.T.A.I.R.E. boundary.

### Explicitly excluded

- Owner-wide repository discovery, scheduled cross-repository mutation, generic planning-file installation, or portfolio-governance issue creation.
- Direct writes to other repositories' default branches.
- Broad owner token distribution or live scheduled mutation.
- Merge, release, deployment, wallet, payment settlement, unrestricted network learning, signing-key, or self-governance authority.
- Automatic inclusion of expanded collectives, Seeker networking, self-learning scaffolds, sprite policy, QSIO adapters, QSO format branches, or other open candidates.
- Treating an envelope, hash, signature, Witness record, accepted routing record, or successful command as permission to act.

## Selected Completed Work

- Product-boundary documentation identifies QSO-FABRIC as the bounded four-QSO integration harness and not the portfolio control plane.
- Architecture documentation defines QSO-FABRIC's role as the deterministic collaboration and evidence subsystem inside A.L.I.S.T.A.I.R.E.
- Candidate governance defines admission, conflict, sequencing, status language, and exact-head evidence rules.
- Developer documentation includes Pages overview, runtime architecture, trust boundaries, onboarding, output-contract notes, failure behavior, and contribution discipline.
- The obstruction and gluing ledger inventories PR #16 and PR #17 conflicts with adjacent repository responsibilities.
- The release punch list decomposes P0–P5, security, privacy, governance, recovery, and documentation evidence.
- PR #1 is closed and preserved only as scope-resolution evidence.
- No executable runtime, adapter, format, expanded collective, or control-plane work is selected for release.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 is `DONE`; included punch-list items have immutable evidence. |
| Scope and authority | PASS | No owner-wide mutation or portfolio-control capability is included in the runtime candidate. |
| System-role clarity | PASS | QSO-FABRIC is documented as a bounded A.L.I.S.T.A.I.R.E. subsystem. |
| Punch-list coverage | PARTIAL | Required work is enumerated; most executable and compatibility items remain incomplete. |
| Candidate sequencing | PARTIAL | Admission and conflict rules exist; PR #16 and PR #17 require explicit selection, ownership, reconciliation, and exact-head evidence. |
| Package/environment | FAIL | Supported Python matrix, package/build definition, dependencies, license, and clean installation are verified. |
| Tests/CI | NO CURRENT RELEASE EVIDENCE | Full pytest and CLI smoke checks pass with retained logs at one accepted immutable head. |
| Determinism/integrity | PARTIAL | Seeded replay and ledger assertions exist; cross-environment canonical hashes, tamper, ordering, timeout, canonicalization, and signature-scope fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Limits and freeze hashes exist; exhaustion, interruption, revocation, recovery, and rollback require evidence. |
| Security and consent | FAIL | Consent policy, secret, dependency, input/path, resource, authority, workflow-token, and supply-chain checks pass on the accepted exact head. |
| Upstream contracts | BLOCKED | Accepted QSO-GENOMES and QuantumStateObjects contracts are validated by immutable version and hash. |
| Format and QSIO gluing | BLOCKED | Canonical owners, field vocabulary, lifecycle/mutation rules, ledger classes, capability boundary, privacy, and recovery are approved with pairwise and triple-overlap fixtures. |
| Documentation | PARTIAL | Core documentation exists; exact-head link validation, Pages-setting review, retained rendered evidence, and accepted operational recovery guidance remain incomplete. |
| Provenance | NO RELEASE EVIDENCE | Commit, Python/OS/tool versions, commands, results, fixture/output hashes, SBOM where applicable, and attestations are retained. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Candidate Admission Gate

An open pull request is not a release input until it:

1. fits the current product directive or has a recorded independent charter;
2. identifies contract, dependency, permission, data, and authority changes;
3. assigns canonical owners for shared fields and lifecycle transitions;
4. rebases and reconciles every shared invariant;
5. produces exact-head deterministic, security, privacy, failure, rollback, and provenance evidence;
6. updates task chain, punch list, release, changelog, migration guidance, and public documentation;
7. receives explicit acceptance.

After combining accepted candidates, all evidence must be regenerated at the final immutable head. Evidence from an earlier branch head cannot be carried forward by assertion.

## Required Gluing Witnesses

The following triple-overlap paths are release-blocking whenever their corresponding candidates are included:

- genome → format → runtime;
- format → runtime → Fabric;
- Fabric → QSIO → Repository `1`;
- freeze → revocation → recovery;
- evidence → interface → correction.

Each witness must include positive, malformed, unsupported-version, stale, replay, wrong-identity, hash-mismatch, authority-denied, partial-failure, and rollback behavior as applicable.

## Artifact Requirements

- Reproducible source archive and Python package artifacts.
- Versioned event, ledger, freeze-point, limit, and report schemas/contracts.
- Positive, negative, boundary, timeout, tamper, determinism, interruption, consent, and rollback fixture bundle.
- Complete test, CLI smoke, static, security, integration, and documentation reports.
- Representative report/ledger, SBOM where applicable, SHA-256 checksums, and provenance manifest.
- Candidate reconciliation record showing accepted, rejected, deferred, and superseded pull requests and their contract effects.
- Field-ownership matrix and obstruction-resolution ledger for included cross-repository contracts.
- Recovery reconstruction manifest pinning contracts, objects, checkpoints, capabilities, and evidence hashes.

## Rollback Criteria

Withdraw or roll back the candidate if seeded runs diverge outside documented nondeterministic fields; ledger tampering is undetected; limits, consent, freeze, revocation, or authority can be bypassed; timeout/interruption corrupts evidence; upstream contracts drift; format ownership remains ambiguous; a local ledger is confused with canonical state; mutation classes become self-authorizing; private objectives or identities are exposed; candidate assumptions conflict; recovery cannot reconstruct the accepted state; or artifact hashes differ.

Restore the prior verified state, revoke any separately issued capabilities, preserve failed-candidate inputs and evidence, and do not delete accepted immutable records during rollback.

## Unresolved Blockers

- P0 remains `READY`; no accepted baseline evidence bundle exists.
- No accepted package/build definition, supported Python matrix, dependency baseline, or license exists.
- Adversarial, timeout, tamper, interruption, rollback, security, consent, checksum, SBOM, and provenance evidence is incomplete or absent on an accepted exact head.
- Upstream compatibility remains blocked by unaccepted QSO-GENOMES and QuantumStateObjects contracts.
- PR #16 and PR #17 require sequencing and ownership decisions; neither is implicitly selected.
- Canonical QSO format/registry ownership, lifecycle and mutation authority, authoritative ledger classes, signing, privacy, retention, capability, and recovery ownership remain unresolved.
- The wider portfolio must retain Repository `0`/Repository `1` or approved successors for orchestration and independent authority rather than silently assigning those roles to Fabric.

## Release Log

- 2026-07-20: Added the obstruction and gluing ledger and release punch list; documented PR #16 and PR #17 as blocked candidates pending ownership and compatibility witnesses. No candidate or authority was accepted.
- 2026-07-19: Documented QSO-FABRIC's A.L.I.S.T.A.I.R.E. subsystem role, autonomous-development boundary, and concurrent-candidate governance; release remained blocked.
- 2026-07-16: Aligned the candidate with the bounded integration-harness directive and excluded owner-wide bootstrap automation from runtime scope.
