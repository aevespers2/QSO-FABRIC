# Changelog

## Unreleased

### Product
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.
- 2026-07-16 — Retained the runtime-verification priority after reviewing PR #1; owner-wide repository bootstrap and portfolio-governance automation are not part of the current MVP.
- 2026-07-16 — Required any future repository bootstrap capability to be opt-in, dry-run by default, pull-request based, least-privilege, non-duplicative, and approved for a dedicated control-plane owner before activation.
- 2026-07-16 — Preserved P0–P3 ordering after five additional PR #1 reliability findings; the findings strengthened the redesign/relocation decision rather than creating a new product priority.
- 2026-07-16 — Recorded closure of PR #1. The portfolio-bootstrap proposal is rejected from the current product scope; no automation capability is accepted, deployed, or scheduled.

### Architecture
- Added a formal task chain that preserves QSO-GENOMES and QuantumStateObjects as schema/hash-validated dependencies without importing executable authority.
- Classified scheduled cross-repository writes as a separate governance/control-plane concern rather than a QSO runtime-fabric responsibility.

### Implementation
- Existing runtime, tests, and CI are recorded as candidate assets; this entry does not claim they have passed current release gates.
- Closed PR #1 remains proposal/review history only and must not be treated as an implemented portfolio capability.

### Security
- PR #1 proposed live scheduled writes, a token capable of writing contents and issues across owned repositories, direct default-branch changes, and duplicate planning files such as `TASK_CHAIN.md` beside `taskchain.md`.
- Five retained review findings show that the proposal could silently miss organization-owned repositories, duplicate orientation issues after the first issue page, report failed writes as successful after swallowed `404` responses, repeatedly fail on repositories with Issues disabled, and leave partially mutated portfolios when unthrottled write bursts hit secondary limits.
- Closure prevents these findings from blocking the runtime release, but they remain mandatory requirements for any separately approved successor.

### Documentation
- 2026-07-19 — Added a GitHub Pages project overview, architecture and trust-boundary guide, developer onboarding workflow, and output-contract design notes for the bounded four-QSO runtime.
- 2026-07-19 — Expanded the README with the product boundary, runtime flow, evidence limitations, safety rules, contribution discipline, and direct links to the active task chain and release gates.
- 2026-07-19 — Documented current JSON, event-hash, freeze-point, determinism, compatibility, and migration behavior as unversioned candidate semantics; no stable contract or release readiness is claimed.

### Release
- The first runtime candidate remains blocked until the harness is reproducible, packaged, licensed, security-tested, checksummed, and tied to provenance.
- The former repository-bootstrap scope conflict is resolved by closure and exclusion, not by accepting the proposed capability.

### Deployment
- No networked or production deployment is in MVP scope.
- No scheduled cross-repository mutation workflow is approved for activation.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable
