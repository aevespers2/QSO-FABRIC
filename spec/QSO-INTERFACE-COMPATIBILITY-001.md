# QSO-INTERFACE-COMPATIBILITY-001

Status: **draft documentation and synthetic-conformance profile**

This profile defines the minimum compatibility evidence required before one repository may claim that it can compose with the `qso-event-ledger` or `qso-runtime-report` interfaces declared by `QSO-FABRIC`.

It does not define the final event or report payload schemas, admit a component to the ecosystem, grant a capability, activate runtime execution, appoint a custodian, or authorize merge, release, publication, deployment, recovery, or canonical-state mutation.

## Governing separation

```text
interface name
!= protocol declaration
!= schema generation
!= producer compatibility
!= consumer compatibility
!= correction compatibility
!= rollback compatibility
!= evidence binding
!= ecosystem admission
!= execution authority
```

A matching string or successful synthetic test is insufficient. Compatibility requires an immutable source tuple and agreement across interface identity, producer/consumer roles, protocol, schema generation, idempotency, retry policy, default-deny behavior, correction semantics, rollback semantics, and exact evidence binding without authority promotion.

## Declared interfaces

| Interface | Producer protocol | Schema generation | Idempotent | Retry limit |
|---|---|---:|---:|---:|
| `qso-event-ledger` | `append-only-json` | `1.0.0` | true | 0 |
| `qso-runtime-report` | `json-file` | `1.0.0` | true | 0 |

These declarations are taken from the exact `qso.manifest.json` generation bound by the producer evidence tuple. They are not substitutes for final payload schemas.

## Compatibility facts

A candidate pair is evaluated over this closed Boolean surface:

1. `source_tuple_current`
2. `known_interface`
3. `interface_name_match`
4. `producer_role_valid`
5. `consumer_role_valid`
6. `protocol_match`
7. `schema_version_match`
8. `idempotency_match`
9. `retry_policy_match`
10. `default_deny_preserved`
11. `correction_supported`
12. `rollback_supported`
13. `evidence_bound`
14. `authority_promotion_absent`

All facts must be true for the bounded disposition `COMPATIBLE_PENDING_ARCHITECTURE_APPROVAL`.

## Ordered obstruction reasons

The validator emits applicable reasons only in this order:

1. `STALE_SOURCE_TUPLE`
2. `UNKNOWN_INTERFACE`
3. `INTERFACE_NAME_MISMATCH`
4. `PRODUCER_ROLE_INVALID`
5. `CONSUMER_ROLE_INVALID`
6. `PROTOCOL_MISMATCH`
7. `SCHEMA_VERSION_MISMATCH`
8. `IDEMPOTENCY_MISMATCH`
9. `RETRY_POLICY_MISMATCH`
10. `DEFAULT_DENY_NOT_PRESERVED`
11. `CORRECTION_SEMANTICS_MISSING`
12. `ROLLBACK_SEMANTICS_MISSING`
13. `EVIDENCE_NOT_BOUND`
14. `AUTHORITY_PROMOTION_DETECTED`

Any applicable reason produces `BLOCKED`.

## Idempotency and retry boundary

`idempotent: true` and `retry_limit: 0` mean that the producer must not depend on transport retry to establish correctness. Consumers must use stable record identities and reject conflicting replays. A future retry-enabled generation requires a new contract generation and explicit duplicate, conflict, ordering, correction, and rollback semantics.

## Correction and rollback boundary

Append-only does not mean uncorrectable. Corrections must create separately identified records that reference the superseded record; they must not erase or silently rewrite prior evidence. Runtime reports must preserve the exact source and execution identities they summarize. Rollback or recovery must identify the checkpoint, the affected interface generation, the invalidated outputs, and the independently verified restored state.

## Default-deny and authority boundary

A compatible interface cannot grant permissions absent from the accepted producer and consumer scopes. Missing fields, unknown generations, unsupported protocols, unregistered consumers, conflicting replays, stale evidence, or incomplete correction/rollback data fail closed.

## Synthetic corpus

`fixtures/qso-interface-compatibility-v1.json` contains positive and hostile cases for both declared interfaces. Passing the corpus proves only deterministic agreement with this proposed fact surface at the recorded source generation.

## Skill-tree mapping

The work applies FYSA-120 capabilities from:

- `CAT-012` — technical writing and documentation consistency;
- `CAT-017` — evidence provenance and source-tuple binding;
- `CAT-031` — verified software engineering and invariant testing;
- `CAT-032` — distributed-systems interface composition;
- `CAT-040` — migration, correction, and rollback readiness;
- `CAT-052` — cryptographic provenance;
- `CAT-054` — cross-repository supply-chain integrity;
- `CAT-059` — attestation and evidence transport.

Proposed subdivision: **cross-repository interface differential conformance**, covering independently implemented compatibility evaluators, replay/conflict semantics, correction propagation, rollback witnesses, and reason/disposition convergence.

## Required architectural decisions

Before adoption, reviewers must approve final payload schemas, canonical bytes, record identities, ordering, duplicate and conflict behavior, correction and withdrawal semantics, retention, trusted time, signatures and key custody, consumer registration, migration, rollback, recovery, evidence retention, and resulting-default-branch verification.
