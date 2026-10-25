"""B06: original-pixel-author teaching only; real WebP bytes, raw-OCR quarantine, no admission."""
from pathlib import Path
import hashlib,json,unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'sudu/data/processed/114'
DIR=ROOT/'sudu/teaching-candidates/114-role-b-20261025-batch06'
IDS={'114-00-C-15','114-00-C-23','114-00-E-10','114-00-E-15','114-00-E-20'}
EXPECTED_CHANGED={'114-00-C-15':[0,1,2,3],'114-00-C-23':[],'114-00-E-10':[3],'114-00-E-15':[3],'114-00-E-20':[3]}
EXPECTED_KEYS={'114-00-C-15':'B','114-00-C-23':'D','114-00-E-10':'C','114-00-E-15':'A','114-00-E-20':'B'}
IPA={'114-00-E-10':('abandon','/əˈbæn.dən/','https://dictionary.cambridge.org/pronunciation/english/abandon'),
     '114-00-E-15':('properly','/ˈprɑː.pɚ.li/','https://dictionary.cambridge.org/pronunciation/english/properly'),
     '114-00-E-20':('invent','/ɪnˈvent/','https://dictionary.cambridge.org/pronunciation/english/invent')}

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(b):return hashlib.sha256(b).hexdigest()
def can(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def h(v):return digest(can(v))
def gitblob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

class ProvisionalB06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=load(DIR/'batch.json')
        cls.b={x['questionId']:x for x in load(DATA/'questions.json')['questions']}
        cls.m={x['questionId']:x for x in load(DATA/'webp-manifest.json')['items']}
        cls.docs={x['questionId']:load(ROOT/x['path']) for x in cls.batch['items']}
    def test_exact_five_no_release_and_no_teacher_credential_dependency(self):
        b=self.batch
        self.assertEqual(b['itemCount'],5)
        self.assertEqual(set(self.docs),IDS)
        self.assertIs(b['humanTeacherRequired'],False)
        self.assertTrue(b['canonicalSourceTextIssueStillPresent'])
        self.assertTrue(b['excludeFromPublisherBeforeRoleAReconciliation'])
        self.assertEqual((b['newReady'],b['newMain'],b['newLive']),(0,0,0))
        self.assertEqual(b['distinctEContentReview'],'PENDING')
    def test_real_five_webp_byte_sha_and_existing_image_only_receipts(self):
        for id in sorted(IDS):
            with self.subTest(id=id):
                d=self.docs[id];q=self.b[id];m=self.m[id]
                self.assertEqual(m['qaStatus'],'PASS')
                self.assertEqual(d['source']['webpSha256'],m['sha256'])
                self.assertEqual(m['sha256'],q['questionProvenance']['webpSha256'])
                self.assertEqual(digest((ROOT/m['output']).read_bytes()),m['sha256'])
                self.assertEqual(digest((ROOT/m['source']).read_bytes()),m['sourceSha256'])
                evidence=load(ROOT/d['source']['imageQaEvidence'])
                item=next(x for x in evidence['items'] if x['questionId']==id)
                self.assertEqual(item['reviewedWebpSha256'],m['sha256'])
                self.assertIn(item.get('result',item.get('reviewResult')),('PASS','PASS_DIRECT_SOURCE_PAGE_TO_SINGLE_WEBP','PASS_DIRECT_ORIGINAL_PAGE_IMAGE'))
                self.assertIs(item.get('answerVerified'),False)
                self.assertIs(item.get('questionVerified'),False)
    def test_keep_canonical_source_issues_and_never_mix_footer_into_clean_options(self):
        for id in sorted(IDS):
            with self.subTest(id=id):
                d=self.docs[id];q=self.b[id];m=self.m[id]
                self.assertEqual((d['question'],d['options'],d['knownAnswerCandidate']),(q['question'],q['options'],q['answer']))
                self.assertEqual(q['answer'],EXPECTED_KEYS[id])
                self.assertIn('last_on_page_check_possible_continuation_or_footer',q['issues'])
                self.assertEqual(d['source']['inheritedSourceIssueCodes'],q['issues'])
                self.assertIs(d['source']['officialSourceTextReconciliationRequired'],True)
                self.assertIs(d['source']['authorImageTranscriptionIsNotCanonical'],True)
                self.assertEqual(d['source']['sourceOptionMismatchIndices'],EXPECTED_CHANGED[id])
                self.assertEqual(len(d['imageTranscribedOptions']),4)
                for idx,(raw,clean) in enumerate(zip(q['options'],d['imageTranscribedOptions'])):
                    self.assertTrue(clean.strip())
                    self.assertNotIn('公告試題僅供參考',clean)
                    self.assertNotIn('共 12 頁',clean)
                    for part in clean.split('／'):
                        self.assertIn(''.join(part.split()),''.join(raw.split()))
                if id in {'114-00-E-10','114-00-E-15','114-00-E-20'}:
                    self.assertTrue(len(q['options'][3])>len(d['imageTranscribedOptions'][3]))
                if id=='114-00-C-15':
                    self.assertIn('▲閱讀下文',q['options'][3])
                if id=='114-00-C-23':
                    self.assertEqual(d['imageTranscribedOptions'],q['options'])
    def test_full_json_digest_binds_both_canonical_and_author_pixel_transcript(self):
        for row in self.batch['items']:
            with self.subTest(qid=row['questionId']):
                id=row['questionId'];d=self.docs[id];q=self.b[id];m=self.m[id]
                sr=h({'question':q['question'],'options':q['options'],'singleQuestionWebpSha256':m['sha256']})
                tr=h({'question':q['question'],'options':d['imageTranscribedOptions'],'singleQuestionWebpSha256':m['sha256']})
                self.assertEqual((sr,tr),(row['sourceRevision'],row['sourceImageTranscriptSha256']))
                self.assertEqual((sr,tr),(d['source']['questionRevision'],d['source']['sourceImageTranscriptSha256']))
                self.assertEqual(d['teachingCanonicalSha256'],h(d['teaching']))
                self.assertEqual(row['teachingCanonicalSha256'],h(d['teaching']))
                complete={'questionId':id,'sourceRevision':sr,'sourceImageTranscriptSha256':tr,'webpSha256':m['sha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
                self.assertEqual(h(complete),d['composedTeachingSha256'])
                self.assertEqual(h(complete),row['composedTeachingSha256'])
                self.assertEqual(digest((ROOT/row['path']).read_bytes()),row['fileSha256'])
    def test_each_option_explained_twice_without_generic_reason(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                t=d['teaching'];self.assertGreaterEqual(len(t['solvingSteps']),3)
                self.assertGreaterEqual(len(t['teacherSummary']),35)
                self.assertGreaterEqual(len(t['elementarySummary']),18)
                self.assertGreaterEqual(len(t['memory']),18)
                self.assertEqual(set(t['optionExplanations']),set('ABCD'))
                explanations=[]
                for key,z in t['optionExplanations'].items():
                    self.assertGreaterEqual(len(z['teacher']),33)
                    self.assertGreaterEqual(len(z['elementary']),13)
                    self.assertGreaterEqual(len(z['reason']),19)
                    self.assertIs(z['isCorrect'],key==EXPECTED_KEYS[id])
                    explanations.append(z['reason'])
                self.assertEqual(len(set(explanations)),4)
                self.assertIs(t['hasExamCalculation'],False)
                self.assertIsNone(t['examCalculation'])
                self.assertNotIn('本題無金額計算',json.dumps(t,ensure_ascii=False))
                self.assertIs(d['reasoningAudit']['answerAlreadyKnown'],True)
                self.assertIs(d['reasoningAudit']['blindSolveClaimed'],False)
    def test_safe_original_literally_highlight_and_graded_english_news(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                corpus=(d['question']+' '+' '.join(d['options'])+' '+' '.join(d['imageTranscribedOptions'])).casefold()
                for x in d['enrichment']['highlights']:
                    self.assertIn(x['text'].casefold(),corpus)
                    self.assertIs(x['bold'],True);self.assertIs(x['highlight'],True)
                    self.assertNotIn('<',x['text']);self.assertNotIn('>',x['text'])
                if id in IPA:
                    word,ipa,url=IPA[id]
                    vocab=d['enrichment']['englishVocabulary']
                    self.assertEqual({x['level'] for x in vocab},{'初級','中級','高級'})
                    entry=next(x for x in vocab if x['headword']==word)
                    self.assertEqual((entry['ipa'],entry['accent'],entry['ipaEvidenceUrl']),(ipa,'US',url))
                    for x in vocab:
                        self.assertTrue(x['synonyms'])
                        self.assertTrue(x['antonyms'])
                        if x['ipa'] is None:self.assertIsNone(x['ipaEvidenceUrl'])
                    news=d['enrichment']['newsExample']
                    self.assertGreaterEqual(int(news['publishedAt'][:4]),2024)
                    self.assertLessEqual(int(news['publishedAt'][:4]),2026)
                    self.assertIn(news['highlightEnglish'],news['english'])
                    self.assertIn(news['highlightZh'],news['zh'])
                    self.assertTrue(news['sourceUrl'].startswith('https://'))
                    self.assertIs(news['authorComposedBasedOnSource'],True)
                    self.assertIs(news['notDirectQuote'],True)
                else:
                    vocab=d['enrichment']['chineseVocabulary']
                    self.assertTrue({x['level'] for x in vocab}.issuperset({'初級','中級','高級'}))
    def test_classical_meanings_and_real_shared_original_webp_unchanged(self):
        d=self.docs['114-00-C-15']
        self.assertIn('威信不足',d['teaching']['concept'])
        self.assertIn('不是「仗勢欺負寡弱」',d['teaching']['concept'])
        self.assertEqual(len(d['enrichment']['classicalTextEvidence']),2)
        ctx=d['enrichment']['readingContext']
        for path,sha1 in [('originalArticlePage4Path','originalArticlePage4GitBlob'),('questionPage5Path','questionPage5GitBlob')]:
            raw=(ROOT/ctx[path]).read_bytes()
            self.assertEqual(gitblob(raw),ctx[sha1])
        c=self.docs['114-00-C-23']
        shared=c['enrichment']['sharedReading']
        self.assertEqual(shared['sharedMaterialId'],'114-00-C-SHARED-20-23')
        self.assertEqual(digest((ROOT/shared['webpPath']).read_bytes()),shared['webpSha256'])
        self.assertEqual(gitblob((ROOT/shared['webpPath']).read_bytes()),shared['webpGitBlob'])
        self.assertEqual(digest((ROOT/shared['sourcePageWebpPath']).read_bytes()),shared['sourcePageWebpSha256'])
        self.assertIn('甚者',c['teaching']['concept'])
    def test_fake_source_clearance_and_ai_self_approval_never_unlock_release(self):
        for d in self.docs.values():
            v=d['review'];e=v['independentAiContentReview']
            self.assertEqual(v['status'],'BLOCKED')
            self.assertIs(v['requiresHumanTeacher'],False)
            self.assertIs(v['formalReady'],False)
            self.assertIs(v['studentReleaseApproved'],False)
            self.assertIs(v['uiQaExactDigest'],False)
            self.assertTrue(v['authorSelfCheckOnly'])
            self.assertEqual(e['status'],'PENDING_ROLE_E')
            self.assertEqual(e['requiredReviewerRole'],'E')
            self.assertIsNone(e['reviewerSessionId'])
            self.assertIsNone(e['trustedEvidencePath'])
            self.assertIn('G2_CANONICAL_OCR_FOOTER_RECONCILIATION_PENDING',v['blockers'])
        d=self.docs['114-00-E-20']
        obj={'questionId':d['questionId'],'sourceRevision':d['source']['questionRevision'],'sourceImageTranscriptSha256':d['source']['sourceImageTranscriptSha256'],'webpSha256':d['source']['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
        current=h(obj)
        self.assertEqual(current,d['composedTeachingSha256'])
        self.assertNotEqual(h(dict(obj,sourceRevision='0'*64)),current)
        self.assertNotEqual(h(dict(obj,sourceImageTranscriptSha256='1'*64)),current)
        self.assertNotEqual(h(dict(obj,webpSha256='2'*64)),current)
        self.assertNotEqual(h(dict(obj,teaching=dict(d['teaching'],memory='CHANGED'))),current)

if __name__=='__main__': unittest.main()
