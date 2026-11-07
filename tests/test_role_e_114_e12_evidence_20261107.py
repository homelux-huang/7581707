"""Read-only, fail-closed ROLE E Q12 evidence checks. This does NOT grant trusted receipt."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QID = "114-00-E-12"
REV = "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
WEBP = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
NOTES = ROOT / "sudu/data/processed/114/review-evidence/role-e-114-e12-20261107/reviewer-notes.md"
EVIDENCE = ROOT / "sudu/data/processed/114/review-evidence/role-e-114-e12-20261107/independent-ai-review.json"
SOURCE = ROOT / "sudu/data/processed/114/questions.json"
IMAGE = ROOT / "sudu/data/processed/114/webp-v1/00-E/114-00-E-12.webp"

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.e = json.loads(EVIDENCE.read_bytes())
        self.rows = json.loads(SOURCE.read_bytes())["questions"]
        self.q = next(x for x in self.rows if x.get("questionId") == QID)

    def test_original_webp_real_bytes(self):
        self.assertEqual(hashlib.sha256(IMAGE.read_bytes()).hexdigest(), WEBP)
        self.assertEqual(self.e["webpSha256"], WEBP)
        self.assertEqual(self.q["questionId"], QID)

    def test_source_bank_still_explicit_not_released(self):
        self.assertEqual(len(self.rows), 205)
        self.assertEqual(len({x["questionId"] for x in self.rows}), 205)
        self.assertEqual(self.q["answer"], "C")
        self.assertIs(self.q["questionVerified"], True)
        self.assertIs(self.q["answerVerified"], True)
        self.assertEqual(self.e["questionRevision"], REV)
        self.assertIs(self.e["studentReleaseApproved"], False)
        self.assertIs(self.e["ready"], False)
        self.assertIs(self.e["live"], False)

    def test_exact_notes_bytes_and_git_blob(self):
        raw = NOTES.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.e["reviewNotesSha256"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
        self.assertEqual(blob, self.e["reviewNotesGitBlob"])

    def test_distinct_four_option_review(self):
        f = self.e["optionByOptionFindings"]
        self.assertEqual(set(f), {"A","B","C","D"})
        self.assertEqual(len(set(f.values())), 4)
        self.assertTrue(all(len(x)>40 for x in f.values()))
        self.assertEqual(self.q["options"], [
          "No wonder I prefer buying plastic containers.",
          "So I keep using plastic straws for all my drinks.",
          "That’s why I always carry my own water bottle.",
          "And I make sure to throw away everything I buy.",
        ])
        self.assertEqual(self.e["officialAnswerCandidate"], "C")
        self.assertEqual(self.e["calculationReview"], "NOT_APPLICABLE_EXPLAINED")

    def test_do_not_forge_distinct_session_or_blind_or_trust(self):
        self.assertIsNone(self.e["reviewerSessionId"])
        self.assertIsNone(self.e["sourceAuthorSessionId"])
        self.assertIsNone(self.e["officialEvidenceSha256"])
        self.assertIsNone(self.e["teachingEvidenceSha256"])
        self.assertIsNone(self.e["reviewedAt"])
        self.assertIs(self.e["independentBlindSolve"], False)
        self.assertIs(self.e["formalTrustedRegistryRegistered"], False)
        self.assertIn("HOLD", self.e["status"])
        self.assertEqual(self.e["reviewIssueCommentId"], 6710031408)
        self.assertIn("AUTHOR_CONFIRMATION_REQUIRED", self.e["ipaFinding"]["status"])

if __name__ == "__main__":
    unittest.main()
