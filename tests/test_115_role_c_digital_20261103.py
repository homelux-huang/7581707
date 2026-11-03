"""ROLE C 115 digital 38/41/42/43/45 candidate-only integrity. No source/E/release gate bypass."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'sudu/teaching-candidates/115-role-c-digital-20261103/'
def sha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
class TestFive(unittest.TestCase):
 def test_exact_source_hash_teaching_and_fail_closed(self):
  batch=json.loads((BASE/'batch.json').read_text(encoding='utf-8'))
  src=json.loads((ROOT/'sudu/data/processed/115/questions.json').read_text(encoding='utf-8'))
  source={x['questionId']:x for x in src['questions']}
  self.assertEqual(len(batch['items']),5)
  self.assertEqual(set(x['questionId'] for x in batch['items']),set(["115-09-1-38","115-09-1-41","115-09-1-42","115-09-1-43","115-09-1-45"]))
  self.assertEqual((batch['newApprovals'],batch['newDeployments']),(0,0))
  for ent in batch['items']:
   p=ROOT/ent['path'];raw=p.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),ent['fileSha256'])
   q=json.loads(raw);s=source[q['questionId']];t=q['teaching']
   self.assertEqual(q['question'],s['question']);self.assertEqual(q['options'],s['options'])
   self.assertEqual(q['imageSha256'],s['assets']['sha256'])
   self.assertEqual(q['sourceTextRevision'],sha(dict(question=s['question'],options=s['options'],singleQuestionWebpSha256=s['assets']['sha256'])))
   self.assertEqual(q['sourceTextRevision'],ent['sourceRevision'])
   self.assertEqual(sha(t),q['teachingCanonicalSha256']);self.assertEqual(sha(t),ent['teachingSha256'])
   self.assertFalse(q['studentReleaseApproved']);self.assertFalse(q['deploy']);self.assertFalse(ent['ready'])
   self.assertFalse(q['sourceQuestionVerified']);self.assertFalse(q['officialFinalDirectVerified'])
   self.assertEqual(q['sourceIndividualVisualQa'],'PENDING_INDIVIDUAL_VISUAL_QA')
   self.assertEqual(q['review']['externalIndependentReview'],'PENDING')
   self.assertIn('DISTINCT_AI_CONTENT_E_REVIEW_RECEIPT_PENDING',q['blockers'])
   self.assertEqual(set(t['optionExplanations']),set('ABCD'))
   self.assertEqual([x for x,v in t['optionExplanations'].items() if v['isCorrect']],[q['answerCandidate']])
   self.assertTrue(t['highlights'] and t['reasoningSteps'])
   for o in t['optionExplanations'].values():
    self.assertGreaterEqual(len(o['teacher']),20);self.assertGreaterEqual(len(o['elementary']),12)
   if t['hasExamCalculation']:
    ex=t['examCalculation']
    self.assertEqual(ex['option'],q['answerCandidate'])
    self.assertTrue(all(ex[k] for k in ('given','formulaUse','substitution','steps','result','unit','verification')))
    self.assertTrue(any('驗算' in x for x in ex['steps']))
   else:self.assertIsNone(t['examCalculation'])
 def test_excel41_example_is_not_presented_as_official_data(self):
  q=json.loads((BASE/'115-09-1-41.json').read_text(encoding='utf-8'))
  self.assertIn('示範',q['teaching']['extension'])
  self.assertEqual(sum([93,88,87,80,79,76]),503)
  self.assertEqual(round(503/6),84)
  self.assertEqual(q['answerCandidate'],'C')
 def test_other_subject_labels(self):
  for id,answer,term in [('115-09-1-38','D','合併列印'),('115-09-1-42','B','Google Meet'),('115-09-1-43','D','XML'),('115-09-1-45','D','iframe')]:
   d=json.loads((BASE/(id+'.json')).read_text(encoding='utf-8'))
   self.assertEqual(d['answerCandidate'],answer);self.assertIn(term,d['teaching']['teacherSummary'])
if __name__=='__main__':unittest.main()
