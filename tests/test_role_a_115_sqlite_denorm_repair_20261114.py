"""Exact baseline projection repair, byte-preserving payloads and fail-closed negatives."""
import copy
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import role_a_115_sqlite_denorm_repair_20261114 as repair


class ProjectionRepair(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / repair.REL
        self.base.parent.mkdir(parents=True)
        shutil.copytree(ROOT / repair.REL, self.base)
        for name in ("question-bank.sqlite3", "inventory.json"):
            raw = subprocess.check_output(["git", "show", f"{repair.BASE_COMMIT}:{repair.REL / name}"], cwd=ROOT)
            (self.base / name).write_bytes(raw)

    def test_reconcile_only_80_projection_cells_with_payload_schema_shared_exact(self):
        before = repair.snapshot(self.base / "question-bank.sqlite3")
        immutable = {name: (self.base / name).read_bytes() for name in ("questions.json", "webp-manifest.json")}
        changes = repair.apply(self.root)
        report = repair.load(self.root / repair.REPORT)
        self.assertEqual(report["changedRows"], 77)
        self.assertEqual(report["changedCells"], 80)
        self.assertEqual(report["countsByColumn"], repair.EXPECTED_COUNTS)
        repair.verify_changes(before, repair.snapshot(self.base / "question-bank.sqlite3"), changes)
        for name, raw in immutable.items():
            self.assertEqual((self.base / name).read_bytes(), raw)
        self.assertFalse(repair.plan(self.root)[0])

    def test_second_application_is_byte_identical_noop(self):
        repair.apply(self.root)
        before = {name: (self.base / name).read_bytes() for name in ("question-bank.sqlite3", "inventory.json", repair.REPORT.name)}
        self.assertEqual(repair.apply(self.root), [])
        self.assertEqual(before, {name: (self.base / name).read_bytes() for name in before})

    def test_unexpected_nonleased_column_mismatch_rejected_before_write(self):
        with sqlite3.connect(self.base / "question-bank.sqlite3") as db:
            db.execute("UPDATE questions SET schema_version=99 WHERE question_id='115-00-MB-05'")
        raw = (self.base / "question-bank.sqlite3").read_bytes()
        with self.assertRaisesRegex(ValueError, "Unexpected projection mismatch"):
            repair.apply(self.root)
        self.assertEqual((self.base / "question-bank.sqlite3").read_bytes(), raw)

    def test_changed_payload_bytes_rejected_by_exact_row_verifier(self):
        changes, before = repair.plan(self.root)
        after = copy.deepcopy(before)
        for change in changes:
            after[1][change["questionId"]][change["column"]] = change["after"]
        after[1]["115-00-MB-05"]["payload_json"] += " "
        with self.assertRaisesRegex(ValueError, "Unexpected database row/column/payload change"):
            repair.verify_changes(before, after, changes)

    def test_inventory_corruption_rejected_before_database_write(self):
        inventory = repair.load(self.base / "inventory.json")
        inventory["sqlite"]["dbSha256"] = "0" * 64
        (self.base / "inventory.json").write_text(json.dumps(inventory))
        raw = (self.base / "question-bank.sqlite3").read_bytes()
        with self.assertRaisesRegex(ValueError, "Inventory DB SHA mismatch"):
            repair.apply(self.root)
        self.assertEqual((self.base / "question-bank.sqlite3").read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
