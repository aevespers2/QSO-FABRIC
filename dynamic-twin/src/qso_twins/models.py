"""Core immutable domain models for the QSO Dynamic Twin Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


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


def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class Subject:
    entity_type: str
    entity_id: str

    def __post_init__(self) -> None:
        if not self.entity_type or not self.entity_id:
            raise ValueError("subject entity_type and entity_id are required")


@dataclass(frozen=True, slots=True)
class QualityScore:
    completeness: float
    reliability: float
    clock_confidence: float

    def __post_init__(self) -> None:
        for name, value in (
            ("completeness", self.completeness),
            ("reliability", self.reliability),
            ("clock_confidence", self.clock_confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class IntegrityProof:
    content_hash: str
    signature: str
    nonce: str
    timestamp: datetime
    authorized_source: bool

    def __post_init__(self) -> None:
        if not self.content_hash.startswith("sha256:"):
            raise ValueError("content_hash must use the sha256: prefix")
        if not self.signature or not self.nonce:
            raise ValueError("signature and nonce are required")
        if self.timestamp.tzinfo is None:
            raise ValueError("integrity timestamp must be timezone-aware")
        if self.authorized_source is not True:
            raise ValueError("observations require an authorized source")


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
        if not self.observation_id:
            raise ValueError("observation_id is required")
        if not self.twin_id.startswith("twin:"):
            raise ValueError("twin_id must use the twin: prefix")
        if not self.source_id.startswith("source:"):
            raise ValueError("source_id must use the source: prefix")
        if self.event_time.tzinfo is None or self.ingestion_time.tzinfo is None:
            raise ValueError("event and ingestion times must be timezone-aware")
        if self.sequence is not None and self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))
        object.__setattr__(self, "provenance", _frozen_mapping(self.provenance))


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
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.valid_from.tzinfo is None or self.observed_at.tzinfo is None:
            raise ValueError("state timestamps must be timezone-aware")
        if self.valid_to is not None and self.valid_to.tzinfo is None:
            raise ValueError("valid_to must be timezone-aware")
        object.__setattr__(self, "source_ids", tuple(self.source_ids))


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for ingestion boundaries."""
    return datetime.now(timezone.utc)
