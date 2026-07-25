"""Deterministic state materialization from append-only twin observations."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .ledger import LedgerEntry
from .models import ObservationType, StateStatus, StateValue


@dataclass(frozen=True, slots=True)
class MaterializedEntityState:
    twin_id: str
    entity_type: str
    entity_id: str
    fields: Mapping[str, StateValue]
    last_ledger_index: int


class StateMaterializer:
    """Build current state deterministically from ledger entries.

    State observations must provide `field` and `value` payload keys. Optional
    keys are `unit`, `confidence`, and `status`. Non-state observations remain
    available in the ledger but do not mutate the current state projection.
    """

    def materialize(
        self,
        entries: Iterable[LedgerEntry],
    ) -> Mapping[tuple[str, str, str], MaterializedEntityState]:
        projections: dict[tuple[str, str, str], dict[str, Any]] = {}

        for entry in entries:
            observation = entry.observation
            if observation.observation_type is not ObservationType.STATE:
                continue

            field_name = observation.payload.get("field")
            if not isinstance(field_name, str) or not field_name:
                raise ValueError("state observation payload requires a non-empty field")

            key = (
                observation.twin_id,
                observation.subject.entity_type,
                observation.subject.entity_id,
            )
            projection = projections.setdefault(
                key,
                {"fields": {}, "last_ledger_index": -1},
            )

            raw_status = observation.payload.get("status", StateStatus.OBSERVED.value)
            status = raw_status if isinstance(raw_status, StateStatus) else StateStatus(raw_status)
            confidence = float(
                observation.payload.get("confidence", observation.quality.reliability)
            )

            projection["fields"][field_name] = StateValue(
                value=observation.payload.get("value"),
                unit=observation.payload.get("unit"),
                valid_from=observation.event_time,
                valid_to=None,
                observed_at=observation.ingestion_time,
                confidence=confidence,
                source_ids=(observation.source_id,),
                status=status,
            )
            projection["last_ledger_index"] = entry.index

        return MappingProxyType(
            {
                key: MaterializedEntityState(
                    twin_id=key[0],
                    entity_type=key[1],
                    entity_id=key[2],
                    fields=MappingProxyType(dict(value["fields"])),
                    last_ledger_index=value["last_ledger_index"],
                )
                for key, value in projections.items()
            }
        )
