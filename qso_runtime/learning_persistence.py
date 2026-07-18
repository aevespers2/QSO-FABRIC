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
class SeekerEvidenceHandoff:
    query_id: str
    source_uri: str
    content: str
    content_sha256: str
    retrieved_by: str = "seeker-proxy"
    qso_network_authority: bool = False
    executable: bool = False

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "SeekerEvidenceHandoff":
        content = str(record["content"])
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        supplied = str(record.get("content_sha256", expected))
        if supplied != expected:
            raise ValueError("Seeker evidence content hash mismatch")
        if record.get("retrieved_by", "seeker-proxy") != "seeker-proxy":
            raise ValueError("network evidence must be retrieved by seeker-proxy")
        if bool(record.get("qso_network_authority", False)):
            raise ValueError("QSO network authority is forbidden")
        if bool(record.get("executable", False)):
            raise ValueError("retrieved evidence must remain non-executable")
        return cls(
            query_id=str(record["query_id"]),
            source_uri=str(record["source_uri"]),
            content=content,
            content_sha256=supplied,
        )

    def as_learning_evidence(self, *, held_out: bool) -> dict[str, Any]:
        return {
            "evidence_id": self.query_id,
            "source": self.source_uri,
            "content": self.content,
            "held_out": held_out,
            "content_sha256": self.content_sha256,
            "retrieved_by": self.retrieved_by,
            "qso_network_authority": self.qso_network_authority,
            "executable": self.executable,
        }


class ReviewedKnowledgeStore:
    """Filesystem-backed durable store with explicit review and rollback manifests."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.durable = root / "durable"
        self.archive = root / "archive"
        self.snapshots = root / "snapshots"
        for path in (self.durable, self.archive, self.snapshots):
            path.mkdir(parents=True, exist_ok=True)

    def _state(self) -> dict[str, Any]:
        records = []
        for path in sorted(self.durable.glob("*.json")):
            records.append(json.loads(path.read_text(encoding="utf-8")))
        return {"records": records, "state_hash": sha256_json(records)}

    def snapshot(self, label: str) -> dict[str, Any]:
        state = self._state()
        manifest = {"label": label, **state}
        snapshot_hash = sha256_json(manifest)
        manifest["snapshot_hash"] = snapshot_hash
        (self.snapshots / f"{snapshot_hash}.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return manifest

    def promote(self, episode: dict[str, Any], *, reviewer: str, approved: bool) -> dict[str, Any]:
        if not approved:
            raise PermissionError("durable promotion requires explicit human approval")
        if not reviewer.strip():
            raise ValueError("reviewer identity is required")
        if not episode.get("human_review_required", True):
            raise ValueError("episode must preserve the human-review boundary")
        if episode.get("promotion_status") != "review-ready":
            raise ValueError("episode is not review-ready")
        if not episode.get("memory_chain_valid"):
            raise ValueError("invalid memory chain cannot be promoted")
        before = self.snapshot("pre-promotion")
        promoted = []
        for memory in episode.get("memories", []):
            durable_record = {
                **memory,
                "layer": "durable",
                "reviewer": reviewer,
                "source_freeze_hash": episode["freeze_hash"],
                "promotion_hash": sha256_json({"memory": memory, "reviewer": reviewer, "freeze": episode["freeze_hash"]}),
            }
            path = self.durable / f"{durable_record['record_hash']}.json"
            path.write_text(json.dumps(durable_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            promoted.append(durable_record)
        after = self.snapshot("post-promotion")
        return {
            "approved": True,
            "reviewer": reviewer,
            "promoted_count": len(promoted),
            "before_snapshot": before["snapshot_hash"],
            "after_snapshot": after["snapshot_hash"],
            "records": promoted,
        }

    def rollback(self, snapshot_hash: str, *, reviewer: str) -> dict[str, Any]:
        if not reviewer.strip():
            raise ValueError("reviewer identity is required")
        path = self.snapshots / f"{snapshot_hash}.json"
        if not path.exists():
            raise FileNotFoundError(snapshot_hash)
        target = json.loads(path.read_text(encoding="utf-8"))
        current = self._state()
        archive_path = self.archive / f"rollback-from-{current['state_hash']}.json"
        archive_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for record_path in self.durable.glob("*.json"):
            record_path.unlink()
        for record in target["records"]:
            (self.durable / f"{record['record_hash']}.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        restored = self._state()
        return {
            "reviewer": reviewer,
            "restored_snapshot": snapshot_hash,
            "restored_state_hash": restored["state_hash"],
            "restored_count": len(restored["records"]),
        }


def consolidate_episodes(episodes: Iterable[dict[str, Any]], *, minimum_occurrences: int = 2) -> dict[str, Any]:
    if minimum_occurrences < 2:
        raise ValueError("minimum_occurrences must be at least 2")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    source_freezes: set[str] = set()
    for episode in episodes:
        source_freezes.add(str(episode["freeze_hash"]))
        for memory in episode.get("memories", []):
            key = (str(memory["qso_name"]), str(memory["record_type"]))
            groups.setdefault(key, []).append(memory)
    concepts = []
    for (qso_name, record_type), records in sorted(groups.items()):
        if len(records) < minimum_occurrences:
            continue
        evidence_ids = sorted({e for record in records for e in record.get("evidence_ids", [])})
        concept = {
            "qso_name": qso_name,
            "record_type": record_type,
            "occurrences": len(records),
            "mean_confidence": round(sum(float(r["confidence"]) for r in records) / len(records), 6),
            "source_record_hashes": sorted(str(r["record_hash"]) for r in records),
            "evidence_ids": evidence_ids,
            "layer": "candidate",
        }
        concept["concept_hash"] = sha256_json(concept)
        concepts.append(concept)
    return {
        "schema_version": "qso-learning-consolidation-v1",
        "source_freeze_hashes": sorted(source_freezes),
        "minimum_occurrences": minimum_occurrences,
        "concepts": concepts,
        "automatic_promotion": False,
        "human_review_required": True,
        "consolidation_hash": sha256_json(concepts),
    }
