# QSO-FABRIC Architecture

QSO-FABRIC is the bounded integration harness for four deterministic Quantum State Objects: Atlas, Nova, Orion, and Lyra. Its current responsibility is deliberately narrow: execute a finite research exercise, preserve a verifiable event history, emit reviewable proposals, and stop without acquiring network, credential, shell, wallet, deployment, or repository authority.

Within the portfolio, **A.L.I.S.T.A.I.R.E. is the canonical system**. QSO-FABRIC is its deterministic collaboration and evidence subsystem, not the system as a whole and not the autonomous-development control plane.

> **Maturity:** implemented candidate runtime, not an accepted release. The architecture below describes the current code and the contract boundaries required by `taskchain.md` and `release.md`; it does not claim that packaging, cross-environment determinism, adversarial tests, upstream compatibility, or release evidence have passed.

## Portfolio context

```mermaid
flowchart TB
    AL[A.L.I.S.T.A.I.R.E.\nmission, architecture, governance]
    CP[Dedicated development control plane\nplanning, repository proposals, approved operations]
    G[QSO-GENOMES\nidentity and evolution contracts]
    Q[QuantumStateObjects\nruntime contracts]
    S[QSO-SEEKER\nbounded evidence artifacts]
    F[QSO-FABRIC\ndeterministic experiments and integrity evidence]
    U[QSO-STUDIO / AionUi\nhuman review and interaction]

    AL --> CP
    AL --> G
    AL --> Q
    AL --> S
    AL --> F
    AL --> U
    G -. versioned manifest .-> F
    Q -. versioned runtime contract .-> F
    S -. bounded evidence .-> F
    CP -. approved objective and candidate .-> F
    F -. report, ledger, hashes .-> CP
    F -. inspectable artifact .-> U
```

Every dotted edge is a proposed contract boundary. It grants no executable or repository authority. The portfolio still requires an explicit decision identifying the repository that owns autonomous development orchestration, credential policy, merge/deploy authority, audit, and cross-repository rollback.

## Runtime system context

```mermaid
flowchart LR
    H[Human researcher] -->|objective, seed, limits| R[Four-QSO runner]
    R --> A[Atlas]
    R --> N[Nova]
    R --> O[Orion]
    R --> L[Lyra]
    A <--> N
    N <--> O
    O <--> L
    L <--> A
    A --> E[Append-only event ledger]
    N --> E
    O --> E
    L --> E
    R --> E
    E --> P[JSON experiment report]
    P --> V[Human review and external verification]
    G[QSO-GENOMES manifest] -. read-only schema/hash validation .-> R
    Q[QuantumStateObjects contracts] -. read-only schema/hash validation .-> R
```

The dotted upstream edges are planned compatibility checks. QSO-FABRIC must not import execution authority, mutate upstream repositories, or treat an upstream artifact as trusted solely because it exists.

## Runtime components

| Component | Current responsibility | Required boundary |
|---|---|---|
| `ExperimentLimits` | Defines round, message, message-length, and runtime limits | Values must be validated and must fail closed when invalid or exhausted |
| `BoundedQSO` | Maintains one role-specific deterministic state and produces observations, inferences, messages, freezes, and a final proposal | No direct shell, network, credential, wallet, filesystem-discovery, deployment, or repository-write capability |
| `AppendOnlyLedger` | Hash-chains ordered events using canonical JSON and SHA-256 | Tampering, reordering, deletion, or incompatible canonicalization must be detectable |
| `run_experiment` | Coordinates initialization, bounded rounds, directed message exchange, freeze points, finalization, and report assembly | One objective, one seed, explicit limits, deterministic ordering, bounded termination |
| CLI entry point | Writes the JSON report to a caller-selected path | Path behavior, overwrite policy, errors, and interruption handling require explicit verification |
| Tests | Exercise seeded replay, ledger validity, freeze/message presence, and Nova's verification posture | Current tests are a baseline only; boundary, timeout, tamper, interruption, rollback, and cross-environment fixtures remain release requirements |

## Four-QSO collaboration model

```mermaid
flowchart TB
    X[Research objective] --> AT[Atlas\nstructure and algorithms]
    X --> NO[Nova\nverification and contradiction]
    X --> OR[Orion\narchitecture and interfaces]
    X --> LY[Lyra\nlanguage and epistemology]

    AT -->|round statement| NO
    NO -->|round statement| OR
    OR -->|round statement| LY
    LY -->|round statement| AT

    AT --> FA[Atlas freeze hash]
    NO --> FN[Nova freeze hash]
    OR --> FO[Orion freeze hash]
    LY --> FL[Lyra freeze hash]

    FA --> C[Final report]
    FN --> C
    FO --> C
    FL --> C
```

The current message topology is a fixed directed ring. Each QSO uses a seed derived from the base seed and its stable insertion order. The resulting statements are deterministic template selections, not autonomous external learning or open-ended cognition.

## Experiment lifecycle

```mermaid
stateDiagram-v2
    [*] --> ValidateInput
    ValidateInput --> Rejected: empty objective or invalid limits
    ValidateInput --> Initialized: accepted
    Initialized --> InitialFreeze
    InitialFreeze --> Round
    Round --> RoundFreeze
    RoundFreeze --> Round: rounds remain and runtime available
    RoundFreeze --> Finalize: round limit reached
    Round --> Finalize: runtime limit reached
    Finalize --> FinalFreeze
    FinalFreeze --> LedgerVerification
    LedgerVerification --> Reported: report assembled
    Rejected --> [*]
    Reported --> [*]
```

The current runtime records a `runtime_limit` event and proceeds to finalization when its time check fires. Release acceptance must verify the exact timeout semantics, including whether work performed inside a round can exceed the configured duration and whether interruption leaves a recoverable artifact.

## Event and integrity design

Each event records:

- a zero-based sequence number;
- an event kind;
- the actor;
- a JSON-compatible payload;
- the previous event hash, or `GENESIS` for the first event;
- the SHA-256 hash of canonical JSON containing the preceding fields.

Canonicalization currently uses sorted keys and compact separators. This is implementation behavior, not yet a versioned public contract. A release must assign explicit schema and canonicalization versions so readers can distinguish compatible records from merely similar JSON.

### Integrity properties

The current verifier checks the previous-hash link and recomputes each event hash. Release fixtures must also prove behavior for:

- changed payloads, actors, event kinds, sequence values, and hashes;
- removed, duplicated, inserted, or reordered events;
- incompatible Unicode and numeric representations;
- alternate JSON serializers and supported Python environments;
- truncated reports and interrupted writes;
- unknown schema or canonicalization versions.

## Freeze-point design

A freeze point hashes the current serialized `QSOResult` and records both a marker in the QSO result and a `freeze` ledger event. The intended purpose is to make state transitions reviewable at initialization, after each round, and at finalization.

The current implementation calculates the digest before appending the new marker to `freeze_points`. Documentation and fixtures must preserve this exact semantic or intentionally migrate it with a contract version. A freeze hash must never be described as a complete proof of semantic correctness; it is an integrity marker for a declared serialization procedure.

## Trust boundaries

```mermaid
flowchart LR
    U[Untrusted objective and CLI arguments] --> B[Input validation boundary]
    B --> C[Bounded deterministic core]
    C --> J[Generated JSON artifact]
    J --> D[Independent review boundary]
    M[External manifests and contracts] --> S[Schema, version, and hash validator]
    S --> C

    C -. forbidden .-> SH[Shell or command execution]
    C -. forbidden .-> NW[Unrestricted network]
    C -. forbidden .-> CR[Credentials or wallets]
    C -. forbidden .-> RW[Repository mutation]
    C -. forbidden .-> DP[Merge, release, or deployment]
```

The generated report is evidence of what the harness recorded, not authority to execute its proposals. Consumers must preserve the distinction between observations, inferences, contradictions, messages, integrity metadata, final proposals, acceptance decisions, and executed actions.

## Autonomous-development separation

The wider A.L.I.S.T.A.I.R.E. mission may automate observation, planning, design, implementation proposals, testing, documentation, review preparation, and eventually policy-approved operations. QSO-FABRIC owns only bounded experiment and evidence responsibilities unless its product directive is explicitly revised.

```mermaid
flowchart LR
    O[Observe approved inputs] --> P[Plan or hypothesize]
    P --> F[QSO-FABRIC bounded experiment]
    F --> E[Evidence, contradictions, ledger, hashes]
    E --> G[Dedicated governance/control plane]
    G -->|approved next objective| F
    G -->|reviewable repository candidate| R[Repository PR process]
    R -->|accepted result| O
```

The control plane must be separately chartered because it requires authorities that the runtime intentionally lacks: repository discovery, credentials, branch and pull-request operations, merge/deploy policy, audit, incident response, and portfolio rollback.

## Dependency and authority rules

QSO-FABRIC may eventually read published QSO-GENOMES and QuantumStateObjects artifacts only through a bounded compatibility layer that verifies:

1. expected artifact identity;
2. supported schema version;
3. declared canonicalization version;
4. artifact hash;
5. required fields and limits;
6. explicit rejection of unknown or incompatible inputs.

Compatibility does not grant code execution, repository write access, network access, deployment access, or policy authority. Cross-repository mutation and owner-wide governance automation remain explicitly outside the current product scope.

## Candidate architecture rules

Several open pull requests explore expanded collectives, Seeker-mediated evidence, self-learning scaffolds, sovereign sprite policy, safety repair, and QSIO integration. They are concurrent candidates, not cumulative accepted architecture.

Before any candidate can join the baseline it must:

- fit the current product directive or receive a separately recorded scope decision;
- declare changed contracts and new authority;
- rebase and reconcile every shared invariant;
- produce exact-head deterministic, security, failure, and rollback evidence;
- update the task chain, release plan, changelog, and public documentation;
- receive an explicit acceptance decision.

See [Candidate governance](CANDIDATE_GOVERNANCE.md) for the full admission and conflict model.

## Failure model

| Failure | Required behavior |
|---|---|
| Empty objective or invalid limits | Reject before creating a candidate report |
| Message cap reached | Stop accepting additional messages for that QSO and preserve evidence of the bounded result |
| Runtime limit reached | Stop bounded iteration, record the condition, and finalize according to documented semantics |
| Ledger verification failure | Mark the artifact invalid and prevent release or downstream acceptance |
| Output path or write failure | Return a visible non-zero failure; never report a successful durable artifact |
| Interruption | Preserve or clearly quarantine partial evidence; do not present it as a complete run |
| Upstream contract missing or incompatible | Fail closed without importing or executing upstream code |
| Seeded replay divergence | Block the candidate and retain both outputs and environment provenance |
| Candidate contract conflict | Hold integration until the conflict is versioned, migrated, or rejected explicitly |
| Unapproved authority path | Stop, preserve evidence, revoke pending capability, and require review |

## Release architecture gates

The architecture is release-eligible only when the repository includes and verifies:

- a package/build definition, supported Python matrix, dependency baseline, and license;
- versioned event, ledger, freeze-point, limit, and report contracts;
- deterministic replay across supported environments;
- boundary, timeout, tamper, interruption, recovery, and rollback fixtures;
- security checks for untrusted input, paths, resources, dependencies, workflow permissions, secrets, consent, and prohibited authority paths;
- read-only upstream compatibility by schema version and hash;
- retained commands, logs, tool versions, artifact hashes, checksums, and provenance at one immutable candidate commit.

## Related documentation

- [Project and Pages overview](index.html)
- [Role in A.L.I.S.T.A.I.R.E.](ALISTAIRE_ROLE.md)
- [Candidate governance](CANDIDATE_GOVERNANCE.md)
- [Developer guide](DEVELOPER_GUIDE.md)
- [Output contract notes](OUTPUT_CONTRACTS.md)
- [Task chain](../taskchain.md)
- [Release plan](../release.md)
- [Changelog](../changelog.md)
