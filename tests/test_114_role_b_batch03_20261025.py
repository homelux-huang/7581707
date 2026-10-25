"""114 Role B third batch: source-bound five candidate lessons, no independent approval."""
from pathlib import Path
from datetime import date
import hashlib, json, unittest

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/teaching-candidates/114-role-b-20261025-batch03"
SRC=ROOT/"sudu/data/processed/114"
IDS={"114-00-E-16","114-00-E-17","114-00-E-18","114-00-E-19","114-00-C-05"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def digest(bs):return hashlib.sha256(bs).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def sha(x):return digest(canonical(x))

class RoleB114ThirdBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(DIR/"batch.json")
        cls.qs={x["questionId"]:x for x in load(SRC/"questions.json")["questions"]}
        cls.ms={x["questionId"]:x for x in load(SRC/"webp-manifest.json")["items"]}
    def test_scope_zero_approval(self):
        b=self.batch
        self.assertEqual((b["itemCount"],b["newReady"],b["newLive"]),(5,0,0))
        self.assertEqual(set(x["questionId"] for x in b["items"]),IDS)
        self.assertIs(b["requiresHumanTeacher"],False)
        self.assertIs(b["authorSelfCheckOnly"],True)
        self.assertEqual(b["distinctAiReview"],"PENDING_ROLE_E")
    def test_five_individual_source_and_content_digests(self):
        for row in self.batch["items"]:
            with self.subTest(q=row["questionId"]):
                raw=(ROOT/row["path"]).read_bytes()
                self.assertEqual(digest(raw),row["fileSha256"])
                d=json.loads(raw)
                q,m=self.qs[d["questionId"]],self.ms[d["questionId"]]
                self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
                self.assertEqual(len(d["options"]),4)
                self.assertFalse(q.get("issues") or m.get("issues"))
                self.assertEqual(m["qaStatus"],"PASS")
                self.assertEqual(m["sha256"],q["questionProvenance"]["webpSha256"])
                self.assertEqual(d["source"]["webpSha256"],m["sha256"])
                self.assertEqual(d["source"]["webpPath"],m["output"])
                self.assertEqual(q["assets"]["singleQuestionWebp"],m["output"])
                rev=sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
                self.assertEqual(row["sourceRevision"],rev)
                self.assertEqual(d["source"]["questionRevision"],rev)
                self.assertEqual(row["webpSha256"],m["sha256"])
                self.assertEqual(row["teachingCanonicalSha256"],sha(d["teaching"]))
                self.assertEqual(d["teachingCanonicalSha256"],sha(d["teaching"]))
                combo={"questionId":d["questionId"],"sourceRevision":rev,"webpSha256":m["sha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]}
                self.assertEqual(sha(combo),row["composedTeachingSha256"])
                self.assertEqual(sha(combo),d["composedTeachingSha256"])
    def test_every_option_is_specific_and_dual_level(self):
        for row in self.batch["items"]:
            d=load(ROOT/row["path"]);t=d["teaching"]
            for k in ("teacherSummary","elementarySummary","concept","memory","source"):
                self.assertGreater(len(t[k]),12)
            self.assertGreaterEqual(len(t["solvingSteps"]),3)
            self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
            reasons=[]
            for ch,o in t["optionExplanations"].items():
                self.assertEqual(o["isCorrect"],ch==d["knownAnswerCandidate"])
                self.assertGreater(len(o["teacher"].strip()),35)
                self.assertGreater(len(o["elementary"].strip()),11)
                self.assertGreater(len(o["reason"].strip()),20)
                reasons.append(o["reason"])
            self.assertEqual(len(set(reasons)),4)
            self.assertIs(t["hasExamCalculation"],False)
            self.assertIsNone(t["examCalculation"])
            self.assertNotIn("本題無金額計算",json.dumps(t,ensure_ascii=False))
            self.assertTrue(d["reasoningAudit"]["answerAlreadyKnown"])
            self.assertFalse(d["reasoningAudit"]["blindSolveClaimed"])
    def test_literal_safe_highlight_and_english_news(self):
        for row in self.batch["items"]:
            d=load(ROOT/row["path"]);e=d["enrichment"];orig=(d["question"]+" ".join(d["options"])).casefold()
            for h in e["highlights"]:
                self.assertTrue(h["bold"] and h["highlight"])
                self.assertIn(h["text"].casefold(),orig)
                self.assertFalse(any(x in h["text"].casefold() for x in ("<",">","javascript:","onerror=")))
            if d["subject"]=="英文":
                for v in e["englishVocabulary"]:
                    self.assertIn(v["headword"].casefold(),orig)
                    self.assertIn(v["level"],("初級","中級","高級"))
                    self.assertTrue(v["ipa"].startswith("/") and v["ipa"].endswith("/"))
                    self.assertTrue(v["synonyms"] and v["antonyms"] and v["usageNote"])
                    self.assertTrue(v["dictionaryUrl"].startswith("https://"))
                n=e["newsExample"]
                self.assertIn(n["highlightActualForm"],n["english"])
                self.assertTrue(n["chinese"] and n["notAnArticleQuote"])
                self.assertTrue(n["source"]["url"].startswith("https://"))
                stamp=date.fromisoformat(n["source"]["publicationDate"])
                self.assertGreaterEqual(stamp,date(2023,10,25))
                self.assertLessEqual(stamp,date(2026,10,25))
            else:
                self.assertTrue(e["chineseVocabulary"])
                for v in e["chineseVocabulary"]:
                    self.assertIn(v["level"],("初級","中級","高級"))
    def test_no_human_required_but_distinct_ai_e_is_mandatory(self):
        for row in self.batch["items"]:
            d=load(ROOT/row["path"]);r=d["review"]
            self.assertEqual(r["policyVersion"],"ISSUE36-OWNER-OVERRIDE-2026-10-25")
            self.assertIs(r["requiresHumanTeacher"],False)
            self.assertEqual(r["status"],"BLOCKED")
            self.assertIs(r["studentReleaseApproved"],False)
            self.assertIs(r["formalReady"],False)
            self.assertIs(r["uiQaExactDigest"],False)
            self.assertIsNone(r["independentReviewer"])
            ai=r["independentAiContentReview"]
            self.assertEqual(ai["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
            self.assertEqual(ai["requiredReviewerRole"],"E")
            for k in ("reviewerSessionId","reviewTaskId","reviewIssueCommentId","trustedEvidencePath","reviewNotesSha256"):
                self.assertIsNone(ai[k])
            self.assertIn("DISTINCT_ROLE_E_AI_SUBSTANTIVE_CONTENT_REVIEW_RECEIPT_PENDING",r["blockers"])
            self.assertFalse(any("HUMAN_TEACHER" in z or "ED25519" in z or "SIGNATURE" in z for z in r["blockers"]))
            self.assertIs(d["source"]["finalOfficialAnswerDirectImageQaThisBatch"],False)
    def test_negative_false_evidence_never_yields_release(self):
        def admissible(x):
            review=x.get("independentAiContentReview")
            return isinstance(review,dict) and review.get("status")=="VERIFIED" and review.get("requiredReviewerRole")=="E" and bool(review.get("trustedEvidencePath")) and bool(review.get("reviewNotesSha256"))
        self.assertFalse(admissible({}))
        self.assertFalse(admissible({"independentAiContentReview":{"status":"VERIFIED","requiredReviewerRole":"B"}}))
        self.assertFalse(admissible({"independentAiContentReview":{"status":"VERIFIED","requiredReviewerRole":"E","trustedEvidencePath":None}}))
        for row in self.batch["items"]:
            self.assertFalse(admissible(load(ROOT/row["path"])["review"]))
if __name__=="__main__":unittest.main()
