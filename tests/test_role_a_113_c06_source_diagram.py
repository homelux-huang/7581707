"""ROLE A exact original 113 Chinese Q06 source-pixel couplet figure + OCR bleed receipt.
This is source candidate validation ONLY: no answerVerified, questionVerified, E, READY, LIVE.
"""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c06_source_diagram as a
from scripts import role_a_113_c01_05_source_pixels as b

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_01_05={
    1:"7530812fb36120a00f1df784da804cb85e8c7cdd03c6eb78fcf886d95625d784",
    2:"4504646281047509ea1bd88b68271e79ef3c44f89893ea8331cfd7f2e3e6c73a",
    3:"ef5244f376272eaf43718c33cac84e3585eaa23a3411e11e024fe627536adf79",
    4:"f548f0e5cdfbc3c669dd5ea161128ba5b277a83ed58ef0d044d61c64f5e4c13a",
    5:"ff1f548bead9b1850688f99b74e1946e2a2e0f5f1c83b299b5002801a51e9cd3",
}
class Source113ChineseOriginalDiagram(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man=a.fromjson(a.MAN)
        cls.old,cls.page_bytes,cls.answer_bytes,_,_=a.source()
        cls.q=cls.man["questions"][0]

    def test_archive_original_source_and_answer_git_shas_are_pinned(self):
        self.assertEqual(b.gitsha(self.page_bytes),b.SRC_GIT)
        self.assertEqual(b.gitsha(self.answer_bytes),b.ANS_GIT)
        self.assertEqual(self.man["sourceOriginalPageWebpSha256"],a.sha(self.page_bytes))
        self.assertEqual(self.man["answerOriginalPageWebpSha256"],a.sha(self.answer_bytes))
        self.assertEqual(self.man["sourceIndex"],"https://web1.tcte.edu.tw/EXAM/113_4y/")
        self.assertFalse(self.man["actualPdfRedownloadedAndRehashed"])
        self.assertFalse(self.man["officialFinalCorrectionNoticeChecked"])

    def test_canonical_single_question_and_exact_four_options_without_page_bleed(self):
        q=self.q
        self.assertEqual(q["questionId"],"113-00-C-06")
        self.assertEqual(q["paperCode"],"00-C")
        self.assertEqual(q["originalQuestionNumber"],6)
        self.assertEqual(q["sourceArchiveOriginalPage"],2)
        self.assertEqual(q["question"],self.old["question"])
        self.assertEqual(len(q["options"]),4)
        self.assertEqual(q["options"][:3],self.old["options"][:3])
        self.assertEqual(q["options"][3],"齊物、無為")
        self.assertNotIn("第3 頁",q["options"][3])
        self.assertNotIn("公告試題",q["options"][3])
        self.assertEqual(q["sourceArchiveOriginalOptions"],self.old["options"])
        self.assertIn("第3 頁",q["sourceArchiveOriginalOptions"][3])
        self.assertIn("公告試題僅供參考",q["sourceArchiveOriginalOptions"][3])
        self.assertEqual(q["sourceArchiveOptionDSha256"],a.sha(self.old["options"][3].encode("utf-8")))
        self.assertEqual(q["correctedOptionDSha256"],a.sha("齊物、無為".encode("utf-8")))
        self.assertFalse(q["sourceRawOptionDChanged"])

    def test_real_original_couplet_figure_and_q06_options_pixels_lossless(self):
        q=self.q
        self.assertEqual(q["asset"]["cropPixels"],[90,1450,1310,1881])
        self.assertTrue(q["asset"]["containsOriginalFigure"])
        self.assertEqual(q["asset"]["pixelSize"],[1220,431])
        self.assertEqual(q["asset"]["path"],"sudu/data/processed/113/role-a-c06/webp/113-00-C-06.webp")
        self.assertLess(q["asset"]["pixelSize"][1],1981/2)
        self.assertEqual(q["asset"]["originalPageSha256"],a.sha(self.page_bytes))
        data=a.WEBP.read_bytes()
        self.assertEqual(a.sha(data),q["asset"]["sha256"])
        self.assertEqual(b.gitsha(data),q["asset"]["gitBlobSha1"])
        with Image.open(b.SOURCE) as source, Image.open(a.WEBP) as part:
            source.load();part.load()
            self.assertEqual(part.format,"WEBP")
            self.assertEqual(part.size,(1220,431))
            self.assertIsNone(ImageChops.difference(
                part.convert("RGB"),b.crop(source,a.CROP)).getbbox())

    def test_reject_first_image_crop_that_touches_vertical_couplet_top(self):
        rejected=self.man["rejectedOldImage"]
        self.assertEqual(rejected["cropPixels"],[90,1472,1310,1881])
        self.assertEqual(rejected["sha256"],"289e16a96ceeeb1c691075b0b553adbd9e31652af0821ab24ad77cf8e15daeb7")
        self.assertNotEqual(rejected["sha256"],self.q["asset"]["sha256"])
        self.assertEqual(self.q["asset"]["cropPixels"][1],1450)
        prior=b.read(b.MANIFEST)["questions"][4]["asset"]["cropPixels"]
        self.assertEqual(prior[3],1450)
        self.assertEqual(prior[3],self.q["asset"]["cropPixels"][1])
        self.assertIn("calligraphy",rejected["reason"])
    def test_official_announced_candidate_B_only_not_final_answer_qa(self):
        q=self.q
        self.assertEqual(self.old["answer"],1)
        self.assertEqual(self.old["officialAnswerCandidate"],"B")
        self.assertEqual(q["answerCandidate"],"B")
        self.assertEqual(q["officialAnswerCandidate"],"B")
        self.assertTrue(q["answerMatchedLegacy"])
        self.assertEqual(q["answerStatus"],
            "ANNOUNCED_ANSWER_PAGE_IMAGE_B_OBSERVED_FINAL_AMENDMENT_PDF_PENDING")
        self.assertFalse(q["answerVerified"])
        self.assertFalse(q["questionVerified"])
        self.assertFalse(q["teachingVerified"])
        self.assertFalse(q["studentReady"])
        self.assertFalse(self.man["officialFinalCorrectionNoticeChecked"])

    def test_source_revision_digest_refuses_mutated_options_or_webp(self):
        q=self.q
        rev={k:q[k] for k in ("questionId","question","options","asset",
                             "originalQuestionPdfSha256RecordedOnly")}
        self.assertEqual(q["sourceRevisionSha256"],
            a.sha(a.canonical(rev).encode("utf-8")))
        altered=copy.deepcopy(rev)
        altered["options"][3]="齊物、無為，偽造"
        self.assertNotEqual(q["sourceRevisionSha256"],
            a.sha(a.canonical(altered).encode("utf-8")))
        altered=copy.deepcopy(rev)
        altered["asset"]["sha256"]="0"*64
        self.assertNotEqual(q["sourceRevisionSha256"],
            a.sha(a.canonical(altered).encode("utf-8")))

    def test_sqlite_exact_one_candidate_with_two_identical_import_sha(self):
        a.check(self.man)
        a.check_db(a.DB,self.man)
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"one.sqlite3";y=Path(td)/"two.sqlite3"
            a.make_db(x,self.man);a.make_db(y,self.man)
            self.assertEqual(a.sha(x.read_bytes()),a.sha(y.read_bytes()))
            self.assertEqual(a.sha(a.DB.read_bytes()),a.sha(x.read_bytes()))
        with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT answer_verified,question_verified,teaching_verified,student_ready FROM questions").fetchone(),
                (0,0,0,0))

    def test_prior_five_archived_webps_unmodified_and_no_new_release(self):
        prior=b.read(b.MANIFEST)
        self.assertEqual(len(prior["questions"]),5)
        for q in prior["questions"]:
            n=q["originalQuestionNumber"]
            with self.subTest(n=n):
                self.assertEqual(q["asset"]["sha256"],EXPECTED_01_05[n])
                self.assertEqual(a.sha((ROOT/q["asset"]["path"]).read_bytes()),EXPECTED_01_05[n])
                self.assertNotEqual(q["questionId"],a.QID)
        self.assertEqual(self.man["newQuestionVerified"],0)
        self.assertEqual(self.man["newAnswerVerified"],0)
        self.assertEqual(self.man["newTeachingVerified"],0)
        self.assertEqual(self.man["newReady"],0)
        self.assertEqual(self.man["newLive"],0)

if __name__=="__main__":
    unittest.main()
