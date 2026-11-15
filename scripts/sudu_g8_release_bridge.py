"""Authenticated private G1-G7 staging, exact-byte G8, then native promotion.

No CLI option can grant E/G6/G8 trust. Trust entries must already be vetted
and pinned at protected main. Raw G6 transport evidence stays outside git.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, shutil, sqlite3, subprocess, tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from scripts import sudu_verified_publish as pub
from scripts import sudu_independent_review_gate as gate

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='AUTHENTICATED_G8_BRIDGE_V1'
MATRIX=tuple((w,h,t) for w,h in [(360,800),(375,812),(390,844),(412,915),(430,932),(768,1024),(1024,768),(1440,900)] for t in ('light','dark'))
FORMAL_WORKFLOW='.github/workflows/work-authenticated-g8-formal-20261115.yml'
CODE=(FORMAL_WORKFLOW,'scripts/sudu_verified_publish.py','scripts/sudu_independent_review_gate.py','scripts/sudu_g8_release_bridge.py','scripts/build.py','tests/sudu_g8_release_bridge_browser.cjs','sudu/v4-115-multisubject-review-demo.html','sudu/verified-questions-runtime.js')
SHA=re.compile(r'^[0-9a-f]{64}$')
class Hold(ValueError): pass

def require(ok,why):
 if not ok: raise Hold('G8_BRIDGE_HOLD: '+why)
def canonical(x): return gate.canonical(x)
def sha(b): return gate.digest(b)
def serialized(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def git(root,*args): return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
def safe(root,rel):
 require(isinstance(rel,str) and rel and not Path(rel).is_absolute() and '..' not in Path(rel).parts and '\\' not in rel,'unsafe relative evidence path')
 root=Path(root).resolve();f=root/rel
 require(f.is_file() and f.resolve().is_relative_to(root),'missing/escaping evidence')
 require(not any(p.is_symlink() for p in (f,*f.parents) if p!=root.parent),'symlink evidence')
 return f

def read(root,rel):
 b=safe(root,rel).read_bytes();d=json.loads(b,object_pairs_hook=gate._no_duplicate_keys)
 require(isinstance(d,dict),'evidence must be object');return d,b

def private_new(path,source):
 path=Path(path).absolute();tmp=Path(tempfile.gettempdir()).resolve()
 require(not path.exists() and not path.is_symlink(),'destination exists')
 require(not any(p.is_symlink() for p in path.parents),'symlink destination')
 resolved=path.resolve()
 require(resolved.is_relative_to(tmp) and resolved!=tmp and path.name.startswith('sudu-g8-'),'isolated OS-temp destination required')
 require(not resolved.is_relative_to(ROOT.resolve()) and not resolved.is_relative_to(Path(source).resolve()),'destination must be outside source/code')
 return path

def put(root,rel,b):
 p=Path(root)/rel;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 with p.open('xb') as f:f.write(b)
 p.chmod(0o600)

def trusted_policy():
 p=gate.policy_from_trusted_main()
 require(isinstance(p,dict) and p.get('reviewMode')=='DISTINCT_AI_CONTENT_RECEIPT_V1' and p.get('requireHumanTeacher') is False,'V1 protected policy required')
 require(gate._ai_registry_exactly_matches_protected_main_policy(p),'policy must equal actual protected-main policy')
 return p

def code_bindings():
 result={}
 paths=set(CODE)
 for rel in git(ROOT,'ls-tree','-r','--name-only','HEAD').splitlines():
  f=Path(rel)
  if (len(f.parts)==1 and f.suffix.lower() in ('.html','.htm')) or (f.parts[0]=='sudu' and len(f.parts)==2 and f.suffix.lower() in ('.html','.htm','.js','.css')) or (f.parts[0]=='assets' and f.suffix.lower() in ('.js','.css')):paths.add(rel)
 for p in sorted(paths):
  b=safe(ROOT,p).read_bytes();oid=gate.blob_oid(b)
  require(git(ROOT,'rev-parse','HEAD:'+p)==oid,'code must match exact committed Blob')
  result[p]=oid
 return result
def authorization(p,qid):
 e=(p.get('trustedAiReviewReceipts') or {}).get(qid);g=(p.get('trustedG6Receipts') or {}).get(qid)
 require(isinstance(e,dict) and isinstance(g,dict),'protected E and G6 receipts required')
 return sha(canonical({'E':e,'G6':g}))

def g6_verified(p,source,audit,q,revision,private_evidence):
 require(not Path(private_evidence).resolve().is_relative_to(Path(source).resolve()) and not Path(private_evidence).resolve().is_relative_to(ROOT.resolve()),'raw G6 must stay outside git')
 require(Path(private_evidence).stat().st_mode & 0o077 == 0,'raw G6 evidence directory must be private')
 d,b=read(source,audit['evidence']['blind']);entry=(p.get('trustedG6Receipts') or {}).get(q['questionId'])
 require(isinstance(entry,dict) and entry.get('evidenceGitBlobSha')==gate.blob_oid(b),'protected G6 evidence Blob required')
 require(d.get('attemptIndex')==1 and d.get('automaticRetries')==0,'actual first attempt without retries required')
 from datetime import datetime,timezone
 require(gate._time(d.get('startedAt'))<=gate._time(d.get('completedAt'))<=datetime.now(timezone.utc),'G6 real UTC chronology')
 require(d.get('questionRevision')==revision and d.get('webpSha256')==pub.image_sha(q),'G6 material mismatch')
 require(d.get('officialAnswerHiddenDuringSolve') is True and d.get('solvedWithoutOfficialAnswer') is True and 'officialAnswer' not in d and 'officialPdfSha256' not in d,'G6 blind separation')
 require(d.get('answer')==q.get('officialFinalAnswer') and pub.good(d.get('blindReasoning')),'G7 answer agreement/reasoning')
 for field in ('provider','model','executionId','operatorSessionId','reviewerSessionId','sourceCommit','modelInputSha256','rawRequestSha256','rawResponseSha256'):
  require(isinstance(d.get(field),str) and d[field] not in ('UNVERIFIED','NOT_EXECUTED') and entry.get(field)==d[field],'G6 actual '+field+' not pinned')
 for field in ('modelInputSha256','rawRequestSha256','rawResponseSha256'):require(SHA.fullmatch(d[field]),'G6 hash format')
 require(gate.HEX40.fullmatch(d['sourceCommit']),'G6 source commit')
 e=p['trustedAiReviewReceipts'][q['questionId']]
 require(d['operatorSessionId'] not in (d['reviewerSessionId'],e.get('sourceAuthorSessionId'),e.get('reviewerSessionId')),'independent G6 operator required')
 require(entry.get('firstAnswer')==d['answer'] and entry.get('reasoningSha256')==sha(d['blindReasoning'].encode()),'G7 first-answer binding')
 for flag in ('isolationVerified','firstAttemptVerified','requestContainsOnlyFrozenSource','noAutomaticRetry','g7ComparisonVerified'):
  require(entry.get(flag) is True,'G6/G7 owner-verified '+flag+' required')
 for name in ('request','response','modelInput'):
  rel=d.get(name+'Path');raw=safe(private_evidence,rel).read_bytes();field={'request':'rawRequestSha256','response':'rawResponseSha256','modelInput':'modelInputSha256'}[name]
  require(sha(raw)==d[field],'private first '+name+' bytes changed')
 return d

def non_ui(source,qid,audit_rel,private_evidence):
 source=Path(source).resolve();commit=git(source,'rev-parse','HEAD')
 require(gate.HEX40.fullmatch(commit) and not git(source,'status','--porcelain','--untracked-files=no'),'clean exact source checkout required')
 require(pub.QID.fullmatch(qid) and qid!='114-00-E-12','valid QID required; E12 remains separate HOLD')
 year=int(qid[:3]);base=f'sudu/data/processed/{year}/';bank,_=read(source,base+'questions.json');manifest,_=read(source,base+'webp-manifest.json');inv,_=read(source,base+'inventory.json')
 qs=bank['questions'];items=manifest['items'];by={q['questionId']:q for q in qs};assets={m['questionId']:m for m in items}
 require(len(qs)==len(items)==len(by)==len(assets)==205 and set(by)==set(assets),'205 source/manifest unique IDs')
 q=copy.deepcopy(by[qid]);m=assets[qid];identity=pub.stable(q,year);require(identity is not None,'source identity')
 dbpath=safe(source,base+'question-bank.sqlite3')
 require(pub.digest(dbpath.read_bytes())==inv['sqlite']['dbSha256'] and pub.digest(safe(source,base+'questions.json').read_bytes())==inv['sqlite']['sourceQuestionsSha256'],'inventory actual DB/bank hashes')
 with sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True) as db:
  require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'SQLite integrity')
  db.row_factory=sqlite3.Row;rows=list(db.execute('SELECT * FROM questions'));require(len(rows)==205,'SQLite205')
  require(len(db.execute('PRAGMA table_info(questions)').fetchall())==(7 if year==114 else 14),'SQLite original schema')
  for row in rows:
   value=by[row['question_id']];payload=row['payload_json']
   require(json.loads(payload)==value and sha(payload.encode())==row['payload_sha256'],'SQLite canonical payload/SHA')
   projections={'schema_version':'schemaVersion','answer_matched':'answerMatched','year':'year','paper_code':'paperCode','original_number':'originalQuestionNumber','subject':'subject','question':'question','answer':'answer','answer_verified':'answerVerified','question_verified':'questionVerified','review_status':'reviewStatus','shared_material_id':'sharedMaterialId'}
   for col,key in projections.items():
    if col in row.keys():
     expected=value.get(key);expected=int(expected is True) if col in ('answer_matched','answer_verified','question_verified') else expected
     require(row[col]==expected,'SQLite denormalized '+col)
 audit,audit_raw=read(source,audit_rel)
 require(git(source,'rev-parse','HEAD:'+audit_rel)==gate.blob_oid(audit_raw),'audit must belong to frozen commit')
 require(audit.get('schemaVersion')==1 and audit.get('status')=='G1_G7_REVIEWED_PENDING_G8' and audit.get('questionId')==qid and audit.get('year')==year,'typed non-UI audit required')
 shared={x['sharedMaterialId']:x for x in manifest.get('sharedMaterialCrops',[])}
 require(not pub.shared_material_ids(q),'shared-material student renderer needs a separate reviewed contract; HOLD')
 certified=pub.certified_visual_assets(source,q,m,shared);require(certified is not None and pub.image_proof(q,m,shared,source),'G1 original and shared images')
 revision=pub.text_revision(q,m['sha256'],source)
 require(pub.source_proof(q,True,True,revision)==(True,True) and q.get('answerMatched') is True and q.get('officialFinalAnswer')==q.get('answer'),'native source/final answer')
 docs={};raws={}
 for kind in ('ocr','official','blind','teaching'):
  rel=audit['evidence'][kind];d,b=read(source,rel);loaded=pub.review_document(source,year,rel,qid)
  require(git(source,'rev-parse','HEAD:'+rel)==gate.blob_oid(b),'issuer must belong to frozen commit')
  require(loaded is not None and loaded[1]==sha(b),'native '+kind+' issuer');docs[kind]=d;raws[kind]=b
 o,off,t=docs['ocr'],docs['official'],docs['teaching']
 require(o.get('questionRevision')==revision and o.get('webpSha256')==m['sha256'] and o.get('question')==q['question'] and o.get('options')==q['options'] and o.get('visualTextCompared') is True,'G2 exact text/image')
 require(off.get('officialPdfSha256')==pub.pdf_sha(q,'answer') and off.get('finalAnswer')==q['answer'] and off.get('officialPage')==pub.official_source_index(year) and off.get('correctionNoticeReviewed') is True and pub.official_notice_scope_certified(source,year,q,off),'G3 official final/correction scope')
 require(t.get('questionRevision')==revision and t.get('allFourOptionsReviewed') is True and t.get('calculationReviewed') is True and pub.teaching_content_complete(t.get('content'),identity[1],q['answer']),'complete native G5 content')
 p=trusted_policy();require(qid in p.get('trustedAiReviewReceipts',{}),'protected E receipt absent')
 approved,reason=gate.certified(source,audit,q,m,t,raws['teaching'],policy=p)
 require(approved and reason!='exact_five_historical_students_preserved','genuine distinct E: '+reason)
 g6=g6_verified(p,source,audit,q,revision,private_evidence)
 q['teaching']=t['content']
 row=pub.public_question(q,year,identity[1],f'data/approved/webp/{year}/{qid}.webp')
 return {'qid':qid,'year':year,'sourceCommit':commit,'sourceRevision':revision,'webpSha256':m['sha256'],'teachingDigest':sha(canonical(t['content'])),'teachingEvidenceSha256':sha(raws['teaching']),'officialEvidenceSha256':sha(raws['official']),'authorizationSha256':authorization(p,qid),'auditPath':audit_rel,'audit':audit,'question':q,'row':row,'rowSha256':sha(canonical(row)),'imageAssets':certified,'codeBindings':code_bindings(),'codeCommit':git(ROOT,'rev-parse','HEAD'),'g6ResponseSha256':g6['rawResponseSha256']}

def stage(source,qid,audit,private_evidence,dest):
 checked=non_ui(source,qid,audit,private_evidence);dest=private_new(dest,source)
 with tempfile.TemporaryDirectory(prefix='sudu-g8-build-') as temporary:
  temp=Path(temporary);native=temp/'native';pub.stage(Path(source),native,checked['sourceCommit'])
  year=checked['year'];rel=f'sudu/data/approved/{year}.json';baseline=safe(native,rel).read_bytes();payload=json.loads(baseline)
  require(qid not in {x['canonicalId'] for x in payload['questions']},'already published QID is not a new admission')
  payload['questions'].append(checked['row']);order={x['questionId']:i for i,x in enumerate(pub.read(Path(source)/f'sudu/data/processed/{year}/questions.json')['questions'])};payload['questions'].sort(key=lambda x:order[x['canonicalId']]);payload['approvedCount']=len(payload['questions']);output=serialized(payload)
  from scripts import build
  build.build(output_dir=temp/'site');shutil.copytree(native/'sudu/data/approved',temp/'site/sudu/data/approved',dirs_exist_ok=True)
  (temp/'site'/rel).write_bytes(output)
  progress=pub.read(temp/'site/sudu/data/approved/progress.json');progress['years'][str(year)]['approvedCount']=payload['approvedCount'];pub.dump(temp/'site/sudu/data/approved/progress.json',progress)
  for image_rel,name,h in checked['imageAssets']:
   f=temp/'site'/f'sudu/data/approved/webp/{year}/{name}.webp';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(safe(source,image_rel).read_bytes());require(sha(f.read_bytes())==h,'staged image race')
  manifest={k:checked[k] for k in ('qid','year','sourceCommit','sourceRevision','webpSha256','teachingDigest','teachingEvidenceSha256','officialEvidenceSha256','authorizationSha256','auditPath','rowSha256','codeBindings','codeCommit','g6ResponseSha256')}
  manifest['siteFiles']={f.relative_to(temp/'site').as_posix():sha(f.read_bytes()) for f in (temp/'site').rglob('*') if f.is_file()}
  manifest.update(schema=SCHEMA,status='PRE_G8_ONLY',pagesEligible=False,baselineSha256=sha(baseline),payloadPath=rel,payloadSha256=sha(output))
  # Manifest excludes any self-asserted UI PASS, private raw G6 or credential.
  (temp/'stage.json').write_bytes(serialized(manifest));(temp/'row.json').write_bytes(serialized(checked['row']))
  os.chmod(temp,0o700);shutil.copytree(temp,dest)
  for f in dest.rglob('*'):
   if f.is_dir():f.chmod(0o700)
   else:f.chmod(0o600)
 return {'status':'PRE_G8_ONLY','stageManifestSha256':sha(safe(dest,'stage.json').read_bytes()),'payloadSha256':manifest['payloadSha256'],'qid':qid,'pagesEligible':False}

def validate_stage(source,stage_root,private_evidence):
 manifest,b=read(stage_root,'stage.json');require(manifest.get('schema')==SCHEMA and manifest.get('status')=='PRE_G8_ONLY' and manifest.get('pagesEligible') is False,'not authenticated staging type')
 checked=non_ui(source,manifest['qid'],manifest['auditPath'],private_evidence)
 for field in ('qid','year','sourceCommit','sourceRevision','webpSha256','teachingDigest','teachingEvidenceSha256','officialEvidenceSha256','authorizationSha256','rowSha256','codeBindings','g6ResponseSha256'):require(manifest.get(field)==checked[field],'stale stage '+field)
 site=Path(stage_root)/'site';actual={f.relative_to(site).as_posix():sha(safe(site,f.relative_to(site).as_posix()).read_bytes()) for f in site.rglob('*') if f.is_file()}
 require(manifest.get('siteFiles')==actual,'staged HTML/runtime/assets changed')
 payload=safe(Path(stage_root)/'site',manifest['payloadPath']).read_bytes();require(sha(payload)==manifest['payloadSha256'],'staged payload bytes changed')
 require(sha(canonical(next(x for x in json.loads(payload)['questions'] if x['canonicalId']==manifest['qid'])))==checked['rowSha256'],'native serialized row changed')
 require(safe(stage_root,'row.json').read_bytes()==serialized(checked['row']),'expected original row changed')
 return manifest,checked,sha(b)

def github(path):
 require(re.fullmatch(r'/actions/(?:runs|jobs|artifacts)/[1-9][0-9]*',path) is not None,'unsupported Actions endpoint')
 headers={'Accept':'application/vnd.github+json','User-Agent':'7581707-G8-bridge'}
 if os.environ.get('GITHUB_TOKEN'):headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
 with urlopen(Request('https://api.github.com/repos/'+gate.REPO+path,headers=headers),timeout=15) as response:return json.loads(response.read(),object_pairs_hook=gate._no_duplicate_keys)

def actions_provenance(entry):
 run=github('/actions/runs/'+str(entry['runId']));job=github('/actions/jobs/'+str(entry['jobId']));artifact=github('/actions/artifacts/'+str(entry['artifactId']))
 require(str(run.get('path','')).split('@')[0]==FORMAL_WORKFLOW and run.get('event')=='workflow_dispatch' and run.get('head_branch')=='main','protected formal workflow required')
 require(job.get('name')=='formal_g8','actual formal Chromium job required')
 require(run.get('head_sha')==entry['codeCommit'] and run.get('status')=='completed' and run.get('conclusion')=='success','successful exact-code Actions run required')
 require(job.get('run_id')==entry['runId'] and job.get('head_sha')==entry['codeCommit'] and job.get('conclusion')=='success','successful formal job required')
 require(artifact.get('expired') is False and artifact.get('digest')=='sha256:'+entry['artifactSha256'] and (artifact.get('workflow_run') or {}).get('id')==entry['runId'],'actual retained G8 artifact digest required')

def g8_authorized(manifest,manifest_sha,report_raw):
 p=trusted_policy();entry=(p.get('trustedG8Receipts') or {}).get(manifest['qid'])
 require(isinstance(entry,dict),'owner-registered protected G8 receipt required')
 for k,v in {'stageManifestSha256':manifest_sha,'payloadSha256':manifest['payloadSha256'],'rowSha256':manifest['rowSha256'],'authorizationSha256':manifest['authorizationSha256'],'reportSha256':sha(report_raw),'codeBindings':manifest['codeBindings']}.items():require(entry.get(k)==v,'protected G8 '+k+' mismatch')
 require(authorization(p,manifest['qid'])==manifest['authorizationSha256'],'E/G6 authorization changed')
 require(entry.get('codeCommit')==manifest['codeCommit'],'formal code execution commit')
 report=json.loads(report_raw);require(report.get('runId')==entry.get('runId'),'formal report actual run')
 actions_provenance(entry);return entry

def verify_report(manifest,manifest_sha,report_root):
 report,b=read(report_root,'report.json')
 require(report.get('schema')==SCHEMA and report.get('status')=='FORMAL_G8' and report.get('stageManifestSha256')==manifest_sha and report.get('payloadSha256')==manifest['payloadSha256'] and report.get('codeCommit')==manifest['codeCommit'] and report.get('codeBindings')==manifest['codeBindings'],'formal report version/bytes')
 from datetime import datetime,timezone
 require(gate._time(report.get('completedAt'))<=datetime.now(timezone.utc),'formal UTC completion')
 require(report.get('errors')==[] and len(report.get('cases',[]))==16,'all16 browser cases required')
 found=set()
 for case in report['cases']:
  key=(case.get('width'),case.get('height'),case.get('theme'));require(key in MATRIX and key not in found and case.get('result')=='PASS','full unique16 matrix');found.add(key)
  require(case.get('stageManifestSha256')==manifest_sha and case.get('payloadSha256')==manifest['payloadSha256'],'case binding')
  raw=safe(report_root,case.get('screenshot')).read_bytes();require(sha(raw)==case.get('screenshotSha256'),'screenshot bytes changed')
  from PIL import Image
  import io
  with Image.open(io.BytesIO(raw)) as im:im.load();require(im.format=='PNG' and im.size==key[:2],'actual PNG viewport dimensions')
 require(found==set(MATRIX),'matrix incomplete')
 return report,b

def verify_archive(report_root,entry,report):
 import zipfile
 archive=safe(report_root,'artifact.zip');require(sha(archive.read_bytes())==entry['artifactSha256'],'actual artifact archive bytes')
 with zipfile.ZipFile(archive) as z:
  names=z.namelist();require(len(names)==len(set(names)),'duplicate artifact members')
  for name in ['report.json']+[case['screenshot'] for case in report['cases']]:
   require(name in names and z.getinfo(name).file_size<=20_000_000,'missing/oversize artifact member')
   require(z.read(name)==safe(report_root,name).read_bytes(),'report/screenshot not from authentic artifact')

def verify_native_ui_receipt(source,q,item,audit,ui):
 require(ui.get('g8BridgeSchema')==SCHEMA,'typed bridge UI receipt')
 p=trusted_policy();entry=(p.get('trustedG8Receipts') or {}).get(q['questionId']);require(isinstance(entry,dict),'protected G8 receipt absent')
 row=pub.public_question(q,q['year'],pub.stable(q,q['year'])[1],f"data/approved/webp/{q['year']}/{q['questionId']}.webp")
 require(entry.get('rowSha256')==ui.get('testedPublicQuestionSha256')==sha(canonical(row)),'UI/native public row differs')
 require(entry.get('codeBindings')==ui.get('codeBindings')==code_bindings(),'publisher/renderer/code changed')
 require(entry.get('authorizationSha256')==ui.get('authorizationSha256')==authorization(p,q['questionId']),'E/G6 changed')
 require(entry.get('reportSha256')==ui.get('formalReportSha256') and entry.get('payloadSha256')==ui.get('testedPayloadSha256'),'registered G8 report/payload')
 blind,raw=read(source,audit['evidence']['blind']);first=(p.get('trustedG6Receipts') or {}).get(q['questionId'])
 require(isinstance(first,dict) and first.get('evidenceGitBlobSha')==gate.blob_oid(raw),'current native G6 issuer not the owner-approved original')
 require(blind.get('questionRevision')==pub.text_revision(q,item['sha256'],source) and blind.get('webpSha256')==item['sha256'] and blind.get('answer')==q['officialFinalAnswer'],'native G6 material/answer changed')
 actions_provenance(entry)

def promote(source,stage_root,private_evidence,report_root,dest):
 manifest,checked,manifest_sha=validate_stage(source,stage_root,private_evidence);report,report_raw=verify_report(manifest,manifest_sha,report_root);entry=g8_authorized(manifest,manifest_sha,report_raw)
 verify_archive(report_root,entry,report)
 dest=private_new(dest,source);year=manifest['year'];qid=manifest['qid']
 ui_rel=f'sudu/data/processed/{year}/review-evidence/{qid}-ui-g8-bridge.json'
 ui={'schemaVersion':1,'year':year,'questionId':qid,'g8BridgeSchema':SCHEMA,'testedQuestionRevision':manifest['sourceRevision'],'testedTeachingDigest':manifest['teachingDigest'],'testedPublicQuestionSha256':manifest['rowSha256'],'testedPayloadSha256':manifest['payloadSha256'],'codeBindings':manifest['codeBindings'],'authorizationSha256':manifest['authorizationSha256'],'formalReportSha256':sha(report_raw),'browserSmokePassed':True,'rwdPassed':True,'verifiedYearQaMode':True,'reviewer':'Owner-registered actual formal Chromium Actions receipt','reviewedAt':report['completedAt'],'ciRunUrl':f"https://github.com/{gate.REPO}/actions/runs/{entry['runId']}"}
 with tempfile.TemporaryDirectory(prefix='sudu-g8-promote-') as temporary:
  temp=Path(temporary);assembled=temp/'source'
  for y in (114,115):shutil.copytree(Path(source)/f'sudu/data/processed/{y}',assembled/f'sudu/data/processed/{y}')
  pub.dump(assembled/ui_rel,ui)
  audit=copy.deepcopy(checked['audit']);audit.update(status='STUDENT_QA_APPROVED',questionBeforeReview=checked['question']['question'],optionsBeforeReview=checked['question']['options'],webpSha256=manifest['webpSha256'],officialPdfSha256=pub.pdf_sha(checked['question'],'answer'),questionPdfSha256=pub.pdf_sha(checked['question'],'question'),originalAnswerCandidate=checked['question']['answer']);audit['evidence']['ui']=ui_rel
  batches=pub.reviewed_student_batches(assembled,year);batches[qid]=audit
  batch_rel=f'sudu/data/processed/{year}/verified-student-batch.json';pub.dump(assembled/batch_rel,{'schemaVersion':1,'year':year,'items':list(batches.values())})
  native=temp/'native';pub.stage(assembled,native,manifest['sourceCommit']);pub.site_check(native)
  require(safe(native,manifest['payloadPath']).read_bytes()==safe(Path(stage_root)/'site',manifest['payloadPath']).read_bytes(),'native final publisher differs from browser-tested bytes')
  dest.mkdir(mode=0o700);shutil.copytree(native/'sudu/data/approved',dest/'sudu/data/approved')
  put(dest,'qa-evidence/'+ui_rel,safe(assembled,ui_rel).read_bytes());put(dest,'qa-evidence/'+batch_rel,safe(assembled,batch_rel).read_bytes())
 return {'status':'PROMOTION_CANDIDATE_NOT_DEPLOYED','qid':qid,'payloadSha256':manifest['payloadSha256'],'requiresProtectedPRAndPagesVerifyLive':True}

def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=('stage','verify-stage','promote'));a.add_argument('--source',type=Path,required=True);a.add_argument('--private-evidence',type=Path,required=True);a.add_argument('--dest',type=Path);a.add_argument('--qid');a.add_argument('--audit');a.add_argument('--stage',type=Path);a.add_argument('--report',type=Path);v=a.parse_args()
 try:
  if v.command=='stage':result=stage(v.source,v.qid,v.audit,v.private_evidence,v.dest)
  elif v.command=='verify-stage':
   m,_,h=validate_stage(v.source,v.stage,v.private_evidence);result={'status':'PRE_G8_ONLY','stageManifestSha256':h,'payloadSha256':m['payloadSha256']}
  else:result=promote(v.source,v.stage,v.private_evidence,v.report,v.dest)
  print(json.dumps(result,sort_keys=True))
 except (OSError,ValueError,TypeError,KeyError,AttributeError,subprocess.SubprocessError) as error:
  a.exit(2,str(error)+'\n' if isinstance(error,Hold) else 'G8_BRIDGE_HOLD: invalid or unavailable evidence\n')
if __name__=='__main__':main()
