# Self-Learning Milestone Two

This milestone connects bounded Seeker evidence handoffs to deterministic QSO learning, explicit human-reviewed durable promotion, reversible snapshots, and candidate-only cross-episode consolidation.

## Enforced boundaries

- Network evidence is accepted only from `seeker-proxy` handoffs.
- QSO network authority remains false.
- Retrieved evidence remains non-executable and content-hash verified.
- Durable promotion requires an explicit reviewer identity and approval.
- Invalid memory chains and non-review-ready episodes cannot be promoted.
- Every promotion creates pre- and post-promotion snapshots.
- Rollback archives the displaced state before restoring a selected snapshot.
- Consolidated concepts remain in the candidate layer and cannot promote themselves.

## Exact lifecycle

`Seeker handoff → hash verification → active/held-out split → four-QSO episode → held-out evaluation → freeze hash → human promotion → durable snapshot → cross-episode consolidation → reviewed rollback`
