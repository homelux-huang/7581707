"""114 Year Math B21 B22 B24 B-author calculations; no source/E/D release."""
import unittest,hashlib,json,math
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"sudu/teaching-candidates/114-role-b-mb21-mb22-mb24-20261102"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class CheckThreeMath(unittest.TestCase):
 def test_source_SHA_and_status(self):
  b=read(F/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(3,0,0,0))
  q={x["questionId"]:x for x in read(ROOT/"sudu/data/processed/114/questions.json")["questions"]}
  m={x["questionId"]:x for x in read(ROOT/"sudu/data/processed/114/webp-manifest.json")["items"]}
  for row in b["items"]:
   id=row["questionId"];raw=(ROOT/row["path"]).read_bytes();v=json.loads(raw);orig=q[id]
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(orig["question"],orig["options"],orig["answer"]))
    self.assertEqual(m[id]["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(v["source"]["webpSha256"],m[id]["sha256"])
    self.assertEqual(row["sourceRevision"],digest({"question":orig["question"],"options":orig["options"],"singleQuestionWebpSha256":m[id]["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],digest({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":m[id]["sha256"],"teaching":v["teaching"]}))
    c=v["teaching"]["examCalculation"];self.assertTrue(v["teaching"]["hasExamCalculation"])
    self.assertGreaterEqual(len(c["steps"]),7)
    self.assertTrue(c["given"] and c["substitution"] and c["formulaUse"] and c["unit"] and c["result"])
    self.assertEqual(c["option"],v["answer"])
    options=v["teaching"]["optionExplanations"];self.assertEqual(set(options),set("ABCD"))
    self.assertEqual([k for k,x in options.items() if x["isCorrect"]],[v["answer"]])
    self.assertEqual(len({x["reason"] for x in options.values()}),4)
    self.assertTrue(all(len(x["teacher"])>20 and len(x["elementary"])>8 for x in options.values()))
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_exact_math_invariants(self):
  # MB21 4 non-watermelon distinct in 4!, select 3 of 5 slots, order W distinct in 3!.
  self.assertEqual(math.factorial(4)*math.comb(5,3)*math.factorial(3),1440)
  self.assertLess(1440,math.factorial(7))
  # MB22 independent integer exhaustive minimization and dual weighted lower bound.
  feasible=[(200*a+210*b,a,b) for a in range(50) for b in range(50) if 3*a+2*b>=48 and 3*a+4*b>=72]
  self.assertEqual(min(feasible),(4120,8,12))
  L1,L2=Fraction(85,3),Fraction(115,3)
  self.assertEqual(3*L1+3*L2,200)
  self.assertEqual(2*L1+4*L2,210)
  self.assertEqual(L1*48+L2*72,4120)
  # MB24 weighted-score reverse check.
  M=Fraction(61,1)
  self.assertEqual(50*80+950*(M-1),1000*M)
  self.assertEqual(Fraction(50*80+950*60,1000),61)
if __name__=="__main__":unittest.main()
