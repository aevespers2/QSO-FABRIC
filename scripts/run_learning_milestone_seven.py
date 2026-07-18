from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.review_operations import AuditMetrics, IncidentController, PromotionRegistry, ReviewAttestor


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Milestone 7 reviewer and incident controls")
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    attestor = ReviewAttestor(b"ci-review-secret")
    registry = PromotionRegistry(args.state_dir / "promotion_registry.json")
    incidents = IncidentController(args.state_dir / "incident_state.json")

    approve = attestor.issue(
        reviewer="ci-reviewer",
        candidate_hash="candidate-1",
        decision="approve",
        reason="qualified under milestone seven",
        valid_through_hash="durable-state-1",
    )
    approved_state = registry.apply(approve, attestor=attestor, current_state_hash="durable-state-1")

    incident_state = incidents.transition(
        actor="ci-operator",
        target_state="containment",
        reason="exercise promotion revocation and containment",
    )

    revoke = attestor.issue(
        reviewer="ci-reviewer",
        candidate_hash="candidate-1",
        decision="revoke",
        reason="containment drill",
        valid_through_hash="durable-state-1",
    )
    revoked_state = registry.apply(revoke, attestor=attestor, current_state_hash="durable-state-1")
    metrics = AuditMetrics().summarize(reviews=[approve, revoke], incidents=incident_state, registry=revoked_state)

    report = {
        "schema_version": "qso-learning-milestone-seven-v1",
        "approve": approve.__dict__,
        "revoke": revoke.__dict__,
        "approved_state": approved_state,
        "revoked_state": revoked_state,
        "incident_state": incident_state,
        "metrics": metrics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "promotion_status": revoked_state["promotions"]["candidate-1"]["status"],
        "incident_state": incident_state["state"],
        "review_count": metrics["review_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
