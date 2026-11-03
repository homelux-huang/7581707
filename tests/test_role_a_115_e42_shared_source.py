"""ROLE A 115 English E42 exact original single + shared reading source-only G1 receipt."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
EVID=BASE/"review-evidence/115-00-E-42-original-shared-G1-20261103.json"
QSHA="a7af2b810230975781ad2831b47ac2c977e70d0e4c4d42d263f7af5f1689e7d0"
QBLOB="ee72360d9aad58fade391fa260269b0222efcc0c"
SSHA="5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b"
SBLOB="4aaac02b7ed9390b8ff7c8a4c4272e74996bd595"
SR="c94b849dc5750a92106c4b5892007010a8ce8b0b41f3cdc9e20d6e590e9353b2"
PAGESHA="6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c"
PAGEBLOB="078dfb51a6b32d652926d4495967791d938ecb37"
ANSBLOB="b8da0d2f8024eb8da2bdb2b096f97d59c0a6609d"
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def validate(r):
 if r["questionId"]!="115-00-E-42":raise ValueError("wrong qid")
 s=r["singleQuestion"];m=r["sharedMaterial"];a=r["officialAnswer"]
 if s["sha256"]!=QSHA or s["gitBlob"]!=QBLOB:raise ValueError("wrong original")
 if m["id"]!="115-00-E-SHARED-39-42" or m["sha256"]!=SSHA or m["sourceRevision"]!=SR:raise ValueError("shared mismatch")
 if m["newlyReviewedQuestionIds"]!=[42] or m["previousIndividualQAQuestionIds"]!=[39,40,41] or m["otherQuestionQaChanges"]:raise ValueError("QA inherited")
 seed="ROLE_A_115_E42_SHARED_LINK_G1_V1\n"+QSHA+"\n"+SSHA+"\n"+SR
 if r["sourceLinkRevisionSeed"]!=seed or r["sourceLinkRevisionSha256"]!=sha(seed.encode("utf-8")):raise ValueError("reversion")
 if a["publishedAnswer"]!="C" or a["namedOfficialEnglishNoticeQids"]!=["115-00-E-34"] or a["formalG3NewlySet"]:raise ValueError("G3 false")
 if any(r["downstream"][k] for k in ("originalImageModified","canonical205QuestionsEdited","sqliteEdited","manifestEdited","authorLessonEdited","officialFormalG3Admitted","independentEReviewedCurrentSource","roleDReal8x2SameDigest","masterReady","live")):raise ValueError("unlicensed admission")
 return True
class RoleAE42(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=read(EVID)
 def test_real_single_original_exact_image_and_page(self):
  self.assertTrue(validate(self.r))
  q=self.r["singleQuestion"]
  for path,ex_sha,ex_blob in ((q["path"],QSHA,QBLOB),(self.r["originalExam"]["originalPageWebp"],PAGESHA,PAGEBLOB)):
   raw=(ROOT/path).read_bytes()
   self.assertEqual(raw[:4],b"RIFF")
   self.assertEqual(raw[8:12],b"WEBP")
   self.assertEqual(sha(raw),ex_sha)
   self.assertEqual(blob(raw),ex_blob)
  self.assertEqual(q["crop"],[90,1436,1310,1623])
  self.assertEqual(q["sizePixels"],[1220,187])
  self.assertFalse(q["reCroppingPerformed"])
  row=next(x for x in read(BASE/"webp-manifest.json")["items"] if x["questionId"]=="115-00-E-42")
  self.assertEqual(row["sha256"],QSHA)
  self.assertEqual(row["qaStatus"],"PASS")
 def test_full_existing_shared_original_evidence_byte_identical(self):
  m=self.r["sharedMaterial"]
  raw=(ROOT/m["path"]).read_bytes()
  self.assertEqual(sha(raw),SSHA)
  self.assertEqual(blob(raw),SBLOB)
  prior=read(ROOT/m["sourceQaReference"])
  s=next(x for x in prior["shared"] if x["id"]==m["id"])
  self.assertEqual(s["sourceRevisionSha256"],SR)
  self.assertEqual(s["sha256"],SSHA)
  self.assertTrue(s["contentsComplete"])
  self.assertTrue(m["aiAssistantOriginalVisualReview"])
 def test_original_published_answer_C_and_notice_scope_not_approval(self):
  a=self.r["officialAnswer"]
  self.assertEqual(blob((ROOT/a["officialAnswerPage"]).read_bytes()),ANSBLOB)
  doc=read(ROOT/a["confirmationLedgerPath"])
  en=next(x for x in doc["docs"] if x["paperCode"]=="00-E")
  self.assertEqual(en["pdfSha256"],a["officialConfirmationPdfShaPreviouslyRecorded"])
  self.assertEqual([x["questionId"] for x in en["confirmed"]],["115-00-E-34"])
  self.assertFalse(a["q42ListedInCorrection"])
  self.assertFalse(a["formalG3NewlySet"])
  year=read(ROOT/"sudu/data/years/115.json")
  q=next(x for p in year["papers"] if p["paper"]=="00-E" for x in p["questions"] if x["id"]=="115-00-E-42")
  self.assertEqual(q["officialAnswerCandidate"],"C")
  self.assertEqual(q["sourceVersion"]["answerPdfSha256"],a["originalSourceAnswerPdfSha256PreviouslyRecorded"])
  self.assertFalse(q["answerVerified"])
 def test_no_mutation_sqlite_and_negative(self):
  with sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True) as c:
   self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
  for typ in ("wrong_qid","image","shared","shared_wrong","answer","notice","g3","ready","e"):
   with self.subTest(typ=typ):
    r=copy.deepcopy(self.r)
    if typ=="wrong_qid":r["questionId"]="115-00-E-41"
    elif typ=="image":r["singleQuestion"]["sha256"]="0"*64
    elif typ=="shared":r["sharedMaterial"]["sha256"]="0"*64
    elif typ=="shared_wrong":r["sharedMaterial"]["id"]="115-00-E-SHARED-29-30"
    elif typ=="answer":r["officialAnswer"]["publishedAnswer"]="B"
    elif typ=="notice":r["officialAnswer"]["namedOfficialEnglishNoticeQids"]=[]
    elif typ=="g3":r["officialAnswer"]["formalG3NewlySet"]=True
    elif typ=="ready":r["downstream"]["masterReady"]=True
    else:r["downstream"]["independentEReviewedCurrentSource"]=True
    with self.assertRaises(ValueError):validate(r)
 def test_exact_five_file_lease(self):
  changed=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True)
  self.assertEqual(set(changed.stdout.splitlines()),{
  "sudu/data/processed/115/webp-v2/00-E/115-00-E-42.webp",
  "sudu/data/processed/115/review-evidence/115-00-E-42-original-shared-G1-20261103.json",
  "tests/test_role_a_115_e42_shared_source.py",
  ".github/workflows/role-a-115-e42-shared-source.yml",
  "docs/ROLE_A_115_E42_SHARED_SOURCE_20261103.md"})
if __name__=="__main__":unittest.main()
