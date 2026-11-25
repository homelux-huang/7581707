import json
from pathlib import Path
import tempfile
import unittest

from scripts import sudu_pages_evidence as evidence
from scripts import sudu_independent_review_gate as gate


class PagesOutputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.site = Path(temporary.name)
        self.target = "a" * 40
        self.code = "b" * 40
        self.write("sudu/verified-questions-runtime.js", "runtime")
        self.write("sudu/data/approved/progress.json", "{}")
        self.write(evidence.MARKER, self.marker(self.code))
        self.stage = {"codeCommit": self.code, "siteFiles": evidence.inventory(self.site)}
        self.write(evidence.MARKER, self.marker(self.target))

    @staticmethod
    def marker(commit):
        return json.dumps({"commit": commit, "testsRequired": True}) + "\n"

    def write(self, rel, content):
        path = self.site / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_full_inventory_and_distinct_release_marker(self):
        evidence.verify_output(self.site, self.stage, self.target)
        with self.assertRaisesRegex(ValueError, "Release marker"):
            evidence.verify_output(self.site, self.stage, self.code)

    def test_non_payload_mismatch_and_missing_file_stop_pages(self):
        progress = "sudu/data/approved/progress.json"
        path = self.write(progress, '{"approvedCount": 2}')
        with self.assertRaisesRegex(ValueError, progress):
            evidence.verify_output(self.site, self.stage, self.target)
        path.unlink()
        with self.assertRaisesRegex(ValueError, progress):
            evidence.verify_output(self.site, self.stage, self.target)

    def test_missing_original_manifest_or_inventory_is_rejected(self):
        keys = ("codeCommit", "codeBindings", "payloadSha256", "rowSha256", "authorizationSha256")
        stage = dict.fromkeys(keys, self.code)
        stage.update(status="PRE_G8_ONLY", pagesEligible=False)
        raw = json.dumps(stage)
        entry = dict(stage, stageManifestSha256=evidence.digest(raw.encode()))
        with self.assertRaises(KeyError):
            evidence.original_stage({}, entry)
        with self.assertRaisesRegex(ValueError, "Missing formal G8 public file inventory"):
            evidence.original_stage({"stageManifest": raw}, entry)

    def test_historical_five_remain_eligible_and_new_row_needs_receipt(self):
        self.write("sudu/data/approved/114.json", '{"approvedCount":0,"questions":[]}')
        self.write("sudu/data/approved/115.json", json.dumps({
            "approvedCount": 5, "questions": [{"canonicalId": qid} for qid in sorted(gate.LEGACY_FIVE_IDS)]
        }))
        evidence.verify_deployment(self.site, self.target, {}, self.fail)
        self.write("sudu/data/approved/114.json",
                   '{"approvedCount":1,"questions":[{"canonicalId":"114-00-E-11"}]}')
        with self.assertRaisesRegex(ValueError, "Missing protected G8 receipt"):
            evidence.verify_deployment(self.site, self.target, {}, self.fail)
