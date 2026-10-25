"""Read-only original 115 English Q03 WebP reinstatement verification.

No new visual QA, OCR, official answer approval or student release is made here.
Uses the exact historical Git WebP blob and archived Demo visual-QA digest.
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
QID = "115-00-E-03"
WEBP_PATH = "sudu/data/processed/115/webp-v2/00-E/115-00-E-03.webp"
WEBP_GIT_BLOB = "f511b6b5447c38f4cb91ec14572adef56f79991f"
WEBP_SHA = "16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd"
PAGE_SHA = "0ae3b4495aa79c71248e8b554494009d13b24086f0c23fa1a8fd9a32e44ff68c"
PDF_SHA_RECORDED = "c13e298c3b05b890c410deac4f8f694905f19fcd3a63bb4fcc0662ee6cb2768a"
DEMO_QA_SHA = "50506b98dba9b3da2d58dd485fe2fe64aaf8e4f16b89efbe91313702b7a66124"
SOURCE_REVISION = "c7e7262a3d5283d547f1dda35f1070c21d432314069286b305265aad9fa8977e"
AUTO_ANSWER_PDF_RECORDED = "185b1c8503898290862cc4ba87d220d9969c882e26d52c4939b72db1d3b1af04"

def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(path):
    return sha256_bytes(path.read_bytes())

def git_blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def assert_real_webp(relative, expected_sha, expected_size):
    path = ROOT / relative
    raw = path.read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", relative
    assert sha256_bytes(raw) == expected_sha, relative + " wrong original byte SHA"
    with Image.open(path) as im:
        assert im.format == "WEBP", relative
        im.load()
        assert im.size == tuple(expected_size), (relative, im.size, expected_size)
    return len(raw)

class RoleA115E03WebpReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = read("sudu/data/processed/115/questions.json")
        cls.manifest = read("sudu/data/processed/115/webp-manifest.json")
        cls.qmap = {q["questionId"]: q for q in cls.bank["questions"]}
        cls.imap = {i["questionId"]: i for i in cls.manifest["items"]}
        assert len(cls.bank["questions"]) == len(cls.qmap) == 205
        assert len(cls.manifest["items"]) == len(cls.imap) == 205
        assert cls.qmap.keys() == cls.imap.keys()
        cls.q = cls.qmap[QID]
        cls.im = cls.imap[QID]

    def test_identical_archived_git_blob_with_actual_decode_and_dimensions(self):
        raw = (ROOT / WEBP_PATH).read_bytes()
        self.assertEqual(git_blob_hash(raw), WEBP_GIT_BLOB)
        self.assertGreater(assert_real_webp(WEBP_PATH, WEBP_SHA, [1220,114]), 0)
        self.assertEqual(self.im["output"], WEBP_PATH)
        self.assertEqual(self.im["sha256"], WEBP_SHA)
        self.assertEqual(self.q["assets"]["sha256"], WEBP_SHA)
        self.assertEqual(self.q["assets"]["singleQuestionWebp"], WEBP_PATH)
        self.assertEqual(self.im["qaStatus"], "PASS")  # historical PASS, not new review
        self.assertEqual(self.q["assets"]["visualQa"], "PASS")

    def test_original_source_page_and_pdf_provenance_pinned(self):
        q, im = self.q, self.im
        self.assertEqual(q["year"], 115)
        self.assertEqual(q["paperCode"], "00-E")
        self.assertEqual(q["originalQuestionNumber"], im["originalQuestionNumber"])
        self.assertEqual(q["originalQuestionNumber"], 3)
        self.assertEqual(q["subject"], "英文")
        self.assertEqual(im["sourcePage"], q["questionProvenance"]["sourcePage"])
        self.assertEqual(im["sourcePage"], 2)
        self.assertEqual(im["sourcePdfSha256"], PDF_SHA_RECORDED)
        self.assertEqual(q["questionProvenance"]["pdfSha256"], PDF_SHA_RECORDED)
        self.assertEqual(q["questionProvenance"]["originalPageWebp"], im["source"])
        self.assertEqual(im["sourceSha256"], PAGE_SHA)
        self.assertEqual(q["assets"]["sourceSha256"], PAGE_SHA)
        self.assertGreater(assert_real_webp(im["source"], PAGE_SHA, [1400,1981]), 0)
        self.assertEqual(q["assets"]["cropCoordinates"], [90,592,1310,706])
        self.assertEqual(im["crop"], [90,592,1310,706])
        self.assertEqual(im["outputSize"], [1220,114])

    def test_old_demo_visual_qa_unchanged_and_exact_sha_bound_not_new_pass(self):
        ev = self.im["visualReviewEvidence"]
        proof_path = ROOT / ev["reference"]
        self.assertEqual(ev["reference"], "sudu/DEMO_VISUAL_QA.md")
        self.assertEqual(sha256_file(proof_path), DEMO_QA_SHA)
        self.assertEqual(ev["referenceSha256"], DEMO_QA_SHA)
        self.assertEqual(ev["reviewedSha256"], WEBP_SHA)
        self.assertIs(ev["freshReviewInThisRun"], False)
        original = proof_path.read_text(encoding="utf-8")
        self.assertIn("| 英文 | 3 | 90,592,1310,706 | 1220×114 | PASS |", original)
        self.assertIn("| 英文 | 3 | 90,592,1310,706 | 1220×114 | PASS | " + chr(96) + WEBP_SHA + chr(96) + " |", original)
        self.assertIn("無相鄰題", original)  # historical written visual criteria, not a new review

    def test_four_original_options_and_source_digest_exact_to_role_c_candidate(self):
        q = self.q
        self.assertIn("The teacher treats all her students", q["question"])
        self.assertIn("giving every student the same opportunity", q["question"])
        self.assertEqual(q["options"], ["carelessly","equally","instantly","silently"])
        self.assertEqual(q["answer"], "B")
        self.assertEqual(q["acceptedAnswers"], ["B"])
        self.assertEqual(publisher.text_revision(q, WEBP_SHA), SOURCE_REVISION)
        self.assertEqual(self.im["visualReviewEvidence"]["reviewedSha256"], WEBP_SHA)

    def test_source_revision_mutation_and_wrong_blob_sha_are_rejected(self):
        with self.assertRaises(AssertionError):
            assert_real_webp(WEBP_PATH, "0" * 64, [1220,114])
        with self.assertRaises(AssertionError):
            assert_real_webp(WEBP_PATH, WEBP_SHA, [1220,115])
        other = copy.deepcopy(self.q)
        other["options"][1] = "unrelated replacement"
        self.assertNotEqual(publisher.text_revision(other, WEBP_SHA), SOURCE_REVISION)
        self.assertNotEqual(publisher.text_revision(self.q, "0"*64), SOURCE_REVISION)

    def test_205_source_json_and_sqlite_payload_hashes_roundtrip(self):
        path = BASE / "question-bank.sqlite3"
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            names = {x[1] for x in db.execute("PRAGMA table_info(questions)")}
            col = "payload" if "payload" in names else "payload_json"
            self.assertTrue({"question_id", col, "payload_sha256"} <= names)
            records = db.execute("SELECT question_id,"+col+",payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(records), 205)
        self.assertEqual({x[0] for x in records}, set(self.qmap))
        for qid, payload, digest in records:
            with self.subTest(questionId=qid):
                self.assertEqual(sha256_bytes(payload.encode("utf-8")), digest)
                self.assertEqual(json.loads(payload), self.qmap[qid])

    def test_per_question_official_notice_scope_not_falsely_paper_wide(self):
        ledger = read("sudu/data/processed/115/QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json")
        notice = read("sudu/data/processed/115/official-confirmation-status.json")
        row = next(x for x in ledger["docs"] if x["paperCode"]=="00-E")
        self.assertEqual(row["pdfSha256"], notice["confirmations"]["00-E"]["revisionDocumentSha256"])
        self.assertEqual({x["questionId"] for x in row["confirmed"]}, {"115-00-E-34"})
        self.assertNotIn(QID, {x["questionId"] for x in row["confirmed"]})
        self.assertEqual(self.q["answerProvenance"]["pdfSha256"], AUTO_ANSWER_PDF_RECORDED)
        self.assertIs(self.q["answerProvenance"]["officialRevisionChecked"], False)

    def test_ocr_and_approved_public_student_state_never_upgraded(self):
        q = self.q
        self.assertIs(q["answerMatched"], True)
        self.assertIs(q["answerVerified"], False)
        self.assertIs(q["questionVerified"], False)
        self.assertEqual(q["reviewStatus"], "needs_review")
        self.assertEqual(q["extraction"]["ocrReviewStatus"], "PENDING_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(publisher.source_proof(q, True, True, SOURCE_REVISION), (False,False))
        approved = read("sudu/data/approved/115.json")
        self.assertEqual(approved["approvedCount"], 5)
        self.assertNotIn(QID, {x["canonicalId"] for x in approved["questions"]})
        self.assertIsNot(q.get("studentReleaseApproved"), True)
        self.assertIsNot(q.get("integrationReady"), True)

if __name__=="__main__":
    unittest.main()
