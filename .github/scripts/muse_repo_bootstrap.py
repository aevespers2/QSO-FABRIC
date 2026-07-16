#!/usr/bin/env python3
"""Apply missing Muse Markdown files to every owned, non-archived repository.

The script is intentionally additive: an existing repository-specific Markdown file
is never overwritten. A GitHub issue is created once to request repository
orientation and Muse task-chain review.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
MARKER = "<!-- muse-repository-orientation-v1 -->"


def request(method: str, path: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "muse-repository-bootstrap",
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 404:
            return None
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def list_owned_repositories(owner: str, token: str) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"affiliation": "owner", "per_page": 100, "page": page, "sort": "created"})
        batch = request("GET", f"/user/repos?{query}", token) or []
        repos.extend(repo for repo in batch if repo.get("owner", {}).get("login", "").lower() == owner.lower())
        if len(batch) < 100:
            return repos
        page += 1


def file_exists(repo: str, path: str, branch: str, token: str) -> bool:
    encoded = urllib.parse.quote(path, safe="/")
    ref = urllib.parse.quote(branch, safe="")
    return request("GET", f"/repos/{repo}/contents/{encoded}?ref={ref}", token) is not None


def create_file(repo: str, path: str, content: str, branch: str, token: str, dry_run: bool) -> None:
    if dry_run:
        return
    encoded = urllib.parse.quote(path, safe="/")
    request(
        "PUT",
        f"/repos/{repo}/contents/{encoded}",
        token,
        {
            "message": f"chore: add repository-specific {path}",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        },
    )


def orientation_body(repo: dict[str, Any], added: list[str], control_repo: str) -> str:
    language = repo.get("language") or "not yet detected"
    description = repo.get("description") or "No repository description is currently set."
    topics = ", ".join(repo.get("topics") or []) or "none"
    return f"""{MARKER}
# Muse repository orientation request

Muse, inspect **{repo['full_name']}** and produce a grounded repository orientation before proposing changes.

## Initial repository signals
- Description: {description}
- Primary language: {language}
- Topics: {topics}
- Default branch: `{repo['default_branch']}`
- Fork: `{str(bool(repo.get('fork'))).lower()}`
- Canonical files added by `{control_repo}`: {', '.join(f'`{name}`' for name in added) if added else 'none; repository-specific versions already existed'}

## Required review chain
- [ ] Inventory source, configuration, documentation, tests, workflows, data, models, and generated artifacts.
- [ ] State the repository's purpose in one precise paragraph, separating evidence from inference.
- [ ] Identify components, entry points, interfaces, dependencies, and external integrations.
- [ ] Extract explicit objectives from the README, issues, code comments, manifests, and existing task files.
- [ ] Identify missing objectives, contradictions, abandoned paths, security risks, and documentation gaps.
- [ ] Update `REPOSITORY_OBJECTIVES.md` with evidence-backed goals and measurable completion criteria.
- [ ] Adapt `TASK_CHAIN.md` into repository-specific phases, dependencies, validation gates, and stop conditions.
- [ ] Update `SCHEDULED_TASKS.md` only with tasks that are safe, bounded, reversible, and auditable.
- [ ] Record Muse-specific operating constraints and questions in `MUSE.md`.
- [ ] Propose changes through a reviewable pull request; do not silently overwrite repository-specific decisions.

## Muse execution policy
Prefer inspection before implementation. Preserve provenance, distinguish facts from hypotheses, avoid destructive operations, and stop when credentials, legal authority, or human judgment are required.
"""


def issue_already_exists(repo: str, token: str) -> bool:
    query = urllib.parse.urlencode({"state": "all", "per_page": 100})
    issues = request("GET", f"/repos/{repo}/issues?{query}", token) or []
    return any(MARKER in (item.get("body") or "") for item in issues)


def create_orientation_issue(repo: dict[str, Any], added: list[str], manifest: dict[str, Any], token: str, control_repo: str, dry_run: bool) -> None:
    name = repo["full_name"]
    if issue_already_exists(name, token) or dry_run:
        return
    request(
        "POST",
        f"/repos/{name}/issues",
        token,
        {
            "title": manifest["issue_title"],
            "body": orientation_body(repo, added, control_repo),
            "labels": manifest.get("issue_labels", []),
        },
    )


def main() -> int:
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        print("MUSE_REPO_TOKEN is required and must have access to each target repository.", file=sys.stderr)
        return 2

    owner = os.environ.get("MUSE_OWNER", "aevespers2")
    dry_run = os.environ.get("MUSE_DRY_RUN", "false").lower() == "true"
    control_repo = os.environ.get("MUSE_CONTROL_REPO", f"{owner}/QSO-FABRIC")
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / ".github/muse/bootstrap-manifest.json").read_text())
    template_root = root / manifest["source_root"]
    excluded = set(manifest.get("exclude_repositories", []))
    report: list[dict[str, Any]] = []

    for repo in list_owned_repositories(owner, token):
        name = repo["full_name"]
        if repo.get("archived") or repo.get("disabled") or name in excluded:
            continue
        branch = repo["default_branch"]
        added: list[str] = []
        errors: list[str] = []
        for filename in manifest["managed_files"]:
            try:
                if not file_exists(name, filename, branch, token):
                    content = (template_root / filename).read_text(encoding="utf-8")
                    create_file(name, filename, content, branch, token, dry_run)
                    added.append(filename)
            except Exception as exc:  # keep scanning other repositories
                errors.append(f"{filename}: {exc}")
        try:
            create_orientation_issue(repo, added, manifest, token, control_repo, dry_run)
        except Exception as exc:
            errors.append(f"orientation issue: {exc}")
        report.append({"repository": name, "added": added, "errors": errors, "dry_run": dry_run})

    Path("muse-bootstrap-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    failures = sum(bool(item["errors"]) for item in report)
    print(json.dumps({"repositories_scanned": len(report), "repositories_with_errors": failures, "dry_run": dry_run}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
