# QSO-FABRIC Output Contracts

This document records the JSON and hashing behavior currently implemented by `qso_runtime.four_qso_experiment`. It is a design and migration reference, not a declaration that the present format is a stable public contract.

`taskchain.md` P1 and `release.md` require explicit versions and canonicalization rules before the first runtime release. Until that work is accepted, consumers should treat current reports as **unversioned candidate artifacts** and reject them for durable interchange unless their exact producing commit and environment are known.

## Top-level report

The current report contains:

| Field | Current type | Meaning |
|---|---|---|
| `objective` | string | Full research objective supplied to all four QSOs |
| `base_seed` | integer | Seed from which per-QSO seeds are derived |
| `limits` | object | Serialized `ExperimentLimits` |
| `ledger_valid` | boolean | Result of verifying the in-memory event chain |
| `event_count` | integer | Number of events in the report |
| `final_event_hash` | string | Hash of the final event |
| `qsos` | object | Map of QSO name to serialized QSO result |
| `events` | array | Ordered serialized event ledger |

The full objective is retained in the top-level report and the `experiment_started` event. Only observation and message text are truncated by `max_message_chars`; the current implementation therefore does not provide a complete report-size or memory bound.

The report currently has no `schema_version`, `canonicalization_version`, producer version, source commit, generation time, environment, or artifact checksum field. These omissions are release blockers, not permission for consumers to infer defaults.

## Limits object

Current fields:

```json
{
  "max_rounds": 4,
  "max_messages_per_qso": 8,
  "max_message_chars": 600,
  "max_runtime_seconds": 10.0
}
```

The runtime rejects non-positive round, message-count, or runtime values. It currently does not apply a separate validation rule to `max_message_chars`; the release contract must define accepted types, ranges, and behavior for zero, negative, extremely large, non-integer, NaN, and infinite values where applicable.

## QSO result

Each entry in `qsos` currently contains:

| Field | Current type | Meaning |
|---|---|---|
| `name` | string | Stable QSO identifier |
| `role` | string | Human-readable role description |
| `seed` | integer | Per-QSO deterministic seed |
| `observations` | array of strings | Objective intake observations, truncated by `max_message_chars` |
| `inferences` | array of strings | Deterministically selected round statements |
| `contradictions` | array of strings | Reserved contradiction records; currently empty in the baseline path |
| `messages_sent` | array of objects | `{to, text}` records |
| `messages_received` | array of objects | `{from, text}` records |
| `freeze_points` | array of strings | `label:digest` markers |
| `final_proposal` | string | Final role-specific proposal |

The four current identifiers are `atlas`, `nova`, `orion`, and `lyra`. Their insertion order affects seed assignment, round order, messaging, ledger order, and hashes. A release contract must either preserve that order explicitly or encode ordering independently.

## Event record

The first event currently has the following shape:

```json
{
  "seq": 0,
  "kind": "experiment_started",
  "actor": "fabric",
  "payload": {
    "objective": "<full objective>",
    "base_seed": 2987,
    "limits": {
      "max_rounds": 4,
      "max_messages_per_qso": 8,
      "max_message_chars": 600,
      "max_runtime_seconds": 10.0
    }
  },
  "previous_hash": "GENESIS",
  "event_hash": "<sha256>"
}
```

Current event kinds include:

- `experiment_started`;
- `observation`;
- `freeze`;
- `inference`;
- `message_sent`;
- `message_received`;
- `runtime_limit` when triggered;
- `proposal`;
- `experiment_completed`.

The set is not yet versioned or declared exhaustive. Consumers must not silently accept unknown event kinds before an extensibility policy is defined.

## Event hashing

The current event digest is SHA-256 over UTF-8 encoded JSON for:

```json
{
  "seq": 0,
  "kind": "...",
  "actor": "...",
  "payload": {},
  "previous_hash": "..."
}
```

Serialization uses Python `json.dumps` with `sort_keys=True` and `separators=(",", ":")`. The first event uses `GENESIS` as `previous_hash`; every later event uses the immediately preceding `event_hash`.

Before release, the contract must define schema and canonicalization versions, Unicode normalization and escaping, number representation, duplicate-key handling, ordering, nesting and size limits, digest identifiers, hexadecimal requirements, unknown-field/version behavior, and a checksum for the complete artifact.

## Freeze-point hashing

A freeze digest is SHA-256 over compact, sorted-key JSON for the current serialized QSO result. The digest is calculated before the new freeze marker is appended; the marker `label:digest` is then appended and a `freeze` event records `{label, state_hash}`.

Recomputing a freeze digest from the final result without reconstructing the state at that point will not necessarily yield the stored digest. A stable contract must either retain this incremental commitment model, define immutable snapshot objects, or declare a field-exclusion rule.

## Determinism boundary

Away from the wall-clock timeout boundary, current deterministic behavior depends on:

- one base seed;
- per-QSO seeds assigned by stable QSO insertion order;
- Python's local `random.Random` behavior;
- fixed role template arrays;
- fixed directed-ring message order;
- fixed round order;
- compact sorted-key JSON serialization;
- no timestamps or external data in report state.

The timeout path is different. Before each round, the runtime compares `time.monotonic()` with `max_runtime_seconds`; host scheduling and execution speed determine which round, if any, receives a `runtime_limit` event. Identical seed, objective, and limits therefore do **not** guarantee identical event counts or hashes near the timeout threshold. Timeout-path artifacts must be treated as nondeterministic until the contract replaces wall-clock placement with deterministic budgeting or explicitly excludes timeout hashes from replay guarantees.

Exact cross-version reproducibility of pseudorandom behavior and serialization must also be demonstrated for the supported environment matrix. Otherwise the release must narrow the supported matrix or define versioned algorithms independent of implementation details.

## Validation order

A future consumer should:

1. read bytes under a declared size limit;
2. parse JSON with duplicate-key and non-finite-number rejection;
3. validate the supported schema and canonicalization versions;
4. validate field types, bounds, identities, and ordering;
5. verify ledger links and event hashes;
6. verify freeze commitments using declared semantics;
7. verify artifact checksum and provenance;
8. accept the artifact only as structurally valid evidence.

Structural validity does not establish the truth or quality of a final proposal.

## Required fixtures

The versioned contract suite should include canonical positive reports; repeated same-seed outputs; different-seed outputs; malformed JSON and duplicate keys; unsupported versions; modified, deleted, inserted, duplicated, and reordered events; broken links and hashes; changed freeze semantics; Unicode, numeric, and boundary-size cases; deterministic-budget and wall-clock-timeout cases; interruption and partial-write artifacts; unknown identifiers; and upstream manifest hash/version mismatches.

Every fixture must identify an expected `PASS`, `FAIL`, or `UNKNOWN` result and a stable reason code.

## Compatibility policy

Until a versioned policy is adopted:

- changes to report fields, event kinds, hashing, ordering, seeds, templates, timeout behavior, or freeze behavior are breaking;
- consumers should pin the source commit and expected hashes;
- unknown fields or versions should fail closed;
- upstream compatibility should remain read-only and hash/version checked;
- no report may authorize code execution, payments, credential use, network access, or repository mutation.

## Related documentation

- [Architecture](ARCHITECTURE.md)
- [Developer guide](DEVELOPER_GUIDE.md)
- [Release plan](https://github.com/aevespers2/QSO-FABRIC/blob/main/release.md)
- [Task chain](https://github.com/aevespers2/QSO-FABRIC/blob/main/taskchain.md)
