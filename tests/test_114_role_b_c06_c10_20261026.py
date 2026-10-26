"""Role B 114 C06/C10: original WebP bytes + G2 OCR quarantine, teacher/elementary candidate NO RELEASE."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'sudu/teaching-candidates/114-role-b-c06-c10-20261026'
SRC=ROOT/'sudu/data/processed/114'
ANS={'114-00-C-06':'C','114-00-C-10':'B'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def hs(b):return hashlib.sha256(b).hexdigest()
def h(o):return hs(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
class CausationAndCrisisAuthorOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=load(DIR/'batch.json')
        cls.source={x['questionId']:x for x in load(SRC/'questions.json')['questions']}
        cls.mani={x['questionId']:x for x in load(SRC/'webp-manifest.json')['items']}
        cls.qa=load(ROOT/cls.b['archivedImageOnlyQaPath'])
        cls.docs={z['questionId']:load(ROOT/z['path']) for z in cls.b['items']}
    def test_01_exact_scope_and_no_release(self):
        self.assertEqual(set(self.docs),set(ANS))
        self.assertEqual(self.b['itemCount'],2)
        self.assertTrue(self.b['roleBAuthorOnly'])
        self.assertTrue(self.b['sourceG2PollutionUnresolved'])
        self.assertFalse(self.b['requiresHumanTeacher'])
        self.assertEqual((self.b['newReady'],self.b['newMain'],self.b['newLive']),(0,0,0))
    def test_02_original_two_webps_and_original_source_pages_bytes(self):
        for id,doc in self.docs.items():
            with self.subTest(id=id):
                q=self.source[id];m=self.mani[id]
                self.assertEqual(m['qaStatus'],'PASS')
                self.assertEqual(m['sha256'],q['questionProvenance']['webpSha256'])
                self.assertEqual(hs((ROOT/m['output']).read_bytes()),m['sha256'])
                self.assertEqual(hs((ROOT/m['source']).read_bytes()),m['sourceSha256'])
                self.assertEqual(doc['source']['webpSha256'],m['sha256'])
                qa=next(x for x in self.qa['records'] if x['questionId']==id)
                self.assertEqual(qa['result'],'PASS')
                self.assertEqual(qa['webpSha256'],m['sha256'])
                self.assertEqual(self.b['archivedImageOnlyQaPath'],doc['source']['roleAOriginalPixelQaReference'])
    def test_03_original_announced_answer_and_no_false_official_verification(self):
        p=(ROOT/self.b['announcedAnswerPage']).read_bytes()
        self.assertEqual(gitblob(p),self.b['announcedAnswerGitBlob'])
        for id,d in self.docs.items():
            self.assertEqual(d['knownAnswerCandidate'],ANS[id])
            self.assertFalse(d['source']['answerVerified'])
            self.assertFalse(d['source']['questionVerified'])
            self.assertFalse(d['source']['officialAnswerFinalCorrectionNoticeVerified'])
    def test_04_raw_ocr_unchanged_and_author_transcript_not_canonical(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                q=self.source[id]
                self.assertEqual(d['question'],q['question'])
                self.assertEqual(d['options'],q['options'])
                self.assertEqual(q['issues'],['last_on_page_check_possible_continuation_or_footer'])
                self.assertEqual(d['source']['sourceIssueCodes'],q['issues'])
                self.assertEqual(len(d['imageTranscribedOptions']),4)
                self.assertIn('公告試題僅供參考',''.join(d['options']))
                self.assertNotIn('公告試題僅供參考',''.join(d['imageTranscribedOptions']))
                self.assertNotIn('▲閱讀下文',''.join(d['imageTranscribedOptions']))
                self.assertTrue(d['source']['authorOnlyPixelTranscription'])
                self.assertTrue(d['source']['sourceNeedsRoleAOfficialG2TableCorrection'])
    def test_05_source_transcript_teaching_composed_full_sha(self):
        for x in self.b['items']:
            with self.subTest(id=x['questionId']):
                d=self.docs[x['questionId']];q=self.source[x['questionId']];img=x['webpSha256']
                rev=h({'question':q['question'],'options':q['options'],'singleQuestionWebpSha256':img})
                trans=h({'question':q['question'],'options':d['imageTranscribedOptions'],'singleQuestionWebpSha256':img})
                self.assertEqual(rev,x['sourceRevision'])
                self.assertEqual(trans,x['imageTranscriptRevision'])
                self.assertEqual(rev,d['source']['sourceRevision'])
                self.assertEqual(trans,d['source']['imageTranscriptRevision'])
                self.assertEqual(h(d['teaching']),d['teachingCanonicalSha256'])
                self.assertEqual(h(d['teaching']),x['teachingCanonicalSha256'])
                comp=h({'questionId':x['questionId'],'sourceRevision':rev,'imageTranscriptRevision':trans,'webpSha256':img,'teaching':d['teaching'],'enrichment':d['enrichment']})
                self.assertEqual(comp,x['composedTeachingSha256'])
                self.assertEqual(comp,d['composedTeachingSha256'])
                self.assertEqual(hs((ROOT/x['path']).read_bytes()),x['fileSha256'])
    def test_06_correct_original_causal_diagram_and_crisis_pairing(self):
        c=self.docs['114-00-C-06']['enrichment']['originalPixelVisual']
        self.assertEqual(c['answerColumn'],'C')
        self.assertEqual(c['diagramForms'],['ONE_TO_ONE','CHAIN','ONE_TO_TWO','TWO_TO_ONE'])
        self.assertIn('舞幽壑之潛蛟',c['exampleCells']['C'])
        self.assertIn('泣孤舟之嫠婦',c['exampleCells']['C'])
        t=self.docs['114-00-C-10']['enrichment']['originalPixelVisual']
        self.assertEqual(t['optionRows']['B'],['①⑥','②'])
        self.assertEqual(t['definitions']['①'],'道歉，表示懺悔')
        self.assertIn('卸責',t['definitions']['②'])
        self.assertIn('切身相關',t['definitions']['⑥'])
        self.assertTrue(t['originalPixelsMustBeDisplayed'])
    def test_07_4_distinct_teacher_child_reasons_and_literal_highlight(self):
        for id,d in self.docs.items():
            with self.subTest(id=id):
                t=d['teaching']
                self.assertGreaterEqual(len(t['teacherSummary']),75)
                self.assertGreaterEqual(len(t['elementarySummary']),38)
                self.assertGreaterEqual(len(t['solvingSteps']),3)
                self.assertEqual(set(t['optionExplanations']),set('ABCD'))
                all_reasons=[]
                for ch,z in t['optionExplanations'].items():
                    self.assertGreaterEqual(len(z['teacher']),43)
                    self.assertGreaterEqual(len(z['elementary']),20)
                    self.assertGreaterEqual(len(z['reason']),25)
                    self.assertEqual(z['isCorrect'],ch==ANS[id])
                    all_reasons.append(z['reason'])
                self.assertEqual(len(set(all_reasons)),4)
                self.assertIsNone(t['examCalculation'])
                self.assertFalse(t['hasExamCalculation'])
                txt=''.join(' '.join([d['question'],*d['options'],*d['imageTranscribedOptions']]).split())
                for mark in d['enrichment']['highlights']:
                    self.assertIn(''.join(mark['text'].split()),txt)
                    self.assertTrue(mark['bold'] and mark['highlight'])
                    self.assertEqual(mark['renderMode'],'LITERAL_SAFE_TEXT_ONLY')
                    self.assertNotIn('<',mark['text'])
                    self.assertNotIn('>',mark['text'])
                self.assertEqual({v['level'] for v in d['enrichment']['chineseVocabulary']},{'初級','中級','高級'})
    def test_08_negative_reject_fake_e_approval_and_stale_revision(self):
        for d in self.docs.values():
            v=d['review']
            self.assertEqual(v['status'],'BLOCKED')
            self.assertTrue(v['roleBAuthorSelfReviewOnly'])
            self.assertFalse(v['formalReady'])
            self.assertFalse(v['studentReleaseApproved'])
            self.assertFalse(v['newMain'])
            self.assertFalse(v['newLive'])
            self.assertEqual(v['independentAiRoleEReview'],'PENDING_DISTINCT_AUTHOR')
            self.assertFalse(d['source']['answerVerified'])
        d=self.docs['114-00-C-06']
        o={'questionId':d['questionId'],'sourceRevision':d['source']['sourceRevision'],'imageTranscriptRevision':d['source']['imageTranscriptRevision'],'webpSha256':d['source']['webpSha256'],'teaching':d['teaching'],'enrichment':d['enrichment']}
        old=h(o)
        self.assertEqual(old,d['composedTeachingSha256'])
        self.assertNotEqual(old,h(dict(o,sourceRevision='0'*64)))
        self.assertNotEqual(old,h(dict(o,imageTranscriptRevision='1'*64)))
        self.assertNotEqual(old,h(dict(o,webpSha256='2'*64)))
        self.assertNotEqual(old,h(dict(o,teaching=dict(d['teaching'],memory='TAMPERED'))))
if __name__=='__main__':unittest.main()
