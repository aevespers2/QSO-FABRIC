# Task Chain

States: `PROPOSED` · `READY` · `IN PROGRESS` · `BLOCKED` · `REVIEW` · `DONE`

## Product directive

- **Next objective:** Stabilize the implemented bounded four-QSO experiment as a reproducible integration harness.
- **User outcome:** A researcher can run Atlas, Nova, Orion, and Lyra with a deterministic seed and explicit limits, then verify the event ledger, freeze-point hashes, messages, and final report without granting network, credential, deployment, repository, format-standard, or canonical-state authority.
- **MVP scope:** existing Python runtime and runner; package/environment definition; license; versioned event/ledger/freeze/report contracts; deterministic, boundary, timeout, tamper, and rollback fixtures; retained CI/test evidence; read-only compatibility with published QSO-GENOMES and QuantumStateObjects contracts.
- **Priority:** Formal acceptance and verification of the existing runtime comes before additional learning, data acquisition, visualization, economic behavior, portfolio administration, a portfolio-wide QSO file-format standard, or authoritative QSIO integration.
- **Success criteria:** clean install and smoke command pass; repeated seeded runs produce identical canonical hashes outside documented timeout fields; tampering is detected; runtime/message limits fail closed; interruption and rollback preserve evidence; no unapproved network, command, credential, repository-write, deployment, cross-repository mutation, signing, or canonical-state path exists.
- **Non-goals:** autonomous internet learning, self-modification, production orchestration, credentialed agents, payment settlement, claims of sentience/physical quantum execution, acting as the control plane for all owned repositories, or silently becoming the canonical QSO format/lifecycle authority.
- **Release rationale:** QSO-FABRIC is the first executable portfolio integration artifact. A narrowly verified harness will expose contract defects safely before broader runtime, UI, format, adapter, or governance automation depends on it.

## A.L.I.S.T.A.I.R.E. alignment

A.L.I.S.T.A.I.R.E. is the canonical system. QSO-FABRIC is its bounded collaboration, experiment, and evidence subsystem. The long-term mission of increasingly autonomous development does not change the current P0–P3 order and does not implicitly grant this repository portfolio-control, format-standard, capability, signing, or canonical-state authority.

QSO-FABRIC may contribute deterministic hypotheses, contradiction-oriented review, integrity-marked reports, local experiment ledgers, and contract-validation evidence. Repository discovery, portfolio planning, branch and pull-request operations, merge/deployment authority, credentials, capability issuance, canonical-state decisions, audit, incident response, signing-key custody, and cross-repository rollback require separately chartered owners with explicit contracts.

Repository `0` and Repository `1` are the current candidates for portable orchestration and independent capability/canonical-state authority. QSO-GENOMES, QuantumStateObjects, and `qsio-kernel` are adjacent contract/runtime/kernel candidates. Until ownership is recorded, QSO-FABRIC outputs and open branches remain reviewable evidence and proposals rather than autonomous actions or portfolio standards.

## Active chain

| Priority | Task | Owner | Depends on | Status | Acceptance criteria |
|---|---|---|---|---|---|
| P0 | Accept and reproduce the current four-QSO runtime baseline | Architect | — | READY | Source, tests, workflow, limits, ledger, freeze behavior, commands, results, privacy limitations, and rollback notes are inventoried and verified at one immutable commit. |
| P1 | Add package, license, and versioned output contracts | QSOBuilder | P0 | PROPOSED | Clean installation works; supported Python versions are declared; event, ledger, freeze-point, limit, and report formats have explicit versions and canonicalization rules. |
| P2 | Publish deterministic security and failure fixtures | QSOBuilder | P1 | PROPOSED | Positive, negative, boundary, timeout, tamper, interruption, partial-write, consent, and rollback fixtures pass with retained hashes and reports. |
| P3 | Validate upstream compatibility without importing authority | Builder | QSO-GENOMES accepted manifest and QuantumStateObjects runnable baseline | BLOCKED | Genome/runtime manifests are checked by schema version and hash; missing or incompatible artifacts fail closed; external code is not imported or executed. |
| P4 | Resolve QSO format and QSIO gluing ownership | Architect | P0–P3, portfolio ownership decisions | BLOCKED | Canonical format/registry owner, field vocabulary, lifecycle/mutation authority, ledger classes, capability boundary, privacy, and recovery semantics are approved with pairwise and triple-overlap fixtures. |
| P5 | Reconcile selected candidates on one trusted base | Builder | P4 and explicit candidate selection | PROPOSED | Selected branches are rebased, shared invariants are resolved, all task/release/docs files are updated, and exact-head evidence is regenerated for the combined result. |

Detailed acceptance work is tracked in [`punchlist.md`](punchlist.md). Cross-repository incompatibilities and witness requirements are tracked in [`docs/OBSTRUCTION_AND_GLUING.md`](docs/OBSTRUCTION_AND_GLUING.md).

## Concurrent candidate rule

Open pull requests that explore expanded collectives, evidence acquisition, self-learning scaffolds, sprite policy, safety repair, QSIO integration, or QSO file formats are candidates only. They must not be treated as cumulative accepted architecture.

The current high-impact candidates include:

- PR #16: disabled QSIO mapping and adapter candidate;
- PR #17: QSO envelope, composition-root, registry, serialization, and mutation-contract candidate.

PR #16 and PR #17 overlap with QSO-GENOMES, QuantumStateObjects, and `qsio-kernel`. Their repository location and internal consistency do not settle portfolio ownership.

A candidate may enter the active chain only after it:

- fits the current directive or receives a recorded scope decision;
- declares changed contracts, permissions, dependencies, data handling, and authority;
- identifies canonical owners for every shared field and lifecycle transition;
- rebases and reconciles shared invariants;
- produces exact-head deterministic, security, failure, provenance, privacy, and rollback evidence;
- updates `taskchain.md`, `punchlist.md`, `release.md`, `changelog.md`, and public documentation;
- receives explicit acceptance.

See `docs/CANDIDATE_GOVERNANCE.md` for the admission and conflict model.

## Gluing doctrine

QSO-FABRIC uses the following compatibility rule:

1. Pairwise adapters are insufficient when three or more repositories share identity, lifecycle, authority, or evidence semantics.
2. A valid hash, envelope, signature, ledger entry, Witness record, or successful command does not independently grant authority.
3. Local experiment evidence, accepted cross-repository records, and canonical portfolio state are separate classes.
4. Mutation classes are requests subject to authoritative policy, not self-executing permissions.
5. Evidence from one branch head does not validate a rebased or combined head.
6. Missing ownership or incompatible semantics fail closed and remain `BLOCKED`.

The required triple-overlap witnesses include genome → format → runtime, format → runtime → Fabric, Fabric → QSIO → Repository `1`, freeze → revocation → recovery, and evidence → interface → correction.

## Closed scope conflict: repository bootstrap automation

PR #1 proposed scheduled owner-wide automation that would write generic Markdown files and issues to other repositories using a broad token. The pull request was closed on 2026-07-16. No portfolio-bootstrap capability is accepted, scheduled, deployed, or part of the QSO-FABRIC runtime MVP, and P0–P5 retain their existing priority.

The review evidence remains preserved for any future control-plane proposal. Any successor must:

- be explicitly opt-in per repository rather than scanning all owned repositories by default;
- default scheduled and manual runs to dry-run;
- avoid duplicate sources of truth such as `TASK_CHAIN.md` alongside an existing `taskchain.md`;
- create reviewable per-repository pull requests rather than writing directly to default branches;
- use least-privilege credentials and document revocation, audit, retry, checkpoint, and rollback behavior;
- respect repository-specific holds, fork identity, licensing, and product directives;
- correctly distinguish user-owned and organization-owned repositories;
- paginate idempotency checks and surface every failed write;
- skip disabled repository features safely;
- throttle mutations and recover or roll back partial runs;
- live in a dedicated governance/control repository unless ownership by QSO-FABRIC is explicitly approved.

The five unresolved review findings for organization discovery, issue pagination, swallowed write failures, disabled-Issues handling, and mutating-request throttling are retained as rejected-proposal evidence, not active runtime blockers.

## Builder rules

Execute only the highest-priority unblocked task. Preserve the existing bounded runtime while adding evidence; do not widen scope to networking, external learning, payments, UI, cross-repository governance automation, portfolio-wide file-format authority, signing, merge/deployment authority, or autonomous policy changes without a recorded approval and revised product directive.

## Evidence rules

For each task record the exact source commit, base, branch, Python/OS/tool versions, commands, results, seeds, fixture hashes, artifact hashes, limitations, failures, changed contracts, data classification, authority effects, recovery behavior, and acceptance decision.

## Builder log

- 2026-07-20 — Added the obstruction and gluing ledger and release punch list; documented PR #16 and PR #17 as separate candidates with unresolved format, lifecycle, ledger, capability, privacy, and recovery ownership. No candidate or authority was accepted.
- 2026-07-19 — Documented QSO-FABRIC as the bounded collaboration and evidence subsystem within A.L.I.S.T.A.I.R.E.; retained P0–P3 ordering and separated autonomous-development control-plane authority from the runtime.
- 2026-07-19 — Added candidate-governance rules for concurrent architecture pull requests; no candidate was accepted or reprioritized.
- 2026-07-16 — Product review retained the runtime-verification priority and classified PR #1 as an out-of-scope portfolio-governance proposal requiring redesign or relocation before approval.
- 2026-07-16 — Recorded five PR #1 reliability findings covering organization discovery, issue pagination, swallowed write failures, disabled-Issues handling, and mutating-request throttling/recovery; no portfolio reprioritization was made.
- 2026-07-16 — Recorded closure of PR #1. The current scope conflict is resolved by exclusion; no bootstrap capability was accepted, and QSO-FABRIC remains focused on the bounded runtime baseline.
