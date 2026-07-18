from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.self_learning_cycle import SelfLearningOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one bounded QSO self-learning episode")
    parser.add_argument("objective")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--promotion-threshold", type=float, default=0.8)
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if not isinstance(evidence, list):
        raise ValueError("evidence file must contain a JSON list")
    report = SelfLearningOrchestrator(args.promotion_threshold).run(args.objective, evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "freeze_hash": report["freeze_hash"],
        "promotion_status": report["promotion_status"],
        "memory_chain_valid": report["memory_chain_valid"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
