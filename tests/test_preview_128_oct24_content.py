import json, hashlib, unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/"sudu"/"teaching-drafts"/"preview-128-20261023"
ROOT=Path(__file__).resolve().parents[1]
def get(p):return json.loads((BASE/p).read_text(encoding="utf8"))
class SelfReview20261024(unittest.TestCase):
 def test_10_sha_and_false_gates(self):
  m=get("content-review-delivery-20261024.json")
  self.assertEqual(len(m["items"]),10)
  self.assertFalse(m["readyForDeployment"])
  p=get("progress.json")
  self.assertEqual((p["scopeTotal"],p["fullyAccepted"],p["deployed"]),(128,0,0))
  for i in m["items"]:
   q=get(i["questionId"]+".json")
   self.assertFalse(q["studentReleaseApproved"])
   self.assertFalse(q["deploy"])
   self.assertEqual(q["qa"]["independentTeachingReview"],"PENDING")
   self.assertEqual(q["qa"]["uiReview"],"PENDING")
   self.assertEqual(hashlib.sha256((ROOT/"sudu"/q["image"]).read_bytes()).hexdigest(),i["originalImageSha256"])
   digest=hashlib.sha256(json.dumps(q["teaching"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
   self.assertEqual(digest,i["teachingDigestSha256"])
 def test_disputes_remain(self):
  for id,a in [("115-09-1-07","B"),("115-09-1-33","A"),("115-09-2-28","A")]:
   q=get(id+".json");self.assertTrue(q["answerComparison"]["conflictWarningRequired"]);self.assertEqual(q["answerComparison"]["officialAnswer"],a)
   self.assertTrue(q["teaching"]["stepByStep"]["needsReview"])
  self.assertIn("發行成本",get("115-09-1-07.json")["teaching"]["optionExplanations"]["C"]["teacher"])
  self.assertIn("雜湊",get("115-09-1-33.json")["teaching"]["stepByStep"]["steps"][2]["content"])
 def test_numeric_and_original_sqrt(self):
  m=get("115-09-2-28.json")["teaching"]
  self.assertEqual(len(set(x["why"] for x in m["examCalculation"]["substitutionAndSteps"])),9)
  self.assertIn("未明示總預算",m["concept"])
  tu=[[0,20,24,25,23],[0,5,7,8,8],[0,15,21,18,12]]
  def val(n):
   prices=[40,50,60]
   return sum(x*p for x,p in zip(n,prices)),sum(g[x] for x,g in zip(n,tu)),[(g[x]-g[x-1])/p for x,g,p in zip(n,tu,prices)]
  self.assertEqual(val([2,1,2]),(250,50,[.1,.1,.1]))
  self.assertEqual(val([3,3,2]),(390,54,[.025,.02,.1]))
  self.assertEqual(500000-2*((500000-5000)/5)-(500000-2*((500000-5000)/5)-2000)*2/3,102000)
  self.assertIn("距離是√2",get("115-00-MB-25.json")["teaching"]["concept"])
 def test_steps_consistency(self):
  s=(BASE/"solution-steps-128.js").read_text(encoding="utf8")
  key="window.PREVIEW_STEP_BY_STEP_DRAFT = "
  data=json.loads(s.split(key,1)[1].strip().rstrip(";"))
  for id in ["115-09-1-07","115-09-1-33","115-09-2-28"]:
   q=get(id+".json");k=q["subject"]+"|"+str(q["questionNumber"])
   self.assertEqual(data["byQuestion"][k],q["teaching"]["stepByStep"])
 def test_english_answer_notice_now_verified(self):
  for n in (1,2,3):
   q=get(f"115-00-E-{n:02d}.json")
   self.assertIn("已有既存核實證據",q["teaching"]["source"]["officialIssueExplanation"])
   self.assertIn("originalText",q["qa"]["officialNoticeHistoricalRecheck20261024"])
if __name__=="__main__": unittest.main()
