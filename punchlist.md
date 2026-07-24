# Punch List

Status: `RUNTIME_RELEASE_BLOCKED — BOOTSTRAP_WRITES_RETIRED`

This list separates the bounded QSO-FABRIC runtime from portfolio-governance automation. Completion of a documentation or workflow item does not authorize package publication, deployment, credentials, repository mutation, or external activation.

## P0 — trusted baseline and scope

- [x] Keep QSO-FABRIC scoped to the bounded four-QSO integration harness.
- [x] Remove scheduled owner-wide repository mutation from the trusted workflow surface.
- [x] Reduce the retained Muse bootstrap workflow to a manual, public-repository, read-only audit.
- [x] Require explicit out-of-band write authorization in the retained script and fail closed before any network mutation when it is absent.
- [x] Pin Actions, disable persisted checkout credentials, isolate generated evidence, retain artifacts, and validate exact submitted heads.
- [ ] Reproduce the runtime baseline at one immutable head with clean-install, pytest, CLI, deterministic-hash, limit, interruption, and rollback evidence.

## P1 — contracts and packaging

- [ ] Define package identity, supported Python versions, dependency policy, and license.
- [ ] Version and canonicalize event, ledger, freeze-point, limit, message, and report formats.
- [ ] Publish strict positive, negative, boundary, malformed, replay, timeout, tamper, interruption, and rollback fixtures.

## P2 — contradiction and repair lifecycle

- [ ] Define versioned contradiction records with source identities, evidence, severity, confidence, and affected state.
- [ ] Separate detection, adjudication, repair proposal, approval, execution receipt, independent revalidation, closure, correction, and rollback.
- [ ] Require repair inverses or explicit non-reversibility records before execution authority can be considered.
- [ ] Prevent duplicate contradictions, reports, and closure claims across exact heads.

## P3 — trace and probe evidence

- [ ] Extract a canonical training-trace schema with parent trace IDs, model and data revisions, seeds, request/response hashes, evaluation records, promotion decisions, corrections, revocations, and replay evidence.
- [ ] Define a Planck-probe-log schema with mission, instrument, channel, trusted time, coordinates, units, calibration, uncertainty or covariance, quality flags, source hashes, preprocessing lineage, and correction history.
- [ ] Add golden fixtures, tamper tests, independent consumers, retained exact-head artifacts, and rollback/restoration evidence.

## Release and authority blockers

- [ ] Accepted upstream QSO-GENOMES and QuantumStateObjects contracts.
- [ ] Security and privacy review, provenance, checksums, SBOM where applicable, accessibility review, and named human approval.
- [ ] Exercised rollback and independently verified restoration.
- [ ] Explicit approval for any future control-plane, credential, network, repository-write, package-publication, deployment, payment, or infrastructure capability.

## FYSA-120 mapping

- `CAT-017`: exact-source provenance, lineage, correction, and substitution detection.
- `CAT-022`: reproducible CI, evidence packaging, and artifact retention.
- `CAT-031`: workflow invariants, hostile regression tests, contradiction and repair validation.
- `CAT-040`: reversible migration, rollback, restoration, and continuity.
- `CAT-052` / `CAT-054`: trust boundaries, least privilege, credential separation, and secure workflow design.
- `CAT-059`: exact-head attestation and independent resulting-state evidence.
- Existing refinement `031-L` covers portfolio exact-state repair orchestration.
- Proposed future refinements remain `009-F` for contradiction adjudication, `047-F` for training-trace lineage, and `024-G` for Planck-probe logging.
