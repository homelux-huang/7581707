"""Role A strict original WebP receipt for 114 E11-14 + C04: no release/QA promotion.

Restores original Git blob bytes from canonical QA branch with no OCR, redraw or crop.
Author B's existing five authored lessons and E independent audit are not modified.
"""
import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path
from PIL import Image
from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
TARGETS = {
    "114-00-E-11": {
        "git": "50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a",
        "sha": "ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0",
        "revision": "646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036",
        "answer": "A",
        "page": 3,
        "qa": "114-english"
    },
    "114-00-E-12": {
        "git": "def397fcc0693d90de40b051fdf4c7c85b4567ce",
        "sha": "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60",
        "revision": "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec",
        "answer": "C",
        "page": 3,
        "qa": "114-english"
    },
    "114-00-E-13": {
        "git": "d3a37cc4ecb6c72b06fa19919a376a34203ed739",
        "sha": "81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7",
        "revision": "074fb9847eda936d31dfd4503f3a7a12cbde9f89ddc888957d8eba4f17fa746c",
        "answer": "A",
        "page": 3,
        "qa": "114-english"
    },
    "114-00-E-14": {
        "git": "2ec99e4912ac49b6c70e84183caadcdb402136bb",
        "sha": "388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94",
        "revision": "6164a310c7d38229aaaf52df678121ee88f6242cf6611310badfb5b1b46714dd",
        "answer": "D",
        "page": 3,
        "qa": "114-english"
    },
    "114-00-C-04": {
        "git": "88f92afe560b11335b57a7cf9e9a53882d47895c",
        "sha": "c16eb7b4768823a669d33456e1abd6829a83db968b8cd5e0ef2b519785b467d9",
        "revision": "2733f2bea0a32a99d6ec3d54d52c92a06962bec2b74a9a3350d30da5a5a31207",
        "answer": "D",
        "page": 2,
        "qa": "114-chinese"
    }
}
GIT_QA_ENG = "c1154562fa30cb4b2720a6000a970cf09ef460ff"
GIT_QA_CN = "6e86d5143787a9389387fd0d607fb7899424bc1b"
PDF_ENG_RECORDED = "1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf"
PDF_CN_RECORDED = "f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def check_webp(relative, expected, dimensions):
    path = ROOT / relative
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", relative
    assert sha256(data) == expected, "SHA drift " + relative
    with Image.open(path) as img:
        assert img.format == "WEBP"
        img.load()
        assert img.size == tuple(dimensions), (relative, img.size, dimensions)
    return len(data)

class RoleA114B2OriginalWebps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bank = read(BASE / "questions.json")
        man = read(BASE / "webp-manifest.json")
        cls.q = {r["questionId"]: r for r in bank["questions"]}
        cls.images = {r["questionId"]: r for r in man["items"]}
        assert len(bank["questions"]) == len(cls.q) == 205
        assert len(man["items"]) == len(cls.images) == 205
        assert cls.q.keys() == cls.images.keys()
        cls.qa_eng_file = BASE / "QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
        cls.qa_cn_file = BASE / "VISUAL_QA_BATCH_01_2026-10-22.json"
        cls.qa_eng = read(cls.qa_eng_file)
        cls.qa_cn = read(cls.qa_cn_file)
        cls.qe = {r["questionId"]: r for r in cls.qa_eng["items"]}
        cls.qc = {r["questionId"]: r for r in cls.qa_cn["records"]}

    def test_all_five_original_archived_webps_have_exact_git_blob_and_decoding(self):
        for qid, pin in TARGETS.items():
            with self.subTest(qid=qid):
                image = self.images[qid]
                self.assertEqual(image["qaStatus"], "PASS")  # historical record, not newly promoted
                self.assertEqual(image["sha256"], pin["sha"])
                self.assertEqual(self.q[qid]["assets"]["imageQaEvidence"], "sudu/data/processed/114/" + ("VISUAL_QA_BATCH_01_2026-10-22.json" if pin["qa"]=="114-chinese" else "QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"))
                self.assertEqual(self.q[qid]["questionProvenance"]["webpSha256"], pin["sha"])
                self.assertEqual(self.q[qid]["assets"]["singleQuestionWebp"], image["output"])
                original_bytes = (ROOT / image["output"]).read_bytes()
                self.assertEqual(git_blob_sha(original_bytes), pin["git"])
                self.assertGreater(check_webp(image["output"], pin["sha"], image["outputSize"]), 0)
                self.assertEqual(image["visualReviewEvidence"]["reviewedSha256"], pin["sha"])

    def test_historical_original_page_crops_and_recorded_official_paper_shas(self):
        for qid,pin in TARGETS.items():
            with self.subTest(qid=qid):
                im = self.images[qid]
                q = self.q[qid]
                self.assertEqual(im["sourcePage"], pin["page"])
                self.assertEqual(q["sourcePage"], pin["page"])
                self.assertEqual(im["sourcePdfSha256"], PDF_CN_RECORDED if pin["qa"]=="114-chinese" else PDF_ENG_RECORDED)
                self.assertEqual(q["questionProvenance"]["officialPdfSha256"], im["sourcePdfSha256"])
                self.assertEqual(q["questionProvenance"]["pixelSourceSha256"], im["sourceSha256"])
                self.assertGreater(check_webp(im["source"], im["sourceSha256"], im["sourceSize"]), 0)
                self.assertEqual(im["crop"], (self.qc[qid]["cropPixels"] if pin["qa"]=="114-chinese" else self.qe[qid]["cropPixels"]))
                self.assertEqual(im["outputSize"], [im["crop"][2]-im["crop"][0], im["crop"][3]-im["crop"][1]])

    def test_two_original_visual_qa_documents_exact_git_blobs_and_ai_scope(self):
        self.assertEqual(git_blob_sha(self.qa_eng_file.read_bytes()), GIT_QA_ENG)
        self.assertEqual(git_blob_sha(self.qa_cn_file.read_bytes()), GIT_QA_CN)
        self.assertEqual(self.qa_eng["passedQuestionWebp"], 15)  # original archival record ONLY
        self.assertIs(self.qa_eng["independentHumanReview"], False)
        self.assertIs(self.qa_eng["releaseAllowed"], False)
        self.assertIs(self.qa_cn["independentHumanReview"], False)
        self.assertEqual(self.qa_cn["scope"], "Image only; no official answer confirmation")
        # Crucial: importing batch evidence never turns other failed crops into PASS.
        self.assertEqual(self.qc["114-00-C-01"]["result"], "FAIL_HEADER_FRAGMENT")
        self.assertEqual(self.qa_eng["answerVerifiedAdded"], 0)
        self.assertEqual(self.qa_eng["questionVerifiedAdded"], 0)

    def test_exact_individual_visual_criteria_and_crop_sha_match_not_batch_pass(self):
        for qid,pin in TARGETS.items():
            with self.subTest(qid=qid):
                im=self.images[qid]
                if pin["qa"]=="114-english":
                    qa=self.qe[qid]
                    self.assertEqual(qa["reviewedWebpSha256"], pin["sha"])
                    self.assertEqual(qa["reviewedWebpPath"], im["output"])
                    self.assertEqual(qa["sourcePageSha256"], im["sourceSha256"])
                    self.assertEqual(qa["cropPixels"], im["crop"])
                    self.assertEqual(qa["result"], "PASS")
                    self.assertTrue(all(qa["criteria"].values()))
                    self.assertIs(qa["independentHumanReview"], False)
                    self.assertIs(qa["answerVerified"], False)
                    self.assertIs(qa["questionVerified"], False)
                else:
                    qa=self.qc[qid]
                    self.assertEqual(qa["webpSha256"], pin["sha"])
                    self.assertEqual(qa["webpPath"], im["output"])
                    self.assertEqual(qa["sourceSha256"], im["sourceSha256"])
                    self.assertEqual(qa["cropPixels"], im["crop"])
                    self.assertEqual(qa["result"], "PASS")

    def test_five_source_revisions_match_existing_role_b_author_digest_source(self):
        for qid,pin in TARGETS.items():
            with self.subTest(qid=qid):
                q=self.q[qid]
                self.assertEqual(q["paperCode"], "00-C" if pin["qa"]=="114-chinese" else "00-E")
                self.assertEqual(q["answer"], pin["answer"])
                self.assertEqual(len(q["options"]),4)
                self.assertTrue(all(isinstance(v,str) and v.strip() for v in q["options"]))
                self.assertEqual(publisher.text_revision(q,pin["sha"]), pin["revision"])

    def test_negatives_wrong_image_sha_size_and_question_option_invalidate(self):
        for qid,pin in TARGETS.items():
            with self.subTest(qid=qid):
                im=self.images[qid]
                with self.assertRaises(AssertionError):
                    check_webp(im["output"], "0"*64, im["outputSize"])
                with self.assertRaises(AssertionError):
                    check_webp(im["output"], pin["sha"], [0,0])
                original=publisher.text_revision(self.q[qid],pin["sha"])
                bad=copy.deepcopy(self.q[qid])
                bad["options"][3] += " malicious-extra"
                self.assertNotEqual(publisher.text_revision(bad,pin["sha"]), original)
                self.assertEqual(publisher.source_proof(self.q[qid],True,True,original), (False,False))

    def test_all_205_canonical_sqlite_payload_hashes_and_json_roundtrip(self):
        path=BASE/"question-bank.sqlite3"
        with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as conn:
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            cols={x[1] for x in conn.execute("PRAGMA table_info(questions)")}
            field="payload" if "payload" in cols else "payload_json"
            self.assertTrue({"question_id",field,"payload_sha256"}<=cols)
            data=conn.execute("SELECT question_id,"+field+",payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(data),205)
        self.assertEqual({r[0] for r in data},set(self.q))
        for qid,payload,digest in data:
            with self.subTest(qid=qid):
                self.assertEqual(sha256(payload.encode("utf-8")),digest)
                self.assertEqual(json.loads(payload),self.q[qid])

    def test_no_final_answer_pedagogy_teacher_or_student_release_approval(self):
        approved=read(ROOT/"sudu/data/approved/114.json")
        self.assertEqual(approved["approvedCount"], 0)
        for qid in TARGETS:
            with self.subTest(qid=qid):
                q=self.q[qid]
                self.assertIs(q["answerMatched"], True)
                self.assertIs(q["answerVerified"], False)
                self.assertIs(q["questionVerified"], False)
                self.assertIsNot(q.get("studentReleaseApproved"), True)
                self.assertIsNot(q.get("integrationReady"), True)

if __name__=="__main__":
    unittest.main()
