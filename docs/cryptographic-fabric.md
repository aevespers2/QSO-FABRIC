# QSO Cryptographic Fabric

Status: `DOCUMENTED_NOT_CRYPTOGRAPHICALLY_APPROVED`

`qso_runtime.crypto_fabric` defines a bounded orchestration contract for combining:

1. a post-quantum key-encapsulation mechanism;
2. fully homomorphic encryption;
3. zero-knowledge proof generation and verification;
4. threshold authorization; and
5. optional program obfuscation.

The module is intentionally provider-neutral. It does **not** claim that a hash,
XOR transform, deterministic test double, ordinary symmetric cipher, provider
metadata flag, or passing unit test is FHE, post-quantum encryption, a
zero-knowledge proof, threshold authorization, or indistinguishability
obfuscation.

## Release pipeline

```text
QSO plaintext state
        |
        v
validate policy, request, context, providers, and approvals
        |
        v
Post-quantum KEM -----> bounded shared evaluation secret
        |
        v
FHE encrypt(input) -----> encrypted input
        |
        v
optional obfuscate(program)
        |
        v
FHE evaluate(ciphertext, program) -----> encrypted output
        |
        v
ZK prove + exact-Boolean verify of the bound statement
        |
        v
threshold authorize policy/context/provider/approval-bound transcript
        |
        v
versioned QSO execution envelope
```

Every required provider must be present before execution begins. Proof or
threshold verification failure aborts release. Production policy additionally
requires each provider to declare production status and an audit; this metadata
is only a fail-closed policy gate and is never evidence that an audit occurred.

## Transcript binding

The orchestration transcript binds the following before threshold authorization:

- the complete validated policy descriptor, not only its name;
- provider name, algorithm, version, security level, post-quantum declaration,
  and audit declaration;
- the request job identifier and bounded JSON context;
- the recipient public-key commitment;
- the source and effective program commitments;
- the KEM key identifier and ciphertext;
- encrypted input and output;
- the zero-knowledge proof; and
- distinct approval identities plus commitments to their approval bytes.

The execution envelope exposes the policy, context, source-program,
effective-program, and approval commitments needed to identify the exact
transcript generation. A commitment is a provenance and substitution-control
primitive; it is not an authorization decision or a proof that a provider is
cryptographically sound.

## Input and provider-output boundaries

The candidate fails closed on:

- non-enum security levels, truthy non-Boolean policy fields, and Boolean values
  supplied as integer thresholds or limits;
- malformed job identifiers, non-byte payloads, programs, or recipient keys;
- non-finite, non-JSON, over-deep, oversized, or non-string-keyed context data;
- duplicate, malformed, insufficient, or excessive threshold approvals;
- malformed KEM results, empty shared secrets, non-byte FHE, proof,
  certificate, or obfuscation outputs;
- oversized provider outputs; and
- truthy non-Boolean proof or authorization verification results.

These checks defend the orchestration boundary. They do not validate native
cryptographic memory handling, side-channel resistance, parameter selection,
proof-system soundness, trusted setup, key custody, or implementation audits.

## Provider contracts

Implement the protocols in `qso_runtime.crypto_fabric`:

- `KEMProvider`
- `FHEProvider`
- `ZeroKnowledgeProvider`
- `ThresholdProvider`
- `ObfuscationProvider`

Recommended concrete integration targets are:

| Capability | Candidate implementations | Notes |
|---|---|---|
| Post-quantum KEM | ML-KEM through a maintained FIPS 203 implementation | Pin versions and parameter sets; require known-answer tests. |
| FHE | OpenFHE, Microsoft SEAL, TFHE-rs, Concrete | Select BFV/BGV for exact arithmetic, CKKS for approximate arithmetic, or TFHE for Boolean/integer circuits. |
| Zero knowledge | Halo2, Plonky2, arkworks, gnark | Bind proofs to the exact program commitment, ciphertexts, policy, providers, approvals, and context. |
| Threshold authorization | FROST or threshold BLS/EdDSA implementation | Distinct participant identities and replay-resistant transcript binding are required. |
| Obfuscation | No general production recommendation | General-purpose iO remains unsuitable for ordinary deployment; keep disabled unless a reviewed specialized construction exists. |

## Security boundary

The orchestrator handles sequencing, commitments, transcript binding, policy
checks, type and resource boundaries, and evidence packaging. Cryptographic
correctness remains the responsibility of injected provider implementations and
their native libraries. Secrets must be held by provider-owned secure memory or
external key management; the orchestrator should receive opaque handles where
possible. The current Python proof-of-contract still passes a shared-secret byte
string between provider calls and is therefore **not** approved for production
secret custody.

## Minimal use

```python
from qso_runtime.crypto_fabric import CryptoPolicy, CryptoProviders, CryptographicFabric

policy = CryptoPolicy()
providers = CryptoProviders(
    kem=production_ml_kem_provider,
    fhe=production_fhe_provider,
    zero_knowledge=production_zk_provider,
    threshold=production_threshold_provider,
)
fabric = CryptographicFabric(policy, providers)
```

Construction fails immediately when a required provider is absent, not
post-quantum when required, malformed, unaudited in production mode, or marked
as a research implementation. Execution separately validates every request,
approval, and provider result.

## Required independent review

No default-branch or production disposition is appropriate until independent
review accepts at least:

- exact provider packages, versions, parameters, build provenance, licenses, and
  known-answer vectors;
- provider-specific serialization and cross-language fixtures;
- native-memory erasure, key-handle, side-channel, fault, and denial-of-service
  behavior;
- trusted-setup or ceremony requirements where applicable;
- threshold participant identity, issuance, revocation, recovery, and incident
  procedures;
- correction, withdrawal, migration, rollback, and restored-state evidence;
- privacy, retention, observability, accessibility, and operator procedures; and
- named security, cryptographic, release, and incident authorities.

## Next integration milestone

Add one provider package at a time behind disabled-by-default feature flags and
isolated CI matrices. Each provider must include known-answer vectors, negative
tests, serialization round-trips, resource bounds, exact dependency locks,
upstream provenance, independent review evidence, and a tested rollback path
before production policy can accept it.
