from __future__ import annotations

import hashlib
import hmac
import unittest

from qso_runtime.crypto_fabric import (
    CapabilityUnavailable,
    CryptoPolicy,
    CryptoProviders,
    CryptographicFabric,
    ExecutionRequest,
    KEMResult,
    ProviderMetadata,
    SecurityLevel,
    ThresholdApproval,
    VerificationFailure,
)


RESEARCH = ProviderMetadata(
    name="deterministic-test-provider",
    algorithm="TEST-ONLY",
    version="1",
    security_level=SecurityLevel.RESEARCH,
    post_quantum=True,
    audited=False,
)


def digest(*parts: bytes) -> bytes:
    h = hashlib.sha3_256()
    for part in parts:
        h.update(part)
    return h.digest()


class TestKEM:
    metadata = RESEARCH

    def encapsulate(self, recipient_public_key: bytes, context: bytes) -> KEMResult:
        secret = digest(b"secret", recipient_public_key, context)
        return KEMResult(digest(b"kem", secret), secret, "test-key")


class TestFHE:
    metadata = RESEARCH

    def encrypt(self, plaintext: bytes, shared_secret: bytes, context: bytes) -> bytes:
        return b"ENC:" + digest(shared_secret, context) + plaintext

    def evaluate(self, encrypted_input: bytes, program: bytes, context: bytes) -> bytes:
        return b"EVAL:" + digest(encrypted_input, program, context)


class TestZK:
    metadata = RESEARCH

    def prove(self, statement: bytes, witness: bytes, context: bytes) -> bytes:
        return hmac.new(digest(witness, context), statement, hashlib.sha3_256).digest()

    def verify(self, statement: bytes, proof: bytes, context: bytes) -> bool:
        return len(statement) == 32 and len(proof) == 32 and bool(context)


class RejectingZK(TestZK):
    def verify(self, statement: bytes, proof: bytes, context: bytes) -> bool:
        return False


class TestThreshold:
    metadata = RESEARCH

    def authorize(self, transcript_hash, approvals, threshold, participant_count):
        unique = {approval.participant_id for approval in approvals}
        if len(unique) < threshold:
            return b""
        return b"CERT:" + digest(transcript_hash, ",".join(sorted(unique)).encode())

    def verify_authorization(self, transcript_hash, certificate, threshold, participant_count):
        return certificate.startswith(b"CERT:") and len(certificate) == 37


class TestObfuscator:
    metadata = RESEARCH

    def obfuscate(self, program: bytes, context: bytes) -> bytes:
        return b"OBF:" + digest(program, context)


class CryptoFabricTests(unittest.TestCase):
    def providers(self, zk=None):
        return CryptoProviders(
            kem=TestKEM(),
            fhe=TestFHE(),
            zero_knowledge=zk or TestZK(),
            threshold=TestThreshold(),
            obfuscation=TestObfuscator(),
        )

    def policy(self, **changes):
        values = {
            "security_level": SecurityLevel.RESEARCH,
            "require_obfuscated_program": True,
            "threshold": 2,
            "participant_count": 3,
        }
        values.update(changes)
        return CryptoPolicy(**values)

    def request(self):
        return ExecutionRequest(
            job_id="job-001",
            plaintext=b"private qso state",
            program=b"aggregate(state)",
            recipient_public_key=b"recipient-key",
            context={"qso": "atlas", "purpose": "bounded-evaluation"},
        )

    def approvals(self):
        return [
            ThresholdApproval("nova", b"approval-1"),
            ThresholdApproval("orion", b"approval-2"),
        ]

    def test_executes_complete_pipeline(self):
        fabric = CryptographicFabric(self.policy(), self.providers())
        envelope = fabric.execute(self.request(), self.approvals())
        self.assertEqual("qso.crypto.execution-envelope.v1", envelope.schema)
        self.assertEqual("job-001", envelope.job_id)
        self.assertEqual(64, len(envelope.transcript_hash))
        self.assertIn("obfuscation", envelope.providers)
        self.assertTrue(envelope.authorization_certificate.startswith(b"CERT:"))
        self.assertEqual(envelope.to_jsonable()["encrypted_output"], envelope.encrypted_output.hex())

    def test_missing_required_provider_fails_closed(self):
        with self.assertRaises(CapabilityUnavailable):
            CryptographicFabric(self.policy(), CryptoProviders(kem=TestKEM()))

    def test_production_rejects_research_provider(self):
        with self.assertRaises(CapabilityUnavailable):
            CryptographicFabric(CryptoPolicy(), self.providers())

    def test_rejected_proof_stops_release(self):
        fabric = CryptographicFabric(self.policy(), self.providers(RejectingZK()))
        with self.assertRaises(VerificationFailure):
            fabric.execute(self.request(), self.approvals())

    def test_insufficient_threshold_stops_release(self):
        fabric = CryptographicFabric(self.policy(), self.providers())
        with self.assertRaises(VerificationFailure):
            fabric.execute(self.request(), [ThresholdApproval("nova", b"one")])

    def test_payload_limit_is_enforced(self):
        fabric = CryptographicFabric(self.policy(max_payload_bytes=2), self.providers())
        with self.assertRaises(ValueError):
            fabric.execute(self.request(), self.approvals())


if __name__ == "__main__":
    unittest.main()
