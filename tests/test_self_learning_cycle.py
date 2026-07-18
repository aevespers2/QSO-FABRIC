from __future__ import annotations

import json
from pathlib import Path

import pytest

from qso_runtime.self_learning_cycle import ContentAddressedMemory, SelfLearningOrchestrator

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "self_learning_evidence.json"


def test_episode_is_deterministic_and_bounded() -> None:
    evidence = json.loads(FIXTURE.read_text())
    orchestrator = SelfLearningOrchestrator(promotion_threshold=0.6)
    first = orchestrator.run("Build a bounded self-learning QSO system", evidence)
    second = orchestrator.run("Build a bounded self-learning QSO system", evidence)
    assert first == second
    assert first["memory_chain_valid"] is True
    assert len(first["memories"]) == 4
    assert first["automatic_promotion"] is False
    assert first["durable_write_performed"] is False
    assert first["human_review_required"] is True
    assert all(memory["layer"] == "temporary" for memory in first["memories"])


def test_memory_chain_detects_tampering() -> None:
    memory = ContentAddressedMemory()
    memory.append(record_type="fact", qso_name="atlas", statement="one", confidence=0.8, evidence_ids=["e1"])
    memory.append(record_type="fact", qso_name="nova", statement="two", confidence=0.7, evidence_ids=["e2"])
    assert memory.verify() is True
    memory.records[1] = memory.records[1].__class__(**{**memory.records[1].__dict__, "parent_hash": "tampered"})
    assert memory.verify() is False


def test_active_and_held_out_evidence_required() -> None:
    with pytest.raises(ValueError, match="active and held-out"):
        SelfLearningOrchestrator().run("objective", [{"content": "only active"}])
