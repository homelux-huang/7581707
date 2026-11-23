"""Role A 115 Math B21/B22 immutable original source stage, no canonical or release edits."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/115"
FROZEN=ROOT/"frozen-source/sudu/data/processed/115"
QIDS=["115-00-MB-21","115-00-MB-22"]
ORIGP7="sudu/data/original/115/00-MB/p007-e82e34d9cd-v2-w1400-q66.webp"
ANSP1="sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"
PINS={
"115-00-MB-21":{"answer":"A","image":"b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693","blob":"75d9bcf6d0d921a6f7a40fd6383d0cd4680398bf","receipt":"3e37500240e1c26fedc2ae827eac95ddf9ebe80b","crop":[90,907,1310,1321],"opts":["5","4.75","4.50","4.25"]},
"115-00-MB-22":{"answer":"B","image":"3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55","blob":"491e02cabe4110d62b510075914e083b51e58ebf","receipt":"5ad5b4fef7570b71eb534a510baec9da27ca47ce","crop":[90,1331,1310,1715],"opts":["32","31","16","5"]}}
ALLOWED={
"sudu/data/processed/115/webp-v2/00-MB/115-00-MB-21.webp",
"sudu/data/processed/115/webp-v2/00-MB/115-00-MB-22.webp",
"sudu/data/processed/115/review-evidence/115-00-MB-21-image-transcription-correction-20261024.json",
"sudu/data/processed/115/review-evidence/115-00-MB-22-image-transcription-correction-20261024.json",
"sudu/data/processed/115/source-stage/115-00-MB-21-staged-20261104.json",
"sudu/data/processed/115/source-stage/115-00-MB-22-staged-20261104.json",
"tests/test_role_a_115_mb21_mb22_source_stage_20261104.py",
".github/workflows/role-a-115-mb21-mb22-source-stage-20261104.yml",
"docs/ROLE_A_115_MB21_MB22_SOURCE_STAGE_20261104.md"}
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def original(raw,digest,git):
 if len(raw)<100 or raw[:4]!=b"RIFF" or raw[8:12]!=b"WEBP":raise ValueError("not an original WebP")
 if sha(raw)!=digest or blob(raw)!=git:raise ValueError("original image hash or Git blob changed")
 return True
def gate(r,q,man,old,official,notice):
 id=r["questionId"]
 if id not in PINS:raise ValueError("wrong scope")
 pin=PINS[id];s=r["originalSource"];ans=r["officialAnswer"];f=r["frozenCanonicalReadOnly"];d=r["downstream"]
 if r["stageStatus"]!="ORIGINAL_SINGLE_WEBP_AND_EXISTING_G2_OFFICIAL_G3_SOURCE_PROOF_STAGED__CANONICAL_SQLITE_UNMODIFIED_NO_RELEASE":raise ValueError("wrong status")
 if s["singleSha256"]!=pin["image"] or s["singleGitBlob"]!=pin["blob"] or s["crop"]!=pin["crop"]:raise ValueError("mismatched original")
 if s["originalCleanQuestion"]!=old["correctedText"]["question"] or s["originalCleanOptions"]!=pin["opts"] or old["correctedText"]["options"]!=pin["opts"]:raise ValueError("OCR source G2 contamination")
 if len(s["originalCleanOptions"])!=4 or not s["originalFigureDescription"] or not old["correctedText"]["figureRequired"]:raise ValueError("source figure incomplete")
 if s["previousG2EvidenceGitBlob"]!=pin["receipt"] or not s["originalRawOcrPreservedInUnchangedEvidence"]:raise ValueError("old OCR not retained")
 if s["singleSha256"]!=man["sha256"] or man["qaStatus"]!="PASS" or man["crop"]!=pin["crop"]:raise ValueError("G1 candidate mismatch")
 if ans["officialPublishedLetter"]!=pin["answer"] or official["officialFinalAnswer"]!=pin["answer"]:raise ValueError("wrong official answer")
 if not official["answerVerified"] or official["officialCorrectionStatus"]!="OFFICIAL_00_MB_NO_OBJECTION_SUBMITTED":raise ValueError("unproven official answer")
 if notice["confirmations"]["00-MB"]["officialStatus"]!="no_objection_submitted" or not ans["officialNoObjectionForPaper"]:raise ValueError("no-objection scope forged")
 if ans["formalNewAnswerVerifiedFlagSet"]:raise ValueError("illegally promoted canonical G3 flag")
 if f["canonicalBankModified"] or f["manifestModified"] or f["sqliteModified"] or not f["canonicalBankNotImportedIntoMain"]:raise ValueError("shared 205 bank unlawfully modified")
 if f["questionsJsonGitBlob"]!="216bc43d57501bc1c3e5842b48413a8967456cda" or f["sqliteGitBlob"]!="9f0154e79fe90e92fa46b4d9bcbe4009cbfb3788":raise ValueError("stale frozen source")
 if d["ready"] or d["approved"] or d["live"]:raise ValueError("unauthorized admission")
 return True

class OriginalMathSourceStage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r={q:load(DATA/"source-stage"/(q+"-staged-20261104.json")) for q in QIDS}
  cls.bank=load(FROZEN/"questions.json")
  cls.manifest=load(FROZEN/"webp-manifest.json")
  cls.bq={q["questionId"]:q for q in cls.bank["questions"]}
  cls.mq={q["questionId"]:q for q in cls.manifest["items"]}
  cls.old={q:load(DATA/"review-evidence"/(q+"-image-transcription-correction-20261024.json")) for q in QIDS}
  cls.off=load(FROZEN/"official-answer-evidence.json")
  cls.official={q["questionId"]:q for q in cls.off["items"]}
  cls.notice=load(FROZEN/"official-confirmation-status.json")
 def test_two_exact_source_rows_without_shared_bank_or_publisher_mutation(self):
  self.assertEqual(len(self.bank["questions"]),205)
  self.assertEqual(len(self.manifest["items"]),205)
  self.assertTrue(set(QIDS).issubset(set(self.bq)))
  for qid in QIDS:self.assertTrue(gate(self.r[qid],self.bq[qid],self.mq[qid],self.old[qid],self.official[qid],self.notice))
 def test_all_original_pixels_hash_and_git_blob(self):
  original((ROOT/ORIGP7).read_bytes(),"7a1732ce33ee6b9f1cc4fcc6f705b2aa1f29a117e0562a62b50428d94845464d","c8e3e806d812a01d417abe83dac7f46adcf84ff7")
  original((ROOT/ANSP1).read_bytes(),"1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d","5ea4b86e929506d595f96fa162d1aae021f68440")
  for qid in QIDS:
   s=self.r[qid]["originalSource"]
   original((ROOT/s["singleWebp"]).read_bytes(),PINS[qid]["image"],PINS[qid]["blob"])
   self.assertTrue(s["originalRawOcrPreservedInUnchangedEvidence"])
   self.assertFalse(s["sourcePixelRecreated"])
 def test_g2_raw_ocr_and_original_four_option_figure_still_present(self):
  for qid in QIDS:
   old=self.old[qid];s=self.r[qid]["originalSource"]
   self.assertEqual(blob((ROOT/s["previousG2Evidence"]).read_bytes()),PINS[qid]["receipt"])
   self.assertEqual(old["questionId"],qid)
   self.assertEqual(len(old["legacyUncorrectedSource"]["options"]),4)
   self.assertEqual(old["knownOfficialAnswer"],PINS[qid]["answer"])
   self.assertEqual(old["correctedText"]["options"],PINS[qid]["opts"])
   self.assertEqual(old["sourceWebpSha256"],PINS[qid]["image"])
   self.assertTrue(old["status"]["aiVisualTranscriptionChecked"])
   self.assertFalse(old["status"]["studentReleaseApproved"])
   self.assertFalse(old["status"]["deploy"])
  self.assertIn("8 公里",self.old["115-00-MB-21"]["correctedText"]["question"])
  self.assertIn("五張卡片",self.old["115-00-MB-22"]["correctedText"]["question"])
  self.assertIn("第8 頁",self.old["115-00-MB-22"]["legacyUncorrectedSource"]["options"][3])
  self.assertNotIn("第8 頁",self.old["115-00-MB-22"]["correctedText"]["options"][3])
 def test_original_official_published_A_B_and_no_objections_115_only(self):
  self.assertEqual(blob((FROZEN/"official-answer-evidence.json").read_bytes()),"ed02ef9cde66720af2142330d79afb5349d0f999")
  self.assertEqual(blob((FROZEN/"official-confirmation-status.json").read_bytes()),"6d21432395294d9ccbcfe1dea8be01f88597bbf3")
  self.assertEqual(self.notice["year"],115)
  self.assertEqual(self.notice["confirmations"]["00-MB"]["officialStatus"],"no_objection_submitted")
  for qid in QIDS:
   o=self.official[qid]
   self.assertEqual(o["officialFinalAnswer"],PINS[qid]["answer"])
   self.assertEqual(o["officialAnswerImageSha256"],"1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d")
   self.assertTrue(o["answerVerified"])
   self.assertFalse(self.r[qid]["officialAnswer"]["formalNewAnswerVerifiedFlagSet"])
 def test_205_row_canonical_sqlite_sha_readonly_legacy_differences_not_hidden(self):
  for name,pin in [("questions.json","216bc43d57501bc1c3e5842b48413a8967456cda"),("webp-manifest.json","2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b"),("question-bank.sqlite3","9f0154e79fe90e92fa46b4d9bcbe4009cbfb3788")]:
   self.assertEqual(blob((FROZEN/name).read_bytes()),pin)
  with sqlite3.connect("file:"+(FROZEN/"question-bank.sqlite3").as_posix()+"?mode=ro",uri=True) as con:
   self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(con.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   for qid in QIDS:
    payload,h=con.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
    self.assertEqual(json.loads(payload),self.bq[qid])
    self.assertEqual(sha(payload.encode("utf-8")),h)
    self.assertTrue(self.r[qid]["frozenCanonicalReadOnly"]["historical115SqliteDenormalizedDifferencesStillRequirePerRowReview"])
 def test_math_answer_reasoning_verification_not_an_E_review(self):
  roots=[x for x in (3,5) if (x*x-8*x+15)==0 and x>4]
  self.assertEqual(roots,[5])
  self.assertEqual(self.r["115-00-MB-21"]["officialAnswer"]["officialPublishedLetter"],"A")
  self.assertEqual(2**5-1,31)
  self.assertEqual(self.r["115-00-MB-22"]["officialAnswer"]["officialPublishedLetter"],"B")
  self.assertEqual(self.r["115-00-MB-21"]["downstream"]["independentEFormalTrust"],"PENDING_TRUSTED_PROTECTED_MAIN_RECEIPT")
 def test_negative_mutations_fail_closed(self):
  for qid in QIDS:
   for mutation in ("wrong_answer","wrong_image","wrong_gitblob","notice","lost_option","bad_text","release","formal_g3"):
    with self.subTest(questionId=qid,mutation=mutation):
     r=copy.deepcopy(self.r[qid])
     if mutation=="wrong_answer":r["officialAnswer"]["officialPublishedLetter"]="D"
     elif mutation=="wrong_image":r["originalSource"]["singleSha256"]="0"*64
     elif mutation=="wrong_gitblob":r["originalSource"]["singleGitBlob"]="0"*40
     elif mutation=="notice":r["officialAnswer"]["officialNoObjectionForPaper"]=False
     elif mutation=="lost_option":r["originalSource"]["originalCleanOptions"].pop()
     elif mutation=="bad_text":r["originalSource"]["originalCleanQuestion"]+=" wrong"
     elif mutation=="release":r["downstream"]["ready"]=True
     else:r["officialAnswer"]["formalNewAnswerVerifiedFlagSet"]=True
     with self.assertRaises(ValueError):gate(r,self.bq[qid],self.mq[qid],self.old[qid],self.official[qid],self.notice)
 def test_only_nine_exclusive_new_source_paths_relative_to_protected_main(self):
  result=subprocess.run(["git","diff","--name-only","ba2f3f0757dbf81eaaf125bd610b0f38de52fea9","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True)
  self.assertEqual(set(result.stdout.splitlines()),ALLOWED)
  self.assertFalse(any("questions.json" in name or "sqlite3" in name or "webp-manifest.json" in name or "approved/" in name for name in result.stdout.splitlines()))
