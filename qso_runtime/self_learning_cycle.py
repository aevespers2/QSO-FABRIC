from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

from .four_qso_experiment import QSO_ROLES


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source: str
    content: str
    content_sha256: str
    held_out: bool
    untrusted_text: bool = True
    executable: bool = False


@dataclass(frozen=True)
class MemoryRecord:
    record_type: str
    qso_name: str
    statement: str
    confidence: float
    evidence_ids: tuple[str, ...]
    parent_hash: str
    record_hash: str
    layer: str = "temporary"


@dataclass
class LearningEpisode:
    objective: str
    evidence: list[EvidenceRecord]
    memories: list[MemoryRecord] = field(default_factory=list)
    evaluations: dict[str, dict[str, Any]] = field(default_factory=dict)
    freeze_hash: str = ""
    promotion_status: str = "pending"
    human_review_required: bool = True


class ContentAddressedMemory:
    def __init__(self) -> None:
        self.records: list[MemoryRecord] = []

    @property
    def head_hash(self) -> str:
        return self.records[-1].record_hash if self.records else "GENESIS"

    def append(
        self,
        *,
        record_type: str,
        qso_name: str,
        statement: str,
        confidence: float,
        evidence_ids: list[str],
    ) -> MemoryRecord:
        if qso_name not in QSO_ROLES:
            raise ValueError(f"unknown QSO: {qso_name}")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        payload = {
            "record_type": record_type,
            "qso_name": qso_name,
            "statement": statement,
            "confidence": round(confidence, 6),
            "evidence_ids": sorted(evidence_ids),
            "parent_hash": self.head_hash,
            "layer": "temporary",
        }
        record = MemoryRecord(
            record_type=payload["record_type"],
            qso_name=payload["qso_name"],
            statement=payload["statement"],
            confidence=payload["confidence"],
            evidence_ids=tuple(payload["evidence_ids"]),
            parent_hash=payload["parent_hash"],
            record_hash=sha256_text(canonical_json(payload)),
        )
        self.records.append(record)
        return record

    def verify(self) -> bool:
        parent = "GENESIS"
        for record in self.records:
            payload = {
                "record_type": record.record_type,
                "qso_name": record.qso_name,
                "statement": record.statement,
                "confidence": record.confidence,
                "evidence_ids": list(record.evidence_ids),
                "parent_hash": parent,
                "layer": record.layer,
            }
            if record.parent_hash != parent:
                return False
            if sha256_text(canonical_json(payload)) != record.record_hash:
                return False
            parent = record.record_hash
        return True


class SelfLearningOrchestrator:
    def __init__(self, promotion_threshold: float = 0.8) -> None:
        if not 0.0 < promotion_threshold <= 1.0:
            raise ValueError("promotion_threshold must be in (0, 1]")
        self.promotion_threshold = promotion_threshold

    def _hypothesis_for(self, qso_name: str, objective: str, active_evidence: list[EvidenceRecord]) -> str:
        lens = {
            "atlas": "structural invariant",
            "nova": "falsifiable risk",
            "orion": "integration dependency",
            "lyra": "semantic distinction",
        }[qso_name]
        digest = sha256_text(canonical_json([e.content_sha256 for e in active_evidence]))[:12]
        return f"{qso_name} proposes a {lens} for '{objective}' grounded in evidence set {digest}."

    def _evaluate(self, memory: MemoryRecord, held_out: list[EvidenceRecord]) -> dict[str, Any]:
        support = 0
        statement_terms = set(memory.statement.lower().split())
        for evidence in held_out:
            evidence_terms = set(evidence.content.lower().split())
            if statement_terms & evidence_terms:
                support += 1
        ratio = support / len(held_out) if held_out else 0.0
        calibrated = round(min(1.0, 0.5 * memory.confidence + 0.5 * ratio), 6)
        return {
            "held_out_count": len(held_out),
            "support_count": support,
            "support_ratio": round(ratio, 6),
            "calibrated_score": calibrated,
            "passes_threshold": calibrated >= self.promotion_threshold,
        }

    def run(self, objective: str, evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
        if not objective.strip():
            raise ValueError("objective must not be empty")
        evidence: list[EvidenceRecord] = []
        for index, item in enumerate(evidence_items):
            content = str(item["content"])
            record = EvidenceRecord(
                evidence_id=str(item.get("evidence_id", f"evidence-{index + 1}")),
                source=str(item.get("source", "fixture")),
                content=content,
                content_sha256=sha256_text(content),
                held_out=bool(item.get("held_out", False)),
            )
            evidence.append(record)
        active = [e for e in evidence if not e.held_out]
        held_out = [e for e in evidence if e.held_out]
        if not active or not held_out:
            raise ValueError("both active and held-out evidence are required")

        memory = ContentAddressedMemory()
        episode = LearningEpisode(objective=objective, evidence=evidence)
        for qso_name in QSO_ROLES:
            statement = self._hypothesis_for(qso_name, objective, active)
            confidence = {"atlas": 0.78, "nova": 0.74, "orion": 0.76, "lyra": 0.72}[qso_name]
            memory_record = memory.append(
                record_type="hypothesis",
                qso_name=qso_name,
                statement=statement,
                confidence=confidence,
                evidence_ids=[e.evidence_id for e in active],
            )
            episode.memories.append(memory_record)
            episode.evaluations[qso_name] = self._evaluate(memory_record, held_out)

        episode.freeze_hash = sha256_text(
            canonical_json(
                {
                    "objective": objective,
                    "evidence": [asdict(e) for e in evidence],
                    "memories": [asdict(m) for m in episode.memories],
                    "evaluations": episode.evaluations,
                }
            )
        )
        all_pass = all(result["passes_threshold"] for result in episode.evaluations.values())
        episode.promotion_status = "review-ready" if all_pass else "retain-temporary"

        return {
            "schema_version": "qso-self-learning-episode-v1",
            "objective": episode.objective,
            "evidence": [asdict(e) for e in episode.evidence],
            "memories": [asdict(m) for m in episode.memories],
            "evaluations": episode.evaluations,
            "memory_chain_valid": memory.verify(),
            "freeze_hash": episode.freeze_hash,
            "promotion_status": episode.promotion_status,
            "human_review_required": episode.human_review_required,
            "automatic_promotion": False,
            "durable_write_performed": False,
        }
