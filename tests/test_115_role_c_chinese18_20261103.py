"""115 C18 exact A original two-column lesson binding, AUTHOR ONLY, no release."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'sudu/teaching-candidates/115-role-c-chinese18-20261103/'
A=ROOT/'sudu/data/processed/115/review-evidence/115-00-C-18-G1-G2-TABLE-CROSSPAGE-20261102.json'
SHARED=ROOT/'sudu/data/processed/115/review-evidence/115-00-C-SHARED-16-18-G2-COLUMNS-20261102.json'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
class Chinese18(unittest.TestCase):
 def test_exact_upstream_chart_and_original_pixel_receipt(self):
  a=json.loads(A.read_text(encoding='utf-8'));s=json.loads(SHARED.read_text(encoding='utf-8'));d=json.loads((DIR/'115-00-C-18.json').read_text(encoding='utf-8'))
  self.assertEqual(a['questionId'],d['questionId'])
  self.assertEqual(d['question'],a['g2StructuredSource']['question'])
  self.assertEqual(d['options'],a['g2StructuredSource']['correctedOptions'])
  self.assertEqual(d['sourceChart'],a['g2StructuredSource']['chart'])
  self.assertEqual(d['sourceTables'][0]['rows'],a['g2StructuredSource']['optionRows'])
  self.assertEqual([x['responseForJia']+x['responseForYi'] for x in d['sourceTables'][0]['rows']],['①③','①④','②③','②④'])
  self.assertEqual(d['sourceTextRevision'],a['g2StructuredSource']['sourceRevision'])
  self.assertEqual(hashlib.sha256(d['sourceTextRevisionSeed'].encode()).hexdigest(),d['sourceTextRevision'])
  self.assertEqual(d['imageSha256'],a['sourceImage']['sha256'])
  self.assertEqual(d['sharedMaterialWebpSha256'],s['sourceImage']['sha256'])
  self.assertEqual(d['sharedMaterialTextRevision'],s['g2SourceText']['sharedMaterialRevision'])
  self.assertEqual(a['officialAnswer']['candidateAndOfficialPrinted'],'D')
  self.assertTrue(a['g2StructuredSource']['crossPageQ19To22Removed'])
  self.assertNotIn('專家座談會',d['question']+' '.join(d['options']))
 def test_teacher_elementary_four_options_digest_release_gate(self):
  d=json.loads((DIR/'115-00-C-18.json').read_text(encoding='utf-8'));b=json.loads((DIR/'batch.json').read_text(encoding='utf-8'));t=d['teaching']
  self.assertEqual(len(b['items']),1)
  self.assertEqual(hashlib.sha256((DIR/'115-00-C-18.json').read_bytes()).hexdigest(),b['items'][0]['fileSha256'])
  self.assertEqual(digest(t),d['teachingCanonicalSha256'])
  self.assertEqual(digest(t),b['items'][0]['teachingSha256'])
  self.assertEqual(set(t['optionExplanations']),set('ABCD'))
  self.assertEqual([x for x,v in t['optionExplanations'].items() if v['isCorrect']],['D'])
  for val in t['optionExplanations'].values():
   self.assertGreaterEqual(len(val['teacher']),20)
   self.assertGreaterEqual(len(val['elementary']),12)
  self.assertIn('甲②',t['teacherSummary'])
  self.assertIn('乙④',t['teacherSummary'])
  self.assertFalse(t['hasExamCalculation']);self.assertIsNone(t['examCalculation'])
  self.assertFalse(d['studentReleaseApproved']);self.assertFalse(d['deploy']);self.assertFalse(d['officialFinalAnswerG3Admitted'])
  self.assertFalse(b['items'][0]['ready']);self.assertEqual((b['newApprovals'],b['newDeployments']),(0,0))
  self.assertIn('DISTINCT_AI_CONTENT_E_REVIEW_RECEIPT_PENDING',d['blockers'])
  self.assertEqual(d['review']['externalIndependentReview'],'PENDING')
if __name__=='__main__':unittest.main()
