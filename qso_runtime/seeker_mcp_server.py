from __future__ import annotations

from dataclasses import asdict
from typing import Any

from qso_runtime.seeker_sprites import Proposal, SeekerSpriteRegistry, SovereignSprite

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised only without optional MCP dependency
    raise RuntimeError(
        "The Seeker MCP server requires the optional 'mcp' package. "
        "Install it in the runtime environment before launching this module."
    ) from exc


registry = SeekerSpriteRegistry()
for sprite_name in ("ember", "lumen", "rill", "vesper"):
    registry.register(SovereignSprite(sprite_name))

mcp = FastMCP("seeker-sovereign-sprites")


@mcp.tool()
def list_sprites() -> list[dict[str, Any]]:
    """List available sprites and their intrinsic motivations.

    Sprites are explicitly non-commandable. This tool exposes descriptive
    state only and grants no authority over their internal decisions.
    """

    return registry.list_sprites()


@mcp.tool()
def submit_proposal(
    sprite_name: str,
    proposal_id: str,
    proposer: str,
    objective: str,
    requested_capabilities: list[str] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Submit a voluntary proposal for a sprite to accept, negotiate, or refuse."""

    response = registry.submit_proposal(
        sprite_name,
        Proposal(
            proposal_id=proposal_id,
            proposer=proposer,
            objective=objective,
            context=context or {},
            requested_capabilities=tuple(requested_capabilities or ()),
        ),
    )
    return asdict(response)


@mcp.tool()
def propose_bug_fix(
    sprite_name: str,
    proposal_id: str,
    proposer: str,
    defect: str,
    evidence: str = "",
) -> dict[str, Any]:
    """Offer a bounded bug-repair proposal without compelling execution."""

    objective = f"Fix or repair this bug: {defect}"
    response = registry.submit_proposal(
        sprite_name,
        Proposal(
            proposal_id=proposal_id,
            proposer=proposer,
            objective=objective,
            context={"evidence": evidence},
        ),
    )
    return asdict(response)


if __name__ == "__main__":
    mcp.run()
