from __future__ import annotations

import argparse
import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from qso_runtime.four_qso_experiment import AppendOnlyLedger, ExperimentLimits, run_experiment

EXPEDITION_TYPES = (
    "cross_domain_analogy",
    "contradiction_hunt",
    "experiment_design",
    "counterfactual_world",
)


@dataclass(frozen=True)
class CuriosityLimits:
    max_expeditions: int = 4
    max_rounds_per_expedition: int = 2
    max_prompt_chars: int = 800
    max_runtime_seconds_per_expedition: float = 10.0


@dataclass(frozen=True)
class DiscoveryScore:
    novelty: float
    evidence: float
    impact: float
    safety: float
    total: float


@dataclass
class Expedition:
    expedition_id: str
    expedition_type: str
    question: str
    seed: int
    hypotheses: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    experiments: list[str] = field(default_factory=list)
    score: DiscoveryScore | None = None
    fabric_report_hash: str = ""


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _stable_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _question_templates(objective: str) -> dict[str, str]:
    objective = objective.strip()
    return {
        "cross_domain_analogy": (
            f"Which structurally precise analogy from an unrelated discipline could clarify or improve: {objective}?"
        ),
        "contradiction_hunt": (
            f"What assumptions, boundary cases, or internal contradictions could invalidate the current model of: {objective}?"
        ),
        "experiment_design": (
            f"What smallest falsifiable experiment would distinguish the leading explanations for: {objective}?"
        ),
        "counterfactual_world": (
            f"How would the system behave if one central constraint were reversed or removed from: {objective}?"
        ),
    }


def plan_expeditions(
    objective: str,
    seed: int = 2987,
    limits: CuriosityLimits | None = None,
) -> list[Expedition]:
    limits = limits or CuriosityLimits()
    if not objective.strip():
        raise ValueError("objective must not be empty")
    if limits.max_expeditions < 1 or limits.max_expeditions > len(EXPEDITION_TYPES):
        raise ValueError(f"max_expeditions must be between 1 and {len(EXPEDITION_TYPES)}")
    if limits.max_prompt_chars < 32:
        raise ValueError("max_prompt_chars must be at least 32")

    rng = random.Random(seed)
    questions = _question_templates(objective[: limits.max_prompt_chars])
    expedition_types = list(EXPEDITION_TYPES)
    rng.shuffle(expedition_types)

    planned: list[Expedition] = []
    for index, expedition_type in enumerate(expedition_types[: limits.max_expeditions]):
        expedition_seed = seed + (index + 1) * 1009
        question = questions[expedition_type][: limits.max_prompt_chars]
        expedition_id = _stable_hash(
            {"objective": objective, "type": expedition_type, "seed": expedition_seed}
        )[:16]
        planned.append(
            Expedition(
                expedition_id=expedition_id,
                expedition_type=expedition_type,
                question=question,
                seed=expedition_seed,
            )
        )
    return planned


def _extract_findings(report: dict[str, Any], expedition: Expedition) -> None:
    qsos = report["qsos"]
    expedition.hypotheses = [
        qsos["atlas"]["final_proposal"],
        qsos["orion"]["final_proposal"],
        qsos["lyra"]["final_proposal"],
    ]
    expedition.contradictions = list(qsos["nova"]["inferences"])
    expedition.experiments = [
        "Run the proposal under deterministic replay with a changed seed and compare invariant outputs.",
        "Construct one adversarial boundary case and record whether the ledger remains valid.",
    ]
    expedition.fabric_report_hash = _stable_hash(report)


def score_expedition(expedition: Expedition, report: dict[str, Any]) -> DiscoveryScore:
    type_bias = {
        "cross_domain_analogy": (0.86, 0.58, 0.70),
        "contradiction_hunt": (0.66, 0.90, 0.82),
        "experiment_design": (0.72, 0.94, 0.88),
        "counterfactual_world": (0.92, 0.48, 0.68),
    }
    novelty_base, evidence_base, impact_base = type_bias[expedition.expedition_type]
    digest = int(expedition.fabric_report_hash[:8], 16)
    jitter = ((digest % 101) - 50) / 1000.0
    evidence_bonus = min(0.08, report["event_count"] / 1000.0)

    novelty = _clamp(novelty_base + jitter)
    evidence = _clamp(evidence_base + evidence_bonus - abs(jitter) / 2)
    impact = _clamp(impact_base + jitter / 2)
    safety = 1.0 if report["ledger_valid"] else 0.0
    total = _clamp(0.30 * novelty + 0.30 * evidence + 0.25 * impact + 0.15 * safety)
    return DiscoveryScore(novelty, evidence, impact, safety, total)


def run_curiosity_engine(
    objective: str,
    seed: int = 2987,
    limits: CuriosityLimits | None = None,
) -> dict[str, Any]:
    limits = limits or CuriosityLimits()
    ledger = AppendOnlyLedger()
    expeditions = plan_expeditions(objective, seed, limits)
    ledger.append(
        "curiosity_started",
        "curiosity_engine",
        {"objective": objective, "seed": seed, "limits": asdict(limits)},
    )

    for expedition in expeditions:
        ledger.append(
            "expedition_started",
            "curiosity_engine",
            {
                "expedition_id": expedition.expedition_id,
                "type": expedition.expedition_type,
                "question": expedition.question,
                "seed": expedition.seed,
            },
        )
        report = run_experiment(
            expedition.question,
            base_seed=expedition.seed,
            limits=ExperimentLimits(
                max_rounds=limits.max_rounds_per_expedition,
                max_runtime_seconds=limits.max_runtime_seconds_per_expedition,
            ),
        )
        _extract_findings(report, expedition)
        expedition.score = score_expedition(expedition, report)
        ledger.append(
            "expedition_completed",
            "curiosity_engine",
            {
                "expedition_id": expedition.expedition_id,
                "fabric_report_hash": expedition.fabric_report_hash,
                "score": asdict(expedition.score),
            },
        )

    ranked = sorted(expeditions, key=lambda item: item.score.total if item.score else 0.0, reverse=True)
    ledger.append(
        "curiosity_completed",
        "curiosity_engine",
        {"ranked_expedition_ids": [item.expedition_id for item in ranked]},
    )
    ledger_valid = ledger.verify()
    return {
        "objective": objective,
        "seed": seed,
        "limits": asdict(limits),
        "ledger_valid": ledger_valid,
        "final_event_hash": ledger.events[-1].event_hash,
        "expeditions": [asdict(item) for item in ranked],
        "events": [asdict(event) for event in ledger.events],
        "human_review_required": True,
        "network_authority": False,
        "execution_authority": False,
    }


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run bounded QSO curiosity expeditions")
    parser.add_argument("objective", help="Research objective to explore")
    parser.add_argument("--seed", type=int, default=2987)
    parser.add_argument("--expeditions", type=int, default=4)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--output", type=Path, default=Path("artifacts/curiosity_report.json"))
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_curiosity_engine(
        args.objective,
        seed=args.seed,
        limits=CuriosityLimits(
            max_expeditions=args.expeditions,
            max_rounds_per_expedition=args.rounds,
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "ledger_valid": report["ledger_valid"],
                "expeditions": len(report["expeditions"]),
                "top_score": report["expeditions"][0]["score"]["total"],
            }
        )
    )


if __name__ == "__main__":
    main()
