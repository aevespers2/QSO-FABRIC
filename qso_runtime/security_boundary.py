"""Fail-closed security controls for untrusted QSO inputs and artifacts.

The QSO runtime is deliberately non-operational: it may reason over text and
structured research artifacts, but it must not execute supplied code, install
packages, access credentials, spawn processes, or obtain unrestricted network
access.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any


class SecurityBoundaryError(ValueError):
    """Raised when untrusted input violates a QSO security invariant."""


EXECUTABLE_SUFFIXES = {
    ".apk", ".app", ".bat", ".bin", ".cmd", ".com", ".dll", ".dmg", ".exe",
    ".jar", ".js", ".msi", ".ps1", ".py", ".scr", ".sh", ".so", ".vbs",
}

ARCHIVE_SUFFIXES = {".7z", ".bz2", ".gz", ".rar", ".tar", ".tgz", ".xz", ".zip"}

DENIED_CAPABILITIES = frozenset({
    "credential_access",
    "dynamic_code_loading",
    "filesystem_write",
    "package_install",
    "process_spawn",
    "shell",
    "unrestricted_network",
    "wallet_access",
})

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_LOOKUP_PATTERNS = re.compile(r"\$\{\s*(?:jndi|env|sys|ctx|docker|k8s):", re.IGNORECASE)


@dataclass(frozen=True)
class SecurityLimits:
    max_text_chars: int = 16_384
    max_artifact_bytes: int = 2_000_000
    max_json_depth: int = 24
    max_json_nodes: int = 25_000


@dataclass(frozen=True)
class ArtifactVerdict:
    accepted: bool
    sha256: str
    media_type: str
    size_bytes: int
    reasons: tuple[str, ...]


def enforce_capability_boundary(requested: set[str] | frozenset[str]) -> None:
    """Reject any request for authority that a QSO must never possess."""
    denied = sorted(set(requested) & DENIED_CAPABILITIES)
    if denied:
        raise SecurityBoundaryError(f"denied QSO capabilities: {', '.join(denied)}")


def sanitize_external_text(text: str, limits: SecurityLimits | None = None) -> str:
    """Normalize bounded text and reject known lookup-style injection strings."""
    limits = limits or SecurityLimits()
    if not isinstance(text, str):
        raise SecurityBoundaryError("external text must be a string")
    if len(text) > limits.max_text_chars:
        raise SecurityBoundaryError("external text exceeds configured size limit")
    if "\x00" in text:
        raise SecurityBoundaryError("NUL bytes are forbidden")
    if _LOOKUP_PATTERNS.search(text):
        raise SecurityBoundaryError("lookup/interpolation injection pattern rejected")
    return _CONTROL_CHARS.sub("", text).replace("\r\n", "\n").replace("\r", "\n")


def _walk_json(value: Any, *, depth: int, counters: list[int], limits: SecurityLimits) -> None:
    if depth > limits.max_json_depth:
        raise SecurityBoundaryError("JSON nesting limit exceeded")
    counters[0] += 1
    if counters[0] > limits.max_json_nodes:
        raise SecurityBoundaryError("JSON node limit exceeded")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise SecurityBoundaryError("JSON object keys must be strings")
            sanitize_external_text(key, limits)
            _walk_json(item, depth=depth + 1, counters=counters, limits=limits)
    elif isinstance(value, list):
        for item in value:
            _walk_json(item, depth=depth + 1, counters=counters, limits=limits)
    elif isinstance(value, str):
        sanitize_external_text(value, limits)
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise SecurityBoundaryError("unsupported JSON value type")


def safe_json_loads(payload: str | bytes, limits: SecurityLimits | None = None) -> Any:
    """Parse JSON with byte, depth, node, and text-injection limits."""
    limits = limits or SecurityLimits()
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload
    if len(raw) > limits.max_artifact_bytes:
        raise SecurityBoundaryError("JSON artifact exceeds configured size limit")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SecurityBoundaryError("invalid UTF-8 JSON artifact") from exc
    _walk_json(value, depth=0, counters=[0], limits=limits)
    return value


def inspect_artifact(
    filename: str,
    content: bytes,
    *,
    media_type: str = "application/octet-stream",
    limits: SecurityLimits | None = None,
) -> ArtifactVerdict:
    """Return a deterministic, fail-closed verdict for an untrusted artifact.

    Executables, scripts, Java archives, and compressed containers are rejected.
    QSO may retain hashes and metadata for analysis, but it must not execute or
    unpack the supplied object.
    """
    limits = limits or SecurityLimits()
    digest = hashlib.sha256(content).hexdigest()
    suffixes = {suffix.lower() for suffix in PurePath(filename).suffixes}
    reasons: list[str] = []

    if len(content) > limits.max_artifact_bytes:
        reasons.append("artifact exceeds configured size limit")
    if suffixes & EXECUTABLE_SUFFIXES:
        reasons.append("executable or script artifact type denied")
    if suffixes & ARCHIVE_SUFFIXES:
        reasons.append("compressed or archive artifact requires external quarantine")
    if content.startswith((b"MZ", b"\x7fELF", b"PK\x03\x04", b"\xca\xfe\xba\xbe")):
        reasons.append("executable/archive magic bytes detected")
    if media_type in {
        "application/java-archive",
        "application/vnd.microsoft.portable-executable",
        "application/x-dosexec",
        "application/x-executable",
        "application/x-sh",
    }:
        reasons.append("executable media type denied")

    return ArtifactVerdict(
        accepted=not reasons,
        sha256=digest,
        media_type=media_type,
        size_bytes=len(content),
        reasons=tuple(reasons),
    )
