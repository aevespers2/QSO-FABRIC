#!/usr/bin/env python3
"""Dependency-free baseline validator for QSO ecosystem manifests."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
REQUIRED = {
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


def fail(message: str) -> None:
    raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate(data: dict[str, Any]) -> list[str]:
    checks: list[str] = []
    missing = REQUIRED - data.keys()
    require(not missing, f"missing required fields: {sorted(missing)}")
    checks.append("required-fields")

    require(data["schema_version"] == "1.0.0", "unsupported schema_version")
    require(isinstance(data["component"], str) and len(data["component"]) >= 2, "invalid component")
    require(isinstance(data["version"], str) and SEMVER.fullmatch(data["version"]) is not None, "version must be semantic")
    require(isinstance(data["purpose"], str) and len(data["purpose"]) >= 20, "purpose is too short")
    checks.append("identity")

    level = data["conformance"].get("claimed_level")
    require(isinstance(level, int) and 0 <= level <= 5, "claimed_level must be 0..5")
    checks.append("conformance-level")

    bounds = data["runtime_bounds"]
    for key in ("max_seconds", "max_rounds", "max_messages"):
        require(isinstance(bounds.get(key), int) and bounds[key] > 0, f"{key} must be positive")
    require(bounds.get("network_default") in {"deny", "allow-declared"}, "invalid network_default")
    checks.append("runtime-bounds")

    capabilities = data["capabilities"]
    require(isinstance(capabilities, list) and capabilities, "at least one capability is required")
    for capability in capabilities:
        require(capability.get("authority") in {"observe", "propose", "execute"}, "invalid capability authority")
        require(capability.get("default") in {"deny", "allow"}, "invalid capability default")
    checks.append("capability-declarations")

    governance = data["governance"]
    require(governance.get("review_component") == "Jacob Redmond", "canonical review component required")
    require(governance.get("human_override") is True, "human override must be enabled")
    require(governance.get("audit_log") is True, "audit log must be enabled")
    checks.append("governance")

    if level >= 1:
        require(Path("README.md").exists(), "L1 requires README.md")
        checks.append("l1-reproducibility-artifact")
    if level >= 2:
        require(Path("tests").is_dir(), "L2 requires tests/")
        checks.append("l2-test-artifact")
    if level >= 4:
        require(Path("SECURITY.md").exists(), "L4 requires SECURITY.md")
        checks.append("l4-security-artifact")

    return checks


def main() -> int:
    manifest_path = Path(sys.argv[1] if len(sys.argv) > 1 else "qso.manifest.json")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        checks = validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 1

    result = {
        "valid": True,
        "component": data["component"],
        "claimed_level": data["conformance"]["claimed_level"],
        "checks": checks,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
