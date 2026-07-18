from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class SeekerArtifactIngestor:
    def ingest(self, artifact: dict[str, Any]) -> list[dict[str, Any]]:
        if artifact.get("network_actor") != "seeker-proxy":
            raise ValueError("artifact network_actor must be seeker-proxy")
        if artifact.get("qso_network_authority") is not False:
            raise ValueError("QSO network authority must remain false")
        records = artifact.get("records") or artifact.get("results") or []
        if not isinstance(records, list) or not records:
            raise ValueError("artifact must contain non-empty records")
        evidence = []
        for index, record in enumerate(records):
            content = str(record.get("content") or record.get("title") or record.get("summary") or "")
            if not content:
                raise ValueError("artifact record content is empty")
            evidence.append({
                "evidence_id": str(record.get("id", f"artifact-{index + 1}")),
                "source": str(record.get("source_uri") or record.get("url") or "seeker-artifact"),
                "content": content,
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "retrieved_by": "seeker-proxy",
                "qso_network_authority": False,
                "executable": False,
                "held_out": bool(record.get("held_out", False)),
            })
        return evidence


class PersistentCurriculum:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"runs": [], "questions": []}, indent=2) + "\n", encoding="utf-8")

    def load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def update(self, episode: dict[str, Any]) -> dict[str, Any]:
        state = self.load()
        run = {
            "freeze_hash": episode["freeze_hash"],
            "promotion_status": episode["promotion_status"],
            "evaluation_scores": {
                name: result["calibrated_score"] for name, result in sorted(episode["evaluations"].items())
            },
        }
        if run not in state["runs"]:
            state["runs"].append(run)
        weakest = min(run["evaluation_scores"], key=run["evaluation_scores"].get)
        question = f"What evidence would most reduce uncertainty for {weakest} after freeze {episode['freeze_hash'][:12]}?"
        if question not in state["questions"]:
            state["questions"].append(question)
        state["state_hash"] = sha256_json({"runs": state["runs"], "questions": state["questions"]})
        self.path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return state


class ContradictionReconciler:
    def reconcile(self, claims: list[dict[str, Any]]) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for claim in claims:
            groups.setdefault(str(claim["subject"]), []).append(claim)
        decisions = []
        for subject, items in sorted(groups.items()):
            values = sorted({canonical_json(item["value"]) for item in items})
            status = "consistent" if len(values) == 1 else "unresolved-contradiction"
            decision = {
                "subject": subject,
                "status": status,
                "claims": items,
                "preserved_values": values,
                "automatic_overwrite": False,
                "human_review_required": status != "consistent",
            }
            decision["decision_hash"] = sha256_json(decision)
            decisions.append(decision)
        return {"decisions": decisions, "reconciliation_hash": sha256_json(decisions)}


@dataclass(frozen=True)
class DeclarativeSkill:
    name: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    steps: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    tests: tuple[str, ...]
    skill_hash: str
    executable: bool = False
    layer: str = "candidate"

    @classmethod
    def create(
        cls,
        *,
        name: str,
        purpose: str,
        inputs: list[str],
        outputs: list[str],
        steps: list[str],
        required_capabilities: list[str],
        tests: list[str],
    ) -> "DeclarativeSkill":
        payload = {
            "name": name,
            "purpose": purpose,
            "inputs": sorted(inputs),
            "outputs": sorted(outputs),
            "steps": steps,
            "required_capabilities": sorted(required_capabilities),
            "tests": tests,
            "executable": False,
            "layer": "candidate",
        }
        return cls(
            name=name,
            purpose=purpose,
            inputs=tuple(payload["inputs"]),
            outputs=tuple(payload["outputs"]),
            steps=tuple(steps),
            required_capabilities=tuple(payload["required_capabilities"]),
            tests=tuple(tests),
            skill_hash=sha256_json(payload),
        )


class SandboxReceiptIssuer:
    ALLOWED_ACTIONS = {"validate-json", "hash-content", "compare-values"}

    def issue(self, skill: DeclarativeSkill, *, action: str, input_payload: dict[str, Any], approved: bool) -> dict[str, Any]:
        if action not in self.ALLOWED_ACTIONS:
            raise PermissionError("action is not sandbox-allowlisted")
        if not approved:
            raise PermissionError("sandbox execution requires explicit approval")
        result = {
            "validate-json": isinstance(input_payload, dict),
            "hash-content": sha256_json(input_payload),
            "compare-values": len({canonical_json(v) for v in input_payload.values()}) <= 1,
        }[action]
        receipt = {
            "skill_hash": skill.skill_hash,
            "action": action,
            "input_hash": sha256_json(input_payload),
            "result": result,
            "network_used": False,
            "filesystem_write": False,
            "subprocess_used": False,
            "approved": True,
        }
        receipt["receipt_hash"] = sha256_json(receipt)
        return receipt
