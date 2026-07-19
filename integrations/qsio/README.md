# QSIO Integration — QSO-FABRIC

Status: Phase 1–3 scaffold, disabled by default.

## Domain mapping

| Local concept | QSIO concept |
|---|---|
| fabric member / node | QSO |
| routed interaction / topology change | QSI |
| accepted immutable routing record | QSIO |
| membership / edge | Nexis |
| orchestration objective | Telion |
| routing history / evidence cache | Memora |
| observable topology | Lumen |
| protected topology commitment | Umbra commitment |
| validation result | Witness record |

Enable with `QSIO_INTEGRATION_ENABLED=true` only after contract, replay, and tamper tests pass. Local storage may cache QSIO-derived state but is not authoritative. Existing mutation paths remain aliases during migration and must be deprecated in Phase 10.

## Rollback

Disable `QSIO_INTEGRATION_ENABLED`, stop QSI submission, retain immutable received records, and rebuild the local cache from the last accepted replay checkpoint. Never rewrite or delete accepted QSIO records during rollback.

## Unsupported

Kernel-internal Canon evaluation, Quietus authority, signing-key custody, and authoritative ledger persistence are intentionally not implemented here.
