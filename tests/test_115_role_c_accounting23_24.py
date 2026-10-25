"""Role C Issue36 accounting 115 Q23-24 source-bound AUTHOR draft tests. No approval."""
import copy
import hashlib
import json
import unittest
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/teaching-candidates/115-role-c-accounting23-24-20261025"
EXPECTED={"115-09-2-23":"A","115-09-2-24":"B"}
SHARED_SHA="18031e91e12d7083d5d9c0fa39b60191fe6c13a295d102e4f27d8cd916ff7343"

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canon(obj):
    return sha(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8"))

def source_revision(q):
    return canon({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":q["imageSha256"]})

def shared_revision(q):
    v=q["sharedMaterial"]
    return canon({"sharedMaterialId":v["sharedMaterialId"],"text":v["text"],"outputSha256":v["imageSha256"]})

class AccountingDraftChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((BASE/"batch.json").read_text(encoding="utf-8"))
        cls.data={}
        for item in cls.batch["items"]:
            cls.data[item["questionId"]]=json.loads((ROOT/item["path"]).read_text(encoding="utf-8"))

    def test_exact_sources_digests_and_tamper_provenance(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-ACCOUNTING-23-24-20261025-04")
        self.assertEqual(b["claimedAtUtc"],"2026-10-25T05:06:58Z")
        self.assertEqual((b["newReady"],b["newLive"]),(0,0))
        self.assertEqual(set(self.data),set(EXPECTED))
        for item in b["items"]:
            q=self.data[item["questionId"]]
            with self.subTest(qid=q["questionId"]):
                self.assertEqual(sha((ROOT/item["path"]).read_bytes()),item["fileSha256"])
                self.assertEqual(q["sourceTextRevision"],item["sourceTextRevision"])
                self.assertEqual(q["sourceTextRevision"],source_revision(q))
                self.assertEqual(q["teachingCanonicalSha256"],item["teachingSha256"])
                self.assertEqual(canon(q["teaching"]),item["teachingSha256"])
                self.assertEqual(q["imageSha256"],item["imageSha256"])
                self.assertEqual(q["sharedMaterial"]["imageSha256"],SHARED_SHA)
                self.assertEqual(q["sharedMaterial"]["qaStatus"],"PENDING_INDIVIDUAL_VISUAL_QA")
                self.assertEqual(shared_revision(q),item["sharedMaterialRevision"])
                self.assertEqual(shared_revision(q),q["sharedMaterial"]["sharedMaterialRevision"])
                self.assertEqual(q["answerCandidate"],EXPECTED[q["questionId"]])
                self.assertFalse(q["sourceQuestionVerified"])
                self.assertFalse(q["sourceAnswerVerified"])
                self.assertFalse(q["studentReleaseApproved"])
                self.assertFalse(q["deploy"])
                self.assertFalse(item["ready"])
                self.assertEqual(q["review"]["independentAiContentReview"],"PENDING")
                self.assertTrue(q["review"]["distinctAuthorRequired"])
                self.assertFalse(q["review"]["selfReviewAllowedAsIndependentQa"])
                self.assertIsNone(q["review"]["independentAiReviewerIdentity"])
                self.assertFalse(q["review"]["newBlindSolveClaimed"])
                self.assertIsNone(q["review"]["officialAnswerEvidenceSha256"])

    def test_four_individual_two_level_explanations_and_formula_visibility(self):
        for qid,q in self.data.items():
            with self.subTest(qid=qid):
                t=q["teaching"]
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([c for c in "ABCD" if t["optionExplanations"][c]["isCorrect"]],[EXPECTED[qid]])
                for c in "ABCD":
                    ex=t["optionExplanations"][c]
                    for key in ("teacher","elementary","reason"):
                        self.assertGreaterEqual(len(ex[key]),15)
                for key in ("teacherSummary","elementarySummary","concept","memory","highlights","stepByStep"):
                    self.assertTrue(t[key])
                self.assertTrue(t["hasExamCalculation"])
                calc=t["examCalculation"]
                self.assertEqual(calc["option"],EXPECTED[qid])
                for key in ("given","formulaUse","substitution","steps","result","unit","verification"):
                    self.assertTrue(calc[key])
                self.assertGreaterEqual(len(calc["steps"]),9)
                self.assertIn("元",calc["unit"])

    def test_23_exact_balance_sheet_ratios_and_option_a(self):
        assets=1_950_000
        liabilities=Fraction(assets,1)/Fraction(5,2)
        current_liabilities=liabilities/Fraction(13,5)
        ca=3*current_liabilities
        qa=Fraction(4,5)*current_liabilities
        wc=ca-current_liabilities
        self.assertEqual((liabilities,current_liabilities,ca,qa,wc),
                         (780_000,300_000,900_000,240_000,600_000))
        self.assertEqual(qa/current_liabilities,Fraction(4,5))
        self.assertEqual(ca/current_liabilities,3)
        q=self.data["115-09-2-23"]
        self.assertIn("240,000",q["teaching"]["examCalculation"]["result"])
        self.assertIn("600,000",q["teaching"]["examCalculation"]["result"])
        self.assertEqual(q["answerCandidate"],"A")
        self.assertNotEqual(Fraction(270000,300000),Fraction(4,5))
        self.assertGreater(1_000_000,ca)

    def test_24_period_end_entries_new_ratios_and_option_b(self):
        unearned_rent=Fraction(27_000*2,9)
        unexpired_insurance=Fraction(45_000*8,12)
        self.assertEqual((unearned_rent,unexpired_insurance),(6_000,30_000))
        ca,cl,qa=900_000+unexpired_insurance,300_000+unearned_rent,240_000
        correct_cr=Fraction(ca,cl)
        correct_qr=Fraction(qa,cl)
        self.assertGreater(correct_cr,3)
        self.assertLess(correct_qr,Fraction(4,5))
        self.assertEqual(correct_cr,Fraction(155,51))
        self.assertEqual(correct_qr,Fraction(40,51))
        q=self.data["115-09-2-24"]
        steps=" ".join(q["teaching"]["examCalculation"]["steps"])
        self.assertIn("租金收入6,000",steps)
        self.assertIn("預收租金6,000",steps)
        self.assertIn("預付保險費30,000",steps)
        self.assertIn("保險費30,000",steps)
        self.assertIn("3.0392",q["teaching"]["optionExplanations"]["B"]["teacher"])
        self.assertIn("0.7843",q["teaching"]["optionExplanations"]["B"]["teacher"])
        self.assertEqual(q["answerCandidate"],"B")

    def test_coordinator_revision_mismatch_blocks_both(self):
        for q in self.data.values():
            self.assertFalse(q["coordinatorLedgerRevisionMatchesCurrentSource"])
            self.assertNotEqual(q["coordinatorLedgerHistoricalRevision"],q["sourceTextRevision"])
            self.assertIn("COORDINATOR_LEDGER_SOURCE_REVISION_MISMATCH_NEEDS_MASTER_A_RECONCILIATION",q["blockers"])
            self.assertIn("ORIGINAL_SHARED_23_24_IMAGE_VISUAL_QA_PENDING",q["blockers"])
            self.assertIn("DISTINCT_INDEPENDENT_AI_CONTENT_REVIEW_EVIDENCE_PENDING",q["blockers"])
            self.assertNotIn("studentReleaseApproved",q["review"])
            self.assertTrue(q["review"]["arithmeticRecomputedAfterKnownAnswer"] if "arithmeticRecomputedAfterKnownAnswer" in q["review"] else q["review"]["knownAnswerBeforeDerivation"])

    def test_source_shared_and_teaching_changes_invalidate_digests(self):
        for qid,q in self.data.items():
            with self.subTest(qid=qid):
                mutated=copy.deepcopy(q)
                mutated["question"]+=" TAMPER"
                self.assertNotEqual(source_revision(mutated),q["sourceTextRevision"])
                mutated=copy.deepcopy(q)
                mutated["options"][0]+=" TAMPER"
                self.assertNotEqual(source_revision(mutated),q["sourceTextRevision"])
                mutated=copy.deepcopy(q)
                mutated["imageSha256"]="0"*64
                self.assertNotEqual(source_revision(mutated),q["sourceTextRevision"])
                mutated=copy.deepcopy(q)
                mutated["sharedMaterial"]["text"]+=" TAMPER"
                self.assertNotEqual(shared_revision(mutated),q["sharedMaterial"]["sharedMaterialRevision"])
                mutated=copy.deepcopy(q)
                mutated["sharedMaterial"]["imageSha256"]="0"*64
                self.assertNotEqual(shared_revision(mutated),q["sharedMaterial"]["sharedMaterialRevision"])
                mutated=copy.deepcopy(q)
                mutated["teaching"]["memory"]+=" TAMPER"
                self.assertNotEqual(canon(mutated["teaching"]),q["teachingCanonicalSha256"])

if __name__=="__main__":
    unittest.main()
