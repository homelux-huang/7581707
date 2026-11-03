"""Role B six source-bound math author lessons: immutable SHA / math / no release."""
import unittest,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"sudu/teaching-candidates/114-role-b-mb03-07-10-11-19-25-20261102"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class CheckMathSix(unittest.TestCase):
 def test_source_hash_four_options_and_no_release(self):
  b=load(F/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(6,0,0,0))
  qs={x["questionId"]:x for x in load(R/"sudu/data/processed/114/questions.json")["questions"]}
  ms={x["questionId"]:x for x in load(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  for row in b["items"]:
   qid=row["questionId"];raw=(R/row["path"]).read_bytes();v=json.loads(raw);q=qs[qid];m=ms[qid]
   with self.subTest(qid=qid):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(v["source"]["webpSha256"],m["sha256"])
    self.assertEqual(row["sourceRevision"],sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],sha({"questionId":qid,"sourceRevision":row["sourceRevision"],"webpSha256":row["webpSha256"],"teaching":v["teaching"]}))
    o=v["teaching"]["optionExplanations"];self.assertEqual(set(o),set("ABCD"))
    self.assertEqual([k for k,x in o.items() if x["isCorrect"]],[v["answer"]])
    self.assertEqual(len({x["reason"] for x in o.values()}),4)
    self.assertTrue(all(len(x["teacher"])>22 and len(x["elementary"])>8 for x in o.values()))
    c=v["teaching"]["examCalculation"];self.assertTrue(v["teaching"]["hasExamCalculation"])
    self.assertGreaterEqual(len(c["steps"]),7)
    self.assertTrue(c["given"] and c["formulaUse"] and c["substitution"] and c["unit"] and c["result"])
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_reverse_numeric(self):
  self.assertEqual(max(6+3*y for y in range(-2,3)),12)
  expr=math.sin(math.radians(10))**2+2*math.sin(math.radians(20))**2+4*math.sin(math.radians(30))**2+2*math.sin(math.radians(70))**2+math.sin(math.radians(80))**2
  self.assertAlmostEqual(expr,4,places=10)
  self.assertEqual(2-6,-4)
  a,b=math.log(2,25),math.log(3,25)
  self.assertAlmostEqual(5**(3*a+2*b+1),30*math.sqrt(2),places=9)
  d=lambda A,B,C,y:abs(B*y+C)/math.hypot(A,B)
  self.assertGreater(d(3,4,2,1),1)
  self.assertEqual(d(3,4,2,2),2)
  self.assertLess(d(3,4,2,3),3)
  odd=[-5*(-3)**k for k in range(5)];even=[55+3*k for k in range(5)]
  self.assertEqual((sum(odd),sum(even),sum(odd)+sum(even)),(-305,305,0))
if __name__=="__main__":unittest.main()
