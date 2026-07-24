"""Deterministic, provenance-preserving lifecycle for bounded research ideas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from hashlib import sha256
import json
import math
from types import MappingProxyType
from typing import Iterable, Mapping, Optional

_MAX_TITLE_CHARS = 240
_MAX_HYPOTHESIS_CHARS = 8_000
_MAX_TEXT_CHARS = 4_000
_MAX_TAGS = 64
_MAX_TAG_CHARS = 128
_MAX_IDENTIFIER_CHARS = 256


class GrowthStage(str, Enum):
    SEED = "seed"
    SPROUT = "sprout"
    SAPLING = "sapling"
    TREE = "tree"
    FLOWER = "flower"
    DORMANT = "dormant"
    DEAD_BRANCH = "dead_branch"


def _bounded_text(value: object, name: str, limit: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    if len(normalized) > limit:
        raise ValueError(f"{name} exceeds {limit} characters")
    return normalized


def _strict_bool(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be a Boolean")
    return value


def _confidence(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be a finite real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("confidence must be finite")
    if not 0.0 <= number <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    return number


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _content_id(prefix: str, material: Mapping[str, object]) -> str:
    digest = sha256(_canonical_json(material).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:32]}"


def _normalize_tags(tags: Iterable[str]) -> tuple[str, ...]:
    if isinstance(tags, (str, bytes)):
        raise TypeError("tags must be an iterable of strings, not a string")
    normalized: set[str] = set()
    for tag in tags:
        normalized.add(_bounded_text(tag, "tag", _MAX_TAG_CHARS))
        if len(normalized) > _MAX_TAGS:
            raise ValueError(f"tags may contain at most {_MAX_TAGS} unique values")
    return tuple(sorted(normalized))


def _identifier(value: object, name: str) -> str:
    return _bounded_text(value, name, _MAX_IDENTIFIER_CHARS)


@dataclass(frozen=True)
class Evidence:
    """One immutable, content-identified evidence contribution."""

    source: str
    summary: str
    confidence: float
    supports: bool = True
    reproducible: bool = False
    evidence_id: str = field(default="")

    def __post_init__(self) -> None:
        source = _bounded_text(self.source, "evidence source", _MAX_TEXT_CHARS)
        summary = _bounded_text(self.summary, "evidence summary", _MAX_TEXT_CHARS)
        confidence = _confidence(self.confidence)
        supports = _strict_bool(self.supports, "supports")
        reproducible = _strict_bool(self.reproducible, "reproducible")
        material = {
            "source": source,
            "summary": summary,
            "confidence": confidence,
            "supports": supports,
            "reproducible": reproducible,
        }
        evidence_id = (
            _identifier(self.evidence_id, "evidence_id")
            if self.evidence_id
            else _content_id("evidence", material)
        )
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "supports", supports)
        object.__setattr__(self, "reproducible", reproducible)
        object.__setattr__(self, "evidence_id", evidence_id)


@dataclass(frozen=True)
class GardenIdea:
    idea_id: str
    title: str
    hypothesis: str
    created_at: str
    stage: GrowthStage = GrowthStage.SEED
    evidence: tuple[Evidence, ...] = ()
    tags: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    archived_reason: Optional[str] = None

    @property
    def support_score(self) -> float:
        if not self.evidence:
            return 0.0
        weighted = [
            item.confidence
            * (1.15 if item.reproducible else 1.0)
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
    """Manage ideas with immutable state values and a deterministic hash chain."""

    def __init__(self) -> None:
        self._ideas: dict[str, GardenIdea] = {}
        self._events: list[GardenEvent] = []

    @property
    def ideas(self) -> Mapping[str, GardenIdea]:
        return MappingProxyType(dict(self._ideas))

    @property
    def events(self) -> tuple[GardenEvent, ...]:
        return tuple(self._events)

    def plant(
        self,
        title: str,
        hypothesis: str,
        *,
        tags: Iterable[str] = (),
        idea_id: Optional[str] = None,
    ) -> GardenIdea:
        title_value = _bounded_text(title, "title", _MAX_TITLE_CHARS)
        hypothesis_value = _bounded_text(hypothesis, "hypothesis", _MAX_HYPOTHESIS_CHARS)
        tag_values = _normalize_tags(tags)
        identifier = (
            _identifier(idea_id, "idea_id")
            if idea_id is not None
            else _content_id(
                "idea",
                {"title": title_value, "hypothesis": hypothesis_value, "tags": tag_values},
            )
        )
        if identifier in self._ideas:
            raise ValueError("idea_id already exists")
        created_at = self._logical_time(len(self._events) + 1)
        idea = GardenIdea(
            idea_id=identifier,
            title=title_value,
            hypothesis=hypothesis_value,
            created_at=created_at,
            tags=tag_values,
        )
        self._ideas[identifier] = idea
        self._record(
            "idea_planted",
            identifier,
            {
                "title": title_value,
                "hypothesis_sha256": sha256(hypothesis_value.encode("utf-8")).hexdigest(),
                "tags": list(tag_values),
                "stage": idea.stage.value,
            },
        )
        return idea

    def add_evidence(self, idea_id: str, evidence: Evidence) -> GardenIdea:
        if not isinstance(evidence, Evidence):
            raise TypeError("evidence must be an Evidence instance")
        idea = self._require(idea_id)
        if any(item.evidence_id == evidence.evidence_id for item in idea.evidence):
            raise ValueError("evidence_id already exists on idea")
        old_stage = idea.stage
        evidence_values = idea.evidence + (evidence,)
        candidate = replace(idea, evidence=evidence_values)
        if old_stage not in {GrowthStage.DEAD_BRANCH, GrowthStage.DORMANT}:
            candidate = replace(candidate, stage=self._derive_stage(candidate))
        self._ideas[idea_id] = candidate
        self._record(
            "evidence_added",
            idea_id,
            {
                "evidence": asdict(evidence),
                "old_stage": old_stage.value,
                "new_stage": candidate.stage.value,
                "support_score": round(candidate.support_score, 6),
            },
        )
        return candidate

    def add_note(self, idea_id: str, note: str) -> GardenIdea:
        idea = self._require(idea_id)
        note_value = _bounded_text(note, "note", _MAX_TEXT_CHARS)
        candidate = replace(idea, notes=idea.notes + (note_value,))
        self._ideas[idea_id] = candidate
        self._record("note_added", idea_id, {"note": note_value})
        return candidate

    def set_dormant(self, idea_id: str, reason: str) -> GardenIdea:
        return self._archive(idea_id, GrowthStage.DORMANT, reason)

    def mark_dead_branch(self, idea_id: str, reason: str) -> GardenIdea:
        return self._archive(idea_id, GrowthStage.DEAD_BRANCH, reason)

    def revive(self, idea_id: str, reason: str) -> GardenIdea:
        idea = self._require(idea_id)
        reason_value = _bounded_text(reason, "revival reason", _MAX_TEXT_CHARS)
        old_stage = idea.stage
        candidate = replace(idea, archived_reason=None)
        candidate = replace(candidate, stage=self._derive_stage(candidate))
        self._ideas[idea_id] = candidate
        self._record(
            "idea_revived",
            idea_id,
            {
                "reason": reason_value,
                "old_stage": old_stage.value,
                "new_stage": candidate.stage.value,
            },
        )
        return candidate

    def snapshot(self) -> Mapping[str, object]:
        rows: list[dict[str, object]] = []
        for idea in sorted(self._ideas.values(), key=lambda item: item.idea_id):
            rows.append(
                {
                    "idea_id": idea.idea_id,
                    "title": idea.title,
                    "hypothesis": idea.hypothesis,
                    "created_at": idea.created_at,
                    "stage": idea.stage.value,
                    "evidence": [asdict(item) for item in idea.evidence],
                    "tags": list(idea.tags),
                    "notes": list(idea.notes),
                    "archived_reason": idea.archived_reason,
                    "support_score": round(idea.support_score, 6),
                }
            )
        snapshot = {
            "schema": "qso.emergence-garden/v1",
            "clock": "deterministic-logical-sequence",
            "ideas": rows,
            "ledger_head": self._events[-1].event_hash if self._events else "GENESIS",
            "event_count": len(self._events),
        }
        _canonical_json(snapshot)
        return snapshot

    def verify_ledger(self) -> bool:
        previous = "GENESIS"
        for expected_sequence, event in enumerate(self._events, start=1):
            if event.sequence != expected_sequence:
                return False
            if event.timestamp != self._logical_time(expected_sequence):
                return False
            if event.previous_hash != previous:
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
        reason_value = _bounded_text(reason, "archive reason", _MAX_TEXT_CHARS)
        candidate = replace(idea, stage=stage, archived_reason=reason_value)
        self._ideas[idea_id] = candidate
        self._record(
            "idea_archived",
            idea_id,
            {
                "reason": reason_value,
                "old_stage": idea.stage.value,
                "new_stage": stage.value,
            },
        )
        return candidate

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
        event_type_value = _bounded_text(event_type, "event_type", 128)
        identifier = _identifier(idea_id, "idea_id")
        canonical_payload = json.loads(_canonical_json(dict(payload)))
        sequence = len(self._events) + 1
        timestamp = self._logical_time(sequence)
        previous = self._events[-1].event_hash if self._events else "GENESIS"
        material = self._event_material(
            sequence,
            timestamp,
            event_type_value,
            identifier,
            canonical_payload,
            previous,
        )
        self._events.append(
            GardenEvent(
                sequence=sequence,
                timestamp=timestamp,
                event_type=event_type_value,
                idea_id=identifier,
                payload=MappingProxyType(canonical_payload),
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
            "payload": dict(payload),
            "previous_hash": previous_hash,
        }
        return _canonical_json(body).encode("utf-8")

    def _require(self, idea_id: str) -> GardenIdea:
        identifier = _identifier(idea_id, "idea_id")
        try:
            return self._ideas[identifier]
        except KeyError as exc:
            raise KeyError(f"unknown garden idea: {identifier}") from exc

    @staticmethod
    def _logical_time(sequence: int) -> str:
        return f"logical:{sequence:012d}"
