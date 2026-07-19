# QSO-FABRIC Developer Guide

This guide covers the current bounded four-QSO integration harness. It is intentionally limited to reproducing, testing, documenting, and safely extending the existing runtime. New networking, autonomous learning, payments, credentialed actions, UI orchestration, or cross-repository governance require a separately approved scope change.

## Before you begin

Read these documents in order:

1. [`README.md`](../README.md) for the repository purpose and quick start.
2. [`taskchain.md`](../taskchain.md) for the active priority and non-goals.
3. [`release.md`](../release.md) for current blockers and required evidence.
4. [`ARCHITECTURE.md`](ARCHITECTURE.md) for component and trust boundaries.
5. [`OUTPUT_CONTRACTS.md`](OUTPUT_CONTRACTS.md) before changing JSON, hashes, events, limits, or freeze behavior.

The highest-priority task is P0: accept and reproduce the current runtime baseline at one immutable commit. Documentation work must not imply that P0 is complete unless the required commands, results, environment information, and retained evidence actually exist.

## Repository map

```text
qso_runtime/
  four_qso_experiment.py   bounded runtime, ledger, QSO roles, runner, CLI

tests/
  test_four_qso_experiment.py
                           current deterministic and structural baseline tests

docs/
  index.html               GitHub Pages project overview
  ARCHITECTURE.md          architecture, trust boundaries, lifecycle, failures
  DEVELOPER_GUIDE.md       onboarding and contribution workflow
  OUTPUT_CONTRACTS.md      current JSON behavior and required versioning

taskchain.md               ordered product work and acceptance criteria
release.md                 release decision, gates, artifacts, rollback
changelog.md               evidence-oriented change history
```

Generated reports normally belong under `artifacts/`. Treat them as generated evidence, not hand-maintained source files. Whether representative artifacts are committed, attached to releases, or retained in CI must be decided explicitly and documented with hashes.

## Environment setup

The repository does not yet declare an accepted package definition, dependency lock, supported Python matrix, or license. Until P1 resolves those items, use an isolated environment and record the exact interpreter and tool versions.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pytest
python --version
python -m pytest --version
```

These commands describe a practical local baseline, not an approved reproducible installation contract. Do not add undeclared runtime dependencies merely to simplify documentation or local execution.

## Run the experiment

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The command should emit a compact summary containing the output path, ledger validity, and event count. Review the complete JSON report rather than relying on the console summary.

Useful inspection commands:

```bash
python -m json.tool artifacts/four_qso_report.json >/dev/null
python - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("artifacts/four_qso_report.json").read_text())
print("ledger_valid:", report["ledger_valid"])
print("event_count:", report["event_count"])
print("final_event_hash:", report["final_event_hash"])
print("qsos:", ", ".join(sorted(report["qsos"])))
PY
```

## Run the current tests

```bash
python -m pytest -q
```

The present suite checks:

- exact equality for two runs using the same seed and limits;
- a valid ledger in the successful baseline;
- the expected four QSO identities;
- freeze points, sent and received messages, and final proposals;
- Nova's release-verification language.

Passing these tests is necessary but not sufficient for release. The release plan also requires clean-environment installation, cross-environment canonical replay, malformed input, limit exhaustion, timeout, tamper, interruption, path/write failure, rollback, dependency, workflow, and upstream-compatibility evidence.

## Establish a reproducible P0 baseline

Record one immutable commit and capture the following without editing results after the fact:

```bash
git rev-parse HEAD
python --version
python -m pip --version
python -m pytest -q
python -m qso_runtime.four_qso_experiment \
  "P0 reproducibility baseline" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/p0-baseline.json
python -m json.tool artifacts/p0-baseline.json >/dev/null
shasum -a 256 artifacts/p0-baseline.json
```

Also record:

- operating system and architecture;
- installed package versions;
- command exit codes;
- complete test and CLI output;
- report hash and final event hash;
- workflow URLs and commit-status results, when available;
- known limitations and any divergence between environments.

A later run that uses a different commit, interpreter, dependency set, command, or artifact must not be presented as evidence for the earlier candidate.

## Development rules

### Preserve determinism

- Keep iteration and message order explicit.
- Use per-instance deterministic random generators rather than global randomness.
- Avoid timestamps, process IDs, unordered external data, environment-specific paths, or nondeterministic serialization inside hashed state.
- Treat changes to insertion order, dictionary shape, Unicode handling, numeric representation, or JSON serialization as contract changes.

### Preserve bounded authority

- Do not add shell execution, unrestricted network calls, credential access, wallet operations, repository mutation, package installation, or arbitrary plugin loading to QSO objects.
- Do not let model- or user-authored text choose commands, import paths, destinations, or write targets.
- Keep adapters outside the deterministic core and deny them by default.
- Treat final proposals as review artifacts, never executable instructions.

### Preserve evidence

- Do not rewrite or silently discard failure records.
- Make output-write, validation, timeout, and compatibility failures visible through non-zero exits or explicit invalid states.
- Preserve failed-candidate artifacts and hashes when testing tamper or rollback behavior.
- Document whether partial files are deleted, quarantined, or retained after interruption.

### Keep scope aligned

Every patch should identify the active `taskchain.md` item it supports. The current ordering is:

1. reproduce and accept the existing baseline;
2. add packaging, license, and versioned contracts;
3. add deterministic security and failure fixtures;
4. validate upstream compatibility without importing authority.

A patch that adds visualization, open-ended learning, payment settlement, portfolio automation, or production orchestration is out of scope unless the product directive and release plan are deliberately revised and approved first.

## Contract-change checklist

Before changing an event, report field, freeze digest, limit, or canonicalization rule:

- identify the old and proposed contract behavior;
- decide whether the change is compatible or requires a new version;
- add positive and negative fixtures;
- add migration or rejection behavior for old artifacts;
- verify deterministic hashes on every supported environment;
- update `OUTPUT_CONTRACTS.md`, architecture documentation, tests, release requirements, and changelog evidence;
- retain before-and-after sample artifacts and checksums.

Do not silently reinterpret existing hashes under a new algorithm or serialization rule.

## Security review checklist

At minimum, inspect:

- objective length and character handling;
- round, message, message-length, and runtime bounds;
- memory and output-size amplification;
- output path traversal, symlink, overwrite, and permission behavior;
- interruption and partial-write behavior;
- ledger tamper and canonicalization edge cases;
- dependency and workflow permissions;
- accidental secrets in source, logs, fixtures, and artifacts;
- prohibited command, network, credential, wallet, and repository-write paths;
- upstream artifact spoofing, downgrade, hash mismatch, and unknown versions.

Document findings as evidence even when the result is `UNKNOWN` or a release blocker.

## Pull-request expectations

A focused PR should include:

- the taskchain item and acceptance criterion addressed;
- a concise scope and explicit non-goals;
- files changed and contract impact;
- exact verification commands and results;
- generated artifact hashes;
- security and rollback notes;
- remaining risks and blockers;
- documentation and changelog updates when behavior changes.

Avoid combining packaging, contract redesign, new capabilities, and unrelated cleanup in one patch. Small reversible changes make deterministic review and rollback substantially easier.

## Rollback

Before merging a behavior change, identify the last verified commit and how to restore it. Roll back or withdraw the candidate when seeded outputs diverge unexpectedly, ledger tampering is not detected, limits can be bypassed, interruption corrupts evidence, prohibited authority appears, upstream compatibility drifts, or documented commands cannot be reproduced.

Rollback must preserve the failed candidate's commit, commands, logs, artifacts, hashes, and explanation. Deleting failed evidence makes later verification weaker.
