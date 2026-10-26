"""Role B C19: verify real original Q19 v2 and p6 cross-page reading, never self-release."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/114"
FOLDER=ROOT/"sudu/teaching-candidates/114-role-b-c19-original-a99-20261027"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha_raw(b): return hashlib.sha256(b).hexdigest()
def canon(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def sha(o): return sha_raw(canon(o))
def git_oid(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()

class C19OriginalLesson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(FOLDER/"batch.json")
        cls.d=load(FOLDER/"114-00-C-19.json")
        cls.q=next(x for x in load(DATA/"questions.json")["questions"] if x["questionId"]=="114-00-C-19")
        cls.m=next(x for x in load(DATA/"webp-manifest.json")["items"] if x["questionId"]=="114-00-C-19")
        cls.row=cls.batch["items"][0]
    def test_one_question_author_only_and_no_release(self):
        b=self.batch
        self.assertEqual(b["questionIds"],["114-00-C-19"])
        self.assertEqual((b["itemCount"],b["newReady"],b["newMain"],b["newLive"]),(1,0,0,0))
        self.assertIs(b["sourceAnswerVerified"],False)
        self.assertIs(b["sourceQuestionVerified"],False)
        self.assertIs(b["sourceSharedReadingAssociationPending"],True)
        self.assertEqual(self.d["review"]["status"],"BLOCKED")
        self.assertIs(self.d["review"]["studentReleaseApproved"],False)
    def test_true_original_single_webp_bytes_not_prior_mixed_page(self):
        d,q,m=self.d,self.q,self.m
        self.assertEqual(m["qaStatus"],"PASS")
        self.assertFalse(q["issues"])
        self.assertEqual(q["assets"]["singleQuestionWebp"],m["output"])
        self.assertEqual(q["questionProvenance"]["webpSha256"],m["sha256"])
        self.assertEqual(d["source"]["webpSha256"],m["sha256"])
        self.assertEqual(sha_raw((ROOT/m["output"]).read_bytes()),m["sha256"])
        self.assertEqual(git_oid((ROOT/m["output"]).read_bytes()),d["source"]["webpGitBlob"])
        old=m["oldAssetBeforeDirectVisualRepair"]
        self.assertEqual(old["qaStatus"],"BLOCKED_VISUAL_NEIGHBOR_SHARED_PASSAGE")
        self.assertNotEqual(old["sha256"],m["sha256"])
        self.assertEqual(sha_raw((ROOT/old["output"]).read_bytes()),old["sha256"])
    def test_old_direct_visual_ai_receipt_is_not_official_answer(self):
        qa=load(ROOT/self.d["source"]["archivedImageQaEvidence"])
        item=next(x for x in qa["items"] if x["questionId"]=="114-00-C-19")
        self.assertEqual(item["reviewedWebpSha256"],self.m["sha256"])
        self.assertEqual(item["result"],"PASS_DIRECT_ORIGINAL_PAGE_IMAGE")
        self.assertIs(item["answerVerified"],False)
        self.assertIs(item["questionVerified"],False)
        self.assertIs(item["independentHumanReview"],False)
        self.assertIs(item["integrationReady"],False)
        self.assertEqual(sha_raw((ROOT/self.m["source"]).read_bytes()),self.m["sourceSha256"])
    def test_real_original_reading_page6_and_page7_immutable(self):
        e=self.d["enrichment"]["originalReading"]
        page6=(ROOT/e["originalOfficialPage6"]).read_bytes()
        self.assertEqual(sha_raw(page6),self.batch["originalReadingPage6Sha256"])
        self.assertEqual(sha_raw(page6),e["page6Sha256"])
        self.assertEqual(git_oid(page6),e["page6GitBlob"])
        self.assertEqual(e["page7Sha256"],self.m["sourceSha256"])
        self.assertTrue(e["required"])
        self.assertTrue(e["requiredSourceAssociationPendingRoleA"])
        self.assertEqual(self.q["sharedMaterialIds"],[])
        self.assertEqual(e["canonicalSharedMaterialIds"],[])
        self.assertIs(e["notNewImageQa"],True)
    def test_original_question_and_answer_provenance_not_promoted(self):
        d,q=self.d,self.q
        self.assertEqual((d["question"],d["options"],d["knownAnswerCandidate"]),(q["question"],q["options"],"B"))
        self.assertEqual(q["answer"],"B")
        self.assertIs(q["answerVerified"],False)
        self.assertIs(q["questionVerified"],False)
        self.assertEqual(d["source"]["originalPdfSha256"],q["questionProvenance"]["officialPdfSha256"])
        self.assertEqual(d["source"]["answerPdfSha256"],q["answerProvenance"]["officialPdfSha256"])
        self.assertEqual(git_oid((ROOT/d["source"]["answerPageWebpPath"]).read_bytes()),d["source"]["answerPageGitBlob"])
        self.assertIs(d["reasoningAudit"]["answerAlreadyKnown"],True)
        self.assertIs(d["reasoningAudit"]["blindSolveClaimed"],False)
    def test_source_and_teacher_sha256_exact_byte_alignment(self):
        d,q,m,row=self.d,self.q,self.m,self.row
        rev=sha({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]})
        self.assertEqual(rev,row["sourceRevision"])
        self.assertEqual(rev,d["source"]["questionRevision"])
        self.assertEqual(sha(d["teaching"]),row["teachingCanonicalSha256"])
        self.assertEqual(sha(d["teaching"]),d["teachingCanonicalSha256"])
        digest=sha({"questionId":d["questionId"],"sourceRevision":rev,"webpSha256":m["sha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]})
        self.assertEqual(digest,row["composedTeachingSha256"])
        self.assertEqual(digest,d["composedTeachingSha256"])
        self.assertEqual(sha_raw((ROOT/row["path"]).read_bytes()),row["fileSha256"])
    def test_four_specific_dual_level_reasons_and_safe_highlight(self):
        d=self.d;t=d["teaching"]
        self.assertEqual(set(t["optionExplanations"]),set("ABCD"))
        self.assertGreaterEqual(len(t["solvingSteps"]),4)
        seen=[]
        for ch,o in t["optionExplanations"].items():
            self.assertEqual(o["isCorrect"],ch=="B")
            self.assertGreaterEqual(len(o["teacher"]),32)
            self.assertGreaterEqual(len(o["elementary"]),14)
            self.assertGreaterEqual(len(o["reason"]),22)
            seen.append(o["reason"])
        self.assertEqual(len(set(seen)),4)
        self.assertGreater(len(t["teacherSummary"]),100)
        self.assertGreater(len(t["elementarySummary"]),35)
        self.assertIn("商、周",t["teacherSummary"])
        self.assertIn("不用太大",t["teacherSummary"])
        self.assertIsNone(t["examCalculation"])
        self.assertIs(t["hasExamCalculation"],False)
        self.assertNotIn("本題無金額計算",json.dumps(t,ensure_ascii=False))
        source=d["question"]+" "+" ".join(d["options"])
        for x in d["enrichment"]["highlights"]:
            self.assertIs(x["bold"],True)
            self.assertIs(x["highlight"],True)
            self.assertIn(x["text"],source)
            self.assertNotIn("<",x["text"])
            self.assertNotIn(">",x["text"])
        self.assertEqual({z["level"] for z in d["enrichment"]["chineseVocabulary"]},{"初級","中級","高級"})
    def test_fail_closed_on_fake_review_or_tampered_source(self):
        d=self.d;v=d["review"]
        self.assertEqual(v["independentAiReview"],"PENDING_ROLE_E")
        self.assertIs(v["authorSelfCheckOnly"],True)
        self.assertIs(v["requiresHumanTeacher"],False)
        self.assertIs(v["formalReady"],False)
        self.assertIs(v["studentReleaseApproved"],False)
        payload={"questionId":d["questionId"],"sourceRevision":d["source"]["questionRevision"],"webpSha256":d["source"]["webpSha256"],"teaching":d["teaching"],"enrichment":d["enrichment"]}
        value=sha(payload)
        self.assertNotEqual(sha(dict(payload,sourceRevision="0"*64)),value)
        self.assertNotEqual(sha(dict(payload,webpSha256="1"*64)),value)
        self.assertNotEqual(sha(dict(payload,teaching=dict(d["teaching"],memory="TAMPER"))),value)

if __name__=="__main__":unittest.main()
