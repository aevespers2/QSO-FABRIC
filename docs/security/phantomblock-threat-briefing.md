# PhantomBlock Threat Briefing and QSO Defensive Controls

**Status:** Defensive research note  
**Assessment:** `phantomblock` is an unverified threat label, not a confirmed exploit or attribution.  
**Scope:** Minecraft/Java-style hostile artifact paths and the controls required to prevent equivalent compromise in QSO-FABRIC.

## Executive assessment

A purported PhantomBlock campaign would most plausibly rely on a malicious mod, launcher, plugin, serialized packet, logging payload, script engine, world file, archive, or compromised update channel. The visible in-game object would be a trigger or delivery abstraction; the actual vulnerability would reside in software that interprets attacker-controlled data.

No terrorism attribution should be made without technical evidence. Preserve artifacts, hashes, logs, process ancestry, authentication records, network telemetry, and a reproducible trigger before escalating attribution.

## Principal intrusion paths

1. **Trojanized executable artifacts:** malicious `.jar`, launcher, plugin, mod, native library, or script.
2. **Unsafe deserialization:** arbitrary Java object reconstruction or equivalent dynamic object loading from network data.
3. **Logging/interpolation injection:** attacker-controlled strings reaching lookup-capable logging or template systems.
4. **Parser abuse:** oversized, deeply nested, compressed, recursive, malformed, duplicate-key, non-finite-number, or path-traversing content.
5. **Credential theft:** access to Microsoft, Discord, GitHub, hosting, SSH, cloud, browser, or CI credentials.
6. **Supply-chain compromise:** unsigned releases, mutable update endpoints, compromised maintainers, CI tokens, or dependencies.
7. **Capability escalation:** an analytical object obtains shell, process, package-installation, filesystem-write, wallet, credential, or unrestricted-network authority.

## QSO-FABRIC prevention model

QSO-FABRIC must remain a bounded analytical runtime. Untrusted content may be represented as text, metadata, and cryptographic hashes, but must never be executed, imported, dynamically loaded, unpacked, installed, or granted ambient authority.

An `accepted` artifact verdict is only a deterministic screening result. It is not malware clearance, authenticity proof, signer verification, or authorization to open, import, execute, unpack, or publish an artifact.

### Enforced invariants

- No shell or child-process spawning.
- No package installation or dynamic code loading.
- No credential, wallet, or browser-session access.
- No unrestricted network authority.
- No automatic extraction of compressed or archive artifacts.
- No executable or script artifacts accepted when identified by suffix, media type, shebang, or recognized executable/archive magic.
- No general-purpose object deserialization.
- Strict bounded UTF-8 JSON only, with duplicate-key, non-finite-number, depth, node, and byte rejection.
- Known lookup/interpolation patterns and unsafe control characters rejected before logging or reasoning.
- Capability requests are restricted to an explicit bounded analytical allowlist; denied, malformed, and unknown capability names fail closed.
- Artifact decisions are deterministic and include SHA-256 provenance.
- Security controls fail closed.

## Implemented controls

The module `qso_runtime.security_boundary` provides:

- `inspect_artifact`: rejects executable and archive suffixes, parameterized executable/archive media types, script shebangs, and common executable/archive magic bytes while producing a deterministic SHA-256 screening verdict.
- `safe_json_loads`: permits strict JSON only under configured byte, depth, node, duplicate-key, non-finite-number, and text limits.
- `sanitize_external_text`: normalizes line endings and rejects NULs, unsafe control characters, and lookup-style interpolation patterns without silently rewriting security-significant content.
- `enforce_capability_boundary`: permits only named bounded analytical capabilities and rejects denied, malformed, non-string, and unknown capability requests.
- `SecurityLimits`: validates a positive-integer bounded-input configuration.

## Operational response for suspected hostile artifacts

1. Do not open, import, install, execute, or unpack the object inside QSO-FABRIC.
2. Record the original filename, byte length, media type, acquisition source, timestamp, and SHA-256 hash.
3. Quarantine the original object in an external malware-analysis environment.
4. Rotate potentially exposed credentials from a clean system.
5. Hunt for Java or launcher processes spawning shells, interpreters, downloaders, or security-control changes.
6. Review repository releases, CI identities, dependency locks, update URLs, and signer provenance.
7. Treat attribution and ideological classification as separate investigative judgments requiring corroborating evidence.

## Required future hardening

- Signed artifact manifests and signer allowlists.
- Reproducible builds and dependency hash pinning.
- Immutable runtime images and read-only execution roots.
- Egress allowlists at the host/container boundary.
- External sandbox detonation for executable evidence.
- Coverage-guided fuzzing for all structured artifact parsers.
- SBOM generation and automated dependency vulnerability review.
- Centralized telemetry for denied capabilities and rejected artifacts.

## Security acceptance criteria

A release is not security-ready unless:

- hostile artifact tests pass;
- executable, script, and archive signals fail closed across suffix, media-type, and magic-byte paths;
- renamed archive and parameterized media-type bypass tests pass;
- lookup-injection and unsafe-control-character tests pass;
- JSON duplicate keys, non-finite values, depth, node, and size violations are rejected;
- malformed, denied, and unknown capabilities fail closed;
- invalid limit configurations are rejected;
- no QSO code path invokes a shell, package manager, dynamic loader, credential store, wallet, or unrestricted network client;
- hashes and rejection reasons remain deterministic under replay; and
- accepted screening verdicts are never represented as malware clearance or execution authorization.
