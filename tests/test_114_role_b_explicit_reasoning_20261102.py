"""Role B 114 four-question source-preserving pedagogy remediation, no student release."""
import hashlib
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-candidates/114-role-b-20261025"
IDS = ["114-00-C-01", "114-00-C-02", "114-00-C-03", "114-00-E-06"]
ANCHORS = {
    "114-00-C-01": ["功德無諒","四海豐饒","千頭萬緒","倨傲"],
    "114-00-C-02": ["岳飛","半碗飯","船身","母親"],
    "114-00-C-03": ["菜蔬稻稗","品類","群類","橐駝"],
    "114-00-E-06": ["authority","bargain","courtesy","infection"],
}
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(v):
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
class TestSourceSafePedagogy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=load(BASE/"batch.json")
        cls.rows={v["questionId"]:v for v in b["items"]}
        cls.qbank={q["questionId"]:q for q in load(ROOT/"sudu/data/processed/114/questions.json")["questions"]}
        cls.manifest={r["questionId"]:r for r in load(ROOT/"sudu/data/processed/114/webp-manifest.json")["items"]}
    def test_four_question_SHA_source_options_and_bilingual_reasons(self):
        for qid in IDS:
            with self.subTest(questionId=qid):
                raw=(BASE/(qid+".json")).read_bytes()
                c=json.loads(raw)
                row=self.rows[qid]
                q=self.qbank[qid]
                m=self.manifest[qid]
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
                self.assertEqual(q["answer"],c["answer"])
                self.assertEqual(c["source"]["questionRevision"],row["sourceRevision"])
                self.assertEqual(c["source"]["webpSha256"],row["webpSha256"])
                self.assertEqual(m["sha256"],row["webpSha256"])
                self.assertEqual(digest({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}),row["sourceRevision"])
                self.assertEqual(set(c["teaching"]["optionExplanations"]),{"A","B","C","D"})
                self.assertEqual(len(c["teaching"]["solvingSteps"])>=4,True)
                self.assertTrue(all(len(s)>=24 for s in c["teaching"]["solvingSteps"]))
                reasons=[]
                for opt,anchor in zip("ABCD",ANCHORS[qid]):
                    v=c["teaching"]["optionExplanations"][opt]
                    self.assertIn(anchor,v["reason"])
                    self.assertGreaterEqual(len(v["reason"]),26)
                    self.assertGreaterEqual(len(v["teacher"]),14)
                    self.assertGreaterEqual(len(v["elementary"]),10)
                    reasons.append(v["reason"])
                    self.assertEqual(v["isCorrect"],opt==c["answer"])
                self.assertEqual(len(set(reasons)),4)
                self.assertEqual(c["authorCorrection"]["reviewLevel"],"AUTHOR_SELF_CHECK_ONLY")
                self.assertNotEqual(c["composedTeachingSha256"],c["authorCorrection"]["priorComposedTeachingSha256"])
                payload={"questionId":qid,"sourceRevision":c["source"]["questionRevision"],"webpSha256":c["source"]["webpSha256"],"teaching":c["teaching"],"enrichment":c["enrichment"]}
                self.assertEqual(digest(payload),c["composedTeachingSha256"])
                self.assertEqual(c["composedTeachingSha256"],row["composedTeachingSha256"])
                self.assertFalse(c["teaching"]["hasExamCalculation"])
                self.assertIsNone(c["teaching"]["examCalculation"])
                self.assertEqual(c["review"]["status"],"BLOCKED")
                self.assertFalse(c["review"]["studentReleaseApproved"])
                self.assertFalse(c["review"]["formalReady"])
                self.assertIsNone(c["review"]["independentReviewer"])
    def test_reject_generic_or_faked_approval(self):
        self.assertNotEqual(len(set(["意思不同。"]*4)),4)
        for qid in IDS:
            c=load(BASE/(qid+".json"))
            self.assertEqual(c["review"]["independentAiContentReview"]["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
            self.assertIsNone(c["review"]["independentAiContentReview"]["trustedEvidencePath"])
            self.assertTrue(c["authorCorrection"]["requiresIndependentRoleE"])
if __name__=="__main__":
    unittest.main()
