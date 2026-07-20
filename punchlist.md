# QSO-FABRIC Punch List

This punch list translates the active task chain, release gates, candidate-governance rules, and obstruction ledger into reviewable work. Completing an item requires evidence at an immutable commit; checking a box in documentation is not evidence by itself.

## P0 — Reproduce the bounded four-QSO baseline

- [ ] Pin one immutable baseline commit from accepted repository state.
- [ ] Record supported operating systems, Python versions, dependency versions, and environment details.
- [ ] Run the complete test suite in a clean environment.
- [ ] Run one documented CLI smoke experiment with a fixed seed and limits.
- [ ] Retain the report, event ledger, freeze hashes, console output, commands, and SHA-256 checksums.
- [ ] Repeat the seeded run and compare canonical artifacts.
- [ ] Document the wall-clock timeout nondeterminism boundary separately from deterministic replay claims.
- [ ] Confirm the complete objective remains visible in the report and first event; classify privacy and size implications.
- [ ] Record rollback and cleanup instructions.
- [ ] Obtain explicit acceptance of P0 evidence.

## P1 — Package, license, and version output contracts

- [ ] Select package name and import namespace.
- [ ] Add or approve a build definition and clean-install procedure.
- [ ] Add or approve a repository license.
- [ ] Declare supported Python versions and dependency policy.
- [ ] Version the report envelope.
- [ ] Version the event and ledger contract.
- [ ] Version freeze-point construction and digest scope.
- [ ] Version configured limits and limit-exhaustion status.
- [ ] Define canonical JSON bytes and numeric/string normalization.
- [ ] Define unknown-field, unsupported-version, and migration/rejection behavior.
- [ ] Add representative schema examples and byte-level test vectors.

## P2 — Deterministic security and failure fixtures

- [ ] Positive seeded replay fixture.
- [ ] Malformed objective and configuration fixtures.
- [ ] Zero, minimum, maximum, and over-limit round fixtures.
- [ ] Message-count and message-length exhaustion fixtures.
- [ ] Ledger tamper, deletion, insertion, reordering, and duplicate-event fixtures.
- [ ] Freeze-hash mismatch fixture.
- [ ] Timeout and interruption fixtures with documented nondeterministic fields.
- [ ] Partial-write and artifact-corruption fixtures.
- [ ] Recovery and rollback fixtures.
- [ ] Consent-policy and authority-bypass fixtures.
- [ ] Dependency, workflow-token, secret, path, and supply-chain checks.
- [ ] Retained exact-head evidence bundle.

## P3 — Upstream contract compatibility

- [ ] Identify accepted QSO-GENOMES manifest version and immutable digest.
- [ ] Identify accepted QuantumStateObjects runtime/lifecycle contract and immutable digest.
- [ ] Identify accepted `qsio-kernel` semantic/conformance contract, or mark it explicitly out of scope.
- [ ] Define read-only dependency acquisition and local cache rules.
- [ ] Reject missing, stale, unsupported, or hash-mismatched artifacts.
- [ ] Prove that external code is not imported or executed merely because a manifest exists.
- [ ] Add genome → runtime identity and immutable-policy fixtures.
- [ ] Add runtime → Fabric registration, lifecycle, and freeze fixtures.

## P4 — Resolve format and QSIO gluing obstructions

See [`docs/OBSTRUCTION_AND_GLUING.md`](docs/OBSTRUCTION_AND_GLUING.md).

- [ ] Assign the canonical owner for the QSO format envelope and registry.
- [ ] Decide whether PR #17 remains in QSO-FABRIC, is namespaced as a Fabric profile, or migrates with history.
- [ ] Publish the field-ownership matrix for identity, schema, version, hash, mutation, lifecycle, evidence, and timestamps.
- [ ] Define canonical serialization, algorithm identifiers, signature scope, and byte-level test vectors.
- [ ] Define mutation classes as requests subject to authoritative policy, not self-executing authority.
- [ ] Define composition resolution, cycle limits, missing references, required/optional references, and privacy.
- [ ] Reconcile PR #16 QSIO terms with PR #17 QSO family objects.
- [ ] Distinguish local experiment ledger, accepted QSIO record, and canonical portfolio state.
- [ ] Reconcile freeze, Quietus, revocation, replay, rollback, and recovery semantics.
- [ ] Add all required pairwise fixtures.
- [ ] Add genome → format → runtime triple-overlap fixtures.
- [ ] Add format → runtime → Fabric triple-overlap fixtures.
- [ ] Add Fabric → QSIO → Repository `1` triple-overlap fixtures.
- [ ] Add freeze → revocation → recovery triple-overlap fixtures.
- [ ] Add evidence → interface → correction triple-overlap fixtures.

## P5 — Candidate reconciliation

- [ ] Inventory every open QSO-FABRIC pull request and its base/head.
- [ ] Classify each as baseline verification, documentation, adapter, expanded runtime, format/contract, governance/control plane, or safety repair.
- [ ] Record changed contracts, permissions, dependencies, and authority.
- [ ] Select, defer, supersede, or reject each candidate explicitly.
- [ ] Do not merge candidates by accumulation.
- [ ] Rebase only selected candidates onto one trusted base.
- [ ] Resolve shared invariants and regenerate all evidence at the combined exact head.
- [ ] Update task chain, release plan, changelog, Pages, migration notes, and rollback instructions.

## Security, privacy, and governance

- [ ] Assign capability issuer, approver, revoker, incident owner, emergency-stop owner, and recovery owner.
- [ ] Assign signing-key custody or keep signing explicitly unimplemented.
- [ ] Classify objectives, messages, reports, caches, and referenced QSO resources.
- [ ] Define minimization, redaction, retention, deletion, correction, and tombstone rules.
- [ ] Ensure hashes, signatures, Witness records, and successful execution cannot be interpreted as authority.
- [ ] Document no-automatic-unlock freeze behavior.
- [ ] Conduct a recovery tabletop that reconstructs state from pinned contracts and evidence.

## Documentation and release evidence

- [x] Pages overview exists.
- [x] Architecture and trust boundaries are documented.
- [x] Developer onboarding exists.
- [x] Candidate governance exists.
- [x] Output-contract limitations are documented.
- [x] Obstruction and gluing analysis exists.
- [x] This punch list exists.
- [ ] Validate all internal links at the exact documentation head.
- [ ] Validate Pages publication settings before merge.
- [ ] Retain rendered or static documentation evidence tied to the exact head.
- [ ] Record final changed-file inventory, tests, artifacts, and hashes.
- [ ] Obtain explicit merge and publication approval.

## Release stop conditions

Stop promotion and preserve evidence if:

- candidate bases or exact heads are ambiguous;
- schema, identity, lifecycle, ledger, or authority ownership conflicts remain hidden;
- deterministic artifacts diverge outside documented nondeterministic fields;
- consent, limits, freeze, revocation, or rollback can be bypassed;
- a `.qso` object, hash, signature, Witness record, or QSIO record is treated as permission without a separate capability;
- private objectives or identity data are exposed without approved handling;
- rollback cannot restore the last accepted bounded state;
- evidence belongs to an earlier head than the proposed merge result.
