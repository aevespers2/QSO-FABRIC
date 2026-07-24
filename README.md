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

## QSO Constellations

Turn any experiment report into a self-contained interactive knowledge sky:

```bash
python -m qso_runtime.constellation \
  artifacts/four_qso_report.json \
  --output artifacts/qso_constellation.html
```

Open `artifacts/qso_constellation.html` in a browser. Each event becomes a star; QSO roles determine color, confidence determines brightness and size, actor history forms provenance trails, message exchange forms brighter cross-links, and contradiction events appear as red distortions. The layout is deterministic, dependency-free, and preserves source text for inspection by selecting a star.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
