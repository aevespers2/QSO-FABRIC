# QSO-FABRIC

Operational bounded runtime for Atlas, Nova, Orion, and Lyra, plus an optional role-based Experimenters collective.

## Run the four-QSO experiment

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The runner produces deterministic per-QSO reports, bounded message exchange, freeze-point hashes, and an append-only hash-chained event ledger.

## Run the Experimenters collective

```bash
python -m qso_runtime.experimenters \
  "Invent and validate a resilient scientific instrument" \
  --rounds 2 \
  --output artifacts/experimenters_report.json
```

The collective uses this bounded workflow:

`Futurist → Theorist → Inventor → Skeptic → Experimentalist → Observer → Synthesist → Engineer → Optimizer → Strategist → Ethicist/Governor → Archivist`

Each role contributes through a distinct scientific or invention lens. The runner preserves deterministic ordering, bounded messages, freeze-point state hashes, an append-only ledger, and an explicit human-review requirement. The existing Atlas/Nova/Orion/Lyra experiment remains unchanged.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured limits.
- Outputs are proposals and research artifacts requiring human review.
