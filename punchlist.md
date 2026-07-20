# QSO-FABRIC Builder Punch List

Execute only the first unblocked item. Keep PR #4 as the single canonical repair path for this work and do not create a competing implementation branch.

## PR #4 — Transactional Graph Persistence
- [ ] Replace sequential belief/knowledge activation with one atomic transaction-activation mechanism whose visible state changes through a single pointer or equivalent indivisible commit.
- [ ] Ensure interruption before the final activation leaves the previously committed transaction fully active and the candidate transaction fully inactive.
- [ ] Bind the active pointer to the transaction ID, belief snapshot hash, knowledge snapshot hash, schema versions, and manifest hash.
- [ ] On restore, verify the transaction identity and every referenced snapshot/hash before changing active state.
- [ ] Reject missing, mismatched, partially written, stale, or cross-transaction snapshot pairs.
- [ ] Add crash-injection tests at every write/rename/pointer boundary and prove no split-brain graph state becomes visible.
- [ ] Add restoration tests for tampered manifest hashes, swapped belief/knowledge snapshots, stale pointers, and interrupted activation.
- [ ] Retain exact-head CI artifacts demonstrating atomic activation, verified restoration, migration integrity, and rollback.

## PR #4 — Candidate Consolidation
- [ ] Reconcile or explicitly supersede overlapping PR #3 work so only one canonical gromerical/network-probe candidate remains.
- [ ] Preserve any verified PR #3 behavior and tests when consolidating; do not silently drop coverage.
- [ ] Keep PR #4 in draft until all transactional findings are repaired and fresh exact-head workflows pass.

## Acceptance Gates
- [ ] No observable state can contain a belief snapshot from one transaction and a knowledge snapshot from another.
- [ ] Restoration never writes or activates data before all manifest and content hashes pass.
- [ ] Rollback restores one complete previously verified transaction.
- [ ] All exact-head workflows pass with retained artifacts and no unresolved transaction-integrity review threads.
