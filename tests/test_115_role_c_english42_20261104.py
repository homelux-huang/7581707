"""Role C 115 English E42 source-bound candidate tests, NO RELEASE."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sudu/teaching-candidates/115-role-c-english42-20261104/'
FILE=BASE/'115-00-E-42.json'
BATCH=BASE/'batch.json'
EVIDENCE=ROOT/'sudu/data/processed/115/review-evidence/115-00-E-42-original-shared-G1-20261103.json'
YEARS=ROOT/'sudu/data/years/115.json'
def digest(x):
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class Q42(unittest.TestCase):
 def test_original_A_evidence_shared_link_and_passage(self):
  e=json.loads(EVIDENCE.read_bytes())
  q=json.loads(FILE.read_bytes())
  papers=json.loads(YEARS.read_bytes())['papers']
  english=next(p for p in papers if p['paper']=='00-E')['questions']
  orig=next(x for x in english if x['number']==42)
  prior=next(x for x in english if x['number']==38)
  self.assertEqual(e['questionId'],q['questionId'])
  self.assertEqual(hashlib.sha256(e['sourceLinkRevisionSeed'].encode()).hexdigest(),q['roleASourceLinkRevision'])
  self.assertEqual(e['sourceLinkRevisionSha256'],q['roleASourceLinkRevision'])
  self.assertEqual(q['individualOriginalWebpSha256'],e['singleQuestion']['sha256'])
  self.assertEqual(q['sharedOriginalWebpSha256'],e['sharedMaterial']['sha256'])
  self.assertEqual(q['sharedOriginalG1Revision'],e['sharedMaterial']['sourceRevision'])
  self.assertEqual(q['question'],orig['question'])
  self.assertEqual(q['options'][:3],orig['options'][:3])
  self.assertTrue(orig['options'][3].startswith(q['options'][3]))
  self.assertGreater(len(orig['options'][3]),len(q['options'][3]))
  self.assertIn('非選擇題',orig['options'][3])
  self.assertNotIn('非選擇題',q['options'][3])
  self.assertEqual(q['answerCandidate'],e['officialAnswer']['publishedAnswer'])
  self.assertEqual(q['answerCandidate'],'C')
  article=prior['options'][3]
  article=article[article.index('Taiwan is a global high-tech powerhouse'):].strip()
  self.assertEqual(hashlib.sha256(article.encode()).hexdigest(),q['legacySharedArticleTextSha256'])
  for phrase in ('Four Taiwanese manufacturers','more money from AI servers than from iPhones','customers’ designs and requirements'):
   self.assertIn(phrase,article)
 def test_four_options_two_levels_IPA_translation_and_no_calculation(self):
  q=json.loads(FILE.read_bytes());t=q['teaching']
  self.assertEqual(set(t['optionExplanations']),set('ABCD'))
  self.assertEqual([k for k,v in t['optionExplanations'].items() if v['isCorrect']],['C'])
  for k,v in t['optionExplanations'].items():
   self.assertGreaterEqual(len(v['teacher']),25,k)
   self.assertGreaterEqual(len(v['elementary']),15,k)
   self.assertTrue(v['reason'])
  self.assertIn('making more money',t['teacherSummary'])
  self.assertIn('台數',t['teacherSummary'])
  self.assertIn('四家',t['optionExplanations']['A']['elementary'])
  self.assertIn('客戶',t['optionExplanations']['D']['elementary'])
  self.assertFalse(t['hasExamCalculation']);self.assertIsNone(t['examCalculation'])
  eng=t['englishSupport']
  self.assertEqual(set(eng['optionTranslations']),set('ABCD'))
  self.assertEqual(eng['questionTranslation'],'依據本文，下列哪一項敘述正確？')
  self.assertGreaterEqual(len(eng['ipaVocabulary']),4)
  for item in eng['ipaVocabulary']:
   self.assertTrue(item['ipa'].startswith('/') and item['ipa'].endswith('/'))
   self.assertIn(item['level'],['初級','中級','高級'])
   self.assertTrue(item['chinese'] and item['synonyms'])
  ex=eng['topicalExample']
  self.assertTrue(ex['english'] and ex['chinese'] and ex['highlightTerms'])
  self.assertIn('非當日新聞查核',ex['type'])
 def test_sha_source_candidate_and_fail_closed(self):
  q=json.loads(FILE.read_bytes());b=json.loads(BATCH.read_bytes())
  self.assertEqual(len(b['items']),1)
  r=b['items'][0]
  self.assertEqual(hashlib.sha256(FILE.read_bytes()).hexdigest(),r['fileSha256'])
  self.assertEqual(digest(q['teaching']),q['teachingCanonicalSha256'])
  self.assertEqual(r['teachingSha256'],q['teachingCanonicalSha256'])
  rev=digest(dict(question=q['question'],options=q['options'],singleQuestionWebpSha256=q['individualOriginalWebpSha256']))
  self.assertEqual(rev,q['sourceG2CleanTextCandidateRevision'])
  self.assertEqual(rev,r['sourceTextCandidateRevision'])
  self.assertFalse(q['officialG3FormallyAccepted'])
  self.assertFalse(q['review']['sourceG2FormallyAccepted'])
  self.assertEqual(q['review']['independentE'],'PENDING')
  self.assertFalse(q['studentReleaseApproved'])
  self.assertFalse(q['deploy']);self.assertFalse(r['ready'])
  self.assertEqual(b['newApprovals'],0)
  self.assertEqual(b['newDeployments'],0)
  self.assertIn('A_39_42_READING_G2_AND_Q42_D_FOOTER_REPAIR_NOT_FORMALLY_ADMITTED',q['blockers'])
  tampered=dict(question=q['question'],options=['Ten Taiwanese companies']+q['options'][1:],singleQuestionWebpSha256=q['individualOriginalWebpSha256'])
  self.assertNotEqual(digest(tampered),rev)
if __name__=='__main__':unittest.main()
