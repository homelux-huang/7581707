"""The draft limit caps actual HTTP attempts, not only accepted model replies."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("teaching_cap_subject", ROOT / "scripts/tcte_teaching.py")
teaching = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(teaching)
FAKE_KEY = "SYNTHETIC_KEY_MUST_NOT_APPEAR_IN_LOGS"


class Response:
    def __init__(self, reply):
        self.reply = reply

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": json.dumps(self.reply)}}]}


def usable_reply():
    return {
        "unable": False,
        "topic": "Test topic",
        "explanation": "A complete example explanation.",
        "principle": "A complete example principle.",
        "steps": "A complete example calculation.",
        "wrongOptions": ["Choice A reason", "Choice B reason", "Choice C reason", "Choice D reason"],
        "extension": "A complete example extension.",
        "practice": {"question": "A complete example practice question?", "options": ["A", "B", "C", "D"],
                     "answerIndex": 0, "explanation": "A complete practice explanation."},
        "sourceNote": "Original-source example only.",
    }


class RequestCap(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        for year in (114, 115):
            self.seed(year, 40)

    def seed(self, year, count, eligible=True):
        questions = [{"year": year, "subject": "English", "paper": "test", "number": n,
                      "question": "An original example question?", "options": ["A", "B", "C", "D"],
                      "answer": 0, "questionVerified": eligible, "answerVerified": True}
                     for n in range(1, count + 1)]
        (self.directory / f"{year}.json").write_text(json.dumps({"papers": [{"paper": "test", "questions": questions}]}))

    def run_drafts(self, cap, reply=None, side_effect=None, api_key=FAKE_KEY):
        output = io.StringIO()
        with patch.object(teaching, "DIR", self.directory), patch.object(teaching, "API", api_key), \
                patch.object(teaching.time, "sleep"), \
                patch.object(teaching.requests, "post", return_value=Response(reply), side_effect=side_effect) as post, \
                patch("sys.argv", ["tcte_teaching.py", "--max-questions", str(cap), "--years", "114", "115"]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            teaching.main()
        self.assertNotIn(FAKE_KEY, output.getvalue())
        for call in post.call_args_list:
            self.assertIs(call.kwargs["allow_redirects"], False)
        return post.call_count, output.getvalue()

    def test_all_unable_replies_still_stop_at_request_cap(self):
        calls, output = self.run_drafts(2, {"unable": True})
        self.assertEqual(calls, 2)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 2 errors 0", output)

    def test_invalid_model_content_still_stops_at_request_cap(self):
        calls, output = self.run_drafts(3, {"unable": False, "explanation": "too short"})
        self.assertEqual(calls, 3)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 3 errors 0", output)

    def test_thirty_attempt_boundary_is_enforced_for_unusable_replies(self):
        calls, output = self.run_drafts(30, {"unable": True})
        self.assertEqual(calls, 30)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 30 errors 0", output)

    def test_transport_failures_count_and_never_log_exception_secret(self):
        calls, output = self.run_drafts(2, side_effect=RuntimeError(FAKE_KEY))
        self.assertEqual(calls, 2)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 2 errors 2", output)

    def test_existing_four_error_stop_remains_stricter_than_larger_cap(self):
        calls, output = self.run_drafts(10, side_effect=RuntimeError(FAKE_KEY))
        self.assertEqual(calls, 4)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 4 errors 4", output)

    def test_mixed_unable_invalid_exception_and_success_share_one_allowance(self):
        replies = [Response({"unable": True}), Response({}), RuntimeError(FAKE_KEY),
                   Response(usable_reply()), Response({"unable": True})]
        calls, output = self.run_drafts(5, side_effect=replies)
        self.assertEqual(calls, 5)
        self.assertIn("DRAFT_SUMMARY 1 request_attempts 5 errors 1", output)
        accepted = json.loads((self.directory / "114.json").read_text())["papers"][0]["questions"][3]
        self.assertEqual(accepted["teachingStatus"], "ai_draft_needs_verification")
        self.assertIs(accepted["teachingVerified"], False)
        self.assertNotIn("studentReleaseApproved", accepted)

    def test_cap_is_shared_across_years(self):
        self.seed(114, 2)
        calls, output = self.run_drafts(3, usable_reply())
        self.assertEqual(calls, 3)
        self.assertIn("DRAFT_SUMMARY 3 request_attempts 3 errors 0", output)

    def test_unusable_json_counts_as_attempt(self):
        malformed = Response(None)
        malformed.json = lambda: {"choices": [{"message": {"content": "not json"}}]}
        calls, output = self.run_drafts(3, side_effect=[malformed] * 3)
        self.assertEqual(calls, 3)
        self.assertIn("DRAFT_SUMMARY 0 request_attempts 3 errors 3", output)

    def test_no_key_or_no_eligible_questions_make_no_request(self):
        calls, _ = self.run_drafts(1, usable_reply(), api_key="")
        self.assertEqual(calls, 0)
        self.seed(114, 3, eligible=False)
        self.seed(115, 3, eligible=False)
        calls, output = self.run_drafts(1, usable_reply())
        self.assertEqual(calls, 0)
        self.assertIn("request_attempts 0", output)

    def test_out_of_range_cap_rejected_before_network(self):
        for cap in (-1, 0, 31):
            with self.subTest(cap=cap), self.assertRaises(SystemExit) as stopped:
                self.run_drafts(cap, usable_reply())
            self.assertEqual(stopped.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
