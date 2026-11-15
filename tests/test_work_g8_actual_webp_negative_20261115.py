"""TEST C: actual frozen MB20-v5/MB23-table bytes; SYNTHETIC unit authority.

No genuine G1-G7 admission, provider execution, browser PASS, trust receipt or
promotion. Fixtures are private OS-temp and never uploaded. Native serializer,
full public build and stage verifier are real. The complete non_ui gate and
authority lookup boundaries are mocked; original material pins are checked
separately so this never establishes real G1-G7 admission.
"""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from scripts import sudu_g8_release_bridge as b
from scripts import sudu_independent_review_gate as gate
from scripts import sudu_verified_publish as pub

FROZEN = '3d7645b9b8c83bd09348115118920501823b3c27'
POLICY_BLOB = 'c77ee2ec8ca1381388fbbbe6bd36e679750678eb'
PINS = {
 '115-00-MB-20': ('webp-v5','20261110','f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf','2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c','2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d'),
 '115-00-MB-23': ('webp-v2','20261110','2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51','9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4','13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6'),
}

class ActualWebpNegativeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  raw=os.environ.get('WORK_G8_FROZEN_SOURCE')
  if not raw:raise unittest.SkipTest('requires explicit frozen source checkout; no substitute assets')
  cls.source=Path(raw).resolve()
  if b.git(cls.source,'rev-parse','HEAD')!=FROZEN:raise AssertionError('wrong TEST C source commit')
  if b.git(cls.source,'status','--porcelain'):raise AssertionError('TEST C source must be unchanged')
  policy_raw=gate.POLICY.read_bytes()
  if gate.blob_oid(policy_raw)!=POLICY_BLOB:raise AssertionError('policy changed; refresh expected state without inferring trust')
  cls.policy=json.loads(policy_raw)
  if cls.policy['trustedAiReviewReceipts']!={}:raise AssertionError('real trust must remain absent for this negative test')
  base=cls.source/'sudu/data/processed/115'
  bank=json.loads((base/'questions.json').read_bytes());manifest=json.loads((base/'webp-manifest.json').read_bytes())
  if len(bank['questions'])!=205 or len({q['questionId'] for q in bank['questions']})!=205:raise AssertionError('205 source integrity')
  cls.records={}
  for qid,(variant,date,image_sha,revision,teaching_digest) in PINS.items():
   q=copy.deepcopy(next(q for q in bank['questions'] if q['questionId']==qid));m=next(m for m in manifest['items'] if m['questionId']==qid)
   image_rel=f'sudu/data/processed/115/{variant}/00-MB/{qid}.webp';image_raw=(cls.source/image_rel).read_bytes()
   if q['assets']['singleQuestionWebp']!=image_rel or b.sha(image_raw)!=image_sha or m['sha256']!=image_sha:raise AssertionError('original full image mismatch')
   with Image.open(io.BytesIO(image_raw)) as im:
    if im.format!='WEBP':raise AssertionError('original WEBP required')
    im.load()
   paths={kind:f'sudu/data/processed/115/review-evidence/{qid}-{suffix}.json' for kind,suffix in [('ocr',f'ocr-publisher-{date}'),('official',f'official-publisher-{date}'),('teaching','teaching-publisher-20261114')]}
   raws={k:(cls.source/v).read_bytes() for k,v in paths.items()};docs={k:json.loads(v) for k,v in raws.items()}
   if pub.text_revision(q,image_sha,cls.source)!=revision or docs['ocr']['questionRevision']!=revision:raise AssertionError('actual original/table-aware QREV mismatch')
   if b.sha(b.canonical(docs['teaching']['content']))!=teaching_digest:raise AssertionError('actual G5 changed')
   if qid.endswith('-23'):
    table=docs['ocr']['sourceTables'][0]
    if len(table['heading'])!=3 or len(table['rows'])!=2 or any(len(row)!=3 for row in table['rows']):raise AssertionError('original MB23 table incomplete')
   if pub.shared_material_ids(q):raise AssertionError('unexpected separate shared-material contract')
   assets=pub.certified_visual_assets(cls.source,q,m,{})
   if not assets or not pub.image_proof(q,m,{},cls.source):raise AssertionError('original G1 image proof absent')
   real_result=gate.certified(cls.source,{},q,m,docs['teaching'],raws['teaching'],policy=cls.policy)
   if real_result!=(False,'distinct_ai_content_review_missing'):raise AssertionError('real candidate must still HOLD')
   q['teaching']=docs['teaching']['content'];row=pub.public_question(q,115,pub.stable(q,115)[1],f'data/approved/webp/115/{qid}.webp')
   checked={'qid':qid,'year':115,'sourceCommit':FROZEN,'sourceRevision':revision,'webpSha256':image_sha,'teachingDigest':teaching_digest,'teachingEvidenceSha256':b.sha(raws['teaching']),'officialEvidenceSha256':b.sha(raws['official']),
            'authorizationSha256':'0'*64,'auditPath':'SYNTHETIC_UNIT_AUTHORITY_ONLY_NOT_REAL_G1_G7','rowSha256':b.sha(b.canonical(row)),
            'codeBindings':b.code_bindings(),'codeCommit':b.git(b.ROOT,'rev-parse','HEAD'),'g6ResponseSha256':'0'*64,'row':row,'imageAssets':assets}
   cls.records[qid]={'q':q,'m':m,'g5':docs['teaching'],'rawG5':raws['teaching'],'imageRaw':image_raw,'checked':checked}

 def fixture(self,qid):
  temp=tempfile.TemporaryDirectory(prefix='sudu-g8-testc-');self.addCleanup(temp.cleanup)
  root=Path(temp.name);private=root/'unit-private';private.mkdir(mode=0o700);stage=root/'sudu-g8-synthetic-authority'
  checked=copy.deepcopy(self.records[qid]['checked'])
  def authority(source,requested_qid,audit,private_root):
   self.assertEqual(Path(source).resolve(),self.source);self.assertEqual(requested_qid,qid)
   self.assertEqual(audit,'SYNTHETIC_UNIT_AUTHORITY_ONLY_NOT_REAL_G1_G7');return copy.deepcopy(checked)
  # No receipt or provider response is fabricated: only test call-boundary values.
  # The production real authority remains empty and is asserted separately.
  for mocked in [patch.object(b,'non_ui',side_effect=authority),patch.object(b,'trusted_policy',return_value=copy.deepcopy(self.policy)),patch.object(gate,'_ai_registry_exactly_matches_protected_main_policy',return_value=True)]:
   mocked.start();self.addCleanup(mocked.stop)
  with contextlib.redirect_stdout(io.StringIO()):b.stage(self.source,qid,checked['auditPath'],private,stage)
  return stage,private

 def test_actual_original_image_and_real_authority_still_hold(self):
  for qid,record in self.records.items():
   with self.subTest(qid=qid):
    self.assertEqual(b.sha(record['imageRaw']),PINS[qid][2])
    self.assertEqual(gate.certified(self.source,{},record['q'],record['m'],record['g5'],record['rawG5'],policy=self.policy),(False,'distinct_ai_content_review_missing'))

 def test_actual_mb20_v5_and_mb23_webp_swap_with_resealed_map_rejected(self):
  for qid in PINS:
   with self.subTest(qid=qid):
    stage,private=self.fixture(qid);mp=stage/'stage.json';m=json.loads(mp.read_bytes());rel=f'sudu/data/approved/webp/115/{qid}.webp';target=stage/'site'/rel
    self.assertEqual(target.read_bytes(),self.records[qid]['imageRaw'])
    other=next(key for key in PINS if key!=qid);target.write_bytes(self.records[other]['imageRaw'])
    # Valid actual WEBP from the other original question, wrong source identity.
    m['siteFiles'][rel]=b.sha(target.read_bytes());mp.write_bytes(b.serialized(m))
    with self.assertRaisesRegex(b.Hold,'reproducible native'):b.validate_stage(self.source,stage,private)

 def test_actual_source_code_teaching_and_html_blob_binding_changes_rejected(self):
  for qid in PINS:
   with self.subTest(qid=qid):
    stage,private=self.fixture(qid);mp=stage/'stage.json';original=mp.read_bytes()
    for field in ['sourceCommit','codeCommit','teachingDigest','codeBindings']:
     m=json.loads(original)
     if field=='codeBindings':m[field]['sudu/v4-115-multisubject-review-demo.html']='f'*40
     else:m[field]='f'*(64 if field=='teachingDigest' else 40)
     mp.write_bytes(b.serialized(m))
     with self.assertRaisesRegex(b.Hold,'stale stage '+field):b.validate_stage(self.source,stage,private)
    mp.write_bytes(original)

 def test_actual_image_missing_extra_or_symlink_reseal_rejected(self):
  for qid in PINS:
   with self.subTest(qid=qid):
    stage,private=self.fixture(qid);mp=stage/'stage.json';original=mp.read_bytes();m=json.loads(original);rel=f'sudu/data/approved/webp/115/{qid}.webp';target=stage/'site'/rel;raw=target.read_bytes()
    target.unlink();m['siteFiles'].pop(rel);mp.write_bytes(b.serialized(m))
    with self.assertRaisesRegex(b.Hold,'reproducible native'):b.validate_stage(self.source,stage,private)
    target.write_bytes(raw);mp.write_bytes(original)
    extra='sudu/data/approved/webp/115/SYNTHETIC_EXTRA.webp';f=stage/'site'/extra;f.write_bytes(raw);m=json.loads(original);m['siteFiles'][extra]=b.sha(raw);mp.write_bytes(b.serialized(m))
    with self.assertRaisesRegex(b.Hold,'reproducible native'):b.validate_stage(self.source,stage,private)
    f.unlink();mp.write_bytes(original)
    target.unlink();target.symlink_to(self.source/self.records[qid]['q']['assets']['singleQuestionWebp'])
    with self.assertRaises(b.Hold):b.validate_stage(self.source,stage,private)
  self.assertEqual(b.git(self.source,'status','--porcelain'),'')

if __name__=='__main__':unittest.main()
