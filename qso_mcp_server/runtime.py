from __future__ import annotations

import hashlib
import json
import math
import threading
import time
import uuid
from dataclasses import asdict
from typing import Any

from qso_runtime.four_qso_experiment import ExperimentLimits, QSO_ROLES, run_experiment

_MAX_JOBS = 1024
_MAX_OBJECTIVE_CHARS = 8192
_MIN_SEED = -(2**63)
_MAX_SEED = 2**63 - 1
_DIGEST_DOMAIN_REQUEST = b"qso-mcp-request-v1\0"
_DIGEST_DOMAIN_REPORT = b"qso-mcp-report-v1\0"


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("value is not strict canonical JSON") from exc
    return encoded.encode("utf-8")


def _json_snapshot(value: Any) -> Any:
    return json.loads(_canonical_json_bytes(value).decode("utf-8"))


def _digest(domain: bytes, value: Any) -> str:
    return hashlib.sha256(domain + _canonical_json_bytes(value)).hexdigest()


def _exact_int(name: str, value: Any, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _finite_number(name: str, value: Any, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    if not minimum <= normalized <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return normalized


def _objective(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("objective must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError("objective must not be empty")
    if len(normalized) > _MAX_OBJECTIVE_CHARS:
        raise ValueError(f"objective must not exceed {_MAX_OBJECTIVE_CHARS} characters")
    if "\x00" in normalized:
        raise ValueError("objective must not contain NUL characters")
    return normalized


def _job_id(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("job_id must be a string")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError("job_id must be a canonical UUID") from exc
    canonical = str(parsed)
    if value != canonical:
        raise ValueError("job_id must be a canonical lowercase UUID")
    return value


def _validate_report(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("simulation report must be an object")
    snapshot = _json_snapshot(report)
    if snapshot.get("ledger_valid") is not True:
        raise ValueError("simulation report ledger_valid must be exactly true")
    if not isinstance(snapshot.get("final_event_hash"), str) or len(snapshot["final_event_hash"]) != 64:
        raise ValueError("simulation report final_event_hash must be a 64-character string")
    return snapshot


class QSOService:
    """Thread-safe, bounded in-memory adapter around the QSO research runtime."""

    def __init__(self, max_jobs: int = 128) -> None:
        self.max_jobs = _exact_int("max_jobs", max_jobs, 1, _MAX_JOBS)
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def capabilities(self) -> dict[str, Any]:
        return {
            "runtime": "qso-fabric",
            "simulation_types": ["four_qso_experiment"],
            "qso_roles": dict(QSO_ROLES),
            "replay": {
                "report_digest_comparison": True,
                "guaranteed": False,
                "nondeterminism_sources": ["runtime_deadline"],
            },
            "ledger": "sha256-hash-chain",
            "storage": {
                "kind": "bounded-in-memory",
                "durable": False,
                "max_jobs": self.max_jobs,
            },
            "transports": ["stdio", "streamable-http-local-opt-in"],
            "authority": {
                "shell": False,
                "package_installation": False,
                "credentials": False,
                "unrestricted_network": False,
                "filesystem_write": False,
            },
        }

    def list_simulations(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "four_qso_experiment",
                "description": "Bounded Atlas/Nova/Orion/Lyra collaborative simulation.",
                "parameters": {
                    "objective": f"non-empty string, at most {_MAX_OBJECTIVE_CHARS} characters",
                    "seed": f"integer {_MIN_SEED}..{_MAX_SEED}",
                    "rounds": "integer 1..32",
                    "max_messages_per_qso": "integer 1..64",
                    "max_message_chars": "integer 64..8000",
                    "max_runtime_seconds": "finite number 0.1..120",
                },
            }
        ]

    def run(
        self,
        objective: str,
        seed: int = 2987,
        rounds: int = 4,
        max_messages_per_qso: int = 8,
        max_message_chars: int = 600,
        max_runtime_seconds: float = 10.0,
    ) -> dict[str, Any]:
        normalized_objective = _objective(objective)
        normalized_seed = _exact_int("seed", seed, _MIN_SEED, _MAX_SEED)
        normalized_rounds = _exact_int("rounds", rounds, 1, 32)
        normalized_messages = _exact_int("max_messages_per_qso", max_messages_per_qso, 1, 64)
        normalized_chars = _exact_int("max_message_chars", max_message_chars, 64, 8000)
        normalized_runtime = _finite_number("max_runtime_seconds", max_runtime_seconds, 0.1, 120.0)

        limits = ExperimentLimits(
            max_rounds=normalized_rounds,
            max_messages_per_qso=normalized_messages,
            max_message_chars=normalized_chars,
            max_runtime_seconds=normalized_runtime,
        )
        request = {
            "objective": normalized_objective,
            "seed": normalized_seed,
            "limits": asdict(limits),
        }
        request = _json_snapshot(request)
        request_digest = _digest(_DIGEST_DOMAIN_REQUEST, request)
        new_job_id = str(uuid.uuid4())
        created_at = time.time()
        running_record = {
            "schema_version": "qso-mcp-job-v1",
            "job_id": new_job_id,
            "status": "running",
            "created_at": created_at,
            "request_digest": request_digest,
            "request": request,
        }

        with self._lock:
            self._evict_if_needed()
            self._jobs[new_job_id] = _json_snapshot(running_record)

        try:
            report = _validate_report(run_experiment(normalized_objective, normalized_seed, limits))
            result_digest = _digest(_DIGEST_DOMAIN_REPORT, report)
            record = {
                **running_record,
                "status": "completed",
                "completed_at": time.time(),
                "result_digest": result_digest,
                "report": report,
            }
        except Exception as exc:
            record = {
                **running_record,
                "status": "failed",
                "completed_at": time.time(),
                "error_type": type(exc).__name__,
                "error": "simulation execution failed",
            }
            with self._lock:
                self._jobs[new_job_id] = _json_snapshot(record)
            raise

        snapshot = _json_snapshot(record)
        with self._lock:
            self._jobs[new_job_id] = snapshot
        return _json_snapshot(snapshot)

    def get_job(self, job_id: str, include_report: bool = True) -> dict[str, Any]:
        canonical_job_id = _job_id(job_id)
        if not isinstance(include_report, bool):
            raise TypeError("include_report must be a boolean")
        with self._lock:
            try:
                record = self._jobs[canonical_job_id]
            except KeyError as exc:
                raise KeyError(f"unknown job_id: {canonical_job_id}") from exc
            snapshot = _json_snapshot(record)
        if not include_report:
            snapshot.pop("report", None)
        return snapshot

    def list_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        normalized_limit = _exact_int("limit", limit, 1, self.max_jobs)
        with self._lock:
            records = sorted(
                self._jobs.values(),
                key=lambda item: (item["created_at"], item["job_id"]),
                reverse=True,
            )[:normalized_limit]
            return [
                _json_snapshot({key: value for key, value in item.items() if key != "report"})
                for item in records
            ]

    def verify_job(self, job_id: str) -> dict[str, Any]:
        record = self.get_job(job_id)
        if record.get("status") != "completed" or "report" not in record:
            return {
                "job_id": record["job_id"],
                "valid": False,
                "reason": "job has no completed report",
            }

        try:
            report = _validate_report(record["report"])
            request_digest = _digest(_DIGEST_DOMAIN_REQUEST, record["request"])
            result_digest = _digest(_DIGEST_DOMAIN_REPORT, report)
        except ValueError:
            return {
                "job_id": record["job_id"],
                "valid": False,
                "reason": "stored job is not strict valid JSON evidence",
            }

        request_matches = request_digest == record.get("request_digest")
        digest_matches = result_digest == record.get("result_digest")
        ledger_valid = report.get("ledger_valid") is True
        return {
            "job_id": record["job_id"],
            "valid": ledger_valid and request_matches and digest_matches,
            "ledger_valid": ledger_valid,
            "request_digest_matches": request_matches,
            "digest_matches": digest_matches,
            "request_digest": request_digest,
            "result_digest": result_digest,
            "final_event_hash": report.get("final_event_hash"),
        }

    def replay(self, job_id: str) -> dict[str, Any]:
        original = self.get_job(job_id)
        if original.get("status") != "completed":
            raise ValueError("only completed jobs can be replayed")
        request = original["request"]
        limits = request["limits"]
        replayed = self.run(
            objective=request["objective"],
            seed=request["seed"],
            rounds=limits["max_rounds"],
            max_messages_per_qso=limits["max_messages_per_qso"],
            max_message_chars=limits["max_message_chars"],
            max_runtime_seconds=limits["max_runtime_seconds"],
        )
        return {
            "source_job_id": original["job_id"],
            "replay_job_id": replayed["job_id"],
            "deterministic_match": replayed["result_digest"] == original.get("result_digest"),
            "source_digest": original.get("result_digest"),
            "replay_digest": replayed.get("result_digest"),
            "guaranteed": False,
        }

    def _evict_if_needed(self) -> None:
        while len(self._jobs) >= self.max_jobs:
            terminal = [
                (key, record)
                for key, record in self._jobs.items()
                if record.get("status") in {"completed", "failed"}
            ]
            if not terminal:
                raise RuntimeError("job capacity is exhausted by running jobs")
            oldest_key, _ = min(
                terminal,
                key=lambda item: (item[1]["created_at"], item[0]),
            )
            del self._jobs[oldest_key]
