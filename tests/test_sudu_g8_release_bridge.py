"""SYNTHETIC unit authority only; never real E/G6/G8 or student admission.

Source fixtures, private transport bytes, 16 PNGs and mocked GitHub authority
are intentionally synthetic. No fixture is committed into a policy/approved.
"""
import copy, hashlib, io, json, os, shutil, sqlite3, subprocess, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from scripts import sudu_g8_release_bridge as b
from scripts import sudu_verified_publish as p
from scripts import sudu_independent_review_gate as gate

class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir();self.private=self.root/'private';self.private.mkdir(mode=0o700)
  self.qid='115-00-MB-20';self.prefix='sudu/data/processed/115/';self.reviews=self.prefix+'review-evidence/';self.stage=self.root/'sudu-g8-stage';self.report=self.root/'report';self.report.mkdir()
  self.policy={'schemaVersion':1,'githubRepository':gate.REPO,'reviewMode':'DISTINCT_AI_CONTENT_RECEIPT_V1','requireHumanTeacher':False,'trustedAiReviewReceipts':{self.qid:{'sourceAuthorSessionId':'SYNTHETIC_AUTHOR','reviewerSessionId':'SYNTHETIC_E'}},'trustedG6Receipts':{},'trustedG8Receipts':{}}
  self.teaching={'teacherSummary':'SYNTHETIC teacher','elementarySummary':'SYNTHETIC elementary','memory':'SYNTHETIC memory','concept':'SYNTHETIC concept','extension':'SYNTHETIC reverse check','source':'SYNTHETIC source','optionExplanations':{L:{'teacher':'SYNTHETIC teacher '+L,'elementary':'SYNTHETIC elementary '+L,'reason':'SYNTHETIC reason '+L} for L in 'ABCD'},'hasExamCalculation':False,'calculationReviewed':True,'examCalculation':None}
  image=io.BytesIO();Image.new('RGB',(40,20),'white').save(image,format='WEBP',lossless=True);im=image.getvalue();self.image_sha=b.sha(im)
  for year in (114,115):
   pref=f'sudu/data/processed/{year}/';questions=[];items=[]
   for code,count in [('00-C',40),('00-E',40),('00-MB',25),('09-1',50),('09-2',50)]:
    for n in range(1,count+1):
     qid=f'{year}-{code}-{n:02d}';rel=pref+f'webp-v1/{code}/{qid}.webp';target=qid==self.qid
     q={'schemaVersion':1,'questionId':qid,'year':year,'paperCode':code,'originalQuestionNumber':n,'subject':p.subject_for(year,code,n),'question':'SYNTHETIC question; this is not a real exam','options':['SYNTHETIC option '+L for L in 'ABCD'],'answer':'B','answerMatched':True,'questionVerified':target,'answerVerified':target,'textQaStatus':'PASS' if target else 'PENDING','officialFinalAnswer':'B','officialCorrectionChecked':target,'reviewStatus':'SYNTHETIC','assets':{'singleQuestionWebp':rel},'questionProvenance':{'officialPdfSha256':'a'*64,'pixelSourceSha256':'b'*64,'webpSha256':self.image_sha},'answerProvenance':{'officialPdfSha256':'c'*64}}
     questions.append(q);items.append({'questionId':qid,'qaStatus':'PASS' if target else 'PENDING','output':rel,'sha256':self.image_sha,'visualReviewEvidence':{'reviewedSha256':self.image_sha,'reference':self.reviews+'image.json'}})
   if year==115:
    self.q=next(q for q in questions if q['questionId']==self.qid);self.revision=p.text_revision(self.q,self.image_sha);self.image_rel=self.q['assets']['singleQuestionWebp'];b.put(self.source,self.image_rel,im)
    self.docs={'ocr':{'questionRevision':self.revision,'webpSha256':self.image_sha,'question':self.q['question'],'options':self.q['options'],'visualTextCompared':True},'official':{'officialPdfSha256':'c'*64,'finalAnswer':'B','officialFinalAnswerImageQaPassed':True,'correctionNoticeReviewed':True,'officialPage':p.official_source_index(115),'noObjectionForPaper':True},'teaching':{'questionRevision':self.revision,'allFourOptionsReviewed':True,'calculationReviewed':True,'content':self.teaching},'blind':{'questionRevision':self.revision,'webpSha256':self.image_sha,'officialAnswerHiddenDuringSolve':True,'solvedWithoutOfficialAnswer':True,'answer':'B','blindReasoning':'SYNTHETIC first response reasoning','provider':'SYNTHETIC_PROVIDER','model':'SYNTHETIC_MODEL','executionId':'SYNTHETIC_EXECUTION','operatorSessionId':'SYNTHETIC_OPERATOR','reviewerSessionId':'SYNTHETIC_G7_REVIEWER','sourceCommit':'a'*40,'attemptIndex':1,'automaticRetries':0,'startedAt':'2020-01-01T00:00:00Z','completedAt':'2020-01-01T00:00:01Z'}}
    for kind,data in [('request',b'{"SYNTHETIC_REQUEST":true}'),('response',b'{"SYNTHETIC_RESPONSE":"B"}'),('modelInput',b'SYNTHETIC source only')]:
     (self.private/(kind+'.bin')).write_bytes(data);self.docs['blind'][kind+'Path']=kind+'.bin';field={'request':'rawRequestSha256','response':'rawResponseSha256','modelInput':'modelInputSha256'}[kind];self.docs['blind'][field]=b.sha(data)
    self.audit={'schemaVersion':1,'year':115,'questionId':self.qid,'status':'G1_G7_REVIEWED_PENDING_G8','independentAiContentEvidence':self.reviews+'SYNTHETIC_E.json','evidence':{}}
    for kind,doc in self.docs.items():
     rel=self.reviews+kind+'.json';self.audit['evidence'][kind]=rel;p.dump(self.source/rel,{'schemaVersion':1,'year':115,'questionId':self.qid,'reviewer':'SYNTHETIC','reviewedAt':'2020-01-01',**doc})
    p.dump(self.source/(self.reviews+'image.json'),{'SYNTHETIC_VISUAL':True});next(m for m in items if m['questionId']==self.qid)['visualReviewEvidence']['referenceSha256']=b.sha((self.source/(self.reviews+'image.json')).read_bytes())
    self.q['textQaEvidence']={'reviewer':'SYNTHETIC','reviewedAt':'2020-01-01','evidencePath':self.audit['evidence']['ocr'],'questionRevision':self.revision,'sourceImageSha256':'b'*64}
    self.q['officialFinalQaEvidence']={'reviewer':'SYNTHETIC','reviewedAt':'2020-01-01','evidencePath':self.audit['evidence']['official'],'answerPdfSha256':'c'*64,'finalCorrectionsReviewed':True}
    p.dump(self.source/(pref+'official-confirmation-status.json'),{'schemaVersion':1,'year':115,'source':p.official_source_index(115),'confirmations':{'00-MB':{'officialStatus':'no_objection_submitted','revisionDocumentContent':'not_applicable'}}})
   p.dump(self.source/(pref+'questions.json'),{'schemaVersion':1,'year':year,'questions':questions});p.dump(self.source/(pref+'webp-manifest.json'),{'schemaVersion':1,'year':year,'expected':205,'items':items})
   dbp=self.source/(pref+'question-bank.sqlite3')
   with sqlite3.connect(dbp) as db:
    if year==114:
     db.execute('CREATE TABLE questions(question_id TEXT PRIMARY KEY,year INTEGER,paper_code TEXT,original_number INTEGER,subject TEXT,payload_json TEXT,payload_sha256 TEXT)')
     for q in questions:
      raw=b.canonical(q);db.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?)',(q['questionId'],year,q['paperCode'],q['originalQuestionNumber'],q['subject'],raw.decode(),b.sha(raw)))
    else:
     db.execute('CREATE TABLE questions(question_id TEXT PRIMARY KEY,schema_version INTEGER,year INTEGER,paper_code TEXT,original_number INTEGER,subject TEXT,question TEXT,answer TEXT,answer_matched INTEGER,answer_verified INTEGER,question_verified INTEGER,review_status TEXT,payload_json TEXT,payload_sha256 TEXT)')
     for q in questions:
      raw=b.canonical(q);db.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(q['questionId'],1,year,q['paperCode'],q['originalQuestionNumber'],q['subject'],q['question'],q['answer'],1,int(q['answerVerified']),int(q['questionVerified']),q['reviewStatus'],raw.decode(),b.sha(raw)))
   p.dump(self.source/(pref+'inventory.json'),{'expected':205,'sqlite':{'rows':205,'roundtripPass':True,'dbSha256':b.sha(dbp.read_bytes()),'sourceQuestionsSha256':b.sha((self.source/(pref+'questions.json')).read_bytes())}})
   if year==115:p.dump(self.source/(pref+'VALIDATION.json'),{'sqlite':'SQLITE_ROUNDTRIP_PASS'})
  self.audit_rel=self.reviews+'audit.json';p.dump(self.source/self.audit_rel,self.audit)
  # The frozen input commit precedes the separate answer issuer commit, to
  # avoid an impossible self-referential Git sourceCommit inside that issuer.
  for command in [('init','-q'),('config','user.name','Synthetic Test'),('config','user.email','synthetic@example.invalid'),('add','-A'),('commit','-qm','SYNTHETIC FROZEN INPUT ONLY')]:subprocess.run(['git','-C',str(self.source),*command],check=True,stdout=subprocess.DEVNULL)
  frozen=b.git(self.source,'rev-parse','HEAD')
  self.docs['blind']['sourceCommit']=frozen
  p.dump(self.source/self.audit['evidence']['blind'],{'schemaVersion':1,'year':115,'questionId':self.qid,'reviewer':'SYNTHETIC','reviewedAt':'2020-01-01',**self.docs['blind']})
  blind=b.read(self.source,self.audit['evidence']['blind']);g=copy.deepcopy(blind[0]);g.update(evidenceGitBlobSha=gate.blob_oid(blind[1]),firstAnswer='B',reasoningSha256=b.sha(g['blindReasoning'].encode()))
  for flag in ('isolationVerified','firstAttemptVerified','requestContainsOnlyFrozenSource','noAutomaticRetry','g7ComparisonVerified'):g[flag]=True
  self.policy['trustedG6Receipts'][self.qid]=g
  for command in [('add','-A'),('commit','-qm','SYNTHETIC FIRST SOLVE ISSUER')]:subprocess.run(['git','-C',str(self.source),*command],check=True,stdout=subprocess.DEVNULL)
  self.patches=[patch.object(gate,'_ai_registry_exactly_matches_protected_main_policy',return_value=True),patch.object(b,'trusted_policy',side_effect=lambda:copy.deepcopy(self.policy)),patch.object(gate,'policy_from_trusted_main',side_effect=lambda:copy.deepcopy(self.policy)),patch.object(gate,'certified',return_value=(True,'SYNTHETIC_AUTHORITY_TEST_ONLY')),patch.object(b,'code_bindings',return_value={'SYNTHETIC_CODE':'d'*40})]
  for x in self.patches:x.start();self.addCleanup(x.stop)
  def fake_build(output_dir=None):
   out=Path(output_dir);out.mkdir();b.put(out,'sudu/v4-115-multisubject-review-demo.html',b'SYNTHETIC UNIT UI NOT G8');b.put(out,'sudu/verified-questions-runtime.js',b'SYNTHETIC UNIT RUNTIME')
  x=patch('scripts.build.build',side_effect=fake_build);x.start();self.addCleanup(x.stop)
 def stage_it(self):return b.stage(self.source,self.qid,self.audit_rel,self.private,self.stage)
 def make_report(self):
  m,_,mh=b.validate_stage(self.source,self.stage,self.private);cases=[]
  for w,h,t in b.MATRIX:
   rel=f'{w}-{h}-{t}.png';Image.new('RGB',(w,h),'white').save(self.report/rel);cases.append({'width':w,'height':h,'theme':t,'result':'PASS','screenshot':rel,'screenshotSha256':b.sha((self.report/rel).read_bytes()),'stageManifestSha256':mh,'payloadSha256':m['payloadSha256']})
  report={'schema':b.SCHEMA,'status':'FORMAL_G8','stageManifestSha256':mh,'payloadSha256':m['payloadSha256'],'codeCommit':m['codeCommit'],'codeBindings':m['codeBindings'],'runId':123,'completedAt':'2020-01-01T00:00:02Z','cases':cases,'errors':[]};p.dump(self.report/'report.json',report)
  with zipfile.ZipFile(self.report/'artifact.zip','w') as z:
   for name in ['report.json']+[c['screenshot'] for c in cases]:z.write(self.report/name,name)
  entry={k:m[k] for k in ('payloadSha256','rowSha256','authorizationSha256','codeBindings','codeCommit')};entry.update(stageManifestSha256=mh,reportSha256=b.sha((self.report/'report.json').read_bytes()),runId=123,jobId=456,artifactId=789,artifactSha256=b.sha((self.report/'artifact.zip').read_bytes()))
  self.policy['trustedG8Receipts'][self.qid]=entry;return m,mh,report,entry
 def test_synthetic_stage_is_private_and_requires_no_fake_ui_pass(self):
  result=self.stage_it();self.assertEqual(result['status'],'PRE_G8_ONLY');m,_,_=b.validate_stage(self.source,self.stage,self.private);self.assertFalse(m['pagesEligible']);self.assertNotIn('uiQaStatus',m);self.assertFalse((self.source/'sudu/data/approved').exists())
 def test_missing_E_or_G6_never_stages(self):
  for key in ('trustedAiReviewReceipts','trustedG6Receipts'):
   with self.subTest(key=key):
    saved=self.policy[key];self.policy[key]={}
    try:
     with self.assertRaises(b.Hold):self.stage_it()
     self.assertFalse(self.stage.exists())
    finally:self.policy[key]=saved
 def test_g6_raw_bytes_and_first_attempt_must_match(self):
  (self.private/'response.bin').write_bytes(b'changed')
  with self.assertRaisesRegex(b.Hold,'bytes changed'):self.stage_it()
 def test_staged_payload_HTML_runtime_and_row_tamper_rejected(self):
  self.stage_it()
  for rel in ['site/sudu/data/approved/115.json','site/sudu/v4-115-multisubject-review-demo.html','site/sudu/verified-questions-runtime.js','row.json']:
   with self.subTest(rel=rel):
    f=self.stage/rel;raw=f.read_bytes();f.write_bytes(raw+b'changed')
    try:
     with self.assertRaises(b.Hold):b.validate_stage(self.source,self.stage,self.private)
    finally:f.write_bytes(raw)
 def test_source_code_and_authorization_changes_invalidate_stage(self):
  self.stage_it()
  with patch.object(b,'code_bindings',return_value={'SYNTHETIC_CODE':'e'*40}):
   with self.assertRaisesRegex(b.Hold,'codeBindings'):b.validate_stage(self.source,self.stage,self.private)
  self.policy['trustedG6Receipts'][self.qid]['model']='CHANGED'
  with self.assertRaises(b.Hold):b.validate_stage(self.source,self.stage,self.private)
 def test_cannot_promote_without_registered_G8(self):
  self.stage_it();self.make_report();self.policy['trustedG8Receipts']={}
  with self.assertRaisesRegex(b.Hold,'protected G8'):b.promote(self.source,self.stage,self.private,self.report,self.root/'sudu-g8-promotion')
 def test_16_matrix_missing_duplicate_stale_or_modified_png_rejected(self):
  self.stage_it();m,mh,report,_=self.make_report();f=self.report/'report.json';raw=f.read_bytes()
  for mutate in [lambda d:d['cases'].pop(),lambda d:d['cases'].__setitem__(1,d['cases'][0]),lambda d:d.__setitem__('payloadSha256','0'*64),lambda d:d['cases'][0].__setitem__('screenshotSha256','0'*64)]:
   d=copy.deepcopy(report);mutate(d);p.dump(f,d)
   with self.assertRaises(b.Hold):b.verify_report(m,mh,self.report)
  f.write_bytes(raw);self.assertEqual(b.verify_report(m,mh,self.report)[0]['status'],'FORMAL_G8')
 def test_actual_Actions_provenance_rejects_wrong_run_job_artifact(self):
  self.stage_it();_,_,_,e=self.make_report();run={'head_sha':e['codeCommit'],'status':'completed','conclusion':'success','path':b.FORMAL_WORKFLOW,'event':'workflow_dispatch','head_branch':'main'};job={'name':'formal_g8','run_id':123,'head_sha':e['codeCommit'],'conclusion':'success'};art={'expired':False,'digest':'sha256:'+e['artifactSha256'],'workflow_run':{'id':123}}
  with patch.object(b,'github',side_effect=[run,job,art]):b.actions_provenance(e)
  for index,bad in [(0,{**run,'head_sha':'f'*40}),(1,{**job,'run_id':999}),(2,{**art,'expired':True})]:
   response=[run,job,art];response[index]=bad
   with patch.object(b,'github',side_effect=response):
    with self.assertRaises(b.Hold):b.actions_provenance(e)
 def test_synthetic_only_promotion_uses_real_final_publisher_same_bytes(self):
  self.stage_it();self.make_report();out=self.root/'sudu-g8-promotion'
  with patch.object(b,'actions_provenance'):
   result=b.promote(self.source,self.stage,self.private,self.report,out)
  self.assertEqual(result['status'],'PROMOTION_CANDIDATE_NOT_DEPLOYED');self.assertEqual((out/'sudu/data/approved/115.json').read_bytes(),(self.stage/'site/sudu/data/approved/115.json').read_bytes());self.assertTrue((out/'qa-evidence'/self.prefix/'verified-student-batch.json').exists());self.assertFalse((self.source/'sudu/data/approved').exists())
 def test_untrusted_artifact_and_paths_rejected(self):
  self.stage_it();_,_,report,e=self.make_report();(self.report/'artifact.zip').write_bytes(b'changed')
  with self.assertRaises(b.Hold):b.verify_archive(self.report,e,report)
  with self.assertRaises(b.Hold):b.safe(self.source,'../private/response.bin')
  with self.assertRaises(b.Hold):b.private_new(self.source/'sudu-g8-escape',self.source)
 def test_source_self_UI_PASS_cannot_avoid_new_bridge(self):
  raw=json.loads((b.ROOT/'tests/fixtures/loop-historical-five-original-blobs.json').read_text())['records']['115-00-MB-02']['rawUtf8'].encode();doc=json.loads(raw);rev=doc['questionRevision'];qid='115-00-MB-20'
  q={'questionId':qid,'year':115,'teaching':doc['content']}
  for name,data in [('teaching',raw),('ui',b.serialized({'testedQuestionRevision':rev,'testedTeachingDigest':b.sha(b.canonical(doc['content'])),'browserSmokePassed':True,'rwdPassed':True}))]:
   rel=self.reviews+'new-'+name+'.json';p.dump(self.source/rel,json.loads(data));actual=(self.source/rel).read_bytes();q[name+'QaEvidence']={'evidencePath':rel,'evidenceSha256':b.sha(actual)}
  result=p.final_review_authorized(self.source,q,{'sha256':self.image_sha},None,rev)
  self.assertEqual(result,(False,'authenticated_formal_g8_receipt_required'))
 def test_g6_same_operator_or_retry_and_unknown_chronology_rejected(self):
  rel=self.audit['evidence']['blind'];original=(self.source/rel).read_bytes();old=copy.deepcopy(self.policy['trustedG6Receipts'][self.qid])
  for change in [{'attemptIndex':2},{'automaticRetries':1},{'operatorSessionId':'SYNTHETIC_AUTHOR'},{'startedAt':'UNKNOWN'}]:
   d=json.loads(original);d.update(change);p.dump(self.source/rel,d);raw=(self.source/rel).read_bytes();e=copy.deepcopy(old);e.update({k:v for k,v in change.items() if k in e});e['evidenceGitBlobSha']=gate.blob_oid(raw);self.policy['trustedG6Receipts'][self.qid]=e
   with self.assertRaises((ValueError,TypeError)):b.g6_verified(self.policy,self.source,self.audit,self.q,self.revision,self.private)
  (self.source/rel).write_bytes(original);self.policy['trustedG6Receipts'][self.qid]=old

 def test_frozen_g6_commit_must_be_ancestor_and_preserve_original_blobs(self):
  rel=self.audit['evidence']['blind'];original=(self.source/rel).read_bytes()
  owner=copy.deepcopy(self.policy['trustedG6Receipts'][self.qid])
  try:
   d=json.loads(original);d['sourceCommit']='f'*40;p.dump(self.source/rel,d)
   attestation=copy.deepcopy(owner);attestation['sourceCommit']=d['sourceCommit'];attestation['evidenceGitBlobSha']=gate.blob_oid((self.source/rel).read_bytes())
   self.policy['trustedG6Receipts'][self.qid]=attestation
   with self.assertRaisesRegex(b.Hold,'G6 frozen source commit not an ancestor'):
    b.g6_verified(self.policy,self.source,self.audit,self.q,self.revision,self.private)
  finally:
   (self.source/rel).write_bytes(original);self.policy['trustedG6Receipts'][self.qid]=owner
  ocr=self.source/self.audit['evidence']['ocr'];doc=json.loads(ocr.read_bytes());doc['question']='SYNTHETIC post-freeze alteration';p.dump(ocr,doc)
  for command in [('add','-A'),('commit','-qm','SYNTHETIC POST-FREEZE TAMPER')]:subprocess.run(['git','-C',str(self.source),*command],check=True,stdout=subprocess.DEVNULL)
  with self.assertRaisesRegex(b.Hold,'G6 frozen G2/G3/G5/WebP blob mismatch'):
   b.g6_verified(self.policy,self.source,self.audit,self.q,self.revision,self.private)

 def test_same_code_blobs_but_changed_code_commit_invalidates_stage(self):
  self.stage_it();original=b.git
  def switched(root,*args):
   if Path(root).resolve()==b.ROOT.resolve() and args==('rev-parse','HEAD'):return 'f'*40
   return original(root,*args)
  with patch.object(b,'git',side_effect=switched):
   with self.assertRaisesRegex(b.Hold,'stale stage codeCommit'):
    b.validate_stage(self.source,self.stage,self.private)

 def test_extra_artifact_zip_member_rejected_even_if_digest_matches(self):
  self.stage_it();_,_,report,entry=self.make_report()
  with zipfile.ZipFile(self.report/'artifact.zip','a') as z:z.writestr('SYNTHETIC_UNEXPECTED_EXTRA.txt',b'not allowed')
  entry['artifactSha256']=b.sha((self.report/'artifact.zip').read_bytes())
  with self.assertRaisesRegex(b.Hold,'unexpected artifact ZIP members'):
   b.verify_archive(self.report,entry,report)

 def test_noCLIflag_can_authorize_production_policy(self):
  self.patches[1].stop()
  try:
   from scripts import sudu_g8_archive
   with patch.object(sudu_g8_archive,'current_policy',return_value=('f'*40,self.policy)), patch.object(gate,'_ai_registry_exactly_matches_protected_main_policy',return_value=False):
    with self.assertRaises(b.Hold):b.trusted_policy()
  finally:self.patches[1].start()

if __name__=='__main__':unittest.main()
