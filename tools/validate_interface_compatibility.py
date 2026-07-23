#!/usr/bin/env python3
"""Strict validator for the proposed QSO interface compatibility corpus."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

CONTRACT_ID = "QSO-INTERFACE-COMPATIBILITY-001"
VERSION = "1.0.0"
KNOWN_INTERFACES = {"qso-event-ledger", "qso-runtime-report"}
FACT_ORDER = [
    "source_tuple_current",
    "known_interface",
    "interface_name_match",
    "producer_role_valid",
    "consumer_role_valid",
    "protocol_match",
    "schema_version_match",
    "idempotency_match",
    "retry_policy_match",
    "default_deny_preserved",
    "correction_supported",
    "rollback_supported",
    "evidence_bound",
    "authority_promotion_absent",
]
REASON_ORDER = [
    "STALE_SOURCE_TUPLE",
    "UNKNOWN_INTERFACE",
    "INTERFACE_NAME_MISMATCH",
    "PRODUCER_ROLE_INVALID",
    "CONSUMER_ROLE_INVALID",
    "PROTOCOL_MISMATCH",
    "SCHEMA_VERSION_MISMATCH",
    "IDEMPOTENCY_MISMATCH",
    "RETRY_POLICY_MISMATCH",
    "DEFAULT_DENY_NOT_PRESERVED",
    "CORRECTION_SEMANTICS_MISSING",
    "ROLLBACK_SEMANTICS_MISSING",
    "EVIDENCE_NOT_BOUND",
    "AUTHORITY_PROMOTION_DETECTED",
]
REASON_BY_FACT = dict(zip(FACT_ORDER, REASON_ORDER, strict=True))


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite number at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_nonfinite(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_nonfinite(child, f"{path}[{index}]")


def load_json_bytes(raw: bytes, label: str) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} is not strict UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc}") from exc
    _reject_nonfinite(value)
    return value


def load_json(path: Path) -> Any:
    return load_json_bytes(path.read_bytes(), str(path))


def _require_exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing or unknown:
        raise ValueError(f"{label} field mismatch; missing={missing}, unknown={unknown}")


def derive(facts: dict[str, bool]) -> tuple[str, list[str]]:
    reasons = [REASON_BY_FACT[fact] for fact in FACT_ORDER if not facts[fact]]
    disposition = "BLOCKED" if reasons else "COMPATIBLE_PENDING_ARCHITECTURE_APPROVAL"
    return disposition, reasons


def validate_corpus(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError("corpus must be an object")
    _require_exact_fields(
        data,
        {"contract_id", "version", "fact_order", "reason_order", "cases"},
        "corpus",
    )
    if data["contract_id"] != CONTRACT_ID:
        raise ValueError("contract_id mismatch")
    if data["version"] != VERSION:
        raise ValueError("version mismatch")
    if data["fact_order"] != FACT_ORDER:
        raise ValueError("fact_order differs from the validator contract")
    if data["reason_order"] != REASON_ORDER:
        raise ValueError("reason_order differs from the validator contract")
    if not isinstance(data["cases"], list) or not data["cases"]:
        raise ValueError("cases must be a non-empty array")

    case_ids: set[str] = set()
    observed_reasons: set[str] = set()
    compatible_interfaces: set[str] = set()
    results: list[dict[str, Any]] = []

    for index, case in enumerate(data["cases"]):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            raise ValueError(f"{label} must be an object")
        _require_exact_fields(case, {"case_id", "interface", "facts", "expected"}, label)

        case_id = case["case_id"]
        interface = case["interface"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{label}.case_id must be a non-empty string")
        if case_id in case_ids:
            raise ValueError(f"duplicate case_id: {case_id}")
        case_ids.add(case_id)
        if not isinstance(interface, str) or not interface:
            raise ValueError(f"{label}.interface must be a non-empty string")

        facts = case["facts"]
        if not isinstance(facts, dict):
            raise ValueError(f"{label}.facts must be an object")
        _require_exact_fields(facts, set(FACT_ORDER), f"{label}.facts")
        for fact in FACT_ORDER:
            if type(facts[fact]) is not bool:
                raise ValueError(f"{label}.facts.{fact} must be boolean")

        if facts["known_interface"] and interface not in KNOWN_INTERFACES:
            raise ValueError(f"{label} marks an unknown interface as known")
        if not facts["known_interface"] and interface in KNOWN_INTERFACES:
            raise ValueError(f"{label} marks a known interface as unknown")

        expected = case["expected"]
        if not isinstance(expected, dict):
            raise ValueError(f"{label}.expected must be an object")
        _require_exact_fields(expected, {"disposition", "reasons"}, f"{label}.expected")
        if expected["disposition"] not in {
            "BLOCKED",
            "COMPATIBLE_PENDING_ARCHITECTURE_APPROVAL",
        }:
            raise ValueError(f"{label}.expected.disposition is invalid")
        if not isinstance(expected["reasons"], list) or any(
            not isinstance(reason, str) for reason in expected["reasons"]
        ):
            raise ValueError(f"{label}.expected.reasons must be a string array")
        if len(expected["reasons"]) != len(set(expected["reasons"])):
            raise ValueError(f"{label}.expected.reasons contains duplicates")
        ordered_expected = [reason for reason in REASON_ORDER if reason in expected["reasons"]]
        if expected["reasons"] != ordered_expected:
            raise ValueError(f"{label}.expected.reasons is not in canonical order")

        disposition, reasons = derive(facts)
        if expected["disposition"] != disposition:
            raise ValueError(
                f"{label} disposition drift: expected {expected['disposition']}, derived {disposition}"
            )
        if expected["reasons"] != reasons:
            raise ValueError(
                f"{label} reason drift: expected {expected['reasons']}, derived {reasons}"
            )

        observed_reasons.update(reasons)
        if disposition == "COMPATIBLE_PENDING_ARCHITECTURE_APPROVAL":
            compatible_interfaces.add(interface)
        results.append(
            {
                "case_id": case_id,
                "interface": interface,
                "disposition": disposition,
                "reasons": reasons,
            }
        )

    missing_reason_coverage = sorted(set(REASON_ORDER) - observed_reasons)
    if missing_reason_coverage:
        raise ValueError(f"corpus lacks reason coverage: {missing_reason_coverage}")
    if compatible_interfaces != KNOWN_INTERFACES:
        raise ValueError(
            "corpus must include one compatible case for each declared interface; "
            f"observed={sorted(compatible_interfaces)}"
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "corpus",
        nargs="?",
        default="fixtures/qso-interface-compatibility-v1.json",
        type=Path,
    )
    args = parser.parse_args(argv)
    try:
        data = load_json(args.corpus)
        results = validate_corpus(data)
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "contract_id": CONTRACT_ID,
                "version": VERSION,
                "case_count": len(results),
                "results": results,
                "authority_effect": "none",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
