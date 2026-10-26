"""Role B 114 English14 Cambridge US idiom URL provenance repair: minimal diff and fail-closed SHA."""
from pathlib import Path
import copy
import hashlib
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/teaching-candidates/114-role-b-20261025-batch02"
BANK=ROOT/"sudu/data/processed/114"
QID="114-00-E-14"
OLD_URL="https://dictionary.cambridge.org/dictionary/english/cut-in-line"
NEW_URL="https://dictionary.cambridge.org/dictionary/english/line"
OLD_DIGEST="b9c464e05fcec6969ef298d5744a9599af8e17612fc5cde2615a6a090e3c560e"
OLD_FILE="cd41a20bedcc54a86467e4412d26737a1f64ad945c46358440567176aee4bf86"
EXPECTED_SOURCE="6164a310c7d38229aaaf52df678121ee88f6242cf6611310badfb5b1b46714dd"
EXPECTED_WEBP="388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94"
TEACHING_UNCHANGED="27c9028082da7aa5d7b8bc1897d5eabfc40d21506b463ced08938841cfcf8811"
OTHERS={
 "114-00-E-11":"6b365291eb43fd37377891149470f3bff9d8a6db5997eaff13295fb36fc402e8",
 "114-00-E-12":"0a7c490b59d4ea985f20ea3919891f7779dcbf98afd9c1f30a12e1d0d6fa9cc4",
 "114-00-E-13":"2e6cdb929a573008a00abf08c510f2c29b590dc0991cd1c65ff2ee5b6a940567",
 "114-00-C-04":"d8750b5df8fcb41250ed5b2143afcc80506cee15036117a493020e08f00433eb",
}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def chash(x):return sha(canonical(x))
class CambridgeLinkE14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read(DIR/(QID+".json"))
        cls.batch=read(DIR/"batch.json")
        cls.row=next(x for x in cls.batch["items"] if x["questionId"]==QID)
        cls.q=next(x for x in read(BANK/"questions.json")["questions"] if x["questionId"]==QID)
        cls.m=next(x for x in read(BANK/"webp-manifest.json")["items"] if x["questionId"]==QID)
    def test_cambridge_US_idiom_only_authoritative_dictionary_entry_url(self):
        d=self.d
        w=[x for x in d["enrichment"]["englishVocabulary"] if x["headword"]=="cut in line"]
        self.assertEqual(len(w),1)
        self.assertEqual(w[0]["dictionaryUrl"],NEW_URL)
        self.assertNotEqual(w[0]["dictionaryUrl"],OLD_URL)
        self.assertEqual(w[0]["meaningZh"],"插隊")
        self.assertEqual(w[0]["ipa"],"/kʌt ɪn laɪn/")
        self.assertEqual(w[0]["level"],"中級")
        self.assertIn("jump the queue",w[0]["synonyms"])
        self.assertEqual(d["knownAnswerCandidate"],"D")
    def test_exact_single_webp_original_and_canonical_revision_unmodified(self):
        d,q,m=self.d,self.q,self.m
        self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],q["answer"]))
        self.assertEqual(len(q["options"]),4)
        self.assertFalse(q.get("issues") or m.get("issues"))
        self.assertEqual(m["qaStatus"],"PASS")
        self.assertEqual(m["sha256"],EXPECTED_WEBP)
        self.assertEqual(q["questionProvenance"]["webpSha256"],EXPECTED_WEBP)
        self.assertEqual(sha((ROOT/m["output"]).read_bytes()),EXPECTED_WEBP)
        rev=chash({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":EXPECTED_WEBP})
        self.assertEqual(rev,EXPECTED_SOURCE)
        self.assertEqual((d["source"]["questionRevision"],self.row["sourceRevision"]),(rev,rev))
        self.assertEqual((d["source"]["webpSha256"],self.row["webpSha256"]),(EXPECTED_WEBP,EXPECTED_WEBP))
    def test_exact_minimal_diff_reconstructs_original_PR44_JSON_SHA(self):
        d=copy.deepcopy(self.d)
        word=next(x for x in d["enrichment"]["englishVocabulary"] if x["headword"]=="cut in line")
        word["dictionaryUrl"]=OLD_URL
        d["composedTeachingSha256"]=OLD_DIGEST
        prior=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        self.assertEqual(sha(prior),OLD_FILE,"Original PR44 E14 content changed outside exact allowed URI/digest")
    def test_recomputed_teacher_and_composed_digests_at_exact_current_bytes(self):
        d,r=self.d,self.row
        self.assertEqual(chash(d["teaching"]),TEACHING_UNCHANGED)
        self.assertEqual(d["teachingCanonicalSha256"],TEACHING_UNCHANGED)
        self.assertEqual(r["teachingCanonicalSha256"],TEACHING_UNCHANGED)
        digest=chash({"questionId":QID,"sourceRevision":EXPECTED_SOURCE,"webpSha256":EXPECTED_WEBP,"teaching":d["teaching"],"enrichment":d["enrichment"]})
        self.assertNotEqual(digest,OLD_DIGEST)
        self.assertEqual(digest,d["composedTeachingSha256"])
        self.assertEqual(digest,r["composedTeachingSha256"])
        self.assertEqual(sha((DIR/(QID+".json")).read_bytes()),r["fileSha256"])
    def test_other_four_original_B_lessons_completely_untouched(self):
        self.assertEqual(self.batch["itemCount"],5)
        for row in self.batch["items"]:
            if row["questionId"]==QID:continue
            with self.subTest(qid=row["questionId"]):
                self.assertEqual(row["fileSha256"],OTHERS[row["questionId"]])
                self.assertEqual(sha((ROOT/row["path"]).read_bytes()),OTHERS[row["questionId"]])
    def test_author_not_independent_reviewer_or_student_publisher(self):
        d=self.d
        self.assertEqual(d["review"]["status"],"BLOCKED")
        self.assertIs(d["review"]["studentReleaseApproved"],False)
        self.assertIs(d["review"]["formalReady"],False)
        self.assertIs(d["review"]["uiQaExactDigest"],False)
        self.assertIs(d["review"]["requiresHumanTeacher"],False)
        self.assertEqual(d["review"]["independentAiContentReview"]["status"],"PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW")
        self.assertEqual(self.batch["newReady"],0)
        self.assertEqual(self.batch["newLive"],0)
        self.assertIs(d["reasoningAudit"]["blindSolveClaimed"],False)
    def test_negative_old_link_and_forged_author_E_receipt_rejected(self):
        d=self.d
        base={"questionId":QID,"sourceRevision":EXPECTED_SOURCE,"webpSha256":EXPECTED_WEBP,"teaching":d["teaching"],"enrichment":d["enrichment"]}
        actual=chash(base)
        old=copy.deepcopy(base)
        old["enrichment"]["englishVocabulary"][0]["dictionaryUrl"]=OLD_URL
        self.assertNotEqual(chash(old),actual)
        self.assertNotEqual(chash(dict(base,webpSha256="0"*64)),actual)
        self.assertIsNone(d["review"]["independentReviewer"])
        self.assertIsNone(d["review"]["independentAiContentReview"]["reviewTaskId"])

if __name__=="__main__":unittest.main()
