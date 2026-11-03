"""Three math lessons: full computation, original-source SHA, and fail-closed release."""
import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"sudu/teaching-candidates/114-role-b-mb09-mb14-mb18-20261102"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sh(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class TestMath114SourceBound(unittest.TestCase):
 def test_original_and_every_calc(self):
  bank={x["questionId"]:x for x in load(R/"sudu/data/processed/114/questions.json")["questions"]}
  manifest={x["questionId"]:x for x in load(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  b=load(F/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(3,0,0,0))
  expected={"114-00-MB-09":"C","114-00-MB-14":"C","114-00-MB-18":"B"}
  for row in b["items"]:
   id=row["questionId"];raw=(R/row["path"]).read_bytes();v=json.loads(raw);q=bank[id];m=manifest[id]
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(v["answer"],expected[id])
    self.assertEqual(v["source"]["webpSha256"],m["sha256"])
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(row["sourceRevision"],sh({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}))
    self.assertEqual(v["source"]["sourceRevision"],row["sourceRevision"])
    self.assertEqual(row["composedTeachingSha256"],sh({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":m["sha256"],"teaching":v["teaching"]}))
    self.assertEqual(v["composedTeachingSha256"],row["composedTeachingSha256"])
    lesson=v["teaching"];calc=lesson["examCalculation"];self.assertTrue(lesson["hasExamCalculation"])
    self.assertGreaterEqual(len(calc["steps"]),6)
    self.assertTrue(calc["given"] and calc["substitution"] and calc["formulaUse"] and calc["result"] and calc["unit"])
    self.assertEqual(calc["option"],v["answer"])
    opts=lesson["optionExplanations"];self.assertEqual(set(opts),set("ABCD"))
    self.assertEqual([k for k,x in opts.items() if x["isCorrect"]],[v["answer"]])
    self.assertEqual(len(set(x["reason"] for x in opts.values())),4)
    self.assertTrue(all(len(x["teacher"])>20 and len(x["elementary"])>8 and len(x["reason"])>20 for x in opts.values()))
    self.assertEqual(v["review"]["status"],"BLOCKED")
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_independent_arithmetic_reverse_checks(self):
  # MB09 unit ratio: 3nm / 0.017mm must be 1.7647e-4, not 1.8e-5.
  self.assertAlmostEqual((3e-9)/(0.017e-3),1.764705882352941e-4,places=12)
  # MB14 expected pay fraction and complementary saving fraction.
  pay=sum(f*n for f,n in [(0.9,32),(0.8,10),(0.6,5),(0.3,2),(0.1,1)])/50
  savings=sum((1-f)*n for f,n in [(0.9,32),(0.8,10),(0.6,5),(0.3,2),(0.1,1)])/50
  self.assertAlmostEqual(pay,0.81,places=12)
  self.assertAlmostEqual(savings,0.19,places=12)
  self.assertAlmostEqual(pay+savings,1,places=12)
  # MB18 add equations first; exact p,q rational check without rounding.
  from fractions import Fraction
  q=Fraction(1325,11);p=Fraction(-1105,11)
  self.assertEqual(35*p+46*q,2025);self.assertEqual(65*p+54*q,-25)
  self.assertEqual(p+q,20);self.assertEqual(-(p+q)/20,-1)
if __name__=="__main__":unittest.main()
