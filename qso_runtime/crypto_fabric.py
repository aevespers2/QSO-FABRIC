from __future__ import annotations

"""Composable, fail-closed cryptographic orchestration for QSO Fabric.

This module deliberately separates orchestration from cryptographic providers.
It never substitutes hashes, XOR, or mock arithmetic for real encryption.
Production deployments must inject reviewed implementations of every required
capability (for example ML-KEM, FHE, ZK, and threshold authorization).
"""

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

MAX_IDENTIFIER_CHARS = 128
MAX_PROVIDER_FIELD_CHARS = 128
MAX_CONTEXT_DEPTH = 8
MAX_CONTEXT_ITEMS = 256
MAX_CONTEXT_TEXT_CHARS = 4_096
MAX_CONTEXT_BYTES = 262_144
MAX_POLICY_BYTES = 67_108_864
MAX_RECIPIENT_KEY_BYTES = 65_536
MAX_SHARED_SECRET_BYTES = 4_096
MAX_APPROVAL_BYTES = 65_536
MAX_PROVIDER_OUTPUT_BYTES = 67_108_864
MAX_PARTICIPANTS = 1_024


class CryptoFabricError(RuntimeError):
    """Base error for cryptographic-fabric failures."""


class CapabilityUnavailable(CryptoFabricError):
    """Raised when a requested cryptographic capability is not configured."""


class VerificationFailure(CryptoFabricError):
    """Raised when cryptographic evidence fails verification."""


class SecurityLevel(str, Enum):
    RESEARCH = "research"
    PRODUCTION = "production"


def _require_text(value: object, *, label: str, max_length: int = MAX_IDENTIFIER_CHARS) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be non-empty and free of surrounding whitespace")
    if len(value) > max_length:
        raise ValueError(f"{label} exceeds {max_length} characters")
    return value


def _require_int(value: object, *, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def _require_bool(value: object, *, label: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{label} must be a boolean")
    return value


def _require_bytes(
    value: object,
    *,
    label: str,
    maximum: int,
    allow_empty: bool = False,
) -> bytes:
    if type(value) is not bytes:
        raise ValueError(f"{label} must be bytes")
    if not allow_empty and not value:
        raise ValueError(f"{label} must not be empty")
    if len(value) > maximum:
        raise ValueError(f"{label} exceeds {maximum} bytes")
    return value


def _normalize_json(value: object, *, label: str = "context", depth: int = 0) -> object:
    if depth > MAX_CONTEXT_DEPTH:
        raise ValueError(f"{label} exceeds the maximum nesting depth")
    if value is None or type(value) is bool:
        return value
    if type(value) is int:
        if not -(2**63) <= value <= 2**63 - 1:
            raise ValueError(f"{label} integer is outside the signed 64-bit range")
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{label} contains a non-finite number")
        return value
    if isinstance(value, str):
        if len(value) > MAX_CONTEXT_TEXT_CHARS:
            raise ValueError(f"{label} text exceeds {MAX_CONTEXT_TEXT_CHARS} characters")
        return value
    if isinstance(value, Mapping):
        if len(value) > MAX_CONTEXT_ITEMS:
            raise ValueError(f"{label} exceeds {MAX_CONTEXT_ITEMS} mapping entries")
        normalized: dict[str, object] = {}
        for key, item in value.items():
            key_text = _require_text(key, label=f"{label} key", max_length=MAX_IDENTIFIER_CHARS)
            normalized[key_text] = _normalize_json(item, label=f"{label}.{key_text}", depth=depth + 1)
        return normalized
    if isinstance(value, (list, tuple)):
        if len(value) > MAX_CONTEXT_ITEMS:
            raise ValueError(f"{label} exceeds {MAX_CONTEXT_ITEMS} sequence entries")
        return [_normalize_json(item, label=f"{label}[{index}]", depth=depth + 1) for index, item in enumerate(value)]
    raise ValueError(f"{label} contains a non-JSON value of type {type(value).__name__}")


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
        _require_text(self.policy_id, label="policy_id")
        if not isinstance(self.security_level, SecurityLevel):
            raise ValueError("security_level must be a SecurityLevel")
        for field_name in (
            "require_post_quantum_kem",
            "require_fhe",
            "require_zero_knowledge",
            "require_threshold_authorization",
            "require_obfuscated_program",
        ):
            _require_bool(getattr(self, field_name), label=field_name)
        threshold = _require_int(self.threshold, label="threshold", minimum=1, maximum=MAX_PARTICIPANTS)
        participant_count = _require_int(
            self.participant_count,
            label="participant_count",
            minimum=1,
            maximum=MAX_PARTICIPANTS,
        )
        if participant_count < threshold:
            raise ValueError("participant_count must be at least threshold")
        _require_int(self.max_program_bytes, label="max_program_bytes", minimum=1, maximum=MAX_POLICY_BYTES)
        _require_int(self.max_payload_bytes, label="max_payload_bytes", minimum=1, maximum=MAX_POLICY_BYTES)

    def descriptor(self) -> dict[str, object]:
        self.validate()
        return {
            "policy_id": self.policy_id,
            "security_level": self.security_level.value,
            "require_post_quantum_kem": self.require_post_quantum_kem,
            "require_fhe": self.require_fhe,
            "require_zero_knowledge": self.require_zero_knowledge,
            "require_threshold_authorization": self.require_threshold_authorization,
            "require_obfuscated_program": self.require_obfuscated_program,
            "threshold": self.threshold,
            "participant_count": self.participant_count,
            "max_program_bytes": self.max_program_bytes,
            "max_payload_bytes": self.max_payload_bytes,
        }


@dataclass(frozen=True)
class ProviderMetadata:
    name: str
    algorithm: str
    version: str
    security_level: SecurityLevel
    post_quantum: bool = False
    audited: bool = False

    def validate(self, *, capability: str) -> None:
        _require_text(self.name, label=f"{capability} provider name", max_length=MAX_PROVIDER_FIELD_CHARS)
        _require_text(self.algorithm, label=f"{capability} provider algorithm", max_length=MAX_PROVIDER_FIELD_CHARS)
        _require_text(self.version, label=f"{capability} provider version", max_length=MAX_PROVIDER_FIELD_CHARS)
        if not isinstance(self.security_level, SecurityLevel):
            raise CapabilityUnavailable(f"{capability} provider security_level is invalid")
        try:
            _require_bool(self.post_quantum, label=f"{capability} provider post_quantum")
            _require_bool(self.audited, label=f"{capability} provider audited")
        except ValueError as exc:
            raise CapabilityUnavailable(str(exc)) from exc

    def descriptor(self) -> dict[str, object]:
        return {
            "name": self.name,
            "algorithm": self.algorithm,
            "version": self.version,
            "security_level": self.security_level.value,
            "post_quantum": self.post_quantum,
            "audited": self.audited,
        }


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
    source_program_commitment: str
    program_commitment: str
    policy_commitment: str
    context_commitment: str
    approval_commitment: str
    kem_key_id: str
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
        value["providers"] = {name: metadata.descriptor() for name, metadata in self.providers.items()}
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
        if not isinstance(policy, CryptoPolicy):
            raise ValueError("policy must be a CryptoPolicy")
        if not isinstance(providers, CryptoProviders):
            raise ValueError("providers must be CryptoProviders")
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
                metadata = getattr(provider, "metadata", None)
                if not isinstance(metadata, ProviderMetadata):
                    raise CapabilityUnavailable(f"{name} provider metadata is missing or malformed")
                self._validate_metadata(name, metadata)

        kem = self.providers.kem
        if self.policy.require_post_quantum_kem and kem is not None and not kem.metadata.post_quantum:
            raise CapabilityUnavailable("configured KEM is not declared post-quantum")

    def _validate_metadata(self, capability: str, metadata: ProviderMetadata) -> None:
        metadata.validate(capability=capability)
        if self.policy.security_level is SecurityLevel.PRODUCTION:
            if metadata.security_level is not SecurityLevel.PRODUCTION:
                raise CapabilityUnavailable(f"{capability} provider is not production-grade")
            if metadata.audited is not True:
                raise CapabilityUnavailable(f"{capability} provider is not declared audited")

    @staticmethod
    def _canonical(value: Mapping[str, Any]) -> bytes:
        normalized = _normalize_json(value)
        encoded = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        if len(encoded) > MAX_CONTEXT_BYTES:
            raise ValueError(f"canonical context exceeds {MAX_CONTEXT_BYTES} bytes")
        return encoded

    @staticmethod
    def _digest(*parts: bytes) -> bytes:
        h = hashlib.sha3_256()
        for part in parts:
            h.update(len(part).to_bytes(8, "big"))
            h.update(part)
        return h.digest()

    def _provider_map(self) -> dict[str, ProviderMetadata]:
        provider_map: dict[str, ProviderMetadata] = {}
        for name in ("kem", "fhe", "zero_knowledge", "threshold", "obfuscation"):
            provider = getattr(self.providers, name)
            if provider is not None and (name != "obfuscation" or self.policy.require_obfuscated_program):
                provider_map[name] = provider.metadata
        return provider_map

    def _validate_request(self, request: ExecutionRequest) -> dict[str, object]:
        if not isinstance(request, ExecutionRequest):
            raise ValueError("request must be an ExecutionRequest")
        _require_text(request.job_id, label="job_id")
        _require_bytes(request.plaintext, label="plaintext", maximum=self.policy.max_payload_bytes, allow_empty=True)
        _require_bytes(request.program, label="program", maximum=self.policy.max_program_bytes)
        _require_bytes(
            request.recipient_public_key,
            label="recipient_public_key",
            maximum=MAX_RECIPIENT_KEY_BYTES,
        )
        if not isinstance(request.context, Mapping):
            raise ValueError("context must be a mapping")
        normalized_context = _normalize_json(request.context, label="context")
        if not isinstance(normalized_context, dict):
            raise ValueError("context must normalize to an object")
        return normalized_context

    def _validate_approvals(self, approvals: list[ThresholdApproval]) -> list[ThresholdApproval]:
        if type(approvals) is not list:
            raise ValueError("approvals must be a list")
        if len(approvals) < self.policy.threshold:
            raise VerificationFailure("insufficient distinct threshold approvals")
        if len(approvals) > self.policy.participant_count:
            raise VerificationFailure("approval count exceeds participant_count")
        participant_ids: set[str] = set()
        for index, approval in enumerate(approvals):
            if not isinstance(approval, ThresholdApproval):
                raise ValueError(f"approval {index} must be a ThresholdApproval")
            participant_id = _require_text(
                approval.participant_id,
                label=f"approval {index} participant_id",
            )
            _require_bytes(
                approval.approval,
                label=f"approval {index} bytes",
                maximum=MAX_APPROVAL_BYTES,
            )
            if participant_id in participant_ids:
                raise VerificationFailure("threshold approvals must use distinct participant identities")
            participant_ids.add(participant_id)
        return approvals

    def execute(
        self,
        request: ExecutionRequest,
        approvals: list[ThresholdApproval],
    ) -> ExecutionEnvelope:
        request_context = self._validate_request(request)
        approvals = self._validate_approvals(approvals)
        provider_map = self._provider_map()
        policy_descriptor = self.policy.descriptor()
        provider_descriptor = {name: metadata.descriptor() for name, metadata in provider_map.items()}
        source_program_commitment = hashlib.sha3_256(request.program).hexdigest()
        policy_bytes = self._canonical(policy_descriptor)
        policy_commitment = hashlib.sha3_256(policy_bytes).hexdigest()

        context = self._canonical(
            {
                "schema": "qso.crypto.execution-context.v1",
                "job_id": request.job_id,
                "policy": policy_descriptor,
                "providers": provider_descriptor,
                "recipient_public_key_sha3_256": hashlib.sha3_256(request.recipient_public_key).hexdigest(),
                "source_program_commitment": source_program_commitment,
                "context": request_context,
            }
        )
        context_commitment = hashlib.sha3_256(context).hexdigest()

        kem = self._require("kem", self.providers.kem)
        fhe = self._require("fhe", self.providers.fhe)
        zk = self._require("zero_knowledge", self.providers.zero_knowledge)
        threshold = self._require("threshold", self.providers.threshold)

        program = request.program
        if self.policy.require_obfuscated_program:
            obfuscator = self._require("obfuscation", self.providers.obfuscation)
            program = _require_bytes(
                obfuscator.obfuscate(program, context),
                label="obfuscated program",
                maximum=MAX_PROVIDER_OUTPUT_BYTES,
            )

        program_commitment = hashlib.sha3_256(program).hexdigest()
        kem_result = kem.encapsulate(request.recipient_public_key, context)
        if not isinstance(kem_result, KEMResult):
            raise VerificationFailure("KEM provider returned a malformed result")
        kem_ciphertext = _require_bytes(
            kem_result.ciphertext,
            label="KEM ciphertext",
            maximum=MAX_PROVIDER_OUTPUT_BYTES,
        )
        shared_secret = _require_bytes(
            kem_result.shared_secret,
            label="KEM shared_secret",
            maximum=MAX_SHARED_SECRET_BYTES,
        )
        kem_key_id = _require_text(kem_result.key_id, label="KEM key_id")

        encrypted_input = _require_bytes(
            fhe.encrypt(request.plaintext, shared_secret, context),
            label="FHE encrypted_input",
            maximum=MAX_PROVIDER_OUTPUT_BYTES,
        )
        encrypted_output = _require_bytes(
            fhe.evaluate(encrypted_input, program, context),
            label="FHE encrypted_output",
            maximum=MAX_PROVIDER_OUTPUT_BYTES,
        )

        statement = self._digest(
            bytes.fromhex(context_commitment),
            kem_key_id.encode("utf-8"),
            kem_ciphertext,
            encrypted_input,
            encrypted_output,
            bytes.fromhex(source_program_commitment),
            bytes.fromhex(program_commitment),
        )
        witness = self._digest(request.plaintext, shared_secret, request.program, program)
        proof = _require_bytes(
            zk.prove(statement, witness, context),
            label="zero-knowledge proof",
            maximum=MAX_PROVIDER_OUTPUT_BYTES,
        )
        proof_result = zk.verify(statement, proof, context)
        if type(proof_result) is not bool or not proof_result:
            raise VerificationFailure("zero-knowledge evaluation proof failed verification")

        approval_descriptor = [
            {
                "participant_id": approval.participant_id,
                "approval_sha3_256": hashlib.sha3_256(approval.approval).hexdigest(),
            }
            for approval in sorted(approvals, key=lambda item: item.participant_id)
        ]
        approval_bytes = self._canonical({"approvals": approval_descriptor})
        approval_commitment = hashlib.sha3_256(approval_bytes).hexdigest()
        transcript_hash = self._digest(statement, proof, bytes.fromhex(approval_commitment))

        certificate = _require_bytes(
            threshold.authorize(
                transcript_hash,
                approvals,
                self.policy.threshold,
                self.policy.participant_count,
            ),
            label="threshold authorization certificate",
            maximum=MAX_PROVIDER_OUTPUT_BYTES,
        )
        authorization_result = threshold.verify_authorization(
            transcript_hash,
            certificate,
            self.policy.threshold,
            self.policy.participant_count,
        )
        if type(authorization_result) is not bool or not authorization_result:
            raise VerificationFailure("threshold authorization failed verification")

        return ExecutionEnvelope(
            schema="qso.crypto.execution-envelope.v1",
            job_id=request.job_id,
            policy_id=self.policy.policy_id,
            kem_ciphertext=kem_ciphertext,
            encrypted_input=encrypted_input,
            encrypted_output=encrypted_output,
            evaluation_proof=proof,
            authorization_certificate=certificate,
            source_program_commitment=source_program_commitment,
            program_commitment=program_commitment,
            policy_commitment=policy_commitment,
            context_commitment=context_commitment,
            approval_commitment=approval_commitment,
            kem_key_id=kem_key_id,
            transcript_hash=transcript_hash.hex(),
            providers=provider_map,
        )

    @staticmethod
    def _require(name: str, provider: Any | None) -> Any:
        if provider is None:
            raise CapabilityUnavailable(f"required provider is unavailable: {name}")
        return provider
