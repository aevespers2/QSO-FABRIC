from __future__ import annotations

"""Composable, fail-closed cryptographic orchestration for QSO Fabric.

This module deliberately separates orchestration from cryptographic providers.
It never substitutes hashes, XOR, or mock arithmetic for real encryption.
Production deployments must inject reviewed implementations of every required
capability (for example ML-KEM, FHE, ZK, and threshold authorization).
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable


class CryptoFabricError(RuntimeError):
    """Base error for cryptographic-fabric failures."""


class CapabilityUnavailable(CryptoFabricError):
    """Raised when a requested cryptographic capability is not configured."""


class VerificationFailure(CryptoFabricError):
    """Raised when cryptographic evidence fails verification."""


class SecurityLevel(str, Enum):
    RESEARCH = "research"
    PRODUCTION = "production"


@dataclass(frozen=True)
class CryptoPolicy:
    """Required capabilities and release rules for an encrypted QSO job."""

    policy_id: str = "QSO-CRYPTO-FABRIC-v1"
    security_level: SecurityLevel = SecurityLevel.PRODUCTION
    require_post_quantum_kem: bool = True
    require_fhe: bool = True
    require_zero_knowledge: bool = True
    require_threshold_authorization: bool = True
    require_obfuscated_program: bool = False
    threshold: int = 2
    participant_count: int = 3
    max_program_bytes: int = 65_536
    max_payload_bytes: int = 1_048_576

    def validate(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id must not be empty")
        if self.threshold < 1:
            raise ValueError("threshold must be positive")
        if self.participant_count < self.threshold:
            raise ValueError("participant_count must be at least threshold")
        if self.max_program_bytes < 1 or self.max_payload_bytes < 1:
            raise ValueError("size limits must be positive")


@dataclass(frozen=True)
class ProviderMetadata:
    name: str
    algorithm: str
    version: str
    security_level: SecurityLevel
    post_quantum: bool = False
    audited: bool = False


@dataclass(frozen=True)
class KEMResult:
    ciphertext: bytes
    shared_secret: bytes
    key_id: str


@dataclass(frozen=True)
class ThresholdApproval:
    participant_id: str
    approval: bytes


@dataclass(frozen=True)
class ExecutionRequest:
    job_id: str
    plaintext: bytes
    program: bytes
    recipient_public_key: bytes
    context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionEnvelope:
    schema: str
    job_id: str
    policy_id: str
    kem_ciphertext: bytes
    encrypted_input: bytes
    encrypted_output: bytes
    evaluation_proof: bytes
    authorization_certificate: bytes
    program_commitment: str
    transcript_hash: str
    providers: Mapping[str, ProviderMetadata]

    def to_jsonable(self) -> dict[str, Any]:
        value = asdict(self)
        for key in (
            "kem_ciphertext",
            "encrypted_input",
            "encrypted_output",
            "evaluation_proof",
            "authorization_certificate",
        ):
            value[key] = value[key].hex()
        return value


@runtime_checkable
class KEMProvider(Protocol):
    metadata: ProviderMetadata

    def encapsulate(self, recipient_public_key: bytes, context: bytes) -> KEMResult: ...


@runtime_checkable
class FHEProvider(Protocol):
    metadata: ProviderMetadata

    def encrypt(self, plaintext: bytes, shared_secret: bytes, context: bytes) -> bytes: ...

    def evaluate(self, encrypted_input: bytes, program: bytes, context: bytes) -> bytes: ...


@runtime_checkable
class ZeroKnowledgeProvider(Protocol):
    metadata: ProviderMetadata

    def prove(self, statement: bytes, witness: bytes, context: bytes) -> bytes: ...

    def verify(self, statement: bytes, proof: bytes, context: bytes) -> bool: ...


@runtime_checkable
class ThresholdProvider(Protocol):
    metadata: ProviderMetadata

    def authorize(
        self,
        transcript_hash: bytes,
        approvals: list[ThresholdApproval],
        threshold: int,
        participant_count: int,
    ) -> bytes: ...

    def verify_authorization(
        self,
        transcript_hash: bytes,
        certificate: bytes,
        threshold: int,
        participant_count: int,
    ) -> bool: ...


@runtime_checkable
class ObfuscationProvider(Protocol):
    metadata: ProviderMetadata

    def obfuscate(self, program: bytes, context: bytes) -> bytes: ...


@dataclass(frozen=True)
class CryptoProviders:
    kem: KEMProvider | None = None
    fhe: FHEProvider | None = None
    zero_knowledge: ZeroKnowledgeProvider | None = None
    threshold: ThresholdProvider | None = None
    obfuscation: ObfuscationProvider | None = None


class CryptographicFabric:
    """Coordinates cryptographic providers without implementing primitives itself."""

    def __init__(self, policy: CryptoPolicy, providers: CryptoProviders) -> None:
        policy.validate()
        self.policy = policy
        self.providers = providers
        self._validate_provider_set()

    def _validate_provider_set(self) -> None:
        required = {
            "kem": self.policy.require_post_quantum_kem,
            "fhe": self.policy.require_fhe,
            "zero_knowledge": self.policy.require_zero_knowledge,
            "threshold": self.policy.require_threshold_authorization,
            "obfuscation": self.policy.require_obfuscated_program,
        }
        for name, is_required in required.items():
            provider = getattr(self.providers, name)
            if is_required and provider is None:
                raise CapabilityUnavailable(f"required provider is unavailable: {name}")
            if provider is not None:
                self._validate_metadata(name, provider.metadata)

        kem = self.providers.kem
        if self.policy.require_post_quantum_kem and kem is not None and not kem.metadata.post_quantum:
            raise CapabilityUnavailable("configured KEM is not declared post-quantum")

    def _validate_metadata(self, capability: str, metadata: ProviderMetadata) -> None:
        if not metadata.name or not metadata.algorithm or not metadata.version:
            raise CapabilityUnavailable(f"{capability} provider metadata is incomplete")
        if self.policy.security_level is SecurityLevel.PRODUCTION:
            if metadata.security_level is not SecurityLevel.PRODUCTION:
                raise CapabilityUnavailable(f"{capability} provider is not production-grade")
            if not metadata.audited:
                raise CapabilityUnavailable(f"{capability} provider is not declared audited")

    @staticmethod
    def _canonical(value: Mapping[str, Any]) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    @staticmethod
    def _digest(*parts: bytes) -> bytes:
        h = hashlib.sha3_256()
        for part in parts:
            h.update(len(part).to_bytes(8, "big"))
            h.update(part)
        return h.digest()

    def execute(
        self,
        request: ExecutionRequest,
        approvals: list[ThresholdApproval],
    ) -> ExecutionEnvelope:
        if not request.job_id.strip():
            raise ValueError("job_id must not be empty")
        if not request.recipient_public_key:
            raise ValueError("recipient_public_key must not be empty")
        if len(request.plaintext) > self.policy.max_payload_bytes:
            raise ValueError("plaintext exceeds policy size limit")
        if len(request.program) > self.policy.max_program_bytes:
            raise ValueError("program exceeds policy size limit")

        context = self._canonical(
            {
                "schema": "qso.crypto.execution-context.v1",
                "job_id": request.job_id,
                "policy_id": self.policy.policy_id,
                "context": dict(request.context),
            }
        )

        kem = self._require("kem", self.providers.kem)
        fhe = self._require("fhe", self.providers.fhe)
        zk = self._require("zero_knowledge", self.providers.zero_knowledge)
        threshold = self._require("threshold", self.providers.threshold)

        program = request.program
        if self.policy.require_obfuscated_program:
            obfuscator = self._require("obfuscation", self.providers.obfuscation)
            program = obfuscator.obfuscate(program, context)

        program_commitment = hashlib.sha3_256(program).hexdigest()
        kem_result = kem.encapsulate(request.recipient_public_key, context)
        encrypted_input = fhe.encrypt(request.plaintext, kem_result.shared_secret, context)
        encrypted_output = fhe.evaluate(encrypted_input, program, context)

        statement = self._digest(
            context,
            kem_result.ciphertext,
            encrypted_input,
            encrypted_output,
            bytes.fromhex(program_commitment),
        )
        witness = self._digest(request.plaintext, kem_result.shared_secret, program)
        proof = zk.prove(statement, witness, context)
        if not zk.verify(statement, proof, context):
            raise VerificationFailure("zero-knowledge evaluation proof failed verification")

        transcript_hash = self._digest(statement, proof)
        certificate = threshold.authorize(
            transcript_hash,
            approvals,
            self.policy.threshold,
            self.policy.participant_count,
        )
        if not threshold.verify_authorization(
            transcript_hash,
            certificate,
            self.policy.threshold,
            self.policy.participant_count,
        ):
            raise VerificationFailure("threshold authorization failed verification")

        provider_map: dict[str, ProviderMetadata] = {
            "kem": kem.metadata,
            "fhe": fhe.metadata,
            "zero_knowledge": zk.metadata,
            "threshold": threshold.metadata,
        }
        if self.policy.require_obfuscated_program and self.providers.obfuscation is not None:
            provider_map["obfuscation"] = self.providers.obfuscation.metadata

        return ExecutionEnvelope(
            schema="qso.crypto.execution-envelope.v1",
            job_id=request.job_id,
            policy_id=self.policy.policy_id,
            kem_ciphertext=kem_result.ciphertext,
            encrypted_input=encrypted_input,
            encrypted_output=encrypted_output,
            evaluation_proof=proof,
            authorization_certificate=certificate,
            program_commitment=program_commitment,
            transcript_hash=transcript_hash.hex(),
            providers=provider_map,
        )

    @staticmethod
    def _require(name: str, provider: Any | None) -> Any:
        if provider is None:
            raise CapabilityUnavailable(f"required provider is unavailable: {name}")
        return provider
