"""Fail-closed security controls for untrusted QSO inputs and artifacts.

The QSO runtime is deliberately non-operational: it may reason over text and
structured research artifacts, but it must not execute supplied code, install
packages, access credentials, spawn processes, or obtain unrestricted network
access.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any


class SecurityBoundaryError(ValueError):
    """Raised when untrusted input violates a QSO security invariant."""


EXECUTABLE_SUFFIXES = {
    ".apk",
    ".app",
    ".bat",
    ".bin",
    ".cmd",
    ".com",
    ".dll",
    ".dmg",
    ".exe",
    ".jar",
    ".js",
    ".msi",
    ".ps1",
    ".py",
    ".scr",
    ".sh",
    ".so",
    ".vbs",
}

ARCHIVE_SUFFIXES = {".7z", ".bz2", ".gz", ".rar", ".tar", ".tgz", ".xz", ".zip"}

ALLOWED_CAPABILITIES = frozenset(
    {
        "artifact_hashing",
        "bounded_json_parse",
        "metadata_read",
        "reasoning",
        "text_sanitization",
    }
)

DENIED_CAPABILITIES = frozenset(
    {
        "credential_access",
        "dynamic_code_loading",
        "filesystem_write",
        "package_install",
        "process_spawn",
        "shell",
        "unrestricted_network",
        "wallet_access",
    }
)

EXECUTABLE_MEDIA_TYPES = frozenset(
    {
        "application/java-archive",
        "application/vnd.microsoft.portable-executable",
        "application/wasm",
        "application/x-dosexec",
        "application/x-executable",
        "application/x-mach-binary",
        "application/x-sh",
    }
)

ARCHIVE_MEDIA_TYPES = frozenset(
    {
        "application/gzip",
        "application/vnd.rar",
        "application/x-7z-compressed",
        "application/x-bzip2",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-xz",
        "application/zip",
    }
)

_EXECUTABLE_MAGIC = (
    b"MZ",
    b"\x7fELF",
    b"\xca\xfe\xba\xbe",
    b"\x00asm",
    b"\xfe\xed\xfa\xce",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xcf\xfa\xed\xfe",
)
_ARCHIVE_MAGIC = (
    b"PK\x03\x04",
    b"\x1f\x8b",
    b"BZh",
    b"7z\xbc\xaf\x27\x1c",
    b"Rar!\x1a\x07",
    b"\xfd7zXZ\x00",
)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_LOOKUP_PATTERNS = re.compile(r"\$\{\s*(?:jndi|env|sys|ctx|docker|k8s):", re.IGNORECASE)
_CAPABILITY_NAME = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class SecurityLimits:
    max_text_chars: int = 16_384
    max_artifact_bytes: int = 2_000_000
    max_json_depth: int = 24
    max_json_nodes: int = 25_000

    def __post_init__(self) -> None:
        for field_name, value in (
            ("max_text_chars", self.max_text_chars),
            ("max_artifact_bytes", self.max_artifact_bytes),
            ("max_json_depth", self.max_json_depth),
            ("max_json_nodes", self.max_json_nodes),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise SecurityBoundaryError(f"{field_name} must be a positive integer")


@dataclass(frozen=True)
class ArtifactVerdict:
    accepted: bool
    sha256: str
    media_type: str
    size_bytes: int
    reasons: tuple[str, ...]


def enforce_capability_boundary(requested: set[str] | frozenset[str]) -> None:
    """Permit only the bounded analytical capabilities named by this module."""
    if not isinstance(requested, (set, frozenset)):
        raise SecurityBoundaryError("requested capabilities must be a set of strings")
    if any(not isinstance(capability, str) for capability in requested):
        raise SecurityBoundaryError("capability names must be strings")

    malformed = sorted(
        capability for capability in requested if not _CAPABILITY_NAME.fullmatch(capability)
    )
    if malformed:
        raise SecurityBoundaryError(f"malformed QSO capabilities: {', '.join(malformed)}")

    denied = sorted(requested & DENIED_CAPABILITIES)
    if denied:
        raise SecurityBoundaryError(f"denied QSO capabilities: {', '.join(denied)}")

    unsupported = sorted(requested - ALLOWED_CAPABILITIES)
    if unsupported:
        raise SecurityBoundaryError(f"unsupported QSO capabilities: {', '.join(unsupported)}")


def sanitize_external_text(text: str, limits: SecurityLimits | None = None) -> str:
    """Normalize line endings and reject unsafe control or lookup text."""
    limits = limits or SecurityLimits()
    if not isinstance(text, str):
        raise SecurityBoundaryError("external text must be a string")
    if len(text) > limits.max_text_chars:
        raise SecurityBoundaryError("external text exceeds configured size limit")
    if _CONTROL_CHARS.search(text):
        raise SecurityBoundaryError("unsafe control characters are forbidden")
    if _LOOKUP_PATTERNS.search(text):
        raise SecurityBoundaryError("lookup/interpolation injection pattern rejected")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SecurityBoundaryError(f"duplicate JSON object key rejected: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise SecurityBoundaryError(f"non-finite JSON number rejected: {value}")


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
    elif isinstance(value, float) and not math.isfinite(value):
        raise SecurityBoundaryError("non-finite JSON number rejected")
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise SecurityBoundaryError("unsupported JSON value type")


def safe_json_loads(payload: str | bytes, limits: SecurityLimits | None = None) -> Any:
    """Parse strict JSON with byte, depth, node, duplicate-key, and text limits."""
    limits = limits or SecurityLimits()
    if not isinstance(payload, (str, bytes)):
        raise SecurityBoundaryError("JSON artifact must be UTF-8 text or bytes")
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload
    if len(raw) > limits.max_artifact_bytes:
        raise SecurityBoundaryError("JSON artifact exceeds configured size limit")
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except SecurityBoundaryError:
        raise
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
    """Return a deterministic screening verdict for an untrusted artifact.

    Executables, scripts, Java archives, and compressed containers are rejected.
    An accepted verdict only means the bounded checks found no denied signal; it
    is not malware clearance and does not authorize opening or execution.
    """
    limits = limits or SecurityLimits()
    if not isinstance(filename, str):
        raise SecurityBoundaryError("artifact filename must be a string")
    if not isinstance(content, bytes):
        raise SecurityBoundaryError("artifact content must be bytes")
    if not isinstance(media_type, str):
        raise SecurityBoundaryError("artifact media type must be a string")

    normalized_filename = sanitize_external_text(filename, limits).strip()
    if not normalized_filename:
        raise SecurityBoundaryError("artifact filename must not be blank")
    normalized_media_type = media_type.split(";", 1)[0].strip().lower()
    if not normalized_media_type:
        raise SecurityBoundaryError("artifact media type must not be blank")

    digest = hashlib.sha256(content).hexdigest()
    suffixes = {suffix.lower() for suffix in PurePath(normalized_filename).suffixes}
    reasons: list[str] = []

    if len(content) > limits.max_artifact_bytes:
        reasons.append("artifact exceeds configured size limit")
    if suffixes & EXECUTABLE_SUFFIXES:
        reasons.append("executable or script artifact type denied")
    if suffixes & ARCHIVE_SUFFIXES:
        reasons.append("compressed or archive artifact requires external quarantine")
    if content.startswith(_EXECUTABLE_MAGIC) or content.startswith(b"#!"):
        reasons.append("executable or script magic bytes detected")
    if content.startswith(_ARCHIVE_MAGIC):
        reasons.append("archive magic bytes detected")
    if normalized_media_type in EXECUTABLE_MEDIA_TYPES:
        reasons.append("executable media type denied")
    if normalized_media_type in ARCHIVE_MEDIA_TYPES:
        reasons.append("archive media type requires external quarantine")

    return ArtifactVerdict(
        accepted=not reasons,
        sha256=digest,
        media_type=normalized_media_type,
        size_bytes=len(content),
        reasons=tuple(reasons),
    )
