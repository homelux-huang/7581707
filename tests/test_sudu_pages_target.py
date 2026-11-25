"""Offline protection checks; no GitHub runs, changes or deployments."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import sudu_pages_target as gate

ROOT = Path(__file__).resolve().parents[1]


class PagesTargetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Offline test")
        self.git("config", "user.email", "pages-target@example.invalid")
        self.git("commit", "--allow-empty", "-qm", "previous")
        self.previous = self.git("rev-parse", "HEAD")
        self.git("commit", "--allow-empty", "-qm", "current")
        self.current = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", self.current)
        self.branch = {"name": "main", "protected": True, "commit": {"sha": self.current}}

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def run_guard(self, target=None, branch=None, event="push", **overrides):
        path = self.repo / "branch-response.json"
        path.write_text(json.dumps(self.branch if branch is None else branch))
        env = {**os.environ, "GITHUB_REPOSITORY": gate.REPOSITORY,
               "GITHUB_REF": gate.MAIN_REF, "GITHUB_REF_PROTECTED": "true",
               "GITHUB_WORKFLOW_REF": gate.PAGES_WORKFLOW_REF,
               "GITHUB_SHA": self.current, "GITHUB_WORKFLOW_SHA": self.current,
               "GITHUB_EVENT_NAME": event, **overrides}
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/sudu_pages_target.py"),
             "--target", self.current if target is None else target,
             "--branch-response", str(path)], cwd=self.repo, env=env,
            text=True, capture_output=True)

    def assert_hold(self, result, message):
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn(message, result.stderr)

    def test_fresh_main_push_and_manual_or_recovery_dispatch(self):
        for event in ("push", "workflow_dispatch"):
            with self.subTest(event=event):
                result = self.run_guard(event=event)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, self.current + "\n")

    def test_event_target_and_executing_workflow_must_agree(self):
        self.assert_hold(self.run_guard(self.previous, event="workflow_dispatch"),
                         "event and executing workflow commits")
        self.assert_hold(self.run_guard(GITHUB_WORKFLOW_SHA=self.previous),
                         "event and executing workflow commits")
        self.assert_hold(self.run_guard(self.current[:10]), "full lowercase")

    def test_main_push_and_retry_older_than_current_tip_hold(self):
        self.git("checkout", "--detach", self.previous)
        for event in ("push", "workflow_dispatch"):
            with self.subTest(event=event):
                self.assert_hold(self.run_guard(self.previous, event=event,
                    GITHUB_SHA=self.previous, GITHUB_WORKFLOW_SHA=self.previous), "stale")

    def test_target_not_in_main_history_is_rejected_using_real_git(self):
        self.git("checkout", "--detach", self.previous)
        self.git("commit", "--allow-empty", "-qm", "another branch commit")
        other = self.git("rev-parse", "HEAD")
        self.assert_hold(self.run_guard(other, event="workflow_dispatch",
            GITHUB_SHA=other, GITHUB_WORKFLOW_SHA=other), "not in the protected main history")

    def test_workflow_ref_and_protection_are_required(self):
        for updates in (
            {"GITHUB_REF": "refs/tags/main"},
            {"GITHUB_WORKFLOW_REF": gate.PAGES_WORKFLOW_REF.replace("pages.yml", "other.yml")},
            {"GITHUB_REF_PROTECTED": "false"},
            {"GITHUB_REPOSITORY": "other-owner/7581707"},
        ):
            with self.subTest(updates=updates):
                self.assert_hold(self.run_guard(**updates), "protected main workflow")
        self.assert_hold(self.run_guard(event="pull_request"), "protected main workflow")
        for flag in (False, None, 1, "true"):
            self.assert_hold(self.run_guard(branch={**self.branch, "protected": flag}),
                             "not confirmed that main is protected")

    def test_fetched_tip_race_and_wrong_checkout_hold(self):
        self.git("update-ref", "refs/remotes/origin/main", self.previous)
        self.assert_hold(self.run_guard(), "Fetched main differs")
        self.git("update-ref", "refs/remotes/origin/main", self.current)
        self.git("checkout", "--detach", self.previous)
        self.assert_hold(self.run_guard(), "Preflight did not check out")


class PagesWorkflowContractTests(unittest.TestCase):
    def test_preflight_gates_all_target_consumers(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text()
        parts = re.split(r"^  (target|verify|build|deploy|verify_live):\n",
                         workflow.split("\njobs:\n", 1)[1], flags=re.M)
        jobs = dict(zip(parts[1::2], parts[2::2]))
        target = jobs["target"]
        self.assertIn("github.ref == 'refs/heads/main'", target)
        self.assertIn("github.ref_protected", target)
        self.assertIn(gate.PAGES_WORKFLOW_REF, target)
        self.assertIn("ref: ${{ github.workflow_sha }}", target)
        self.assertIn('python -m scripts.sudu_pages_target --target "$REQUESTED_SHA"', target)
        self.assertIn("needs: target", jobs["verify"])
        self.assertIn("needs: [target, verify]", jobs["build"])
        self.assertIn("needs: [target, verify, build]", jobs["deploy"])
        self.assertIn("needs: [target, verify, build, deploy]", jobs["verify_live"])
        for name in ("verify", "build", "deploy", "verify_live"):
            self.assertNotIn("inputs.target_sha", jobs[name])
        for name in ("verify", "build", "verify_live"):
            self.assertIn("${{ needs.target.outputs.sha }}", jobs[name])
        self.assertLess(jobs["build"].index("scripts.sudu_pages_evidence"),
                        jobs["build"].index("actions/upload-pages-artifact"))

    def test_recovery_keeps_main_ref_and_rechecks_before_dispatch(self):
        recovery = (ROOT / ".github/workflows/sudu-verified-autopublish.yml").read_text()
        retry = recovery.split("\n            retry)\n", 1)[1].split(";;", 1)[0]
        self.assertIn('select(.name == "main" and .protected == true)', retry)
        self.assertLess(retry.index('[ "$MAIN_SHA" != "$CURRENT_MAIN" ]'),
                        retry.index('workflow run pages.yml --ref main -f target_sha="$MAIN_SHA"'))


if __name__ == "__main__":
    unittest.main()
