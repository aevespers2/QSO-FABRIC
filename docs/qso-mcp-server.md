# QSO MCP simulation runtime

This server exposes the bounded QSO-FABRIC experiment through Model Context Protocol (MCP), allowing any MCP-compatible LLM or agent host to discover and run QSO simulations without receiving shell, credential, package-installation, unrestricted-network, or filesystem-write authority.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-mcp.txt
```

## Run over stdio

```bash
python -m qso_mcp_server.server --transport stdio
```

Example client configuration:

```json
{
  "mcpServers": {
    "qso": {
      "command": "python",
      "args": ["-m", "qso_mcp_server.server", "--transport", "stdio"],
      "cwd": "/absolute/path/to/QSO-FABRIC"
    }
  }
}
```

## Run over Streamable HTTP

```bash
python -m qso_mcp_server.server --transport streamable-http
```

The MCP endpoint is available at `http://127.0.0.1:8000/mcp` by default. Put an authenticated reverse proxy in front of it before exposing it outside a trusted host or network.

## MCP tools

| Tool | Purpose |
| --- | --- |
| `qso_capabilities` | Describe simulations, transports, roles, provenance, and denied authorities. |
| `qso_list_simulations` | Discover supported simulation types and parameter bounds. |
| `qso_run_simulation` | Run the bounded four-QSO experiment synchronously. |
| `qso_get_job` | Retrieve job metadata, report, and append-only event ledger. |
| `qso_list_jobs` | List recent jobs without embedding full reports. |
| `qso_verify_job` | Verify report digest and ledger validity. |
| `qso_replay_job` | Re-run the original request and compare deterministic digests. |

## Runtime contract

The initial adapter supports `four_qso_experiment`, backed directly by `qso_runtime.four_qso_experiment.run_experiment`. Inputs are validated before execution. Jobs are retained in a bounded in-memory store and evicted oldest-first. Reports retain the existing QSO freeze points, SHA-256 hash chain, per-QSO observations and inferences, and final proposals.

The HTTP mode is intentionally stateless at the MCP protocol layer, but job records live in the server process. For multi-process or durable deployments, replace `QSOService`'s in-memory job dictionary with a signed artifact store while preserving the same public methods.

## Validation

```bash
python -m pytest tests/test_qso_mcp_runtime.py
```

Use the MCP Inspector for protocol-level validation:

```bash
npx -y @modelcontextprotocol/inspector
```
