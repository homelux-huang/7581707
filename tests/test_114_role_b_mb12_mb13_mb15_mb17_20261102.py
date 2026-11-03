"""114 math B author candidate source SHA / calculation and release negative tests."""
import hashlib,json,math,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"sudu/teaching-candidates/114-role-b-mb12-mb13-mb15-mb17-20261102"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class TestFourMath(unittest.TestCase):
 def test_source_bound_four_options_and_blocked(self):
  b=load(F/"batch.json");q={x["questionId"]:x for x in load(R/"sudu/data/processed/114/questions.json")["questions"]};m={x["questionId"]:x for x in load(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(4,0,0,0))
  for row in b["items"]:
   id=row["questionId"];raw=(R/row["path"]).read_bytes();v=json.loads(raw)
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(q[id]["question"],q[id]["options"],q[id]["answer"]))
    self.assertEqual(m[id]["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertEqual(v["source"]["webpSha256"],m[id]["sha256"])
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(row["sourceRevision"],sh({"question":q[id]["question"],"options":q[id]["options"],"singleQuestionWebpSha256":m[id]["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],sh({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":row["webpSha256"],"teaching":v["teaching"]}))
    c=v["teaching"]["examCalculation"];self.assertTrue(v["teaching"]["hasExamCalculation"])
    self.assertGreaterEqual(len(c["steps"]),7)
    self.assertTrue(c["given"] and c["formulaUse"] and c["substitution"] and c["unit"] and c["result"])
    self.assertEqual(c["option"],v["answer"])
    o=v["teaching"]["optionExplanations"];self.assertEqual(set(o),set("ABCD"))
    self.assertEqual(len(set(x["reason"] for x in o.values())),4)
    self.assertEqual([k for k,x in o.items() if x["isCorrect"]],[v["answer"]])
    self.assertTrue(all(len(x["teacher"])>20 and len(x["elementary"])>8 and len(x["reason"])>20 for x in o.values()))
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
    self.assertEqual(v["review"]["status"],"BLOCKED")
 def test_math_reverse_verification(self):
  # MB12 enumerate all and only y >= ceil(x/2).
  combinations=[(x,y) for x in [6,7,8] for y in range(x+1) if 2*y>=x]
  self.assertEqual(len(combinations),13)
  self.assertEqual([sum(1 for p in combinations if p[0]==x) for x in [6,7,8]],[4,4,5])
  # MB13 sample standard deviation uses n-1, not n.
  vals=[3,4,6,10,12];avg=sum(vals)/len(vals)
  self.assertEqual(avg,7)
  self.assertEqual(max(vals)-min(vals),9)
  self.assertEqual(vals[len(vals)//2],6)
  self.assertEqual(sum((v-avg)**2 for v in vals),60)
  self.assertAlmostEqual(math.sqrt(60/(len(vals)-1)),math.sqrt(15),places=12)
  # MB15 check all visited points of 5 presses, not only endpoints.
  x,y=1,4;visited={(x,y)}
  for press in range(5):
   for step in range(3):x+=1;visited.add((x,y))
   y-=1;visited.add((x,y))
  self.assertIn((5,3),visited);self.assertIn((7,2),visited)
  self.assertIn((16,-1),visited);self.assertNotIn((10,0),visited)
  # MB17 4 meat * C(5,3) * 4 sides, independent equivalent C(5,2).
  self.assertEqual(4*math.comb(5,3)*4,160)
  self.assertEqual(math.comb(5,3),math.comb(5,2))
if __name__=="__main__":unittest.main()
