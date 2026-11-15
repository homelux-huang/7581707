#!/usr/bin/env python3
"""ROLE A 114 English Q11: source-only G1/G2/G3 and 205-row canonical SQLite parity. NO RELEASE."""
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
BASE = ROOT / "sudu/data/processed/114"
QID = "114-00-E-11"
ORIGINAL_QA = "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2"
SOURCE_STAGE = "bc625d5eba9bf67f29b236258754941f0c9d999e"
MANIFEST_OLD_BLOB = "f507470ac6ef36c653ed669d5a9c1a313f456e28"
BANK_OLD_BLOB = "804a8b046e97b5fb4fc55f33af25c7a8c08e8a7d"
SQLITE_OLD_BLOB = "6c3efd8c3d20507e09f76178fc6927951235a754"
INVENTORY_OLD_BLOB = "8fe194ee8722c9461151aa2665c762f695f167c2"
QREV = "646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036"
WEBP = "ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0"
PAGE = "51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
ANSWER_IMAGE = "a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
PAPER_PDF = "1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf"
ANSWER_PDF = "ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325"
NOTICE_PDF = "79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"
VISUAL_REL = "sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
STAGE_REL = "sudu/data/processed/114/source-stage/114-00-E-11-staged-20261104.json"
A_TEXT_REL = "sudu/data/processed/114/review-evidence/114-00-E-11-source-text-20261028.json"
A_OFFICIAL_REL = "sudu/data/processed/114/review-evidence/114-00-E-11-official.json"
OCR_REL = "sudu/data/processed/114/review-evidence/114-00-E-11-ocr-publisher-20261107.json"
G3_REL = "sudu/data/processed/114/review-evidence/114-00-E-11-official-publisher-20261107.json"
REPORT_REL = "sudu/data/processed/114/review-evidence/114-00-E-11-MASTER-SOURCE-ADMISSION-20261107.json"
SQL_REPORT_REL = "sudu/data/processed/114/SQLITE_QA_E11_SOURCE_BRIDGE_20261107.json"
HISTORICAL_BLOBS = {
    STAGE_REL: "d64132d1cae7fb1a4797e89f5853f529e29f01c5",
    A_TEXT_REL: "bd90a3c3814353379eacf89759fcd3153099fa53",
    A_OFFICIAL_REL: "bc3d19885e2ebc3d27092b673636bd84c89f65c6",
}
WEBP_REL = "sudu/data/processed/114/webp-v1/00-E/114-00-E-11.webp"
PAGE_REL = "sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp"
ANSWER_IMAGE_REL = "sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp"
WEBP_BLOB = "50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a"
PAGE_BLOB = "5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
ANSWER_IMAGE_BLOB = "5f2920313607af4e756095cd3d6098c8a3ab7440"
VISUAL_BLOB = "c1154562fa30cb4b2720a6000a970cf09ef460ff"
LEDGER_BLOB = "6b9a919f224bec8dc3659052a404b4173b6ef366"

def demand(flag: bool, why: str):
    if not flag: raise RuntimeError("E11_SOURCE_HOLD: " + why)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def canon(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def readable(path: Path) -> bytes:
    demand(path.is_file() and not path.is_symlink(), "required immutable source missing: " + str(path))
    return path.read_bytes()

def json_file(path: Path) -> dict:
    return json.loads(readable(path))

def jwrite(rel: str, obj):
    path = ROOT / rel
    demand(not path.exists(), "new-only issuer or report already exists: " + rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def image_check(path: str, expected_sha: str, expected_blob: str):
    b = readable(ROOT / path)
    demand(b[:4] == b"RIFF" and b[8:12] == b"WEBP", "not source WebP: " + path)
    demand(sha(b) == expected_sha and blob(b) == expected_blob, "WebP SHA/Blob mismatch: " + path)

def rev(q, webp):
    return sha(canon({"question": q["question"], "options": q["options"], "singleQuestionWebpSha256": webp}))

def db_rows(path):
    with sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True) as cx:
        demand(cx.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity")
        cols = [c[1] for c in cx.execute("PRAGMA table_info(questions)")]
        demand(len(cols) == 7 and {"question_id", "payload_json", "payload_sha256"} <= set(cols), "not existing normalized seven-column SQLite")
        rows = cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions ORDER BY question_id").fetchall()
    demand(len(rows) == 205 and len({x[0] for x in rows}) == 205, "SQLite row uniqueness")
    demand(all(sha(payload.encode("utf-8")) == digest for _,payload,digest in rows), "SQLite row digest")
    return {qid: (payload, digest) for qid,payload,digest in rows}

def validate_pristine(bank, manifest, inventory, stage_root):
    questions=bank["questions"]
    items=manifest["items"]
    demand(bank["year"] == manifest["year"] == 114, "wrong annual source")
    demand(len(questions) == len(items) == 205, "annual 205 count")
    demand(len({x["questionId"] for x in questions}) == 205 and len({x["questionId"] for x in items}) == 205, "duplicate QID")
    q = next(x for x in questions if x["questionId"] == QID)
    m = next(x for x in items if x["questionId"] == QID)
    demand(q["questionVerified"] is False and q["answerVerified"] is False and q["reviewStatus"] == "needs_review", "E11 baseline unexpectedly admitted")
    demand(q["answer"] == "A" and q["answerMatched"] is True, "canonical E11 source candidate not A")
    demand(q["questionProvenance"]["officialPdfSha256"] == PAPER_PDF and q["answerProvenance"]["officialPdfSha256"] == ANSWER_PDF, "source or answer PDF pin mismatch")
    demand(q["questionProvenance"]["pixelSourceSha256"] == PAGE and q["questionProvenance"]["webpSha256"] == WEBP and rev(q,WEBP)==QREV, "Q11 source revision or image binding mismatch")
    demand(q["originalQuestionNumber"] == 11 and q["sourcePage"] == 3 and q["paperCode"] == "00-E", "not source 00-E Q11 p3")
    demand(len(q["options"]) == 4 and all(v.strip() for v in q["options"]), "bad A-D")
    demand(m["qaStatus"] == q["imageQaStatus"] == "PASS" and m["output"] == WEBP_REL and m["source"] == PAGE_REL and m["sha256"] == WEBP and m["sourceSha256"] == PAGE and m["crop"] == [90,275,1310,591], "source manifest E11 identity mismatch")
    ev=m["visualReviewEvidence"]
    demand(ev.get("reference") == VISUAL_REL and ev.get("reviewedSha256") == WEBP and ev.get("sourcePageSha256") == PAGE and ev.get("referenceSha256") is None, "unexpected old visual SHA or manifest drift")
    visual_bytes=readable(ROOT/VISUAL_REL)
    demand(blob(visual_bytes)==VISUAL_BLOB,"old G1 visual record Git blob changed")
    record=json.loads(visual_bytes)
    matches=[x for x in record["items"] if x["questionId"]==QID]
    demand(len(matches)==1, "genuine original G1 item missing")
    old=matches[0]
    demand(old["result"]=="PASS" and old["reviewedWebpPath"]==WEBP_REL and old["reviewedWebpSha256"]==WEBP and old["sourcePageSha256"]==PAGE and old["cropPixels"]==m["crop"],"archived E11 direct visual status mismatch")
    demand(all(old["criteria"].get(k) is True for k in ("original_number","complete_stem","all_four_options","no_neighboring_question","readable","source_and_output_sha256_matched","exact_source_crop_pixel_match")), "original source visual criteria not passed")
    image_check(WEBP_REL,WEBP,WEBP_BLOB)
    image_check(PAGE_REL,PAGE,PAGE_BLOB)
    image_check(ANSWER_IMAGE_REL,ANSWER_IMAGE,ANSWER_IMAGE_BLOB)
    archived = {}
    for rel,expected in HISTORICAL_BLOBS.items():
        payload=readable(stage_root/rel)
        demand(blob(payload)==expected,"immutable prior ROLE A source evidence altered: "+rel)
        archived[rel]=json.loads(payload)
    stage=archived[STAGE_REL]
    source=archived[A_TEXT_REL]
    official=archived[A_OFFICIAL_REL]
    demand(stage["questionId"] == source["questionId"] == official["questionId"] == QID,"historical source QID")
    demand(stage["source"]["question"]==q["question"] and stage["source"]["options"]==q["options"] and stage["source"]["revision"]==QREV, "prior original Q11 G2 source content differs")
    demand(source["directStructuredSourceTextVisualObservation"]["canonicalQuestionExact"]==q["question"] and source["directStructuredSourceTextVisualObservation"]["printedOptionsExact"]==q["options"], "previous direct E11 text QA mismatch")
    demand(stage["source"]["originalSingleSha256"]==WEBP and stage["source"]["originalPageSha256"]==PAGE, "original stage source SHA mismatch")
    demand(stage["official"]["publishedAnswer"]==official["finalAnswer"]==official["individualPrintedAnswerCell"]["observedLetter"]=="A", "original published answer not A")
    demand(stage["official"]["originalPublishedAnswerWebpSha256"]==official["officialAnswerImageSha256"]==ANSWER_IMAGE, "original official A image SHA mismatch")
    demand(stage["official"]["noticeQuestionIds"]==["114-00-E-26"] and official["officialConfirmationNamedQuestionIds"]==["114-00-E-26"] and official["noCorrectionForThisQuestion"] is True, "official English correction scope wrong")
    ledger_bytes=readable(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")
    demand(blob(ledger_bytes)==LEDGER_BLOB, "original official notice ledger changed")
    led=json.loads(ledger_bytes)
    docs=[d for d in led["docs"] if d["paperCode"]=="00-E"]
    demand(len(docs)==1 and docs[0]["pdfSha256"]==NOTICE_PDF and docs[0]["allPagesVisuallyReviewed"] is True and [x["questionId"] for x in docs[0]["confirmed"]]==["114-00-E-26"], "notice is specifically E26, not blanket exam")
    status=json_file(BASE/"official-confirmation-status.json")
    state=status["confirmations"]["00-E"]
    demand(state["revisionDocumentSha256"]==NOTICE_PDF and state["revisionDocumentContent"]=="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED" and state["perQuestionOfficialNoticeScopeEvidenceComplete"] is True,"official year notice not fully indexed")
    demand(inventory["sqlite"]["roundtripPass"] is True and inventory["sqlite"]["rows"] == 205,"old SQLite inventory not complete")
    return q,m,sha(visual_bytes),archived

def issuer_docs(q,m,visual_sha,archived):
    ocr={
      "schemaVersion":1,"year":114,"questionId":QID,"role":"ROLE_A_SOURCE_NOT_ROLE_E",
      "sourceTaskId":"A-114-E11-CANONICAL-G2G3-20261107-MASTER-DISPATCH",
      "questionRevision":QREV,"webpSha256":WEBP,
      "question":q["question"],"options":q["options"],"visualTextCompared":True,
      "reviewer":"ROLE A directly reviewed immutable official p3 + Q11 image and reconciled archived original direct G2; NOT ROLE E content reviewer",
      "reviewedAt":"2026-11-07","reviewType":"REAL_ARCHIVED_SOURCE_G1_G2_TEXT_RECONCILIATION_NOT_BLIND_OR_TEACHING",
      "sourceYear":114,"sourcePaper":"00-E","originalSourcePage":3,
      "sourcePdfSha256":PAPER_PDF,"sourceOriginalPageSha256":PAGE,
      "originalImageCrop":[90,275,1310,591],
      "archivedVisualQaPath":VISUAL_REL,"archivedVisualQaGitBlob":VISUAL_BLOB,"archivedVisualQaSha256":visual_sha,
      "archivedSourceTextQaPath":A_TEXT_REL,"archivedSourceTextGitBlob":HISTORICAL_BLOBS[A_TEXT_REL],
      "archivedSourceStagePath":STAGE_REL,"archivedSourceStageGitBlob":HISTORICAL_BLOBS[STAGE_REL],
      "originalSingleWebpGitBlob":WEBP_BLOB,"originalPaperPageGitBlob":PAGE_BLOB,
      "sourceOriginalSingleWebpSha256":WEBP,
      "visualQaResult":"PASS","originalWebpUnchanged":True,"sourceQuestionAndFourOptionsExactMatch":True,
      "independentRoleEApproval":False,"independentBlindSolvePerformed":False,"studentReady":False,"studentLive":False,
    }
    official={
      "schemaVersion":1,"year":114,"questionId":QID,
      "reviewer":"ROLE A original printed-answer p1 Q11 A + historic correction E26-only scope; NOT independent ROLE E",
      "reviewedAt":"2026-11-07",
      "sourceReviewType":"ARCHIVED_DIRECT_ORIGINAL_PUBLISHED_IMAGE_Q11_RECHECK_NOT_FRESH_PDF_DOWNLOAD",
      "officialPage":"https://web1.tcte.edu.tw/EXAM/114_4y/",
      "officialPdfSha256":ANSWER_PDF,"finalAnswer":"A",
      "officialFinalAnswerImageQaPassed":True,"correctionNoticeReviewed":True,
      "noObjectionForPaper":False,"noCorrectionForThisQuestion":True,"correctionForQuestionReviewed":False,
      "confirmationPdfSha256":NOTICE_PDF,
      "sourceQuestionRevision":QREV,"sourceOriginalSingleWebpSha256":WEBP,
      "officialPrintedAnswerImageSource":ANSWER_IMAGE_REL,"officialPrintedAnswerImageGitBlobSha1":ANSWER_IMAGE_BLOB,
      "officialPrintedAnswerImageSha256":ANSWER_IMAGE,
      "sourceRoleAOfficialReceipt":A_OFFICIAL_REL,"sourceRoleAOfficialReceiptGitBlobSha1":HISTORICAL_BLOBS[A_OFFICIAL_REL],
      "sourceRoleATextReceipt":A_TEXT_REL,"sourceRoleATextReceiptGitBlobSha1":HISTORICAL_BLOBS[A_TEXT_REL],
      "originalCorrectionLedgerGitBlobSha1":LEDGER_BLOB,
      "namedOfficialCorrectionQuestionIds":["114-00-E-26"],"question11ListedInCorrection":False,
      "otherQuestionIdsChanged":False,
      "status":"SOURCE_G3_PUBLISHER_DOCUMENT_ONLY_NOT_REVIEW_E_NOT_STUDENT_RELEASE",
      "originalPublishedAnswerImageRecheckedFromArchivedVisualQA":True,
      "downloadedAndRehashedOfficialPdfThisTask":False,"independentRoleEContentReviewedThisTask":False,
      "studentReleaseApproved":False,
    }
    return ocr,official

def create_source_admission():
    bankpath=BASE/"questions.json"
    mp=BASE/"webp-manifest.json"
    invp=BASE/"inventory.json"
    dbp=BASE/"question-bank.sqlite3"
    original={p:readable(p) for p in (bankpath,mp,invp,dbp)}
    demand(blob(original[bankpath])==BANK_OLD_BLOB and blob(original[mp])==MANIFEST_OLD_BLOB and blob(original[invp])==INVENTORY_OLD_BLOB and blob(original[dbp])==SQLITE_OLD_BLOB, "frozen official QA source/manifest/inventory/SQLite moved; no update")
    bank=json.loads(original[bankpath]);manifest=json.loads(original[mp]);inventory=json.loads(original[invp])
    q,m,vis_sha,archived=validate_pristine(bank,manifest,inventory,ROOT/"_role_a_stage")
    oldbank={x["questionId"]:canon(x) for x in bank["questions"]}
    oldmanifest={x["questionId"]:canon(x) for x in manifest["items"]}
    oldrows=db_rows(dbp)
    demand(set(oldrows)==set(oldbank) and all(json.loads(oldrows[k][0])==next(x for x in bank["questions"] if x["questionId"]==k) for k in oldrows), "preexisting 205 source JSON/SQLite parity")
    ocr,official=issuer_docs(q,m,vis_sha,archived)
    for rel in HISTORICAL_BLOBS:
        target=ROOT/rel
        demand(not target.exists(),"historical ROLE A source receipt unexpectedly exists at QA")
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/"_role_a_stage"/rel,target)
        demand(blob(target.read_bytes())==HISTORICAL_BLOBS[rel],"source receipt copy altered")
    jwrite(OCR_REL,ocr)
    jwrite(G3_REL,official)
    accepted=copy.deepcopy(q)
    accepted.update({
      "questionVerified":True,"answerVerified":True,
      "textQaStatus":"PASS",
      "textQaEvidence":{
          "reviewer":"ROLE A original official p3 + Q11 G2 source visual, no independent ROLE E",
          "reviewedAt":"2026-11-07","evidencePath":A_TEXT_REL,
          "sourceImageSha256":PAGE,"questionRevision":QREV,
          "evidenceSha256":sha((ROOT/A_TEXT_REL).read_bytes()),
      },
      "officialFinalAnswer":"A","officialCorrectionChecked":True,
      "officialFinalQaEvidence":{
          "reviewer":"ROLE A original published official p1 A + E26-only notice (NOT ROLE E)",
          "reviewedAt":"2026-11-07","evidencePath":A_OFFICIAL_REL,
          "answerPdfSha256":ANSWER_PDF,"finalCorrectionsReviewed":True,
          "evidenceSha256":sha((ROOT/A_OFFICIAL_REL).read_bytes()),
      },
      "reviewStatus":"SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI",
    })
    accepted["answerProvenance"]["independentVisualVerification"]=True
    demand("studentReleaseApproved" not in accepted and accepted.get("teachingQaStatus")!="PASS" and accepted.get("uiQaStatus")!="PASS", "source may not self release")
    bank["questions"][next(i for i,x in enumerate(bank["questions"]) if x["questionId"]==QID)]=accepted
    manifest["items"][next(i for i,x in enumerate(manifest["items"]) if x["questionId"]==QID)]["visualReviewEvidence"]["referenceSha256"]=vis_sha
    demand(all(canon(x)==oldbank[x["questionId"]] for x in bank["questions"] if x["questionId"]!=QID), "other 204 source QIDs changed")
    demand(all(canon(x)==oldmanifest[x["questionId"]] for x in manifest["items"] if x["questionId"]!=QID), "other 204 source images changed")
    demand(original[bankpath]==(json.dumps(json.loads(original[bankpath]),ensure_ascii=False,indent=2)+"\n").encode("utf-8"), "source bank format drift")
    demand(original[mp]==(json.dumps(json.loads(original[mp]),ensure_ascii=False,indent=2)+"\n").encode("utf-8"), "source manifest format drift")
    bankpath.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    payload=canon(accepted).decode("utf-8")
    with sqlite3.connect(dbp) as cx:
        cur=cx.execute("UPDATE questions SET payload_json=?, payload_sha256=? WHERE question_id=?",(payload,sha(payload.encode("utf-8")),QID))
        demand(cur.rowcount==1, "E11 SQLite row update not exactly one")
        cx.commit()
    afterrows=db_rows(dbp)
    demand({k:v for k,v in afterrows.items() if k!=QID}=={k:v for k,v in oldrows.items() if k!=QID}, "other 204 SQLite payloads changed")
    demand(all(json.loads(afterrows[x["questionId"]][0])==x for x in bank["questions"]), "post-commit 205 JSON/SQLite parity")
    inventory["sqlite"]["dbSha256"]=sha(readable(dbp))
    inventory["sqlite"]["sourceQuestionsSha256"]=sha(readable(bankpath))
    inventory["sqlite"]["evidencePath"]=SQL_REPORT_REL
    inventory["sqlite"]["releaseApproved"]=False
    invp.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sqlite_receipt={
      "schemaVersion":1,"year":114,"questionId":QID,
      "taskId":"A-114-E11-CANONICAL-G2G3-20261107-MASTER-DISPATCH",
      "sourceQaBaseline":ORIGINAL_QA,
      "sourceBankBlobBefore":BANK_OLD_BLOB,"sourceManifestBlobBefore":MANIFEST_OLD_BLOB,
      "sqliteBlobBefore":SQLITE_OLD_BLOB,
      "sourceBankSha256After":sha(readable(bankpath)),
      "manifestSha256After":sha(readable(mp)),
      "sqliteSha256After":sha(readable(dbp)),
      "sqliteRows":205,"sqliteIntegrity":"ok","singleQidUpdated":QID,
      "other204CanonicalJsonUnchanged":True,"other204SqlitePayloadsUnchanged":True,
      "other204ManifestItemsUnchanged":True,"status":"SOURCE_ONLY_SQLITE_205_PARITY_NOT_STUDENT_RELEASE",
      "ready":False,"live":False
    }
    jwrite(SQL_REPORT_REL,sqlite_receipt)
    report={
      "schemaVersion":1,"year":114,"questionId":QID,
      "taskId":"A-114-E11-CANONICAL-G2G3-20261107-MASTER-DISPATCH",
      "claim":"https://github.com/homelux-huang/7581707/issues/36#issuecomment-6718106733",
      "qaBaselineCommit":ORIGINAL_QA,
      "reviewer":"ROLE A source visual reviewer; NOT E content reviewer",
      "sourceOnly":True,"questionRevision":QREV,"originalSingleWebpSha256":WEBP,
      "sourceOriginalPageSha256":PAGE,"originalPublishedAnswerImageSha256":ANSWER_IMAGE,
      "originalSourcePdfSha256PreviouslyRecorded":PAPER_PDF,
      "officialAnswerPdfSha256PreviouslyRecorded":ANSWER_PDF,
      "correctionNoticePdfSha256PreviouslyRecorded":NOTICE_PDF,
      "onlyEnglishCorrectionQuestionIds":["114-00-E-26"],
      "officialPrintedAnswer":"A","originalDocumentDownloadedAndRehashedThisTask":False,
      "webpOriginalUnchanged":True,"optionsOriginalUnchanged":True,
      "imageVisualReceiptSha256":vis_sha,
      "publisherOcrIssuerPath":OCR_REL,"publisherOcrIssuerSha256":sha(readable(ROOT/OCR_REL)),
      "publisherOfficialIssuerPath":G3_REL,"publisherOfficialIssuerSha256":sha(readable(ROOT/G3_REL)),
      "canonicalQuestionVerified":True,"canonicalAnswerVerified":True,
      "sqliteRowCount":205,"sqliteOther204PayloadsUnchanged":True,
      "canonicalOther204Unchanged":True,"manifestOther204Unchanged":True,
      "studentReady":False,"independentRoleETrusted":False,"roleDFormal16of16":False,
      "mainApprovedOrLive":False,"status":"SOURCE_G1_G2_G3_CONFIRMED_PENDING_DISTINCT_E_D_MASTER"
    }
    jwrite(REPORT_REL,report)
    print("E11_SOURCE_ONLY_APPLIED: 205 JSON+SQLite identical except E11, 204 immutable, original image A, E26 correction notice only; NO E/D/READY/LIVE",flush=True)

def verify_post():
    bank=json_file(BASE/"questions.json")
    manifest=json_file(BASE/"webp-manifest.json")
    inventory=json_file(BASE/"inventory.json")
    report=json_file(ROOT/REPORT_REL)
    sqlproof=json_file(ROOT/SQL_REPORT_REL)
    rows=db_rows(BASE/"question-bank.sqlite3")
    demand(len(bank["questions"])==205 and len(manifest["items"])==205, "post 205 source")
    q=next(x for x in bank["questions"] if x["questionId"]==QID)
    m=next(x for x in manifest["items"] if x["questionId"]==QID)
    demand(q["questionVerified"] and q["answerVerified"] and q["textQaStatus"]=="PASS" and q["officialCorrectionChecked"] is True and q["officialFinalAnswer"]=="A" and q["reviewStatus"].startswith("SOURCE_VERIFIED_"), "post source admission G2/G3 flags")
    demand(q["answerProvenance"]["independentVisualVerification"] is True, "post printed answer verification")
    demand(m["visualReviewEvidence"]["referenceSha256"]==sha(readable(ROOT/VISUAL_REL)), "post G1 SHA document")
    demand(rev(q,WEBP)==QREV and q["answer"]=="A", "post original exact source revision")
    demand(all(json.loads(rows[x["questionId"]][0])==x for x in bank["questions"]), "205 post SQLite/JSON parity")
    demand(sha(readable(BASE/"question-bank.sqlite3"))==inventory["sqlite"]["dbSha256"]==sqlproof["sqliteSha256After"], "SQLite inventory/report SHA drift")
    demand(sha(readable(BASE/"questions.json"))==inventory["sqlite"]["sourceQuestionsSha256"]==sqlproof["sourceBankSha256After"], "bank SHA drift")
    demand(sha(readable(BASE/"webp-manifest.json"))==sqlproof["manifestSha256After"], "manifest SHA drift")
    demand(report["publisherOcrIssuerSha256"]==sha(readable(ROOT/OCR_REL)) and report["publisherOfficialIssuerSha256"]==sha(readable(ROOT/G3_REL)), "publisher G2/G3 raw bytes changed")
    demand(q["textQaEvidence"]["evidenceSha256"]==sha(readable(ROOT/A_TEXT_REL)) and q["officialFinalQaEvidence"]["evidenceSha256"]==sha(readable(ROOT/A_OFFICIAL_REL)), "admitted A source receipt mismatch")
    for rel,expected in HISTORICAL_BLOBS.items():
        demand(blob(readable(ROOT/rel))==expected,"post historical source receipt modified "+rel)
    demand(report["studentReady"] is False and report["independentRoleETrusted"] is False and report["mainApprovedOrLive"] is False and report["roleDFormal16of16"] is False,"forbidden fake release")
    for field in ("independentSolve","teachingQaStatus","teachingQaEvidence","uiQaStatus","uiQaEvidence","studentReleaseApproved"):
        demand(field not in q, "source-only E11 fake student evidence "+field)
    image_check(WEBP_REL,WEBP,WEBP_BLOB)
    image_check(PAGE_REL,PAGE,PAGE_BLOB)
    image_check(ANSWER_IMAGE_REL,ANSWER_IMAGE,ANSWER_IMAGE_BLOB)
    import sys
    sys.path.insert(0,str(ROOT/"_publisher_main"))
    from scripts import sudu_verified_publish as pub
    image_good=pub.image_proof(q,m,{},ROOT) and pub.visual_certificate(ROOT,m,QID)
    demand(image_good and pub.verify_bytes(ROOT,WEBP_REL,WEBP), "actual main publisher image G1 fail")
    text_good,ans_good=pub.source_proof(q,True,True,QREV)
    demand(text_good and ans_good,"actual main publisher G2/G3 canonical source fail")
    g2=pub.review_document(ROOT,114,OCR_REL,QID)
    g3=pub.review_document(ROOT,114,G3_REL,QID)
    demand(g2 is not None and g3 is not None, "actual publisher cannot load new G2/G3 issuer")
    demand(g2[0]["questionRevision"]==QREV and g2[0]["webpSha256"]==WEBP and g2[0]["question"]==q["question"] and g2[0]["options"]==q["options"] and g2[0]["visualTextCompared"] is True, "G2 issuer invalid")
    demand(g3[0]["finalAnswer"]=="A" and g3[0]["officialPdfSha256"]==ANSWER_PDF and pub.official_notice_scope_certified(ROOT,114,q,g3[0]), "G3 issuer notice incorrect")
    demand(pub.certificates_complete(ROOT,q,m,{}) is False, "source must not claim full student certificates")
    print(json.dumps({"status":"E11_SOURCE_ONLY_POSITIVE_G1_G2_G3","questionRevision":QREV,
       "webpSha256":WEBP,"ocrIssuerSha256":g2[1],"officialIssuerSha256":g3[1],
       "sqliteSha256":inventory["sqlite"]["dbSha256"],
       "approvedOrLive":False,"independentE":False,"formalD":False},ensure_ascii=False),flush=True)

def negative_test():
    q=json_file(BASE/"questions.json")["questions"]
    q=next(x for x in q if x["questionId"]==QID)
    g2=json_file(ROOT/OCR_REL);g3=json_file(ROOT/G3_REL)
    ledger=json_file(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")
    validate=lambda d: d.get("questionRevision")==QREV and d.get("webpSha256")==WEBP and d.get("question")==q["question"] and d.get("options")==q["options"] and d.get("visualTextCompared") is True
    demand(validate(g2),"positive G2 shape")
    altered=copy.deepcopy(g2);altered["webpSha256"]="0"*64;demand(not validate(altered),"fake G2 WebP not rejected")
    altered=copy.deepcopy(g2);altered["options"][0]+=" bad";demand(not validate(altered),"fake G2 options not rejected")
    altered=copy.deepcopy(g2);altered["questionRevision"]="0"*64;demand(not validate(altered),"fake revision not rejected")
    ensure_answer=lambda d: d.get("finalAnswer")=="A" and d.get("officialPdfSha256")==ANSWER_PDF and d.get("confirmationPdfSha256")==NOTICE_PDF and d.get("namedOfficialCorrectionQuestionIds")==["114-00-E-26"] and d.get("noObjectionForPaper") is False and d.get("noCorrectionForThisQuestion") is True and d.get("studentReleaseApproved") is False
    demand(ensure_answer(g3),"positive G3 shape")
    for field,value in (("finalAnswer","B"),("confirmationPdfSha256","0"*64),("noObjectionForPaper",True),("namedOfficialCorrectionQuestionIds",["114-00-E-11"]),("studentReleaseApproved",True)):
        wrong=copy.deepcopy(g3);wrong[field]=value;demand(not ensure_answer(wrong), "fake G3 "+field+" not rejected")
    en=[d for d in ledger["docs"] if d["paperCode"]=="00-E"]
    demand(len(en)==1 and [x["questionId"] for x in en[0]["confirmed"]]==["114-00-E-26"],"actual official named list")
    print("E11 3 OCR + 5 official release mutation negatives PASS",flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply",action="store_true")
    g.add_argument("--verify-post",action="store_true")
    ap.add_argument("--negatives",action="store_true")
    args=ap.parse_args()
    if args.apply: create_source_admission()
    else: verify_post()
    if args.negatives: negative_test()
