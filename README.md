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
- Executable, script, Java-archive, and compressed-container signals are rejected by suffix, normalized media type, shebang, or recognized magic bytes.
- Structured input uses strict bounded JSON parsing with duplicate-key, non-finite-number, byte, depth, node, and text-injection rejection.
- Capability requests use an explicit bounded analytical allowlist; denied, malformed, and unknown capability names fail closed.
- An accepted artifact verdict is screening evidence only, not malware clearance or authorization to open, import, execute, unpack, or publish the object.

See [`docs/security/phantomblock-threat-briefing.md`](docs/security/phantomblock-threat-briefing.md) for the threat model and [`qso_runtime/security_boundary.py`](qso_runtime/security_boundary.py) for the implemented controls.
