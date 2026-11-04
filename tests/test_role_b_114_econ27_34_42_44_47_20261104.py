"""ROLE B 114 economics 27/34/42/44/47 author-only SHA, source and math QA."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "sudu/teaching-candidates/114-role-b-econ27-34-42-44-47-20261104"
IDS = {f"114-09-2-{n:02d}" for n in (27,34,42,44,47)}

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))
def sha256(data):
    return hashlib.sha256(data).hexdigest()
def digest(obj):
    return sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))

class AuthorOnly(unittest.TestCase):
    def test_five_source_exact_and_fail_closed(self):
        bank=load(ROOT/"sudu/data/processed/114/questions.json")
        manifest=load(ROOT/"sudu/data/processed/114/webp-manifest.json")
        qs={q["questionId"]:q for q in bank["questions"]}
        ms={m["questionId"]:m for m in manifest["items"]}
        batch=load(DIR/"batch.json")
        self.assertEqual(set(x["questionId"] for x in batch["items"]), IDS)
        self.assertEqual((batch["total"],batch["newReady"],batch["newMain"],batch["newLive"]),(5,0,0,0))
        self.assertTrue(batch["noRelease"])
        self.assertFalse(batch["independentE"])
        self.assertFalse(batch["sourceApproved"])
        self.assertFalse(batch["requiresHumanTeacher"])
        for row in batch["items"]:
            qid=row["questionId"]
            with self.subTest(qid=qid):
                q=qs[qid]
                m=ms[qid]
                raw=(ROOT/row["path"]).read_bytes()
                item=json.loads(raw)
                self.assertEqual(sha256(raw),row["fileSha256"])
                self.assertEqual((item["question"],item["options"],item["answer"]),(q["question"],q["options"],q["answer"]))
                self.assertEqual(row["webpSha256"],m["sha256"])
                self.assertEqual(item["source"]["webpSha256"],m["sha256"])
                self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
                self.assertFalse(item["source"]["questionVerified"])
                self.assertFalse(item["source"]["answerVerified"])
                src=digest({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
                self.assertEqual((src,item["source"]["sourceRevision"]),(row["sourceRevision"],row["sourceRevision"]))
                d=digest({"questionId":qid,"sourceRevision":src,"webpSha256":m["sha256"],"teaching":item["teaching"]})
                self.assertEqual(d,item["composedTeachingSha256"])
                self.assertEqual(d,row["composedTeachingSha256"])
                ex=item["teaching"]["optionExplanations"]
                self.assertEqual(set(ex),set("ABCD"))
                self.assertEqual([label for label,value in ex.items() if value["isCorrect"]],[q["answer"]])
                self.assertEqual(len(set(v["reason"] for v in ex.values())),4)
                self.assertTrue(all(len(v["teacher"])>22 and len(v["elementary"])>8 for v in ex.values()))
                self.assertGreaterEqual(len(item["teaching"]["solvingSteps"]),5)
                self.assertEqual(item["teaching"]["hasExamCalculation"],item["teaching"]["examCalculation"] is not None)
                self.assertIsNone(item["review"]["independentReviewer"])
                self.assertFalse(item["review"]["formalReady"])
                self.assertFalse(item["review"]["studentReleaseApproved"])

    def test_author_math_and_known_ocr_blocker(self):
        q27=load(DIR/"114-09-2-27.json")
        self.assertIn("A_G2_MATH_Q_SQUARED_SYMBOL_AND_MC_CONSISTENCY_CONFIRM",q27["review"]["blockers"])
        self.assertIn("q2",q27["question"])
        self.assertEqual(9**2-16*9+74,11)
        self.assertEqual((14-11)*9,27)
        self.assertEqual((14*9)-(11*9),27)
        self.assertEqual(q27["teaching"]["examCalculation"]["result"],"27")
        for qid in ("34","42","44","47"):
            obj=load(DIR/f"114-09-2-{qid}.json")
            self.assertFalse(obj["teaching"]["hasExamCalculation"])
            self.assertIsNone(obj["teaching"]["examCalculation"])
        q44=load(DIR/"114-09-2-44.json")
        self.assertIn("②③④",q44["teaching"]["memory"])
        self.assertEqual(q44["answer"],"D")

if __name__ == "__main__":
    unittest.main()
