from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.graph_persistence import (
    GraphMigrationRegistry,
    MultiGraphTransaction,
    VersionedGraphStore,
    consolidate_graph_runs,
)


def make_state(prefix: str) -> dict:
    return {
        "schema_version": 1,
        "nodes": [
            {"node_id": f"{prefix}-claim", "node_type": "claim", "payload": {"prefix": prefix}},
            {"node_id": f"{prefix}-evidence", "node_type": "evidence", "payload": {"prefix": prefix}},
        ],
        "edges": [
            {
                "edge_id": f"{prefix}-derived",
                "edge_type": "derived_from",
                "source": f"{prefix}-claim",
                "target": f"{prefix}-evidence",
                "payload": {},
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Milestone 6 transactional graph qualification")
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    belief = VersionedGraphStore(args.state_dir, "belief")
    knowledge = VersionedGraphStore(args.state_dir, "knowledge")
    transactions = MultiGraphTransaction(args.state_dir / "transactions")

    first_belief = make_state("belief-a")
    first_knowledge = make_state("knowledge-a")
    first_tx = transactions.commit(
        memory_state={"records": ["memory-a"]},
        belief_store=belief,
        belief_state=first_belief,
        knowledge_store=knowledge,
        knowledge_state=first_knowledge,
    )

    second_belief = make_state("belief-b")
    second_knowledge = make_state("knowledge-b")
    second_tx = transactions.commit(
        memory_state={"records": ["memory-b"]},
        belief_store=belief,
        belief_state=second_belief,
        knowledge_store=knowledge,
        knowledge_state=second_knowledge,
    )

    restored = transactions.restore(first_tx["transaction_id"], belief_store=belief, knowledge_store=knowledge)

    migrations = GraphMigrationRegistry()
    migrations.register(1, 2, lambda state: {**state, "metadata": {"migration": "1-to-2"}})
    migrated = migrations.migrate(first_belief, 2)

    consolidation = consolidate_graph_runs([first_belief, second_belief, first_belief])
    report = {
        "schema_version": "qso-learning-milestone-six-v1",
        "first_transaction": first_tx,
        "second_transaction": second_tx,
        "restored_transaction": restored,
        "active_belief_state": belief.read(),
        "active_knowledge_state": knowledge.read(),
        "migrated_belief_state": migrated,
        "consolidation": consolidation,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "restored_transaction": restored["transaction_id"],
        "migrated_schema_version": migrated["schema_version"],
        "consolidated_nodes": len(consolidation["nodes"]),
        "orphan_edges": len(consolidation["orphan_edge_ids"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
