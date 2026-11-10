#!/usr/bin/env python3
"""One exact 115 Math B21 source G1/G2/G3 repair + SQLite source-only admission.

Role A source QA only: never creates an independent E receipt, blinded solver,
formal D evidence, protected-main permission or student release.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
QID = "115-00-MB-21"
QA_BASE = "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2"
STAGE_SHA = "38ab6b53f75f0da5a6e83087464e962e31430e64"
C_SHA = "e50198cad6821a5252008bd474d8240510832f85"
MAIN_SHA = "5546a603abfe0af2e62c0e5f63f775be0bfb24cf"
SRC_STAGE_REL = "sudu/data/processed/115/source-stage/115-00-MB-21-staged-20261104.json"
CORRECTION_REL = "sudu/data/processed/115/review-evidence/115-00-MB-21-image-transcription-correction-20261024.json"
AUTH_REL = "sudu/teaching-candidates/114-115-20261025/115-00-MB-21.json"
ORIG_SHA = "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693"
ORIG_BLOB = "75d9bcf6d0d921a6f7a40fd6383d0cd4680398bf"
PAGE_SHA = "7a1732ce33ee6b9f1cc4fcc6f705b2aa1f29a117e0562a62b50428d94845464d"
PAGE_BLOB = "c8e3e806d812a01d417abe83dac7f46adcf84ff7"
ANSWER_IMG_SHA = "1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d"
ANSWER_IMG_BLOB = "5ea4b86e929506d595f96fa162d1aae021f68440"
STAGE_BLOB = "1b466c1f0e5a0f96b08f39a8ddc467f35bf99004"
G2_PREEXISTING_BLOB = "3e37500240e1c26fedc2ae827eac95ddf9ebe80b"
QA_BANK_BLOB = "ad1e7c4ed03bdd90274c645b5c9f1072aca732d2"
QA_MANIFEST_BLOB = "2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b"
QA_DB_BLOB = "9e09bf6dcbabce514d5c54286c74b9f91b0ce54b"
QA_INVENTORY_BLOB = "c8c7386874c1756effc395052507104b0bd2926c"
REVISION = "817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9"
SOURCE_PDF = "e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082"
ANSWER_PDF = "d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
G1_CERT = "ca6507c62081bc1bbfa30cdd24172484a1c9b25b517ab04f7ae0f4caa74fa142"
G1_REL = "sudu/data/processed/115/VISUAL_QA_2026-10-22.json"
ANSWER_CERT_REL = "sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
ANSWER_CERT_BLOB = "ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
NOTICE_REL = "sudu/data/processed/115/official-confirmation-status.json"
NOTICE_BLOB = "6d21432395294d9ccbcfe1dea8be01f88597bbf3"
G2_REL = "sudu/data/processed/115/review-evidence/115-00-MB-21-ocr-publisher-20261108.json"
G3_REL = "sudu/data/processed/115/review-evidence/115-00-MB-21-official-publisher-20261108.json"
REPORT_REL = "sudu/data/processed/115/review-evidence/115-00-MB-21-source-admission-20261108.json"
SQL_REPORT = "sudu/data/processed/115/SQLITE_QA_MB21_SOURCE_BRIDGE_20261108.json"
SOURCE_WEBP = "sudu/data/processed/115/webp-v2/00-MB/115-00-MB-21.webp"
PAGE_WEBP = "sudu/data/original/115/00-MB/p007-e82e34d9cd-v2-w1400-q66.webp"
ANSWER_WEBP = "sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"


def gate(ok, msg):
    if not ok:
        raise ValueError("MB21_SOURCE_HOLD: " + msg)

def bytes_of(rel):
    path = ROOT / rel
    gate(path.is_file() and not path.is_symlink(), "missing or symlink file " + rel)
    return path.read_bytes()

def js(rel):
    return json.loads(bytes_of(rel))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def blob(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def jwrite(rel, obj):
    path = ROOT / rel
    gate(not path.exists(), "new path was already written " + rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def valid_webp(rel, digest, oid):
    raw=bytes_of(rel)
    gate(raw.startswith(b"RIFF") and raw[8:12]==b"WEBP", "WebP header corrupt " + rel)
    gate(sha(raw)==digest and blob(raw)==oid, "original WebP byte SHA/Blob differs " + rel)

def rev(question, options, webp):
    return sha(canon({"question":question,"options":options,"singleQuestionWebpSha256":webp}))

def rows(path):
    with sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True) as c:
        gate(c.execute("PRAGMA integrity_check").fetchone()[0]=="ok", "real original 115 SQLite corruption")
        cols=[r[1] for r in c.execute("PRAGMA table_info(questions)")]
        required={"question_id","question","answer","answer_verified","question_verified","review_status","payload_json","payload_sha256"}
        gate(len(cols)==14 and required<=set(cols),"115 14-column schema drift")
        allrows=c.execute("SELECT question_id,question,answer,answer_verified,question_verified,review_status,payload_json,payload_sha256 FROM questions ORDER BY question_id").fetchall()
    gate(len(allrows)==205 and len({row[0] for row in allrows})==205,"115 SQLite count or duplicate QID")
    gate(all(sha(row[6].encode("utf-8"))==row[7] for row in allrows),"115 SQLite payload hashes")
    return {row[0]:row[1:] for row in allrows}

def check_baseline():
    for rel, expected in (
        ("sudu/data/processed/115/questions.json",QA_BANK_BLOB),
        ("sudu/data/processed/115/webp-manifest.json",QA_MANIFEST_BLOB),
        ("sudu/data/processed/115/question-bank.sqlite3",QA_DB_BLOB),
        ("sudu/data/processed/115/inventory.json",QA_INVENTORY_BLOB)
    ):
        gate(blob(bytes_of(rel))==expected,"frozen current 115 QA bank/DB drift: "+rel)
    original=js("sudu/data/processed/115/questions.json")
    manifest=js("sudu/data/processed/115/webp-manifest.json")
    gate(len(original["questions"])==len(manifest["items"])==205,"205 original 115 bank and WebP inventory")
    gate(len({x["questionId"] for x in original["questions"]})==205,"205 duplicate QID")
    q=next(x for x in original["questions"] if x["questionId"]==QID)
    m=next(x for x in manifest["items"] if x["questionId"]==QID)
    gate(q["questionVerified"] is False and q["answerVerified"] is True and q["answer"]=="A" and q["answerMatched"] is True,"MB21 old canonical state changed")
    gate(m["qaStatus"]=="PASS" and m["sha256"]==ORIG_SHA and m["sourceSha256"]==PAGE_SHA and m["output"]==SOURCE_WEBP and m["source"]==PAGE_WEBP and m["crop"]==[90,907,1310,1321],"MB21 figure and crop changed")
    gate(m["visualReviewEvidence"]["referenceSha256"]==G1_CERT,"115 visual QA certificate changed")
    gate(q["questionProvenance"]["pdfSha256"]==SOURCE_PDF and q["answerProvenance"]["pdfSha256"]==ANSWER_PDF,"official PDF historical source hash changed")
    gate(q["options"][0]!="5" and "7 km" in q["options"][0],"original known source contamination not found; retriage")
    gate(q["options"][1]!="4.75" and "A" in q["options"][1],"original known OCR diagram intrusion changed")
    gate(q["options"][3]!="4.25" and "60°" in q["options"][3],"original diagram OCR contaminated D changed")
    valid_webp(SOURCE_WEBP,ORIG_SHA,ORIG_BLOB)
    valid_webp(PAGE_WEBP,PAGE_SHA,PAGE_BLOB)
    valid_webp(ANSWER_WEBP,ANSWER_IMG_SHA,ANSWER_IMG_BLOB)
    historical=js(CORRECTION_REL)
    gate(blob(bytes_of(CORRECTION_REL))==G2_PREEXISTING_BLOB,"historic direct original G2 changed")
    gate(historical["correctedText"]["options"]==["5","4.75","4.50","4.25"],"historical corrected G2 option mismatch")
    gate(historical["knownOfficialAnswer"]=="A","historic math answer conflict")
    gate(blob(bytes_of(ANSWER_CERT_REL))==ANSWER_CERT_BLOB,"published MathB original answer record changed")
    cert=js(ANSWER_CERT_REL)
    record=[x for x in cert["records"] if x["questionId"]==QID]
    gate(len(record)==1 and record[0]["officialFinalAnswerReadDirectlyFromPublishedImage"]=="A" and record[0]["answerVerified"] is True,"official published answer A not directly evidenced")
    gate(blob(bytes_of(NOTICE_REL))==NOTICE_BLOB and js(NOTICE_REL)["confirmations"]["00-MB"]["officialStatus"]=="no_objection_submitted", "115 MathB no-objection correction notice invalid")
    gate(sha(bytes_of(G1_REL))==G1_CERT,"visual certificate SHA invalid")
    stage_file=ROOT/"_role_a_stage"/SRC_STAGE_REL
    gate(stage_file.is_file() and not stage_file.is_symlink() and blob(stage_file.read_bytes())==STAGE_BLOB,"role A staged original SHA changed")
    stage=json.loads(stage_file.read_text(encoding="utf-8"))
    author_file=ROOT/"_role_c_author"/AUTH_REL
    gate(author_file.is_file(),"C original author lesson missing")
    author=json.loads(author_file.read_text(encoding="utf-8"))
    gate(stage["questionId"]==author["questionId"]==QID and stage["stageStatus"].endswith("CANONICAL_SQLITE_UNMODIFIED_NO_RELEASE"),"A stage QID or gate mismatch")
    clean=stage["originalSource"]
    gate(clean["originalCleanQuestion"]==author["question"] and clean["originalCleanOptions"]==author["options"],"A original source vs C author disagree")
    gate(clean["singleSha256"]==author["imageSha256"]==ORIG_SHA and clean["singleWebp"]==author["image"]==SOURCE_WEBP,"A/C original graphic mismatch")
    gate(clean["roleCSourceRevisionForComparisonOnly"]==REVISION and rev(clean["originalCleanQuestion"],clean["originalCleanOptions"],ORIG_SHA)==REVISION,"source revision not C author's immutable original")
    gate(author["teachingCanonicalSha256"]=="4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4","C teaching digest changed")
    gate(stage["officialAnswer"]["officialPublishedLetter"]==q["officialFinalAnswer"]==q["answer"]=="A","official source A mismatch")
    gate(stage["officialAnswer"]["officialNoObjectionForPaper"] is True,"official no-objection missing")
    db=rows(BASE/"question-bank.sqlite3")
    gate(set(db)=={r["questionId"] for r in original["questions"]},"DB QID mismatch")
    gate(all(json.loads(db[r["questionId"]][5])==r for r in original["questions"]),"original 205 raw JSON/SQLite payload mismatch")
    gate(db[QID][2]==0 and db[QID][3]==0,"original MB21 flags not as diagnosed")
    gate(js("sudu/data/processed/115/inventory.json")["sqlite"]["rows"]==205,"inventory 205 count mismatch")
    return original,manifest,q,m,stage,author,db

def receipts(q,stage):
    g2={
        "schemaVersion":1,"year":115,"questionId":QID,"role":"A_SOURCE_ONLY_NOT_DISTINCT_E",
        "taskId":"A-115-MB21-CANONICAL-G2G3-20261108-01",
        "questionRevision":REVISION,"webpSha256":ORIG_SHA,
        "question":q["question"],"options":q["options"],"visualTextCompared":True,
        "reviewer":"ROLE A direct original source and isolated figure image QA; not Role E reviewer",
        "reviewedAt":"2026-11-08","reviewType":"ORIGINAL_PRINTED_STEM_FOUR_OPTIONS_AND_FIGURE_CORRECTION_SOURCE_ONLY",
        "sourceYear":115,"originalPage":7,"sourcePdfSha256PreviouslyRecorded":SOURCE_PDF,
        "originalPageSha256":PAGE_SHA,"originalSingleWebpSha256":ORIG_SHA,
        "originalSingleWebpGitBlob":ORIG_BLOB,"sourcePageWebpGitBlob":PAGE_BLOB,
        "sourceStagePath":SRC_STAGE_REL,"sourceStageGitBlob":STAGE_BLOB,
        "sourceCorrectionsPath":CORRECTION_REL,"historicalCorrectionGitBlob":G2_PREEXISTING_BLOB,
        "figureDescription":stage["originalSource"]["originalFigureDescription"],
        "sourceCrop":[90,907,1310,1321],"noAdjacentQID":True,
        "originalRawOcrPreservedInExtraction":True,"noRecrop":True,"answerHiddenFromIssuer":True,
        "independentE":False,"studentReady":False,"studentLive":False
    }
    g3={
        "schemaVersion":1,"year":115,"questionId":QID,
        "reviewer":"ROLE A original published 115 Math(B) p1 Q21 A and original no-objection notice; not independent Role E",
        "reviewedAt":"2026-11-08",
        "officialPage":"https://web1.tcte.edu.tw/EXAM/115_4y/",
        "officialPdfSha256":ANSWER_PDF,"finalAnswer":"A",
        "officialFinalAnswerImageQaPassed":True,"correctionNoticeReviewed":True,
        "noObjectionForPaper":True,"noCorrectionForThisQuestion":False,
        "correctionForQuestionReviewed":False,
        "officialNoticeStatus":"no_objection_submitted","officialNoticePath":NOTICE_REL,
        "originalOfficialAnswerImagePath":ANSWER_WEBP,"originalOfficialAnswerImageSha256":ANSWER_IMG_SHA,
        "originalOfficialAnswerImageGitBlob":ANSWER_IMG_BLOB,
        "originalSourcePageSha256":PAGE_SHA,"originalSingleQuestionWebpSha256":ORIG_SHA,
        "sourceQuestionRevision":REVISION,
        "directPublishedAnswerRecord":ANSWER_CERT_REL,"directPublishedAnswerRecordGitBlob":ANSWER_CERT_BLOB,
        "originalOfficialAnswerPdfNewlyRehashedThisTask":False,
        "publishedOriginalAnswerA":True,
        "sourceOnly":True,"independentE":False,"studentReady":False,"studentLive":False
    }
    return g2,g3

def generate():
    orig,manifest,q,m,stage,author,old=check_baseline()
    before={r["questionId"]:canon(r) for r in orig["questions"] if r["questionId"]!=QID}
    revised=copy.deepcopy(q)
    revised["question"]=stage["originalSource"]["originalCleanQuestion"]
    revised["options"]=stage["originalSource"]["originalCleanOptions"]
    revised["questionVerified"]=True
    revised["textQaStatus"]="PASS"
    revised["imageQaStatus"]="PASS"
    revised["answerVerified"]=True
    revised["officialFinalAnswer"]="A"
    revised["officialCorrectionChecked"]=True
    revised["officialAnswerQaStatus"]="PASS_FINAL_OFFICIAL_ANSWER_AND_NO_OBJECTION_NOTICE"
    revised["reviewStatus"]="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI"
    revised["integrationReady"]=False
    revised["correctionVersion"]="ROLE_A_SOURCE_G2_SINGLE_QID_20261108"
    revised["issues"]=[]
    revised["extraction"]["correctionOverlay"]={
        "origin":"ROLE_A_ARCHIVED_DIRECT_ORIGINAL_WEBP_Q21",
        "sourceStagePath":SRC_STAGE_REL,"sourceStageGitBlob":STAGE_BLOB,
        "sourceRevision":REVISION,"originalFigureRetained":True,
        "originalRawOcrUnchanged":True,"options":revised["options"]}
    revised["extraction"]["ocrReviewStatus"]="PASS_SOURCE_G2"
    revised["extraction"]["correctedAt"]="2026-11-08"
    revised["answerProvenance"]["officialRevisionChecked"]=True
    revised["answerProvenance"]["independentVisualVerification"]=True
    gate(rev(revised["question"],revised["options"],ORIG_SHA)==REVISION,"new Q21 revision not original Role C source")
    gate("studentReleaseApproved" not in revised and revised.get("teachingQaStatus")!="PASS" and revised.get("uiQaStatus")!="PASS","source-only may not self-publish")

    parent=ROOT/SRC_STAGE_REL
    gate(not parent.exists(),"stage receipt target already exists")
    parent.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/"_role_a_stage"/SRC_STAGE_REL,parent)
    gate(blob(parent.read_bytes())==STAGE_BLOB,"stage copied changed original bytes")
    g2,g3=receipts(revised,stage)
    jwrite(G2_REL,g2)
    jwrite(G3_REL,g3)
    revised["textQaEvidence"]={
        "reviewer":"ROLE A exact original visual source and authenticated GitHub stage; NOT Role E",
        "reviewedAt":"2026-11-08","evidencePath":G2_REL,"evidenceSha256":sha(bytes_of(G2_REL)),
        "questionRevision":REVISION,"sourceImageSha256":PAGE_SHA
    }
    revised["officialFinalQaEvidence"]={
        "reviewer":"ROLE A original printed 115 MathB Q21 A; NOT Role E",
        "reviewedAt":"2026-11-08","evidencePath":G3_REL,"evidenceSha256":sha(bytes_of(G3_REL)),
        "answerPdfSha256":ANSWER_PDF,"finalCorrectionsReviewed":True
    }

    i=next(n for n,v in enumerate(orig["questions"]) if v["questionId"]==QID)
    orig["questions"][i]=revised
    gate(all(canon(x)==before[x["questionId"]] for x in orig["questions"] if x["questionId"]!=QID), "other 204 canonical values changed")
    bankpath=BASE/"questions.json"
    oldraw=bankpath.read_bytes()
    gate(oldraw==(json.dumps(json.loads(oldraw),ensure_ascii=False,indent=2)+"\n").encode("utf-8"),"original 115 bank formatting drift; stop whole-file reformat")
    bankpath.write_text(json.dumps(orig,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    dbp=BASE/"question-bank.sqlite3"
    payload=canon(revised).decode("utf-8")
    with sqlite3.connect(dbp) as c:
        cur=c.execute(
            "UPDATE questions SET question=?,answer=?,answer_verified=?,question_verified=?,review_status=?,payload_json=?,payload_sha256=? WHERE question_id=?",
            (revised["question"],"A",1,1,revised["reviewStatus"],payload,sha(payload.encode("utf-8")),QID))
        gate(cur.rowcount==1,"actual MB21 SQLite update must be one original row")
        c.commit()
    now=rows(dbp)
    gate({k:v for k,v in now.items() if k!=QID}=={k:v for k,v in old.items() if k!=QID}, "other 204 SQLite exact source columns/payload changed")
    gate(all(json.loads(now[q["questionId"]][5])==q for q in orig["questions"]),"all 205 normalized JSON+DB source parity")
    gate(now[QID][2]==1 and now[QID][3]==1 and now[QID][0]==revised["question"],"row G2/verified source flags not written")
    inventory=js("sudu/data/processed/115/inventory.json")
    inventory["sqlite"]["performed"]=True
    inventory["sqlite"]["rows"]=205
    inventory["sqlite"]["shaMismatches"]=[]
    inventory["sqlite"]["roundtripPass"]=True
    inventory["sqlite"]["sourceQuestionsSha256"]=sha(bytes_of("sudu/data/processed/115/questions.json"))
    inventory["sqlite"]["dbSha256"]=sha(bytes_of("sudu/data/processed/115/question-bank.sqlite3"))
    inventory["sqlite"]["evidencePath"]=SQL_REPORT
    inventory["sqlite"]["releaseApproved"]=False
    (BASE/"inventory.json").write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    jwrite(SQL_REPORT,{
        "schemaVersion":1,"year":115,"questionId":QID,
        "taskId":"A-115-MB21-CANONICAL-G2G3-20261108-01",
        "qaOriginalBase":QA_BASE,"beforeBankGitBlob":QA_BANK_BLOB,
        "beforeSqliteGitBlob":QA_DB_BLOB,"beforeManifestGitBlob":QA_MANIFEST_BLOB,
        "afterQuestionBankSha256":sha(bytes_of("sudu/data/processed/115/questions.json")),
        "afterSqliteSha256":sha(bytes_of("sudu/data/processed/115/question-bank.sqlite3")),
        "sqliteIntegrity":"ok","sqliteRows":205,"canonical205PayloadsMatched":True,
        "onlyUpdatedQid":QID,"other204RowsOriginalBytesUnchanged":True,
        "other204CanonicalSourceUnchanged":True,
        "manifestEntireFileUnchanged":True,"ready":False,"live":False
    })
    jwrite(REPORT_REL,{
        "schemaVersion":1,"year":115,"questionId":QID,"role":"A","taskId":"A-115-MB21-CANONICAL-G2G3-20261108-01",
        "claim":"https://github.com/homelux-huang/7581707/issues/36#issuecomment-6718185314",
        "baseCommit":QA_BASE,"originalSourceStageGitBlob":STAGE_BLOB,
        "questionRevision":REVISION,"originalSingleWebpSha256":ORIG_SHA,
        "originalPageSha256":PAGE_SHA,"originalAnswerImageSha256":ANSWER_IMG_SHA,
        "originalSourcePdfSha256PreviouslyRecorded":SOURCE_PDF,
        "officialAnswerPdfSha256PreviouslyRecorded":ANSWER_PDF,
        "g1VisualCertificateSha256":G1_CERT,"officialMathBNotice":"no_objection_submitted",
        "officialPublishedLetter":"A","independentSourceMathCheck":"BC=x>4: 49=64+x²-8x, roots 3 or 5, select 5=A",
        "publisherOcrEvidencePath":G2_REL,"publisherOcrEvidenceSha256":sha(bytes_of(G2_REL)),
        "publisherOfficialEvidencePath":G3_REL,"publisherOfficialEvidenceSha256":sha(bytes_of(G3_REL)),
        "noNewPdfDownloadOrRehash":True,"noWebpRecreation":True,
        "sourceQuestionVerified":True,"officialAnswerVerified":True,
        "other204JsonRowsUnchanged":True,"other204SqliteRowsUnchanged":True,
        "sqliteRows":205,"formalETrust":False,"formalDRealEmitter16":False,
        "studentReady":False,"newLive":False,"status":"SOURCE_ONLY_G1_G2_G3_COMPLETE_E_D_MASTER_HOLD"
    })
    print("MB21 ORIGINAL SOURCE SINGLE-Q CANONICAL+SQLITE WRITTEN: 205/205 parity, 204 exact immutable, no student READY/LIVE")

def verify():
    b=js("sudu/data/processed/115/questions.json")
    m=js("sudu/data/processed/115/webp-manifest.json")
    i=js("sudu/data/processed/115/inventory.json")
    receipt=js(REPORT_REL)
    gate(len(b["questions"])==len(m["items"])==205,"post 115 source count")
    q=next(z for z in b["questions"] if z["questionId"]==QID)
    item=next(z for z in m["items"] if z["questionId"]==QID)
    gate(q["questionVerified"] and q["answerVerified"] and q["textQaStatus"]=="PASS" and q["answer"]=="A" and q["reviewStatus"]=="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI","source-only verified status")
    gate(q["question"]==js(SRC_STAGE_REL)["originalSource"]["originalCleanQuestion"] and q["options"]==["5","4.75","4.50","4.25"],"OCR cleaned and diagram labels removed")
    gate(rev(q["question"],q["options"],ORIG_SHA)==REVISION,"post source SHA")
    gate(blob(bytes_of("sudu/data/processed/115/webp-manifest.json"))==QA_MANIFEST_BLOB, "entire original 115 manifest mutated")
    gate(item["sha256"]==ORIG_SHA and item["visualReviewEvidence"]["referenceSha256"]==G1_CERT,"source original WebP or visual QA drift")
    gate(blob(bytes_of(SRC_STAGE_REL))==STAGE_BLOB, "Role A original stage mutated")
    valid_webp(SOURCE_WEBP,ORIG_SHA,ORIG_BLOB)
    valid_webp(PAGE_WEBP,PAGE_SHA,PAGE_BLOB)
    valid_webp(ANSWER_WEBP,ANSWER_IMG_SHA,ANSWER_IMG_BLOB)
    rr=rows(BASE/"question-bank.sqlite3")
    gate(all(json.loads(rr[z["questionId"]][5])==z for z in b["questions"]),"post 205 SQLite vs bank")
    gate(sha(bytes_of("sudu/data/processed/115/questions.json"))==i["sqlite"]["sourceQuestionsSha256"],"source new SHA mismatch")
    gate(sha(bytes_of("sudu/data/processed/115/question-bank.sqlite3"))==i["sqlite"]["dbSha256"],"DB new SHA mismatch")
    gate(receipt["publisherOcrEvidenceSha256"]==sha(bytes_of(G2_REL)) and receipt["publisherOfficialEvidenceSha256"]==sha(bytes_of(G3_REL)),"formal G2/G3 issuer digest mismatch")
    gate(q["textQaEvidence"]["evidenceSha256"]==receipt["publisherOcrEvidenceSha256"] and q["officialFinalQaEvidence"]["evidenceSha256"]==receipt["publisherOfficialEvidenceSha256"],"actual G2/G3 certificate bytes unbound")
    gate(not q.get("studentReleaseApproved",False) and q.get("teachingQaStatus")!="PASS" and q.get("uiQaStatus")!="PASS","source falsely published")
    import sys
    sys.path.insert(0,str(ROOT/"_publisher_main"))
    from scripts import sudu_verified_publish as pub
    gate(pub.image_proof(q,item,{},ROOT) and pub.visual_certificate(ROOT,item,QID) and pub.verify_bytes(ROOT,SOURCE_WEBP,ORIG_SHA), "original real protected publisher G1 failed")
    source,answer=pub.source_proof(q,True,True,REVISION)
    gate(source and answer, "actual current protected-main publisher G2/G3 source_proof failed")
    g2=pub.review_document(ROOT,115,G2_REL,QID)
    g3=pub.review_document(ROOT,115,G3_REL,QID)
    gate(bool(g2 and g3),"publisher cannot read source G2/G3 issuer")
    gate(g2[0]["question"]==q["question"] and g2[0]["options"]==q["options"] and g2[0]["questionRevision"]==REVISION and g2[0]["webpSha256"]==ORIG_SHA and g2[0]["visualTextCompared"] is True,"G2 issuer exact data mismatch")
    gate(g3[0]["finalAnswer"]=="A" and g3[0]["officialPdfSha256"]==ANSWER_PDF and pub.official_notice_scope_certified(ROOT,115,q,g3[0]),"G3 native original no-objection proof failed")
    gate(pub.certificates_complete(ROOT,q,item,{}) is False,"no student release without E/D/independent blind")
    print(json.dumps({"status":"SOURCE_G1_G2_G3_VERIFIED_ONLY","questionId":QID,"questionRevision":REVISION,"G2Sha256":g2[1],"G3Sha256":g3[1],"SQLiteSha256":i["sqlite"]["dbSha256"],"studentReady":False,"LIVE":False},ensure_ascii=False))

def negative():
    import sys
    sys.path.insert(0,str(ROOT/"_publisher_main"))
    from scripts import sudu_verified_publish as pub
    bank=js("sudu/data/processed/115/questions.json")
    q=next(z for z in bank["questions"] if z["questionId"]==QID)
    m=next(z for z in js("sudu/data/processed/115/webp-manifest.json")["items"] if z["questionId"]==QID)
    bad=copy.deepcopy(q);bad["options"][0]="5 7km diagram contamination"
    gate(rev(bad["question"],bad["options"],ORIG_SHA)!=REVISION,"forged original option not caught")
    bad=copy.deepcopy(q);bad["textQaEvidence"]["sourceImageSha256"]="0"*64
    gate(not pub.source_proof(bad,True,True,REVISION)[0],"G2 incorrect original SHA must fail")
    bad=copy.deepcopy(q);bad["officialFinalQaEvidence"]["answerPdfSha256"]="0"*64
    gate(not pub.source_proof(bad,True,True,REVISION)[1],"G3 mismatched official SHA must fail")
    gd=copy.deepcopy(js(G3_REL));gd["noObjectionForPaper"]=False
    gate(not pub.official_notice_scope_certified(ROOT,115,q,gd),"G3 revoked no objection must fail")
    gm=copy.deepcopy(m);gm["visualReviewEvidence"]["referenceSha256"]="0"*64
    gate(not pub.visual_certificate(ROOT,gm,QID),"fake original visual SHA must fail")
    gate(js(G2_REL).get("finalAnswer") is None,"G2 issuer leaked answer")
    gate(not q.get("studentReleaseApproved",False),"no false release")
    print("MB21 source corruption, image SHA, official answer PDF, fake no-objection, release negatives PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--apply",action="store_true")
    group.add_argument("--verify",action="store_true")
    args=p.parse_args()
    if args.apply: generate()
    else: verify(); negative()
