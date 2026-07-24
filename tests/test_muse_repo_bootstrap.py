from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github/scripts/muse_repo_bootstrap.py"
WORKFLOW = ROOT / ".github/workflows/muse-repository-bootstrap.yml"


def load_module():
    spec = importlib.util.spec_from_file_location("muse_repo_bootstrap", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load bootstrap module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MuseBootstrapSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_dry_run_never_calls_file_write_api(self) -> None:
        with mock.patch.object(self.module, "request", side_effect=AssertionError("write attempted")):
            self.module.create_file(
                "aevespers2/example",
                "MUSE.md",
                "content",
                "main",
                "token",
                dry_run=True,
                write_authorized=False,
            )

    def test_live_file_write_requires_separate_authorization(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "live repository mutation is blocked"):
            self.module.create_file(
                "aevespers2/example",
                "MUSE.md",
                "content",
                "main",
                "token",
                dry_run=False,
                write_authorized=False,
            )

    def test_issue_lookup_paginates_until_marker_or_terminal_page(self) -> None:
        first = [{"body": "unrelated"}] * 100
        second = [{"body": self.module.MARKER}]
        with mock.patch.object(self.module, "request", side_effect=[first, second]) as request:
            self.assertTrue(self.module.issue_already_exists("aevespers2/example", "token"))
        self.assertEqual(2, request.call_count)
        self.assertIn("page=2", request.call_args_list[1].args[1])

    def test_unauthorized_main_fails_before_network_and_retains_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            env = {
                "GH_TOKEN": "token",
                "MUSE_OWNER": "aevespers2",
                "MUSE_DRY_RUN": "false",
                "MUSE_WRITE_AUTHORIZED": "false",
                "MUSE_REPORT_PATH": str(report),
            }
            with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
                self.module,
                "list_owned_repositories",
                side_effect=AssertionError("network attempted"),
            ):
                self.assertEqual(3, self.module.main())
            self.assertIn('"status": "BLOCKED"', report.read_text(encoding="utf-8"))

    def test_workflow_is_manual_read_only_exact_head_and_secret_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("issues: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("issues: write", text)
        self.assertNotIn("MUSE_REPO_TOKEN", text)
        self.assertIn('MUSE_DRY_RUN: "true"', text)
        self.assertIn('MUSE_WRITE_AUTHORIZED: "false"', text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("${{ github.workflow }}-${{ github.sha }}", text)
        self.assertIn("cancel-in-progress: false", text)
        self.assertRegex(text, r"actions/checkout@[0-9a-f]{40}")
        self.assertRegex(text, r"actions/setup-python@[0-9a-f]{40}")
        self.assertRegex(text, r"actions/upload-artifact@[0-9a-f]{40}")


if __name__ == "__main__":
    unittest.main()
