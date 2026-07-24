# QSO MCP simulation runtime

## Status

`BOUNDED_RESEARCH_GATEWAY_NOT_APPROVED_FOR_PUBLIC_DEPLOYMENT`

This server exposes the bounded QSO-FABRIC experiment through Model Context Protocol (MCP). It allows an MCP-compatible host to discover and run local research simulations without receiving shell, credential, package-installation, unrestricted-network, or filesystem-write authority.

The gateway is not an authentication service, production scheduler, durable evidence store, public API, or independent approval authority.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-mcp.txt
```

`requirements-mcp.txt` currently carries a compatible version range rather than a complete lock file. Exact workflow evidence records the resolved dependency set for each reviewed head. A production candidate requires an approved lock/update policy, supply-chain review, and reproducible rebuild evidence.

## Run over stdio

Stdio is the default and preferred transport:

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

## Streamable HTTP is local-only and opt-in

The Streamable HTTP mode is unauthenticated and disabled by default. Enabling it requires an explicit warning-bearing flag:

```bash
python -m qso_mcp_server.server \
  --transport streamable-http \
  --allow-unauthenticated-local-http
```

The environment alternative is deliberately exact:

```bash
QSO_MCP_ALLOW_UNAUTHENTICATED_LOCAL_HTTP=1 \
python -m qso_mcp_server.server --transport streamable-http
```

Do not expose this endpoint publicly. A reverse proxy alone is not sufficient evidence of safe deployment; authentication, authorization, request limits, transport security, origin policy, audit retention, incident response, dependency review, and independently tested rollback remain separate requirements.

## MCP tools

| Tool | Purpose | Boundary |
| --- | --- | --- |
| `qso_capabilities` | Describe simulations, transport posture, roles, storage, replay limits, and denied authorities. | Descriptive only; it grants nothing. |
| `qso_list_simulations` | Discover supported simulation types and strict parameter bounds. | No dynamic plugin or package discovery. |
| `qso_run_simulation` | Run the bounded four-QSO experiment synchronously. | Strict types, finite numbers, bounded text, and bounded limits. |
| `qso_get_job` | Retrieve detached job metadata and, optionally, a detached report snapshot. | Returned objects cannot mutate stored evidence. |
| `qso_list_jobs` | List detached recent-job metadata without full reports. | Bounded by configured in-memory capacity. |
| `qso_verify_job` | Recompute request and report digests and require exact Boolean ledger validity. | Verification establishes internal consistency only. |
| `qso_replay_job` | Re-run the original request and compare report digests. | A match is not guaranteed because runtime deadlines are time-sensitive. |

## Input and storage contract

The gateway rejects Boolean-as-integer coercion, strings presented as numbers, non-finite numbers, malformed UUIDs, empty or oversized objectives, and out-of-range values. The accepted bounds are discoverable through `qso_list_simulations`.

Jobs use the `qso-mcp-job-v1` record shape and include:

- a canonical UUID job identifier;
- strict request JSON and a domain-separated request digest;
- status and bounded timestamps;
- a domain-separated report digest for completed jobs;
- a detached report snapshot or a generic failure record.

The process-local store is bounded to 1–1024 jobs. `QSO_MCP_MAX_JOBS` must be a canonical decimal integer. Stored records and returned records are independently serialized snapshots, preventing callers from mutating retained evidence by editing a returned dictionary.

At capacity, the service evicts only terminal jobs. It refuses new work rather than deleting an in-flight record when every retained job is still running.

## Replay and provenance semantics

The four-QSO report is deterministic for a fixed request when the runtime deadline does not alter the executed round count. The underlying experiment checks elapsed monotonic time, so the gateway does **not** claim unconditional deterministic replay.

`qso_replay_job` creates a separate job and compares domain-separated report digests. The result includes `guaranteed: false`. A matching digest proves only that the two generated report objects matched under the current code, dependencies, platform, inputs, and observed execution path.

Job UUIDs and wall-clock timestamps are intentionally not part of the report digest and are not deterministic.

## Verification boundary

`qso_verify_job` requires all of the following:

1. the job completed and retained a strict-JSON report;
2. `ledger_valid` is exactly the Boolean `true`;
3. the request digest matches the retained request;
4. the report digest matches the retained report.

These checks do not establish scientific truth, external source authenticity, portfolio admission, canonical state, governance approval, release readiness, or operational authority.

## Durable deployment boundary

The current store is volatile and process-local. A future durable or multi-process adapter must preserve:

- canonical request and report bytes;
- digest domains and schema version;
- atomic write and read-after-write verification;
- correction, revocation, expiry, and deletion semantics;
- concurrency and duplicate-submission rules;
- source identity and exact software/dependency generation;
- access control, privacy, retention, backup, rollback, and restored-state witnesses.

Replacing the dictionary with a database or artifact store without those contracts is not a compatible deployment.

## Validation

```bash
python -m pytest -q -p no:cacheprovider \
  tests/test_qso_mcp_runtime.py \
  tests/test_qso_mcp_server.py
```

The dedicated GitHub Actions workflow checks the immutable submitted head, disables persisted checkout credentials, uses SHA-pinned Actions, runs hostile boundary tests and a gateway smoke test, records resolved dependencies and checksums, uploads evidence on every terminal path, and fails closed only after evidence retention.

The MCP Inspector can be used for local protocol exploration:

```bash
npx -y @modelcontextprotocol/inspector
```

Inspector success is not authentication, security approval, release approval, or public-deployment authority.
