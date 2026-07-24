"""Create every path in roadmap/scaffold-plan.json with a unique roadmap header.

Phase: full runtime development. Stages: contract, implementation, verification, integration, release. Tasks: validate paths, create missing files, preserve existing code, record deterministic output, require review. Steps: dry-run, inspect, write, diff, test, approve.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "roadmap" / "scaffold-plan.json"

def describe(path: Path) -> str:
    area = path.parent.as_posix() or "repository root"
    return f"Own the bounded Experimenters responsibility for {path.stem} within {area}."

def data(path: Path) -> dict[str, object]:
    return {"file": path.as_posix(), "purpose": describe(path), "phase": "planned", "stages": ["contract", "implementation", "verification", "integration", "release"], "tasks": ["Define typed inputs, outputs, invariants, ownership, and failure behavior.", "Implement deterministic bounded behavior without expanding authority.", "Add positive, negative, boundary, replay, and tamper tests.", "Connect provenance, freeze points, governance, and human review.", "Document compatibility, migration, rollback, and release evidence."], "steps": ["Review upstream contracts.", "Implement or document the responsibility.", "Add fail-closed fixtures and tests.", "Run exact-head validation and replay.", "Record human acceptance evidence."], "status": "scaffold"}

def render(path: Path) -> str:
    item = data(path); suffix = path.suffix.lower(); body = "\n".join([f"Roadmap: {item['file']}", f"Purpose: {item['purpose']}", f"Phase: {item['phase']}", "Stages: contract -> implementation -> verification -> integration -> release", "Tasks:", *[f"- {x}" for x in item["tasks"]], "Steps:", *[f"{i}. {x}" for i, x in enumerate(item["steps"], 1)]])
    if suffix == ".json": return json.dumps({"roadmap": item}, indent=2) + "\n"
    if suffix == ".py": return f'"""\n{body}\n"""\n\nfrom __future__ import annotations\n\n# TODO: implement and test.\n'
    if suffix in {".ts", ".tsx"}: return "/**\n * " + body.replace("\n", "\n * ") + "\n */\n\nexport {};\n"
    if suffix in {".yml", ".yaml", ".toml"} or path.name in {"requirements.txt", "CODEOWNERS"}: return "# " + body.replace("\n", "\n# ") + "\n"
    return f"# {path.stem.replace('-', ' ').title()}\n\n{body}\n"

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--force", action="store_true"); args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    for folder, names in plan["groups"].items():
        for name in names:
            relative = Path(folder) / name; target = ROOT / relative
            print(("replace" if target.exists() else "create") + ": " + relative.as_posix())
            if not args.write or (target.exists() and not args.force): continue
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(render(relative), encoding="utf-8")
if __name__ == "__main__": main()
