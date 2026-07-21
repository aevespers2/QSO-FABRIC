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

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
- Executables, scripts, Java archives, and compressed containers are rejected from QSO artifact ingestion.
- Structured input uses bounded JSON parsing with byte, depth, node, and text-injection limits.
- Capability requests fail closed when they include process spawning, dynamic loading, filesystem writes, credentials, wallets, or unrestricted networking.

See [`docs/security/phantomblock-threat-briefing.md`](docs/security/phantomblock-threat-briefing.md) for the threat model and [`qso_runtime/security_boundary.py`](qso_runtime/security_boundary.py) for the implemented controls.
