# Changelog

## Unreleased

### Product
- 2026-07-20 — Preserved the bounded four-QSO runtime as the next release objective while classifying PR #16 (QSIO adapter) and PR #17 (QSO file-format subsystem) as separate unaccepted candidates.
- 2026-07-20 — Clarified that QSO-FABRIC is not the canonical owner of portfolio-wide QSO serialization, lifecycle, capability, signing, or canonical-state semantics unless the architecture explicitly assigns those responsibilities.
- 2026-07-19 — Defined A.L.I.S.T.A.I.R.E. as the canonical system and QSO-FABRIC as its bounded collaboration, experiment, and evidence subsystem; no portfolio-control authority was added.
- 2026-07-19 — Preserved P0–P3 runtime-verification priority while documenting how the harness supports increasingly autonomous development through reproducible evidence rather than implicit authority expansion.
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.
- 2026-07-16 — Recorded closure of PR #1. The portfolio-bootstrap proposal is rejected from the current product scope; no automation capability is accepted, deployed, or scheduled.

### Architecture
- 2026-07-20 — Added a fifteen-item obstruction ledger spanning canonical format ownership, directory identity, field ownership, canonicalization, integrity scope, mutation authority, composition resolution, QSIO mapping, ledger classes, freeze/recovery semantics, candidate bases, privacy, capabilities, contradiction records, and reconstruction.
- 2026-07-20 — Added pairwise gluing maps for genome → format, format → runtime, runtime → Fabric, Fabric → QSIO, QSIO → Repository `1`, and Fabric → review interfaces.
- 2026-07-20 — Added required triple-overlap witnesses for genome → format → runtime, format → runtime → Fabric, Fabric → QSIO → Repository `1`, freeze → revocation → recovery, and evidence → interface → correction.
- 2026-07-20 — Documented the lowest-coupling sequence: verify the baseline, assign owners, stabilize vocabulary and minimal envelope, validate upstream/runtime/Fabric edges, then admit QSIO and broader serialization capabilities.
- 2026-07-19 — Added the portfolio-level context, capability ladder, continuous-improvement loop, authority separation, and required control-plane decision for A.L.I.S.T.A.I.R.E.
- 2026-07-19 — Added concurrent-candidate governance for baseline verification, documentation, adapters, expanded runtimes, control planes, and safety repairs.
- 2026-07-19 — Required exact-head reconciliation before combining candidates that alter identities, event/freeze semantics, message topology, consent, dependencies, authority, packaging, or release scope.

### Implementation
- Existing runtime, tests, workflows, and consent policy are recorded as candidate assets; these entries do not claim they have passed current release gates.
- PR #16 remains a disabled QSIO integration candidate.
- PR #17 remains a QSO format and contract candidate.
- Open pull requests remain candidate branches and must not be treated as cumulative accepted architecture.
- Closed PR #1 remains proposal/review history only and must not be treated as an implemented portfolio capability.
- No runtime, schema, adapter, serialization, signing, credential, network, release, publication, or deployment behavior changed through this documentation milestone.

### Security
- 2026-07-20 — Clarified that envelopes, hashes, signatures, Witness records, immutable routing records, successful validation, or successful execution do not independently grant authority.
- 2026-07-20 — Required separate capability references, fail-closed ownership, privacy classification, signing-key custody decisions, no-automatic-unlock freeze behavior, and bounded reconstruction evidence before cross-repository activation.
- 2026-07-19 — Added documentation requirements for consent constraints, unapproved-authority shutdown, candidate permission disclosure, least privilege, audit, exact-head evidence, and rollback.
- PR #1 proposed live scheduled writes, a token capable of writing contents and issues across owned repositories, direct default-branch changes, and duplicate planning files such as `TASK_CHAIN.md` beside `taskchain.md`.
- Closure prevents those findings from blocking the runtime release, but they remain mandatory requirements for any separately approved successor.

### Documentation
- 2026-07-20 — Added `docs/OBSTRUCTION_AND_GLUING.md` with local-section inventory, obstruction ledger, gluing maps, triple-overlap witnesses, sequencing recommendation, release effect, and approval questions.
- 2026-07-20 — Added `punchlist.md` covering P0–P5, security, privacy, governance, recovery, documentation evidence, and release stop conditions.
- 2026-07-20 — Reconciled `README.md`, `taskchain.md`, `release.md`, and this changelog with PR #16 and PR #17 without accepting either candidate.
- 2026-07-19 — Added a GitHub Pages project overview, architecture and trust-boundary guide, developer onboarding workflow, and output-contract design notes for the bounded four-QSO runtime.
- 2026-07-19 — Added `docs/ALISTAIRE_ROLE.md` to define QSO-FABRIC's subsystem role, autonomous-development ladder, portfolio interfaces, invariants, and unresolved control-plane ownership decision.
- 2026-07-19 — Added `docs/CANDIDATE_GOVERNANCE.md` to distinguish implemented, verified, accepted, and released states and to govern concurrent architecture proposals.

### Release
- The first runtime candidate remains blocked until the harness is reproducible, packaged, licensed, security-tested, checksummed, and tied to provenance.
- Format and QSIO integration remain blocked until ownership, field vocabulary, lifecycle/mutation semantics, ledger classes, capability separation, privacy, signing, and recovery are approved with deterministic witnesses.
- Documentation and obstruction visibility advanced, but no executable candidate, adapter, format, expanded runtime, consent repair, or autonomous-development control plane was selected for release.
- The former repository-bootstrap scope conflict remains resolved by closure and exclusion, not by accepting the proposed capability.

### Deployment
- No networked or production deployment is in MVP scope.
- No scheduled cross-repository mutation workflow is approved for activation.
- No merge, release, deployment, publication, signing, or portfolio-control authority is granted by this documentation.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable
