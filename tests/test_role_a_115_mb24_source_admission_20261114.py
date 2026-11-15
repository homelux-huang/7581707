"""Original MB24 native source acceptance and source/answer/no-release negatives."""
import copy
import importlib.util
import math
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import role_a_115_mb24_source_admission_20261114 as admission


@unittest.skipUnless(os.environ.get("MB24_FROZEN_SOURCE_ADMISSION") == "1",
                     "Historical MB24 snapshot acceptance runs only in its dedicated source workflow")
class MB24SourceAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub, cls.question, cls.manifest = admission.verify()

    def test_native_original_g1_g2_g3_and_205_full_tuple_parity(self):
        # verify() compares exact original Git objects, every other complete tuple,
        # all canonical objects, schema/shared rows and strict projection columns.
        self.assertEqual(admission.verify()[1]["questionId"], "115-00-MB-24")

    def test_full_fraction_source_and_independent_ceiling_check(self):
        q = self.question
        self.assertIn("A＝110/r", q["question"])
        self.assertIn("B＝log₁₀(3)／log₁₀(1＋r/100)", q["question"])
        self.assertEqual(q["options"], ["D＝C－1", "D＝C", "D＝C＋1", "D＝C＋2"])
        self.assertTrue(1.08**14 < 3 < 1.08**15)
        self.assertEqual((math.ceil(110 / 8), math.ceil(math.log(3) / math.log(1.08))), (14, 15))
        self.assertEqual(q["answer"], "C")

    def test_stale_text_or_wrong_official_hash_rejected_by_native_gates(self):
        q = copy.deepcopy(self.question)
        q["question"] = q["question"].replace("110/r", "110")
        changed_revision = self.pub.text_revision(q, admission.IMAGE_SHA)
        self.assertNotEqual(changed_revision, admission.REV)
        self.assertFalse(self.pub.source_proof(q, True, True, changed_revision)[0])
        q = copy.deepcopy(self.question)
        q["officialFinalQaEvidence"]["answerPdfSha256"] = "0" * 64
        self.assertFalse(self.pub.source_proof(q, True, True, admission.REV)[1])
        q = copy.deepcopy(self.question)
        q["questionVerified"] = False
        self.assertFalse(self.pub.source_proof(q, True, True, admission.REV)[0])

    def test_wrong_image_no_objection_and_cross_qid_fail_closed(self):
        m = copy.deepcopy(self.manifest)
        m["visualReviewEvidence"]["referenceSha256"] = "0" * 64
        self.assertFalse(self.pub.visual_certificate(ROOT, m, admission.QID))
        self.assertFalse(self.pub.verify_bytes(ROOT, admission.IMAGE_REL, "0" * 64))
        official = admission.js(admission.G3_REL)
        official["noObjectionForPaper"] = False
        self.assertFalse(self.pub.official_notice_scope_certified(ROOT, 115, self.question, official))
        self.assertIsNone(self.pub.review_document(ROOT, 115, admission.G2_REL, "115-00-MB-25"))

    def test_source_only_cannot_mint_student_or_e_approval(self):
        q = copy.deepcopy(self.question)
        q["studentReleaseApproved"] = True
        self.assertFalse(self.pub.certificates_complete(ROOT, q, self.manifest, {}))
        r = admission.js(admission.REPORT_REL)
        for key in ("formalETrust", "formalDRealEmitter16", "studentReady", "newLive"):
            self.assertIs(r[key], False)
        g2 = admission.js(admission.G2_REL)
        self.assertNotIn("finalAnswer", g2)
        self.assertNotIn("officialAnswer", g2)
        self.assertIs(g2["independentE"], False)


if __name__ == "__main__":
    unittest.main()
