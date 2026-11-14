"""ROLE C original author native teaching G5 issuer: exact source and fail-closed gates."""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = os.environ.get("PUBLISHER_CHECKER_PATH")
publisher = None
if PUBLISHER and Path(PUBLISHER).is_file():
    spec = importlib.util.spec_from_file_location("pinned_main_publisher", PUBLISHER)
    publisher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publisher)

QID = "115-00-MB-21"
REL = "sudu/data/processed/115/review-evidence/115-00-MB-21-teaching-publisher-20261114.json"
G2 = ROOT / "sudu/data/processed/115/review-evidence/115-00-MB-21-ocr-publisher-20261108.json"
G3 = ROOT / "sudu/data/processed/115/review-evidence/115-00-MB-21-official-publisher-20261108.json"
AUTHOR = os.environ.get("ORIGINAL_AUTHOR_MB21_FILE")
REV = "817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9"
WEBP = "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693"
TEACH = "4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4"
BLOB = "e1905bec344dfa3650663821a85aa872c0e03c62"
SOURCE_G2 = "fd8e0b2f60f60c69d40250a13449bef8fbfd28a9fd686239854f126c6fa6c6be"
SOURCE_G3 = "227f14b683dcdb165bc1526bca5fdbef081b7af15ea80546e67aeaf68f08bb14"

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

@unittest.skipUnless(PUBLISHER, "Dedicated native G5 fixtures are configured by the issuer workflow")
class TestRoleC115MB21NativeG5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if publisher is None:
            raise RuntimeError("Configured protected-main publisher is missing")
        if not AUTHOR or not Path(AUTHOR).is_file():
            raise RuntimeError("Missing immutable original C GitBlob")
        cls.t = read(ROOT / REL)
        cls.original = read(AUTHOR)
        cls.bank = read(ROOT / "sudu/data/processed/115/questions.json")["questions"]
        cls.q = next(x for x in cls.bank if x["questionId"] == QID)
        cls.manifest = read(ROOT / "sudu/data/processed/115/webp-manifest.json")["items"]
        cls.m = next(x for x in cls.manifest if x["questionId"] == QID)
        cls.g2 = read(G2)
        cls.g3 = read(G3)

    def test_immutable_author_and_native_issuer(self):
        t, a = self.t, self.original
        self.assertEqual(subprocess.check_output(["git", "hash-object", AUTHOR], text=True).strip(), BLOB)
        self.assertEqual(t["sourceAuthorGitBlobSha1"], BLOB)
        self.assertEqual(t["sourceAuthorRole"], "C")
        self.assertEqual(t["sourceAuthorReturnIssueCommentId"], 6876441051)
        self.assertEqual(t["sourceAuthorCommit"], "afaba171eec77cc27c3171b8bc8282f68ade74b9")
        self.assertEqual(t["content"], a["teaching"])
        self.assertEqual(t["canonicalTeachingSha256"], a["teachingCanonicalSha256"])
        self.assertEqual(sha(canon(t["content"])), TEACH)
        self.assertEqual((t["questionRevision"], t["webpSha256"]), (REV, WEBP))
        native = publisher.review_document(ROOT, 115, REL, QID)
        self.assertIsNotNone(native)
        self.assertEqual(native[0], t)
        self.assertEqual(native[1], sha((ROOT / REL).read_bytes()))

    def test_exact_current_qa_source_and_official(self):
        t,q,m,a = self.t,self.q,self.m,self.original
        self.assertEqual(len(self.bank), 205)
        self.assertEqual(len(self.manifest), 205)
        self.assertEqual(len({x["questionId"] for x in self.bank}), 205)
        self.assertEqual(len({x["questionId"] for x in self.manifest}), 205)
        self.assertIs(q["questionVerified"], True)
        self.assertIs(q["answerVerified"], True)
        self.assertEqual((q["answer"], q["officialFinalAnswer"]), ("A", "A"))
        self.assertEqual(m["sha256"], WEBP)
        self.assertEqual(sha((ROOT / m["output"]).read_bytes()), WEBP)
        self.assertEqual(publisher.text_revision(q, WEBP), REV)
        self.assertEqual((q["question"],q["options"]),(a["question"],a["options"]))
        self.assertEqual((self.g2["question"],self.g2["options"]),(q["question"],q["options"]))
        self.assertEqual((self.g2["questionRevision"],self.g2["webpSha256"]), (REV, WEBP))
        self.assertEqual((self.g3["sourceQuestionRevision"],self.g3["finalAnswer"]),(REV,"A"))
        self.assertTrue(publisher.official_notice_scope_certified(ROOT,115,q,self.g3))
        self.assertEqual((sha(G2.read_bytes()),sha(G3.read_bytes())),(SOURCE_G2,SOURCE_G3))
        self.assertEqual((t["sourceG2Sha256"],t["sourceG3Sha256"]),(SOURCE_G2,SOURCE_G3))

    def test_four_options_calculation_and_highlights(self):
        t=self.t; c=t["content"]
        self.assertEqual(set(c["optionExplanations"]),set("ABCD"))
        self.assertTrue(t["allFourOptionsReviewed"])
        self.assertTrue(t["calculationReviewed"])
        self.assertEqual([k for k,v in c["optionExplanations"].items() if v["isCorrect"]],["A"])
        self.assertEqual(len({c["optionExplanations"][x]["reason"] for x in "ABCD"}),4)
        for k in "ABCD":
            self.assertTrue(all(c["optionExplanations"][k][key].strip() for key in ("teacher","elementary","reason")))
        self.assertTrue(c["hasExamCalculation"])
        self.assertGreaterEqual(len(c["examCalculation"]["steps"]), 5)
        self.assertEqual(c["examCalculation"]["option"], "A")
        self.assertEqual(c["examCalculation"]["result"], "5公里")
        self.assertEqual([x["text"] for x in t["sourceHighlights"]], c["highlights"])
        self.assertTrue(all(x["bold"] is True and x["highlight"] is True for x in t["sourceHighlights"]))

    def test_negative_wrong_qid_tamper_and_stale_revision(self):
        self.assertIsNone(publisher.review_document(ROOT,115,REL,"115-00-MB-22"))
        self.assertIsNone(publisher.review_document(ROOT,115,"../../missing.json",QID))
        altered=copy.deepcopy(self.t)
        altered["content"]["optionExplanations"]["A"]["teacher"]="TAMPER"
        self.assertNotEqual(sha(canon(altered["content"])),TEACH)
        stale=copy.deepcopy(self.q); stale["options"][0]="tampered source"
        self.assertNotEqual(publisher.text_revision(stale,WEBP),REV)
        stale_g3=copy.deepcopy(self.g3); stale_g3["finalAnswer"]="B"
        self.assertNotEqual(stale_g3["finalAnswer"],self.q["officialFinalAnswer"])
        self.assertNotEqual(sha(canon(dict(self.t["content"], examCalculation={}))),TEACH)

    def test_author_only_never_trusted_or_ready(self):
        t=self.t
        self.assertEqual(t["status"],"AUTHOR_CONTENT_ISSUED_IN_QA_NOT_E_TRUST_NOT_UI_NOT_READY")
        self.assertIs(t["independentAiContentReviewed"],False)
        self.assertIs(t["studentReleaseApproved"],False)
        self.assertIsNone(t["sourceAuthorSessionId"])
        self.assertIsNone(t["reviewerSessionId"])
        self.assertNotEqual(self.q["reviewStatus"],"STUDENT_QA_APPROVED")
        approved=ROOT / "sudu/data/processed/115/approved.json"
        if approved.exists():
            self.assertNotIn(QID,approved.read_text(encoding="utf-8"))
        self.assertIs(self.original["studentReleaseApproved"],False)
        self.assertIs(self.original["deploy"],False)

if __name__=="__main__":
    unittest.main()
