"""114 Role B batch02 author-only candidate gates; never releases."""
import hashlib
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "sudu/teaching-candidates/114-role-b-20261025-batch02"
DATA = ROOT / "sudu/data/processed/114"
IDS = {"114-00-E-11","114-00-E-12","114-00-E-13","114-00-E-14","114-00-C-04"}
LETTERS = {"A","B","C","D"}
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def chash(obj): return sha(canonical(obj))

class RoleB114Batch02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read(BATCH/"batch.json")
        cls.questions={q["questionId"]:q for q in read(DATA/"questions.json")["questions"]}
        cls.manifest={m["questionId"]:m for m in read(DATA/"webp-manifest.json")["items"]}
    def test_scope_and_blocking(self):
        b=self.batch
        self.assertEqual(b["role"],"B")
        self.assertEqual((b["itemCount"],b["newReady"],b["newLive"]),(5,0,0))
        self.assertEqual({r["questionId"] for r in b["items"]},IDS)
        self.assertFalse(b["independentHumanTeacherVerified"])
        self.assertFalse(b["officialFinalAnswersIndividualQaVerified"])
    def test_revisions_and_canonical_digests(self):
        for r in self.batch["items"]:
            with self.subTest(q=r["questionId"]):
                raw=(ROOT/r["path"]).read_bytes()
                self.assertEqual(sha(raw),r["fileSha256"])
                d=json.loads(raw); q=self.questions[d["questionId"]]; m=self.manifest[d["questionId"]]
                self.assertEqual(d["question"],q["question"])
                self.assertEqual(d["options"],q["options"])
                self.assertEqual(d["knownAnswerCandidate"],q["answer"])
                self.assertFalse(q.get("issues") or m.get("issues"))
                self.assertEqual(m["qaStatus"],"PASS")
                self.assertEqual(q["questionProvenance"]["webpSha256"],m["sha256"])
                self.assertEqual((d["source"]["webpSha256"],d["source"]["webpPath"]),(m["sha256"],m["output"]))
                self.assertEqual(q["assets"]["singleQuestionWebp"],m["output"])
                self.assertEqual(d["source"]["questionPdfSha256"],q["questionProvenance"]["officialPdfSha256"])
                self.assertEqual(d["source"]["answerPdfSha256"],q["answerProvenance"]["officialPdfSha256"])
                rev=chash({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
                self.assertEqual(rev,d["source"]["questionRevision"])
                self.assertEqual(rev,r["sourceRevision"])
                self.assertEqual(r["webpSha256"],m["sha256"])
                self.assertEqual(d["teachingCanonicalSha256"],chash(d["teaching"]))
                self.assertEqual(r["teachingCanonicalSha256"],d["teachingCanonicalSha256"])
                body={"questionId":d["questionId"],"sourceRevision":rev,"webpSha256":m["sha256"],
                      "teaching":d["teaching"],"enrichment":d["enrichment"]}
                self.assertEqual(chash(body),d["composedTeachingSha256"])
                self.assertEqual(r["composedTeachingSha256"],d["composedTeachingSha256"])
    def test_four_specific_distinct_options_and_no_calculation_placeholders(self):
        for r in self.batch["items"]:
            d=read(ROOT/r["path"]); t=d["teaching"]
            for k in ("teacherSummary","elementarySummary","concept","extension","memory","source"):
                self.assertGreater(len(t[k]),12,(d["questionId"],k))
            self.assertGreaterEqual(len(t["solvingSteps"]),3)
            self.assertEqual(set(t["optionExplanations"]),LETTERS)
            reasons=[]
            for k,v in t["optionExplanations"].items():
                self.assertEqual(v["isCorrect"],k==d["knownAnswerCandidate"])
                self.assertGreater(len(v["teacher"].strip()),20)
                self.assertGreater(len(v["elementary"].strip()),9)
                self.assertGreater(len(v["reason"].strip()),20)
                reasons.append(v["reason"])
            self.assertEqual(len(set(reasons)),4)
            self.assertIs(t["hasExamCalculation"],False)
            self.assertIsNone(t["examCalculation"])
            self.assertNotIn("本題無金額計算",json.dumps(t,ensure_ascii=False))
            self.assertTrue(d["reasoningAudit"]["answerAlreadyKnown"])
            self.assertFalse(d["reasoningAudit"]["blindSolveClaimed"])
    def test_highlight_is_literal_safe_source_text(self):
        for r in self.batch["items"]:
            d=read(ROOT/r["path"])
            corpus=(d["question"]+" "+" ".join(d["options"])).casefold()
            for h in d["enrichment"]["highlights"]:
                self.assertTrue(h["bold"] and h["highlight"])
                self.assertIn(h["text"].casefold(),corpus)
                self.assertFalse(any(x in h["text"].casefold() for x in ("<",">","javascript:","onerror=")))
    def test_english_news_vocab_and_chinese_levels(self):
        for r in self.batch["items"]:
            d=read(ROOT/r["path"]); e=d["enrichment"]
            if d["subject"]=="英文":
                for word in e["englishVocabulary"]:
                    self.assertIn(word["level"],("初級","中級","高級"))
                    self.assertTrue(word["ipa"].startswith("/") and word["ipa"].endswith("/"))
                    self.assertIn(word["headword"].casefold(),(d["question"]+" ".join(d["options"])).casefold())
                    self.assertTrue(word["synonyms"] and word["antonyms"] and word["usageNote"])
                    self.assertTrue(word["dictionaryUrl"].startswith("https://"))
                news=e["newsExample"]
                self.assertIn(news["highlightActualForm"],news["english"])
                self.assertTrue(news["chinese"] and news["notAnArticleQuote"])
                self.assertTrue(news["source"]["url"].startswith("https://"))
                date_=date.fromisoformat(news["source"]["publicationDate"])
                self.assertGreaterEqual(date_,date(2023,10,25))
                self.assertLessEqual(date_,date(2026,10,25))
            else:
                self.assertTrue(e["chineseVocabulary"] and e["caution"])
                for w in e["chineseVocabulary"]:
                    self.assertIn(w["level"],("初級","中級","高級"))
    def test_fail_closed_teacher_and_source_not_fake(self):
        for r in self.batch["items"]:
            d=read(ROOT/r["path"]); v=d["review"]
            self.assertEqual(v["status"],"BLOCKED")
            self.assertIsNone(v["independentReviewer"])
            self.assertIs(v["humanTeacherVerified"],False)
            self.assertIs(v["studentReleaseApproved"],False)
            self.assertIs(v["formalReady"],False)
            self.assertIs(v["uiQaExactDigest"],False)
            self.assertIs(d["source"]["finalAnswerDirectQaThisBatch"],False)
        self.assertFalse({}.get("humanTeacherVerified",False))
        self.assertFalse({"humanTeacherVerified":False}.get("humanTeacherVerified"))
        self.assertFalse({"humanTeacherVerified":"true"}.get("humanTeacherVerified") is True)
    def test_negative_generic_reasons_rejected(self):
        def four_valid(xs):
            return len(xs)==4 and len(set(xs))==4 and all(isinstance(x,str) and len(x.strip())>20 for x in xs)
        self.assertFalse(four_valid(["詞義不同。"]*4))
        self.assertFalse(four_valid(["類＝種類。","類＝種類。","類＝相似。","類＝種類。"]))
        self.assertFalse(four_valid(["the option is wrong"]*4))
        for r in self.batch["items"]:
            d=read(ROOT/r["path"])
            reasons=[x["reason"] for x in d["teaching"]["optionExplanations"].values()]
            self.assertTrue(four_valid(reasons),d["questionId"])

if __name__=="__main__": unittest.main()
