"""ROLE B immutable author-only 114 economics 37–41 source and calculation checks."""
import hashlib, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"sudu/teaching-candidates/114-role-b-econ37-41-20261104"
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def digest(value): return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
class RoleB114Econ(unittest.TestCase):
 def test_author_five_exact(self):
  bank=read(ROOT/"sudu/data/processed/114/questions.json")
  manifest=read(ROOT/"sudu/data/processed/114/webp-manifest.json")
  qmap={q["questionId"]:q for q in bank["questions"]}
  mmap={m["questionId"]:m for m in manifest["items"]}
  batch=read(F/"batch.json")
  expected={"114-09-2-"+str(n) for n in range(37,42)}
  self.assertEqual({x["questionId"] for x in batch["items"]}, expected)
  self.assertEqual((batch["total"],batch["newReady"],batch["newMain"],batch["newLive"]),(5,0,0,0))
  self.assertFalse(batch["sourceApproved"] or batch["independentE"] or batch["requiresHumanTeacher"])
  self.assertTrue(batch["noRelease"])
  for row in batch["items"]:
   qid=row["questionId"];q=qmap[qid];m=mmap[qid]
   raw=(ROOT/row["path"]).read_bytes()
   obj=json.loads(raw)
   with self.subTest(qid=qid):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((obj["question"],obj["options"],obj["answer"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(obj["source"]["webpSha256"],m["sha256"])
    self.assertEqual(row["webpSha256"],m["sha256"])
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(obj["source"]["questionVerified"] or obj["source"]["answerVerified"])
    source=digest({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
    self.assertEqual(source,row["sourceRevision"])
    self.assertEqual(obj["source"]["sourceRevision"],source)
    composed=digest({"questionId":qid,"sourceRevision":source,"webpSha256":m["sha256"],"teaching":obj["teaching"]})
    self.assertEqual(composed,row["composedTeachingSha256"])
    self.assertEqual(obj["composedTeachingSha256"],composed)
    opt=obj["teaching"]["optionExplanations"]
    self.assertEqual(set(opt),set("ABCD"))
    self.assertEqual([k for k,v in opt.items() if v["isCorrect"]],[obj["answer"]])
    self.assertEqual(len({v["reason"] for v in opt.values()}),4)
    self.assertTrue(all(len(v["teacher"])>22 and len(v["elementary"])>8 for v in opt.values()))
    self.assertGreaterEqual(len(obj["teaching"]["solvingSteps"]),5)
    self.assertEqual(obj["teaching"]["hasExamCalculation"],obj["teaching"]["examCalculation"] is not None)
    self.assertIsNone(obj["review"]["independentReviewer"])
    self.assertFalse(obj["review"]["formalReady"] or obj["review"]["studentReleaseApproved"])
 def test_numeric_invariants(self):
  self.assertEqual((200+120)/0.04,8000)
  self.assertEqual(8000*0.04,320)
  y=950;yd=y-50;c=100+0.5*yd
  self.assertEqual(c+300+100,y)
  for n in (750,800,1000):
   self.assertNotEqual(100+0.5*(n-50)+300+100,n)
  self.assertEqual(1/(1-0.5),2)
  self.assertEqual(round(1/(1-0.8)),5)
if __name__=="__main__":unittest.main()
