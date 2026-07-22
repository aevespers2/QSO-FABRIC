# QSO-FABRIC Obstruction and Gluing Analysis

## Purpose

This document analyzes whether QSO-FABRIC's current baseline and open candidates can compose safely with the wider A.L.I.S.T.A.I.R.E. portfolio. It uses **obstruction** and **gluing** as engineering terms:

- a **local section** is one repository or candidate's internally coherent contract;
- a **gluing map** is a versioned transformation between two local sections;
- an **obstruction** is an unresolved incompatibility that prevents one global interpretation;
- a **witness** is a deterministic fixture, receipt, or proof artifact showing that a gluing map preserves identity, authority, semantics, and rollback behavior.

This is not a claim that formal cohomology or homology has been computed. It is a disciplined compatibility ledger for repository contracts.

## Current local sections

| Section | Current or candidate responsibility | Status |
|---|---|---|
| Four-QSO baseline | Bounded Atlas, Nova, Orion, and Lyra experiment; event ledger, freeze hashes, messages, and report | Implemented candidate on `main`; release unverified |
| Documentation candidate PR #15 | Architecture, onboarding, output-contract notes, candidate governance, and scope repair | Documentation candidate |
| QSIO adapter PR #16 | Disabled mapping from Fabric concepts to QSO/QSI/QSIO, Nexis, Telion, Memora, Lumen, Umbra, and Witness records | Integration candidate |
| QSO file-format PR #17 | Proposed envelope, composition root, registry, mutation classes, JSON/CBOR/package/stream formats, validator, and example | Contract and format candidate |
| QSO-GENOMES | Candidate data-only authority for genomes, identity, immutable policy, lineage, manifests, and compatibility | External candidate authority |
| QuantumStateObjects | Candidate bounded runtime and lifecycle authority | External candidate runtime |
| `qsio-kernel` | Candidate low-level semantic and conformance kernel | External candidate kernel |
| Repository `0` / Repository `1` | Portable orchestration and independent capability/canonical-state authority | External governance candidates |

No open candidate is accepted merely because it exists, is mergeable, or passes its own tests.

## Active obstruction ledger

| ID | Obstruction | Why gluing fails | Lowest-scope repair candidate | Gate |
|---|---|---|---|---|
| FAB-O01 | **Canonical QSO format ownership is unresolved** | PR #17 places a normative `QSO Format Standard 0.1` and `quantum-state-objects/` tree inside QSO-FABRIC, while QSO-GENOMES, QuantumStateObjects, and `qsio-kernel` already claim adjacent contract, runtime, and semantic responsibilities. Repository location could be mistaken for portfolio-wide authority. | Assign one canonical format/registry owner. Keep QSO-FABRIC as a consumer, conformance-fixture host, or experiment-specific profile unless the portfolio explicitly assigns broader authority. | Architectural approval |
| FAB-O02 | **The directory name implies broader ownership than the repository charter** | `quantum-state-objects/` inside Fabric can appear to be the canonical home of all QSO objects rather than a candidate file-format profile. | Rename or namespace the candidate after ownership is decided, such as `integrations/qso-format-profile/`, or migrate the standard to the canonical contract repository with preserved history. | Naming and migration decision |
| FAB-O03 | **Envelope fields overlap existing identity and lifecycle contracts** | `object_id`, `format_version`, `schema`, `content_hash`, `mutation_class`, and `created_at` may conflict with genome identity, runtime lifecycle, kernel semantics, and evidence-envelope fields. | Produce a field-ownership matrix and normative vocabulary. Define whether fields are canonical, derived, transport-only, or repository-local. | Versioned schema review |
| FAB-O04 | **Canonicalization is claimed beyond implemented evidence** | PR #17 names canonical CBOR, signatures, packages, and streams, but the initial validator and tests cover only a minimal JSON envelope and mutation-class rejection. | Mark unimplemented serializations as reserved. Define canonical JSON/CBOR algorithms, normalization, critical-field behavior, and test vectors before normative use. | Conformance fixtures |
| FAB-O05 | **Hash and signature scope is underspecified** | The standard says hashes exclude transport-only fields and signatures bind several identifiers, but exact field order, canonical bytes, algorithms, domain separators, and algorithm agility are not fixed. | Publish byte-level test vectors, algorithm identifiers, domain separation, unsupported-algorithm rejection, and migration rules. | Integrity contract |
| FAB-O06 | **Mutation-class ownership conflicts with runtime and genome authority** | A file-format mutation class can accidentally authorize changes that QSO-GENOMES policy or QuantumStateObjects lifecycle rules prohibit. | Treat mutation class as a declared request, never authority. Require policy validation by the authoritative genome/runtime/capability layer before acceptance. | Negative fixtures |
| FAB-O07 | **Composition-root semantics lack a canonical resolver** | A `.qso` root may reference specialized objects by ID and hash, but no owner is assigned for resolution, trust, missing references, cycles, privacy, or retention. | Define an offline resolver interface, dependency manifest, cycle limits, required/optional reference semantics, and fail-closed evidence. | Resolver contract |
| FAB-O08 | **PR #16 and PR #17 define parallel integration vocabularies** | QSIO mapping uses QSO/QSI/QSIO, Nexis, Telion, Memora, Lumen, Umbra, and Witness, while the format branch defines QSO family objects and composition roots. There is no shared mapping between topology records and serialized object families. | Create one mapping table and round-trip fixtures showing which records serialize as which family objects and which concepts remain kernel-internal. | Triple-overlap test |
| FAB-O09 | **Fabric event ledger versus QSIO authoritative record is ambiguous** | The baseline event ledger is local experiment evidence; PR #16 calls accepted QSIO routing records immutable and non-authoritative local caches. Consumers could mistake either ledger for canonical portfolio state. | Assign ledger classes: local experiment evidence, accepted cross-repository record, and canonical state. Require explicit translation receipts and prohibit silent promotion. | Authority contract |
| FAB-O10 | **Freeze, Quietus, rollback, and mutation semantics do not yet glue** | Fabric freeze hashes, QSIO replay checkpoints, QSO file mutation classes, runtime freeze/stop controls, and kernel Quietus may describe different state transitions. | Publish a shared state-transition matrix and fixtures for freeze, reject, revoke, interrupt, resume, rollback, and permanent stop. | Lifecycle owner decision |
| FAB-O11 | **Open candidates are based on different repository states** | Documentation PR #15, QSIO PR #16, and format PR #17 have distinct bases and may not include identical consent, workflow, runtime, or contract state. | Rebase only after scope selection, then regenerate exact-head tests and evidence on the combined immutable head. Never carry evidence forward by assertion. | Candidate admission |
| FAB-O12 | **No privacy and retention model exists for composed QSO objects** | Composition roots, messages, objectives, evidence caches, and referenced objects may reveal private objectives or persistent identity data. | Add classification, minimization, redaction, encryption-at-rest boundary, retention, deletion, and tombstone semantics before persistent or external use. | Data-governance approval |
| FAB-O13 | **Capability authority is absent from serialization and adapter flows** | A valid envelope, content hash, Witness record, or accepted QSIO record could be misread as permission to execute, mutate, publish, or deploy. | Require separate Repository `1` or human-approved capability references. Integrity proves content identity, not authority. | Capability fixtures |
| FAB-O14 | **Conflict and contradiction records are not standardized** | Nova has a contradiction-oriented review posture but the baseline `contradictions` field is reserved and empty; parallel candidates add validation and Witness concepts without one conflict model. | Define contradiction, validation failure, disagreement, unknown, unsupported, and policy rejection as distinct records with provenance and resolution state. | Evidence vocabulary |
| FAB-O15 | **Recovery cannot yet reconstruct one global state** | Fabric rollback, QSIO replay, format-object migration, genome compatibility, runtime checkpoints, and capability revocation have separate or proposed recovery paths. | Define one bounded restart order and a reconstruction manifest that pins every contract, object, checkpoint, capability, and evidence hash. | Recovery tabletop |

## Required pairwise gluing maps

| Edge | Required input | Required output | Witnesses |
|---|---|---|---|
| QSO-GENOMES → QSO format | Accepted genome manifest, schema version, immutable-policy digest | Serialized genome-family object or referenced resource | valid, unknown critical field, policy mismatch, stale version, digest mismatch |
| QSO format → QuantumStateObjects | Resolved and validated composition root | Bounded runtime initialization request | missing reference, cycle, unsupported family, resource limit, identity mismatch |
| QuantumStateObjects → QSO-FABRIC | Runtime object identity and lifecycle contract | Fabric member registration and experiment-local state | duplicate ID, incompatible lifecycle, freeze before start, unsupported version |
| QSO-FABRIC → QSIO adapter | Ordered local events and topology proposals | Versioned QSI request or Witness candidate | replay, tamper, partial batch, timeout, local-ledger/canonical-state distinction |
| QSIO adapter → Repository `1` | Quarantined proposal, evidence, identity, and expected state | capability decision, accepted record, rejection, or revocation | stale request, wrong issuer, unsupported contract, expected-head mismatch, expiry |
| QSO-FABRIC → QSO-STUDIO/AionUi | Redacted report, ledger proof, limitations, and status vocabulary | read-only human review surface | privacy redaction, unverified-state display, correction, supersession |

## Required triple-overlap witnesses

Pairwise compatibility is insufficient where three sections must agree. The following diagrams must commute under deterministic fixtures.

### Genome → format → runtime

A genome accepted by QSO-GENOMES and serialized by the canonical format must initialize exactly the same identity, immutable policy, and compatibility state in QuantumStateObjects. A serialization round trip must not broaden mutable fields or drop critical policy.

### Format → runtime → Fabric

A composition root accepted by the runtime and registered in Fabric must preserve object identity, contract version, lifecycle state, and content digest. Fabric-local aliases must not become new canonical identities.

### Fabric → QSIO → Repository `1`

A Fabric topology proposal translated into QSI/QSIO must preserve requester identity, event provenance, expected state, and authority boundaries. Execution or validation success must not automatically become canonical acceptance.

### Freeze → revocation → recovery

A freeze in Fabric, capability revocation in Repository `1`, and replay/recovery through QSIO must converge on one fail-closed state. There is no automatic unlock, silent record deletion, or rollback that resurrects revoked authority.

### Evidence → interface → correction

The same report shown through QSO-STUDIO or AionUi must retain source commit, verification status, limitations, and supersession links. A corrected record must not make the prior record disappear or appear to have always been correct.

## Candidate sequencing recommendation

The lowest-coupling sequence is:

1. finish P0 verification of the bounded four-QSO baseline;
2. assign canonical ownership for QSO identity, file formats, lifecycle semantics, and capability authority;
3. publish a shared field and status vocabulary;
4. stabilize the minimal envelope and byte-level conformance vectors in the selected contract repository;
5. validate genome → format → runtime fixtures;
6. validate runtime → Fabric fixtures;
7. admit the disabled QSIO adapter with replay, tamper, authority, and rollback fixtures;
8. test the complete Fabric → Repository `1` route;
9. only then consider package, stream, signing, self-learning, or expanded collective candidates.

This recommendation does not reject PR #16 or PR #17. It prevents either candidate from silently becoming a portfolio-wide standard before ownership and compatibility are established.

## Release effect

Until FAB-O01 through FAB-O15 are resolved or explicitly deferred with owners and evidence:

- the four-QSO baseline may continue as a local research candidate;
- PR #16 remains a disabled integration candidate;
- PR #17 remains a format and contract proposal;
- no `.qso` artifact, Witness record, hash, signature, ledger entry, or successful test grants execution or canonical-state authority;
- no combined runtime release is eligible.

## Approval questions

Architectural clarification is required for:

1. the canonical owner and repository path for the QSO format registry and envelope;
2. the ownership split among QSO-GENOMES, QuantumStateObjects, QSO-FABRIC, and `qsio-kernel`;
3. the authoritative field vocabulary for identity, lifecycle, mutation, integrity, evidence, and status;
4. the local-ledger, QSIO-record, and canonical-state distinction;
5. capability issuance, signing-key custody, privacy, retention, incident, freeze, recovery, and rollback owners.
