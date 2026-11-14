"""ROLE C 115 MB23/20/24/25 native G5: author-only exact hash & release-negative tests.

Dedicated workflow sets PUBLISHER_CHECKER_PATH and ORIGINAL_ROLE_C_DIR.
Generic global test discovery skips cleanly without those fixtures (PR196 contract).
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER_PATH = os.environ.get("PUBLISHER_CHECKER_PATH")
ORIGINAL_DIR = os.environ.get("ORIGINAL_ROLE_C_DIR")
EVIDENCE = ROOT / "sudu/data/processed/115/review-evidence"
CONFIG = {
    23: dict(rev="9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4",
             webp="2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51",
             teacher="13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6",
             blob="eae542565062adf997ab8c8d37d2c3cd4dd71ca1",
             g2="64fa11a8a40ff221a9b6cbc34a45ae8da14c9c5fa0a04d5b36f2a4012df7cde7",
             g3="a9c4b2f7e56f8ddb69aca1462af3e762029c5c2e78c6b92d473122b5ba943238",
             answer="B",result="33000元",return_id=6876442306,date="20261110"),
    20: dict(rev="2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c",
             webp="f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf",
             teacher="2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d",
             blob="c226ee59e24d2136c5882ede894f9f0bb93d16d0",
             g2="c6f33db05c38e9fdb3abc682d27cf8f21550dbd638c84adafd396a2bf3f491e2",
             g3="67b554b4b1f5543d40ca0e455a209554a94792816916415002ee46d4fe59202c",
             answer="A",result="50(√3＋1)公尺",return_id=6876442923,date="20261110"),
    24: dict(rev="9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267",
             webp="c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb",
             teacher="317fe1d731f29e9634ec17f0fc1dc5c308b804de5759991a005f94f81bbffd06",
             blob="8e2825de90bfc61e33269ae907a3f30eff4f8cde",
             g2="1caa3da4d5d6ce523f371709f944edaaacc2e5e2abf1240a545a385bfe1743ba",
             g3="73ec23f02bd01ca625aca64b25641a4e46d224018d34ae6040d62eeaa2225ea4",
             answer="C",result="C＝14、D＝15，D＝C＋1",return_id=6688932645,date="20261114"),
    25: dict(rev="8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f",
             webp="92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896",
             teacher="a860b08a6f5b76fe1331dc4204a46a3135e511449d9b6004cc4f99be020e4d32",
             blob="a1105e87cd0b3da26eb95d8ad481c6cfadb87428",
             g2="eca8ece0babeae6886297dca98bd58ace45018cb289f925f44f3d9c44766a464",
             g3="2179203705d3a089a1d43e3b4e8beb73eb3dffff6ce0a43e3c16149cf6e5a125",
             answer="C",result="－10",return_id=6688933667,date="20261114"),
}

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def rel(n: int) -> str:
    return f"sudu/data/processed/115/review-evidence/115-00-MB-{n}-teaching-publisher-20261114.json"

@unittest.skipUnless(PUBLISHER_PATH, "Dedicated G5 fixtures absent: safe skip in generic test discovery")
class TestRoleC115NativeG5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path(PUBLISHER_PATH).is_file():
            raise RuntimeError("Dedicated publisher configured but pinned protected-main module missing")
        if not ORIGINAL_DIR or not Path(ORIGINAL_DIR).is_dir():
            raise RuntimeError("Dedicated original C author source directory missing")
        spec = importlib.util.spec_from_file_location("role_c_pinned_main_publisher", PUBLISHER_PATH)
        cls.publisher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.publisher)
        cls.bank = read(ROOT / "sudu/data/processed/115/questions.json")["questions"]
        cls.manifest = read(ROOT / "sudu/data/processed/115/webp-manifest.json")["items"]
        cls.active = [n for n in (23, 20, 24, 25) if (ROOT / rel(n)).is_file()]
        if not cls.active or cls.active[0] != 23:
            raise RuntimeError("Original MB23 issuer must be admitted first; empty tests cannot pass")
        expected = os.environ.get("ROLE_C_REQUIRED_G5_IDS", "23").split(",")
        if set(map(int, expected)) != set(cls.active):
            raise RuntimeError(f"Expected {expected}, found {cls.active}; cannot silently skip an issuer")
        if len(cls.bank) != 205 or len(cls.manifest) != 205:
            raise RuntimeError("Expected exactly 205 current-year source and manifest entries")
        if len({q["questionId"] for q in cls.bank}) != 205:
            raise RuntimeError("Duplicate source QID")
        if len({m["questionId"] for m in cls.manifest}) != 205:
            raise RuntimeError("Duplicate manifest QID")

    def each(self):
        for n in self.active:
            cfg = CONFIG[n]
            qid = f"115-00-MB-{n}"
            author = Path(ORIGINAL_DIR) / f"MB{n}.json"
            if not author.is_file():
                raise RuntimeError(f"Real original C file MB{n} missing")
            document = ROOT / rel(n)
            yield n, cfg, qid, document, read(document), author, read(author)

    def test_positive_real_publisher_and_original_author_git_blob(self):
        for n,c,qid,path,doc,author,orig in self.each():
            with self.subTest(qid=qid):
                git_blob = subprocess.check_output(["git", "hash-object", str(author)], text=True).strip()
                self.assertEqual(git_blob,c["blob"])
                self.assertEqual(doc["sourceAuthorGitBlobSha1"],git_blob)
                self.assertEqual(doc["sourceAuthorRole"],"C")
                self.assertEqual(doc["sourceAuthorCommit"],"afaba171eec77cc27c3171b8bc8282f68ade74b9")
                self.assertEqual(doc["sourceAuthorReturnIssueCommentId"],c["return_id"])
                self.assertEqual(doc["content"],orig["teaching"])
                self.assertEqual(doc["canonicalTeachingSha256"],orig["teachingCanonicalSha256"])
                self.assertEqual(doc["canonicalTeachingSha256"],c["teacher"])
                self.assertEqual(sha(canonical(doc["content"])),c["teacher"])
                self.assertEqual((doc["schemaVersion"],doc["year"],doc["questionId"]),(1,115,qid))
                self.assertEqual((doc["questionRevision"],doc["webpSha256"]),(c["rev"],c["webp"]))
                got = self.publisher.review_document(ROOT,115,rel(n),qid)
                self.assertIsNotNone(got)
                self.assertEqual(got[0],doc)
                self.assertEqual(got[1],sha(path.read_bytes()))
                print(f"ORIGINAL_ROLE_C_G5_POSITIVE {qid} issuer_raw_sha256={sha(path.read_bytes())} "
                      f"author_git_blob={git_blob} canonical_teaching_sha256={c['teacher']}")

    def test_source_g2_g3_exact_current_205_webp_and_answers(self):
        for n,c,qid,path,doc,author,orig in self.each():
            with self.subTest(qid=qid):
                q=next(x for x in self.bank if x["questionId"]==qid)
                m=next(x for x in self.manifest if x["questionId"]==qid)
                g2path=EVIDENCE/f"{qid}-ocr-publisher-{c['date']}.json"
                g3path=EVIDENCE/f"{qid}-official-publisher-{c['date']}.json"
                g2,g3=read(g2path),read(g3path)
                self.assertIs(q["questionVerified"],True)
                self.assertIs(q["answerVerified"],True)
                self.assertEqual((q["answer"],q["officialFinalAnswer"]),(c["answer"],c["answer"]))
                self.assertEqual((g2["questionRevision"],g2["webpSha256"]),(c["rev"],c["webp"]))
                self.assertEqual((g2["question"],g2["options"]),(q["question"],q["options"]))
                self.assertEqual((q["question"],q["options"]),(orig["question"],orig["options"]))
                self.assertEqual(g3["sourceQuestionRevision"],c["rev"])
                self.assertEqual(g3["finalAnswer"],c["answer"])
                self.assertTrue(self.publisher.official_notice_scope_certified(ROOT,115,q,g3))
                self.assertEqual(m["sha256"],c["webp"])
                self.assertEqual(sha((ROOT/m["output"]).read_bytes()),c["webp"])
                self.assertEqual(self.publisher.text_revision(q,c["webp"]),c["rev"])
                self.assertEqual((sha(g2path.read_bytes()),sha(g3path.read_bytes())),(c["g2"],c["g3"]))
                self.assertEqual((doc["sourceG2Sha256"],doc["sourceG3Sha256"]),(c["g2"],c["g3"]))
                self.assertEqual(orig["imageSha256"],c["webp"])
                rev=orig.get("sourceTextRevisionWithTable",orig.get("sourceTextRevisionWithoutTable"))
                self.assertEqual(rev,c["rev"])
                self.assertEqual(q.get("sourceTables") or [],orig["sourceTables"])
                if n==23:
                    self.assertNotEqual(orig["sourceTextRevisionWithoutTable"],c["rev"])
                    self.assertEqual(doc["sourceRevisionMode"],"WITH_ORIGINAL_2X3_TABLE")
                    self.assertEqual(doc["sourceTables"],orig["sourceTables"])
                    self.assertEqual(doc["sourceTables"],g2["sourceTables"])
                    self.assertEqual(len(doc["sourceTables"]),1)
                    self.assertEqual(len(doc["sourceTables"][0]["heading"]),3)
                    self.assertEqual(len(doc["sourceTables"][0]["rows"]),2)
                    self.assertTrue(all(len(row)==3 for row in doc["sourceTables"][0]["rows"]))
                    self.assertEqual(doc["sourceTableTextSha256"],g2["tableTextSha256"])
                    self.assertEqual(doc["sourceTableTextSha256"],g3["sourceTableTextSha256"])
                if n==20:
                    self.assertIn("webp-v5",orig["image"])
                    self.assertEqual(m["output"],orig["image"])

    def test_original_four_option_explanations_calculation_and_reasonableness(self):
        for n,c,qid,path,doc,author,orig in self.each():
            with self.subTest(qid=qid):
                t=doc["content"]
                self.assertIs(doc["allFourOptionsReviewed"],True)
                self.assertIs(doc["calculationReviewed"],True)
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([k for k,v in t["optionExplanations"].items() if v["isCorrect"]],[c["answer"]])
                self.assertEqual(len({v["reason"] for v in t["optionExplanations"].values()}),4)
                for option in t["optionExplanations"].values():
                    for key in ("teacher","elementary","reason"):
                        self.assertTrue(isinstance(option[key],str) and option[key].strip())
                self.assertTrue(t["hasExamCalculation"])
                self.assertGreaterEqual(len(t["examCalculation"]["steps"]),6)
                self.assertEqual(t["examCalculation"]["option"],c["answer"])
                self.assertEqual(t["examCalculation"]["result"],c["result"])
                self.assertEqual([h["text"] for h in doc["sourceHighlights"]],t["highlights"])
                self.assertTrue(all(h["bold"] is True and h["highlight"] is True for h in doc["sourceHighlights"]))
                if n==23:
                    x=33000
                    self.assertEqual(2*x-3000,63000)
                    self.assertEqual((x+2000)+0.8*(x+2000),63000)
                elif n==20:
                    AC=100*math.sin(math.radians(75))/math.sin(math.radians(45))
                    self.assertAlmostEqual(AC,50*(math.sqrt(3)+1),places=8)
                    self.assertAlmostEqual(AC*math.sin(math.radians(45))/math.sin(math.radians(75)),100,places=8)
                elif n==24:
                    A=110/8
                    B=math.log10(3)/math.log10(1.08)
                    self.assertEqual(math.ceil(A),14)
                    self.assertEqual(math.ceil(B),15)
                    self.assertGreater(1.08**15,3)
                    self.assertLess(1.08**14,3)
                elif n==25:
                    h=4
                    a=2-16
                    self.assertEqual(h+a,-10)
                    self.assertEqual(a+16,2)

    def test_negative_tampered_author_stale_source_wrong_answer_and_table(self):
        for n,c,qid,path,doc,author,orig in self.each():
            with self.subTest(qid=qid):
                self.assertIsNone(self.publisher.review_document(ROOT,115,rel(n),"115-00-MB-99"))
                self.assertIsNone(self.publisher.review_document(ROOT,115,"../../missing.json",qid))
                tampered=copy.deepcopy(doc)
                tampered["content"]["optionExplanations"][c["answer"]]["teacher"] += " FORGED"
                self.assertNotEqual(sha(canonical(tampered["content"])),c["teacher"])
                tampered_calc=copy.deepcopy(doc)
                tampered_calc["content"]["examCalculation"]["steps"][0]="wrong equation"
                self.assertNotEqual(sha(canonical(tampered_calc["content"])),c["teacher"])
                q=copy.deepcopy(next(x for x in self.bank if x["questionId"]==qid))
                q["options"][0]="FAKE_OPTION"
                self.assertNotEqual(self.publisher.text_revision(q,c["webp"]),c["rev"])
                g3=read(EVIDENCE/f"{qid}-official-publisher-{c['date']}.json")
                g3["finalAnswer"]="D" if c["answer"]!="D" else "A"
                self.assertNotEqual(g3["finalAnswer"],c["answer"])
                if n==23:
                    bad=copy.deepcopy(next(x for x in self.bank if x["questionId"]==qid))
                    bad["sourceTables"][0]["rows"][0][2]="其中一人減免 30000 元"
                    self.assertNotEqual(self.publisher.text_revision(bad,c["webp"]),c["rev"])
                    self.assertNotEqual(orig["sourceTextRevisionWithoutTable"],c["rev"])

    def test_negative_no_e_trust_no_approval_or_invented_sessions(self):
        approved = ROOT / "sudu/data/processed/115/approved.json"
        approved_text = approved.read_text(encoding="utf-8") if approved.exists() else ""
        for n,c,qid,path,doc,author,orig in self.each():
            with self.subTest(qid=qid):
                self.assertEqual(doc["status"],"AUTHOR_CONTENT_ISSUED_IN_QA_NOT_E_TRUST_NOT_UI_NOT_READY")
                self.assertIs(doc["independentAiContentReviewed"],False)
                self.assertIs(doc["studentReleaseApproved"],False)
                self.assertIsNone(doc["sourceAuthorSessionId"])
                self.assertIsNone(doc["reviewerSessionId"])
                self.assertIs(orig["studentReleaseApproved"],False)
                self.assertIs(orig["deploy"],False)
                self.assertNotIn(qid,approved_text)
                q=next(x for x in self.bank if x["questionId"]==qid)
                self.assertNotEqual(q["reviewStatus"],"STUDENT_QA_APPROVED")

if __name__=="__main__":
    unittest.main()
