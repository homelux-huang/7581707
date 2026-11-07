"""Read-only, SHA-bound ROLE E Q12 source and review evidence. Never grants TRUST/READY."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QID = "114-00-E-12"
REV = "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
WEBP = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
G2_SHA = "8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc"
G3_SHA = "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"
G5_SHA = "6a9235ac6c1af701c9e414ec106ebc2e56b905ad3c61373041d5cb05b2f2714f"
DIR = ROOT / "sudu/data/processed/114/review-evidence/role-e-114-e12-20261107"
NOTES = DIR / "reviewer-notes.md"
ADDENDUM = DIR / "reviewer-addendum-g2-g3-20261107.md"
EVIDENCE = DIR / "independent-ai-review.json"
SOURCE = ROOT / "sudu/data/processed/114/questions.json"
IMAGE = ROOT / "sudu/data/processed/114/webp-v1/00-E/114-00-E-12.webp"
G2 = ROOT / "sudu/data/processed/114/review-evidence/114-00-E-12-ocr-publisher-20261107.json"
G3 = ROOT / "sudu/data/processed/114/review-evidence/114-00-E-12-official-publisher-20261107.json"
G5 = ROOT / "sudu/data/processed/114/review-evidence/114-00-E-12-teaching-publisher-20261107.json"

def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.e = json.loads(EVIDENCE.read_bytes())
        self.rows = json.loads(SOURCE.read_bytes())["questions"]
        self.q = next(x for x in self.rows if x.get("questionId")==QID)
        self.g2 = json.loads(G2.read_bytes())
        self.g3 = json.loads(G3.read_bytes())

    def test_source_and_real_original_image_bytes(self):
        self.assertEqual(len(self.rows),205)
        self.assertEqual(len({x["questionId"] for x in self.rows}),205)
        self.assertEqual(hashlib.sha256(IMAGE.read_bytes()).hexdigest(),WEBP)
        self.assertEqual(blob_sha(IMAGE.read_bytes()),self.e["webpGitBlob"])
        self.assertEqual(self.e["webpSha256"],WEBP)
        self.assertEqual(self.e["questionRevision"],REV)
        self.assertEqual(self.q["answer"],"C")
        self.assertIs(self.q["questionVerified"],True)
        self.assertIs(self.q["answerVerified"],True)

    def test_real_merged_g2_no_answer_exact_ocr(self):
        raw=G2.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),G2_SHA)
        self.assertEqual(blob_sha(raw),self.e["ocrEvidenceGitBlob"])
        self.assertEqual(self.e["ocrEvidenceSha256"],G2_SHA)
        self.assertEqual(self.e["ocrEvidenceByteLength"],len(raw))
        self.assertEqual(self.g2["questionId"],QID)
        self.assertEqual(self.g2["question"],self.q["question"])
        self.assertEqual(self.g2["options"],self.q["options"])
        self.assertEqual(self.g2["questionRevision"],REV)
        self.assertEqual(self.g2["webpSha256"],WEBP)
        self.assertNotIn("answer",self.g2)
        self.assertNotIn("finalAnswer",self.g2)
        self.assertIs(self.g2["independentBlindSolvePerformed"],False)

    def test_real_merged_g3_published_c_notice_scope(self):
        raw=G3.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),G3_SHA)
        self.assertEqual(blob_sha(raw),self.e["officialEvidenceGitBlob"])
        self.assertEqual(self.e["officialEvidenceSha256"],G3_SHA)
        self.assertEqual(self.e["officialEvidenceByteLength"],len(raw))
        self.assertEqual(self.g3["questionId"],QID)
        self.assertEqual(self.g3["sourceQuestionRevision"],REV)
        self.assertEqual(self.g3["sourceOriginalSingleWebpSha256"],WEBP)
        self.assertEqual(self.g3["finalAnswer"],"C")
        self.assertIs(self.g3["officialFinalAnswerImageQaPassed"],True)
        self.assertIs(self.g3["correctionNoticeReviewed"],True)
        self.assertIs(self.g3["noCorrectionForThisQuestion"],True)
        self.assertEqual(self.g3["namedOfficialCorrectionQuestionIds"],["114-00-E-26"])
        self.assertIs(self.g3["noObjectionForPaper"],False)
        self.assertIs(self.g3["independentRoleEContentReviewedThisTask"],False)

    def test_preserve_original_reviewer_notes_and_addendum(self):
        original=NOTES.read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(),self.e["reviewNotesSha256"])
        self.assertEqual(blob_sha(original),self.e["reviewNotesGitBlob"])
        self.assertEqual(blob_sha(ADDENDUM.read_bytes()),self.e["reviewAddendumGitBlob"])
        self.assertEqual(self.e["reviewNotesSha256"],"3ad64f45749ae501798d447b8ae5913b2cbf16e5ced807da7d528a42d99cce03")

    def test_four_explanations_and_same_digest(self):
        f=self.e["optionByOptionFindings"]
        self.assertEqual(set(f),{"A","B","C","D"})
        self.assertEqual(len(set(f.values())),4)
        self.assertTrue(all(len(x)>40 for x in f.values()))
        self.assertEqual(self.e["officialAnswerCandidate"],"C")
        self.assertEqual(self.e["teachingDigest"],"c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a")
        self.assertEqual(self.e["composedTeachingDigest"],"fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4")
        self.assertEqual(self.e["calculationReview"],"NOT_APPLICABLE_EXPLAINED")

    def test_ipa_exact_cambridge_phrase_and_no_author_rewrite(self):
        f=self.e["ipaFinding"]
        self.assertEqual(f["actualPr107"],f["officialCambridgeUS"])
        self.assertEqual(f["actualPr107"],"/ˈwɑː.t̬ɚ ˌbɑː.t̬ə l/")
        self.assertIn("dictionary.cambridge.org/pronunciation/english/water-bottle",f["officialSource"])
        self.assertIs(f["supersedesOldReviewWarning"],True)
        self.assertEqual(f["status"],"VERIFIED_CORRECT_EXACT_CAMBRIDGE_US_FULL_PHRASE_NO_AUTHOR_CHANGE")

    def test_actual_merged_author_teaching_issuer_bytes(self):
        raw = G5.read_bytes()
        self.assertEqual(len(raw), 3905)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), G5_SHA)
        self.assertEqual(blob_sha(raw), self.e["teachingEvidenceGitBlob"])
        self.assertEqual(self.e["teachingEvidenceSha256"], G5_SHA)
        self.assertEqual(self.e["teachingEvidenceByteLength"], len(raw))
        lesson = json.loads(raw)
        self.assertEqual(lesson["questionId"], QID)
        self.assertEqual(lesson["questionRevision"], REV)
        self.assertEqual(lesson["webpSha256"], WEBP)
        self.assertEqual(lesson["canonicalTeachingSha256"], self.e["teachingDigest"])
        self.assertEqual(lesson["composedTeachingSha256"], self.e["composedTeachingDigest"])
        self.assertEqual(lesson["sourceAuthorCommit"], self.e["authorHead"])
        self.assertEqual(lesson["sourceAuthorGitBlobSha1"], self.e["authorLessonGitBlob"])
        self.assertEqual(set(lesson["content"]["optionExplanations"]), set("ABCD"))
        self.assertIs(lesson["content"]["hasExamCalculation"], False)
        self.assertIsNone(lesson["content"]["examCalculation"])
        self.assertIs(lesson["independentAiContentReviewed"], False)
        self.assertIsNone(lesson["sourceAuthorSessionId"])
        self.assertIsNone(lesson["reviewerSessionId"])
        self.assertIs(lesson["studentReleaseApproved"], False)
        self.assertEqual(self.e["sourceCommit"], "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2")

    def test_no_forged_blind_solver_provenance_or_session_pass(self):
        self.assertIsNone(self.e["blindSolveOriginalTranscriptSha256"])
        self.assertIsNone(self.e["blindSolveOriginalTranscriptGitBlob"])
        self.assertIsNone(self.e["independentBlindSolveEvidence"])
        self.assertIs(self.e["independentBlindSolve"], False)
        self.assertIn("NO_ORIGINAL_VERBATIM_FIRST_ANSWER", self.e["blindSolveProvenanceStatus"])
        self.assertIn("NOT_ADMISSIBLE", self.e["externalExecutionAttestationStatus"])

    def test_user_paste_first_answer_exact_raw_bytes_and_g6_hold(self):
        raw_path = DIR / "user-pasted-first-answer-20261107.txt"
        metadata_path = DIR / "blind-candidate-intake-20261107.json"
        raw = raw_path.read_bytes()
        intake = json.loads(metadata_path.read_bytes())
        expected_sha = "6cb2694fa6a20e0b913972c6b0a3cf9c1af07bb9b712494fc0cb4d25314e75ff"
        expected_blob = "c673ae0acc0ba8a8080403abf996a21324e2cf90"
        self.assertEqual(len(raw), 311)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
        self.assertEqual(blob_sha(raw), expected_blob)
        self.assertEqual(intake["userPasteSha256"], expected_sha)
        self.assertEqual(intake["userPasteGitBlobSha1"], expected_blob)
        self.assertEqual(intake["userPasteByteLength"], len(raw))
        self.assertEqual(intake["questionId"], QID)
        self.assertEqual(intake["sourceQaCommit"], self.e["sourceCommit"])
        self.assertEqual(intake["sourceQuestionRevision"], REV)
        self.assertEqual(intake["webpSha256"], WEBP)
        self.assertEqual(intake["officialEvidenceSha256"], G3_SHA)
        self.assertEqual(intake["ocrEvidenceSha256"], G2_SHA)
        self.assertEqual(intake["canonicalTeachingSha256"], self.e["teachingDigest"])
        self.assertEqual(intake["teachingIssuerSha256"], G5_SHA)
        self.assertTrue(raw.decode("utf-8").startswith("題號：114-00-E-12\\n\\n首次作答"))
        self.assertIn("# C — That's why I always carry my own water bottle.", raw.decode("utf-8"))
        self.assertIn("信心： 99%", raw.decode("utf-8"))
        self.assertIn("官方答案核對： 尚未進行", raw.decode("utf-8"))
        self.assertFalse(intake["fullABCDOriginalFirstReplyReasoningPresent"])
        self.assertFalse(intake["originalFirstAssistantReplyEntireVerbatimAvailable"])
        self.assertFalse(intake["verifiedAnswerNaiveChronology"])
        self.assertFalse(intake["blindPass"])
        self.assertFalse(intake["independentBlindSolve"])
        self.assertIsNone(intake["originalSourceSessionId"])
        self.assertIsNone(intake["originalFirstAnswerTimestamp"])
        self.assertEqual(intake["g6Status"], "BLIND_SOLVE_NEW_INDEPENDENT_SESSION_REQUIRED")
        self.assertFalse(self.e["blindCandidateQualified"])
        self.assertEqual(self.e["blindCandidateUserPasteSha256"], expected_sha)

    def test_fail_closed_sessions_blind_ui_trust(self):
        self.assertIsNone(self.e["reviewerSessionId"])
        self.assertIsNone(self.e["sourceAuthorSessionId"])
        self.assertEqual(self.e["teachingEvidenceSha256"], G5_SHA)
        self.assertEqual(self.e["reviewedAt"],"2026-11-07T20:24:00Z")
        self.assertIs(self.e["independentBlindSolve"],False)
        self.assertIs(self.e["formalTrustedRegistryRegistered"],False)
        self.assertIs(self.e["studentReleaseApproved"],False)
        self.assertIs(self.e["ready"],False)
        self.assertIs(self.e["live"],False)
        self.assertIn("HOLD",self.e["status"])
        self.assertEqual(self.e["reviewClaimCommentId"],6710006916)
        self.assertEqual(self.e["reviewAddendumClaimCommentId"],6712534842)
        self.assertEqual(self.e["reviewReturnCommentId"],6712572797)
        self.assertEqual(self.e["reviewIssueCommentId"],6712572797)
        self.assertEqual(self.e["sourceCommit"], "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2")

if __name__=="__main__":
    unittest.main()
