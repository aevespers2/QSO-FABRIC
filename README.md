# QSO-FABRIC

QSO-FABRIC is a bounded research harness for coordinating **Atlas, Nova, Orion, and Lyra** and recording their proposals, contradictions, freeze points, and append-only experiment evidence. This reconciliation candidate also contains the QSO file-format development subsystem used to explore schemas, registries, canonicalization, packaging, migration, and reversible conversion of local artifacts.

These are related but distinct surfaces:

- the **four-QSO runtime** produces bounded research artifacts;
- the **QSO format subsystem** validates and packages candidate representations;
- the **conversion tools** preserve source artifacts while producing derived report and provenance objects;
- the **architecture and governance documents** describe candidate boundaries and unresolved ownership decisions;
- none of those surfaces grants mutation, credential, capability, signing, release, deployment, publication, or canonical-state authority.

## Start here

| Goal | Read or run |
|---|---|
| Understand the bounded runtime | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`taskchain.md`](taskchain.md) |
| Understand QSO-FABRIC's portfolio role | [`docs/ALISTAIRE_ROLE.md`](docs/ALISTAIRE_ROLE.md) |
| Review candidate admission and overlap rules | [`docs/CANDIDATE_GOVERNANCE.md`](docs/CANDIDATE_GOVERNANCE.md) |
| Review format ownership questions | [`docs/FORMAT_GOVERNANCE.md`](docs/FORMAT_GOVERNANCE.md) |
| Review active cross-repository obstructions | [`docs/OBSTRUCTION_AND_GLUING.md`](docs/OBSTRUCTION_AND_GLUING.md) |
| Review current runtime output semantics | [`docs/OUTPUT_CONTRACTS.md`](docs/OUTPUT_CONTRACTS.md) |
| Review the format subsystem | [`quantum-state-objects/README.md`](quantum-state-objects/README.md) |
| Understand format trust boundaries | [`quantum-state-objects/docs/ARCHITECTURE.md`](quantum-state-objects/docs/ARCHITECTURE.md) |
| Review conversion behavior | [`quantum-state-objects/docs/CONVERSION-BOUNDARY.md`](quantum-state-objects/docs/CONVERSION-BOUNDARY.md) |
| Follow development guidance | [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) and [`quantum-state-objects/docs/IMPLEMENTATION-GUIDE.md`](quantum-state-objects/docs/IMPLEMENTATION-GUIDE.md) |
| Review reconciliation provenance | [`docs/RECONCILIATION_PROVENANCE.md`](docs/RECONCILIATION_PROVENANCE.md) |
| Review release blockers | [`release.md`](release.md) and [`punchlist.md`](punchlist.md) |
| See implementation history | [`changelog.md`](changelog.md) |

## Run the bounded four-QSO experiment

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The runner produces deterministic per-QSO reports, bounded message exchange, freeze-point hashes, and an append-only hash-chained event ledger. Wall-clock timeout behavior and unbounded objective length remain explicit release-review items; do not infer stronger resource bounds than the implemented limits provide.

## Convert a report without replacing its source

```bash
python quantum-state-objects/tools/convert_four_qso_report.py \
  artifacts/four_qso_report.json \
  --created-at 2026-07-23T00:00:00Z \
  --report-output artifacts/converted/four-qso.qreport.json \
  --provenance-output artifacts/converted/four-qso.qprov.json
```

The timestamp is an explicit conversion input. Reproducibility therefore requires the same source bytes, source-path string, timestamp, converter implementation, and serialization rules. The original report remains the source of record; converted objects are derived representations with separate identities and hashes.

## Reconciliation status

This candidate combines two previously independent histories without rewriting either:

- **PR #15 / `e358e8f5486f884c1479d365878d8b17a712594a`** supplies the architecture, onboarding, output-contract, candidate-governance, format-governance, obstruction, Pages, and release-punch-list documentation;
- **PR #19 / `29371d7a4956238de6860b2364e3cb9be57f0f80`** supplies the format implementation, hostile package validation, conversion tools, conformance tests, and current implementation-aligned root planning documents.

The reconciliation commit records both source heads as parents. Overlapping implementation-aligned root files follow PR #19 unless this candidate explicitly changes them; PR #15-only documentation is retained byte-for-byte. This preserves provenance while avoiding a destructive rebase or silent replacement of either lineage.

A passing workflow, valid package, successful conversion, or deterministic experiment is evidence for the exact source tested. It is not format acceptance, architecture approval, neutral contract ownership, runtime admission, or release authorization.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages, rounds, input sizes, package members, and extraction paths are bounded only where the applicable component explicitly enforces those limits.
- Validators inspect data; they do not execute embedded resources.
- Conversion does not authorize mutation, capability use, policy changes, source deletion, or canonical-state promotion.
- Documentation and implementation reconciliation does not accept the unresolved ownership, signing, privacy, recovery, publication, or release decisions.
- Outputs remain proposals and research artifacts requiring independent human review.

## Development posture

Work remains pre-release. Keep changes reversible, preserve exact source identities, add negative and rollback fixtures, and update `taskchain.md`, `release.md`, `punchlist.md`, and `changelog.md` whenever repository direction or evidence changes.
