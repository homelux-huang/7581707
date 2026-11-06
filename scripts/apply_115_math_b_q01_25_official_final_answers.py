#!/usr/bin/env python3
"""G3-only: 115 common subject Math B 00-MB Q01-25 FINAL official answers.

Verified visually against the official final-answer WebP derived from the
published TCTE PDF and the official 115 index saying "4-00-MB 未提出疑義".
Every value has an independently recorded manual image read + SHA-bound source.
Preserves G1/G2/questionVerified/old QA image work and release blockers.
This program NEVER independently marks any image or OCR QA PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/115")
BRANCH="qa/114-115-official-visual-review"
EVID=BASE/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
IMAGE=Path("sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp")
PDF_SHA="d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
INDEX_SHA="ce4d0b1c73d393c34f7a8e9409fcde3bc012739cbd36f700e5d7fdcfe046588c"
VALUES={f"115-00-MB-{i:02d}":v for i,v in enumerate("BAACBDBDACDDADDCCCBAABBCC",start=1)}
N=205

def path(p):
    t=(ROOT/p).resolve()
    if not t.is_relative_to(ROOT): raise RuntimeError("Repository path escape")
    return t

def load(p):
    return json.loads(path(p).read_text("utf8"))

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def git_blob_sha(data):
    return hashlib.sha1(("blob "+str(len(data))).encode("ascii")+bytes([0])+data).hexdigest()

def idx(items):
    x={p["questionId"]:p for p in items}
    assert len(x)==len(items)
    return x

def put(p,o):
    path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def run(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    ledger=load(EVID)
    assert ledger["year"]==115 and ledger["paperCode"]=="00-MB"
    assert ledger["itemCount"]==25 and ledger["answerVerifiedAddedAfterApply"]==25
    assert ledger["imageQaAdded"]==0 and ledger["questionVerifiedAdded"]==0
    assert not ledger["releaseAllowed"] and not ledger["integrationReady"]
    assert not ledger["independentHumanReview"]
    published=ledger["officialPublishedFinalAnswer"]
    assert published["pdfSha256"]==PDF_SHA and published["image"]==IMAGE.as_posix()
    assert published["page"]==1
    actual=path(IMAGE).read_bytes()
    assert actual.startswith(b"RIFF") and b"WEBP" in actual[:16]
    assert git_blob_sha(actual)==published["imageGitBlobSha1"],"Image has been modified since direct visual review"
    image_sha=sha_bytes(actual)
    official=ledger["officialNotice"]
    assert official["officialIndexSha256InExistingLedger"]==INDEX_SHA
    assert official["statusAtCode"]=="4-00-MB 未提出疑義"
    confirmed=load(BASE/"official-confirmation-status.json")
    assert confirmed["confirmations"]["00-MB"]["officialStatus"]=="no_objection_submitted"
    assert confirmed["officialNoticeEvidencePath"]==(
        BASE/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json").as_posix()
    c=load(BASE/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json")
    assert c["allPagesInThreeDocumentsReviewed"] and c["officialNoticeAnswerConflicts"]==0
    records=idx(ledger["records"])
    assert set(records)==set(VALUES)
    b=load(BASE/"questions.json")
    evidence=load(BASE/"official-answer-evidence.json")
    inv=load(BASE/"inventory.json")
    validation=load(BASE/"VALIDATION.json")
    release=load(BASE/"release-manifest.json")
    assert len(b["questions"])==len(evidence["items"])==N
    qs=idx(b["questions"])
    ev=idx(evidence["items"])
    assert set(qs)==set(ev)
    assert evidence["papers"]["00-MB"]["pdfSha256"]==PDF_SHA
    before=sum(x.get("answerVerified") is True for x in b["questions"])
    assert before in (56,81)
    assert inv["officialAnswerIndependentVerified"]==before
    assert evidence["answerVerifiedCount"]==before
    assert inv["imageVisualQaPass"]==143 and inv["perSubject"]["國文"]["visualQaPass"]==17
    pending=[qid for qid in sorted(VALUES) if qs[qid].get("answerVerified") is not True]
    assert len(pending) in (0,25),"Partially applied answer batch requires manual reconciliation"
    for qid,letter in VALUES.items():
        row=records[qid];q=qs[qid];e=ev[qid]
        assert row["officialFinalAnswerReadDirectlyFromPublishedImage"]==letter
        assert row["officialCandidateExpected"]==letter
        assert row["correctionStatus"]=="NO_OBJECTION_SUBMITTED_4_00_MB"
        assert row["officialCorrectionChecked"] and row["answerVerified"]
        assert row["sourceOfficialAnswerPdfSha256"]==PDF_SHA and row["sourcePage"]==1
        assert q["answer"]==e["candidateValue"]==e["officialExtractedValue"]==letter
        assert q["answerProvenance"]["pdfSha256"]==PDF_SHA
        assert e["officialSourceSha256"]==PDF_SHA
        assert e["sourcePage"]==1
        assert e["answerMatched"] and e["comparison"]=="MATCHED"
        assert not q.get("integrationReady")
        if qid not in pending:
            assert e["answerVerified"] and e["officialAnswerImageSha256"]==image_sha
            assert q["answerQaEvidence"]==EVID.as_posix()
    if not stage or not pending:
        return {"mode":"CHECK" if not stage else "IDEMPOTENT",
                "existingVerified":before,"pending":len(pending),
                "currentImageSHA256":image_sha,"answerVerifiedAdded":0 if not stage else len(pending),
                "releaseAllowed":False}
    for qid in pending:
        row=records[qid];q=qs[qid];e=ev[qid]
        q["answerVerified"]=True
        q["officialFinalAnswer"]=VALUES[qid]
        q["officialCorrectionChecked"]=True
        q["officialAnswerQaStatus"]="PASS_FINAL_OFFICIAL_ANSWER_AND_NO_OBJECTION_NOTICE"
        q["answerQaEvidence"]=EVID.as_posix()
        q["integrationReady"]=False
        e["answerVerified"]=True
        e["officialFinalAnswer"]=VALUES[qid]
        e["qaStatus"]="PASS_TCTE_115_FINAL_AND_00_MB_NO_OBJECTION"
        e["visualReviewStatus"]="PASS_DIRECT_FINAL_ANSWER_IMAGE"
        e["officialCorrectionStatus"]="OFFICIAL_00_MB_NO_OBJECTION_SUBMITTED"
        e["officialCorrectionChecked"]=True
        e["officialCorrectionPageUrl"]=official["url"]
        e["officialCorrectionPageSha256"]=INDEX_SHA
        e["officialAnswerImageSha256"]=image_sha
        e["qaReviewer"]="ChatGPT assistant"
        e["qaReviewedAt"]="2026-10-23"
        e["qaEvidencePath"]=EVID.as_posix()
    assert sum(x.get("answerVerified") is True for x in b["questions"])==81
    evidence["answerVerifiedCount"]=81
    evidence["verificationRule"]=(
        "6 00-C verified final answers, all 50 09-1 verified answers, "
        "and all 25 Math(B) answers directly matched the source official final image/no-objection notice")
    inv["officialAnswerIndependentVerified"]=81
    inv["perSubject"]["數學B"]["officialAnswerIndependentlyVerified"]+=25
    validation["stats"]["數學B"]["officialAnswerIndependentlyVerified"]+=25
    validation["officialAnswers"]="PARTIAL_81_SHA_BOUND_TCTE_FINAL_ANSWERS_OTHERS_PENDING"
    validation["integrationReady"]=False
    release["officialFinalAnswerQA"]="PARTIAL_81_OF_205"
    release["releaseAllowed"]=False
    release["integrationReady"]=False
    confirmed["interpretation"]=(
        "TCTE confirmation PDFs 00-C, 00-E, 09-2 reviewed; 00-MB and 09-1 no objections. "
         "Six 00-C, all fifty 09-1, and all twenty-five Math B answers individually visually verified. All other "
        "answers, text, shared materials, and G6 release require separate review.")
    assert not any(x.get("integrationReady") for x in b["questions"])
    assert sum(x.get("answerVerified") is True for x in evidence["items"])==81
    dbfile=path(BASE/"question-bank.sqlite3")
    with sqlite3.connect(dbfile) as db:
        cols={x[1] for x in db.execute("PRAGMA table_info(questions)")}
        assert {"question_id","payload_sha256"}<=cols
        field="payload" if "payload" in cols else "payload_json"
        assert field in cols
        tables={t[0] for t in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert not {"student_answers","student_results","student_progress"}.intersection(tables)
        for qid in pending:
            wire=json.dumps(qs[qid],ensure_ascii=False,sort_keys=True,separators=(",",":"))
            digest=sha_bytes(wire.encode("utf8"))
            assert db.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                              (wire,digest,qid)).rowcount==1
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==N
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        for qid,wire,digest in db.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
            assert sha_bytes(wire.encode("utf8"))==digest
            assert json.loads(wire)["questionId"]==qid
    for filename,obj in (
        ("questions.json",b),("official-answer-evidence.json",evidence),
        ("inventory.json",inv),("VALIDATION.json",validation),
        ("release-manifest.json",release),("official-confirmation-status.json",confirmed)):
        put(BASE/filename,obj)
    return {"mode":"STAGE","answerVerifiedAdded":25,"answerVerifiedTotal":81,
            "imageQaUnchanged":143,"textQaUnchanged":True,"releaseAllowed":False,
            "officialAnswerImageSha256":image_sha}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check",action="store_true")
    modes.add_argument("--stage",action="store_true")
    z=parser.parse_args()
    print(json.dumps(run(stage=z.stage),ensure_ascii=False))
