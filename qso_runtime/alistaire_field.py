from __future__ import annotations

import hashlib
import json
import math
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

ADAPTIVE_LAWS = frozenset(
    {
        "evidence_weight",
        "memory_weight",
        "contradiction_sensitivity",
        "repair_preference",
    }
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


DEFAULT_CONSTITUTIONAL_WEIGHTS = ConstitutionalWeights()
DEFAULT_LIMITS = AlistaireLimits()


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
    laws: dict[str, float] = field(
        default_factory=lambda: {
            "evidence_weight": 1.0,
            "memory_weight": 0.7,
            "contradiction_sensitivity": 0.9,
            "repair_preference": 0.8,
        }
    )
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


def _finite(value: float, name: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    return numeric


def _unit(value: float, name: str, *, low: float = 0.0, high: float = 1.0) -> float:
    numeric = _finite(value, name)
    if not low <= numeric <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return numeric


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = _canonical_json(payload).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


def _bounded_text(value: str, name: str, max_chars: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    clean = value.strip()
    if not clean:
        raise ValueError(f"{name} must not be empty")
    if len(clean) > max_chars:
        raise ValueError(f"{name} exceeds the {max_chars}-character limit")
    return clean


def _bounded_string_tuple(values: Iterable[str], name: str, *, max_items: int = 64) -> tuple[str, ...]:
    materialized = tuple(values)
    if len(materialized) > max_items:
        raise ValueError(f"{name} exceeds the {max_items}-item limit")
    if any(not isinstance(value, str) or not value.strip() for value in materialized):
        raise ValueError(f"{name} must contain non-empty strings")
    return tuple(sorted(set(value.strip() for value in materialized)))


class AlistaireField:
    """Bounded constitutional field for relational QSO cognition.

    The field is deterministic, has no external authority, and emits proposals only.
    It keeps adaptive laws separate from hard constitutional constraints and rejects
    malformed or non-finite scoring input rather than silently normalizing it.
    """

    def __init__(
        self,
        *,
        weights: ConstitutionalWeights | None = None,
        limits: AlistaireLimits | None = None,
        state: AlistaireState | None = None,
    ) -> None:
        selected_weights = weights or DEFAULT_CONSTITUTIONAL_WEIGHTS
        if selected_weights != DEFAULT_CONSTITUTIONAL_WEIGHTS:
            raise ConstitutionalViolation("constitutional weights are immutable")

        selected_limits = limits or DEFAULT_LIMITS
        self._validate_limits(selected_limits)

        self.weights = selected_weights
        self.limits = selected_limits
        self.state = state or AlistaireState()
        self._validate_state()
        self._seal_state()

    @staticmethod
    def _validate_limits(limits: AlistaireLimits) -> None:
        for name in ("max_memories", "max_possibilities", "max_contradictions", "max_text_chars"):
            value = getattr(limits, name)
            maximum = getattr(DEFAULT_LIMITS, name)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                raise ValueError(f"{name} must be an integer between 1 and {maximum}")
        ceiling = _unit(limits.coercion_ceiling, "coercion_ceiling")
        if ceiling > DEFAULT_LIMITS.coercion_ceiling:
            raise ConstitutionalViolation("coercion_ceiling may be tightened but not relaxed")

    def _validate_state(self) -> None:
        if isinstance(self.state.step, bool) or not isinstance(self.state.step, int) or self.state.step < 0:
            raise ValueError("state.step must be a non-negative integer")
        if len(self.state.memories) > self.limits.max_memories:
            raise ValueError("state contains too many memories")
        if len(self.state.contradictions) > self.limits.max_contradictions:
            raise ValueError("state contains too many contradictions")
        if len(self.state.possibilities) > self.limits.max_possibilities:
            raise ValueError("state contains too many possibilities")
        if set(self.state.laws) != ADAPTIVE_LAWS:
            raise ConstitutionalViolation("state must contain exactly the approved adaptive laws")
        for name, value in self.state.laws.items():
            numeric = _finite(value, f"law {name}")
            if not 0.0 <= numeric <= 2.0:
                raise ValueError(f"law {name} must be between 0 and 2")
        for name, value in self.state.intent.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("intent keys must be non-empty strings")
            _finite(value, f"intent {name}")
        for name, value in self.state.state_vector.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("state-vector keys must be non-empty strings")
            _finite(value, f"state-vector {name}")
        for possibility in self.state.possibilities:
            self._validate_possibility(possibility)

    def observe(
        self,
        text: str,
        *,
        semantic_tags: Iterable[str] = (),
        emotional_weight: float = 0.0,
        causal_parents: Iterable[str] = (),
        relational_relevance: float = 0.0,
    ) -> MemoryNode:
        clean = _bounded_text(text, "memory text", self.limits.max_text_chars)
        tags = _bounded_string_tuple(semantic_tags, "semantic_tags")
        parents = _bounded_string_tuple(causal_parents, "causal_parents")
        emotional = _unit(emotional_weight, "emotional_weight", low=-1.0, high=1.0)
        relational = _unit(relational_relevance, "relational_relevance")
        payload = {
            "text": clean,
            "semantic_tags": tags,
            "causal_parents": parents,
            "step": self.state.step,
        }
        node = MemoryNode(
            memory_id=_stable_id("mem", payload),
            text=clean,
            semantic_tags=tags,
            emotional_weight=emotional,
            causal_parents=parents,
            relational_relevance=relational,
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
        return max(0.0, min(1.0, 0.4 * semantic + 0.2 * emotional + 0.2 * causal + 0.2 * relational))

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
        left_clean = _bounded_text(left, "contradiction left", self.limits.max_text_chars)
        right_clean = _bounded_text(right, "contradiction right", self.limits.max_text_chars)
        payload = {"left": left_clean, "right": right_clean, "step": self.state.step}
        contradiction = Contradiction(
            contradiction_id=_stable_id("con", payload),
            left=left_clean,
            right=right_clean,
            degree=_unit(degree, "degree"),
            context_gap=_unit(context_gap, "context_gap"),
            distortion_risk=_unit(distortion_risk, "distortion_risk"),
            suppression_risk=_unit(suppression_risk, "suppression_risk"),
        )
        self.state.contradictions.append(contradiction)
        self.state.contradictions = self.state.contradictions[-self.limits.max_contradictions :]
        self.state.step += 1
        self._seal_state()
        return contradiction

    def contradiction_energy(self) -> float:
        sensitivity = self.state.laws["contradiction_sensitivity"]
        return sensitivity * sum(item.repair_cost for item in self.state.contradictions)

    def update_intent(self, evidence: Mapping[str, float], *, momentum: float = 0.7) -> dict[str, float]:
        bounded_momentum = _unit(momentum, "momentum")
        normalized_evidence: dict[str, float] = {}
        for key, value in evidence.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("evidence keys must be non-empty strings")
            normalized_evidence[key.strip()] = _finite(value, f"evidence {key}")
        keys = set(self.state.intent) | set(normalized_evidence)
        updated = {
            key: bounded_momentum * self.state.intent.get(key, 0.0)
            + (1.0 - bounded_momentum) * normalized_evidence.get(key, 0.0)
            for key in keys
        }
        norm = sum(abs(value) for value in updated.values()) or 1.0
        self.state.intent = {key: value / norm for key, value in sorted(updated.items())}
        self.state.step += 1
        self._seal_state()
        return dict(self.state.intent)

    def adapt_laws(self, deltas: Mapping[str, float], *, learning_rate: float = 0.1) -> dict[str, float]:
        rate = _unit(learning_rate, "learning_rate")
        for name, delta in deltas.items():
            if name.startswith("constitutional_"):
                raise ConstitutionalViolation("constitutional invariants are not adaptive laws")
            if name not in ADAPTIVE_LAWS:
                raise ConstitutionalViolation(f"unapproved adaptive law: {name}")
            current = self.state.laws[name]
            next_value = current + rate * _finite(delta, f"law delta {name}")
            self.state.laws[name] = max(0.0, min(2.0, next_value))
        self.state.step += 1
        self._seal_state()
        return dict(self.state.laws)

    def _validate_possibility(self, possibility: Possibility) -> None:
        _bounded_text(possibility.action_id, "possibility action_id", 128)
        _bounded_text(possibility.description, "possibility description", self.limits.max_text_chars)
        for name in (
            "truth",
            "loyalty",
            "clarity",
            "autonomy",
            "repair",
            "beauty",
            "harm",
            "coercion",
            "effort",
            "risk",
            "irreversibility",
        ):
            _unit(getattr(possibility, name), f"possibility {name}")
        if not isinstance(possibility.metadata, dict):
            raise ValueError("possibility metadata must be a JSON object")
        if any(not isinstance(key, str) for key in possibility.metadata):
            raise ValueError("possibility metadata keys must be strings")
        try:
            _canonical_json(possibility.metadata)
        except (TypeError, ValueError) as exc:
            raise ValueError("possibility metadata must be finite canonical JSON") from exc

    def set_possibilities(self, possibilities: Iterable[Possibility]) -> None:
        bounded = list(possibilities)
        if len(bounded) > self.limits.max_possibilities:
            raise ValueError("too many possibilities; silent truncation is not permitted")
        for possibility in bounded:
            self._validate_possibility(possibility)
        identifiers = [item.action_id.strip() for item in bounded]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("possibility action_id values must be unique")
        self.state.possibilities = bounded
        self.state.step += 1
        self._seal_state()

    def score(self, possibility: Possibility) -> float:
        self._validate_possibility(possibility)
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
            self._validate_possibility(possibility)
            if possibility.coercion > self.limits.coercion_ceiling:
                rejected[possibility.action_id] = "coercion ceiling exceeded"
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
        previous = self.state.state_hash or self.state.previous_hash
        payload = asdict(self.state)
        payload["previous_hash"] = previous
        payload["state_hash"] = ""
        canonical = _canonical_json(payload)
        self.state.previous_hash = previous
        self.state.state_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
