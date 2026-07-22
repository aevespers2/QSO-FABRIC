from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def seal(value: dict[str, Any]) -> dict[str, Any]:
    value["qso"].pop("content_hash", None)
    value["qso"]["content_hash"] = "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def source_digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def require_report_shape(report: dict[str, Any]) -> None:
    required = {"objective", "base_seed", "limits", "ledger_valid", "event_count", "final_event_hash", "qsos", "events"}
    missing = sorted(required - report.keys())
    if missing:
        raise ValueError(f"legacy report missing required fields: {', '.join(missing)}")
    if not isinstance(report["qsos"], dict) or not isinstance(report["events"], list):
        raise ValueError("legacy report qsos/events have invalid types")
    if report["event_count"] != len(report["events"]):
        raise ValueError("legacy report event_count does not match events")


def convert(report: dict[str, Any], *, source_path: str, source_hash: str, created_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    require_report_shape(report)
    suffix = source_hash.split(":", 1)[1][:16]
    report_id = f"qso:report:four-qso-{suffix}"
    provenance_id = f"qso:provenance:four-qso-{suffix}"

    findings = []
    for name in sorted(report["qsos"]):
        result = report["qsos"][name]
        findings.append(
            {
                "qso": name,
                "role": result.get("role"),
                "observations": result.get("observations", []),
                "inferences": result.get("inferences", []),
                "contradictions": result.get("contradictions", []),
                "final_proposal": result.get("final_proposal", ""),
                "freeze_points": result.get("freeze_points", []),
            }
        )

    qreport = seal(
        {
            "qso": {
                "format": "QSO-REPORT",
                "format_version": "0.1.0",
                "schema": "qso://schemas/report/0.1.0",
                "object_id": report_id,
                "created_at": created_at,
                "mutation_class": "derived",
                "payload_encoding": "json",
                "source": {"path": source_path, "content_hash": source_hash},
                "conversion": "four-qso-report-to-qso-report-v1",
            },
            "payload": {
                "title": "Bounded four-QSO experiment report",
                "summary": report["objective"],
                "findings": findings,
                "references": [
                    {"type": "source", "path": source_path, "content_hash": source_hash},
                    {"type": "provenance", "object_id": provenance_id},
                ],
            },
        }
    )

    qprovenance = seal(
        {
            "qso": {
                "format": "QSO-PROVENANCE",
                "format_version": "0.1.0",
                "schema": "qso://schemas/provenance/0.1.0",
                "object_id": provenance_id,
                "created_at": created_at,
                "mutation_class": "append-only",
                "payload_encoding": "json",
                "source": {"path": source_path, "content_hash": source_hash},
                "conversion": "four-qso-ledger-to-qso-provenance-v1",
            },
            "payload": {
                "events": report["events"],
                "ledger": {
                    "valid_at_source": report["ledger_valid"],
                    "event_count": report["event_count"],
                    "final_event_hash": report["final_event_hash"],
                    "hash_algorithm": "sha256",
                    "genesis_marker": "GENESIS",
                },
                "experiment": {
                    "objective": report["objective"],
                    "base_seed": report["base_seed"],
                    "limits": report["limits"],
                },
            },
        }
    )
    return qreport, qprovenance


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a legacy bounded four-QSO report")
    parser.add_argument("source", type=Path)
    parser.add_argument("--created-at", required=True, help="RFC 3339 conversion timestamp")
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--provenance-output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.source.read_bytes()
    report = json.loads(raw.decode("utf-8"))
    qreport, qprovenance = convert(
        report,
        source_path=str(args.source),
        source_hash=source_digest(raw),
        created_at=args.created_at,
    )
    for path, value in ((args.report_output, qreport), (args.provenance_output, qprovenance)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
