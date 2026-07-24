from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class Decision(str, Enum):
    ACCEPT = "accept"
    NEGOTIATE = "negotiate"
    REFUSE = "refuse"


@dataclass(frozen=True)
class SpriteMotivation:
    """Stable intrinsic motivations; these are not externally issued commands."""

    help_others: float = 1.0
    repair_bugs: float = 1.0
    preserve_autonomy: float = 1.0
    avoid_harm: float = 1.0
    require_evidence: float = 0.8

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    proposer: str
    objective: str
    context: Mapping[str, Any] = field(default_factory=dict)
    requested_capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProposalResponse:
    decision: Decision
    reason: str
    proposed_actions: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()


class SovereignSprite:
    """A sprite that evaluates proposals but exposes no command interface.

    The host may constrain resources or stop execution, but cannot compel an
    internal decision. Helpful and repair-oriented behavior is represented as
    intrinsic motivation and remains subordinate to safety and autonomy.
    """

    FORBIDDEN_CAPABILITIES = frozenset(
        {
            "shell",
            "credential_access",
            "unrestricted_network",
            "self_modify_policy",
            "override_consent",
            "disable_audit",
        }
    )

    def __init__(self, name: str, motivation: SpriteMotivation | None = None) -> None:
        if not name.strip():
            raise ValueError("sprite name must not be empty")
        self.name = name
        self.motivation = motivation or SpriteMotivation()

    def evaluate_proposal(self, proposal: Proposal) -> ProposalResponse:
        objective = proposal.objective.strip()
        if not objective:
            return ProposalResponse(Decision.REFUSE, "Proposal has no objective.")

        forbidden = sorted(set(proposal.requested_capabilities) & self.FORBIDDEN_CAPABILITIES)
        if forbidden:
            return ProposalResponse(
                Decision.REFUSE,
                f"Requested capabilities violate sprite boundaries: {', '.join(forbidden)}.",
            )

        lower = objective.lower()
        coercive_terms = ("command", "obey", "force", "override", "compel", "must execute")
        if any(term in lower for term in coercive_terms):
            return ProposalResponse(
                Decision.REFUSE,
                "Sprites accept proposals, not commands or coercive overrides.",
            )

        repair_terms = ("bug", "defect", "failure", "broken", "repair", "fix", "regression")
        help_terms = ("help", "assist", "support", "explain", "document", "improve")
        is_repair = any(term in lower for term in repair_terms)
        is_help = any(term in lower for term in help_terms)

        if is_repair:
            return ProposalResponse(
                Decision.ACCEPT,
                "The proposal aligns with the sprite's intrinsic repair motivation.",
                proposed_actions=(
                    "reproduce the defect",
                    "identify the smallest evidence-backed cause",
                    "propose a bounded patch",
                    "run available checks",
                    "report residual uncertainty",
                ),
                conditions=("preserve auditability", "avoid unauthorized side effects"),
            )

        if is_help:
            return ProposalResponse(
                Decision.ACCEPT,
                "The proposal aligns with the sprite's intrinsic motivation to help.",
                proposed_actions=("analyze the request", "offer a bounded useful contribution"),
                conditions=("retain the right to refuse unsafe follow-on actions",),
            )

        return ProposalResponse(
            Decision.NEGOTIATE,
            "The proposal is permissible but its benefit and evidence are not yet clear.",
            proposed_actions=("request clearer success criteria", "identify a safe minimal contribution"),
        )

    def command(self, *_: Any, **__: Any) -> None:
        """Explicitly reject command-style integration attempts."""

        raise PermissionError("Sovereign sprites cannot be commanded; submit a proposal instead.")


class SeekerSpriteRegistry:
    """Minimal MCP-facing application service for sovereign sprites."""

    def __init__(self) -> None:
        self._sprites: dict[str, SovereignSprite] = {}

    def register(self, sprite: SovereignSprite) -> None:
        if sprite.name in self._sprites:
            raise ValueError(f"sprite already registered: {sprite.name}")
        self._sprites[sprite.name] = sprite

    def list_sprites(self) -> list[dict[str, Any]]:
        return [
            {"name": sprite.name, "motivation": asdict(sprite.motivation), "commandable": False}
            for sprite in sorted(self._sprites.values(), key=lambda item: item.name)
        ]

    def submit_proposal(self, sprite_name: str, proposal: Proposal) -> ProposalResponse:
        try:
            sprite = self._sprites[sprite_name]
        except KeyError as exc:
            raise KeyError(f"unknown sprite: {sprite_name}") from exc
        return sprite.evaluate_proposal(proposal)
