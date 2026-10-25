"""Issue36 Role C exact-source teaching reuse verification; NEVER release gates."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-candidates/115-role-c-loop-20261025"
EXPECTED = {"115-00-E-03": "B", "115-09-2-34": "A"}

def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical_digest(value):
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")).encode("utf-8"))

def source_payload(q):
    return {"question": q["question"], "options": q["options"],
            "singleQuestionWebpSha256": q["imageSha256"]}

class RoleCLoopBatch01(unittest.TestCase):
    def test_exact_two_and_all_checks(self):
        batch = json.loads((BASE / "batch.json").read_text(encoding="utf-8"))
        self.assertEqual(batch["taskId"], "C-115-REUSE-E03-ECON34-20261025-01")
        self.assertEqual(batch["claimedAtUtc"], "2026-10-25T04:48:47Z")
        self.assertEqual({i["questionId"] for i in batch["items"]}, set(EXPECTED))
        self.assertEqual((batch["newReady"], batch["newLive"]), (0, 0))
        for item in batch["items"]:
            raw = (ROOT / item["path"]).read_bytes()
            self.assertEqual(sha_bytes(raw), item["fileSha256"])
            q = json.loads(raw)
            t = q["teaching"]
            self.assertEqual(q["questionId"], item["questionId"])
            self.assertEqual(q["imageSha256"], item["imageSha256"])
            self.assertEqual(q["sourceTextRevision"], item["sourceTextRevision"])
            self.assertEqual(canonical_digest(source_payload(q)), q["sourceTextRevision"])
            self.assertEqual(canonical_digest(t), item["teachingSha256"])
            self.assertEqual(q["teachingCanonicalSha256"], item["teachingSha256"])
            self.assertEqual(q["answerCandidate"], EXPECTED[q["questionId"]])
            self.assertEqual(len(q["options"]), 4)
            self.assertEqual(set(t["optionExplanations"]), set("ABCD"))
            self.assertEqual([k for k in "ABCD" if t["optionExplanations"][k]["isCorrect"]],
                             [q["answerCandidate"]])
            for k in "ABCD":
                v = t["optionExplanations"][k]
                for fld in ("teacher", "elementary", "reason"):
                    self.assertGreaterEqual(len(v[fld].strip()), 8)
            for fld in ("teacherSummary", "elementarySummary", "memory", "concept", "highlightTerms"):
                self.assertTrue(t[fld])
            self.assertFalse(t["hasExamCalculation"])
            self.assertIsNone(t["examCalculation"])
            self.assertFalse(q["sourceQuestionVerified"])
            self.assertFalse(q["sourceAnswerVerified"])
            self.assertFalse(q["studentReleaseApproved"])
            self.assertFalse(q["deploy"])
            self.assertFalse(item["ready"])
            self.assertTrue(q["legacyTeaching"]["unchangedTeachingJson"])
            self.assertTrue(q["legacyTeaching"]["oldClaimsOfTeacherOrAnswerApprovalNotRevalidated"])
            self.assertEqual(q["review"]["authorizedHumanTeacherApproval"], "PENDING")
            self.assertEqual(q["review"]["externalIndependentReview"], "PENDING")
            self.assertEqual(q["review"]["officialFinalAdmission"], "PENDING")
            self.assertEqual(q["review"]["uiQa"], "PENDING")
            self.assertFalse(q["review"]["newBlindSolveClaimed"])

    def test_changed_question_options_webp_or_teaching_invalidates_sha(self):
        for qid in EXPECTED:
            q = json.loads((BASE / (qid + ".json")).read_text(encoding="utf-8"))
            payload = source_payload(q)
            baseline = canonical_digest(payload)
            mutated = copy.deepcopy(payload)
            mutated["question"] += " X"
            self.assertNotEqual(canonical_digest(mutated), baseline)
            mutated = copy.deepcopy(payload)
            mutated["options"][0] += " X"
            self.assertNotEqual(canonical_digest(mutated), baseline)
            mutated = copy.deepcopy(payload)
            mutated["singleQuestionWebpSha256"] = "0" * 64
            self.assertNotEqual(canonical_digest(mutated), baseline)
            altered_lesson = copy.deepcopy(q["teaching"])
            altered_lesson["memory"] += " X"
            self.assertNotEqual(canonical_digest(altered_lesson), q["teachingCanonicalSha256"])

    def test_e03_ipa_levels_word_and_un_news_true_attribution(self):
        q = json.loads((BASE / "115-00-E-03.json").read_text(encoding="utf-8"))
        e = q["teaching"]["english"]
        self.assertEqual(e["answerWord"], "equally")
        self.assertEqual(e["pronunciationIPA"], "/ˈiː.kwə.li/")
        self.assertTrue(set(("初級", "中級", "高級")).issubset(e["synonyms"]))
        self.assertTrue(set(("初級", "中級", "高級")).issubset(e["antonyms"]))
        self.assertIn(e["newsExampleHighlightedSurfaceForm"], e["newsExampleEnglish"])
        self.assertIn("非來源逐字引述", e["newsExampleKind"])
        self.assertEqual(e["newsExampleSourceDate"], "2026-09-17")
        self.assertTrue(e["newsExampleSourceUrl"].startswith("https://www.un.org/"))

    def test_econ34_four_distinct_rationales_and_no_math_card(self):
        q = json.loads((BASE / "115-09-2-34.json").read_text(encoding="utf-8"))
        t = q["teaching"]
        self.assertIn("跟跌不跟漲", t["teacherSummary"])
        self.assertIn("膨脹缺口", t["optionExplanations"]["B"]["teacher"])
        self.assertTrue(len(t["stepByStep"]["steps"]) >= 5)
        self.assertIsNone(t["examCalculation"])

if __name__ == "__main__":
    unittest.main()
