from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class ModelAdapter(Protocol):
    provider: str
    model: str
    model_revision: str

    def generate(self, request: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class AuditorProfile:
    name: str
    role: str
    system_boundary: str
    provider_family: str


AUDITOR_PROFILES = {
    "atlas": AuditorProfile("atlas", "structural audit", "Check invariants and topology only.", "family-a"),
    "nova": AuditorProfile("nova", "falsification audit", "Seek counterevidence and failure modes only.", "family-b"),
    "orion": AuditorProfile("orion", "integration audit", "Check interfaces, state transitions, and deployment only.", "family-c"),
    "lyra": AuditorProfile("lyra", "semantic audit", "Check definitions, ambiguity, and human interpretability only.", "family-d"),
    "aria": AuditorProfile("aria", "adversarial synthesis", "Challenge shared assumptions and synthesize counterexamples only.", "family-e"),
}


class DeterministicAuditEnvelope:
    def __init__(self, capture_dir: Path) -> None:
        self.capture_dir = capture_dir
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        *,
        auditor_name: str,
        adapter: ModelAdapter,
        evidence_hashes: list[str],
        prompt: str,
        seed: int = 0,
    ) -> dict[str, Any]:
        if auditor_name not in AUDITOR_PROFILES:
            raise ValueError(f"unknown auditor: {auditor_name}")
        profile = AUDITOR_PROFILES[auditor_name]
        request = {
            "auditor": auditor_name,
            "role": profile.role,
            "system_boundary": profile.system_boundary,
            "provider": adapter.provider,
            "model": adapter.model,
            "model_revision": adapter.model_revision,
            "temperature": 0,
            "top_p": 1,
            "seed": seed,
            "evidence_hashes": sorted(evidence_hashes),
            "prompt": prompt,
        }
        response = adapter.generate(request)
        if response.get("request_echo_hash") != sha256_json(request):
            raise ValueError("model adapter did not bind response to exact request")
        transcript = {
            "request": request,
            "response": response,
            "request_hash": sha256_json(request),
            "response_hash": sha256_json(response),
        }
        transcript["transcript_hash"] = sha256_json(transcript)
        path = self.capture_dir / f"{auditor_name}-{transcript['transcript_hash']}.json"
        path.write_text(json.dumps(transcript, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return transcript


class DeterministicFixtureAdapter:
    provider = "fixture-provider"
    model = "fixture-auditor"
    model_revision = "fixture-auditor@sha256:1"

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        digest = sha256_json({
            "auditor": request["auditor"],
            "prompt": request["prompt"],
            "evidence_hashes": request["evidence_hashes"],
            "seed": request["seed"],
            "model_revision": request["model_revision"],
        })
        verdict = "challenge" if request["auditor"] in {"nova", "aria"} else "provisional-accept"
        return {
            "verdict": verdict,
            "analysis_digest": digest,
            "confidence": 0.5,
            "request_echo_hash": sha256_json(request),
            "raw_token_log": [digest[index:index + 8] for index in range(0, 32, 8)],
        }


class AuditDiversityGate:
    def evaluate(self, transcripts: list[dict[str, Any]], *, ambiguous: bool) -> dict[str, Any]:
        if len(transcripts) < 2:
            raise ValueError("at least two auditor transcripts are required")
        providers = {t["request"]["provider"] for t in transcripts}
        revisions = {t["request"]["model_revision"] for t in transcripts}
        verdicts = [t["response"]["verdict"] for t in transcripts]
        unanimous = len(set(verdicts)) == 1
        low_model_diversity = len(revisions) == 1
        trigger_aria = ambiguous and unanimous
        promotion_blocked = trigger_aria or low_model_diversity
        return {
            "auditor_count": len(transcripts),
            "provider_count": len(providers),
            "model_revision_count": len(revisions),
            "unanimous": unanimous,
            "low_model_diversity": low_model_diversity,
            "trigger_aria": trigger_aria,
            "promotion_blocked": promotion_blocked,
        }


class ReplayVerifier:
    def verify(self, transcript: dict[str, Any], adapter: ModelAdapter) -> bool:
        request = transcript["request"]
        replay_response = adapter.generate(request)
        return (
            sha256_json(request) == transcript["request_hash"]
            and sha256_json(replay_response) == transcript["response_hash"]
            and replay_response == transcript["response"]
        )
