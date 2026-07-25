"""Core immutable domain models for the QSO Dynamic Twin Engine."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import math
import re
from types import MappingProxyType
from typing import Any

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class ObservationType(StrEnum):
    STATE = "state"
    STRUCTURE = "structure"
    BEHAVIOR = "behavior"
    PERFORMANCE = "performance"
    METRIC = "metric"
    EVENT = "event"
    METADATA = "metadata"


class StateStatus(StrEnum):
    OBSERVED = "observed"
    DERIVED = "derived"
    PREDICTED = "predicted"
    SIMULATED = "simulated"
    ASSUMED = "assumed"
    DISPUTED = "disputed"
    STALE = "stale"
    INVALIDATED = "invalidated"


def _require_nonempty_text(name: str, value: object) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _require_aware_datetime(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be a timezone-aware datetime")
    return value


def _require_probability(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite numeric value between 0 and 1")
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be a finite numeric value between 0 and 1")
    return numeric


def _deep_freeze(value: Any) -> Any:
    """Return an immutable JSON-like value without silently coercing unsupported types."""

    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("mapping keys must be strings")
            frozen[key] = _deep_freeze(item)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    if value is None or type(value) in (str, bool, int, float):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("non-finite numeric values are not allowed")
        return value
    raise ValueError(f"unsupported immutable payload type: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class Subject:
    entity_type: str
    entity_id: str

    def __post_init__(self) -> None:
        _require_nonempty_text("subject entity_type", self.entity_type)
        _require_nonempty_text("subject entity_id", self.entity_id)


@dataclass(frozen=True, slots=True)
class QualityScore:
    completeness: float
    reliability: float
    clock_confidence: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "completeness", _require_probability("completeness", self.completeness)
        )
        object.__setattr__(
            self, "reliability", _require_probability("reliability", self.reliability)
        )
        object.__setattr__(
            self,
            "clock_confidence",
            _require_probability("clock_confidence", self.clock_confidence),
        )


@dataclass(frozen=True, slots=True)
class IntegrityProof:
    content_hash: str
    signature: str
    nonce: str
    timestamp: datetime
    authorized_source: bool

    def __post_init__(self) -> None:
        if type(self.content_hash) is not str or not _SHA256_RE.fullmatch(self.content_hash):
            raise ValueError("content_hash must be sha256: followed by 64 lowercase hex digits")
        _require_nonempty_text("signature", self.signature)
        _require_nonempty_text("nonce", self.nonce)
        _require_aware_datetime("integrity timestamp", self.timestamp)
        if type(self.authorized_source) is not bool or self.authorized_source is not True:
            raise ValueError("observations require authorized_source to be exactly true")


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: str
    twin_id: str
    source_id: str
    source_type: str
    observation_type: ObservationType
    subject: Subject
    event_time: datetime
    ingestion_time: datetime
    payload: Mapping[str, Any]
    provenance: Mapping[str, Any]
    quality: QualityScore
    integrity: IntegrityProof
    sequence: int | None = None
    schema_ref: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty_text("observation_id", self.observation_id)
        _require_nonempty_text("source_type", self.source_type)
        if type(self.twin_id) is not str or not self.twin_id.startswith("twin:") or len(self.twin_id) <= 5:
            raise ValueError("twin_id must use the twin: prefix with a non-empty suffix")
        if type(self.source_id) is not str or not self.source_id.startswith("source:") or len(self.source_id) <= 7:
            raise ValueError("source_id must use the source: prefix with a non-empty suffix")
        if not isinstance(self.observation_type, ObservationType):
            raise ValueError("observation_type must be an ObservationType value")
        if not isinstance(self.subject, Subject):
            raise ValueError("subject must be a Subject")
        _require_aware_datetime("event_time", self.event_time)
        _require_aware_datetime("ingestion_time", self.ingestion_time)
        if not isinstance(self.quality, QualityScore):
            raise ValueError("quality must be a QualityScore")
        if not isinstance(self.integrity, IntegrityProof):
            raise ValueError("integrity must be an IntegrityProof")
        if self.sequence is not None:
            if type(self.sequence) is not int or self.sequence < 0:
                raise ValueError("sequence must be a non-negative integer or null")
        if self.schema_ref is not None:
            _require_nonempty_text("schema_ref", self.schema_ref)
        object.__setattr__(self, "payload", _deep_freeze(self.payload))
        object.__setattr__(self, "provenance", _deep_freeze(self.provenance))


@dataclass(frozen=True, slots=True)
class StateValue:
    value: Any
    status: StateStatus
    valid_from: datetime
    observed_at: datetime
    confidence: float
    source_ids: Sequence[str] = field(default_factory=tuple)
    unit: str | None = None
    valid_to: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, StateStatus):
            raise ValueError("status must be a StateStatus value")
        object.__setattr__(self, "confidence", _require_probability("confidence", self.confidence))
        _require_aware_datetime("valid_from", self.valid_from)
        _require_aware_datetime("observed_at", self.observed_at)
        if self.valid_to is not None:
            _require_aware_datetime("valid_to", self.valid_to)
            if self.valid_to < self.valid_from:
                raise ValueError("valid_to cannot precede valid_from")
        if isinstance(self.source_ids, (str, bytes)) or not isinstance(self.source_ids, Sequence):
            raise ValueError("source_ids must be a sequence of source identifiers")
        normalized_source_ids: list[str] = []
        for source_id in self.source_ids:
            if type(source_id) is not str or not source_id.startswith("source:") or len(source_id) <= 7:
                raise ValueError("every source_id must use the source: prefix with a non-empty suffix")
            normalized_source_ids.append(source_id)
        if self.unit is not None:
            _require_nonempty_text("unit", self.unit)
        object.__setattr__(self, "source_ids", tuple(normalized_source_ids))
        object.__setattr__(self, "value", _deep_freeze(self.value))


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for ingestion boundaries."""

    return datetime.now(timezone.utc)
