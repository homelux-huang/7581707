"""Role C: Issue #36 new five authored lessons, fail-closed draft-only checks."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-candidates/115-role-c-loop-batch02-20261025"
EXPECTED = {
    "115-00-C-06": "B",
    "115-00-E-29": "A",
    "115-00-E-39": "B",
    "115-00-E-40": "D",
    "115-00-E-41": "D",
}
SHARED = {
    "115-00-E-29": "e932d3fc246b55604cabd6fa1716d0fa6f8f67d658ed6a16c6d88f91bfdb49b6",
    "115-00-E-39": "5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b",
    "115-00-E-40": "5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b",
    "115-00-E-41": "5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b",
}

def checksum(v):
    return hashlib.sha256(v).hexdigest()

def canonical(v):
    return checksum(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))

class TestRoleCFive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = json.loads((BASE / "batch.json").read_text(encoding="utf-8"))
        cls.lessons = {}
        cls.items = {}
        for item in cls.batch["items"]:
            cls.items[item["questionId"]] = item
            cls.lessons[item["questionId"]] = json.loads((ROOT / item["path"]).read_text(encoding="utf-8"))

    def test_exact_original_question_ids_and_pr_isolation(self):
        b = self.batch
        self.assertEqual(b["taskId"], "C-115-NEW-FIVE-20261025-02")
        self.assertEqual(b["claimedAtUtc"], "2026-10-25T04:54:20Z")
        self.assertEqual(set(self.items), set(EXPECTED))
        self.assertEqual(b["baseSHA"], "3356e53c94c1ac0aae9f5aeb2b325b66698bf8a5")
        self.assertEqual((b["newReady"], b["newLive"]), (0, 0))

    def test_source_and_teaching_sha_content_structures(self):
        for qid, q in self.lessons.items():
            item = self.items[qid]
            with self.subTest(qid=qid):
                raw = (ROOT / item["path"]).read_bytes()
                self.assertEqual(checksum(raw), item["fileSha256"])
                self.assertEqual(q["questionId"], qid)
                self.assertEqual(q["sourceTextRevision"], item["sourceTextRevision"])
                self.assertEqual(q["teachingCanonicalSha256"], item["teachingSha256"])
                self.assertEqual(q["imageSha256"], item["imageSha256"])
                source = {"question": q["question"], "options": q["options"],
                          "singleQuestionWebpSha256": q["imageSha256"]}
                self.assertEqual(canonical(source), item["sourceTextRevision"])
                self.assertEqual(canonical(q["teaching"]), item["teachingSha256"])
                self.assertEqual(q["answerCandidate"], EXPECTED[qid])
                self.assertEqual(len(q["options"]), 4)
                self.assertEqual(set(q["teaching"]["optionExplanations"]), set("ABCD"))
                self.assertEqual([c for c in "ABCD" if q["teaching"]["optionExplanations"][c]["isCorrect"]], [EXPECTED[qid]])
                for c in "ABCD":
                    entry = q["teaching"]["optionExplanations"][c]
                    for fld in ("teacher", "elementary", "reason"):
                        self.assertGreaterEqual(len(entry[fld]), 15, (qid, c, fld))
                for fld in ("teacherSummary", "elementarySummary", "concept", "memory", "highlights", "stepByStep"):
                    self.assertTrue(q["teaching"][fld], (qid, fld))
                self.assertFalse(q["teaching"]["hasExamCalculation"])
                self.assertIsNone(q["teaching"]["examCalculation"])
                self.assertFalse(q["studentReleaseApproved"])
                self.assertFalse(q["deploy"])
                self.assertFalse(item["ready"])
                self.assertFalse(q["sourceFormalAdmissionThisBatch"]) if qid == "115-00-C-06" else self.assertFalse(q["sourceAnswerVerified"])
                self.assertFalse(q["review"]["newBlindSolveClaimed"])
                self.assertIn("AUTHORIZED_DISTINCT_HUMAN_TEACHER_REVIEW", " ".join(q["blockers"]))

    def test_shared_visual_qa_is_never_promoted(self):
        for qid, q in self.lessons.items():
            if qid in SHARED:
                with self.subTest(qid=qid):
                    s = q["sharedMaterial"]
                    self.assertEqual(s["sha256"], SHARED[qid])
                    self.assertEqual(self.items[qid]["sharedImageSha256"], s["sha256"])
                    self.assertEqual(s["qaStatus"], "PENDING_INDIVIDUAL_VISUAL_QA")
                    self.assertEqual(q["review"]["sharedMaterialIndependentVisualQa"], "PENDING")
                    self.assertIn("SHARED_MATERIAL_INDEPENDENT_VISUAL_QA_PENDING", q["blockers"])
            else:
                self.assertIsNone(q["sharedMaterialId"])
                self.assertIsNone(self.items[qid]["sharedImageSha256"])

    def test_english_news_ipa_graded_language_and_actual_surface(self):
        for qid, q in self.lessons.items():
            if qid == "115-00-C-06":
                self.assertEqual(set(q["teaching"]["chineseLevelVocabulary"]), {"初級", "中級", "高級"})
                self.assertTrue(q["upstreamAnswerVerifiedFlag"])
                self.assertFalse(q["upstreamQuestionVerifiedFlag"])
                continue
            with self.subTest(qid=qid):
                t = q["teaching"]
                e = t["english"]
                self.assertTrue(e["pronunciationIPA"].startswith("/"))
                for k in ("synonyms", "antonyms"):
                    self.assertEqual(set(e[k]), {"初級", "中級", "高級"})
                    self.assertTrue(all(e[k][d] for d in ("初級", "中級", "高級")))
                marker = e["newsExampleHighlightedSurfaceForm"]
                self.assertIn("**" + marker + "**", e["newsExampleEnglish"])
                self.assertIn("非來源逐字引述", e["newsExampleKind"])
                self.assertGreater(len(e["newsExampleChinese"]), 15)
                self.assertIn(e["newsExampleSourceDate"][:4], ("2025", "2026"))
                self.assertTrue(e["newsExampleSourceUrl"].startswith("https://"))
                self.assertFalse(q["sourceAnswerVerified"])
                self.assertFalse(q["sourceQuestionVerified"])

    def test_revision_and_lesson_tampering_rejected(self):
        for qid, q in self.lessons.items():
            original = {"question": q["question"], "options": q["options"],
                        "singleQuestionWebpSha256": q["imageSha256"]}
            for mode in ("question", "options", "image"):
                with self.subTest(qid=qid, mode=mode):
                    p = copy.deepcopy(original)
                    if mode == "question":
                        p["question"] += " changed"
                    elif mode == "options":
                        p["options"][0] += " changed"
                    else:
                        p["singleQuestionWebpSha256"] = "0" * 64
                    self.assertNotEqual(canonical(p), q["sourceTextRevision"])
            t = copy.deepcopy(q["teaching"])
            t["memory"] += " changed"
            self.assertNotEqual(canonical(t), q["teachingCanonicalSha256"])

    def test_no_shared_or_other_question_is_included(self):
        self.assertEqual([c for c in EXPECTED if c.startswith("115-00-E")].__len__(), 4)
        self.assertNotIn("115-00-E-42", self.lessons)
        e40 = self.lessons["115-00-E-40"]["teaching"]
        self.assertIn("NOT", e40["teacherSummary"])
        self.assertIn("rather than", e40["teacherSummary"])
        self.assertIn("ride the wave of change", self.lessons["115-00-E-41"]["teaching"]["teacherSummary"])

if __name__ == "__main__":
    unittest.main()
