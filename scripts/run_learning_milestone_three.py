from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.learning_milestone_three import (
    ContradictionReconciler,
    DeclarativeSkill,
    PersistentCurriculum,
    SandboxReceiptIssuer,
    SeekerArtifactIngestor,
)
from qso_runtime.self_learning_cycle import SelfLearningOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run persistent QSO self-learning milestone three")
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    evidence = SeekerArtifactIngestor().ingest(artifact)
    episode = SelfLearningOrchestrator(promotion_threshold=0.55).run(
        "Build persistent self-learning capabilities", evidence
    )
    curriculum = PersistentCurriculum(args.state_dir / "curriculum.json").update(episode)
    reconciliation = ContradictionReconciler().reconcile([
        {"subject": "automatic-promotion", "value": False, "source": "fabric-policy"},
        {"subject": "automatic-promotion", "value": True, "source": "adversarial-fixture"},
        {"subject": "network-authority", "value": False, "source": "seeker-boundary"},
    ])
    skill = DeclarativeSkill.create(
        name="validate-evidence-bundle",
        purpose="Validate canonical Seeker evidence before evaluation",
        inputs=["bundle"],
        outputs=["validation-result"],
        steps=["validate schema", "verify content hashes", "record receipt"],
        required_capabilities=["read-candidate-memory"],
        tests=["reject malformed bundle", "reject network authority"],
    )
    receipt = SandboxReceiptIssuer().issue(
        skill,
        action="hash-content",
        input_payload={"evidence_hashes": [item["content_sha256"] for item in evidence]},
        approved=True,
    )
    report = {
        "episode": episode,
        "curriculum": curriculum,
        "reconciliation": reconciliation,
        "skill": skill.__dict__,
        "sandbox_receipt": receipt,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "freeze_hash": episode["freeze_hash"],
        "curriculum_runs": len(curriculum["runs"]),
        "contradictions": sum(d["status"] == "unresolved-contradiction" for d in reconciliation["decisions"]),
        "skill_hash": skill.skill_hash,
        "receipt_hash": receipt["receipt_hash"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
