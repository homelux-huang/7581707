"""Real post-commit 114 E11 source-ONLY positive/negative CI, compared with original official QA SHA."""
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
sys.path.insert(0,str(ROOT/"_publisher_main"))
sys.path.insert(0,str(ROOT/"scripts"))
from scripts import sudu_verified_publish as pub
import role_a_114_e11_canonical_g2g3_20261107 as e11

BASE=ROOT/"sudu/data/processed/114"
QID=e11.QID

def git_original(rel):
    return subprocess.check_output(["git","show",e11.ORIGINAL_QA+":"+rel],cwd=ROOT)

def bank(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def table_values(data):
    return {x["questionId"]: x for x in data}

class E11PostCommit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=bank("sudu/data/processed/114/questions.json")
        cls.manifest=bank("sudu/data/processed/114/webp-manifest.json")
        cls.oldbank=json.loads(git_original("sudu/data/processed/114/questions.json"))
        cls.oldmanifest=json.loads(git_original("sudu/data/processed/114/webp-manifest.json"))
        cls.q=table_values(cls.bank["questions"])[QID]
        cls.m=table_values(cls.manifest["items"])[QID]
        cls.g2=bank(e11.OCR_REL)
        cls.g3=bank(e11.G3_REL)

    def test_real_main_publisher_positive_g1_g2_g3_no_student(self):
        e11.verify_post()
        self.assertFalse(self.q.get("studentReleaseApproved",False))
        self.assertFalse(self.q.get("teachingQaStatus")=="PASS")
        self.assertFalse(self.q.get("uiQaStatus")=="PASS")
        self.assertEqual(self.q["answer"],"A")
        self.assertTrue(pub.official_notice_scope_certified(ROOT,114,self.q,self.g3))
        self.assertEqual(e11.rev(self.q,e11.WEBP),e11.QREV)
        self.assertTrue(pub.visual_certificate(ROOT,self.m,QID))
        self.assertFalse(pub.certificates_complete(ROOT,self.q,self.m,{}))

    def test_all_204_other_questions_and_manifest_unchanged(self):
        before=table_values(self.oldbank["questions"])
        after=table_values(self.bank["questions"])
        self.assertEqual(set(before),set(after))
        self.assertEqual(len(after),205)
        self.assertEqual(len(self.manifest["items"]),205)
        for qid in before:
            if qid!=QID:
                with self.subTest(qid=qid):
                    self.assertEqual(after[qid],before[qid])
        om=table_values(self.oldmanifest["items"])
        nm=table_values(self.manifest["items"])
        self.assertEqual(set(om),set(nm))
        for qid in om:
            if qid!=QID:
                with self.subTest(qid=qid):
                    self.assertEqual(nm[qid],om[qid])
        self.assertEqual(self.oldbank["sharedMaterials"],self.bank["sharedMaterials"])
        self.assertEqual(self.oldmanifest["sharedMaterialCrops"],self.manifest["sharedMaterialCrops"])
        self.assertEqual(self.m["sha256"],om[QID]["sha256"])
        self.assertEqual(self.m["crop"],om[QID]["crop"])
        self.assertEqual(self.m["qaStatus"],om[QID]["qaStatus"])
        self.assertEqual(self.m["visualReviewEvidence"]["referenceSha256"],e11.sha((ROOT/e11.VISUAL_REL).read_bytes()))

    def test_actual_sqlite_204_original_payload_bytes_remain_and_integrity(self):
        before=git_original("sudu/data/processed/114/question-bank.sqlite3")
        with tempfile.TemporaryDirectory() as tmp:
            original_db=Path(tmp)/"original.sqlite3"
            original_db.write_bytes(before)
            old=e11.db_rows(original_db)
        new=e11.db_rows(BASE/"question-bank.sqlite3")
        self.assertEqual(set(old),set(new))
        self.assertEqual(len(new),205)
        self.assertEqual({k:v for k,v in old.items() if k!=QID},
                         {k:v for k,v in new.items() if k!=QID})
        self.assertNotEqual(old[QID],new[QID])
        self.assertEqual(json.loads(new[QID][0]),self.q)
        self.assertEqual(new[QID][1],hashlib.sha256(new[QID][0].encode("utf-8")).hexdigest())
        with sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True) as cx:
            self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)

    def test_exact_source_image_and_historical_evidence_blobs(self):
        for p,sha,blob in ((e11.WEBP_REL,e11.WEBP,e11.WEBP_BLOB),
                           (e11.PAGE_REL,e11.PAGE,e11.PAGE_BLOB),
                           (e11.ANSWER_IMAGE_REL,e11.ANSWER_IMAGE,e11.ANSWER_IMAGE_BLOB)):
            b=(ROOT/p).read_bytes()
            self.assertEqual(e11.sha(b),sha)
            self.assertEqual(e11.blob(b),blob)
        for p,blob in e11.HISTORICAL_BLOBS.items():
            self.assertEqual(e11.blob((ROOT/p).read_bytes()),blob)
        self.assertEqual(e11.blob((ROOT/e11.VISUAL_REL).read_bytes()),e11.VISUAL_BLOB)
        self.assertEqual(e11.blob((BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json").read_bytes()),e11.LEDGER_BLOB)

    def test_publisher_native_corruption_negative_g2_g3_release(self):
        original_rev=e11.QREV
        fake=copy.deepcopy(self.q)
        fake["options"][0]="unapproved different option"
        self.assertNotEqual(e11.rev(fake,e11.WEBP),original_rev)
        fake=copy.deepcopy(self.q)
        fake["textQaEvidence"]["sourceImageSha256"]="0"*64
        self.assertFalse(pub.source_proof(fake,True,True,e11.QREV)[0])
        fake=copy.deepcopy(self.q)
        fake["officialFinalQaEvidence"]["answerPdfSha256"]="0"*64
        self.assertFalse(pub.source_proof(fake,True,True,e11.QREV)[1])
        fake=copy.deepcopy(self.g3)
        fake["finalAnswer"]="D"
        self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.q,fake) and fake["finalAnswer"]==self.q["answer"])
        fake=copy.deepcopy(self.g3)
        fake["noObjectionForPaper"]=True
        self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.q,fake))
        fake=copy.deepcopy(self.g3)
        fake["confirmationPdfSha256"]="0"*64
        self.assertFalse(pub.official_notice_scope_certified(ROOT,114,self.q,fake))
        fake=copy.deepcopy(self.m)
        fake["visualReviewEvidence"]["referenceSha256"]="0"*64
        self.assertFalse(pub.visual_certificate(ROOT,fake,QID))
        self.assertFalse(self.q.get("studentReleaseApproved",False))
        e11.negative_test()

    def test_only_authorized_single_source_file_paths(self):
        expected={
            "scripts/role_a_114_e11_canonical_g2g3_20261107.py",
            "tests/test_role_a_114_e11_source_20261107.py",
            ".github/workflows/role-a-114-e11-source-admission-20261107.yml",
            ".github/workflows/role-a-114-e11-postcommit-20261107.yml",
            "docs/ROLE_A_114_E11_SOURCE_ADMISSION_20261107.md",
            "sudu/data/processed/114/questions.json",
            "sudu/data/processed/114/webp-manifest.json",
            "sudu/data/processed/114/question-bank.sqlite3",
            "sudu/data/processed/114/inventory.json",
            e11.STAGE_REL,e11.A_TEXT_REL,e11.A_OFFICIAL_REL,
            e11.OCR_REL,e11.G3_REL,e11.REPORT_REL,e11.SQL_REPORT_REL,
        }
        r=subprocess.check_output(["git","diff","--name-only",e11.ORIGINAL_QA,"HEAD"],text=True,cwd=ROOT)
        self.assertEqual(set(r.splitlines()),expected)
        self.assertFalse(any(x.startswith("sudu/data/approved/") or x.startswith("sudu/release-governance/") for x in expected))

if __name__=="__main__":
    unittest.main()
