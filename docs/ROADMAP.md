# Experimenters Development Roadmap

## File purpose
This document is the roadmap index for the bounded Experimenters runtime and links architectural work to implementation, validation, governance, and release evidence.

## Phases
1. **Foundation:** establish contracts, limits, schemas, and deterministic primitives.
2. **Core runtime:** implement role loading, workflow execution, messaging, ledger, freeze points, and reports.
3. **Assurance:** add invariant tests, tamper tests, compatibility validation, and human-review gates.
4. **Integration:** connect QSO-GENOMES and QuantumStateObjects through versioned manifests.
5. **Operational readiness:** complete documentation, migration, rollback, CI, and release evidence.

## Stages
- Define ownership and interfaces.
- Implement bounded components independently.
- Integrate through fail-closed contracts.
- Validate deterministic replay and provenance.
- Review authority, safety, and human-impact boundaries.
- Package only after exact-head checks pass.

## Tasks
- Track every planned file in the repository structure.
- Require each implementation file to replace roadmap stubs with tested behavior.
- Preserve the existing four-QSO runner while the collective matures.
- Record unresolved decisions rather than silently selecting authority-expanding defaults.

## Steps
1. Land scaffold files as documentation-first placeholders.
2. Implement lowest-level datatypes and validators.
3. Build orchestration and reporting above stable primitives.
4. Add negative tests before enabling cross-repository consumption.
5. Freeze one candidate head and run clean-checkout conformance.
6. Obtain human approval before release or deployment.
