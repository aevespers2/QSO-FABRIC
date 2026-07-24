from __future__ import annotations

"""Report which optional cryptographic provider dependencies are available."""

import argparse
import importlib.util
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityProbe:
    capability: str
    module: str
    available: bool
    production_accepted: bool
    detail: str


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def probe_capabilities() -> dict[str, Any]:
    oqs = _module_available("oqs")
    openfhe = _module_available("openfhe")
    probes = [
        CapabilityProbe(
            capability="post_quantum_kem",
            module="oqs",
            available=oqs,
            production_accepted=False,
            detail=(
                "liboqs-python detected; QSO adapter supports ML-KEM but remains research-grade"
                if oqs
                else "liboqs-python not detected"
            ),
        ),
        CapabilityProbe(
            capability="fully_homomorphic_encryption",
            module="openfhe",
            available=openfhe,
            production_accepted=False,
            detail=(
                "OpenFHE Python detected; concrete QSO serialization/evaluation adapter is still required"
                if openfhe
                else "OpenFHE Python not detected"
            ),
        ),
        CapabilityProbe(
            capability="zero_knowledge",
            module="external-provider",
            available=False,
            production_accepted=False,
            detail="no concrete zero-knowledge provider configured",
        ),
        CapabilityProbe(
            capability="threshold_authorization",
            module="external-provider",
            available=False,
            production_accepted=False,
            detail="no concrete threshold-signature provider configured",
        ),
        CapabilityProbe(
            capability="program_obfuscation",
            module="external-provider",
            available=False,
            production_accepted=False,
            detail="general-purpose indistinguishability obfuscation is not enabled",
        ),
    ]
    return {
        "schema": "qso.crypto.capability-probe.v1",
        "ready_for_research": oqs,
        "ready_for_production": all(item.production_accepted for item in probes[:4]),
        "capabilities": [asdict(item) for item in probes],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe optional QSO cryptographic providers")
    parser.add_argument("--require-research-ready", action="store_true")
    parser.add_argument("--require-production-ready", action="store_true")
    args = parser.parse_args()
    report = probe_capabilities()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_production_ready and not report["ready_for_production"]:
        raise SystemExit(2)
    if args.require_research_ready and not report["ready_for_research"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
