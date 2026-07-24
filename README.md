# QSO-FABRIC

Operational bounded runtime for Atlas, Nova, Orion, and Lyra.

## Run

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The runner produces deterministic per-QSO reports, bounded message exchange, freeze-point hashes, and an append-only hash-chained event ledger.

## Emergence Garden

The Emergence Garden gives QSO research ideas an auditable lifecycle:

- `seed` — hypothesis recorded
- `sprout` — initial supporting evidence
- `sapling` — several positively weighted observations
- `tree` — substantial support with reproducible evidence
- `flower` — mature, strongly supported result
- `dormant` — paused without deletion
- `dead_branch` — rejected or falsified, but retained for provenance and possible revival

```python
from qso_runtime.emergence_garden import EmergenceGarden, Evidence


garden = EmergenceGarden()
idea = garden.plant(
    "Adaptive repair resonance",
    "Bounded resonance improves contradiction repair.",
    tags=("repair", "resonance"),
)

garden.add_evidence(
    idea.idea_id,
    Evidence(
        source="experiment-001",
        summary="Repair convergence improved across seeded trials.",
        confidence=0.86,
        reproducible=True,
    ),
)

assert garden.verify_ledger()
report = garden.snapshot()
```

Every change is recorded in a SHA-256 hash-chained event ledger. Failed paths are never silently erased, and snapshots use the schema identifier `qso.emergence-garden/v1` for future visualization and interchange.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
