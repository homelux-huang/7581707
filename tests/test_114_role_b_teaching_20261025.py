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
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

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
                    teach = json.loads(json.dumps(base["content"], ensure_ascii=False))
                    self.assertEqual(sha(teach), c["source"]["baseTeachingCanonicalSha256"])
                    # PR21's actual Git blob stays unchanged; apply a narrow authored
                    # reason-only patch to the effective candidate before digesting.
                    overrides = c.get("optionReasonOverrides") or {}
                    self.assertIsInstance(overrides, dict)
                    self.assertTrue(set(overrides).issubset(LETTERS))
                    for ch, reason in overrides.items():
                        self.assertIsInstance(reason, str)
                        self.assertGreater(len(reason.strip()), 20)
                        self.assertNotEqual(reason, teach["optionExplanations"][ch]["reason"])
                        teach["optionExplanations"][ch]["reason"] = reason
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

    def test_repaired_option_reasons_are_distinct_and_source_specific(self):
        # Distinct actual meanings, not different padding around generic wording.
        markers = {
            "114-00-E-08": {
                "A": "was named after", "B": "made fun of",
                "C": "was in charge of", "D": "stood out as",
            },
            "114-00-E-09": {
                "A": "actively", "B": "entirely",
                "C": "internally", "D": "obviously",
            },
            "114-00-C-03": {
                "A": "菜蔬稻稗", "B": "品類", "C": "群類", "D": "橐駝",
            },
        }
        for qid, required in markers.items():
            with self.subTest(qid=qid):
                c = load(BASE / (qid + ".json"))
                if c["kind"] == "PRESERVE_BASE_AND_ENRICH":
                    self.assertIsNone(c["teaching"])
                    reasons = c["optionReasonOverrides"]
                    self.assertEqual(set(reasons), LETTERS)
                else:
                    self.assertNotIn("optionReasonOverrides", c)
                    reasons = {ch: c["teaching"]["optionExplanations"][ch]["reason"]
                               for ch in LETTERS}
                self.assertEqual(len(set(reasons.values())), 4)
                for ch, source_anchor in required.items():
                    reason = reasons[ch]
                    self.assertGreater(len(reason.strip()), 20)
                    self.assertIn(source_anchor, reason)
                    self.assertNotIn(reason.strip(), ("詞義不同。", "類＝種類。",
                                                   "類＝相似。", "語意衝突。"))

    def test_regressions_reject_generic_and_duplicated_reasons(self):
        def specific(reasons):
            return (isinstance(reasons, dict) and set(reasons) == LETTERS
                    and len(set(reasons.values())) == 4
                    and all(isinstance(x, str) and len(x.strip()) > 20
                            for x in reasons.values()))
        self.assertFalse(specific(dict.fromkeys(LETTERS, "詞義不同。")))
        self.assertFalse(specific({"A": "菜蔬稻稗指種類", "B": "品類指種類",
                                   "C": "群類指種類", "D": "橐駝指相似"}))
        self.assertFalse(specific({"A": "同一句過長的泛稱理由不能同時用在所有四個選項",
                                   "B": "同一句過長的泛稱理由不能同時用在所有四個選項",
                                   "C": "不同的選項只是換了幾個字但語義仍有相同錯因",
                                   "D": "正解的推理需要指出原句所提供的語境線索和對應"}))
        for qid in ("114-00-E-08", "114-00-E-09", "114-00-C-03"):
            c = load(BASE / (qid + ".json"))
            actual = (c["optionReasonOverrides"] if c["kind"] == "PRESERVE_BASE_AND_ENRICH"
                      else {ch: c["teaching"]["optionExplanations"][ch]["reason"]
                            for ch in LETTERS})
            self.assertTrue(specific(actual), qid)

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
