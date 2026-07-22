# QSO Format Security

## Security posture

The QSO format subsystem treats every object, registry, package, stream, conversion source, reference, and signature as untrusted until the exact applicable checks succeed. Validation remains separate from execution and authority.

The current branch contains development safeguards and hostile fixtures. It has not completed independent security review and is not a production trust root.

## Threat model

The subsystem must defend against:

- malformed or ambiguous UTF-8 and JSON;
- duplicate keys, non-finite numbers, type confusion, and oversized structures;
- unsupported or downgraded format, schema, profile, algorithm, and extension versions;
- identifier collisions and reference substitution;
- stale, replayed, superseded, corrected, or revoked records;
- forged or unauthorized signatures;
- content-hash, manifest, package-member, and registry drift;
- path traversal, absolute paths, drive-qualified names, case-fold collisions, symlinks, special files, encryption, unsupported compression, and decompression bombs;
- polyglot or nested archives that bypass the selected policy;
- conversion that discards source evidence or invents authority;
- capability, governance, or mutation records being treated as self-executing;
- privacy, credential, key, biometric, or sensitive incident data entering public artifacts;
- partial writes, interrupted extraction, inconsistent retries, and rollback failure; and
- a compromised validator, registry, build, dependency, or workflow producing misleading success.

## Security invariants

1. Parse strict UTF-8 and reject duplicate keys and non-finite values.
2. Apply explicit byte, nesting, member, aggregate, and execution-time limits.
3. Reject unknown critical fields and unsupported major versions.
4. Bind every reference to identity, type, version, and expected digest.
5. Validate complete package structure before creating the extraction destination.
6. Never execute embedded resources during schema, package, conversion, or signature validation.
7. Separate signature validity from signer authorization and current trust.
8. Separate mutation description from mutation capability.
9. Separate successful conversion from source authenticity and admission.
10. Preserve source, correction, revocation, supersession, and rollback evidence.
11. Fail closed when ownership, privacy, licensing, freshness, replay, or recovery state is unknown.
12. Treat CI success as evidence for one immutable source, not as production approval.

## Package controls

The current package boundary is designed to:

- sort deterministic members;
- normalize timestamps and permissions;
- reject source symlinks and output paths inside the source tree;
- bind every member path, byte size, media type, and SHA-256 digest in a manifest;
- preflight the complete central directory;
- reject unsafe paths and member types;
- stream decompression through member and aggregate ceilings;
- compare archive and manifest sets, sizes, media types, and digests; and
- extract manually only to a safe, empty destination.

Remaining package-security work includes nested archive policy, polyglot detection, signed manifests, authenticated signer policy, storage-race hardening, filesystem-specific path behavior, complete fuzzing, SBOMs, and independent assessment.

## Conversion controls

Converters must preserve source bytes and emit separate lineage. They must not:

- infer source truth from parse success;
- treat source-declared ledger validity as independent verification;
- invent trusted time;
- overwrite or delete source artifacts;
- collapse source and derived identities;
- silently perform lossy mapping; or
- promote representation migration into runtime, policy, or authority acceptance.

See [`CONVERSION-BOUNDARY.md`](CONVERSION-BOUNDARY.md).

## Signature and key-custody boundary

A valid cryptographic signature proves only that the corresponding key signed the defined bytes under the declared algorithm and domain. Production acceptance also requires:

- approved signer identity and role;
- protected key generation, storage, use, rotation, recovery, and revocation;
- trusted or uncertainty-aware time;
- algorithm and parameter policy;
- domain separation by contract, version, environment, and purpose;
- replay and supersession handling;
- independent verification; and
- incident and compromise response.

The current validator does not provide that complete chain.

## Workflow and supply-chain controls

Documentation and CI should:

- pin Actions and dependencies to reviewed immutable versions;
- use read-only permissions unless a separate approved operation requires more;
- disable persisted checkout credentials;
- assert the exact submitted source and clean worktree;
- retain commands, tool versions, tests, fixtures, hashes, failures, and artifacts;
- scan generated and public outputs for secrets and sensitive fields;
- fail the final gate when any required check is absent or inconclusive; and
- avoid publishing directly from an unreconciled branch.

## Incident response

Freeze affected format admission, conversion, packaging, publication, or mutation when:

- a registry or canonicalization generation is disputed;
- a signature key or workflow credential may be compromised;
- a package bypass or path-safety defect is found;
- source or derived identities collide;
- correction or revocation fails to propagate;
- outputs expose restricted data;
- evidence cannot be reproduced; or
- PR #15 and PR #19 disagree on a security-critical boundary.

Preserve exact inputs, outputs, logs, commits, tool versions, registry generations, affected consumers, and rollback points. Emergency suspension is not permanent revocation; restart requires independent verification and explicit approval.

## Security review gates

Production consideration requires:

- complete schema and reference resolution;
- cross-language canonicalization and hostile vectors;
- detached signature and key-custody design;
- fuzzing and archive-security review;
- privacy, retention, licensing, and public-output review;
- correction, revocation, replay, rollback, and recovery exercises;
- SBOM and reproducible-build evidence;
- independent security review; and
- named incident, revocation, recovery, release, and deployment owners.

## Non-authority statement

Security validation reduces specific risks at one exact source. It does not make an object true, appoint a steward, authorize a mutation, issue a capability, accept canonical state, or approve release or deployment.