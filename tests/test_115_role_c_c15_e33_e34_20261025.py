"""Read-only Role C 115 C15/E33/E34 author candidate integrity; NEVER QA/PUBLISH."""
import copy
import hashlib
import json
import math
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "sudu/teaching-candidates/115-role-c-c15-e33-e34-20261025"
BANK = ROOT / "sudu/data/processed/115/questions.json"
MANIFEST = ROOT / "sudu/data/processed/115/webp-manifest.json"
EXPECTED = {
    "115-00-C-15": ("B", True, False),
    "115-00-E-33": ("B", False, True),
    "115-00-E-34": ("B", False, False),
}
SHARED_SHA = {
    "115-00-C-15": "bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66",
    "115-00-E-33": "eb19a37ba2d85414ebe06551aac145cb7053befa6622f7adfb1d86d4e63046ea",
    "115-00-E-34": "eb19a37ba2d85414ebe06551aac145cb7053befa6622f7adfb1d86d4e63046ea",
}
CHART = {"Nobu Restaurant":10.1,"The Cheesecake Factory":12.4,
         "Smith and Wollensky":13.4,"Del Frisco's Double Eagle Steak House":13.8,
         "Mastro's Restaurants":14.5,"Din Tai Fung":27.4}

def raw_digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return raw_digest(json.dumps(obj,ensure_ascii=False,sort_keys=True,
                       separators=(",",":")).encode("utf-8"))

def revision(q):
    return canonical({"question":q["question"],"options":q["options"],
                      "singleQuestionWebpSha256":q["individualWebpSha256"]})

def shared_revision(q):
    s=q["sharedMaterial"]
    return canonical({"sharedMaterialId":s["id"],"text":s["sourceText"],
                      "outputSha256":s["imageSha256"]})

class RoleCThreeReadOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((DIR/"batch.json").read_text(encoding="utf-8"))
        cls.bank=json.loads(BANK.read_text(encoding="utf-8"))
        cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.items={v["questionId"]:v for v in cls.batch["items"]}
        cls.lessons={qid:json.loads((ROOT/item["path"]).read_text(encoding="utf-8"))
                     for qid,item in cls.items.items()}
        cls.sources={v["questionId"]:v for v in cls.bank["questions"]}
        cls.images={v["questionId"]:v for v in cls.manifest["items"]}
        cls.shared={v["sharedMaterialId"]:v for v in cls.bank["sharedMaterials"]}

    def test_exact_task_original_role_a_lease_and_no_release(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-C15-E33-E34-20261025-07")
        self.assertEqual(b["claimedAtUtc"],"2026-10-25T06:16:26Z")
        self.assertEqual(b["baseSHA"],"b6c449629efc80d37fa2e6dbb9e680e321367c14")
        self.assertEqual(b["baseRoleASourcePR"],64)
        self.assertEqual(set(self.items),set(EXPECTED))
        self.assertEqual((b["addedReady"],b["addedLive"]),(0,0))
        self.assertTrue(all(not i["ready"] for i in self.items.values()))
        self.assertEqual(len(self.bank["questions"]),205)
        self.assertEqual(len(self.manifest["items"]),205)

    def test_actual_original_source_git_blobs_and_schema_parity(self):
        for path,sha in (
            (BANK,self.batch["sourceQuestionBankGitBlobSHA"]),
            (MANIFEST,self.batch["sourceManifestGitBlobSHA"]),
        ):
            actual=subprocess.check_output(["git","hash-object",str(path)],
                                           cwd=ROOT,text=True).strip()
            self.assertEqual(actual,sha, f"Original source branch moved: {path}")
        self.assertEqual(self.batch["sourceQuestionBankGitBlobSHA"],
                         "0128adc3f41e748950c3f5af83fca6dd1c331f5c")
        self.assertEqual(self.batch["sourceManifestGitBlobSHA"],
                         "2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b")

    def test_sha_source_text_four_options_shared_and_full_lesson(self):
        for qid,q in self.lessons.items():
            i=self.items[qid]
            official=self.sources[qid]
            img=self.images[qid]
            shared=self.shared[official["sharedMaterialId"]]
            with self.subTest(qid=qid):
                self.assertEqual(raw_digest((ROOT/i["path"]).read_bytes()),i["fileSha256"])
                self.assertEqual(q["question"],official["question"])
                self.assertEqual(q["options"],official["options"])
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["answerCandidate"],official["answer"])
                self.assertEqual(q["individualWebpSha256"],img["sha256"])
                self.assertEqual(q["individualWebpSha256"],i["individualWebpSha256"])
                self.assertEqual(revision(q),q["sourceTextRevision"])
                self.assertEqual(revision(q),i["sourceRevision"])
                self.assertEqual(canonical(q["teaching"]),q["teachingCanonicalSha256"])
                self.assertEqual(q["teachingCanonicalSha256"],i["teachingCanonicalSha256"])
                s=q["sharedMaterial"]
                self.assertEqual(s["id"],shared["sharedMaterialId"])
                self.assertEqual(s["sourceText"],shared["text"])
                self.assertEqual(s["imageSha256"],shared["asset"]["sha256"])
                self.assertEqual(s["imageSha256"],SHARED_SHA[qid])
                self.assertEqual(shared_revision(q),i["sharedMaterialRevision"])
                self.assertEqual(shared_revision(q),s["sharedMaterialRevision"])
                self.assertEqual(raw_digest(s["sourceText"].encode()),s["sourceTextSha256"])
                self.assertEqual(q["sourceQuestionPdfSha256"],img["sourcePdfSha256"])

    def test_role_a_c15_correction_does_not_erase_original_raw_ocr(self):
        q=self.sources["115-00-C-15"]
        self.assertEqual(q["options"][3],"拘泥禮法 ／ 不知變通")
        self.assertIn("▲閱讀下文，回答第16-18 題",q["extraction"]["rawOptions"][3])
        self.assertIn("- 5-",q["extraction"]["rawOptions"][3])
        self.assertEqual(q["answer"],"B")
        self.assertFalse(q["questionVerified"])
        self.assertTrue(q["answerVerified"])  # historical source flag, not C certification
        self.assertFalse(q["integrationReady"])
        t=self.lessons["115-00-C-15"]["teaching"]
        self.assertIn("人情淡薄",t["teacherSummary"])
        self.assertIn("徒具儀式",t["teacherSummary"])
        self.assertEqual(set(t["chineseLevelVocabulary"]),{"初級","中級","高級"})

    def test_individual_four_choice_dual_level_critical_rationales(self):
        for qid,q in self.lessons.items():
            t=q["teaching"]
            with self.subTest(qid=qid):
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([k for k in "ABCD" if t["optionExplanations"][k]["isCorrect"]],
                                 [EXPECTED[qid][0]])
                for letter in "ABCD":
                    o=t["optionExplanations"][letter]
                    self.assertGreaterEqual(len(o["teacher"]),46,(qid,letter,"teacher"))
                    self.assertGreaterEqual(len(o["elementary"]),20,(qid,letter,"elementary"))
                    self.assertGreaterEqual(len(o["sourceEvidence"]),35,(qid,letter,"sourceEvidence"))
                    self.assertEqual(o["reason"],o["teacher"])
                    self.assertIn("**",o["teacher"])
                for field in ("teacherSummary","elementarySummary","memory","concept",
                              "extension","highlights","stepByStep","source"):
                    self.assertTrue(t[field],(qid,field))
                self.assertIn("**",t["teacherSummary"])
                self.assertIn("**",t["memory"])
                self.assertGreaterEqual(len(t["highlights"]),5)
                self.assertGreaterEqual(len(t["stepByStep"]),3)

    def test_e33_chart_values_formula_steps_units_and_verification(self):
        q=self.lessons["115-00-E-33"]
        t=q["teaching"]
        self.assertTrue(t["hasExamCalculation"])
        self.assertEqual(t["chartValuesMillionUsd"],CHART)
        c=t["examCalculation"]
        self.assertEqual(c["option"],"B")
        self.assertIn("百萬美元",c["unit"])
        for field in ("given","formulaUse","substitution","steps","result","unit","verification"):
            self.assertTrue(c[field],field)
        self.assertGreaterEqual(len(c["steps"]),6)
        raw="".join(q["sharedMaterial"]["sourceText"].split()).lower()
        self.assertIn("therevenueperstorefortheusrestaurantchains",raw)
        for val in CHART.values():
            self.assertIn(str(val),raw)
        self.assertTrue(math.isclose(27.4/2,13.7))
        self.assertNotEqual(12.4,27.4/2)
        self.assertTrue(math.isclose(14.5-10.1,4.4))
        self.assertTrue(math.isclose(10.1+4.4,14.5))
        self.assertTrue(math.isclose(13.8-10.1,3.7))
        self.assertTrue(math.isclose(13.4-27.4,-14.0))
        steps=" ".join(c["steps"])
        for expr in ("27.4÷2","12.4×2","14.5−10.1","10.1＋4.4","13.8−10.1","13.4−27.4"):
            self.assertIn(expr,steps)

    def test_english_news_real_surface_highlight_2025_and_no_calc_hidden(self):
        for id in ("115-00-E-33","115-00-E-34"):
            q=self.lessons[id]
            t=q["teaching"]; e=t["english"]
            with self.subTest(qid=id):
                self.assertEqual(set(e["synonyms"]),{"初級","中級","高級"})
                self.assertEqual(set(e["antonyms"]),{"初級","中級","高級"})
                self.assertTrue(all(e[k][level] for k in ("synonyms","antonyms")
                                    for level in ("初級","中級","高級")))
                self.assertTrue(e["pronunciationIPA"].startswith("/"))
                self.assertTrue(e["pronunciationIPA"].endswith("/"))
                self.assertIn("**"+e["newsExampleHighlightedSurfaceForm"]+"**",
                              e["newsExampleEnglish"])
                self.assertGreater(len(e["newsExampleChinese"]),20)
                self.assertEqual(e["newsExampleSourceDate"],"2025-06-06")
                self.assertIn("restaurantbusinessonline.com",e["newsExampleSourceUrl"])
                self.assertIn("NOT VERBATIM",e["newsExampleKind"])
        self.assertFalse(self.lessons["115-00-C-15"]["teaching"]["hasExamCalculation"])
        self.assertIsNone(self.lessons["115-00-C-15"]["teaching"]["examCalculation"])
        self.assertFalse(self.lessons["115-00-E-34"]["teaching"]["hasExamCalculation"])
        self.assertIsNone(self.lessons["115-00-E-34"]["teaching"]["examCalculation"])

    def test_fail_closed_pending_shared_source_ai_and_uiqa(self):
        for qid,q in self.lessons.items():
            with self.subTest(qid=qid):
                self.assertEqual(q["sourceImageManifestQa"],"PASS")
                self.assertEqual(q["sharedMaterial"]["qaStatus"],
                                 "PENDING_INDIVIDUAL_VISUAL_QA")
                self.assertFalse(q["sourceQuestionVerified"])
                self.assertEqual(q["sourceAnswerVerified"],EXPECTED[qid][1])
                self.assertFalse(q["knownAnswerBeforeDerivation"] is False)
                self.assertFalse(q["newBlindSolveClaimed"])
                self.assertFalse(q["originalImageBytesRehashedThisTurn"])
                self.assertFalse(q["sharedMaterial"]["originalImageBytesRehashedThisTurn"])
                self.assertFalse(q["studentReleaseApproved"])
                self.assertFalse(q["deploy"])
                self.assertFalse(q["newReady"])
                r=q["review"]
                self.assertEqual(r["independentAiReviewer"],"PENDING")
                self.assertTrue(r["authorSelfReviewNotAcceptable"])
                self.assertIsNone(r["independentAiReviewEvidenceSha256"])
                self.assertIsNone(r["sourceOfficialEvidenceSha256"])
                self.assertEqual(r["v4SameDigest8Viewports2Themes"],"PENDING")
                self.assertTrue(all("REAL_TEACHER_REQUIRED" not in b for b in q["blockers"]))

    def test_negative_tamper_source_images_shared_and_teaching(self):
        for qid,q in self.lessons.items():
            for case in ("question","option","single","shared_text","shared_image","teaching"):
                with self.subTest(qid=qid,case=case):
                    x=copy.deepcopy(q)
                    if case=="question":
                        x["question"]+="modified"
                        self.assertNotEqual(revision(x),q["sourceTextRevision"])
                    elif case=="option":
                        x["options"][3]+="modified"
                        self.assertNotEqual(revision(x),q["sourceTextRevision"])
                    elif case=="single":
                        x["individualWebpSha256"]="0"*64
                        self.assertNotEqual(revision(x),q["sourceTextRevision"])
                    elif case=="shared_text":
                        x["sharedMaterial"]["sourceText"]+="modified"
                        self.assertNotEqual(shared_revision(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    elif case=="shared_image":
                        x["sharedMaterial"]["imageSha256"]="0"*64
                        self.assertNotEqual(shared_revision(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    elif case=="teaching":
                        x["teaching"]["memory"]+="modified"
                        self.assertNotEqual(canonical(x["teaching"]),q["teachingCanonicalSha256"])

if __name__=="__main__":
    unittest.main()
