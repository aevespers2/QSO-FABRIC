import sys

import pytest

pytest.importorskip("mcp", reason="protocol tests require the optional MCP SDK")

import qso_mcp_server.server as server


@pytest.mark.parametrize("value", ["0", "1025", "-1", "1.0", "01", " 1", "true", ""])
def test_max_jobs_environment_is_canonical_and_bounded(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("QSO_MCP_MAX_JOBS", value)
    with pytest.raises(ValueError):
        server._max_jobs_from_env()


def test_max_jobs_environment_accepts_bounded_decimal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QSO_MCP_MAX_JOBS", "64")
    assert server._max_jobs_from_env() == 64


@pytest.mark.parametrize("value", ["http", "STREAMABLE-HTTP", "", " streamable-http"])
def test_transport_environment_is_closed(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("QSO_MCP_TRANSPORT", value)
    with pytest.raises(ValueError):
        server._transport_from_env()


def test_http_environment_requires_exact_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(server._HTTP_OPT_IN_ENV, raising=False)
    assert server._local_http_env_opt_in() is False
    monkeypatch.setenv(server._HTTP_OPT_IN_ENV, "1")
    assert server._local_http_env_opt_in() is True
    monkeypatch.setenv(server._HTTP_OPT_IN_ENV, "true")
    with pytest.raises(ValueError):
        server._local_http_env_opt_in()


def test_streamable_http_is_blocked_without_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(server._HTTP_OPT_IN_ENV, raising=False)
    monkeypatch.setattr(sys, "argv", ["qso-mcp", "--transport", "streamable-http"])
    with pytest.raises(SystemExit) as exc:
        server.main()
    assert exc.value.code == 2


def test_streamable_http_flag_allows_only_the_requested_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[str] = []
    monkeypatch.delenv(server._HTTP_OPT_IN_ENV, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qso-mcp",
            "--transport",
            "streamable-http",
            "--allow-unauthenticated-local-http",
        ],
    )
    monkeypatch.setattr(server.mcp, "run", lambda *, transport: called.append(transport))
    server.main()
    assert called == ["streamable-http"]


def test_capabilities_disclose_http_authentication_boundary() -> None:
    capabilities = server.qso_capabilities()
    assert capabilities["transport_security"] == {
        "stdio_default": True,
        "streamable_http_authenticated": False,
        "streamable_http_local_opt_in_required": True,
    }
