# Changelog

## Unreleased

### Product

- 2026-07-16 — Established QSO-FABRIC as the bounded, deterministic four-QSO integration harness rather than a general autonomous-agent platform.
- 2026-07-16 — Excluded owner-wide repository bootstrap and portfolio-governance automation from the current runtime scope.
- 2026-07-22 — Recorded PR #19 as an interacting QSO format implementation lineage rather than silently treating it as accepted repository direction.
- 2026-07-23 — Clarified two candidate release slices: the bounded four-QSO research harness and a separately governed QSO format development/conformance package.

### Architecture

- Added the candidate QSO format subsystem with common envelope, family schemas, registries, profiles, composition references, canonicalization, package/stream specifications, migration, conversions, and reference tooling.
- Added a source-preserving four-QSO report conversion path producing separate `QSO-REPORT` and `QSO-PROVENANCE` objects.
- Documented the full parsing, envelope, payload, registry/profile, graph, canonicalization, package/stream, conversion, independent-consumer, and separate-admission architecture.
- Distinguished QSO-FABRIC-owned experiment/event/freeze semantics from still-unresolved neutral envelope, canonicalization, namespace, registry, mapping, and fixture stewardship.
- Made PR #15/#19 reconciliation a blocking repository-direction gate.

### Added

- Polished root and subsystem overviews with reading paths and local commands.
- Expanded architecture, governance, security, implementation, roadmap, and conversion documentation.
- Added `quantum-state-objects/docs/CONVERSION-BOUNDARY.md` with a diagram, prose alternative, identity model, trust boundary, failure posture, and reviewer checklist.
- Added conversion registry entries and tests for the bounded four-QSO report adapter.
- Added package and hostile-input fixtures, reference validation, hashing, packing, unpacking, migration, conversion, and registry utilities on PR #19.

### Changed

- Replaced the stale runtime-only task chain with one that tracks the runtime baseline, PR #15/#19 reconciliation, format ownership, conversion hardening, security fixtures, compatibility, and documentation-only release evidence.
- Replaced the stale release plan and obsolete candidate-head claims with current lineage, two-slice, security, conversion, provenance, recovery, and approval gates.
- Clarified that conversion determinism depends on source bytes, source-path string, explicit timestamp, converter implementation, and serialization rules.
- Clarified that registry states such as `ready` and `converted` describe local implementation state, not portfolio acceptance.

### Security

- Preserved strict package preflight, path/member rejection, manifest equality, streamed decompression ceilings, and safe extraction behavior.
- Documented threats from malformed input, version downgrade, identity/reference substitution, stale or revoked records, forged or unauthorized signatures, archive abuse, conversion evidence loss, self-executing authority records, sensitive public output, interrupted writes, and compromised validation supply chains.
- Documented remaining work for strict conversion parsing, event-chain recomputation, atomic output, nested/polyglot archives, signed manifests, key custody, fuzzing, SBOMs, reproducible builds, and independent security review.
- Retained closed PR #1 security and reliability findings as rejected-proposal evidence; no cross-repository mutation capability is accepted.

### Documentation

- Aligned README, architecture, governance, security, onboarding, task chain, release plan, and changelog with the implemented PR #19 surface and the owning PR #15 documentation lineage.
- Added explicit non-authority statements separating validation, conversion, packaging, admission, capability, canonical disposition, release, publication, and deployment.
- Added Mermaid diagrams with prose alternatives for subsystem and conversion architecture.

### Release

- Release remains blocked pending PR #15/#19 reconciliation, package and license decisions, neutral and repository-local ownership, complete conformance and security evidence, privacy/licensing/accessibility review, recovery exercises, and named human approval.
- Passing workflows validate only their exact submitted source and do not accept the format, authorize mutation, or approve release.

### Deployment

- No networked or production deployment is in scope.
- No scheduled cross-repository mutation, credential use, signing, canonical-state service, or runtime authority is approved.

## Entry format

Each future entry should include:

- date;
- category;
- concise summary;
- evidence source such as PR, commit, workflow, fixture, or artifact;
- implementation and documentation impact;
- migration, correction, revocation, or rollback notes; and
- explicit authority and release effect.