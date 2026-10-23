import unittest
from scripts.sudu_pages_recovery import decision


SHA = "a" * 40
OLD = "b" * 40


def run(sha=SHA, status="completed", conclusion="cancelled"):
    return {"head_sha": sha, "status": status, "conclusion": conclusion}


class PagesRecoveryTests(unittest.TestCase):
    def test_failed_or_cancelled_release_is_retried(self):
        for outcome in ("cancelled", "failure", "timed_out", "skipped"):
            self.assertEqual(decision(SHA, {"workflow_runs": [run(conclusion=outcome)]}), "retry")

    def test_empty_or_only_old_sha_is_retried(self):
        self.assertEqual(decision(SHA, {"workflow_runs": []}), "retry")
        self.assertEqual(decision(SHA, {"workflow_runs": [run(OLD, "completed", "success")]}), "retry")

    def test_exact_sha_in_progress_is_not_restarted(self):
        for stage in ("in_progress", "pending", "waiting", "requested", "queued"):
            self.assertEqual(decision(SHA, {"workflow_runs": [run(SHA, stage, None)]}), "active")

    def test_success_from_other_sha_never_counts(self):
        results = {"workflow_runs": [run(OLD, "completed", "success"),
                                     run(SHA, "completed", "failure")]}
        self.assertEqual(decision(SHA, results), "retry")

    def test_success_on_exact_sha_is_verified(self):
        self.assertEqual(decision(SHA, {"workflow_runs": [run(SHA, "completed", "success")]}), "verified")

    def test_active_same_sha_prevents_parallel_duplicate_dispatch(self):
        results = {"workflow_runs": [run(SHA, "in_progress", None),
                                     run(SHA, "completed", "cancelled")]}
        self.assertEqual(decision(SHA, results), "active")

    def test_malformed_api_response_fails_closed(self):
        for value in ({}, {"workflow_runs":None}, {"workflow_runs":[None]}):
            with self.assertRaises(ValueError):
                decision(SHA, value)
        with self.assertRaises(ValueError):
            decision("invalid", {"workflow_runs":[]})


if __name__=="__main__":
    unittest.main()
