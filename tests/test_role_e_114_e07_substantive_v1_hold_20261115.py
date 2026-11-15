"""ROLE E 114 E07: actual original G1/G2/G3/B G5 material-positive + protected V1 negative gate."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"sudu/data/processed/114"
QID="114-00-E-07"
G2=BANK/"review-evidence/114-00-E-07-ocr-publisher-20261115.json"
G3=BANK/"review-evidence/114-00-E-07-official-publisher-20261115.json"
NOTE=BANK/"review-evidence/role-e-20261115/114-00-E-07-CONTENT-NOTES-V1-HOLD.md"
REV="8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c"
WEBP="0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc"
BASE="d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf"
COMPOSED="f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b"
G2SHA="ecc2fd5e4dca51185a008d978a9dcdae9e5feeedaa0512f9841a35e764bfe2b0"
G3SHA="f5519fa817883f0d6cc97ee4bb9e3ba47c75a21f03e126d7330b266b50442303"
G5SHA="83053bdbb33b5ad6a5f92eede06f58bed64fba9eb41ef33afd96a836681ee854"

def sha(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def read(p):return json.loads(Path(p).read_bytes())

class E07IndependentContentHold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g5raw=Path(os.environ["ROLE_B_G5_REAL_FILE"]).read_bytes()
        cls.g5=json.loads(cls.g5raw)
        cls.mainpolicy=read(os.environ["PROTECTED_MAIN_V1_POLICY"])
        spec=importlib.util.spec_from_file_location("pinned_protected_main_gate",os.environ["PROTECTED_MAIN_V1_GATE"])
        cls.gate=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.gate)

    def test_real_original_source_and_author_material_positive(self):
        self.assertEqual(sha(b"abc"),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertIn("四選項獨立語意 QA",NOTE.read_text(encoding="utf-8"))
        self.assertEqual(sha((BANK/"webp-v1/00-E/114-00-E-07.webp").read_bytes()),WEBP)
        self.assertEqual(sha(G2.read_bytes()),G2SHA)
        self.assertEqual(sha(G3.read_bytes()),G3SHA)
        self.assertEqual(sha(self.g5raw),G5SHA)
        g2,g3=read(G2),read(G3)
        self.assertEqual(sha(canonical({"question":g2["question"],"options":g2["options"],"singleQuestionWebpSha256":WEBP})),REV)
        self.assertEqual(g2["questionRevision"],REV)
        self.assertEqual(g3["finalAnswer"],"A")
        self.assertTrue(g3["noCorrectionForThisQuestion"])
        self.assertEqual(g3["namedOfficialCorrectionQuestionIds"],["114-00-E-26"])
        self.assertEqual(self.g5["questionRevision"],REV)
        self.assertEqual(self.g5["webpSha256"],WEBP)
        self.assertEqual(sha(canonical(self.g5["content"])),BASE)
        self.assertEqual(sha(canonical({"questionId":QID,"sourceRevision":REV,"webpSha256":WEBP,"teaching":self.g5["content"],"enrichment":self.g5["enrichment"]})),COMPOSED)
        self.assertEqual(self.g5["sourceG2Sha256"],G2SHA)
        self.assertEqual(self.g5["sourceG3Sha256"],G3SHA)
        self.assertEqual((self.g5["content"]["hasExamCalculation"],self.g5["content"]["examCalculation"]),(False,None))
        self.assertEqual(set(self.g5["content"]["optionExplanations"]),set("ABCD"))
        self.assertTrue(self.g5["enrichment"]["newsExample"]["notAnArticleQuote"])
        self.assertEqual(self.g5["enrichment"]["newsExample"]["kind"],"SELF_WRITTEN_NEWS_CONTEXT_EXAMPLE")

    def test_actual_protected_v1_gate_negative_no_trust(self):
        self.assertEqual(self.mainpolicy["reviewMode"],"DISTINCT_AI_CONTENT_RECEIPT_V1")
        self.assertEqual(self.mainpolicy["trustedAiReviewReceipts"],{})
        q=next(x for x in read(BANK/"questions.json")["questions"] if x["questionId"]==QID)
        m=next(x for x in read(BANK/"webp-manifest.json")["items"] if x["questionId"]==QID)
        self.assertEqual(m["sha256"],WEBP)
        # Runs genuine protected main verifier against real source/author material, with no fabricated E IDs.
        allowed,reason=self.gate.separate_ai_content_receipt_verified(
            ROOT,{},q,m,self.g5,self.g5raw,trusted_receipts=self.mainpolicy["trustedAiReviewReceipts"])
        self.assertFalse(allowed)
        self.assertEqual(reason,"separate_ai_reviewer_trusted_receipt_absent")
        self.assertIsNone(self.g5["sourceAuthorSessionId"])
        self.assertIsNone(self.g5["reviewerSessionId"])
        self.assertFalse(self.g5["studentReleaseApproved"])

if __name__=="__main__":unittest.main()
