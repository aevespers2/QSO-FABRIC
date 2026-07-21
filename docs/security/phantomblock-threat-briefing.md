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
4. **Parser abuse:** oversized, deeply nested, compressed, recursive, malformed, or path-traversing world/NBT/archive content.
5. **Credential theft:** access to Microsoft, Discord, GitHub, hosting, SSH, cloud, browser, or CI credentials.
6. **Supply-chain compromise:** unsigned releases, mutable update endpoints, compromised maintainers, CI tokens, or dependencies.
7. **Capability escalation:** an analytical object obtains shell, process, package-installation, filesystem-write, wallet, credential, or unrestricted-network authority.

## QSO-FABRIC prevention model

QSO-FABRIC must remain a bounded analytical runtime. Untrusted content may be represented as text, metadata, and cryptographic hashes, but must never be executed, imported, dynamically loaded, unpacked, installed, or granted ambient authority.

### Enforced invariants

- No shell or child-process spawning.
- No package installation or dynamic code loading.
- No credential, wallet, or browser-session access.
- No unrestricted network authority.
- No automatic extraction of compressed or archive artifacts.
- No executable or script artifacts accepted into the runtime.
- No general-purpose object deserialization.
- Bounded UTF-8 JSON only, with depth, node, and byte ceilings.
- Known lookup/interpolation patterns rejected before logging or reasoning.
- Artifact decisions are deterministic and include SHA-256 provenance.
- Security controls fail closed.

## Implemented controls

The module `qso_runtime.security_boundary` provides:

- `inspect_artifact`: rejects executable suffixes, archive suffixes, executable media types, and common executable/archive magic bytes while producing a deterministic SHA-256 verdict.
- `safe_json_loads`: permits JSON only under configured byte, depth, node, and text limits.
- `sanitize_external_text`: rejects NUL bytes and lookup-style interpolation patterns and strips unsafe control characters.
- `enforce_capability_boundary`: blocks requests for shell, process spawning, dynamic loading, package installation, filesystem writes, credentials, wallets, and unrestricted networking.
- `SecurityLimits`: central bounded-input configuration.

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
- executable and archive inputs fail closed;
- lookup-injection tests pass;
- JSON depth and size limits are enforced;
- denied capabilities cannot be requested indirectly;
- no QSO code path invokes a shell, package manager, dynamic loader, credential store, wallet, or unrestricted network client;
- hashes and rejection reasons remain deterministic under replay.
