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


if __name__ == "__main__":
    unittest.main()
