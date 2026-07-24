from __future__ import annotations

"""ML-KEM adapter backed by the optional ``oqs`` Python package.

The Open Quantum Safe project describes liboqs as a prototyping/evaluation
library. This provider therefore declares RESEARCH status by default and cannot
satisfy QSO Fabric production policy unless a downstream deployment explicitly
subclasses it with independently justified metadata.
"""

import hashlib
import hmac
import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from ..crypto_fabric import KEMResult, ProviderMetadata, SecurityLevel


class OQSUnavailable(RuntimeError):
    """Raised when liboqs-python is missing or does not expose the requested KEM."""


@dataclass(frozen=True)
class OQSKEMKeypair:
    mechanism: str
    public_key: bytes
    secret_key: bytes


class OQSKEMProvider:
    """Context-bound ML-KEM encapsulation using liboqs-python.

    ``context`` is mixed into the raw KEM shared secret using an extract/expand
    construction based on HMAC-SHA3-256. This prevents the same raw shared
    secret from being reused across QSO protocol contexts.
    """

    DEFAULT_MECHANISM = "ML-KEM-768"

    def __init__(
        self,
        mechanism: str = DEFAULT_MECHANISM,
        *,
        oqs_module: ModuleType | Any | None = None,
    ) -> None:
        self.mechanism = mechanism
        self._oqs = oqs_module or self._load_oqs()
        enabled = set(self._oqs.get_enabled_kem_mechanisms())
        if mechanism not in enabled:
            raise OQSUnavailable(f"KEM mechanism is not enabled in liboqs: {mechanism}")
        version = str(getattr(self._oqs, "oqs_version", lambda: "unknown")())
        self.metadata = ProviderMetadata(
            name="liboqs-python",
            algorithm=mechanism,
            version=version,
            security_level=SecurityLevel.RESEARCH,
            post_quantum=True,
            audited=False,
        )

    @staticmethod
    def _load_oqs() -> ModuleType:
        try:
            return importlib.import_module("oqs")
        except ImportError as exc:
            raise OQSUnavailable(
                "liboqs-python is not installed; install and verify liboqs/oqs before enabling this provider"
            ) from exc

    @staticmethod
    def _derive_context_key(raw_secret: bytes, context: bytes) -> bytes:
        if not raw_secret:
            raise ValueError("raw KEM secret must not be empty")
        salt = hashlib.sha3_256(b"QSO-CRYPTO-FABRIC-v1/context-kem" + context).digest()
        pseudorandom_key = hmac.new(salt, raw_secret, hashlib.sha3_256).digest()
        return hmac.new(
            pseudorandom_key,
            b"qso/ml-kem/session-key\x01",
            hashlib.sha3_256,
        ).digest()

    @staticmethod
    def _key_id(public_key: bytes) -> str:
        return hashlib.sha3_256(public_key).hexdigest()[:32]

    def encapsulate(self, recipient_public_key: bytes, context: bytes) -> KEMResult:
        if not recipient_public_key:
            raise ValueError("recipient_public_key must not be empty")
        with self._oqs.KeyEncapsulation(self.mechanism) as kem:
            ciphertext, raw_secret = kem.encap_secret(recipient_public_key)
        return KEMResult(
            ciphertext=bytes(ciphertext),
            shared_secret=self._derive_context_key(bytes(raw_secret), context),
            key_id=self._key_id(recipient_public_key),
        )

    def generate_keypair(self) -> OQSKEMKeypair:
        """Generate a recipient keypair for provisioning or integration tests."""
        with self._oqs.KeyEncapsulation(self.mechanism) as kem:
            public_key = bytes(kem.generate_keypair())
            secret_key = bytes(kem.export_secret_key())
        return OQSKEMKeypair(self.mechanism, public_key, secret_key)

    def decapsulate(self, secret_key: bytes, ciphertext: bytes, context: bytes) -> bytes:
        """Recover the same context-bound session key on the recipient side."""
        if not secret_key or not ciphertext:
            raise ValueError("secret_key and ciphertext must not be empty")
        with self._oqs.KeyEncapsulation(self.mechanism, secret_key) as kem:
            raw_secret = kem.decap_secret(ciphertext)
        return self._derive_context_key(bytes(raw_secret), context)
