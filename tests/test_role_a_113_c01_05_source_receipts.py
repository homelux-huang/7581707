"""Strict original 113 Chinese questions 1-5 candidate pixel/answer/SQL evidence; NEVER a release test."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageChops
from scripts import role_a_113_c01_05_source_pixels as a
ROOT=Path(__file__).resolve().parents[1]
class RoleA113C01To05SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man=a.read(a.MANIFEST)
        cls.doc,cls.paper,cls.source_raw,cls.answer_raw,_=a.source()
    def test_source_git_sha_and_recorded_pdf_sha_provenance(self):
        self.assertEqual(a.gitsha(self.source_raw),a.SRC_GIT)
        self.assertEqual(a.gitsha(self.answer_raw),a.ANS_GIT)
        self.assertEqual(self.man["sourcePdfSha256RecordedOnly"],a.SRC_PDF_RECORDED)
        self.assertEqual(self.man["answerPdfSha256RecordedOnly"],a.ANS_PDF_RECORDED)
        self.assertEqual(self.man["pdfRehashStatus"],"UNAVAILABLE_NOT_FRESHLY_DOWNLOADED")
        self.assertEqual(self.man["sourceIndex"],"https://web1.tcte.edu.tw/EXAM/113_4y/")
    def test_113_legacy_discovered_count_discrepancy_is_not_official_gap(self):
        self.assertEqual(len(self.doc["papers"]),5)
        self.assertEqual(sum(len(x["questions"]) for x in self.doc["papers"]),205)
        self.assertEqual(self.doc["questionsFound"],196)
        self.assertEqual(205-196,9)
        self.assertEqual(self.paper["expectedCount"],38)
        self.assertEqual(self.paper["discoveredCount"],38)
        self.assertEqual(self.paper["answerCount"],38)
    def test_question_ids_options_and_candidate_answers_no_promotion(self):
        self.assertEqual([q["questionId"] for q in self.man["questions"]],
            [f"113-00-C-{n:02d}" for n in range(1,6)])
        self.assertEqual("".join(q["answerCandidate"] for q in self.man["questions"]),"CDDCD")
        for n,q in enumerate(self.man["questions"],1):
            with self.subTest(number=n):
                orig=self.paper["questions"][n-1]
                self.assertEqual(q["originalQuestionNumber"],n)
                self.assertEqual(q["question"],orig["question"])
                self.assertEqual(q["options"],orig["options"])
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["answerCandidate"],orig["officialAnswerCandidate"])
                self.assertEqual(q["answerCandidate"],chr(ord("A")+orig["answer"]))
                self.assertFalse(q["answerVerified"])
                self.assertFalse(q["questionVerified"])
                self.assertFalse(q["teachingVerified"])
                self.assertFalse(q["studentReady"])
                self.assertEqual(q["individualImageQa"],"DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA")
                self.assertEqual(q["officialFinalAnswerQa"],"PENDING_CORRECTION_PDF_SCOPE")
    def test_five_lossless_same_source_pixels_not_repainted_no_whole_page(self):
        a.check(self.man)
        with Image.open(a.SOURCE) as img:
            img.load()
            for n,q in enumerate(self.man["questions"],1):
                with self.subTest(n=n):
                    box=q["asset"]["cropPixels"]
                    self.assertEqual(box,a.CROPS[n])
                    self.assertLess(box[3]-box[1],img.height/2)
                    self.assertGreater(box[2]-box[0],1000)
                    self.assertEqual(q["asset"]["originalPageSha256"],a.sha(self.source_raw))
                    self.assertTrue((ROOT/q["asset"]["path"]).exists())
                    with Image.open(ROOT/q["asset"]["path"]) as crop:
                        crop.load()
                        self.assertEqual(crop.format,"WEBP")
                        self.assertIsNone(ImageChops.difference(
                            crop.convert("RGB"),a.crop(img,box)).getbbox())
    def test_no_shared_article_in_q1_q5_and_crop_regions_do_not_overlap(self):
        bounds=[tuple(q["asset"]["cropPixels"]) for q in self.man["questions"]]
        self.assertEqual(len(set(bounds)),5)
        self.assertEqual(sorted(bounds,key=lambda x:x[1]),bounds)
        for l,r in zip(bounds,bounds[1:]):
            self.assertLess(l[3],r[1],"two original question croppings must not overlap")
        for q in self.man["questions"]:
            self.assertEqual(q["sharedMaterialIds"],[])
            self.assertNotIn("full-page",q["asset"]["path"])
    def test_partial_sqlite_hard_zero_qa_and_dual_replay_hash(self):
        a.check_db(a.DB,self.man)
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"x.sqlite3";y=Path(td)/"y.sqlite3"
            a.make_db(x,self.man);a.make_db(y,self.man)
            self.assertEqual(a.sha(x.read_bytes()),a.sha(y.read_bytes()))
            self.assertEqual(a.sha(a.DB.read_bytes()),a.sha(x.read_bytes()))
        with sqlite3.connect(a.DB.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("SELECT count(*) FROM questions").fetchone()[0],5)
            for row in db.execute("SELECT answer_verified,question_verified,teaching_verified,student_ready FROM questions"):
                self.assertEqual(tuple(row),(0,0,0,0))
    def test_negative_mutated_image_or_question_source_revision_is_rejected(self):
        q=copy.deepcopy(self.man["questions"][0])
        orig=q["sourceRevisionSha256"]
        q["options"][0]+=" forged"
        change={k:q[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
        self.assertNotEqual(orig,a.sha(a.canon(change).encode("utf-8")))
        self.assertNotEqual(a.sha(self.source_raw),a.sha(self.source_raw+b"wrong"))
        self.assertNotEqual(a.gitsha(self.answer_raw),a.gitsha(self.source_raw))
    def test_no_release_or_other_subject_canonical_artifacts_in_this_batch(self):
        m=self.man
        self.assertEqual(m["partialCandidateRows"],5)
        self.assertEqual(m["readyNew"],m["liveNew"])
        self.assertEqual(m["readyNew"],0)
        self.assertFalse(m["answerVerified"])
        self.assertFalse(m["questionVerified"])
        self.assertFalse(m["independentEReview"])
        self.assertFalse(m["uiQaVerified"])
        self.assertEqual({q["paperCode"] for q in m["questions"]},{"00-C"})
if __name__=="__main__":unittest.main()
