"""ROLE A official 114 Economics Q27 original OCR superscript + printed answer evidence; fail closed, NO RELEASE."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
QID = "114-09-2-27"
RECEIPT = BASE / "review-evidence/114-09-2-27-math-ocr-source-20261107.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def gitblob(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def src_revision(question, opts, webp_sha):
    data = {"question":question,"options":opts,"singleQuestionWebpSha256":webp_sha}
    return sha(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))

def valid(receipt, q, manifest, notices):
    s,ans,math,canonical,nxt = (receipt[k] for k in ("source","officialAnswer","mathConsistency","canonical","next"))
    if receipt["questionId"] != QID or q["questionId"] != QID or manifest["questionId"] != QID:
        raise ValueError("different question")
    if s["rawOcrQuestionUnchanged"] != q["question"] or s["optionsRawKeptUnmodified"] != q["options"]:
        raise ValueError("raw source mismatch")
    if q["options"] != ["0","10","27","36"]:
        raise ValueError("option mismatch")
    old = "AC = q2 – 16 q + 74"
    new = "AC = q² – 16 q + 74"
    if q["question"].count(old) != 1 or s["sourceImageCorrectedQuestionCandidate"] != q["question"].replace(old,new):
        raise ValueError("uncorrected or broad source rewrite")
    if s["correctedExactSubstringOld"] != old or s["correctedExactSubstringNew"] != new:
        raise ValueError("G2 diff")
    if s["singleWebpSha256"] != manifest["sha256"] or s["singleWebpPath"] != manifest["output"] or s["originalPagePath"] != manifest["source"]:
        raise ValueError("image mismatch")
    if s["rawSourceRevisionFromRoleB"] != src_revision(q["question"],q["options"],manifest["sha256"]):
        raise ValueError("old revision mismatch")
    if s["proposedCorrectedSourceRevision"] != src_revision(s["sourceImageCorrectedQuestionCandidate"],q["options"],manifest["sha256"]):
        raise ValueError("new revision mismatch")
    named = [v for v in notices["confirmed"] if v["questionId"] == QID]
    if len(named)!=1 or named[0]["officialConfirmedAnswer"]!="C" or named[0]["changeFromExistingOfficialPdfTextCandidate"]!="NONE_OBSERVED" or named[0]["pdfPageNumbers"] != [3]:
        raise ValueError("notice scope mismatch")
    if ans["printedAnswer"] != "C" or ans["namedNoticeConfirmedAnswer"]!="C" or ans["noticeChangeFromCandidate"]!="NONE_OBSERVED" or ans["namedNoticePage"] != [3] or q["answer"]!="C":
        raise ValueError("incorrect or unverified printed answer")
    if math["q9MC"] != 29 or math["q9ExpectedAR"] != 14 or math["q8MC"] != math["q8AC"] or math["q10AC"]!=math["q10ExpectedAR"]:
        raise ValueError("printed math inconsistency not recorded")
    if not math["status"].startswith("QUARANTINED_"):
        raise ValueError("unresolved MC contradiction cannot pass")
    if canonical["all205CanonicalAndSqliteUntouched"] is not True or canonical["questionVerifiedOriginally"] or canonical["answerVerifiedOriginally"] or s["canonicalBankOrManifestEdited"]:
        raise ValueError("canonical admission not allowed")
    if ans["formalAnswerVerifiedFlagPromoted"] or nxt["READY"] or nxt["LIVE"] or nxt["ROLE_D"]!="HOLD":
        raise ValueError("unauthorized release")
    return True

class SourceQ27(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = read(BASE/"questions.json")
        cls.manifest = read(BASE/"webp-manifest.json")
        cls.q = next(q for q in cls.bank["questions"] if q["questionId"]==QID)
        cls.m = next(m for m in cls.manifest["items"] if m["questionId"]==QID)
        cls.notice_file = BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
        cls.notices = next(d for d in read(cls.notice_file)["docs"] if d["paperCode"]=="09-2")
        cls.e = read(RECEIPT)

    def test_original_205_schema_and_read_only_sqlite(self):
        self.assertEqual(len(self.bank["questions"]),205)
        self.assertEqual(len(self.manifest["items"]),205)
        self.assertEqual(self.m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
        self.assertFalse(self.q["questionVerified"])
        self.assertFalse(self.q["answerVerified"])
        with sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
            row=con.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(json.loads(row[0]),self.q)
            self.assertEqual(sha(row[0].encode("utf-8")),row[1])

    def test_original_image_paper_answer_and_revision(self):
        self.assertTrue(valid(self.e,self.q,self.m,self.notices))
        s,a=self.e["source"],self.e["officialAnswer"]
        for path,digest,blob in (
            (s["singleWebpPath"],s["singleWebpSha256"],s["singleWebpGitBlob"]),
            (s["originalPagePath"],s["originalPageSha256"],s["originalPageGitBlob"]),
            (a["originalPrintedAnswerPagePath"],None,a["printedAnswerPageGitBlob"]),
            (a["noticeLedgerPath"],None,a["noticeLedgerGitBlob"])):
            data=(ROOT/path).read_bytes()
            if digest:
                self.assertEqual(sha(data),digest)
            self.assertEqual(gitblob(data),blob)
        self.assertEqual(s["originalCrop"],self.m["crop"])
        self.assertFalse(s["sourceImageRecreated"])
        self.assertEqual(self.e["officialAnswer"]["printedAnswer"],"C")
        self.assertEqual(self.e["source"]["proposedCorrectedSourceRevision"],"516abf551e1896d6afb8b578733c38d44b06b1140b0e26fc32090bb8eba65b20")

    def test_printed_cost_math_contradiction_preserved(self):
        self.assertEqual(8**2-16*8+74,10)
        self.assertEqual(3*8**2-32*8+74,10)
        self.assertEqual(3*9**2-32*9+74,29)
        self.assertNotEqual(29,14)
        self.assertEqual(10**2-16*10+74,14)
        self.assertEqual((14-(9**2-16*9+74))*9,27)
        self.assertIn("QUARANTINED",self.e["mathConsistency"]["status"])

    def test_fail_closed_negative_source_answer_and_release(self):
        for key in ("wrong_answer","false_notice","fake_corrected_text","wrong_sha","hide_contradiction","promote_ready","promote_answer"):
            with self.subTest(key=key):
                d=copy.deepcopy(self.e)
                if key=="wrong_answer":d["officialAnswer"]["printedAnswer"]="D"
                if key=="false_notice":d["officialAnswer"]["noticeChangeFromCandidate"]="CHANGED"
                if key=="fake_corrected_text":d["source"]["sourceImageCorrectedQuestionCandidate"] += "  "
                if key=="wrong_sha":d["source"]["singleWebpSha256"]="0"*64
                if key=="hide_contradiction":d["mathConsistency"]["status"]="PASS"
                if key=="promote_ready":d["next"]["READY"]=True
                if key=="promote_answer":d["officialAnswer"]["formalAnswerVerifiedFlagPromoted"]=True
                with self.assertRaises(ValueError):
                    valid(d,self.q,self.m,self.notices)

    def test_only_four_new_lease_paths_in_last_four_commits(self):
        expected={
          "sudu/data/processed/114/review-evidence/114-09-2-27-math-ocr-source-20261107.json",
          "tests/test_role_a_114_econ27_math_ocr_source_20261107.py",
          ".github/workflows/role-a-114-econ27-math-ocr-source-20261107.yml",
          "docs/ROLE_A_114_ECON27_MATH_OCR_SOURCE_20261107.md"}
        res=subprocess.run(["git","diff","--name-only","HEAD~4","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(set(res.stdout.splitlines()),expected)

if __name__=="__main__":
    unittest.main()
