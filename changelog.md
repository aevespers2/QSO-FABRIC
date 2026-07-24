# Changelog

## Unreleased

### Product
- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Prioritized acceptance of the existing runtime, packaging, canonical output contracts, limit/tamper fixtures, and rollback evidence before new capabilities.
- 2026-07-16 — Retained the runtime-verification priority after reviewing PR #1; owner-wide repository bootstrap and portfolio-governance automation are not part of the current MVP.
- 2026-07-24 — Reaffirmed that repository mutation, portfolio governance, credentials, package publication, deployment, payments, and infrastructure remain outside the runtime authority boundary.

### Architecture
- Added a formal task chain that preserves QSO-GENOMES and QuantumStateObjects as schema/hash-validated dependencies without importing executable authority.
- Classified scheduled cross-repository writes as a separate governance/control-plane concern rather than a QSO runtime-fabric responsibility.
- 2026-07-24 — Added `punchlist.md` to separate runtime reproduction, contradiction/repair lifecycle work, training traces, Planck-probe logs, and authority blockers.

### Implementation
- Existing runtime, tests, and CI remain candidate assets; this changelog does not claim that they satisfy current release gates.
- 2026-07-24 — Converted `Muse Repository Bootstrap` from a six-hour live-write workflow to a manual public-repository audit with read-only permissions, exact-head checkout, disabled credential persistence, isolated evidence, retained artifacts, and a terminal fail-closed gate.
- 2026-07-24 — Made script dry-run the default, required explicit out-of-band write authorization before any mutation, corrected GET-only `404` handling, paginated orientation-issue detection, and added an external report path.
- 2026-07-24 — Added focused bootstrap safety regressions and an exact-head `Bootstrap Safety Validation` workflow.

### Security
- The trusted base contained a scheduled workflow with `contents: write`, `issues: write`, `MUSE_REPO_TOKEN`, persisted checkout credentials, and direct cross-repository default-branch and issue mutations. The live mutation step failed on run `30099853062`.
- The repair removes the schedule, write scopes, broad secret use, and automatic mutation path. The retained manual workflow sets `MUSE_DRY_RUN=true` and `MUSE_WRITE_AUTHORIZED=false` and cannot activate writes.
- The underlying write helpers remain preserved as historical implementation material but fail closed unless a separately approved direct execution explicitly enables them. No credential or execution is approved by this change.

### Release
- The runtime remains blocked until it is reproducible, packaged, licensed, security-tested, checksummed, tied to provenance, and validated against accepted upstream contracts.
- The former release statement that no bootstrap workflow existed was corrected: a contradictory scheduled workflow did exist on the trusted base and is being replaced by a manual read-only audit.
- Exact-head workflow success is evidence only and grants no release, deployment, repository-write, publication, payment, or infrastructure authority.

### FYSA-120
- Applied `CAT-017`, `CAT-022`, `CAT-031`, `CAT-040`, `CAT-052`, `CAT-054`, and `CAT-059` for provenance, reproducible CI, hostile regression testing, reversible repair, least privilege, workflow security, and retained attestation.
- Existing refinement `031-L — portfolio exact-state repair orchestration` covers this repair class.
- Future gaps remain `009-F` for contradiction adjudication, `047-F` for training-trace lineage, and `024-G` for Planck-probe logging.

### Deployment
- No networked or production deployment is in MVP scope.
- No scheduled cross-repository mutation workflow is approved for activation.

## Entry Format
- Date
- Category: Product / Architecture / Added / Changed / Fixed / Security / Release / Deployment
- Summary
- Evidence: issue, PR, commit, workflow, artifact, or deployment record
- Impact and migration notes where applicable
