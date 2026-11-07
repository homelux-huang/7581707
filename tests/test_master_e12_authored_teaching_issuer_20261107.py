"""Real E12 B authored lesson issuer, fail-closed, no student approval."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "_publisher_main"))
from scripts import sudu_verified_publish as pub
from scripts import sudu_independent_review_gate as reviewer

QID="114-00-E-12"
QA_PATH="sudu/data/processed/114/review-evidence/114-00-E-12-teaching-publisher-20261107.json"
B_PATH="sudu/teaching-candidates/114-role-b-20261025-batch02/114-00-E-12.json"
REV="0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
WEBP="99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
CANONICAL="c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a"
COMPOSED="fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4"
RAW_SHA="cccc7c5fcc5491d4004c8e72d3e9fca696f2e1a9bdcca23ec7e28b298610c51d"
G2="8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc"
G3="63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"

def sha(x):return hashlib.sha256(x).hexdigest()
def blob(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\\x00"+x).hexdigest()

class E12TeachingIssuerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/"sudu/data/processed/114/questions.json").read_text(encoding="utf8"))
        cls.q=next(q for q in cls.source["questions"] if q["questionId"]==QID)
        cls.manifest=json.loads((ROOT/"sudu/data/processed/114/webp-manifest.json").read_text(encoding="utf8"))
        cls.item=next(i for i in cls.manifest["items"] if i["questionId"]==QID)
        cls.raw=(ROOT/"_author_b"/B_PATH).read_bytes()
        cls.author=json.loads(cls.raw)
        cls.issuer_raw=(ROOT/QA_PATH).read_bytes()
        cls.issuer=json.loads(cls.issuer_raw)
    def test_publisher_is_exact_protected_main_code(self):
        self.assertEqual(sha((ROOT/"_publisher_main/scripts/sudu_verified_publish.py").read_bytes()),
                         "aa7a774e8f0dde288210a5c584b874a7ded3d45d008d023abf7494dc133232d8")
    def test_original_author_bytes_untouched(self):
        self.assertEqual(sha(self.raw),RAW_SHA)
        self.assertEqual(blob(self.raw),"3d8e3b7164b31cc6607c45baf9a3a644f128c0c0")
        self.assertEqual(self.issuer["sourceAuthorCommit"],"57d969888c57fdcd2b16c933e92c7a2c9eebb3a5")
        self.assertEqual(self.issuer["sourceAuthorGitBlobSha1"],blob(self.raw))
        self.assertEqual(self.issuer["sourceAuthorReturnIssueCommentId"],6712537831)
        self.assertEqual(self.issuer["sourceAuthorRawSha256"],sha(self.raw))
    def test_exact_original_four_choice_teaching_content_digest(self):
        self.assertEqual(self.issuer["content"],self.author["teaching"])
        self.assertEqual(reviewer.digest(reviewer.canonical(self.issuer["content"])),CANONICAL)
        self.assertEqual(self.issuer["canonicalTeachingSha256"],CANONICAL)
        self.assertEqual(self.issuer["composedTeachingSha256"],COMPOSED)
        self.assertEqual(self.author["teachingCanonicalSha256"],CANONICAL)
        self.assertEqual(self.author["composedTeachingSha256"],COMPOSED)
        self.assertEqual(set(self.issuer["content"]["optionExplanations"]),set("ABCD"))
        self.assertFalse(self.issuer["content"]["hasExamCalculation"])
        self.assertIsNone(self.issuer["content"]["examCalculation"])
    def test_exact_canonical_question_and_official_sha(self):
        self.assertEqual(len(self.source["questions"]),205)
        self.assertEqual(len(self.manifest["items"]),205)
        self.assertTrue(self.q["questionVerified"])
        self.assertTrue(self.q["answerVerified"])
        self.assertEqual(self.q["officialFinalAnswer"],"C")
        self.assertEqual(self.issuer["questionRevision"],REV)
        self.assertEqual(self.issuer["webpSha256"],WEBP)
        self.assertEqual(pub.text_revision(self.q,WEBP),REV)
        self.assertEqual(self.item["sha256"],WEBP)
        self.assertEqual(self.issuer["questionId"],QID)
        self.assertEqual(self.issuer["year"],114)
        self.assertEqual(self.issuer["schemaVersion"],1)
        self.assertEqual(self.author["question"],self.q["question"])
        self.assertEqual(self.author["options"],self.q["options"])
    def test_publisher_can_parse_real_issuer_bytes(self):
        returned=pub.review_document(ROOT,114,QA_PATH,QID)
        self.assertIsNotNone(returned)
        self.assertEqual(returned[0],self.issuer)
        self.assertEqual(returned[1],sha(self.issuer_raw))
    def test_existing_g2_g3_sources_are_actual(self):
        p2=ROOT/"sudu/data/processed/114/review-evidence/114-00-E-12-ocr-publisher-20261107.json"
        p3=ROOT/"sudu/data/processed/114/review-evidence/114-00-E-12-official-publisher-20261107.json"
        self.assertEqual(sha(p2.read_bytes()),G2)
        self.assertEqual(sha(p3.read_bytes()),G3)
        self.assertTrue(pub.official_notice_scope_certified(ROOT,114,self.q,json.loads(p3.read_text(encoding="utf8"))))
    def test_negative_stale_revision_rejected_by_issuer_binding(self):
        mutated=copy.deepcopy(self.q)
        mutated["question"]+=" injected"
        self.assertNotEqual(pub.text_revision(mutated,WEBP),self.issuer["questionRevision"])
    def test_negative_modified_teaching_breaks_canonical_digest(self):
        bad=copy.deepcopy(self.issuer["content"])
        bad["optionExplanations"]["A"]["teacher"]+=" forged"
        self.assertNotEqual(reviewer.digest(reviewer.canonical(bad)),CANONICAL)
    def test_no_fabricated_e_or_blind_or_qa_pass(self):
        self.assertFalse(self.issuer["independentAiContentReviewed"])
        self.assertFalse(self.issuer["studentReleaseApproved"])
        self.assertIsNone(self.issuer["reviewerSessionId"])
        self.assertIsNone(self.issuer["sourceAuthorSessionId"])
        self.assertEqual(self.issuer["status"],"AUTHOR_CONTENT_ISSUED_IN_QA_NOT_E_TRUST_NOT_UI_NOT_READY")
        self.assertNotIn("independentBlindSolve",self.issuer)
        self.assertNotIn("trustedAiReviewReceipts",self.issuer)
        self.assertNotIn("uiQaStatus",self.issuer)
    def test_not_approved_in_protected_main(self):
        p=json.loads((ROOT/"_publisher_main/sudu/data/approved/114.json").read_text(encoding="utf8"))
        self.assertEqual(p["approvedCount"],0)
        policy=json.loads((ROOT/"_publisher_main/sudu/release-governance/independent-review-policy.json").read_text(encoding="utf8"))
        self.assertNotIn(QID,policy.get("trustedAiReviewReceipts",{}))
        self.assertFalse(self.q.get("studentReleaseApproved",False))
if __name__=="__main__":
    unittest.main()
