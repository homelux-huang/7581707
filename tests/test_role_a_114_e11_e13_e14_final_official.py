"""Role A official 114 English 11/13/14 published-answer QA, notice scope, 205 SQL parity.
These are A-source/official checks, NOT independent Role E content, new READY, or LIVE.
"""
import copy
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts import role_a_114_e11_e13_e14_final_official as a
from scripts import sudu_verified_publish as pub

ROOT=Path(__file__).resolve().parents[1]
def oldblob(path):
    return subprocess.run(["git","show",a.BASE_SHA+":"+path],cwd=ROOT,capture_output=True,check=True).stdout
class RoleA114PublishedFinalAnswerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.latest=a.read(a.BANK)
        cls.old=json.loads(oldblob("sudu/data/processed/114/questions.json"))
        cls.newby={q["questionId"]:q for q in cls.latest["questions"]}
        cls.oldby={q["questionId"]:q for q in cls.old["questions"]}
        assert len(cls.newby)==len(cls.oldby)==205
    def test_official_page_exact_original_git_sha_and_source_webp_pixels(self):
        a.verify_archives()
        self.assertEqual(a.gitsha(a.SOURCE_IMG.read_bytes()),a.SRC_GIT)
        self.assertEqual(a.gitsha(a.ANSWER_IMG.read_bytes()),a.ANSWER_GIT)
        self.assertEqual(a.sha(a.SOURCE_IMG.read_bytes()),a.SOURCE_SHA)
        self.assertEqual(a.sha(a.ANSWER_IMG.read_bytes()),a.ANSWER_SHA)
        for qid,hashvalue in a.WEBP.items():
            with self.subTest(qid=qid):
                q=self.newby[qid]
                self.assertEqual(a.sha((ROOT/q["assets"]["singleQuestionWebp"]).read_bytes()),hashvalue)
                self.assertEqual(q["questionProvenance"]["webpSha256"],hashvalue)
                self.assertEqual(q["questionProvenance"]["officialPdfSha256"],a.PDF_Q_SHA)
                self.assertEqual(q["answerProvenance"]["officialPdfSha256"],a.PDF_A_SHA)
    def test_original_114_confirmation_pdf_all_pages_scope_only_E26(self):
        status=a.read(a.STATUS)
        doc=a.read(a.NOTICE)
        self.assertEqual(a.gitsha(a.NOTICE.read_bytes()),a.NOTICE_LEDGER_GIT)
        self.assertEqual(a.gitsha(a.STATUS.read_bytes()),a.NOTICE_STATUS_GIT)
        self.assertEqual(status["confirmations"]["00-E"]["revisionDocumentSha256"],a.NOTICE_PDF_SHA)
        self.assertEqual([x["questionId"] for x in next(
            x for x in doc["docs"] if x["paperCode"]=="00-E")["confirmed"]],["114-00-E-26"])
        self.assertEqual(doc["allPagesInFourDocumentsReviewed"],True)
        self.assertEqual(status["finalAnswerPublishedAt"],"2025-05-09 17:00 Asia/Taipei")
        for qid in a.ANSWER:
            receipt=a.read(a.receipt_path(qid))
            self.assertFalse(receipt["noObjectionForPaper"])
            self.assertTrue(receipt["noCorrectionForThisQuestion"])
            self.assertFalse(receipt["correctionForQuestionReviewed"])
            self.assertTrue(pub.official_notice_scope_certified(ROOT,114,self.newby[qid],receipt))
            bad=copy.deepcopy(receipt)
            bad["confirmationPdfSha256"]="0"*64
            self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.newby[qid],bad))
            bad=copy.deepcopy(receipt)
            bad["noObjectionForPaper"]=True
            self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.newby[qid],bad))
            bad=copy.deepcopy(receipt)
            bad["noCorrectionForThisQuestion"]=False
            self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.newby[qid],bad))
            self.assertFalse(pub.official_notice_scope_certified(
                ROOT,114,{"paperCode":"00-E","questionId":"114-00-E-26"},receipt))
    def test_205_canonical_records_change_exactly_three_official_answer_fields_only(self):
        self.assertEqual(set(self.newby),set(self.oldby))
        self.assertEqual(self.latest["year"],114)
        expected_keys={"answerVerified","officialFinalAnswer","officialCorrectionChecked",
                       "answerProvenance","officialFinalQaEvidence"}
        for qid,old in self.oldby.items():
            now=self.newby[qid]
            with self.subTest(qid=qid):
                if qid in a.ANSWER:
                    self.assertFalse(old["answerVerified"])
                    self.assertTrue(now["answerVerified"])
                    self.assertEqual(now["officialFinalAnswer"],a.ANSWER[qid])
                    self.assertTrue(now["officialCorrectionChecked"])
                    self.assertTrue(now["answerProvenance"]["independentVisualVerification"])
                    old_without=copy.deepcopy(old)
                    new_without=copy.deepcopy(now)
                    for key in expected_keys:
                        old_without.pop(key,None)
                        new_without.pop(key,None)
                    self.assertEqual(old_without,new_without)
                    expect=copy.deepcopy(old["answerProvenance"])
                    expect["independentVisualVerification"]=True
                    self.assertEqual(now["answerProvenance"],expect)
                    self.assertEqual(now["question"],old["question"])
                    self.assertEqual(now["options"],old["options"])
                    self.assertFalse(now["questionVerified"])
                    self.assertEqual(now["reviewStatus"],"needs_review")
                    self.assertIsNot(now.get("studentReleaseApproved"),True)
                    self.assertEqual(pub.text_revision(old,a.WEBP[qid]),
                                     pub.text_revision(now,a.WEBP[qid]))
                else:
                    self.assertEqual(now,old)
    def test_three_exact_true_official_answers_are_real_source_reviews_not_auto_match(self):
        self.assertEqual(a.ANSWER,{
            "114-00-E-11":"A","114-00-E-13":"A","114-00-E-14":"D"})
        for qid,answer in a.ANSWER.items():
            with self.subTest(qid=qid):
                q=self.newby[qid]
                receipt=a.read(a.receipt_path(qid))
                self.assertEqual(receipt["questionId"],qid)
                self.assertEqual(receipt["finalAnswer"],answer)
                self.assertTrue(receipt["officialFinalAnswerImageQaPassed"])
                self.assertTrue(receipt["archivedAnswerImageOpenedAndVisuallyReviewedThisSession"])
                self.assertFalse(receipt["independentDirectOfficialFinalAnswerPdfRenderedInCurrentReview"])
                self.assertFalse(receipt["confirmationPdfDownloadedAndRehashedThisSession"])
                self.assertFalse(receipt["officialAnswerPdfDownloadedAndRehashedThisSession"])
                self.assertFalse(receipt["humanReviewerClaimed"])
                self.assertFalse(receipt["independentRoleEContentQaPerformed"])
                self.assertEqual(receipt["officialAnswerImageGitBlobSha1"],a.ANSWER_GIT)
                self.assertEqual(receipt["officialAnswerImageSha256"],a.ANSWER_SHA)
                self.assertEqual(receipt["reviewedSingleQuestionWebpSha256"],a.WEBP[qid])
                self.assertEqual(receipt["individualPrintedAnswerCell"]["observedLetter"],answer)
                self.assertEqual(receipt["officialConfirmationNamedQuestionIds"],["114-00-E-26"])
                self.assertEqual(q["officialFinalQaEvidence"]["evidencePath"],
                                 a.receipt_path(qid).relative_to(ROOT).as_posix())
                self.assertEqual(q["officialFinalQaEvidence"]["answerPdfSha256"],a.PDF_A_SHA)
                self.assertIsNot(q.get("integrationReady"),True)
                self.assertIsNot(q.get("studentReleaseApproved"),True)
    def test_all_205_sqlite_payloads_match_canonical_bank_and_integrity(self):
        a.precheck_db(a.DB,self.latest)
        with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM questions WHERE question_id IN (?,?,?) AND answer_verified=1",
                tuple(sorted(a.ANSWER))).fetchone()[0],3)
    def test_original_sqlite_row_level_diff_only_three_exact_fields(self):
        orig=oldblob("sudu/data/processed/114/question-bank.sqlite3")
        self.assertEqual(a.gitsha(orig),a.BASE_DB_GIT)
        with tempfile.TemporaryDirectory() as td:
            old=Path(td)/"original.sqlite3";old.write_bytes(orig)
            with sqlite3.connect(old.as_uri()+"?mode=ro",uri=True) as db:
                cols=[c[1] for c in db.execute("PRAGMA table_info(questions)")]
                records_before={r[cols.index("question_id")]:dict(zip(cols,r)) for r in db.execute("SELECT * FROM questions")}
            with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
                cols_after=[c[1] for c in db.execute("PRAGMA table_info(questions)")]
                records_after={r[cols.index("question_id")]:dict(zip(cols,r)) for r in db.execute("SELECT * FROM questions")}
            self.assertEqual(cols,cols_after)
            self.assertEqual(set(records_before),set(records_after))
            diffs={}
            for qid,prev in records_before.items():
                changed=[col for col in cols if prev[col]!=records_after[qid][col]]
                if changed:
                    diffs[qid]=set(changed)
            self.assertEqual(set(diffs),set(a.ANSWER))
            for qid in a.ANSWER:
                self.assertEqual(diffs[qid],{"payload_json","payload_sha256","answer_verified"})
                self.assertEqual(records_before[qid]["answer_verified"],0)
                self.assertEqual(records_after[qid]["answer_verified"],1)
                self.assertEqual(records_before[qid]["question_verified"],
                                 records_after[qid]["question_verified"])
    def test_binary_replay_two_isolated_imports_exact_same_sha(self):
        baseline=oldblob("sudu/data/processed/114/question-bank.sqlite3")
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/"base.sqlite3";src.write_bytes(baseline)
            out1=Path(td)/"out1.sqlite3";out2=Path(td)/"out2.sqlite3"
            updates={qid:self.newby[qid] for qid in a.ANSWER}
            a.update_three_sqlite(src,out1,updates)
            a.update_three_sqlite(src,out2,updates)
            self.assertEqual(a.sha(out1.read_bytes()),a.sha(out2.read_bytes()))
            self.assertEqual(a.sha(out1.read_bytes()),a.sha(a.DB.read_bytes()))
    def test_wrong_official_key_or_modified_q12_cannot_be_admitted(self):
        old=self.oldby["114-00-E-12"];now=self.newby["114-00-E-12"]
        self.assertEqual(old,now)
        self.assertFalse(now["answerVerified"])
        for qid in a.ANSWER:
            receipt=a.read(a.receipt_path(qid))
            fake=copy.deepcopy(receipt);fake["officialAnswerImageSha256"]="0"*64
            self.assertNotEqual(fake["officialAnswerImageSha256"],a.ANSWER_SHA)
            fake=copy.deepcopy(receipt);fake["finalAnswer"]="B" if receipt["finalAnswer"]!="B" else "C"
            self.assertNotEqual(fake["finalAnswer"],self.newby[qid]["answer"])
        approvals=a.read(ROOT/"sudu/data/approved/114.json")
        self.assertEqual(approvals["approvedCount"],0)
        self.assertEqual(approvals["questions"],[])
if __name__=="__main__":
    unittest.main()
