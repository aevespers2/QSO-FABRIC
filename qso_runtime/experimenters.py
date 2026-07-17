from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROLE_ORDER = (
    "futurist",
    "theorist",
    "inventor",
    "skeptic",
    "experimentalist",
    "observer",
    "synthesist",
    "engineer",
    "optimizer",
    "strategist",
    "ethicist_governor",
    "archivist",
)

ROLE_PURPOSES = {
    "futurist": "explore plural futures, signals, risks, opportunities, and second-order effects",
    "theorist": "form falsifiable hypotheses, assumptions, mechanisms, and predictions",
    "inventor": "create novel mechanisms, algorithms, devices, architectures, and prototype paths",
    "skeptic": "attempt falsification and expose assumptions, contradictions, and failure modes",
    "experimentalist": "design controlled experiments, simulations, metrics, and stopping conditions",
    "observer": "record measurements, provenance, anomalies, and the distinction between evidence and interpretation",
    "synthesist": "integrate evidence across roles while preserving uncertainty and material disagreement",
    "engineer": "translate validated concepts into bounded architectures, interfaces, prototypes, and tests",
    "optimizer": "improve performance and efficiency without weakening safety or provenance invariants",
    "strategist": "prioritize work, dependencies, resources, and decision criteria",
    "ethicist_governor": "review safety, authority, reversibility, governance, and human impact",
    "archivist": "preserve decisions, provenance, artifact indexes, and reproduction instructions",
}

ROLE_PROMPTS = {
    "futurist": "Describe three plausible time-horizon scenarios and the signals that would distinguish them.",
    "theorist": "State a falsifiable hypothesis, its assumptions, and at least one prediction.",
    "inventor": "Propose a novel embodiment, explain the claimed novelty, and identify a minimal prototype.",
    "skeptic": "Identify the strongest counterexample, hidden assumption, and disconfirming test.",
    "experimentalist": "Define controls, variables, metrics, stopping conditions, and acceptance criteria.",
    "observer": "Separate direct observations from interpretations and record any anomalies.",
    "synthesist": "Integrate agreements and conflicts without erasing uncertainty or dissent.",
    "engineer": "Specify components, interfaces, dependencies, tests, and bounded implementation steps.",
    "optimizer": "Define a baseline, objective function, tradeoffs, and invariant-preserving improvements.",
    "strategist": "Rank the next actions by value, dependency, risk, and reversibility.",
    "ethicist_governor": "Assess authority, safety, reversibility, human impact, and required review gates.",
    "archivist": "Create a provenance record, artifact index, decision log, and reproduction checklist.",
}


@dataclass(frozen=True)
class CollectiveLimits:
    max_rounds: int = 2
    max_messages_per_role: int = 4
    max_message_chars: int = 800


@dataclass
class RoleResult:
    role: str
    purpose: str
    contributions: list[str] = field(default_factory=list)
    messages_sent: list[dict[str, str]] = field(default_factory=list)
    messages_received: list[dict[str, str]] = field(default_factory=list)
    freeze_points: list[str] = field(default_factory=list)


@dataclass
class LedgerEvent:
    seq: int
    kind: str
    actor: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


class AppendOnlyLedger:
    def __init__(self) -> None:
        self.events: list[LedgerEvent] = []

    def append(self, kind: str, actor: str, payload: dict[str, Any]) -> LedgerEvent:
        seq = len(self.events)
        previous_hash = self.events[-1].event_hash if self.events else "GENESIS"
        canonical = json.dumps(
            {"seq": seq, "kind": kind, "actor": actor, "payload": payload, "previous_hash": previous_hash},
            sort_keys=True,
            separators=(",", ":"),
        )
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        event = LedgerEvent(seq, kind, actor, payload, previous_hash, event_hash)
        self.events.append(event)
        return event

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for event in self.events:
            canonical = json.dumps(
                {
                    "seq": event.seq,
                    "kind": event.kind,
                    "actor": event.actor,
                    "payload": event.payload,
                    "previous_hash": previous_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            if event.previous_hash != previous_hash:
                return False
            if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != event.event_hash:
                return False
            previous_hash = event.event_hash
        return True


class Experimenter:
    def __init__(self, role: str, limits: CollectiveLimits, ledger: AppendOnlyLedger) -> None:
        if role not in ROLE_PURPOSES:
            raise ValueError(f"unknown experimenter role: {role}")
        self.role = role
        self.limits = limits
        self.ledger = ledger
        self.result = RoleResult(role=role, purpose=ROLE_PURPOSES[role])

    def contribute(self, objective: str, round_number: int) -> str:
        objective_excerpt = objective[: self.limits.max_message_chars]
        contribution = f"Round {round_number}: {ROLE_PROMPTS[self.role]} Objective: {objective_excerpt}"
        self.result.contributions.append(contribution)
        self.ledger.append("contribution", self.role, {"round": round_number, "text": contribution})
        return contribution

    def send(self, recipient: "Experimenter", text: str) -> None:
        if len(self.result.messages_sent) >= self.limits.max_messages_per_role:
            return
        bounded = text[: self.limits.max_message_chars]
        self.result.messages_sent.append({"to": recipient.role, "text": bounded})
        self.ledger.append("message_sent", self.role, {"to": recipient.role, "text": bounded})
        recipient.receive(self.role, bounded)

    def receive(self, sender: str, text: str) -> None:
        if len(self.result.messages_received) >= self.limits.max_messages_per_role:
            return
        bounded = text[: self.limits.max_message_chars]
        self.result.messages_received.append({"from": sender, "text": bounded})
        self.ledger.append("message_received", self.role, {"from": sender, "text": bounded})

    def freeze(self, label: str) -> None:
        digest = hashlib.sha256(
            json.dumps(asdict(self.result), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        marker = f"{label}:{digest}"
        self.result.freeze_points.append(marker)
        self.ledger.append("freeze", self.role, {"label": label, "state_hash": digest})


def run_collective(
    objective: str,
    limits: CollectiveLimits | None = None,
    roles: tuple[str, ...] = ROLE_ORDER,
) -> dict[str, Any]:
    limits = limits or CollectiveLimits()
    if not objective.strip():
        raise ValueError("objective must not be empty")
    if limits.max_rounds < 1 or limits.max_messages_per_role < 1 or limits.max_message_chars < 1:
        raise ValueError("collective limits must be positive")
    if not roles or len(set(roles)) != len(roles):
        raise ValueError("roles must be non-empty and unique")

    ledger = AppendOnlyLedger()
    experimenters = {role: Experimenter(role, limits, ledger) for role in roles}
    ledger.append(
        "collective_started",
        "fabric",
        {"objective": objective, "roles": list(roles), "limits": asdict(limits)},
    )

    for experimenter in experimenters.values():
        experimenter.freeze("initial")

    for round_number in range(1, limits.max_rounds + 1):
        contributions = {
            role: experimenters[role].contribute(objective, round_number)
            for role in roles
        }
        for index, sender_role in enumerate(roles):
            recipient_role = roles[(index + 1) % len(roles)]
            experimenters[sender_role].send(experimenters[recipient_role], contributions[sender_role])
        for experimenter in experimenters.values():
            experimenter.freeze(f"round-{round_number}")

    ledger.append("human_review_required", "ethicist_governor", {"required": True})
    for experimenter in experimenters.values():
        experimenter.freeze("final")
    ledger.append("collective_completed", "fabric", {"ledger_valid": ledger.verify()})

    return {
        "objective": objective,
        "workflow": list(roles),
        "limits": asdict(limits),
        "human_review_required": True,
        "ledger_valid": ledger.verify(),
        "event_count": len(ledger.events),
        "final_event_hash": ledger.events[-1].event_hash,
        "experimenters": {role: asdict(experimenters[role].result) for role in roles},
        "events": [asdict(event) for event in ledger.events],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the bounded QSO Experimenters collective")
    parser.add_argument("objective", help="Research or invention objective supplied to the collective")
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--output", type=Path, default=Path("artifacts/experimenters_report.json"))
    args = parser.parse_args()

    report = run_collective(args.objective, CollectiveLimits(max_rounds=args.rounds))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "ledger_valid": report["ledger_valid"],
                "event_count": report["event_count"],
            }
        )
    )


if __name__ == "__main__":
    main()
