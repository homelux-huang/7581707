"""Only original 114 E12/E11 source assets staged; all publisher admission gates fail closed."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/114"
FROZEN=ROOT/"frozen-source/sudu/data/processed/114"
QIDS=["114-00-E-12","114-00-E-11"]
PINS={
"114-00-E-12":("C","99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60","def397fcc0693d90de40b051fdf4c7c85b4567ce","0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec",False,[90,589,1310,872],"e166524f2e3f6921c1ba55fb23862e739307b518"),
"114-00-E-11":("A","ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0","50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a","646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036",True,[90,275,1310,591],"bc3d19885e2ebc3d27092b673636bd84c89f65c6")}
EXPECTED={
"sudu/data/processed/114/webp-v1/00-E/114-00-E-12.webp",
"sudu/data/processed/114/webp-v1/00-E/114-00-E-11.webp",
"sudu/data/processed/114/review-evidence/114-00-E-12-official-20261102.json",
"sudu/data/processed/114/review-evidence/114-00-E-11-official.json",
"sudu/data/processed/114/review-evidence/114-00-E-11-source-text-20261028.json",
"sudu/data/processed/114/source-stage/114-00-E-12-staged-20261104.json",
"sudu/data/processed/114/source-stage/114-00-E-11-staged-20261104.json",
"tests/test_role_a_114_e12_e11_source_stage_20261104.py",
".github/workflows/role-a-114-e12-e11-source-stage-20261104.yml",
"docs/ROLE_A_114_E12_E11_SOURCE_STAGE_20261104.md"}
def sha(b):return hashlib.sha256(b).hexdigest()
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def validate(x,q,im):
 qid=x["questionId"]
 if qid not in PINS:raise ValueError("wrong question")
 ans,pixel,blob,rev,oldflag,crop,receipt=PINS[qid]
 s=x["source"];a=x["official"];f=x["frozenBank"];d=x["downstream"]
 if x["status"]!="SOURCE_ORIGINAL_WEBP_STAGED__SHARED_CANONICAL_DB_C27_LEASE_HOLD_NO_RELEASE":raise ValueError("falsely staged")
 if s["question"]!=q["question"] or s["options"]!=q["options"] or len(s["options"])!=4:raise ValueError("question options changed")
 if s["revision"]!=rev or s["originalSingleSha256"]!=pixel or s["originalSingleGitBlob"]!=blob:raise ValueError("stale source hash")
 if s["crop"]!=crop or im["sha256"]!=pixel or s["originalImageQAStatus"]!="PASS" or s["originalPixelsRecropped"]:raise ValueError("false G1")
 if a["publishedAnswer"]!=ans or a["originalRoleAReceiptGitBlob"]!=receipt or a["noticeQuestionIds"]!=["114-00-E-26"] or a["thisQuestionChangedByNotice"]:raise ValueError("official answer/scope")
 if a["originalAnswerVerified"]!=oldflag or a["formalNewG3Approval"]:raise ValueError("illegal G3 approval")
 if f["originalQuestionVerified"] is not False or f["originalAnswerVerified"]!=oldflag:raise ValueError("retroactive bank flags")
 if f["sharedFilesImported"] or f["sharedFilesModified"] or f["count"]!=205:raise ValueError("shared lease bypass")
 if f["canonicalJsonSha1"]!="1535754345a08d25636e00b4ba3270a1f764bf66" or f["sqliteSha1"]!="27314572b3d18fd0bd20003297bccadbc6c59737":raise ValueError("stale bank")
 if any(d[z] for z in ("newReady","newLive","approved")):raise ValueError("illegal release")
 return True
class SourceStage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.docs={qid:load(DATA/"source-stage"/(qid+"-staged-20261104.json")) for qid in QIDS}
  cls.bank=load(FROZEN/"questions.json")
  cls.man=load(FROZEN/"webp-manifest.json")
  cls.rows={q["questionId"]:q for q in cls.bank["questions"]}
  cls.images={i["questionId"]:i for i in cls.man["items"]}
 def test_source_staging_uses_two_only_and_does_not_edit_shared_bank(self):
  self.assertEqual(len(self.rows),205)
  self.assertEqual(len(self.images),205)
  for path in ("questions.json","question-bank.sqlite3","webp-manifest.json"):
   self.assertFalse((DATA/path).exists(),path+" belongs to C27 lease")
  for qid in QIDS:self.assertTrue(validate(self.docs[qid],self.rows[qid],self.images[qid]))
 def test_original_p3_and_answer_page_unchanged_on_main_ancestor(self):
  for path,expected,blob in [
   ("sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp","51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb","5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"),
   ("sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp","a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863","5f2920313607af4e756095cd3d6098c8a3ab7440")]:
   data=(ROOT/path).read_bytes()
   self.assertEqual(data[:4],b"RIFF");self.assertEqual(data[8:12],b"WEBP")
   self.assertEqual(sha(data),expected);self.assertEqual(gitsha(data),blob)
 def test_exact_two_individual_original_webp_immutable_and_not_recropped(self):
  for qid in QIDS:
   a=self.docs[qid]["source"];data=(ROOT/a["originalSingleWebp"]).read_bytes()
   self.assertEqual(data[:4],b"RIFF");self.assertEqual(data[8:12],b"WEBP")
   self.assertEqual(sha(data),PINS[qid][1]);self.assertEqual(gitsha(data),PINS[qid][2])
   self.assertEqual(a["originalSingleSha256"],PINS[qid][1])
 def test_frozen_205_canonical_and_sqlite_exact_row_payload_sha(self):
  for path,blob in [("questions.json","1535754345a08d25636e00b4ba3270a1f764bf66"),("question-bank.sqlite3","27314572b3d18fd0bd20003297bccadbc6c59737"),("webp-manifest.json","249a41d5a64558ccaa3084b21f915922a55c6a1b")]:
   self.assertEqual(gitsha((FROZEN/path).read_bytes()),blob)
  cx=sqlite3.connect("file:"+(FROZEN/"question-bank.sqlite3").as_posix()+"?mode=ro",uri=True)
  try:
   self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   for qid in QIDS:
    payload,digest=cx.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
    self.assertEqual(load_payload(payload),self.rows[qid]);self.assertEqual(sha(payload.encode("utf-8")),digest)
  finally:cx.close()
 def test_archived_official_notice_only_e26_and_original_qa_sources(self):
  g1=FROZEN/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
  notice=FROZEN/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
  self.assertEqual(gitsha(g1.read_bytes()),"c1154562fa30cb4b2720a6000a970cf09ef460ff")
  self.assertEqual(gitsha(notice.read_bytes()),"6b9a919f224bec8dc3659052a404b4173b6ef366")
  g={i["questionId"]:i for i in load(g1)["items"]}
  e=next(x for x in load(notice)["docs"] if x["paperCode"]=="00-E")
  self.assertEqual(e["pdfSha256"],"79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53cbc")
  self.assertEqual([i["questionId"] for i in e["confirmed"]],["114-00-E-26"])
  for qid in QIDS:
   self.assertEqual(g[qid]["result"],"PASS");self.assertEqual(g[qid]["reviewedWebpSha256"],PINS[qid][1])
   self.assertFalse(g[qid]["answerVerified"]);self.assertFalse(g[qid]["questionVerified"])
   path=ROOT/self.docs[qid]["official"]["originalRoleAReceiptPath"]
   self.assertEqual(gitsha(path.read_bytes()),PINS[qid][6])
 def test_g2_source_is_existing_immutable_a_receipt_not_role_e(self):
  path=ROOT/"sudu/data/processed/114/review-evidence/114-00-E-11-source-text-20261028.json"
  self.assertEqual(gitsha(path.read_bytes()),"bd90a3c3814353379eacf89759fcd3153099fa53")
  prior=load(path)
  self.assertEqual(prior["directStructuredSourceTextVisualObservation"]["canonicalQuestionExact"],self.docs["114-00-E-11"]["source"]["question"])
  self.assertEqual(prior["currentSourceAndAnswerBindings"]["publisherQuestionRevisionSha256"],PINS["114-00-E-11"][3])
 def test_negative_changes_fail_gates(self):
  for qid in QIDS:
   for case in ["answer","sha","imgblob","notice","qID","option","g3","live"]:
    with self.subTest(qid=qid,case=case):
     x=copy.deepcopy(self.docs[qid])
     if case=="answer":x["official"]["publishedAnswer"]="D" if PINS[qid][0]!="D" else "B"
     elif case=="sha":x["source"]["originalSingleSha256"]="0"*64
     elif case=="imgblob":x["source"]["originalSingleGitBlob"]="0"*40
     elif case=="notice":x["official"]["noticeQuestionIds"].append(qid)
     elif case=="qID":x["questionId"]="115-00-E-11"
     elif case=="option":x["source"]["options"].pop()
     elif case=="g3":x["official"]["formalNewG3Approval"]=True
     else:x["downstream"]["newLive"]=True
     with self.assertRaises(ValueError):validate(x,self.rows[qid],self.images[qid])
 def test_exact_main_based_claimed_file_scope(self):
  result=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,check=True,text=True,capture_output=True)
  self.assertEqual(set(result.stdout.splitlines()),EXPECTED)
def load_payload(payload):return json.loads(payload)
