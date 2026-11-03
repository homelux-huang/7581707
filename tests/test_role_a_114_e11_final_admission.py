"""114 E11 strict source evidence reconciliation only; cannot admit to student release."""
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
DOC=BASE/"review-evidence/114-00-E-11-final-admission-20261103.json"
QID="114-00-E-11"
FILES={
"source":"sudu/data/processed/114/review-evidence/114-00-E-11-source-text-20261028.json",
"official":"sudu/data/processed/114/review-evidence/114-00-E-11-official.json",
}
CHANGES={
"sudu/data/processed/114/review-evidence/114-00-E-11-final-admission-20261103.json",
"tests/test_role_a_114_e11_final_admission.py",
".github/workflows/role-a-114-e11-final-admission.yml",
"docs/ROLE_A_114_E11_FINAL_ADMISSION_20261103.md",
}
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
class SourceE11(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=load(DOC.relative_to(ROOT))
  cls.s=load(FILES["source"])
  cls.a=load(FILES["official"])
  cls.bank=load("sudu/data/processed/114/questions.json")
  cls.man=load("sudu/data/processed/114/webp-manifest.json")
  cls.q=next(q for q in cls.bank["questions"] if q["questionId"]==QID)
  cls.image=next(x for x in cls.man["items"] if x["questionId"]==QID)
 def test_exact_source_and_official_pins(self):
  r=self.r
  self.assertEqual(r["questionId"],QID)
  self.assertEqual(blob((ROOT/FILES["source"]).read_bytes()),r["source"]["rawOriginalEvidenceBlob"])
  self.assertEqual(blob((ROOT/FILES["official"]).read_bytes()),r["source"]["rawOfficialAnswerEvidenceBlob"])
  self.assertEqual(r["source"]["question"],self.q["question"])
  self.assertEqual(r["source"]["options"],self.q["options"])
  self.assertEqual(len(r["source"]["options"]),4)
  self.assertEqual(r["source"]["singleQuestionSha256"],self.image["sha256"])
  self.assertEqual(r["source"]["sourceTextRevision"],self.r["canonical"]["questionRevisionPinned"])
  self.assertEqual(r["official"]["answer"],self.a["finalAnswer"])
  self.assertEqual(r["official"]["answer"],"A")
  self.assertEqual(r["official"]["onlyCorrectionNamedForEnglish"],"114-00-E-26")
  self.assertEqual(r["official"]["confirmationNamedQuestionIds"],["114-00-E-26"])
  self.assertFalse(r["official"]["formalNewSourceApprovalFlagSet"])
  self.assertFalse(r["official"]["q11ChangedByNotice"])
 def test_real_archived_immutable_bytes(self):
  r=self.r
  for name,expected,git in [
   (r["source"]["originalPageWebp"],r["source"]["originalPageSha256"],r["source"]["originalPageGitBlob"]),
   (r["source"]["singleQuestionWebp"],r["source"]["singleQuestionSha256"],r["source"]["singleQuestionGitBlob"]),
   (r["official"]["officialAnswerImage"],r["official"]["officialAnswerImageSha256"],r["official"]["officialAnswerImageGitBlob"]),
  ]:
   raw=(ROOT/name).read_bytes()
   self.assertEqual(raw[:4],b"RIFF")
   self.assertEqual(raw[8:12],b"WEBP")
   self.assertEqual(sha(raw),expected)
   self.assertEqual(blob(raw),git)
  self.assertEqual(r["source"]["crop"],[90,275,1310,591])
  self.assertFalse(r["source"]["sourcePixelsRecreatedThisTask"])
 def test_205_json_sqlite_exact_payload_and_no_release(self):
  self.assertEqual(len(self.bank["questions"]),205)
  self.assertEqual(self.q["questionId"],QID)
  self.assertFalse(self.q["questionVerified"])
  self.assertTrue(self.q["answerVerified"])
  self.assertEqual(self.q["officialFinalAnswer"],"A")
  self.assertFalse(self.r["canonical"]["canonicalG2QuestionVerifiedExpected"])
  self.assertTrue(self.r["canonical"]["canonicalG3AnswerVerifiedExpected"])
  self.assertFalse(self.r["canonical"]["canonicalStudentReleaseApprovedExpected"])
  db="file:"+(BASE/"question-bank.sqlite3").as_posix()+"?mode=ro"
  with sqlite3.connect(db,uri=True) as cx:
   self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   payload,hashvalue=cx.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
  self.assertEqual(json.loads(payload),self.q)
  self.assertEqual(sha(payload.encode("utf-8")),hashvalue)
  self.assertFalse(self.r["canonical"]["sqliteModifiedInThisTask"])
  self.assertFalse(self.r["downstream"]["READY"])
  self.assertFalse(self.r["downstream"]["LIVE"])
 def test_negative_checks_before_any_admission(self):
  from copy import deepcopy
  for changed in ["wrongQ","wrongA","fakedNotice","publish"]:
   r=deepcopy(self.r)
   if changed=="wrongQ":r["source"]["options"].pop()
   elif changed=="wrongA":r["official"]["answer"]="B"
   elif changed=="fakedNotice":r["official"]["confirmationNamedQuestionIds"].append(QID)
   else:r["downstream"]["READY"]=True
   accepted=(r["questionId"]==QID and r["source"]["options"]==self.q["options"] and
             r["official"]["answer"]=="A" and r["official"]["confirmationNamedQuestionIds"]==["114-00-E-26"]
             and not r["downstream"]["READY"] and not r["downstream"]["LIVE"])
   self.assertFalse(accepted,changed)
 def test_leased_diff_only(self):
  result=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True)
  self.assertEqual(set(result.stdout.splitlines()),CHANGES)
  self.assertFalse(self.r["canonical"]["sourceFilesModifiedInThisTask"])
