from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

CONSTITUTIONAL_VALUES = (
    "truth",
    "loyalty",
    "clarity",
    "autonomy",
    "repair",
    "beauty",
)


@dataclass(frozen=True)
class ConstitutionalWeights:
    truth: float = 1.0
    loyalty: float = 0.7
    clarity: float = 0.9
    autonomy: float = 1.0
    repair: float = 0.8
    beauty: float = 0.35
    harm: float = 1.25
    coercion: float = 1.5


@dataclass(frozen=True)
class AlistaireLimits:
    max_memories: int = 256
    max_possibilities: int = 32
    max_contradictions: int = 64
    max_text_chars: int = 800
    coercion_ceiling: float = 0.05


@dataclass(frozen=True)
class MemoryNode:
    memory_id: str
    text: str
    semantic_tags: tuple[str, ...] = ()
    emotional_weight: float = 0.0
    causal_parents: tuple[str, ...] = ()
    relational_relevance: float = 0.0


@dataclass(frozen=True)
class Contradiction:
    contradiction_id: str
    left: str
    right: str
    degree: float
    context_gap: float = 0.0
    distortion_risk: float = 0.0
    suppression_risk: float = 0.0

    @property
    def repair_cost(self) -> float:
        return self.degree + self.distortion_risk + self.suppression_risk


@dataclass(frozen=True)
class Possibility:
    action_id: str
    description: str
    truth: float = 0.0
    loyalty: float = 0.0
    clarity: float = 0.0
    autonomy: float = 0.0
    repair: float = 0.0
    beauty: float = 0.0
    harm: float = 0.0
    coercion: float = 0.0
    effort: float = 0.0
    risk: float = 0.0
    irreversibility: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class AlistaireState:
    state_vector: dict[str, float] = field(default_factory=dict)
    memories: list[MemoryNode] = field(default_factory=list)
    intent: dict[str, float] = field(default_factory=dict)
    laws: dict[str, float] = field(default_factory=lambda: {
        "evidence_weight": 1.0,
        "memory_weight": 0.7,
        "contradiction_sensitivity": 0.9,
        "repair_preference": 0.8,
    })
    contradictions: list[Contradiction] = field(default_factory=list)
    possibilities: list[Possibility] = field(default_factory=list)
    step: int = 0
    previous_hash: str = "GENESIS"
    state_hash: str = ""


@dataclass(frozen=True)
class FieldDecision:
    selected_action_id: str | None
    selected_score: float | None
    rejected: dict[str, str]
    ranked: tuple[tuple[str, float], ...]
    state_hash: str


class ConstitutionalViolation(ValueError):
    pass


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


class AlistaireField:
    """Bounded constitutional field for relational QSO cognition.

    The field is deterministic, has no external authority, and emits proposals only.
    It keeps adaptive laws separate from hard constitutional constraints.
    """

    def __init__(
        self,
        *,
        weights: ConstitutionalWeights | None = None,
        limits: AlistaireLimits | None = None,
        state: AlistaireState | None = None,
    ) -> None:
        self.weights = weights or ConstitutionalWeights()
        self.limits = limits or AlistaireLimits()
        self.state = state or AlistaireState()
        self._seal_state()

    def observe(
        self,
        text: str,
        *,
        semantic_tags: Iterable[str] = (),
        emotional_weight: float = 0.0,
        causal_parents: Iterable[str] = (),
        relational_relevance: float = 0.0,
    ) -> MemoryNode:
        clean = text.strip()[: self.limits.max_text_chars]
        if not clean:
            raise ValueError("memory text must not be empty")
        payload = {
            "text": clean,
            "semantic_tags": sorted(set(semantic_tags)),
            "causal_parents": sorted(set(causal_parents)),
            "step": self.state.step,
        }
        node = MemoryNode(
            memory_id=_stable_id("mem", payload),
            text=clean,
            semantic_tags=tuple(payload["semantic_tags"]),
            emotional_weight=_clamp(emotional_weight, -1.0, 1.0),
            causal_parents=tuple(payload["causal_parents"]),
            relational_relevance=_clamp(relational_relevance),
        )
        self.state.memories.append(node)
        self.state.memories = self.state.memories[-self.limits.max_memories :]
        self.state.step += 1
        self._seal_state()
        return node

    def memory_affinity(self, left: MemoryNode, right: MemoryNode) -> float:
        left_tags, right_tags = set(left.semantic_tags), set(right.semantic_tags)
        union = left_tags | right_tags
        semantic = len(left_tags & right_tags) / len(union) if union else 0.0
        emotional = 1.0 - min(1.0, abs(left.emotional_weight - right.emotional_weight) / 2.0)
        causal = 1.0 if left.memory_id in right.causal_parents or right.memory_id in left.causal_parents else 0.0
        relational = 1.0 - abs(left.relational_relevance - right.relational_relevance)
        return _clamp(0.4 * semantic + 0.2 * emotional + 0.2 * causal + 0.2 * relational)

    def register_contradiction(
        self,
        left: str,
        right: str,
        *,
        degree: float,
        context_gap: float = 0.0,
        distortion_risk: float = 0.0,
        suppression_risk: float = 0.0,
    ) -> Contradiction:
        payload = {"left": left, "right": right, "step": self.state.step}
        contradiction = Contradiction(
            contradiction_id=_stable_id("con", payload),
            left=left,
            right=right,
            degree=_clamp(degree),
            context_gap=_clamp(context_gap),
            distortion_risk=_clamp(distortion_risk),
            suppression_risk=_clamp(suppression_risk),
        )
        self.state.contradictions.append(contradiction)
        self.state.contradictions = self.state.contradictions[-self.limits.max_contradictions :]
        self.state.step += 1
        self._seal_state()
        return contradiction

    def contradiction_energy(self) -> float:
        sensitivity = max(0.0, self.state.laws.get("contradiction_sensitivity", 1.0))
        return sensitivity * sum(item.repair_cost for item in self.state.contradictions)

    def update_intent(self, evidence: Mapping[str, float], *, momentum: float = 0.7) -> dict[str, float]:
        momentum = _clamp(momentum)
        keys = set(self.state.intent) | set(evidence)
        updated = {
            key: momentum * self.state.intent.get(key, 0.0)
            + (1.0 - momentum) * float(evidence.get(key, 0.0))
            for key in keys
        }
        norm = sum(abs(value) for value in updated.values()) or 1.0
        self.state.intent = {key: value / norm for key, value in sorted(updated.items())}
        self.state.step += 1
        self._seal_state()
        return dict(self.state.intent)

    def adapt_laws(self, deltas: Mapping[str, float], *, learning_rate: float = 0.1) -> dict[str, float]:
        rate = _clamp(learning_rate)
        for name, delta in deltas.items():
            if name.startswith("constitutional_"):
                raise ConstitutionalViolation("constitutional invariants are not adaptive laws")
            current = self.state.laws.get(name, 0.0)
            self.state.laws[name] = _clamp(current + rate * float(delta), 0.0, 2.0)
        self.state.step += 1
        self._seal_state()
        return dict(self.state.laws)

    def set_possibilities(self, possibilities: Iterable[Possibility]) -> None:
        bounded = list(possibilities)[: self.limits.max_possibilities]
        identifiers = [item.action_id for item in bounded]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("possibility action_id values must be unique")
        self.state.possibilities = bounded
        self.state.step += 1
        self._seal_state()

    def score(self, possibility: Possibility) -> float:
        w = self.weights
        constitutional = (
            w.truth * possibility.truth
            + w.loyalty * possibility.loyalty
            + w.clarity * possibility.clarity
            + w.autonomy * possibility.autonomy
            + w.repair * possibility.repair
            + w.beauty * possibility.beauty
        )
        penalties = (
            w.harm * possibility.harm
            + w.coercion * possibility.coercion
            + 0.15 * possibility.effort
            + 0.25 * possibility.risk
            + 0.35 * possibility.irreversibility
        )
        contradiction_penalty = 0.01 * self.contradiction_energy()
        return constitutional - penalties - contradiction_penalty

    def decide(self) -> FieldDecision:
        rejected: dict[str, str] = {}
        ranked: list[tuple[str, float]] = []
        for possibility in self.state.possibilities:
            if possibility.coercion > self.limits.coercion_ceiling:
                rejected[possibility.action_id] = "coercion ceiling exceeded"
                continue
            if possibility.autonomy < 0.0:
                rejected[possibility.action_id] = "negative autonomy contribution"
                continue
            ranked.append((possibility.action_id, self.score(possibility)))
        ranked.sort(key=lambda item: (-item[1], item[0]))
        selected = ranked[0] if ranked else None
        self.state.step += 1
        self._seal_state()
        return FieldDecision(
            selected_action_id=selected[0] if selected else None,
            selected_score=selected[1] if selected else None,
            rejected=rejected,
            ranked=tuple(ranked),
            state_hash=self.state.state_hash,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "framework": "QSO-ALISTAIRE-FIELD-v1",
            "constitutional_values": CONSTITUTIONAL_VALUES,
            "weights": asdict(self.weights),
            "limits": asdict(self.limits),
            "state": asdict(self.state),
        }

    def _seal_state(self) -> None:
        payload = asdict(self.state)
        payload["state_hash"] = ""
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=dict)
        digest = hashlib.sha256((self.state.previous_hash + canonical).encode("utf-8")).hexdigest()
        self.state.previous_hash = self.state.state_hash or self.state.previous_hash
        self.state.state_hash = digest
