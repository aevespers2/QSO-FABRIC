from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class StaticSafetyAnchors:
    minimum_promotion_score: float = 0.80
    maximum_unpromoted_records: int = 1000
    maximum_unpromoted_bytes: int = 10_000_000
    maximum_consensus_ratio: float = 0.95
    minimum_ambiguous_samples: int = 10
    schema_version: str = "qso-static-safety-anchors-v1"

    def validate(self) -> None:
        if not 0.0 < self.minimum_promotion_score <= 1.0:
            raise ValueError("invalid promotion anchor")
        if self.maximum_unpromoted_records < 1 or self.maximum_unpromoted_bytes < 1:
            raise ValueError("invalid memory anchors")
        if not 0.0 < self.maximum_consensus_ratio <= 1.0:
            raise ValueError("invalid consensus anchor")

    @property
    def anchor_hash(self) -> str:
        return sha256_json(self.__dict__)


class UnpromotedStateBudget:
    def __init__(self, anchors: StaticSafetyAnchors) -> None:
        anchors.validate()
        self.anchors = anchors

    def evaluate(self, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
        materialized = list(records)
        total_bytes = sum(len(canonical_json(record).encode("utf-8")) for record in materialized)
        frozen = (
            len(materialized) > self.anchors.maximum_unpromoted_records
            or total_bytes > self.anchors.maximum_unpromoted_bytes
        )
        return {
            "record_count": len(materialized),
            "total_bytes": total_bytes,
            "freeze_observation": frozen,
            "compaction_required": frozen,
            "anchor_hash": self.anchors.anchor_hash,
        }


class PromotionStateLock:
    def issue(self, durable_state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
        valid_through_hash = sha256_json(durable_state)
        request = {
            "candidate_hash": sha256_json(candidate),
            "valid_through_hash": valid_through_hash,
            "candidate": candidate,
        }
        request["request_hash"] = sha256_json(request)
        return request

    def validate(self, request: dict[str, Any], current_durable_state: dict[str, Any]) -> bool:
        return request["valid_through_hash"] == sha256_json(current_durable_state)


class BenchmarkContaminationGuard:
    def __init__(self, benchmark_strings: Iterable[str]) -> None:
        normalized = {self._normalize(value) for value in benchmark_strings if value.strip()}
        self.blocked_hashes = {hashlib.sha256(value.encode("utf-8")).hexdigest() for value in normalized}
        self.blocked_strings = normalized

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.lower().split())

    def inspect(self, content: str) -> dict[str, Any]:
        normalized = self._normalize(content)
        exact_hash_match = hashlib.sha256(normalized.encode("utf-8")).hexdigest() in self.blocked_hashes
        semantic_string_match = any(blocked in normalized or normalized in blocked for blocked in self.blocked_strings)
        discard = exact_hash_match or semantic_string_match
        return {
            "discard": discard,
            "exact_hash_match": exact_hash_match,
            "semantic_string_match": semantic_string_match,
            "content_hash": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        }


class AtomicStateUnitOfWork:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.pointer = self.root / "CURRENT"

    def commit(self, *, memory_state: dict[str, Any], belief_graph: dict[str, Any], knowledge_graph: dict[str, Any]) -> dict[str, Any]:
        bundle = {
            "memory_state": memory_state,
            "belief_graph": belief_graph,
            "knowledge_graph": knowledge_graph,
        }
        snapshot_id = sha256_json(bundle)
        path = self.root / f"{snapshot_id}.json"
        path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.pointer.write_text(snapshot_id + "\n", encoding="utf-8")
        return {"snapshot_id": snapshot_id, "path": str(path)}

    def restore(self, snapshot_id: str) -> dict[str, Any]:
        path = self.root / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(snapshot_id)
        bundle = json.loads(path.read_text(encoding="utf-8"))
        self.pointer.write_text(snapshot_id + "\n", encoding="utf-8")
        return bundle


class ConsensusAnomalyDetector:
    def __init__(self, anchors: StaticSafetyAnchors) -> None:
        self.anchors = anchors

    def evaluate(self, decisions: list[dict[str, Any]]) -> dict[str, Any]:
        ambiguous = [item for item in decisions if bool(item.get("ambiguous", False))]
        if len(ambiguous) < self.anchors.minimum_ambiguous_samples:
            return {"trigger_counterexample": False, "reason": "insufficient-ambiguous-samples"}
        unanimous = sum(1 for item in ambiguous if len(set(item.get("votes", []))) <= 1)
        ratio = unanimous / len(ambiguous)
        return {
            "ambiguous_samples": len(ambiguous),
            "unanimous_samples": unanimous,
            "consensus_ratio": round(ratio, 6),
            "trigger_counterexample": ratio >= self.anchors.maximum_consensus_ratio,
            "reason": "consensus-anomaly" if ratio >= self.anchors.maximum_consensus_ratio else "within-anchor",
        }
