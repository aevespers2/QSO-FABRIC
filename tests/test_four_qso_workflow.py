from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/four-qso-ci.yml"


class FourQsoWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_actions_are_pinned_to_commit_shas(self) -> None:
        uses = re.findall(r"^\s*uses:\s*([^\s]+)$", self.text, flags=re.MULTILINE)
        self.assertTrue(uses)
        for action in uses:
            with self.subTest(action=action):
                self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$")

    def test_exact_head_is_checked_out_without_credentials(self) -> None:
        self.assertIn("ref: ${{ env.EXPECTED_SHA }}", self.text)
        self.assertIn("persist-credentials: false", self.text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"', self.text)

    def test_each_head_retains_fail_closed_evidence(self) -> None:
        self.assertIn("cancel-in-progress: false", self.text)
        self.assertIn("if: always()", self.text)
        self.assertIn("four-qso-ci-${{ env.EXPECTED_SHA }}", self.text)
        self.assertIn("retention-days: 90", self.text)
        self.assertIn("Enforce fail-closed completion", self.text)

    def test_test_runner_is_exactly_pinned(self) -> None:
        self.assertIn("pytest==9.1.1", self.text)
        self.assertNotIn("pip install --upgrade pip pytest", self.text)


if __name__ == "__main__":
    unittest.main()
