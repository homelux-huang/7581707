import copy,json,unittest
from pathlib import Path
from scripts import sudu_independent_review_gate as g
class ImmutableBaseline(unittest.TestCase):
 def setUp(self):
  self.policy=json.loads((Path(__file__).resolve().parents[1]/'sudu/release-governance/independent-review-policy.json').read_text())
 def test_all_five_original_rows_and_no_sixth(self):
  rows=self.policy['legacyAlreadyPublished'];self.assertTrue(g._legacy_five_registry_is_original(rows))
  for qid,row in rows.items():
   for key in row:
    changed=copy.deepcopy(rows);changed[qid][key]=114 if key=='year' else 'f'*64
    self.assertFalse(g._legacy_five_registry_is_original(changed),(qid,key))
  changed=copy.deepcopy(rows);changed['115-09-2-34']=dict(next(iter(rows.values())))
  self.assertFalse(g._legacy_five_registry_is_original(changed))
 def test_removed_and_wrong_types(self):
  rows=copy.deepcopy(self.policy['legacyAlreadyPublished']);rows.pop('115-00-MB-05')
  for x in (rows,None,[],{},'true'):self.assertFalse(g._legacy_five_registry_is_original(x))
 def test_all_role_spellings_without_substring_forgery(self):
  for text in ('RETURN Role E report','RETURN ROLE=E report','RETURN role: E report','RETURN role e report'):
   self.assertTrue(g._has_role_e_token(text),text)
  for text in ('RETURN Role Evil report','RETURN parole E','RETURN role Elementary','RETURN troll E','RETURN'):self.assertFalse(g._has_role_e_token(text),text)
if __name__=='__main__':unittest.main()
