"""Exact original 115 English E29/E39-41 and two unapproved shared-passage receipts.

Only restores original QA-archived Git WebP objects, no new visual PASS,
no re-OCR, new blind, answer verification or teacher/student release.
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
IMAGE_IDS = (29, 39, 40, 41)
DETAILS = {
    29: {"git": "122436f959d7ed8ce5e8c2f8f5e5c2711f81f889",
         "sha": "200722eaba0530fc8f3963cfe9c72e2749630de188ad538d5ce23200d949717d",
         "page": 6, "source": "b34b9c3c8d94d8d54589634a4403cfa14810b8736e1a9a3202b240a1490423df",
         "crop": [90,1510,1310,1630], "sourceRevision": "23952dc29ed2622029cce5b7a431e4c9209ca99c41f25fc7eea5b15af56f883d",
         "shared": "115-00-E-SHARED-29-30", "answer": "A"},
    39: {"git": "6af1245cc9e866192eef312be9c3463739b31282",
         "sha": "0e71395b101b6e255d48b3eea86e8a4a1086cafabab62104ade3474b32f11d3c",
         "page": 10, "source": "6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c",
         "crop": [90,982,1310,1167], "sourceRevision": "9a098b1db2de04ecdf3af694a686e30a573ba4d63356dbf1dfe39e7ea230956a",
         "shared": "115-00-E-SHARED-39-42", "answer": "B"},
    40: {"git": "63a608f38943cd3919afb31a628cd00b2104ad93",
         "sha": "afa2a88eb2574bae17aad8d4a16f662e889b906f024b8950e45439f12210fbef",
         "page": 10, "source": "6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c",
         "crop": [90,1166,1310,1318], "sourceRevision": "1066b79c8271d1882e9f443609665de1dab0f6a0a49553349e1d65904091fb31",
         "shared": "115-00-E-SHARED-39-42", "answer": "D"},
    41: {"git": "cfb8001f89418c2f5a12cf7c68384aa9d48230a4",
         "sha": "b10a8ba84292df22dc481107280522e8f8dc168ef0496f9af3f4bf71329740a4",
         "page": 10, "source": "6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c",
         "crop": [90,1317,1310,1437], "sourceRevision": "b5b2282057f093845c8745986a9e034e1bdfb6e6df10c18ab8d445507a68f0fd",
         "shared": "115-00-E-SHARED-39-42", "answer": "D"},
}
SHARED = {
    "115-00-E-SHARED-29-30": {
        "path": "sudu/data/processed/115/webp-v2/shared/115-00-E-SHARED-29-30.webp",
        "git": "1938fe2a22233a82528c111547ec3f1a522d201b",
        "sha": "e932d3fc246b55604cabd6fa1716d0fa6f8f67d658ed6a16c6d88f91bfdb49b6",
        "source": "b34b9c3c8d94d8d54589634a4403cfa14810b8736e1a9a3202b240a1490423df",
        "crop": [90,165,1310,1498], "page": 6},
    "115-00-E-SHARED-39-42": {
        "path": "sudu/data/processed/115/webp-v3/shared/115-00-E-SHARED-39-42.webp",
        "git": "4aaac02b7ed9390b8ff7c8a4c4272e74996bd595",
        "sha": "5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b",
        "source": "6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c",
        "crop": [90,166,1310,978], "page": 10},
}
ORIGINAL_PDF_SHA_RECORDED = "c13e298c3b05b890c410deac4f8f694905f19fcd3a63bb4fcc0662ee6cb2768a"
ORIGINAL_B2_GIT = "1b3b0f7667dd1534b385698d5875d74c0db768cf"
ORIGINAL_B2_SHA = "9a28eefef299d2b50f81c623cd4316b51f0091c0ecb705055c8bf12ba1815aa5"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def original_webp(path, digest, dimensions):
    p = ROOT/path
    raw = p.read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", path
    assert sha(raw) == digest, "altered WebP: "+path
    with Image.open(p) as im:
        assert im.format == "WEBP"
        im.load()
        assert im.size == tuple(dimensions), (path,im.size,dimensions)
    return len(raw)

class RoleA115EnglishSharedOriginalReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = read(BASE / "questions.json")
        m = read(BASE / "webp-manifest.json")
        cls.q = {x["questionId"]:x for x in b["questions"]}
        cls.im = {x["questionId"]:x for x in m["items"]}
        assert len(b["questions"]) == len(m["items"]) == len(cls.q) == len(cls.im) == 205
        assert set(cls.q) == set(cls.im)
        cls.shared = {x["sharedMaterialId"]:x for x in m["sharedMaterialCrops"]}
        qa = BASE / "VISUAL_QA_2026-10-22_B2.json"
        raw = qa.read_bytes()
        assert git_sha(raw) == ORIGINAL_B2_GIT
        assert sha(raw) == ORIGINAL_B2_SHA
        cls.b2 = read(qa)
        cls.b2_by_id = {x["questionId"]:x for x in cls.b2["questions"]}

    def test_all_four_original_question_webps_are_same_immutable_git_blob_and_exact_sha(self):
        for n, pin in DETAILS.items():
            qid = f"115-00-E-{n:02d}"
            with self.subTest(qid=qid):
                item = self.im[qid]
                self.assertEqual(item["qaStatus"],"PASS")  # original individual historical AI QA
                self.assertEqual(item["output"],f"sudu/data/processed/115/webp-v2/00-E/{qid}.webp")
                self.assertEqual(item["sha256"],pin["sha"])
                self.assertEqual(item["sourcePage"],pin["page"])
                self.assertEqual(item["crop"],pin["crop"])
                self.assertEqual(item["outputSize"],[pin["crop"][2]-pin["crop"][0],pin["crop"][3]-pin["crop"][1]])
                raw = (ROOT/item["output"]).read_bytes()
                self.assertEqual(git_sha(raw),pin["git"])
                self.assertGreater(original_webp(item["output"],pin["sha"],item["outputSize"]),0)
                self.assertEqual(item["visualReviewEvidence"]["reviewedSha256"],pin["sha"])
                self.assertFalse(item["visualReviewEvidence"]["independentHumanReview"])

    def test_exact_original_english_page_pixel_sha_and_pdf_provenance(self):
        checked = set()
        for n,pin in DETAILS.items():
            qid = f"115-00-E-{n:02d}"
            with self.subTest(qid=qid):
                q,im=self.q[qid],self.im[qid]
                self.assertEqual(im["sourceSha256"],pin["source"])
                self.assertEqual(q["assets"]["sourceSha256"],pin["source"])
                self.assertEqual(q["questionProvenance"]["pdfSha256"],ORIGINAL_PDF_SHA_RECORDED)
                self.assertEqual(im["sourcePdfSha256"],ORIGINAL_PDF_SHA_RECORDED)
                self.assertEqual(q["questionProvenance"]["sourcePage"],pin["page"])
                self.assertEqual(q["assets"]["singleQuestionWebp"],im["output"])
                self.assertEqual(q["assets"]["sha256"],pin["sha"])
                self.assertEqual(q["assets"]["cropCoordinates"],pin["crop"])
                self.assertEqual(q["sharedMaterialId"],pin["shared"])
                if im["source"] not in checked:
                    self.assertGreater(original_webp(im["source"],pin["source"],im["sourceSize"]),0)
                    checked.add(im["source"])
        self.assertEqual(len(checked),2)

    def test_two_original_shared_passage_candidates_exist_but_must_remain_unapproved(self):
        for sid,pin in SHARED.items():
            with self.subTest(sharedMaterialId=sid):
                im=self.shared[sid]
                self.assertEqual(im["output"],pin["path"])
                self.assertEqual(im["sha256"],pin["sha"])
                self.assertEqual(im["sourceSha256"],pin["source"])
                self.assertEqual(im["sourcePage"],pin["page"])
                self.assertEqual(im["crop"],pin["crop"])
                self.assertEqual(im["qaStatus"],"DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA")
                self.assertNotEqual(im["qaStatus"],"PASS")
                self.assertTrue(im["issues"])
                raw=(ROOT/pin["path"]).read_bytes()
                self.assertEqual(git_sha(raw),pin["git"])
                dims=[pin["crop"][2]-pin["crop"][0],pin["crop"][3]-pin["crop"][1]]
                self.assertGreater(original_webp(pin["path"],pin["sha"],dims),0)
                # Two source-pixel-cropped shared passages are candidates, NOT accepted reading material.
                self.assertNotEqual((im.get("visualReviewEvidence") or {}).get("reviewedSha256"),pin["sha"])

    def test_per_question_historical_b2_pass_only_and_real_qa_unchanged(self):
        self.assertEqual(self.b2["records"],60)
        for n,pin in DETAILS.items():
            id_=f"115-00-E-{n:02d}"
            with self.subTest(qid=id_):
                qa=self.b2_by_id[id_]
                self.assertEqual(qa["result"],"PASS_ASSISTANT_VISUAL_QA")
                self.assertEqual(qa["sourceSha256"],pin["source"])
                self.assertEqual(qa["assetSha256"],pin["sha"])
                self.assertEqual(qa["asset"],self.im[id_]["output"])
                self.assertEqual(qa["crop"],pin["crop"])
                self.assertTrue(qa["allFourOptionsComplete"])
                self.assertTrue(qa["contentComplete"])
                self.assertTrue(qa["noAdjacentQuestion"])
                self.assertTrue(qa["noWholePage"])
                self.assertFalse(qa["secondHumanReview"])
                self.assertEqual(self.im[id_]["visualReviewEvidence"]["referenceSha256"],ORIGINAL_B2_SHA)

    def test_existing_separate_C_author_source_revision_matches_without_approval(self):
        for n,pin in DETAILS.items():
            qid=f"115-00-E-{n:02d}"
            q=self.q[qid]
            with self.subTest(qid=qid):
                self.assertEqual(q["originalQuestionNumber"],n)
                self.assertEqual(q["paperCode"],"00-E")
                self.assertEqual(q["subject"],"英文")
                self.assertEqual(q["answer"],pin["answer"])
                self.assertEqual(len(q["options"]),4)
                self.assertTrue(all(isinstance(t,str) and t for t in q["options"]))
                self.assertEqual(publisher.text_revision(q,pin["sha"]),pin["sourceRevision"])
                self.assertIs(q["questionVerified"],False)
                self.assertIs(q["answerVerified"],False)
                self.assertIsNot(q.get("integrationReady"),True)
                self.assertTrue("shared_reading_material_crop_requires_review" in q["issues"])
                self.assertEqual(publisher.source_proof(q,True,True,pin["sourceRevision"]),(False,False))

    def test_strict_negative_wrong_image_sha_shared_image_and_question_option(self):
        for n,pin in DETAILS.items():
            qid=f"115-00-E-{n:02d}"
            with self.subTest(qid=qid):
                im=self.im[qid]
                with self.assertRaises(AssertionError):
                    original_webp(im["output"],"0"*64,im["outputSize"])
                mutated=copy.deepcopy(self.q[qid])
                mutated["options"][0]="WRONG OPTION"
                self.assertNotEqual(publisher.text_revision(mutated,pin["sha"]),pin["sourceRevision"])
        for sid,pin in SHARED.items():
            with self.subTest(shared=sid):
                with self.assertRaises(AssertionError):
                    original_webp(pin["path"],"0"*64,
                                  [pin["crop"][2]-pin["crop"][0],pin["crop"][3]-pin["crop"][1]])

    def test_205_sqlite_rows_payload_hash_and_json_parity(self):
        path=BASE/"question-bank.sqlite3"
        with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            names={x[1] for x in db.execute("PRAGMA table_info(questions)")}
            field="payload" if "payload" in names else "payload_json"
            self.assertTrue({"question_id",field,"payload_sha256"}<=names)
            rows=db.execute("SELECT question_id,"+field+",payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({x[0] for x in rows},set(self.q))
        for qid,payload,digest in rows:
            with self.subTest(qid=qid):
                self.assertEqual(sha(payload.encode("utf-8")),digest)
                self.assertEqual(json.loads(payload),self.q[qid])

    def test_no_new_student_approved_reading_or_release(self):
        approved=read(ROOT/"sudu/data/approved/115.json")
        self.assertEqual(approved["approvedCount"],5)
        for n in DETAILS:
            id_=f"115-00-E-{n:02d}"
            self.assertNotIn(id_,{x["canonicalId"] for x in approved["questions"]})
            self.assertEqual(self.q[id_]["extraction"]["ocrReviewStatus"],"PENDING_INDIVIDUAL_VISUAL_QA")
        self.assertFalse(any(self.shared[sid]["qaStatus"]=="PASS" for sid in SHARED))

if __name__=="__main__":
    unittest.main()
