"""Deterministic compositional glyph language for QSO Fabric.

Glyphs are semantic objects assembled from a small geometric vocabulary. The
module intentionally stores geometry as data so renderers, agents, and ledgers
can share the same canonical representation without granting drawing or font
engine authority to a QSO.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
import math
from typing import Iterable, Mapping, Sequence

GRID_SIZE = 7
PRIMITIVES = frozenset({"circle", "vertical", "horizontal", "curve", "triangle", "diamond", "dot", "arc"})
FAMILIES = frozenset({"organic", "mechanical", "mathematical", "emotional", "computational", "spiritual"})

MAX_STROKES = 64
MAX_POINTS_PER_STROKE = 64
MAX_TAGS = 32
MAX_COMPONENTS = 32
MAX_NAME_LENGTH = 128
MAX_MEANING_LENGTH = 1_024
MAX_PHONEME_LENGTH = 64
MAX_LABEL_LENGTH = 64

_GLYPH_FIELDS = frozenset(
    {"name", "meaning", "family", "strokes", "phoneme", "certainty", "abstraction", "tags", "components"}
)
_REQUIRED_GLYPH_FIELDS = frozenset({"name", "meaning", "family", "strokes"})
_STROKE_FIELDS = frozenset({"primitive", "points", "weight", "rotation"})
_REQUIRED_STROKE_FIELDS = frozenset({"primitive", "points"})


def _require_closed_fields(value: Mapping[str, object], *, allowed: frozenset[str], required: frozenset[str], label: str) -> None:
    keys = set(value)
    unknown = keys - allowed
    missing = required - keys
    if unknown:
        raise ValueError(f"{label} contains unknown fields: {sorted(unknown)}")
    if missing:
        raise ValueError(f"{label} is missing required fields: {sorted(missing)}")


def _require_text(value: object, *, label: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be non-empty and free of surrounding whitespace")
    if len(value) > max_length:
        raise ValueError(f"{label} exceeds {max_length} characters")
    return value


def _require_int(value: object, *, label: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    return value


def _require_finite_number(value: object, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _require_text_sequence(
    value: object,
    *,
    label: str,
    max_items: int,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise ValueError(f"{label} must be a list or tuple of strings")
    if len(value) > max_items:
        raise ValueError(f"{label} exceeds {max_items} items")
    result = tuple(_require_text(item, label=f"{label} item", max_length=MAX_LABEL_LENGTH) for item in value)
    if not allow_empty and not result:
        raise ValueError(f"{label} must not be empty")
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must not contain duplicates")
    return result


@dataclass(frozen=True, slots=True)
class Stroke:
    primitive: str
    points: tuple[tuple[int, int], ...]
    weight: int = 1
    rotation: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.primitive, str) or self.primitive not in PRIMITIVES:
            raise ValueError(f"unknown primitive: {self.primitive!r}")
        if not isinstance(self.points, tuple) or not self.points:
            raise ValueError("a stroke requires a tuple of points")
        if len(self.points) > MAX_POINTS_PER_STROKE:
            raise ValueError(f"a stroke may contain at most {MAX_POINTS_PER_STROKE} points")
        if type(self.weight) is not int or self.weight not in range(1, 5):
            raise ValueError("weight must be an integer between 1 and 4")
        if type(self.rotation) is not int or self.rotation % 45:
            raise ValueError("rotation must be an integer multiple of 45 degrees")
        for point in self.points:
            if not isinstance(point, tuple) or len(point) != 2:
                raise ValueError("each point must be a two-integer tuple")
            x, y = point
            if type(x) is not int or type(y) is not int:
                raise ValueError("point coordinates must be integers")
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
        _require_text(self.name, label="name", max_length=MAX_NAME_LENGTH)
        _require_text(self.meaning, label="meaning", max_length=MAX_MEANING_LENGTH)
        if not isinstance(self.family, str) or self.family not in FAMILIES:
            raise ValueError(f"unknown family: {self.family!r}")
        if not isinstance(self.strokes, tuple) or not self.strokes:
            raise ValueError("a glyph requires a tuple of strokes")
        if len(self.strokes) > MAX_STROKES:
            raise ValueError(f"a glyph may contain at most {MAX_STROKES} strokes")
        if any(not isinstance(stroke, Stroke) for stroke in self.strokes):
            raise ValueError("strokes must contain only Stroke values")
        if self.phoneme is not None:
            _require_text(self.phoneme, label="phoneme", max_length=MAX_PHONEME_LENGTH)
        certainty = _require_finite_number(self.certainty, label="certainty")
        if not 0.0 <= certainty <= 1.0:
            raise ValueError("certainty must be between 0 and 1")
        if type(self.abstraction) is not int or self.abstraction not in range(0, 8):
            raise ValueError("abstraction must be an integer between 0 and 7")
        _require_text_sequence(self.tags, label="tags", max_items=MAX_TAGS)
        _require_text_sequence(self.components, label="components", max_items=MAX_COMPONENTS)

    def canonical_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["strokes"] = [asdict(stroke) for stroke in self.strokes]
        return value

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

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
        if not isinstance(glyph, Glyph):
            raise ValueError("registry entries must be Glyph values")
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
        if isinstance(components, (str, bytes, bytearray)):
            raise ValueError("components must be an iterable of glyph names, not a string")
        names = tuple(components)
        if len(names) < 2:
            raise ValueError("composition requires at least two component glyphs")
        if len(names) > MAX_COMPONENTS:
            raise ValueError(f"composition may contain at most {MAX_COMPONENTS} components")
        if any(not isinstance(component, str) for component in names):
            raise ValueError("component names must be strings")
        if len(set(names)) != len(names):
            raise ValueError("composition component names must be unique")
        source = tuple(self.get(component) for component in names)
        seen: set[tuple[object, ...]] = set()
        strokes: list[Stroke] = []
        for glyph in source:
            for stroke in glyph.strokes:
                key = (stroke.primitive, stroke.points, stroke.weight, stroke.rotation)
                if key not in seen:
                    seen.add(key)
                    strokes.append(stroke)
        if len(strokes) > MAX_STROKES:
            raise ValueError(f"composed glyph exceeds the {MAX_STROKES}-stroke limit")
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
        payload = {
            "format": "QSO-GLYPH-1",
            "grid_size": GRID_SIZE,
            "glyphs": [g.canonical_dict() | {"glyph_id": g.glyph_id} for g in ordered],
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
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
    """Decode an external mapping without coercing malformed values."""
    if not isinstance(value, Mapping):
        raise ValueError("glyph input must be a mapping")
    _require_closed_fields(value, allowed=_GLYPH_FIELDS, required=_REQUIRED_GLYPH_FIELDS, label="glyph")

    raw_strokes = value["strokes"]
    if not isinstance(raw_strokes, list):
        raise ValueError("strokes must be a list")
    if not raw_strokes:
        raise ValueError("strokes must not be empty")
    if len(raw_strokes) > MAX_STROKES:
        raise ValueError(f"strokes exceeds {MAX_STROKES} items")

    strokes: list[Stroke] = []
    for index, item in enumerate(raw_strokes):
        if not isinstance(item, Mapping):
            raise ValueError(f"stroke {index} must be a mapping")
        _require_closed_fields(item, allowed=_STROKE_FIELDS, required=_REQUIRED_STROKE_FIELDS, label=f"stroke {index}")

        primitive = _require_text(item["primitive"], label=f"stroke {index} primitive", max_length=MAX_LABEL_LENGTH)
        raw_points = item["points"]
        if not isinstance(raw_points, list) or not raw_points:
            raise ValueError(f"stroke {index} points must be a non-empty list")
        if len(raw_points) > MAX_POINTS_PER_STROKE:
            raise ValueError(f"stroke {index} exceeds {MAX_POINTS_PER_STROKE} points")

        points: list[tuple[int, int]] = []
        for point_index, point in enumerate(raw_points):
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError(f"stroke {index} point {point_index} must contain exactly two integers")
            x = _require_int(point[0], label=f"stroke {index} point {point_index} x")
            y = _require_int(point[1], label=f"stroke {index} point {point_index} y")
            points.append((x, y))

        weight = _require_int(item.get("weight", 1), label=f"stroke {index} weight")
        rotation = _require_int(item.get("rotation", 0), label=f"stroke {index} rotation")
        strokes.append(Stroke(primitive=primitive, points=tuple(points), weight=weight, rotation=rotation))

    name = _require_text(value["name"], label="name", max_length=MAX_NAME_LENGTH)
    meaning = _require_text(value["meaning"], label="meaning", max_length=MAX_MEANING_LENGTH)
    family = _require_text(value["family"], label="family", max_length=MAX_LABEL_LENGTH)

    raw_phoneme = value.get("phoneme")
    phoneme = None if raw_phoneme is None else _require_text(raw_phoneme, label="phoneme", max_length=MAX_PHONEME_LENGTH)
    certainty = _require_finite_number(value.get("certainty", 1.0), label="certainty")
    abstraction = _require_int(value.get("abstraction", 0), label="abstraction")
    tags = _require_text_sequence(value.get("tags", ()), label="tags", max_items=MAX_TAGS)
    components = _require_text_sequence(value.get("components", ()), label="components", max_items=MAX_COMPONENTS)

    return Glyph(
        name=name,
        meaning=meaning,
        family=family,
        strokes=tuple(strokes),
        phoneme=phoneme,
        certainty=certainty,
        abstraction=abstraction,
        tags=tags,
        components=components,
    )
