# Changelog

## Unreleased

### Product
- 2026-07-19 — Defined A.L.I.S.T.A.I.R.E. as the canonical system and QSO-FABRIC as its bounded collaboration, experiment, and evidence subsystem; no portfolio-control authority was added.
- 2026-07-19 — Preserved P0–P3 runtime-verification priority while documenting how the harness supports increasingly autonomous development through reproducible evidence rather than implicit authority expansion.
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.
- 2026-07-16 — Retained the runtime-verification priority after reviewing PR #1; owner-wide repository bootstrap and portfolio-governance automation are not part of the current MVP.
- 2026-07-16 — Required any future repository bootstrap capability to be opt-in, dry-run by default, pull-request based, least-privilege, non-duplicative, and approved for a dedicated control-plane owner before activation.
- 2026-07-16 — Preserved P0–P3 ordering after five additional PR #1 reliability findings; the findings strengthened the redesign/relocation decision rather than creating a new product priority.
- 2026-07-16 — Recorded closure of PR #1. The portfolio-bootstrap proposal is rejected from the current product scope; no automation capability is accepted, deployed, or scheduled.

### Architecture
- 2026-07-19 — Added the portfolio-level context, capability ladder, continuous-improvement loop, authority separation, and required control-plane decision for A.L.I.S.T.A.I.R.E.
- 2026-07-19 — Added concurrent-candidate governance for baseline verification, documentation, adapters, expanded runtimes, control planes, and safety repairs.
- 2026-07-19 — Required exact-head reconciliation before combining candidates that alter identities, event/freeze semantics, message topology, consent, dependencies, authority, packaging, or release scope.
- Added a formal task chain that preserves QSO-GENOMES and QuantumStateObjects as schema/hash-validated dependencies without importing executable authority.
- Classified scheduled cross-repository writes as a separate governance/control-plane concern rather than a QSO runtime-fabric responsibility.

### Implementation
- Existing runtime, tests, workflows, and consent policy are recorded as candidate assets; these entries do not claim they have passed current release gates.
- Open pull requests remain candidate branches and must not be treated as cumulative accepted architecture.
- Closed PR #1 remains proposal/review history only and must not be treated as an implemented portfolio capability.

### Security
- 2026-07-19 — Added documentation requirements for consent constraints, unapproved-authority shutdown, candidate permission disclosure, least privilege, audit, exact-head evidence, and rollback.
- PR #1 proposed live scheduled writes, a token capable of writing contents and issues across owned repositories, direct default-branch changes, and duplicate planning files such as `TASK_CHAIN.md` beside `taskchain.md`.
- Five retained review findings show that the proposal could silently miss organization-owned repositories, duplicate orientation issues after the first issue page, report failed writes as successful after swallowed `404` responses, repeatedly fail on repositories with Issues disabled, and leave partially mutated portfolios when unthrottled write bursts hit secondary limits.
- Closure prevents these findings from blocking the runtime release, but they remain mandatory requirements for any separately approved successor.

### Documentation
- 2026-07-19 — Added a GitHub Pages project overview, architecture and trust-boundary guide, developer onboarding workflow, and output-contract design notes for the bounded four-QSO runtime.
- 2026-07-19 — Expanded the README with the product boundary, runtime flow, evidence limitations, safety rules, contribution discipline, and direct links to the active task chain and release gates.
- 2026-07-19 — Documented current JSON, event-hash, freeze-point, determinism, compatibility, and migration behavior as unversioned candidate semantics; no stable contract or release readiness is claimed.
- 2026-07-19 — Added `docs/ALISTAIRE_ROLE.md` to define QSO-FABRIC's subsystem role, autonomous-development ladder, portfolio interfaces, invariants, and unresolved control-plane ownership decision.
- 2026-07-19 — Added `docs/CANDIDATE_GOVERNANCE.md` to distinguish implemented, verified, accepted, and released states and to govern concurrent architecture proposals.
- 2026-07-19 — Reconciled `README.md`, `docs/ARCHITECTURE.md`, `taskchain.md`, `release.md`, and `changelog.md` around one scope and maturity model.

### Release
- The first runtime candidate remains blocked until the harness is reproducible, packaged, licensed, security-tested, checksummed, and tied to provenance.
- Documentation and system-role clarity advanced, but no executable candidate, adapter, expanded runtime, consent repair, or autonomous-development control plane was selected for release.
- The former repository-bootstrap scope conflict is resolved by closure and exclusion, not by accepting the proposed capability.

### Deployment
- No networked or production deployment is in MVP scope.
- No scheduled cross-repository mutation workflow is approved for activation.
- No merge, release, deployment, or portfolio-control authority is granted by the A.L.I.S.T.A.I.R.E. alignment documentation.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable
