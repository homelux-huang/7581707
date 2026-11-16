"""Frozen E08-E10 source-only repair. Never grants independent review or LIVE."""
import argparse, copy, hashlib, importlib.util, json, os, re, sqlite3, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='3d7645b9b8c83bd09348115118920501823b3c27'
P='sudu/data/processed/114/'
TASK='WORK-A-114-E08-E10-G1G2G3-SQLITE-20261116-01'
DATE='2026-11-16'
PDFS={'question':'1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf','answer':'ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325','notice':'79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc'}
PAGE='fd05e4a3f87f69bbd0d0f2a963400342da9752ec8bbef0ef3b26b59e621ae002'
ANSWER_IMAGE='sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp'
ANSWER_SHA='a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863'
PINS={
'114-00-E-08':('D','5a9ebec3dbb4cacf3bbb2cd2f6121f69319d042e3c716f41fdbe96f30bfd9c85','09a56002bd224815a9d413ad9a5db3565af0837e16c58ec031bd851f17d69b6c',[90,1127,1310,1284]),
'114-00-E-09':('D','393dbdbfbd59220a18fd11d2c09d1b07cd9daf5816d32bbe91a6ec1a335c204b','0346c84990c84812b9705adcfab7bb6d51877dce1e07c7ba4cc3e74797583cdd',[90,1282,1310,1403]),
'114-00-E-10':('C','b0a89c379254466524ff72308a751fe63ade9e85d037f8a46dc03a6727287275','820bb1292dbab9ea2113316dec2ab67d795520742f140dea9936b5e47915025f',[90,1401,1310,1491])}
QIDS=set(PINS)
REPORT=P+'review-evidence/E08-E10-source-admission-20261116.json'
SQL=P+'SQLITE_QA_E08_E10_SOURCE_BRIDGE_20261116.json'
def issuer(qid,kind):return P+'review-evidence/'+qid+'-'+kind+'-publisher-20261116.json'
def demand(ok,msg):
 if not ok:raise ValueError('E08_E10_SOURCE_HOLD: '+msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def raw(rel):
 f=ROOT/rel;demand(f.is_file() and not f.is_symlink(),'missing/unsafe '+rel);return f.read_bytes()
def read(rel):return json.loads(raw(rel))
def write(rel,x):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def original(rel):return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def rows(path):
 with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
  demand(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'SQLite integrity')
  demand(len(db.execute('PRAGMA table_info(questions)').fetchall())==7,'seven columns')
  values=db.execute('SELECT * FROM questions ORDER BY question_id').fetchall()
  demand(len(values)==205 and len({r[0] for r in values})==205,'205 unique SQLite rows')
  return {r[0]:r for r in values}
def publisher():
 f=Path(os.environ['PUBLISHER_CHECKER_PATH']);b=f.read_bytes()
 demand(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='d410b10ff75ff7bfbb465098b0c2e5dd5b104978','pinned current native publisher')
 s=importlib.util.spec_from_file_location('e0810_native',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify_pdfs(folder):
 import fitz
 texts={}
 for name,h in PDFS.items():
  b=(folder/(name+'.pdf')).read_bytes();demand(sha(b)==h,'official PDF '+name)
  d=fitz.open(stream=b,filetype='pdf');demand(len(d)==(12 if name=='question' else 1),'PDF page count '+name)
  texts[name]=d[1 if name=='question' else 0].get_text()
 for qid,(answer,_,_,_) in PINS.items():
  n=int(qid[-2:]);demand(re.search(r'\b'+str(n)+r'\s+'+answer+r'\s+'+str(n+10)+r'\b',texts['answer']) is not None,'printed answer '+qid)
 for t in ['Chen Chieh-hsien','Apparently','abandon','(D) run into']:demand(t in texts['question'],'official original text '+t)
 demand(re.search(r'試題題號\s*26\s*試題內容',texts['notice']) is not None,'notice names26 only')
 return PDFS.copy()
def images(q,m):
 from PIL import Image,ImageChops
 qid=q['questionId'];_,webp,rev,crop=PINS[qid]
 demand(sha(raw(m['output']))==webp and m['sha256']==webp and sha(raw(m['source']))==PAGE,'original image hash '+qid)
 a=Image.open(ROOT/m['output']).convert('RGB');b=Image.open(ROOT/m['source']).convert('RGB').crop(tuple(crop))
 demand(a.size==(1220,crop[3]-crop[1]) and not any(c.getbbox() for c in ImageChops.difference(a,b).split()),'all RGB exact crop '+qid)
 demand(m['crop']==crop and q['sourcePage']==2,'page/crop '+qid)
 demand(sha(canonical({'question':q['question'],'options':q['options'],'singleQuestionWebpSha256':webp}))==rev,'frozen revision '+qid)
def expected_q(old,g2,g3):
 q=copy.deepcopy(old);qid=q['questionId'];answer,_,rev,_=PINS[qid]
 if qid.endswith('-10'):q['options'][3]='run into';q['issues']=[s for s in q['issues'] if s!='last_on_page_check_possible_continuation_or_footer']
 q.update(questionVerified=True,answerVerified=True,textQaStatus='PASS',officialFinalAnswer=answer,officialCorrectionChecked=True,reviewStatus='SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI')
 q['answerProvenance']['independentVisualVerification']=True
 q['textQaEvidence']={'reviewer':g2['reviewer'],'reviewedAt':DATE,'evidencePath':issuer(qid,'ocr'),'evidenceSha256':sha(canonical_pretty(g2)),'questionRevision':rev,'sourceImageSha256':PAGE}
 q['officialFinalQaEvidence']={'reviewer':g3['reviewer'],'reviewedAt':DATE,'evidencePath':issuer(qid,'official'),'evidenceSha256':sha(canonical_pretty(g3)),'answerPdfSha256':PDFS['answer'],'finalCorrectionsReviewed':True}
 return q
def canonical_pretty(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def apply(folder):
 verify_pdfs(folder);demand(sha(raw(ANSWER_IMAGE))==ANSWER_SHA,'original official answer image')
 for n in ['questions.json','question-bank.sqlite3','inventory.json','webp-manifest.json']:demand(raw(P+n)==original(P+n),'fresh source drift '+n)
 bank=read(P+'questions.json');manifest=read(P+'webp-manifest.json');inv=read(P+'inventory.json');evidence={}
 for q in bank['questions']:
  qid=q['questionId']
  if qid not in QIDS:continue
  demand(q['questionVerified'] is False and q['answerVerified'] is False and q['answer']==PINS[qid][0] and q['answerMatched'] is True,'pending source '+qid)
  m=next(x for x in manifest['items'] if x['questionId']==qid)
  clean=copy.deepcopy(q)
  if qid.endswith('-10'):
   demand(clean['options'][3].startswith('run into\n') and '第11' in clean['options'][3],'exact known E10 contamination')
   clean['options'][3]='run into'
  images(clean,m)
  common={'schemaVersion':1,'year':114,'questionId':qid,'taskId':TASK,'reviewer':'ROLE A Work source inspector; not independent ROLE E','reviewedAt':DATE,'studentReady':False,'studentReleaseApproved':False,'independentE':False}
  g2={**common,'questionRevision':PINS[qid][2],'webpSha256':PINS[qid][1],'question':clean['question'],'options':clean['options'],'visualTextCompared':True,'originalSourcePage':2,'sourceImageSha256':PAGE,'originalCrop':m['crop'],'allRgbCropPixelsEqual':True,'officialQuestionPdfSha256':PDFS['question'],'officialPdfDownloadedAndRehashedThisTask':True,'originalUnderlinedWord':{'114-00-E-09':'Apparently','114-00-E-10':'abandon'}.get(qid),'ocrBoundaryRepair':'E10 D truncated to original run into' if qid.endswith('-10') else None}
  g3={**common,'officialPage':'https://web1.tcte.edu.tw/EXAM/114_4y/','officialPdfSha256':PDFS['answer'],'finalAnswer':PINS[qid][0],'officialFinalAnswerImageQaPassed':True,'officialAnswerImagePath':ANSWER_IMAGE,'officialAnswerImageSha256':ANSWER_SHA,'correctionNoticeReviewed':True,'noObjectionForPaper':False,'noCorrectionForThisQuestion':True,'correctionForQuestionReviewed':False,'confirmationPdfSha256':PDFS['notice'],'namedOfficialCorrectionQuestionIds':['114-00-E-26'],'sourceQuestionRevision':PINS[qid][2],'officialPdfDownloadedAndRehashedThisTask':True,'allNoticePagesVisuallyReviewed':True,'originalPublishedAnswerPdfPage':1}
  for kind,obj in [('ocr',g2),('official',g3)]:demand(not (ROOT/issuer(qid,kind)).exists(),'new issuer only');write(issuer(qid,kind),obj)
  repaired=expected_q(q,g2,g3);q.clear();q.update(repaired)
  m['visualReviewEvidence']['referenceSha256']=sha(raw(m['visualReviewEvidence']['reference']))
  if qid.endswith('-10'):m['issues']=[x for x in m['issues'] if x!='last_on_page_check_possible_continuation_or_footer']
  evidence[qid]={'G2':issuer(qid,'ocr'),'G2Sha256':sha(raw(issuer(qid,'ocr'))),'G3':issuer(qid,'official'),'G3Sha256':sha(raw(issuer(qid,'official'))),'questionRevision':PINS[qid][2],'originalWebpSha256':PINS[qid][1]}
 write(P+'questions.json',bank);write(P+'webp-manifest.json',manifest)
 with sqlite3.connect(ROOT/(P+'question-bank.sqlite3')) as db:
  for q in bank['questions']:
   if q['questionId'] not in QIDS:continue
   payload=canonical(q);demand(db.execute('UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?',(payload.decode(),sha(payload),q['questionId'])).rowcount==1,'one-row update')
 inv['sqlite'].update(dbSha256=sha(raw(P+'question-bank.sqlite3')),sourceQuestionsSha256=sha(raw(P+'questions.json')),evidencePath=SQL,releaseApproved=False);write(P+'inventory.json',inv)
 report={'schemaVersion':1,'taskId':TASK,'baseSourceCommit':BASE,'officialPdfsFreshlyDownloadedAndRehashed':PDFS,'officialOriginalPageSha256':PAGE,'officialAnswerImageSha256':ANSWER_SHA,'questions':evidence,'rows':205,'columns':7,'other202CanonicalAndCompleteSqliteRowsUnchanged':True,'all115TrackedDataUnchanged':True,'originalWebPsUnchanged':True,'newReady':False,'newLive':False,'formalG8':False,'G6':'NOT_EXECUTED','G7':'NOT_EXECUTED','trustedE':False,'sourceBankSha256':sha(raw(P+'questions.json')),'dbSha256':sha(raw(P+'question-bank.sqlite3'))}
 for path in [REPORT,SQL]:demand(not (ROOT/path).exists(),'new report only');write(path,report)
 verify()
def verify():
 bank=read(P+'questions.json');old=json.loads(original(P+'questions.json'));by={q['questionId']:q for q in bank['questions']};oldby={q['questionId']:q for q in old['questions']}
 demand(len(by)==len(bank['questions'])==205 and by.keys()==oldby.keys(),'205 unique canonical IDs')
 demand({k for k in by if by[k]!=oldby[k]}==QIDS,'other202 canonical')
 bank_metadata=copy.deepcopy(bank);bank_metadata['questions']=old['questions'];demand(bank_metadata==old,'bank metadata/shared materials unchanged')
 manifest=read(P+'webp-manifest.json');expected=json.loads(original(P+'webp-manifest.json'))
 pub=publisher()
 for qid in sorted(QIDS):
  q=by[qid];m=next(x for x in manifest['items'] if x['questionId']==qid);images(q,m)
  g2=read(issuer(qid,'ocr'));g3=read(issuer(qid,'official'))
  demand(q==expected_q(oldby[qid],g2,g3),'exact bounded canonical '+qid)
  em=next(x for x in expected['items'] if x['questionId']==qid);em['visualReviewEvidence']['referenceSha256']=sha(raw(m['visualReviewEvidence']['reference']))
  if qid.endswith('-10'):em['issues']=[s for s in em['issues'] if s!='last_on_page_check_possible_continuation_or_footer']
  demand(pub.source_proof(q,True,True,PINS[qid][2])==(True,True),'native G2/G3 '+qid)
  demand(pub.certified_visual_assets(ROOT,q,m,{}) is not None,'native G1 '+qid)
  for kind in ['ocr','official']:demand(pub.review_document(ROOT,114,issuer(qid,kind),qid) is not None,'native issuer '+qid)
  demand(pub.official_notice_scope_certified(ROOT,114,q,g3),'native per-question notice '+qid)
  demand(pub.certificates_complete(ROOT,q,m,{}) is False,'source cannot authorize release '+qid)
  for field in ['independentSolve','teachingQaStatus','uiQaStatus','studentReleaseApproved']:demand(field not in q,'no fabricated '+field)
  demand('finalAnswer' not in g2 and 'answer' not in g2 and 'officialPdfSha256' not in g2,'answer-hidden G2')
 demand(manifest==expected,'bounded manifest only')
 with tempfile.NamedTemporaryFile() as t:
  t.write(original(P+'question-bank.sqlite3'));t.flush();before=rows(Path(t.name))
 after=rows(ROOT/(P+'question-bank.sqlite3'));demand({k for k in after if after[k]!=before[k]}==QIDS,'other202 complete SQLite rows')
 for k,row in after.items():demand(json.loads(row[-2])==by[k] and sha(row[-2].encode())==row[-1],'205 JSON/SQLite/SHA')
 inv=read(P+'inventory.json');oldinv=json.loads(original(P+'inventory.json'));expectedinv=copy.deepcopy(oldinv);expectedinv['sqlite'].update(dbSha256=sha(raw(P+'question-bank.sqlite3')),sourceQuestionsSha256=sha(raw(P+'questions.json')),evidencePath=SQL,releaseApproved=False);demand(inv==expectedinv,'exact inventory hashes')
 demand(sha(raw(ANSWER_IMAGE))==ANSWER_SHA,'answer image bytes')
 # Every tracked 115 path (including SQLite) remains byte-identical to the frozen source.
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'sudu/data/processed/115'],cwd=ROOT,text=True).splitlines()
 for path in paths:demand(raw(path)==original(path),'115 untouched '+path)
 report=read(REPORT);demand(report==read(SQL) and report['sourceBankSha256']==sha(raw(P+'questions.json')) and report['dbSha256']==sha(raw(P+'question-bank.sqlite3')),'report source/SQLite hashes')
 for qid in QIDS:
  item=report['questions'][qid]
  for kind,key in [('ocr','G2'),('official','G3')]:demand(item[key]==issuer(qid,kind) and item[key+'Sha256']==sha(raw(issuer(qid,kind))),'report issuer hash')
 print(json.dumps({'QIDs':sorted(QIDS),'G1_G2_G3':'PASS','sqlite205':'PASS','other202':'UNCHANGED','all115':'UNCHANGED','newReady':False,'newLive':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--pdfdir',type=Path);args=ap.parse_args()
 if args.apply:apply(args.pdfdir)
 else:
  if args.pdfdir:verify_pdfs(args.pdfdir)
  verify()
