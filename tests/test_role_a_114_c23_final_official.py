"""114 Chinese C23 exact published original answer D after C20-22 original shared QA.

Role A is source author only; E, D, full question OCR QA and release pending.
"""
import copy
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts import role_a_114_c23_final_official as a
from scripts import role_a_114_c20_c22_final_official as earlier

ROOT=earlier.ROOT
def old_file(path):
    return subprocess.run(["git","show",a.BASE_SHA+":"+path],cwd=ROOT,check=True,capture_output=True).stdout

class RoleA114C23FinalOfficial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.q=a.source()
        cls.base=json.loads(old_file("sudu/data/processed/114/questions.json").decode("utf-8"))
        cls.prev={q["questionId"]:q for q in cls.base["questions"]}
        cls.proof=earlier.read(a.PROOF)

    def test_114_c20_to22_existing_sha_and_205_precondition_still_valid(self):
        earlier.verify_final()
        self.assertEqual(self.bank["year"],114)
        self.assertEqual(len(self.bank["questions"]),205)
        self.assertEqual(len({q["questionId"] for q in self.bank["questions"]}),205)

    def test_original_c23_webp_immutable_and_historical_assistant_source_qa(self):
        raw=a.ORIGINAL_PATH.read_bytes()
        self.assertEqual(earlier.gitsha(raw),a.ORIGINAL_GIT)
        self.assertEqual(earlier.sha(raw),a.ORIGINAL_SHA)
        self.assertEqual(self.q["questionProvenance"]["webpSha256"],a.ORIGINAL_SHA)
        self.assertEqual(self.q["assets"]["sha256"],a.ORIGINAL_SHA)
        self.assertEqual(self.q["assets"]["sharedMaterialIds"],[earlier.SHARED_ID])
        v=next(x for x in earlier.read(earlier.VISUAL)["items"] if x["questionId"]==a.QID)
        self.assertEqual(v["result"],"PASS_DIRECT_ORIGINAL_PAGE_IMAGE")
        self.assertEqual(v["cropSourcePixelBounds"],a.ORIGINAL_CROP)
        self.assertTrue(all(v["visualCriteria"].values()))
        self.assertIs(v["independentHumanReview"],False)
        self.assertIs(v["questionVerified"],False)

    def test_actual_answer_p1_cell23_D_with_exact_sha_and_scoped_notice(self):
        p=self.proof
        self.assertEqual(p["taskId"],a.TASK)
        self.assertEqual(p["questionId"],a.QID)
        self.assertEqual(p["finalAnswer"],"D")
        self.assertEqual(p["individualPrintedAnswerCell"]["number"],23)
        self.assertEqual(p["individualPrintedAnswerCell"]["observedLetter"],"D")
        self.assertEqual(p["officialAnswerImageSha256"],
                         earlier.sha(earlier.ORIGINAL_ANSWER.read_bytes()))
        self.assertEqual(p["officialAnswerImageGitBlobSha1"],earlier.ORIGINAL_ANSWER_GIT)
        self.assertEqual(p["officialPdfSha256"],earlier.ANSWER_PDF_SHA)
        self.assertEqual(p["confirmationPdfSha256"],earlier.NOTICE_PDF_SHA)
        self.assertTrue(earlier.publisher.official_notice_scope_certified(ROOT,114,self.q,p))
        for bad in [
            {**p,"noObjectionForPaper":True},
            {**p,"noCorrectionForThisQuestion":False},
            {**p,"confirmationPdfSha256":"0"*64},
        ]:
            self.assertFalse(earlier.publisher.official_notice_scope_certified(ROOT,114,self.q,bad))
        self.assertFalse(earlier.publisher.official_notice_scope_certified(
            ROOT,114,{"questionId":"114-00-C-24","paperCode":"00-C"},p))

    def test_exactly_c23_official_fields_changed_no_text_regression(self):
        m={q["questionId"]:q for q in self.bank["questions"]}
        self.assertEqual(set(m),set(self.prev))
        for qid,original in self.prev.items():
            after=m[qid]
            with self.subTest(qid=qid):
                if qid==a.QID:
                    expected=copy.deepcopy(original)
                    expected["answerVerified"]=True
                    expected["officialFinalAnswer"]="D"
                    expected["officialCorrectionChecked"]=True
                    expected["answerProvenance"]["independentVisualVerification"]=True
                    expected["officialFinalQaEvidence"]=after["officialFinalQaEvidence"]
                    self.assertEqual(expected,after)
                    self.assertEqual(earlier.publisher.text_revision(original,a.ORIGINAL_SHA),
                                     earlier.publisher.text_revision(after,a.ORIGINAL_SHA))
                    self.assertEqual(after["issues"],["last_on_page_check_possible_continuation_or_footer"])
                    self.assertFalse(after["questionVerified"])
                else:self.assertEqual(after,original)
        self.assertEqual([m[f"114-00-C-{n:02d}"]["answer"] for n in [20,21,22,23]],
                         ["C","C","A","D"])
        self.assertTrue(all(m[f"114-00-C-{n:02d}"]["answerVerified"] for n in [20,21,22,23]))

    def test_all_205_sql_payload_sha_and_only_one_new_row(self):
        earlier.db_precheck(earlier.DB,self.bank)
        with tempfile.TemporaryDirectory() as td:
            prior=Path(td)/"base.sqlite3";prior.write_bytes(old_file("sudu/data/processed/114/question-bank.sqlite3"))
            with sqlite3.connect(prior) as db:
                before={i:(p,h) for i,p,h in db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            with sqlite3.connect(earlier.DB) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                now={i:(p,h) for i,p,h in db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            self.assertEqual(set(before),set(now))
            self.assertEqual({qid for qid in before if before[qid]!=now[qid]},{a.QID})
            self.assertTrue(json.loads(now[a.QID][0])["answerVerified"])
            self.assertFalse(json.loads(now[a.QID][0])["questionVerified"])
            fst=Path(td)/"fst.sqlite3";snd=Path(td)/"snd.sqlite3"
            earlier.update_db(prior,fst,{a.QID:self.q})
            earlier.update_db(prior,snd,{a.QID:self.q})
            self.assertEqual(earlier.sha(fst.read_bytes()),earlier.sha(snd.read_bytes()))
            self.assertEqual(earlier.sha(fst.read_bytes()),earlier.sha(earlier.DB.read_bytes()))

    def test_no_new_question_e_teacher_ui_ready_or_live_promotion(self):
        self.assertTrue(self.q["answerVerified"])
        self.assertFalse(self.q["questionVerified"])
        self.assertFalse(self.q["integrationReady"])
        self.assertEqual(self.q["reviewStatus"],"needs_review")
        self.assertEqual(self.q["issues"],["last_on_page_check_possible_continuation_or_footer"])
        for field in ("humanReviewerClaimed","independentRoleEContentQaPerformed",
                      "sourceTextVerifiedPromoted","questionVerifiedPromoted",
                      "teachingQaPromoted","uiQaPromoted","readyOrLivePromoted"):
            self.assertFalse(self.proof[field])
        self.assertFalse(self.proof["officialAnswerPdfDownloadedAndRehashedThisSession"])

    def test_negative_tampered_source_option_or_webp_or_official_sha(self):
        q=copy.deepcopy(self.q)
        rev=earlier.publisher.text_revision(q,a.ORIGINAL_SHA)
        q["options"][0]+=" FALSE"
        self.assertNotEqual(earlier.publisher.text_revision(q,a.ORIGINAL_SHA),rev)
        self.assertNotEqual(earlier.publisher.text_revision(self.q,"0"*64),rev)
        with self.assertRaises(AssertionError):
            earlier.assert_webp(a.ORIGINAL_PATH,a.ORIGINAL_GIT,"0"*64,[1220,241])
        with self.assertRaises(AssertionError):
            earlier.assert_webp(a.ORIGINAL_PATH,a.ORIGINAL_GIT,a.ORIGINAL_SHA,[1220,240])

if __name__=="__main__":
    unittest.main()
