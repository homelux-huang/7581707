#!/usr/bin/env python3
"""ROLE A: single-QID 115 Math B20 original v5 figure, canonical & SQLite source-only.
Neither an independent teaching E receipt nor formal student release.
"""
from __future__ import annotations
import argparse,copy,hashlib,io,json,shutil,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
QID="115-00-MB-20"
TASK="A-115-MB20-CANONICAL-V5-PIXEL-G2G3-20261110-02"
CLAIM="https://github.com/homelux-huang/7581707/issues/36#issuecomment-6769081931"
PARENT="24f8962b7fb51a8baa6f111abb1a7414a4b26420"
BANK_BLOB="4b1b167ca7bbc3d1a8fa7441a80318965450aa91"
DB_BLOB="84ce71800b760664b3d2f8bd0bd69bfebc974783"
INVENTORY_BLOB="372d454e4f40210a6eebcaa5930b789284ebd4ca"
MANIFEST_BLOB="2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b"
A_STAGE_HEAD="80f87ddcbc1de06202a59d45e12557a20cc1394c"
C_AUTHOR_HEAD="e50198cad6821a5252008bd474d8240510832f85"
E_IMAGE_HEAD="4f70fe9fccbd2b783524d0f8a74290a39373c413"
SOURCE_REV="2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c"
TEACHING_SHA="2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d"
SINGLE_SHA="f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf"
SINGLE_BLOB="bd77281f8ee755074cf3b7ebcada5c06f3720c12"
PAGE_SHA="7a1732ce33ee6b9f1cc4fcc6f705b2aa1f29a117e0562a62b50428d94845464d"
PAGE_BLOB="c8e3e806d812a01d417abe83dac7f46adcf84ff7"
OLD_V2_SHA="26a407982e66ac5196fa38a8e45d3fcb684fe7de53453891b2b5a414f1582ba9"
OLD_V2_BLOB="fb055f43e0d186343015a6f6542cdc302e9ef5d5"
ANS_SHA="1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d"
ANS_BLOB="5ea4b86e929506d595f96fa162d1aae021f68440"
SOURCE_PDF="e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082"
ANS_PDF="d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
G1_CERT="ca6507c62081bc1bbfa30cdd24172484a1c9b25b517ab04f7ae0f4caa74fa142"
STAGE_REL="sudu/data/processed/115/source-stage/115-00-MB-20-v5-staged-20261104.json"
STAGE_BLOB="1fbcf2bba4a46335f54f05d60e3a179db5f99244"
A_G2_REL="sudu/data/processed/115/review-evidence/115-00-MB-20-image-transcription-correction-20261024.json"
A_G2_BLOB="c5278848e46d07dba45734413bc0b79a9b9afcb4"
C_AUTHOR_REL="sudu/teaching-candidates/114-115-20261025/115-00-MB-20.json"
C_AUTHOR_BLOB="c226ee59e24d2136c5882ede894f9f0bb93d16d0"
E_DOC_REL="docs/ROLE_E_115_MB20_DIRECT_PIXEL_QA_20261104.md"
E_DOC_BLOB="51035f72487f24bb19ebcbd1a507f8d1b0dead22"
MANIFEST_REL="sudu/data/processed/115/webp-manifest.json"
BANK_REL="sudu/data/processed/115/questions.json"
DB_REL="sudu/data/processed/115/question-bank.sqlite3"
INV_REL="sudu/data/processed/115/inventory.json"
PAGE_REL="sudu/data/original/115/00-MB/p007-e82e34d9cd-v2-w1400-q66.webp"
SINGLE_REL="sudu/data/processed/115/webp-v5/00-MB/115-00-MB-20.webp"
OLD_V2_REL="sudu/data/processed/115/webp-v2/00-MB/115-00-MB-20.webp"
ANS_REL="sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"
G1_REL="sudu/data/processed/115/VISUAL_QA_2026-10-22.json"
CERT_REL="sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
CERT_BLOB="ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
NOTICE_REL="sudu/data/processed/115/official-confirmation-status.json"
NOTICE_BLOB="6d21432395294d9ccbcfe1dea8be01f88597bbf3"
G2_REL="sudu/data/processed/115/review-evidence/115-00-MB-20-ocr-publisher-20261110.json"
G3_REL="sudu/data/processed/115/review-evidence/115-00-MB-20-official-publisher-20261110.json"
REPORT_REL="sudu/data/processed/115/review-evidence/115-00-MB-20-v5-source-admission-20261110.json"
SQL_REPORT_REL="sudu/data/processed/115/SQLITE_QA_MB20_V5_BRIDGE_20261110.json"
OPTIONS=["50(√3＋1)","50(√3－1)","20(√3＋1)","20(√3－1)"]

def gate(ok,msg):
    if not ok: raise ValueError("MB20_SOURCE_HOLD: "+msg)
def read(rel):
    p=ROOT/rel
    gate(p.is_file() and not p.is_symlink(),"missing "+rel)
    return p.read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def js(rel):return json.loads(read(rel))
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")
def jwrite(rel,value):
    p=ROOT/rel
    gate(not p.exists(),"evidence path already exists "+rel)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def pin_webp(rel,digest,oid):
    b=read(rel)
    gate(b[:4]==b"RIFF" and b[8:12]==b"WEBP","header "+rel)
    gate(sha(b)==digest and blob(b)==oid,"original SHA/GitBlob mismatch "+rel)
def db_rows():
    with sqlite3.connect("file:"+str(ROOT/DB_REL)+"?mode=ro",uri=True) as c:
        gate(c.execute("PRAGMA integrity_check").fetchone()[0]=="ok","SQLite integrity_check")
        cols=[r[1] for r in c.execute("PRAGMA table_info(questions)")]
        gate(len(cols)==14 and "payload_sha256" in cols,"real 14-column 115 schema")
        r=c.execute("SELECT * FROM questions ORDER BY question_id").fetchall()
    gate(len(r)==205 and len({x[0] for x in r})==205,"205 SQLite QID count")
    gate(all(sha(x[12].encode("utf8"))==x[13] for x in r),"205 SQLite SHA")
    return {x[0]:x for x in r}
def actual_pixel_recheck():
    from PIL import Image,ImageChops
    page=Image.open(io.BytesIO(read(PAGE_REL))).convert("RGB")
    original=Image.open(io.BytesIO(read(SINGLE_REL))).convert("RGB")
    old=Image.open(io.BytesIO(read(OLD_V2_REL))).convert("RGB")
    cut=page.crop((90,469,1310,902))
    gate(page.size==(1400,1980) and original.size==cut.size==(1220,433),"source crop dimensions")
    gate(ImageChops.difference(cut,original).getbbox() is None,"new v5 must be original pixel exactly")
    gate(old.size==(1220,386) and old.size[1]+47==original.size[1],"historical v2 missing original 47 pixels")
    return {"officialPageSize":[1400,1980],"crop":[90,469,1310,902],"v5Size":[1220,433],
            "historicV2Size":[1220,386],"oldMissingBottomPixels":47,"v5PixelDifference":"zero_each_RGB_channel"}
def baseline():
    for rel,oid in ((BANK_REL,BANK_BLOB),(DB_REL,DB_BLOB),(INV_REL,INVENTORY_BLOB),(MANIFEST_REL,MANIFEST_BLOB)):
        gate(blob(read(rel))==oid,"stale source stacked baseline "+rel)
    bank=js(BANK_REL);man=js(MANIFEST_REL)
    gate(len(bank["questions"])==len(man["items"])==205,"original 205 JSON/image")
    q=next(x for x in bank["questions"] if x["questionId"]==QID)
    m=next(x for x in man["items"] if x["questionId"]==QID)
    gate(q["questionVerified"] is False and q["answerVerified"] is True and q["answer"]=="A","old Q20 state")
    gate(q["options"]!=OPTIONS and "60°" in q["options"][2] and "100m" in q["options"][3],"original OCR geometry pollution altered; retriage")
    gate(m["sha256"]==SINGLE_SHA and m["sourceSha256"]==PAGE_SHA and m["output"]==SINGLE_REL and m["crop"]==[90,469,1310,902],"original fixed v5 source manifest")
    gate(m["visualDefectHistory"]["repairStatus"]=="generated_pending_independent_visual_recheck","old visual defect not as diagnosed")
    gate(q["questionProvenance"]["pdfSha256"]==SOURCE_PDF and q["answerProvenance"]["pdfSha256"]==ANS_PDF,"official SHA historical")
    pin_webp(PAGE_REL,PAGE_SHA,PAGE_BLOB)
    pin_webp(SINGLE_REL,SINGLE_SHA,SINGLE_BLOB)
    pin_webp(OLD_V2_REL,OLD_V2_SHA,OLD_V2_BLOB)
    pin_webp(ANS_REL,ANS_SHA,ANS_BLOB)
    gate(sha(read(G1_REL))==G1_CERT,"original G1 certificate")
    gate(blob(read(A_G2_REL))==A_G2_BLOB,"historical source text corrections")
    gate(blob(read(CERT_REL))==CERT_BLOB and blob(read(NOTICE_REL))==NOTICE_BLOB,"original answer & no objection evidence")
    cert=[r for r in js(CERT_REL)["records"] if r["questionId"]==QID]
    gate(len(cert)==1 and cert[0]["officialFinalAnswerReadDirectlyFromPublishedImage"]=="A" and cert[0]["answerVerified"] is True,"published answer A original")
    gate(js(NOTICE_REL)["confirmations"]["00-MB"]["officialStatus"]=="no_objection_submitted","original notice no objection")
    stagep=ROOT/"_role_a_stage"/STAGE_REL
    cp=ROOT/"_role_c_author"/C_AUTHOR_REL
    ep=ROOT/"_role_e_source"/E_DOC_REL
    for p,oid in ((stagep,STAGE_BLOB),(cp,C_AUTHOR_BLOB),(ep,E_DOC_BLOB)):
        gate(p.is_file() and not p.is_symlink() and blob(p.read_bytes())==oid,"source A / C lesson / E original pixel evidence changed")
    stage=json.loads(stagep.read_text(encoding="utf8"))
    lesson=json.loads(cp.read_text(encoding="utf8"))
    edoc=ep.read_text(encoding="utf8")
    gate(QID==stage["questionId"]==lesson["questionId"],"Q20 staged/lesson mismatch")
    gate(stage["g2Source"]["question"]==lesson["question"] and stage["g2Source"]["options"]==lesson["options"]==OPTIONS,"A/C exact original source text")
    gate(stage["g2Source"]["currentCPr118SourceRevisionForComparisonOnly"]==lesson["sourceTextRevisionWithoutTable"]==SOURCE_REV,"A/C source revision match")
    gate(sha(canon({"question":lesson["question"],"options":lesson["options"],"singleQuestionWebpSha256":SINGLE_SHA}))==SOURCE_REV,"computed C source revision mismatch")
    gate(lesson["imageSha256"]==SINGLE_SHA and lesson["teachingCanonicalSha256"]==TEACHING_SHA,"author teaching not immutable")
    gate("diff RGB per channel = [0.0, 0.0, 0.0]" in edoc and "v5 single WebP" in edoc and "question 20 printed answer A" in edoc, "real distinct E original image QA report does not contain expected test")
    gate(stage["official"]["printedOfficialAnswer"]=="A","A archived official original")
    old=db_rows()
    gate(set(old)=={z["questionId"] for z in bank["questions"]},"205 source QIDs")
    gate(all(json.loads(old[z["questionId"]][12])==z for z in bank["questions"]),"pre 205 raw JSON/SQLite")
    gate(old[QID][9]==0 and old[QID][10]==0,"initial Q20 14-column flags")
    return bank,man,q,m,stage,lesson,old,actual_pixel_recheck()
def issuers(q,stage,pixels):
    g2={"schemaVersion":1,"year":115,"questionId":QID,
       "role":"A_SOURCE_ONLY_NOT_DISTINCT_E","taskId":TASK,"questionRevision":SOURCE_REV,
       "webpSha256":SINGLE_SHA,"question":q["question"],"options":q["options"],
       "visualTextCompared":True,"reviewer":"ROLE A original v5 p7 crop + existing ROLE E PR156 source-pixel QA; not trusted E content reviewer",
       "reviewedAt":"2026-11-10","reviewType":"ORIGINAL_V5_SINGLE_QUESTION_G2_SOURCE_ONLY",
       "sourceYear":115,"originalPage":7,"sourcePdfSha256PreviouslyRecorded":SOURCE_PDF,
       "originalPageSha256":PAGE_SHA,"originalSingleWebpSha256":SINGLE_SHA,
       "originalSingleWebpGitBlob":SINGLE_BLOB,"sourcePageWebpGitBlob":PAGE_BLOB,
       "sourceStagePath":STAGE_REL,"sourceStageGitBlob":STAGE_BLOB,
       "historicTextCorrectionPath":A_G2_REL,"historicTextCorrectionGitBlob":A_G2_BLOB,
       "independentSourcePixelEvidenceUrl":"https://github.com/homelux-huang/7581707/pull/156",
       "independentSourcePixelEvidenceGitBlob":E_DOC_BLOB,
       "sourcePixelEvidence":pixels,"sourceCrop":[90,469,1310,902],"oldV2Forbidden":True,
       "originalRawOcrPreserved":True,"noRecropOrRedraw":True,"answerHiddenFromIssuer":True,
       "independentEContentTrust":False,"studentReady":False,"studentLive":False}
    g3={"schemaVersion":1,"year":115,"questionId":QID,
       "reviewer":"ROLE A original published 115 MathB p1 Q20 A and paper no-objection, not independent E",
       "reviewedAt":"2026-11-10","officialPage":"https://web1.tcte.edu.tw/EXAM/115_4y/",
       "officialPdfSha256":ANS_PDF,"finalAnswer":"A",
       "officialFinalAnswerImageQaPassed":True,"correctionNoticeReviewed":True,
       "noObjectionForPaper":True,"noCorrectionForThisQuestion":False,
       "correctionForQuestionReviewed":False,"officialNoticeStatus":"no_objection_submitted",
       "officialNoticePath":NOTICE_REL,"originalOfficialAnswerImagePath":ANS_REL,
       "originalOfficialAnswerImageSha256":ANS_SHA,"originalOfficialAnswerImageGitBlob":ANS_BLOB,
       "originalSourcePageSha256":PAGE_SHA,"originalSingleQuestionWebpSha256":SINGLE_SHA,
       "sourceQuestionRevision":SOURCE_REV,"directPublishedAnswerRecord":CERT_REL,
       "directPublishedAnswerRecordGitBlob":CERT_BLOB,
       "originalOfficialAnswerPdfNewlyRehashedThisTask":False,
       "publishedOriginalAnswerA":True,"sourceOnly":True,"independentE":False,
       "studentReady":False,"studentLive":False}
    gate("finalAnswer" not in g2,"G2 must not leak official answer")
    return g2,g3
def generate():
    bank,man,q,m,stage,lesson,old,pixels=baseline()
    before={r["questionId"]:canon(r) for r in bank["questions"] if r["questionId"]!=QID}
    before_images={r["questionId"]:canon(r) for r in man["items"] if r["questionId"]!=QID}
    newq=copy.deepcopy(q)
    newq["question"]=stage["g2Source"]["question"]
    newq["options"]=OPTIONS
    newq["questionVerified"]=True
    newq["textQaStatus"]="PASS"
    newq["imageQaStatus"]="PASS"
    newq["answerVerified"]=True
    newq["officialFinalAnswer"]="A"
    newq["officialCorrectionChecked"]=True
    newq["officialAnswerQaStatus"]="PASS_FINAL_OFFICIAL_ANSWER_AND_NO_OBJECTION_NOTICE"
    newq["reviewStatus"]="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI"
    newq["integrationReady"]=False
    newq["correctionVersion"]="ROLE_A_MB20_ORIGINAL_V5_VISUAL_ONLY_20261110"
    newq["issues"]=[]
    newq["extraction"]["correctionOverlay"]={
       "origin":"ROLE_A_ORIGINAL_MB20_CORRECTED_V5_WITH_ROLE_E_INDEPENDENT_PIXEL_PROOF",
       "sourceStagePath":STAGE_REL,"sourceRevision":SOURCE_REV,
       "originalVisualDefectHistoryPreservedInManifest":True,
       "originalRawOcrUnchanged":True,
       "sourceImageGitBlob":SINGLE_BLOB,
       "independentVisualProofGitBlob":E_DOC_BLOB,"options":OPTIONS}
    newq["extraction"]["ocrReviewStatus"]="PASS_SOURCE_G2_ORIGINAL_V5"
    newq["extraction"]["correctedAt"]="2026-11-10"
    newq["answerProvenance"]["officialRevisionChecked"]=True
    newq["answerProvenance"]["independentVisualVerification"]=True
    gate(not newq.get("studentReleaseApproved",False) and newq.get("teachingQaStatus")!="PASS","never set source student approval")
    stagep=ROOT/"_role_a_stage"/STAGE_REL
    dest=ROOT/STAGE_REL
    gate(not dest.exists(),"source stage already exists")
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(stagep,dest)
    gate(blob(dest.read_bytes())==STAGE_BLOB,"original A stage copied changed")
    # Preserve 2026-10-22 defect history. Resolve the outstanding SOURCE IMAGE recheck
    # with real frozen E pixel QA and new direct 0-pixel-diff; NOT a new E content receipt.
    mi=next(i for i,x in enumerate(man["items"]) if x["questionId"]==QID)
    newm=copy.deepcopy(m)
    newm["visualDefectHistory"]["repairStatus"]="source_pixel_recheck_pass_original_v5_role_e_20261104"
    newm["originalIndependentSourceVisualRecheck"]={
       "evidencePrUrl":"https://github.com/homelux-huang/7581707/pull/156",
       "evidenceHead":E_IMAGE_HEAD,"evidenceDocGitBlob":E_DOC_BLOB,
       "evidenceWorkflowRun":41784295447,"pixelRecheck":pixels,
       "independentContentReviewerReceipt":False,"studentReady":False}
    man["items"][mi]=newm
    gate(all(canon(r)==before_images[r["questionId"]] for r in man["items"] if r["questionId"]!=QID),"other 204 original webp manifest entries changed")
    path=ROOT/MANIFEST_REL
    oldbytes=path.read_bytes()
    gate(oldbytes==(json.dumps(json.loads(oldbytes),ensure_ascii=False,indent=2)+"\n").encode("utf8"),"source manifest formatting drift")
    path.write_text(json.dumps(man,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    g2,g3=issuers(newq,stage,pixels)
    jwrite(G2_REL,g2)
    jwrite(G3_REL,g3)
    newq["textQaEvidence"]={"reviewer":"ROLE A source G2, actual frozen independent E image recheck only",
       "reviewedAt":"2026-11-10","evidencePath":G2_REL,"evidenceSha256":sha(read(G2_REL)),
       "questionRevision":SOURCE_REV,"sourceImageSha256":PAGE_SHA}
    newq["officialFinalQaEvidence"]={"reviewer":"ROLE A original printed answer A (not E)",
       "reviewedAt":"2026-11-10","evidencePath":G3_REL,"evidenceSha256":sha(read(G3_REL)),
       "answerPdfSha256":ANS_PDF,"finalCorrectionsReviewed":True}
    index=next(i for i,x in enumerate(bank["questions"]) if x["questionId"]==QID)
    bank["questions"][index]=newq
    gate(all(canon(r)==before[r["questionId"]] for r in bank["questions"] if r["questionId"]!=QID),"other 204 bank QIDs changed")
    raw=read(BANK_REL)
    gate(raw==(json.dumps(json.loads(raw),ensure_ascii=False,indent=2)+"\n").encode("utf8"),"bank formatting drift")
    (ROOT/BANK_REL).write_text(json.dumps(bank,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    payload=canon(newq).decode("utf8")
    with sqlite3.connect(BASE/"question-bank.sqlite3") as c:
        cur=c.execute("UPDATE questions SET question=?,answer=?,answer_verified=?,question_verified=?,review_status=?,payload_json=?,payload_sha256=? WHERE question_id=?",
            (newq["question"],"A",1,1,newq["reviewStatus"],payload,sha(payload.encode()),QID))
        gate(cur.rowcount==1,"Q20 one SQL row")
        c.commit()
    changed=db_rows()
    gate({k:v for k,v in changed.items() if k!=QID}=={k:v for k,v in old.items() if k!=QID},"other 204 full DB row changed")
    gate(changed[QID][9]==1 and changed[QID][10]==1,"Q20 source SQLite flags")
    gate(all(json.loads(changed[r["questionId"]][12])==r for r in bank["questions"]),"205 JSON/SQLite exact parity")
    inv=js(INV_REL)
    inv["sqlite"]["performed"]=True
    inv["sqlite"]["rows"]=205
    inv["sqlite"]["shaMismatches"]=[]
    inv["sqlite"]["roundtripPass"]=True
    inv["sqlite"]["sourceQuestionsSha256"]=sha(read(BANK_REL))
    inv["sqlite"]["dbSha256"]=sha(read(DB_REL))
    inv["sqlite"]["evidencePath"]=SQL_REPORT_REL
    inv["sqlite"]["releaseApproved"]=False
    (ROOT/INV_REL).write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    jwrite(SQL_REPORT_REL,{"schemaVersion":1,"year":115,"questionId":QID,"taskId":TASK,"parentSourceSha":PARENT,
       "beforeBankBlob":BANK_BLOB,"beforeSqliteBlob":DB_BLOB,"beforeManifestBlob":MANIFEST_BLOB,
       "afterBankSha256":sha(read(BANK_REL)),"afterSqliteSha256":sha(read(DB_REL)),
       "afterWebpManifestSha256":sha(read(MANIFEST_REL)),"sqliteIntegrity":"ok",
       "rows":205,"other204SqliteWholeTuplesUnchanged":True,"other204CanonicalQuestionsUnchanged":True,
       "other204ManifestItemsUnchanged":True,"originalQ23Preserved":True,"ready":False,"live":False})
    jwrite(REPORT_REL,{"schemaVersion":1,"year":115,"role":"A","questionId":QID,"taskId":TASK,"claim":CLAIM,
       "parentSourceSha":PARENT,"originalSourceStageGitBlob":STAGE_BLOB,
       "sourceRevision":SOURCE_REV,"webpSha256":SINGLE_SHA,"sourceVisualOriginalPixel":pixels,
       "sourceImageIndependentRecheckEvidencePr":156,"sourceImageIndependentRecheckEvidenceBlob":E_DOC_BLOB,
       "g1VisualCertificateSha256":G1_CERT,"officialAnswer":"A",
       "officialNoObjectionForPaper":True,"noNewPdfDownloadOrRehash":True,"noWebpRecreation":True,
       "teacherCanonicalSha256Unchanged":TEACHING_SHA,
       "publisherOcrEvidencePath":G2_REL,"publisherOcrEvidenceSha256":sha(read(G2_REL)),
       "publisherOfficialEvidencePath":G3_REL,"publisherOfficialEvidenceSha256":sha(read(G3_REL)),
       "other204JsonRowsUnchanged":True,"other204SqliteRowsUnchanged":True,"other204ManifestRowsUnchanged":True,
       "sqliteRows":205,"formalETrust":False,"formalDRealEmitter16":False,
       "studentReady":False,"newLive":False,
       "status":"SOURCE_ONLY_ORIGINAL_V5_E_IMAGE_PIXEL_G1_G2_G3_COMPLETE_DISTINCT_E_TRUST_D_MASTER_HOLD"})
    print("MB20 source G1 direct original v5 pixel and frozen E source QA; G2/G3/205 DB one row. No TRUST/READY/LIVE")
def verify():
    bank=js(BANK_REL)
    man=js(MANIFEST_REL)
    inv=js(INV_REL)
    receipt=js(REPORT_REL)
    q=next(x for x in bank["questions"] if x["questionId"]==QID)
    m=next(x for x in man["items"] if x["questionId"]==QID)
    stage=js(STAGE_REL)
    gate(len(bank["questions"])==len(man["items"])==205,"post 205 parity")
    gate(q["questionVerified"] and q["answerVerified"] and q["textQaStatus"]=="PASS" and q["answer"]=="A" and q["reviewStatus"]=="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI","source-only flags")
    gate(q["question"]==stage["g2Source"]["question"] and q["options"]==OPTIONS,"Q20 corrected original options")
    gate(sha(canon({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":SINGLE_SHA}))==SOURCE_REV,"source revision original C proof")
    gate(m["originalIndependentSourceVisualRecheck"]["evidenceDocGitBlob"]==E_DOC_BLOB and m["visualDefectHistory"]["repairStatus"]=="source_pixel_recheck_pass_original_v5_role_e_20261104","original defect source recheck not documented")
    gate(m["visualDefectHistory"]["finding"]=="previous_candidate_missing_figure_IV_lower_edge_and_caption","original defect history must be preserved")
    gate(m["sha256"]==SINGLE_SHA and m["sourceSha256"]==PAGE_SHA and m["crop"]==[90,469,1310,902],"current original v5 manifest")
    pin_webp(SINGLE_REL,SINGLE_SHA,SINGLE_BLOB)
    pin_webp(PAGE_REL,PAGE_SHA,PAGE_BLOB)
    gate(actual_pixel_recheck()["v5PixelDifference"]=="zero_each_RGB_channel","fresh original source pixels differ")
    updated=db_rows()
    gate(all(json.loads(updated[z["questionId"]][12])==z for z in bank["questions"]),"205 SQLite full payload mismatch")
    gate(sha(read(BANK_REL))==inv["sqlite"]["sourceQuestionsSha256"] and sha(read(DB_REL))==inv["sqlite"]["dbSha256"],"db/source sha")
    gate(receipt["publisherOcrEvidenceSha256"]==sha(read(G2_REL)) and receipt["publisherOfficialEvidenceSha256"]==sha(read(G3_REL)),"issuer SHA changed")
    gate(q["textQaEvidence"]["evidenceSha256"]==receipt["publisherOcrEvidenceSha256"] and q["officialFinalQaEvidence"]["evidenceSha256"]==receipt["publisherOfficialEvidenceSha256"],"G2/G3 SHA chain")
    gate(not q.get("studentReleaseApproved",False) and q.get("teachingQaStatus")!="PASS" and q.get("uiQaStatus")!="PASS","unapproved release")
    sys.path.insert(0,str(ROOT/"_publisher_main"))
    from scripts import sudu_verified_publish as pub
    gate(pub.image_proof(q,m,{},ROOT) and pub.visual_certificate(ROOT,m,QID) and pub.verify_bytes(ROOT,SINGLE_REL,SINGLE_SHA),"native G1 source original")
    text,answer=pub.source_proof(q,True,True,SOURCE_REV)
    gate(text and answer,"native G2/G3 source proof false")
    g2=pub.review_document(ROOT,115,G2_REL,QID)
    g3=pub.review_document(ROOT,115,G3_REL,QID)
    gate(g2 and g3 and g2[0]["question"]==q["question"] and g2[0]["options"]==OPTIONS and g2[0]["questionRevision"]==SOURCE_REV and g2[0]["webpSha256"]==SINGLE_SHA,"native G2 issuer original mismatch")
    gate(g3[0]["finalAnswer"]=="A" and g3[0]["officialPdfSha256"]==ANS_PDF and pub.official_notice_scope_certified(ROOT,115,q,g3[0]),"native G3 official/no objection")
    gate(not pub.certificates_complete(ROOT,q,m,{}),"unverified E or D full student certificates")
    negative(pub,q,m)
    print(json.dumps({"status":"ORIGINAL_V5_SOURCE_ONLY_G1_G2_G3_VERIFIED","qid":QID,"rev":SOURCE_REV,"g2Sha256":g2[1],"g3Sha256":g3[1],"dbSha256":inv["sqlite"]["dbSha256"],"ready":False,"live":False},ensure_ascii=False))
def negative(pub,q,m):
    bad=copy.deepcopy(q)
    bad["options"][3]="20(√3－1) A B 100m OCR contamination"
    gate(bad["options"]!=js(G2_REL)["options"],"geometry OCR mutant not caught")
    bad=copy.deepcopy(q);bad["textQaEvidence"]["questionRevision"]="0"*64
    gate(not pub.source_proof(bad,True,True,SOURCE_REV)[0],"forged G2 accepted")
    bad=copy.deepcopy(q);bad["officialFinalQaEvidence"]["answerPdfSha256"]="0"*64
    gate(not pub.source_proof(bad,True,True,SOURCE_REV)[1],"forged official PDF accepted")
    g3=copy.deepcopy(js(G3_REL));g3["noObjectionForPaper"]=False
    gate(not pub.official_notice_scope_certified(ROOT,115,q,g3),"notice fake accepted")
    m2=copy.deepcopy(m);m2["visualReviewEvidence"]["referenceSha256"]="0"*64
    gate(not pub.visual_certificate(ROOT,m2,QID),"visual SHA mutant accepted")
    gate("finalAnswer" not in js(G2_REL),"answer key leaked in G2")
    gate(not q.get("studentReleaseApproved",False),"source cannot set ready")
    print("MB20 false image/source/official/old v2/G2/READY release negatives PASS")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply",action="store_true")
    g.add_argument("--verify",action="store_true")
    a=p.parse_args()
    generate() if a.apply else verify()
