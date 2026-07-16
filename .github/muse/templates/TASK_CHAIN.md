# Repository Task Chain

> This file is a repository-local planning contract. Adapt it to the code and evidence in this repository; do not copy assumptions from another project.

## 1. Orient
- Inventory the repository tree, languages, manifests, entry points, workflows, tests, datasets, and documentation.
- Separate directly observed facts from hypotheses.
- Identify the current default branch, release state, and active work.

## 2. Define
- State the repository purpose and intended users.
- Convert objectives into measurable outcomes and acceptance criteria.
- Record dependencies, constraints, risks, and required human decisions.

## 3. Plan
- Break work into small, reversible tasks.
- Give every task an owner or agent, inputs, outputs, validation method, dependencies, and stop condition.
- Prefer reviewable pull requests over direct changes to the default branch.

## 4. Execute
- Work in dependency order.
- Preserve provenance and existing repository-specific decisions.
- Avoid destructive operations, credential handling, deployment, or external publication without explicit authority.

## 5. Validate
- Run applicable tests, linters, type checks, security checks, and documentation validation.
- Compare results against acceptance criteria.
- Record failures and uncertainty rather than hiding them.

## 6. Report
- Summarize what changed, why it changed, evidence used, validation performed, unresolved risks, and next actions.
- Update this task chain when the repository's actual architecture or objectives change.
