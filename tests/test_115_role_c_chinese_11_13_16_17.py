"""Role C / Issue #36 five Chinese author drafts, NO independent certification or release."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "sudu/teaching-candidates/115-role-c-chinese11-13-16-17-20261025"
EXPECTED = {
    "115-00-C-11": ("D", True),
    "115-00-C-12": ("C", True),
    "115-00-C-13": ("D", True),
    "115-00-C-16": ("A", False),
    "115-00-C-17": ("C", False),
}
PASSAGE_SHA = {
    "115-00-C-11": "bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66",
    "115-00-C-12": "bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66",
    "115-00-C-13": "bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66",
    "115-00-C-16": "f1a3eac89b4f1db5d32a6511f070ef463a8759116a780257a7c213ab5d1fd77c",
    "115-00-C-17": "f1a3eac89b4f1db5d32a6511f070ef463a8759116a780257a7c213ab5d1fd77c",
}
ANCHORS = {
    "115-00-C-11": ("六個也算老女人的女兒輩都回來", "所以，我們與你一起坐上救護車"),
    "115-00-C-12": ("粉娘又彌留在廳頭", "我知道我人生最荒謬的一趟旅程"),
    "115-00-C-13": ("對方言語支吾", "我們竟然說好"),
    "115-00-C-16": ("皆因夫人看重", "探春當家，豈能逾矩"),
    "115-00-C-17": ("這都叫按例而行嗎", "妳越發該拉拔拉拔我們"),
}

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return sha256(json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8"))

def source_revision(q):
    return canonical({
        "question": q["question"], "options": q["options"],
        "singleQuestionWebpSha256": q["imageSha256"],
    })

def shared_revision(q):
    s=q["sharedMaterial"]
    return canonical({
        "sharedMaterialId":s["id"], "text":s["sourceText"],
        "outputSha256":s["imageSha256"],
    })

class NewFiveChineseAuthorOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=json.loads((DIR/"batch.json").read_text(encoding="utf-8"))
        cls.items={i["questionId"]:i for i in cls.batch["items"]}
        cls.lessons={
            k:json.loads((ROOT/v["path"]).read_text(encoding="utf-8"))
            for k,v in cls.items.items()
        }

    def test_exact_claim_task_scope_and_no_new_release(self):
        b=self.batch
        self.assertEqual(b["taskId"],"C-115-C11-13-C16-17-DUAL-LEVEL-20261025-05")
        self.assertEqual(b["claimedAtUtc"],"2026-10-25T05:20:54Z")
        self.assertEqual(b["baseSHA"],"3c13c12f8dbaf92f23f9fbb58cde3916f9e6b088")
        self.assertEqual(b["sourceHead"],"e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5")
        self.assertEqual(set(self.items),set(EXPECTED))
        self.assertEqual((b["newReady"],b["newLive"]),(0,0))
        self.assertEqual(len(self.items),5)
        self.assertTrue(all(not i["ready"] for i in self.items.values()))

    def test_exact_source_text_option_and_binary_manifest_sha_bindings(self):
        for qid,q in self.lessons.items():
            i=self.items[qid]
            with self.subTest(qid=qid):
                self.assertEqual(sha256((ROOT/i["path"]).read_bytes()),i["fileSha256"])
                self.assertEqual(q["sourceTextRevision"],i["sourceTextRevision"])
                self.assertEqual(source_revision(q),i["sourceTextRevision"])
                self.assertEqual(q["teachingCanonicalSha256"],i["teachingCanonicalSha256"])
                self.assertEqual(canonical(q["teaching"]),i["teachingCanonicalSha256"])
                self.assertEqual(q["imageSha256"],i["individualWebpSha256"])
                self.assertEqual(q["sharedMaterial"]["imageSha256"],PASSAGE_SHA[qid])
                self.assertEqual(q["sharedMaterial"]["imageSha256"],i["sharedOriginalImageSha256"])
                self.assertEqual(q["sharedMaterial"]["sharedMaterialRevision"],i["sharedMaterialRevision"])
                self.assertEqual(shared_revision(q),i["sharedMaterialRevision"])
                self.assertEqual(sha256(q["sharedMaterial"]["sourceText"].encode("utf-8")),
                                 q["sharedMaterial"]["textSha256"])
                self.assertEqual(len(q["options"]),4)
                self.assertEqual(q["questionId"],qid)
                self.assertEqual(q["year"],115)
                self.assertEqual(q["subject"],"國文")
                self.assertEqual(q["answerCandidate"],EXPECTED[qid][0])

    def test_a_to_d_are_individually_complete_and_both_reading_levels(self):
        for qid,q in self.lessons.items():
            t=q["teaching"]
            with self.subTest(qid=qid):
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                self.assertEqual([c for c in "ABCD" if t["optionExplanations"][c]["isCorrect"]],
                                 [EXPECTED[qid][0]])
                raw="".join(q["sharedMaterial"]["sourceText"].split())
                for letter in "ABCD":
                    v=t["optionExplanations"][letter]
                    self.assertGreaterEqual(len(v["teacher"]),50,(qid,letter,"teacher"))
                    self.assertGreaterEqual(len(v["elementary"]),25,(qid,letter,"elementary"))
                    self.assertGreaterEqual(len(v["sourceEvidence"]),18,(qid,letter,"evidence"))
                    self.assertEqual(v["reason"],v["teacher"])
                    # Every option quotes a substantive fragment actually present in
                    # the saved original passage candidate; doesn't certify PDF pixels.
                    tokens=re.findall(r"[\u4e00-\u9fff]{4,}", "".join(v["sourceEvidence"].split()))
                    self.assertTrue(any(token in raw for token in tokens),
                                    (qid,letter,"ungrounded passage evidence"))
                for key in ("teacherSummary","elementarySummary","memory","concept",
                            "extension","highlights","stepByStep","source"):
                    self.assertTrue(t[key],(qid,key))
                self.assertIn("**",t["teacherSummary"])
                self.assertIn("**",t["memory"])
                self.assertGreaterEqual(len(t["highlights"]),5)
                self.assertGreaterEqual(len(t["stepByStep"]),3)
                self.assertEqual(set(t["chineseLevelVocabulary"]),{"初級","中級","高級"})
                self.assertTrue(all(t["chineseLevelVocabulary"][level]
                                    for level in ("初級","中級","高級")))
                self.assertFalse(t["hasExamCalculation"])
                self.assertIsNone(t["examCalculation"])

    def test_two_shared_passages_have_grounded_anchors_but_qa_is_pending(self):
        for qid,q in self.lessons.items():
            with self.subTest(qid=qid):
                raw="".join(q["sharedMaterial"]["sourceText"].split())
                for anchor in ANCHORS[qid]:
                    self.assertIn("".join(anchor.split()),raw)
                expected_qa = ("PASS_DIRECT_ORIGINAL_OFFICIAL_PAGE_SHARED_MATERIAL_VISUAL"
                               if qid in ("115-00-C-16", "115-00-C-17")
                               else "PENDING_INDIVIDUAL_VISUAL_QA")
                self.assertEqual(q["sharedMaterial"]["qaStatus"], expected_qa)
                self.assertEqual(self.items[qid]["sharedImageQa"], expected_qa)
                if qid in ("115-00-C-16", "115-00-C-17"):
                    self.assertEqual(q["sharedMaterial"]["image"],
                        "sudu/data/processed/115/qa-drafts/webp-v4/shared/115-00-C-SHARED-16-18.webp")
                    self.assertIn("SHARED_SOURCE_TEXT_TWO_COLUMN_G2_OCR_RECONCILIATION_PENDING",
                                  q["blockers"])
                self.assertTrue(q["sourceImageManifestQa"]=="PASS")
                self.assertFalse(q["sharedMaterial"]["originalSharedWebpBytesRehashedThisSession"])
                self.assertFalse(q["originalImageBytesRehashedThisSession"])

    def test_review_is_distinct_ai_and_no_official_or_live_promotion(self):
        for qid,q in self.lessons.items():
            with self.subTest(qid=qid):
                self.assertFalse(q["sourceQuestionVerified"])
                self.assertEqual(q["sourceAnswerVerified"],EXPECTED[qid][1])
                self.assertEqual(self.items[qid]["historicalSourceAnswerVerified"],
                                 EXPECTED[qid][1])
                self.assertFalse(q["studentReleaseApproved"])
                self.assertFalse(q["deploy"])
                self.assertFalse(q["newBlindSolveClaimed"])
                r=q["review"]
                self.assertEqual(r["independentAiContentReview"],"PENDING")
                self.assertTrue(r["distinctAuthorRequired"])
                self.assertFalse(r["selfReviewAllowedAsIndependentQa"])
                self.assertIsNone(r["independentAiReviewerIdentity"])
                self.assertIsNone(r["reviewEvidenceSha256"])
                self.assertIsNone(r["sourceOfficialEvidenceSha256"])
                self.assertEqual(r["officialAnswerAndNoticeAdmission"],"PENDING")
                self.assertEqual(
                    r["originalTextAndSharedImageIndependentQa"],
                    ("G1_V4_IMAGE_ONLY_PASS_G2_TEXT_PENDING"
                     if qid in ("115-00-C-16","115-00-C-17") else "PENDING"))
                self.assertEqual(r["v4ExactDigestEightViewportsTwoThemes"],"PENDING")
                self.assertTrue(all("HUMAN_TEACHER" not in b for b in q["blockers"]))
                self.assertIn("DISTINCT_AI_CONTENT_REVIEW_EXACT_SOURCE_IMAGE_LESSON_EVIDENCE_PENDING",
                              q["blockers"])

    def test_any_question_option_or_image_change_invalidates_source_digest(self):
        for qid,q in self.lessons.items():
            original=q["sourceTextRevision"]
            for edit in ("question","option","image"):
                with self.subTest(qid=qid,edit=edit):
                    x=copy.deepcopy(q)
                    if edit=="question": x["question"]+=" tampered"
                    elif edit=="option": x["options"][0]+=" tampered"
                    else: x["imageSha256"]="0"*64
                    self.assertNotEqual(source_revision(x),original)

    def test_any_shared_text_image_or_lesson_change_invalidates_digest(self):
        for qid,q in self.lessons.items():
            for edit in ("shared_text","shared_image","lesson"):
                with self.subTest(qid=qid,edit=edit):
                    x=copy.deepcopy(q)
                    if edit=="shared_text":
                        x["sharedMaterial"]["sourceText"]+=" tampered"
                        self.assertNotEqual(shared_revision(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    elif edit=="shared_image":
                        x["sharedMaterial"]["imageSha256"]="0"*64
                        self.assertNotEqual(shared_revision(x),q["sharedMaterial"]["sharedMaterialRevision"])
                    else:
                        x["teaching"]["memory"]+=" tampered"
                        self.assertNotEqual(canonical(x["teaching"]),q["teachingCanonicalSha256"])

if __name__=="__main__":
    unittest.main()
