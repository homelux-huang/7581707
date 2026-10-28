"""ROLE A 114 English Q11 source pixel + printed stem/options immutable receipt.

This does not approve authored B lesson, E reviewer, new questionVerified,
formal student READY or main/Pages; complete-source original PDF bytes were not
redownloaded by this batch. Existing PR94 205-row original DB is read-only.
"""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

from PIL import Image, ImageChops
from scripts import sudu_verified_publish as publisher

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
QID="114-00-E-11"
EVIDENCE=BASE/"review-evidence/114-00-E-11-source-text-20261028.json"
QPATH=BASE/"questions.json"
MFPATH=BASE/"webp-manifest.json"
DB=BASE/"question-bank.sqlite3"
ORIGINAL=ROOT/"sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp"
SINGLE=ROOT/"sudu/data/processed/114/webp-v1/00-E/114-00-E-11.webp"
ANSWER_PAGE=ROOT/"sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp"
LEGACY=ROOT/"sudu/data/years/114.json"
ORIGINAL_QA=BASE/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
ORIGINAL_ANSWER=BASE/"review-evidence/114-00-E-11-official.json"
NOTICE=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
ORIGINAL_PAGE_SHA="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
SINGLE_SHA="ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0"
ORIGINAL_PAGE_GIT="5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
SINGLE_GIT="50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a"
ANSWER_PAGE_SHA="a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
SOURCE_REV="646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036"
SRC_PDF_PREVIOUS="1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf"
NOTICE_PDF_PREVIOUS="79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"
OPTIONS=[
"Then I should use it less.",
"Should I use a new phone?",
"Do you like to watch videos, too?",
"So you should play online games.",
]
STEM=("Dad:  Hey, you’re always on your phone!\n"
      "    Son:   I know. I just like playing games and watching videos.\n"
      "   Dad:  But if you use the phone too much, you might hurt your eyes.\n"
      "    Son:  ____________\n"
      "   Dad:  Yeah, let’s go jogging. It’s more fun.")
EXPECTED_PINS={
"sudu/data/processed/114/questions.json":"1535754345a08d25636e00b4ba3270a1f764bf66",
"sudu/data/processed/114/webp-manifest.json":"249a41d5a64558ccaa3084b21f915922a55c6a1b",
"sudu/data/processed/114/question-bank.sqlite3":"27314572b3d18fd0bd20003297bccadbc6c59737",
"sudu/data/years/114.json":"1e2e82854e7041011733eb2d3ab21c3d5c6e0a04",
"sudu/data/processed/114/review-evidence/114-00-E-11-official.json":"bc3d19885e2ebc3d27092b673636bd84c89f65c6",
"sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json":"c1154562fa30cb4b2720a6000a970cf09ef460ff",
}
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def gitblob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
def canonical(q): return json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))

class RoleA114E11ActualOriginalSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=read(EVIDENCE)
        cls.bank=read(QPATH)
        cls.qs={q["questionId"]:q for q in cls.bank["questions"]}
        assert len(cls.bank["questions"])==len(cls.qs)==205
        cls.q=cls.qs[QID]
        cls.man=next(m for m in read(MFPATH)["items"] if m["questionId"]==QID)
        cls.old=next(q for q in read(LEGACY)["papers"]
                     if q["paper"]=="00-E")["questions"][10]
        cls.archiveQa=next(q for q in read(ORIGINAL_QA)["items"] if q["questionId"]==QID)
        cls.answer=read(ORIGINAL_ANSWER)
    def test_exact_original_archived_blob_sha_and_pdf_provenance_not_new_pdf_qa(self):
        e=self.doc
        self.assertEqual(e["questionId"],QID)
        self.assertEqual(e["role"],"A")
        self.assertEqual(e["reviewerType"],
            "AI_SOURCE_IMAGE_AND_STRUCTURED_TEXT_EXAMINER_NOT_ROLE_E_TEACHING_REVIEWER")
        p=e["historicalOriginal"]
        self.assertEqual(sha(ORIGINAL.read_bytes()),ORIGINAL_PAGE_SHA)
        self.assertEqual(gitblob(ORIGINAL.read_bytes()),ORIGINAL_PAGE_GIT)
        self.assertEqual(sha(SINGLE.read_bytes()),SINGLE_SHA)
        self.assertEqual(gitblob(SINGLE.read_bytes()),SINGLE_GIT)
        self.assertEqual(sha(ANSWER_PAGE.read_bytes()),ANSWER_PAGE_SHA)
        self.assertEqual(p["originalPageImageGitBlobSha1"],ORIGINAL_PAGE_GIT)
        self.assertEqual(p["singleQuestionWebpGitBlobSha1"],SINGLE_GIT)
        self.assertEqual(p["sourcePdfSha256PreviouslyRecorded"],SRC_PDF_PREVIOUS)
        self.assertFalse(p["originalQuestionPdfDownloadedAndRehashedThisTask"])
        self.assertFalse(e["officialFullOriginalPdfByteRehashThisTask"])

    def test_actual_decoded_original_single_question_crop_rgb_equal_no_page_or_q12(self):
        e=self.doc
        crop=[90,275,1310,591]
        self.assertEqual(self.man["crop"],crop)
        self.assertEqual(self.man["outputSize"],[1220,316])
        self.assertEqual(self.man["qaStatus"],"PASS") # original archived image QA only
        self.assertEqual(self.man["sourceSha256"],ORIGINAL_PAGE_SHA)
        self.assertEqual(self.man["sha256"],SINGLE_SHA)
        self.assertEqual(e["historicalOriginal"]["originalCropPixels"],crop)
        with Image.open(ORIGINAL) as src,Image.open(SINGLE) as single:
            src.load()
            single.load()
            self.assertEqual(src.format,single.format)
            self.assertEqual(src.format,"WEBP")
            self.assertEqual(src.size,(1400,1981))
            self.assertEqual(single.size,(1220,316))
            self.assertIsNone(ImageChops.difference(src.convert("RGB").crop(tuple(crop)),
                                                     single.convert("RGB")).getbbox())

    def test_real_source_question_dad_son_blank_and_four_choices_exact_old_and_new(self):
        q=self.q
        o=self.doc["directStructuredSourceTextVisualObservation"]
        self.assertEqual(q["questionId"],QID)
        self.assertEqual(q["year"],114)
        self.assertEqual(q["paperCode"],"00-E")
        self.assertEqual(q["originalQuestionNumber"],11)
        self.assertEqual(q["sourcePage"],3)
        self.assertEqual(q["question"],STEM)
        self.assertEqual(q["options"],OPTIONS)
        self.assertEqual(o["canonicalQuestionExact"],STEM)
        self.assertEqual(o["printedOptionsExact"],OPTIONS)
        self.assertEqual(o["questionIdPrinted"],11)
        self.assertEqual(o["paperCode"],"00-E")
        for k in ["dialogueRolesComplete","blankPreserved","allFourPrintedOptionsComplete",
                  "questionNumberInSourceImage","readableAndSharp","noAdjacentQ12",
                  "noHeaderOrFooterInSingleCrop","noSharedPassageRequired",
                  "noCalculationOrFigureRequired","originalPixelCropExactComparisonRequired"]:
            self.assertTrue(o[k],k)
        self.assertEqual(o["passType"],"PASS_ROLE_A_DIRECT_ARCHIVED_SOURCE_PIXEL_AND_TEXT_MATCH_ONLY")
        self.assertEqual(self.old["id"],QID)
        self.assertEqual(self.old["question"],STEM)
        self.assertEqual(self.old["options"],OPTIONS)
        self.assertEqual(self.old["page"],3)
        self.assertFalse(self.old["questionVerified"])
        self.assertEqual(q["sharedMaterialIds"],[])
        self.assertEqual(q["assets"]["sharedMaterialIds"],[])

    def test_source_question_revision_bound_to_text_and_image_no_answer_leak(self):
        self.assertEqual(publisher.text_revision(self.q,SINGLE_SHA),SOURCE_REV)
        self.assertEqual(self.doc["currentSourceAndAnswerBindings"]["publisherQuestionRevisionSha256"],SOURCE_REV)
        self.assertEqual(self.q["questionProvenance"]["webpSha256"],SINGLE_SHA)
        self.assertEqual(self.q["questionProvenance"]["pixelSourceSha256"],ORIGINAL_PAGE_SHA)
        altered=copy.deepcopy(self.q)
        altered["options"][3]="So you should play games offline."
        self.assertNotEqual(publisher.text_revision(altered,SINGLE_SHA),SOURCE_REV)
        altered=copy.deepcopy(self.q)
        altered["question"]+=" EXTRA"
        self.assertNotEqual(publisher.text_revision(altered,SINGLE_SHA),SOURCE_REV)
        self.assertNotEqual(publisher.text_revision(self.q,"0"*64),SOURCE_REV)
        # Answer is deliberately EXCLUDED from source text revision, avoiding leak.
        altered=copy.deepcopy(self.q)
        altered["answer"]="B"
        self.assertEqual(publisher.text_revision(altered,SINGLE_SHA),SOURCE_REV)

    def test_historical_individual_image_qa_is_sha_bound_but_not_e_approval(self):
        a=self.archiveQa
        self.assertEqual(a["reviewedWebpSha256"],SINGLE_SHA)
        self.assertEqual(a["sourcePageSha256"],ORIGINAL_PAGE_SHA)
        self.assertEqual(a["cropPixels"],[90,275,1310,591])
        self.assertEqual(a["result"],"PASS")
        self.assertTrue(all(a["criteria"].values()))
        self.assertFalse(a["independentHumanReview"])
        self.assertFalse(a["answerVerified"])
        self.assertFalse(a["questionVerified"])
        self.assertFalse(a["integrationReady"])
        self.assertEqual(self.man["visualReviewEvidence"]["reviewedSha256"],SINGLE_SHA)
        self.assertEqual(self.man["visualReviewEvidence"]["qaReviewer"],"ChatGPT assistant")

    def test_prior_official_english_A_and_notice_E26_only_separate_from_source_qa(self):
        ans=self.answer
        self.assertEqual(ans["questionId"],QID)
        self.assertEqual(ans["finalAnswer"],"A")
        self.assertEqual(ans["officialAnswerImageSha256"],ANSWER_PAGE_SHA)
        self.assertEqual(ans["reviewedSingleQuestionWebpSha256"],SINGLE_SHA)
        self.assertEqual(ans["originalQuestionImageSha256"],ORIGINAL_PAGE_SHA)
        self.assertTrue(ans["noCorrectionForThisQuestion"])
        self.assertFalse(ans["noObjectionForPaper"])
        self.assertTrue(ans["officialFinalAnswerImageQaPassed"])
        self.assertEqual(ans["confirmationPdfSha256"],NOTICE_PDF_PREVIOUS)
        self.assertEqual(ans["officialConfirmationNamedQuestionIds"],["114-00-E-26"])
        doc=read(NOTICE)
        entry=next(x for x in doc["docs"] if x["paperCode"]=="00-E")
        self.assertEqual(entry["pdfSha256"],NOTICE_PDF_PREVIOUS)
        self.assertEqual([x["questionId"] for x in entry["confirmed"]],["114-00-E-26"])
        self.assertTrue(self.q["answerVerified"]) # inherited from PR94, NOT granted now
        self.assertEqual(self.q["answer"],"A")
        self.assertFalse(self.q["questionVerified"])
        self.assertTrue(publisher.official_notice_scope_certified(ROOT,114,self.q,ans))
        falsified=copy.deepcopy(ans)
        falsified["confirmationPdfSha256"]="0"*64
        self.assertFalse(publisher.official_notice_scope_certified(ROOT,114,self.q,falsified))
        self.assertFalse(self.doc["officialFinalAnswerReverificationThisTask"])

    def test_full_205_114_seven_column_sqlite_payloads_sha_and_integrity(self):
        qids=set(self.qs)
        with sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True) as cx:
            self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            columns=[row[1] for row in cx.execute("PRAGMA table_info(questions)")]
            self.assertEqual(columns,["question_id","year","paper_code","original_number",
                                      "subject","payload_json","payload_sha256"])
            rows=cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({x[0] for x in rows},qids)
        for qid,payload,h in rows:
            with self.subTest(qid=qid):
                self.assertEqual(sha(payload.encode("utf-8")),h)
                self.assertEqual(payload,canonical(self.qs[qid]))
                self.assertEqual(json.loads(payload),self.qs[qid])

    def test_existing_source_and_205_sqlite_git_blobs_unchanged_no_mutations(self):
        for path,expected in EXPECTED_PINS.items():
            with self.subTest(path=path):
                self.assertEqual(gitblob((ROOT/path).read_bytes()),expected)
                res=subprocess.run(["git","ls-files","--error-unmatch",path],
                                   cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(res.returncode,0,path)
        self.assertEqual(self.doc["currentSourceAndAnswerBindings"]["sourceQuestionsGitBlobSha1"],
                         EXPECTED_PINS["sudu/data/processed/114/questions.json"])
        self.assertEqual(self.doc["currentSourceAndAnswerBindings"]["sourceManifestGitBlobSha1"],
                         EXPECTED_PINS["sudu/data/processed/114/webp-manifest.json"])
        self.assertEqual(self.doc["currentSourceAndAnswerBindings"]["existingAnswerReceiptGitBlobSha1"],
                         EXPECTED_PINS["sudu/data/processed/114/review-evidence/114-00-E-11-official.json"])

    def test_role_B_author_source_revision_read_only_not_e_qa_or_actual_v4(self):
        e=self.doc["externalOtherRoleAuthorCandidateReadOnly"]
        self.assertEqual(e["role"],"B")
        self.assertEqual(e["draftPR"],44)
        self.assertEqual(e["composedTeachingDigest"],
                         "3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee")
        self.assertTrue(e["sourceRevisionMatchesThisReceipt"])
        self.assertFalse(e["independentRoleEFinalContentQa"])
        self.assertFalse(e["actualPublisherEmittedSameDigestV4UiQa"])
        self.assertEqual(self.doc["newReady"],0)
        self.assertEqual(self.doc["newApproved114Main"],0)
        self.assertEqual(self.doc["newLive"],0)
        self.assertFalse(self.doc["questionVerifiedPromoted"])
        self.assertFalse(self.doc["teacherIdentityOrSignatureClaimed"])
        approved=read(ROOT/"sudu/data/approved/114.json")
        self.assertEqual(approved["approvedCount"],0)
        self.assertEqual(approved["questions"],[])

if __name__=="__main__":
    unittest.main()
