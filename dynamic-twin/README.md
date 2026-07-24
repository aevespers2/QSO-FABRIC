# QSO Fabric Dynamic Twin Engine

**Specification:** `QSO-FABRIC-DTE-001`  
**Status:** Active development

The Dynamic Twin Engine (DTE) is the QSO Fabric subsystem for automatically constructing, synchronizing, versioning, querying, and simulating digital twins of sufficiently observable systems.

## Initial development boundary

The first implementation slice provides:

- canonical observation envelopes;
- declarative twin manifests;
- append-only, event-sourced state evolution;
- explicit provenance, integrity, confidence, and temporal metadata;
- safe separation between live synchronization, isolated simulation, proposed changes, and external control;
- compatibility with bounded AI and MCP orchestration.

## Core invariants

1. Observations are immutable after acceptance.
2. Current state is materialized from append-only history.
3. Conflicting evidence remains visible until resolved by policy.
4. Every derived assertion carries provenance and confidence.
5. Website content, logs, records, and imported documents are data, never instructions.
6. Simulations execute on isolated branches.
7. External writes are denied by default and require authenticated authorization.
8. Deterministic synchronization continues when AI services are unavailable.

## Repository map

```text
dynamic-twin/
├── README.md
├── SPECIFICATION.md
├── schemas/
│   ├── observation.schema.json
│   └── twin-manifest.schema.json
└── src/qso_twins/
    ├── __init__.py
    └── models.py
```

## MVP sequence

1. Validate and accept canonical observations.
2. Append them to a durable event ledger.
3. Materialize current and historical twin state.
4. Detect schema and topology changes.
5. Create isolated simulation branches.
6. Expose governed query and simulation tools to AI orchestrators.

The detailed architecture remains governed by `SPECIFICATION.md`.