"""Role C author-only, no-release evidence checks for 115 accounting 01/11/13/17/21.
Correct arithmetic and SHA integrity DO NOT certify official answers, E review, D UI or LIVE.
"""
import copy
import hashlib
import json
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "sudu/teaching-candidates/115-role-c-acc01-11-13-17-21-20261026"
EXPECTED = {
    "115-09-2-01": ("C", False),
    "115-09-2-11": ("B", False),
    "115-09-2-13": ("D", True),
    "115-09-2-17": ("D", False),
    "115-09-2-21": ("C", True),
}
PDF_SHA = "fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e"

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canon(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode("utf-8"))

def source_revision(q):
    return canon({"question":q["question"],"options":q["options"],
                  "singleQuestionWebpSha256":q["individualImageSha256"]})

class NewRoleCFiveAccounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((DIR/"batch.json").read_text(encoding="utf-8"))
        cls.items={i["questionId"]:i for i in cls.batch["items"]}
        cls.q={qid:json.loads((ROOT/i["path"]).read_text(encoding="utf-8"))
               for qid,i in cls.items.items()}

    def test_scope_claim_versions_and_readiness_still_zero(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-ACC-01-11-13-17-21-20261026-07")
        self.assertEqual(b["claimedAtUtc"],"2026-10-26T05:30:00Z")
        self.assertEqual(b["claimIssueCommentId"],6408960861)
        self.assertEqual(b["baseSHA"],"8910cfbbfedb638206b4b37b1b51817b75137edc")
        self.assertEqual(b["sourceCommit"],"b6c449629efc80d37fa2e6dbb9e680e321367c14")
        self.assertEqual(b["sourceQuestionsGitBlobSha"],"0128adc3f41e748950c3f5af83fca6dd1c331f5c")
        self.assertEqual(b["sourceManifestGitBlobSha"],"2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b")
        self.assertEqual(set(self.q),set(EXPECTED))
        for k in ("newReady","newStaged","newMain","newLive"):
            self.assertEqual(b[k],0)
        self.assertTrue(all(not x["ready"] for x in self.items.values()))

    def test_actual_full_file_source_option_webp_and_lesson_digest_sha(self):
        for qid,q in self.q.items():
            i=self.items[qid]
            with self.subTest(qid=qid):
                self.assertEqual(sha((ROOT/i["path"]).read_bytes()),i["fileSha256"])
                self.assertEqual(source_revision(q),q["sourceTextRevision"])
                self.assertEqual(source_revision(q),i["sourceTextRevision"])
                self.assertEqual(canon(q["teaching"]),q["teachingCanonicalSha256"])
                self.assertEqual(q["teachingCanonicalSha256"],i["teachingCanonicalSha256"])
                self.assertEqual(q["individualImageSha256"],i["originalSingleWebpSha256"])
                self.assertTrue(q["individualImage"].endswith("/"+qid+".webp"))
                self.assertEqual(q["originalPaperPdfSha256"],PDF_SHA)
                self.assertEqual(i["originalPaperPdfSha256"],PDF_SHA)
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["questionId"],qid)
                self.assertEqual(q["subject"],"會計學")
                self.assertEqual(q["year"],115)
                self.assertEqual(q["sourceIssues"],[])
                self.assertEqual(q["answerCandidate"],EXPECTED[qid][0])
                self.assertFalse(q["sourceAnswerVerified"])
                self.assertFalse(q["sourceQuestionVerified"])
                self.assertEqual(q["imageManifestHistoricalQa"],"PASS")
                self.assertEqual(q["imageQuestionAssetHistoricalQa"],"PASS")
                self.assertFalse(q["originalImageBytesRehashedByRoleC"])

    def test_four_distinct_answer_rationales_dual_level_highlight(self):
        for qid,q in self.q.items():
            t=q["teaching"]
            with self.subTest(qid=qid):
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([k for k in "ABCD" if t["optionExplanations"][k]["isCorrect"]],
                                 [q["answerCandidate"]])
                for k in "ABCD":
                    x=t["optionExplanations"][k]
                    self.assertGreaterEqual(len(x["teacher"]),45,(qid,k,"teacher"))
                    self.assertGreaterEqual(len(x["elementary"]),25,(qid,k,"elementary"))
                    self.assertEqual(x["reason"],x["teacher"])
                for k in ("teacherSummary","elementarySummary","memory","concept",
                          "extension","highlights","gradedVocabulary","stepByStep","source"):
                    self.assertTrue(t[k],(qid,k))
                self.assertIn("**",t["teacherSummary"])
                self.assertIn("**",t["memory"])
                self.assertGreaterEqual(len(t["highlights"]),5)
                self.assertGreaterEqual(len(t["stepByStep"]),4)
                self.assertEqual(set(t["gradedVocabulary"]),{"初級","中級","高級"})
                self.assertTrue(all(t["gradedVocabulary"][x] for x in ("初級","中級","高級")))
                self.assertEqual(t["hasExamCalculation"],EXPECTED[qid][1])
                if EXPECTED[qid][1]:
                    z=t["examCalculation"]
                    for k in ("given","formulaUse","substitution","steps","result","unit","option","verification"):
                        self.assertTrue(z[k],(qid,k))
                    self.assertGreaterEqual(len(z["steps"]),6)
                    self.assertEqual(z["option"],q["answerCandidate"])
                    self.assertIn("元",z["unit"])
                else:
                    self.assertIsNone(t["examCalculation"])

    def test_13_all_four_dates_discount_computation_and_reversal(self):
        q=self.q["115-09-2-13"]
        amount=50_000
        paid=49_000
        discount=amount-paid
        annual_rate=Fraction(6,100)
        remaining_months=Fraction(discount*12,1)/ (amount*annual_rate)
        self.assertEqual(discount,1_000)
        self.assertEqual(remaining_months,4)
        self.assertEqual(amount-amount*annual_rate*Fraction(4,12),paid)
        self.assertEqual(amount-amount*annual_rate*Fraction(7,12),48_250) # A Apr 1
        self.assertEqual(amount-amount*annual_rate*Fraction(5,12),48_750) # B Jun 1
        self.assertEqual(amount-amount*annual_rate*Fraction(9,24),48_875) # C approx Jun 15
        calc=q["teaching"]["examCalculation"]
        self.assertIn("7月1日",calc["result"])
        self.assertIn("11月1日","".join(calc["steps"]))
        self.assertIn("4個月","".join(calc["steps"]))
        self.assertIn("49,000",calc["verification"])
        self.assertTrue(q["teaching"]["optionExplanations"]["D"]["isCorrect"])

    def test_21_prior_period_error_both_sides_and_current_year_not_touched(self):
        q=self.q["115-09-2-21"]
        t=q["teaching"]
        self.assertIn("累計折舊－機器設備3,000",t["examCalculation"]["result"])
        self.assertIn("追溯適用及追溯重編之影響數3,000",t["examCalculation"]["result"])
        steps=" ".join(t["examCalculation"]["steps"])
        self.assertIn("借：累計折舊－機器設備3,000",steps)
        self.assertIn("貸：追溯適用及追溯重編之影響數3,000",steps)
        self.assertIn("借方3,000元＝貸方3,000元",steps)
        self.assertIn("X2",t["teacherSummary"])
        self.assertTrue(t["optionExplanations"]["C"]["isCorrect"])
        self.assertFalse(t["optionExplanations"]["A"]["isCorrect"])

    def test_01_11_17_sensitive_concept_checks(self):
        one=self.q["115-09-2-01"]["teaching"]
        self.assertIn("特定日期",one["teacherSummary"])
        self.assertIn("④",one["optionExplanations"]["D"]["teacher"])
        eleven=self.q["115-09-2-11"]["teaching"]
        self.assertIn("次期仍可",eleven["optionExplanations"]["B"]["teacher"])
        self.assertIn("重複",eleven["optionExplanations"]["B"]["teacher"])
        seventeen=self.q["115-09-2-17"]["teaching"]
        self.assertIn("合理確信",seventeen["optionExplanations"]["A"]["teacher"])
        self.assertIn("減損",seventeen["optionExplanations"]["B"]["teacher"])
        self.assertIn("淨額法",seventeen["optionExplanations"]["D"]["teacher"])
        self.assertIn("課綱",seventeen["extension"])
        self.assertTrue(any("ifrs.org" in r["url"] for r in seventeen["outsideReferences"]))

    def test_fail_closed_unapproved_independent_e_official_and_real_ui(self):
        for qid,q in self.q.items():
            with self.subTest(qid=qid):
                self.assertFalse(q["studentReleaseApproved"])
                self.assertFalse(q["deploy"])
                self.assertFalse(q["review"]["newBlindSolveClaimed"])
                self.assertTrue(q["review"]["answersKnownBeforeAuthoring"])
                self.assertTrue(q["review"]["differentAuthorAiReviewerRequired"])
                self.assertTrue(q["review"]["authorSelfReviewProhibited"])
                self.assertEqual(q["review"]["independentAiReviewStatus"],"PENDING")
                self.assertIsNone(q["review"]["independentAiReviewerIdentity"])
                self.assertIsNone(q["review"]["independentAiReviewEvidenceSha256"])
                self.assertIsNone(q["review"]["officialFinalAnswerAndCorrectionProofSha256"])
                self.assertEqual(q["review"]["v4ExactSameSourceAndTeachingDigest8x2"],"PENDING")
                self.assertIn("MASTER_ONLY_PUBLISHER_MAIN_LIVE_GATE_NOT_SATISFIED",q["blockers"])
                self.assertTrue(all("HUMAN_TEACHER" not in x for x in q["blockers"]))

    def test_q21_historical_source_revision_difference_blocks_without_forgery(self):
        q=self.q["115-09-2-21"]
        row=self.items["115-09-2-21"]
        self.assertFalse(q["coordinatorLedgerPriorRevisionMatchesCurrentSource"])
        self.assertTrue(row["ledgerMismatch"])
        self.assertEqual(q["coordinatorLedgerPriorQuestionRevision"],"817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9")
        self.assertNotEqual(q["sourceTextRevision"],q["coordinatorLedgerPriorQuestionRevision"])
        self.assertIn("Q21_COORDINATOR_LEDGER_REVISION_DIFFERS_FROM_CURRENT_SOURCE_REVISION_A_MASTER_RECONCILIATION_REQUIRED",q["blockers"])
        for id in ("115-09-2-01","115-09-2-11","115-09-2-13","115-09-2-17"):
            self.assertFalse(self.items[id]["ledgerMismatch"])

    def test_question_options_webp_or_lesson_changes_invalidate_digest(self):
        for id,q in self.q.items():
            for changed in ("question","options","image","teaching"):
                with self.subTest(qid=id,changed=changed):
                    x=copy.deepcopy(q)
                    if changed=="question":
                        x["question"]+=" TAMPER"
                        self.assertNotEqual(source_revision(x),q["sourceTextRevision"])
                    elif changed=="options":
                        x["options"][0]+=" TAMPER"
                        self.assertNotEqual(source_revision(x),q["sourceTextRevision"])
                    elif changed=="image":
                        x["individualImageSha256"]="0"*64
                        self.assertNotEqual(source_revision(x),q["sourceTextRevision"])
                    else:
                        x["teaching"]["memory"]+=" TAMPER"
                        self.assertNotEqual(canon(x["teaching"]),q["teachingCanonicalSha256"])

if __name__=="__main__":
    unittest.main()
