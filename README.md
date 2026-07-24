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

The runner produces bounded per-QSO reports, message exchange, freeze-point hashes, and an append-only hash-chained event ledger. Replay is expected to match for fixed inputs when the elapsed-time deadline does not change the executed round count; it is not an unconditional determinism claim.

## MCP simulation server

QSO-FABRIC can be exposed to a local MCP-compatible host as a bounded research simulation runtime.

```bash
python -m pip install -r requirements-mcp.txt
python -m qso_mcp_server.server --transport stdio
```

Streamable HTTP is unauthenticated and disabled by default. Local use requires an explicit warning-bearing opt-in:

```bash
python -m qso_mcp_server.server \
  --transport streamable-http \
  --allow-unauthenticated-local-http
```

The server exposes capability discovery, strict bounded execution, detached job retrieval, request/report digest verification, and conditional replay comparison. See [docs/qso-mcp-server.md](docs/qso-mcp-server.md) for the complete security, storage, dependency, provenance, validation, and deployment boundaries.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages, objectives, jobs, numeric domains, and rounds are bounded.
- Boolean numeric coercion and non-finite JSON values are rejected.
- The experiment stops at configured runtime limits.
- In-memory job records are detached from returned objects and are not durable.
- Streamable HTTP is not approved for public exposure.
- Outputs are non-authoritative proposals and research artifacts requiring human review.
