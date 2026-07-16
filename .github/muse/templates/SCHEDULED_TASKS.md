# Scheduled Tasks

Scheduled tasks must be bounded, auditable, reversible, and safe to run without unattended judgment.

## Repository discovery
- **Cadence:** Every six hours from the control repository.
- **Purpose:** Detect newly created, forked, imported, or otherwise newly accessible owned repositories.
- **Action:** Add only missing canonical Markdown files and create one Muse orientation issue.
- **Validation:** Store a JSON audit artifact for every run.

## Permitted unattended tasks
- Inventory repository metadata and file structure.
- Detect missing documentation, tests, workflows, and configuration.
- Open issues or pull requests containing proposed changes.
- Run existing non-destructive tests and static analysis.
- Refresh repository maps, task status, and evidence citations.

## Tasks requiring explicit authorization
- Merging pull requests or modifying protected branches.
- Deploying, publishing packages, creating releases, or changing infrastructure.
- Rotating or using credentials beyond the minimum read/write repository token.
- Deleting, migrating, rewriting history, or changing licensing or ownership.
- Acting on legal, financial, identity, safety, or production decisions.

## Audit fields
Every scheduled run should record timestamp, repository, trigger, files inspected, files added or proposed, validation performed, errors, uncertainty, and next action.
