"""Synthetic unit fixtures only; NEVER actual independent AI reviewer approval.

The inactive reviewer-contract verifier is tested for exact material changes and
role separation. An in-test allowlist is NOT an authorized real QA receipt.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import sudu_independent_review_gate as gate


class SeparateAiContentReceiptContract(unittest.TestCase):
    def setUp(self):
        self.root_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.root_tmp.cleanup)
        self.root = Path(self.root_tmp.name)
        prefix = "sudu/data/processed/115/review-evidence/"
        self.official_path = prefix + "115-MB23-official.json"
        self.ai_path = prefix + "115-MB23-independent-ai.json"
        self.notes_path = prefix + "115-MB23-independent-ai.md"
        self.q = {"year": 115, "questionId": "115-00-MB-23", "answer": "B"}
        self.asset = {"sha256": "a" * 64}
        self.lesson = {
            "questionRevision": "b" * 64,
            "content": {"teacherSummary": "Explains all source conditions and correct answer",
                        "elementarySummary": "The same idea in primary school language",
                        "optionExplanations": {x: {"teacher": "reason", "elementary": "why"} for x in "ABCD"}},
        }
        self.teaching_raw = json.dumps(self.lesson, ensure_ascii=False).encode("utf-8")
        self.audit = {"evidence": {"official": self.official_path},
                      "independentAiContentEvidence": self.ai_path}
        self.write(self.official_path, {"questionId": self.q["questionId"],
                                        "finalAnswer": "B", "source": "UNIT_TEST_NOT_OFFICIAL"})
        self.write_bytes(self.notes_path, b"115 MB23 unit test independent findings, source table, source revision and exact four options. Not real QA.")
        self.statement = {
            "schemaVersion": 1, "year": 115, "questionId": self.q["questionId"],
            "questionRevision": "b" * 64, "webpSha256": "a" * 64,
            "teachingDigest": gate.digest(gate.canonical(self.lesson["content"])),
            "teachingEvidenceSha256": gate.digest(self.teaching_raw),
            "officialEvidenceSha256": gate.digest((self.root / self.official_path).read_bytes()),
            "officialAnswerCandidate": "B",
            "sourceAuthorSessionId": "role-c-author-20261025",
            "reviewerSessionId": "role-e-reviewer-20261025",
            "sourceAuthorTaskId": "C-115-UNIT-FIXTURE",
            "reviewTaskId": "E-115-UNIT-FIXTURE",
            "sourceAuthorRole": "C", "reviewerRole": "E",
            "reviewIssueNumber": 36, "reviewIssueCommentId": 123456789,
            "sourceCommit": "c" * 40, "reviewedAt": "2026-10-24T14:00:00Z",
            "optionByOptionFindings": {
                "A": "Option A conflicts with the original two-row travel fare table.",
                "B": "Option B satisfies both discounted total-fee equalities.",
                "C": "Option C yields two different payments and must be rejected.",
                "D": "Option D violates the discounted passenger arithmetic."},
            "teacherAndElementaryReviewed": True,
            "correctAnswerComparedToOfficial": True,
            "officialCorrectionsReviewed": True,
            "calculationReview": "APPLICABLE_ALL_STEPS_CHECKED",
            "reviewNotesPath": self.notes_path,
            "reviewNotesSha256": gate.digest((self.root / self.notes_path).read_bytes()),
        }
        self.reseal()

    def write_bytes(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def write(self, path, doc):
        self.write_bytes(path, gate.canonical(doc))

    def reseal(self):
        self.write(self.ai_path, self.statement)
        raw = (self.root / self.ai_path).read_bytes()
        s = self.statement
        self.registry = {self.q["questionId"]: {
            "evidencePath": self.ai_path,
            "evidenceGitBlobSha": gate.blob_oid(raw),
            "reviewTaskId": s["reviewTaskId"],
            "reviewerSessionId": s["reviewerSessionId"],
            "sourceAuthorSessionId": s["sourceAuthorSessionId"],
            "questionRevision": s["questionRevision"],
            "webpSha256": s["webpSha256"],
            "teachingDigest": s["teachingDigest"],
            "officialEvidenceSha256": s["officialEvidenceSha256"],
            "reviewNotesSha256": s["reviewNotesSha256"],
        }}

    def verify(self, registry=None):
        return gate.separate_ai_content_receipt_verified(
            self.root, self.audit, self.q, self.asset,
            self.lesson, self.teaching_raw,
            trusted_receipts=self.registry if registry is None else registry)

    def test_valid_synthetic_contract_only_not_publisher_admission(self):
        self.assertEqual(self.verify(),
                         (True, "distinct_ai_content_receipt_exact_registry_and_material_match"))
        # Old publisher still requires its own trusted policy and full G0-G10.
        legacy = {"schemaVersion": 1, "githubRepository": gate.REPO,
                  "requireHumanTeacher": True, "authorizedReviewers": {},
                  "legacyAlreadyPublished": {}}
        allowed, why = gate.certified(self.root, self.audit, self.q,
                                       self.asset, self.lesson, self.teaching_raw,
                                       policy=legacy)
        self.assertIs(allowed, False)
        self.assertEqual(why, "not_independently_attested")

    def test_unregistered_or_changed_review_blob_rejected(self):
        self.assertEqual(self.verify({})[1], "separate_ai_reviewer_trusted_receipt_absent")
        self.statement["optionByOptionFindings"]["B"] += " Untrusted editing."
        self.write(self.ai_path, self.statement)  # trust registry deliberately NOT resealed
        self.assertEqual(self.verify()[1], "ai_review_receipt_not_trusted_or_modified")

    def test_author_cannot_self_review_even_if_blob_registered(self):
        self.statement["reviewerSessionId"] = self.statement["sourceAuthorSessionId"]
        self.reseal()  # stronger adversarial case: even pre-registered copy rejected
        self.assertEqual(self.verify()[1], "ai_review_author_or_reviewer_not_distinct")
        self.statement["reviewerSessionId"] = "role-e-reviewer-20261025"
        self.statement["reviewerRole"] = "C"
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_author_or_reviewer_not_distinct")

    def test_revision_webp_teaching_or_official_sha_tamper_rejected(self):
        mutations = [
            lambda: self.q.update(answer="A"),
            lambda: self.asset.update(sha256="d" * 64),
            lambda: self.lesson.update(questionRevision="e" * 64),
            lambda: self.lesson["content"].update(teacherSummary="changed author lesson"),
            lambda: self.write(self.official_path, {"questionId": self.q["questionId"],
                                                     "finalAnswer": "C"}),
        ]
        for change in mutations:
            with self.subTest(mutation=mutations.index(change)):
                self.setUp()
                change()
                self.assertFalse(self.verify()[0])

    def test_omitted_or_duplicate_or_generic_four_option_findings_rejected(self):
        self.statement["optionByOptionFindings"] = {k: "same generic explanation repeated across all four options" for k in "ABCD"}
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_four_distinct_substantive_option_findings_missing")
        self.statement["optionByOptionFindings"].pop("D")
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_four_distinct_substantive_option_findings_missing")

    def test_fake_answer_check_or_shortened_math_review_rejected(self):
        self.statement["officialCorrectionsReviewed"] = False
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_required_teaching_or_answer_checks_missing")
        self.statement["officialCorrectionsReviewed"] = True
        self.statement["calculationReview"] = "SKIP_MATH"
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_required_teaching_or_answer_checks_missing")

    def test_edited_notes_or_fake_comment_and_task_id_rejected(self):
        self.write_bytes(self.notes_path, b"changed false notes")
        self.assertEqual(self.verify()[1], "ai_review_substantive_notes_not_sha_bound")
        self.write_bytes(self.notes_path, b"115 MB23 unit test independent findings, source table, source revision and exact four options. Not real QA.")
        self.statement["reviewIssueCommentId"] = "123456789"
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_traceability_missing")
        self.statement["reviewIssueCommentId"] = 123456789
        self.statement["reviewTaskId"] = "C-pretending-to-be-E"
        self.reseal()
        self.assertEqual(self.verify()[1], "ai_review_author_or_reviewer_not_distinct")

    def test_invalid_path_or_missing_report_rejected(self):
        self.audit["independentAiContentEvidence"] = "../../outside.json"
        self.assertEqual(self.verify()[1], "ai_review_evidence_path_untrusted")
        self.audit["independentAiContentEvidence"] = (
            "sudu/data/processed/115/review-evidence/missing-report.json")
        self.assertEqual(self.verify()[1], "ai_review_evidence_missing")


if __name__ == "__main__":
    unittest.main()
