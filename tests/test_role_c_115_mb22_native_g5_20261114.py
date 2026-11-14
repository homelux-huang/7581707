"""ROLE C MB22 original native teaching issuer: exact source and fail-closed gates."""
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
if not PUBLISHER or not Path(PUBLISHER).is_file():
    raise RuntimeError("Missing exact protected-main native publisher")
spec = importlib.util.spec_from_file_location("pinned_main_publisher", PUBLISHER)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

QID = "115-00-MB-22"
REL = "sudu/data/processed/115/review-evidence/115-00-MB-22-teaching-publisher-20261114.json"
G2 = ROOT / "sudu/data/processed/115/review-evidence/115-00-MB-22-ocr-publisher-20261108.json"
G3 = ROOT / "sudu/data/processed/115/review-evidence/115-00-MB-22-official-publisher-20261108.json"
AUTHOR = os.environ.get("ORIGINAL_AUTHOR_MB22_FILE")
REV = "7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17"
WEBP = "3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55"
TEACH = "5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600"
BLOB = "97567e55aa0a25c995f388b8007e9c00dff6a08e"
SOURCE_G2 = "7b08398714a4c459cca4824db600ef00370c143365af09a89eb3fed86f6540fd"
SOURCE_G3 = "9505ef9f63389cf517b8ffdc6c66c337756c56e9af08c3bd70ee4a249f5f12f7"

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

class TestRoleC115MB22NativeG5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        self.assertEqual(t["sourceAuthorReturnIssueCommentId"], 6876441691)
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
        self.assertEqual((q["answer"], q["officialFinalAnswer"]), ("B", "B"))
        self.assertEqual(m["sha256"], WEBP)
        self.assertEqual(sha((ROOT / m["output"]).read_bytes()), WEBP)
        self.assertEqual(publisher.text_revision(q, WEBP), REV)
        self.assertEqual((q["question"],q["options"]),(a["question"],a["options"]))
        self.assertEqual((self.g2["question"],self.g2["options"]),(q["question"],q["options"]))
        self.assertEqual((self.g2["questionRevision"],self.g2["webpSha256"]), (REV, WEBP))
        self.assertEqual((self.g3["sourceQuestionRevision"],self.g3["finalAnswer"]),(REV,"B"))
        self.assertTrue(publisher.official_notice_scope_certified(ROOT,115,q,self.g3))
        self.assertEqual((sha(G2.read_bytes()),sha(G3.read_bytes())),(SOURCE_G2,SOURCE_G3))
        self.assertEqual((t["sourceG2Sha256"],t["sourceG3Sha256"]),(SOURCE_G2,SOURCE_G3))

    def test_four_options_calculation_and_highlights(self):
        t=self.t; c=t["content"]
        self.assertEqual(set(c["optionExplanations"]),set("ABCD"))
        self.assertTrue(t["allFourOptionsReviewed"])
        self.assertTrue(t["calculationReviewed"])
        self.assertEqual([k for k,v in c["optionExplanations"].items() if v["isCorrect"]],["B"])
        self.assertEqual(len({c["optionExplanations"][x]["reason"] for x in "ABCD"}),4)
        for k in "ABCD":
            self.assertTrue(all(c["optionExplanations"][k][key].strip() for key in ("teacher","elementary","reason")))
        self.assertTrue(c["hasExamCalculation"])
        self.assertGreaterEqual(len(c["examCalculation"]["steps"]), 4)
        self.assertEqual(c["examCalculation"]["option"], "B")
        self.assertEqual(c["examCalculation"]["result"], "31種")
        self.assertEqual([x["text"] for x in t["sourceHighlights"]], c["highlights"])
        self.assertTrue(all(x["bold"] is True and x["highlight"] is True for x in t["sourceHighlights"]))

    def test_negative_wrong_qid_tamper_and_stale_revision(self):
        self.assertIsNone(publisher.review_document(ROOT,115,REL,"115-00-MB-21"))
        self.assertIsNone(publisher.review_document(ROOT,115,"../../missing.json",QID))
        altered=copy.deepcopy(self.t)
        altered["content"]["optionExplanations"]["B"]["teacher"]="TAMPER"
        self.assertNotEqual(sha(canon(altered["content"])),TEACH)
        stale=copy.deepcopy(self.q); stale["options"][0]="tampered source"
        self.assertNotEqual(publisher.text_revision(stale,WEBP),REV)
        stale_g3=copy.deepcopy(self.g3); stale_g3["finalAnswer"]="A"
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
