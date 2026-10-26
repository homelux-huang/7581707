#!/usr/bin/env python3
"""ROLE A: 114 English E11/E13/E14 FINAL TCTE answer-image/correction-scope QA.

Changes only three independently visually inspected official-answer admissions in
the 205-question canonical bank and the SAME three SQLite rows. Does not grant
source question QA, teaching, independent Role E content review, READY or LIVE.
Archived original pages/answers, visual QA and full correction notices are reused.
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/data/processed/114"
BANK=DIR/"questions.json"
DB=DIR/"question-bank.sqlite3"
REVIEW=DIR/"review-evidence"
NOTICE=DIR/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
STATUS=DIR/"official-confirmation-status.json"
SOURCE_QA=DIR/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
SOURCE_IMG=ROOT/"sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp"
ANSWER_IMG=ROOT/"sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp"
SRC_GIT="5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
ANSWER_GIT="5f2920313607af4e756095cd3d6098c8a3ab7440"
SOURCE_SHA="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
ANSWER_SHA="a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
PDF_Q_SHA="1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf"
PDF_A_SHA="ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325"
NOTICE_PDF_SHA="79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"
NOTICE_LEDGER_GIT="6b9a919f224bec8dc3659052a404b4173b6ef366"
NOTICE_STATUS_GIT="ecfb5663d5af6008fb71f721ec5f23c69d557f5f"
SOURCE_QA_GIT="c1154562fa30cb4b2720a6000a970cf09ef460ff"
BASE_SHA="47afa7108b92cbd37b81e0f2d9369a4a3c226ab1"
BASE_BANK_GIT="074bff8cbb9ca7bbc0aefd8580454892d21f7d6b"
BASE_DB_GIT="d0b94f2f3b2455590e303a1d3f193de1e4ce2b2b"
TASK="A-114-E11-E13-E14-FINAL-OFFICIAL-ANSWER-20261026-14"
ANSWER={"114-00-E-11":"A","114-00-E-13":"A","114-00-E-14":"D"}
WEBP={
  "114-00-E-11":"ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0",
  "114-00-E-13":"81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7",
  "114-00-E-14":"388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94",
}
CROP={"114-00-E-11":[90,275,1310,591],
      "114-00-E-13":[90,870,1310,1120],
      "114-00-E-14":[90,1118,1310,1369]}
EXPECTED_ORIGINAL_ANSWER_IMAGE_NUMBERS={"11":"A","13":"A","14":"D"}
OFFICIAL_REVIEWER="GPT-6 ChatGPT ROLE A actual official-announced answer WebP image QA (NOT human or ROLE E independent teaching review)"
REVIEWED_AT="2026-10-26"
def sha(b):return hashlib.sha256(b).hexdigest()
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def archived(name,blob):
    b=name.read_bytes()
    assert gitsha(b)==blob, (name,"archived Git blob differs")
    return b
def verify_archives():
    from scripts import sudu_verified_publish as publisher
    a=archived(SOURCE_IMG,SRC_GIT);b=archived(ANSWER_IMG,ANSWER_GIT)
    assert sha(a)==SOURCE_SHA and sha(b)==ANSWER_SHA
    with Image.open(SOURCE_IMG) as im,Image.open(ANSWER_IMG) as answer:
        im.load();answer.load()
        assert im.format==answer.format=="WEBP" and im.size==(1400,1981) and answer.size==(1400,1980)
    assert gitsha(NOTICE.read_bytes())==NOTICE_LEDGER_GIT
    assert gitsha(STATUS.read_bytes())==NOTICE_STATUS_GIT
    assert gitsha(SOURCE_QA.read_bytes())==SOURCE_QA_GIT
    notice=read(NOTICE);status=read(STATUS);visual=read(SOURCE_QA)
    assert notice["year"]==status["year"]==114
    assert notice["allPagesInFourDocumentsReviewed"] is True
    row=[x for x in notice["docs"] if x["paperCode"]=="00-E"]
    assert len(row)==1 and row[0]["pdfSha256"]==NOTICE_PDF_SHA
    assert row[0]["pageCount"]==1 and row[0]["allPagesVisuallyReviewed"] is True
    assert [i["questionId"] for i in row[0]["confirmed"]]==["114-00-E-26"]
    rec=status["confirmations"]["00-E"]
    assert rec["revisionDocumentSha256"]==NOTICE_PDF_SHA
    assert rec["revisionDocumentPages"]==1
    assert rec["perQuestionOfficialNoticeScopeEvidenceComplete"] is True
    assert rec["officialStatus"]=="question_or_answer_confirmation_document_exists"
    assert rec["revisionDocumentContent"]=="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED"
    assert status["officialNoticeEvidencePath"]==NOTICE.relative_to(ROOT).as_posix()
    assert status["finalAnswerMeetingDate"]=="2025-05-09"
    assert status["finalAnswerPublishedAt"]=="2025-05-09 17:00 Asia/Taipei"
    image_qa={x["questionId"]:x for x in visual["items"]}
    assert set(ANSWER)<=set(image_qa)
    for qid,letter in ANSWER.items():
        v=image_qa[qid]
        assert v["result"]=="PASS" and v["independentHumanReview"] is False
        assert v["reviewedWebpSha256"]==WEBP[qid]
        assert v["cropPixels"]==CROP[qid] and v["sourcePageSha256"]==SOURCE_SHA
        assert v["answerVerified"] is False and v["questionVerified"] is False
        p=ROOT/v["reviewedWebpPath"]
        imagedata=p.read_bytes()
        assert sha(imagedata)==WEBP[qid],("source WebP changed",qid)
        with Image.open(p) as im:
            im.load()
            assert im.format=="WEBP" and im.size==(1220,CROP[qid][3]-CROP[qid][1])
        assert len(letter)==1
    # Test the ACTUAL repository's year-specific official scoped notice validator.
    for qid,letter in ANSWER.items():
        proof={"noObjectionForPaper":False,"noCorrectionForThisQuestion":True,
               "correctionForQuestionReviewed":False,"confirmationPdfSha256":NOTICE_PDF_SHA}
        q={"paperCode":"00-E","questionId":qid}
        assert publisher.official_notice_scope_certified(ROOT,114,q,proof),(qid,"notice gate")
        assert not publisher.official_notice_scope_certified(ROOT,114,q,{**proof,"noObjectionForPaper":True})
        assert not publisher.official_notice_scope_certified(ROOT,114,q,{**proof,"confirmationPdfSha256":"0"*64})
        assert not publisher.official_notice_scope_certified(ROOT,114,q,{**proof,"noCorrectionForThisQuestion":False})
        # Guard against falsely treating the actual E26 correction as nonexistent.
        assert not publisher.official_notice_scope_certified(ROOT,114,{"paperCode":"00-E","questionId":"114-00-E-26"},proof)
    return notice,visual

def source_bank():
    d=read(BANK)
    assert d["year"]==114 and len(d["questions"])==205
    q={x["questionId"]:x for x in d["questions"]}
    assert len(q)==205 and set(ANSWER)<=set(q)
    for qid,letter in ANSWER.items():
        x=q[qid]
        assert x["year"]==114 and x["paperCode"]=="00-E"
        assert x["originalQuestionNumber"]==int(qid[-2:])
        assert x["answer"]==letter and x["answerMatched"] is True
        assert len(x["options"])==4 and all(str(a).strip() for a in x["options"])
        assert x["questionVerified"] is False and x["reviewStatus"]=="needs_review"
        assert x["questionProvenance"]["webpSha256"]==WEBP[qid]
        assert x["questionProvenance"]["pixelSourceSha256"]==SOURCE_SHA
        assert x["questionProvenance"]["officialPdfSha256"]==PDF_Q_SHA
        assert x["answerProvenance"]["officialPdfSha256"]==PDF_A_SHA
        assert x["imageQaStatus"]=="PASS"
    return d,q

def make_receipt(qid):
    letter=ANSWER[qid]
    return {
        "schemaVersion":1,"year":114,"questionId":qid,"reviewedAt":REVIEWED_AT,
        "reviewer":OFFICIAL_REVIEWER,"humanReviewerClaimed":False,
        "officialPdfSha256":PDF_A_SHA,"finalAnswer":letter,
        "correctionNoticeReviewed":True,"officialFinalAnswerImageQaPassed":True,
        "noObjectionForPaper":False,"noCorrectionForThisQuestion":True,
        "correctionForQuestionReviewed":False,"confirmationPdfSha256":NOTICE_PDF_SHA,
        "officialPage":"https://web1.tcte.edu.tw/EXAM/114_4y/",
        "officialFinalAnswerPdfUrl":"https://web1.tcte.edu.tw/EXAM/114_4y/downloader.php?obj=MTE0LTR5LTAwLWUtc3RhbmRhcmQucGRm",
        "officialAnswerImageSource":ANSWER_IMG.relative_to(ROOT).as_posix(),
        "officialAnswerImageSha256":ANSWER_SHA,
        "officialAnswerImageGitBlobSha1":ANSWER_GIT,
        "originalQuestionImageSource":SOURCE_IMG.relative_to(ROOT).as_posix(),
        "originalQuestionImageSha256":SOURCE_SHA,
        "originalQuestionImageGitBlobSha1":SRC_GIT,
        "reviewedSingleQuestionWebpSha256":WEBP[qid],
        "originalQuestionPdfSha256PreviouslyRecorded":PDF_Q_SHA,
        "officialAnswerPdfDownloadedAndRehashedThisSession":False,
        "originalQuestionPdfDownloadedAndRehashedThisSession":False,
        "confirmationPdfDownloadedAndRehashedThisSession":False,
        "archivedAnswerImageOpenedAndVisuallyReviewedThisSession":True,
        "archivedQuestionAndSingleImageVisuallyReviewedThisSession":True,
        "individualPrintedAnswerCell":{"number":int(qid[-2:]),"observedLetter":letter,
                                       "answerColumnIndex":2,
                                       "manualDirectObservation":"Read printed original 114 4-00-E announced-answer table in real archived WebP, and matching printed question"},
        "independentDirectOfficialFinalAnswerPdfRenderedInCurrentReview":False,
        "underlyingOfficialPdfDownloadAndShaEvidence":"https://github.com/homelux-huang/7581707/actions/runs/40097216703",
        "underlyingOfficialCorrectionPdfDownloadAndAllPageQa":"https://github.com/homelux-huang/7581707/actions/runs/40094431419",
        "underlyingOriginalQuestionVisualQa":"sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json",
        "underlyingOfficialCorrectionLedger":NOTICE.relative_to(ROOT).as_posix(),
        "officialConfirmationNamedQuestionIds":["114-00-E-26"],
        "independentRoleEContentQaPerformed":False,
        "sourceTextVerifiedPromoted":False,
        "questionVerifiedPromoted":False,
        "teachingQaPromoted":False,
        "uiQaPromoted":False,
        "readyOrLivePromoted":False,
        "evidenceStatus":"ORIGINAL_OFFICIAL_ANNOUNCED_ANSWER_VISUAL_QA__EXCLUDED_FROM_FULL_00E_CONFIRMATION_DOCUMENT__NO_CONTENT_RELEASE"
    }

def receipt_path(qid):
    return REVIEW/(qid+"-official.json")

def promote_answer_only(q,proof):
    from scripts import sudu_verified_publish as publisher
    q=copy.deepcopy(q)
    qid=q["questionId"]
    src_rev=publisher.text_revision(q,WEBP[qid])
    assert q.get("answerVerified") is False
    assert q.get("questionVerified") is False
    assert q.get("officialCorrectionChecked") is not True
    assert q.get("officialFinalQaEvidence") is None
    assert proof["questionId"]==qid and proof["finalAnswer"]==q["answer"]
    assert publisher.official_notice_scope_certified(ROOT,114,q,proof)
    q["answerVerified"]=True
    q["officialFinalAnswer"]=proof["finalAnswer"]
    q["officialCorrectionChecked"]=True
    q["answerProvenance"]["independentVisualVerification"]=True
    q["officialFinalQaEvidence"]={
        "reviewer":OFFICIAL_REVIEWER,"reviewedAt":REVIEWED_AT,
        "evidencePath":receipt_path(qid).relative_to(ROOT).as_posix(),
        "answerPdfSha256":PDF_A_SHA,"finalCorrectionsReviewed":True}
    assert publisher.text_revision(q,WEBP[qid])==src_rev,"answer-only QA altered teaching source revision"
    assert q["questionVerified"] is False and q["reviewStatus"]=="needs_review"
    assert q.get("integrationReady") is not True
    assert q.get("studentReleaseApproved") is not True
    return q

def precheck_db(path,bank):
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        cols={c[1] for c in db.execute("PRAGMA table_info(questions)")}
        # Actual 114 database has NO flattened answer_verified/question_verified:
        # exact normalized seven-column schema, all per-question approval flags
        # live only inside cryptographically checked canonical payload_json.
        required={"question_id","year","paper_code","original_number","subject","payload_json","payload_sha256"}
        assert cols==required, f"Unexpected 114 source SQLite schema: {sorted(cols)}"
        rows=db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205
    assert {x[0] for x in rows}=={q["questionId"] for q in bank["questions"]}
    qs={q["questionId"]:q for q in bank["questions"]}
    for qid,payload,digest in rows:
        assert sha(payload.encode("utf-8"))==digest,qid
        assert json.loads(payload)==qs[qid],qid
        assert payload==canonical(qs[qid]),qid

def update_three_sqlite(src,target,updates):
    shutil.copy2(src,target)
    with sqlite3.connect(target) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        for qid,q in sorted(updates.items()):
            row=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
            assert row is not None and sha(row[0].encode("utf-8"))==row[1]
            previous=json.loads(row[0])
            assert previous["answerVerified"] is False and previous["questionVerified"] is False
            assert q["answerVerified"] is True and q["questionVerified"] is False
            payload=canonical(q)
            result=db.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                 (payload,sha(payload.encode("utf-8")),qid))
            assert result.rowcount==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        records=db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions WHERE question_id IN (?,?,?)",tuple(sorted(ANSWER))).fetchall()
        assert len(records)==3
        for qid,payload,digest in records:
            assert sha(payload.encode("utf-8"))==digest
            assert json.loads(payload)["answerVerified"] is True
            assert json.loads(payload)["questionVerified"] is False
    return sha(target.read_bytes())

def verify_final(bank):
    verify_archives()
    data,mapping=source_bank()
    assert data==bank
    proof={}
    from scripts import sudu_verified_publish as publisher
    for qid,letter in ANSWER.items():
        q=mapping[qid]
        r=read(receipt_path(qid))
        proof[qid]=r
        assert r["finalAnswer"]==letter and r["officialFinalAnswerImageQaPassed"] is True
        assert r["archivedAnswerImageOpenedAndVisuallyReviewedThisSession"] is True
        assert r["officialAnswerImageSha256"]==ANSWER_SHA
        assert r["reviewedSingleQuestionWebpSha256"]==WEBP[qid]
        assert r["officialConfirmationNamedQuestionIds"]==["114-00-E-26"]
        assert r["noCorrectionForThisQuestion"] is True
        assert r["noObjectionForPaper"] is False
        assert not r["questionVerifiedPromoted"] and not r["independentRoleEContentQaPerformed"]
        assert publisher.official_notice_scope_certified(ROOT,114,q,r)
        assert q["answerVerified"] is True and q["officialFinalAnswer"]==letter
        assert q["officialCorrectionChecked"] is True
        assert q["answerProvenance"]["independentVisualVerification"] is True
        e=q["officialFinalQaEvidence"]
        assert e["answerPdfSha256"]==PDF_A_SHA and e["finalCorrectionsReviewed"] is True
        assert e["evidencePath"]==receipt_path(qid).relative_to(ROOT).as_posix()
        assert e["reviewer"]==OFFICIAL_REVIEWER
        assert q["questionVerified"] is False and q["reviewStatus"]=="needs_review"
        assert q.get("studentReleaseApproved") is not True
    print("ROLE_A_114_E11_E13_E14_SOURCE_REVISIONS",json.dumps({
        qid:{"sourceRevisionSha256":publisher.text_revision(mapping[qid],WEBP[qid]),
             "webpSha256":WEBP[qid],"officialPdfSha256":PDF_A_SHA,
             "answer":ANSWER[qid],"questionVerified":False}
        for qid in sorted(ANSWER)},sort_keys=True))
    precheck_db(DB,bank)
    with tempfile.TemporaryDirectory() as td:
        first=Path(td)/"x.sqlite3";second=Path(td)/"y.sqlite3"
        base_sql=Path(td)/"base.sqlite3"
        orig_git=subprocess.run(["git","show",BASE_SHA+":sudu/data/processed/114/question-bank.sqlite3"],cwd=ROOT,capture_output=True,check=True).stdout
        assert gitsha(orig_git)==BASE_DB_GIT
        base_sql.write_bytes(orig_git)
        update_three_sqlite(base_sql,first,{qid:mapping[qid] for qid in ANSWER})
        update_three_sqlite(base_sql,second,{qid:mapping[qid] for qid in ANSWER})
        assert sha(first.read_bytes())==sha(second.read_bytes())==sha(DB.read_bytes())
    print("ROLE_A_114_E11_E13_E14_OFFICIAL_PASS_3_205_SQL_PARITY_no_new_READY")

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--apply",action="store_true")
    cli.add_argument("--verify",action="store_true")
    opt=cli.parse_args()
    if opt.apply==opt.verify:cli.error("Select exactly one mode")
    verify_archives()
    data,qs=source_bank()
    if opt.verify:
        verify_final(data)
        return
    if all(qs[qid]["answerVerified"] is True for qid in ANSWER):
        verify_final(data)
        print("IDEMPOTENT_SOURCE_AND_SQL_NO_REWRITE")
        return
    bankbytes=BANK.read_bytes();dbbytes=DB.read_bytes()
    assert gitsha(bankbytes)==BASE_BANK_GIT,"source questions.json changed; re-derive diff before applying"
    assert gitsha(dbbytes)==BASE_DB_GIT,"source SQL changed; re-derive diff before applying"
    assert all(qs[qid]["answerVerified"] is False for qid in ANSWER)
    precheck_db(DB,data)
    proofs={qid:make_receipt(qid) for qid in ANSWER}
    for qid in ANSWER:
        assert not receipt_path(qid).exists(),"existing receipt cannot be overwritten"
    updated=copy.deepcopy(data)
    revised={qid:promote_answer_only(qs[qid],proofs[qid]) for qid in ANSWER}
    for i,q in enumerate(updated["questions"]):
        if q["questionId"] in ANSWER:
            updated["questions"][i]=revised[q["questionId"]]
        else:
            assert q==data["questions"][i]
    assert len(updated["questions"])==len(data["questions"])==205
    with tempfile.TemporaryDirectory(prefix="rolea-114-e11-13-14-",dir=DIR) as td:
        td=Path(td)
        tmpdb=td/"question-bank.sqlite3"
        update_three_sqlite(DB,tmpdb,revised)
        temporary=td/"questions.json"
        temporary.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        # Every unrelated row remains byte-for-byte data identical; no E12 promotion.
        assert len({q["questionId"] for q in updated["questions"]})==205
        with sqlite3.connect(tmpdb.as_uri()+"?mode=ro",uri=True) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        for qid,p in proofs.items():
            file=td/(qid+"-official.json")
            file.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        # Post-commit check verifies original notice+external evidence on real repo.
        os.replace(temporary,BANK)
        os.replace(tmpdb,DB)
        for qid in ANSWER:
            os.replace(td/(qid+"-official.json"),receipt_path(qid))
    print("ACTUAL_OFFICIAL_ANSWER_VISUAL_AND_NOTICE_SCOPE_3_NEW_VERIFIED_NO_READY")

if __name__=="__main__":main()
