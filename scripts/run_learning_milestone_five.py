from __future__ import annotations

import argparse
import json
from pathlib import Path

from qso_runtime.model_audit_envelope import (
    AuditDiversityGate,
    DeterministicAuditEnvelope,
    DeterministicFixtureAdapter,
    ReplayVerifier,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Milestone 5 deterministic multi-auditor qualification")
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    adapter = DeterministicFixtureAdapter()
    envelope = DeterministicAuditEnvelope(args.capture_dir)
    transcripts = [
        envelope.run(
            auditor_name=name,
            adapter=adapter,
            evidence_hashes=["evidence-a", "evidence-b"],
            prompt="Audit a review-ready candidate under frozen evidence.",
            seed=0,
        )
        for name in ("atlas", "nova", "orion", "lyra", "aria")
    ]
    diversity = AuditDiversityGate().evaluate(transcripts, ambiguous=True)
    replay = {t["request"]["auditor"]: ReplayVerifier().verify(t, adapter) for t in transcripts}
    report = {
        "schema_version": "qso-learning-milestone-five-v1",
        "transcripts": transcripts,
        "diversity": diversity,
        "replay": replay,
        "all_replays_valid": all(replay.values()),
        "promotion_allowed": not diversity["promotion_blocked"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_replays_valid": report["all_replays_valid"],
        "promotion_allowed": report["promotion_allowed"],
        "transcript_count": len(transcripts),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
