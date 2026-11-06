"""ROLE A 114 business 04/09/10 true original single WebP and published answer; NO RELEASE."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
QIDS = ("114-09-1-04","114-09-1-09","114-09-1-10")
ANSWERS = {"114-09-1-04":"A","114-09-1-09":"A","114-09-1-10":"D"}
BLOBS = {"114-09-1-04":"11ea2aec2a6e12c941bc7ae15134e99faf17cc49",
         "114-09-1-09":"ee76b9ed40b36bc4522e47009b3ca65906e2b92a",
         "114-09-1-10":"246035c42fe43f3c44621f98a9493a656e3366f2"}
PAGES = {"114-09-1-04":"5bf2c1a3f8f4ee088361c6acfdb81fb7cf3ba624",
         "114-09-1-09":"5ebd8047cda1af01d1074f307764a4979d5fc83c",
         "114-09-1-10":"5ebd8047cda1af01d1074f307764a4979d5fc83c"}
ANSWER_BLOB="88d42b12af03fc605f01bd1ff5df259686c055e7"
NOTICE_BLOB="6b9a919f224bec8dc3659052a404b4173b6ef366"
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def gitblob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def valid(e,q,m,notice):
    if e["questionId"]!=q["questionId"] or e["source"]["questionRawKeptUnmodified"]!=q["question"] or e["source"]["optionsRawKeptUnmodified"]!=q["options"]:raise ValueError("text changed")
    if len(q["options"])!=4 or e["source"]["originalWebpSha256"]!=m["sha256"]:raise ValueError("original source mismatch")
    if e["officialAnswer"]["printedAnswer"]!=ANSWERS[q["questionId"]]:raise ValueError("printed answer mismatch")
    if e["officialAnswer"]["publishedAnswerSourceGitBlob"]!=ANSWER_BLOB:raise ValueError("answer image blob mismatch")
    if e["officialAnswer"]["officialNoticeLedgerGitBlob"]!=NOTICE_BLOB:raise ValueError("notice blob changed")
    named=[c for c in notice["confirmed"] if c["questionId"]==q["questionId"]]
    if bool(named)!=e["officialAnswer"]["noticeNamedForQuestion"]:raise ValueError("notice scope")
    if named and (named[0]["officialConfirmedAnswer"]!=e["officialAnswer"]["printedAnswer"] or named[0]["changeFromExistingOfficialPdfTextCandidate"]!="NONE_OBSERVED"):raise ValueError("correction altered answer")
    if e["canonical"]["canonicalJsonOrSqliteEdited"] or e["next"]["READY"] or e["next"]["LIVE"] or e["officialAnswer"]["formalAnswerVerifiedFlagPromoted"]:raise ValueError("illegal release")
    return True
class OriginalBusinessQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=read(BASE/"questions.json")
        cls.m=read(BASE/"webp-manifest.json")
        cls.notice=next(d for d in read(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")["docs"] if d["paperCode"]=="09-1")
        cls.q={q["questionId"]:q for q in cls.bank["questions"]}
        cls.mq={q["questionId"]:q for q in cls.m["items"]}
        cls.e={qid:read(BASE/"review-evidence"/(qid+"-original-20261106.json")) for qid in QIDS}
    def test_exact_source_provenance_original_pixels(self):
        self.assertEqual(len(self.bank["questions"]),205)
        self.assertEqual(len(self.m["items"]),205)
        for qid in QIDS:
            with self.subTest(qid=qid):
                q,m,e=self.q[qid],self.mq[qid],self.e[qid]
                self.assertTrue(valid(e,q,m,self.notice))
                self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
                self.assertFalse(q["questionVerified"])
                self.assertFalse(q["answerVerified"])
                self.assertFalse(e["source"]["sourceWebpRecreated"])
                for rel,hashval,blobid in ((m["output"],m["sha256"],BLOBS[qid]),(m["source"],m["sourceSha256"],PAGES[qid])):
                    raw=(ROOT/rel).read_bytes()
                    self.assertEqual(raw[:4],b"RIFF")
                    self.assertEqual(raw[8:12],b"WEBP")
                    self.assertEqual(sha(raw),hashval)
                    self.assertEqual(gitblob(raw),blobid)
    def test_real_original_printed_answer_and_official_9page_scope(self):
        p=ROOT/"sudu/data/original/114/09-1-answers/p001-f0cbc82606-v2-w1400-q66.webp"
        self.assertEqual(gitblob(p.read_bytes()),ANSWER_BLOB)
        n=(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json").read_bytes()
        self.assertEqual(gitblob(n),NOTICE_BLOB)
        self.assertEqual(self.notice["pageCount"],9)
        self.assertTrue(self.notice["allPagesVisuallyReviewed"])
        self.assertEqual(self.e["114-09-1-09"]["officialAnswer"]["noticePageNumbers"],[4])
        self.assertFalse(self.e["114-09-1-04"]["officialAnswer"]["noticeNamedForQuestion"])
        self.assertFalse(self.e["114-09-1-10"]["officialAnswer"]["noticeNamedForQuestion"])
        self.assertTrue(self.e["114-09-1-09"]["officialAnswer"]["noticeNamedForQuestion"])
    def test_no_flag_or_bank_changes_and_sqlite_integrity(self):
        db=BASE/"question-bank.sqlite3"
        with sqlite3.connect("file:"+str(db)+"?mode=ro",uri=True) as c:
            self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
            for qid in QIDS:
                row=c.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(json.loads(row[0]),self.q[qid])
                self.assertEqual(sha(row[0].encode("utf-8")),row[1])
    def test_negative_untrusted_source_and_admission(self):
        for qid in QIDS:
            q,m,e=self.q[qid],self.mq[qid],self.e[qid]
            for case in ("wronganswer","missingoption","notice","ready","originalsha"):
                with self.subTest(qid=qid,case=case):
                    d=copy.deepcopy(e)
                    if case=="wronganswer":d["officialAnswer"]["printedAnswer"]="B" if qid!="114-09-1-10" else "A"
                    elif case=="missingoption":d["source"]["optionsRawKeptUnmodified"].pop()
                    elif case=="notice":d["officialAnswer"]["noticeNamedForQuestion"]=not d["officialAnswer"]["noticeNamedForQuestion"]
                    elif case=="ready":d["next"]["READY"]=True
                    else:d["source"]["originalWebpSha256"]="0"*64
                    with self.assertRaises(ValueError):valid(d,q,m,self.notice)
    def test_only_six_leased_new_files(self):
        expected={*(f"sudu/data/processed/114/review-evidence/{qid}-original-20261106.json" for qid in QIDS),
                  "tests/test_role_a_114_bus04_09_10_source_20261106.py",
                  ".github/workflows/role-a-114-bus04-09-10-source-20261106.yml",
                  "docs/ROLE_A_114_BUS04_09_10_SOURCE_20261106.md"}
        r=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],capture_output=True,text=True,check=True,cwd=ROOT)
        self.assertEqual(set(r.stdout.splitlines()),expected)
if __name__=="__main__":unittest.main()
