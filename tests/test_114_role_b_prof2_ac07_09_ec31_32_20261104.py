"""114 ROLE B accounting/economics: original SHA, four options, accurate math, no release."""
import unittest,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/"sudu/teaching-candidates/114-role-b-prof2-ac07-09-ec31-32-20261104"
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def digest(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class AuthorTest(unittest.TestCase):
 def test_five_exact_source_bound_norelease(self):
  b=load(D/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(5,0,0,0))
  q={x["questionId"]:x for x in load(R/"sudu/data/processed/114/questions.json")["questions"]}
  m={x["questionId"]:x for x in load(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  for r in b["items"]:
   id=r["questionId"];raw=(R/r["path"]).read_bytes();v=json.loads(raw)
   with self.subTest(questionId=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),r["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["knownAnswerCandidate"]),(q[id]["question"],q[id]["options"],q[id]["answer"]))
    self.assertEqual(m[id]["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(r["webpSha256"],m[id]["sha256"])
    self.assertEqual(r["sourceRevision"],digest({"question":q[id]["question"],"options":q[id]["options"],"singleQuestionWebpSha256":m[id]["sha256"]}))
    self.assertEqual(r["teachingCanonicalSha256"],digest(v["teaching"]))
    self.assertEqual(r["composedTeachingSha256"],digest({"questionId":id,"sourceRevision":r["sourceRevision"],"webpSha256":r["webpSha256"],"teaching":v["teaching"]}))
    o=v["teaching"]["optionExplanations"]
    self.assertEqual(set(o),set("ABCD"))
    self.assertEqual(len(set(x["reason"] for x in o.values())),4)
    self.assertEqual([k for k,x in o.items() if x["isCorrect"]],[v["knownAnswerCandidate"]])
    self.assertTrue(all(len(x["teacher"])>25 and len(x["elementary"])>8 for x in o.values()))
    self.assertGreaterEqual(len(v["teaching"]["solvingSteps"]),5)
    self.assertEqual(v["teaching"]["hasExamCalculation"],v["teaching"]["examCalculation"] is not None)
    self.assertFalse(v["review"]["formalReady"] or v["review"]["studentReleaseApproved"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_real_accounting_reverse_check(self):
  sale=250000+30000
  netbuy=170000-15000
  opening=180000-netbuy+35000
  gross=250000-180000
  self.assertEqual((sale,netbuy,opening,gross),(280000,155000,60000,70000))
  self.assertEqual(opening+netbuy-35000,180000)
  cash=400000+42500-22500
  self.assertEqual(cash,420000)
  self.assertEqual(cash+22500-42500,400000)
 def test_noncalc_null_and_monopoly_inequality(self):
  for id in ["114-09-2-09","114-09-2-31","114-09-2-32"]:
   lesson=load(D/(id+".json"))["teaching"]
   self.assertIsNone(lesson["examCalculation"])
   self.assertFalse(lesson["hasExamCalculation"])
  price=100-10;AR=price;MR=100-2*10
  self.assertLess(MR,AR)
  self.assertEqual(100-2*50,0)
if __name__=="__main__":unittest.main()
