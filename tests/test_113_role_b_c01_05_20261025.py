"""Role B historical 113 C01-05: A original pixel source-bound pedagogy, NO RELEASE."""
from pathlib import Path
import hashlib, json, unittest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "sudu/teaching-candidates/113-role-b-c01-05-20261025"
A = ROOT / "sudu/data/processed/113/role-a-c01-05"
YR = ROOT / "sudu/data/years/113.json"
IDS = [f"113-00-C-{n:02d}" for n in range(1, 6)]
EXPECTED_ANS = ["C", "D", "D", "C", "D"]
PIXELS = [
    "7530812fb36120a00f1df784da804cb85e8c7cdd03c6eb78fcf886d95625d784",
    "4504646281047509ea1bd88b68271e79ef3c44f89893ea8331cfd7f2e3e6c73a",
    "ef5244f376272eaf43718c33cac84e3585eaa23a3411e11e024fe627536adf79",
    "f548f0e5cdfbc3c669dd5ea161128ba5b277a83ed58ef0d044d61c64f5e4c13a",
    "ff1f548bead9b1850688f99b74e1946e2a2e0f5f1c83b299b5002801a51e9cd3",
]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def h(obj):
    return sha(canonical(obj))

def gitblob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class RoleB113(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read(DIR / "batch.json")
        cls.source = read(A / "manifest.json")
        cls.visual = read(A / "VISUAL_QA_ASSISTANT_20261025.json")
        cls.year = read(YR)
        cls.q = {x["questionId"]: x for x in cls.source["questions"]}
        cls.qyear = {x["id"]: x for p in cls.year["papers"] for x in p["questions"]}
        cls.d = {x["questionId"]: read(ROOT / x["path"]) for x in cls.batch["items"]}
        cls.qa = {x["questionId"]: x for x in cls.visual["questions"]}

    def test_five_exact_questions_and_zero_admission(self):
        b = self.batch
        self.assertEqual(b["itemCount"], 5)
        self.assertEqual([x["questionId"] for x in b["items"]], IDS)
        self.assertEqual(b["sourceAnswerCandidates"], EXPECTED_ANS)
        self.assertEqual((b["newReady"], b["newMain"], b["newLive"]), (0, 0, 0))
        self.assertEqual(b["masterRelease"], "NOT_AUTHORIZED")
        self.assertFalse(b["requiresRealHumanTeacher"])
        self.assertTrue(b["authorSelfCheckOnly"])
        self.assertEqual(b["distinctAiEReview"], "PENDING")
        self.assertFalse(b["officialPdfRehashPerformed"])

    def test_true_original_webp_sha_git_blob_and_qa_receipt():
        for i, qid in enumerate(IDS):
            with self.subTest(qid=qid):
                q = self.q[qid]
                d = self.d[qid]
                receipt = self.qa[qid]
                blob = (ROOT / q["asset"]["path"]).read_bytes()
                self.assertEqual(sha(blob), PIXELS[i])
                self.assertEqual(gitblob(blob), q["asset"]["gitBlobSha1"])
                self.assertEqual(d["source"]["webpSha256"], PIXELS[i])
                self.assertEqual(receipt["assetSha256"], PIXELS[i])
                self.assertEqual(receipt["reviewResult"], "PASS_ASSISTANT_DIRECT_ORIGINAL_PIXEL_VISUAL_QA")
                self.assertEqual(receipt["reviewerRole"], "A_SOURCE_ONLY")
                self.assertIs(receipt["independentRoleEContentReview"], False)
                self.assertEqual(q["individualImageQa"], "DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA")
                self.assertEqual(d["source"]["sourceManifestG1Status"], q["individualImageQa"])
                self.assertEqual(receipt["cropPixels"], q["asset"]["cropPixels"])

    def test_true_archived_page_and_answer_page_git_blob_but_no_final_notice_claim(self):
        p = self.source["originalPage"]
        a = self.source["answerPage"]
        org = (ROOT / p["path"]).read_bytes()
        ans = (ROOT / a["path"]).read_bytes()
        self.assertEqual(sha(org), p["sha256"])
        self.assertEqual(gitblob(org), p["gitBlobSha1"])
        self.assertEqual(sha(ans), a["sha256"])
        self.assertEqual(gitblob(ans), a["gitBlobSha1"])
        self.assertEqual(self.visual["originalPageGitBlobSha1"], p["gitBlobSha1"])
        self.assertEqual(self.visual["originalOfficialAnswerPageGitBlobSha1"], a["gitBlobSha1"])
        self.assertIs(self.visual["finalPerNumberCorrectionNoticeChecked"], False)
        self.assertIs(self.visual["pdfByteRehashPerformed"], False)
        self.assertFalse(self.batch["officialPdfRehashPerformed"])

    def test_original_year_source_question_and_answers_are_not_altered(self):
        for i, qid in enumerate(IDS):
            d = self.d[qid]
            q = self.q[qid]
            y = self.qyear[qid]
            self.assertEqual(d["question"], y["question"])
            self.assertEqual(d["options"], y["options"])
            self.assertEqual(d["options"], q["options"])
            self.assertEqual(d["knownAnswerCandidate"], EXPECTED_ANS[i])
            self.assertEqual(q["answerCandidate"], EXPECTED_ANS[i])
            self.assertEqual(d["source"]["sourceRevision"], q["sourceRevisionSha256"])
            self.assertFalse(y["answerVerified"])
            self.assertFalse(y["questionVerified"])
            self.assertFalse(q["answerVerified"])
            self.assertFalse(q["questionVerified"])
            self.assertEqual(d["source"]["sourceTextQa"], "PENDING_FULL_OFFICIAL_PDF_PAGE_REVIEW")
            self.assertEqual(d["source"]["finalOfficialAnswerQa"], "PENDING_CORRECTION_PDF_SCOPE")
        self.assertIn("摒息凝視", self.d["113-00-C-01"]["options"][2])
        self.assertIn("屏息凝視", self.d["113-00-C-01"]["teaching"]["teacherSummary"])
        self.assertEqual(self.source["legacyYearQuestionsFound"], 196)
        self.assertEqual(self.source["candidateYearQuestions"], 205)

    def test_dual_layer_four_choices_and_non_calculation_blocks(self):
        for qid, d in self.d.items():
            with self.subTest(qid=qid):
                t = d["teaching"]
                self.assertGreaterEqual(len(t["teacherSummary"]), 65)
                self.assertGreaterEqual(len(t["elementarySummary"]), 25)
                self.assertGreaterEqual(len(t["solvingSteps"]), 4)
                self.assertEqual(set(t["optionExplanations"]), set("ABCD"))
                reasons = []
                for letter, opt in t["optionExplanations"].items():
                    self.assertIs(opt["isCorrect"], letter == d["knownAnswerCandidate"])
                    self.assertGreaterEqual(len(opt["teacher"]), 20)
                    self.assertGreaterEqual(len(opt["elementary"]), 10)
                    self.assertGreaterEqual(len(opt["why"]), 14)
                    reasons.append(opt["why"])
                self.assertEqual(len(set(reasons)), 4)
                self.assertTrue(t["concept"])
                self.assertTrue(t["memory"])
                self.assertIsNone(t["examCalculation"])
                self.assertIs(t["hasExamCalculation"], False)
                self.assertNotIn("本題無金額計算", json.dumps(t, ensure_ascii=False))

    def test_safe_literal_highlight_three_levels_and_no_invented_textbook(self):
        for qid, d in self.d.items():
            with self.subTest(qid=qid):
                src = d["question"] + " " + " ".join(d["options"])
                vocab = d["enrichment"]["chineseVocabulary"]
                self.assertEqual({v["level"] for v in vocab}, {"初級", "中級", "高級"})
                for m in d["enrichment"]["highlights"]:
                    self.assertIn(m["text"], src)
                    self.assertNotIn("<", m["text"])
                    self.assertNotIn(">", m["text"])
                    self.assertIs(m["bold"], True)
                    self.assertIs(m["highlight"], True)
                for key in ("publisher", "edition", "chapter", "page"):
                    self.assertIsNone(d["textbook"][key])

    def test_sha_source_image_teacher_composition_and_file_bytes_mutation_negative(self):
        for row in self.batch["items"]:
            d = self.d[row["questionId"]]
            src = self.q[row["questionId"]]
            self.assertEqual(src["sourceRevisionSha256"], row["sourceRevision"])
            self.assertEqual(d["source"]["sourceRevision"], row["sourceRevision"])
            self.assertEqual(d["source"]["webpSha256"], row["webpSha256"])
            self.assertEqual(h(d["teaching"]), d["teachingCanonicalSha256"])
            self.assertEqual(h(d["teaching"]), row["teachingCanonicalSha256"])
            bound = {"questionId": d["questionId"], "sourceRevision": src["sourceRevisionSha256"],
                     "webpSha256": src["asset"]["sha256"], "teaching": d["teaching"],
                     "enrichment": d["enrichment"]}
            self.assertEqual(h(bound), d["composedTeachingSha256"])
            self.assertEqual(h(bound), row["composedTeachingSha256"])
            self.assertEqual(sha((ROOT / row["path"]).read_bytes()), row["fileSha256"])
            self.assertNotEqual(h(dict(bound, sourceRevision="0"*64)), row["composedTeachingSha256"])
            self.assertNotEqual(h(dict(bound, webpSha256="1"*64)), row["composedTeachingSha256"])
            self.assertNotEqual(h(dict(bound, teaching=dict(d["teaching"], memory="tampered"))), row["composedTeachingSha256"])
            self.assertNotEqual(h(dict(bound, enrichment={"tampered": True})), row["composedTeachingSha256"])

    def test_strict_separate_e_review_and_source_official_d_master_blocks():
        for d in self.d.values():
            r = d["review"]
            self.assertEqual(r["status"], "BLOCKED")
            self.assertIs(r["authorSelfCheckOnly"], True)
            self.assertIs(r["requiresRealHumanTeacher"], False)
            self.assertEqual(r["roleE"], "PENDING_DISTINCT_AI_REVIEW")
            self.assertEqual(r["roleD"], "PENDING_SAME_SHA_8X2")
            self.assertIs(r["officialFinalAnswerVerified"], False)
            self.assertIs(r["sourceFinalQaVerified"], False)
            self.assertIs(r["formalReady"], False)
            self.assertIs(r["newMain"], False)
            self.assertIs(r["newLive"], False)

if __name__ == "__main__":
    unittest.main()
