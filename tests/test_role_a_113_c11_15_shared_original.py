"""Role A exact original 113 11-15 shared reading and per-question pixel candidates, NO RELEASE."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c11_15_shared_original as a
from scripts import role_a_113_c01_05_source_pixels as prev

ROOT=Path(__file__).resolve().parents[1]
class Original113Chinese11To15(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=a.read(a.MAN)
        cls.doc,cls.p,cls.pixels,cls.answer=a.load_archive()
        cls.q={x["originalQuestionNumber"]:x for x in cls.m["questions"]}
        assert set(cls.q)==set(range(11,16))

    def test_two_historical_official_source_pages_git_and_actual_pixel_sha(self):
        self.assertEqual(set(a.PAGE_GIT),{4,5})
        for n in (4,5):
            with self.subTest(page=n):
                self.assertEqual(a.gitsha(self.pixels[n]),a.PAGE_GIT[n])
                self.assertEqual(a.sha(self.pixels[n]),self.m["originalPages"][str(n)]["sha256"])
                self.assertEqual(self.m["originalPages"][str(n)]["pixelSize"],[1400,1981])
        self.assertEqual(a.gitsha(self.answer),prev.ANS_GIT)
        self.assertEqual(self.m["originalAnnouncedAnswerPage"]["sha256"],a.sha(self.answer))
        self.assertEqual(self.m["originalQuestionPdfSha256RecordedOnly"],prev.SRC_PDF_RECORDED)
        self.assertEqual(self.m["originalAnswerPdfSha256RecordedOnly"],prev.ANS_PDF_RECORDED)
        self.assertFalse(self.m["originalPdfsRehashedThisBatch"])

    def test_one_full_archived_original_reading_shared_by_all_five_cross_page_numbers(self):
        shared=self.m["sharedMaterials"][0]
        self.assertEqual(shared["sharedMaterialId"],a.SHARED_ID)
        self.assertEqual(shared["originalQuestionNumbers"],[11,12,13,14,15])
        self.assertEqual(shared["linkedQuestionPages"],[4,5])
        self.assertEqual(shared["asset"]["cropPixels"],a.SHARED_CROP)
        self.assertEqual(shared["asset"]["sourceOriginalPageNumber"],4)
        self.assertEqual(shared["qaStatus"],"DRAFT_NEEDS_SHA_BOUND_INDIVIDUAL_IMAGE_QA")
        self.assertFalse(shared["independentHumanReview"])
        self.assertFalse(shared["independentRoleEContentReview"])
        a.verify_asset(shared["asset"])
        for q in self.q.values():
            self.assertEqual(q["sharedMaterialId"],a.SHARED_ID)
            self.assertEqual(q["sharedMaterialAssetSha256"],shared["asset"]["sha256"])
            self.assertTrue(q["mandatorySharedReadingOriginalPixels"])
        self.assertLess(shared["asset"]["cropPixels"][3],self.q[11]["sourceAsset"]["cropPixels"][1])

    def test_five_canonical_source_ids_four_choices_and_announced_answers_unapproved(self):
        self.assertEqual([q["questionId"] for q in self.m["questions"]],
                         [f"113-00-C-{n:02d}" for n in range(11,16)])
        self.assertEqual("".join(q["answerCandidate"] for q in self.m["questions"]),"CBCAA")
        for n,q in self.q.items():
            old=self.p["questions"][n-1]
            with self.subTest(number=n):
                self.assertEqual(q["question"],old["question"])
                self.assertEqual(q["originalRawQuestionText"],old["question"])
                self.assertEqual(q["originalRawOptions"],old["options"])
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["answerCandidate"],old["officialAnswerCandidate"])
                self.assertEqual(q["answerCandidate"],chr(ord("A")+old["answer"]))
                self.assertEqual(q["sourcePageNumber"],a.CROPS[n][0])
                self.assertEqual(q["sourceAsset"]["cropPixels"],a.CROPS[n][1])
                self.assertFalse(q["answerVerified"])
                self.assertFalse(q["questionVerified"])
                self.assertFalse(q["teachingVerified"])
                self.assertFalse(q["studentReady"])
                self.assertFalse(q["independentRoleEContentReview"])
                self.assertEqual(q["officialAnswerStatus"],
                                 "PUBLISHED_ANSWER_IMAGE_CANDIDATE_CORRECTION_PDF_NOT_CHECKED")
                self.assertEqual(q["originalSourceTextQaStatus"],
                                 "PENDING_NUMBER_LEVEL_OFFICIAL_VISUAL_TEXT_QA")

    def test_c13_original_two_column_comparison_and_footer_leak_not_in_new_D(self):
        q=self.q[13]
        self.assertTrue(q["mandatoryOriginalTable"])
        self.assertTrue(q["optionDSurgicallyTrimmed"])
        self.assertIn("蘭亭集序",q["question"])
        self.assertIn("-4-",q["originalRawOptions"][3])
        self.assertIn("第5 頁",q["originalRawOptions"][3])
        self.assertEqual(q["options"][:3],q["originalRawOptions"][:3])
        self.assertEqual(q["options"][3],q["originalRawOptions"][3].split("\n",1)[0])
        self.assertNotIn("第5 頁",q["options"][3])
        self.assertNotEqual(q["originalRawOptionsSha256"],q["correctedOptionsSha256"])

    def test_c14_original_two_poem_boxes_not_discarded_in_photo(self):
        q=self.q[14]
        self.assertTrue(q["mandatoryOriginalPoetryBlocks"])
        self.assertFalse(q["mandatoryOriginalIllustration"])
        self.assertFalse(q["optionDSurgicallyTrimmed"])
        self.assertEqual(q["options"],q["originalRawOptions"])
        self.assertIn("梅嶺花初發",q["question"])
        self.assertIn("匈奴",q["question"])

    def test_c15_original_large_poem_figure_and_next_article_leak_not_in_D(self):
        q=self.q[15]
        self.assertTrue(q["mandatoryOriginalIllustration"])
        self.assertTrue(q["optionDSurgicallyTrimmed"])
        self.assertIn("下圖",q["question"])
        self.assertIn("▲閱讀下文，回答第16-19 題",q["originalRawOptions"][3])
        self.assertEqual(q["options"][3],q["originalRawOptions"][3].split("\n",1)[0])
        self.assertNotIn("▲閱讀下文",q["options"][3])
        self.assertNotIn("第6 頁",q["options"][3])
        self.assertNotEqual(q["originalRawOptionsSha256"],q["correctedOptionsSha256"])

    def test_every_source_webp_pixel_exact_and_no_adjacent_page_question(self):
        a.check(self.m)
        for n,q in self.q.items():
            a.verify_asset(q["sourceAsset"])
        for page in (4,5):
            group=[q["sourceAsset"]["cropPixels"] for q in self.q.values()
                   if q["sourcePageNumber"]==page]
            self.assertEqual(group,sorted(group,key=lambda x:x[1]))
            for first,next_ in zip(group,group[1:]):
                self.assertLess(first[3],next_[1])
        self.assertLess(self.m["sharedMaterials"][0]["asset"]["cropPixels"][3],
                        self.q[11]["sourceAsset"]["cropPixels"][1])
        self.assertLess(self.q[14]["sourceAsset"]["cropPixels"][3],
                        self.q[15]["sourceAsset"]["cropPixels"][1])

    def test_source_revision_fails_if_option_or_shared_original_image_changes(self):
        for n,q in self.q.items():
            raw={k:q[k] for k in ("questionId","question","options","sourceAsset",
                                  "sharedMaterialId","sharedMaterialAssetSha256",
                                  "originalQuestionPdfSha256RecordedOnly")}
            self.assertEqual(q["sourceRevisionSha256"],a.sha(a.canon(raw).encode("utf-8")))
            wrong=copy.deepcopy(raw)
            wrong["options"][0]+="FAKE_ORIGINAL"
            self.assertNotEqual(q["sourceRevisionSha256"],a.sha(a.canon(wrong).encode("utf-8")))
            wrong=copy.deepcopy(raw)
            wrong["sharedMaterialAssetSha256"]="0"*64
            self.assertNotEqual(q["sourceRevisionSha256"],a.sha(a.canon(wrong).encode("utf-8")))

    def test_five_question_one_shared_sqlite_payload_dual_rebuild_sha_and_integrity(self):
        a.check_db(a.DB,self.m)
        with tempfile.TemporaryDirectory() as temp:
            x=Path(temp)/"x.sqlite3";y=Path(temp)/"y.sqlite3"
            a.write_db(x,self.m);a.write_db(y,self.m)
            a.check_db(x,self.m);a.check_db(y,self.m)
            self.assertEqual(a.sha(x.read_bytes()),a.sha(y.read_bytes()))
            self.assertEqual(a.sha(x.read_bytes()),a.sha(a.DB.read_bytes()))
        with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],5)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0],1)
            for flags in db.execute("SELECT answer_verified,question_verified,teaching_verified,student_ready FROM questions"):
                self.assertEqual(flags,(0,0,0,0))

    def test_no_release_prior_ten_sources_unchanged_and_year_original_not_rebuilt(self):
        for key in ("newQuestionVerified","newAnswerVerified","newTeachingVerified",
                    "newIndependentEReview","newReady","newLive"):
            self.assertEqual(self.m[key],0)
        self.assertFalse(self.m["officialFinalCorrectionNoticeChecked"])
        self.assertEqual(self.m["status"],"ORIGINAL_MULTIPAGE_SOURCE_READING_CANDIDATE_NOT_RELEASED")
        prior=prev.read(prev.MANIFEST)
        self.assertEqual(len(prior["questions"]),5)
        q6=ROOT/"sudu/data/processed/113/role-a-c06/manifest.json"
        self.assertEqual(json.loads(q6.read_text(encoding="utf-8"))["questions"][0]["sourceAsset"]["sha256"]
                         if False else json.loads(q6.read_text(encoding="utf-8"))["questions"][0]["asset"]["sha256"],
                         "57064b9f8da602c2894216b5f0ce7577988c2e534272d5da02affd5080f1a071")
        old=ROOT/"sudu/data/processed/113/role-a-c07-10/manifest.json"
        base=json.loads(old.read_text(encoding="utf-8"))
        self.assertEqual(len(base["questions"]),4)
        self.assertEqual(base["questions"][2]["sourceAsset"]["sha256"] if False else base["questions"][2]["asset"]["sha256"],
                         "428585747ee518a3e2d0e2d206bffd26a9b124402081cc5c504c16bfe7d3784b")

if __name__=="__main__":
    unittest.main()
