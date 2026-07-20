from __future__ import annotations

import json
from pathlib import Path

import pytest

from qso_runtime.learning_persistence import ReviewedKnowledgeStore, SeekerEvidenceHandoff, consolidate_episodes
from qso_runtime.self_learning_cycle import SelfLearningOrchestrator

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "seeker_handoffs.json"


def build_episode() -> dict:
    raw = json.loads(FIXTURE.read_text())
    handoffs = [SeekerEvidenceHandoff.from_record(item) for item in raw]
    evidence = [handoff.as_learning_evidence(held_out=index >= 2) for index, handoff in enumerate(handoffs)]
    return SelfLearningOrchestrator(promotion_threshold=0.55).run("Reviewed durable learning", evidence)


def test_seeker_handoff_rejects_network_authority() -> None:
    with pytest.raises(ValueError, match="network authority"):
        SeekerEvidenceHandoff.from_record({
            "query_id": "bad",
            "source_uri": "fixture://bad",
            "content": "unsafe",
            "qso_network_authority": True,
        })


def test_promotion_requires_review_and_rollback_restores(tmp_path: Path) -> None:
    episode = build_episode()
    store = ReviewedKnowledgeStore(tmp_path)
    with pytest.raises(PermissionError):
        store.promote(episode, reviewer="reviewer", approved=False)
    result = store.promote(episode, reviewer="reviewer", approved=True)
    assert result["promoted_count"] == 4
    assert len(list((tmp_path / "durable").glob("*.json"))) == 4
    rollback = store.rollback(result["before_snapshot"], reviewer="reviewer")
    assert rollback["restored_count"] == 0
    assert len(list((tmp_path / "durable").glob("*.json"))) == 0


def test_consolidation_stays_candidate_and_deterministic() -> None:
    episode = build_episode()
    first = consolidate_episodes([episode, episode])
    second = consolidate_episodes([episode, episode])
    assert first == second
    assert len(first["concepts"]) == 4
    assert all(item["layer"] == "candidate" for item in first["concepts"])
    assert first["automatic_promotion"] is False
    assert first["human_review_required"] is True
