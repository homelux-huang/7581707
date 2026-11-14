"""Regression and malicious-input rejection for original 115 MB23 table QREV.

This module NEVER grants a reviewer receipt, learner approval or G8.
It validates genuine A G2 2x3 immutable official-source provenance
against protected-main publisher revision computation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sudu_verified_publish as pub

QID = "115-00-MB-23"
WITH_TABLE = "9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4"
WITHOUT_TABLE = "4dc7a376e0b9e5929a0a0df3e652ea0811d3b662ddce431eff4ebc539c859731"
TABLE_SHA = "3ae20c9b53eb5ba38ffa354cbda868806bb7716700548bbe88618e0104a89088"
IMAGE_SHA = "2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51"
OFFICIAL_PDF = "d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
ORIGINAL_EVIDENCE_BLOB = "0f63d6a5f91015dd2b146731c48dce08668c1fa2"
REL = "sudu/data/processed/115/review-evidence/115-00-MB-23-table-source-20261103.json"


class TableAwareRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidate = os.environ.get("SUDU_TABLE_SOURCE_QA")
        if not candidate:
            raise unittest.SkipTest("real QA source checkout required for integration tests")
        cls.source = Path(candidate).resolve()
        base = cls.source / "sudu/data/processed/115"
        cls.bank = json.loads((base / "questions.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((base / "webp-manifest.json").read_text(encoding="utf-8"))
        cls.byid = {q["questionId"]: q for q in cls.bank["questions"]}
        cls.assets = {i["questionId"]: i for i in cls.manifest["items"]}
        assert len(cls.byid) == len(cls.assets) == 205
        cls.q = cls.byid[QID]
        cls.image = cls.assets[QID]
        cls.original_evidence = (cls.source / REL).read_bytes()

    def test_original_evidence_blob_and_source_revision_seed(self):
        raw = self.original_evidence
        self.assertEqual(hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        ).hexdigest(), ORIGINAL_EVIDENCE_BLOB)
        evidence = json.loads(raw)
        original = evidence["originalTextAndTable"]
        table = original["sourceTable"]
        self.assertEqual(len(table["columns"]), 3)
        self.assertEqual(len(table["rows"]), 2)
        self.assertTrue(all(len(row) == 3 for row in table["rows"]))
        self.assertEqual(table["columns"], ["行程", "原價", "優惠"])
        self.assertEqual(
            self.q["tables"],
            [{"heading": table["columns"], "rows": table["rows"]}]
        )
        corrected = hashlib.sha256(json.dumps({
            "question": self.q["question"], "options": self.q["options"],
            "table": table
        }, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        self.assertEqual(corrected, TABLE_SHA)
        self.assertEqual(original["correctedTextSourceSha256"], TABLE_SHA)
        self.assertEqual(pub.pdf_sha(self.q, "answer"), OFFICIAL_PDF)
        expected = ("ROLE_A_115_MB23_TABLE_G2_G3_SOURCE_EVIDENCE_V1\n"
                    + TABLE_SHA + "\n" + IMAGE_SHA + "\n" + OFFICIAL_PDF)
        self.assertEqual(original["sourceRevisionSeed"], expected)
        self.assertEqual(
            hashlib.sha256(expected.encode("utf-8")).hexdigest(), WITH_TABLE
        )

    def test_true_qa_mb23_source_proof_accepts_table_revision(self):
        self.assertEqual(self.image["sha256"], IMAGE_SHA)
        revision = pub.text_revision(self.q, self.image["sha256"], self.source)
        self.assertEqual(revision, WITH_TABLE)
        self.assertNotEqual(revision, WITHOUT_TABLE)
        self.assertEqual(pub.source_proof(self.q, True, True, revision), (True, True))
        self.assertTrue(self.q["answerMatched"])
        self.assertFalse(self.q.get("studentReleaseApproved") is True)

    def test_no_implicit_tableless_fallback(self):
        self.assertEqual(pub.text_revision(self.q, IMAGE_SHA), "")
        self.assertEqual(pub.text_revision(self.q, IMAGE_SHA, Path("/missing")), "")
        self.assertEqual(pub.source_proof(
            self.q, True, True, WITHOUT_TABLE
        )[0], False)

    def test_tampered_table_question_answer_pdf_and_sha_rejected(self):
        changes = [
            ("discount", lambda q: q["tables"][0]["rows"][1].__setitem__(2, "Both people 80% (tampered)")),
            ("one_header", lambda q: q["tables"][0]["heading"].pop()),
            ("wrong_question", lambda q: q.__setitem__("question", q["question"] + " wrong")),
            ("wrong_option", lambda q: q["options"].__setitem__(1, "33333")),
            ("wrong_pdf", lambda q: q["answerProvenance"].__setitem__("pdfSha256", "a" * 64)),
            ("wrong_qid", lambda q: q.__setitem__("questionId", "115-00-MB-24")),
            ("wrong_year", lambda q: q.__setitem__("year", 114)),
            ("wrong_table_digest", lambda q: q["extraction"]["correctionOverlay"].__setitem__("tableTextSha256", "a" * 64)),
            ("wrong_evidence_path", lambda q: q["extraction"]["correctionOverlay"].__setitem__(
                "tableEvidencePath", "../../approved/115.json")),
            ("wrong_table_revision", lambda q: q["textQaEvidence"].__setitem__("questionRevision", WITHOUT_TABLE)),
            ("wrong_overlay_revision", lambda q: q["extraction"]["correctionOverlay"].__setitem__("questionRevision", WITHOUT_TABLE)),
            ("wrong_overlay_table", lambda q: q["extraction"]["correctionOverlay"]["sourceTables"][0]["rows"][1].__setitem__(2,"tampered")),
        ]
        for description, transform in changes:
            with self.subTest(description=description):
                q = copy.deepcopy(self.q)
                transform(q)
                self.assertEqual(pub.text_revision(q, IMAGE_SHA, self.source), "")
        self.assertEqual(pub.text_revision(self.q, "b" * 64, self.source), "")
        self.assertEqual(pub.text_revision(self.q, "../wrongsha", self.source), "")

    def test_original_source_evidence_must_match_immutable_blob(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / REL
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.original_evidence)
            self.assertEqual(pub.text_revision(self.q, IMAGE_SHA, root), WITH_TABLE)
            target.write_bytes(self.original_evidence.replace(b"3000", b"9000"))
            self.assertEqual(pub.text_revision(self.q, IMAGE_SHA, root), "")
            target.unlink()
            target.symlink_to(self.source / REL)
            self.assertEqual(pub.text_revision(self.q, IMAGE_SHA, root), "")
            target.unlink()
            self.assertEqual(pub.text_revision(self.q, IMAGE_SHA, root), "")

    def test_other_205_record_ids_and_five_published_baselines_unchanged(self):
        # No other record opts in to original source-table provenance.
        table_overlays = [
            q["questionId"] for q in self.bank["questions"]
            if isinstance((q.get("extraction") or {}).get("correctionOverlay"), dict)
            and any(k in q["extraction"]["correctionOverlay"]
                    for k in ("sourceTables", "tableTextSha256", "tableEvidencePath"))
        ]
        self.assertEqual(table_overlays, [QID])
        for name in ("115-00-MB-20", "115-00-MB-21", "115-00-MB-22",
                     "115-00-MB-24", "115-00-MB-25"):
            q = self.byid[name]
            revision = pub.text_revision(q, self.assets[name]["sha256"], self.source)
            self.assertEqual(revision, q["textQaEvidence"]["questionRevision"])
        q = self.byid[QID]
        self.assertEqual(pub.text_revision(q, IMAGE_SHA, self.source), WITH_TABLE)
        # Verify it cannot certify or release content on its own.
        self.assertFalse(pub.final_review_authorized(
            self.source, q, self.image, None, WITH_TABLE
        )[0])


if __name__ == "__main__":
    unittest.main()
