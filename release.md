# Release Plan

## Current Decision
Status: `BLOCKED — UNVERIFIED RUNTIME BASELINE`

QSO-FABRIC is no longer empty. Reviewed implementation head `7c36883c649041a8d041c48b7eb415584ae3fb39` contains a bounded four-QSO Python runtime, a CLI-style experiment runner, three pytest cases, and a least-privilege GitHub Actions workflow. No release is eligible because `taskchain.md` and `punchlist.md` are absent, no task is accepted as `DONE`, no current workflow result or independent test report is attached, and packaging, security, documentation, provenance, licensing, artifacts, and repository-specific limit/rollback evidence remain incomplete.

## Versioning
- Scheme: Semantic Versioning after package identity, supported Python versions, license, and ecosystem contract boundaries are approved.
- First eligible runtime candidate: `0.1.0-alpha.1`.
- Deterministic output, ledger, event, limit, freeze-point, and report formats must be explicitly versioned before consumer compatibility is claimed.
- Do not tag merely because source, tests, and a workflow exist; the immutable candidate commit must satisfy every acceptance gate.

## Candidate Scope
- Bounded Atlas, Nova, Orion, and Lyra runtime with deterministic seeded behavior.
- Append-only hash-chained event ledger and verifiable final event hash.
- Explicit limits for rounds, per-QSO messages, message size, and runtime.
- Freeze-point state hashes and per-QSO observations, inferences, messages, and proposals.
- Library and CLI smoke behavior with deterministic positive, negative, boundary, timeout, and tamper fixtures.
- Versioned integration boundary with QuantumStateObjects and QSO-GENOMES without importing executable authority.
- Reproducible tests, static validation, security review, documentation, artifacts, checksums, provenance, and rollback evidence.

## Existing Candidate Assets
- `qso_runtime/four_qso_experiment.py` implements the bounded experiment, ledger verification, freeze points, deterministic seeded selection, message routing, and JSON report generation.
- `qso_runtime/__init__.py` exposes `ExperimentLimits` and `run_experiment`.
- `tests/test_four_qso_experiment.py` contains deterministic replay, message/freeze-point, ledger, and Nova verification assertions.
- `.github/workflows/four-qso-ci.yml` defines Python 3.11 pytest and smoke checks with `contents: read`, disabled checkout credentials, concurrency control, and a ten-minute job timeout.
- `README.md` documents a run command and a non-operational safety boundary.

These files are candidate implementation inputs, not releasable completed work until the results and controls below are independently reproduced and tied to one immutable commit.

## Selected Completed Work
None selected for release. The implementation, tests, and workflow are present, but there is no approved task chain, completed punch-list evidence, current CI/test record, security report, package/license baseline, artifact bundle, or provenance manifest.

## Planned Changelog Entries
- `Added`: verified bounded four-QSO runner, library API, CLI smoke path, deterministic report contract, and hash-chained ledger.
- `Security`: resource-limit, timeout, untrusted-input, command/network/credential, repository-write, dependency, workflow-permission, and generated-artifact findings.
- `Changed`: explicit event/report schema versions, canonicalization rules, compatibility contract, and failure semantics.
- `Fixed`: determinism, ledger verification, message-cap, runtime-limit, freeze/rollback, or output-integrity defects found during baseline testing.
- `Documentation`: supported environment, setup, exact commands, limits, trust boundaries, limitations, recovery, and consumer guidance.
- `Release`: source/package artifacts, reports, SBOM where applicable, checksums, provenance, and approval decision.

## Acceptance Gates
| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | Create `taskchain.md` and `punchlist.md`; mark the bounded runtime baseline `DONE` with linked commits, commands, results, and rollback notes. |
| Package/environment | FAIL | Define supported Python versions, package metadata/build method, dependency policy, license, and clean-environment installation. |
| Tests/CI | NO CURRENT EVIDENCE | Full pytest and CLI smoke checks pass at the immutable candidate commit with retained logs. |
| Determinism/integrity | PARTIAL | Seeded equality and ledger assertions exist; repeated cross-environment hashes, canonical JSON, ledger tamper, ordering, and timeout fixtures must pass. |
| Limits/freeze/rollback | PARTIAL | Runtime/message limits and freeze hashes exist; boundary, exhaustion, interruption, recovery, and rollback behavior require evidence. |
| Security | NO EVIDENCE | Secret, dependency, input, output-path, resource-exhaustion, command/network/credential, repository-write, workflow-permission, and supply-chain checks pass. |
| Integration contracts | NO EVIDENCE | Versioned, hash-verified boundaries with QuantumStateObjects and QSO-GENOMES are documented and tested without granting external execution authority. |
| Documentation | PARTIAL | README purpose and run command exist; install, API/report schema, supported matrix, failure modes, operations, artifact retention, and rollback remain unverified. |
| Provenance | NO EVIDENCE | Candidate commit, Python/OS/tool versions, commands, exit codes, test reports, output hashes, SBOM, repository URL, and attestations are recorded. |
| Approval | PENDING | Explicit release approval after all blocking gates pass. |

## Artifact Requirements
- Reproducible source archive and Python package artifacts if packaging is included.
- Versioned event, ledger, freeze-point, and report schemas or documented canonical contracts.
- Positive, negative, boundary, timeout, tamper, determinism, and rollback fixture bundle.
- Complete test, CLI smoke, static-validation, security, integration, and documentation reports.
- Representative four-QSO report and ledger with no unapproved sensitive data.
- SBOM where applicable, SHA-256 checksum manifest, and provenance record tied to the candidate commit.

## Rollback Criteria
Withdraw or roll back if deterministic runs diverge, ledger tampering is not detected, message/runtime limits can be bypassed, timeout or interruption corrupts evidence, freeze-point hashes are not reproducible, untrusted input gains command/network/credential/repository authority, integration contracts drift, documented commands fail, severe security findings remain, or artifact hashes differ. Restore the last verified tag or reviewed pre-release commit and preserve failed-candidate inputs, reports, logs, and hashes.

## Unresolved Blockers
- `taskchain.md` and `punchlist.md` do not exist, so no implementation work has formal completion or acceptance evidence.
- No current GitHub Actions result or independent clean-environment pytest/CLI report is attached to the reviewed implementation head.
- No `pyproject.toml`, package/build definition, dependency baseline, supported Python matrix, or license is present.
- Security coverage is limited to workflow permissions and stated runtime boundaries; no adversarial, dependency, secret, path, resource-exhaustion, or supply-chain report exists.
- Event/report schema versioning, canonical output rules, timeout behavior, ledger tamper fixtures, rollback procedure, artifact retention, checksums, SBOM, and provenance are absent.
- Cross-repository genome/runtime compatibility has not been validated against a complete QSO-GENOMES contract set.

## Release Log
- 2026-07-16: Corrected the prior empty-repository assessment after identifying the bounded runtime, tests, and CI workflow; candidate remains `BLOCKED — UNVERIFIED RUNTIME BASELINE` pending task acceptance and complete release evidence.
