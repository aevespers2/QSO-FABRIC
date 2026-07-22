# Mutation and Lifecycle Specification

A QSO change is represented as a proposal, authorization decision, patch, resulting object, provenance event, and optional snapshot.

## Mutation classes

- `immutable`: replacement requires a new object identifier.
- `append-only`: history may grow but existing records may not change.
- `externally-mutable`: designated authorities may change the object.
- `self-proposable`: the QSO may draft but not authorize changes.
- `self-modifiable`: bounded self-change is allowed by policy.
- `ephemeral`: runtime state may be discarded.
- `derived`: output must be reproducible from cited inputs.
- `constitutional`: threshold authorization is required.
- `mixed`: mutation rules are declared per compartment.

## Required transition record

Every accepted transition records previous hash, next hash, patch identifier, authorizer set, policy decision, timestamp, rollback reference, and provenance identifier.

## Safety invariants

Identity continuity, consent locks, constitutional governance, immutable evidence, and provenance records cannot be bypassed by a lower-authority mutation rule.
