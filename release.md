# Release Plan

## Current decision

**Status:** `BLOCKED — REPOSITORY LINEAGES, OWNERSHIP, AND RELEASE EVIDENCE UNRESOLVED`

QSO-FABRIC contains:

1. a bounded four-QSO Python research runtime and experiment runner;
2. a candidate QSO format subsystem with schemas, registries, profiles, reference tools, packaging, migration, conversions, and tests; and
3. two open lineages that have not yet been reconciled:
   - PR #15 for documentation, architecture, onboarding, and format governance;
   - PR #19 for implementation and conformance work.

No release is eligible until one resulting candidate preserves both histories, resolves their contradictions, passes exact-head validation, and receives explicit release approval.

## Release identity

- Versioning scheme: Semantic Versioning only after package identity, supported Python versions, license, compatibility policy, and contract boundaries are accepted.
- Earliest bounded runtime candidate: `0.1.0-alpha.1`.
- The QSO format subsystem may require a separately versioned package or profile; repository colocation does not require one release identity.
- Runtime event, ledger, freeze-point, limit, and report contracts must be versioned independently from generic QSO envelope, package, conversion, and registry contracts.
- Do not tag from an unreconciled PR head or reuse passing evidence from a superseded head.

## Proposed release slices

### Slice A — bounded four-QSO research harness

Potentially included:

- Atlas, Nova, Orion, and Lyra experiment with deterministic seeds and explicit limits;
- append-only event ledger, freeze-point hashes, bounded messages, and final report;
- package/environment definition and supported Python matrix;
- versioned runtime output contracts;
- positive, negative, boundary, timeout, tamper, interruption, determinism, and rollback fixtures; and
- read-only compatibility checks against accepted external sources.

### Slice B — QSO format development/conformance package

Potentially included only after separate ownership and package decisions:

- common envelope and family schemas;
- registries and bounded profiles;
- canonicalization and hashing vectors;
- safe package creation and preflight extraction;
- source-preserving conversion tools and provenance records;
- migration and interoperability utilities; and
- conformance, hostile-input, conversion, and package tests.

Slice B must not be presented as the neutral portfolio standard unless neutral stewardship and cross-repository acceptance are separately recorded.

## Explicitly excluded

- owner-wide repository discovery or mutation;
- direct writes to other repositories' default branches;
- broad owner tokens or live scheduled automation;
- autonomous self-modification or self-approval;
- credential, capability, wallet, payment, signing-key, or canonical-state authority;
- execution of embedded package resources during validation;
- production networking, deployment, or portfolio control-plane behavior; and
- claims of sentience, consciousness, AGI, or physical quantum execution.

## Reconciliation gate

Before release review:

```text
freeze PR #15 and PR #19 exact heads
→ compare project scope and architecture
→ classify every implementation and document source
→ resolve format ownership and canonicalization contradictions
→ align README, Pages, onboarding, task chain, release plan, and changelog
→ preserve both histories in an ancestry-aware candidate
→ rerun runtime, format, security, documentation, and consent checks
→ independently review the resulting immutable head
```

A mergeable branch or passing workflow is not a substitute for this sequence.

## Acceptance gates

| Gate | Status | Requirement |
|---|---|---|
| Repository direction | BLOCKED | PR #15 and PR #19 are reconciled and locally dispositioned. |
| Scope and authority | PARTIAL | Cross-repository bootstrap is excluded; format ownership and operational non-authority still require acceptance. |
| Package and license | FAIL | Package identities, supported Python versions, build definitions, license, notices, and support routes are approved. |
| Runtime tests | REVIEW | Exact-head runtime, deterministic replay, limits, ledger, freeze, timeout, interruption, and rollback evidence pass on the reconciled source. |
| Format conformance | REVIEW | Schemas, registries, profiles, canonicalization, conversion, migration, package, hostile, and cross-language fixtures pass at the reconciled head. |
| Conversion integrity | PARTIAL | Source preservation and local tests exist; strict source parsing, event-chain recomputation, atomic output, privacy, correction, revocation, and rollback remain. |
| Package security | PARTIAL | Strong preflight exists; nested/polyglot policy, signed manifests, storage races, fuzzing, and independent security review remain. |
| Signatures and custody | FAIL | Signature domains, signer authorization, key generation/storage/rotation/revocation/recovery, and trusted-time policy are approved and tested. |
| Integration contracts | BLOCKED | Neutral and repository-local owners, mappings, versions, and pairwise/triple-overlap fixtures are accepted. |
| Documentation | REVIEW | Project overview, architecture, diagrams, onboarding, operations, task chain, release plan, changelog, and limitations align at one head. |
| Privacy/licensing/accessibility | FAIL | Data classes, retention, redaction, licenses, public-output review, and rendered accessibility are independently approved. |
| Provenance | PARTIAL | Current workflows retain evidence, but one complete reconciled release bundle and resulting-head verification are absent. |
| Recovery and rollback | FAIL | Interrupted operations, package/conversion rollback, correction/revocation propagation, and restored-state verification are rehearsed. |
| Human approval | PENDING | Named repository, security, release, signing, publication, and deployment owners approve the bounded slice. |

## Required release evidence

- exact repository, branch, commit, base, and reconciliation provenance;
- Python, OS, build, dependency, and tool versions;
- commands, results, logs, tests, fixtures, and failure reports;
- runtime outputs and hashes;
- schema, registry, profile, canonicalization, conversion, and package fixture bundle;
- SBOM and reproducible source/package artifacts where applicable;
- licenses, notices, support and security routes;
- privacy and public-output assessment;
- security review and unresolved-risk register;
- correction, revocation, rollback, and recovery exercise evidence;
- SHA-256 checksums and signatures when approved; and
- explicit release disposition with scope and expiry.

## Rollback criteria

Withdraw or roll back a candidate if:

- seeded runs diverge unexpectedly;
- ledger tampering or package drift is undetected;
- limits, path safety, or decompression ceilings can be bypassed;
- conversion changes or loses source/provenance identity;
- canonicalization differs across supported implementations;
- signatures validate under an unauthorized or revoked identity;
- stale, corrected, revoked, or superseded records remain accepted;
- interruption or retry leaves partial output represented as complete;
- documentation disagrees with implementation or repository direction;
- privacy, licensing, or security findings remain unresolved; or
- artifact hashes or resulting-head evidence cannot be reproduced.

Restore the prior verified generation, preserve the failed candidate and evidence, invalidate affected claims and caches, and require independent verification before reconsideration.

## Release log

- 2026-07-16 — Established the bounded four-QSO integration-harness directive and excluded owner-wide repository bootstrap automation.
- 2026-07-22 — PR #19 introduced the broad format implementation, package hardening, conversion registry, and conformance tests as an interacting lineage.
- 2026-07-23 — Replaced stale runtime-only release assertions with a two-slice plan and explicit PR #15/#19 reconciliation, conversion, ownership, security, provenance, and recovery gates.

No release, publication, signing, deployment, or operational authority is approved by this plan.