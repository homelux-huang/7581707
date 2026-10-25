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
    def test_actual_five_individual_image_visual_qa_receipt_exact_sha_no_self_e(self):
        receipt=ROOT/"sudu/data/processed/113/role-a-c01-05/VISUAL_QA_ASSISTANT_20261025.json"
        self.assertTrue(receipt.exists())
        data=a.read(receipt)
        self.assertEqual(data["taskId"],a.TASK)
        self.assertEqual(data["originalPageWebpSha256"],self.man["originalPage"]["sha256"])
        self.assertEqual(data["originalOfficialAnswerPageWebpSha256"],self.man["answerPage"]["sha256"])
        self.assertFalse(data["officialFinalAnswerApproved"])
        self.assertFalse(data["pdfByteRehashPerformed"])
        self.assertFalse(data["lessonContentReviewedByE"])
        self.assertFalse(data["sourceQuestionVerifiedPromoted"])
        self.assertFalse(data["finalPerNumberCorrectionNoticeChecked"])
        self.assertEqual(data["newImageOnlyAssistantPassCount"],5)
        self.assertEqual(data["newReady"],data["newLive"])
        self.assertEqual(data["newLive"],0)
        reviewed={q["questionId"]:q for q in data["questions"]}
        self.assertEqual(len(reviewed),5)
        for q in self.man["questions"]:
            with self.subTest(q=q["questionId"]):
                r=reviewed[q["questionId"]]
                self.assertEqual(r["assetSha256"],q["asset"]["sha256"])
                self.assertEqual(r["assetGitBlobSha1"],q["asset"]["gitBlobSha1"])
                self.assertEqual(r["originalPageWebpSha256"],self.man["originalPage"]["sha256"])
                self.assertEqual(r["assetPath"],q["asset"]["path"])
                self.assertEqual(r["cropPixels"],q["asset"]["cropPixels"])
                self.assertEqual(r["publishedAnswerImageCandidate"],q["answerCandidate"])
                self.assertEqual(r["reviewResult"],"PASS_ASSISTANT_DIRECT_ORIGINAL_PIXEL_VISUAL_QA")
                self.assertEqual(r["reviewerRole"],"A_SOURCE_ONLY")
                self.assertFalse(r["independentHumanReview"])
                self.assertFalse(r["independentRoleEContentReview"])
                self.assertTrue(all(r["criteria"].values()))
                self.assertGreater(len(r["note"]),15)
                # Image QA is real but cannot promote the candidate DB or official answer.
                self.assertFalse(q["questionVerified"])
                self.assertFalse(q["answerVerified"])
                self.assertFalse(q["studentReady"])
                self.assertEqual(q["individualImageQa"],"DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA")
    def test_rejected_prior_c05_adjacent_crop_sha_is_not_current(self):
        qa=a.read(ROOT/"sudu/data/processed/113/role-a-c01-05/VISUAL_QA_ASSISTANT_20261025.json")
        rejected=qa["wrongPreviousCrop"]
        self.assertEqual(rejected["questionId"],"113-00-C-05")
        self.assertEqual(rejected["result"],"FAIL_MIXED_NEXT_QUESTION")
        self.assertEqual(rejected["originalCropPixels"],[90,1085,1310,1475])
        self.assertEqual(rejected["sha256"],
            "c749bb5993921d303fc8d59b1c849b2a68f366dbb4e3ff76696d9830b4626a81")
        current=self.man["questions"][4]
        self.assertEqual(current["asset"]["cropPixels"],[90,1085,1310,1450])
        self.assertEqual(current["asset"]["sha256"],
            "ff1f548bead9b1850688f99b74e1946e2a2e0f5f1c83b299b5002801a51e9cd3")
        self.assertNotEqual(rejected["sha256"],current["asset"]["sha256"])
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
