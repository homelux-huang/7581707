"""Issue36 Role C three authored source-bound Chinese/English lessons: NEVER mark READY."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/teaching-candidates/115-role-c-chinese14-english36-37-20261025"
EXPECTED={"115-00-C-14":("B",True),"115-00-E-36":("D",False),"115-00-E-37":("D",False)}
SHARED_SHA={
    "115-00-C-14":"bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66",
    "115-00-E-36":"180430801f1b7c0775f2ff360c80d0b8d1828e26b95742ca52f57e72c5f4e418",
    "115-00-E-37":"180430801f1b7c0775f2ff360c80d0b8d1828e26b95742ca52f57e72c5f4e418",
}
ANCHORS={
    "115-00-C-14":("對方想表示即時回去有困難","那另一面是什麼？難道哈利路亞？"),
    "115-00-E-36":("plenty of free, unsupervised outdoor play","Instead of interacting face to face"),
    "115-00-E-37":("protect them too much and carefully control their daily activities","shift from a play-based childhood to a phone-based one"),
}
def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()
def canon(obj):
    return digest_bytes(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def textrev(q):
    return canon({"question":q["question"],"options":q["options"],
                  "singleQuestionWebpSha256":q["individualImageSha256"]})
def sharedrev(q):
    s=q["sharedMaterial"]
    return canon({"sharedMaterialId":s["id"],"text":s["sourceText"],
                  "outputSha256":s["originalImageSha256"]})
class ThreeNewRoleC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((DIR/"batch.json").read_text(encoding="utf-8"))
        cls.items={i["questionId"]:i for i in cls.batch["items"]}
        cls.q={qid:json.loads((ROOT/i["path"]).read_text(encoding="utf-8"))
               for qid,i in cls.items.items()}
    def test_exact_claim_three_and_zero_ready(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-C14-E36-E37-20261025-06")
        self.assertEqual(b["claimedAtUtc"],"2026-10-25T05:27:53Z")
        self.assertEqual(b["baseSHA"],"3c696903ac5b089f355885c98ab71a74cb79dced")
        self.assertEqual(set(self.q),set(EXPECTED))
        self.assertEqual((b["newReady"],b["newLive"]),(0,0))
        self.assertTrue(all(not i["ready"] for i in self.items.values()))
    def test_canonical_sha_source_shared_and_teaching_integrity(self):
        for qid,q in self.q.items():
            i=self.items[qid]
            with self.subTest(qid=qid):
                self.assertEqual(digest_bytes((ROOT/i["path"]).read_bytes()),i["fileSha256"])
                self.assertEqual(textrev(q),i["sourceTextRevision"])
                self.assertEqual(q["sourceTextRevision"],i["sourceTextRevision"])
                self.assertEqual(canon(q["teaching"]),i["teachingDigest"])
                self.assertEqual(q["teachingCanonicalSha256"],i["teachingDigest"])
                self.assertEqual(q["individualImageSha256"],i["individualImageSha256"])
                self.assertEqual(sharedrev(q),i["sharedMaterialRevision"])
                self.assertEqual(q["sharedMaterial"]["sharedMaterialRevision"],i["sharedMaterialRevision"])
                self.assertEqual(q["sharedMaterial"]["originalImageSha256"],SHARED_SHA[qid])
                self.assertEqual(q["sharedMaterial"]["originalImageSha256"],i["sharedOriginalImageSha256"])
                self.assertEqual(digest_bytes(q["sharedMaterial"]["sourceText"].encode("utf-8")),
                                 q["sharedMaterial"]["textSha256"])
                self.assertEqual(q["answerCandidate"],EXPECTED[qid][0])
                self.assertEqual(len(q["options"]),4)
    def test_all_four_options_with_both_levels_and_primary_evidence(self):
        for qid,q in self.q.items():
            t=q["teaching"]
            with self.subTest(qid=qid):
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([k for k in "ABCD" if t["optionExplanations"][k]["isCorrect"]],[q["answerCandidate"]])
                for letter in "ABCD":
                    reason=t["optionExplanations"][letter]
                    self.assertGreaterEqual(len(reason["teacher"]),60)
                    self.assertGreaterEqual(len(reason["elementary"]),25)
                    self.assertGreaterEqual(len(reason["sourceEvidence"]),20)
                    self.assertEqual(reason["reason"],reason["teacher"])
                for fld in ("teacherSummary","elementarySummary","concept","memory","extension","highlights","stepByStep"):
                    self.assertTrue(t[fld])
                self.assertIn("**",t["teacherSummary"])
                self.assertIn("**",t["memory"])
                self.assertGreaterEqual(len(t["highlights"]),5)
                self.assertGreaterEqual(len(t["stepByStep"]),3)
                self.assertFalse(t["hasExamCalculation"])
                self.assertIsNone(t["examCalculation"])
    def test_passage_anchors_c14_table_and_actual_news_highlights(self):
        for qid,q in self.q.items():
            with self.subTest(qid=qid):
                text=" ".join(q["sharedMaterial"]["sourceText"].split()).lower()
                for anchor in ANCHORS[qid]:
                    self.assertIn(" ".join(anchor.split()).lower(),text)
                t=q["teaching"]
                if qid=="115-00-C-14":
                    for term in ("何者不適當","第一人稱敘述觀點","第三人稱全知敘述觀點"):
                        self.assertIn(term,q["question"])
                    self.assertEqual(set(t["chineseLevelVocabulary"]),{"初級","中級","高級"})
                    self.assertIn("C14_TABLE_RAW_OFFICIAL_PIXELS_NOT_VISUALLY_CONFIRMED",q["blockers"])
                else:
                    e=t["english"]
                    self.assertEqual(set(e["synonyms"]),{"初級","中級","高級"})
                    self.assertEqual(set(e["antonyms"]),{"初級","中級","高級"})
                    self.assertTrue(all(e[k][level] for k in ("synonyms","antonyms") for level in ("初級","中級","高級")))
                    self.assertTrue(e["pronunciationIPA"].startswith("/"))
                    self.assertIn("**"+e["newsExampleHighlightedSurfaceForm"]+"**",e["newsExampleEnglish"])
                    self.assertGreater(len(e["newsExampleChinese"]),20)
                    self.assertIn("非來源逐字引述",e["newsExampleKind"])
                    self.assertTrue(e["newsExampleSourceUrl"].startswith("https://www.unicef.org/"))
                    self.assertTrue(e["newsExampleSourceDate"].startswith("2025-"))
        self.assertIn("no clear proof",self.q["115-00-E-37"]["teaching"]["english"]["newsExampleEnglish"])
        self.assertIn("螢幕時間本身",self.q["115-00-E-36"]["teaching"]["extension"])
    def test_independent_review_source_approval_shared_still_pending(self):
        for qid,q in self.q.items():
            r=q["review"]
            self.assertFalse(q["studentReleaseApproved"])
            self.assertFalse(q["deploy"])
            self.assertFalse(q["sourceQuestionVerified"])
            self.assertEqual(q["sourceAnswerVerified"],EXPECTED[qid][1])
            self.assertFalse(q["newBlindSolveClaimed"])
            self.assertFalse(q["individualImageBytesRehashedThisSession"])
            self.assertFalse(q["sharedMaterial"]["sharedImageBytesRehashedThisSession"])
            self.assertEqual(q["sharedMaterial"]["qaStatus"],"PENDING_INDIVIDUAL_VISUAL_QA")
            self.assertEqual(self.items[qid]["sharedQa"],"PENDING_INDIVIDUAL_VISUAL_QA")
            self.assertTrue(r["differentAuthorRequired"])
            self.assertTrue(r["sameAuthorApprovalProhibited"])
            self.assertEqual(r["distinctAiContentReview"],"PENDING")
            self.assertIsNone(r["independentAiReviewerIdentity"])
            self.assertIsNone(r["reviewEvidenceSha256"])
            self.assertIsNone(r["officialEvidenceSha256"])
            self.assertEqual(r["v4EightByTwoExactDigest"],"PENDING")
            self.assertTrue(all("HUMAN_TEACHER" not in k for k in q["blockers"]))
    def test_negative_tampering_source_shared_image_and_teaching_must_fail(self):
        for qid,q in self.q.items():
            for edit in ("question","option","individual","sharedtext","sharedimage","teaching"):
                with self.subTest(qid=qid,edit=edit):
                    x=copy.deepcopy(q)
                    if edit=="question":
                        x["question"]+=" tampered"
                        self.assertNotEqual(textrev(x),q["sourceTextRevision"])
                    elif edit=="option":
                        x["options"][0]+=" tampered"
                        self.assertNotEqual(textrev(x),q["sourceTextRevision"])
                    elif edit=="individual":
                        x["individualImageSha256"]="0"*64
                        self.assertNotEqual(textrev(x),q["sourceTextRevision"])
                    elif edit=="sharedtext":
                        x["sharedMaterial"]["sourceText"]+=" tampered"
                        self.assertNotEqual(sharedrev(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    elif edit=="sharedimage":
                        x["sharedMaterial"]["originalImageSha256"]="0"*64
                        self.assertNotEqual(sharedrev(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    else:
                        x["teaching"]["memory"]+=" tampered"
                        self.assertNotEqual(canon(x["teaching"]),q["teachingCanonicalSha256"])
if __name__=="__main__":
    unittest.main()
