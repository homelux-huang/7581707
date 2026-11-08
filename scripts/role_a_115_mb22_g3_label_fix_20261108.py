#!/usr/bin/env python3
"""Fix MB22 G3 reviewer prose A->B, rebind hash/SQLite, preserve other 204.
Only the human-readable claim was wrong; actual official finalAnswer was B.
No new review is claimed and no student release is authorized.
"""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'sudu/data/processed/115'
QID='115-00-MB-22'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g3p=BASE/'review-evidence/115-00-MB-22-official-publisher-20261108.json'
bp=BASE/'questions.json'
rp=BASE/'review-evidence/115-00-MB-22-source-admission-20261108.json'
ip=BASE/'inventory.json'
sp=BASE/'question-bank.sqlite3'
qp=BASE/'SQLITE_QA_MB22_SOURCE_BRIDGE_20261108.json'
g3=json.loads(g3p.read_text())
assert g3['finalAnswer']=='B'
assert g3['reviewer']=='ROLE A original published 115 Math(B) p1 Q22 A and original no-objection notice; not independent Role E'
g3['reviewer']=g3['reviewer'].replace('Q22 A','Q22 B')
save(g3p,g3)
bank=json.loads(bp.read_text())
assert len(bank['questions'])==205
q=[x for x in bank['questions'] if x['questionId']==QID]
assert len(q)==1 and q[0]['answer']=='B' and q[0]['officialFinalAnswer']=='B'
q[0]['officialFinalQaEvidence']['evidenceSha256']=digest(g3p)
save(bp,bank)
receipt=json.loads(rp.read_text())
assert receipt['officialPublishedLetter']=='B' and not receipt['studentReady'] and not receipt['newLive']
receipt['publisherOfficialEvidenceSha256']=digest(g3p)
save(rp,receipt)
payload=json.dumps(q[0],ensure_ascii=False,sort_keys=True,separators=(',',':'))
with sqlite3.connect(sp) as c:
    n=c.execute('UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?',(payload,hashlib.sha256(payload.encode()).hexdigest(),QID)).rowcount
    assert n==1
    c.commit()
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    rows=c.execute('SELECT question_id,payload_json,payload_sha256 FROM questions').fetchall()
assert len(rows)==205
allq={x['questionId']:x for x in bank['questions']}
assert all(json.loads(p)==allq[k] and hashlib.sha256(p.encode()).hexdigest()==h for k,p,h in rows)
inventory=json.loads(ip.read_text())
inventory['sqlite']['sourceQuestionsSha256']=digest(bp)
inventory['sqlite']['dbSha256']=digest(sp)
save(ip,inventory)
report=json.loads(qp.read_text())
assert report['onlyUpdatedQid']==QID and not report['ready'] and not report['live']
report['afterQuestionBankSha256']=digest(bp)
report['afterSqliteSha256']=digest(sp)
save(qp,report)
print('MB22 G3 wording corrected to B; 205 parity maintained; other 204 cannot change by single-row SQL; student READY and LIVE false.')
