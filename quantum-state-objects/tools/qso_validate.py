#!/usr/bin/env python3
"""Minimal dependency-free structural validator for QSO JSON authoring files."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

FORMAT = re.compile(r"^QSO-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
MUTATION = {
    "immutable", "append-only", "externally-mutable", "self-proposable",
    "self-modifiable", "ephemeral", "derived", "constitutional", "mixed",
}


def validate(value: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["root must be an object"]
    if set(value) - {"qso", "payload"}:
        errors.append("root contains unsupported fields")
    meta = value.get("qso")
    if not isinstance(meta, dict):
        return errors + ["qso metadata must be an object"]
    required = ("format", "format_version", "schema", "object_id", "created_at", "content_hash", "mutation_class", "payload_encoding")
    for field in required:
        if field not in meta:
            errors.append(f"missing qso.{field}")
    if isinstance(meta.get("format"), str) and not FORMAT.fullmatch(meta["format"]):
        errors.append("invalid qso.format")
    if isinstance(meta.get("format_version"), str) and not SEMVER.fullmatch(meta["format_version"]):
        errors.append("invalid qso.format_version")
    if meta.get("mutation_class") not in MUTATION:
        errors.append("invalid qso.mutation_class")
    if "payload" not in value:
        errors.append("missing payload")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: qso_validate.py FILE", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}")
        return 1
    errors = validate(value)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
