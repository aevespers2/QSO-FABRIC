# QSO Format Roadmap

## Roadmap principles

The roadmap advances conformance and safety before capability. Version labels are planning targets, not promises or release designations. No phase becomes accepted because files or tests exist; each phase requires repository-local review, immutable evidence, and the applicable architecture, security, licensing, and release decisions.

## Current state — implementation candidate

PR #19 implements a broad 0.1 development surface: envelope and family schemas, registries, profiles, reference tools, deterministic packaging controls, migration hooks, compatibility conversions, examples, tests, and CI.

Before this work can be called a release candidate, it must be reconciled with PR #15's project overview, architecture, ownership, onboarding, release, and rollback model.

## 0.1 — bounded development profile

### Implemented candidate surfaces

- common envelope and QSO-CORE composition references;
- initial family schemas and registries;
- JSON authoring canonicalization and SHA-256 content addressing;
- bounded package creation and preflight extraction;
- profiles, examples, reference tools, conversions, tests, and CI;
- source-preserving four-QSO report conversion; and
- hostile package fixtures and deterministic round-trip checks.

### Required before 0.1 release consideration

- reconcile PR #15 and PR #19 at one immutable resulting head;
- define repository versus neutral format ownership;
- close documentation, task-chain, release-plan, and changelog contradictions;
- add complete source-schema validation and strict duplicate-key handling to conversion input;
- publish exact canonicalization vectors and limits;
- complete package, conversion, interruption, retry, and rollback evidence;
- approve license, package identity, supported Python versions, and support/security routes;
- retain exact-head build, test, security, documentation, and artifact evidence; and
- obtain explicit human release disposition.

## 0.2 — conformance and security hardening

Planned work:

- complete family schemas and reference resolution;
- cross-language RFC 8785-style vectors or an explicitly selected alternative;
- bounded canonicalization and parser limits;
- detached signatures and signature-domain rules;
- signed package manifests and signer-authorization policy;
- authorized patch application with pre/post-state evidence;
- stale, replay, correction, revocation, supersession, and recovery fixtures;
- nested archive and polyglot policy;
- fuzzing, dependency review, SBOM, reproducible builds, and independent security assessment; and
- independently implemented consumers for critical profiles.

## 0.3 — transport and negotiated profiles

Planned work, dependent on 0.2 acceptance:

- canonical CBOR only after byte-level vectors and ownership are approved;
- stream framing with bounded negotiation and backpressure;
- explicit capability negotiation that cannot create authority;
- reproducible multi-object bundles;
- profile discovery, downgrade prevention, and unsupported-version behavior;
- portable correction, revocation, and cache-invalidation propagation; and
- a reviewed unikernel profile with strict resource and authority boundaries.

## 1.0 — stable interoperability profile

A 1.0 designation requires:

- stable media types, namespaces, package identities, and compatibility policy;
- accepted neutral and repository-local semantic ownership;
- two or more independent implementations for critical conformance paths;
- complete security, privacy, licensing, accessibility, migration, support, and incident review;
- stable correction, revocation, supersession, rollback, and recovery guarantees;
- reference SDKs that do not become operational authorities;
- release signing and key custody;
- long-lived fixture and artifact retention; and
- approved release and deprecation governance.

## Explicitly deferred

The roadmap does not authorize:

- autonomous mutation or self-approval;
- production credential or capability issuance;
- execution of embedded resources during validation;
- portfolio-wide canonical state inside QSO-FABRIC;
- unsupervised cross-repository migration;
- payment settlement;
- release or deployment before reconciliation and approval; or
- claims that the format establishes consciousness, sentience, or physical quantum execution.

## Decision checkpoints

At every phase, reviewers must answer:

1. What exact problem and repository role does the phase solve?
2. Which records and semantics are repository-owned versus neutral?
3. What bytes, identities, mappings, and versions are canonical or explicitly non-canonical?
4. What negative, stale, replay, partial, correction, revocation, and rollback fixtures exist?
5. Who may approve, execute, verify, revoke, recover, release, and publish?
6. What prior generation is the rollback target?
7. What evidence is retained at the exact candidate head?

Unknown answers block promotion.