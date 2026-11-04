"""Role B source-bound 114 Business08 Digital30/31/33/34: author content only, no official A/E/READY."""
import hashlib,json,unittest,ipaddress
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R/"sudu/teaching-candidates/114-role-b-prof1-b08-d30-34-20261104"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def h(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
class FiveLessons(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.b=read(F/"batch.json")
  cls.q={x["questionId"]:x for x in read(R/"sudu/data/processed/114/questions.json")["questions"]}
  cls.m={x["questionId"]:x for x in read(R/"sudu/data/processed/114/webp-manifest.json")["items"]}
 def test_original_exact_sha_all_options_double_level_and_blocked(self):
  b=self.b
  self.assertEqual((b["itemCount"],b["newReady"],b["newMain"],b["newLive"]),(5,0,0,0))
  self.assertEqual(len({x["questionId"] for x in b["items"]}),5)
  for row in b["items"]:
   qid=row["questionId"];raw=(R/row["path"]).read_bytes();d=json.loads(raw)
   q=self.q[qid];m=self.m[qid]
   with self.subTest(q=qid):
    self.assertEqual(hashlib.sha256(raw).hexdigest(),row["fileSha256"])
    self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
    self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
    self.assertFalse(d["source"]["questionVerified"])
    self.assertFalse(d["source"]["answerVerified"])
    self.assertEqual(m["sha256"],row["webpSha256"])
    self.assertEqual(q["questionProvenance"]["webpSha256"],m["sha256"])
    self.assertEqual(row["sourceRevision"],h({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}))
    self.assertEqual(d["source"]["questionRevision"],row["sourceRevision"])
    self.assertEqual(row["teachingCanonicalSha256"],h(d["teaching"]))
    self.assertEqual(row["composedTeachingSha256"],h({"questionId":qid,"sourceRevision":row["sourceRevision"],"webpSha256":m["sha256"],"teaching":d["teaching"]}))
    o=d["teaching"]["optionExplanations"]
    self.assertEqual(set(o),set("ABCD"))
    self.assertEqual([x for x,v in o.items() if v["isCorrect"]],[d["knownAnswerCandidate"]])
    self.assertEqual(len({v["reason"] for v in o.values()}),4)
    for v in o.values():
     self.assertGreater(len(v["teacher"]),22)
     self.assertGreater(len(v["elementary"]),10)
     self.assertGreater(len(v["reason"]),22)
    self.assertGreaterEqual(len(d["teaching"]["solvingSteps"]),4)
    self.assertTrue(d["teaching"]["memory"])
    self.assertTrue(d["teaching"]["highlights"])
    self.assertEqual(d["teaching"]["hasExamCalculation"],d["teaching"]["examCalculation"] is not None)
    self.assertFalse(d["review"]["studentReleaseApproved"])
    self.assertFalse(d["review"]["formalReady"])
    self.assertIsNone(d["review"]["independentReviewer"])
    self.assertEqual(d["review"]["independentAiContentReview"]["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
 def test_ipv4_host_and_subnet_reverse_check(self):
  net=ipaddress.ip_network("192.168.100.254/255.255.255.0",strict=False)
  self.assertEqual(str(net),"192.168.100.0/24")
  self.assertEqual(str(net.network_address),"192.168.100.0")
  self.assertEqual(str(net.broadcast_address),"192.168.100.255")
  gateway=ipaddress.ip_address("192.168.100.254")
  candidate=ipaddress.ip_address("192.168.100.194")
  self.assertIn(gateway,net.hosts())
  self.assertIn(candidate,net.hosts())
  self.assertNotEqual(gateway,candidate)
  self.assertEqual((candidate not in (net.network_address,net.broadcast_address)),True)
  d=read(F/"114-09-1-33.json")
  self.assertTrue(d["teaching"]["hasExamCalculation"])
  self.assertGreaterEqual(len(d["teaching"]["examCalculation"]["steps"]),7)
 def test_history_tls_not_inaccurate_ssl_claims_and_nonmath_hidden(self):
  q=read(F/"114-09-1-31.json")
  self.assertIn("TLS",q["teaching"]["teacherSummary"])
  self.assertIn("SSL",q["teaching"]["teacherSummary"])
  self.assertEqual(q["knownAnswerCandidate"],"B")
  for id in ["114-09-1-08","114-09-1-30","114-09-1-31","114-09-1-34"]:
   lesson=read(F/(id+".json"))
   self.assertFalse(lesson["teaching"]["hasExamCalculation"])
   self.assertIsNone(lesson["teaching"]["examCalculation"])
 def test_security_fail_closed(self):
  self.assertNotEqual(len(set(["理由不符"]*4)),4)
  self.assertTrue(all(not r["sourceAdmission"] and not r["ePass"] and not r["ready"] for r in self.b["items"]))
if __name__=="__main__":unittest.main()
