"""Role D offline adversarial regressions, NEVER real review/UI admission.

Use the real AI verifier and publisher together. Only remote trust and official
notice services are simulated. No API key, real reviewer, or student data is
created; these synthetic receipts cannot enter the published source tree.
"""
import copy
import importlib.util
import json
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from scripts import sudu_independent_review_gate as gate
from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ai_contract_fixture", ROOT / "tests/test_sudu_ai_review_content_contract.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class AiPolicyQualityRegressions(unittest.TestCase):
    def setUp(self):
        # Reuse the already-tested receipt shape; never mock certified(True).
        self.f = fixtures.SeparateAiContentReceiptContract("runTest")
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        f = self.f
        f.q.update({
            "question": "SYNTHETIC: two tickets at 30 units each cost how much?",
            "options": ["30", "60", "90", "120"], "answerMatched": True,
            "questionProvenance": {"officialPdfSha256": "e" * 64},
        })
        self.revision = publisher.text_revision(f.q, f.asset["sha256"])
        f.lesson.update(questionRevision=self.revision, allFourOptionsReviewed=True,
                        calculationReviewed=True)
        f.lesson["content"].update({
            "memory": "Multiply unit price by count", "concept": "Multiplication",
            "extension": "Check with repeated addition", "source": "UNIT TEST ONLY",
            "hasExamCalculation": True, "calculationReviewed": True,
            "examCalculation": {"given": ["2 tickets", "30 units per ticket"],
                "formulaUse": "Total = price * count", "substitution": ["30 * 2"],
                "steps": ["30 + 30 = 60"], "result": "60", "unit": "units",
                "option": "B"},
        })
        for letter, row in f.lesson["content"]["optionExplanations"].items():
            row["reason"] = "Synthetic option " + letter + " checked against total"
        self.docs = {
            "ocr": {"questionRevision": self.revision, "webpSha256": f.asset["sha256"],
                    "question": f.q["question"], "options": f.q["options"],
                    "visualTextCompared": True},
            "official": json.loads((f.root / f.official_path).read_bytes()),
            "blind": {"questionRevision": self.revision, "webpSha256": f.asset["sha256"],
                      "officialAnswerHiddenDuringSolve": True, "solvedWithoutOfficialAnswer": True,
                      "answer": "B", "blindReasoning": "SYNTHETIC 30 + 30 = 60"},
            "teaching": f.lesson,
            "ui": {"testedQuestionRevision": self.revision,
                   "testedTeachingDigest": gate.digest(gate.canonical(f.lesson["content"])),
                   "browserSmokePassed": True, "rwdPassed": True, "verifiedYearQaMode": True,
                   "ciRunUrl": "https://github.com/homelux-huang/7581707/actions/runs/1"},
        }
        f.audit.update({"status": "STUDENT_QA_APPROVED", "questionId": f.q["questionId"],
            "year": 115, "questionBeforeReview": f.q["question"],
            "optionsBeforeReview": f.q["options"], "webpSha256": f.asset["sha256"],
            "officialPdfSha256": "d" * 64, "questionPdfSha256": "e" * 64,
            "originalAnswerCandidate": "B"})
        self.policy = json.loads((ROOT / "sudu/release-governance/independent-review-policy.json").read_bytes())
        self.reseal_lesson_review()

    def write_docs(self):
        f = self.f
        for name, doc in self.docs.items():
            doc.update(schemaVersion=1, year=115, questionId=f.q["questionId"],
                       reviewer="SYNTHETIC AI", reviewedAt="2026-10-24T14:00:00Z")
            rel = f.official_path if name == "official" else (
                "sudu/data/processed/115/review-evidence/synthetic-" + name + ".json")
            f.audit["evidence"][name] = rel
            f.write(rel, doc)
        f.teaching_raw = (f.root / f.audit["evidence"]["teaching"]).read_bytes()

    def reseal_lesson_review(self):
        self.write_docs()
        f = self.f
        f.statement.update(questionRevision=self.revision,
            teachingDigest=gate.digest(gate.canonical(f.lesson["content"])),
            teachingEvidenceSha256=gate.digest(f.teaching_raw),
            officialEvidenceSha256=gate.digest((f.root / f.official_path).read_bytes()))
        f.reseal()
        f.mock_comment = f.build_mock_comment()
        self.policy["trustedAiReviewReceipts"] = copy.deepcopy(f.registry)

    def apply(self):
        f = self.f
        with ExitStack() as stack:
            stack.enter_context(patch.object(gate, "policy_from_trusted_main", return_value=self.policy))
            stack.enter_context(patch.object(gate, "_ai_registry_exactly_matches_protected_main_policy", return_value=True))
            stack.enter_context(patch.object(gate, "_github_json", side_effect=f.mock_github))
            stack.enter_context(patch.object(publisher, "official_notice_scope_certified", return_value=True))
            # Any accidental dependency on teacher APPROVED/signing fails loudly.
            stack.enter_context(patch.object(gate, "_author_and_github_review_verified",
                                            side_effect=AssertionError("Teacher path used")))
            return publisher.apply_independently_certified_review(f.root, 115, f.q, f.asset, f.audit)

    def assert_rejected(self):
        result = self.apply()
        self.assertTrue(result is self.f.q, "invalid new admission was promoted")
        self.assertNotIn("studentReleaseApproved", result)

    def test_complete_ai_chain_has_no_teacher_roster_or_signature_dependency(self):
        self.assertIs(self.policy["requireHumanTeacher"], False)
        self.assertNotIn("authorizedReviewers", self.policy)
        result = self.apply()
        self.assertIsNot(result, self.f.q)
        self.assertIs(result["studentReleaseApproved"], True)
        self.assertTrue(publisher.teaching_complete(result, "數學 B", "B"))

    def test_missing_ui_teaching_digest_rejected(self):
        self.docs["ui"].pop("testedTeachingDigest")
        self.write_docs()
        self.assert_rejected()

    def test_old_ui_digest_rejected_even_after_valid_new_ai_review(self):
        old_digest = self.docs["ui"]["testedTeachingDigest"]
        self.f.lesson["content"]["elementarySummary"] += " A NEW example needing browser QA."
        self.reseal_lesson_review()  # stronger case: the new AI content review is valid
        self.assertNotEqual(old_digest, self.f.statement["teachingDigest"])
        self.assert_rejected()

    def test_source_image_or_revision_mutation_is_not_covered_by_ai_pass(self):
        self.f.asset["sha256"] = "f" * 64
        self.assert_rejected()

    def test_forged_self_review_is_rejected_in_actual_publisher_path(self):
        self.f.statement["reviewerSessionId"] = self.f.statement["sourceAuthorSessionId"]
        self.f.reseal()
        self.policy["trustedAiReviewReceipts"] = copy.deepcopy(self.f.registry)
        self.assert_rejected()

    def test_changed_calculation_without_new_independent_review_is_rejected(self):
        self.f.lesson["content"]["examCalculation"]["steps"] = ["30 + 30 = 90 (WRONG)"]
        self.write_docs()  # do not reseal the independent review
        self.assert_rejected()

    def test_changed_official_answer_cannot_be_resealed_into_agreement(self):
        self.docs["official"]["finalAnswer"] = "C"
        self.reseal_lesson_review()
        self.assert_rejected()

    def test_table_deletion_invalidates_existing_source_revision(self):
        self.f.q["originalSourceTableCandidate"] = {
            "heading": "UNIT TEST TABLE", "rows": [["count", "price"], ["2", "30"]]}
        self.assertNotEqual(publisher.text_revision(self.f.q, self.f.asset["sha256"]), self.revision)
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
