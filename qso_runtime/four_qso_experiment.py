from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

QSO_ROLES = {
    "atlas": "mathematical structure, algorithms, compression, and cross-domain mapping",
    "nova": "verification, anomaly detection, testing, security, and contradiction analysis",
    "orion": "software architecture, interfaces, protocols, and systems composition",
    "lyra": "language, documentation, ontology, epistemology, and human context",
}


@dataclass(frozen=True)
class ExperimentLimits:
    max_rounds: int = 4
    max_messages_per_qso: int = 8
    max_message_chars: int = 600
    max_runtime_seconds: float = 10.0


@dataclass
class Event:
    seq: int
    kind: str
    actor: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


@dataclass
class QSOResult:
    name: str
    role: str
    seed: int
    observations: list[str] = field(default_factory=list)
    inferences: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    messages_sent: list[dict[str, str]] = field(default_factory=list)
    messages_received: list[dict[str, str]] = field(default_factory=list)
    freeze_points: list[str] = field(default_factory=list)
    final_proposal: str = ""


class AppendOnlyLedger:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def append(self, kind: str, actor: str, payload: dict[str, Any]) -> Event:
        seq = len(self.events)
        previous_hash = self.events[-1].event_hash if self.events else "GENESIS"
        canonical = json.dumps(
            {"seq": seq, "kind": kind, "actor": actor, "payload": payload, "previous_hash": previous_hash},
            sort_keys=True,
            separators=(",", ":"),
        )
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        event = Event(seq, kind, actor, payload, previous_hash, event_hash)
        self.events.append(event)
        return event

    def verify(self) -> bool:
        prior = "GENESIS"
        for event in self.events:
            canonical = json.dumps(
                {
                    "seq": event.seq,
                    "kind": event.kind,
                    "actor": event.actor,
                    "payload": event.payload,
                    "previous_hash": prior,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            if event.previous_hash != prior:
                return False
            if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != event.event_hash:
                return False
            prior = event.event_hash
        return True


class BoundedQSO:
    def __init__(self, name: str, seed: int, limits: ExperimentLimits, ledger: AppendOnlyLedger) -> None:
        self.name = name
        self.role = QSO_ROLES[name]
        self.seed = seed
        self.rng = random.Random(seed)
        self.limits = limits
        self.ledger = ledger
        self.result = QSOResult(name=name, role=self.role, seed=seed)

    def observe(self, objective: str) -> None:
        observation = f"Objective received: {objective[: self.limits.max_message_chars]}"
        self.result.observations.append(observation)
        self.ledger.append("observation", self.name, {"text": observation})

    def reason(self, round_number: int) -> str:
        templates = {
            "atlas": [
                "Represent the objective as a constrained graph with explicit invariants.",
                "Seek a minimal structure preserving provenance and deterministic replay.",
            ],
            "nova": [
                "Test every claim against failure modes, contradictions, and boundary violations.",
                "Require fail-closed validation and evidence before capability claims.",
            ],
            "orion": [
                "Separate object lifecycle, messaging, policy, ledger, and adapters behind versioned interfaces.",
                "Prefer a small composable runtime with explicit dependency order.",
            ],
            "lyra": [
                "Clarify terminology, user intent, limitations, and human-readable explanations.",
                "Distinguish observations, inferences, hypotheses, and proposals.",
            ],
        }
        inference = templates[self.name][self.rng.randrange(len(templates[self.name]))]
        inference = f"Round {round_number}: {inference}"
        self.result.inferences.append(inference)
        self.ledger.append("inference", self.name, {"round": round_number, "text": inference})
        return inference

    def receive(self, sender: str, text: str) -> None:
        if len(self.result.messages_received) >= self.limits.max_messages_per_qso:
            return
        text = text[: self.limits.max_message_chars]
        self.result.messages_received.append({"from": sender, "text": text})
        self.ledger.append("message_received", self.name, {"from": sender, "text": text})

    def send(self, recipient: "BoundedQSO", text: str) -> None:
        if len(self.result.messages_sent) >= self.limits.max_messages_per_qso:
            return
        text = text[: self.limits.max_message_chars]
        self.result.messages_sent.append({"to": recipient.name, "text": text})
        self.ledger.append("message_sent", self.name, {"to": recipient.name, "text": text})
        recipient.receive(self.name, text)

    def freeze(self, label: str) -> None:
        digest = hashlib.sha256(
            json.dumps(asdict(self.result), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        marker = f"{label}:{digest}"
        self.result.freeze_points.append(marker)
        self.ledger.append("freeze", self.name, {"label": label, "state_hash": digest})

    def finalize(self) -> None:
        if self.name == "nova":
            proposal = "Release only after deterministic replay, ledger verification, limit tests, and contradiction review pass."
        elif self.name == "atlas":
            proposal = "Use a bounded directed message graph and hash-chained state snapshots as the experiment core."
        elif self.name == "orion":
            proposal = "Expose the runner as a library and CLI, with policy and settlement adapters outside the core loop."
        else:
            proposal = "Publish per-QSO reports that clearly label evidence, inference, uncertainty, and non-operational limits."
        self.result.final_proposal = proposal
        self.ledger.append("proposal", self.name, {"text": proposal})


def run_experiment(objective: str, base_seed: int = 2987, limits: ExperimentLimits | None = None) -> dict[str, Any]:
    limits = limits or ExperimentLimits()
    if not objective.strip():
        raise ValueError("objective must not be empty")
    if limits.max_rounds < 1 or limits.max_messages_per_qso < 1 or limits.max_runtime_seconds <= 0:
        raise ValueError("experiment limits must be positive")

    started = time.monotonic()
    ledger = AppendOnlyLedger()
    qsos = {
        name: BoundedQSO(name, base_seed + offset, limits, ledger)
        for offset, name in enumerate(QSO_ROLES)
    }
    ledger.append("experiment_started", "fabric", {"objective": objective, "base_seed": base_seed, "limits": asdict(limits)})

    for qso in qsos.values():
        qso.observe(objective)
        qso.freeze("initial")

    order = list(qsos)
    for round_number in range(1, limits.max_rounds + 1):
        if time.monotonic() - started > limits.max_runtime_seconds:
            ledger.append("runtime_limit", "fabric", {"round": round_number})
            break
        statements: dict[str, str] = {}
        for name in order:
            statements[name] = qsos[name].reason(round_number)
        for index, sender_name in enumerate(order):
            recipient_name = order[(index + 1) % len(order)]
            qsos[sender_name].send(qsos[recipient_name], statements[sender_name])
        for qso in qsos.values():
            qso.freeze(f"round-{round_number}")

    for qso in qsos.values():
        qso.finalize()
        qso.freeze("final")

    ledger.append("experiment_completed", "fabric", {"ledger_valid": ledger.verify()})
    return {
        "objective": objective,
        "base_seed": base_seed,
        "limits": asdict(limits),
        "ledger_valid": ledger.verify(),
        "event_count": len(ledger.events),
        "final_event_hash": ledger.events[-1].event_hash,
        "qsos": {name: asdict(qso.result) for name, qso in qsos.items()},
        "events": [asdict(event) for event in ledger.events],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the bounded Atlas/Nova/Orion/Lyra QSO experiment")
    parser.add_argument("objective", help="Research objective supplied to all four QSOs")
    parser.add_argument("--seed", type=int, default=2987)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--output", type=Path, default=Path("artifacts/four_qso_report.json"))
    args = parser.parse_args()

    report = run_experiment(args.objective, args.seed, ExperimentLimits(max_rounds=args.rounds))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "ledger_valid": report["ledger_valid"], "event_count": report["event_count"]}))


if __name__ == "__main__":
    main()
