#!/usr/bin/env python3
"""Strict, dependency-free validator for QSO ecosystem manifests."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn

MAX_JSON_BYTES = 1_048_576
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,127}$")
RELATIVE_PATH = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9._/-]+$")

TOP_LEVEL_FIELDS = {
    "schema_version",
    "component",
    "version",
    "purpose",
    "conformance",
    "runtime_bounds",
    "capabilities",
    "interfaces",
    "governance",
}
CONFORMANCE_FIELDS = {"claimed_level", "evidence_path"}
RUNTIME_FIELDS = {
    "max_seconds",
    "max_rounds",
    "max_messages",
    "max_memory_mb",
    "network_default",
}
CAPABILITY_FIELDS = {"name", "authority", "default", "constraints"}
INTERFACE_FIELDS = {
    "name",
    "role",
    "protocol",
    "schema_version",
    "idempotent",
    "retry_limit",
}
GOVERNANCE_FIELDS = {
    "review_component",
    "deprecated_aliases",
    "human_override",
    "audit_log",
}


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def is_int(value: Any) -> bool:
    return type(value) is int


def reject_constant(value: str) -> NoReturn:
    fail(f"non-finite numeric constant is not permitted: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate object key: {key}")
        result[key] = value
    return result


def load_json_bytes(raw: bytes, source: str) -> Any:
    require(len(raw) <= MAX_JSON_BYTES, f"{source} exceeds {MAX_JSON_BYTES} bytes")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(f"{source} is not strict UTF-8: {exc}")
    return json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )


def load_json_file(path: Path) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        fail(f"unable to read {path}: {exc}")
    return load_json_bytes(raw, str(path))


def require_closed_object(
    value: Any,
    *,
    name: str,
    required: set[str],
    allowed: set[str],
) -> dict[str, Any]:
    require(isinstance(value, dict), f"{name} must be an object")
    missing = required - set(value)
    unknown = set(value) - allowed
    require(not missing, f"{name} missing required fields: {sorted(missing)}")
    require(not unknown, f"{name} has unknown fields: {sorted(unknown)}")
    return value


def require_nonempty_string(value: Any, message: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), message)
    return value


def validate_schema_contract(schema: Any) -> None:
    root = require_closed_object(
        schema,
        name="schema",
        required={
            "$schema",
            "$id",
            "title",
            "type",
            "additionalProperties",
            "required",
            "properties",
        },
        allowed={
            "$schema",
            "$id",
            "title",
            "type",
            "additionalProperties",
            "required",
            "properties",
        },
    )
    require(root["type"] == "object", "schema root type must be object")
    require(root["additionalProperties"] is False, "schema root must be closed")
    require(
        isinstance(root["required"], list)
        and set(root["required"]) == TOP_LEVEL_FIELDS,
        "schema required-field set differs from validator",
    )
    require(
        isinstance(root["properties"], dict)
        and set(root["properties"]) == TOP_LEVEL_FIELDS,
        "schema property set differs from validator",
    )


def validate(data: Any, *, repository_root: Path) -> list[str]:
    checks: list[str] = []
    root = require_closed_object(
        data,
        name="manifest",
        required=TOP_LEVEL_FIELDS,
        allowed=TOP_LEVEL_FIELDS,
    )
    checks.append("closed-required-fields")

    require(root["schema_version"] == "1.0.0", "unsupported schema_version")
    component = require_nonempty_string(root["component"], "invalid component")
    require(IDENTIFIER.fullmatch(component) is not None, "invalid component identifier")
    require(
        isinstance(root["version"], str)
        and SEMVER.fullmatch(root["version"]) is not None,
        "version must be semantic",
    )
    purpose = require_nonempty_string(root["purpose"], "purpose must be a string")
    require(len(purpose) >= 20, "purpose is too short")
    checks.append("identity")

    conformance = require_closed_object(
        root["conformance"],
        name="conformance",
        required=CONFORMANCE_FIELDS,
        allowed=CONFORMANCE_FIELDS,
    )
    level = conformance["claimed_level"]
    require(is_int(level) and 0 <= level <= 5, "claimed_level must be integer 0..5")
    evidence_path = require_nonempty_string(
        conformance["evidence_path"], "evidence_path must be a non-empty string"
    )
    require(
        RELATIVE_PATH.fullmatch(evidence_path) is not None,
        "evidence_path must be a safe repository-relative path",
    )
    checks.append("conformance-level")

    bounds = require_closed_object(
        root["runtime_bounds"],
        name="runtime_bounds",
        required=RUNTIME_FIELDS,
        allowed=RUNTIME_FIELDS,
    )
    for key in ("max_seconds", "max_rounds", "max_messages", "max_memory_mb"):
        require(is_int(bounds[key]) and bounds[key] > 0, f"{key} must be a positive integer")
    require(
        bounds["network_default"] in {"deny", "allow-declared"},
        "invalid network_default",
    )
    checks.append("runtime-bounds")

    capabilities = root["capabilities"]
    require(isinstance(capabilities, list) and capabilities, "capabilities must be a non-empty array")
    capability_names: set[str] = set()
    for index, raw_capability in enumerate(capabilities):
        capability = require_closed_object(
            raw_capability,
            name=f"capabilities[{index}]",
            required=CAPABILITY_FIELDS,
            allowed=CAPABILITY_FIELDS,
        )
        name = require_nonempty_string(capability["name"], f"capabilities[{index}].name is invalid")
        require(IDENTIFIER.fullmatch(name) is not None, f"invalid capability name: {name}")
        require(name not in capability_names, f"duplicate capability name: {name}")
        capability_names.add(name)
        require(
            capability["authority"] in {"observe", "propose", "execute"},
            f"invalid capability authority: {name}",
        )
        require(capability["default"] in {"deny", "allow"}, f"invalid capability default: {name}")
        constraints = capability["constraints"]
        require(
            isinstance(constraints, list)
            and constraints
            and all(isinstance(item, str) and item.strip() for item in constraints),
            f"capability constraints must be a non-empty string array: {name}",
        )
        require(len(set(constraints)) == len(constraints), f"duplicate capability constraint: {name}")
        if capability["authority"] == "execute" and capability["default"] == "allow":
            normalized = " ".join(constraints).lower()
            require(
                any(token in normalized for token in ("bound", "limit", "deterministic")),
                f"default-allow execution capability lacks a bounded constraint: {name}",
            )
    checks.append("capability-declarations")

    interfaces = root["interfaces"]
    require(isinstance(interfaces, list) and interfaces, "interfaces must be a non-empty array")
    interface_names: set[str] = set()
    for index, raw_interface in enumerate(interfaces):
        interface = require_closed_object(
            raw_interface,
            name=f"interfaces[{index}]",
            required=INTERFACE_FIELDS,
            allowed=INTERFACE_FIELDS,
        )
        name = require_nonempty_string(interface["name"], f"interfaces[{index}].name is invalid")
        require(IDENTIFIER.fullmatch(name) is not None, f"invalid interface name: {name}")
        require(name not in interface_names, f"duplicate interface name: {name}")
        interface_names.add(name)
        require(
            interface["role"] in {"producer", "consumer", "bidirectional"},
            f"invalid interface role: {name}",
        )
        require_nonempty_string(interface["protocol"], f"invalid interface protocol: {name}")
        require(
            isinstance(interface["schema_version"], str)
            and SEMVER.fullmatch(interface["schema_version"]) is not None,
            f"invalid interface schema_version: {name}",
        )
        require(type(interface["idempotent"]) is bool, f"idempotent must be boolean: {name}")
        require(
            is_int(interface["retry_limit"]) and interface["retry_limit"] >= 0,
            f"retry_limit must be a non-negative integer: {name}",
        )
    checks.append("interface-declarations")

    governance = require_closed_object(
        root["governance"],
        name="governance",
        required=GOVERNANCE_FIELDS,
        allowed=GOVERNANCE_FIELDS,
    )
    require(
        governance["review_component"] == "Jacob Redmond",
        "canonical review component required",
    )
    aliases = governance["deprecated_aliases"]
    require(
        isinstance(aliases, list)
        and all(isinstance(alias, str) and alias.strip() for alias in aliases),
        "deprecated_aliases must be a string array",
    )
    require(len(set(aliases)) == len(aliases), "deprecated_aliases must be unique")
    require("Jacob Redmond" not in aliases, "canonical review component cannot be deprecated")
    require(governance["human_override"] is True, "human override must be enabled")
    require(governance["audit_log"] is True, "audit log must be enabled")
    checks.append("governance")

    if level >= 1:
        readme = repository_root / "README.md"
        workflow = repository_root / ".github" / "workflows" / "ecosystem-conformance.yml"
        require(readme.is_file() and readme.stat().st_size > 0, "L1 requires a non-empty README.md")
        require(workflow.is_file(), "L1 requires ecosystem-conformance workflow")
        checks.append("l1-reproducibility-artifacts")
    if level >= 2:
        require((repository_root / "tests").is_dir(), "L2 requires tests/")
        require((repository_root / evidence_path).is_dir(), "L2 requires evidence_path directory")
        checks.append("l2-verification-artifacts")
    if level >= 4:
        security = repository_root / "SECURITY.md"
        require(security.is_file() and security.stat().st_size > 0, "L4 requires SECURITY.md")
        checks.append("l4-security-artifact")

    return checks


def main() -> int:
    manifest_path = Path(sys.argv[1] if len(sys.argv) > 1 else "qso.manifest.json")
    schema_path = Path(
        sys.argv[2] if len(sys.argv) > 2 else "schemas/qso-manifest.schema.json"
    )
    repository_root = manifest_path.resolve().parent
    try:
        data = load_json_file(manifest_path)
        schema = load_json_file(schema_path)
        validate_schema_contract(schema)
        checks = validate(data, repository_root=repository_root)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1

    result = {
        "valid": True,
        "component": data["component"],
        "claimed_level": data["conformance"]["claimed_level"],
        "checks": checks,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
