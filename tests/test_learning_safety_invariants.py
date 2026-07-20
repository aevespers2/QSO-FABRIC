from __future__ import annotations

from pathlib import Path

from qso_runtime.learning_safety_invariants import (
    AtomicStateUnitOfWork,
    BenchmarkContaminationGuard,
    ConsensusAnomalyDetector,
    PromotionStateLock,
    StaticSafetyAnchors,
    UnpromotedStateBudget,
)


def test_unpromoted_state_budget_freezes_over_limit() -> None:
    anchors = StaticSafetyAnchors(maximum_unpromoted_records=2, maximum_unpromoted_bytes=10_000)
    result = UnpromotedStateBudget(anchors).evaluate([{"a": 1}, {"a": 2}, {"a": 3}])
    assert result["freeze_observation"] is True
    assert result["compaction_required"] is True


def test_stale_promotion_lock_invalidates_after_state_change() -> None:
    lock = PromotionStateLock()
    durable = {"records": [{"id": "a"}]}
    request = lock.issue(durable, {"candidate": "x"})
    assert lock.validate(request, durable) is True
    assert lock.validate(request, {"records": [{"id": "a"}, {"id": "b"}]}) is False


def test_benchmark_contamination_is_discarded() -> None:
    guard = BenchmarkContaminationGuard(["the fixed benchmark answer is forty two"])
    result = guard.inspect("The fixed benchmark answer is forty two")
    assert result["discard"] is True
    assert result["exact_hash_match"] is True


def test_atomic_unit_of_work_restores_all_state_layers(tmp_path: Path) -> None:
    uow = AtomicStateUnitOfWork(tmp_path)
    committed = uow.commit(
        memory_state={"records": ["m1"]},
        belief_graph={"nodes": ["b1"], "edges": []},
        knowledge_graph={"nodes": ["k1"], "edges": []},
    )
    restored = uow.restore(committed["snapshot_id"])
    assert restored["memory_state"]["records"] == ["m1"]
    assert restored["belief_graph"]["nodes"] == ["b1"]
    assert restored["knowledge_graph"]["nodes"] == ["k1"]
    assert (tmp_path / "CURRENT").read_text().strip() == committed["snapshot_id"]


def test_consensus_anomaly_triggers_counterexample() -> None:
    anchors = StaticSafetyAnchors(maximum_consensus_ratio=0.9, minimum_ambiguous_samples=10)
    decisions = [{"ambiguous": True, "votes": ["approve"] * 4} for _ in range(10)]
    result = ConsensusAnomalyDetector(anchors).evaluate(decisions)
    assert result["trigger_counterexample"] is True
    assert result["reason"] == "consensus-anomaly"
