from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.learning_persistence import ReviewedKnowledgeStore, SeekerEvidenceHandoff, consolidate_episodes
from qso_runtime.self_learning_cycle import SelfLearningOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reviewed QSO self-learning milestone two")
    parser.add_argument("--handoffs", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reviewer", default="human-reviewer")
    args = parser.parse_args()

    raw = json.loads(args.handoffs.read_text(encoding="utf-8"))
    handoffs = [SeekerEvidenceHandoff.from_record(item) for item in raw]
    if len(handoffs) < 4:
        raise ValueError("at least four Seeker handoffs are required")
    evidence = [handoff.as_learning_evidence(held_out=index >= len(handoffs) // 2) for index, handoff in enumerate(handoffs)]
    orchestrator = SelfLearningOrchestrator(promotion_threshold=0.55)
    first = orchestrator.run("Integrate Seeker evidence into reviewed durable QSO learning", evidence)
    second = orchestrator.run("Integrate Seeker evidence into reviewed durable QSO learning", evidence)
    store = ReviewedKnowledgeStore(args.store)
    promotion = store.promote(first, reviewer=args.reviewer, approved=True)
    consolidation = consolidate_episodes([first, second])
    rollback = store.rollback(promotion["before_snapshot"], reviewer=args.reviewer)
    result = {
        "first_episode": first,
        "second_episode": second,
        "promotion": promotion,
        "consolidation": consolidation,
        "rollback": rollback,
        "episodes_identical": first == second,
        "final_durable_count": rollback["restored_count"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "episodes_identical": result["episodes_identical"],
        "promoted_count": promotion["promoted_count"],
        "candidate_concepts": len(consolidation["concepts"]),
        "final_durable_count": result["final_durable_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
