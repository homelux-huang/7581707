"""ROLE A official 115 MB23 original 2-row x 3-column source table, answer B and no-release QA."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
EVID=BASE/"review-evidence/115-00-MB-23-table-source-20261103.json"
OLD=BASE/"review-evidence/115-00-MB-23-image-transcription-correction-20261024.json"
ANSWER=BASE/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
IMAGE_SHA="2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51"
IMAGE_BLOB="f8c1fa03e8e97b7d7dae789c8ecf9cd618058bbb"
PAGE_BLOB="4c98df22dd3096c5d59178f4f2b6b3e88415bbee"
PAGE_SHA="3272c1a1df85614af3e65ae56aac3d819c9d25a7e44366d3a514de4fa8cd0555"
OLD_BLOB="170cd2238bb7c1b942a7a5389797295cdfe26953"
ANSWER_QA_BLOB="ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
OFFICIAL_BLOB="5ea4b86e929506d595f96fa162d1aae021f68440"
NOTICE_BLOB="6d21432395294d9ccbcfe1dea8be01f88597bbf3"
EXPECTED_FILES={
"sudu/data/processed/115/review-evidence/115-00-MB-23-image-transcription-correction-20261024.json",
"sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json",
"sudu/data/processed/115/review-evidence/115-00-MB-23-table-source-20261103.json",
"tests/test_role_a_115_mb23_source_table_proof.py",
".github/workflows/role-a-115-mb23-source-table.yml",
"docs/ROLE_A_115_MB23_G2_G3_TABLE_20261103.md",
}
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def table_sha(x):
 t=x["originalTextAndTable"]
 return sha(json.dumps({"question":t["correctedQuestion"],"options":t["originalOptions"],"table":t["sourceTable"]},ensure_ascii=False,separators=(",",":")).encode("utf-8"))
def validate(x):
 s=x["source"];t=x["originalTextAndTable"];a=x["publishedOfficialAnswer"];d=x["downstream"]
 if x["questionId"]!="115-00-MB-23":raise ValueError("wrong qid")
 if s["originalSingleWebpSha256"]!=IMAGE_SHA or s["originalSingleWebpGitBlob"]!=IMAGE_BLOB:raise ValueError("original changed")
 if t["sourceTable"]["columns"]!=["行程","原價","優惠"]:raise ValueError("lost 2x3 headers")
 if len(t["sourceTable"]["rows"])!=2 or any(len(row)!=3 for row in t["sourceTable"]["rows"]):raise ValueError("lost 2x3 table")
 if t["sourceTable"]["rows"]!=[
  ["行程Ⅰ","每位收費 x 元","兩人同行，其中一人減免 3000 元"],
  ["行程Ⅱ","每位收費 (x＋2000) 元","兩人同行，其中一人打八折"]]:raise ValueError("table changed")
 if t["originalOptions"]!=["32000","33000","34000","35000"]:raise ValueError("lost A-D")
 if t["correctedTextSourceSha256"]!=table_sha(x):raise ValueError("bad table text SHA")
 seed="ROLE_A_115_MB23_TABLE_G2_G3_SOURCE_EVIDENCE_V1\n"+t["correctedTextSourceSha256"]+"\n"+IMAGE_SHA+"\n"+a["officialPublishedAnswerPdfSha256PreviouslyRecorded"]
 if t["sourceRevisionSeed"]!=seed or t["sourceRevisionSha256"]!=sha(seed.encode("utf-8")):raise ValueError("source revision missing table")
 if a["value"]!="B" or a["officialNoticeForPaper"]!="NO_OBJECTION_SUBMITTED_4_00_MB" or a["canonicalFormalG3FlagNewlySet"]:raise ValueError("wrong G3 scope")
 if any(d[k] for k in ("canonicalQuestionsJsonEdited","canonical205SqliteEdited","manifestEdited","CExistingTeachingEdited","independentEContentRegistryApproved","roleDReal8x2ExactRevision","masterCanonicalSourceAdmitted","ready","approved","live")):raise ValueError("illegal admission")
 return True
class RoleAMathB23(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=load(EVID)
 def test_original_p8_question_image_exact(self):
  s=self.r["source"]
  for path,expectedsha,expectedblob in [
   (s["originalSingleWebp"],IMAGE_SHA,IMAGE_BLOB),
   (s["originalPageWebp"],PAGE_SHA,PAGE_BLOB)]:
   raw=(ROOT/path).read_bytes()
   self.assertEqual(raw[:4],b"RIFF")
   self.assertEqual(raw[8:12],b"WEBP")
   self.assertEqual(sha(raw),expectedsha)
   self.assertEqual(blob(raw),expectedblob)
  m=load(BASE/"webp-manifest.json")
  q=next(i for i in m["items"] if i["questionId"]=="115-00-MB-23")
  self.assertEqual(q["sha256"],IMAGE_SHA)
  self.assertEqual(q["crop"],[90,167,1310,603])
  self.assertEqual(q["qaStatus"],"PASS")
  self.assertFalse(self.r["downstream"]["originalWebpRecreated"])
 def test_true_original_table_and_raw_ocr_previous_proof_unchanged(self):
  r=self.r;t=r["originalTextAndTable"]
  self.assertEqual(blob(OLD.read_bytes()),OLD_BLOB)
  old=load(OLD)
  self.assertEqual(old["questionId"],"115-00-MB-23")
  self.assertEqual(old["sourceWebpSha256"],IMAGE_SHA)
  self.assertEqual(old["correctedText"]["table"]["heading"],t["sourceTable"]["columns"])
  self.assertEqual(old["correctedText"]["table"]["rows"],t["sourceTable"]["rows"])
  self.assertIn("legacyUncorrectedSource",old)
  self.assertTrue(t["historicalOriginalSourceOCRPreservedInProof"])
  self.assertTrue(validate(r))
 def test_official_published_answer_B_and_no_objection(self):
  r=self.r;a=r["publishedOfficialAnswer"]
  self.assertEqual(blob(ANSWER.read_bytes()),ANSWER_QA_BLOB)
  qa=load(ANSWER)
  q=next(z for z in qa["records"] if z["questionId"]=="115-00-MB-23")
  self.assertEqual(q["officialFinalAnswerReadDirectlyFromPublishedImage"],"B")
  self.assertEqual(q["sourceOfficialAnswerPdfSha256"],a["officialPublishedAnswerPdfSha256PreviouslyRecorded"])
  self.assertEqual(q["correctionStatus"],a["officialNoticeForPaper"])
  self.assertTrue(q["answerVerified"]) # prior historical direct answer QA only, not newly set in canonical
  self.assertFalse(q["integrationReady"])
  self.assertEqual(blob((ROOT/a["originalAnswerWebp"]).read_bytes()),OFFICIAL_BLOB)
  st=BASE/"official-confirmation-status.json"
  self.assertEqual(blob(st.read_bytes()),NOTICE_BLOB)
  self.assertEqual(load(st)["confirmations"]["00-MB"]["officialStatus"],"no_objection_submitted")
  self.assertFalse(a["officialPdfDownloadedOrRehashedInThisTask"])
 def test_math_2_trip_cost_equation_matches_B(self):
  q=self.r["mathCheck"];x=q["solutionYuan"]
  self.assertEqual(x,33000)
  self.assertEqual(2*x-3000,(x+2000)*1.8)
  self.assertEqual(2*x-3000,63000)
  self.assertEqual(q["tripIFinalYuan"],63000)
  self.assertEqual(q["tripIIFinalYuan"],63000)
  self.assertEqual(q["printedAnswerLetter"],"B")
 def test_205_row_json_db_integrity_unchanged(self):
  q=load(BASE/"questions.json")
  self.assertEqual(len(q["questions"]),205)
  con=sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True)
  try:self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
  finally:con.close()
  self.assertFalse(self.r["downstream"]["canonical205SqliteEdited"])
 def test_negative_missing_table_replaces_revision_and_no_release(self):
  for case in ("wrong_image","lost_column","lost_row","altered_discount","wrong_answer","altered_revision","promote_g3","ready","formally_reviewed"):
   with self.subTest(case=case):
    r=copy.deepcopy(self.r)
    if case=="wrong_image":r["source"]["originalSingleWebpSha256"]="0"*64
    elif case=="lost_column":r["originalTextAndTable"]["sourceTable"]["columns"].pop()
    elif case=="lost_row":r["originalTextAndTable"]["sourceTable"]["rows"].pop()
    elif case=="altered_discount":r["originalTextAndTable"]["sourceTable"]["rows"][1][2]="兩人同行，其中一人打九折"
    elif case=="wrong_answer":r["publishedOfficialAnswer"]["value"]="A"
    elif case=="altered_revision":r["originalTextAndTable"]["sourceRevisionSha256"]="0"*64
    elif case=="promote_g3":r["publishedOfficialAnswer"]["canonicalFormalG3FlagNewlySet"]=True
    elif case=="ready":r["downstream"]["ready"]=True
    elif case=="formally_reviewed":r["downstream"]["independentEContentRegistryApproved"]=True
    with self.assertRaises(ValueError):validate(r)
 def test_exact_file_lease_commit_paths(self):
  c=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True)
  self.assertEqual(set(c.stdout.splitlines()),EXPECTED_FILES)
if __name__=="__main__":unittest.main()
