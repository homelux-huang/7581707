"""Source-only immutable 115 Chinese Q06 WebP, official final-answer and QA receipts.

No OCR, crop, AI blind solve, independent teacher or student release performed.
"""
import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path
from PIL import Image
from scripts import sudu_verified_publish as publisher

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
QID="115-00-C-06"
IMAGE_PATH="sudu/data/processed/115/webp-v2/00-C/115-00-C-06.webp"
IMAGE_GIT_SHA="f351e496fe61b8b5a358bf2d4d8054876021fa4e"
IMAGE_SHA="f031f108b2805bffd737479bb019a682439db5ef31bf1e8082b8a65c4942691c"
PAGE_SHA="08ae32b6b9e6633aa60f2f60321045cd10c5402ee80562e4603d2477ab13eeba"
QUESTION_PDF_SHA_RECORDED="6b454d65902f2fb326b1ac1ae28aa44749532e30369ba2c599db97d20a542135"
ANSWER_PDF_SHA_RECORDED="ec9871b659d81726de5b6412ed5252d62541afb287951b5d6cf923c1ea763e64"
ANSWER_PAGE_SHA="5422c00920ef4f18fa32fffd51c7edb78acd80aac84974713a61e2a02987126f"
CONFIRM_PDF_SHA_RECORDED="231f21ac52bb1006717ec6a17b325454a37269317a1f49944dbfd0a31d28c4c0"
SOURCE_REVISION="d072001630c98baa5ce22cc4939fe01149cc96345e1c89960ee0efbc09f625ba"
QA_IMAGE="QA_115_C_Q06_Q11_15_DIRECT_VISUAL_20261023.json"
QA_OFFICIAL="QA_115_C_6_FINAL_OFFICIAL_ANSWERS_20261023.json"
IMAGE_QA_GIT="fca5b8e9e16b390f245c93caeb420b4b86f97f60"
OFFICIAL_QA_GIT="250ed2949b54099ee86511e0d1c4bcf69f33c9be"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def git_blob_sha(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def verify_webp(relative, digest, size):
    raw=(ROOT/relative).read_bytes()
    assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP",relative
    assert sha(raw)==digest, "image bytes not original: "+relative
    with Image.open(ROOT/relative) as image:
        assert image.format=="WEBP"
        image.load()
        assert image.size==tuple(size), (relative,image.size,size)
    return len(raw)

class C06OriginalAndOfficialReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bank=load(BASE/"questions.json")
        manifest=load(BASE/"webp-manifest.json")
        cls.qmap={r["questionId"]:r for r in bank["questions"]}
        cls.imap={r["questionId"]:r for r in manifest["items"]}
        assert len(bank["questions"])==len(cls.qmap)==len(manifest["items"])==len(cls.imap)==205
        assert set(cls.qmap)==set(cls.imap)
        cls.q=cls.qmap[QID]
        cls.im=cls.imap[QID]
        cls.image_qa_file=BASE/QA_IMAGE
        cls.answer_qa_file=BASE/QA_OFFICIAL
        cls.imageqa=load(cls.image_qa_file)
        cls.answerqa=load(cls.answer_qa_file)
        cls.irow=next(r for r in cls.imageqa["items"] if r["questionId"]==QID)
        cls.arow=next(r for r in cls.answerqa["records"] if r["questionId"]==QID)

    def test_reuse_real_original_single_webp_exact_git_and_sha_byte_decode(self):
        data=(ROOT/IMAGE_PATH).read_bytes()
        self.assertEqual(git_blob_sha(data),IMAGE_GIT_SHA)
        self.assertGreater(verify_webp(IMAGE_PATH,IMAGE_SHA,[1220,325]),0)
        self.assertEqual(self.im["output"],IMAGE_PATH)
        self.assertEqual(self.im["sha256"],IMAGE_SHA)
        self.assertEqual(self.q["assets"]["sha256"],IMAGE_SHA)
        self.assertEqual(self.q["assets"]["singleQuestionWebp"],IMAGE_PATH)
        self.assertEqual(self.im["qaStatus"],"PASS")
        self.assertEqual(self.q["imageQaStatus"],"PASS")

    def test_page_three_and_official_question_pdf_provenance_without_new_pdf_download(self):
        q,im=self.q,self.im
        self.assertEqual(q["year"],115)
        self.assertEqual(q["paperCode"],"00-C")
        self.assertEqual(q["originalQuestionNumber"],6)
        self.assertEqual(im["paperCode"],"00-C")
        self.assertEqual(im["sourcePage"],3)
        self.assertEqual(q["questionProvenance"]["sourcePage"],3)
        self.assertEqual(q["questionProvenance"]["pdfSha256"],QUESTION_PDF_SHA_RECORDED)
        self.assertEqual(im["sourcePdfSha256"],QUESTION_PDF_SHA_RECORDED)
        self.assertEqual(im["sourceSha256"],PAGE_SHA)
        self.assertEqual(q["assets"]["sourceSha256"],PAGE_SHA)
        self.assertEqual(im["crop"],[90,157,1310,482])
        self.assertEqual(q["assets"]["cropCoordinates"],im["crop"])
        self.assertGreater(verify_webp(im["source"],PAGE_SHA,[1400,1981]),0)

    def test_two_original_unchanged_git_qa_ledgers_and_no_batch_promotion(self):
        self.assertEqual(git_blob_sha(self.image_qa_file.read_bytes()),IMAGE_QA_GIT)
        self.assertEqual(git_blob_sha(self.answer_qa_file.read_bytes()),OFFICIAL_QA_GIT)
        self.assertIs(self.imageqa["independentHumanReview"],False)
        self.assertIs(self.answerqa["independentHumanReview"],False)
        self.assertIs(self.imageqa["releaseAllowed"],False)
        self.assertIs(self.answerqa["releaseAllowed"],False)
        self.assertEqual(self.imageqa["answerVerifiedAdded"],0)
        self.assertEqual(self.imageqa["questionVerifiedAdded"],0)
        self.assertEqual(self.answerqa["finalAnswerVerifiedAdded"],6)
        self.assertEqual(self.answerqa["questionVerifiedAdded"],0)
        self.assertEqual(self.answerqa["ocrTextVerifiedAdded"],0)
        self.assertEqual(self.answerqa["teachingVerifiedAdded"],0)

    def test_individual_visual_qa_matches_sha_and_original_image_with_four_choices(self):
        r=self.irow
        self.assertEqual(r["sourcePage"],3)
        self.assertEqual(r["sourcePageSha256"],PAGE_SHA)
        self.assertEqual(r["reviewedWebpPath"],IMAGE_PATH)
        self.assertEqual(r["reviewedWebpSha256"],IMAGE_SHA)
        self.assertEqual(r["reviewedWebpSize"],[1220,325])
        self.assertEqual(r["cropPixels"],[90,157,1310,482])
        self.assertEqual(r["result"],"PASS")
        self.assertTrue(all(r["criteria"].values()))
        self.assertIs(r["answerVerified"],False) # image stage, separate from official answer stage
        self.assertIs(r["questionVerified"],False)
        self.assertIs(r["independentHumanReview"],False)
        q=self.q
        self.assertEqual(len(q["options"]),4)
        self.assertTrue(all(isinstance(v,str) and v.strip() for v in q["options"]))
        self.assertEqual(publisher.text_revision(q,IMAGE_SHA),SOURCE_REVISION)

    def test_exact_original_official_answer_image_and_correction_scope_not_paper_wide(self):
        qa=self.arow
        self.assertEqual(qa["candidateValue"],"B")
        self.assertEqual(qa["officialPublishedFinalAnswer"],"B")
        self.assertEqual(qa["officialPublishedAnswerImageSha256"],ANSWER_PAGE_SHA)
        self.assertEqual(qa["officialPublishedAnswerSourcePdfSha256"],ANSWER_PDF_SHA_RECORDED)
        self.assertEqual(qa["officialConfirmationDocumentSha256"],CONFIRM_PDF_SHA_RECORDED)
        self.assertTrue(qa["officialCorrectionChecked"])
        self.assertTrue(qa["officialFinalAnswerImageDirectVisualChecked"])
        self.assertTrue(qa["candidateMatchedOfficialAnswer"])
        self.assertTrue(qa["answerVerified"]) # historical scoped original answer check
        self.assertFalse(qa["questionVerified"])
        self.assertEqual(qa["officialNoticeStatus"],"NO_ENTRY_IN_FULL_10_PAGE_00_C_CONFIRMATION_PDF")
        path=self.answerqa["originalFinalAnswerPageWebp"]
        self.assertGreater(verify_webp(path,ANSWER_PAGE_SHA,[1400,1980]),0)
        with self.assertRaises(AssertionError):
            verify_webp(path,ANSWER_PAGE_SHA,[1400,1981])  # rejected wrong height
        official=load(BASE/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json")
        doc=next(x for x in official["docs"] if x["paperCode"]=="00-C")
        self.assertEqual(doc["pdfSha256"],CONFIRM_PDF_SHA_RECORDED)
        self.assertEqual({v["questionId"] for v in doc["confirmed"]},
                         {"115-00-C-12","115-00-C-16","115-00-C-18",
                          "115-00-C-23","115-00-C-24","115-00-C-34"})
        self.assertNotIn(QID,{v["questionId"] for v in doc["confirmed"]})

    def test_no_new_ocr_or_question_verification_promotion_and_legacy_visual_flag(self):
        q=self.q
        self.assertEqual(q["answer"],"B")
        self.assertTrue(q["answerVerified"]) # existed prior; this task DOES NOT change it
        self.assertEqual(q["officialFinalAnswer"],"B")
        self.assertTrue(q["officialCorrectionChecked"])
        self.assertFalse(q["questionVerified"])
        self.assertFalse(q["integrationReady"])
        self.assertEqual(q["extraction"]["ocrReviewStatus"],"PENDING_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(q["assets"]["visualQa"],"PENDING_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(q["imageQaStatus"],"PASS")
        self.assertEqual(q["answerQaEvidence"],"sudu/data/processed/115/"+QA_OFFICIAL)
        self.assertEqual(q["assets"]["imageQaEvidence"],"sudu/data/processed/115/"+QA_IMAGE)
        self.assertIsNot(q.get("studentReleaseApproved"),True)
        self.assertEqual(publisher.source_proof(q,True,True,SOURCE_REVISION),(False,False))
        approved=load(ROOT/"sudu/data/approved/115.json")
        self.assertEqual(approved["approvedCount"],5)
        self.assertNotIn(QID,{x["canonicalId"] for x in approved["questions"]})

    def test_strict_source_digest_changes_on_wrong_image_or_option(self):
        with self.assertRaises(AssertionError):
            verify_webp(IMAGE_PATH,"0"*64,[1220,325])
        with self.assertRaises(AssertionError):
            verify_webp(IMAGE_PATH,IMAGE_SHA,[1220,326])
        q=copy.deepcopy(self.q)
        q["options"][0]="tampered answer choice"
        self.assertNotEqual(publisher.text_revision(q,IMAGE_SHA),SOURCE_REVISION)
        self.assertNotEqual(publisher.text_revision(self.q,"0"*64),SOURCE_REVISION)

    def test_205_sqlite_rows_exactly_same_json_and_record_hash(self):
        path=BASE/"question-bank.sqlite3"
        with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            cols={r[1] for r in con.execute("PRAGMA table_info(questions)")}
            col="payload" if "payload" in cols else "payload_json"
            self.assertTrue({"question_id",col,"payload_sha256"}<=cols)
            rows=con.execute("SELECT question_id,"+col+",payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({x[0] for x in rows},set(self.qmap))
        for qid,payload,digest in rows:
            with self.subTest(qid=qid):
                self.assertEqual(sha(payload.encode("utf-8")),digest)
                self.assertEqual(json.loads(payload),self.qmap[qid])

if __name__=="__main__":
    unittest.main()
