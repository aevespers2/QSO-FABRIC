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

## MCP simulation server

QSO-FABRIC can be exposed to any MCP-compatible LLM or agent host as a bounded simulation runtime.

```bash
pip install -r requirements-mcp.txt
python -m qso_mcp_server.server --transport stdio
```

For a shared local endpoint:

```bash
python -m qso_mcp_server.server --transport streamable-http
```

The server exposes capability discovery, simulation execution, job retrieval, ledger verification, and deterministic replay. See [docs/qso-mcp-server.md](docs/qso-mcp-server.md) for client configuration and deployment guidance.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
