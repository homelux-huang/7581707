"""ROLE C exact original MB23 A PR129 source fixture, teaching and fail-closed tests."""
import hashlib,json,unittest
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sudu/teaching-candidates/114-115-20261025/'
C=BASE/'115-00-MB-23.json'
BATCH=BASE/'batch.json'
UP=ROOT/'tests/fixtures/role_c_115_mb23_a_pr129_source_evidence_20261104.json'
A_GIT_BLOB='0f63d6a5f91015dd2b146731c48dce08668c1fa2'
A_REV='9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4'
C_OLD_REV='c3df98d4c15185803c1b17294c514a19496395d0087364825d2bdce144a10b92'
TEACH_SHA='13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6'
def teachhash(x):
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class ReconcileMB23(unittest.TestCase):
 def test_source_evidence_is_exact_upstream_git_blob(self):
  raw=UP.read_bytes()
  self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),A_GIT_BLOB)
  a=json.loads(raw)
  self.assertEqual(a['questionId'],'115-00-MB-23')
  x=a['originalTextAndTable']
  self.assertEqual(hashlib.sha256(x['sourceRevisionSeed'].encode()).hexdigest(),A_REV)
  self.assertEqual(x['sourceRevisionSha256'],A_REV)
  self.assertFalse(a['downstream']['masterCanonicalSourceAdmitted'])
  self.assertFalse(a['downstream']['independentEContentRegistryApproved'])
  self.assertFalse(a['downstream']['ready'])
 def test_same_original_question_four_options_two_by_three_table(self):
  a=json.loads(UP.read_bytes());q=json.loads(C.read_bytes())
  x=a['originalTextAndTable']
  self.assertEqual(q['question'],x['correctedQuestion'])
  self.assertEqual(q['options'],x['originalOptions'])
  self.assertEqual(q['imageSha256'],a['source']['originalSingleWebpSha256'])
  self.assertEqual(q['sourceTables'][0]['heading'],x['sourceTable']['columns'])
  self.assertEqual(q['sourceTables'][0]['rows'],x['sourceTable']['rows'])
  self.assertEqual([len(z) for z in q['sourceTables'][0]['rows']],[3,3])
  self.assertEqual(len(q['sourceTables'][0]['heading']),3)
  self.assertEqual(q['sourceTextRevisionWithTable'],A_REV)
  self.assertNotEqual(q['sourceTextRevisionWithTable'],C_OLD_REV)
  self.assertEqual(q['sourceTableProvenance']['sourceEvidenceGitBlob'],A_GIT_BLOB)
  self.assertEqual(q['sourceTableProvenance']['referencePR'],129)
 def test_author_unchanged_math_and_source_release_gates(self):
  q=json.loads(C.read_bytes())
  self.assertEqual(teachhash(q['teaching']),TEACH_SHA)
  self.assertEqual(q['teachingCanonicalSha256'],TEACH_SHA)
  self.assertEqual(q['teaching']['examCalculation']['option'],'B')
  self.assertEqual([k for k,v in q['teaching']['optionExplanations'].items() if v['isCorrect']],['B'])
  self.assertEqual([x for x in (32000,33000,34000,35000) if 2*x-3000==Fraction(9,5)*(x+2000)],[33000])
  self.assertEqual(2*33000-3000,63000)
  self.assertEqual(Fraction(9,5)*(33000+2000),63000)
  self.assertFalse(q['sourceTableProvenance']['masterCanonicalQuestionSqliteAdmitted'])
  self.assertFalse(q['review']['sourceRevisionAccepted'])
  self.assertEqual(q['review']['externalIndependentReview'],'PENDING')
  self.assertFalse(q['studentReleaseApproved']);self.assertFalse(q['deploy'])
  self.assertIn('TABLE_A_PR129_G2_G3_CANDIDATE_NOT_MASTER_ADMITTED',q['blockers'])
  self.assertIn('DISTINCT_AI_CONTENT_E_REVIEW_RECEIPT_PENDING',q['blockers'])
 def test_exact_batch_file_hash_and_other_lessons_unchanged(self):
  batch=json.loads(BATCH.read_bytes())
  self.assertEqual(len(batch['items']),6)
  q=next(i for i in batch['items'] if i['questionId']=='115-00-MB-23')
  self.assertEqual(q['sourceTextRevisionWithTable'],A_REV)
  self.assertEqual(q['teachingSha256'],TEACH_SHA)
  self.assertEqual(hashlib.sha256(C.read_bytes()).hexdigest(),q['fileSha256'])
  self.assertFalse(q['ready'])
  for id,digest in {
   '115-00-MB-21':'4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4',
   '115-00-MB-22':'5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600'}.items():
   row=next(i for i in batch['items'] if i['questionId']==id)
   self.assertEqual(row['teachingSha256'],digest)
   self.assertEqual(teachhash(json.loads((ROOT/row['path']).read_bytes())['teaching']),digest)
 def test_mutated_original_table_is_rejected(self):
  q=json.loads(C.read_bytes());s=json.loads(UP.read_bytes())['originalTextAndTable']
  bad=json.loads(json.dumps(s['sourceTable']))
  bad['rows'][1][2]='兩人都打八折'
  self.assertNotEqual(q['sourceTables'][0]['rows'],bad['rows'])
  self.assertNotEqual(q['sourceTextRevisionWithTable'],'00'*32)
if __name__=='__main__':unittest.main()
