"""Source-pinned draft checks and mathematical recomputation; no release approval."""
import hashlib
import itertools
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sudu/teaching-candidates/114-115-20261025'
def digest(value):
 return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class Lessons(unittest.TestCase):
 def test_six_exact_lessons_hash_options_and_isolation(self):
  batch=json.loads((BASE/'batch.json').read_text())
  self.assertEqual(len(batch['items']),6)
  for item in batch['items']:
   path=ROOT/item['path'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['fileSha256'])
   q=json.loads(path.read_text());t=q['teaching']
   self.assertFalse(q['studentReleaseApproved']);self.assertFalse(q['deploy'])
   self.assertEqual(digest(t),item['teachingSha256'])
   self.assertEqual(q['review']['externalIndependentReview'],'PENDING')
   self.assertFalse(q['review']['newBlindSolveClaimed'])
   self.assertEqual(len(q['options']),4)
   self.assertEqual([k for k,v in t['optionExplanations'].items() if v['isCorrect']],[t['examCalculation']['option']])
   for v in t['optionExplanations'].values():
    self.assertTrue(all(v.get(k) for k in ('teacher','elementary','reason')))
   self.assertTrue(all(t['examCalculation'].get(k) for k in ('given','formulaUse','substitution','steps','result','unit')))
 def test20_sine_ratio(self):
  x=100*math.sin(math.radians(75))/math.sin(math.radians(45))
  self.assertAlmostEqual(x,50*(math.sqrt(3)+1))
 def test21_both_roots_and_all_options(self):
  roots=[x for x in range(1,20) if 8**2+x*x-2*8*x*0.5==49]
  self.assertEqual(roots,[3,5]);self.assertEqual([x for x in roots if x>4],[5])
  self.assertEqual([x for x in (5,4.75,4.5,4.25) if abs(x*x-8*x+15)<1e-10],[5])
 def test22_enumerated_not_formula_only(self):
  arrangements=[x for x in itertools.product((0,1),repeat=5) if any(x)]
  self.assertEqual(len(arrangements),31)
 def test23_one_discounted_person_both_plans(self):
  options=[32000,33000,34000,35000]
  from fractions import Fraction
  def totals(x):return (2*x-3000,(1+Fraction(4,5))*(x+2000))
  self.assertEqual([x for x in options if totals(x)[0]==totals(x)[1]],[33000])
  self.assertEqual(totals(33000),(63000,63000))
  q=json.loads((BASE/'115-00-MB-23.json').read_text())
  self.assertFalse(q['review']['hasRequiredSourceTable'])
  self.assertIn('SOURCE_2X3_TABLE_MUST_USE_PR24_REVISION_NOT_TEXT_ONLY_HASH',q['blockers'])
 def test24_ceiling_and_power_bounds(self):
  c=math.ceil(110/8);d=math.ceil(math.log(3)/math.log(1.08))
  self.assertEqual((c,d),(14,15));self.assertLess(1.08**14,3);self.assertGreater(1.08**15,3)
 def test25_circle_and_all_distractors(self):
  h=4;r2=2;a=r2-16;self.assertEqual(h+a,-10)
  implied_r2={v:v-h+16 for v in (-59,-16,-10,10)}
  self.assertEqual(implied_r2,{-59:-47,-16:-4,-10:2,10:22})
if __name__=='__main__':unittest.main()
