"""Source provenance/tamper tests; no independent E, blind solve, or release authority."""
import copy, importlib.util, json, os, shutil, sqlite3, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('e0810source',ROOT/'scripts/role_a_114_e08_e10_source_admission_20261116.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
@unittest.skipUnless(os.environ.get('E0810_FROZEN_SOURCE_ADMISSION')=='1','dedicated frozen source job only')
class SourceTests(unittest.TestCase):
 def question(self,qid='114-00-E-10'):
  return next(q for q in a.read(a.P+'questions.json')['questions'] if q['questionId']==qid)
 def test_native_positive_205_parity_and_three_original_pdfs(self):
  self.assertEqual(a.verify_pdfs(Path(os.environ['E0810_PDF_DIR'])),a.PDFS);a.verify()
 def test_footer_or_changed_option_rejected(self):
  for qid in a.QIDS:
   with self.subTest(qid=qid):
    q=self.question(qid);q['options'][3]+='\n-2-\n第11至20題';m=next(x for x in a.read(a.P+'webp-manifest.json')['items'] if x['questionId']==qid)
    with self.assertRaisesRegex(ValueError,'frozen revision'):a.images(q,m)
 def test_official_notice_scope_cannot_be_inflated(self):
  p=a.publisher();q=self.question();g=a.read(a.issuer(q['questionId'],'official'))
  for field,value in [('noObjectionForPaper',True),('confirmationPdfSha256','0'*64),('noCorrectionForThisQuestion',False),('correctionForQuestionReviewed',True)]:
   with self.subTest(field=field):self.assertFalse(p.official_notice_scope_certified(a.ROOT,114,q,{**g,field:value}))
 def test_issuer_path_wrong_qid_or_traversal_rejected(self):
  p=a.publisher()
  for path,qid in [(a.issuer('114-00-E-10','ocr'),'114-00-E-08'),('../outside.json','114-00-E-10'),('/tmp/outside.json','114-00-E-10')]:
   self.assertIsNone(p.review_document(a.ROOT,114,path,qid))
 def test_other_202_canonical_drift_rejected(self):
  path=a.ROOT/(a.P+'questions.json');original=path.read_bytes();bank=json.loads(original);bank['questions'][0]['answer']='Z'
  try:
   path.write_bytes(a.canonical_pretty(bank))
   with self.assertRaisesRegex(ValueError,'other202 canonical'):a.verify()
  finally:path.write_bytes(original)
 def test_wrong_target_answer_rejected(self):
  path=a.ROOT/(a.P+'questions.json');original=path.read_bytes();bank=json.loads(original);next(q for q in bank['questions'] if q['questionId']=='114-00-E-10')['answer']='D'
  try:
   path.write_bytes(a.canonical_pretty(bank))
   with self.assertRaisesRegex(ValueError,'exact bounded canonical'):a.verify()
  finally:path.write_bytes(original)
 def test_other_complete_sqlite_row_drift_rejected(self):
  path=a.ROOT/(a.P+'question-bank.sqlite3');original=path.read_bytes()
  try:
   with sqlite3.connect(path) as db:db.execute("UPDATE questions SET payload_sha256=? WHERE question_id='114-00-C-01'",('0'*64,))
   with self.assertRaisesRegex(ValueError,'other202 complete SQLite rows'):a.verify()
  finally:path.write_bytes(original)
 def test_actual_webp_byte_tamper_rejected(self):
  q=self.question();m=next(x for x in a.read(a.P+'webp-manifest.json')['items'] if x['questionId']==q['questionId']);path=a.ROOT/m['output'];original=path.read_bytes()
  try:
   path.write_bytes(original+b'tamper')
   with self.assertRaisesRegex(ValueError,'original image hash'):a.images(q,m)
  finally:path.write_bytes(original)
 def test_original_pdf_byte_tamper_rejected(self):
  folder=Path(os.environ['E0810_PDF_DIR'])
  with tempfile.TemporaryDirectory() as raw:
   tmp=Path(raw)
   for name in a.PDFS:shutil.copyfile(folder/(name+'.pdf'),tmp/(name+'.pdf'))
   with (tmp/'notice.pdf').open('ab') as f:f.write(b'tamper')
   with self.assertRaisesRegex(ValueError,'official PDF notice'):a.verify_pdfs(tmp)
 def test_g2_contains_no_official_answer_and_source_never_releases(self):
  p=a.publisher()
  for qid in a.QIDS:
   q=self.question(qid);g2=a.read(a.issuer(qid,'ocr'));m=next(x for x in a.read(a.P+'webp-manifest.json')['items'] if x['questionId']==qid)
   for key in ['answer','finalAnswer','officialPdfSha256']:self.assertNotIn(key,g2)
   self.assertFalse(p.certificates_complete(a.ROOT,q,m,{}));self.assertFalse(g2['studentReleaseApproved'])
