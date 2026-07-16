# Changelog

## Unreleased

### Product
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.
- 2026-07-16 — Retained the runtime-verification priority after reviewing draft PR #1; owner-wide repository bootstrap and portfolio-governance automation are not part of the current MVP.
- 2026-07-16 — Required any future repository bootstrap capability to be opt-in, dry-run by default, pull-request based, least-privilege, non-duplicative, and approved for a dedicated control-plane owner before activation.
- 2026-07-16 — Preserved P0–P3 ordering after five additional PR #1 reliability findings; the findings strengthen the existing redesign/relocation decision rather than creating a new product priority.

### Architecture
- Added a formal task chain that preserves QSO-GENOMES and QuantumStateObjects as schema/hash-validated dependencies without importing executable authority.
- Classified scheduled cross-repository writes as a separate governance/control-plane concern rather than a QSO runtime-fabric responsibility.

### Implementation
- Existing runtime, tests, and CI are recorded as candidate assets; this entry does not claim they have passed current release gates.
- Draft PR #1 adds templates and an owner-wide bootstrap workflow, but it remains unaccepted and must not be treated as an implemented portfolio capability.

### Security
- Draft PR #1 currently defaults scheduled execution to live writes, requests a token capable of writing contents and issues across owned repositories, writes directly to default branches, and can create duplicate planning files such as `TASK_CHAIN.md` beside `taskchain.md`; these are blocking review findings.
- Five additional unresolved findings show that the proposal can silently miss organization-owned repositories, duplicate orientation issues after the first issue page, report failed writes as successful after swallowed `404` responses, repeatedly fail on repositories with Issues disabled, and leave partially mutated portfolios when unthrottled write bursts hit secondary limits.

### Release
- The first runtime candidate remains blocked until the harness is reproducible, packaged, licensed, security-tested, checksummed, and tied to provenance.
- Repository bootstrap automation has no release rationale under the current QSO-FABRIC charter and requires redesign or relocation plus explicit approval.

### Deployment
- No networked or production deployment is in MVP scope.
- No scheduled cross-repository mutation workflow is approved for activation.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable
