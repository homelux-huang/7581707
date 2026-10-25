"""Role B 114 C16-18 original Han/Song three lamps pedagogical drafts, source G1 pending."""
from pathlib import Path
import hashlib,json,unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'sudu/data/processed/114'
DRAFT=ROOT/'sudu/teaching-candidates/114-role-b-20261025-batch08'
IDS={'114-00-C-16','114-00-C-17','114-00-C-18'}
EXPECTED={'114-00-C-16':'B','114-00-C-17':'D','114-00-C-18':'A'}
WEBP={
  '114-00-C-16':'d04b2f4b9bd7bb2a1212fdb12da4ee7d9b0cee14afd3e17d4bd1733061952d4a',
  '114-00-C-17':'9fd277ec092fe55fb9bc12080b6bce9749ffe9f6b7cb468e33439ae5b23c985e',
  '114-00-C-18':'50c3718fc832c152e735ad773272fd4466888d57cc18b6b319c85218773c53ed',
}
PAGE6_SHA='a7b74caa809a87696bdb8b657cd5a77968d61cea1d8d4ccb8a37c4384a688df4'
PAGE6_BLOB='8719fddcdb4ddd835a573828710994936d329b80'
ANSWER_BLOB='c3090e94ab1cbf7adf9f7efd0581529eff00e26b'

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sh(b):return hashlib.sha256(b).hexdigest()
def can(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def h(x):return sh(can(x))
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def norm(s):return ''.join(s.split())

class OriginalThreeLampsB08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(DRAFT/'batch.json')
        cls.bank={q['questionId']:q for q in load(SRC/'questions.json')['questions']}
        cls.manifest={m['questionId']:m for m in load(SRC/'webp-manifest.json')['items']}
        cls.docs={x['questionId']:load(ROOT/x['path']) for x in cls.batch['items']}

    def test_three_g1_drafts_not_pass_and_zero_student_release(self):
        b=self.batch
        self.assertEqual(b['itemCount'],3)
        self.assertEqual(set(self.docs),IDS)
        self.assertEqual(b['g1ImageStatus'],'DRAFT_NEEDS_DIRECT_VISUAL_QA')
        self.assertEqual(b['g2SharedReadingAndTableStatus'],'PENDING_ROLE_A')
        self.assertEqual(b['g3OfficialFinalAnswerNoticeStatus'],'PENDING_ROLE_A')
        self.assertEqual(b['eIndependentAiContentReview'],'PENDING')
        self.assertIs(b['humanTeacherPrerequisite'],False)
        self.assertEqual((b['newReady'],b['newMain'],b['newLive']),(0,0,0))
        self.assertEqual(b['masterPublisherRelease'],'NOT_AUTHORIZED')
        for qid in IDS:
            d=self.docs[qid]
            self.assertEqual(d['review']['sourceImageQaG1'],'DRAFT_NEEDS_DIRECT_VISUAL_QA')
            self.assertIs(d['review']['formalReady'],False)
            self.assertIs(d['review']['studentReleaseApproved'],False)
            self.assertIs(d['review']['newMain'],False)
            self.assertIs(d['review']['newLive'],False)

    def test_three_actual_original_single_question_and_source_page_byte_sha(self):
        for qid in IDS:
            q=self.bank[qid];m=self.manifest[qid];d=self.docs[qid]
            with self.subTest(qid=qid):
                self.assertEqual(m['qaStatus'],'DRAFT_NEEDS_DIRECT_VISUAL_QA')
                self.assertEqual(m['sha256'],WEBP[qid])
                self.assertEqual(q['questionProvenance']['webpSha256'],WEBP[qid])
                self.assertEqual(sh((ROOT/m['output']).read_bytes()),WEBP[qid])
                self.assertEqual(sh((ROOT/m['source']).read_bytes()),m['sourceSha256'])
                self.assertEqual(d['source']['webpSha256'],WEBP[qid])
                self.assertEqual(d['source']['sourcePageWebpSha256'],m['sourceSha256'])
                self.assertEqual(d['source']['archivedManifestQaStatus'],'DRAFT_NEEDS_DIRECT_VISUAL_QA')
                self.assertIs(d['source']['authorOriginalPixelTranscriptNotImageQa'],True)

    def test_actual_shared_reading_page6_blob_unchanged_and_official_answer_image_bytes(self):
        b=self.batch
        for qid in IDS:
            context=self.docs[qid]['enrichment']['readingContext']
            raw=(ROOT/context['originalPage6WebpPath']).read_bytes()
            self.assertEqual(sh(raw),PAGE6_SHA)
            self.assertEqual(gitblob(raw),PAGE6_BLOB)
            self.assertEqual(context['originalPage6WebpSha256'],PAGE6_SHA)
            self.assertIs(context['independentSharedReadingQa'],False)
            self.assertTrue(context['originalFigureAndTextAreNotRepainted'])
        answer=(ROOT/self.docs['114-00-C-16']['source']['officialAnswerPageWebpPath']).read_bytes()
        self.assertEqual(gitblob(answer),ANSWER_BLOB)
        self.assertEqual(b['originalReadingPage6GitBlob'],PAGE6_BLOB)
        self.assertEqual(b['originalAnswerPageGitBlob'],ANSWER_BLOB)

    def test_known_answer_not_blind_and_source_question_and_official_flags_preserved(self):
        for qid in IDS:
            q=self.bank[qid];d=self.docs[qid]
            self.assertEqual(q['answer'],EXPECTED[qid])
            self.assertEqual(d['knownAnswerCandidate'],EXPECTED[qid])
            self.assertEqual(d['question'],q['question'])
            self.assertEqual(d['options'],q['options'])
            self.assertEqual(d['source']['sourceIssueCodes'],q['issues'])
            self.assertIs(q['answerVerified'],False)
            self.assertIs(q['questionVerified'],False)
            self.assertIs(d['reasoningAudit']['answerAlreadyKnown'],True)
            self.assertIs(d['reasoningAudit']['notBlindSolve'],True)
            self.assertIs(d['source']['sharedReadingLinkNotYetCanonical'],True)

    def test_c16_pictorial_three_column_and_c17_footer_provisional_only(self):
        d=self.docs['114-00-C-16']
        v=d['enrichment']['originalVisual']
        self.assertEqual(v['type'],'ORIGINAL_3_COLUMN_COMPONENT_LOCATION_TABLE')
        self.assertEqual(v['correctSymbols'],['ㄅ','ㄈ','ㄉ'])
        self.assertEqual(v['choiceSymbols']['B'],['ㄅ','ㄈ','ㄉ'])
        self.assertTrue(v['notIndependentImageQa'])
        self.assertEqual(d['options'],d['imageTranscribedOptions'])
        c17=self.docs['114-00-C-17']
        self.assertIn('公告試題僅供參考',c17['options'][3])
        self.assertNotIn('公告試題僅供參考',c17['imageTranscribedOptions'][3])
        self.assertTrue(norm(c17['options'][3]).startswith(norm(c17['imageTranscribedOptions'][3])))
        for id in {'114-00-C-16','114-00-C-18'}:
            self.assertEqual(self.docs[id]['options'],self.docs[id]['imageTranscribedOptions'])
        for qid in IDS:
            self.assertEqual(len(self.docs[qid]['imageTranscribedOptions']),4)

    def test_four_distinct_adult_and_child_choice_reasons_and_no_arithmetic_card(self):
        for qid,d in self.docs.items():
            t=d['teaching']
            self.assertGreaterEqual(len(t['teacherSummary']),120)
            self.assertGreaterEqual(len(t['elementarySummary']),75)
            self.assertGreaterEqual(len(t['solvingSteps']),4)
            self.assertGreaterEqual(len(t['memory']),20)
            self.assertEqual(set(t['optionExplanations']),set('ABCD'))
            reasons=[]
            for k,v in t['optionExplanations'].items():
                self.assertIs(v['isCorrect'],k==EXPECTED[qid])
                self.assertGreaterEqual(len(v['teacher']),55)
                self.assertGreaterEqual(len(v['elementary']),25)
                self.assertGreaterEqual(len(v['why']),25)
                reasons.append(v['why'])
            self.assertEqual(len(set(reasons)),4)
            self.assertIs(t['hasExamCalculation'],False)
            self.assertIsNone(t['examCalculation'])
            self.assertNotIn('本題無金額計算',json.dumps(t,ensure_ascii=False))

    def test_safe_literal_highlights_chinese_three_levels_and_no_fake_textbook(self):
        for qid,d in self.docs.items():
            vocab=d['enrichment']['chineseVocabulary']
            self.assertEqual({w['level'] for w in vocab},{'初級','中級','高級'})
            for k in ('publisher','edition','chapter','page'):
                self.assertIsNone(d['textbook'][k])
            content=d['question']+' '+' '.join(d['options'])
            for mark in d['enrichment']['highlights']:
                self.assertIn(mark['text'],content)
                self.assertNotIn('<',mark['text'])
                self.assertNotIn('>',mark['text'])
                self.assertIs(mark['bold'],True)
                self.assertIs(mark['highlight'],True)
                self.assertEqual(mark['renderMode'],'literal_text_only')

    def test_per_question_revisions_and_composed_sha_detect_source_image_or_lesson_tamper(self):
        for row in self.batch['items']:
            qid=row['questionId'];d=self.docs[qid];q=self.bank[qid];m=self.manifest[qid]
            src=h({'question':q['question'],'options':q['options'],'singleQuestionWebpSha256':m['sha256']})
            tr=h({'question':q['question'],'options':d['imageTranscribedOptions'],'singleQuestionWebpSha256':m['sha256']})
            self.assertEqual(src,row['sourceRevision'])
            self.assertEqual(tr,row['sourceImageTranscriptSha256'])
            self.assertEqual(src,d['source']['questionRevision'])
            self.assertEqual(tr,d['source']['sourceImageTranscriptSha256'])
            self.assertEqual(h(d['teaching']),row['teachingCanonicalSha256'])
            self.assertEqual(h(d['teaching']),d['teachingCanonicalSha256'])
            composed={'questionId':qid,'sourceRevision':src,'sourceImageTranscriptSha256':tr,'webpSha256':m['sha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
            self.assertEqual(h(composed),row['composedTeachingSha256'])
            self.assertEqual(h(composed),d['composedTeachingSha256'])
            self.assertEqual(sh((ROOT/row['path']).read_bytes()),row['fileSha256'])
            self.assertNotEqual(h(dict(composed,sourceRevision='0'*64)),d['composedTeachingSha256'])
            self.assertNotEqual(h(dict(composed,sourceImageTranscriptSha256='1'*64)),d['composedTeachingSha256'])
            self.assertNotEqual(h(dict(composed,webpSha256='2'*64)),d['composedTeachingSha256'])
            self.assertNotEqual(h(dict(composed,teaching=dict(d['teaching'],memory='tampered'))),d['composedTeachingSha256'])
            self.assertNotEqual(h(dict(composed,enrichment={'tampered':True})),d['composedTeachingSha256'])

    def test_strict_role_a_e_d_master_blockers_no_author_self_approval(self):
        for d in self.docs.values():
            r=d['review']
            self.assertEqual(r['status'],'BLOCKED')
            self.assertIs(r['requiresHumanTeacher'],False)
            self.assertIs(r['authorSelfCheckOnly'],True)
            self.assertEqual(r['distinctAiE']['status'],'PENDING')
            self.assertEqual(r['distinctAiE']['reviewerRole'],'E')
            self.assertIsNone(r['distinctAiE']['reviewTaskId'])
            self.assertIsNone(r['distinctAiE']['reviewSessionId'])
            self.assertEqual(r['dV4ExactDigest8x2'],'PENDING')
            self.assertIn('G1_PER_QUESTION_ORIGINAL_WEBP_MANIFEST_DRAFT_QA_NOT_YET_PASS',r['blockers'])
            self.assertIn('E_DISTINCT_AI_PEDAGOGY_REVIEW_PENDING',r['blockers'])
            self.assertIn('MASTER_PROTECTED_MAIN_TRUST_AND_SAME_SHA_LIVE_PENDING',r['blockers'])

if __name__=='__main__':
    unittest.main()
