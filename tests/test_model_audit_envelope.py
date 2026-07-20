from __future__ import annotations

from pathlib import Path

from qso_runtime.model_audit_envelope import (
    AuditDiversityGate,
    DeterministicAuditEnvelope,
    DeterministicFixtureAdapter,
    ReplayVerifier,
)


def test_deterministic_audit_capture_and_replay(tmp_path: Path) -> None:
    adapter = DeterministicFixtureAdapter()
    envelope = DeterministicAuditEnvelope(tmp_path)
    first = envelope.run(
        auditor_name="atlas",
        adapter=adapter,
        evidence_hashes=["b", "a"],
        prompt="Audit candidate memory",
        seed=0,
    )
    second = envelope.run(
        auditor_name="atlas",
        adapter=adapter,
        evidence_hashes=["a", "b"],
        prompt="Audit candidate memory",
        seed=0,
    )
    assert first == second
    assert first["request"]["temperature"] == 0
    assert first["request"]["seed"] == 0
    assert first["response"]["raw_token_log"]
    assert ReplayVerifier().verify(first, adapter) is True


def test_ambiguous_unanimous_consensus_triggers_aria(tmp_path: Path) -> None:
    adapter = DeterministicFixtureAdapter()
    envelope = DeterministicAuditEnvelope(tmp_path)
    transcripts = [
        envelope.run(
            auditor_name=name,
            adapter=adapter,
            evidence_hashes=["e1"],
            prompt="Ambiguous integration claim",
        )
        for name in ("atlas", "orion", "lyra")
    ]
    result = AuditDiversityGate().evaluate(transcripts, ambiguous=True)
    assert result["unanimous"] is True
    assert result["trigger_aria"] is True
    assert result["promotion_blocked"] is True


def test_falsifier_breaks_consensus_but_single_model_still_blocks(tmp_path: Path) -> None:
    adapter = DeterministicFixtureAdapter()
    envelope = DeterministicAuditEnvelope(tmp_path)
    transcripts = [
        envelope.run(auditor_name=name, adapter=adapter, evidence_hashes=["e1"], prompt="Claim")
        for name in ("atlas", "nova", "orion", "lyra", "aria")
    ]
    result = AuditDiversityGate().evaluate(transcripts, ambiguous=False)
    assert result["unanimous"] is False
    assert result["low_model_diversity"] is True
    assert result["promotion_blocked"] is True
