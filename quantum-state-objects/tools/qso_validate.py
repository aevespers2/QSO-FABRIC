#!/usr/bin/env python3
"""Fail-closed dependency-free validator for QSO JSON authoring files."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

FORMAT = re.compile(r"^QSO-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
OBJECT_ID = re.compile(r"^qso:[a-z0-9-]+:.+$")
CONTENT_HASH = re.compile(r"^(sha256|blake3):([0-9a-f]{64})$")
MUTATION = {
    "immutable",
    "append-only",
    "externally-mutable",
    "self-proposable",
    "self-modifiable",
    "ephemeral",
    "derived",
    "constitutional",
    "mixed",
}
PAYLOAD_ENCODINGS = {"json", "cbor", "binary", "reference"}


def canonical_json_bytes(value: object) -> bytes:
    """Return the QSO JSON authoring-profile hash preimage.

    The top-level qso.content_hash field is omitted to avoid a circular digest.
    """
    candidate = copy.deepcopy(value)
    if isinstance(candidate, dict) and isinstance(candidate.get("qso"), dict):
        candidate["qso"].pop("content_hash", None)
    return json.dumps(
        candidate,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def compute_sha256_content_hash(value: object) -> str:
    return f"sha256:{hashlib.sha256(canonical_json_bytes(value)).hexdigest()}"


def _validate_timestamp(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"invalid {field}")
        return
    if parsed.tzinfo is None:
        errors.append(f"{field} must include a timezone")


def _validate_hash(
    value: object,
    field: str,
    errors: list[str],
    *,
    verify_root: object | None = None,
) -> None:
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return
    match = CONTENT_HASH.fullmatch(value)
    if not match:
        errors.append(f"invalid {field}")
        return
    algorithm, digest = match.groups()
    if digest == "0" * 64:
        errors.append(f"{field} must not be a placeholder digest")
        return
    if verify_root is not None:
        if algorithm != "sha256":
            errors.append(f"unsupported {field} algorithm: {algorithm}")
            return
        try:
            expected = compute_sha256_content_hash(verify_root)
        except (TypeError, ValueError):
            errors.append("QSO content is not canonical JSON")
            return
        if value != expected:
            errors.append(f"{field} does not match canonical content")


def _validate_reference(value: object, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return None
    allowed = {"object_id", "format", "content_hash", "required", "uri"}
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        errors.append(f"{field} contains unsupported fields: {', '.join(unsupported)}")

    required = ("object_id", "format", "content_hash", "required")
    for name in required:
        if name not in value:
            errors.append(f"missing {field}.{name}")

    object_id = value.get("object_id")
    if "object_id" in value:
        if not isinstance(object_id, str):
            errors.append(f"{field}.object_id must be a string")
        elif not OBJECT_ID.fullmatch(object_id):
            errors.append(f"invalid {field}.object_id")

    format_name = value.get("format")
    if "format" in value:
        if not isinstance(format_name, str):
            errors.append(f"{field}.format must be a string")
        elif not FORMAT.fullmatch(format_name):
            errors.append(f"invalid {field}.format")

    if "content_hash" in value:
        _validate_hash(value.get("content_hash"), f"{field}.content_hash", errors)

    if "required" in value and not isinstance(value.get("required"), bool):
        errors.append(f"{field}.required must be a boolean")

    if "uri" in value and not isinstance(value.get("uri"), str):
        errors.append(f"{field}.uri must be a string")

    return object_id if isinstance(object_id, str) else None


def _validate_core_payload(payload: object, errors: list[str]) -> None:
    if not isinstance(payload, dict):
        errors.append("QSO-CORE payload must be an object")
        return

    for field in ("manifest", "identity", "components"):
        if field not in payload:
            errors.append(f"missing payload.{field}")

    seen_ids: set[str] = set()
    for field in ("manifest", "identity"):
        if field in payload:
            object_id = _validate_reference(payload[field], f"payload.{field}", errors)
            if object_id:
                if object_id in seen_ids:
                    errors.append(f"duplicate QSO reference object_id: {object_id}")
                seen_ids.add(object_id)

    components = payload.get("components")
    if "components" in payload:
        if not isinstance(components, list):
            errors.append("payload.components must be an array")
        else:
            for index, component in enumerate(components):
                object_id = _validate_reference(
                    component, f"payload.components[{index}]", errors
                )
                if object_id:
                    if object_id in seen_ids:
                        errors.append(f"duplicate QSO reference object_id: {object_id}")
                    seen_ids.add(object_id)

    entrypoints = payload.get("entrypoints")
    if "entrypoints" in payload:
        if not isinstance(entrypoints, list) or not all(
            isinstance(item, str) for item in entrypoints
        ):
            errors.append("payload.entrypoints must be an array of strings")
        elif len(entrypoints) != len(set(entrypoints)):
            errors.append("payload.entrypoints must be unique")


def validate(value: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["root must be an object"]

    unsupported_root = sorted(set(value) - {"qso", "payload"})
    if unsupported_root:
        errors.append(f"root contains unsupported fields: {', '.join(unsupported_root)}")

    meta = value.get("qso")
    if not isinstance(meta, dict):
        return errors + ["qso metadata must be an object"]

    required = (
        "format",
        "format_version",
        "schema",
        "object_id",
        "created_at",
        "content_hash",
        "mutation_class",
        "payload_encoding",
    )
    for field in required:
        if field not in meta:
            errors.append(f"missing qso.{field}")

    format_name = meta.get("format")
    if "format" in meta:
        if not isinstance(format_name, str):
            errors.append("qso.format must be a string")
        elif not FORMAT.fullmatch(format_name):
            errors.append("invalid qso.format")

    version = meta.get("format_version")
    if "format_version" in meta:
        if not isinstance(version, str):
            errors.append("qso.format_version must be a string")
        elif not SEMVER.fullmatch(version):
            errors.append("invalid qso.format_version")

    schema = meta.get("schema")
    if "schema" in meta:
        if not isinstance(schema, str):
            errors.append("qso.schema must be a string")
        elif not schema or any(character.isspace() for character in schema):
            errors.append("invalid qso.schema")

    object_id = meta.get("object_id")
    if "object_id" in meta:
        if not isinstance(object_id, str):
            errors.append("qso.object_id must be a string")
        elif not OBJECT_ID.fullmatch(object_id):
            errors.append("invalid qso.object_id")

    if "created_at" in meta:
        _validate_timestamp(meta.get("created_at"), "qso.created_at", errors)
    if "modified_at" in meta:
        _validate_timestamp(meta.get("modified_at"), "qso.modified_at", errors)

    if "content_hash" in meta:
        _validate_hash(
            meta.get("content_hash"),
            "qso.content_hash",
            errors,
            verify_root=value,
        )

    if "mutation_class" in meta and meta.get("mutation_class") not in MUTATION:
        errors.append("invalid qso.mutation_class")

    if "payload_encoding" in meta and meta.get("payload_encoding") not in PAYLOAD_ENCODINGS:
        errors.append("invalid qso.payload_encoding")

    critical = meta.get("critical")
    if "critical" in meta:
        if not isinstance(critical, list) or not all(
            isinstance(item, str) for item in critical
        ):
            errors.append("qso.critical must be an array of strings")
        elif len(critical) != len(set(critical)):
            errors.append("qso.critical must be unique")

    if "payload" not in value:
        errors.append("missing payload")
    elif format_name == "QSO-CORE":
        _validate_core_payload(value["payload"], errors)

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: qso_validate.py FILE", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        value: Any = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value: {constant}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
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
