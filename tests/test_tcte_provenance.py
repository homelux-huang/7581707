"""Regression tests for material data-loss, wrong-paper and false-verification risks."""
import copy, hashlib, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tcte_preserve_teaching import merge_year, stable_key
from check_tcte_corpus import in_scope, complete_reasons, complete_teaching, webp_dimensions


def sample():
    return {'id':'fixture-01','year':115,'paper':'09-2','number':1,'subject':'會計學',
        'question':'A fixture question, not an official exam.','options':['one','two','three','four'],
        'answer':0,'acceptedAnswers':[0,2],'source':'https://web1.tcte.edu.tw/EXAM/115_4y/question.pdf',
        'answerSource':'https://web1.tcte.edu.tw/EXAM/115_4y/answer.pdf',
        'sourceVersion':{'questionPdfSha256':'a'*64,'answerPdfSha256':'b'*64},
        'questionVerified':True,'answerVerified':True,'answerReviewedBy':'fixture reviewer','answerReviewedAt':'2026-01-01',
        'teachingVerified':True,'textbookVerified':True,'explanation':'An existing reviewed explanation.',
        'principle':'A known fixture principle.','steps':'A fixture step.','wrongOptions':['reason1','reason2','reason3','reason4'],
        'extension':'A known fixture extension.','practice':{'question':'A self-authored fixture question.',
        'options':['one','two','three','four'],'answerIndex':0,'explanation':'This is fixture teaching.'}}

def annual(q):return {'papers':[{'paper':'09-2','questions':[q]}]}

class ProvenanceTests(unittest.TestCase):
    def test_98_is_modern_commerce_and_97_09_is_not(self):
        self.assertTrue(in_scope(98,'09-1'));self.assertFalse(in_scope(97,'09-1'))
        self.assertTrue(in_scope(91,'BIZ-1'));self.assertFalse(in_scope(98,'BIZ-1'))

    def test_unchanged_review_survives_import(self):
        old=sample();new=copy.deepcopy(old)
        for key in ['explanation','questionVerified','answerVerified','teachingVerified','textbookVerified']:new.pop(key)
        self.assertEqual(merge_year(annual(old),annual(new)),(1,0))
        self.assertTrue(new['answerVerified']);self.assertEqual(new['explanation'],old['explanation'])

    def test_legacy_machine_answer_does_not_regain_review(self):
        old=sample();old.pop('answerReviewedBy');new=copy.deepcopy(old);new['answerVerified']=False
        merge_year(annual(old),annual(new))
        self.assertFalse(new['answerVerified']);self.assertTrue(new['answerMatched'])

    def assert_invalidated(self,old,new):
        doc=annual(new);merge_year(annual(old),doc)
        for flag in ['questionVerified','answerVerified','teachingVerified','textbookVerified']:self.assertFalse(new[flag])
        self.assertTrue(new['scoringNeedsReview']);self.assertEqual(new['verificationHistory'][0]['snapshot']['answer'],old['answer'])
        before=json.dumps(doc,sort_keys=True);merge_year(annual(old),doc);self.assertEqual(before,json.dumps(doc,sort_keys=True))

    def test_question_source_pdf_change_invalidates_and_archives(self):
        old=sample();new=copy.deepcopy(old);new['sourceVersion']['questionPdfSha256']='c'*64
        self.assert_invalidated(old,new)

    def test_answer_pdf_change_invalidates_even_same_numeric_answer(self):
        old=sample();new=copy.deepcopy(old);new['sourceVersion']['answerPdfSha256']='c'*64
        self.assert_invalidated(old,new)

    def test_official_accepted_answer_change_invalidates(self):
        old=sample();new=copy.deepcopy(old);new['acceptedAnswers']=[0]
        self.assert_invalidated(old,new)

    def test_source_url_change_is_not_ignored(self):
        old=sample();new=copy.deepcopy(old);new['source']='https://web1.tcte.edu.tw/EXAM/114_4y/question.pdf'
        self.assert_invalidated(old,new)

    def test_english_word_boundary_change_is_not_ignored(self):
        old=sample();new=copy.deepcopy(old);old['question']='nowhere';new['question']='now here'
        self.assertNotEqual(stable_key(old),stable_key(new))

    def test_retired_question_keeps_version_and_id(self):
        old=sample();new={'papers':[]};merge_year(annual(old),new)
        self.assertEqual(new['retiredQuestionVersions'][0]['snapshot']['id'],old['id'])
        before=json.dumps(new,sort_keys=True);merge_year(annual(old),new);self.assertEqual(before,json.dumps(new,sort_keys=True))

    def test_textbook_review_is_independent_of_teaching_completeness(self):
        q=sample();q['textbook']=None;q['textbookVerified']=False
        self.assertTrue(complete_teaching(q))

    def test_generic_wrong_reason_is_not_complete(self):
        q=sample();q['wrongOptions'][1]='不符合題意。'
        self.assertFalse(complete_reasons(q))

    def test_truncated_webp_fails(self):
        with self.assertRaises(ValueError):webp_dimensions(b'RIFF'+b'\x00'*40)

@unittest.skipUnless(importlib.util.find_spec('requests') and importlib.util.find_spec('bs4'),'optional importer dependencies not installed')
class NativeExtractionTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('fitz') and importlib.util.find_spec('PIL'),'optional renderer dependencies not installed')
    def test_rendered_pages_are_complete_color_webp(self):
        import fitz
        from PIL import Image
        import tcte_source_images as renderer
        pdf=fitz.open();page=pdf.new_page(width=200,height=200)
        page.draw_rect(page.rect,color=(1,0,0),fill=(1,0,0))
        payload=pdf.tobytes();pdf.close()
        original_root,original_out=renderer.ROOT,renderer.OUT
        with tempfile.TemporaryDirectory() as temporary:
            try:
                renderer.ROOT=Path(temporary);renderer.OUT=renderer.ROOT/'sudu/data/original'
                result=renderer.render_pdf(payload,115,'fixture',[],
                    'https://web1.tcte.edu.tw/EXAM/115_4y/fixture.pdf',width=700)
                for pg in result['pages']:
                    path=renderer.ROOT/'sudu'/pg['src'];data=path.read_bytes()
                    self.assertGreater(len(data),0);self.assertEqual(len(data),pg['bytes'])
                    self.assertEqual(hashlib.sha256(data).hexdigest(),pg['sha256'])
                    with Image.open(path) as image:
                        image.load();red,green,blue=image.convert('RGB').getpixel((350,350))
                        self.assertGreater(red,200);self.assertLess(green,30);self.assertLess(blue,30)
                self.assertEqual(list(renderer.OUT.rglob('*.tmp')),[])
            finally:
                renderer.ROOT,renderer.OUT=original_root,original_out

    def test_cover_instructions_do_not_consume_real_question_ids(self):
        from tcte_auto import extract_questions
        cover='1. 請先核對考試科目與報考類別是否相符。\n2. 本試題共50題，每題2分，共100分，請依題號順序作答。\n3. 本試題均為單一選擇題，每題都有 (A)、(B)、(C)、(D)四個選項。'
        real='1. The actual first fixture question is here. (A) first (B) second (C) third (D) fourth\n2. The actual second fixture question is here. (A) first (B) second (C) third (D) fourth\n3. The actual third fixture question is here. (A) first (B) second (C) third (D) fourth'
        qs=extract_questions([cover,real],92,'00-E','https://web1.tcte.edu.tw/EXAM/092_4y/fixture.pdf',[])
        self.assertEqual([q['number'] for q in qs],[1,2,3]);self.assertTrue(all(q['page']==2 for q in qs))
        self.assertTrue(all(q['question'].startswith('The actual') for q in qs))

    def test_teaching_generator_rejects_unreviewed_question(self):
        from tcte_teaching import eligible
        q=sample();q['questionVerified']=False;q['teachingVerified']=False
        self.assertFalse(eligible(q))

if __name__=='__main__':unittest.main()
