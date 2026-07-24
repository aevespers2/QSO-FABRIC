# QSO Cryptographic Fabric

`qso_runtime.crypto_fabric` defines the bounded orchestration layer for combining:

1. a post-quantum key-encapsulation mechanism;
2. fully homomorphic encryption;
3. zero-knowledge proof generation and verification;
4. threshold authorization; and
5. optional program obfuscation.

The module is intentionally provider-neutral. It does **not** claim that a hash,
XOR transform, deterministic test double, or ordinary symmetric cipher is FHE,
post-quantum encryption, a zero-knowledge proof, or indistinguishability
obfuscation.

## Release pipeline

```text
QSO plaintext state
        |
        v
Post-quantum KEM -----> shared evaluation secret
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
ZK prove + verify evaluation statement
        |
        v
threshold authorize transcript
        |
        v
versioned QSO execution envelope
```

Every required provider must be present before execution begins. Proof or
threshold verification failure aborts release. Production policy additionally
requires each provider to declare production status and an audit; this metadata
is a policy gate, not a substitute for independent verification.

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
| Zero knowledge | Halo2, Plonky2, arkworks, gnark | Bind proofs to the exact program commitment, ciphertexts, policy, and context. |
| Threshold authorization | FROST or threshold BLS/EdDSA implementation | Distinct participant identities and replay-resistant transcript binding are required. |
| Obfuscation | No general production recommendation | General-purpose iO remains unsuitable for ordinary deployment; keep disabled unless a reviewed specialized construction exists. |

## Security boundary

The orchestrator handles sequencing, commitments, transcript binding, policy
checks, and evidence packaging. Cryptographic correctness remains the
responsibility of the injected provider implementations and their native
libraries. Secrets must be held by provider-owned secure memory or external key
management; the orchestrator should receive opaque handles where possible.

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
post-quantum when required, unaudited in production mode, or marked as a
research implementation.

## Next integration milestone

Add one provider package at a time behind feature flags and CI matrices. Each
provider must include known-answer vectors, negative tests, serialization
round-trips, resource bounds, exact dependency locks, and provenance for the
upstream implementation before production policy can accept it.
