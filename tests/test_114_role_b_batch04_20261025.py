"""Role B 114 Chinese 08/11-14: source-bound AI author candidates; NO RELEASE."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BATCH_DIR=ROOT/"sudu/teaching-candidates/114-role-b-20261025-batch04"
DATA=ROOT/"sudu/data/processed/114"
IDS={"114-00-C-08","114-00-C-11","114-00-C-12","114-00-C-13","114-00-C-14"}
SOURCE_REV_FIELDS={"question","options","singleQuestionWebpSha256"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical_hash(v):return digest(canonical(v))
def git_blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

class RoleB114ChineseBatch04(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(BATCH_DIR/"batch.json")
        cls.q={q["questionId"]:q for q in load(DATA/"questions.json")["questions"]}
        cls.m={q["questionId"]:q for q in load(DATA/"webp-manifest.json")["items"]}
        cls.docs={r["questionId"]:load(ROOT/r["path"]) for r in cls.batch["items"]}
    def test_inventory_policy_and_no_release(self):
        b=self.batch
        self.assertEqual(b["itemCount"],5)
        self.assertEqual(set(self.docs),IDS)
        self.assertEqual((b["newReady"],b["newMain"],b["newLive"]),(0,0,0))
        self.assertEqual(b["distinctAiReviewerStatus"],"PENDING_ROLE_E")
        self.assertIs(b["requiresHumanTeacher"],False)
        self.assertIs(b["authorSelfCheckOnly"],True)
    def test_source_and_all_five_existing_original_webp_bytes(self):
        for row in self.batch["items"]:
            with self.subTest(qid=row["questionId"]):
                qid=row["questionId"];q=self.q[qid];m=self.m[qid];d=self.docs[qid]
                self.assertFalse(q.get("issues") or m.get("issues"))
                self.assertEqual(len(q["options"]),4)
                self.assertTrue(all(isinstance(x,str) and x.strip() for x in q["options"]))
                self.assertEqual(m["qaStatus"],"PASS")
                self.assertEqual(q["questionProvenance"]["webpSha256"],m["sha256"])
                self.assertEqual(q["assets"]["singleQuestionWebp"],m["output"])
                self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
                asset=ROOT/m["output"]
                self.assertTrue(asset.is_file(),str(asset))
                self.assertEqual(digest(asset.read_bytes()),m["sha256"])
                self.assertEqual(d["source"]["webpSha256"],m["sha256"])
                self.assertEqual(d["source"]["webpPath"],m["output"])
                self.assertEqual(d["source"]["originalQuestionPdfSha256"],q["questionProvenance"]["officialPdfSha256"])
                self.assertEqual(d["source"]["officialAnswerPdfSha256"],q["answerProvenance"]["officialPdfSha256"])
                self.assertIs(d["source"]["finalOfficialAnswerDirectQaThisBatch"],False)
    def test_original_shared_article_is_existing_pixels_not_regenerated(self):
        for qid in sorted(IDS-{"114-00-C-08"}):
            with self.subTest(qid=qid):
                d=self.docs[qid];r=d["source"]["readingContext"]
                self.assertTrue(r["checkedByAuthorFromExistingOriginalPixels"])
                self.assertIs(r["ocrRecreated"],False)
                self.assertIs(r["recropPerformed"],False)
                self.assertIs(r["formalIndependentSharedMaterialQaAdded"],False)
                for suffix in ("4","5"):
                    path=ROOT/r["originalReadingPage4Path" if suffix=="4" else "originalQuestionPage5Path"]
                    oid=r["originalReadingPage4GitBlob" if suffix=="4" else "originalQuestionPage5GitBlob"]
                    self.assertTrue(path.is_file())
                    self.assertEqual(git_blob(path.read_bytes()),oid)
                self.assertEqual(digest((ROOT/r["originalQuestionPage5Path"]).read_bytes()),r["questionPage5PixelSha256"])
                self.assertEqual(r["questionPage5PixelSha256"],self.m[qid]["sourceSha256"])
                qa_path=ROOT/d["source"]["originalImageQaEvidence"]
                self.assertTrue(qa_path.is_file())
                old=load(qa_path)
                record=next(x for x in old["items"] if x["questionId"]==qid)
                self.assertEqual(record["reviewedWebpSha256"],d["source"]["webpSha256"])
                self.assertEqual(record["reviewResult"],"PASS_DIRECT_SOURCE_PAGE_TO_SINGLE_WEBP")
                self.assertIs(record["answerVerified"],False)
    def test_source_revision_teaching_canonical_digest_and_full_file_sha(self):
        for row in self.batch["items"]:
            with self.subTest(qid=row["questionId"]):
                d=self.docs[row["questionId"]];q=self.q[row["questionId"]];m=self.m[row["questionId"]]
                source={"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]}
                rev=canonical_hash(source)
                self.assertEqual(set(source),SOURCE_REV_FIELDS)
                self.assertEqual(rev,row["sourceRevision"])
                self.assertEqual(rev,d["source"]["questionRevision"])
                self.assertEqual(m["sha256"],row["webpSha256"])
                self.assertEqual(canonical_hash(d["teaching"]),row["teachingCanonicalSha256"])
                self.assertEqual(canonical_hash(d["teaching"]),d["teachingCanonicalSha256"])
                composed={"questionId":row["questionId"],"sourceRevision":rev,"webpSha256":m["sha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]}
                self.assertEqual(canonical_hash(composed),row["composedTeachingSha256"])
                self.assertEqual(canonical_hash(composed),d["composedTeachingSha256"])
                self.assertEqual(digest((ROOT/row["path"]).read_bytes()),row["fileSha256"])
    def test_each_option_specific_double_layer_and_no_calculation_placeholder(self):
        for d in self.docs.values():
            t=d["teaching"]
            for key in ("teacherSummary","elementarySummary","concept","memory"):
                self.assertGreater(len(t[key]),25)
            self.assertGreaterEqual(len(t["solvingSteps"]),3)
            self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
            rs=[]
            for option,z in t["optionExplanations"].items():
                self.assertGreaterEqual(len(z["teacher"].strip()),34)
                self.assertGreaterEqual(len(z["elementary"].strip()),12)
                self.assertGreaterEqual(len(z["reason"].strip()),27)
                self.assertIs(type(z["isCorrect"]),bool)
                self.assertEqual(z["isCorrect"],option==d["knownAnswerCandidate"])
                rs.append(z["reason"].strip())
            self.assertEqual(len(set(rs)),4)
            self.assertIs(t["hasExamCalculation"],False)
            self.assertIsNone(t["examCalculation"])
            self.assertNotIn("本題無金額計算",json.dumps(t,ensure_ascii=False))
            self.assertIs(d["reasoningAudit"]["answerAlreadyKnown"],True)
            self.assertIs(d["reasoningAudit"]["blindSolveClaimed"],False)
    def test_highlights_are_exact_original_source_text_and_graded(self):
        for d in self.docs.values():
            original=(d["question"]+" "+" ".join(d["options"])).casefold()
            hits=d["enrichment"]["highlights"]
            self.assertTrue(hits)
            for h in hits:
                self.assertIs(h["bold"],True);self.assertIs(h["highlight"],True)
                self.assertIn(h["text"].casefold(),original)
                for bad in ("<",">","javascript:","onerror="):
                    self.assertNotIn(bad,h["text"].casefold())
            levels={v["level"] for v in d["enrichment"]["chineseVocabulary"]}
            self.assertTrue(levels.issubset({"初級","中級","高級"}))
            self.assertGreaterEqual(len(levels),2)
    def test_independent_ai_review_and_final_answer_never_self_approved(self):
        for d in self.docs.values():
            v=d["review"];a=v["independentAiContentReview"]
            self.assertEqual(v["status"],"BLOCKED")
            self.assertEqual(v["policyVersion"],"ISSUE36-OWNER-OVERRIDE-2026-10-25")
            self.assertIs(v["requiresHumanTeacher"],False)
            self.assertIs(v["studentReleaseApproved"],False)
            self.assertIs(v["formalReady"],False)
            self.assertIs(v["uiQaExactDigest"],False)
            self.assertIsNone(v["independentReviewer"])
            self.assertEqual(a["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
            self.assertEqual(a["requiredReviewerRole"],"E")
            for k in ("reviewerSessionId","reviewTaskId","reviewIssueCommentId","trustedEvidencePath","reviewNotesSha256"):
                self.assertIsNone(a[k])
            self.assertIn("DISTINCT_ROLE_E_AI_SUBSTANTIVE_CONTENT_REVIEW_RECEIPT_PENDING",v["blockers"])
            self.assertFalse(any(x in z for z in v["blockers"] for x in ("HUMAN_TEACHER","ED25519","SIGNATURE")))
            self.assertEqual(set(d["textbook"].values())-{None},{"待核對"})
    def test_negative_modification_and_fabricated_approval_rejected(self):
        d=self.docs["114-00-C-11"]
        expected=d["composedTeachingSha256"]
        combo={"questionId":d["questionId"],"sourceRevision":d["source"]["questionRevision"],"webpSha256":d["source"]["webpSha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]}
        self.assertEqual(canonical_hash(combo),expected)
        modified=dict(combo,webpSha256="0"*64)
        self.assertNotEqual(canonical_hash(modified),expected)
        changed=dict(combo,sourceRevision="f"*64)
        self.assertNotEqual(canonical_hash(changed),expected)
        no_receipt={"status":"VERIFIED","requiredReviewerRole":"E","trustedEvidencePath":None,"reviewNotesSha256":None}
        self.assertFalse(bool(no_receipt.get("trustedEvidencePath") and no_receipt.get("reviewNotesSha256")))
        self.assertNotEqual(d["review"]["independentAiContentReview"]["status"],"VERIFIED")

if __name__=="__main__":unittest.main()
