"""Emergence Garden: a deterministic lifecycle for QSO research ideas.

The garden turns hypotheses into visible growth states without deleting failed
paths. Every mutation is recorded in a hash-chained ledger so a garden can be
replayed, audited, and rendered by a future UI.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Dict, Iterable, List, Mapping, Optional, Tuple
from uuid import uuid4


class GrowthStage(str, Enum):
    SEED = "seed"
    SPROUT = "sprout"
    SAPLING = "sapling"
    TREE = "tree"
    FLOWER = "flower"
    DORMANT = "dormant"
    DEAD_BRANCH = "dead_branch"


@dataclass(frozen=True)
class Evidence:
    """A bounded evidence contribution attached to one idea."""

    source: str
    summary: str
    confidence: float
    supports: bool = True
    reproducible: bool = False
    evidence_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence source cannot be empty")
        if not self.summary.strip():
            raise ValueError("evidence summary cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class GardenIdea:
    idea_id: str
    title: str
    hypothesis: str
    created_at: str
    stage: GrowthStage = GrowthStage.SEED
    evidence: List[Evidence] = field(default_factory=list)
    tags: Tuple[str, ...] = ()
    notes: List[str] = field(default_factory=list)
    archived_reason: Optional[str] = None

    @property
    def support_score(self) -> float:
        """Return a deterministic score in [-1, 1]."""
        if not self.evidence:
            return 0.0
        weighted = [
            item.confidence * (1.15 if item.reproducible else 1.0)
            * (1.0 if item.supports else -1.0)
            for item in self.evidence
        ]
        return max(-1.0, min(1.0, sum(weighted) / len(weighted)))

    @property
    def reproducible_support_count(self) -> int:
        return sum(1 for item in self.evidence if item.supports and item.reproducible)


@dataclass(frozen=True)
class GardenEvent:
    sequence: int
    timestamp: str
    event_type: str
    idea_id: str
    payload: Mapping[str, object]
    previous_hash: str
    event_hash: str


class EmergenceGarden:
    """Manage QSO ideas as an auditable, provenance-preserving garden."""

    def __init__(self) -> None:
        self._ideas: Dict[str, GardenIdea] = {}
        self._events: List[GardenEvent] = []

    @property
    def ideas(self) -> Mapping[str, GardenIdea]:
        return dict(self._ideas)

    @property
    def events(self) -> Tuple[GardenEvent, ...]:
        return tuple(self._events)

    def plant(
        self,
        title: str,
        hypothesis: str,
        *,
        tags: Iterable[str] = (),
        idea_id: Optional[str] = None,
    ) -> GardenIdea:
        title = title.strip()
        hypothesis = hypothesis.strip()
        if not title or not hypothesis:
            raise ValueError("title and hypothesis are required")
        identifier = idea_id or uuid4().hex
        if identifier in self._ideas:
            raise ValueError("idea_id already exists")
        idea = GardenIdea(
            idea_id=identifier,
            title=title,
            hypothesis=hypothesis,
            created_at=self._now(),
            tags=tuple(sorted({tag.strip() for tag in tags if tag.strip()})),
        )
        self._ideas[identifier] = idea
        self._record("idea_planted", identifier, {"title": title, "stage": idea.stage.value})
        return idea

    def add_evidence(self, idea_id: str, evidence: Evidence) -> GardenIdea:
        idea = self._require(idea_id)
        if any(item.evidence_id == evidence.evidence_id for item in idea.evidence):
            raise ValueError("evidence_id already exists on idea")
        old_stage = idea.stage
        idea.evidence.append(evidence)
        if idea.stage not in {GrowthStage.DEAD_BRANCH, GrowthStage.DORMANT}:
            idea.stage = self._derive_stage(idea)
        self._record(
            "evidence_added",
            idea_id,
            {
                "evidence": asdict(evidence),
                "old_stage": old_stage.value,
                "new_stage": idea.stage.value,
                "support_score": round(idea.support_score, 6),
            },
        )
        return idea

    def add_note(self, idea_id: str, note: str) -> GardenIdea:
        idea = self._require(idea_id)
        note = note.strip()
        if not note:
            raise ValueError("note cannot be empty")
        idea.notes.append(note)
        self._record("note_added", idea_id, {"note": note})
        return idea

    def set_dormant(self, idea_id: str, reason: str) -> GardenIdea:
        return self._archive(idea_id, GrowthStage.DORMANT, reason)

    def mark_dead_branch(self, idea_id: str, reason: str) -> GardenIdea:
        """Preserve a rejected idea and its complete provenance."""
        return self._archive(idea_id, GrowthStage.DEAD_BRANCH, reason)

    def revive(self, idea_id: str, reason: str) -> GardenIdea:
        idea = self._require(idea_id)
        old_stage = idea.stage
        idea.archived_reason = None
        idea.stage = self._derive_stage(idea)
        self._record(
            "idea_revived",
            idea_id,
            {"reason": reason.strip(), "old_stage": old_stage.value, "new_stage": idea.stage.value},
        )
        return idea

    def snapshot(self) -> Mapping[str, object]:
        ideas = []
        for idea in sorted(self._ideas.values(), key=lambda item: item.idea_id):
            row = asdict(idea)
            row["stage"] = idea.stage.value
            row["support_score"] = round(idea.support_score, 6)
            ideas.append(row)
        return {
            "schema": "qso.emergence-garden/v1",
            "ideas": ideas,
            "ledger_head": self._events[-1].event_hash if self._events else "GENESIS",
            "event_count": len(self._events),
        }

    def verify_ledger(self) -> bool:
        previous = "GENESIS"
        for expected_sequence, event in enumerate(self._events, start=1):
            if event.sequence != expected_sequence or event.previous_hash != previous:
                return False
            material = self._event_material(
                event.sequence,
                event.timestamp,
                event.event_type,
                event.idea_id,
                event.payload,
                event.previous_hash,
            )
            if sha256(material).hexdigest() != event.event_hash:
                return False
            previous = event.event_hash
        return True

    def _archive(self, idea_id: str, stage: GrowthStage, reason: str) -> GardenIdea:
        idea = self._require(idea_id)
        reason = reason.strip()
        if not reason:
            raise ValueError("archive reason cannot be empty")
        old_stage = idea.stage
        idea.stage = stage
        idea.archived_reason = reason
        self._record(
            "idea_archived",
            idea_id,
            {"reason": reason, "old_stage": old_stage.value, "new_stage": stage.value},
        )
        return idea

    @staticmethod
    def _derive_stage(idea: GardenIdea) -> GrowthStage:
        score = idea.support_score
        evidence_count = len(idea.evidence)
        reproducible = idea.reproducible_support_count
        if evidence_count >= 8 and score >= 0.80 and reproducible >= 3:
            return GrowthStage.FLOWER
        if evidence_count >= 5 and score >= 0.68 and reproducible >= 2:
            return GrowthStage.TREE
        if evidence_count >= 3 and score >= 0.50:
            return GrowthStage.SAPLING
        if evidence_count >= 1 and score > 0.0:
            return GrowthStage.SPROUT
        return GrowthStage.SEED

    def _record(self, event_type: str, idea_id: str, payload: Mapping[str, object]) -> None:
        sequence = len(self._events) + 1
        timestamp = self._now()
        previous = self._events[-1].event_hash if self._events else "GENESIS"
        material = self._event_material(sequence, timestamp, event_type, idea_id, payload, previous)
        self._events.append(
            GardenEvent(
                sequence=sequence,
                timestamp=timestamp,
                event_type=event_type,
                idea_id=idea_id,
                payload=dict(payload),
                previous_hash=previous,
                event_hash=sha256(material).hexdigest(),
            )
        )

    @staticmethod
    def _event_material(
        sequence: int,
        timestamp: str,
        event_type: str,
        idea_id: str,
        payload: Mapping[str, object],
        previous_hash: str,
    ) -> bytes:
        body = {
            "sequence": sequence,
            "timestamp": timestamp,
            "event_type": event_type,
            "idea_id": idea_id,
            "payload": payload,
            "previous_hash": previous_hash,
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _require(self, idea_id: str) -> GardenIdea:
        try:
            return self._ideas[idea_id]
        except KeyError as exc:
            raise KeyError("unknown garden idea: %s" % idea_id) from exc

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
