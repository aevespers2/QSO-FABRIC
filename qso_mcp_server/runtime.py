from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from dataclasses import asdict
from typing import Any

from qso_runtime.four_qso_experiment import ExperimentLimits, QSO_ROLES, run_experiment


class QSOService:
    """Thread-safe, in-memory adapter around the bounded QSO runtime."""

    def __init__(self, max_jobs: int = 128) -> None:
        if max_jobs < 1:
            raise ValueError("max_jobs must be positive")
        self.max_jobs = max_jobs
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def capabilities(self) -> dict[str, Any]:
        return {
            "runtime": "qso-fabric",
            "simulation_types": ["four_qso_experiment"],
            "qso_roles": dict(QSO_ROLES),
            "deterministic_replay": True,
            "ledger": "sha256-hash-chain",
            "transports": ["stdio", "streamable-http"],
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
                    "objective": "non-empty string",
                    "seed": "integer",
                    "rounds": "1..32",
                    "max_messages_per_qso": "1..64",
                    "max_message_chars": "64..8000",
                    "max_runtime_seconds": "0.1..120",
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
        objective = objective.strip()
        if not objective:
            raise ValueError("objective must not be empty")
        if not 1 <= rounds <= 32:
            raise ValueError("rounds must be between 1 and 32")
        if not 1 <= max_messages_per_qso <= 64:
            raise ValueError("max_messages_per_qso must be between 1 and 64")
        if not 64 <= max_message_chars <= 8000:
            raise ValueError("max_message_chars must be between 64 and 8000")
        if not 0.1 <= max_runtime_seconds <= 120.0:
            raise ValueError("max_runtime_seconds must be between 0.1 and 120")

        job_id = str(uuid.uuid4())
        created_at = time.time()
        limits = ExperimentLimits(
            max_rounds=rounds,
            max_messages_per_qso=max_messages_per_qso,
            max_message_chars=max_message_chars,
            max_runtime_seconds=max_runtime_seconds,
        )
        with self._lock:
            self._evict_if_needed()
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "running",
                "created_at": created_at,
                "request": {"objective": objective, "seed": seed, "limits": asdict(limits)},
            }

        try:
            report = run_experiment(objective, seed, limits)
            result_digest = hashlib.sha256(
                json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            record = {
                "job_id": job_id,
                "status": "completed",
                "created_at": created_at,
                "completed_at": time.time(),
                "request": {"objective": objective, "seed": seed, "limits": asdict(limits)},
                "result_digest": result_digest,
                "report": report,
            }
        except Exception as exc:
            record = {
                "job_id": job_id,
                "status": "failed",
                "created_at": created_at,
                "completed_at": time.time(),
                "request": {"objective": objective, "seed": seed, "limits": asdict(limits)},
                "error": f"{type(exc).__name__}: {exc}",
            }
            with self._lock:
                self._jobs[job_id] = record
            raise

        with self._lock:
            self._jobs[job_id] = record
        return record

    def get_job(self, job_id: str, include_report: bool = True) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(f"unknown job_id: {job_id}")
            record = dict(self._jobs[job_id])
        if not include_report:
            record.pop("report", None)
        return record

    def list_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        if not 1 <= limit <= self.max_jobs:
            raise ValueError(f"limit must be between 1 and {self.max_jobs}")
        with self._lock:
            records = sorted(self._jobs.values(), key=lambda item: item["created_at"], reverse=True)[:limit]
            return [{key: value for key, value in item.items() if key != "report"} for item in records]

    def verify_job(self, job_id: str) -> dict[str, Any]:
        record = self.get_job(job_id)
        report = record.get("report")
        if not report:
            return {"job_id": job_id, "valid": False, "reason": "job has no completed report"}
        digest = hashlib.sha256(
            json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return {
            "job_id": job_id,
            "valid": bool(report.get("ledger_valid")) and digest == record.get("result_digest"),
            "ledger_valid": bool(report.get("ledger_valid")),
            "digest_matches": digest == record.get("result_digest"),
            "result_digest": digest,
            "final_event_hash": report.get("final_event_hash"),
        }

    def replay(self, job_id: str) -> dict[str, Any]:
        original = self.get_job(job_id)
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
            "source_job_id": job_id,
            "replay_job_id": replayed["job_id"],
            "deterministic_match": replayed["result_digest"] == original.get("result_digest"),
            "source_digest": original.get("result_digest"),
            "replay_digest": replayed.get("result_digest"),
        }

    def _evict_if_needed(self) -> None:
        while len(self._jobs) >= self.max_jobs:
            oldest = min(self._jobs, key=lambda key: self._jobs[key]["created_at"])
            del self._jobs[oldest]
