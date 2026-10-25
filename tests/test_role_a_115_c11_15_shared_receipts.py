"""Role A source-only receipt: 115 C11-C15 original images and shared C11-15 passage.

Only exact historically QA-reviewed source pixels. C15 text carries next-page contamination:
DO NOT upgrade questionVerified/READY from the image-only QA record.
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
BASE = ROOT / "sudu/data/processed/115"
SRC_PDF_RECORDED = "6b454d65902f2fb326b1ac1ae28aa44749532e30369ba2c599db97d20a542135"
ANS_PDF_RECORDED = "ec9871b659d81726de5b6412ed5252d62541afb287951b5d6cf923c1ea763e64"
NOTICE_PDF_RECORDED = "231f21ac52bb1006717ec6a17b325454a37269317a1f49944dbfd0a31d28c4c0"
ANSWER_PAGE_SHA = "5422c00920ef4f18fa32fffd51c7edb78acd80aac84974713a61e2a02987126f"
ARCHIVED_IMAGE_QA_BLOB = "fca5b8e9e16b390f245c93caeb420b4b86f97f60"
ARCHIVED_ANSWER_QA_BLOB = "250ed2949b54099ee86511e0d1c4bcf69f33c9be"
ORIGINAL_EXAM_PAGE_4 = "b317ce491d6849193572adc6e96c255d0074bfe6c54246e8638a754432df7808"
ORIGINAL_EXAM_PAGE_5 = "bf0678abeeddb131a843fe0461182a3a15ffaf836461933539dc3db1602cd98b"
SHARED_ID = "115-00-C-SHARED-11-15"
SHARED_PATH = "sudu/data/processed/115/webp-v3/shared/115-00-C-SHARED-11-15.webp"
SHARED_ORIGINAL_GIT = "faee3ef1ca6371a769492d568ecf086f268a3cda"
SHARED_SHA = "bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66"

IMAGE_PINS = {
    11: ("12feb2dbeca7ad4c412a0476747e87a0fc6a916e","101bcdaf6b77f421fa0a20a2220a0e592e7fdd6a28595f0b58ec46eda4c767ce","D",[90,157,1310,360]),
    12: ("9859591671be246b45ffb17e8afb6ec49e8281c3","ac9b20198dea3530262fa9c35b2ecd46e17d1ef8a05a705d2c4255a243dc7f5e","C",[90,362,1310,565]),
    13: ("6b525bc2613f3368c26cdfece23a7992d4786a73","575c1ecd856e31d4c861f675225ecc553c2c4d4060ba7534a8eaa24fa0eba82f","D",[90,567,1310,770]),
    14: ("4ed65dce400df50e254df96a7d189cc2d0fbd3b8","2d5d49607eb941df0f6ed272447a312723bfbf050555f53deb1e0cd675a1888e","B",[90,772,1310,1421]),
    15: ("2ea856c923d21743272d28ef5318d638f96d937b","74dc7bb966f1ee508456a962a6fbcff0f42a15b2ffdd8db747477a55b831405f","B",[90,1421,1310,1660]),
}
ROLE_C_REV = {
    11: "8802bc8fa44af457c25fcca5a784aec60b0c05bfa9969cac4eca9d431cabee71",
    12: "c4e6891c02cd68e3b0af38b178cbd96a9453b057fc88092398fd03af9bc3fa92",
    13: "5261e86bcd01822edc85c38b4df86be4f1477fa885310d8be37abec183e65225",
}

def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def check_image(path, expected_sha, dimensions):
    b = (ROOT/path).read_bytes()
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", path
    assert sha(b) == expected_sha, "corrupted WebP SHA "+path
    with Image.open(ROOT/path) as im:
        assert im.format == "WEBP"
        im.load()
        assert im.size == tuple(dimensions), (path, im.size, dimensions)
    return b

class C11To15ImmutableOriginalReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bank = read("sudu/data/processed/115/questions.json")
        man = read("sudu/data/processed/115/webp-manifest.json")
        cls.bank = {q["questionId"]:q for q in bank["questions"]}
        cls.man = {m["questionId"]:m for m in man["items"]}
        assert len(cls.bank) == len(cls.man) == len(bank["questions"]) == len(man["items"]) == 205
        assert set(cls.bank) == set(cls.man)
        cls.shared = {s["sharedMaterialId"]:s for s in man["sharedMaterialCrops"]}
        cls.original_visual_file = "sudu/data/processed/115/QA_115_C_Q06_Q11_15_DIRECT_VISUAL_20261023.json"
        cls.original_answer_file = "sudu/data/processed/115/QA_115_C_6_FINAL_OFFICIAL_ANSWERS_20261023.json"
        cls.imageqa = read(cls.original_visual_file)
        cls.official = read(cls.original_answer_file)
        cls.visual_by_id = {i["questionId"]:i for i in cls.imageqa["items"]}
        cls.answer_by_id = {i["questionId"]:i for i in cls.official["records"]}

    def test_exact_five_original_git_webps_and_per_image_qa(self):
        for n,(original_git,original_sha,_,crop) in IMAGE_PINS.items():
            qid=f"115-00-C-{n:02d}"
            with self.subTest(qid=qid):
                m=self.man[qid]
                self.assertEqual(m["output"], f"sudu/data/processed/115/webp-v2/00-C/{qid}.webp")
                self.assertEqual(m["sha256"],original_sha)
                self.assertEqual(m["crop"],crop)
                self.assertEqual(m["outputSize"],[crop[2]-crop[0],crop[3]-crop[1]])
                self.assertEqual(m["qaStatus"],"PASS") # prior archived AI visual pass only
                raw=check_image(m["output"],original_sha,m["outputSize"])
                self.assertEqual(git_blob(raw),original_git)
                self.assertEqual(m["visualReviewEvidence"]["reviewedSha256"],original_sha)
                self.assertEqual(self.bank[qid]["assets"]["sha256"],original_sha)

    def test_real_official_question_page_sha_and_exact_crop_binding(self):
        checked=set()
        for n,(_,_,_,crop) in IMAGE_PINS.items():
            qid=f"115-00-C-{n:02d}"
            with self.subTest(qid=qid):
                q,m=self.bank[qid],self.man[qid]
                self.assertEqual(m["sourcePage"],5)
                self.assertEqual(m["sourcePdfSha256"],SRC_PDF_RECORDED)
                self.assertEqual(q["questionProvenance"]["pdfSha256"],SRC_PDF_RECORDED)
                self.assertEqual(q["assets"]["sourceSha256"],ORIGINAL_EXAM_PAGE_5)
                self.assertEqual(m["sourceSha256"],ORIGINAL_EXAM_PAGE_5)
                self.assertEqual(q["sharedMaterialId"],SHARED_ID)
                self.assertEqual(q["assets"]["singleQuestionWebp"],m["output"])
                self.assertEqual(q["assets"]["cropCoordinates"],crop)
                self.assertEqual(q["questionProvenance"]["sourcePage"],5)
                if m["source"] not in checked:
                    check_image(m["source"],ORIGINAL_EXAM_PAGE_5,m["sourceSize"])
                    checked.add(m["source"])
        self.assertEqual(len(checked),1)

    def test_shared_v3_complete_article_original_blob_historical_pass_not_new_approval(self):
        im=self.shared[SHARED_ID]
        self.assertEqual(im["output"],SHARED_PATH)
        self.assertEqual(im["sha256"],SHARED_SHA)
        self.assertEqual(im["sourceSha256"],ORIGINAL_EXAM_PAGE_4)
        self.assertEqual(im["sourcePdfSha256"] if "sourcePdfSha256" in im else SRC_PDF_RECORDED,SRC_PDF_RECORDED)
        self.assertEqual(im["sourcePage"],4)
        self.assertEqual(im["crop"],[90,160,1310,1530])
        self.assertEqual(im["outputSize"],[1220,1370])
        self.assertEqual(im["qaStatus"],"PASS") # historical AI only, not E teaching review
        self.assertEqual(im["processingVersion"],"v3-visual-review-draft-source-pixel-only")
        raw=check_image(SHARED_PATH,SHARED_SHA,[1220,1370])
        self.assertEqual(git_blob(raw),SHARED_ORIGINAL_GIT)
        check_image(im["source"],ORIGINAL_EXAM_PAGE_4,im["sourceSize"])
        self.assertEqual(im["visualReviewEvidence"]["reviewedSha256"],SHARED_SHA)

    def test_historical_qa_two_original_documents_pinned_and_scope_separate(self):
        self.assertEqual(git_blob((ROOT/self.original_visual_file).read_bytes()),ARCHIVED_IMAGE_QA_BLOB)
        self.assertEqual(git_blob((ROOT/self.original_answer_file).read_bytes()),ARCHIVED_ANSWER_QA_BLOB)
        self.assertFalse(self.imageqa["independentHumanReview"])
        self.assertFalse(self.official["independentHumanReview"])
        self.assertFalse(self.imageqa["releaseAllowed"])
        self.assertFalse(self.official["releaseAllowed"])
        self.assertEqual(self.imageqa["answerVerifiedAdded"],0)
        self.assertEqual(self.imageqa["questionVerifiedAdded"],0)
        self.assertEqual(self.official["questionVerifiedAdded"],0)
        shared=next(x for x in self.imageqa["sharedMaterials"] if x["sharedMaterialId"]==SHARED_ID)
        self.assertEqual(shared["reviewedWebpPath"],SHARED_PATH)
        self.assertEqual(shared["reviewedWebpSha256"],SHARED_SHA)
        self.assertEqual(shared["sourcePageSha256"],ORIGINAL_EXAM_PAGE_4)
        self.assertEqual(shared["cropPixels"],[90,160,1310,1530])
        self.assertEqual(shared["result"],"PASS")
        self.assertTrue(all(shared["criteria"].values()))
        self.assertFalse(shared["independentHumanReview"])

    def test_each_original_question_visual_qa_and_official_published_answer(self):
        for n,(_,digest,letter,crop) in IMAGE_PINS.items():
            id_=f"115-00-C-{n:02d}"
            with self.subTest(qid=id_):
                q,qa,ans=self.bank[id_],self.visual_by_id[id_],self.answer_by_id[id_]
                self.assertEqual(qa["result"],"PASS")
                self.assertEqual(qa["cropPixels"],crop)
                self.assertEqual(qa["sourcePageSha256"],ORIGINAL_EXAM_PAGE_5)
                self.assertEqual(qa["reviewedWebpSha256"],digest)
                self.assertEqual(qa["reviewedWebpPath"],self.man[id_]["output"])
                self.assertTrue(all(qa["criteria"].values()))
                self.assertFalse(qa["independentHumanReview"])
                self.assertFalse(qa["answerVerified"]) # AI image QA does not sign off answer
                self.assertEqual(q["answer"],letter)
                self.assertEqual(ans["candidateValue"],letter)
                self.assertEqual(ans["officialPublishedFinalAnswer"],letter)
                self.assertEqual(ans["officialPublishedAnswerImageSha256"],ANSWER_PAGE_SHA)
                self.assertEqual(ans["officialPublishedAnswerSourcePdfSha256"],ANS_PDF_RECORDED)
                self.assertEqual(ans["officialConfirmationDocumentSha256"],NOTICE_PDF_RECORDED)
                self.assertTrue(ans["officialCorrectionChecked"])
                self.assertTrue(ans["officialFinalAnswerImageDirectVisualChecked"])
                self.assertTrue(ans["answerVerified"]) # old independent official stage, not new
                self.assertFalse(ans["questionVerified"])
                self.assertTrue(q["answerVerified"])
                self.assertFalse(q["questionVerified"])

    def test_q12_notice_explicit_c_others_not_whole_paper(self):
        self.assertEqual(self.answer_by_id["115-00-C-12"]["officialNoticeStatus"],
                         "EXPLICITLY_CONFIRMED_QUESTION_12_ANSWER_C_PAGES_1_2")
        for n in (11,13,14,15):
            self.assertEqual(self.answer_by_id[f"115-00-C-{n:02d}"]["officialNoticeStatus"],
                             "NO_ENTRY_IN_FULL_10_PAGE_00_C_CONFIRMATION_PDF")
        answer_im=self.official["originalFinalAnswerPageWebp"]
        check_image(answer_im,ANSWER_PAGE_SHA,[1400,1980])
        confirmation=read("sudu/data/processed/115/QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json")
        doc=next(x for x in confirmation["docs"] if x["paperCode"]=="00-C")
        self.assertEqual(doc["pdfSha256"],NOTICE_PDF_RECORDED)
        self.assertEqual({x["questionId"] for x in doc["confirmed"]},
                         {"115-00-C-12","115-00-C-16","115-00-C-18","115-00-C-23","115-00-C-24","115-00-C-34"})

    def test_role_c_exact_source_revision_not_independent_lesson_approval(self):
        for n,rev in ROLE_C_REV.items():
            qid=f"115-00-C-{n:02d}"
            with self.subTest(qid=qid):
                self.assertEqual(publisher.text_revision(self.bank[qid],self.man[qid]["sha256"]),rev)
                bad=copy.deepcopy(self.bank[qid])
                bad["options"][0]="TAMPERED SOURCE TEXT"
                self.assertNotEqual(publisher.text_revision(bad,self.man[qid]["sha256"]),rev)
        for n in IMAGE_PINS:
            qid=f"115-00-C-{n:02d}"
            self.assertFalse(self.bank[qid]["questionVerified"])
            self.assertFalse(self.bank[qid]["integrationReady"])
            self.assertEqual(publisher.source_proof(self.bank[qid],True,True,
                              publisher.text_revision(self.bank[qid],self.man[qid]["sha256"])),(False,False))

    def test_q15_cross_page_text_pollution_remains_quarantined_not_pass(self):
        q=self.bank["115-00-C-15"]
        self.assertEqual(len(q["options"]),4)
        self.assertTrue(q["options"][3].startswith("拘泥禮法 ／ 不知變通"))
        # Genuine newly identified source-text defect: D appends p5 footer and p6 Q16-18 article.
        self.assertIn("▲閱讀下文，回答第16-18 題",q["options"][3])
        self.assertIn("公告試題僅供參考",q["options"][3])
        self.assertFalse(q["questionVerified"])
        self.assertFalse(q["integrationReady"])
        self.assertEqual(q["assets"]["visualQa"],"PENDING_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(q["imageQaStatus"],"PASS") # image-only historical
        self.assertNotEqual("PASS_TEXT",q.get("ocrTextQaStatus"))
        with self.assertRaises(AssertionError):
            check_image(self.man["115-00-C-15"]["output"],"0"*64,[1220,239])
        with self.assertRaises(AssertionError):
            check_image(SHARED_PATH,SHARED_SHA,[1220,1371])

    def test_205_sqlite_rows_match_canonical_exactly_without_promotion(self):
        path=BASE/"question-bank.sqlite3"
        with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
            field="payload" if "payload" in cols else "payload_json"
            self.assertTrue({"question_id",field,"payload_sha256"}<=cols)
            rows=db.execute("SELECT question_id,"+field+",payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({r[0] for r in rows},set(self.bank))
        for qid,raw,digest in rows:
            with self.subTest(qid=qid):
                self.assertEqual(sha(raw.encode("utf-8")),digest)
                self.assertEqual(json.loads(raw),self.bank[qid])
        approved=read("sudu/data/approved/115.json")
        self.assertEqual(approved["approvedCount"],5)
        for n in IMAGE_PINS:
            self.assertNotIn(f"115-00-C-{n:02d}",{x["canonicalId"] for x in approved["questions"]})

if __name__=="__main__":
    unittest.main()
