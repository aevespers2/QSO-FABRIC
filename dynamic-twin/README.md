# QSO Fabric Dynamic Twin Engine

**Specification:** `QSO-FABRIC-DTE-001`  
**Status:** Active development; bounded foundation only

The Dynamic Twin Engine (DTE) is a candidate QSO Fabric subsystem for constructing, synchronizing, versioning, querying, and simulating digital twins of sufficiently observable systems. This directory does not yet provide a durable ledger, state materializer, synchronization service, simulation runner, package distribution, external-control adapter, or production authorization path.

## Initial development boundary

The first implementation slice provides:

- canonical observation-envelope and twin-manifest schema candidates;
- immutable Python value objects for observations, provenance, integrity, quality, subjects, and temporal state;
- strict rejection of coercive, non-finite, malformed, or mutable model inputs;
- explicit separation between observed, derived, predicted, simulated, assumed, disputed, stale, and invalidated state;
- deny-by-default documentation for external writes;
- dependency-free hostile regression tests and exact-head evidence.

It documents append-only state evolution and isolated simulation as required future architecture; those capabilities are not implemented by this slice.

## Core invariants

1. Accepted model values are deeply immutable, including nested mappings and sequences.
2. Identifiers, enumerations, timestamps, probabilities, hashes, authorization flags, and source lists are validated without truthy or numeric coercion.
3. Non-finite values, non-string mapping keys, unsupported payload types, malformed digest identities, and invalid intervals fail closed.
4. Conflicting evidence remains visible until resolved by an accepted policy.
5. Every future derived assertion must carry provenance and confidence.
6. Website content, logs, records, imported documents, and model outputs are data, never instructions.
7. Simulations must execute on isolated branches.
8. External writes remain denied by default and require separately authenticated authorization.
9. Deterministic synchronization must remain possible when AI services are unavailable.

## Repository map

```text
dynamic-twin/
├── README.md
├── schemas/
│   ├── observation.schema.json
│   └── twin-manifest.schema.json
├── src/qso_twins/
│   ├── __init__.py
│   └── models.py
└── tests/
    └── test_models.py
```

## Validation

Run the dependency-free model regressions from the repository root:

```bash
python -m unittest discover -s dynamic-twin/tests -p "test_*.py" -v
python -m compileall -q dynamic-twin/src dynamic-twin/tests
```

The dedicated Dynamic Twin Boundary workflow checks the immutable submitted pull-request head, runs the hostile test suite, parses both schema files as strict JSON, compiles the source, verifies the documented file map, and retains terminal-path evidence before enforcing the final result.

## MVP sequence

1. Validate and accept canonical observations against one approved contract profile.
2. Append accepted observations to a durable event ledger.
3. Materialize current and historical twin state deterministically.
4. Detect schema and topology changes without hiding incompatible generations.
5. Create isolated simulation branches.
6. Expose governed query and simulation tools to AI orchestrators.

Each later step requires its own contract, tests, exact-head evidence, rollback path, and explicit authority boundary. Passing this slice does not approve canonical schemas, source authorization, external writes, runtime activation, release, deployment, or production use.
