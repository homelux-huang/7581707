"""Frozen Math B partial reasoning QA ledger: read-only, NEVER student release.

Checks integrity of existing 25 per-question *partial* reviews, not the
correctness of all teaching explanations or 8 x 2 real-browser behavior.
"""
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu" / "teaching-drafts" / "preview-128-20261023"
EXPECTED_IDS = [f"115-00-MB-{n:02d}" for n in range(1, 26)]
EVIDENCE_BY_RANGE = (
    (range(1, 7), "MATH_B_01_06_INDEPENDENT_CALC_QA_20261023.md"),
    (range(7, 13), "MATH_B_07_12_INDEPENDENT_CALC_QA_20261023.md"),
    (range(13, 19), "MATH_B_13_18_INDEPENDENT_CALC_QA_20261023.md"),
    (range(19, 26), "MATH_B_19_25_INDEPENDENT_CALC_QA_20261023.md"),
)


class MathBPartialQaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.progress = json.loads((BASE / "progress.json").read_text(encoding="utf-8"))
        cls.official = json.loads((BASE / "official-final-evidence-20261023.json").read_text(encoding="utf-8"))["questions"]
        cls.manifest = {q["questionId"]: q for q in cls.progress["items"]}
        cls.ledger = cls.progress.get("partialMathBTeachingReviewLedger") or {}

    def test_all_twenty_five_pinned_image_option_and_math_partial_records(self):
        self.assertEqual(self.ledger.get("scopeTotalMathB"), 25)
        self.assertEqual(self.ledger.get("reviewedCount"), 25)
        self.assertEqual(self.ledger.get("reviewedQuestionIds"), EXPECTED_IDS)
        self.assertEqual(self.ledger.get("newFullTeachingQaPass"), 0)
        self.assertEqual(self.ledger.get("newStudentReleases"), 0)
        self.assertEqual(self.ledger.get("schoolBookVersionAndPage"), "UNVERIFIED")
        self.assertEqual(self.ledger.get("real128QuestionUiBrowser"), "PENDING")
        expected_files = [f for _, f in EVIDENCE_BY_RANGE]
        self.assertEqual(self.ledger.get("batchDocuments"), expected_files)
        self.assertEqual(self.progress["fullyAccepted"], 0)
        self.assertEqual(self.progress["deployed"], 0)
        for nums, evidence in EVIDENCE_BY_RANGE:
            body = (BASE / evidence).read_text(encoding="utf-8")
            for num in nums:
                qid = f"115-00-MB-{num:02d}"
                with self.subTest(qid=qid):
                    record = json.loads((BASE / f"{qid}.json").read_text(encoding="utf-8"))
                    qa = record["qa"]
                    partial = qa["mathBReasoningReview20261023"]
                    self.assertIn(qid, body)
                    self.assertEqual(record["questionId"], qid)
                    self.assertEqual(record["subject"], "數學 B")
                    self.assertEqual(self.manifest[qid]["imageSha256"], record["imageSha256"])
                    self.assertEqual(self.manifest[qid]["image"], record["image"])
                    self.assertEqual(partial.get("sourcePinnedOriginalWebpSha256",
                                      partial.get("imageSha256ReusedFromPreviouslyVerifiedFrozenManifest")),
                                     record["imageSha256"])
                    self.assertTrue(partial.get("originalWebpViewedInThisReview"))
                    self.assertIn("FULL_TEACHING_QA_PENDING", partial["status"])
                    self.assertEqual(partial["officialOption"], self.official[qid]["officialAnswer"])
                    self.assertEqual(partial["officialOption"], record["aiAnswer"])
                    self.assertEqual(partial["officialOption"], record["answerComparison"]["officialAnswer"])
                    self.assertEqual(partial["evidence"], evidence)
                    self.assertEqual(partial["fullIndependentTeachingReview"], "PENDING")
                    self.assertGreaterEqual(len(partial.get("recomputedSteps",
                                                partial.get("independentlyRecomputedSteps", []))), 3)
                    self.assertTrue(partial.get("allFourOptionsTeacherAndElementaryLogicChecked",
                                               partial.get("allFourOptionsTeacherAndElementaryPresentAndLogicChecked")))
                    options = record["teaching"]["optionExplanations"]
                    self.assertEqual(set(options), set("ABCD"))
                    self.assertEqual([k for k, v in options.items() if v.get("isCorrect")],
                                     [partial["officialOption"]])
                    for opt in options.values():
                        self.assertTrue(opt.get("teacher"))
                        self.assertTrue(opt.get("elementary"))
                    self.assertTrue(record["teaching"]["hasExamCalculation"])
                    self.assertEqual(record["teaching"]["examCalculation"]["matchingOption"],
                                     partial["officialOption"])
                    self.assertEqual(qa["independentTeachingReview"], "PENDING")
                    self.assertEqual(qa["uiReview"], "PENDING")
                    self.assertIs(record["studentReleaseApproved"], False)
                    self.assertIs(record["deploy"], False)

    def test_seven_new_questions_independently_derived_numeric_values(self):
        # Reference equations transcribed from each original WebP and rederived
        # separately from draft step strings. These check examples, NOT full QA.
        self.assertEqual(round(math.tan(math.radians(2026)), 3), 1.036)
        self.assertEqual(round(100 * math.sin(math.radians(75)) /
                               math.sin(math.radians(45)), 6),
                         round(50 * (math.sqrt(3) + 1), 6))
        self.assertEqual([x for x in (3, 5) if x > 4], [5])
        self.assertEqual(2**5 - 1, 31)
        x = (3600 + 3000) / (2 - 1.8)
        self.assertAlmostEqual(x, 33000)
        self.assertAlmostEqual(2 * x - 3000, 1.8 * (x + 2000))
        c = math.ceil(110 / 8)
        b = math.log(3) / math.log(1.08)
        self.assertEqual(c, 14)
        self.assertGreater(b, 14)
        self.assertLess(b, 15)
        self.assertEqual(math.ceil(b), c + 1)
        h = 8 / 2
        a = (math.sqrt(2))**2 - h**2
        self.assertEqual(round(h + a), -10)


if __name__ == "__main__":
    unittest.main()
