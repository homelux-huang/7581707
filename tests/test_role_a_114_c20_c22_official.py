"""ROLE A bounded 114 C20/C21/C22 original official announced-answer/notice check.

Actual three 205-row SQLite payloads may gain answerVerified only, never
questionVerified, E review, human-teacher APPROVED, D UIQA, READY or LIVE.
"""
import copy
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts import role_a_114_c20_c22_final_official as a
ROOT=Path(__file__).resolve().parents[1]

def old_file(path):
    r=subprocess.run(["git","show",a.BASE_SHA+":"+path],cwd=ROOT,capture_output=True,check=True)
    return r.stdout

class RoleA114C20C22FinalOfficial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.mapping=a.source_bank()
        cls.earlier=json.loads(old_file("sudu/data/processed/114/questions.json").decode("utf-8"))
        cls.old={q["questionId"]:q for q in cls.earlier["questions"]}
        cls.notice=a.read(a.NOTICE)
        cls.answer_sha=a.verify_archives()

    def test_original_source_page_and_official_answer_pixel_sha_stable(self):
        self.assertEqual(a.gitsha(a.ORIGINAL_QUESTION.read_bytes()),a.ORIGINAL_QUESTION_GIT)
        self.assertEqual(a.sha(a.ORIGINAL_QUESTION.read_bytes()),a.ORIGINAL_QUESTION_SHA)
        self.assertEqual(a.gitsha(a.ORIGINAL_ANSWER.read_bytes()),a.ORIGINAL_ANSWER_GIT)
        self.assertEqual(a.sha(a.ORIGINAL_ANSWER.read_bytes()),self.answer_sha)
        self.assertEqual(a.sha(a.SHARED_PATH.read_bytes()),a.SHARED_SHA)

    def test_three_exact_original_webps_and_shared_historical_qa_not_new_pass(self):
        visual=a.read(a.VISUAL)
        self.assertEqual(a.gitsha(a.VISUAL.read_bytes()),a.VISUAL_GIT)
        self.assertFalse(visual["releaseAllowed"])
        self.assertEqual(visual["answerVerifiedAdded"],0)
        self.assertEqual(visual["questionVerifiedAdded"],0)
        for qid,(blob,digest,crop) in a.IMAGE.items():
            with self.subTest(qid=qid):
                path=ROOT/f"sudu/data/processed/114/webp-v1/00-C/{qid}.webp"
                self.assertEqual(a.gitsha(path.read_bytes()),blob)
                self.assertEqual(a.sha(path.read_bytes()),digest)
                self.assertEqual(self.mapping[qid]["assets"]["sha256"],digest)
                row=next(x for x in visual["items"] if x["questionId"]==qid)
                self.assertEqual(row["cropSourcePixelBounds"],crop)
                self.assertEqual(row["reviewedWebpSha256"],digest)
                self.assertEqual(row["result"],"PASS_DIRECT_ORIGINAL_PAGE_IMAGE")
                self.assertFalse(row["independentHumanReview"])
        self.assertEqual(visual["sharedMaterial"]["outputSha256"],a.SHARED_SHA)
        self.assertEqual(visual["sharedMaterial"]["result"],"PASS_DIRECT_ORIGINAL_PAGE_SHARED_ARTICLE_VISUAL")

    def test_final_announced_answer_p1_individual_cells_exact_C_C_A(self):
        for number,letter in [(20,"C"),(21,"C"),(22,"A")]:
            qid=f"114-00-C-{number:02d}"
            with self.subTest(qid=qid):
                self.assertEqual(a.ANSWER[qid],letter)
                self.assertEqual(self.mapping[qid]["answer"],letter)
                proof=a.read(a.receipt_path(qid))
                self.assertEqual(proof["individualPrintedAnswerCell"]["number"],number)
                self.assertEqual(proof["individualPrintedAnswerCell"]["observedLetter"],letter)
                self.assertEqual(proof["officialAnswerImageSha256"],self.answer_sha)
                self.assertEqual(proof["officialPdfSha256"],a.ANSWER_PDF_SHA)
                self.assertTrue(proof["archivedAnswerImageOpenedAndVisuallyReviewedThisSession"])
                self.assertFalse(proof["independentDirectOfficialFinalAnswerPdfRenderedInCurrentReview"])
                self.assertFalse(proof["officialAnswerPdfDownloadedAndRehashedThisSession"])

    def test_114_year_correction_scope_five_pdf_pages_and_negative_override(self):
        doc=next(d for d in self.notice["docs"] if d["paperCode"]=="00-C")
        self.assertEqual(doc["pdfSha256"],a.NOTICE_PDF_SHA)
        self.assertEqual(doc["pageCount"],5)
        self.assertEqual([x["questionId"] for x in doc["confirmed"]],a.NAMED)
        self.assertFalse(set(a.ANSWER)&set(a.NAMED))
        for qid in a.ANSWER:
            p=a.read(a.receipt_path(qid))
            self.assertTrue(a.publisher.official_notice_scope_certified(ROOT,114,self.mapping[qid],p))
            self.assertFalse(a.publisher.official_notice_scope_certified(ROOT,114,self.mapping[qid],{**p,"noObjectionForPaper":True}))
            self.assertFalse(a.publisher.official_notice_scope_certified(ROOT,114,self.mapping[qid],{**p,"confirmationPdfSha256":"0"*64}))
            self.assertFalse(a.publisher.official_notice_scope_certified(ROOT,114,self.mapping[qid],{**p,"noCorrectionForThisQuestion":False}))
            self.assertFalse(a.publisher.official_notice_scope_certified(ROOT,114,{"questionId":"114-00-C-24","paperCode":"00-C"},p))

    def test_exact_three_canonical_question_diffs_preserve_other_202_and_own_c19(self):
        self.assertEqual(self.bank["year"],114)
        self.assertEqual(len(self.bank["questions"]),205)
        self.assertEqual(set(self.old),set(self.mapping))
        for id_,prior in self.old.items():
            current=self.mapping[id_]
            with self.subTest(qid=id_):
                if id_ in a.ANSWER:
                    copy_prior=copy.deepcopy(prior)
                    copy_prior["answerVerified"]=True
                    copy_prior["officialFinalAnswer"]=a.ANSWER[id_]
                    copy_prior["officialCorrectionChecked"]=True
                    copy_prior["answerProvenance"]["independentVisualVerification"]=True
                    copy_prior["officialFinalQaEvidence"]=current["officialFinalQaEvidence"]
                    self.assertEqual(current,copy_prior)
                    self.assertEqual(
                        a.publisher.text_revision(prior,a.IMAGE[id_][1]),
                        a.publisher.text_revision(current,a.IMAGE[id_][1]))
                else:
                    self.assertEqual(current,prior)
        q19=self.mapping["114-00-C-19"]
        self.assertEqual(q19["questionProvenance"]["webpSha256"],
                         "4c549405cfef2061a42abdac873c6146bb61e52a5cccae2f232d1a5ca35baff1")
        self.assertFalse(q19["answerVerified"])

    def test_full_205_sqlite_exact_json_payload_sha_and_only_three_different_rows(self):
        a.db_precheck(a.DB,self.bank)
        with tempfile.TemporaryDirectory() as td:
            before_db=Path(td)/"old.sqlite3"
            before_db.write_bytes(old_file("sudu/data/processed/114/question-bank.sqlite3"))
            with sqlite3.connect(before_db.as_uri()+"?mode=ro",uri=True) as db:
                past={id_:(payload,digest) for id_,payload,digest in db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                now={id_:(payload,digest) for id_,payload,digest in db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            self.assertEqual(set(past),set(now))
            self.assertEqual({qid for qid in past if past[qid]!=now[qid]},set(a.ANSWER))
            for id_ in a.ANSWER:
                self.assertTrue(json.loads(now[id_][0])["answerVerified"])
                self.assertFalse(json.loads(now[id_][0])["questionVerified"])
            f=Path(td)/"1.sqlite3";g=Path(td)/"2.sqlite3"
            for candidate in (f,g):
                a.update_db(before_db,candidate,{qid:self.mapping[qid] for qid in a.ANSWER})
            self.assertEqual(a.sha(f.read_bytes()),a.sha(g.read_bytes()))
            self.assertEqual(a.sha(f.read_bytes()),a.sha(a.DB.read_bytes()))

    def test_negative_wrong_source_image_option_and_official_notice_sha(self):
        qid="114-00-C-20"
        q=copy.deepcopy(self.mapping[qid])
        rev=a.publisher.text_revision(q,a.IMAGE[qid][1])
        q["options"][0]+=" TAMPERED"
        self.assertNotEqual(a.publisher.text_revision(q,a.IMAGE[qid][1]),rev)
        self.assertNotEqual(a.publisher.text_revision(self.mapping[qid],"0"*64),rev)
        self.assertNotEqual(a.sha(a.ORIGINAL_ANSWER.read_bytes()+b"x"),self.answer_sha)
        self.assertNotEqual(a.sha(a.SHARED_PATH.read_bytes()+b"x"),a.SHARED_SHA)
        with self.assertRaises(AssertionError):
            a.assert_webp(a.SHARED_PATH,a.SHARED_GIT,"0"*64,[1220,455])

    def test_no_independent_e_teacher_ui_source_full_or_student_release_promotion(self):
        for qid in a.ANSWER:
            q=self.mapping[qid]
            p=a.read(a.receipt_path(qid))
            self.assertTrue(q["answerVerified"])
            self.assertFalse(q["questionVerified"])
            self.assertEqual(q["reviewStatus"],"needs_review")
            self.assertIsNot(q.get("studentReleaseApproved"),True)
            self.assertIsNot(q.get("integrationReady"),True)
            self.assertFalse(p["independentRoleEContentQaPerformed"])
            self.assertFalse(p["sourceTextVerifiedPromoted"])
            self.assertFalse(p["teachingQaPromoted"])
            self.assertFalse(p["uiQaPromoted"])
            self.assertFalse(p["readyOrLivePromoted"])
        approved=a.read(ROOT/"sudu/data/approved/114.json") if (ROOT/"sudu/data/approved/114.json").exists() else {"questions":[]}
        self.assertFalse(set(a.ANSWER)&{v.get("canonicalId") for v in approved.get("questions",[])})
if __name__=="__main__":
    unittest.main()
