"""Frozen source admission; dedicated fixtures only; does not grant E or LIVE."""
import copy, importlib.util, json, os, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('e07source',ROOT/'scripts/role_a_114_e07_source_admission_20261115.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
@unittest.skipUnless(os.environ.get('E07_FROZEN_SOURCE_ADMISSION')=='1','dedicated frozen E07 source job only')
class E07SourceTests(unittest.TestCase):
 def test_source_and_205_full_tuple_parity(self): a.verify()
 def test_changed_option_invalidates_source_binding(self):
  q=next(q for q in a.read(a.P+'questions.json')['questions'] if q['questionId']==a.QID);m=next(m for m in a.read(a.P+'webp-manifest.json')['items'] if m['questionId']==a.QID)
  q['options'][0]='forged'
  with self.assertRaisesRegex(ValueError,'revision'):a.images(q,m)
 def test_wrong_official_notice_scope_rejected_by_native_publisher(self):
  q=next(q for q in a.read(a.P+'questions.json')['questions'] if q['questionId']==a.QID);g=a.read(a.G3);p=a.publisher()
  for field,value in [('noObjectionForPaper',True),('confirmationPdfSha256','0'*64),('noCorrectionForThisQuestion',False),('correctionForQuestionReviewed',True)]:
   with self.subTest(field=field):
    bad={**g,field:value};self.assertFalse(p.official_notice_scope_certified(a.ROOT,114,q,bad))
 def test_native_document_path_and_wrong_question_rejected(self):
  p=a.publisher()
  for rel,qid in [('../outside.json',a.QID),(a.G2,'114-00-E-08'),('/tmp/outside.json',a.QID)]:self.assertIsNone(p.review_document(a.ROOT,114,rel,qid))
 def test_other_question_sqlite_drift_and_wrong_answer_rejected(self):
  path=a.ROOT/(a.P+'questions.json');b=path.read_bytes();doc=json.loads(b);doc['questions'][0]['answer']='Z'
  try:
   path.write_bytes(json.dumps(doc,ensure_ascii=False).encode())
   with self.assertRaisesRegex(ValueError,'other204'):a.verify()
  finally:path.write_bytes(b)
 def test_official_three_pdf_bytes_and_tamper_rejected(self):
  import tempfile,shutil
  folder=Path(os.environ['E07_PDF_DIR']);self.assertEqual(a.verify_pdfs(folder),a.PDFS)
  with tempfile.TemporaryDirectory() as d:
   tmp=Path(d)
   for name in a.PDFS:shutil.copyfile(folder/(name+'.pdf'),tmp/(name+'.pdf'))
   with (tmp/'notice.pdf').open('ab') as f:f.write(b'tamper')
   with self.assertRaisesRegex(ValueError,'official PDF notice'):a.verify_pdfs(tmp)
