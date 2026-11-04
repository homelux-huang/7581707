"""Role A 115 MB23 original 2 rows x 3 cols table source-staged WITHOUT releasing anyone."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/115"
FROZEN=ROOT/"frozen-source/sudu/data/processed/115"
QID="115-00-MB-23"
RECEIPT=DATA/"source-stage/115-00-MB-23-staged-20261104.json"
ORIG_TABLE=DATA/"review-evidence/115-00-MB-23-table-source-20261103.json"
ORIG_G2=DATA/"review-evidence/115-00-MB-23-image-transcription-correction-20261024.json"
OFFICIAL_QA=DATA/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
REV="9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4"
PIX="2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51"
GIT="f8c1fa03e8e97b7d7dae789c8ecf9cd618058bbb"
TBL=[
["行程Ⅰ","每位收費 x 元","兩人同行，其中一人減免 3000 元"],
["行程Ⅱ","每位收費 (x＋2000) 元","兩人同行，其中一人打八折"]]
ALLOWED={
"sudu/data/processed/115/webp-v2/00-MB/115-00-MB-23.webp",
"sudu/data/processed/115/review-evidence/115-00-MB-23-image-transcription-correction-20261024.json",
"sudu/data/processed/115/review-evidence/115-00-MB-23-table-source-20261103.json",
"sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json",
"sudu/data/processed/115/source-stage/115-00-MB-23-staged-20261104.json",
"tests/test_role_a_115_mb23_original_table_stage_20261104.py",
".github/workflows/role-a-115-mb23-original-table-stage-20261104.yml",
"docs/ROLE_A_115_MB23_ORIGINAL_TABLE_STAGE_20261104.md"}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def webp(path,hexsha,git):
 raw=path.read_bytes()
 if raw[:4]!=b"RIFF" or raw[8:12]!=b"WEBP" or sha(raw)!=hexsha or blob(raw)!=git:raise ValueError("source image not exact original")
 return True
def gate(r,src,g2,qa,man):
 if r["questionId"]!=QID or r["status"]!="ROLE_A_OFFICIAL_ORIGINAL_2X3_TABLE_SOURCE_STAGED__CANONICAL_205_DB_NOT_IMPORTED_NO_RELEASE":raise ValueError("not exact QID source scope")
 s=r["source"];o=r["official"];f=r["frozenCanonical"];d=r["downstream"]
 if s["singleSha256"]!=PIX or s["singleGitBlob"]!=GIT or s["crop"]!=[90,167,1310,603]:raise ValueError("changed original pixel")
 if s["sourceRevision"]!=REV or s["sourceRevision"]!=src["originalTextAndTable"]["sourceRevisionSha256"]:raise ValueError("stale table source revision")
 table=s["table"]
 if table["columns"]!=["行程","原價","優惠"] or table["rows"]!=TBL or len(table["rows"])!=2 or any(len(row)!=3 for row in table["rows"]):raise ValueError("original 2x3 table corrupted")
 if s["tableDimensions"]!={"headerColumns":3,"dataRows":2,"dataCells":6}:raise ValueError("source table dimension")
 if s["tableTextSha256"]!=src["originalTextAndTable"]["correctedTextSourceSha256"]:raise ValueError("source table text SHA")
 if s["question"]!=g2["correctedText"]["question"] or s["options"]!=["32000","33000","34000","35000"] or s["options"]!=g2["correctedText"]["options"]:raise ValueError("wrong stem or four options")
 if g2["correctedText"]["table"]["rows"]!=TBL or s["rawG2EvidenceGitBlob"]!="170cd2238bb7c1b942a7a5389797295cdfe26953":raise ValueError("old OCR table evidence altered")
 if man["sha256"]!=PIX or man["qaStatus"]!="PASS" or man["crop"]!=[90,167,1310,603]:raise ValueError("old G1 manifest mismatch")
 if o["letter"]!="B" or o["valueYuan"]!=33000 or qa["officialFinalAnswerReadDirectlyFromPublishedImage"]!="B":raise ValueError("published answer changed")
 if o["correctionStatus"]!="115_00_MB_NO_OBJECTION_SUBMITTED" or qa["correctionStatus"]!="NO_OBJECTION_SUBMITTED_4_00_MB":raise ValueError("notice scope")
 if 2*33000-3000!=63000 or 1.8*(33000+2000)!=63000:raise ValueError("math check")
 if o["formalQuestionG3FlagNewlySet"]:raise ValueError("unauthorized formal G3 flag")
 if any(f[x] for x in ("canonicalQuestionBankCopiedIntoMain","manifestCopiedIntoMain","sqliteCopiedIntoMain")):raise ValueError("bank/sql lease breach")
 if f["expectedCount"]!=205 or f["historical81SqliteDenormIssuesRemainUnresolved"] is not True:raise ValueError("source QA flags forged")
 if d["approved"] or d["ready"] or d["live"]:raise ValueError("student release forged")
 return True
class ActualOriginalMB23(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=load(RECEIPT);cls.src=load(ORIG_TABLE);cls.g2=load(ORIG_G2)
  cls.qa=load(OFFICIAL_QA)
  cls.q=next(x for x in cls.qa["records"] if x["questionId"]==QID)
  cls.bank=load(FROZEN/"questions.json")
  cls.manifest=load(FROZEN/"webp-manifest.json")
  cls.m=next(x for x in cls.manifest["items"] if x["questionId"]==QID)
 def test_original_source_image_with_exact_p8_and_answer_png(self):
  s=self.r["source"];o=self.r["official"]
  webp(ROOT/s["originalPage"],"3272c1a1df85614af3e65ae56aac3d819c9d25a7e44366d3a514de4fa8cd0555","4c98df22dd3096c5d59178f4f2b6b3e88415bbee")
  webp(ROOT/s["single"],PIX,GIT)
  webp(ROOT/o["publishedOriginalAnswerWebp"],"1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d","5ea4b86e929506d595f96fa162d1aae021f68440")
  self.assertFalse(s["imageRecropped"])
 def test_evidence_original_g2_and_actual_table_dimensions(self):
  self.assertEqual(blob(ORIG_TABLE.read_bytes()),"0f63d6a5f91015dd2b146731c48dce08668c1fa2")
  self.assertEqual(blob(ORIG_G2.read_bytes()),"170cd2238bb7c1b942a7a5389797295cdfe26953")
  self.assertEqual(blob(OFFICIAL_QA.read_bytes()),"ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e")
  self.assertTrue(gate(self.r,self.src,self.g2,self.q,self.m))
  self.assertEqual(self.src["originalTextAndTable"]["correctedTextSourceSha256"],"3ae20c9b53eb5ba38ffa354cbda868806bb7716700548bbe88618e0104a89088")
 def test_original_205_sqlite_payload_integrity_and_no_dependent_release(self):
  self.assertEqual(blob((FROZEN/"questions.json").read_bytes()),"216bc43d57501bc1c3e5842b48413a8967456cda")
  self.assertEqual(blob((FROZEN/"webp-manifest.json").read_bytes()),"2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b")
  self.assertEqual(blob((FROZEN/"question-bank.sqlite3").read_bytes()),"9f0154e79fe90e92fa46b4d9bcbe4009cbfb3788")
  self.assertEqual(len(self.bank["questions"]),205)
  with sqlite3.connect("file:"+(FROZEN/"question-bank.sqlite3").as_posix()+"?mode=ro",uri=True) as db:
   self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   payload,hashval=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
  self.assertEqual(json.loads(payload),next(q for q in self.bank["questions"] if q["questionId"]==QID))
  self.assertEqual(sha(payload.encode("utf-8")),hashval)
  self.assertFalse(self.r["downstream"]["approved"])
  self.assertFalse(self.r["downstream"]["ready"])
 def test_official_published_B_and_no_objection_not_automatically_final_gate(self):
  self.assertEqual(self.q["officialFinalAnswerReadDirectlyFromPublishedImage"],"B")
  self.assertTrue(self.q["answerVerified"])
  self.assertFalse(self.q["questionVerified"])
  self.assertFalse(self.q["integrationReady"])
  self.assertEqual(self.r["official"]["equalTripCostYuan"],63000)
  self.assertEqual(self.src["mathCheck"]["solutionYuan"],33000)
 def test_negative_table_and_source_mutations_fail(self):
  for mutation in ("loss_row","loss_col","wrong_offer","oldrevision","alterhash","change_answer","wrong_scope","promote_g3","approve"):
   with self.subTest(mutation=mutation):
    x=copy.deepcopy(self.r)
    if mutation=="loss_row":x["source"]["table"]["rows"].pop()
    elif mutation=="loss_col":x["source"]["table"]["rows"][0].pop()
    elif mutation=="wrong_offer":x["source"]["table"]["rows"][1][2]="兩人都打八折"
    elif mutation=="oldrevision":x["source"]["sourceRevision"]="c3df98d4c15185803c1b17294c514a19496395d0087364825d2bdce144a10b92"
    elif mutation=="alterhash":x["source"]["singleSha256"]="0"*64
    elif mutation=="change_answer":x["official"]["letter"]="A"
    elif mutation=="wrong_scope":x["questionId"]="115-00-MB-22"
    elif mutation=="promote_g3":x["official"]["formalQuestionG3FlagNewlySet"]=True
    else:x["downstream"]["ready"]=True
    with self.assertRaises(ValueError):gate(x,self.src,self.g2,self.q,self.m)
 def test_8_path_exclusive_role_a_source_only_protected_main_diff(self):
  r=subprocess.run(["git","diff","--name-only","ba2f3f0757dbf81eaaf125bd610b0f38de52fea9","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True)
  self.assertEqual(set(r.stdout.splitlines()),ALLOWED)
