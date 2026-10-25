"""Role B 114 drafts: strict content and digest check; never authorizes publishing."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-candidates/114-role-b-20261025"
DATA = ROOT / "sudu/data/processed/114"
LETTERS = {"A", "B", "C", "D"}
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))
def raw_sha(raw):
    return hashlib.sha256(raw).hexdigest()
def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
def sha(v):
    return raw_sha(canonical(v))
def revision(q, sha_webp):
    return sha({"question": q["question"], "options": q["options"], "singleQuestionWebpSha256": sha_webp})
def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()

class TestRoleB114Draft(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = load(BASE / "batch.json")
        cls.questions = {q["questionId"]: q for q in load(DATA / "questions.json")["questions"]}
        cls.manifest = {q["questionId"]: q for q in load(DATA / "webp-manifest.json")["items"]}

    def test_scope_and_status(self):
        b = self.batch
        self.assertEqual((b["total"], b["reusedOriginalLessons"], b["newDraftLessons"]), (7, 3, 4))
        self.assertEqual((b["newReady"], b["newLive"]), (0, 0))
        self.assertEqual(set(r["questionId"] for r in b["items"]), {
            "114-00-E-06", "114-00-E-07", "114-00-E-08", "114-00-E-09",
            "114-00-C-01", "114-00-C-02", "114-00-C-03"
        })

    def test_all_source_bound_and_all_options(self):
        for entry in self.batch["items"]:
            with self.subTest(qid=entry["questionId"]):
                path = ROOT / entry["path"]
                raw = path.read_bytes()
                self.assertEqual(raw_sha(raw), entry["fileSha256"])
                c = json.loads(raw)
                q, m = self.questions[c["questionId"]], self.manifest[c["questionId"]]
                self.assertEqual(c["answer"], q["answer"])
                self.assertEqual(m["qaStatus"], "PASS")
                self.assertEqual(m["sha256"], c["source"]["webpSha256"])
                self.assertEqual(m["output"], c["source"]["webpPath"])
                self.assertEqual(q["questionProvenance"]["webpSha256"], m["sha256"])
                self.assertEqual(q["questionProvenance"]["officialPdfSha256"], c["source"]["questionPdfSha256"])
                self.assertEqual(revision(q, m["sha256"]), c["source"]["questionRevision"])
                self.assertEqual(c["source"]["questionRevision"], entry["sourceRevision"])
                if c["kind"] == "PRESERVE_BASE_AND_ENRICH":
                    self.assertIsNone(c["teaching"])
                    base_path = ROOT / c["source"]["baseTeachingEvidencePath"]
                    base_bytes = base_path.read_bytes()
                    self.assertEqual(git_blob_sha(base_bytes), c["source"]["baseTeachingGitBlobSha"])
                    base = json.loads(base_bytes)
                    self.assertEqual(base["questionRevision"], c["source"]["questionRevision"])
                    teach = base["content"]
                    self.assertEqual(sha(teach), c["source"]["baseTeachingCanonicalSha256"])
                else:
                    self.assertIsNone(c["source"]["baseTeachingEvidencePath"])
                    teach = c["teaching"]
                    self.assertTrue(teach)
                for required in ("topic", "teacherSummary", "elementarySummary", "concept", "memory", "source"):
                    self.assertTrue(teach.get(required), (c["questionId"], required))
                self.assertEqual(set(teach["optionExplanations"]), LETTERS)
                correct = []
                for ch, item in teach["optionExplanations"].items():
                    for field in ("teacher", "elementary", "reason"):
                        self.assertGreater(len(item[field].strip()), 5)
                    if c["kind"] == "NEW_AUTHOR_DRAFT" and item["isCorrect"]:
                        correct.append(ch)
                if c["kind"] == "NEW_AUTHOR_DRAFT":
                    self.assertEqual(correct, [q["answer"]])
                self.assertIs(teach["hasExamCalculation"], False)
                self.assertIsNone(teach["examCalculation"])
                self.assertNotIn("本題無金額計算", json.dumps(teach, ensure_ascii=False))
                payload = {"questionId": c["questionId"], "sourceRevision": c["source"]["questionRevision"],
                           "webpSha256": m["sha256"], "teaching": teach, "enrichment": c["enrichment"]}
                self.assertEqual(sha(payload), c["composedTeachingSha256"])
                self.assertEqual(c["composedTeachingSha256"], entry["composedTeachingSha256"])
                self.assertEqual(c["review"]["status"], "BLOCKED")
                self.assertFalse(c["review"]["studentReleaseApproved"])
                self.assertFalse(c["review"]["humanTeacherVerified"])
                self.assertIsNone(c["review"]["independentReviewer"])
                self.assertIs(c["reasoningAudit"]["answerAlreadyKnown"], True)
                self.assertIs(c["reasoningAudit"]["blindSolveClaimedThisBatch"], False)

    def test_only_actual_source_forms_highlighted(self):
        for entry in self.batch["items"]:
            c = load(ROOT / entry["path"])
            q = self.questions[c["questionId"]]
            original = (q["question"] + " " + " ".join(q["options"])).casefold()
            for item in c["enrichment"]["highlights"]:
                self.assertTrue(item["bold"] and item["highlight"])
                self.assertIn(item["text"].casefold(), original)
                self.assertNotRegex(item["text"], r"<[^>]+>|javascript:|onerror\\s*=", "unsafe source markup")

    def test_english_news_and_phonetics(self):
        for entry in self.batch["items"]:
            c = load(ROOT / entry["path"])
            e = c["enrichment"]
            if c["subject"] == "英文":
                self.assertGreater(len(e["englishVocabulary"]), 0)
                for vocab in e["englishVocabulary"]:
                    self.assertIn(vocab["level"], ("初級", "中級", "高級"))
                    self.assertRegex(vocab["ipa"], r"^/.+/$")
                    self.assertTrue(vocab["synonyms"] and vocab["antonyms"] and vocab["usageNote"])
                    self.assertIn(vocab["headword"].casefold(), (self.questions[c["questionId"]]["question"] +
                        " ".join(self.questions[c["questionId"]]["options"])).casefold())
                    self.assertTrue(vocab["dictionaryUrl"].startswith("https://"))
                n = e["newsExample"]
                self.assertIn(n["highlightActualForm"], n["english"])
                self.assertTrue(n["chinese"] and n["notAnArticleQuote"])
                self.assertTrue(n["source"]["url"].startswith("https://"))
                self.assertGreaterEqual(date.fromisoformat(n["source"]["publicationDate"]), date(2023, 10, 25))
                self.assertLessEqual(date.fromisoformat(n["source"]["publicationDate"]), date(2026, 10, 25))
            else:
                self.assertGreater(len(e["chineseVocabulary"]), 0)
                for word in e["chineseVocabulary"]:
                    self.assertIn(word["level"], ("初級", "中級", "高級"))
                    self.assertTrue(word["term"] and word["meaning"])

if __name__ == "__main__":
    unittest.main()
