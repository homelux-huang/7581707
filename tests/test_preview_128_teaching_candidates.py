"""Synthetic, isolated false-release prevention for frozen teaching candidates."""
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_preview_128_teaching_candidates.py"
SPEC = importlib.util.spec_from_file_location("preview128_candidates", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class PerQuestionReleaseSafety(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.asset = self.root / "sudu/data/approved/webp/115/115-00-MB-02.webp"
        self.asset.parent.mkdir(parents=True)
        self.asset.write_bytes(b"synthetic-webp-placeholder-only")
        img_sha = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.teach = {"hasExamCalculation": True,
                      "examCalculation": {"substitutionAndSteps": ["2+2=4"], "result": "4"},
                      "optionExplanations": {
                          k: {"teacher": "Specific algebraic reason " + k,
                              "elementary": "Reason for child " + k,
                              "isCorrect": k == "A"}
                          for k in "ABCD"}}
        self.item = {"questionId": "115-00-MB-02", "year": 115,
                     "image": "data/approved/webp/115/115-00-MB-02.webp",
                     "imageSha256": img_sha}
        self.record = {"questionId": "115-00-MB-02", "year": 115,
                       "image": self.item["image"], "imageSha256": img_sha,
                       "aiAnswer": "A", "answerComparison": {
                           "officialAnswer": "A", "officialFinalCorrectionVerified": True,
                           "conflictWarningRequired": False},
                       "qa": {"officialFinalEvidence": {"officialFinalCorrectionVerified": True},
                              "independentTeachingReview": "PASS",
                              "uiReview": "PASS", "textHighlightRendering": "PASS"},
                       "studentReleaseApproved": False, "deploy": False,
                       "teaching": self.teach}
        self.official = {"officialAnswer": "A"}
        p = self.root / "evidence" / "review.md"
        p.parent.mkdir()
        p.write_text("Synthetic QA only")
        self.proof = {"result": "PASS", "reviewer": "Synthetic fixture",
                      "reviewedAt": "2026-10-23", "path": "evidence/review.md",
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        ui_path = self.root / "evidence" / "ui-browser.md"
        ui_path.write_text("Synthetic browser viewport and interaction evidence")
        self.ui_proof = dict(self.proof, path="evidence/ui-browser.md",
                             reviewer="Synthetic UI reviewer",
                             sha256=hashlib.sha256(ui_path.read_bytes()).hexdigest())
        self.cert = {"questionId": "115-00-MB-02", "status": "QA_APPROVED",
                     "releaseApproved": True, "officialAnswer": "A",
                     "originalImageSha256": img_sha,
                     "teachingDigestSha256": gate.teaching_digest(self.teach),
                     "teachingReviewEvidence": self.proof, "uiReviewEvidence": self.ui_proof,
                     "textbookUnknownClearlyLabeled": True,
                     "rwdResults": {theme: {d: "PASS" for d in gate.RWD}
                                    for theme in ("light", "dark")},
                     "interactionChecks": {k: True for k in gate.INTERACTIONS}}

    def check(self, reason, certificate=None):
        blockers = gate.assess_record(self.item, self.record, self.official,
                                     self.cert if certificate is None else certificate,
                                     self.root)
        self.assertIn(reason, blockers, blockers)

    def test_synthetic_complete_certificate_can_be_eligible_only_in_fixture(self):
        self.assertEqual(gate.assess_record(self.item, self.record, self.official,
                                            self.cert, self.root), [])

    def test_missing_or_false_certificate_is_never_approved(self):
        self.assertIn("release_certificate_absent",
                      gate.assess_record(self.item, self.record, self.official, None, self.root))
        self.cert["releaseApproved"] = False
        self.check("release_certificate_not_bound_to_question_content")

    def test_same_document_for_teaching_and_ui_is_rejected(self):
        self.cert["uiReviewEvidence"] = self.proof
        self.check("teaching_and_ui_evidence_not_independent")

    def test_identical_content_digest_even_different_paths_rejected(self):
        second = self.root / "evidence" / "duplicate-review.md"
        second.write_bytes((self.root / "evidence" / "review.md").read_bytes())
        self.cert["uiReviewEvidence"] = dict(
            self.proof, path="evidence/duplicate-review.md",
            reviewer="Synthetic UI reviewer")
        self.check("teaching_and_ui_evidence_not_independent")

    def test_ai_official_disagreement_is_isolated_even_with_certificate(self):
        self.record["aiAnswer"] = "D"
        self.check("ai_literal_official_disagreement")

    def test_prior_changed_answer_still_blocks_even_if_now_matches(self):
        self.record["answerComparison"]["conflictWarningRequired"] = True
        self.check("historic_disagreement_or_unresolved_warning")

    def test_malformed_warning_flag_not_falsely_accepted(self):
        self.record["answerComparison"]["conflictWarningRequired"] = "false"
        self.check("historic_disagreement_or_unresolved_warning")

    def test_teaching_change_invalidates_certificate_sha(self):
        self.teach["optionExplanations"]["B"]["teacher"] = "Changed after review"
        self.check("release_certificate_not_bound_to_question_content")

    def test_missing_visual_sha_or_fake_evidence_rejected(self):
        self.cert["uiReviewEvidence"] = dict(self.proof, sha256="f" * 64)
        self.check("review_evidence_not_sha_verified")

    def test_missing_one_mobile_dark_viewport_rejected(self):
        self.cert["rwdResults"]["dark"]["390x844"] = "PENDING"
        self.check("eight_viewports_or_theme_qa_pending")

    def test_missing_real_student_interaction_rejected(self):
        self.cert["interactionChecks"]["memory_dismiss_restore"] = False
        self.check("student_interactions_qa_pending")

    def test_incomplete_four_options_or_incorrect_option_rejected(self):
        self.teach["optionExplanations"]["A"]["isCorrect"] = False
        self.check("four_option_content_or_answer_mismatch")

    def test_draft_release_flags_must_remain_closed(self):
        self.record["deploy"] = True
        self.check("draft_release_isolation_modified")


if __name__ == "__main__":
    unittest.main()
