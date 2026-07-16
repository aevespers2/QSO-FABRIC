# Task Chain

States: `PROPOSED` · `READY` · `IN PROGRESS` · `BLOCKED` · `REVIEW` · `DONE`

## Product directive

- **Next objective:** Stabilize the implemented bounded four-QSO experiment as a reproducible integration harness.
- **User outcome:** A researcher can run Atlas, Nova, Orion, and Lyra with a deterministic seed and explicit limits, then verify the event ledger, freeze-point hashes, messages, and final report without granting network, credential, or repository authority.
- **MVP scope:** existing Python runtime and runner; package/environment definition; license; versioned event/ledger/freeze/report contracts; deterministic, boundary, timeout, tamper, and rollback fixtures; retained CI/test evidence; read-only compatibility with published QSO-GENOMES and QuantumStateObjects contracts.
- **Priority:** Formal acceptance and verification of the existing runtime comes before additional learning, data acquisition, visualization, economic behavior, or portfolio administration.
- **Success criteria:** clean install and smoke command pass; repeated seeded runs produce identical canonical hashes; tampering is detected; runtime/message limits fail closed; interruption and rollback preserve evidence; no unapproved network, command, credential, repository-write, or cross-repository mutation path exists.
- **Non-goals:** autonomous internet learning, self-modification, production orchestration, credentialed agents, payment settlement, claims of sentience/physical quantum execution, or acting as the control plane for all owned repositories.
- **Release rationale:** QSO-FABRIC is the first executable portfolio integration artifact. A narrowly verified harness will expose contract defects safely before broader runtime, UI, or governance automation depends on it.

## Active chain

| Priority | Task | Owner | Depends on | Status | Acceptance criteria |
|---|---|---|---|---|---|
| P0 | Accept and reproduce the current four-QSO runtime baseline | Architect | — | READY | Source, tests, workflow, limits, ledger, freeze behavior, commands, results, and rollback notes are inventoried and verified at one immutable commit. |
| P1 | Add package, license, and versioned output contracts | QSOBuilder | P0 | PROPOSED | Clean installation works; supported Python versions are declared; event, ledger, freeze-point, and report formats have explicit versions and canonicalization rules. |
| P2 | Publish deterministic security and failure fixtures | QSOBuilder | P1 | PROPOSED | Positive, negative, boundary, timeout, tamper, interruption, and rollback fixtures pass with retained hashes and reports. |
| P3 | Validate upstream compatibility without importing authority | Builder | QSO-GENOMES accepted manifest and QuantumStateObjects runnable baseline | BLOCKED | Genome/runtime manifests are checked by schema version and hash; missing or incompatible artifacts fail closed; external code is not imported or executed. |

## Scope conflict: repository bootstrap automation

Draft PR #1 proposes a scheduled owner-wide automation that writes generic Markdown files and issues to other repositories using a broad token. That capability is not part of the current QSO-FABRIC MVP and must not displace P0–P3 without an approved product decision.

Before any such automation can be considered, it must:

- be explicitly opt-in per repository rather than scanning all owned repositories by default;
- default scheduled and manual runs to dry-run;
- avoid duplicate sources of truth such as `TASK_CHAIN.md` alongside an existing `taskchain.md`;
- create reviewable per-repository pull requests rather than writing directly to default branches;
- use least-privilege credentials and document revocation, audit, retry, and rollback behavior;
- respect repository-specific holds, fork identity, licensing, and product directives;
- live in a dedicated governance/control repository unless ownership by QSO-FABRIC is explicitly approved.

### Current PR #1 reliability blockers

Five unresolved review findings further prevent acceptance even as a separate control-plane proposal:

- organization owners are queried through a user-owned repository endpoint and can silently produce an empty target set;
- orientation-issue detection reads only the first 100 issues/PRs and can create duplicates;
- the shared API helper treats write-operation `404` responses as missing resources, allowing false-success reports;
- repositories with Issues disabled are not skipped, causing repeated partial-run failures;
- mutating API calls have no throttling, retry, or resumable checkpoint design, risking secondary-rate-limit interruption and partially modified portfolios.

These findings reinforce the existing decision to keep PR #1 outside the runtime MVP. They do not change P0–P3 priority.

## Builder rules

Execute only the highest-priority unblocked task. Preserve the existing bounded runtime while adding evidence; do not widen scope to networking, external learning, payments, UI, or cross-repository governance automation without a recorded approval and revised product directive.

## Builder log

Record commits, Python/tool versions, commands/results, workflow URLs, seeds, fixture and artifact hashes, failures, limits, rollback evidence, and follow-ups.

- 2026-07-16 — Product review retained the runtime-verification priority and classified draft PR #1 as an out-of-scope portfolio-governance proposal requiring redesign or relocation before approval.
- 2026-07-16 — Recorded five unresolved PR #1 reliability findings covering organization discovery, issue pagination, swallowed write failures, disabled-Issues handling, and mutating-request throttling/recovery; no portfolio reprioritization was made.
