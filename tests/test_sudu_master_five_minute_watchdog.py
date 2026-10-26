"""Fail-closed tests for the 7581707 read-only five-minute watchdog."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sudu_master_five_minute_watchdog.py"
spec = importlib.util.spec_from_file_location("watchdog_under_test", SCRIPT)
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)
SHA = "a" * 40
TASK = "E-PR57-EXACT-AI-PUBLISHER-SECURITY-20261025-18"


class TestFiveMinuteMasterWatchdog(unittest.TestCase):
    def test_dispatch_comment_is_not_agent_claim(self):
        comments = [{
            "id": 1, "body": "MASTER DISPATCH role E should claim taskId: " + TASK
        }]
        self.assertEqual(watchdog.events_from_comments(comments), {})

    def test_explicit_claim_never_means_runner_active(self):
        comments = [{"id": 4, "body": "CLAIMED — taskId: " + TASK}]
        r = watchdog.make_report(SHA, {}, comments, {}, "now")
        entry = next(x for x in r["workQueue"] if x["taskId"] == TASK)
        self.assertEqual(entry["state"], "CLAIM_RECORDED_NOT_PROOF_RUNNING")
        self.assertEqual(entry["issueEvidence"]["commentId"], 4)

    def test_return_never_promotes_ready(self):
        comments = [
            {"id": 4, "body": "CLAIMED — taskId: " + TASK},
            {"id": 6, "body": "RETURN — taskId **" + TASK + "**; CI SUCCESS, NO RELEASE"}
        ]
        r = watchdog.make_report(SHA, {}, comments, {}, "now")
        e = next(x for x in r["workQueue"] if x["taskId"] == TASK)
        self.assertEqual(e["state"], "RETURN_RECORDED_REVIEW_PENDING")
        self.assertEqual(r["release"]["newReady"], "NOT_VERIFIED")
        self.assertTrue(r["release"]["neverApproveMergeOrDeploy"])

    def test_unknown_sha_fails_closed(self):
        with self.assertRaises(ValueError):
            watchdog.make_report("last_known_head", {}, [], {}, "now")
        with self.assertRaises(ValueError):
            watchdog.make_report(SHA, {}, [], {57: {"head": {"sha": "bad"}}}, "now")

    def test_queued_roles_stay_queued_without_signed_evidence(self):
        r = watchdog.make_report(SHA, {"comments": 0}, [], {}, "now")
        self.assertEqual({x["role"] for x in r["workQueue"]}, {"A", "B", "C", "D", "E"})
        self.assertTrue(all(x["state"] == "QUEUED_NOT_ACKNOWLEDGED"
                            for x in r["workQueue"]))
        self.assertEqual(r["release"]["independentEQA"], "NOT_VERIFIED")
        self.assertEqual(r["release"]["newLive"], "NOT_VERIFIED")
        self.assertIn("Not an AI worker", watchdog.summary_markdown(r))

    def test_no_104_115_legacy_count_promoted_to_qa(self):
        r = watchdog.make_report(SHA, {}, [], {}, "now")
        rendered = json.dumps(r, ensure_ascii=False)
        self.assertNotIn("LIVE_VERIFIED", rendered)
        self.assertNotIn("answerVerified=true", rendered)
        self.assertEqual(r["kind"], "READ_ONLY_COORDINATION_NOT_AGENT_EXECUTION")


    def test_real_issue_claim_and_return_formats_are_seen(self):
        samples = [
            {"id": 7, "body": "CLAIM — taskId A-113-C11-15-SHARED-READING-20261025-13"},
            {"id": 8, "body": "CLAIMED — B-114-C16-C18-THREE-LAMPS-20261025-10"},
            {"id": 9, "body": "RETURN — **A-113-C11-15-SHARED-READING-20261025-13** real QA, NOT READY"},
            {"id": 10, "body": "**RETURN** — taskId: B-114-C16-C18-THREE-LAMPS-20261025-10"},
            {"id": 11, "body": "\ufeff### CLAIMED — taskId: E-PR80-IMMUTABLE-BOUNDARY-REAUDIT-20261025"},
            {"id": 12, "body": "MASTER DISPATCH should CLAIMED — taskId: C-115-FAKE-ASSIGNMENT-20261025-01"},
        ]
        events = watchdog.events_from_comments(list(reversed(samples)))
        self.assertEqual(len(events), 3, "dispatch and embedded CLAIM must not become ACK")
        self.assertEqual(events["A-113-C11-15-SHARED-READING-20261025-13"]["event"], "RETURN")
        self.assertEqual(events["B-114-C16-C18-THREE-LAMPS-20261025-10"]["event"], "RETURN")
        self.assertEqual(events["E-PR80-IMMUTABLE-BOUNDARY-REAUDIT-20261025"]["event"], "CLAIM")
        self.assertNotIn("C-115-FAKE-ASSIGNMENT-20261025-01", events)

    def test_dynamic_open_pr_80_and_new_task_events_are_visible(self):
        comments = [{"id": 3, "body": "CLAIM — taskId E-PR80-IMMUTABLE-BOUNDARY-REAUDIT-20261025"}]
        pulls = {80: {"head": {"sha": SHA}, "state": "open",
                      "draft": True, "base": {"ref": "governance/ai-gate"}}}
        result = watchdog.make_report(SHA, {"comments": 1}, comments, pulls, "now")
        self.assertIn("80", result["pullRequests"])
        self.assertEqual(result["openPullRequestCount"], 1)
        self.assertEqual(result["recentActualTaskEvents"][0]["role"], "E")
        self.assertEqual(result["recentActualTaskEvents"][0]["state"], "CLAIM_RECORDED_NOT_PROOF_RUNNING")
        self.assertEqual(result["release"]["newMain"], "NOT_VERIFIED")
        self.assertTrue(result["release"]["neverApproveMergeOrDeploy"])

    def test_api_open_pr_pagination_and_incomplete_payload_fail_closed(self):
        from unittest.mock import patch
        paths = []
        def fake_api(path, token):
            paths.append(path)
            self.assertEqual(token, "fake-auth-token")
            return [{"number": 80, "head": {"sha": SHA}}]
        with patch.object(watchdog, "api_get", side_effect=fake_api):
            results = watchdog.get_open_pulls("/repos/homelux-huang/7581707/pulls", "fake-auth-token")
        self.assertEqual([p["number"] for p in results], [80])
        self.assertIn("state=open", paths[0])
        self.assertIn("per_page=100", paths[0])
        with patch.object(watchdog, "api_get", return_value={"error": "partial"}):
            with self.assertRaises(ValueError):
                watchdog.get_open_pulls("/repos/homelux-huang/7581707/pulls", "fake-auth-token")

    def test_task_comment_text_never_exposes_content_or_claims_independence(self):
        item = {"id": 9, "body": "CLAIMED — taskId: E-PR80-BOUNDARY-SECURITY-20261025\napi-key dummy not a secret"}
        result = watchdog.make_report(SHA, {}, [item], {}, "now")
        text_value = json.dumps(result)
        self.assertNotIn("api-key dummy", text_value)
        self.assertNotIn("APPROVED", text_value)
        self.assertEqual(result["release"]["independentEQA"], "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
