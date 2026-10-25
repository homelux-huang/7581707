"""ROLE E independent PR57 adversarial review; SYNTHETIC fixtures, never a release.

This is deliberately a RED regression suite against frozen PR57 head 8c998e00.
Do not weaken assertions to obtain green checks. Independent AI QA is not an
author's PASS flag, a human teacher signature, or a GitHub account identity.
"""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sudu_independent_review_gate as gate

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "sudu/release-governance/independent-review-policy.json"
FIVE = {f"115-00-MB-{n:02d}" for n in (2, 3, 4, 5, 9)}


class EAdversarialPolicyBoundary(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.new_qid = "115-09-2-34"
        self.revision = "a" * 64
        self.webp = "b" * 64
        self.teaching = {
            "questionRevision": self.revision,
            "content": {"teacherSummary": "SYNTHETIC NOT A REAL TEACHING RECEIPT"},
        }
        self.raw = json.dumps(
            self.teaching, ensure_ascii=False, sort_keys=True
        ).encode("utf-8")

    def check(self, qid, trust):
        return gate.certified(
            ROOT, {}, {"year": 115, "questionId": qid},
            {"sha256": self.webp}, self.teaching, self.raw, policy=trust,
        )

    def synthetic_legacy(self):
        return {
            "year": 115,
            "questionRevision": self.revision,
            "webpSha256": self.webp,
            "teachingEvidenceGitBlob": gate.blob_oid(self.raw),
        }

    def test_current_policy_still_has_exactly_five_known_student_exceptions(self):
        self.assertEqual(set(self.policy["legacyAlreadyPublished"]), FIVE)
        self.assertEqual(self.policy["reviewMode"], "DISTINCT_AI_CONTENT_RECEIPT_V1")
        self.assertIs(self.policy["requireHumanTeacher"], False)
        self.assertEqual(self.policy["trustedAiReviewReceipts"], {})

    def test_current_new_question_is_denied_without_real_e_receipt(self):
        allowed, reason = self.check(self.new_qid, self.policy)
        self.assertFalse(allowed)
        self.assertEqual(reason, "distinct_ai_content_review_missing")

    def test_new_question_cannot_impersonate_sixth_historical_exception(self):
        """P0: a source-branch edited registry MUST NOT create a sixth legacy ID.

        The current implementation checks an arbitrary local legacy row before
        consulting protected main, so this is expected to FAIL on PR57.
        """
        fake = copy.deepcopy(self.policy)
        fake["legacyAlreadyPublished"][self.new_qid] = self.synthetic_legacy()
        allowed, reason = self.check(self.new_qid, fake)
        self.assertFalse(
            allowed,
            "P0: injected sixth 'legacy' row bypassed distinct E receipt: " + reason,
        )

    def test_existing_five_cannot_be_resealed_to_unreviewed_new_content(self):
        """P0: historical exceptions must be immutable, not policy-local labels."""
        historical = "115-00-MB-02"
        fake = copy.deepcopy(self.policy)
        fake["legacyAlreadyPublished"][historical] = self.synthetic_legacy()
        allowed, reason = self.check(historical, fake)
        self.assertFalse(
            allowed,
            "P0: historical qid accepted edited review/WebP/teaching triple: " + reason,
        )

    def test_role_e_return_casing_must_not_deny_valid_authenticity(self):
        """P1: normal 'Role E' and 'ROLE=E' are legitimate report spelling.

        Mocking isolates literal Issue36 body parsing only. All GitHub identity,
        issue, commit/tree, timestamp and material tokens are matched. This is
        NOT a real GitHub E approval or student receipt.
        """
        statement = {
            "reviewIssueCommentId": 900001,
            "sourceCommit": "f" * 40,
            "reviewTaskId": "E-SYNTHETIC-TEST-NO-APPROVAL",
            "reviewerSessionId": "separate-ai-session-123",
            "questionId": self.new_qid,
            "questionRevision": self.revision,
            "webpSha256": self.webp,
            "teachingDigest": "c" * 64,
            "officialEvidenceSha256": "d" * 64,
            "reviewedAt": "2026-10-24T01:00:00Z",
        }
        registry = {
            "reviewIssueCommentId": 900001,
            "sourceCommit": statement["sourceCommit"],
            "reviewerGithubUserId": 123456,
            "reviewerGithubLogin": "synthetic-e-actor",
        }
        body = "RETURN — Role E independent review, no release.\n" + "\n".join(
            str(statement[k]) for k in (
                "reviewTaskId", "reviewerSessionId", "questionId",
                "questionRevision", "webpSha256", "teachingDigest",
                "officialEvidenceSha256", "sourceCommit",
            )
        )
        comment = {
            "id": 900001,
            "issue_url": "https://api.github.com/repos/homelux-huang/7581707/issues/36",
            "user": {"id": 123456, "login": "synthetic-e-actor"},
            "created_at": "2026-10-24T02:00:00Z",
            "body": body,
        }
        commit = {
            "sha": "f" * 40,
            "commit": {"tree": {"sha": "a" * 40}},
        }
        def fake_github(path):
            if path == "/issues/comments/900001":
                return comment
            if path == "/commits/" + "f" * 40:
                return commit
            raise AssertionError("Unexpected remote lookup in synthetic fixture")

        with patch.object(gate, "_protected_main_trust_verified", return_value=True), \
                patch.object(gate, "_github_json", side_effect=fake_github):
            allowed, reason = gate._ai_real_issue36_return_verified(
                statement, registry
            )
        self.assertTrue(
            allowed,
            "P1: genuine attributable 'Role E' report falsely rejected: " + reason,
        )


if __name__ == "__main__":
    unittest.main()
