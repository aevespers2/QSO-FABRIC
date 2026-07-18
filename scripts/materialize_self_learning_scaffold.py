from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "architecture" / "self_learning_scaffold.json"
DEFAULT_TARGET = ROOT


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def placeholder(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name
    if name == ".gitkeep":
        return ""
    if suffix == ".py":
        module = path.stem.replace("_", " ").title()
        return f'"""{module} module for the bounded QSO self-learning architecture.\n\nScaffold only: implementation must preserve capability, provenance, checkpoint,\nand human-review boundaries defined by the canonical architecture manifest.\n"""\n'
    if suffix == ".json":
        return json.dumps({"$comment": "Scaffold placeholder; replace through a reviewed contract change."}, indent=2) + "\n"
    if suffix in {".yaml", ".yml"}:
        return "# Scaffold placeholder. Changes require policy or workflow review.\n"
    if suffix == ".md":
        title = path.stem.replace("_", " ").replace("-", " ").title()
        return f"# {title}\n\nScaffold placeholder governed by `architecture/self_learning_scaffold.json`.\n"
    if suffix in {".txt", ".cff", ".toml", ".tf", ".sql", ".cypher"} or name in {"LICENSE", "NOTICE", "Makefile", "Dockerfile"}:
        return "# Scaffold placeholder; implementation pending reviewed milestone.\n"
    if suffix == ".sh":
        return "#!/usr/bin/env bash\nset -euo pipefail\necho 'Scaffold placeholder; no operation performed.'\n"
    return "# Scaffold placeholder.\n"


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "qso-self-learning-scaffold-v1":
        raise ValueError("unsupported scaffold schema_version")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("manifest files must be a non-empty list")
    if len(files) != len(set(files)):
        raise ValueError("manifest contains duplicate paths")
    for raw in files:
        path_value = Path(raw)
        if path_value.is_absolute() or ".." in path_value.parts:
            raise ValueError(f"unsafe scaffold path: {raw}")
    return manifest


def materialize(manifest_path: Path, target: Path, write: bool) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    created: list[str] = []
    existing: list[str] = []
    for raw in sorted(manifest["files"]):
        destination = target / raw
        if destination.exists():
            existing.append(raw)
            continue
        created.append(raw)
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(placeholder(destination), encoding="utf-8")
            if destination.suffix == ".sh":
                destination.chmod(0o755)
    summary = {
        "schema_version": manifest["schema_version"],
        "manifest_sha256": hashlib.sha256(canonical_json(manifest).encode("utf-8")).hexdigest(),
        "declared_file_count": len(manifest["files"]),
        "created_file_count": len(created),
        "existing_file_count": len(existing),
        "write": write,
        "created": created,
        "existing": existing,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize the canonical QSO self-learning scaffold")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--write", action="store_true", help="Create missing files; default is a dry run")
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    summary = materialize(args.manifest, args.target, args.write)
    output = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
