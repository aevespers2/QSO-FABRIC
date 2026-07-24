from __future__ import annotations

import argparse
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .runtime import QSOService

service = QSOService(max_jobs=int(os.environ.get("QSO_MCP_MAX_JOBS", "128")))
mcp = FastMCP(
    "QSO Simulation Runtime",
    instructions=(
        "Use QSO as a bounded deterministic simulation runtime. Discover simulations before running them; "
        "treat all outputs as research artifacts requiring human review."
    ),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def qso_capabilities() -> dict[str, Any]:
    """Return QSO runtime capabilities, transports, roles, and denied authorities."""
    return service.capabilities()


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
    """Run a bounded deterministic Atlas/Nova/Orion/Lyra simulation."""
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
    """Verify a completed job's report digest and hash-chained ledger status."""
    return service.verify_job(job_id)


@mcp.tool()
def qso_replay_job(job_id: str) -> dict[str, Any]:
    """Replay a job from its original seed and limits and compare deterministic digests."""
    return service.replay(job_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Expose QSO-FABRIC through Model Context Protocol")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default=os.environ.get("QSO_MCP_TRANSPORT", "stdio"),
    )
    args = parser.parse_args()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
