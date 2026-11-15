#!/usr/bin/env python3
"""Source-only 115 MathB23 original complete 2x3 table and SQLite admission.
Preserve C lesson / E review / D UI / protected main / approved / LIVE.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
QID="115-00-MB-23"
TASK="A-115-MB23-CANONICAL-G2G3-TABLE-20261110-01"
CLAIM="https://github.com/homelux-huang/7581707/issues/36#issuecomment-6768575685"
QA_BASE="15108e8e657d070724889f1df3d3a6ae6da96d97"
QA_BANK_BLOB="696ec3cba5ffd54717ae1b07985b2d332ecf1a19"
QA_DB_BLOB="758e2ebc993291ed8101549a750aa635a979f16b"
QA_INVENTORY_BLOB="0ac1dd8e003fec4c9d801059f9b2db2d9490151d"
QA_MANIFEST_BLOB="2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b"
STAGE_REF="a0e8ea8e5d7cde6fc0f13430037c242771809938"
AUTHOR_REF="afaba171eec77cc27c3171b8bc8282f68ade74b9"
MAIN_REF="5546a603abfe0af2e62c0e5f63f775be0bfb24cf"
REV="9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4"
TABLE_TEXT_SHA="3ae20c9b53eb5ba38ffa354cbda868806bb7716700548bbe88618e0104a89088"
TEACHING_SHA="13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6"
SINGLE_SHA="2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51"
SINGLE_BLOB="f8c1fa03e8e97b7d7dae789c8ecf9cd618058bbb"
PAGE_SHA="3272c1a1df85614af3e65ae56aac3d819c9d25a7e44366d3a514de4fa8cd0555"
PAGE_BLOB="4c98df22dd3096c5d59178f4f2b6b3e88415bbee"
ANSWER_SHA="1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d"
ANSWER_BLOB="5ea4b86e929506d595f96fa162d1aae021f68440"
SOURCE_PDF="e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082"
ANSWER_PDF="d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
G1_CERT="ca6507c62081bc1bbfa30cdd24172484a1c9b25b517ab04f7ae0f4caa74fa142"
STAGE_REL="sudu/data/processed/115/source-stage/115-00-MB-23-staged-20261104.json"
STAGE_BLOB="a96c73b60e5617b79166ae076a854341bae934c4"
TABLE_REL="sudu/data/processed/115/review-evidence/115-00-MB-23-table-source-20261103.json"
TABLE_BLOB="0f63d6a5f91015dd2b146731c48dce08668c1fa2"
OLD_G2_REL="sudu/data/processed/115/review-evidence/115-00-MB-23-image-transcription-correction-20261024.json"
OLD_G2_BLOB="170cd2238bb7c1b942a7a5389797295cdfe26953"
AUTHOR_REL="sudu/teaching-candidates/114-115-20261025/115-00-MB-23.json"
AUTHOR_BLOB="eae542565062adf997ab8c8d37d2c3cd4dd71ca1"
WEBP_REL="sudu/data/processed/115/webp-v2/00-MB/115-00-MB-23.webp"
PAGE_REL="sudu/data/original/115/00-MB/p008-e82e34d9cd-v2-w1400-q66.webp"
ANSWER_REL="sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"
MANIFEST_REL="sudu/data/processed/115/webp-manifest.json"
BANK_REL="sudu/data/processed/115/questions.json"
SQLITE_REL="sudu/data/processed/115/question-bank.sqlite3"
INVENTORY_REL="sudu/data/processed/115/inventory.json"
G1_REL="sudu/data/processed/115/VISUAL_QA_2026-10-22.json"
CERT_REL="sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
CERT_BLOB="ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
NOTICE_REL="sudu/data/processed/115/official-confirmation-status.json"
NOTICE_BLOB="6d21432395294d9ccbcfe1dea8be01f88597bbf3"
G2_REL="sudu/data/processed/115/review-evidence/115-00-MB-23-ocr-publisher-20261110.json"
G3_REL="sudu/data/processed/115/review-evidence/115-00-MB-23-official-publisher-20261110.json"
REPORT_REL="sudu/data/processed/115/review-evidence/115-00-MB-23-source-admission-20261110.json"
SQL_REPORT="sudu/data/processed/115/SQLITE_QA_MB23_TABLE_BRIDGE_20261110.json"
EXPECTED_OPTIONS=["32000","33000","34000","35000"]

def gate(condition,detail):
    if not condition:
        raise ValueError("MB23_SOURCE_HOLD: "+detail)

def read(rel):
    p=ROOT/rel
    gate(p.is_file() and not p.is_symlink(),"missing original "+rel)
    return p.read_bytes()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def js(rel):
    return json.loads(read(rel))

def canon(item):
    return json.dumps(item,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")

def write_new(rel,item):
    path=ROOT/rel
    gate(not path.exists(),"new evidence path exists "+rel)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(item,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def webp(rel,digest,oid):
    raw=read(rel)
    gate(raw[:4]==b"RIFF" and raw[8:12]==b"WEBP","original WebP header "+rel)
    gate(sha(raw)==digest and blob(raw)==oid,"original WebP bytes "+rel)

def db_rows(path):
    with sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True) as c:
        gate(c.execute("PRAGMA integrity_check").fetchone()[0]=="ok","SQLite PRAGMA")
        cols=[x[1] for x in c.execute("PRAGMA table_info(questions)")]
        gate(len(cols)==14 and "payload_json" in cols and "question_verified" in cols,"115 SQLite schema drift")
        rows=c.execute("SELECT * FROM questions ORDER BY question_id").fetchall()
    gate(len(rows)==205 and len({x[0] for x in rows})==205,"SQLite 205/205")
    gate(all(sha(r[12].encode("utf8"))==r[13] for r in rows),"DB payload SHA")
    return {r[0]:r for r in rows}

def assert_table(table):
    gate(table["title"]=="表（二）","table label")
    gate(table["columns"]==["行程","原價","優惠"],"all three table columns")
    gate(table["rows"]==[
        ["行程Ⅰ","每位收費 x 元","兩人同行，其中一人減免 3000 元"],
        ["行程Ⅱ","每位收費 (x＋2000) 元","兩人同行，其中一人打八折"]
    ],"exact six price-table cells")
    gate(len(table["rows"])==2 and all(len(row)==3 for row in table["rows"]),"source 2x3 dimensions")

def tables(table):
    return [{"heading":table["columns"],"rows":table["rows"]}]

def source_originals():
    for rel,oid in ((BANK_REL,QA_BANK_BLOB),(SQLITE_REL,QA_DB_BLOB),
                    (INVENTORY_REL,QA_INVENTORY_BLOB),(MANIFEST_REL,QA_MANIFEST_BLOB)):
        gate(blob(read(rel))==oid,"new QA baseline drift: "+rel)
    bank=js(BANK_REL)
    man=js(MANIFEST_REL)
    gate(len(bank["questions"])==len(man["items"])==205,"205 bank+manifest")
    q=next(x for x in bank["questions"] if x["questionId"]==QID)
    m=next(x for x in man["items"] if x["questionId"]==QID)
    gate(q["answer"]==q["officialFinalAnswer"]=="B" and q["answerVerified"] is True and q["questionVerified"] is False,"Q23 canonical baseline state")
    gate(q["tables"]==[] and "表 ( 二 )" in q["question"],"old table missing from structured source")
    gate(q["options"]==EXPECTED_OPTIONS,"four printed source options")
    gate(q["assets"]["sha256"]==m["sha256"]==SINGLE_SHA,"Q23 original SHA not preserved")
    gate(q["questionProvenance"]["pdfSha256"]==SOURCE_PDF and q["answerProvenance"]["pdfSha256"]==ANSWER_PDF,"official PDF provenance")
    gate(m["qaStatus"]=="PASS" and m["crop"]==[90,167,1310,603] and m["visualReviewEvidence"]["referenceSha256"]==G1_CERT,"original table photo visual certificate")
    webp(WEBP_REL,SINGLE_SHA,SINGLE_BLOB)
    webp(PAGE_REL,PAGE_SHA,PAGE_BLOB)
    webp(ANSWER_REL,ANSWER_SHA,ANSWER_BLOB)
    gate(sha(read(G1_REL))==G1_CERT,"Q23 visual QA SHA")
    gate(blob(read(OLD_G2_REL))==OLD_G2_BLOB,"archived raw OCR evidence Git blob")
    gate(blob(read(CERT_REL))==CERT_BLOB,"original printed answer QA record")
    a=[x for x in js(CERT_REL)["records"] if x["questionId"]==QID]
    gate(len(a)==1 and a[0]["officialFinalAnswerReadDirectlyFromPublishedImage"]=="B" and a[0]["answerVerified"] is True,"actual official B visual proof")
    gate(blob(read(NOTICE_REL))==NOTICE_BLOB and js(NOTICE_REL)["confirmations"]["00-MB"]["officialStatus"]=="no_objection_submitted","115 math B correction scope")
    stagepath=ROOT/"_role_a_stage"/STAGE_REL
    tablepath=ROOT/"_role_a_stage"/TABLE_REL
    authorpath=ROOT/"_role_c_author"/AUTHOR_REL
    for p,b in ((stagepath,STAGE_BLOB),(tablepath,TABLE_BLOB),(authorpath,AUTHOR_BLOB)):
        gate(p.is_file() and blob(p.read_bytes())==b,"frozen A/C stage Git blob")
    stage=json.loads(stagepath.read_text(encoding="utf8"))
    proof=json.loads(tablepath.read_text(encoding="utf8"))
    author=json.loads(authorpath.read_text(encoding="utf8"))
    src=stage["source"]
    orig=proof["originalTextAndTable"]
    gate(stage["questionId"]==proof["questionId"]==author["questionId"]==QID,"same QID")
    gate(src["question"]==orig["correctedQuestion"]==author["question"],"original exact stem equality")
    gate(src["options"]==orig["originalOptions"]==author["options"]==EXPECTED_OPTIONS,"original four options/teacher equality")
    assert_table(src["table"])
    gate(src["table"]==orig["sourceTable"],"different A table source versions")
    gate(tables(src["table"])==author["sourceTables"],"original C table mismatch")
    gate(src["sourceRevision"]==orig["sourceRevisionSha256"]==author["sourceTextRevisionWithTable"]==REV,"accepted A/C table-inclusive revision")
    gate(src["tableTextSha256"]==orig["correctedTextSourceSha256"]==TABLE_TEXT_SHA,"table text SHA drift")
    gate(sha(orig["sourceRevisionSeed"].encode("utf8"))==REV,"table-inclusive original A revision hash")
    gate(src["singleSha256"]==author["imageSha256"]==SINGLE_SHA and author["image"]==WEBP_REL,"A C WebP SHA difference")
    gate(author["teachingCanonicalSha256"]==TEACHING_SHA,"original teaching digest must not be rewritten")
    gate(stage["official"]["letter"]==proof["publishedOfficialAnswer"]["value"]=="B","original answer B")
    gate(2*33000-3000==int(1.8*(33000+2000))==63000,"official Q23 mathematics")
    gate(all((2*x-3000)!=int(1.8*(x+2000)) for x in (32000,34000,35000)),"incorrect distractor math")
    old=db_rows(BASE/"question-bank.sqlite3")
    gate(set(old)=={x["questionId"] for x in bank["questions"]},"DB and bank QIDs")
    gate(all(json.loads(old[x["questionId"]][12])==x for x in bank["questions"]),"205 baseline payload equality")
    gate(old[QID][9]==0 and old[QID][10]==0,"old Q23 denormalized SQLite flags")
    return bank,man,q,m,stage,proof,author,old

def issuers(q,stage,table):
    g2={
        "schemaVersion":1,"year":115,"questionId":QID,"role":"A_SOURCE_ONLY_NOT_DISTINCT_E",
        "taskId":TASK,"questionRevision":REV,"webpSha256":SINGLE_SHA,
        "question":q["question"],"options":q["options"],"visualTextCompared":True,
        "reviewer":"ROLE A original MathB Q23 p8 2x3 source table visual/candidate; not independent E",
        "reviewedAt":"2026-11-10","reviewType":"SOURCE_TABLE_2X3_G2_ORIGINAL",
        "sourceYear":115,"originalPage":8,"sourcePdfSha256PreviouslyRecorded":SOURCE_PDF,
        "originalPageSha256":PAGE_SHA,"originalSingleWebpSha256":SINGLE_SHA,
        "originalSingleWebpGitBlob":SINGLE_BLOB,"sourcePageWebpGitBlob":PAGE_BLOB,
        "originalSourceTable":table,"sourceTables":tables(table),
        "tableTextSha256":TABLE_TEXT_SHA,"sourceTableRequired":True,
        "tableHeaderColumns":3,"tableDataRows":2,"tableDataCells":6,
        "sourceStagePath":STAGE_REL,"sourceStageGitBlob":STAGE_BLOB,
        "sourceTableEvidencePath":TABLE_REL,"sourceTableEvidenceGitBlob":TABLE_BLOB,
        "originalRawOcrPreserved":True,"noRecrop":True,"noAdjacentQID":True,
        "answerHiddenFromIssuer":True,"independentE":False,"studentReady":False,"studentLive":False
    }
    g3={
        "schemaVersion":1,"year":115,"questionId":QID,
        "reviewer":"ROLE A original published 115 Math(B) p1 Q23 B and no-objection notice; not independent E",
        "reviewedAt":"2026-11-10","officialPage":"https://web1.tcte.edu.tw/EXAM/115_4y/",
        "officialPdfSha256":ANSWER_PDF,"finalAnswer":"B",
        "officialFinalAnswerImageQaPassed":True,"correctionNoticeReviewed":True,
        "noObjectionForPaper":True,"noCorrectionForThisQuestion":False,
        "correctionForQuestionReviewed":False,"officialNoticeStatus":"no_objection_submitted",
        "officialNoticePath":NOTICE_REL,"originalOfficialAnswerImagePath":ANSWER_REL,
        "originalOfficialAnswerImageSha256":ANSWER_SHA,"originalOfficialAnswerImageGitBlob":ANSWER_BLOB,
        "originalSourcePageSha256":PAGE_SHA,"originalSingleQuestionWebpSha256":SINGLE_SHA,
        "sourceQuestionRevision":REV,"sourceTableTextSha256":TABLE_TEXT_SHA,
        "directPublishedAnswerRecord":CERT_REL,"directPublishedAnswerRecordGitBlob":CERT_BLOB,
        "originalOfficialAnswerPdfNewlyRehashedThisTask":False,
        "publishedOriginalAnswerB":True,"sourceOnly":True,"independentE":False,
        "studentReady":False,"studentLive":False
    }
    gate("finalAnswer" not in g2 and "officialPdfSha256" not in g2,"G2 may not disclose answer")
    return g2,g3

def generate():
    bank,man,oldq,m,stage,proof,author,oldrows=source_originals()
    original={x["questionId"]:canon(x) for x in bank["questions"] if x["questionId"]!=QID}
    revised=copy.deepcopy(oldq)
    revised["question"]=stage["source"]["question"]
    revised["options"]=EXPECTED_OPTIONS
    revised["tables"]=tables(stage["source"]["table"])
    revised["questionVerified"]=True
    revised["textQaStatus"]="PASS"
    revised["imageQaStatus"]="PASS"
    revised["answerVerified"]=True
    revised["officialFinalAnswer"]="B"
    revised["officialCorrectionChecked"]=True
    revised["officialAnswerQaStatus"]="PASS_FINAL_OFFICIAL_ANSWER_AND_NO_OBJECTION_NOTICE"
    revised["reviewStatus"]="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI"
    revised["integrationReady"]=False
    revised["correctionVersion"]="ROLE_A_ORIGINAL_2X3_TABLE_SINGLE_QID_20261110"
    revised["issues"]=[]
    revised["extraction"]["correctionOverlay"]={
        "origin":"ROLE_A_ARCHIVED_ORIGINAL_MATHB23_2X3_WEBP",
        "sourceStagePath":STAGE_REL,"sourceStageGitBlob":STAGE_BLOB,
        "tableEvidencePath":TABLE_REL,"tableEvidenceGitBlob":TABLE_BLOB,
        "tableTextSha256":TABLE_TEXT_SHA,"questionRevision":REV,
        "sourceTables":revised["tables"],"originalRawOcrPreserved":True
    }
    revised["extraction"]["ocrReviewStatus"]="PASS_SOURCE_G2_ORIGINAL_2X3_TABLE"
    revised["extraction"]["correctedAt"]="2026-11-10"
    revised["answerProvenance"]["officialRevisionChecked"]=True
    revised["answerProvenance"]["independentVisualVerification"]=True
    gate(revised["tables"]==author["sourceTables"],"canonical 2x3 mismatch")
    gate(not revised.get("studentReleaseApproved",False) and not revised.get("teachingQaStatus")=="PASS" and not revised.get("uiQaStatus")=="PASS","source cannot self-publish")
    for rel,b in ((STAGE_REL,STAGE_BLOB),(TABLE_REL,TABLE_BLOB)):
        src=ROOT/"_role_a_stage"/rel
        dst=ROOT/rel
        gate(not dst.exists(),"unexpected existing copied evidence "+rel)
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        gate(blob(dst.read_bytes())==b,"copied original evidence changed")
    g2,g3=issuers(revised,stage,stage["source"]["table"])
    write_new(G2_REL,g2)
    write_new(G3_REL,g3)
    revised["textQaEvidence"]={
        "reviewer":"ROLE A real archived original source/table evidence; not E",
        "reviewedAt":"2026-11-10","evidencePath":G2_REL,
        "evidenceSha256":sha(read(G2_REL)),"questionRevision":REV,
        "sourceImageSha256":PAGE_SHA,"originalTableSha256":TABLE_TEXT_SHA
    }
    revised["officialFinalQaEvidence"]={
        "reviewer":"ROLE A original 115 MathB printed B; not E",
        "reviewedAt":"2026-11-10","evidencePath":G3_REL,
        "evidenceSha256":sha(read(G3_REL)),"answerPdfSha256":ANSWER_PDF,
        "finalCorrectionsReviewed":True
    }
    index=next(i for i,x in enumerate(bank["questions"]) if x["questionId"]==QID)
    bank["questions"][index]=revised
    gate(all(canon(x)==original[x["questionId"]] for x in bank["questions"] if x["questionId"]!=QID),"other 204 canonical question objects edited")
    old_raw=read(BANK_REL)
    gate(old_raw==(json.dumps(json.loads(old_raw),ensure_ascii=False,indent=2)+"\n").encode("utf8"),"205 bank original format drift")
    (ROOT/BANK_REL).write_text(json.dumps(bank,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    payload=canon(revised).decode("utf8")
    db=BASE/"question-bank.sqlite3"
    with sqlite3.connect(db) as c:
        cur=c.execute("UPDATE questions SET question=?,answer=?,answer_verified=?,question_verified=?,review_status=?,payload_json=?,payload_sha256=? WHERE question_id=?",
          (revised["question"],"B",1,1,revised["reviewStatus"],payload,sha(payload.encode("utf8")),QID))
        gate(cur.rowcount==1,"SQLite must update Q23 once")
        c.commit()
    updated=db_rows(db)
    gate({k:v for k,v in updated.items() if k!=QID}=={k:v for k,v in oldrows.items() if k!=QID},"204 other full 14-column SQLite rows changed")
    gate(updated[QID][9]==1 and updated[QID][10]==1,"new actual Q23 SQLite verified flags")
    gate(all(json.loads(updated[x["questionId"]][12])==x for x in bank["questions"]),"205 JSON/SQLite exact parity")
    inv=js(INVENTORY_REL)
    inv["sqlite"]["performed"]=True
    inv["sqlite"]["rows"]=205
    inv["sqlite"]["shaMismatches"]=[]
    inv["sqlite"]["roundtripPass"]=True
    inv["sqlite"]["sourceQuestionsSha256"]=sha(read(BANK_REL))
    inv["sqlite"]["dbSha256"]=sha(read(SQLITE_REL))
    inv["sqlite"]["evidencePath"]=SQL_REPORT
    inv["sqlite"]["releaseApproved"]=False
    (ROOT/INVENTORY_REL).write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    write_new(SQL_REPORT,{
        "schemaVersion":1,"year":115,"questionId":QID,"taskId":TASK,"qaBaseSha":QA_BASE,
        "beforeBankGitBlob":QA_BANK_BLOB,"beforeSqliteGitBlob":QA_DB_BLOB,
        "beforeManifestGitBlob":QA_MANIFEST_BLOB,
        "afterQuestionBankSha256":sha(read(BANK_REL)),"afterSqliteSha256":sha(read(SQLITE_REL)),
        "sqliteIntegrity":"ok","sqliteRows":205,"canonical205PayloadsMatched":True,
        "onlyUpdatedQid":QID,"other204RowsOriginalFullTupleUnchanged":True,
        "other204CanonicalSourceUnchanged":True,"manifestEntireFileUnchanged":True,
        "originalTableColumns":3,"originalTableDataRows":2,
        "ready":False,"live":False
    })
    write_new(REPORT_REL,{
        "schemaVersion":1,"year":115,"questionId":QID,"role":"A","taskId":TASK,
        "claim":CLAIM,"baseCommit":QA_BASE,"originalSourceStageGitBlob":STAGE_BLOB,
        "originalSourceTableEvidenceGitBlob":TABLE_BLOB,
        "questionRevision":REV,"tableTextSha256":TABLE_TEXT_SHA,
        "originalSingleWebpSha256":SINGLE_SHA,"originalPageSha256":PAGE_SHA,
        "originalAnswerImageSha256":ANSWER_SHA,
        "originalSourcePdfSha256PreviouslyRecorded":SOURCE_PDF,
        "officialAnswerPdfSha256PreviouslyRecorded":ANSWER_PDF,
        "g1VisualCertificateSha256":G1_CERT,"officialMathBNotice":"no_objection_submitted",
        "officialPublishedLetter":"B",
        "independentSourceMathCheck":"2*x - 3000 = 1.8*(x+2000); x=33000 B; both totals 63000",
        "publisherOcrEvidencePath":G2_REL,"publisherOcrEvidenceSha256":sha(read(G2_REL)),
        "publisherOfficialEvidencePath":G3_REL,"publisherOfficialEvidenceSha256":sha(read(G3_REL)),
        "noNewPdfDownloadOrRehash":True,"noWebpRecreation":True,
        "sourceQuestionVerified":True,"officialAnswerVerified":True,
        "other204JsonRowsUnchanged":True,"other204SqliteRowsUnchanged":True,
        "sqliteRows":205,"formalETrust":False,"formalDRealEmitter16":False,
        "studentReady":False,"newLive":False,
        "status":"SOURCE_ONLY_G1_G2_G3_2X3_TABLE_COMPLETE_E_D_MASTER_HOLD"
    })
    print("MB23 SOURCE 2x3 TABLE 205 JSON/SQLITE ONE-Q WRITTEN; 204 UNCHANGED; NO READY/LIVE")

def verify():
    b=js(BANK_REL)
    man=js(MANIFEST_REL)
    inv=js(INVENTORY_REL)
    receipt=js(REPORT_REL)
    q=next(x for x in b["questions"] if x["questionId"]==QID)
    m=next(x for x in man["items"] if x["questionId"]==QID)
    gate(len(b["questions"])==len(man["items"])==205,"post-205")
    gate(q["questionVerified"] and q["answerVerified"] and q["textQaStatus"]=="PASS" and q["reviewStatus"]=="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI","source-only verified")
    gate(q["question"]==js(STAGE_REL)["source"]["question"] and q["options"]==EXPECTED_OPTIONS,"Q23 clean original text and options")
    table=js(STAGE_REL)["source"]["table"]
    assert_table(table)
    gate(q["tables"]==tables(table),"canonical complete 2x3 structured source table absent")
    gate(js(G2_REL)["sourceTables"]==q["tables"] and js(G2_REL)["tableTextSha256"]==TABLE_TEXT_SHA,"G2 issuer table original data mismatch")
    gate(sha(js(TABLE_REL)["originalTextAndTable"]["sourceRevisionSeed"].encode("utf8"))==REV,"true A-source revision")
    gate(q["textQaEvidence"]["questionRevision"]==REV and q["textQaEvidence"]["originalTableSha256"]==TABLE_TEXT_SHA,"G2 table revision not bound")
    gate(blob(read(MANIFEST_REL))==QA_MANIFEST_BLOB and m["sha256"]==SINGLE_SHA and m["visualReviewEvidence"]["referenceSha256"]==G1_CERT,"original 205 image manifest changed")
    gate(blob(read(STAGE_REL))==STAGE_BLOB and blob(read(TABLE_REL))==TABLE_BLOB,"A old original source immutable")
    webp(WEBP_REL,SINGLE_SHA,SINGLE_BLOB)
    webp(PAGE_REL,PAGE_SHA,PAGE_BLOB)
    webp(ANSWER_REL,ANSWER_SHA,ANSWER_BLOB)
    db=db_rows(BASE/"question-bank.sqlite3")
    gate(all(json.loads(db[x["questionId"]][12])==x for x in b["questions"]),"post 205 JSON/SQLite mismatch")
    gate(sha(read(BANK_REL))==inv["sqlite"]["sourceQuestionsSha256"] and sha(read(SQLITE_REL))==inv["sqlite"]["dbSha256"],"post inventory HASH mismatch")
    gate(receipt["publisherOcrEvidenceSha256"]==sha(read(G2_REL)) and receipt["publisherOfficialEvidenceSha256"]==sha(read(G3_REL)),"issuer G2/G3 bytes changed")
    gate(q["textQaEvidence"]["evidenceSha256"]==receipt["publisherOcrEvidenceSha256"] and q["officialFinalQaEvidence"]["evidenceSha256"]==receipt["publisherOfficialEvidenceSha256"],"issuer G2 G3 not SHA-bound")
    gate(not q.get("studentReleaseApproved",False) and q.get("teachingQaStatus")!="PASS" and q.get("uiQaStatus")!="PASS","source-only cannot self-release")
    sys.path.insert(0,str(ROOT/"_publisher_main"))
    from scripts import sudu_verified_publish as pub
    gate(pub.image_proof(q,m,{},ROOT) and pub.visual_certificate(ROOT,m,QID) and pub.verify_bytes(ROOT,WEBP_REL,SINGLE_SHA),"original source publisher image G1")
    t,f=pub.source_proof(q,True,True,REV)
    gate(t and f,"native publisher G2 or G3 source proof failed")
    g2=pub.review_document(ROOT,115,G2_REL,QID)
    g3=pub.review_document(ROOT,115,G3_REL,QID)
    gate(g2 and g3,"native publisher issuer file read fail")
    gate(g2[0]["question"]==q["question"] and g2[0]["options"]==q["options"] and g2[0]["sourceTables"]==q["tables"] and g2[0]["questionRevision"]==REV,"issuer cannot match 2x3 original table")
    gate(g3[0]["finalAnswer"]=="B" and g3[0]["officialPdfSha256"]==ANSWER_PDF and pub.official_notice_scope_certified(ROOT,115,q,g3[0]),"original published official B/no objection G3")
    gate(not pub.certificates_complete(ROOT,q,m,{}),"false E/trust student certificate")
    negative(pub,q,m,table)
    print(json.dumps({"status":"SOURCE_G1_G2_G3_ORIGINAL_2X3_TABLE_ONLY","qid":QID,"revision":REV,"g2Sha256":g2[1],"g3Sha256":g3[1],"sqliteSha256":inv["sqlite"]["dbSha256"],"studentReady":False,"studentLive":False},ensure_ascii=False))

def negative(pub,q,m,table):
    corrupt=copy.deepcopy(q)
    corrupt["tables"][0]["rows"][1][2]="兩人均打八折 WRONG"
    gate(corrupt["tables"]!=tables(table),"table wrong discount mutant must diverge")
    gate(corrupt["tables"]!=js(G2_REL)["sourceTables"],"source table mutant must fail original issuer match")
    corrupt=copy.deepcopy(q)
    corrupt["textQaEvidence"]["questionRevision"]="0"*64
    gate(not pub.source_proof(corrupt,True,True,REV)[0],"false source SHA must deny")
    corrupt=copy.deepcopy(q)
    corrupt["officialFinalQaEvidence"]["answerPdfSha256"]="0"*64
    gate(not pub.source_proof(corrupt,True,True,REV)[1],"false answer PDF must deny")
    g3=copy.deepcopy(js(G3_REL))
    g3["noObjectionForPaper"]=False
    gate(not pub.official_notice_scope_certified(ROOT,115,q,g3),"false official notice must deny")
    m2=copy.deepcopy(m)
    m2["visualReviewEvidence"]["referenceSha256"]="0"*64
    gate(not pub.visual_certificate(ROOT,m2,QID),"false visual certificate must deny")
    gate("finalAnswer" not in js(G2_REL),"G2 leaked official key")
    gate(not q.get("studentReleaseApproved",False),"source must not release")
    print("MB23 original price table, false G2/G3, WebP, notice, no release negatives PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--apply",action="store_true")
    group.add_argument("--verify",action="store_true")
    a=p.parse_args()
    generate() if a.apply else verify()
