"""Append-only hash-chained event ledger for accepted twin observations."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from threading import RLock
from typing import Iterable, Iterator

from .models import Observation


GENESIS_HASH = "sha256:" + ("0" * 64)


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    index: int
    observation: Observation
    previous_hash: str
    entry_hash: str


class DuplicateObservationError(ValueError):
    """Raised when an observation identifier already exists in the ledger."""


class AppendOnlyLedger:
    """Thread-safe in-memory ledger suitable for deterministic tests and replay.

    A durable adapter can implement the same append/iterate contract later. The
    ledger never exposes mutable storage and never supports update or deletion.
    """

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []
        self._observation_ids: set[str] = set()
        self._lock = RLock()

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def __iter__(self) -> Iterator[LedgerEntry]:
        with self._lock:
            return iter(tuple(self._entries))

    @property
    def head_hash(self) -> str:
        with self._lock:
            return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def append(self, observation: Observation) -> LedgerEntry:
        with self._lock:
            if observation.observation_id in self._observation_ids:
                raise DuplicateObservationError(observation.observation_id)

            index = len(self._entries)
            previous_hash = self.head_hash
            entry_hash = self._compute_hash(index, previous_hash, observation)
            entry = LedgerEntry(
                index=index,
                observation=observation,
                previous_hash=previous_hash,
                entry_hash=entry_hash,
            )
            self._entries.append(entry)
            self._observation_ids.add(observation.observation_id)
            return entry

    def extend(self, observations: Iterable[Observation]) -> tuple[LedgerEntry, ...]:
        return tuple(self.append(observation) for observation in observations)

    def verify(self) -> bool:
        with self._lock:
            previous_hash = GENESIS_HASH
            for index, entry in enumerate(self._entries):
                if entry.index != index or entry.previous_hash != previous_hash:
                    return False
                expected = self._compute_hash(index, previous_hash, entry.observation)
                if entry.entry_hash != expected:
                    return False
                previous_hash = entry.entry_hash
            return True

    @staticmethod
    def _compute_hash(index: int, previous_hash: str, observation: Observation) -> str:
        canonical = "|".join(
            (
                str(index),
                previous_hash,
                observation.observation_id,
                observation.twin_id,
                observation.source_id,
                observation.observation_type.value,
                observation.subject.entity_type,
                observation.subject.entity_id,
                observation.event_time.isoformat(),
                observation.ingestion_time.isoformat(),
                observation.integrity.content_hash,
                observation.integrity.signature,
                observation.integrity.nonce,
                observation.integrity.timestamp.isoformat(),
            )
        ).encode("utf-8")
        return "sha256:" + sha256(canonical).hexdigest()
