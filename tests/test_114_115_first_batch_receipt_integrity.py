"""Independent machine checks of first-batch receipts. NEVER authorizes new students."""
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ["114-00-E-07", "114-00-E-08", "114-00-E-09",
            "115-00-MB-20", "115-00-MB-21", "115-00-MB-22",
            "115-00-MB-23", "115-00-MB-24", "115-00-MB-25",
            "115-09-2-34"]
LEGACY = [f"115-00-MB-{n:02d}" for n in (2, 3, 4, 5, 9)]
ALL_ASSETS = PRIORITY + LEGACY

def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class CandidateIntegrityOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = {}
        cls.asset = {}
        cls.banks = {}
        for year in (114, 115):
            base = f"sudu/data/processed/{year}"
            data = read_json(f"{base}/questions.json")
            manifest = read_json(f"{base}/webp-manifest.json")
            cls.banks[year] = data
            cls.q.update({q["questionId"]: q for q in data["questions"]})
            cls.asset.update({a["questionId"]: a for a in manifest["items"]})
            assert len(data["questions"]) == len(manifest["items"]) == 205
            assert len({q["questionId"] for q in data["questions"]}) == 205
            assert len({a["questionId"] for a in manifest["items"]}) == 205

    def test_410_candidate_ids_not_officially_certified_by_this_test(self):
        self.assertEqual(len(self.q), 410)
        self.assertEqual(len(self.asset), 410)
        self.assertEqual(set(self.q), set(self.asset))
        for year in (114, 115):
            ids = {k for k in self.q if k.startswith(str(year) + "-")}
            self.assertEqual(len(ids), 205)

    def test_real_webp_file_bytes_and_sha_of_priority_and_legacy(self):
        self.assertEqual(len(ALL_ASSETS), 15)
        for id_ in ALL_ASSETS:
            with self.subTest(qid=id_):
                asset = self.asset[id_]
                self.assertEqual(asset["qaStatus"], "PASS")
                path = ROOT / asset["output"]
                self.assertTrue(path.is_file(), id_)
                raw = path.read_bytes()
                self.assertTrue(raw.startswith(b"RIFF"), id_)
                self.assertEqual(raw[8:12], b"WEBP", id_)
                self.assertEqual(sha256(path), asset["sha256"], id_)
                q = self.q[id_]
                self.assertEqual(q["paperCode"], id_.split("-")[1] + "-" + id_.split("-")[2])
                claims = q.get("questionProvenance") or {}
                claimed = claims.get("webpSha256") or (q.get("assets") or {}).get("sha256")
                self.assertEqual(claimed, asset["sha256"])

    def test_114_c19_stale_provenance_is_explicitly_blocked_not_ignored(self):
        id_ = "114-00-C-19"
        q, image = self.q[id_], self.asset[id_]
        self.assertEqual((q.get("assets") or {}).get("sha256"), image["sha256"])
        self.assertNotEqual(q["questionProvenance"]["webpSha256"], image["sha256"])
        self.assertFalse(q["answerVerified"])
        self.assertFalse(q["questionVerified"])

    def test_205_sqlite_rows_each_with_readonly_integrity_check(self):
        for year in (114, 115):
            with self.subTest(year=year):
                path = ROOT / f"sudu/data/processed/{year}/question-bank.sqlite3"
                self.assertTrue(path.is_file())
                con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
                try:
                    self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                    self.assertEqual(con.execute("SELECT COUNT(*) FROM questions").fetchone()[0], 205)
                    db_ids = {r[0] for r in con.execute("SELECT question_id FROM questions")}
                    corpus_ids = {q["questionId"] for q in self.banks[year]["questions"]}
                    self.assertEqual(db_ids, corpus_ids)
                finally:
                    con.close()

    def test_teacher_gate_nonempty_impossible_with_current_policy(self):
        policy = read_json("sudu/release-governance/independent-review-policy.json")
        self.assertIs(policy["requireHumanTeacher"], True)
        self.assertEqual(policy["authorizedReviewers"], {})
        self.assertEqual(len(policy["legacyAlreadyPublished"]), 5)
        existing = read_json("sudu/data/approved/115.json")
        self.assertEqual(existing["approvedCount"], 5)
        self.assertEqual({q["canonicalId"] for q in existing["questions"]}, set(LEGACY))
        self.assertEqual(read_json("sudu/data/approved/114.json")["approvedCount"], 0)
        for public in existing["questions"]:
            self.assertEqual(public["imageSha256"],
                             policy["legacyAlreadyPublished"][public["canonicalId"]]["webpSha256"])

    def test_new_content_received_as_candidates_not_granted(self):
        for folder, expected in (("114-role-b-20261025", 7),
                                 ("114-115-20261025", 6)):
            root = ROOT / "sudu/teaching-candidates" / folder
            manifest = read_json(str(root.relative_to(ROOT) / "batch.json"))
            self.assertEqual(len(manifest["items"]), expected)
            for item in manifest["items"]:
                with self.subTest(questionId=item["questionId"]):
                    path = ROOT / item["path"]
                    self.assertEqual(sha256(path), item["fileSha256"])
                    doc = json.loads(path.read_text(encoding="utf-8"))
                    self.assertIn(item["questionId"], self.q)
                    self.assertEqual(doc["questionId"], item["questionId"])
                    if folder.startswith("114-"):
                        self.assertFalse(doc["review"]["humanTeacherVerified"])
                        self.assertFalse(doc["review"]["studentReleaseApproved"])
                    else:
                        self.assertFalse(doc["studentReleaseApproved"])
                        self.assertEqual(doc["review"]["externalIndependentReview"], "PENDING")

    def test_mb23_original_table_is_present_but_not_teacher_approved(self):
        q = self.q["115-00-MB-23"]
        table = q.get("originalSourceTableCandidate")
        self.assertIsInstance(table, dict)
        self.assertEqual(len(table["heading"]), 3)
        self.assertEqual(len(table["rows"]), 2)
        self.assertTrue(all(len(row) == 3 for row in table["rows"]))
        draft = read_json("sudu/teaching-candidates/114-115-20261025/115-00-MB-23.json")
        self.assertEqual(draft["sourceTables"], [table])
        self.assertIs(draft["review"]["hasRequiredSourceTable"], True)
        self.assertIs(draft["review"]["formalIndependentTableQa"], False)
        self.assertEqual(draft["originalSourceTableCandidate"], table)
        self.assertNotEqual(draft["sourceTextRevisionWithTable"], draft["sourceTextRevisionWithoutTable"])
        self.assertIs(draft["review"]["sourceRevisionAccepted"], False)
        self.assertFalse(q["questionVerified"])
        self.assertFalse(draft["studentReleaseApproved"])

    def test_econ34_is_image_candidate_only(self):
        q = self.q["115-09-2-34"]
        self.assertFalse(q["answerVerified"])
        self.assertFalse(q["questionVerified"])
        self.assertEqual(self.asset[q["questionId"]]["qaStatus"], "PASS")
        self.assertFalse(
            (ROOT / "sudu/teaching-candidates/114-115-20261025/115-09-2-34.json").exists()
        )

if __name__ == "__main__":
    unittest.main()
