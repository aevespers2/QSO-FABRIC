from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from qso_runtime.gromerical_orchestrator import crossref_url, propose_queries

MAX_BYTES = 400_000
TIMEOUT_SECONDS = 20
USER_AGENT = "QSO-FABRIC/1.0 (bounded research probe; mailto:example@example.invalid)"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise RuntimeError(f"unexpected HTTP status: {response.status}")
        content_type = response.headers.get_content_type().lower()
        if content_type not in {"application/json", "application/vnd.api+json"}:
            raise RuntimeError(f"unexpected content type: {content_type}")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise RuntimeError("response exceeded byte limit")
    payload = json.loads(body.decode("utf-8"))
    return {"payload": payload, "body_sha256": sha256_bytes(body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("objective")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("artifacts/gromerical-network-probe.json"))
    args = parser.parse_args()

    plan = propose_queries(args.objective, steps=args.steps)
    results: dict[str, list[dict[str, Any]]] = {}
    for qso_name, proposals in plan["proposals"].items():
        qso_results: list[dict[str, Any]] = []
        for proposal in proposals:
            url = crossref_url(proposal["query"], rows=3)
            fetched = fetch_json(url)
            items = fetched["payload"].get("message", {}).get("items", [])
            qso_results.append({
                "proposal": proposal,
                "request_url": url,
                "result_count": len(items),
                "items": items,
                "response_body_sha256": fetched["body_sha256"],
                "network_used": True,
                "network_actor": "seeker-proxy",
                "qso_network_authority": False,
                "automatic_release": False,
                "human_review_required": True,
            })
        results[qso_name] = qso_results

    report = {
        "schema_version": "qso-gromerical-network-probe-v1",
        "plan": plan,
        "results": results,
        "status": "checkpoint-ready",
        "network_used": True,
        "network_actor": "seeker-proxy",
        "qso_network_authority": False,
        "automatic_release": False,
        "human_review_required": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "queries": {name: [p["proposal"]["query"] for p in entries] for name, entries in results.items()},
        "status": report["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
