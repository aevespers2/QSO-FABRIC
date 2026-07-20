from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    edge_type: str
    source: str
    target: str
    payload: dict[str, Any]


class GraphInvariantError(ValueError):
    pass


class VersionedGraphStore:
    def __init__(self, root: Path, name: str, schema_version: int = 1) -> None:
        self.root = root / name
        self.root.mkdir(parents=True, exist_ok=True)
        self.name = name
        self.schema_version = schema_version
        self.pointer = self.root / "CURRENT"

    def empty_state(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "nodes": [], "edges": []}

    def validate(self, state: dict[str, Any]) -> None:
        node_ids = [node["node_id"] for node in state.get("nodes", [])]
        if len(node_ids) != len(set(node_ids)):
            raise GraphInvariantError(f"duplicate nodes in {self.name}")
        edge_ids = [edge["edge_id"] for edge in state.get("edges", [])]
        if len(edge_ids) != len(set(edge_ids)):
            raise GraphInvariantError(f"duplicate edges in {self.name}")
        nodes = set(node_ids)
        for edge in state.get("edges", []):
            if edge["source"] not in nodes or edge["target"] not in nodes:
                raise GraphInvariantError(f"orphaned edge {edge['edge_id']} in {self.name}")

    def write_snapshot(self, state: dict[str, Any]) -> str:
        self.validate(state)
        snapshot_id = sha256_json({"name": self.name, "state": state})
        path = self.root / f"{snapshot_id}.json"
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return snapshot_id

    def activate(self, snapshot_id: str) -> None:
        path = self.root / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(snapshot_id)
        self.pointer.write_text(snapshot_id + "\n", encoding="utf-8")

    def read(self, snapshot_id: str | None = None) -> dict[str, Any]:
        selected = snapshot_id
        if selected is None:
            if not self.pointer.exists():
                return self.empty_state()
            selected = self.pointer.read_text(encoding="utf-8").strip()
        state = json.loads((self.root / f"{selected}.json").read_text(encoding="utf-8"))
        self.validate(state)
        return state


class GraphMigrationRegistry:
    def __init__(self) -> None:
        self._migrations: dict[tuple[int, int], Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register(self, source: int, target: int, migration: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        if target != source + 1:
            raise ValueError("migrations must advance exactly one schema version")
        self._migrations[(source, target)] = migration

    def migrate(self, state: dict[str, Any], target_version: int) -> dict[str, Any]:
        current = int(state.get("schema_version", 1))
        migrated = json.loads(json.dumps(state))
        while current < target_version:
            key = (current, current + 1)
            if key not in self._migrations:
                raise KeyError(f"missing migration {key}")
            migrated = self._migrations[key](migrated)
            current += 1
            migrated["schema_version"] = current
        if current != target_version:
            raise ValueError("downgrade migrations are forbidden")
        return migrated


class MultiGraphTransaction:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.pointer = self.root / "CURRENT_TRANSACTION"

    def commit(
        self,
        *,
        memory_state: dict[str, Any],
        belief_store: VersionedGraphStore,
        belief_state: dict[str, Any],
        knowledge_store: VersionedGraphStore,
        knowledge_state: dict[str, Any],
    ) -> dict[str, Any]:
        belief_store.validate(belief_state)
        knowledge_store.validate(knowledge_state)
        belief_snapshot = belief_store.write_snapshot(belief_state)
        knowledge_snapshot = knowledge_store.write_snapshot(knowledge_state)
        manifest = {
            "memory_state": memory_state,
            "memory_state_hash": sha256_json(memory_state),
            "belief_snapshot": belief_snapshot,
            "knowledge_snapshot": knowledge_snapshot,
        }
        transaction_id = sha256_json(manifest)
        manifest["transaction_id"] = transaction_id
        (self.root / f"{transaction_id}.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        belief_store.activate(belief_snapshot)
        knowledge_store.activate(knowledge_snapshot)
        self.pointer.write_text(transaction_id + "\n", encoding="utf-8")
        return manifest

    def restore(
        self,
        transaction_id: str,
        *,
        belief_store: VersionedGraphStore,
        knowledge_store: VersionedGraphStore,
    ) -> dict[str, Any]:
        manifest_path = self.root / f"{transaction_id}.json"
        if not manifest_path.exists():
            raise FileNotFoundError(transaction_id)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        belief_store.read(manifest["belief_snapshot"])
        knowledge_store.read(manifest["knowledge_snapshot"])
        belief_store.activate(manifest["belief_snapshot"])
        knowledge_store.activate(manifest["knowledge_snapshot"])
        self.pointer.write_text(transaction_id + "\n", encoding="utf-8")
        return manifest


def consolidate_graph_runs(states: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}
    source_hashes = []
    for state in states:
        source_hashes.append(sha256_json(state))
        for node in state.get("nodes", []):
            nodes.setdefault(node["node_id"], node)
        for edge in state.get("edges", []):
            edges.setdefault(edge["edge_id"], edge)
    consolidated = {
        "schema_version": max((int(s.get("schema_version", 1)) for s in states), default=1),
        "nodes": sorted(nodes.values(), key=lambda item: item["node_id"]),
        "edges": sorted(edges.values(), key=lambda item: item["edge_id"]),
        "source_state_hashes": sorted(source_hashes),
        "automatic_promotion": False,
        "human_review_required": True,
    }
    node_ids = {node["node_id"] for node in consolidated["nodes"]}
    consolidated["orphan_edge_ids"] = sorted(
        edge["edge_id"]
        for edge in consolidated["edges"]
        if edge["source"] not in node_ids or edge["target"] not in node_ids
    )
    consolidated["consolidation_hash"] = sha256_json(consolidated)
    return consolidated
