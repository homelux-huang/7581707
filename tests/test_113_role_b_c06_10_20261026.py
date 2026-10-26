"""Role B 113 C06-10: A original pixel bytes and full source-bound dual-level author drafts; NO RELEASE."""
import hashlib,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'sudu/teaching-candidates/113-role-b-c06-10-20261026'
A=ROOT/'sudu/data/processed/113'
IDS={'113-00-C-06','113-00-C-07','113-00-C-08','113-00-C-09','113-00-C-10'}
CANDIDATES={'113-00-C-06':'B','113-00-C-07':'A','113-00-C-08':'D','113-00-C-09':'B','113-00-C-10':'B'}
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()
def canon(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def canonical_sha(obj):return sha_bytes(canon(obj))
def git_blob_sha(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

class RoleB113SourceBound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read(DIR/'batch.json')
        m6=read(A/'role-a-c06/manifest.json')
        m7=read(A/'role-a-c07-10/manifest.json')
        cls.manifests={x['questionId']:x for x in m6['questions']+m7['questions']}
        cls.qa6=read(A/'role-a-c06/VISUAL_QA_ASSISTANT_20261025.json')
        cls.qa7=read(A/'role-a-c07-10/VISUAL_QA_ASSISTANT_20261025.json')
        cls.docs={x['questionId']:read(ROOT/x['path']) for x in cls.batch['items']}
    def test_01_exact_ids_and_no_release_policy(self):
        b=self.batch
        self.assertEqual(set(self.docs),IDS)
        self.assertEqual(b['itemCount'],5)
        self.assertTrue(b['authorRoleBOnly'])
        self.assertIs(b['requiresHumanTeacher'],False)
        self.assertEqual(b['distinctEApproval'],'PENDING')
        self.assertEqual((b['newReady'],b['newMain'],b['newLive']),(0,0,0))
    def test_02_every_original_single_webp_bytes_and_git_blob_sha1(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                m=self.manifests[id];asset=m['asset']
                raw=(ROOT/asset['path']).read_bytes()
                self.assertEqual(sha_bytes(raw),asset['sha256'])
                self.assertEqual(git_blob_sha(raw),asset['gitBlobSha1'])
                self.assertEqual(d['source']['webpSha256'],asset['sha256'])
                self.assertEqual(d['source']['webpGitBlobSha1'],asset['gitBlobSha1'])
                self.assertEqual(d['source']['originalSingleWebpPath'],asset['path'])
                self.assertEqual(d['source']['sourceRevision'],m['sourceRevisionSha256'])
                self.assertEqual(d['source']['answerVerified'],False)
                self.assertEqual(d['source']['questionVerified'],False)
    def test_03_original_source_page_and_answer_page_bytes(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                s=d['source']
                self.assertEqual(sha_bytes((ROOT/s['sourcePagePath']).read_bytes()),s['sourcePageSha256'])
                self.assertEqual(sha_bytes((ROOT/s['answerPagePath']).read_bytes()),s['answerPageSha256'])
                self.assertEqual(git_blob_sha((ROOT/s['answerPagePath']).read_bytes()),s['answerPageGitBlob'])
                self.assertIs(s['officialYearCorrectionNoticeVerified'],False)
                self.assertIs(s['roleAImageOnlyCheck'],True)
        self.assertEqual(self.qa6['result'],'PASS_ASSISTANT_DIRECT_ORIGINAL_SOURCE_IMAGE_ONLY')
        self.assertFalse(self.qa6['newAnswerVerified'])
        self.assertFalse(self.qa7['officialFinalAmendmentChecked'])
        self.assertFalse(self.qa7['newAnswerVerified'])
        self.assertEqual({x['questionId'] for x in self.qa7['questionResults']},IDS-{'113-00-C-06'})
        for q in self.qa7['questionResults']:
            self.assertEqual(q['visualSourceResult'],'PASS_ROLE_A_SOURCE_IMAGE_ONLY')
            self.assertIs(q['answerVerified'],False)
            self.assertIs(q['questionVerified'],False)
    def test_04_original_exact_stems_options_known_not_blind(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                s=self.manifests[id]
                self.assertEqual(d['question'],s['question'])
                self.assertEqual(d['options'],s['options'])
                self.assertEqual(len(d['options']),4)
                self.assertEqual(d['knownAnswerCandidate'],CANDIDATES[id])
                self.assertEqual(d['knownAnswerCandidate'],s['answerCandidate'])
                self.assertTrue(d['reasoningAudit']['alreadyKnewCandidateAnswer'])
                self.assertFalse(d['reasoningAudit']['blindSolveClaimed'])
                self.assertFalse(s['answerVerified'])
                self.assertFalse(s['questionVerified'])
    def test_05_current_teaching_and_composed_and_whole_file_sha(self):
        for row in self.batch['items']:
            with self.subTest(id=row['questionId']):
                d=self.docs[row['questionId']]
                self.assertEqual(canonical_sha(d['teaching']),d['teachingCanonicalSha256'])
                self.assertEqual(d['teachingCanonicalSha256'],row['teachingCanonicalSha256'])
                combined={'questionId':row['questionId'],'sourceRevision':row['sourceRevision'],'webpSha256':row['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
                self.assertEqual(canonical_sha(combined),d['composedTeachingSha256'])
                self.assertEqual(d['composedTeachingSha256'],row['composedTeachingSha256'])
                self.assertEqual(sha_bytes((ROOT/row['path']).read_bytes()),row['fileSha256'])
                self.assertEqual(row['status'],'BLOCKED')
    def test_06_all_four_distinct_teacher_elementary_and_reasons(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                t=d['teaching']
                self.assertGreaterEqual(len(t['teacherSummary']),55)
                self.assertGreaterEqual(len(t['elementarySummary']),35)
                self.assertGreaterEqual(len(t['solvingSteps']),3)
                self.assertGreaterEqual(len(t['memory']),18)
                self.assertEqual(set(t['optionExplanations']),set('ABCD'))
                reasons=[]
                for ch,x in t['optionExplanations'].items():
                    self.assertGreaterEqual(len(x['teacher']),40)
                    self.assertGreaterEqual(len(x['elementary']),17)
                    self.assertGreaterEqual(len(x['reason']),20)
                    self.assertIs(x['isCorrect'],ch==CANDIDATES[id])
                    reasons.append(x['reason'])
                self.assertEqual(len(set(reasons)),4)
                self.assertIs(t['hasExamCalculation'],False)
                self.assertIsNone(t['examCalculation'])
                self.assertNotIn('本題無金額計算',json.dumps(t,ensure_ascii=False))
    def test_07_safe_source_literal_highlight_and_chinese_vocabulary(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                corpus=''.join((' '.join([d['question'],*d['options']])).split())
                hits=d['enrichment']['highlights']
                self.assertGreaterEqual(len(hits),4)
                for x in hits:
                    self.assertIn(''.join(x['text'].split()),corpus)
                    self.assertTrue(x['bold'] and x['highlight'])
                    self.assertEqual(x['renderAs'],'safe-literal-text')
                    self.assertNotIn('<',x['text']);self.assertNotIn('>',x['text'])
                vocab=d['enrichment']['chineseVocabulary']
                self.assertEqual({x['level'] for x in vocab},{'初級','中級','高級'})
    def test_08_correct_required_figures_and_no_clipped_older_crop(self):
        figure=self.docs['113-00-C-06']['enrichment']['originalVisual']
        self.assertEqual((figure['circle'],figure['square']),('孝弟','詩書'))
        seq=self.docs['113-00-C-07']['enrichment']['originalVisual']
        self.assertEqual(seq['sequence'],['③','④','⑤','①','②'])
        mat=self.docs['113-00-C-09']
        chart=mat['enrichment']['originalVisual']
        self.assertEqual(chart['sourceFinalPixelSha256'],mat['source']['webpSha256'])
        self.assertNotEqual(chart['rejectedClippedOldSha256'],mat['source']['webpSha256'])
        self.assertEqual(chart['zones']['右下'],'順應')
        fish=self.docs['113-00-C-10']['enrichment']['originalVisual']
        self.assertEqual(fish['headers'],['①','①－1','②','②－1'])
        self.assertEqual(fish['correctRowB'],['載人','怕走路累','運貨','互通有無'])
        self.assertTrue(fish['officialOriginalFigureRequired'])
    def test_09_negative_not_author_review_and_not_v4_qa(self):
        for d in self.docs.values():
            v=d['review']
            self.assertEqual(v['status'],'BLOCKED')
            self.assertTrue(v['authorSelfCheckOnly'])
            self.assertFalse(v['formalReady'])
            self.assertFalse(v['studentReleaseApproved'])
            self.assertFalse(v['newMain'])
            self.assertFalse(v['newLive'])
            self.assertFalse(v['requiresHumanTeacher'])
            self.assertEqual(v['independentEContent'],'PENDING')
            self.assertTrue(v['blockers'])
            self.assertIsNone(d['textbook']['publisher'])
    def test_10_changed_source_or_image_invalidates_current_digest(self):
        d=self.docs['113-00-C-10']
        base={'questionId':d['questionId'],'sourceRevision':d['source']['sourceRevision'],'webpSha256':d['source']['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
        now=canonical_sha(base)
        self.assertEqual(now,d['composedTeachingSha256'])
        self.assertNotEqual(now,canonical_sha(dict(base,sourceRevision='0'*64)))
        self.assertNotEqual(now,canonical_sha(dict(base,webpSha256='1'*64)))
        self.assertNotEqual(now,canonical_sha(dict(base,teaching=dict(d['teaching'],memory='TAMPERED'))))

if __name__=='__main__':unittest.main()
