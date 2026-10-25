"""Role B07: real original 114 C07 word-frequency chart + C09 double bubble, fail-closed G2."""
from pathlib import Path
import hashlib, json, unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sudu/data/processed/114"
BASE = ROOT / "sudu/teaching-candidates/114-role-b-20261025-batch07"
IDS = {"114-00-C-07", "114-00-C-09"}
ANS = {"114-00-C-07": "C", "114-00-C-09": "A"}
WEBP = {
    "114-00-C-07": "de3aa6dc943acc5e086acdddf3a6922abd505d0eba99c9ece82dec7641e3bc20",
    "114-00-C-09": "c49f150c96f564e63d8697937e40acf5b123a363db9b05fb4c8db09c30a5c2be",
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def hash_obj(obj):
    return sha(canonical(obj))

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def compact(text):
    return "".join(text.split())

class TestRoleB07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = load(BASE / "batch.json")
        cls.bank = {q["questionId"]: q for q in load(SOURCE / "questions.json")["questions"]}
        cls.mani = {m["questionId"]: m for m in load(SOURCE / "webp-manifest.json")["items"]}
        cls.qa = load(SOURCE / "VISUAL_QA_BATCH_01_2026-10-22.json")
        cls.docs = {r["questionId"]: load(ROOT / r["path"]) for r in cls.batch["items"]}

    def test_two_explicitly_quarantined_no_ready_no_human_gate(self):
        b = self.batch
        self.assertEqual(set(self.docs), IDS)
        self.assertEqual(b["itemCount"], 2)
        self.assertEqual(b["sourceG2"], "TABLE_AND_DIAGRAM_CHOICE_TEXT_UNCERTIFIED")
        self.assertEqual((b["newReady"], b["newMain"], b["newLive"]), (0, 0, 0))
        self.assertEqual(b["distinctAiEContentReview"], "PENDING")
        self.assertEqual(b["masterRelease"], "NOT_AUTHORIZED")
        self.assertIs(b["requiresRealHumanTeacher"], False)
        self.assertIs(b["authorSelfCheckOnly"], True)

    def test_original_webp_and_source_page_actual_byte_sha_and_old_image_only_qa(self):
        self.assertEqual(self.qa["scope"], "Image only; no official answer confirmation")
        for qid in sorted(IDS):
            with self.subTest(qid=qid):
                q = self.bank[qid]
                m = self.mani[qid]
                d = self.docs[qid]
                self.assertEqual(m["qaStatus"], "PASS")
                self.assertEqual(m["sha256"], WEBP[qid])
                self.assertEqual(q["questionProvenance"]["webpSha256"], WEBP[qid])
                self.assertEqual(sha((ROOT / m["output"]).read_bytes()), WEBP[qid])
                self.assertEqual(sha((ROOT / m["source"]).read_bytes()), m["sourceSha256"])
                self.assertEqual(d["source"]["webpSha256"], WEBP[qid])
                receipt = next(x for x in self.qa["records"] if x["questionId"] == qid)
                self.assertEqual(receipt["result"], "PASS")
                self.assertEqual(receipt["webpSha256"], WEBP[qid])
                self.assertEqual(receipt["sourceSha256"], m["sourceSha256"])
                self.assertEqual(receipt["cropPixels"], m["crop"])

    def test_original_answer_page_real_git_blob_and_existing_only_candidates(self):
        a = self.docs["114-00-C-07"]["source"]
        raw = (ROOT / a["answerPageWebpPath"]).read_bytes()
        self.assertEqual(git_blob(raw), "c3090e94ab1cbf7adf9f7efd0581529eff00e26b")
        for qid in IDS:
            q = self.bank[qid]
            d = self.docs[qid]
            self.assertEqual(q["answer"], ANS[qid])
            self.assertEqual(d["knownAnswerCandidate"], ANS[qid])
            self.assertIs(q["answerVerified"], False)
            self.assertIs(q["questionVerified"], False)
            self.assertTrue(d["reasoningAudit"]["answerAlreadyKnown"])
            self.assertTrue(d["reasoningAudit"]["notBlindSolve"])
            self.assertTrue(d["review"]["officialFinalAnswerYearCorrectionScopeNotCertified"])

    def test_raw_source_choices_are_preserved_and_visual_transcription_is_separate(self):
        for qid in IDS:
            with self.subTest(qid=qid):
                q = self.bank[qid]
                d = self.docs[qid]
                self.assertEqual(d["question"], q["question"])
                self.assertEqual(d["options"], q["options"])
                self.assertEqual(q["issues"], [])
                self.assertEqual(len(d["imageTranscribedOptions"]), 4)
                for raw, clean in zip(q["options"], d["imageTranscribedOptions"]):
                    self.assertTrue(compact(raw).startswith(compact(clean)))
                self.assertTrue(d["source"]["sourceNeedsRoleACanonicalTableDiagramReconciliation"])
                self.assertTrue(d["source"]["authorTranscriptIsNotCanonicallyVerified"])
                self.assertTrue(d["review"]["sourceTextAndTableQaNotCertified"])
                self.assertTrue(d["source"]["unresolvedNewG2Issue"].startswith("G2_"))
        q7 = self.docs["114-00-C-07"]
        self.assertIn("①", q7["options"][1])
        self.assertIn("風流", q7["options"][3])
        self.assertNotIn("①", q7["imageTranscribedOptions"][1])
        q9 = self.docs["114-00-C-09"]
        self.assertIn("耳鑒", q9["options"][2])
        self.assertIn("收藏", q9["options"][0])
        self.assertNotIn("耳鑒", q9["imageTranscribedOptions"][2])

    def test_q07_exact_original_frequency_groups_and_q09_bubble_mappings(self):
        freq = self.docs["114-00-C-07"]["enrichment"]["originalVisual"]
        self.assertEqual(freq["visualType"], "ORIGINAL_WORD_FREQUENCY_TABLE")
        self.assertTrue(freq["notCanonicalTextQa"])
        self.assertEqual([g["label"] for g in freq["groups"]], ["①", "②", "③", "④"])
        self.assertEqual([g["interpretation"] for g in freq["groups"]], ["豪放", "婉約", "豪放", "婉約"])
        self.assertIn("劍", freq["groups"][0]["col2"])
        self.assertIn("相思", freq["groups"][3]["col2"])
        bubble = self.docs["114-00-C-09"]["enrichment"]["originalVisual"]
        self.assertEqual(bubble["visualType"], "ORIGINAL_DOUBLE_BUBBLE_DIAGRAM")
        self.assertTrue(bubble["notCanonicalTextQa"])
        self.assertEqual(bubble["diagram"]["sharedCircle"], "①")
        self.assertEqual(bubble["diagram"]["leftOnlyCircle"], "②")
        self.assertEqual(bubble["diagram"]["rightOnlyCircle"], "③")
        self.assertEqual(bubble["mapping"], {"①": "鑑定粗糙", "②": "憑畫者名聲", "③": "憑視覺觸感"})

    def test_every_abcd_distinct_teacher_elementary_and_why_with_no_fake_calculation(self):
        for qid, d in self.docs.items():
            with self.subTest(qid=qid):
                t = d["teaching"]
                self.assertGreaterEqual(len(t["teacherSummary"]), 120)
                self.assertGreaterEqual(len(t["elementarySummary"]), 50)
                self.assertGreaterEqual(len(t["solvingSteps"]), 4)
                self.assertGreaterEqual(len(t["memory"]), 20)
                self.assertEqual(set(t["optionExplanations"]), set("ABCD"))
                reasons = []
                for letter, val in t["optionExplanations"].items():
                    self.assertIs(val["isCorrect"], letter == ANS[qid])
                    self.assertGreaterEqual(len(val["teacher"]), 45)
                    self.assertGreaterEqual(len(val["elementary"]), 20)
                    self.assertGreaterEqual(len(val["reason"]), 25)
                    reasons.append(val["reason"])
                self.assertEqual(len(set(reasons)), 4)
                self.assertIs(t["hasExamCalculation"], False)
                self.assertIsNone(t["examCalculation"])
                self.assertNotIn("本題無金額計算", json.dumps(t, ensure_ascii=False))

    def test_safe_literals_graded_chinese_and_no_invented_textbook_pages(self):
        for qid, d in self.docs.items():
            vocab = d["enrichment"]["chineseVocabulary"]
            self.assertEqual({v["level"] for v in vocab}, {"初級", "中級", "高級"})
            self.assertIsNone(d["textbook"]["publisher"])
            self.assertIsNone(d["textbook"]["edition"])
            self.assertIsNone(d["textbook"]["chapter"])
            self.assertIsNone(d["textbook"]["page"])
            evidence = d["question"] + " " + " ".join(d["options"]) + " " + " ".join(d["imageTranscribedOptions"])
            for highlight in d["enrichment"]["highlights"]:
                self.assertIn(highlight["text"], evidence)
                self.assertNotIn("<", highlight["text"])
                self.assertNotIn(">", highlight["text"])
                self.assertIs(highlight["bold"], True)
                self.assertIs(highlight["highlight"], True)
                self.assertEqual(highlight["renderMode"], "literal_text_only")

    def test_sha_bind_source_visual_teacher_and_enrichment_and_reject_tamper(self):
        for row in self.batch["items"]:
            qid = row["questionId"]
            d = self.docs[qid]
            q = self.bank[qid]
            m = self.mani[qid]
            source_rev = hash_obj({"question": q["question"], "options": q["options"], "singleQuestionWebpSha256": m["sha256"]})
            transcript_rev = hash_obj({"question": q["question"], "options": d["imageTranscribedOptions"], "singleQuestionWebpSha256": m["sha256"]})
            self.assertEqual(source_rev, row["sourceRevision"])
            self.assertEqual(transcript_rev, row["sourceImageTranscriptSha256"])
            self.assertEqual(d["source"]["questionRevision"], source_rev)
            self.assertEqual(d["source"]["sourceImageTranscriptSha256"], transcript_rev)
            self.assertEqual(d["teachingCanonicalSha256"], hash_obj(d["teaching"]))
            self.assertEqual(row["teachingCanonicalSha256"], d["teachingCanonicalSha256"])
            joined = {"questionId": qid, "sourceRevision": source_rev, "sourceImageTranscriptSha256": transcript_rev,
                      "webpSha256": m["sha256"], "teaching": d["teaching"], "enrichment": d["enrichment"]}
            self.assertEqual(hash_obj(joined), row["composedTeachingSha256"])
            self.assertEqual(hash_obj(joined), d["composedTeachingSha256"])
            self.assertEqual(sha((ROOT / row["path"]).read_bytes()), row["fileSha256"])
            self.assertNotEqual(hash_obj(dict(joined, sourceRevision="0"*64)), d["composedTeachingSha256"])
            self.assertNotEqual(hash_obj(dict(joined, sourceImageTranscriptSha256="1"*64)), d["composedTeachingSha256"])
            self.assertNotEqual(hash_obj(dict(joined, webpSha256="2"*64)), d["composedTeachingSha256"])
            self.assertNotEqual(hash_obj(dict(joined, teaching=dict(d["teaching"], memory="tampered"))), d["composedTeachingSha256"])
            self.assertNotEqual(hash_obj(dict(joined, enrichment={"tampered": True})), d["composedTeachingSha256"])

    def test_no_author_self_approved_e_or_d_or_student_main_live(self):
        for qid, d in self.docs.items():
            rv = d["review"]
            e = rv["independentAiContentReview"]
            self.assertEqual(rv["status"], "BLOCKED")
            self.assertIs(rv["requiresHumanTeacher"], False)
            self.assertIs(rv["authorSelfCheckOnly"], True)
            self.assertEqual(e["status"], "PENDING_DISTINCT_ROLE_E")
            self.assertEqual(e["reviewerRole"], "E")
            self.assertIsNone(e["reviewTaskId"])
            self.assertIsNone(e["reviewSessionId"])
            self.assertIsNone(e["trustedEvidencePath"])
            self.assertIs(rv["formalReady"], False)
            self.assertIs(rv["studentReleaseApproved"], False)
            self.assertIs(rv["uiQaExactDigest"], False)
            self.assertIs(rv["newMain"], False)
            self.assertIs(rv["newLive"], False)
            self.assertIn("E_DISTINCT_AI_OPTION_REASON_VERIFICATION_PENDING", rv["blockers"])
            self.assertIn("MASTER_TRUSTED_E_REVIEW_PROTECTED_MAIN_PUBLISHER_LIVE_PENDING", rv["blockers"])

if __name__ == "__main__":
    unittest.main()
