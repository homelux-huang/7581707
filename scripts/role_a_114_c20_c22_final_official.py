#!/usr/bin/env python3
"""ROLE A — 114 Chinese C20/C21/C22, authentic TCTE answer-page visual QA.

Original lossless historical question WebPs and 20-23 shared article are reused.
Updates ONLY the three official answer QA records and matching 114 canonical SQLite
payloads. No new question OCR/teacher approval/independent E/UI/READY/LIVE flags.
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
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from scripts import sudu_verified_publish as publisher

BASE=ROOT/"sudu/data/processed/114"
BANK=BASE/"questions.json"
DB=BASE/"question-bank.sqlite3"
MANIFEST=BASE/"webp-manifest.json"
EVIDENCE=BASE/"review-evidence"
VISUAL=BASE/"qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json"
NOTICE=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
NOTICE_STATUS=BASE/"official-confirmation-status.json"
ORIGINAL_QUESTION=ROOT/"sudu/data/original/114/00-C/p007-f7c8a4b732-v2-w1400-q66.webp"
ORIGINAL_ANSWER=ROOT/"sudu/data/original/114/00-C-answers/p001-455eae60e7-v2-w1400-q66.webp"
SHARED_PATH=ROOT/"sudu/data/processed/114/webp-v2/shared/114-00-C-SHARED-20-23.webp"
BASE_SHA="abb1c711307409ab2cc40ea62e0772d3d26381af"
BASE_BANK_GIT="17e70610edd35744aa399f38fd0fe915c808d190"
BASE_DB_GIT="519bde855682b575e96ff24705bb1735d64774e9"
ORIGINAL_QUESTION_GIT="eddea1c33102085accd4a33cc5835e2a70188800"
ORIGINAL_ANSWER_GIT="c3090e94ab1cbf7adf9f7efd0581529eff00e26b"
ORIGINAL_QUESTION_SHA="63d68af4507fd198cd045a5a24b4efd4f33f95b1c234e991fe0f9ed65c76bfa2"
QUESTION_PDF_SHA="f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74"
ANSWER_PDF_SHA="455eae60e7c8f943ada011bac3f488520a460432310448dc531dee7f0fd9e1e0"
NOTICE_PDF_SHA="afc4ad2e67004a40539d05406813ff361d99696607cf6fc71c62484cc3001a71"
NOTICE_GIT="6b9a919f224bec8dc3659052a404b4173b6ef366"
NOTICE_STATUS_GIT="ecfb5663d5af6008fb71f721ec5f23c69d557f5f"
VISUAL_GIT="ccb9e0dd590e5649d57832a728552fbe88d2efac"
SHARED_GIT="2f3ee33a071975a74e9b5c5b28db423a4b49003f"
SHARED_SHA="7b7f592f01378a6fa9ece08d87291810420479c9529f2d5233f10ad458c47f8a"
SHARED_ID="114-00-C-SHARED-20-23"
TASK="A-114-C20-C22-FINAL-ANSWERS-SHARED-PIXELS-20261026-15"
REVIEWED_AT="2026-10-26"
REVIEWER="ChatGPT Role A direct original TCTE published-answer image QA, NOT different-author Role E teaching QA or human teacher"
PDF_URL="https://web1.tcte.edu.tw/EXAM/114_4y/downloader.php?obj=MTE0LTR5LTAwLWMtc3RhbmRhcmQucGRm"
ANSWER={
    "114-00-C-20":"C",
    "114-00-C-21":"C",
    "114-00-C-22":"A",
}
IMAGE={
    "114-00-C-20":("6381a4a7c8d48b85c26d6968246c4da3a52f6f2e",
        "13ceb4e57baa428cfa09a59e381b84d7f3bf114d6ff60fe1df20f0fe527ae19c",[90,1022,1310,1223]),
    "114-00-C-21":("13a551f04a63bbc5c08c5bccbd583c524bda6292",
        "290d7b3a11395cbe05e2fb1f86fa47986b3c03fc1dde44d97b0baef7e405e975",[90,1221,1310,1422]),
    "114-00-C-22":("9b60c67a0bf36c17de5b0ae8cda0622766c01415",
        "b795e87aabd5b3d3ea07b32afc7ebc51a983afaa72351fe1eebaace49772482b",[90,1420,1310,1584]),
}
NAMED=["114-00-C-14","114-00-C-24","114-00-C-28","114-00-C-30"]
def sha(data):return hashlib.sha256(data).hexdigest()
def gitsha(data):return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def assert_webp(path,gitblob,expected_sha=None,dims=None):
    raw=path.read_bytes()
    assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP",str(path)
    assert gitsha(raw)==gitblob,(str(path),"original Git object mismatch")
    if expected_sha is not None:assert sha(raw)==expected_sha,(str(path),"wrong SHA256")
    with Image.open(path) as im:
        im.load()
        assert im.format=="WEBP"
        if dims is not None:assert im.size==tuple(dims),(str(path),im.size,dims)
    return sha(raw)
def receipt_path(qid):return EVIDENCE/(qid+"-official.json")
def verify_archives():
    original_sha=assert_webp(ORIGINAL_QUESTION,ORIGINAL_QUESTION_GIT,ORIGINAL_QUESTION_SHA,(1400,1981))
    answer_sha=assert_webp(ORIGINAL_ANSWER,ORIGINAL_ANSWER_GIT,dims=(1400,1980))
    shared_sha=assert_webp(SHARED_PATH,SHARED_GIT,SHARED_SHA,(1220,455))
    assert shared_sha==SHARED_SHA and original_sha==ORIGINAL_QUESTION_SHA
    assert gitsha(VISUAL.read_bytes())==VISUAL_GIT
    assert gitsha(NOTICE.read_bytes())==NOTICE_GIT
    assert gitsha(NOTICE_STATUS.read_bytes())==NOTICE_STATUS_GIT
    doc=read(NOTICE);status=read(NOTICE_STATUS);visual=read(VISUAL)
    assert doc["year"]==status["year"]==114
    assert doc["allPagesInFourDocumentsReviewed"] is True
    docs=[x for x in doc["docs"] if x["paperCode"]=="00-C"]
    assert len(docs)==1
    notice=docs[0]
    assert notice["pdfSha256"]==NOTICE_PDF_SHA and notice["pageCount"]==5
    assert notice["allPagesVisuallyReviewed"] is True and notice["noticeScopeOnly"] is True
    assert [x["questionId"] for x in notice["confirmed"]]==NAMED
    assert all(x["publishedFinalAnswerImageIndependentlyVerified"] is False for x in notice["confirmed"])
    assert status["confirmations"]["00-C"]["revisionDocumentSha256"]==NOTICE_PDF_SHA
    assert status["confirmations"]["00-C"]["perQuestionOfficialNoticeScopeEvidenceComplete"] is True
    assert status["finalAnswerMeetingDate"]=="2025-05-09"
    assert status["finalAnswerPublishedAt"]=="2025-05-09 17:00 Asia/Taipei"
    assert visual["imageQaPassAdded"]==5 and visual["sharedMaterialQaPassAdded"]==1
    assert visual["answerVerifiedAdded"]==0 and visual["questionVerifiedAdded"]==0
    assert visual["releaseAllowed"] is False and visual["integrationReady"] is False
    shared=visual["sharedMaterial"]
    assert shared["sharedMaterialId"]==SHARED_ID
    assert shared["outputSha256"]==SHARED_SHA
    assert shared["result"]=="PASS_DIRECT_ORIGINAL_PAGE_SHARED_ARTICLE_VISUAL"
    assert shared["sourcePageWebpSha256"]==ORIGINAL_QUESTION_SHA
    assert shared["cropSourcePixelBounds"]==[90,565,1310,1020]
    for qid,letter in ANSWER.items():
        _,expected_sha,crop=IMAGE[qid]
        imagedir=ROOT/f"sudu/data/processed/114/webp-v1/00-C/{qid}.webp"
        file_sha=assert_webp(imagedir,IMAGE[qid][0],expected_sha,[1220,crop[3]-crop[1]])
        assert file_sha==expected_sha
        v=next(v for v in visual["items"] if v["questionId"]==qid)
        assert v["result"]=="PASS_DIRECT_ORIGINAL_PAGE_IMAGE"
        assert v["reviewedWebpPath"]==imagedir.relative_to(ROOT).as_posix()
        assert v["reviewedWebpSha256"]==expected_sha
        assert v["sourcePageWebpSha256"]==ORIGINAL_QUESTION_SHA
        assert v["cropSourcePixelBounds"]==crop and all(v["visualCriteria"].values())
        assert v["independentHumanReview"] is False
        assert v["answerVerified"] is False and v["questionVerified"] is False
        assert v["sharedMaterialIds"]==[SHARED_ID]
        proof={"noObjectionForPaper":False,"noCorrectionForThisQuestion":True,
               "correctionForQuestionReviewed":False,"confirmationPdfSha256":NOTICE_PDF_SHA}
        testq={"questionId":qid,"paperCode":"00-C"}
        assert publisher.official_notice_scope_certified(ROOT,114,testq,proof)
        assert not publisher.official_notice_scope_certified(ROOT,114,testq,{**proof,"noObjectionForPaper":True})
        assert not publisher.official_notice_scope_certified(ROOT,114,testq,{**proof,"confirmationPdfSha256":"0"*64})
        assert not publisher.official_notice_scope_certified(ROOT,114,testq,{**proof,"noCorrectionForThisQuestion":False})
        assert not publisher.official_notice_scope_certified(ROOT,114,{"paperCode":"00-C","questionId":"114-00-C-24"},proof)
    man=read(MANIFEST)
    shared_items=[x for x in man["sharedMaterialCrops"] if x["sharedMaterialId"]==SHARED_ID]
    assert len(shared_items)==1 and shared_items[0]["sha256"]==SHARED_SHA
    assert shared_items[0]["qaStatus"]=="PASS"
    for qid,letter in ANSWER.items():
        im=next(x for x in man["items"] if x["questionId"]==qid)
        assert im["sha256"]==IMAGE[qid][1] and im["qaStatus"]=="PASS"
        assert im["sourceSha256"]==ORIGINAL_QUESTION_SHA
        assert im["crop"]==IMAGE[qid][2]
    return answer_sha
def source_bank():
    d=read(BANK);arr=d["questions"]
    assert d["year"]==114 and len(arr)==205
    m={q["questionId"]:q for q in arr}
    assert len(m)==205 and set(ANSWER)<=set(m)
    for qid,letter in ANSWER.items():
        q=m[qid]
        assert q["year"]==114 and q["paperCode"]=="00-C" and q["originalQuestionNumber"]==int(qid[-2:])
        assert q["answer"]==letter and q["answerMatched"] is True
        assert q["questionVerified"] is False and q["reviewStatus"]=="needs_review"
        assert len(q["options"])==4 and all(isinstance(t,str) and t.strip() for t in q["options"])
        assert q["imageQaStatus"]=="PASS"
        assert q["questionProvenance"]["webpSha256"]==IMAGE[qid][1]
        assert q["questionProvenance"]["pixelSourceSha256"]==ORIGINAL_QUESTION_SHA
        assert q["questionProvenance"]["officialPdfSha256"]==QUESTION_PDF_SHA
        assert q["answerProvenance"]["officialPdfSha256"]==ANSWER_PDF_SHA
        assert q["assets"]["sha256"]==IMAGE[qid][1]
        assert q["assets"]["sharedMaterialIds"]==[SHARED_ID]
        assert q["assets"]["sharedMaterialWebp"]==SHARED_PATH.relative_to(ROOT).as_posix()
        assert q.get("integrationReady") is not True
    return d,m
def receipt(qid,ans_sha):
    letter=ANSWER[qid]
    return {
        "schemaVersion":1,"year":114,"questionId":qid,"taskId":TASK,
        "reviewer":REVIEWER,"reviewedAt":REVIEWED_AT,"humanReviewerClaimed":False,
        "officialPdfSha256":ANSWER_PDF_SHA,"finalAnswer":letter,
        "officialFinalAnswerImageQaPassed":True,"correctionNoticeReviewed":True,
        "noObjectionForPaper":False,"noCorrectionForThisQuestion":True,
        "correctionForQuestionReviewed":False,"confirmationPdfSha256":NOTICE_PDF_SHA,
        "officialFinalAnswerPdfUrl":PDF_URL,
        "sourceIndex":"https://web1.tcte.edu.tw/EXAM/114_4y/",
        "officialAnswerImageSource":ORIGINAL_ANSWER.relative_to(ROOT).as_posix(),
        "officialAnswerImageSha256":ans_sha,"officialAnswerImageGitBlobSha1":ORIGINAL_ANSWER_GIT,
        "officialQuestionPageSource":ORIGINAL_QUESTION.relative_to(ROOT).as_posix(),
        "officialQuestionPageWebpSha256":ORIGINAL_QUESTION_SHA,
        "officialQuestionPageGitBlobSha1":ORIGINAL_QUESTION_GIT,
        "reviewedSingleQuestionWebpSha256":IMAGE[qid][1],
        "sharedMaterialId":SHARED_ID,"sharedMaterialWebpSha256":SHARED_SHA,
        "originalQuestionPdfSha256PreviouslyRecorded":QUESTION_PDF_SHA,
        "officialAnswerPdfDownloadedAndRehashedThisSession":False,
        "originalQuestionPdfDownloadedAndRehashedThisSession":False,
        "confirmationPdfDownloadedAndRehashedThisSession":False,
        "archivedAnswerImageOpenedAndVisuallyReviewedThisSession":True,
        "archivedQuestionAndSharedImagesVisuallyReviewedThisSession":True,
        "individualPrintedAnswerCell":{"number":int(qid[-2:]),"observedLetter":letter,
            "answerColumnIndex":2,
            "manualDirectObservation":"Directly read genuine archived 114 4-00-C announced answer p1 cell and genuine C20–C22 exam p7 original pixels"},
        "independentDirectOfficialFinalAnswerPdfRenderedInCurrentReview":False,
        "underlyingOfficialCorrectionPdfFullScopeEvidence":"sudu/data/processed/114/QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json",
        "underlyingOriginalVisualQa":"sudu/data/processed/114/qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json",
        "officialConfirmationNamedQuestionIds":NAMED,
        "independentRoleEContentQaPerformed":False,
        "sourceTextVerifiedPromoted":False,"questionVerifiedPromoted":False,
        "teachingQaPromoted":False,"uiQaPromoted":False,
        "readyOrLivePromoted":False,
        "evidenceStatus":"ORIGINAL_OFFICIAL_00C_ANSWER_VISUAL_QA_AND_COMPLETE_NOTICE_SCOPE__NO_INDEPENDENT_CONTENT_RELEASE"
    }
def promote_answer_only(q,p):
    q=copy.deepcopy(q)
    qid=q["questionId"]
    oldrev=publisher.text_revision(q,IMAGE[qid][1])
    assert q["answerVerified"] is False and q["questionVerified"] is False
    assert q.get("officialCorrectionChecked") is not True
    assert q.get("officialFinalQaEvidence") is None
    assert p["questionId"]==qid and p["finalAnswer"]==q["answer"]
    assert publisher.official_notice_scope_certified(ROOT,114,q,p)
    q["answerVerified"]=True
    q["officialFinalAnswer"]=p["finalAnswer"]
    q["officialCorrectionChecked"]=True
    q["answerProvenance"]["independentVisualVerification"]=True
    q["officialFinalQaEvidence"]={
        "reviewer":REVIEWER,"reviewedAt":REVIEWED_AT,
        "evidencePath":receipt_path(qid).relative_to(ROOT).as_posix(),
        "answerPdfSha256":ANSWER_PDF_SHA,"finalCorrectionsReviewed":True}
    assert publisher.text_revision(q,IMAGE[qid][1])==oldrev
    assert q["questionVerified"] is False and q["reviewStatus"]=="needs_review"
    assert q.get("integrationReady") is not True and q.get("studentReleaseApproved") is not True
    return q
def db_precheck(path,bank):
    items={q["questionId"]:q for q in bank["questions"]}
    assert len(items)==len(bank["questions"])==205
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        columns={r[1] for r in db.execute("PRAGMA table_info(questions)")}
        assert columns=={"question_id","year","paper_code","original_number","subject","payload_json","payload_sha256"}
        rows=db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205 and {r[0] for r in rows}==set(items)
    for qid,payload,digest in rows:
        assert sha(payload.encode("utf-8"))==digest,qid
        assert payload==canonical(items[qid]),qid
        assert json.loads(payload)==items[qid],qid
def update_db(source,target,updates):
    shutil.copy2(source,target)
    with sqlite3.connect(target) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        for qid,q in sorted(updates.items()):
            original=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
            assert original is not None and sha(original[0].encode("utf-8"))==original[1]
            before=json.loads(original[0])
            assert before["answerVerified"] is False and before["questionVerified"] is False
            assert q["answerVerified"] is True and q["questionVerified"] is False
            payload=canonical(q)
            changed=db.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                (payload,sha(payload.encode("utf-8")),qid))
            assert changed.rowcount==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    return sha(target.read_bytes())
def verify_final():
    ans_sha=verify_archives()
    bank,items=source_bank()
    for qid in ANSWER:
        q=items[qid]
        p=read(receipt_path(qid))
        assert p["questionId"]==qid and p["finalAnswer"]==ANSWER[qid]
        assert p["officialAnswerImageSha256"]==ans_sha and p["officialAnswerImageGitBlobSha1"]==ORIGINAL_ANSWER_GIT
        assert p["reviewedSingleQuestionWebpSha256"]==IMAGE[qid][1]
        assert p["sharedMaterialWebpSha256"]==SHARED_SHA
        assert p["officialConfirmationNamedQuestionIds"]==NAMED
        assert p["noCorrectionForThisQuestion"] is True and p["noObjectionForPaper"] is False
        assert p["officialFinalAnswerImageQaPassed"] is True
        assert not p["independentRoleEContentQaPerformed"]
        assert not p["sourceTextVerifiedPromoted"] and not p["questionVerifiedPromoted"]
        assert not p["teachingQaPromoted"] and not p["uiQaPromoted"]
        assert not p["readyOrLivePromoted"]
        assert publisher.official_notice_scope_certified(ROOT,114,q,p)
        assert q["answerVerified"] is True and q["officialFinalAnswer"]==ANSWER[qid]
        assert q["officialCorrectionChecked"] is True
        assert q["officialFinalQaEvidence"]["answerPdfSha256"]==ANSWER_PDF_SHA
        assert q["officialFinalQaEvidence"]["evidencePath"]==receipt_path(qid).relative_to(ROOT).as_posix()
        assert q["answerProvenance"]["independentVisualVerification"] is True
        assert q["questionVerified"] is False and q["reviewStatus"]=="needs_review"
        assert q.get("integrationReady") is not True and q.get("studentReleaseApproved") is not True
    db_precheck(DB,bank)
    with tempfile.TemporaryDirectory() as tmp:
        prior=Path(tmp)/"previous.sqlite3"
        raw=subprocess.run(["git","show",BASE_SHA+":sudu/data/processed/114/question-bank.sqlite3"],
            cwd=ROOT,check=True,capture_output=True).stdout
        assert gitsha(raw)==BASE_DB_GIT
        prior.write_bytes(raw)
        first=Path(tmp)/"1.sqlite3";second=Path(tmp)/"2.sqlite3"
        for x in [first,second]:
            update_db(prior,x,{qid:items[qid] for qid in ANSWER})
            assert sha(x.read_bytes())==sha(DB.read_bytes())
        with sqlite3.connect(prior) as db1,sqlite3.connect(DB) as db2:
            b={x[0]:x[1:] for x in db1.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            a={x[0]:x[1:] for x in db2.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
        assert set(b)==set(a) and {k for k in b if b[k]!=a[k]}==set(ANSWER)
    print("ROLE_A_114_C20_C22_FINAL_OFFICIAL_3_205_SQL_PARITY",
          json.dumps({qid:{"answer":ANSWER[qid],"sourceRevisionSha256":publisher.text_revision(items[qid],IMAGE[qid][1]),
                           "webpSha256":IMAGE[qid][1],"sharedWebpSha256":SHARED_SHA,
                           "officialAnswerPdfSha256":ANSWER_PDF_SHA,"questionVerified":False}
                      for qid in ANSWER},sort_keys=True))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true");parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply==args.verify:parser.error("select exactly one of --apply / --verify")
    answer_sha=verify_archives()
    bank,mapping=source_bank()
    if args.verify:
        verify_final()
        return
    if all(mapping[k]["answerVerified"] is True for k in ANSWER):
        verify_final();print("IDEMPOTENT NO WRITE")
        return
    assert gitsha(BANK.read_bytes())==BASE_BANK_GIT,"baseline canonical JSON drift; rebase after review"
    assert gitsha(DB.read_bytes())==BASE_DB_GIT,"baseline SQLite drift; do not overwrite"
    db_precheck(DB,bank)
    assert all(mapping[k]["answerVerified"] is False for k in ANSWER)
    evidence={k:receipt(k,answer_sha) for k in ANSWER}
    assert all(not receipt_path(k).exists() for k in ANSWER)
    changes={k:promote_answer_only(mapping[k],evidence[k]) for k in ANSWER}
    updated=copy.deepcopy(bank)
    for i,q in enumerate(updated["questions"]):
        if q["questionId"] in changes:updated["questions"][i]=changes[q["questionId"]]
        else:assert q==bank["questions"][i],q["questionId"]
    with tempfile.TemporaryDirectory(prefix="role-a114-c20-22-",dir=BASE) as tmp:
        tmp=Path(tmp)
        tmpdb=tmp/"question-bank.sqlite3"
        update_db(DB,tmpdb,changes)
        with sqlite3.connect(tmpdb) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        tmpbank=tmp/"questions.json"
        tmpbank.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,p in evidence.items(): (tmp/(k+"-official.json")).write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        os.replace(tmpbank,BANK)
        os.replace(tmpdb,DB)
        for k in ANSWER:os.replace(tmp/(k+"-official.json"),receipt_path(k))
    verify_final()
    print("APPLIED ONLY 114 C20-22 official answer QA to canonical+205 SQL, no E/READY/LIVE")
if __name__=="__main__":main()
