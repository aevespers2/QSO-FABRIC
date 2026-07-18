from __future__ import annotations

from pathlib import Path

import pytest

from qso_runtime.review_operations import AuditMetrics, IncidentController, PromotionRegistry, ReviewAttestor


def test_signed_review_and_stale_lock(tmp_path: Path) -> None:
    attestor = ReviewAttestor(b"0123456789abcdef")
    decision = attestor.issue(
        reviewer="reviewer-a",
        candidate_hash="candidate-1",
        decision="approve",
        reason="validated",
        valid_through_hash="state-1",
    )
    assert attestor.verify(decision) is True
    registry = PromotionRegistry(tmp_path / "registry.json")
    state = registry.apply(decision, attestor=attestor, current_state_hash="state-1")
    assert state["promotions"]["candidate-1"]["status"] == "active"
    with pytest.raises(ValueError, match="stale"):
        registry.apply(decision, attestor=attestor, current_state_hash="state-2")


def test_revocation_and_incident_metrics(tmp_path: Path) -> None:
    attestor = ReviewAttestor(b"0123456789abcdef")
    registry = PromotionRegistry(tmp_path / "registry.json")
    approve = attestor.issue(reviewer="r", candidate_hash="c", decision="approve", reason="ok", valid_through_hash="s")
    registry.apply(approve, attestor=attestor, current_state_hash="s")
    revoke = attestor.issue(reviewer="r", candidate_hash="c", decision="revoke", reason="incident", valid_through_hash="s")
    reg = registry.apply(revoke, attestor=attestor, current_state_hash="s")
    incidents = IncidentController(tmp_path / "incident.json")
    incident_state = incidents.transition(actor="operator", target_state="containment", reason="revocation drill")
    metrics = AuditMetrics().summarize(reviews=[approve, revoke], incidents=incident_state, registry=reg)
    assert reg["promotions"]["c"]["status"] == "revoked"
    assert metrics["revoked_promotions"] == 1
    assert metrics["incident_state"] == "containment"
