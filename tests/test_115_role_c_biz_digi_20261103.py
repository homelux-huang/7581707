"""Role C first five new 115 business/digital lessons. Source and release remain fail closed."""
import hashlib, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sudu/teaching-candidates/115-role-c-biz-digi-20261103/'
SOURCE=ROOT/'sudu/data/processed/115/questions.json'
def digest(v):
 return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
class CandidateCheck(unittest.TestCase):
 def test_exact_content_source_hash_and_no_release(self):
  b=json.loads((BASE/'batch.json').read_text(encoding='utf-8'))
  bank=json.loads(SOURCE.read_text(encoding='utf-8'))
  source={q['questionId']:q for q in bank['questions']}
  self.assertEqual(len(b['items']),5)
  self.assertEqual(len({x['questionId'] for x in b['items']}),5)
  self.assertEqual(b['newApprovals'],0)
  self.assertEqual(b['newDeployments'],0)
  for item in b['items']:
   path=ROOT/item['path'];raw=path.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),item['fileSha256'])
   q=json.loads(raw);s=source[q['questionId']];t=q['teaching']
   self.assertEqual(q['question'],s['question']);self.assertEqual(q['options'],s['options'])
   self.assertEqual(q['answerCandidate'],s['answer']);self.assertEqual(q['imageSha256'],s['assets']['sha256'])
   rev=digest(dict(question=s['question'],options=s['options'],singleQuestionWebpSha256=s['assets']['sha256']))
   self.assertEqual(q['sourceTextRevision'],rev);self.assertEqual(item['sourceRevision'],rev)
   self.assertEqual(digest(t),q['teachingCanonicalSha256']);self.assertEqual(digest(t),item['teachingSha256'])
   self.assertFalse(q['sourceQuestionVerified']);self.assertFalse(q['sourceAnswerFormalFinalVerified'])
   self.assertEqual(q['sourceIndividualVisualQa'],'PENDING_INDIVIDUAL_VISUAL_QA')
   self.assertFalse(q['studentReleaseApproved']);self.assertFalse(q['deploy']);self.assertFalse(item['ready'])
   self.assertEqual(q['review']['externalIndependentReview'],'PENDING')
   self.assertIn('DISTINCT_AI_CONTENT_E_REVIEW_RECEIPT_PENDING',q['blockers'])
   self.assertEqual(set(t['optionExplanations']),set('ABCD'))
   self.assertEqual([k for k,v in t['optionExplanations'].items() if v['isCorrect']],[q['answerCandidate']])
   self.assertTrue(t['highlights'])
   for k,v in t['optionExplanations'].items():
    self.assertGreaterEqual(len(v['teacher']),20,(q['questionId'],k))
    self.assertGreaterEqual(len(v['elementary']),12,(q['questionId'],k))
    self.assertTrue(v['reason'])
   if t['hasExamCalculation']:
    ex=t['examCalculation']
    self.assertTrue(all(ex.get(k) for k in ('given','formulaUse','substitution','steps','result','unit','option','verification')))
    self.assertEqual(ex['option'],q['answerCandidate'])
    self.assertTrue(any('驗算' in step for step in ex['steps']))
   else:self.assertIsNone(t['examCalculation'])
 def test_business08_independent_formulas(self):
  self.assertEqual(1.5*100000,150000)
  self.assertEqual(150000-15000-5000,130000)
  self.assertEqual(130000/100000,1.3)
  self.assertEqual((1005000-5000)/5,200000)
  self.assertEqual((1005000-5000)/200000,5)
 def test_ascii37_roundtrip_every_character(self):
  s='o6Lig@tE';v=[ord(c) for c in s]
  self.assertEqual(v,[111,54,76,105,103,64,116,69])
  self.assertEqual('、'.join(f'{i:03d}' for i in v),'111、054、076、105、103、064、116、069')
  self.assertEqual(''.join(chr(i) for i in v),s)
 def test_signature_terminology_and_e_quarantine(self):
  d=json.loads((BASE/'115-09-1-35.json').read_text(encoding='utf-8'))
  self.assertIn('驗證簽章',d['teaching']['teacherSummary'])
  self.assertIn('E_DIGITAL_SIGNATURE_VERIFICATION_VS_DECRYPTION_TERMINOLOGY_REVIEW',d['blockers'])
if __name__=='__main__':unittest.main()
