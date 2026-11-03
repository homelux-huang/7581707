"""114 Role B five profession1 author-only lessons, immutable original SHA, no release."""
import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/"sudu/teaching-candidates/114-role-b-prof1-20261102"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class CheckProf1(unittest.TestCase):
 def test_all_five_source_and_options(self):
  b=read(F/"batch.json");self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(5,0,0,0))
  bank={x["questionId"]:x for x in read(R/"sudu/data/processed/114/questions.json")["questions"]}
  man={x["questionId"]:x for x in read(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  for row in b["items"]:
   id=row["questionId"];raw=(R/row["path"]).read_bytes();v=json.loads(raw);q=bank[id];m=man[id]
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(row["webpSha256"],m["sha256"])
    self.assertEqual(row["sourceRevision"],sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],sha({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":m["sha256"],"teaching":v["teaching"]}))
    o=v["teaching"]["optionExplanations"];self.assertEqual(set(o),set("ABCD"))
    self.assertEqual([k for k,x in o.items() if x["isCorrect"]],[v["answer"]])
    self.assertEqual(len({x["reason"] for x in o.values()}),4)
    self.assertTrue(all(len(x["teacher"])>22 and len(x["elementary"])>8 for x in o.values()))
    self.assertGreaterEqual(len(v["teaching"]["solvingSteps"]),4)
    self.assertEqual(v["teaching"]["hasExamCalculation"],v["teaching"]["examCalculation"] is not None)
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_numeric_checks(self):
  self.assertEqual(60+(2000000*0.5)/40000,85)
  self.assertEqual(60*1.5,90)
  groups=[(int("1010101",2),int("127",8),int("57",16)),(int("1110001",2),int("157",8),int("71",16)),(int("1101101",2),int("155",8),int("6D",16)),(int("1011010",2),int("132",8),int("4A",16))]
  self.assertEqual([len(set(g))==1 for g in groups],[False,False,True,False])
if __name__=="__main__":unittest.main()
