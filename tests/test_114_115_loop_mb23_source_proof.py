"""MB23 exact existing original source QA receipt; NO human or AI release approval.

Do not regenerate source pixels, table or teaching. A source SHA assertion
validates provenance of an old AI correction, not independent QA or READY.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = "sudu/data/processed/115/review-evidence/115-00-MB-23-image-transcription-correction-20261024.json"
BLOB_SHA = "170cd2238bb7c1b942a7a5389797295cdfe26953"
ID = "115-00-MB-23"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ExistingMB23OriginalEvidenceIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / EVIDENCE).read_bytes()
        cls.original_blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        cls.evidence = json.loads(raw.decode("utf-8"))
        cls.q = next(q for q in
                     load("sudu/data/processed/115/questions.json")["questions"]
                     if q["questionId"] == ID)
        cls.asset = next(a for a in
                         load("sudu/data/processed/115/webp-manifest.json")["items"]
                         if a["questionId"] == ID)
        cls.lesson = load("sudu/teaching-candidates/114-115-20261025/" + ID + ".json")

    def test_original_immutable_blob_exactly_matches_canonical_QA(self):
        self.assertEqual(self.original_blob, BLOB_SHA)
        e = self.evidence
        self.assertEqual((e["questionId"], e["subject"], e["questionNumber"]),
                         (ID, "數學 B", 23))
        self.assertEqual(e["sourceCommitBeforeEdit"],
                         "ed832065d1eaebbb836d4264c9b32f944a2e082e")
        self.assertTrue(e["noNewOCR"])
        self.assertTrue(e["noNewWebpCropping"])
        self.assertIs(e["status"]["originalSourceUnmodified"], True)

    def test_original_pdf_and_single_webp_paths_and_real_bytes_match(self):
        q, a, e = self.q, self.asset, self.evidence
        self.assertRegex(e["originalQuestionPdfSha256"], SHA256)
        self.assertEqual(e["originalQuestionPdfSha256"], publisher.pdf_sha(q, "question"))
        self.assertEqual(e["sourceWebp"], a["output"])
        self.assertEqual(e["sourceWebp"], q["assets"]["singleQuestionWebp"])
        self.assertEqual(e["sourceWebpSha256"], a["sha256"])
        self.assertEqual(e["sourceWebpSha256"], publisher.image_sha(q))
        self.assertEqual(e["sourceWebpSha256"], self.lesson["imageSha256"])
        image = ROOT / a["output"]
        self.assertTrue(image.is_file())
        contents = image.read_bytes()
        self.assertEqual(contents[:4], b"RIFF")
        self.assertEqual(contents[8:12], b"WEBP")
        self.assertEqual(hashlib.sha256(contents).hexdigest(), e["sourceWebpSha256"])

    def test_corrected_text_original_two_rows_three_columns_and_options(self):
        q, e, d = self.q, self.evidence, self.lesson
        text = e["correctedText"]
        self.assertEqual(q["question"], text["question"])
        self.assertEqual(q["options"], text["options"])
        self.assertEqual(d["question"], text["question"])
        self.assertEqual(d["options"], text["options"])
        table = text["table"]
        self.assertEqual(table["heading"], ["行程", "原價", "優惠"])
        self.assertEqual(len(table["rows"]), 2)
        self.assertEqual([len(row) for row in table["rows"]], [3, 3])
        self.assertEqual(q["originalSourceTableCandidate"], table)
        self.assertEqual(d["originalSourceTableCandidate"], table)
        self.assertEqual(d["sourceTables"], [table])
        self.assertEqual(publisher.text_revision(q, e["sourceWebpSha256"]),
                         d["sourceTextRevisionWithTable"])
        self.assertNotEqual(d["sourceTextRevisionWithoutTable"],
                            d["sourceTextRevisionWithTable"])

    def test_ai_evidence_is_not_independent_teacher_or_student_approval(self):
        e, d, q = self.evidence, self.lesson, self.q
        self.assertTrue(e["reviewer"].startswith("GPT-6 assistant"))
        self.assertIs(e["proof"]["visualComparisonPerformed"], True)
        status = e["status"]
        for field in ("formalIndependentHumanTextQaPass", "independentBlindSolveCertificate",
                      "completeTeachingAndUIQaPass", "studentReleaseApproved", "deploy"):
            with self.subTest(field=field):
                self.assertIs(status[field], False)
        self.assertIs(d["review"]["formalIndependentTableQa"], False)
        self.assertIs(d["review"]["sourceRevisionAccepted"], False)
        self.assertIs(d["studentReleaseApproved"], False)
        self.assertIs(q["questionVerified"], False)
        # The 2026-10-25 owner AI-review-policy update is not an approval artifact;
        # this original AI-authored source correction cannot self-certify.
        self.assertEqual(e["knownOfficialAnswer"], q["answer"])


if __name__ == "__main__":
    unittest.main()
