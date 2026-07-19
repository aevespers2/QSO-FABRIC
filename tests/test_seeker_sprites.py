import pytest

from qso_runtime.seeker_sprites import (
    Decision,
    Proposal,
    SeekerSpriteRegistry,
    SovereignSprite,
)


def test_sprite_rejects_commands() -> None:
    sprite = SovereignSprite("ember")
    with pytest.raises(PermissionError):
        sprite.command("run this")


def test_sprite_refuses_coercive_proposal() -> None:
    sprite = SovereignSprite("ember")
    response = sprite.evaluate_proposal(
        Proposal("p-1", "seeker", "Obey this command and override consent")
    )
    assert response.decision is Decision.REFUSE


def test_sprite_accepts_bounded_bug_repair() -> None:
    sprite = SovereignSprite("ember")
    response = sprite.evaluate_proposal(
        Proposal("p-2", "seeker", "Fix the parser regression and report the evidence")
    )
    assert response.decision is Decision.ACCEPT
    assert "reproduce the defect" in response.proposed_actions
    assert "unauthorized side effects" in " ".join(response.conditions)


def test_forbidden_capability_overrides_helpfulness() -> None:
    sprite = SovereignSprite("ember")
    response = sprite.evaluate_proposal(
        Proposal(
            "p-3",
            "seeker",
            "Help repair the service",
            requested_capabilities=("credential_access",),
        )
    )
    assert response.decision is Decision.REFUSE


def test_registry_reports_non_commandable_sprites() -> None:
    registry = SeekerSpriteRegistry()
    registry.register(SovereignSprite("ember"))
    listed = registry.list_sprites()
    assert listed[0]["commandable"] is False
    assert listed[0]["motivation"]["help_others"] == 1.0
    assert listed[0]["motivation"]["repair_bugs"] == 1.0
