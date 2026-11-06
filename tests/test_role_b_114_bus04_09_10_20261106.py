"""114 Role B 商業概論 04/09/10 immutable source and author-only teaching QA."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"sudu/teaching-candidates/114-role-b-bus04-09-10-20261106"
IDS={f"114-09-1-{s}" for s in ("04","09","10")}
def read(p):
    return json.loads(p.read_text(encoding="utf-8"))
def hashobj(v):
    return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

class Test114BAuthoredBusiness(unittest.TestCase):
    def test_frozen_source_and_four_option_teaching(self):
        bank=read(ROOT/"sudu/data/processed/114/questions.json")
        manifest=read(ROOT/"sudu/data/processed/114/webp-manifest.json")
        qs={x["questionId"]:x for x in bank["questions"]}
        ms={x["questionId"]:x for x in manifest["items"]}
        batch=read(F/"batch.json")
        self.assertEqual(set(x["questionId"] for x in batch["items"]), IDS)
        self.assertEqual((batch["total"],batch["newReady"],batch["newMain"],batch["newLive"]),(3,0,0,0))
        self.assertFalse(batch["sourceApproved"] or batch["independentE"] or batch["requiresHumanTeacher"])
        self.assertTrue(batch["noRelease"])
        for row in batch["items"]:
            qid=row["questionId"]
            with self.subTest(qid=qid):
                q=qs[qid];m=ms[qid]
                raw=(ROOT/row["path"]).read_bytes()
                o=json.loads(raw)
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
                self.assertEqual((o["question"],o["options"],o["answer"]),(q["question"],q["options"],q["answer"]))
                self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
                self.assertEqual(m["sha256"],row["webpSha256"])
                self.assertEqual(m["sha256"],o["source"]["webpSha256"])
                self.assertFalse(o["source"]["questionVerified"] or o["source"]["answerVerified"])
                src=hashobj({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
                self.assertEqual(src,row["sourceRevision"])
                self.assertEqual(src,o["source"]["sourceRevision"])
                composed=hashobj({"questionId":qid,"sourceRevision":src,"webpSha256":m["sha256"],"teaching":o["teaching"]})
                self.assertEqual(composed,row["composedTeachingSha256"])
                self.assertEqual(composed,o["composedTeachingSha256"])
                t=o["teaching"];v=t["optionExplanations"]
                self.assertEqual(set(v),set("ABCD"))
                self.assertEqual([c for c,z in v.items() if z["isCorrect"]],[q["answer"]])
                self.assertEqual(len(set(z["reason"] for z in v.values())),4)
                self.assertTrue(all(len(z["teacher"])>30 and len(z["elementary"])>10 for z in v.values()))
                self.assertGreaterEqual(len(t["solvingSteps"]),5)
                self.assertFalse(t["hasExamCalculation"])
                self.assertIsNone(t["examCalculation"])
                self.assertIsNone(o["review"]["independentReviewer"])
                self.assertFalse(o["review"]["formalReady"] or o["review"]["studentReleaseApproved"])
    def test_business_specific_invariants(self):
        lesson={n:read(F/f"114-09-1-{n}.json") for n in ("04","09","10")}
        self.assertEqual([lesson[n]["answer"] for n in ("04","09","10")],["A","A","D"])
        self.assertIn("選擇性配銷",lesson["04"]["teaching"]["optionExplanations"]["B"]["teacher"])
        self.assertIn("工作擴大化",lesson["09"]["teaching"]["optionExplanations"]["D"]["teacher"])
        self.assertIn("信用限額",lesson["10"]["teaching"]["optionExplanations"]["B"]["teacher"])
        self.assertIn("交易動機",lesson["10"]["teaching"]["optionExplanations"]["C"]["teacher"])

if __name__=="__main__": unittest.main()
