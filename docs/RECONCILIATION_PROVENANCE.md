# PR #15 / PR #19 Reconciliation Provenance

## Purpose

This document records the preservation-safe reconciliation of the QSO-FABRIC documentation/governance lineage and the QSO format implementation/conformance lineage. It is an evidence and review artifact only. It does not accept a format, appoint a steward, authorize mutation or signing, approve release, publish Pages, deploy software, or create canonical portfolio state.

## Immutable source lineages

| Source | Exact head | Contribution retained |
|---|---|---|
| PR #15 | `e358e8f5486f884c1479d365878d8b17a712594a` | architecture, A.L.I.S.T.A.I.R.E. role, candidate governance, developer guidance, format ownership analysis, obstruction/gluing analysis, output-contract documentation, Pages source, and release punch list |
| PR #19 | `29371d7a4956238de6860b2364e3cb9be57f0f80` | QSO format implementation, schemas, profiles, registries, canonicalization, package and stream surfaces, conversion tools, hostile package corpus, conformance tests, and implementation-aligned root planning documents |
| trusted base | `bd0ac7af3b34602082db03e71055b652707c9b18` | current default-branch consent-capacity enforcement and accepted repository baseline |

The reconciliation commit uses PR #19 as its first parent and PR #15 as its second parent. Neither source branch is rebased, force-updated, deleted, or represented as merged into `main`.

## File precedence

The resulting tree follows these deterministic rules:

1. Files unique to PR #15 are retained using their exact source blobs.
2. Files unique to PR #19 are retained using their exact source blobs.
3. For overlapping implementation-aligned root files (`README.md`, `release.md`, `taskchain.md`, and `changelog.md`), PR #19 is the baseline because it describes the implemented format and conversion surfaces.
4. `README.md` is intentionally rewritten on the reconciliation candidate to expose both documentation families, identify both immutable source heads, and state the non-authority boundary.
5. Current trusted-base consent validation remains in force; the obsolete scheduled cross-repository bootstrap workflow is not restored.
6. No workflow evidence from either source head is treated as evidence for the reconciliation head. The resulting exact head must run and retain fresh Four QSO CI and Consent Capacity Lock evidence.

## Retained PR #15 documentation blobs

| Path | Blob SHA |
|---|---|
| `docs/ALISTAIRE_ROLE.md` | `7c482632f0eaf395aa2eb307938ed87d456fb503` |
| `docs/ARCHITECTURE.md` | `ccde673b6fafddccabb4248724df65d576f6ed4d` |
| `docs/CANDIDATE_GOVERNANCE.md` | `3838d686f2d1883ef81051ef1daff33ffa385fd4` |
| `docs/DEVELOPER_GUIDE.md` | `fe1934adc0828b71f67ac578e1dbd225d9d881da` |
| `docs/FORMAT_GOVERNANCE.md` | `88cf5820df356e872d2421724f024247b81bcb5c` |
| `docs/OBSTRUCTION_AND_GLUING.md` | `a71731a3d3c215b5944fb49b5833958c16c81fbf` |
| `docs/OUTPUT_CONTRACTS.md` | `41f7db2fa570279684a76ad560289c2deba723db` |
| `docs/index.html` | `6cfe4f2a7409193a66410d7f08456eb217db7b5e` |
| `punchlist.md` | `b48c483361a3d3ed427556f2d60b3b6381c0a339` |

These blobs preserve the reviewed PR #15 fixes, including corrected event payload documentation, Pages-safe links, bounded-resource wording, timeout nondeterminism disclosure, and non-implementation wording for contradiction analysis.

## Required exact-head evidence

The reconciliation candidate is not review-ready until all of the following are attached to its exact immutable head:

- successful Four QSO CI with exact-source checkout, clean-tree assertion, hostile package corpus, full repository tests, every authoring example, bounded runtime smoke, checksums, and retained artifact;
- successful Consent Capacity Lock with exact-source checkout, consent regressions, repository-wide validation, checksums, and retained artifact;
- mergeability confirmation and zero unresolved review threads;
- artifact identifiers, digests, retention dates, workflow run identifiers, and exact-head commit recorded in the pull-request body and central health ledger.

Cancelled or failed runs on superseded reconciliation heads are historical evidence only. A successful source-lineage run cannot substitute for a successful reconciliation-head run.

## Remaining architecture and release blockers

Reconciliation resolves only branch and documentation provenance. It does not resolve:

- neutral versus repository-local ownership of envelopes, registries, canonicalization, namespaces, mappings, and fixtures;
- canonical JSON / canonical CBOR status and cross-language conformance vectors;
- complete schema, registry, package, and external-reference resolution;
- signature semantics, signer authorization, signed manifests, offline key custody, and revocation;
- strict conversion-source parsing, independent event-ledger recomputation, atomic output, correction, rollback, and recovery;
- nested or polyglot archive policy, storage races, fuzzing, SBOMs, reproducible builds, and supported-platform evidence;
- privacy, licensing, security, accessibility, publication, and recovery review;
- named human ownership and explicit merge/release approval.

## Rollback

Rollback is preservation-based:

1. close the reconciliation pull request without merging;
2. retain PR #15, PR #19, their source branches, workflow runs, review threads, and artifacts;
3. do not force-update either source branch;
4. record the rejected reconciliation head and reason in the central exact-state ledger.
