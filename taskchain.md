# Task Chain

States: `PROPOSED` · `READY` · `IN PROGRESS` · `BLOCKED` · `REVIEW` · `DONE`

## Product directive

- **Next objective:** Stabilize the implemented bounded four-QSO experiment as a reproducible integration harness.
- **User outcome:** A researcher can run Atlas, Nova, Orion, and Lyra with a deterministic seed and explicit limits, then verify the event ledger, freeze-point hashes, messages, and final report without granting network, credential, or repository authority.
- **MVP scope:** existing Python runtime and runner; package/environment definition; license; versioned event/ledger/freeze/report contracts; deterministic, boundary, timeout, tamper, and rollback fixtures; retained CI/test evidence; read-only compatibility with published QSO-GENOMES and QuantumStateObjects contracts.
- **Priority:** Formal acceptance and verification of the existing runtime comes before additional learning, data acquisition, visualization, or economic behavior.
- **Success criteria:** clean install and smoke command pass; repeated seeded runs produce identical canonical hashes; tampering is detected; runtime/message limits fail closed; interruption and rollback preserve evidence; no unapproved network, command, credential, or repository-write path exists.
- **Non-goals:** autonomous internet learning, self-modification, production orchestration, credentialed agents, payment settlement, or claims of sentience/physical quantum execution.
- **Release rationale:** QSO-FABRIC is the first executable portfolio integration artifact. A narrowly verified harness will expose contract defects safely before broader runtime or UI work depends on it.

## Active chain

| Priority | Task | Owner | Depends on | Status | Acceptance criteria |
|---|---|---|---|---|---|
| P0 | Accept and reproduce the current four-QSO runtime baseline | Architect | — | READY | Source, tests, workflow, limits, ledger, freeze behavior, commands, results, and rollback notes are inventoried and verified at one immutable commit. |
| P1 | Add package, license, and versioned output contracts | QSOBuilder | P0 | PROPOSED | Clean installation works; supported Python versions are declared; event, ledger, freeze-point, and report formats have explicit versions and canonicalization rules. |
| P2 | Publish deterministic security and failure fixtures | QSOBuilder | P1 | PROPOSED | Positive, negative, boundary, timeout, tamper, interruption, and rollback fixtures pass with retained hashes and reports. |
| P3 | Validate upstream compatibility without importing authority | Builder | QSO-GENOMES P1 and QuantumStateObjects runnable baseline | BLOCKED | Genome/runtime manifests are checked by schema version and hash; missing or incompatible artifacts fail closed; external code is not imported or executed. |

## Builder rules

Execute only the highest-priority unblocked task. Preserve the existing bounded runtime while adding evidence; do not widen scope to networking, external learning, payments, or UI.

## Builder log

Record commits, Python/tool versions, commands/results, workflow URLs, seeds, fixture and artifact hashes, failures, limits, rollback evidence, and follow-ups.