"""114 E11 original Role B content issuer — fail-closed, author-only, no student release."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# QA source intentionally does not contain protected-main's publisher.
# In CI load the exact read-only main SHA's publisher from a runner temp file.
publisher_path = os.environ.get("PUBLISHER_CHECKER_PATH")
if not publisher_path or not Path(publisher_path).is_file():
    raise RuntimeError("Exact protected-main publisher not supplied by CI")
spec = importlib.util.spec_from_file_location("role_b_pinned_main_publisher", publisher_path)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

QID = "114-00-E-11"
BANK = ROOT / "sudu/data/processed/114"
REL = "sudu/data/processed/114/review-evidence/114-00-E-11-teaching-publisher-20261113.json"
G2 = BANK / "review-evidence/114-00-E-11-ocr-publisher-20261107.json"
G3 = BANK / "review-evidence/114-00-E-11-official-publisher-20261107.json"
REV = "646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036"
WEBP = "ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0"
TEACH = "ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb"
COMPOSED = "3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee"
RAW_AUTHOR = "6b365291eb43fd37377891149470f3bff9d8a6db5997eaff13295fb36fc402e8"
SOURCE_G2 = "f8d316fcf6c44dbce476f394e5537692ea7b45bf957dd2187c547e74bae5c034"
SOURCE_G3 = "e767d4c5eb60dced6b2a86b73b29167b8d7b47430925da60f13a1bb6c7c8cbbf"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class TestRoleB114E11Issuer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read(ROOT / REL)
        cls.question_rows = read(BANK / "questions.json")["questions"]
        cls.manifest_rows = read(BANK / "webp-manifest.json")["items"]
        cls.q = next(x for x in cls.question_rows if x["questionId"] == QID)
        cls.m = next(x for x in cls.manifest_rows if x["questionId"] == QID)
        cls.g2 = read(G2)
        cls.g3 = read(G3)

    def test_real_native_review_document_and_pinned_author_sha(self):
        t = self.doc
        native = publisher.review_document(ROOT, 114, REL, QID)
        self.assertIsNotNone(native)
        self.assertEqual(native[0], t)
        self.assertEqual(native[1], sha((ROOT / REL).read_bytes()))
        self.assertEqual((t["schemaVersion"], t["year"], t["questionId"]), (1, 114, QID))
        self.assertEqual((t["questionRevision"], t["webpSha256"]), (REV, WEBP))
        self.assertEqual(t["sourceAuthorRole"], "B")
        self.assertEqual(t["sourceAuthorTaskId"], "B-114-NEXT5-E11-E14-C04-20261025-02")
        self.assertEqual(t["sourceAuthorPrUrl"], "https://github.com/homelux-huang/7581707/pull/44")
        self.assertEqual(t["sourceAuthorCommit"], "e0d4532c751127204e73af9cd9d3a95c52449131")
        self.assertEqual(t["sourceAuthorGitBlobSha1"], "a4aa8df70cf3f3fa8c4f62a568d73fe90511154b")
        self.assertEqual(t["sourceAuthorRawSha256"], RAW_AUTHOR)
        self.assertEqual(t["canonicalTeachingSha256"], sha(canonical(t["content"])))
        self.assertEqual(t["canonicalTeachingSha256"], TEACH)
        self.assertEqual(t["composedTeachingSha256"], COMPOSED)

    def test_exact_official_source_205_and_original_webp(self):
        t, q, m = self.doc, self.q, self.m
        self.assertEqual(len(self.question_rows), 205)
        self.assertEqual(len(self.manifest_rows), 205)
        self.assertEqual(len(set(x["questionId"] for x in self.question_rows)), 205)
        self.assertEqual(len(set(x["questionId"] for x in self.manifest_rows)), 205)
        self.assertIs(q["questionVerified"], True)
        self.assertIs(q["answerVerified"], True)
        self.assertEqual((q["answer"], q["officialFinalAnswer"]), ("A", "A"))
        self.assertEqual(m["qaStatus"], "PASS")
        self.assertEqual(m["sha256"], WEBP)
        self.assertEqual(sha((ROOT / m["output"]).read_bytes()), WEBP)
        self.assertEqual(publisher.text_revision(q, WEBP), REV)
        self.assertEqual((self.g2["questionRevision"], self.g2["webpSha256"]), (REV, WEBP))
        self.assertEqual((self.g2["question"], self.g2["options"]), (q["question"], q["options"]))
        self.assertTrue(self.g2["sourceQuestionAndFourOptionsExactMatch"])
        self.assertEqual(self.g3["finalAnswer"], "A")
        self.assertEqual(self.g3["sourceQuestionRevision"], REV)
        self.assertTrue(publisher.official_notice_scope_certified(ROOT, 114, q, self.g3))
        self.assertEqual(sha(G2.read_bytes()), t["sourceG2Sha256"])
        self.assertEqual(sha(G3.read_bytes()), t["sourceG3Sha256"])
        self.assertEqual((t["sourceG2Sha256"], t["sourceG3Sha256"]), (SOURCE_G2, SOURCE_G3))

    def test_all_four_distinct_teacher_elementary_highlights_and_no_calculation(self):
        t = self.doc
        c = t["content"]
        self.assertEqual(set(c["optionExplanations"]), set("ABCD"))
        self.assertTrue(t["allFourOptionsReviewed"] and t["calculationReviewed"])
        self.assertEqual(sum(v["isCorrect"] for v in c["optionExplanations"].values()), 1)
        self.assertEqual([k for k, v in c["optionExplanations"].items() if v["isCorrect"]], ["A"])
        reasons = set()
        for letter in "ABCD":
            v = c["optionExplanations"][letter]
            self.assertGreater(len(v["teacher"].strip()), 20)
            self.assertGreater(len(v["elementary"].strip()), 9)
            self.assertGreater(len(v["reason"].strip()), 20)
            reasons.add(v["reason"])
        self.assertEqual(len(reasons), 4)
        self.assertGreater(len(c["teacherSummary"]), 20)
        self.assertGreater(len(c["elementarySummary"]), 20)
        self.assertEqual(c["hasExamCalculation"], False)
        self.assertIsNone(c["examCalculation"])
        corpus = (self.q["question"] + " " + " ".join(self.q["options"])).casefold()
        self.assertEqual({x["text"] for x in t["sourceHighlights"]},
                         {"use the phone too much", "hurt your eyes", "use it less", "jogging"})
        for x in t["sourceHighlights"]:
            self.assertIs(x["bold"], True)
            self.assertIs(x["highlight"], True)
            self.assertIn(x["text"].casefold(), corpus)

    def test_negative_stale_source_content_and_issuer_mismatch(self):
        self.assertIsNone(publisher.review_document(ROOT, 114, REL, "114-00-E-12"))
        t = copy.deepcopy(self.doc)
        t["content"]["optionExplanations"]["A"]["teacher"] = "An altered answer would be invalid"
        self.assertNotEqual(sha(canonical(t["content"])), TEACH)
        bad_q = copy.deepcopy(self.q)
        bad_q["options"][0] = "changed source option"
        self.assertNotEqual(publisher.text_revision(bad_q, WEBP), REV)
        bad_g3 = copy.deepcopy(self.g3)
        bad_g3["finalAnswer"] = "B"
        self.assertNotEqual(bad_g3["finalAnswer"], self.q["answer"])
        self.assertNotEqual(sha(canonical(dict(self.doc["content"], examCalculation={}))), TEACH)
        self.assertIsNone(publisher.review_document(ROOT, 114, "../../wrong.json", QID))

    def test_author_only_never_role_e_trust_or_student_release(self):
        t = self.doc
        self.assertEqual(t["status"], "AUTHOR_CONTENT_ISSUED_IN_QA_NOT_E_TRUST_NOT_UI_NOT_READY")
        self.assertIs(t["independentAiContentReviewed"], False)
        self.assertIsNone(t["sourceAuthorSessionId"])
        self.assertIsNone(t["reviewerSessionId"])
        self.assertIs(t["studentReleaseApproved"], False)
        self.assertNotEqual(self.q["reviewStatus"], "STUDENT_QA_APPROVED")
        approved = read(BANK / "approved.json") if (BANK / "approved.json").is_file() else {}
        self.assertNotIn(QID, json.dumps(approved, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
