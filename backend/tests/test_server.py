"""Real HTTP, private persistence, scoring and scope-isolation checks with synthetic fixtures."""
import copy
import http.client
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sudu_private_server", ROOT / "backend/server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
backup_spec = importlib.util.spec_from_file_location("sudu_private_backup", ROOT / "backend/backup.py")
backup = importlib.util.module_from_spec(backup_spec)
backup_spec.loader.exec_module(backup)


class TestPrivateAdmin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved_root = server.ROOT
        server.ROOT = Path(self.tmp.name) / "repo"
        (server.ROOT / "sudu/data/years").mkdir(parents=True)
        for page in ("admin.html", "share.html"):
            shutil.copy2(ROOT / "sudu" / page, server.ROOT / "sudu" / page)
        self.one = {"id": "114-09-2-01", "year": 114, "paper": "09-2", "number": 1, "subject": "會計學", "question": "Synthetic fixture question one", "options": ["A", "B", "C", "D"], "answer": 1, "acceptedAnswers": [1, 3], "answerVerified": True, "questionVerified": True, "source": "https://web1.tcte.edu.tw/EXAM/114_4y/fixture.pdf"}
        self.two = {**self.one, "id": "114-09-2-02", "number": 2, "answer": 0, "acceptedAnswers": [0]}
        self.other = {**self.one, "id": "114-09-1-01", "paper": "09-1", "subject": "商業概論", "question": "OTHER PAPER PRIVATE CONTENT"}
        self.year = {"year": 114, "papers": [{"paper": "09-2", "expectedCount": 2, "questions": [self.one, self.two]}, {"paper": "09-1", "expectedCount": 1, "questions": [self.other]}]}
        self.rule = {"year": 114, "paper": "09-2", "expectedCount": 2, "verified": True, "type": "per-question", "version": "synthetic-test-v1", "points": {"1": 2.5, "2": 2.5}, "maxScore": 5, "sourceUrl": self.one["source"], "reviewedBy": "SYNTHETIC FIXTURE", "reviewedAt": "2026-10-18"}
        self.write_data()
        server.DB = Path(self.tmp.name) / "private.sqlite3"
        server.DEV, server.BOOTSTRAP, server.PUBLIC_BASE = True, "", ""
        server.FAILURES.clear()
        server.initialize()
        self.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.cookie, self.csrf = None, None

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        server.ROOT = self.saved_root
        server._year_questions.cache_clear()
        server.PUBLIC_BASE = ""
        self.tmp.cleanup()

    def write_data(self):
        (server.ROOT / "sudu/data/years/114.json").write_text(json.dumps(self.year))
        (server.ROOT / "sudu/data/scoring-rules.json").write_text(json.dumps({"rules": [self.rule]}))

    def request(self, path, data=None, headers=None, cookie=True):
        h = {"Content-Type": "application/json", **(headers or {})}
        if cookie and self.cookie:
            h["Cookie"] = self.cookie
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        conn.request("POST" if data is not None else "GET", path, json.dumps(data) if data is not None else None, h)
        response = conn.getresponse()
        body = response.read()
        if response.getheader("Set-Cookie"):
            self.cookie = response.getheader("Set-Cookie").split(";", 1)[0]
        result = json.loads(body) if body and "application/json" in response.getheader("Content-Type", "") else body.decode()
        code = response.status
        conn.close()
        return code, result

    def auth(self, change=True):
        code, result = self.request("/api/admin/login", {"username": "admin", "password": "admin"})
        self.assertEqual(code, 200)
        self.csrf = result["csrf"]
        if change:
            code, result = self.request("/api/admin/change-password", {"oldPassword": "admin", "newPassword": "private-test-password-123"}, {"X-CSRF-Token": self.csrf})
            self.assertEqual(code, 200)
            self.csrf = result["csrf"]

    def enroll(self):
        code, result = self.request("/api/students/enroll", {"nickname": "PRIVATE PERSON NAME"}, cookie=False)
        self.assertEqual(code, 201)
        return result["studentId"], result["accessToken"]

    def snapshot(self, first=3, second=0):
        return {"id": "fixture-submission-1", "year": "114", "paper": "09-2", "startedAt": "2026-10-18T01:00:00Z", "submittedAt": "2026-10-18T01:06:00Z", "elapsedMs": 360000, "questionCount": 2, "choices": {self.one["id"]: first, self.two["id"]: second}, "questionVersions": {q["id"]: server.fingerprint(q) for q in [self.one, self.two]}}

    def student_state(self):
        return {"attempts": {self.one["id"]: [{"choice": 2, "correct": True, "at": "2026-10-18T01:00:01Z"}, {"choice": 3, "correct": False, "at": "2026-10-18T01:01:01Z"}], self.two["id"]: [{"choice": 0, "correct": False, "at": "2026-10-18T01:04:01Z"}], self.other["id"]: [{"choice": 2, "correct": True, "at": "2026-10-18T03:00:01Z"}]}, "examSubmissions": {"114/09-2": self.snapshot()}, "password": "MUST NOT SYNC", "accessToken": "MUST NOT SYNC"}

    def sync(self, token, state=None):
        return self.request("/api/students/sync", {"state": self.student_state() if state is None else state}, {"Authorization": "Bearer " + token}, cookie=False)

    def test_password_hash_default_and_production_rejection(self):
        with server.connect() as db:
            account = db.execute("SELECT * FROM admins").fetchone()
        self.assertTrue(server.verify("admin", account["password"]))
        self.assertEqual(account["must_change"], 1)
        self.assertNotIn("admin", account["password"])
        server.DEV, server.BOOTSTRAP = False, "admin"
        with self.assertRaises(RuntimeError):
            server.initialize()
        server.DEV, server.BOOTSTRAP, server.PUBLIC_BASE = True, "", "https://public.example.org"
        with self.assertRaises(RuntimeError):
            server.initialize()

    def test_http_login_forced_change_session_rotation_and_logout(self):
        self.assertEqual(self.request("/api/admin/students", cookie=False)[0], 401)
        self.auth(change=False)
        old_cookie = self.cookie
        self.assertEqual(self.request("/api/admin/students")[0], 403)
        self.assertEqual(self.request("/api/admin/change-password", {"oldPassword": "admin", "newPassword": "private-test-password-123"})[0], 401)
        code, result = self.request("/api/admin/change-password", {"oldPassword": "admin", "newPassword": "private-test-password-123"}, {"X-CSRF-Token": self.csrf})
        self.assertEqual(code, 200)
        self.csrf = result["csrf"]
        self.assertNotEqual(old_cookie, self.cookie)
        self.assertEqual(self.request("/api/admin/me", headers={"Cookie": old_cookie}, cookie=False)[0], 401)
        self.assertEqual(self.request("/api/admin/students")[0], 200)
        self.assertEqual(self.request("/api/admin/logout", {}, {"X-CSRF-Token": self.csrf})[0], 200)
        self.assertEqual(self.request("/api/admin/students")[0], 401)

    def test_expired_session_and_login_rate_limit(self):
        self.auth()
        with server.connect() as db:
            db.execute("UPDATE sessions SET expires=0")
            db.commit()
        self.assertEqual(self.request("/api/admin/students")[0], 401)
        for _ in range(5):
            self.assertEqual(self.request("/api/admin/login", {"username": "admin", "password": "bad"})[0], 401)
        self.assertEqual(self.request("/api/admin/login", {"username": "admin", "password": "bad"})[0], 429)

    def test_cors_csrf_and_input_validation(self):
        self.assertEqual(self.request("/api/students/enroll", {}, {"Origin": "https://attacker.invalid"})[0], 403)
        self.assertEqual(self.request("/api/students/enroll", [1, 2, 3])[0], 400)
        self.assertEqual(self.request("/api/students/sync", {"state": {}}, {"Authorization": "Bearer not-a-token"})[0], 401)
        self.auth()
        self.assertEqual(self.request("/api/admin/logout", {}, {"X-CSRF-Token": "wrong"})[0], 401)
        self.assertEqual(self.request("/api/admin/students")[0], 200)

    def test_server_regrades_answers_never_trusts_client_correct(self):
        clean = server.clean_state(self.student_state())
        self.assertFalse(clean["attempts"][self.one["id"]][0]["correct"])
        self.assertTrue(clean["attempts"][self.one["id"]][1]["correct"], "official alternative accepted answer")
        self.assertNotIn("password", clean)
        self.assertNotIn("accessToken", clean)
        unknown = server.clean_state({"attempts": {"unknown": [{"choice": 0, "correct": True}]}})
        self.assertIsNone(unknown["attempts"]["unknown"][0]["correct"])
        self.assertIsNone(unknown["attempts"]["unknown"][0]["at"])

    def test_snapshot_scoring_multiple_accepted_answers_and_version_change(self):
        entry = self.snapshot()
        self.assertEqual(server.official_score("114/09-2", entry)["score"], 5)
        entry["choices"][self.one["id"]] = 2
        self.assertEqual(server.official_score("114/09-2", entry)["score"], 2.5)
        del entry["questionVersions"]
        self.assertIsNone(server.official_score("114/09-2", entry))
        entry = self.snapshot()
        self.one["question"] = "Changed official question source"
        self.write_data()
        self.assertIsNone(server.official_score("114/09-2", entry))

    def test_partial_or_manual_papers_never_claim_full_score(self):
        self.rule["manualSections"] = [{"id": "essay", "maxScore": 5}]
        self.rule["maxScore"] = 10
        self.write_data()
        result = server.official_score_details("114/09-2", self.snapshot())
        self.assertEqual(result["status"], "pending-marking")
        self.assertIsNone(result["score"])
        self.assertEqual(result["objectiveScore"], 5)
        self.assertEqual(result["maxScore"], 10)
        entry = self.snapshot()
        del entry["choices"][self.two["id"]]
        self.assertIsNone(server.clean_submission("114/09-2", entry))

    def test_http_sync_append_only_preserves_first_error_and_submissions(self):
        sid, token = self.enroll()
        self.assertEqual(self.sync(token)[0], 200)
        changed = self.student_state()
        changed["attempts"] = {}
        changed["examSubmissions"]["114/09-2"]["choices"][self.one["id"]] = 2
        self.assertEqual(self.sync(token, changed)[0], 200)
        with server.connect() as db:
            row = db.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
            state = json.loads(row["state_json"])
        self.assertEqual(len(state["attempts"][self.one["id"]]), 2)
        self.assertFalse(state["attempts"][self.one["id"]][0]["correct"])
        self.assertEqual(state["examSubmissions"]["114/09-2"]["choices"][self.one["id"]], 3)
        self.assertNotEqual(row["token_hash"], token)
        second = self.snapshot()
        second.update(id="fixture-submission-2", submittedAt="2026-10-18T01:10:00Z", elapsedMs=600000)
        self.assertEqual(self.sync(token, {"examSubmissionHistory": {"114/09-2": [second]}})[0], 200)
        with server.connect() as db:
            state = json.loads(db.execute("SELECT state_json FROM students WHERE id=?", (sid,)).fetchone()[0])
        self.assertEqual(len(state["examSubmissionHistory"]["114/09-2"]), 1)

    def test_unknown_legacy_time_is_na(self):
        entry = self.snapshot()
        entry.pop("startedAt")
        entry.pop("elapsedMs")
        clean = server.clean_submission("114/09-2", entry)
        self.assertIsNone(clean["startedAt"])
        self.assertIsNone(clean["elapsedMs"])
        self.assertIsNone(clean["activeMs"])

    def test_share_scope_filters_questions_counters_dates_identity_and_scores(self):
        sid, token = self.enroll()
        self.sync(token)
        self.auth()
        code, share = self.request("/api/admin/share", {"studentId": sid, "paper": "114/09-2"}, {"X-CSRF-Token": self.csrf})
        self.assertEqual(code, 201)
        code, report = self.request("/api/share/" + share["token"], cookie=False)
        self.assertEqual(code, 200)
        raw = json.dumps(report)
        for forbidden in [self.other["id"], "OTHER PAPER PRIVATE CONTENT", "PRIVATE PERSON NAME", sid, "03:00:01"]:
            self.assertNotIn(forbidden, raw)
        self.assertEqual(report["report"]["answeredQuestions"], 2)
        self.assertEqual(report["report"]["firstWrongCount"], 1)
        self.assertEqual(report["report"]["wrongEventCount"], 1)
        self.assertNotIn("id", report["report"])
        self.assertEqual(report["report"]["scores"][0]["score"], 5)
        self.assertEqual(self.request("/api/admin/share", {"studentId": sid, "paper": "115/09-2"}, {"X-CSRF-Token": self.csrf})[0], 400)
        self.assertEqual(self.request("/api/admin/revoke-share", {"studentId": sid, "shareId": share["shareId"]}, {"X-CSRF-Token": self.csrf})[0], 200)
        self.assertEqual(self.request("/api/share/" + share["token"], cookie=False)[0], 404)

    def test_share_expiry_and_student_revocation_or_deletion(self):
        sid, token = self.enroll()
        self.sync(token)
        self.auth()
        _, share = self.request("/api/admin/share", {"studentId": sid, "paper": "114/09-2"}, {"X-CSRF-Token": self.csrf})
        with server.connect() as db:
            db.execute("UPDATE shares SET expires=0")
            db.commit()
        self.assertEqual(self.request("/api/share/" + share["token"], cookie=False)[0], 404)
        self.assertEqual(self.request("/api/students/revoke", {}, {"Authorization": "Bearer " + token}, cookie=False)[0], 200)
        self.assertEqual(self.sync(token)[0], 401)
        self.assertEqual(self.request("/api/share/" + share["token"], cookie=False)[0], 404)
        sid2, token2 = self.enroll()
        self.sync(token2)
        self.assertEqual(self.request("/api/students/delete", {}, {"Authorization": "Bearer " + token2}, cookie=False)[0], 200)
        self.assertEqual(self.sync(token2)[0], 401)
        with server.connect() as db:
            self.assertIsNone(db.execute("SELECT 1 FROM students WHERE id=?", (sid2,)).fetchone())

    def test_admin_adjustment_preserves_official_score_and_audit(self):
        sid, token = self.enroll()
        self.sync(token)
        self.auth()
        change = {"studentId": sid, "paper": "114/09-2", "score": 4, "reason": "測試人工調整分數原因", "source": "https://web1.tcte.edu.tw/EXAM/114_4y/fixture.pdf"}
        self.assertEqual(self.request("/api/admin/adjust", {**change, "source": ""}, {"X-CSRF-Token": self.csrf})[0], 400)
        self.assertEqual(self.request("/api/admin/adjust", change, {"X-CSRF-Token": self.csrf})[0], 200)
        _, data = self.request("/api/admin/student?id=" + sid)
        self.assertEqual(data["student"]["scores"][0]["score"], 5)
        self.assertEqual(data["student"]["scores"][0]["adjustedScore"], 4)
        self.assertEqual(data["student"]["adjustments"][0]["old_score"], 5)
        self.assertEqual(data["student"]["adjustments"][0]["rule_version"], "synthetic-test-v1")
        self.assertEqual(self.request("/api/admin/adjust", {**change, "score": 6}, {"X-CSRF-Token": self.csrf})[0], 400)

    def test_browser_and_server_fingerprints_match_unicode_and_source_changes(self):
        question = {**self.one, "question": "中文與 x² − 5，完整來源 🧾", "sourceChangePending": {"role": "question", "newPdfSha256": "fixture-sha"}, "questionPresentation": "original_image_required"}
        code = "const S=require('./sudu/exam_scoring.js');console.log(S.fingerprint(JSON.parse(process.argv[1])))"
        result = subprocess.run(["node", "-e", code, json.dumps(question, ensure_ascii=False)], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertEqual(server.fingerprint(question), result.stdout.strip())

    def test_schema_upgrade_backs_up_before_additive_migration(self):
        sid, _ = self.enroll()
        with server.connect() as db:
            db.executescript("ALTER TABLE adjustments RENAME TO adjustments_new; CREATE TABLE adjustments AS SELECT id,student_id,paper_key,old_score,new_score,reason,source,created,admin FROM adjustments_new; DROP TABLE adjustments_new;")
            db.commit()
        server.initialize()
        copies = list(server.DB.parent.glob("private-before-schema2-*.sqlite3"))
        self.assertEqual(len(copies), 1)
        with server.sqlite3.connect(copies[0]) as old:
            self.assertEqual(old.execute("SELECT id FROM students").fetchone()[0], sid)
            self.assertNotIn("submission_id", {row[1] for row in old.execute("PRAGMA table_info(adjustments)")})
        server.initialize()
        self.assertEqual(len(list(server.DB.parent.glob("private-before-schema2-*.sqlite3"))), 1)

    def test_unverified_historical_wrong_choice_is_preserved_as_pending(self):
        self.one["questionVerified"] = False
        self.write_data()
        sid, token = self.enroll()
        state = {"attempts": {self.one["id"]: [{"choice": 2, "correct": False, "at": "2026-10-18T01:00:00Z"}]}}
        self.assertEqual(self.sync(token, state)[0], 200)
        with server.connect() as db:
            student = db.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
            report = server.summarize(student, db, True)
        self.assertEqual(report["firstWrongCount"], 1)
        self.assertEqual(report["verifiedWrongQuestionCount"], 0)
        self.assertEqual(report["wrongEventCount"], 0)
        self.assertEqual(report["firstWrong"][0]["reportedWrongCount"], 1)
        self.assertEqual(report["firstWrong"][0]["gradingStatus"], "pending-verification")

    def test_review_only_history_and_source_changes_preserve_pending_errors(self):
        sid, token = self.enroll()
        state = {"reviewHistory": {self.one["id"]: [{"choice": 2, "correct": True, "at": "2026-10-18T01:00:00Z"}]}}
        self.assertEqual(self.sync(token, state)[0], 200)
        with server.connect() as db:
            student = db.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
            original = student["state_json"]
            report = server.summarize(student, db, True)
            self.assertEqual(report["answeredQuestions"], 1)
            self.assertEqual(report["wrongEventCount"], 1)
            self.one["question"] = "Official source changed after the historical answer"
            self.one["questionVerified"] = False
            self.write_data()
            report = server.summarize(student, db, True)
            self.assertEqual(report["firstWrongCount"], 1)
            self.assertEqual(report["wrongEventCount"], 0)
            self.assertEqual(report["pendingGradingEvents"], 1)
            self.assertEqual(report["firstWrong"][0]["reportedWrongCount"], 1)
            self.assertEqual(db.execute("SELECT state_json FROM students WHERE id=?", (sid,)).fetchone()[0], original)
        self.auth()
        code, share = self.request("/api/admin/share", {"studentId": sid, "paper": "114/09-2"}, {"X-CSRF-Token": self.csrf})
        self.assertEqual(code, 201)
        self.assertEqual(self.request("/api/share/" + share["token"], cookie=False)[1]["report"]["firstWrongCount"], 1)

    def test_multiple_choice_event_history_is_preserved_and_server_validated(self):
        self.one["questionType"] = "multiple-choice"
        self.write_data()
        state = {"attempts": {self.one["id"]: [{"choice": [3, 1], "correct": False}, {"choice": [1], "correct": True}, {"choice": [1, 1], "correct": True}]}}
        cleaned = server.clean_state(state)["attempts"][self.one["id"]]
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned[0]["choice"], [3, 1])
        self.assertTrue(cleaned[0]["correct"])
        self.assertFalse(cleaned[1]["correct"])
        snapshot = self.snapshot()
        self.assertIsNone(server.clean_submission("114/09-2", snapshot), "multiple-choice snapshot cannot use a scalar choice")
        snapshot["choices"][self.one["id"]] = [1, 3]
        self.assertIsNotNone(server.clean_submission("114/09-2", snapshot))

    def test_verified_private_backup_and_restore(self):
        sid, token = self.enroll()
        self.sync(token)
        saved = Path(self.tmp.name) / "private-backups/backup.sqlite3"
        restored = Path(self.tmp.name) / "private-backups/restored.sqlite3"
        checksum = backup.backup_database(server.DB, saved)
        self.assertEqual(backup.verify_database(saved), checksum)
        backup.restore_database(saved, restored)
        self.assertEqual(backup.verify_database(restored), checksum)
        self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError):
            backup.restore_database(saved, restored)
        with server.sqlite3.connect(restored) as db:
            self.assertEqual(db.execute("SELECT id FROM students").fetchone()[0], sid)
        Path(str(saved) + ".sha256").write_text("incorrect")
        with self.assertRaises(ValueError):
            backup.restore_database(saved, Path(self.tmp.name) / "bad.sqlite3")


if __name__ == "__main__":
    unittest.main()
