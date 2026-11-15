"""E07 original source bridge; frozen one-question QA only, never student admission."""
import argparse, copy, hashlib, importlib.util, json, os, sqlite3, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='f9a6bc84531b5a6a8b5d57cde3828323e500cbbc'
P='sudu/data/processed/114/'
QID='114-00-E-07'
TASK='WORK-A114-E07-BINARY-SQLITE-20261114-01'
REV='8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c'
WEBP='0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc'
PAGE='fd05e4a3f87f69bbd0d0f2a963400342da9752ec8bbef0ef3b26b59e621ae002'
PDFS={'question':'1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf','answer':'ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325','notice':'79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc'}
G2=P+'review-evidence/'+QID+'-ocr-publisher-20261115.json'
G3=P+'review-evidence/'+QID+'-official-publisher-20261115.json'
REPORT=P+'review-evidence/'+QID+'-source-admission-20261115.json'
SQL=P+'SQLITE_QA_E07_SOURCE_BRIDGE_20261115.json'

def demand(ok,msg):
 if not ok: raise ValueError('E07_SOURCE_HOLD: '+msg)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def raw(rel):
 f=ROOT/rel;demand(f.is_file() and not f.is_symlink(),'missing/unsafe '+rel);return f.read_bytes()
def read(rel): return json.loads(raw(rel))
def write(rel,x):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def original(rel): return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def rows(path):
 with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
  demand(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'SQLite integrity')
  demand(len(db.execute('PRAGMA table_info(questions)').fetchall())==7,'seven columns')
  return {x[0]:x for x in db.execute('SELECT * FROM questions ORDER BY question_id')}
def publisher():
 f=Path(os.environ['PUBLISHER_CHECKER_PATH']);b=f.read_bytes()
 demand(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='64db5dd620dec230287ff0ea92a64b6e181e45a9','pinned native publisher')
 s=importlib.util.spec_from_file_location('e07_publisher',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify_pdfs(folder):
 import fitz
 texts={}
 for name,h in PDFS.items():
  b=(folder/(name+'.pdf')).read_bytes();demand(sha(b)==h,'official PDF '+name)
  d=fitz.open(stream=b,filetype='pdf');texts[name]=''.join(p.get_text() for p in d)
  demand(len(d)==(12 if name=='question' else 1),'PDF page count '+name)
 demand('the sensor lights in the park' in texts['question'],'original question PDF')
 import re
 demand(re.search(r'7\s+A\s+17\s+B',texts['answer']) is not None,'published original row7 A')
 demand(re.search(r'試題題號\s*26\s*試題內容',texts['notice']) is not None,'notice names26')
 return {k:sha((folder/(k+'.pdf')).read_bytes()) for k in PDFS}

def images(q,m):
 from PIL import Image,ImageChops
 demand(sha(raw(m['output']))==WEBP and sha(raw(m['source']))==PAGE,'original image hashes')
 a=Image.open(ROOT/m['output']).convert('RGB');b=Image.open(ROOT/m['source']).convert('RGB').crop(tuple(m['crop']))
 demand(a.size==(1220,122) and not any(c.getbbox() for c in ImageChops.difference(a,b).split()),'all RGB exact source crop')
 demand(m['crop']==[90,1007,1310,1129] and q['sourcePage']==2,'original page/crop')
 demand(sha(canonical({'question':q['question'],'options':q['options'],'singleQuestionWebpSha256':WEBP}))==REV,'frozen text revision')

def apply(folder):
 verify_pdfs(folder)
 for n in ['questions.json','question-bank.sqlite3','inventory.json','webp-manifest.json']:demand(raw(P+n)==original(P+n),'fresh source drift '+n)
 bank=read(P+'questions.json');manifest=read(P+'webp-manifest.json');inventory=read(P+'inventory.json')
 q=next(q for q in bank['questions'] if q['questionId']==QID);m=next(m for m in manifest['items'] if m['questionId']==QID)
 demand(q['questionVerified'] is False and q['answerVerified'] is False and q['answer']=='A' and q['answerMatched'] is True,'pending source A')
 images(q,m)
 for rel in [G2,G3,REPORT,SQL]:demand(not (ROOT/rel).exists(),'new evidence only')
 common={'schemaVersion':1,'year':114,'questionId':QID,'taskId':TASK,'reviewer':'ROLE A Work source inspection; not independent ROLE E','reviewedAt':'2026-11-15','studentReady':False,'studentReleaseApproved':False,'independentE':False}
 g2={**common,'questionRevision':REV,'webpSha256':WEBP,'question':q['question'],'options':q['options'],'visualTextCompared':True,'originalSourcePage':2,'sourceImageSha256':PAGE,'originalCrop':m['crop'],'allRgbCropPixelsEqual':True,'officialQuestionPdfSha256':PDFS['question'],'officialPdfDownloadedAndRehashedThisTask':True}
 g3={**common,'officialPage':'https://web1.tcte.edu.tw/EXAM/114_4y/','officialPdfSha256':PDFS['answer'],'finalAnswer':'A','officialFinalAnswerImageQaPassed':True,'correctionNoticeReviewed':True,'noObjectionForPaper':False,'noCorrectionForThisQuestion':True,'correctionForQuestionReviewed':False,'confirmationPdfSha256':PDFS['notice'],'namedOfficialCorrectionQuestionIds':['114-00-E-26'],'sourceQuestionRevision':REV,'officialPdfDownloadedAndRehashedThisTask':True,'allNoticePagesVisuallyReviewed':True,'originalPublishedAnswerPdfPage':1}
 write(G2,g2);write(G3,g3)
 q.update(questionVerified=True,answerVerified=True,textQaStatus='PASS',officialFinalAnswer='A',officialCorrectionChecked=True,reviewStatus='SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI')
 q['answerProvenance']['independentVisualVerification']=True
 q['textQaEvidence']={'reviewer':g2['reviewer'],'reviewedAt':g2['reviewedAt'],'evidencePath':G2,'evidenceSha256':sha(raw(G2)),'questionRevision':REV,'sourceImageSha256':PAGE}
 q['officialFinalQaEvidence']={'reviewer':g3['reviewer'],'reviewedAt':g3['reviewedAt'],'evidencePath':G3,'evidenceSha256':sha(raw(G3)),'answerPdfSha256':PDFS['answer'],'finalCorrectionsReviewed':True}
 m['visualReviewEvidence']['referenceSha256']=sha(raw(m['visualReviewEvidence']['reference']))
 write(P+'questions.json',bank);write(P+'webp-manifest.json',manifest)
 payload=canonical(q)
 with sqlite3.connect(ROOT/(P+'question-bank.sqlite3')) as db:
  demand(db.execute('UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?',(payload.decode(),sha(payload),QID)).rowcount==1,'one-row update')
 inventory['sqlite'].update(dbSha256=sha(raw(P+'question-bank.sqlite3')),sourceQuestionsSha256=sha(raw(P+'questions.json')),evidencePath=SQL,releaseApproved=False)
 write(P+'inventory.json',inventory)
 report={**common,'baseSourceCommit':BASE,'sourceRevision':REV,'originalWebpSha256':WEBP,'originalPageSha256':PAGE,'officialPdfsFreshlyRehashed':PDFS,'sourceG2':G2,'sourceG3':G3,'g2Sha256':sha(raw(G2)),'g3Sha256':sha(raw(G3)),'rows':205,'columns':7,'other204CanonicalUnchanged':True,'other204CompleteSqliteRowsUnchanged':True,'manifestChange':'only E07 SHA-pins existing visual report','newReady':False,'newLive':False,'formalG8':False,'trustedE':False,'sourceBankSha256':sha(raw(P+'questions.json')),'dbSha256':sha(raw(P+'question-bank.sqlite3'))}
 write(REPORT,report);write(SQL,report);verify()

def verify():
 bank=read(P+'questions.json');old=json.loads(original(P+'questions.json'));manifest=read(P+'webp-manifest.json');oldm=json.loads(original(P+'webp-manifest.json'))
 by={q['questionId']:q for q in bank['questions']};oldby={q['questionId']:q for q in old['questions']}
 demand(len(by)==len(bank['questions'])==205,'205 canonical')
 demand([k for k in by if by[k]!=oldby[k]]==[QID],'other204 canonical')
 q=by[QID];m=next(x for x in manifest['items'] if x['questionId']==QID);images(q,m)
 expected=copy.deepcopy(oldm);next(x for x in expected['items'] if x['questionId']==QID)['visualReviewEvidence']['referenceSha256']=sha(raw(m['visualReviewEvidence']['reference']))
 demand(manifest==expected,'only E07 manifest evidence SHA')
 import tempfile
 with tempfile.NamedTemporaryFile() as t:
  t.write(original(P+'question-bank.sqlite3'));t.flush();before=rows(Path(t.name))
 after=rows(ROOT/(P+'question-bank.sqlite3'));demand(len(after)==205 and [k for k in after if after[k]!=before[k]]==[QID],'other204 complete rows')
 for k,row in after.items():demand(json.loads(row[-2])==by[k] and sha(row[-2].encode())==row[-1],'205 JSON/SQLite/SHA')
 inv=read(P+'inventory.json')['sqlite'];demand(inv['dbSha256']==sha(raw(P+'question-bank.sqlite3')) and inv['sourceQuestionsSha256']==sha(raw(P+'questions.json')),'inventory')
 pub=publisher();demand(pub.source_proof(q,True,True,REV)==(True,True),'native G2/G3')
 demand(pub.certified_visual_assets(ROOT,q,m,{}) is not None,'native original visual certificate')
 for rel in [G2,G3]:demand(pub.review_document(ROOT,114,rel,QID) is not None,'native issuer')
 demand(pub.official_notice_scope_certified(ROOT,114,q,read(G3)),'native notice E26 only')
 for field in ['independentSolve','teachingQaStatus','uiQaStatus','studentReleaseApproved']:demand(field not in q,'no forged '+field)
 demand(pub.certificates_complete(ROOT,q,m,{}) is False,'source cannot authorize release')
 report=read(REPORT);demand(report['g2Sha256']==sha(raw(G2)) and report['g3Sha256']==sha(raw(G3)),'report SHA')
 print(json.dumps({'qid':QID,'sourceRevision':REV,'G1_G2_G3':'PASS','sqlite205':'PASS','other204':'UNCHANGED','newReady':False,'newLive':False}))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--pdfdir',type=Path);a=ap.parse_args()
 if a.apply:apply(a.pdfdir)
 else:
  if a.pdfdir:verify_pdfs(a.pdfdir)
  verify()
