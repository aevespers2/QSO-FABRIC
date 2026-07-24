from __future__ import annotations

import hashlib
import unittest

from qso_runtime.crypto_fabric import SecurityLevel
from qso_runtime.providers.oqs_kem import OQSKEMProvider, OQSUnavailable


class FakeKEM:
    def __init__(self, mechanism: str, secret_key: bytes | None = None) -> None:
        self.mechanism = mechanism
        self.secret_key = secret_key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def generate_keypair(self):
        self.secret_key = b"secret-key"
        return b"public-key"

    def export_secret_key(self):
        return self.secret_key

    def encap_secret(self, public_key: bytes):
        raw = hashlib.sha3_256(b"shared:" + public_key).digest()
        return b"ciphertext:" + public_key, raw

    def decap_secret(self, ciphertext: bytes):
        public_key = ciphertext.removeprefix(b"ciphertext:")
        return hashlib.sha3_256(b"shared:" + public_key).digest()


class FakeOQS:
    KeyEncapsulation = FakeKEM

    @staticmethod
    def get_enabled_kem_mechanisms():
        return ["ML-KEM-768"]

    @staticmethod
    def oqs_version():
        return "test-0.0"


class OQSKEMProviderTests(unittest.TestCase):
    def test_keypair_encapsulation_and_decapsulation_match(self):
        provider = OQSKEMProvider(oqs_module=FakeOQS())
        keypair = provider.generate_keypair()
        context = b"qso-context"
        result = provider.encapsulate(keypair.public_key, context)
        recovered = provider.decapsulate(keypair.secret_key, result.ciphertext, context)
        self.assertEqual(result.shared_secret, recovered)
        self.assertEqual("ML-KEM-768", keypair.mechanism)
        self.assertEqual(32, len(result.shared_secret))
        self.assertEqual(32, len(result.key_id))

    def test_context_separates_session_keys(self):
        provider = OQSKEMProvider(oqs_module=FakeOQS())
        first = provider.encapsulate(b"public-key", b"context-a")
        second = provider.encapsulate(b"public-key", b"context-b")
        self.assertNotEqual(first.shared_secret, second.shared_secret)

    def test_metadata_remains_research_grade(self):
        provider = OQSKEMProvider(oqs_module=FakeOQS())
        self.assertEqual(SecurityLevel.RESEARCH, provider.metadata.security_level)
        self.assertTrue(provider.metadata.post_quantum)
        self.assertFalse(provider.metadata.audited)

    def test_disabled_mechanism_fails_closed(self):
        with self.assertRaises(OQSUnavailable):
            OQSKEMProvider("ML-KEM-1024", oqs_module=FakeOQS())

    def test_empty_decapsulation_values_rejected(self):
        provider = OQSKEMProvider(oqs_module=FakeOQS())
        with self.assertRaises(ValueError):
            provider.decapsulate(b"", b"ciphertext", b"context")


if __name__ == "__main__":
    unittest.main()
