# QSO-FABRIC

QSO-FABRIC is a bounded research harness for coordinating **Atlas, Nova, Orion, and Lyra** and recording their proposals, contradictions, freeze points, and append-only experiment evidence. The current implementation branch also contains a candidate QSO file-format subsystem used to explore schemas, registries, canonicalization, packaging, migration, and reversible conversion of local artifacts.

These are related but distinct surfaces:

- the **four-QSO runtime** produces bounded research artifacts;
- the **QSO format subsystem** validates and packages candidate representations;
- the **conversion tools** preserve source artifacts while producing derived report and provenance objects;
- none of those surfaces grants mutation, credential, capability, signing, release, deployment, or canonical-state authority.

## Start here

| Goal | Read or run |
|---|---|
| Understand the bounded runtime | [`taskchain.md`](taskchain.md) and the command below |
| Review the format subsystem | [`quantum-state-objects/README.md`](quantum-state-objects/README.md) |
| Understand architecture and trust boundaries | [`quantum-state-objects/docs/ARCHITECTURE.md`](quantum-state-objects/docs/ARCHITECTURE.md) |
| Review conversion behavior | [`quantum-state-objects/docs/CONVERSION-BOUNDARY.md`](quantum-state-objects/docs/CONVERSION-BOUNDARY.md) |
| Follow development guidance | [`quantum-state-objects/docs/IMPLEMENTATION-GUIDE.md`](quantum-state-objects/docs/IMPLEMENTATION-GUIDE.md) |
| Review release blockers | [`release.md`](release.md) |
| See implementation history | [`changelog.md`](changelog.md) |

## Run the bounded four-QSO experiment

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The runner produces deterministic per-QSO reports, bounded message exchange, freeze-point hashes, and an append-only hash-chained event ledger.

## Convert a report without replacing its source

```bash
python quantum-state-objects/tools/convert_four_qso_report.py \
  artifacts/four_qso_report.json \
  --created-at 2026-07-23T00:00:00Z \
  --report-output artifacts/converted/four-qso.qreport.json \
  --provenance-output artifacts/converted/four-qso.qprov.json
```

The timestamp is an explicit conversion input. Reproducibility therefore requires the same source bytes **and** the same timestamp. The original report remains the source of record; converted objects are derived representations with separate identities and hashes.

## Repository status

This repository currently has two open lineages that must be reconciled before either can represent accepted repository direction:

- **PR #15** — documentation, architecture, onboarding, and format-governance candidate;
- **PR #19** — implementation and conformance candidate for the format subsystem and conversion tools.

A passing workflow, valid package, successful conversion, or deterministic experiment is evidence for the exact source tested. It is not format acceptance, architecture approval, neutral contract ownership, runtime admission, or release authorization.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages, rounds, input sizes, package members, and extraction paths are bounded by the applicable component.
- Validators inspect data; they do not execute embedded resources.
- Conversion does not authorize mutation, capability use, policy changes, or source deletion.
- Documentation and implementation lineages must be reconciled before publication or release claims.
- Outputs remain proposals and research artifacts requiring independent human review.

## Development posture

Work remains pre-release. Keep changes reversible, preserve exact source identities, add negative and rollback fixtures, and update `taskchain.md`, `release.md`, and `changelog.md` whenever repository direction or evidence changes.