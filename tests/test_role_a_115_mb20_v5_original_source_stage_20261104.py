"""ROLE A exact original Math B20 v5 source WebP and official A, fail closed on unreviewed historical v2 defect."""
import copy,hashlib,json,math,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/115"
FROZEN=ROOT/"frozen-source/sudu/data/processed/115"
RECEIPT=DATA/"source-stage/115-00-MB-20-v5-staged-20261104.json"
G2=DATA/"review-evidence/115-00-MB-20-image-transcription-correction-20261024.json"
ANSWERQA=DATA/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
QID="115-00-MB-20"
SOURCE_IMAGE="f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf"
SOURCE_BLOB="bd77281f8ee755074cf3b7ebcada5c06f3720c12"
BAD_OLD_V2_BLOB="fb055f43e0d186343015a6f6542cdc302e9ef5d5"
EXPECTED={
"sudu/data/processed/115/webp-v5/00-MB/115-00-MB-20.webp",
"sudu/data/processed/115/review-evidence/115-00-MB-20-image-transcription-correction-20261024.json",
"sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json",
"sudu/data/processed/115/source-stage/115-00-MB-20-v5-staged-20261104.json",
"tests/test_role_a_115_mb20_v5_original_source_stage_20261104.py",
".github/workflows/role-a-115-mb20-v5-original-source-stage-20261104.yml",
"docs/ROLE_A_115_MB20_V5_ORIGINAL_STAGE_20261104.md"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(data):return hashlib.sha256(data).hexdigest()
def blob(data):return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def validate_image(p,digest,git):
 raw=p.read_bytes()
 if raw[:4]!=b"RIFF" or raw[8:12]!=b"WEBP" or sha(raw)!=digest or blob(raw)!=git:raise ValueError("original source image altered")
 return True
def gate(r,g2,man,answer):
 s=r["originalSource"];q=r["g2Source"];a=r["official"];f=r["frozenCanonical"];d=r["downstream"]
 if r["questionId"]!=QID or r["status"]!="ROLE_A_ORIGINAL_V5_CORRECTED_FIGURE_SOURCE_STAGED__INDEPENDENT_G1_CANONICAL_ADMISSION_PENDING_NO_RELEASE":raise ValueError("scope")
 if s["originalCorrectedSingleWebpSha256"]!=SOURCE_IMAGE or s["originalCorrectedSingleWebpGitBlob"]!=SOURCE_BLOB:raise ValueError("v5 missing")
 if s["oldDefectiveV2GitBlob"]!=BAD_OLD_V2_BLOB or s["historicalRepairStatus"]!="generated_pending_independent_visual_recheck":raise ValueError("v2 original defect suppressed")
 if s["oldDefect"]!="previous_candidate_missing_figure_IV_lower_edge_and_caption":raise ValueError("original v2 boundary issue suppressed")
 if s["originalCrop"]!=[90,469,1310,902] or s["originalPixelSize"]!=[1220,433]:raise ValueError("actual crop mismatch")
 if s["formalIndependentVisualReviewRecheckRecorded"] or s["formalCanonicalImageG1FlagNewlySet"] or s["imageRecroppedOrRedrawnThisTask"]:raise ValueError("fake formal G1")
 if man["sha256"]!=SOURCE_IMAGE or man["output"]!=s["originalCorrectedSingleWebp"] or man["visualDefectHistory"]["repairStatus"]!=s["historicalRepairStatus"]:raise ValueError("frozen manifest mismatch")
 if q["historicalRoleAProofGitBlob"]!="c5278848e46d07dba45734413bc0b79a9b9afcb4" or not q["oldRawOCRPreservedInProof"]:raise ValueError("lost original OCR")
 if q["question"]!=g2["correctedText"]["question"] or q["options"]!=["50(√3＋1)","50(√3－1)","20(√3＋1)","20(√3－1)"]:raise ValueError("original four choices wrong")
 if q["figureDescription"]!=g2["correctedText"]["figureDescription"] or q["newAFormalCanonicalSourceRevisionSet"]:raise ValueError("forged G2")
 if a["printedOfficialAnswer"]!="A" or answer["officialFinalAnswerReadDirectlyFromPublishedImage"]!="A":raise ValueError("official A incorrect")
 if a["noticeStatus"]!="no_objection_submitted" or not answer["officialCorrectionChecked"] or a["canonicalFinalAnswerVerifiedFlagNewlySet"]:raise ValueError("official notice/admission")
 if not math.isclose(a["approxMetres"],50*(math.sqrt(3)+1),abs_tol=1e-8):raise ValueError("wrong source calculation")
 if any(f[x] for x in ("canonicalJsonTouched","canonicalSqliteTouched","canonicalManifestTouched")):raise ValueError("bank lease")
 if any(d[x] for x in ("approved","ready","live")):raise ValueError("illegal release")
 return True
class OriginalMB20V5(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=load(RECEIPT);cls.g2=load(G2);cls.qa=load(ANSWERQA)
  cls.answer=next(x for x in cls.qa["records"] if x["questionId"]==QID)
  cls.bank=load(FROZEN/"questions.json")
  cls.man=load(FROZEN/"webp-manifest.json")
  cls.m=next(x for x in cls.man["items"] if x["questionId"]==QID)
 def test_actual_original_v5_pixels_not_old_defective_v2(self):
  s=self.r["originalSource"]
  validate_image(ROOT/s["officialOriginalPageWebp"],"7a1732ce33ee6b9f1cc4fcc6f705b2aa1f29a117e0562a62b50428d94845464d","c8e3e806d812a01d417abe83dac7f46adcf84ff7")
  validate_image(ROOT/s["originalCorrectedSingleWebp"],SOURCE_IMAGE,SOURCE_BLOB)
  validate_image(ROOT/self.r["official"]["oldPublishedAnswerFullImage"],"1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d","5ea4b86e929506d595f96fa162d1aae021f68440")
  old=FROZEN/"webp-v2/00-MB/115-00-MB-20.webp"
  self.assertEqual(blob(old.read_bytes()),BAD_OLD_V2_BLOB)
  self.assertNotEqual(blob(old.read_bytes()),blob((ROOT/s["originalCorrectedSingleWebp"]).read_bytes()))
  self.assertFalse(s["formalIndependentVisualReviewRecheckRecorded"])
 def test_real_source_G2_evidence_legacy_original_OCR_and_corrected_text(self):
  self.assertEqual(blob(G2.read_bytes()),"c5278848e46d07dba45734413bc0b79a9b9afcb4")
  self.assertEqual(blob(ANSWERQA.read_bytes()),"ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e")
  self.assertEqual(self.g2["sourceWebpSha256"],SOURCE_IMAGE)
  self.assertEqual(len(self.g2["legacyUncorrectedSource"]["options"]),4)
  self.assertEqual(self.g2["correctedText"]["options"],["50(√3＋1)","50(√3－1)","20(√3＋1)","20(√3－1)"])
  self.assertEqual(self.g2["knownOfficialAnswer"],"A")
  self.assertTrue(self.g2["correctedText"]["figureRequired"])
  self.assertTrue(gate(self.r,self.g2,self.m,self.answer))
 def test_205_canonical_sqlite_readonly_preserve_unadmitted_figure_revision(self):
  for name,expected in [("questions.json","216bc43d57501bc1c3e5842b48413a8967456cda"),("webp-manifest.json","2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b"),("question-bank.sqlite3","9f0154e79fe90e92fa46b4d9bcbe4009cbfb3788")]:
   self.assertEqual(blob((FROZEN/name).read_bytes()),expected)
  self.assertEqual(len(self.bank["questions"]),205)
  self.assertEqual(len(self.man["items"]),205)
  with sqlite3.connect("file:"+(FROZEN/"question-bank.sqlite3").as_posix()+"?mode=ro",uri=True) as db:
   self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   data,h=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
  self.assertEqual(sha(data.encode("utf-8")),h)
  self.assertEqual(json.loads(data),next(x for x in self.bank["questions"] if x["questionId"]==QID))
  self.assertFalse(self.r["frozenCanonical"]["canonicalJsonTouched"])
 def test_math_accuracy_and_reverse_check_not_independent_E(self):
  s=self.r["official"];ac=100*math.sin(math.radians(75))/math.sin(math.radians(45))
  self.assertAlmostEqual(ac,s["approxMetres"],places=8)
  self.assertAlmostEqual(ac*math.sin(math.radians(45))/math.sin(math.radians(75)),100,places=8)
  self.assertEqual(s["printedOfficialAnswer"],"A")
  self.assertTrue(self.answer["answerVerified"])
  self.assertFalse(self.answer["questionVerified"])
  self.assertFalse(self.r["downstream"]["ready"])
 def test_negative_v2_fallback_source_flag_official_and_release(self):
  for case in ("old_image","wrong_source_sha","erase_defect","fake_formalG1","wrong_answer","bad_question","bad_options","false_revision","approve"):
   with self.subTest(case=case):
    r=copy.deepcopy(self.r)
    if case=="old_image":r["originalSource"]["originalCorrectedSingleWebpGitBlob"]=BAD_OLD_V2_BLOB
    elif case=="wrong_source_sha":r["originalSource"]["originalCorrectedSingleWebpSha256"]="0"*64
    elif case=="erase_defect":r["originalSource"]["historicalRepairStatus"]="PASS"
    elif case=="fake_formalG1":r["originalSource"]["formalCanonicalImageG1FlagNewlySet"]=True
    elif case=="wrong_answer":r["official"]["printedOfficialAnswer"]="B"
    elif case=="bad_question":r["g2Source"]["question"]+=" fake"
    elif case=="bad_options":r["g2Source"]["options"].pop()
    elif case=="false_revision":r["g2Source"]["newAFormalCanonicalSourceRevisionSet"]=True
    else:r["downstream"]["approved"]=True
    with self.assertRaises(ValueError):gate(r,self.g2,self.m,self.answer)
 def test_7_source_only_paths_and_protected_main_diff(self):
  diff=subprocess.run(["git","diff","--name-only","ba2f3f0757dbf81eaaf125bd610b0f38de52fea9","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True)
  self.assertEqual(set(diff.stdout.splitlines()),EXPECTED)
