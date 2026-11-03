"""114 E01-05 B author draft validation only; G1/G2/G3 and E/D still pending."""
import unittest,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/"sudu/teaching-candidates/114-role-b-e01-e05-20261102"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sh(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()
class TestB114English(unittest.TestCase):
 def test_all_five(self):
  b=load(P/"batch.json")
  q={x["questionId"]:x for x in load(R/"sudu/data/processed/114/questions.json")["questions"]}
  m={x["questionId"]:x for x in load(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
  self.assertEqual((b["total"],b["newReady"],b["newMain"],b["newLive"]),(5,0,0,0))
  for row in b["items"]:
   id=row["questionId"];r=(R/row["path"]).read_bytes();v=json.loads(r);qq=q[id];mm=m[id]
   with self.subTest(id=id):
    self.assertEqual(hashlib.sha256(r).hexdigest(),row["fileSha256"])
    self.assertEqual((v["question"],v["options"],v["answer"]),(qq["question"],qq["options"],qq["answer"]))
    self.assertEqual(v["source"]["webpSha256"],mm["sha256"])
    self.assertEqual(mm["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(v["source"]["questionVerified"] or v["source"]["answerVerified"])
    self.assertEqual(row["sourceRevision"],sh({"question":qq["question"],"options":qq["options"],"singleQuestionWebpSha256":mm["sha256"]}))
    self.assertEqual(row["composedTeachingSha256"],sh({"questionId":id,"sourceRevision":row["sourceRevision"],"webpSha256":mm["sha256"],"teaching":v["teaching"],"enrichment":v["enrichment"]}))
    opts=v["teaching"]["optionExplanations"]
    self.assertEqual(set(opts),"ABCD")
    self.assertEqual([k for k,x in opts.items() if x["isCorrect"]],[v["answer"]])
    self.assertEqual(len(set(x["reason"] for x in opts.values())),4)
    self.assertTrue(all(len(x["reason"])>24 and len(x["teacher"])>24 and len(x["elementary"])>8 for x in opts.values()))
    self.assertGreaterEqual(len(v["teaching"]["solvingSteps"]),4)
    self.assertIsNone(v["teaching"]["examCalculation"])
    self.assertFalse(v["teaching"]["hasExamCalculation"])
    org=(qq["question"]+" "+" ".join(qq["options"])).lower()
    self.assertTrue(all(x["text"].lower() in org for x in v["enrichment"]["sourceHighlights"]))
    e=v["enrichment"]["newsExample"]
    self.assertIn(e["highlightActualForm"],e["english"])
    self.assertTrue(e["chinese"] and e["notAnArticleQuote"])
    self.assertFalse(v["review"]["studentReleaseApproved"] or v["review"]["formalReady"])
    self.assertIsNone(v["review"]["independentReviewer"])
 def test_fail_closed(self):
  b=load(P/"batch.json")
  self.assertTrue(all(not v["sourceAdmission"] and not v["roleEPass"] and not v["ready"] for v in b["items"]))
if __name__=="__main__":unittest.main()
