"""Role B E12: source-identical water bottle Cambridge-US IPA correction with strict byte delta."""
from pathlib import Path
import copy
import hashlib
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"sudu/teaching-candidates/114-role-b-20261025-batch02"
BANK=ROOT/"sudu/data/processed/114"
ID="114-00-E-12"
BEFORE="/ˈwɔː.t̬ɚ ˌbɑː.t̬əl/"
AFTER="/ˈwɑː.t̬ɚ ˈbɑː.t̬əl/"
OLD_COMPOSED="335fa42da12236564daf4304522b454f6788d36be9bb1c50361d88bb23180263"
OLD_FILE_SHA="0a7c490b59d4ea985f20ea3919891f7779dcbf98afd9c1f30a12e1d0d6fa9cc4"
SOURCE_REV="0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
WEBP_SHA="99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
TEACH_ONLY="c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a"
UNCHANGED={
 "114-00-E-11":"6b365291eb43fd37377891149470f3bff9d8a6db5997eaff13295fb36fc402e8",
 "114-00-E-13":"2e6cdb929a573008a00abf08c510f2c29b590dc0991cd1c65ff2ee5b6a940567",
 "114-00-E-14":"9c37773e5a5f39527b8bd515426db6edb249d9a2f6117940fc774057189ef867",
 "114-00-C-04":"d8750b5df8fcb41250ed5b2143afcc80506cee15036117a493020e08f00433eb",
}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def digest(x):return sha(canonical(x))
class RoleB114E12IPA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lesson=read(F/(ID+".json"))
        cls.batch=read(F/"batch.json")
        cls.entry=next(x for x in cls.batch["items"] if x["questionId"]==ID)
        cls.q=next(x for x in read(BANK/"questions.json")["questions"] if x["questionId"]==ID)
        cls.m=next(x for x in read(BANK/"webp-manifest.json")["items"] if x["questionId"]==ID)
    def test_cambridge_US_water_bottle_combined_phrase_and_dict_attribution_scope(self):
        d=self.lesson
        entries=[x for x in d["enrichment"]["englishVocabulary"] if x["headword"]=="water bottle"]
        self.assertEqual(len(entries),1)
        w=entries[0]
        self.assertEqual(w["ipa"],AFTER)
        self.assertNotEqual(w["ipa"],BEFORE)
        self.assertEqual(w["dictionaryUrl"],"https://dictionary.cambridge.org/dictionary/english/bottle")
        self.assertEqual(w["level"],"初級")
        self.assertEqual(w["meaningZh"],"水壺／水瓶")
        self.assertIn("refillable bottle",w["synonyms"])
        self.assertEqual(d["knownAnswerCandidate"],"C")
    def test_real_original_Q12_webp_bytes_and_source_hash_not_edited(self):
        d,m,q=self.lesson,self.m,self.q
        self.assertFalse(q["issues"] or m["issues"])
        self.assertEqual(m["qaStatus"],"PASS")
        self.assertEqual(m["sha256"],WEBP_SHA)
        self.assertEqual(sha((ROOT/m["output"]).read_bytes()),WEBP_SHA)
        self.assertEqual(q["questionProvenance"]["webpSha256"],WEBP_SHA)
        self.assertEqual(d["source"]["webpSha256"],WEBP_SHA)
        self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
        rev=digest({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":WEBP_SHA})
        self.assertEqual(rev,SOURCE_REV)
        self.assertEqual((d["source"]["questionRevision"],self.entry["sourceRevision"]),(SOURCE_REV,SOURCE_REV))
    def test_minimal_only_IPA_delta_reconstructs_PR44_original_complete_json_SHA(self):
        d=copy.deepcopy(self.lesson)
        word=next(x for x in d["enrichment"]["englishVocabulary"] if x["headword"]=="water bottle")
        word["ipa"]=BEFORE
        d["composedTeachingSha256"]=OLD_COMPOSED
        raw=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        self.assertEqual(sha(raw),OLD_FILE_SHA)
    def test_no_rewrite_of_teaching_options_or_news_and_recomputed_composed_digest(self):
        d=self.lesson
        self.assertEqual(digest(d["teaching"]),TEACH_ONLY)
        self.assertEqual(d["teachingCanonicalSha256"],TEACH_ONLY)
        self.assertEqual(self.entry["teachingCanonicalSha256"],TEACH_ONLY)
        composed=digest({"questionId":ID,"sourceRevision":SOURCE_REV,"webpSha256":WEBP_SHA,"teaching":d["teaching"],"enrichment":d["enrichment"]})
        self.assertNotEqual(composed,OLD_COMPOSED)
        self.assertEqual(composed,d["composedTeachingSha256"])
        self.assertEqual(composed,self.entry["composedTeachingSha256"])
        self.assertEqual(sha((F/(ID+".json")).read_bytes()),self.entry["fileSha256"])
        self.assertEqual(set(d["teaching"]["optionExplanations"]),set("ABCD"))
        self.assertEqual(sum(x["isCorrect"] for x in d["teaching"]["optionExplanations"].values()),1)
        self.assertIsNone(d["teaching"]["examCalculation"])
    def test_all_other_prior_B_lessons_including_just_fixed_E14_unchanged(self):
        self.assertEqual(self.batch["itemCount"],5)
        for entry in self.batch["items"]:
            if entry["questionId"]==ID:continue
            with self.subTest(qid=entry["questionId"]):
                self.assertEqual(entry["fileSha256"],UNCHANGED[entry["questionId"]])
                self.assertEqual(sha((ROOT/entry["path"]).read_bytes()),UNCHANGED[entry["questionId"]])
        e14=read(F/"114-00-E-14.json")
        self.assertEqual(e14["composedTeachingSha256"],"88aa9992f062197be0f930dda08ad61e71b9dcc21f1b10eb48cd12a125e07644")
    def test_status_blocked_author_not_independent_role_E_or_publisher(self):
        d=self.lesson
        self.assertEqual(d["review"]["status"],"BLOCKED")
        self.assertIs(d["review"]["studentReleaseApproved"],False)
        self.assertIs(d["review"]["formalReady"],False)
        self.assertIs(d["review"]["uiQaExactDigest"],False)
        self.assertIs(d["review"]["requiresHumanTeacher"],False)
        self.assertEqual(d["review"]["independentAiContentReview"]["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
        self.assertIsNone(d["review"]["independentReviewer"])
        self.assertEqual(self.batch["newReady"],0)
        self.assertEqual(self.batch["newLive"],0)
        self.assertIs(d["reasoningAudit"]["blindSolveClaimed"],False)
    def test_negative_changed_source_or_stale_IPA_can_never_reuse_exact_digest(self):
        d=self.lesson
        base={"questionId":ID,"sourceRevision":SOURCE_REV,"webpSha256":WEBP_SHA,"teaching":d["teaching"],"enrichment":d["enrichment"]}
        h=digest(base)
        previous=copy.deepcopy(base)
        next(x for x in previous["enrichment"]["englishVocabulary"] if x["headword"]=="water bottle")["ipa"]=BEFORE
        self.assertNotEqual(digest(previous),h)
        self.assertNotEqual(digest(dict(base,sourceRevision="0"*64)),h)
        self.assertNotEqual(digest(dict(base,webpSha256="1"*64)),h)
if __name__=="__main__":unittest.main()
