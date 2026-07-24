from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
from dataclasses import asdict, dataclass
from typing import Any

from .four_qso_experiment import AppendOnlyLedger, QSO_ROLES
from .gromerical_engine import AugmentationLimits, GromericalEngine, canonical_json


@dataclass(frozen=True)
class SearchProposal:
    qso_name: str
    step: int
    query: str
    rationale: str
    parent_request_sha256: str
    proposal_sha256: str
    network_authority: bool = False
    requires_seeker: bool = True


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bounded_terms(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", text.lower())
    blocked = {"with", "from", "that", "this", "into", "their", "using", "request", "search", "data"}
    unique: list[str] = []
    for word in words:
        if word in blocked or word in unique:
            continue
        unique.append(word)
        if len(unique) >= limit:
            break
    return unique


def propose_queries(objective: str, steps: int = 2) -> dict[str, Any]:
    if not objective.strip():
        raise ValueError("objective must not be empty")
    if not 1 <= steps <= 4:
        raise ValueError("steps must be between 1 and 4")

    ledger = AppendOnlyLedger()
    ledger.append("search_planning_started", "fabric", {"objective": objective, "steps": steps})
    base_terms = bounded_terms(objective)
    if not base_terms:
        raise ValueError("objective produced no searchable terms")

    role_terms = {
        "atlas": ["topology", "mathematical model", "invariants"],
        "nova": ["validation", "failure modes", "security"],
        "orion": ["architecture", "protocol", "orchestration"],
        "lyra": ["ontology", "human factors", "epistemology"],
    }

    proposals: dict[str, list[dict[str, Any]]] = {}
    for qso_name in QSO_ROLES:
        engine = GromericalEngine(qso_name, AugmentationLimits(max_steps=steps, max_delta_chars=220, max_request_chars=1800))
        current = objective
        qso_proposals: list[dict[str, Any]] = []
        for step in range(1, steps + 1):
            augmentation = engine.augment(objective, current, step)
            current = augmentation.augmented_request
            terms = base_terms[:5] + [role_terms[qso_name][(step - 1) % len(role_terms[qso_name])]]
            query = " ".join(terms)[:180]
            rationale = f"Increment {step}: apply the {qso_name} analytical lens while preserving the original objective."
            payload = {
                "qso_name": qso_name,
                "step": step,
                "query": query,
                "rationale": rationale,
                "parent_request_sha256": augmentation.parent_request_sha256,
                "network_authority": False,
                "requires_seeker": True,
            }
            proposal = SearchProposal(
                qso_name=qso_name,
                step=step,
                query=query,
                rationale=rationale,
                parent_request_sha256=augmentation.parent_request_sha256,
                proposal_sha256=sha256_text(canonical_json(payload)),
            )
            record = asdict(proposal)
            qso_proposals.append(record)
            ledger.append("search_proposed", qso_name, record)
        proposals[qso_name] = qso_proposals
        freeze_hash = sha256_text(canonical_json(qso_proposals))
        ledger.append("search_plan_freeze", qso_name, {"state_hash": freeze_hash, "human_review_required": True})

    ledger.append("search_planning_completed", "fabric", {"ledger_valid": ledger.verify()})
    return {
        "schema_version": "qso-gromerical-search-plan-v1",
        "objective": objective,
        "steps": steps,
        "proposals": proposals,
        "ledger_valid": ledger.verify(),
        "events": [asdict(event) for event in ledger.events],
        "network_authority": "seeker-only",
        "automatic_release": False,
        "human_review_required": True,
    }


def crossref_url(query: str, rows: int = 3) -> str:
    return "https://api.crossref.org/works?" + urllib.parse.urlencode({"query": query, "rows": rows, "select": "DOI,title,author,published,URL,type"})
