# Release Plan

## Current Decision
Status: `BLOCKED — INITIALIZATION APPROVAL REQUIRED`

QSO-FABRIC is empty. It has no `taskchain.md`, `punchlist.md`, charter, source, schemas, tests, workflows, documentation, security evidence, provenance, artifacts, or rollback baseline. No release is eligible.

## Versioning
- Use Semantic Versioning only after the repository charter and package/publication identity are approved.
- First possible documentation-only candidate: `0.0.1-charter.1`.
- First implementation candidate must remain a pre-release until integration contracts, tests, security, and rollback pass.

## Candidate Scope
- Approved purpose, users, inputs, outputs, non-goals, trust boundary, and relationship to QuantumStateObjects, QSO-GENOMES, QSO-SEEKER, QSO-PAYMENTS, and QSO-STUDIO.
- Builder task chain and punch list with one bounded implementation task.
- Schema-first contracts, deterministic fixtures, tests, CI, security review, documentation, provenance, and rollback.
- No autonomous execution, credentials, unrestricted network/repository writes, production settlement, or capability claims before verification.

## Selected Completed Work
None. The repository contains no releaseable content.

## Planned Changelog Entries
- `Documentation`: approved QSO-FABRIC charter, architecture, boundaries, and verification strategy.
- `Added`: minimal schema-first skeleton and deterministic fixtures after approval.
- `Security`: trust-boundary, credential, network, execution, dependency, and workflow-permission checks.
- `Release`: checksums, provenance, artifacts, and approval decision.

## Acceptance Gates
| Gate | Status | Requirement |
|---|---|---|
| Charter approval | BLOCKED | Approve purpose, repository relationships, data/control flow, non-goals, license, and publication model. |
| Task completion | FAIL | P0/P1 task chain and punch list exist and included work is `DONE`. |
| Build/tests | NO EVIDENCE | Clean build, static checks, deterministic tests, integration tests, and smoke test pass. |
| Security | NO EVIDENCE | Secret, dependency, input, execution, network, repository-write, workflow-permission, and supply-chain checks pass. |
| Documentation | FAIL | README, setup, contracts, limitations, operations, and rollback are absent. |
| Provenance | NO EVIDENCE | Commit, tools, commands, artifact hashes, SBOM where applicable, and attestations recorded. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Artifact Requirements
- Approved charter, task chain, punch list, and architecture/contract documentation.
- Versioned schemas and deterministic positive/negative fixtures.
- Test, integration, security, and documentation reports.
- Source/package artifacts, SBOM where applicable, SHA-256 checksums, and provenance manifest.

## Rollback Criteria
Withdraw a charter candidate if scope conflicts with another repository or remains ambiguous. Roll back implementation if contracts are incompatible, state/evidence is corrupted, authority exceeds the charter, verification is non-reproducible, severe security findings remain, or artifact hashes differ. Restore the previous verified tag and preserve failed-candidate evidence.

## Unresolved Blockers
- Approval is required for the repository charter, ecosystem role, license, and publication model.
- Repository is empty; `taskchain.md` and `punchlist.md` do not exist.
- No implementation, contracts, tests, CI, security, documentation, provenance, or artifacts exist.

## Release Log
- 2026-07-16: Empty repository evaluated and held `BLOCKED — INITIALIZATION APPROVAL REQUIRED`.