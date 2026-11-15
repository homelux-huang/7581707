"""114 E07 native G5: frozen PR21 teaching + PR31 enrichment, author-only fail-closed."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "sudu/data/processed/114"
QID = "114-00-E-07"
ISSUER = "sudu/data/processed/114/review-evidence/114-00-E-07-teaching-publisher-20261115.json"
G2 = BANK / "review-evidence/114-00-E-07-ocr-publisher-20261115.json"
G3 = BANK / "review-evidence/114-00-E-07-official-publisher-20261115.json"
REV = "8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c"
WEBP = "0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc"
BASE_SHA = "d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf"
COMPOSED = "f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b"
AUTHOR_SHA = "59f7bc3d4c100cad7a37a6f16e2b6a27e564a01d6e96d77af23ef9987f2731c4"
G2_SHA = "ecc2fd5e4dca51185a008d978a9dcdae9e5feeedaa0512f9841a35e764bfe2b0"
G3_SHA = "f5519fa817883f0d6cc97ee4bb9e3ba47c75a21f03e126d7330b266b50442303"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def composed(content, enrichment, source_revision=REV, webp=WEBP):
    return sha(canonical({"questionId": QID, "sourceRevision": source_revision, "webpSha256": webp,
                          "teaching": content, "enrichment": enrichment}))


def require_env_file(name):
    p = os.environ.get(name)
    if not p or not Path(p).is_file():
        raise RuntimeError(f"Fail closed: genuine {name} missing")
    return Path(p)


class TestRoleB114E07NativeG5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pub = require_env_file("PUBLISHER_CHECKER_PATH")
        spec = importlib.util.spec_from_file_location("pinned_main_publisher", pub)
        cls.publisher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.publisher)
        cls.original_path = require_env_file("ORIGINAL_TEACHING_FILE")
        cls.addon_path = require_env_file("AUTHOR_ADDENDUM_FILE")
        cls.original = load(cls.original_path)
        cls.addon = load(cls.addon_path)
        cls.issuer = load(ROOT / ISSUER)
        qrows = load(BANK / "questions.json")["questions"]
        mrows = load(BANK / "webp-manifest.json")["items"]
        cls.q = next(q for q in qrows if q["questionId"] == QID)
        cls.m = next(m for m in mrows if m["questionId"] == QID)
        cls.g2, cls.g3 = load(G2), load(G3)
        cls.row_count = len(qrows)
        cls.manifest_count = len(mrows)

    def test_original_unchanged_content_and_two_exact_digests(self):
        t, base, addon = self.issuer, self.original, self.addon
        self.assertEqual(sha(canonical(base["content"])), BASE_SHA)
        self.assertEqual(base["content"], t["content"])  # byte-independent semantic equality, not rewrite
        self.assertEqual(addon["enrichment"], t["enrichment"])
        self.assertIsNone(addon["teaching"])
        self.assertEqual(sha(self.addon_path.read_bytes()), AUTHOR_SHA)
        self.assertEqual(t["canonicalTeachingSha256"], BASE_SHA)
        self.assertEqual(t["composedTeachingSha256"], COMPOSED)
        self.assertEqual(composed(t["content"], t["enrichment"]), COMPOSED)
        self.assertEqual(addon["composedTeachingSha256"], COMPOSED)
        self.assertEqual((base["questionRevision"], addon["source"]["questionRevision"]), (REV, REV))
        self.assertEqual((base["webpSha256"], addon["source"]["webpSha256"]), (WEBP, WEBP))
        self.assertEqual(t["sourceAuthorGitBlobSha1"], "03b1686ca549f72d1f999de5b99656273e0c1e05")
        self.assertEqual(t["enrichmentAuthorGitBlobSha1"], "ac26c39ddea751ed9837edf1e6875539499fab6f")

    def test_real_official_source_g2_g3_205_rows_and_webp(self):
        t = self.issuer
        self.assertEqual((self.row_count, self.manifest_count), (205, 205))
        self.assertEqual(self.q["questionId"], QID)
        self.assertIs(self.q["questionVerified"], True)
        self.assertIs(self.q["answerVerified"], True)
        self.assertEqual((self.q["answer"], self.q["officialFinalAnswer"]), ("A", "A"))
        self.assertEqual((self.m["qaStatus"], self.m["sha256"]), ("PASS", WEBP))
        self.assertEqual(sha((ROOT / self.m["output"]).read_bytes()), WEBP)
        self.assertEqual(self.publisher.text_revision(self.q, WEBP), REV)
        self.assertEqual((self.g2["questionRevision"], self.g2["webpSha256"]), (REV, WEBP))
        self.assertEqual((self.g2["question"], self.g2["options"]), (self.q["question"], self.q["options"]))
        self.assertTrue(self.g2["visualTextCompared"])
        self.assertTrue(self.g2["allRgbCropPixelsEqual"])
        self.assertEqual(self.g3["finalAnswer"], "A")
        self.assertEqual(self.g3["sourceQuestionRevision"], REV)
        self.assertTrue(self.g3["noCorrectionForThisQuestion"])
        self.assertTrue(self.publisher.official_notice_scope_certified(ROOT, 114, self.q, self.g3))
        self.assertEqual((sha(G2.read_bytes()), sha(G3.read_bytes())), (G2_SHA, G3_SHA))
        self.assertEqual((t["sourceG2Sha256"], t["sourceG3Sha256"]), (G2_SHA, G3_SHA))

    def test_four_distinct_teacher_elementary_reasons_and_no_math_card(self):
        t = self.issuer
        c = t["content"]
        options = c["optionExplanations"]
        self.assertEqual(set(options), set("ABCD"))
        self.assertTrue(t["allFourOptionsReviewed"] and t["calculationReviewed"])
        self.assertEqual((c["hasExamCalculation"], c["examCalculation"]), (False, None))
        self.assertEqual(c["formula"], "")
        self.assertEqual(len(self.q["options"]), 4)
        self.assertEqual(self.q["options"], ["automatically", "organically", "productively", "selfishly"])
        for k in "ABCD":
            for f in ("teacher", "elementary", "reason"):
                self.assertGreater(len(options[k][f].strip()), 5, (k, f))
        self.assertEqual(len({options[k]["teacher"] for k in "ABCD"}), 4)
        self.assertEqual(len({options[k]["elementary"] for k in "ABCD"}), 4)
        self.assertEqual(len({options[k]["reason"] for k in "ABCD"}), 4)
        self.assertIn("automatically", options["A"]["teacher"])
        self.assertIn("organically", options["B"]["teacher"])
        self.assertIn("productively", options["C"]["teacher"])
        self.assertIn("selfishly", options["D"]["teacher"])
        original_text = (self.q["question"] + " " + " ".join(self.q["options"])).casefold()
        self.assertEqual({x["text"] for x in t["sourceHighlights"]},
                         {"sensor lights", "by themselves", "automatically"})
        for mark in t["sourceHighlights"]:
            self.assertTrue(mark["bold"] and mark["highlight"])
            self.assertIn(mark["text"].casefold(), original_text)
        self.assertTrue(t["enrichment"]["newsExample"]["notAnArticleQuote"])

    def test_native_publisher_document_and_qid_boundary(self):
        native = self.publisher.review_document(ROOT, 114, ISSUER, QID)
        self.assertIsNotNone(native)
        self.assertEqual(native[0], self.issuer)
        self.assertEqual(native[1], sha((ROOT / ISSUER).read_bytes()))
        self.assertIsNone(self.publisher.review_document(ROOT, 114, ISSUER, "114-00-E-08"))
        self.assertIsNone(self.publisher.review_document(ROOT, 114, "../../wrong.json", QID))

    def test_negative_modified_answer_options_source_teaching_and_enrichment(self):
        bad = copy.deepcopy(self.q)
        bad["options"][0] = "incorrect fake choice"
        self.assertNotEqual(self.publisher.text_revision(bad, WEBP), REV)
        bad = copy.deepcopy(self.q)
        bad["question"] = "false substituted stem"
        self.assertNotEqual(self.publisher.text_revision(bad, WEBP), REV)
        self.assertNotEqual(self.publisher.text_revision(self.q, "0" * 64), REV)
        bad_teach = copy.deepcopy(self.issuer["content"])
        bad_teach["optionExplanations"]["A"]["teacher"] += " tamper"
        self.assertNotEqual(sha(canonical(bad_teach)), BASE_SHA)
        bad_enrich = copy.deepcopy(self.issuer["enrichment"])
        bad_enrich["englishVocabulary"][0]["ipa"] = "tampered"
        self.assertNotEqual(composed(self.issuer["content"], bad_enrich), COMPOSED)
        self.assertNotEqual(composed(self.issuer["content"], self.issuer["enrichment"], webp="0"*64), COMPOSED)
        fake = copy.deepcopy(self.g3)
        fake["finalAnswer"] = "B"
        self.assertNotEqual(fake["finalAnswer"], self.q["answer"])

    def test_no_fake_original_session_no_independent_e_no_release(self):
        t = self.issuer
        self.assertIsNone(t["sourceAuthorSessionId"])
        self.assertIsNone(t["reviewerSessionId"])
        self.assertEqual(t["sourceAuthorTaskId"], "UNVERIFIED")
        self.assertEqual(t["enrichmentAuthorTaskId"], "UNVERIFIED")
        self.assertIs(t["independentAiContentReviewed"], False)
        self.assertIs(t["studentReleaseApproved"], False)
        self.assertIs(t["answerAlreadyKnown"], True)
        self.assertIs(t["blindSolveClaimedThisTask"], False)
        self.assertEqual(t["status"], "AUTHOR_CONTENT_ISSUED_IN_QA_NOT_E_TRUST_NOT_UI_NOT_READY")
        self.assertNotEqual(self.q["reviewStatus"], "STUDENT_QA_APPROVED")
        p = BANK / "approved.json"
        if p.exists():
            self.assertNotIn(QID, json.dumps(load(p), ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
