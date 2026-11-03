"""Five accounting/economics source SHA and math invariants, author only."""
import unittest,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/"sudu/teaching-candidates/114-role-b-prof2-20261102"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class TestB114Prof2(unittest.TestCase):
 def test_five_immutable_source_bound(self):
  b=read(F/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(5,0,0,0))
  qs={x["questionId"]:x for x in read(R/"sudu/data/processed/114/questions.json")["questions"]}
  ms={x["questionId"]:x for x in read(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  for row in b["items"]:
   id=row["questionId"];raw=(R/row["path"]).read_bytes();v=json.loads(raw);q=qs[id];m=ms[id]
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(row["webpSha256"],m["sha256"])
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(row["sourceRevision"],sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],sha({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":m["sha256"],"teaching":v["teaching"]}))
    o=v["teaching"]["optionExplanations"];self.assertEqual(set(o),set("ABCD"))
    self.assertEqual(len(set(x["reason"] for x in o.values())),4)
    self.assertEqual([k for k,x in o.items() if x["isCorrect"]],[v["answer"]])
    self.assertTrue(all(len(x["teacher"])>22 and len(x["elementary"])>8 for x in o.values()))
    self.assertGreaterEqual(len(v["teaching"]["solvingSteps"]),4)
    self.assertEqual(v["teaching"]["hasExamCalculation"],v["teaching"]["examCalculation"] is not None)
    self.assertIsNone(v["review"]["independentReviewer"])
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
 def test_arithmetic_substantive_invariants(self):
  # Accounting 06: discount periods and half payments
  costs=[0.5*.99+.5,0.5*.98+.5,0.5*.98+.5*.99,1]
  self.assertEqual(max(costs),costs[-1])
  self.assertAlmostEqual(costs[0],.995)
  self.assertAlmostEqual(costs[1],.99)
  self.assertAlmostEqual(costs[2],.985)
  # Economics 28 individual supply and ten firm horizontal addition.
  self.assertEqual([(10*p-2) for p in [1,2,3]],[8,18,28])
  self.assertEqual([(100*p-20) for p in [1,2,3]],[80,180,280])
  # Economics 29 demand linear and triangle CS.
  intercept=20+2*100/10
  self.assertEqual(intercept,40)
  newQ=10+(20-10)*(10/(40-20))
  self.assertEqual(newQ,15)
  self.assertEqual(.5*(intercept-10)*newQ,225)
if __name__=="__main__":unittest.main()
