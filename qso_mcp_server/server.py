from __future__ import annotations

import argparse
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .runtime import QSOService

_MAX_JOBS = 1024
_HTTP_OPT_IN_ENV = "QSO_MCP_ALLOW_UNAUTHENTICATED_LOCAL_HTTP"


def _max_jobs_from_env() -> int:
    raw = os.environ.get("QSO_MCP_MAX_JOBS", "128")
    if not raw.isascii() or not raw.isdecimal() or str(int(raw)) != raw:
        raise ValueError("QSO_MCP_MAX_JOBS must be a canonical positive decimal integer")
    value = int(raw)
    if not 1 <= value <= _MAX_JOBS:
        raise ValueError(f"QSO_MCP_MAX_JOBS must be between 1 and {_MAX_JOBS}")
    return value


def _transport_from_env() -> str:
    value = os.environ.get("QSO_MCP_TRANSPORT", "stdio")
    if value not in {"stdio", "streamable-http"}:
        raise ValueError("QSO_MCP_TRANSPORT must be 'stdio' or 'streamable-http'")
    return value


def _local_http_env_opt_in() -> bool:
    value = os.environ.get(_HTTP_OPT_IN_ENV)
    if value is None:
        return False
    if value != "1":
        raise ValueError(f"{_HTTP_OPT_IN_ENV} must be exactly '1' when set")
    return True


service = QSOService(max_jobs=_max_jobs_from_env())
mcp = FastMCP(
    "QSO Simulation Runtime",
    instructions=(
        "Use QSO as a bounded research simulation runtime. Discover simulations before running them; "
        "treat all outputs as non-authoritative research artifacts requiring human review."
    ),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def qso_capabilities() -> dict[str, Any]:
    """Return QSO runtime capabilities, transports, roles, and denied authorities."""
    capabilities = service.capabilities()
    capabilities["transport_security"] = {
        "stdio_default": True,
        "streamable_http_authenticated": False,
        "streamable_http_local_opt_in_required": True,
    }
    return capabilities


@mcp.tool()
def qso_list_simulations() -> list[dict[str, Any]]:
    """List simulation types and their accepted parameters."""
    return service.list_simulations()


@mcp.tool()
def qso_run_simulation(
    objective: str,
    seed: int = 2987,
    rounds: int = 4,
    max_messages_per_qso: int = 8,
    max_message_chars: int = 600,
    max_runtime_seconds: float = 10.0,
) -> dict[str, Any]:
    """Run a bounded Atlas/Nova/Orion/Lyra research simulation."""
    return service.run(
        objective=objective,
        seed=seed,
        rounds=rounds,
        max_messages_per_qso=max_messages_per_qso,
        max_message_chars=max_message_chars,
        max_runtime_seconds=max_runtime_seconds,
    )


@mcp.tool()
def qso_get_job(job_id: str, include_report: bool = True) -> dict[str, Any]:
    """Retrieve a simulation job and optionally its full report and event ledger."""
    return service.get_job(job_id, include_report=include_report)


@mcp.tool()
def qso_list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    """List recent simulation jobs without embedding full reports."""
    return service.list_jobs(limit=limit)


@mcp.tool()
def qso_verify_job(job_id: str) -> dict[str, Any]:
    """Verify a completed job's request, report digest, and ledger status."""
    return service.verify_job(job_id)


@mcp.tool()
def qso_replay_job(job_id: str) -> dict[str, Any]:
    """Replay a job and compare report digests without claiming guaranteed determinism."""
    return service.replay(job_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Expose QSO-FABRIC through Model Context Protocol")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default=_transport_from_env(),
    )
    parser.add_argument(
        "--allow-unauthenticated-local-http",
        action="store_true",
        help=(
            "Explicitly allow the unauthenticated Streamable HTTP transport for local/trusted-host use. "
            "This does not make public exposure safe."
        ),
    )
    args = parser.parse_args()
    allow_local_http = args.allow_unauthenticated_local_http or _local_http_env_opt_in()
    if args.transport == "streamable-http" and not allow_local_http:
        parser.error(
            "streamable-http is unauthenticated and disabled by default; use "
            "--allow-unauthenticated-local-http only on a trusted local host"
        )
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
