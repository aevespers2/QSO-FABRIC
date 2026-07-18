from __future__ import annotations

import json
from pathlib import Path

import pytest

from qso_runtime.learning_milestone_three import (
    ContradictionReconciler,
    DeclarativeSkill,
    PersistentCurriculum,
    SandboxReceiptIssuer,
    SeekerArtifactIngestor,
)
from qso_runtime.self_learning_cycle import SelfLearningOrchestrator

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "tests" / "fixtures" / "qso_seeker_artifact.json"


def build_episode() -> dict:
    artifact = json.loads(ARTIFACT.read_text())
    evidence = SeekerArtifactIngestor().ingest(artifact)
    return SelfLearningOrchestrator(promotion_threshold=0.55).run(
        "Build persistent self-learning capabilities", evidence
    )


def test_seeker_artifact_ingestion_preserves_boundaries() -> None:
    evidence = SeekerArtifactIngestor().ingest(json.loads(ARTIFACT.read_text()))
    assert len(evidence) == 4
    assert all(item["retrieved_by"] == "seeker-proxy" for item in evidence)
    assert all(item["qso_network_authority"] is False for item in evidence)
    assert all(item["executable"] is False for item in evidence)


def test_curriculum_persists_without_duplicate_runs(tmp_path: Path) -> None:
    episode = build_episode()
    curriculum = PersistentCurriculum(tmp_path / "curriculum.json")
    first = curriculum.update(episode)
    second = curriculum.update(episode)
    assert first == second
    assert len(second["runs"]) == 1
    assert len(second["questions"]) == 1


def test_contradictions_are_preserved_not_overwritten() -> None:
    result = ContradictionReconciler().reconcile([
        {"subject": "claim-a", "value": True, "source": "e1"},
        {"subject": "claim-a", "value": False, "source": "e2"},
    ])
    decision = result["decisions"][0]
    assert decision["status"] == "unresolved-contradiction"
    assert decision["automatic_overwrite"] is False
    assert decision["human_review_required"] is True
    assert len(decision["preserved_values"]) == 2


def test_declarative_skill_is_non_executable_and_receipt_is_bounded() -> None:
    skill = DeclarativeSkill.create(
        name="validate-evidence-bundle",
        purpose="Validate a canonical evidence bundle before evaluation",
        inputs=["bundle"],
        outputs=["validation-result"],
        steps=["validate schema", "hash canonical content"],
        required_capabilities=["read-candidate-memory"],
        tests=["reject malformed bundle"],
    )
    assert skill.executable is False
    assert skill.layer == "candidate"
    issuer = SandboxReceiptIssuer()
    with pytest.raises(PermissionError):
        issuer.issue(skill, action="hash-content", input_payload={"a": 1}, approved=False)
    receipt = issuer.issue(skill, action="hash-content", input_payload={"a": 1}, approved=True)
    assert receipt["network_used"] is False
    assert receipt["filesystem_write"] is False
    assert receipt["subprocess_used"] is False
