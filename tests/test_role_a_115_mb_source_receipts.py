"""Verify five immutable Math B source corrections against exact PR35 JSON/DB/WebP; no release."""
import copy
import hashlib
import json
import math
import sqlite3
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
REVIEW = BASE / "review-evidence"
NUMBERS = (20, 21, 22, 24, 25)  # 23 is under MASTER's separate PR39 lease.
SHAS = {
    20: "f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf",
    21: "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693",
    22: "3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55",
    24: "c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb",
    25: "92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896",
}
ORIGINAL_GIT = {
    20: "c5278848e46d07dba45734413bc0b79a9b9afcb4",
    21: "3e37500240e1c26fedc2ae827eac95ddf9ebe80b",
    22: "5ad5b4fef7570b71eb534a510baec9da27ca47ce",
    24: "ede8ce34695bc9e9429aab40079115f94610d669",
    25: "6228cca369d369c183cb578519c383257f579f8b",
}
KEY_CANDIDATE = {20: "A", 21: "A", 22: "B", 24: "C", 25: "C"}
QUESTION_PDF_SHA_RECORDED = "e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def check_webp(rel, expected):
    raw = (ROOT / rel).read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", rel
    assert hashlib.sha256(raw).hexdigest() == expected, rel
    return len(raw)

class MathBOriginalSourceReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bank = read(BASE / "questions.json")
        man = read(BASE / "webp-manifest.json")
        cls.bank = {x["questionId"]: x for x in bank["questions"]}
        cls.image = {x["questionId"]: x for x in man["items"]}
        cls.index = {x["qid"]: x for x in read(REVIEW / "MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json")["items"]}
        cls.legacy = {
            x["id"]: x
            for p in read(ROOT / "sudu/data/years/115.json")["papers"]
            if p["paper"] == "00-MB"
            for x in p["questions"]
        }
        cls.docs = {
            n: read(REVIEW / f"115-00-MB-{n}-image-transcription-correction-20261024.json")
            for n in NUMBERS
        }
        assert len(bank["questions"]) == len(man["items"]) == len(cls.bank) == len(cls.image) == 205

    def test_reuse_five_exact_original_git_objects_not_rewrite(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                path = REVIEW / f"115-00-MB-{n}-image-transcription-correction-20261024.json"
                self.assertEqual(git_sha(path), ORIGINAL_GIT[n])
        self.assertNotIn(23, NUMBERS)

    def test_original_webp_bytes_sha_pdf_page_and_ledger_all_link(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                qid = f"115-00-MB-{n}"
                q, image, corr, item = self.bank[qid], self.image[qid], self.docs[n], self.index[qid]
                self.assertEqual(q["questionId"], image["questionId"])
                self.assertEqual(q["originalQuestionNumber"], image["originalQuestionNumber"])
                self.assertEqual(q["paperCode"], "00-MB")
                self.assertEqual(corr["questionNumber"], n)
                self.assertEqual(corr["originalQuestionPdfSha256"], QUESTION_PDF_SHA_RECORDED)
                self.assertEqual(q["questionProvenance"]["pdfSha256"], QUESTION_PDF_SHA_RECORDED)
                self.assertEqual(image["sourcePdfSha256"], QUESTION_PDF_SHA_RECORDED)
                self.assertEqual(image["sourcePage"], corr["sourcePage"])
                self.assertEqual(corr["sourceWebp"], image["output"])
                self.assertEqual(q["assets"]["singleQuestionWebp"], image["output"])
                self.assertEqual(item["entry"], "sudu/data/processed/115/review-evidence/"
                                 + f"115-00-MB-{n}-image-transcription-correction-20261024.json")
                self.assertEqual(image["qaStatus"], "PASS")
                self.assertEqual(image["sha256"], SHAS[n])
                self.assertEqual(q["assets"]["sha256"], SHAS[n])
                self.assertEqual(corr["sourceWebpSha256"], item["sourceWebpSha256"])
                self.assertEqual(item["sourceWebpSha256"], SHAS[n])
                self.assertEqual(image["visualReviewEvidence"]["reviewedSha256"], SHAS[n])
                self.assertFalse(image["visualReviewEvidence"]["independentHumanReview"])
                self.assertGreater(check_webp(image["output"], SHAS[n]), 0)
                self.assertGreater(check_webp(image["source"], image["sourceSha256"]), 0)
                if n == 20:
                    self.assertIn("webp-v5/", image["output"])  # do NOT regress to cropped v2.

    def test_source_before_after_exact_preserved_original_year_json_and_four_options(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                qid = f"115-00-MB-{n}"
                q, corr = self.bank[qid], self.docs[n]
                old, new = corr["legacyUncorrectedSource"], corr["correctedText"]
                self.assertEqual(q["legacyUnverifiedQuestion"], old["question"])
                self.assertEqual(q["legacyUnverifiedOptions"], old["options"])
                self.assertEqual(self.legacy[qid]["question"], old["question"])
                self.assertEqual(self.legacy[qid]["options"], old["options"])
                self.assertEqual(q["question"], new["question"])
                self.assertEqual(q["options"], new["options"])
                self.assertEqual(len(q["options"]), 4)
                self.assertTrue(all(isinstance(x, str) and x for x in q["options"]))
                self.assertIs(new["figureRequired"], True)
                self.assertIs(q["sourceFigureRequired"], True)
                self.assertIs(corr["noNewOCR"], True)
                self.assertIs(corr["noNewWebpCropping"], True)
                self.assertEqual(q["originalWebpTextCorrectionCandidate"],
                                 f"sudu/data/processed/115/review-evidence/"
                                 f"115-00-MB-{n}-image-transcription-correction-20261024.json")
                self.assertNotEqual(q["question"], old["question"])

    def test_exact_source_revision_matches_existing_C_author_candidate(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                qid = f"115-00-MB-{n}"
                q = self.bank[qid]
                draft = read(ROOT / f"sudu/teaching-candidates/114-115-20261025/{qid}.json")
                revision = publisher.text_revision(q, SHAS[n])
                self.assertEqual(draft["sourceTextRevisionWithoutTable"], revision)
                self.assertEqual(draft["imageSha256"], SHAS[n])
                self.assertFalse(draft["studentReleaseApproved"])
                self.assertEqual(draft["review"]["externalIndependentReview"], "PENDING")

    def test_key_is_candidate_and_has_not_been_independently_accepted(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                qid = f"115-00-MB-{n}"
                q, corr, row = self.bank[qid], self.docs[n], self.index[qid]
                self.assertEqual(q["answer"], KEY_CANDIDATE[n])
                self.assertEqual(row["officialAnswer"], KEY_CANDIDATE[n])
                self.assertEqual(corr["knownOfficialAnswer"], KEY_CANDIDATE[n])
                self.assertIs(q["answerMatched"], True)
                self.assertIs(q["questionVerified"], False)
                self.assertIs(q["formalTextApproval"], False)
                self.assertIs(q["integrationReady"], False)
                self.assertIs(q["studentReleaseApproved"], False)
                self.assertIs(corr["status"]["formalIndependentHumanTextQaPass"], False)
                self.assertIs(corr["status"]["studentReleaseApproved"], False)
                self.assertIs(corr["status"]["independentBlindSolveCertificate"], False)
                self.assertIs(corr["status"]["deploy"], False)
                self.assertNotEqual(q.get("textQaStatus"), "PASS")
                self.assertEqual(publisher.source_proof(q, True, True,
                                 publisher.text_revision(q, SHAS[n])), (False, False))

    def test_specific_high_risk_formula_and_figure_transcription_preserved(self):
        self.assertIn("100 公尺", self.bank["115-00-MB-20"]["question"])
        self.assertIn("∠CBA＝75°", self.bank["115-00-MB-20"]["question"])
        self.assertEqual(self.bank["115-00-MB-20"]["options"][0], "50(√3＋1)")
        self.assertIn("大於 4 公里", self.bank["115-00-MB-21"]["question"])
        self.assertEqual(self.bank["115-00-MB-21"]["options"][0], "5")
        self.assertIn("至少有一張", self.bank["115-00-MB-22"]["question"])
        self.assertIn("ū", self.bank["115-00-MB-22"]["question"])
        self.assertIn("bô", self.bank["115-00-MB-22"]["question"])
        self.assertEqual(self.bank["115-00-MB-22"]["options"][1], "31")
        self.assertIn("log₁₀(3)／log₁₀(1＋r/100)", self.bank["115-00-MB-24"]["question"])
        self.assertEqual(self.bank["115-00-MB-24"]["options"][2], "D＝C＋1")
        self.assertIn("距離為 √2", self.bank["115-00-MB-25"]["question"])
        self.assertNotIn("距離為 2", self.bank["115-00-MB-25"]["question"])
        self.assertIn("x²－8x＋(y－7)²＝a", self.bank["115-00-MB-25"]["question"])
        self.assertEqual(self.bank["115-00-MB-25"]["options"][2], "－10")
        # Arithmetic sanity only, NOT blind solving or independent teacher review.
        self.assertAlmostEqual(100 * math.sin(math.radians(75))/math.sin(math.radians(45)),
                               50*(math.sqrt(3)+1), places=6)
        self.assertEqual(2**5-1,31)
        self.assertEqual(math.ceil(110/8),14)
        self.assertEqual(math.ceil(math.log(3)/math.log(1.08)),15)

    def test_wrong_sha_and_mutated_option_invalidate_candidate_source_revision(self):
        for n in NUMBERS:
            with self.subTest(number=n):
                q = self.bank[f"115-00-MB-{n}"]
                current = publisher.text_revision(q, SHAS[n])
                self.assertNotEqual(publisher.text_revision(q, "0"*64), current)
                mutated = copy.deepcopy(q)
                mutated["options"][0] += " tampered"
                self.assertNotEqual(publisher.text_revision(mutated, SHAS[n]), current)
                self.assertEqual(publisher.source_proof(q, True, True, current), (False, False))

    def test_205_sqlite_payloads_have_integrity_hashes_and_same_canonical_records(self):
        dbpath = BASE / "question-bank.sqlite3"
        with sqlite3.connect(dbpath.as_uri() + "?mode=ro", uri=True) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            names = {r[1] for r in db.execute("PRAGMA table_info(questions)")}
            col = "payload" if "payload" in names else "payload_json"
            self.assertTrue({"question_id", col, "payload_sha256"} <= names)
            rows = db.execute("SELECT question_id," + col + ",payload_sha256 FROM questions").fetchall()
            self.assertEqual(len(rows), 205)
        seen = set()
        for qid, raw, hexdigest in rows:
            self.assertNotIn(qid, seen)
            seen.add(qid)
            self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), hexdigest, qid)
            self.assertEqual(json.loads(raw), self.bank[qid], qid)
        self.assertEqual(seen, set(self.bank))

if __name__ == "__main__":
    unittest.main()
