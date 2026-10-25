"""ROLE A 113 Chinese C07-10 actual original figures and isolated draft SQL.

Only QA source pixels and source-transcribed option candidate. Never promotes
historical answerMatched, studentReady, teacher/Role-E review or Pages.
"""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c07_10_source_figures as a
from scripts import role_a_113_c01_05_source_pixels as archived

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_Q01_TO05={
    1:"7530812fb36120a00f1df784da804cb85e8c7cdd03c6eb78fcf886d95625d784",
    2:"4504646281047509ea1bd88b68271e79ef3c44f89893ea8331cfd7f2e3e6c73a",
    3:"ef5244f376272eaf43718c33cac84e3585eaa23a3411e11e024fe627536adf79",
    4:"f548f0e5cdfbc3c669dd5ea161128ba5b277a83ed58ef0d044d61c64f5e4c13a",
    5:"ff1f548bead9b1850688f99b74e1946e2a2e0f5f1c83b299b5002801a51e9cd3",
}
class Original113Chinese07To10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc,cls.paper,cls.sourceBytes,cls.answerBytes=a.source()
        cls.man=a.read(a.MAN)
        cls.q={q["originalQuestionNumber"]:q for q in cls.man["questions"]}
        assert set(cls.q)=={7,8,9,10}

    def test_exact_archived_original_source_and_published_answer_image_sha(self):
        self.assertEqual(a.gitsha(self.sourceBytes),a.SOURCE_GIT)
        self.assertEqual(a.gitsha(self.answerBytes),archived.ANS_GIT)
        self.assertEqual(self.man["originalPage"]["sha256"],a.sha(self.sourceBytes))
        self.assertEqual(self.man["originalAnswerPage"]["sha256"],a.sha(self.answerBytes))
        self.assertEqual(self.man["questionPdfSha256RecordedOnly"],archived.SRC_PDF_RECORDED)
        self.assertEqual(self.man["answerPdfSha256RecordedOnly"],archived.ANS_PDF_RECORDED)
        self.assertFalse(self.man["originalPdfsFreshlyDownloadedAndHashed"])
        self.assertFalse(self.man["officialFinalAmendmentCheckedForNumbers"])

    def test_all_four_real_canonical_ids_and_answers_are_only_unverified_candidates(self):
        self.assertEqual(self.man["questionCount"],4)
        self.assertEqual([q["questionId"] for q in self.man["questions"]],
            [f"113-00-C-{n:02d}" for n in range(7,11)])
        self.assertEqual("".join(q["answerCandidate"] for q in self.man["questions"]),"ADBB")
        for n,q in self.q.items():
            with self.subTest(qid=q["questionId"]):
                old=self.paper["questions"][n-1]
                self.assertEqual(q["originalQuestionNumber"],n)
                self.assertEqual(q["question"],old["question"])
                self.assertEqual(q["originalRawQuestionText"],old["question"])
                self.assertEqual(q["originalRawOptions"],old["options"])
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["answerCandidate"],old["officialAnswerCandidate"])
                self.assertEqual(q["answerCandidate"],chr(ord("A")+old["answer"]))
                self.assertFalse(q["answerVerified"])
                self.assertFalse(q["questionVerified"])
                self.assertFalse(q["teachingVerified"])
                self.assertFalse(q["studentReady"])
                self.assertTrue(q["answerMatchedLegacy"])
                self.assertEqual(q["officialAnswerStatus"],"ANNOUNCED_IMAGE_CANDIDATE_FINAL_CORRECTION_SCOPE_PENDING")
                self.assertEqual(q["visualQaStatus"],"DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA")
                self.assertEqual(q["originalQuestionTextQa"],"PENDING_FINAL_PAGE_VISUAL_TEXT_QA")

    def test_correct_q7_q8_options_are_preserved_without_any_transcription(self):
        for n in (7,8):
            q=self.q[n]
            self.assertFalse(q["optionTextCorrection"])
            self.assertEqual(q["options"],self.paper["questions"][n-1]["options"])
            self.assertEqual(q["originalRawOptionsSha256"],q["candidateCorrectedOptionsSha256"])
            self.assertFalse(q["mandatoryOriginalFigure"])

    def test_q9_five_strategy_chart_original_pixel_and_options_no_embedded_axis_noise(self):
        q=self.q[9]
        self.assertTrue(q["optionTextCorrection"])
        self.assertTrue(q["mandatoryOriginalFigure"])
        self.assertEqual(q["originalFigureKind"],"five_strategy_positioning_matrix")
        self.assertEqual(q["options"],["①、②皆正確","①、②皆錯誤","①正確，②錯誤","①錯誤，②正確"])
        self.assertNotEqual(q["originalRawOptionsSha256"],q["candidateCorrectedOptionsSha256"])
        self.assertIn("配合他人的程度",q["originalRawOptions"][3])
        self.assertTrue(all("高" not in option and "低" not in option for option in q["options"]))

    def test_q10_fishbone_diagram_and_four_column_original_choices_not_next_p4_article(self):
        q=self.q[10]
        self.assertTrue(q["optionTextCorrection"])
        self.assertTrue(q["mandatoryOriginalFigure"])
        self.assertEqual(q["originalFigureKind"],"fishbone_cause_chart_and_four_column_AD_table")
        self.assertEqual(q["originalAnswerOptionColumnLabels"],["①","①－1","②","②－1"])
        self.assertEqual(q["options"],a.CLEAN_OPTIONS[10])
        self.assertIn("▲閱讀下文，回答第11-15 題",q["originalRawOptions"][3])
        self.assertNotIn("▲閱讀下文",q["options"][3])
        self.assertFalse(any("第4 頁" in t for t in q["options"]))
        self.assertIn("互通有無",q["options"][3])
        self.assertIn("魚骨",q["question"])
        self.assertNotEqual(q["originalRawOptionsSha256"],q["candidateCorrectedOptionsSha256"])

    def test_all_four_original_webps_are_lossless_source_pixels_and_do_not_overlap(self):
        with Image.open(a.ORIGIN) as page:
            page.load()
            for n,q in self.q.items():
                with self.subTest(number=n):
                    self.assertEqual(q["asset"]["cropPixels"],a.CROPS[n])
                    self.assertEqual(q["asset"]["page"],3)
                    self.assertEqual(q["asset"]["sourceOriginalPageSha256"],a.sha(self.sourceBytes))
                    self.assertEqual(q["asset"]["pixelSize"],
                                     [a.CROPS[n][2]-a.CROPS[n][0],a.CROPS[n][3]-a.CROPS[n][1]])
                    self.assertLess(q["asset"]["pixelSize"][1],page.height/2)
                    raw=(ROOT/q["asset"]["path"]).read_bytes()
                    self.assertEqual(raw[:4],b"RIFF")
                    self.assertEqual(a.sha(raw),q["asset"]["sha256"])
                    self.assertEqual(a.gitsha(raw),q["asset"]["gitBlobSha1"])
                    with Image.open(ROOT/q["asset"]["path"]) as im:
                        im.load()
                        self.assertEqual(im.format,"WEBP")
                        self.assertIsNone(ImageChops.difference(
                            im.convert("RGB"),archived.crop(page,a.CROPS[n])).getbbox())
        crops=[a.CROPS[n] for n in range(7,11)]
        self.assertEqual(crops,sorted(crops,key=lambda x:x[1]))
        for left,right in zip(crops,crops[1:]):
            self.assertLess(left[3],right[1],"no adjacent question pixels in individual candidates")

    def test_exact_source_revision_changes_on_corrupt_option_image_or_table(self):
        for n,q in self.q.items():
            raw={k:q[k] for k in ("questionId","question","options","asset",
                                  "originalQuestionPdfSha256RecordedOnly")}
            self.assertEqual(q["sourceRevisionSha256"],a.sha(a.canonical(raw).encode("utf-8")))
            bad=copy.deepcopy(raw)
            bad["options"][0]+="TAMPERED_OPTION"
            self.assertNotEqual(q["sourceRevisionSha256"],a.sha(a.canonical(bad).encode("utf-8")))
            bad=copy.deepcopy(raw)
            bad["asset"]["sha256"]="0"*64
            self.assertNotEqual(q["sourceRevisionSha256"],a.sha(a.canonical(bad).encode("utf-8")))

    def test_partial_four_row_sqlite_two_independent_imports_integrity_and_zero_approval(self):
        a.check(self.man)
        a.read_db(a.DB,self.man)
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"x.sqlite3";y=Path(td)/"y.sqlite3"
            a.write_db(x,self.man);a.write_db(y,self.man)
            self.assertEqual(a.sha(x.read_bytes()),a.sha(y.read_bytes()))
            self.assertEqual(a.sha(a.DB.read_bytes()),a.sha(x.read_bytes()))
        with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],4)
            for r in db.execute("SELECT answer_verified,question_verified,teaching_verified,student_ready FROM questions"):
                self.assertEqual(tuple(r),(0,0,0,0))

    def test_already_verified_six_previous_original_assets_not_modified(self):
        earlier=archived.read(archived.MANIFEST)
        for row in earlier["questions"]:
            n=row["originalQuestionNumber"]
            self.assertEqual(row["asset"]["sha256"],EXPECTED_Q01_TO05[n])
            self.assertEqual(a.sha((ROOT/row["asset"]["path"]).read_bytes()),EXPECTED_Q01_TO05[n])
        previous6=ROOT/"sudu/data/processed/113/role-a-c06/manifest.json"
        q6=json.loads(previous6.read_text(encoding="utf-8"))["questions"][0]
        self.assertEqual(q6["asset"]["sha256"],"57064b9f8da602c2894216b5f0ce7577988c2e534272d5da02affd5080f1a071")
        self.assertEqual(q6["sourceRevisionSha256"],"f5dd92e4d8b3184590011569c08977d59e3454d18b7489c3d60aca01f3343730")

    def test_visual_boundary_correction_rejects_old_Q9_graph_foot_and_preserves_Q7_Q8(self):
        old={r["questionId"]:r for r in self.man["rejectedInitialCrops"]}
        self.assertEqual(set(old),{"113-00-C-09","113-00-C-10"})
        self.assertEqual(old["113-00-C-09"]["cropPixels"],[90,661,1310,1123])
        self.assertEqual(old["113-00-C-09"]["sha256"],
            "2c42042d8f75bba4123e76e151e088659d769c90ad665fb26589f3fff87c54ac")
        self.assertEqual(old["113-00-C-10"]["cropPixels"],[90,1125,1310,1840])
        self.assertEqual(old["113-00-C-10"]["sha256"],
            "d4491b6806725f979615be77164a943732f511991b680fdfc6383a21190c1491")
        self.assertEqual(self.q[9]["asset"]["cropPixels"],[90,661,1310,1136])
        self.assertEqual(self.q[10]["asset"]["cropPixels"],[90,1137,1310,1840])
        self.assertNotEqual(old["113-00-C-09"]["sha256"],self.q[9]["asset"]["sha256"])
        self.assertNotEqual(old["113-00-C-10"]["sha256"],self.q[10]["asset"]["sha256"])
        self.assertEqual(self.q[7]["asset"]["sha256"],
            "dc654891d368033b5b422cf01181231aefc62e9a31452ad1e64aaca478291b4a")
        self.assertEqual(self.q[8]["asset"]["sha256"],
            "4ea59fb90d9bbec2f255944b0a5fc6be4f9a25257e3f74caa7aa3b5e10e88e49")
        self.assertLess(self.q[9]["asset"]["cropPixels"][3],self.q[10]["asset"]["cropPixels"][1])

    def test_four_actual_source_visual_observations_exact_sha_and_explicit_not_e(self):
        receipt=ROOT/"sudu/data/processed/113/role-a-c07-10/VISUAL_QA_ASSISTANT_20261025.json"
        self.assertTrue(receipt.exists())
        j=a.read(receipt)
        self.assertEqual(j["taskId"],a.TASK)
        self.assertEqual(j["originalSourcePage"]["sha256"],self.man["originalPage"]["sha256"])
        self.assertEqual(j["originalAnswerPage"]["sha256"],self.man["originalAnswerPage"]["sha256"])
        self.assertEqual(j["oldRejectedCrops"],self.man["rejectedInitialCrops"])
        self.assertEqual(j["newSourceImageAssistantPassCount"],4)
        for key in ("newAnswerVerified","newQuestionVerified","newTeachingVerified",
                    "newIndependentRoleEReview","newReady","newLive"):
            self.assertEqual(j[key],0)
        for key in ("independentHumanReview","independentRoleEContentReview",
                    "officialFinalAmendmentChecked","originalPdfBytesRehashedThisBatch",
                    "wholeYearOriginalQuestionVerified"):
            self.assertFalse(j[key])
        self.assertTrue(j["observedQ09OriginalFigureComplete"])
        self.assertTrue(j["observedQ10FishboneAndOptionTableComplete"])
        byid={x["questionId"]:x for x in j["questionResults"]}
        self.assertEqual(len(byid),4)
        for n,q in self.q.items():
            with self.subTest(number=n):
                item=byid[q["questionId"]]
                self.assertEqual(item["asset"],q["asset"])
                self.assertEqual(item["sourceRevisionSha256"],q["sourceRevisionSha256"])
                self.assertEqual(item["originalPublishedAnswerCandidate"],q["answerCandidate"])
                self.assertEqual(item["visualSourceResult"],"PASS_ROLE_A_SOURCE_IMAGE_ONLY")
                self.assertFalse(item["answerVerified"])
                self.assertFalse(item["questionVerified"])
                self.assertFalse(item["independentRoleEReview"])
                self.assertTrue(all(item["criteria"].values()))
                self.assertGreater(len(item["observation"]),100)
                self.assertEqual(item["figureReview"],"PASS_ORIGINAL_PX_FIGURE_FULL" if n in (9,10) else "NOT_APPLICABLE")
                self.assertEqual(item["tableReview"],"PASS_ALL_FOUR_COLUMN_LABELS_AND_AD_ROWS" if n==10 else "NOT_APPLICABLE")
                # Despite actual image inspection, the publisher candidate remains
                # unapproved pending per-year original official answer corrections.
                self.assertEqual(q["visualQaStatus"],"DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA")

    def test_never_treat_four_image_candidates_or_auto_answers_as_final_ready(self):
        for key in ("newQuestionVerified","newAnswerVerified","newTeachingVerified","newIndependentEReview","newReady","newLive"):
            self.assertEqual(self.man[key],0)
        self.assertEqual(self.man["status"],"ORIGINAL_PIXEL_SOURCE_CANDIDATES_UNRELEASED")
        self.assertEqual(self.man["yearCandidateQuestionCount"],205)
        self.assertEqual(self.man["yearLegacyQuestionsFound"],196)

if __name__=="__main__":
    unittest.main()
