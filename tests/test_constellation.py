from qso_runtime.constellation import compile_constellation, render_constellation_html


def sample_report() -> dict:
    return {
        "objective": "Map bounded QSO knowledge",
        "ledger_valid": True,
        "events": [
            {"seq": 0, "kind": "experiment_started", "actor": "fabric", "payload": {"objective": "Map bounded QSO knowledge"}},
            {"seq": 1, "kind": "observation", "actor": "atlas", "payload": {"text": "Graph received"}},
            {"seq": 2, "kind": "message_sent", "actor": "atlas", "payload": {"to": "nova", "text": "Verify graph"}},
            {"seq": 3, "kind": "message_received", "actor": "nova", "payload": {"from": "atlas", "text": "Verify graph"}},
            {"seq": 4, "kind": "contradiction", "actor": "nova", "payload": {"text": "Edge violates invariant"}},
        ],
    }


def test_constellation_is_deterministic() -> None:
    first = compile_constellation(sample_report())
    second = compile_constellation(sample_report())
    assert first == second
    assert first["schema"] == "qso.constellation.v1"


def test_constellation_preserves_message_and_distortion_edges() -> None:
    result = compile_constellation(sample_report())
    assert result["summary"]["distortion_count"] == 1
    assert any(edge["kind"] == "message" for edge in result["edges"])
    assert any(node["distorted"] for node in result["nodes"])


def test_html_is_self_contained() -> None:
    result = compile_constellation(sample_report())
    page = render_constellation_html(result)
    assert "<svg" in page
    assert "Map bounded QSO knowledge" in page
    assert "qso.constellation.v1" in page
    assert "https://" not in page
