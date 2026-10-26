"""Role C 115 accounting Q07/09/16/18/20 author-only provenance and arithmetic checks.
Passing does NOT mean A official answer, E independent reviewer, D real browser QA or LIVE.
"""
import copy
import hashlib
import json
import unittest
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/teaching-candidates/115-role-c-acc07-09-16-18-20-20261026"
ANSWERS={
    "115-09-2-07":"B",
    "115-09-2-09":"D",
    "115-09-2-16":"D",
    "115-09-2-18":"C",
    "115-09-2-20":"A",
}
PDF_SHA="fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e"

def sha(content):
    return hashlib.sha256(content).hexdigest()

def canonical(obj):
    return sha(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))

def source_rev(q):
    return canonical({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":q["individualImageSha256"]})

class RoleCAuthorFiveAccounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((DIR/"batch.json").read_text(encoding="utf-8"))
        cls.items={r["questionId"]:r for r in cls.batch["items"]}
        cls.records={id:json.loads((ROOT/r["path"]).read_text(encoding="utf-8"))
                     for id,r in cls.items.items()}

    def test_actual_claim_scope_versions_and_zero_release(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-ACC-07-09-16-18-20-20261026-08")
        self.assertEqual(b["claimIssueCommentId"],6409080325)
        self.assertEqual(b["claimedAtUtc"],"2026-10-26T05:39:41Z")
        self.assertEqual(b["baseSHA"],"b018e43aa899ed14fba5cb74a6c46a25e1153528")
        self.assertEqual(b["sourceCommit"],"b6c449629efc80d37fa2e6dbb9e680e321367c14")
        self.assertEqual(b["sourceQuestionsGitBlobSha"],"0128adc3f41e748950c3f5af83fca6dd1c331f5c")
        self.assertEqual(b["sourceManifestGitBlobSha"],"2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b")
        self.assertEqual(set(self.records),set(ANSWERS))
        self.assertEqual((b["newReady"],b["newStaged"],b["newMain"],b["newLive"]),(0,0,0,0))
        self.assertTrue(all(not r["ready"] for r in self.items.values()))

    def test_exact_full_file_source_image_and_teaching_digests(self):
        for id,q in self.records.items():
            with self.subTest(id=id):
                item=self.items[id]
                self.assertEqual(sha((ROOT/item["path"]).read_bytes()),item["fileSha256"])
                self.assertEqual(q["sourceTextRevision"],item["sourceTextRevision"])
                self.assertEqual(source_rev(q),item["sourceTextRevision"])
                self.assertEqual(canonical(q["teaching"]),item["teachingCanonicalSha256"])
                self.assertEqual(q["teachingCanonicalSha256"],item["teachingCanonicalSha256"])
                self.assertEqual(q["individualImageSha256"],item["originalSingleWebpSha256"])
                self.assertEqual(q["originalPaperPdfSha256"],PDF_SHA)
                self.assertEqual(item["originalPaperPdfSha256"],PDF_SHA)
                self.assertTrue(q["individualImage"].endswith("/"+id+".webp"))
                self.assertEqual(q["questionId"],id)
                self.assertEqual(q["subject"],"會計學")
                self.assertEqual(q["year"],115)
                self.assertEqual(q["sourceIssues"],[])
                self.assertFalse(q["sourceQuestionVerified"])
                self.assertFalse(q["sourceAnswerVerified"])
                self.assertEqual(q["answerCandidate"],ANSWERS[id])
                self.assertEqual(q["imageManifestHistoricalQa"],"PASS")
                self.assertFalse(q["sourceOriginalImageBytesRehashedByC"])
                self.assertEqual(len(q["options"]),4)

    def test_four_distinct_detailed_teacher_and_child_explanations_all_require_math(self):
        for id,q in self.records.items():
            with self.subTest(id=id):
                t=q["teaching"]
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([k for k in "ABCD" if t["optionExplanations"][k]["isCorrect"]],[ANSWERS[id]])
                for letter in "ABCD":
                    x=t["optionExplanations"][letter]
                    self.assertGreaterEqual(len(x["teacher"]),50,(id,letter,"teacher"))
                    self.assertGreaterEqual(len(x["elementary"]),25,(id,letter,"elementary"))
                    self.assertEqual(x["reason"],x["teacher"])
                for fld in ("teacherSummary","elementarySummary","concept","memory","extension",
                            "highlights","gradedVocabulary","stepByStep","source"):
                    self.assertTrue(t[fld],(id,fld))
                self.assertIn("**",t["teacherSummary"])
                self.assertIn("**",t["memory"])
                self.assertEqual(set(t["gradedVocabulary"]),{"初級","中級","高級"})
                self.assertGreaterEqual(len(t["highlights"]),7)
                self.assertGreaterEqual(len(t["stepByStep"]),4)
                self.assertTrue(t["hasExamCalculation"])
                calc=t["examCalculation"]
                for fld in ("given","formulaUse","substitution","steps","result","unit","option","verification"):
                    self.assertTrue(calc[fld],(id,fld))
                self.assertEqual(calc["option"],ANSWERS[id])
                self.assertGreaterEqual(len(calc["steps"]),8)
                self.assertIn("元",calc["unit"])

    def test_07_full_income_statement_margins_tax(self):
        sales=1650000-50000
        cogs=800000-14000+30000
        margin=sales-cogs
        expenses=300000+80000+4000
        op_income=margin-expenses
        pretax=op_income-16000
        tax=pretax*Fraction(20,100)
        after_tax=pretax-tax
        self.assertEqual((sales,cogs,margin,expenses,op_income,pretax,tax,after_tax),
                         (1600000,816000,784000,384000,400000,384000,76800,307200))
        self.assertEqual(Fraction(op_income,sales),Fraction(1,4))
        self.assertEqual(Fraction(cogs,sales),Fraction(51,100))
        q=self.records["115-09-2-07"]
        self.assertIn("400,000",q["teaching"]["examCalculation"]["result"])
        self.assertIn("307,200",q["teaching"]["examCalculation"]["result"])
        self.assertTrue(q["teaching"]["optionExplanations"]["B"]["isCorrect"])

    def test_09_5pct_input_exclusions_payable_and_current_ratio(self):
        rate=Fraction(5,100)
        output=(9000000-1500000)*rate
        land=2250000*Fraction(60,100)
        eligible_base=8750000-land-950000-18000-15000
        input_credit=eligible_base*rate
        payable=output-input_credit-18000
        limit=1500000*rate+(2250000-land+350000)*rate
        self.assertEqual((output,land,eligible_base,input_credit,payable,limit),
                         (375000,1350000,6417000,320850,36150,137500))
        L=1000000
        d=input_credit+18000
        before=Fraction(3,2)
        after=Fraction(before*L-d,L-d)
        self.assertGreater(after,before)
        self.assertGreater(L,d)
        q=self.records["115-09-2-09"]
        self.assertIn("320,850",q["teaching"]["teacherSummary"])
        self.assertIn("36,150",q["teaching"]["examCalculation"]["result"])
        self.assertIn("137,500",q["teaching"]["optionExplanations"]["C"]["teacher"])
        self.assertTrue(q["teaching"]["optionExplanations"]["D"]["isCorrect"])

    def test_16_fvtpl_shares_cash_dividend_fair_value_and_crossyear(self):
        shares=5000
        dividend=shares*2
        bonus=shares*Fraction(4,100)
        new_shares=shares+bonus
        opening=shares*30
        closing=new_shares*40
        x1=dividend+(closing-opening)-100
        sale=new_shares*50
        x2=sale-1000-closing
        lifetime=dividend+sale-opening-100-1000
        self.assertEqual((new_shares,dividend,closing,x1,sale,x2,lifetime),
                         (5200,10000,208000,67900,260000,51000,118900))
        self.assertEqual(x1+x2,lifetime)
        q=self.records["115-09-2-16"]
        self.assertIn("67,900",q["teaching"]["examCalculation"]["result"])
        self.assertIn("51,000",q["teaching"]["examCalculation"]["result"])
        self.assertTrue(q["teaching"]["optionExplanations"]["D"]["isCorrect"])

    def test_18_original_then_revised_depreciation_syd(self):
        straight=(500000-5000)/5
        opening=500000-2*straight
        revised_depreciable=opening-2000
        x3=revised_depreciable*Fraction(2,3)
        close=opening-x3
        x4=close-revised_depreciable*Fraction(1,3)
        self.assertEqual((straight,opening,revised_depreciable,x3,close,x4),
                         (99000,302000,300000,200000,102000,2000))
        q=self.records["115-09-2-18"]
        self.assertIn("102,000",q["teaching"]["examCalculation"]["result"])
        self.assertIn("2,000",q["teaching"]["examCalculation"]["verification"])
        self.assertTrue(q["teaching"]["optionExplanations"]["C"]["isCorrect"])

    def test_20_premium_bond_effective_interest_amortization(self):
        opening=5803274
        closing=5755405
        cash=280000
        amort=opening-closing
        effective=cash-amort
        annual=Fraction(4,100)
        self.assertEqual((amort,effective),(47869,232131))
        self.assertLess(abs(Fraction(effective,opening)-annual),Fraction(1,1000000))
        next_effective=closing*annual
        next_amort=cash-next_effective
        self.assertLess(next_effective,effective)
        self.assertGreater(next_amort,amort)
        self.assertEqual(opening+effective-cash,closing)
        self.assertLess(6*effective,6*cash)
        q=self.records["115-09-2-20"]
        self.assertIn("232,131",q["teaching"]["examCalculation"]["result"])
        self.assertIn("47,869",q["teaching"]["examCalculation"]["result"])
        self.assertTrue(q["teaching"]["optionExplanations"]["A"]["isCorrect"])

    def test_no_forged_e_approval_official_qa_ui_ready_deployment(self):
        for id,q in self.records.items():
            r=q["review"]
            self.assertTrue(r["answerKnownBeforeReasoning"])
            self.assertFalse(r["newBlindSolveClaimed"])
            self.assertTrue(r["differentAuthorRequired"])
            self.assertFalse(r["selfReviewAllowedAsIndependentQa"])
            self.assertEqual(r["independentAiContentReview"],"PENDING")
            self.assertIsNone(r["independentReviewerIdentity"])
            self.assertIsNone(r["reviewEvidenceSha256"])
            self.assertIsNone(r["officialAnswerEvidenceSha256"])
            self.assertEqual(r["v4ExactDigest8x2"],"PENDING")
            self.assertFalse(q["studentReleaseApproved"])
            self.assertFalse(q["deploy"])
            self.assertFalse(self.items[id]["ready"])
            self.assertTrue(all("HUMAN_TEACHER_CREDENTIAL" not in x for x in q["blockers"]))

    def test_20_sole_ledger_revision_is_not_the_current_q_and_webp(self):
        q=self.records["115-09-2-20"]
        self.assertEqual(q["coordinatorLedgerPriorQuestionRevision"],
                         "2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c")
        self.assertFalse(q["coordinatorLedgerPriorRevisionMatchesCurrentSource"])
        self.assertNotEqual(q["sourceTextRevision"],q["coordinatorLedgerPriorQuestionRevision"])
        self.assertTrue(self.items["115-09-2-20"]["ledgerRevisionMismatch"])
        self.assertIn("Q20_COORDINATOR_LEDGER_SOURCE_REVISION_DISCREPANCY_REQUIRES_A_MASTER_RECONCILIATION",q["blockers"])
        for id in ("115-09-2-07","115-09-2-09","115-09-2-16","115-09-2-18"):
            self.assertIsNone(self.items[id]["ledgerHistoricalRevision"])
            self.assertFalse(self.items[id]["ledgerRevisionMismatch"])

    def test_mutated_source_options_webp_or_teaching_fail_same_digest(self):
        for id,q in self.records.items():
            for name in ("question","option","originalWebp","teaching"):
                with self.subTest(id=id,changed=name):
                    m=copy.deepcopy(q)
                    if name=="question":
                        m["question"]+=" TAMPER"
                        self.assertNotEqual(source_rev(m),q["sourceTextRevision"])
                    elif name=="option":
                        m["options"][1]+=" TAMPER"
                        self.assertNotEqual(source_rev(m),q["sourceTextRevision"])
                    elif name=="originalWebp":
                        m["individualImageSha256"]="0"*64
                        self.assertNotEqual(source_rev(m),q["sourceTextRevision"])
                    else:
                        m["teaching"]["memory"]+=" TAMPER"
                        self.assertNotEqual(canonical(m["teaching"]),q["teachingCanonicalSha256"])

if __name__=="__main__":
    unittest.main()
