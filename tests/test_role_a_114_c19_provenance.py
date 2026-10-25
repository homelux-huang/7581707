"""Role A C19 exact-v2 source and SQLite QA — NOT a teacher/release approval."""
import copy
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import repair_114_c19_provenance as r

class C19SourceParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank, cls.byid, cls.image, cls.sizes = r.evidence_and_source()

    def test_only_new_v2_is_current_and_old_v1_remains_quarantined(self):
        image = self.image
        self.assertEqual(image["sha256"], r.NEW)
        self.assertEqual(image["oldAssetBeforeDirectVisualRepair"]["sha256"], r.OLD)
        self.assertTrue(image["oldAssetBeforeDirectVisualRepair"]["qaStatus"].startswith("BLOCKED"))
        self.assertNotEqual(r.OLD, r.NEW)
        self.assertEqual(self.byid[r.QID]["questionProvenance"]["webpSha256"], r.NEW)
        self.assertGreater(self.sizes["v1Size"], self.sizes["v2Size"])

    def test_exact_205_sqlite_json_integrity_after_reconciliation(self):
        report = r.validate_fixed()
        self.assertEqual(report["rows"], 205)
        _, bank = r.rows(r.BASE / "question-bank.sqlite3")
        self.assertEqual(bank, self.byid)

    def test_all_204_untouched_question_objects_have_matching_sqlite(self):
        _, rows = r.rows(r.BASE / "question-bank.sqlite3")
        self.assertEqual(len(self.byid) - 1, 204)
        for qid, q in self.byid.items():
            if qid != r.QID:
                with self.subTest(qid=qid):
                    self.assertEqual(rows[qid], q)

    def test_wrong_old_version_cannot_satisfy_current_image_sha(self):
        with self.assertRaises(AssertionError):
            r.check_webp(r.V1, r.NEW)

    def test_payload_hash_tampering_fails_even_when_sqlite_integrity_ok(self):
        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp) / "tampered.sqlite3"
            shutil.copy2(r.BASE / "question-bank.sqlite3", tmp)
            with sqlite3.connect(tmp) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                db.execute("UPDATE questions SET payload_sha256=? WHERE question_id=?",
                           ("0" * 64, r.QID))
                db.commit()
            with self.assertRaises(AssertionError):
                r.rows(tmp)

    def test_two_isolated_reimports_are_idempotent_and_byte_deterministic(self):
        current = self.byid[r.QID]
        old = copy.deepcopy(current)
        old["questionProvenance"]["webpSha256"] = r.OLD
        others = {qid: copy.deepcopy(q) for qid, q in self.byid.items() if qid != r.QID}
        with tempfile.TemporaryDirectory() as tmp:
            hashes = []
            for n in (1, 2):
                out = Path(tmp) / f"db{n}.sqlite3"
                shutil.copy2(r.BASE / "question-bank.sqlite3", out)
                hashes.append(r.modify_sqlite(out, old, current, others))
                self.assertEqual(r.modify_sqlite(out, old, current, others), hashes[-1])
            self.assertEqual(hashes[0], hashes[1])

    def test_no_ai_to_human_or_answer_release_promotion(self):
        q = self.byid[r.QID]
        self.assertFalse(q["questionVerified"])
        self.assertFalse(q["answerVerified"])
        self.assertFalse(q["integrationReady"])
        direct = r.read(r.ROOT / r.DIRECT)
        self.assertFalse(direct["independentExternalHumanRecheck"])
        self.assertEqual(direct["answerVerifiedAdded"], 0)
        self.assertEqual(direct["questionVerifiedAdded"], 0)
        self.assertEqual(q["textQaStatus"], "PARTIAL_OPTION_D_CORRECTED_NOT_FULL_TEXT_QA")

if __name__ == "__main__":
    unittest.main()
