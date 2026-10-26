"""Role B 113 original shared plum passage and 5 teacher/child A-D drafts, NO RELEASE."""
from pathlib import Path
import hashlib,json,unittest

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'sudu/teaching-candidates/113-role-b-c11-15-20261026'
SOURCE=ROOT/'sudu/data/processed/113/role-a-c11-15'
EXPECTED={'113-00-C-11':'C','113-00-C-12':'B','113-00-C-13':'C','113-00-C-14':'A','113-00-C-15':'A'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def gitblob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def canonical(d):return json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def h(d):return sha(canonical(d))
class RoleB113Shared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=load(DIR/'batch.json')
        cls.m=load(SOURCE/'manifest.json')
        cls.qa=load(SOURCE/'VISUAL_QA_ASSISTANT_20261025.json')
        cls.src={x['questionId']:x for x in cls.m['questions']}
        cls.docs={row['questionId']:load(ROOT/row['path']) for row in cls.b['items']}
    def test_01_exact_scope_and_fail_closed_author_only(self):
        self.assertEqual(set(self.docs),set(EXPECTED))
        self.assertEqual(self.b['questionCount'],5)
        self.assertIs(self.b['authorSelfAssessmentOnly'],True)
        self.assertFalse(self.b['requiresHumanTeacher'])
        self.assertEqual(self.b['roleEIndependentQa'],'PENDING')
        self.assertEqual((self.b['newReady'],self.b['newMain'],self.b['newLive']),(0,0,0))
    def test_02_exact_original_shared_article_real_bytes(self):
        shared=self.m['sharedMaterials'][0]
        x=shared['asset']
        self.assertEqual(shared['sharedMaterialId'],'113-00-C-SHARED-11-15')
        raw=(ROOT/x['path']).read_bytes()
        self.assertEqual(sha(raw),x['sha256'])
        self.assertEqual(gitblob(raw),x['gitBlobSha1'])
        self.assertEqual(x['sha256'],self.b['sourceSharedWebpSha256'])
        self.assertEqual(x['sha256'],self.qa['sharedOriginal']['asset']['sha256'])
        self.assertEqual(self.qa['sharedOriginal']['reviewStatus'],'PASS_ROLE_A_SOURCE_IMAGE_ONLY')
        self.assertEqual(sha((ROOT/self.m['originalPages']['4']['path']).read_bytes()),self.b['sourceOriginalPage4Sha256'])
        self.assertEqual(sha((ROOT/self.m['originalPages']['5']['path']).read_bytes()),self.b['sourceOriginalPage5Sha256'])
        self.assertEqual(self.qa['fullOfficialAmendmentScopeChecked'],False)
    def test_03_all_five_exact_original_image_sha_and_original_source(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                s=self.src[id];a=s['sourceAsset']
                raw=(ROOT/a['path']).read_bytes()
                self.assertEqual(sha(raw),a['sha256'])
                self.assertEqual(gitblob(raw),a['gitBlobSha1'])
                self.assertEqual(d['source']['webpSha256'],a['sha256'])
                self.assertEqual(d['source']['sourceRevision'],s['sourceRevisionSha256'])
                self.assertEqual(d['question'],s['question'])
                self.assertEqual(d['options'],s['options'])
                self.assertEqual(len(d['options']),4)
                self.assertEqual(s['answerCandidate'],EXPECTED[id])
                self.assertFalse(s['answerVerified'])
                self.assertFalse(s['questionVerified'])
                self.assertEqual(d['source']['sharedWebpSha256'],self.b['sourceSharedWebpSha256'])
                self.assertEqual(d['enrichment']['sharedReading']['originalSharedWebpSha256'],self.b['sourceSharedWebpSha256'])
                self.assertEqual(sha((ROOT/d['source']['sourcePagePath']).read_bytes()),d['source']['sourcePageSha256'])
                q=next(x for x in self.qa['questions'] if x['questionId']==id)
                self.assertEqual(q['asset']['sha256'],a['sha256'])
                self.assertEqual(q['sourceImageReviewResult'],'PASS_ROLE_A_SOURCE_IMAGE_ONLY')
                self.assertIs(q['answerVerified'],False)
                self.assertIs(q['questionVerified'],False)
    def test_04_announced_answer_page_is_not_final_amendment_approval(self):
        page=self.m['originalAnnouncedAnswerPage']
        self.assertEqual(sha((ROOT/page['path']).read_bytes()),page['sha256'])
        self.assertEqual(gitblob((ROOT/page['path']).read_bytes()),page['gitBlobSha1'])
        self.assertIs(self.m['officialFinalCorrectionNoticeChecked'],False)
        for d in self.docs.values():
            self.assertFalse(d['source']['answerVerified'])
            self.assertTrue(d['source']['fullYearCorrectionNoticeScopePending'])
            self.assertTrue(d['reasoningAudit']['answerCandidateAlreadyKnown'])
            self.assertFalse(d['reasoningAudit']['blindSolveClaimed'])
    def test_05_canonical_lesson_shared_material_and_file_hashes(self):
        for row in self.b['items']:
            with self.subTest(id=row['questionId']):
                d=self.docs[row['questionId']]
                self.assertEqual(h(d['teaching']),d['teachingCanonicalSha256'])
                self.assertEqual(h(d['teaching']),row['teachingCanonicalSha256'])
                combined={'questionId':row['questionId'],'sourceRevision':row['sourceRevision'],'webpSha256':row['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
                self.assertEqual(h(combined),d['composedTeachingSha256'])
                self.assertEqual(h(combined),row['composedTeachingSha256'])
                self.assertEqual(sha((ROOT/row['path']).read_bytes()),row['fileSha256'])
                self.assertEqual(row['status'],'BLOCKED')
    def test_06_four_distinct_option_reasons_both_levels_and_steps(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                t=d['teaching']
                self.assertGreaterEqual(len(t['teacherSummary']),55)
                self.assertGreaterEqual(len(t['elementarySummary']),28)
                self.assertGreaterEqual(len(t['solvingSteps']),3)
                self.assertGreaterEqual(len(t['memory']),20)
                self.assertEqual(set(t['optionExplanations']),set('ABCD'))
                reasons=[]
                for ch,x in t['optionExplanations'].items():
                    self.assertGreaterEqual(len(x['teacher']),45)
                    self.assertGreaterEqual(len(x['elementary']),19)
                    self.assertGreaterEqual(len(x['reason']),23)
                    self.assertIs(x['isCorrect'],ch==EXPECTED[id])
                    reasons.append(x['reason'])
                self.assertEqual(len(set(reasons)),4)
                self.assertFalse(t['hasExamCalculation'])
                self.assertIsNone(t['examCalculation'])
                self.assertNotIn('本題無金額計算',json.dumps(t,ensure_ascii=False))
    def test_07_literal_safe_highlights_and_three_levels(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                corpus=''.join(' '.join([d['question'],*d['options']]).split())
                for x in d['enrichment']['highlights']:
                    self.assertIn(''.join(x['text'].split()),corpus)
                    self.assertTrue(x['bold'] and x['highlight'])
                    self.assertEqual(x['renderAs'],'safe-literal-text')
                    self.assertNotIn('<',x['text'])
                self.assertEqual({v['level'] for v in d['enrichment']['chineseVocabulary']},{'初級','中級','高級'})
    def test_08_true_original_c13_table_c14_poems_and_c15_people_figure(self):
        q13=self.docs['113-00-C-13']['enrichment']['originalVisual']
        self.assertTrue(q13['sourceOriginalTableRequired'])
        self.assertEqual(q13['rowNumbers'],['①','②','③','④'])
        q14=self.docs['113-00-C-14']['enrichment']['originalVisual']
        self.assertTrue(q14['originalVerseBoxesPreserved'])
        self.assertEqual(q14['goodSentences'],['①','③'])
        q15=self.docs['113-00-C-15']['enrichment']['originalVisual']
        self.assertTrue(q15['doNotRegenerateWakaOriginalPicture'])
        self.assertEqual(q15['poemPersonPositions'],['甲','乙','丙','丁'])
        self.assertEqual(q15['resultClaims'],[True,True])
        self.assertEqual(self.qa['questions'][2]['originalTableReview'],'PASS_ORIGINAL_TWO_COLUMN_COMPARISON_TABLE_FULL')
        self.assertEqual(self.qa['questions'][3]['originalPoetryReview'],'PASS_TWO_PRINTED_BOXES_COMPLETE')
    def test_09_negative_author_self_review_cannot_publish(self):
        for d in self.docs.values():
            v=d['review']
            self.assertEqual(v['status'],'BLOCKED')
            self.assertIs(v['authorSelfCheckOnly'],True)
            self.assertIs(v['formalReady'],False)
            self.assertIs(v['studentReleaseApproved'],False)
            self.assertIs(v['newMain'],False)
            self.assertIs(v['newLive'],False)
            self.assertEqual(v['independentEContentReview'],'PENDING_DISTINCT_AI_ROLE_E')
            self.assertTrue(v['blockers'])
            self.assertIsNone(d['textbook']['publisher'])
    def test_10_source_or_shared_image_revision_invalidates_old_digest(self):
        d=self.docs['113-00-C-13']
        data={'questionId':d['questionId'],'sourceRevision':d['source']['sourceRevision'],'webpSha256':d['source']['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
        current=h(data)
        self.assertEqual(current,d['composedTeachingSha256'])
        self.assertNotEqual(current,h(dict(data,sourceRevision='0'*64)))
        self.assertNotEqual(current,h(dict(data,webpSha256='1'*64)))
        bogus=dict(d['enrichment'])
        bogus['sharedReading']=dict(d['enrichment']['sharedReading'],originalSharedWebpSha256='2'*64)
        self.assertNotEqual(current,h(dict(data,enrichment=bogus)))
if __name__=='__main__':unittest.main()
