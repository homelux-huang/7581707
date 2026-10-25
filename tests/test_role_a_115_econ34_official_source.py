"""Role A ECON34 original official-source evidence receipt: read-only, NO RELEASE."""
import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
REVIEW = BASE / "review-evidence"
QID = "115-09-2-34"
SOURCE_SHA = "5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02"
PAGE_SHA = "defcfedf7cbc0f117d0731854efee59da41547716b0a88805454d9972da92ee5"
QUESTION_PDF_SHA = "fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e"
OFFICIAL_PDF_SHA = "6a2aacc705eb06edaf59c7ab6abe594763822e595e396bc0c279eef37235b9bc"
ANSWER_PAGE_SHA = "60482dbb1ac147d23e57b113790a1c2867c798a56e67611c5aa58c096c3cce67"
NOTICE_SHA = "b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133"
REVISION = "162c9a4f4d16d25e77a6c09034eb87f9a27b1b5775ac334274f6447c3c957cc8"

# Exact SHA-1 Git objects archived before official-key review; never regenerate as a new blind answer.
ORIGINAL_GIT_BLOBS = {
    "115-09-2-34-ocr.json": "5cd52d374259e1d808d4b12973e49f90e1058384",
    "115-09-2-34-official-visual-20261024.json": "ca8bbac18e2d39bfe0f0374ff40ce96ac961843f",
    "115-09-2-34-official.json": "1df0e78c2e38036923d47f39e8e9bb02558523c1",
    "115-09-2-34-blind-original-20261024.json": "a7e2c64f397c51be3db8457659ac5976ceb8a7af",
}

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def hex_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def check_image(rel, sha):
    p = ROOT / rel
    b = p.read_bytes()
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", rel
    assert hashlib.sha256(b).hexdigest() == sha, rel
    return len(b)

class Econ34SourceEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = read(BASE / "questions.json")
        cls.manifest = read(BASE / "webp-manifest.json")
        assert len(cls.bank["questions"]) == len(cls.manifest["items"]) == 205
        cls.byid = {q["questionId"]: q for q in cls.bank["questions"]}
        cls.images = {im["questionId"]: im for im in cls.manifest["items"]}
        assert len(cls.byid) == len(cls.images) == 205 and set(cls.byid) == set(cls.images)
        cls.q = cls.byid[QID]
        cls.image = cls.images[QID]
        cls.ocr = read(REVIEW / "115-09-2-34-ocr.json")
        cls.off = read(REVIEW / "115-09-2-34-official.json")
        cls.visual = read(REVIEW / "115-09-2-34-official-visual-20261024.json")
        cls.prekey = read(REVIEW / "115-09-2-34-blind-original-20261024.json")
        cls.notice = read(BASE / "QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json")
        cls.status = read(BASE / "official-confirmation-status.json")

    def test_four_original_documents_reused_byte_for_byte(self):
        for name, original_sha in ORIGINAL_GIT_BLOBS.items():
            with self.subTest(name=name):
                self.assertEqual(git_blob_sha(REVIEW / name), original_sha)

    def test_original_question_image_full_question_and_record(self):
        q, im = self.q, self.image
        self.assertEqual(q["questionId"], QID)
        self.assertEqual(q["year"], 115)
        self.assertEqual(q["paperCode"], im["paperCode"] == "09-2" and "09-2")
        self.assertEqual(q["originalQuestionNumber"], 34)
        self.assertEqual(q["subject"], "經濟學")
        self.assertEqual(len(q["options"]), 4)
        self.assertTrue("寡占市場中僅存在兩間廠商" in q["question"])
        self.assertEqual(q["question"], self.ocr["question"])
        self.assertEqual(q["options"], self.ocr["options"])
        self.assertEqual(im["qaStatus"], "PASS")
        self.assertEqual(im["sha256"], SOURCE_SHA)
        self.assertEqual(q["assets"]["sha256"], SOURCE_SHA)
        self.assertEqual(q["assets"]["singleQuestionWebp"], im["output"])
        self.assertEqual(self.ocr["sourceWebpPath"], im["output"])
        self.assertEqual(self.ocr["webpSha256"], SOURCE_SHA)
        self.assertEqual(im["sourcePdfSha256"], QUESTION_PDF_SHA)
        self.assertEqual(q["questionProvenance"]["pdfSha256"], QUESTION_PDF_SHA)
        self.assertEqual(im["sourceSha256"], PAGE_SHA)
        self.assertEqual(q["assets"]["sourceSha256"], PAGE_SHA)
        self.assertGreater(check_image(im["output"], SOURCE_SHA), 0)
        self.assertGreater(check_image(im["source"], PAGE_SHA), 0)
        self.assertEqual(im["visualReviewEvidence"]["reviewedSha256"], SOURCE_SHA)
        self.assertIs(im["visualReviewEvidence"]["independentHumanReview"], False)

    def test_exact_source_revision_not_mutated_by_past_blind_typo(self):
        q = self.q
        self.assertEqual(publisher.text_revision(q, SOURCE_SHA), REVISION)
        self.assertEqual(self.ocr["questionRevision"], REVISION)
        self.assertEqual(self.prekey["sourceQuestionTranscriptionFromOriginalImage"],
                         "假設人工智慧（AI）伺服器的寡占市場僅存在兩間廠商，下列敘述何者正確？")
        self.assertNotEqual(q["question"], self.prekey["sourceQuestionTranscriptionFromOriginalImage"])
        self.assertTrue(self.visual["preKeyTransparency"]["newBlindSolveAfterKeyClaimed"] is False)
        self.assertTrue(self.ocr["rawOcrPreserved"])
        self.assertIn("寡占市場中僅存在兩間廠商", q["question"])
        self.assertIn("寡占市場中僅存在兩間廠商", self.ocr["question"])
        self.assertIn("寡占市場中僅存在兩間廠商", self.visual["preKeyTransparency"]["correctedSourceImageTranscription"])

    def test_shas_of_official_answer_page_and_answer_pdf_record(self):
        q = self.q
        self.assertEqual(q["answer"], "A")
        self.assertEqual(q["acceptedAnswers"], ["A"])
        self.assertIs(q["answerMatched"], True)
        self.assertEqual(q["answerProvenance"]["pdfSha256"], OFFICIAL_PDF_SHA)
        self.assertEqual(self.off["officialPdfSha256"], OFFICIAL_PDF_SHA)
        self.assertEqual(self.visual["sourceAnswerPdfSha256"], OFFICIAL_PDF_SHA)
        self.assertEqual(self.visual["sourceAnswerPageWebpSha256"], ANSWER_PAGE_SHA)
        self.assertEqual(self.off["originalAnswerVisualSha256"], ANSWER_PAGE_SHA)
        self.assertEqual(self.off["finalAnswer"], "A")
        self.assertEqual(self.visual["officialFinalOptionReadVisually"], "A")
        self.assertGreater(check_image(self.visual["sourceAnswerPageWebpPath"], ANSWER_PAGE_SHA), 0)
        self.assertIs(self.off["originalHumanReviewClaimed"], False)
        self.assertIs(self.visual["sourceReleaseCertificate"], False)

    def test_notice_applies_only_09_2_06_28_44_not_34(self):
        notice = self.notice
        rec = self.status["confirmations"]["09-2"]
        self.assertEqual(notice["year"], 115)
        self.assertEqual(notice["sourceIndexUrl"], "https://web1.tcte.edu.tw/EXAM/115_4y/")
        self.assertIs(notice["allPagesInThreeDocumentsReviewed"], True)
        doc = next(row for row in notice["docs"] if row["paperCode"] == "09-2")
        self.assertEqual(doc["pdfSha256"], rec["revisionDocumentSha256"] == NOTICE_SHA and NOTICE_SHA)
        self.assertEqual(doc["pageCount"], 3)
        self.assertEqual({row["questionId"] for row in doc["confirmed"]},
                         {"115-09-2-06", "115-09-2-28", "115-09-2-44"})
        self.assertNotIn(QID, {row["questionId"] for row in doc["confirmed"]})
        self.assertEqual(self.off["confirmationPdfSha256"], NOTICE_SHA)
        self.assertFalse(self.off["noObjectionForPaper"])
        self.assertTrue(self.off["noCorrectionForThisQuestion"])
        self.assertFalse(self.off["correctionForQuestionReviewed"])
        self.assertTrue(publisher.official_notice_scope_certified(ROOT, 115, self.q, self.off))

    def test_wrong_notice_sha_and_incorrect_paper_wide_claim_rejected(self):
        scenarios = [
            {"confirmationPdfSha256": "0" * 64},
            {"noObjectionForPaper": True},
            {"noCorrectionForThisQuestion": False},
            {"correctionForQuestionReviewed": True},
            {"finalAnswer": "D", "correctionForQuestionReviewed": True},
        ]
        for mutate in scenarios:
            with self.subTest(mutate=mutate):
                proof = copy.deepcopy(self.off)
                proof.update(mutate)
                self.assertFalse(publisher.official_notice_scope_certified(ROOT, 115, self.q, proof))

    def test_canonical_db_matches_all_205_json_payloads_and_hashes(self):
        path = BASE / "question-bank.sqlite3"
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            col = {row[1] for row in db.execute("PRAGMA table_info(questions)")}
            field = "payload" if "payload" in col else "payload_json"
            self.assertTrue({"question_id", field, "payload_sha256"} <= col)
            rows = db.execute("SELECT question_id," + field + ",payload_sha256 FROM questions").fetchall()
            self.assertEqual(len(rows), 205)
        found = set()
        for qid, raw, digest in rows:
            self.assertNotIn(qid, found)
            found.add(qid)
            self.assertEqual(hashlib.sha256(raw.encode("utf-8")).hexdigest(), digest)
            self.assertEqual(json.loads(raw), self.byid[qid])
        self.assertEqual(found, set(self.byid))

    def test_no_new_approvals_and_no_ai_review_persona_promoted(self):
        q = self.q
        self.assertIs(q["questionVerified"], False)
        self.assertIs(q["answerVerified"], False)
        self.assertNotEqual(q.get("textQaStatus"), "PASS")
        self.assertIs(q["answerProvenance"]["officialRevisionChecked"], False)
        self.assertIs(self.prekey["studentReleaseApproved"], False)
        self.assertIs(self.prekey["officialComparisonNotPerformedYet"], True)
        self.assertFalse(self.visual["sourceReleaseCertificate"])
        self.assertIs(self.off["originalHumanReviewClaimed"], False)
        self.assertIs(self.ocr["studentReleaseApprovedInThisDocument"], False)
        revision = publisher.text_revision(q, SOURCE_SHA)
        self.assertEqual(publisher.source_proof(q, True, True, revision), (False, False))
        self.assertEqual(publisher.apply_independently_certified_review(ROOT, 115, q, self.image, None), q)

if __name__ == "__main__":
    unittest.main()
