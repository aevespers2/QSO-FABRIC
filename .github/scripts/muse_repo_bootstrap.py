#!/usr/bin/env python3
"""Audit missing Muse orientation files across public owned repositories.

The repository workflow invokes this module only as a manual, read-only audit.
Mutation helpers remain available solely for a separately authorized direct run and
fail closed unless both dry-run is disabled and an explicit write-authorization
flag is present. Existing repository-specific files are never overwritten.
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
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "muse-repository-bootstrap-audit",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 404 and method == "GET":
            return None
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def list_owned_repositories(owner: str, token: str, public_only: bool) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        params: dict[str, Any] = {"per_page": 100, "page": page, "sort": "created"}
        if public_only:
            params["type"] = "owner"
            path = f"/users/{urllib.parse.quote(owner, safe='')}/repos?{urllib.parse.urlencode(params)}"
        else:
            params["affiliation"] = "owner"
            path = f"/user/repos?{urllib.parse.urlencode(params)}"
        batch = request("GET", path, token) or []
        if not isinstance(batch, list):
            raise RuntimeError("GitHub repository listing returned a non-list response")
        repos.extend(
            repo
            for repo in batch
            if isinstance(repo, dict)
            and repo.get("owner", {}).get("login", "").lower() == owner.lower()
        )
        if len(batch) < 100:
            return repos
        page += 1


def file_exists(repo: str, path: str, branch: str, token: str) -> bool:
    encoded = urllib.parse.quote(path, safe="/")
    ref = urllib.parse.quote(branch, safe="")
    return request("GET", f"/repos/{repo}/contents/{encoded}?ref={ref}", token) is not None


def require_write_authority(dry_run: bool, write_authorized: bool) -> None:
    if not dry_run and not write_authorized:
        raise RuntimeError(
            "live repository mutation is blocked unless MUSE_WRITE_AUTHORIZED=true is supplied "
            "by a separately approved direct execution"
        )


def create_file(
    repo: str,
    path: str,
    content: str,
    branch: str,
    token: str,
    dry_run: bool,
    write_authorized: bool,
) -> None:
    require_write_authority(dry_run, write_authorized)
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
    page = 1
    while True:
        query = urllib.parse.urlencode({"state": "all", "per_page": 100, "page": page})
        issues = request("GET", f"/repos/{repo}/issues?{query}", token) or []
        if not isinstance(issues, list):
            raise RuntimeError(f"{repo}: issue listing returned a non-list response")
        if any(MARKER in (item.get("body") or "") for item in issues if isinstance(item, dict)):
            return True
        if len(issues) < 100:
            return False
        page += 1


def create_orientation_issue(
    repo: dict[str, Any],
    added: list[str],
    manifest: dict[str, Any],
    token: str,
    control_repo: str,
    dry_run: bool,
    write_authorized: bool,
) -> None:
    require_write_authority(dry_run, write_authorized)
    if dry_run:
        return
    name = repo["full_name"]
    if issue_already_exists(name, token):
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


def report_path(root: Path) -> Path:
    configured = os.environ.get("MUSE_REPORT_PATH", "").strip()
    return Path(configured) if configured else root / "muse-bootstrap-report.json"


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    token = os.environ.get("GH_TOKEN", "").strip()
    owner = os.environ.get("MUSE_OWNER", "aevespers2").strip() or "aevespers2"
    dry_run = os.environ.get("MUSE_DRY_RUN", "true").lower() == "true"
    write_authorized = os.environ.get("MUSE_WRITE_AUTHORIZED", "false").lower() == "true"
    control_repo = os.environ.get("MUSE_CONTROL_REPO", f"{owner}/QSO-FABRIC")
    root = Path(__file__).resolve().parents[2]
    output = report_path(root)

    try:
        require_write_authority(dry_run, write_authorized)
    except RuntimeError as exc:
        write_report(
            output,
            {
                "status": "BLOCKED",
                "owner": owner,
                "dry_run": dry_run,
                "write_authorized": write_authorized,
                "errors": [str(exc)],
                "repositories": [],
            },
        )
        print(str(exc), file=sys.stderr)
        return 3

    if not token and not dry_run:
        message = "a separately approved write token is required for live mutation"
        write_report(
            output,
            {
                "status": "BLOCKED",
                "owner": owner,
                "dry_run": dry_run,
                "write_authorized": write_authorized,
                "errors": [message],
                "repositories": [],
            },
        )
        print(message, file=sys.stderr)
        return 2

    manifest = json.loads((root / ".github/muse/bootstrap-manifest.json").read_text(encoding="utf-8"))
    template_root = root / manifest["source_root"]
    excluded = set(manifest.get("exclude_repositories", []))
    repositories: list[dict[str, Any]] = []

    try:
        owned = list_owned_repositories(owner, token, public_only=dry_run)
    except Exception as exc:
        write_report(
            output,
            {
                "status": "ERROR",
                "owner": owner,
                "dry_run": dry_run,
                "write_authorized": write_authorized,
                "errors": [str(exc)],
                "repositories": [],
            },
        )
        print(str(exc), file=sys.stderr)
        return 1

    for repo in owned:
        name = repo["full_name"]
        if repo.get("archived") or repo.get("disabled") or name in excluded:
            continue
        branch = repo["default_branch"]
        missing_files: list[str] = []
        errors: list[str] = []
        for filename in manifest["managed_files"]:
            try:
                if not file_exists(name, filename, branch, token):
                    missing_files.append(filename)
                    content = (template_root / filename).read_text(encoding="utf-8")
                    create_file(
                        name,
                        filename,
                        content,
                        branch,
                        token,
                        dry_run,
                        write_authorized,
                    )
            except Exception as exc:
                errors.append(f"{filename}: {exc}")
        try:
            create_orientation_issue(
                repo,
                missing_files,
                manifest,
                token,
                control_repo,
                dry_run,
                write_authorized,
            )
        except Exception as exc:
            errors.append(f"orientation issue: {exc}")
        repositories.append(
            {
                "repository": name,
                "missing_files": missing_files,
                "errors": errors,
                "dry_run": dry_run,
                "write_authorized": write_authorized,
            }
        )

    failures = sum(bool(item["errors"]) for item in repositories)
    report = {
        "status": "PASS" if failures == 0 else "ERROR",
        "owner": owner,
        "coverage_mode": "public_owner_repositories" if dry_run else "authorized_owner_repositories",
        "repositories_scanned": len(repositories),
        "repositories_with_errors": failures,
        "dry_run": dry_run,
        "write_authorized": write_authorized,
        "errors": [],
        "repositories": repositories,
    }
    write_report(output, report)
    print(json.dumps({key: report[key] for key in ("status", "coverage_mode", "repositories_scanned", "repositories_with_errors", "dry_run", "write_authorized")}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
