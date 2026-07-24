"""Deterministic compositional glyph language for QSO Fabric.

Glyphs are semantic objects assembled from a small geometric vocabulary.  The
module intentionally stores geometry as data so renderers, agents, and ledgers
can share the same canonical representation without granting drawing or font
engine authority to a QSO.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Iterable, Mapping

GRID_SIZE = 7
PRIMITIVES = frozenset({"circle", "vertical", "horizontal", "curve", "triangle", "diamond", "dot", "arc"})
FAMILIES = frozenset({"organic", "mechanical", "mathematical", "emotional", "computational", "spiritual"})


@dataclass(frozen=True, slots=True)
class Stroke:
    primitive: str
    points: tuple[tuple[int, int], ...]
    weight: int = 1
    rotation: int = 0

    def __post_init__(self) -> None:
        if self.primitive not in PRIMITIVES:
            raise ValueError(f"unknown primitive: {self.primitive}")
        if not self.points:
            raise ValueError("a stroke requires at least one point")
        if self.weight not in range(1, 5):
            raise ValueError("weight must be between 1 and 4")
        if self.rotation % 45:
            raise ValueError("rotation must be a multiple of 45 degrees")
        for x, y in self.points:
            if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                raise ValueError(f"point {(x, y)} lies outside the {GRID_SIZE}x{GRID_SIZE} grid")


@dataclass(frozen=True, slots=True)
class Glyph:
    name: str
    meaning: str
    family: str
    strokes: tuple[Stroke, ...]
    phoneme: str | None = None
    certainty: float = 1.0
    abstraction: int = 0
    tags: tuple[str, ...] = field(default_factory=tuple)
    components: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.meaning.strip():
            raise ValueError("name and meaning are required")
        if self.family not in FAMILIES:
            raise ValueError(f"unknown family: {self.family}")
        if not self.strokes:
            raise ValueError("a glyph requires at least one stroke")
        if not 0.0 <= self.certainty <= 1.0:
            raise ValueError("certainty must be between 0 and 1")
        if self.abstraction not in range(0, 8):
            raise ValueError("abstraction must be between 0 and 7")

    def canonical_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["strokes"] = [asdict(stroke) for stroke in self.strokes]
        return value

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @property
    def glyph_id(self) -> str:
        return "qg:" + sha256(self.canonical_json().encode("utf-8")).hexdigest()[:24]


class GlyphRegistry:
    """Validated registry with deterministic composition and serialization."""

    def __init__(self, glyphs: Iterable[Glyph] = ()) -> None:
        self._glyphs: dict[str, Glyph] = {}
        for glyph in glyphs:
            self.register(glyph)

    def register(self, glyph: Glyph) -> Glyph:
        existing = self._glyphs.get(glyph.name)
        if existing is not None and existing != glyph:
            raise ValueError(f"glyph name already registered with different content: {glyph.name}")
        self._glyphs[glyph.name] = glyph
        return glyph

    def get(self, name: str) -> Glyph:
        try:
            return self._glyphs[name]
        except KeyError as exc:
            raise KeyError(f"unknown glyph: {name}") from exc

    def compose(self, name: str, meaning: str, components: Iterable[str], *, family: str = "computational") -> Glyph:
        names = tuple(components)
        if len(names) < 2:
            raise ValueError("composition requires at least two component glyphs")
        source = tuple(self.get(component) for component in names)
        seen: set[tuple[object, ...]] = set()
        strokes: list[Stroke] = []
        for glyph in source:
            for stroke in glyph.strokes:
                key = (stroke.primitive, stroke.points, stroke.weight, stroke.rotation)
                if key not in seen:
                    seen.add(key)
                    strokes.append(stroke)
        result = Glyph(
            name=name,
            meaning=meaning,
            family=family,
            strokes=tuple(strokes),
            certainty=min(g.certainty for g in source),
            abstraction=min(7, max(g.abstraction for g in source) + 1),
            tags=tuple(sorted({tag for glyph in source for tag in glyph.tags})),
            components=names,
        )
        return self.register(result)

    def manifest(self) -> dict[str, object]:
        ordered = [self._glyphs[name] for name in sorted(self._glyphs)]
        payload = {"format": "QSO-GLYPH-1", "grid_size": GRID_SIZE, "glyphs": [g.canonical_dict() | {"glyph_id": g.glyph_id} for g in ordered]}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return payload | {"manifest_sha256": sha256(encoded).hexdigest()}


def core_registry() -> GlyphRegistry:
    """Return the first canonical QSO semantic roots."""
    center = (3, 3)
    return GlyphRegistry(
        (
            Glyph("existence", "an object or bounded state", "mathematical", (Stroke("circle", (center,)),), tags=("entity",)),
            Glyph("time", "ordered change", "mathematical", (Stroke("vertical", ((3, 1), (3, 5))),), tags=("sequence",)),
            Glyph("state", "stability or persistence", "mechanical", (Stroke("horizontal", ((1, 3), (5, 3))),), tags=("persistence",)),
            Glyph("change", "continuous transformation", "organic", (Stroke("curve", ((1, 4), (3, 2), (5, 4))),), tags=("transition",)),
            Glyph("intent", "directed objective", "computational", (Stroke("triangle", ((3, 1), (1, 5), (5, 5))),), tags=("objective",)),
            Glyph("transform", "discrete transformation", "mechanical", (Stroke("diamond", ((3, 1), (5, 3), (3, 5), (1, 3))),), tags=("transition",)),
            Glyph("observer", "a situated point of observation", "computational", (Stroke("dot", (center,)), Stroke("circle", (center,), weight=2)), tags=("agent", "observation")),
            Glyph("memory", "retained state available for recall", "computational", (Stroke("arc", ((1, 3), (3, 1), (5, 3))), Stroke("dot", ((3, 4),))), tags=("recall", "state")),
        )
    )


def glyph_from_mapping(value: Mapping[str, object]) -> Glyph:
    """Decode an external mapping while preserving validation boundaries."""
    raw_strokes = value.get("strokes")
    if not isinstance(raw_strokes, list):
        raise ValueError("strokes must be a list")
    strokes = tuple(
        Stroke(
            primitive=str(item["primitive"]),
            points=tuple((int(point[0]), int(point[1])) for point in item["points"]),
            weight=int(item.get("weight", 1)),
            rotation=int(item.get("rotation", 0)),
        )
        for item in raw_strokes
        if isinstance(item, Mapping)
    )
    return Glyph(
        name=str(value["name"]),
        meaning=str(value["meaning"]),
        family=str(value["family"]),
        strokes=strokes,
        phoneme=None if value.get("phoneme") is None else str(value["phoneme"]),
        certainty=float(value.get("certainty", 1.0)),
        abstraction=int(value.get("abstraction", 0)),
        tags=tuple(str(tag) for tag in value.get("tags", ())),
        components=tuple(str(component) for component in value.get("components", ())),
    )
