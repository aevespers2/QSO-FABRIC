from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import math
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


class MalformedKEM(TestKEM):
    def encapsulate(self, recipient_public_key: bytes, context: bytes):
        return {"ciphertext": b"not-a-result"}


class EmptySecretKEM(TestKEM):
    def encapsulate(self, recipient_public_key: bytes, context: bytes) -> KEMResult:
        return KEMResult(b"ciphertext", b"", "test-key")


class TestFHE:
    metadata = RESEARCH

    def encrypt(self, plaintext: bytes, shared_secret: bytes, context: bytes) -> bytes:
        return b"ENC:" + digest(shared_secret, context) + plaintext

    def evaluate(self, encrypted_input: bytes, program: bytes, context: bytes) -> bytes:
        return b"EVAL:" + digest(encrypted_input, program, context)


class MalformedFHE(TestFHE):
    def evaluate(self, encrypted_input: bytes, program: bytes, context: bytes):
        return "not-bytes"


class TestZK:
    metadata = RESEARCH

    def prove(self, statement: bytes, witness: bytes, context: bytes) -> bytes:
        return hmac.new(digest(witness, context), statement, hashlib.sha3_256).digest()

    def verify(self, statement: bytes, proof: bytes, context: bytes) -> bool:
        return len(statement) == 32 and len(proof) == 32 and bool(context)


class RejectingZK(TestZK):
    def verify(self, statement: bytes, proof: bytes, context: bytes) -> bool:
        return False


class TruthyZK(TestZK):
    def verify(self, statement: bytes, proof: bytes, context: bytes):
        return 1


class TestThreshold:
    metadata = RESEARCH

    def authorize(self, transcript_hash, approvals, threshold, participant_count):
        unique = {approval.participant_id for approval in approvals}
        if len(unique) < threshold:
            return b""
        return b"CERT:" + digest(transcript_hash, ",".join(sorted(unique)).encode())

    def verify_authorization(self, transcript_hash, certificate, threshold, participant_count):
        return certificate.startswith(b"CERT:") and len(certificate) == 37


class TruthyThreshold(TestThreshold):
    def verify_authorization(self, transcript_hash, certificate, threshold, participant_count):
        return "yes"


class TestObfuscator:
    metadata = RESEARCH

    def obfuscate(self, program: bytes, context: bytes) -> bytes:
        return b"OBF:" + digest(program, context)


class CryptoFabricTests(unittest.TestCase):
    def providers(self, *, kem=None, fhe=None, zk=None, threshold=None):
        return CryptoProviders(
            kem=kem or TestKEM(),
            fhe=fhe or TestFHE(),
            zero_knowledge=zk or TestZK(),
            threshold=threshold or TestThreshold(),
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

    def request(self, **changes):
        values = {
            "job_id": "job-001",
            "plaintext": b"private qso state",
            "program": b"aggregate(state)",
            "recipient_public_key": b"recipient-key",
            "context": {"qso": "atlas", "purpose": "bounded-evaluation"},
        }
        values.update(changes)
        return ExecutionRequest(**values)

    def approvals(self, **changes):
        approvals = [
            ThresholdApproval("nova", b"approval-1"),
            ThresholdApproval("orion", b"approval-2"),
        ]
        return [replace(approval, **changes) for approval in approvals]

    def test_executes_complete_pipeline(self):
        fabric = CryptographicFabric(self.policy(), self.providers())
        envelope = fabric.execute(self.request(), self.approvals())
        self.assertEqual("qso.crypto.execution-envelope.v1", envelope.schema)
        self.assertEqual("job-001", envelope.job_id)
        self.assertEqual(64, len(envelope.transcript_hash))
        self.assertEqual(64, len(envelope.policy_commitment))
        self.assertEqual(64, len(envelope.context_commitment))
        self.assertEqual(64, len(envelope.approval_commitment))
        self.assertEqual("test-key", envelope.kem_key_id)
        self.assertIn("obfuscation", envelope.providers)
        self.assertTrue(envelope.authorization_certificate.startswith(b"CERT:"))
        jsonable = envelope.to_jsonable()
        self.assertEqual(jsonable["encrypted_output"], envelope.encrypted_output.hex())
        self.assertEqual("research", jsonable["providers"]["kem"]["security_level"])

    def test_missing_required_provider_fails_closed(self):
        with self.assertRaises(CapabilityUnavailable):
            CryptographicFabric(self.policy(), CryptoProviders(kem=TestKEM()))

    def test_production_rejects_research_provider(self):
        with self.assertRaises(CapabilityUnavailable):
            CryptographicFabric(CryptoPolicy(), self.providers())

    def test_rejected_proof_stops_release(self):
        fabric = CryptographicFabric(self.policy(), self.providers(zk=RejectingZK()))
        with self.assertRaises(VerificationFailure):
            fabric.execute(self.request(), self.approvals())

    def test_truthy_non_boolean_verification_is_rejected(self):
        with self.assertRaises(VerificationFailure):
            CryptographicFabric(self.policy(), self.providers(zk=TruthyZK())).execute(
                self.request(), self.approvals()
            )
        with self.assertRaises(VerificationFailure):
            CryptographicFabric(
                self.policy(), self.providers(threshold=TruthyThreshold())
            ).execute(self.request(), self.approvals())

    def test_insufficient_or_duplicate_threshold_stops_release(self):
        fabric = CryptographicFabric(self.policy(), self.providers())
        with self.assertRaises(VerificationFailure):
            fabric.execute(self.request(), [ThresholdApproval("nova", b"one")])
        with self.assertRaises(VerificationFailure):
            fabric.execute(
                self.request(),
                [ThresholdApproval("nova", b"one"), ThresholdApproval("nova", b"two")],
            )

    def test_payload_limit_is_enforced(self):
        fabric = CryptographicFabric(self.policy(max_payload_bytes=2), self.providers())
        with self.assertRaises(ValueError):
            fabric.execute(self.request(), self.approvals())

    def test_policy_types_fail_closed(self):
        invalid = (
            {"security_level": "production"},
            {"threshold": True},
            {"participant_count": False},
            {"require_fhe": 1},
            {"max_payload_bytes": True},
            {"max_program_bytes": 0},
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                CryptographicFabric(CryptoPolicy(**changes), self.providers())

    def test_provider_metadata_types_fail_closed(self):
        malformed = ProviderMetadata(
            name="provider",
            algorithm="algorithm",
            version="1",
            security_level="production",  # type: ignore[arg-type]
            post_quantum=True,
            audited=True,
        )
        provider = TestKEM()
        provider.metadata = malformed
        with self.assertRaises(CapabilityUnavailable):
            CryptographicFabric(self.policy(), self.providers(kem=provider))

    def test_request_types_and_context_fail_closed(self):
        invalid_requests = (
            self.request(job_id=7),
            self.request(plaintext="not-bytes"),
            self.request(program=b""),
            self.request(recipient_public_key=bytearray(b"key")),
            self.request(context={"score": math.nan}),
            self.request(context={"payload": object()}),
            self.request(context={1: "non-string-key"}),
        )
        fabric = CryptographicFabric(self.policy(), self.providers())
        for request in invalid_requests:
            with self.subTest(request=request), self.assertRaises(ValueError):
                fabric.execute(request, self.approvals())

    def test_malformed_provider_outputs_fail_closed(self):
        with self.assertRaises(VerificationFailure):
            CryptographicFabric(self.policy(), self.providers(kem=MalformedKEM())).execute(
                self.request(), self.approvals()
            )
        with self.assertRaises(ValueError):
            CryptographicFabric(self.policy(), self.providers(kem=EmptySecretKEM())).execute(
                self.request(), self.approvals()
            )
        with self.assertRaises(ValueError):
            CryptographicFabric(self.policy(), self.providers(fhe=MalformedFHE())).execute(
                self.request(), self.approvals()
            )

    def test_policy_request_and_approvals_are_transcript_bound(self):
        base = CryptographicFabric(self.policy(), self.providers()).execute(
            self.request(), self.approvals()
        )
        policy_change = CryptographicFabric(
            self.policy(threshold=1), self.providers()
        ).execute(self.request(), self.approvals())
        recipient_change = CryptographicFabric(self.policy(), self.providers()).execute(
            self.request(recipient_public_key=b"other-key"), self.approvals()
        )
        approval_change = CryptographicFabric(self.policy(), self.providers()).execute(
            self.request(),
            [ThresholdApproval("nova", b"changed"), ThresholdApproval("orion", b"approval-2")],
        )
        self.assertNotEqual(base.policy_commitment, policy_change.policy_commitment)
        self.assertNotEqual(base.transcript_hash, policy_change.transcript_hash)
        self.assertNotEqual(base.context_commitment, recipient_change.context_commitment)
        self.assertNotEqual(base.transcript_hash, recipient_change.transcript_hash)
        self.assertNotEqual(base.approval_commitment, approval_change.approval_commitment)
        self.assertNotEqual(base.transcript_hash, approval_change.transcript_hash)


if __name__ == "__main__":
    unittest.main()
