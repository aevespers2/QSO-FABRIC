from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROLE_COLORS = {
    "atlas": "#7dd3fc",
    "nova": "#fda4af",
    "orion": "#c4b5fd",
    "lyra": "#fde68a",
    "fabric": "#94a3b8",
}

KIND_CONFIDENCE = {
    "experiment_started": 1.0,
    "observation": 0.82,
    "inference": 0.62,
    "message_sent": 0.70,
    "message_received": 0.68,
    "freeze": 0.95,
    "proposal": 0.76,
    "experiment_completed": 1.0,
    "runtime_limit": 0.35,
    "contradiction": 0.28,
}


@dataclass(frozen=True)
class ConstellationNode:
    id: str
    label: str
    actor: str
    kind: str
    confidence: float
    brightness: float
    radius: float
    x: float
    y: float
    color: str
    detail: str
    distorted: bool = False


@dataclass(frozen=True)
class ConstellationEdge:
    source: str
    target: str
    kind: str
    weight: float
    dashed: bool = False


def _stable_unit(value: str, salt: str) -> float:
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def _event_text(event: dict[str, Any]) -> str:
    payload = event.get("payload") or {}
    for key in ("text", "objective", "label", "state_hash"):
        value = payload.get(key)
        if value:
            return str(value)
    return event.get("kind", "event").replace("_", " ")


def _truncate(value: str, limit: int = 72) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def compile_constellation(report: dict[str, Any]) -> dict[str, Any]:
    """Compile a QSO experiment report into a deterministic constellation graph."""
    events = report.get("events")
    if not isinstance(events, list):
        raise ValueError("report must contain an events list")

    nodes: list[ConstellationNode] = []
    edges: list[ConstellationEdge] = []
    latest_by_actor: dict[str, str] = {}
    sent_by_signature: dict[tuple[str, str, str], str] = {}

    count = max(len(events), 1)
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        actor = str(event.get("actor", "fabric"))
        kind = str(event.get("kind", "event"))
        seq = int(event.get("seq", index))
        node_id = f"event-{seq}"
        text = _event_text(event)
        confidence = float(KIND_CONFIDENCE.get(kind, 0.55))
        distorted = kind == "contradiction" or bool((event.get("payload") or {}).get("contradiction"))
        if distorted:
            confidence = min(confidence, 0.32)

        angle = (2 * math.pi * index / count) + (_stable_unit(node_id, "angle") - 0.5) * 0.35
        orbit = 165 + 105 * _stable_unit(actor, "orbit")
        jitter = (_stable_unit(node_id, "radius") - 0.5) * 58
        x = 400 + (orbit + jitter) * math.cos(angle)
        y = 330 + (orbit + jitter) * math.sin(angle)
        brightness = round(0.35 + confidence * 0.65, 4)
        radius = round(4.5 + confidence * 7.5, 3)
        color = ROLE_COLORS.get(actor, "#e2e8f0")

        node = ConstellationNode(
            id=node_id,
            label=_truncate(text),
            actor=actor,
            kind=kind,
            confidence=round(confidence, 4),
            brightness=brightness,
            radius=radius,
            x=round(x, 3),
            y=round(y, 3),
            color=color,
            detail=text,
            distorted=distorted,
        )
        nodes.append(node)

        previous = latest_by_actor.get(actor)
        if previous:
            edges.append(ConstellationEdge(previous, node_id, "provenance", 0.46))
        latest_by_actor[actor] = node_id

        payload = event.get("payload") or {}
        if kind == "message_sent":
            signature = (actor, str(payload.get("to", "")), str(payload.get("text", "")))
            sent_by_signature[signature] = node_id
        elif kind == "message_received":
            signature = (str(payload.get("from", "")), actor, str(payload.get("text", "")))
            source = sent_by_signature.get(signature)
            if source:
                edges.append(ConstellationEdge(source, node_id, "message", 0.9))
        elif kind == "contradiction":
            prior = latest_by_actor.get(actor)
            if prior and prior != node_id:
                edges.append(ConstellationEdge(prior, node_id, "contradiction", 1.0, dashed=True))

    objective = str(report.get("objective", "QSO constellation"))
    return {
        "schema": "qso.constellation.v1",
        "title": objective,
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "distortion_count": sum(node.distorted for node in nodes),
            "ledger_valid": bool(report.get("ledger_valid", False)),
        },
        "nodes": [asdict(node) for node in nodes],
        "edges": [asdict(edge) for edge in edges],
    }


def render_constellation_html(constellation: dict[str, Any]) -> str:
    """Render an interactive, dependency-free HTML constellation."""
    payload = json.dumps(constellation, separators=(",", ":"), ensure_ascii=False)
    title = html.escape(str(constellation.get("title", "QSO Constellation")))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — QSO Constellation</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: radial-gradient(circle at 50% 42%, #101b35 0, #050914 48%, #02040a 100%); color: #e5eefc; overflow: hidden; }}
header {{ position: fixed; z-index: 4; left: 24px; top: 20px; max-width: 520px; }}
h1 {{ margin: 0 0 6px; font-size: clamp(21px, 3vw, 34px); letter-spacing: -.03em; }}
p {{ margin: 0; color: #a9b7cf; line-height: 1.45; }}
#sky {{ width: 100vw; height: 100vh; display: block; }}
.edge {{ stroke: #7183a8; stroke-opacity: .34; }}
.edge.message {{ stroke: #d9e7ff; stroke-opacity: .62; }}
.edge.contradiction {{ stroke: #fb7185; stroke-opacity: .78; stroke-dasharray: 8 7; }}
.star {{ cursor: pointer; transition: opacity .16s ease; }}
.star circle {{ filter: drop-shadow(0 0 7px currentColor); }}
.star.distorted circle {{ stroke: #fb7185; stroke-width: 2.4; stroke-dasharray: 3 3; }}
.star:hover circle {{ stroke: white; stroke-width: 2; }}
.label {{ fill: #cbd8ee; font-size: 10px; pointer-events: none; opacity: .72; }}
#panel {{ position: fixed; right: 18px; bottom: 18px; width: min(390px, calc(100vw - 36px)); min-height: 120px; padding: 16px; background: rgba(7, 13, 28, .86); border: 1px solid rgba(159, 180, 220, .22); border-radius: 16px; backdrop-filter: blur(12px); z-index: 5; }}
#panel strong {{ display: block; font-size: 16px; margin-bottom: 7px; }}
#panel small {{ display: block; color: #93a4c2; margin-bottom: 9px; text-transform: uppercase; letter-spacing: .08em; }}
#legend {{ position: fixed; left: 24px; bottom: 22px; display: flex; flex-wrap: wrap; gap: 10px 16px; z-index: 5; color: #a9b7cf; font-size: 12px; }}
.key::before {{ content: ""; display: inline-block; width: 8px; height: 8px; margin-right: 6px; border-radius: 50%; background: var(--c); box-shadow: 0 0 8px var(--c); }}
</style>
</head>
<body>
<header><h1>{title}</h1><p>Brightness represents confidence. Event trails preserve provenance. Dashed red geometry marks contradictions or distortions.</p></header>
<svg id="sky" viewBox="0 0 800 660" role="img" aria-label="Interactive QSO constellation"></svg>
<div id="legend"></div>
<aside id="panel"><small>QSO Constellations</small><strong>Select a star</strong><div>Inspect its actor, event type, confidence, and source text.</div></aside>
<script>
const data = {payload};
const svg = document.getElementById("sky");
const panel = document.getElementById("panel");
const ns = "http://www.w3.org/2000/svg";
const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]));
for (const edge of data.edges) {{
  const a = byId[edge.source], b = byId[edge.target];
  if (!a || !b) continue;
  const line = document.createElementNS(ns, "line");
  line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
  line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
  line.setAttribute("stroke-width", 0.6 + edge.weight * 1.8);
  line.setAttribute("class", "edge " + edge.kind);
  svg.appendChild(line);
}}
for (const node of data.nodes) {{
  const g = document.createElementNS(ns, "g");
  g.setAttribute("class", "star" + (node.distorted ? " distorted" : ""));
  g.style.color = node.color;
  const c = document.createElementNS(ns, "circle");
  c.setAttribute("cx", node.x); c.setAttribute("cy", node.y); c.setAttribute("r", node.radius);
  c.setAttribute("fill", node.color); c.setAttribute("fill-opacity", node.brightness);
  g.appendChild(c);
  if (node.confidence >= .75 || node.distorted) {{
    const t = document.createElementNS(ns, "text");
    t.setAttribute("x", node.x + node.radius + 5); t.setAttribute("y", node.y + 3);
    t.setAttribute("class", "label"); t.textContent = node.actor + " · " + node.kind.replaceAll("_", " ");
    g.appendChild(t);
  }}
  g.addEventListener("click", () => {{
    panel.innerHTML = `<small>${{node.actor}} · ${{node.kind.replaceAll("_"," ")}}</small><strong>${{node.label}}</strong><div>${{node.detail}}</div><p style="margin-top:10px">Confidence: ${{Math.round(node.confidence*100)}}%</p>`;
  }});
  svg.appendChild(g);
}}
const roles = [...new Set(data.nodes.map(n => n.actor))];
document.getElementById("legend").innerHTML = roles.map(role => {{
 const node = data.nodes.find(n => n.actor === role);
 return `<span class="key" style="--c:${{node.color}}">${{role}}</span>`;
}}).join("");
</script>
</body>
</html>"""


def write_constellation(report: dict[str, Any], output: Path) -> dict[str, Any]:
    constellation = compile_constellation(report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_constellation_html(constellation), encoding="utf-8")
    return constellation


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a QSO experiment report as an interactive constellation")
    parser.add_argument("report", type=Path, help="JSON report created by four_qso_experiment")
    parser.add_argument("--output", type=Path, default=Path("artifacts/qso_constellation.html"))
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    constellation = write_constellation(report, args.output)
    print(json.dumps({"output": str(args.output), **constellation["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
