from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "materialize_self_learning_scaffold.py"
MANIFEST = ROOT / "architecture" / "self_learning_scaffold.json"

spec = importlib.util.spec_from_file_location("materialize_self_learning_scaffold", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_manifest_is_safe_unique_and_comprehensive() -> None:
    manifest = module.load_manifest(MANIFEST)
    files = manifest["files"]
    assert len(files) >= 400
    assert len(files) == len(set(files))
    required = {
        "src/self_learning_orchestrator/orchestrator/orchestrator.py",
        "src/self_learning_orchestrator/engines/gromerical/engine.py",
        "src/self_learning_orchestrator/seeker/proxy.py",
        "src/self_learning_orchestrator/memory/hash_registry.py",
        "src/self_learning_orchestrator/fabric/promoter.py",
        "src/self_learning_orchestrator/rollback/manager.py",
        "src/self_learning_orchestrator/security/prompt_injection.py",
        "contracts/learning-cycle.schema.json",
        "tests/adversarial/test_memory_corruption_suite.py",
        "docs/SELF_LEARNING_ARCHITECTURE.md",
    }
    assert required.issubset(set(files))


def test_dry_run_is_deterministic(tmp_path: Path) -> None:
    first = module.materialize(MANIFEST, tmp_path, write=False)
    second = module.materialize(MANIFEST, tmp_path, write=False)
    assert first == second
    assert first["created_file_count"] == first["declared_file_count"]
    assert first["existing_file_count"] == 0


def test_materialization_is_idempotent(tmp_path: Path) -> None:
    first = module.materialize(MANIFEST, tmp_path, write=True)
    second = module.materialize(MANIFEST, tmp_path, write=True)
    assert first["created_file_count"] == first["declared_file_count"]
    assert second["created_file_count"] == 0
    assert second["existing_file_count"] == second["declared_file_count"]
    assert (tmp_path / "src/self_learning_orchestrator/memory/hash_registry.py").exists()
    assert json.loads((tmp_path / "contracts/learning-cycle.schema.json").read_text())["$comment"]
