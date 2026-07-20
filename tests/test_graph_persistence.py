from __future__ import annotations

from pathlib import Path

import pytest

from qso_runtime.graph_persistence import (
    GraphInvariantError,
    GraphMigrationRegistry,
    MultiGraphTransaction,
    VersionedGraphStore,
    consolidate_graph_runs,
)


def graph_state(prefix: str) -> dict:
    return {
        "schema_version": 1,
        "nodes": [
            {"node_id": f"{prefix}-1", "node_type": "claim", "payload": {}},
            {"node_id": f"{prefix}-2", "node_type": "evidence", "payload": {}},
        ],
        "edges": [
            {
                "edge_id": f"{prefix}-edge",
                "edge_type": "derived_from",
                "source": f"{prefix}-1",
                "target": f"{prefix}-2",
                "payload": {},
            }
        ],
    }


def test_orphan_edges_fail_closed(tmp_path: Path) -> None:
    store = VersionedGraphStore(tmp_path, "belief")
    invalid = {
        "schema_version": 1,
        "nodes": [{"node_id": "a", "node_type": "claim", "payload": {}}],
        "edges": [{"edge_id": "e", "edge_type": "contradicts", "source": "a", "target": "missing", "payload": {}}],
    }
    with pytest.raises(GraphInvariantError, match="orphaned edge"):
        store.write_snapshot(invalid)


def test_transaction_commit_and_restore_moves_all_pointers(tmp_path: Path) -> None:
    belief = VersionedGraphStore(tmp_path, "belief")
    knowledge = VersionedGraphStore(tmp_path, "knowledge")
    tx = MultiGraphTransaction(tmp_path / "transactions")
    first = tx.commit(
        memory_state={"records": ["m1"]},
        belief_store=belief,
        belief_state=graph_state("b1"),
        knowledge_store=knowledge,
        knowledge_state=graph_state("k1"),
    )
    second = tx.commit(
        memory_state={"records": ["m2"]},
        belief_store=belief,
        belief_state=graph_state("b2"),
        knowledge_store=knowledge,
        knowledge_state=graph_state("k2"),
    )
    assert first["transaction_id"] != second["transaction_id"]
    restored = tx.restore(first["transaction_id"], belief_store=belief, knowledge_store=knowledge)
    assert restored == first
    assert belief.read()["nodes"][0]["node_id"] == "b1-1"
    assert knowledge.read()["nodes"][0]["node_id"] == "k1-1"


def test_schema_migration_is_explicit_and_deterministic() -> None:
    registry = GraphMigrationRegistry()
    registry.register(1, 2, lambda state: {**state, "metadata": {"migrated": True}})
    original = graph_state("x")
    first = registry.migrate(original, 2)
    second = registry.migrate(original, 2)
    assert first == second
    assert first["schema_version"] == 2
    assert first["metadata"]["migrated"] is True
    with pytest.raises(ValueError, match="downgrade"):
        registry.migrate(first, 1)


def test_multi_run_consolidation_preserves_review_boundary() -> None:
    first = graph_state("a")
    second = graph_state("b")
    result = consolidate_graph_runs([first, second, first])
    assert len(result["nodes"]) == 4
    assert len(result["edges"]) == 2
    assert result["orphan_edge_ids"] == []
    assert result["automatic_promotion"] is False
    assert result["human_review_required"] is True
