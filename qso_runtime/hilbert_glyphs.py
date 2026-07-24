"""QSO-HILBERT-1: exact Hilbert-space objects with deterministic visual projections.

The mathematical layer is canonical. Visual nodes and edges are explicitly a
finite projection and never claim to exhaust an infinite-dimensional space.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Iterable

MAX_DIMENSION = 256
MAX_LABEL_LENGTH = 128
NORMALIZATION_TOLERANCE = 1e-9


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a non-empty trimmed string")
    if len(value) > MAX_LABEL_LENGTH:
        raise ValueError(f"{label} exceeds {MAX_LABEL_LENGTH} characters")
    return value


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class ComplexAmplitude:
    real: float
    imag: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "real", _finite(self.real, "real"))
        object.__setattr__(self, "imag", _finite(self.imag, "imag"))

    @property
    def magnitude_squared(self) -> float:
        return self.real * self.real + self.imag * self.imag

    @property
    def phase(self) -> float:
        return math.atan2(self.imag, self.real)


@dataclass(frozen=True, slots=True)
class HilbertSpace:
    name: str
    dimension: int | None
    basis: tuple[str, ...]
    field: str = "complex"

    def __post_init__(self) -> None:
        _text(self.name, "space name")
        if self.field != "complex":
            raise ValueError("QSO-HILBERT-1 currently supports complex Hilbert spaces only")
        if self.dimension is not None:
            if type(self.dimension) is not int or not 1 <= self.dimension <= MAX_DIMENSION:
                raise ValueError(f"dimension must be between 1 and {MAX_DIMENSION}, or None for infinite")
        if not isinstance(self.basis, tuple) or not self.basis:
            raise ValueError("basis must be a non-empty tuple")
        if len(self.basis) > MAX_DIMENSION:
            raise ValueError(f"basis exceeds {MAX_DIMENSION} displayed vectors")
        labels = tuple(_text(item, "basis label") for item in self.basis)
        if len(set(labels)) != len(labels):
            raise ValueError("basis labels must be unique")
        if self.dimension is not None and len(labels) != self.dimension:
            raise ValueError("finite spaces require one basis label per dimension")


@dataclass(frozen=True, slots=True)
class StateVector:
    name: str
    space: str
    coefficients: tuple[ComplexAmplitude, ...]
    normalized: bool = True

    def __post_init__(self) -> None:
        _text(self.name, "state name")
        _text(self.space, "space reference")
        if not isinstance(self.coefficients, tuple) or not self.coefficients:
            raise ValueError("coefficients must be a non-empty tuple")
        if len(self.coefficients) > MAX_DIMENSION:
            raise ValueError(f"coefficients exceed {MAX_DIMENSION} entries")
        if any(not isinstance(value, ComplexAmplitude) for value in self.coefficients):
            raise ValueError("coefficients must contain ComplexAmplitude values")
        norm = sum(value.magnitude_squared for value in self.coefficients)
        if self.normalized and not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=NORMALIZATION_TOLERANCE):
            raise ValueError(f"normalized state has squared norm {norm!r}, expected 1")


@dataclass(frozen=True, slots=True)
class LinearOperator:
    name: str
    space: str
    matrix: tuple[tuple[ComplexAmplitude, ...], ...]
    operator_type: str = "linear"

    def __post_init__(self) -> None:
        _text(self.name, "operator name")
        _text(self.space, "space reference")
        if self.operator_type not in {"linear", "unitary", "hermitian", "projector", "density"}:
            raise ValueError("unsupported operator type")
        if not isinstance(self.matrix, tuple) or not self.matrix:
            raise ValueError("matrix must be a non-empty tuple of rows")
        size = len(self.matrix)
        if size > MAX_DIMENSION:
            raise ValueError(f"matrix exceeds {MAX_DIMENSION}x{MAX_DIMENSION}")
        for row in self.matrix:
            if not isinstance(row, tuple) or len(row) != size:
                raise ValueError("operator matrix must be square")
            if any(not isinstance(value, ComplexAmplitude) for value in row):
                raise ValueError("matrix entries must be ComplexAmplitude values")


@dataclass(frozen=True, slots=True)
class VisualNode:
    node_id: str
    kind: str
    label: str
    glyph: str
    x: float
    y: float
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class VisualEdge:
    source: str
    target: str
    relation: str
    magnitude: float | None = None
    phase: float | None = None


class HilbertScene:
    """Canonical mathematical scene plus a deterministic 2D projection."""

    def __init__(self, space: HilbertSpace) -> None:
        self.space = space
        self._states: dict[str, StateVector] = {}
        self._operators: dict[str, LinearOperator] = {}

    def add_state(self, state: StateVector) -> StateVector:
        if state.space != self.space.name:
            raise ValueError("state references a different Hilbert space")
        if len(state.coefficients) != len(self.space.basis):
            raise ValueError("state coefficient count must match displayed basis")
        if state.name in self._states:
            raise ValueError(f"duplicate state: {state.name}")
        self._states[state.name] = state
        return state

    def add_operator(self, operator: LinearOperator) -> LinearOperator:
        if operator.space != self.space.name:
            raise ValueError("operator references a different Hilbert space")
        if len(operator.matrix) != len(self.space.basis):
            raise ValueError("operator matrix size must match displayed basis")
        if operator.name in self._operators:
            raise ValueError(f"duplicate operator: {operator.name}")
        self._operators[operator.name] = operator
        return operator

    def inner_product(self, left: str, right: str) -> ComplexAmplitude:
        a = self._states[left]
        b = self._states[right]
        real = 0.0
        imag = 0.0
        for x, y in zip(a.coefficients, b.coefficients, strict=True):
            real += x.real * y.real + x.imag * y.imag
            imag += x.real * y.imag - x.imag * y.real
        return ComplexAmplitude(real, imag)

    def projection(self) -> dict[str, object]:
        nodes: list[VisualNode] = [VisualNode("space", "space", self.space.name, "existence", 0.0, 0.0)]
        edges: list[VisualEdge] = []
        count = len(self.space.basis)
        for index, label in enumerate(self.space.basis):
            angle = (2.0 * math.pi * index / count) - math.pi / 2.0
            node_id = f"basis:{index}"
            nodes.append(VisualNode(node_id, "basis", label, "state", math.cos(angle), math.sin(angle)))
            edges.append(VisualEdge("space", node_id, "contains"))
        for state_index, state in enumerate(sorted(self._states.values(), key=lambda item: item.name)):
            state_id = f"state:{state.name}"
            radius = 0.35 + 0.08 * state_index
            nodes.append(VisualNode(state_id, "state", state.name, "observer", radius, 0.0))
            for index, amplitude in enumerate(state.coefficients):
                if amplitude.magnitude_squared > NORMALIZATION_TOLERANCE:
                    edges.append(VisualEdge(state_id, f"basis:{index}", "superposition", math.sqrt(amplitude.magnitude_squared), amplitude.phase))
        for operator_index, operator in enumerate(sorted(self._operators.values(), key=lambda item: item.name)):
            nodes.append(VisualNode(f"operator:{operator.name}", "operator", operator.name, "transform", -0.4, 0.15 * operator_index, (("operator_type", operator.operator_type),)))
            edges.append(VisualEdge("space", f"operator:{operator.name}", "acts_on"))
        payload = {
            "format": "QSO-HILBERT-1",
            "projection_notice": "finite 2D projection; not the Hilbert space itself",
            "space": asdict(self.space),
            "states": [asdict(self._states[name]) for name in sorted(self._states)],
            "operators": [asdict(self._operators[name]) for name in sorted(self._operators)],
            "nodes": [asdict(node) for node in nodes],
            "edges": [asdict(edge) for edge in edges],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        return payload | {"manifest_sha256": sha256(encoded).hexdigest()}


def qubit_scene(name: str = "H_qubit") -> HilbertScene:
    """Return a canonical two-dimensional complex Hilbert-space scene."""
    return HilbertScene(HilbertSpace(name=name, dimension=2, basis=("|0>", "|1>")))


def equal_superposition() -> StateVector:
    amplitude = 1.0 / math.sqrt(2.0)
    return StateVector("|+>", "H_qubit", (ComplexAmplitude(amplitude), ComplexAmplitude(amplitude)))
