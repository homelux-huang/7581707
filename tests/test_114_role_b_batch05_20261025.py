"""Role B 114 C20-22 source-bound separate shared original asset author drafts; no RELEASE."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"sudu/data/processed/114"
DIR=ROOT/"sudu/teaching-candidates/114-role-b-20261025-batch05"
IDS={"114-00-C-20","114-00-C-21","114-00-C-22"}
SID="114-00-C-SHARED-20-23"
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")
def sha(obj):return sha_bytes(canonical(obj))
def blob_sha(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

class ChineseSharedBatch05(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(DIR/"batch.json")
        src=load(BANK/"questions.json")
        cls.bank={x["questionId"]:x for x in src["questions"]}
        cls.shared=next(x for x in src["sharedMaterials"] if x["sharedMaterialId"]==SID)
        cls.m={x["questionId"]:x for x in load(BANK/"webp-manifest.json")["items"]}
        cls.docs={r["questionId"]:load(ROOT/r["path"]) for r in cls.batch["items"]}
        cls.qa=load(ROOT/cls.batch["priorVisualQA"])
    def test_exact_scope_and_fail_closed_no_release(self):
        b=self.batch
        self.assertEqual(b["itemCount"],3)
        self.assertEqual(set(self.docs),IDS)
        self.assertNotIn("114-00-C-23",IDS)
        self.assertIn("114-00-C-23",b["excludedQuarantinedIds"])
        self.assertEqual((b["newReady"],b["newMain"],b["newLive"]),(0,0,0))
        self.assertIs(b["requiresHumanTeacher"],False)
        self.assertIs(b["authorSelfCheckOnly"],True)
        self.assertEqual(b["independentAiContentReviewer"],"PENDING_ROLE_E")
    def test_real_original_shared_article_bytes_sha_and_archived_qa(self):
        b=self.batch;s=self.shared
        self.assertEqual(s["sharedMaterialId"],SID)
        self.assertEqual(s["qaStatus"],"PASS")
        self.assertEqual(s["sha256"],b["sharedMaterialWebpSha256"])
        self.assertEqual(s["sha256"],b["items"][0]["sharedWebpSha256"])
        raw=(ROOT/s["output"]).read_bytes()
        self.assertEqual(sha_bytes(raw),s["sha256"])
        self.assertEqual(blob_sha(raw),b["sharedArticleOriginalGitBlob"])
        original=(ROOT/s["source"]).read_bytes()
        self.assertEqual(sha_bytes(original),s["sourceSha256"])
        self.assertEqual(s["sourceSha256"],b["originalPage7Sha256"])
        self.assertEqual(self.qa["sharedMaterial"]["outputSha256"],s["sha256"])
        self.assertEqual(self.qa["sharedMaterial"]["result"],"PASS_DIRECT_ORIGINAL_PAGE_SHARED_ARTICLE_VISUAL")
        self.assertIs(self.qa["sharedMaterial"]["integrationReady"],False)
    def test_each_original_question_webp_bytes_and_shared_link(self):
        for id in sorted(IDS):
            with self.subTest(id=id):
                q=self.bank[id];m=self.m[id];d=self.docs[id]
                self.assertFalse(q.get("issues") or m.get("issues"))
                self.assertEqual(m["qaStatus"],"PASS")
                self.assertEqual(len(q["options"]),4)
                self.assertTrue(all(isinstance(o,str) and o.strip() for o in q["options"]))
                self.assertEqual(q["questionProvenance"]["webpSha256"],m["sha256"])
                self.assertEqual(sha_bytes((ROOT/m["output"]).read_bytes()),m["sha256"])
                self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
                self.assertEqual(d["source"]["webpSha256"],m["sha256"])
                self.assertEqual(d["source"]["webpPath"],m["output"])
                self.assertEqual(q["sharedMaterialIds"],[SID])
                self.assertEqual(d["source"]["sharedMaterialId"],SID)
                self.assertEqual(d["source"]["sharedMaterialWebpSha256"],self.shared["sha256"])
                self.assertEqual(d["source"]["originalQuestionPdfSha256"],q["questionProvenance"]["officialPdfSha256"])
                self.assertEqual(d["source"]["officialAnswerPdfSha256"],q["answerProvenance"]["officialPdfSha256"])
                original_evidence=next(e for e in self.qa["items"] if e["questionId"]==id)
                self.assertEqual(original_evidence["reviewedWebpSha256"],m["sha256"])
                self.assertEqual(original_evidence["result"],"PASS_DIRECT_ORIGINAL_PAGE_IMAGE")
                self.assertIs(original_evidence["answerVerified"],False)
                self.assertIs(original_evidence["questionVerified"],False)
                self.assertIs(d["source"]["finalOfficialAnswerPerQuestionImageQaThisBatch"],False)
    def test_source_revision_teaching_digest_and_all_full_file_hashes(self):
        for row in self.batch["items"]:
            with self.subTest(id=row["questionId"]):
                id=row["questionId"];d=self.docs[id];q=self.bank[id];m=self.m[id]
                rev=sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
                self.assertEqual(d["source"]["questionRevision"],rev)
                self.assertEqual(row["sourceRevision"],rev)
                self.assertEqual(row["webpSha256"],m["sha256"])
                self.assertEqual(row["sharedMaterialId"],SID)
                self.assertEqual(row["sharedWebpSha256"],self.shared["sha256"])
                self.assertEqual(d["teachingCanonicalSha256"],sha(d["teaching"]))
                self.assertEqual(row["teachingCanonicalSha256"],sha(d["teaching"]))
                composed=sha({"questionId":id,"sourceRevision":rev,"webpSha256":m["sha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]})
                self.assertEqual(composed,d["composedTeachingSha256"])
                self.assertEqual(composed,row["composedTeachingSha256"])
                self.assertEqual(sha_bytes((ROOT/row["path"]).read_bytes()),row["fileSha256"])
                e=d["enrichment"]["sharedReading"]
                self.assertEqual(e["webpSha256"],self.shared["sha256"])
                self.assertEqual(e["originalPage7Sha256"],self.shared["sourceSha256"])
                self.assertIs(e["sourceAlreadyOriginalNotRegenerated"],True)
    def test_all_four_distinct_option_reasons_and_elementary_clarity(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                t=d["teaching"]
                self.assertTrue(all(len(t[k].strip())>=22 for k in ("teacherSummary","elementarySummary","concept","memory")))
                self.assertGreaterEqual(len(t["solvingSteps"]),3)
                self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
                seen=[]
                for ch,z in t["optionExplanations"].items():
                    self.assertGreaterEqual(len(z["teacher"].strip()),32)
                    self.assertGreaterEqual(len(z["elementary"].strip()),14)
                    self.assertGreaterEqual(len(z["reason"].strip()),26)
                    self.assertIs(type(z["isCorrect"]),bool)
                    self.assertEqual(z["isCorrect"],ch==d["knownAnswerCandidate"])
                    seen.append(z["reason"].strip())
                self.assertEqual(len(set(seen)),4)
                self.assertIs(t["hasExamCalculation"],False)
                self.assertIsNone(t["examCalculation"])
                self.assertNotIn("本題無金額計算",json.dumps(t,ensure_ascii=False))
                self.assertIs(d["reasoningAudit"]["answerAlreadyKnown"],True)
                self.assertIs(d["reasoningAudit"]["blindSolveClaimed"],False)
    def test_only_literal_text_highlight_and_chinese_graded_terms(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                corpus=(d["question"]+" ".join(d["options"])).casefold()
                h=d["enrichment"]["highlights"]
                self.assertTrue(h)
                for word in h:
                    self.assertIs(word["bold"],True)
                    self.assertIs(word["highlight"],True)
                    self.assertIn(word["text"].casefold(),corpus)
                    self.assertFalse(any(x in word["text"].casefold() for x in ("<",">","javascript:","onerror=")))
                vocab=d["enrichment"]["chineseVocabulary"]
                self.assertGreaterEqual(len(vocab),3)
                levels={v["level"] for v in vocab}
                self.assertTrue(levels.issubset({"初級","中級","高級"}))
                self.assertGreaterEqual(len(levels),2)
    def test_author_cannot_independently_approve_or_override_quarantine(self):
        for d in self.docs.values():
            v=d["review"];ai=v["independentAiContentReview"]
            self.assertEqual(v["policyVersion"],"ISSUE36-OWNER-OVERRIDE-2026-10-25")
            self.assertEqual(v["status"],"BLOCKED")
            self.assertIs(v["requiresHumanTeacher"],False)
            self.assertIs(v["studentReleaseApproved"],False)
            self.assertIs(v["formalReady"],False)
            self.assertIs(v["uiQaExactDigest"],False)
            self.assertIsNone(v["independentReviewer"])
            self.assertEqual(ai["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
            self.assertEqual(ai["requiredReviewerRole"],"E")
            for k in ("reviewerSessionId","reviewTaskId","reviewIssueCommentId","trustedEvidencePath","reviewNotesSha256"):
                self.assertIsNone(ai[k])
            self.assertIn("DISTINCT_ROLE_E_AI_SUBSTANTIVE_CONTENT_REVIEW_RECEIPT_PENDING",v["blockers"])
        self.assertNotIn("114-00-C-23",self.docs)
    def test_negative_tampered_original_or_shared_asset_is_not_same_version(self):
        d=self.docs["114-00-C-20"]
        base={"questionId":d["questionId"],"sourceRevision":d["source"]["questionRevision"],"webpSha256":d["source"]["webpSha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]}
        original=sha(base)
        self.assertEqual(original,d["composedTeachingSha256"])
        bad=dict(base,sourceRevision="f"*64)
        self.assertNotEqual(sha(bad),original)
        fake=dict(base)
        fake["enrichment"]=dict(d["enrichment"])
        fake["enrichment"]["sharedReading"]=dict(d["enrichment"]["sharedReading"],webpSha256="0"*64)
        self.assertNotEqual(sha(fake),original)
        self.assertNotEqual(self.docs["114-00-C-21"]["composedTeachingSha256"],self.docs["114-00-C-22"]["composedTeachingSha256"])

if __name__=="__main__":unittest.main()
