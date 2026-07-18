from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReviewDecision:
    reviewer: str
    candidate_hash: str
    decision: str
    reason: str
    valid_through_hash: str
    attestation_hash: str
    signature: str


class ReviewAttestor:
    ALLOWED_DECISIONS = {"approve", "reject", "revoke"}

    def __init__(self, secret: bytes) -> None:
        if len(secret) < 16:
            raise ValueError("review signing secret must be at least 16 bytes")
        self.secret = secret

    def issue(
        self,
        *,
        reviewer: str,
        candidate_hash: str,
        decision: str,
        reason: str,
        valid_through_hash: str,
    ) -> ReviewDecision:
        if not reviewer.strip() or not reason.strip():
            raise ValueError("reviewer and reason are required")
        if decision not in self.ALLOWED_DECISIONS:
            raise ValueError("unsupported review decision")
        payload = {
            "reviewer": reviewer,
            "candidate_hash": candidate_hash,
            "decision": decision,
            "reason": reason,
            "valid_through_hash": valid_through_hash,
        }
        attestation_hash = sha256_json(payload)
        signature = hmac.new(self.secret, attestation_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        return ReviewDecision(**payload, attestation_hash=attestation_hash, signature=signature)

    def verify(self, decision: ReviewDecision) -> bool:
        expected = hmac.new(self.secret, decision.attestation_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        payload = {
            "reviewer": decision.reviewer,
            "candidate_hash": decision.candidate_hash,
            "decision": decision.decision,
            "reason": decision.reason,
            "valid_through_hash": decision.valid_through_hash,
        }
        return hmac.compare_digest(expected, decision.signature) and sha256_json(payload) == decision.attestation_hash


class PromotionRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"promotions": {}, "revocations": []}, indent=2) + "\n", encoding="utf-8")

    def load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def apply(self, decision: ReviewDecision, *, attestor: ReviewAttestor, current_state_hash: str) -> dict[str, Any]:
        if not attestor.verify(decision):
            raise PermissionError("invalid review signature")
        if decision.valid_through_hash != current_state_hash:
            raise ValueError("stale review attestation")
        state = self.load()
        if decision.decision == "approve":
            state["promotions"][decision.candidate_hash] = {
                "status": "active",
                "attestation_hash": decision.attestation_hash,
                "reviewer": decision.reviewer,
            }
        elif decision.decision == "revoke":
            if decision.candidate_hash not in state["promotions"]:
                raise KeyError("cannot revoke unknown promotion")
            state["promotions"][decision.candidate_hash]["status"] = "revoked"
            state["revocations"].append({
                "candidate_hash": decision.candidate_hash,
                "attestation_hash": decision.attestation_hash,
                "reviewer": decision.reviewer,
                "reason": decision.reason,
            })
        else:
            state["promotions"].setdefault(decision.candidate_hash, {})["status"] = "rejected"
        state["registry_hash"] = sha256_json({"promotions": state["promotions"], "revocations": state["revocations"]})
        self.path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return state


class IncidentController:
    ALLOWED_STATES = {"normal", "observation-frozen", "promotion-frozen", "containment", "recovery"}

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"state": "normal", "events": []}, indent=2) + "\n", encoding="utf-8")

    def transition(self, *, actor: str, target_state: str, reason: str) -> dict[str, Any]:
        if target_state not in self.ALLOWED_STATES:
            raise ValueError("unsupported incident state")
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason are required")
        state = json.loads(self.path.read_text(encoding="utf-8"))
        event = {
            "from": state["state"],
            "to": target_state,
            "actor": actor,
            "reason": reason,
        }
        event["event_hash"] = sha256_json(event)
        state["state"] = target_state
        state["events"].append(event)
        state["incident_hash"] = sha256_json({"state": state["state"], "events": state["events"]})
        self.path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return state


class AuditMetrics:
    def summarize(self, *, reviews: list[ReviewDecision], incidents: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
        decisions = {name: sum(1 for item in reviews if item.decision == name) for name in ReviewAttestor.ALLOWED_DECISIONS}
        active = sum(1 for item in registry.get("promotions", {}).values() if item.get("status") == "active")
        revoked = sum(1 for item in registry.get("promotions", {}).values() if item.get("status") == "revoked")
        summary = {
            "review_count": len(reviews),
            "decision_counts": decisions,
            "active_promotions": active,
            "revoked_promotions": revoked,
            "incident_state": incidents["state"],
            "incident_event_count": len(incidents.get("events", [])),
        }
        summary["metrics_hash"] = sha256_json(summary)
        return summary
