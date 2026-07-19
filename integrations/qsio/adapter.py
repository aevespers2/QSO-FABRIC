"""QSIO integration boundary for QSO-FABRIC.

The adapter is intentionally dependency-light: domain code emits QSI envelopes and
consumes immutable QSIO records without importing kernel internals.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import os
from typing import Any, Mapping, Protocol

SCHEMA_VERSION = "qsio.integration.v1"
FEATURE_FLAG = "QSIO_INTEGRATION_ENABLED"


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(value: Mapping[str, Any]) -> str:
    return "sha256:" + sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CompatibilityReport:
    compatible: bool
    schema_version: str = SCHEMA_VERSION
    unsupported_mappings: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class LocalApplicationResult:
    applied: bool
    canonical_id: str
    record_hash: str
    reason: str | None = None


class QSIOAdapter(Protocol):
    def describe_local_entity(self, local_id: str) -> Mapping[str, Any]: ...
    def to_qsi(self, local_event: object) -> Mapping[str, Any]: ...
    def apply_qsio(self, qsio: Mapping[str, Any]) -> LocalApplicationResult: ...
    def verify_compatibility(self) -> CompatibilityReport: ...


@dataclass
class FabricQSIOAdapter:
    """Maps fabric nodes, routes, and constellation changes to QSIO contracts."""

    repository: str = "qso-fabric"
    accepted_hashes: set[str] = field(default_factory=set)

    @staticmethod
    def enabled() -> bool:
        return os.getenv(FEATURE_FLAG, "false").lower() in {"1", "true", "yes", "on"}

    def describe_local_entity(self, local_id: str) -> Mapping[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "canonical_id": f"qso:fabric:{local_id}",
            "local_id": local_id,
            "repository": self.repository,
            "entity_type": "fabric_member",
        }

    def to_qsi(self, local_event: object) -> Mapping[str, Any]:
        payload = local_event if isinstance(local_event, Mapping) else vars(local_event)
        qsi = {
            "schema_version": SCHEMA_VERSION,
            "kind": "QSI",
            "source": self.repository,
            "action": payload.get("action", "fabric.interaction"),
            "subject": payload.get("canonical_id") or f"qso:fabric:{payload['local_id']}",
            "payload": dict(payload),
            "capabilities": tuple(payload.get("capabilities", ())),
        }
        return {**qsi, "content_hash": content_hash(qsi)}

    def apply_qsio(self, qsio: Mapping[str, Any]) -> LocalApplicationResult:
        if not self.enabled():
            return LocalApplicationResult(False, str(qsio.get("subject", "unknown")), "", "feature_disabled")
        if qsio.get("kind") != "QSIO" or qsio.get("schema_version") != SCHEMA_VERSION:
            return LocalApplicationResult(False, str(qsio.get("subject", "unknown")), "", "incompatible_record")
        supplied = str(qsio.get("content_hash", ""))
        body = {k: v for k, v in qsio.items() if k != "content_hash"}
        expected = content_hash(body)
        if supplied != expected:
            return LocalApplicationResult(False, str(qsio.get("subject", "unknown")), supplied, "hash_mismatch")
        self.accepted_hashes.add(supplied)
        return LocalApplicationResult(True, str(qsio["subject"]), supplied)

    def verify_compatibility(self) -> CompatibilityReport:
        return CompatibilityReport(True, notes=("Direct fabric mutation remains legacy-only until Phase 10.",))
