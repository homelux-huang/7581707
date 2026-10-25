#!/usr/bin/env python3
"""Role A minimal 115-C15 option-D source text+SQLite surgical repair.

Only repairs contamination after the real original D choice; original raw extraction
remains intact as evidence. No answer/lesson/independent QA/READY or other QIDs touched.
Works idempotently and fails closed against source/image/DB SHA mismatch.
"""
import argparse
import copy
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/data/processed/115"
BANK=DIR/"questions.json"
DB=DIR/"question-bank.sqlite3"
QID="115-00-C-15"
CLEAN_D="拘泥禮法 ／ 不知變通"
Q15_WEBP=ROOT/"sudu/data/processed/115/webp-v2/00-C/115-00-C-15.webp"
Q15_WEBP_SHA="74dc7bb966f1ee508456a962a6fbcff0f42a15b2ffdd8db747477a55b831405f"
SOURCE_PAGE=ROOT/"sudu/data/original/115/00-C/p005-6b454d6590-v2-w1400-q66.webp"
SOURCE_PAGE_SHA="bf0678abeeddb131a843fe0461182a3a15ffaf836461933539dc3db1602cd98b"
VISUAL_EVIDENCE=DIR/"QA_115_C_Q06_Q11_15_DIRECT_VISUAL_20261023.json"
OFFICIAL_EVIDENCE=DIR/"QA_115_C_6_FINAL_OFFICIAL_ANSWERS_20261023.json"
PROOF_FILE=DIR/"QA_115_C15_OPTION_D_CROSSPAGE_CORRECTION_20261025.json"
VISUAL_EVIDENCE_GIT="fca5b8e9e16b390f245c93caeb420b4b86f97f60"
OFFICIAL_EVIDENCE_GIT="250ed2949b54099ee86511e0d1c4bcf69f33c9be"
INITIAL_BANK_GIT="216bc43d57501bc1c3e5842b48413a8967456cda"
OFFICIAL_PDF_RECORDED="ec9871b659d81726de5b6412ed5252d62541afb287951b5d6cf923c1ea763e64"

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def proof_image(path, digest, size):
    b=path.read_bytes()
    assert b[:4]==b"RIFF" and b[8:12]==b"WEBP", str(path)
    assert sha(b)==digest, "source pixel SHA drift: "+str(path)
    with Image.open(path) as image:
        assert image.format=="WEBP",str(path)
        image.load()
        assert image.size==size,(str(path),image.size,size)

def verify_sources():
    proof_image(Q15_WEBP,Q15_WEBP_SHA,(1220,239))
    proof_image(SOURCE_PAGE,SOURCE_PAGE_SHA,(1400,1981))
    assert blob(VISUAL_EVIDENCE.read_bytes())==VISUAL_EVIDENCE_GIT
    assert blob(OFFICIAL_EVIDENCE.read_bytes())==OFFICIAL_EVIDENCE_GIT
    qa=json.loads(VISUAL_EVIDENCE.read_text(encoding="utf-8"))
    v=next(x for x in qa["items"] if x["questionId"]==QID)
    assert v["reviewedWebpSha256"]==Q15_WEBP_SHA
    assert v["result"]=="PASS"
    assert v["sourcePageSha256"]==SOURCE_PAGE_SHA
    assert v["cropPixels"]==[90,1421,1310,1660]
    assert v["independentHumanReview"] is False
    official=json.loads(OFFICIAL_EVIDENCE.read_text(encoding="utf-8"))
    o=next(x for x in official["records"] if x["questionId"]==QID)
    assert o["officialPublishedFinalAnswer"]=="B"
    assert o["officialPublishedAnswerSourcePdfSha256"]==OFFICIAL_PDF_RECORDED
    assert o["answerVerified"] is True and o["questionVerified"] is False
    assert o["officialNoticeStatus"]=="NO_ENTRY_IN_FULL_10_PAGE_00_C_CONFIRMATION_PDF"

def check_bank(data):
    assert data["year"]==115
    questions=data["questions"]
    assert len(questions)==205
    d={q["questionId"]:q for q in questions}
    assert len(d)==205 and QID in d
    q=d[QID]
    assert q["year"]==115 and q["paperCode"]=="00-C" and q["originalQuestionNumber"]==15
    assert len(q["options"])==4 and q["answer"]=="B" and q["answerVerified"] is True
    assert q["questionVerified"] is False and q["integrationReady"] is False
    assert q["assets"]["sha256"]==Q15_WEBP_SHA
    assert q["extraction"]["rawOptions"][3].startswith(CLEAN_D)
    assert "▲閱讀下文，回答第16-18 題" in q["extraction"]["rawOptions"][3]
    return q,d

def verify_sqlite_against(data):
    qs={q["questionId"]:q for q in data["questions"]}
    with sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        schema={r[1] for r in db.execute("PRAGMA table_info(questions)")}
        assert {"question_id","question","payload_json","payload_sha256","answer","answer_verified","question_verified","review_status"}<=schema
        rows=db.execute("""SELECT question_id,question,payload_json,payload_sha256,answer,
                          answer_verified,question_verified FROM questions""").fetchall()
    assert len(rows)==205 and {r[0] for r in rows}==set(qs)
    for qid,stem,payload,digest,letter,av,qv in rows:
        q=qs[qid]
        assert stem==q["question"],qid
        assert sha(payload.encode("utf-8"))==digest,qid
        assert json.loads(payload)==q,qid
        assert payload==canonical(q),qid
        assert letter==q["answer"] and bool(av)==bool(q["answerVerified"]) and bool(qv)==bool(q["questionVerified"]),qid

def publisher_revision(q):
    from scripts import sudu_verified_publish
    return sudu_verified_publish.text_revision(q,Q15_WEBP_SHA)

def minimal_replace(original_text, original_q, new_d):
    # Replace ONLY Q15's original canonical options[3] JSON string literal.
    pos=original_text.find('"questionId": "115-00-C-15"')
    assert pos>=0 and original_text.count('"questionId": "115-00-C-15"')==1
    options_pos=original_text.find('"options": [',pos)
    assert 0<options_pos<pos+12000
    array_start=original_text.index("[",options_pos)
    arr,end=json.JSONDecoder().raw_decode(original_text[array_start:])
    assert arr==original_q["options"]
    before=original_text[array_start:array_start+end]
    old_d=original_q["options"][3]
    old_lit=json.dumps(old_d,ensure_ascii=False)
    new_lit=json.dumps(new_d,ensure_ascii=False)
    assert before.count(old_lit)==1, "Q15 options JSON unexpected encoding; do not rewrite entire year"
    assert new_lit!=old_lit
    after=before.replace(old_lit,new_lit,1)
    updated=original_text[:array_start]+after+original_text[array_start+end:]
    verify=json.loads(updated)
    assert len(verify["questions"])==205
    for q in verify["questions"]:
        a=next(x for x in json.loads(original_text)["questions"] if x["questionId"]==q["questionId"])
        if q["questionId"]==QID:
            expect=copy.deepcopy(a);expect["options"][3]=CLEAN_D
            assert q==expect
        else: assert q==a, "non-C15 source modified"
    return updated,verify

def update_db_copy(new_q, target_db):
    with sqlite3.connect(target_db) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        original=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
        assert original is not None
        oldpayload,oldsha=original
        assert sha(oldpayload.encode("utf-8"))==oldsha
        assert json.loads(oldpayload)["options"][3].startswith(CLEAN_D)
        payload=canonical(new_q)
        digest=sha(payload.encode("utf-8"))
        cursor=db.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                          (payload,digest,QID))
        assert cursor.rowcount==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        assert db.execute("SELECT payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()[0]==digest
    return digest

def main():
    import sys
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply == args.verify: parser.error("select exactly one of --apply or --verify")
    verify_sources()
    raw=BANK.read_bytes()
    data=json.loads(raw.decode("utf-8"))
    q,mapping=check_bank(data)
    if args.verify:
        assert q["options"][3]==CLEAN_D, "C15 not corrected"
        evidence=json.loads(PROOF_FILE.read_text(encoding="utf-8"))
        assert evidence["questionId"]==QID
        assert evidence["correctedOptionD"]==CLEAN_D
        assert evidence["sourceRevisionAfter"]==publisher_revision(q)
        assert evidence["originalRawOptionDSha256"]==sha(q["extraction"]["rawOptions"][3].encode("utf-8"))
        assert q["answer"]=="B" and q["answerVerified"] and not q["questionVerified"]
        verify_sqlite_against(data)
        print("SUCCESS verified exact corrected C15 option D / 205 SQL SHA / original RAW preserved / no release")
        return
    old=q["options"][3]
    if old==CLEAN_D:
        # Idempotence for safely re-run verification on post-patch HEAD.
        assert PROOF_FILE.exists()
        verify_sqlite_against(data)
        print("ALREADY CORRECTED, no git source mutation")
        return
    assert blob(raw)==INITIAL_BANK_GIT, "source bank drift: fresh rebase required"
    assert old.startswith(CLEAN_D)
    tail=old[len(CLEAN_D):]
    assert "▲閱讀下文，回答第16-18 題" in tail
    assert "公告試題僅供參考" in tail
    assert "第6 頁" in tail
    before_revision=publisher_revision(q)
    new_text,new_data=minimal_replace(raw.decode("utf-8"),q,CLEAN_D)
    new_q,_=check_bank(new_data)
    assert new_q["options"][3]==CLEAN_D
    assert new_q["extraction"]["rawOptions"][3]==q["extraction"]["rawOptions"][3]
    after_revision=publisher_revision(new_q)
    assert before_revision!=after_revision
    # Guarantee pre-existing 205-row SQLite integrity and semantic bank equality.
    verify_sqlite_against(data)
    with tempfile.TemporaryDirectory(prefix="role-a-c15-",dir=DIR) as d:
        import shutil
        d=Path(d)
        tmpdb=d/"q.sqlite3"
        shutil.copy2(DB,tmpdb)
        updated_payload=update_db_copy(new_q,tmpdb)
        tmpbank=d/"questions.json"
        tmpbank.write_text(new_text,encoding="utf-8")
        proof={
          "schemaVersion":1, "taskId":"A-115-C15-OPTION-D-CROSSPAGE-SQLITE-20261025-09",
          "questionId":QID,"role":"A source/OCR correction author, not independent E",
          "sourceOriginalSingleWebpSha256":Q15_WEBP_SHA,
          "sourceOriginalPageWebpSha256":SOURCE_PAGE_SHA,
          "sourceHistoricalImageEvidenceGitBlob":VISUAL_EVIDENCE_GIT,
          "sourceHistoricalAnswerEvidenceGitBlob":OFFICIAL_EVIDENCE_GIT,
          "originalBankGitBlob":INITIAL_BANK_GIT,
          "originalRawOptionDSha256":sha(old.encode("utf-8")),
          "correctedOptionD":CLEAN_D,
          "correctedOptionDSha256":sha(CLEAN_D.encode("utf-8")),
          "sourceRevisionBefore":before_revision,
          "sourceRevisionAfter":after_revision,
          "sqliteCorrectedPayloadSha256":updated_payload,
          "officialFinalAnswer":"B",
          "preservedRawExtraction":True,
          "questionVerified":False, "independentOriginalTextQa":"PENDING",
          "independentRoleEContentReview":"PENDING",
          "studentReleaseApproved":False,"newReady":0,"newLive":0,
          "correctionScope":"Only 115-00-C-15 options[3] structured text, not raw OCR or other questions",
          "evidence":"Archived exact original Q15 WebP and historical visual QA show A-D with no adjacent Q16; extracted D appended p5 footer/p6 unrelated text",
        }
        tmpproof=d/"proof.json"
        tmpproof.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        # Copy all staged artifacts after successful source and DB QA, no student data.
        os.replace(tmpbank,BANK)
        os.replace(tmpdb,DB)
        os.replace(tmpproof,PROOF_FILE)
    verify_sqlite_against(new_data)
    assert json.loads(PROOF_FILE.read_text(encoding="utf-8"))["sourceRevisionAfter"]==after_revision
    print("REPAIRED original bank+SQLite one Q15 D, 205 rows PASS; old revision="+before_revision+" new revision="+after_revision+" no READY")

if __name__=="__main__":
    main()
