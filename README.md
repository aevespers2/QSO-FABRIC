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

## Curiosity Engine

The Curiosity Engine launches deterministic, bounded research expeditions across four modes:

- cross-domain analogy
- contradiction hunting
- falsifiable experiment design
- counterfactual worlds

Each expedition is processed by Atlas, Nova, Orion, and Lyra, scored for novelty, evidence, impact, and safety, then written to a ranked discovery report with provenance hashes.

```bash
python -m qso_runtime.curiosity_engine \
  "Explore whether contradiction repair can improve QSO memory" \
  --seed 2987 \
  --expeditions 4 \
  --rounds 2 \
  --output artifacts/curiosity_report.json
```

The engine has no network, shell, credential, package-installation, wallet, or autonomous execution authority. Its findings remain proposals requiring human review.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
