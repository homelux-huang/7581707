"""Current bank corruption regressions and historical one-PR gate routing."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("integrity", ROOT / "scripts/qa_current_source_integrity_20261114.py")
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


class CurrentPayloadIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "sudu/data/processed/115"
        self.base.parent.mkdir(parents=True)
        shutil.copytree(ROOT / "sudu/data/processed/115", self.base)

    def update(self, filename, edit):
        path = self.base / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        edit(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_current_205_payloads_pass_and_sources_stay_byte_identical(self):
        before = {p.name: integrity.sha(p) for p in self.base.iterdir() if p.is_file()}
        result = integrity.check_year(self.root, 115)
        self.assertEqual(result["rows"], 205)
        self.assertEqual(result["studentReleaseVerdict"], "NOT_EVALUATED")
        self.assertEqual(before, {p.name: integrity.sha(p) for p in self.base.iterdir() if p.is_file()})

    def test_duplicate_canonical_id_rejected(self):
        self.update("questions.json", lambda data: data["questions"].__setitem__(1, data["questions"][0]))
        with self.assertRaisesRegex(ValueError, "unique canonical"):
            integrity.check_year(self.root, 115)

    def test_altered_canonical_payload_rejected(self):
        self.update("questions.json", lambda data: data["questions"][0].__setitem__("question", "altered"))
        with self.assertRaisesRegex(ValueError, "JSON/SQLite mismatch"):
            integrity.check_year(self.root, 115)

    def test_sqlite_payload_hash_rejected(self):
        with sqlite3.connect(self.base / "question-bank.sqlite3") as db:
            db.execute("UPDATE questions SET payload_sha256=? WHERE question_id=(SELECT question_id FROM questions LIMIT 1)", ("0" * 64,))
        with self.assertRaisesRegex(ValueError, "payload SHA mismatch"):
            integrity.check_year(self.root, 115)

    def test_missing_manifest_id_rejected(self):
        self.update("webp-manifest.json", lambda data: data["items"].pop())
        with self.assertRaisesRegex(ValueError, "manifest IDs/count"):
            integrity.check_year(self.root, 115)

    def test_stale_inventory_digest_rejected(self):
        self.update("inventory.json", lambda data: data["sqlite"].__setitem__("dbSha256", "0" * 64))
        with self.assertRaisesRegex(ValueError, "inventory database SHA"):
            integrity.check_year(self.root, 115)


class FrozenWorkflowRouting(unittest.TestCase):
    def test_historic_jobs_bind_both_push_and_pr_to_original_branch(self):
        for key, branch in (("114-e11", "qa/role-a-114-e11-canonical-g2g3-20261107"),
                            ("115-mb21", "qa/role-a-115-mb21-canonical-g2g3-20261108")):
            with self.subTest(key=key):
                path = next((ROOT / ".github/workflows").glob(f"role-a-{key}-postcommit-*.yml"))
                text = path.read_text()
                condition = text.split("    if: >-\n", 1)[1].split("    runs-on:", 1)[0]
                self.assertIn(f"github.ref == 'refs/heads/{branch}'", condition)
                self.assertIn(f"github.head_ref == '{branch}'", condition)
                self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", condition)
                self.assertIn("github.event_name == 'push'", condition)
                self.assertIn("github.event_name == 'pull_request'", condition)
                # Historical narrow full-source tests remain in their original gate.
                self.assertIn(f"test_role_a_{key.replace('-', '_')}_source_", text)

    def test_qa_has_separate_current_payload_integrity_gate(self):
        text = (ROOT / ".github/workflows/qa-current-source-integrity-20261114.yml").read_text()
        self.assertIn("pull_request:\n    branches: [qa/114-115-official-visual-review]", text)
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("python scripts/qa_current_source_integrity_20261114.py", text)
        self.assertNotIn("--apply", text)
        self.assertNotIn("continue-on-error", text)


if __name__ == "__main__":
    unittest.main()
