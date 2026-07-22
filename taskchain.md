# Task Chain

States: `PROPOSED` · `READY` · `IN PROGRESS` · `BLOCKED` · `REVIEW` · `DONE`

## Product directive

- **Primary objective:** stabilize the bounded four-QSO experiment as a reproducible integration harness.
- **Secondary candidate:** review and reconcile the QSO format subsystem implemented on PR #19 without allowing it to silently redefine repository purpose or portfolio-wide ownership.
- **User outcome:** a researcher can run Atlas, Nova, Orion, and Lyra with a deterministic seed and explicit limits; inspect the event ledger, freeze-point hashes, messages, and report; validate or package candidate QSO objects; and convert a report while preserving its source and provenance.
- **MVP scope:** the existing Python runtime and runner; package/environment definition; license; versioned event/ledger/freeze/report contracts; deterministic, boundary, timeout, tamper, conversion, package, interruption, and rollback fixtures; retained CI evidence; and read-only compatibility with accepted external contracts.
- **Priority:** verification, security, reconciliation, and ownership decisions precede additional learning, data acquisition, visualization, economic behavior, autonomous mutation, or portfolio administration.
- **Non-goals:** autonomous internet learning, self-authorization, production orchestration, credentialed agents, payment settlement, owner-wide repository mutation, or claims of sentience or physical quantum execution.

## Current repository lineages

| Lineage | Purpose | Current treatment |
|---|---|---|
| PR #15 | Project overview, architecture, onboarding, format governance, task/release alignment | Owning documentation candidate; requires branch reconciliation and architecture decisions |
| PR #19 | Implemented schemas, registries, profiles, tools, packaging, conversion, and tests | Interacting implementation candidate; requires reconciliation with PR #15 |
| Closed PR #1 | Owner-wide repository bootstrap proposal | Excluded from runtime and format scope; retained as rejected-proposal evidence |

Neither open lineage is the accepted repository direction until an explicit reconciliation and resulting-head review is complete.

## Active chain

| Priority | Task | Owner | Depends on | Status | Acceptance criteria |
|---|---|---|---|---|---|
| P0 | Freeze and reproduce the current four-QSO runtime baseline | Architect | — | READY | Source, tests, workflow, limits, ledger, freeze behavior, commands, results, and rollback notes are verified at one immutable commit. |
| P1 | Reconcile PR #15 and PR #19 without losing provenance | Architect + maintainers | P0 | REVIEW | One ancestry-preserving candidate aligns README, Pages, architecture, format ownership, onboarding, `taskchain.md`, `release.md`, `changelog.md`, tests, and rollback evidence. |
| P2 | Define accepted repository and neutral format boundaries | Architecture review | P1 | BLOCKED | QSO-FABRIC-owned experiment/event/freeze semantics are separated from neutral envelope, canonicalization, namespace, registry, mapping, and fixture stewardship. |
| P3 | Stabilize package, license, supported environment, and versioned output contracts | QSOBuilder | P1–P2 | PROPOSED | Clean installation works; supported Python versions and license are declared; runtime and format contracts have explicit versions and limits. |
| P4 | Harden conversion and provenance adapters | QSOBuilder | P2–P3 | PROPOSED | Source bytes are preserved; strict source parsing, schema validation, event-chain verification, atomic outputs, deterministic complete-input fixtures, privacy, correction, revocation, and rollback checks pass. |
| P5 | Publish deterministic security and failure fixtures | QSOBuilder | P3–P4 | PROPOSED | Positive, malformed, boundary, timeout, tamper, package, conversion, interruption, retry, replay, correction, revocation, and rollback fixtures pass with retained hashes and reports. |
| P6 | Validate upstream and downstream compatibility without importing authority | Independent verifier | Accepted genome/runtime/contract sources | BLOCKED | External contracts are checked by exact version, mapping, and digest; missing, incompatible, stale, or unsupported artifacts fail closed; no external code or authority is imported implicitly. |
| P7 | Prepare a documentation-only release evidence bundle | Release reviewer | P0–P6 | BLOCKED | Exact source, commands, tools, artifacts, licenses, SBOM where applicable, checksums, limitations, rollback, and explicit approval are complete. |

## Conversion-specific review path

```text
preserve source bytes
→ validate source shape and version
→ bind source identity and digest
→ apply explicit conversion mapping and timestamp
→ emit separate report and provenance identities
→ verify outputs independently
→ retain correction, revocation, and rollback paths
→ request separate admission or disposition when needed
```

Conversion success does not move an artifact to an accepted runtime, policy, or authority state.

## Closed scope conflict: repository bootstrap automation

PR #1 proposed scheduled owner-wide automation that would write generic Markdown files and issues to other repositories using a broad token. It was closed on 2026-07-16. No portfolio-bootstrap capability is accepted, scheduled, deployed, or part of the QSO-FABRIC runtime or format MVP.

Any successor must be independently chartered, opt-in per repository, dry-run by default, pull-request based, least-privilege, idempotent across paginated state, explicit about every failed write, safe for disabled features, throttled, checkpointed, reversible, and separate from QSO-FABRIC unless ownership is formally approved.

## Builder rules

Execute only the highest-priority unblocked task. Preserve the bounded runtime and source artifacts while adding evidence. Do not widen scope to networking, credentials, external learning, payments, automatic mutation, cross-repository governance, release, or deployment without a recorded approval and revised product directive.

Every change must update the applicable documentation, tests, fixtures, exact-source evidence, failure posture, and rollback target.

## Builder log

Record commits, Python/tool versions, commands and results, workflow URLs, seeds, fixture and artifact hashes, failures, limits, source and output identities, rollback evidence, and follow-ups.

- 2026-07-16 — Product review retained the runtime-verification priority and excluded owner-wide portfolio-bootstrap automation from QSO-FABRIC.
- 2026-07-22 — PR #19 expanded the candidate QSO format subsystem with registries, profiles, schemas, packaging, migration, conversion, and hostile-input tests.
- 2026-07-23 — Documentation aligned the runtime and format lineages, added the conversion/provenance boundary, and made PR #15/#19 reconciliation the first architecture task after baseline reproduction.