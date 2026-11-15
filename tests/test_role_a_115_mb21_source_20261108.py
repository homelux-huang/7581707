"""One question G2/G3 source admission 115 MathB21: exact immutable 204 and SQLite rows, deny READY."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"_publisher_main"))
import role_a_115_mb21_source_admission_20261108 as a
from scripts import sudu_verified_publish as pub

def original(path):
    return subprocess.check_output(["git","show",a.QA_BASE+":"+str(path)],cwd=ROOT)

def current(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def keyed(rows):
    return {x["questionId"]:x for x in rows}

class OneSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=current("sudu/data/processed/115/questions.json")
        cls.beforebank=json.loads(original("sudu/data/processed/115/questions.json"))
        cls.manifest=current("sudu/data/processed/115/webp-manifest.json")
        cls.q=keyed(cls.bank["questions"])[a.QID]
        cls.m=keyed(cls.manifest["items"])[a.QID]
        cls.g2=current(a.G2_REL)
        cls.g3=current(a.G3_REL)

    def test_exact_main_publisher_positive_g1_g2_g3_and_no_release(self):
        a.verify()
        self.assertTrue(self.q["questionVerified"])
        self.assertTrue(self.q["answerVerified"])
        self.assertEqual(self.q["answer"],"A")
        self.assertEqual(self.q["options"],["5","4.75","4.50","4.25"])
        self.assertEqual(a.rev(self.q["question"],self.q["options"],a.ORIG_SHA),a.REVISION)
        self.assertTrue(pub.official_notice_scope_certified(ROOT,115,self.q,self.g3))
        self.assertFalse(pub.certificates_complete(ROOT,self.q,self.m,{}))
        self.assertFalse(self.q.get("studentReleaseApproved",False))
        self.assertNotIn("independentSolve",self.q)
        self.assertNotIn("teachingQaEvidence",self.q)
        self.assertNotIn("uiQaEvidence",self.q)

    def test_204_original_canonical_rows_unchanged_and_manifest_original(self):
        old=keyed(self.beforebank["questions"])
        new=keyed(self.bank["questions"])
        self.assertEqual(len(old),len(new))
        self.assertEqual(set(old),set(new))
        self.assertEqual(len(new),205)
        for qid in old:
            if qid!=a.QID:
                with self.subTest(qid=qid):
                    self.assertEqual(old[qid],new[qid])
        self.assertEqual(original("sudu/data/processed/115/webp-manifest.json"),
            (ROOT/"sudu/data/processed/115/webp-manifest.json").read_bytes())
        self.assertEqual(self.beforebank["sharedMaterials"],self.bank["sharedMaterials"])
        self.assertEqual(self.q["assets"]["sha256"],a.ORIG_SHA)

    def test_204_original_sqlite_rows_identical_and_205_matches_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"initial.sqlite3"
            p.write_bytes(original("sudu/data/processed/115/question-bank.sqlite3"))
            old=a.rows(p)
        new=a.rows(ROOT/"sudu/data/processed/115/question-bank.sqlite3")
        self.assertEqual(set(old),set(new))
        self.assertEqual(len(new),205)
        for qid in old:
            if qid!=a.QID:
                with self.subTest(qid=qid):
                    self.assertEqual(old[qid],new[qid])
        self.assertNotEqual(old[a.QID],new[a.QID])
        self.assertEqual(new[a.QID][2],1)
        self.assertEqual(new[a.QID][3],1)
        self.assertEqual(new[a.QID][0],self.q["question"])
        self.assertEqual(json.loads(new[a.QID][5]),self.q)
        self.assertTrue(all(json.loads(new[q["questionId"]][5])==q for q in self.bank["questions"]))
        with sqlite3.connect("file:"+str(ROOT/"sudu/data/processed/115/question-bank.sqlite3")+"?mode=ro",uri=True) as c:
            self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)

    def test_original_immutable_images_stage_and_notices(self):
        for path,sha,blob in ((a.SOURCE_WEBP,a.ORIG_SHA,a.ORIG_BLOB),(a.PAGE_WEBP,a.PAGE_SHA,a.PAGE_BLOB),(a.ANSWER_WEBP,a.ANSWER_IMG_SHA,a.ANSWER_IMG_BLOB)):
            b=(ROOT/path).read_bytes()
            self.assertEqual(a.sha(b),sha)
            self.assertEqual(a.blob(b),blob)
        self.assertEqual(a.blob((ROOT/a.SRC_STAGE_REL).read_bytes()),a.STAGE_BLOB)
        self.assertEqual(a.blob((ROOT/a.CORRECTION_REL).read_bytes()),a.G2_PREEXISTING_BLOB)
        self.assertEqual(a.blob((ROOT/a.ANSWER_CERT_REL).read_bytes()),a.ANSWER_CERT_BLOB)
        self.assertEqual(a.blob((ROOT/a.NOTICE_REL).read_bytes()),a.NOTICE_BLOB)
        self.assertEqual(a.sha((ROOT/a.G1_REL).read_bytes()),a.G1_CERT)

    def test_failclosed_negatives_change_option_image_answer_notice(self):
        a.negative()
        bad=copy.deepcopy(self.q)
        bad["options"][0]+=" NOT PRINTED"
        self.assertNotEqual(a.rev(bad["question"],bad["options"],a.ORIG_SHA),a.REVISION)
        bad=copy.deepcopy(self.q)
        bad["textQaEvidence"]["questionRevision"]="0"*64
        self.assertFalse(pub.source_proof(bad,True,True,a.REVISION)[0])
        bad=copy.deepcopy(self.q)
        bad["officialFinalQaEvidence"]["answerPdfSha256"]="0"*64
        self.assertFalse(pub.source_proof(bad,True,True,a.REVISION)[1])
        bad=copy.deepcopy(self.g3)
        bad["noObjectionForPaper"]=False
        self.assertFalse(pub.official_notice_scope_certified(ROOT,115,self.q,bad))
        bad=copy.deepcopy(self.m)
        bad["visualReviewEvidence"]["referenceSha256"]="0"*64
        self.assertFalse(pub.visual_certificate(ROOT,bad,a.QID))
        self.assertFalse(pub.certificates_complete(ROOT,self.q,self.m,{}))

    def test_whitelist_paths_and_no_approved_main_student_work(self):
        expected={
            "tests/role_a_115_mb21_schema_probe_20261108.py",
            ".github/workflows/role-a-115-mb21-schema-probe-20261108.yml",
            "scripts/role_a_115_mb21_source_admission_20261108.py",
            "tests/test_role_a_115_mb21_source_20261108.py",
            "docs/ROLE_A_115_MB21_SOURCE_ADMISSION_20261108.md",
            ".github/workflows/role-a-115-mb21-source-admission-20261108.yml",
            ".github/workflows/role-a-115-mb21-postcommit-20261108.yml",
            "sudu/data/processed/115/questions.json",
            "sudu/data/processed/115/question-bank.sqlite3",
            "sudu/data/processed/115/inventory.json",
            a.SRC_STAGE_REL,a.G2_REL,a.G3_REL,a.REPORT_REL,a.SQL_REPORT
        }
        paths=set(subprocess.check_output(["git","diff","--name-only",a.QA_BASE,"HEAD"],text=True,cwd=ROOT).splitlines())
        self.assertEqual(paths,expected)
        self.assertFalse(any(p.startswith("sudu/data/approved/") or p.startswith("sudu/release-governance/") or "/114/" in p for p in paths))

if __name__=="__main__":
    unittest.main()
