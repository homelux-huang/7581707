"""Annual ROLE A 410-row source inventory integrity. Not a shortcut to per-QID official source QA."""
import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path
from scripts import role_a_114_115_source_gate_inventory as inv

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/ROLE_A_114_115_SOURCE_GATES_20261103.json"

class YearlySourceGateInventory(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_no_410_question_source_gate_approval_claim(self):
  d=self.report
  self.assertEqual(d["schemaVersion"],1)
  self.assertEqual(d["type"],"ROLE_A_ANNUAL_410_READ_ONLY_SOURCE_GAP_INVENTORY_NOT_G1_G2_G3_READY")
  self.assertEqual(d["snapshotSourceBaseCommit"],"e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5")
  self.assertEqual([x["year"] for x in d["years"]],[114,115])
  self.assertEqual(d["overallSummary"]["sourceCandidates"],410)
  self.assertEqual([x["summary"]["sourceCandidates"] for x in d["years"]],[205,205])
  self.assertIn("NO G1 VISUAL",d["status"])
  self.assertNotIn("READY_PASS",d["status"])
 def test_exact_input_410_ids_no_duplicate_with_205_annual_db(self):
  for year in self.report["years"]:
   ids=[q["qid"] for q in year["questions"]]
   self.assertEqual(len(ids),205)
   self.assertEqual(len(set(ids)),205)
   self.assertTrue(all(qid.startswith(str(year["year"])+"-") for qid in ids))
   db=year["sqliteReadOnly"]
   self.assertTrue(db["filePresent"])
   self.assertEqual(db["integrityCheck"],"ok")
   self.assertTrue(db["tableRowCounts"])
   self.assertIn(205,db["tableRowCounts"].values())
 def test_all_qid_source_webp_sha_and_stored_manifest_flags_are_consistent(self):
  for year in self.report["years"]:
   manifest=json.loads((ROOT/f"sudu/data/processed/{year['year']}/webp-manifest.json").read_text(encoding="utf-8"))
   m={x["questionId"]:x for x in manifest["items"]}
   for q in year["questions"]:
    with self.subTest(qid=q["qid"]):
     i=m[q["qid"]]
     self.assertEqual(i.get("qaStatus","UNKNOWN"),q["historicalManifestG1Status"])
     self.assertEqual(i.get("sha256"),q["sourceSingleWebp"]["expectedSha256"])
     self.assertEqual(i.get("sourceSha256"),q["sourcePageWebp"]["expectedSha256"])
     self.assertIsInstance(q["sourceSingleWebp"]["shaMatched"],bool)
     self.assertIsInstance(q["canonicalQuestionVerifiedFlag"],bool)
     self.assertIsInstance(q["canonicalAnswerVerifiedFlag"],bool)
     if q["sourceSingleWebp"]["shaMatched"]:
      self.assertTrue(q["sourceSingleWebp"]["present"])
      self.assertTrue(q["sourceSingleWebp"]["isWebp"])
     if q["historicalG1PassWithMatchingBytes"]:
      self.assertTrue(q["sourceSingleWebp"]["shaMatched"])
      self.assertTrue(q["sourcePageWebp"]["shaMatched"])
      self.assertTrue(q["historicalG1ManifestPass"])
 def test_report_is_deterministic_recomputed_from_source_bytes(self):
  same=inv.build()
  self.assertEqual(self.report,same)
  body=json.dumps(same,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
  self.assertEqual(REPORT.read_text(encoding="utf-8"),body)
 def test_negative_untrusted_bytes_cannot_auto_pass_G1(self):
  valid=b"RIFF"+bytes(4)+b"WEBP"+b"original"
  self.assertTrue(inv.is_real_webp(valid))
  self.assertFalse(inv.is_real_webp(b"BAD!"+valid))
  self.assertFalse(inv.is_real_webp(b""))
  self.assertFalse(inv.is_real_webp(b"RIFF" + bytes(7)))
  self.assertFalse(inv.inspect_asset("does-not-exist.webp","0"*64)["shaMatched"])
  self.assertFalse(inv.inspect_asset(None,None)["shaMatched"])
  with self.assertRaises(ValueError):
   inv.inspect_asset("../etc/passwd","0"*64)
 def test_no_student_ready_written_and_approved_counts_uninferred(self):
  r=self.report
  for year in r["years"]:
   for q in year["questions"]:
    self.assertNotIn("approved",q)
    self.assertNotIn("READY",q)
    self.assertNotIn("LIVE",q)
    self.assertIsInstance(q["issues"],list)
    if not q["canonicalQuestionVerifiedFlag"]:
     self.assertIn("CANONICAL_QUESTION_VERIFIED_FLAG_FALSE_NOT_G2",q["issues"])
    if not q["canonicalAnswerVerifiedFlag"]:
     self.assertIn("CANONICAL_ANSWER_VERIFIED_FLAG_FALSE_NOT_G3",q["issues"])
 def test_sqlite_original_file_read_only_integrity(self):
  for year in (114,115):
   path=ROOT/f"sudu/data/processed/{year}/question-bank.sqlite3"
   con=sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True)
   try: self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   finally:con.close()
if __name__=="__main__":
 unittest.main()
