#!/usr/bin/env python3
"""115 Math(B) Q05: apply the already visually-reviewed fraction text, preserving
all original OCR and answers; update only this isolated QA record and its SQLite
payload. This script does NOT certify pedagogy, UI or release.
"""
import argparse
import difflib
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/115")
QID="115-00-MB-05"
BRANCH="qa/114-115-official-visual-review"
EVIDENCE=BASE/"review-evidence/115-00-MB-05-ocr-correction-20261024.json"
REPORT=BASE/"review-evidence/115-00-MB-05-source-text-applied-20261024.json"

def path(p):
    z=(ROOT/p).resolve()
    assert z.is_relative_to(ROOT), p
    return z

def read(p):
    return json.loads(path(p).read_text("utf8"))

def write(p,obj):
    path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def sha(p):
    return hashlib.sha256(path(p).read_bytes()).hexdigest()

def canon(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def verify_db(dbfile,expected):
    with sqlite3.connect(path(dbfile)) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
        field="payload" if "payload" in cols else "payload_json"
        assert {"question_id","payload_sha256",field}<=cols
        rows=db.execute("SELECT question_id,"+field+",payload_sha256 FROM questions").fetchall()
        assert len(rows)==len(expected)==205
        expected_ids={q["questionId"]:q for q in expected}
        assert len(expected_ids)==205
        for qid,wire,h in rows:
            assert qid in expected_ids
            assert hashlib.sha256(wire.encode("utf8")).hexdigest()==h, qid
            assert json.loads(wire)==expected_ids[qid],qid
    return field

def execute(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    ev=read(EVIDENCE)
    assert ev["questionId"]==QID and ev["year"]==115
    assert ev["stage"]=="SOURCE_WEBP_TO_TEXT_CORRECTION_EVIDENCE_ONLY"
    assert sha(ev["imagePath"])==ev["imageSha256"]
    bank=read(BASE/"questions.json")
    qs=bank["questions"]
    assert len(qs)==205 and len({q["questionId"] for q in qs})==205
    q=next(q for q in qs if q["questionId"]==QID)
    m=next(x for x in read(BASE/"webp-manifest.json")["items"] if x["questionId"]==QID)
    assert m["qaStatus"]=="PASS" and m["sha256"]==ev["imageSha256"]
    assert m["visualReviewEvidence"]["reviewedSha256"]==ev["imageSha256"]
    assert sha(m["output"])==ev["imageSha256"]
    assert sha(q["assets"]["sourcePageWebp"])==q["assets"]["sourceSha256"]
    assert q["assets"]["sha256"]==ev["imageSha256"]
    assert q["questionProvenance"]["pdfSha256"]==ev["questionPdfSha256"]
    assert q["answerMatched"] is True and q["answer"]=="B"
    assert q["answerVerified"] is True and q["officialFinalAnswer"]=="B"
    assert q["officialCorrectionChecked"] is True
    assert q["paperCode"]=="00-MB" and q["originalQuestionNumber"]==5
    checked=ev["verifiedFromOriginalSingleQuestionImage"]
    assert len(checked["options"])==4 and all(checked["options"])
    origQ=ev["originalCandidateQuestion"]; origO=ev["originalCandidateOptions"]
    already=q["question"]==checked["question"] and q["options"]==checked["options"]
    if already:
        assert q.get("legacyUnverifiedQuestion")==origQ
        assert q.get("legacyUnverifiedOptions")==origO
        assert q["questionVerified"] is True
        assert q.get("textQaStatus")=="PASS"
    else:
        assert q["question"]==origQ and q["options"]==origO
        assert q["questionVerified"] is False
    dbfile=BASE/"question-bank.sqlite3"
    # The original JSON and SQLite must agree before any write.
    field=verify_db(dbfile,qs)
    ocr=read(BASE/"ocr-raw-candidates.json")
    o=next(x for x in ocr["items"] if x["questionId"]==QID)
    assert o["sourceWebp"]==ev["imagePath"]
    assert o["ocrRawText"] and o["engine"]
    inv=read(BASE/"inventory.json")
    val=read(BASE/"VALIDATION.json")
    status={"mode":"IDEMPOTENT" if already else "READY_TO_PATCH",
            "questionId":QID,"qaSourceImageSha256":ev["imageSha256"],
            "sourcePdfSha256":ev["questionPdfSha256"],
            "officialAnswerPreserved":"B","releaseApproved":False,
            "originalsPreserved":True,"questionCount":205}
    if not stage or already:
        if already:
            assert o.get("qaStatus")=="PASS_ORIGINAL_WEBP_TEXT_REVIEW"
            assert read(REPORT)["correctedText"]==checked
        return status
    # Add only text correction; do not infer any approval for teaching or UI.
    q["legacyUnverifiedQuestion"]=origQ
    q["legacyUnverifiedOptions"]=origO
    q["question"]=checked["question"]
    q["options"]=checked["options"]
    q["questionVerified"]=True
    q["textQaStatus"]="PASS"
    q["sourceTextCorrectionEvidence"]=REPORT.as_posix()
    q["reviewStatus"]="original_webp_text_reviewed_other_release_gates_pending"
    q["integrationReady"]=False
    q["studentReleaseApproved"]=False
    assert q["answer"]==q["officialFinalAnswer"]=="B" and q["answerVerified"] is True
    o["correctedText"]=checked["question"]
    o["correctedOptions"]=checked["options"]
    o["qaStatus"]="PASS_ORIGINAL_WEBP_TEXT_REVIEW"
    o["qaReviewer"]="GPT-6 AI, post-image visual inspection, not human"
    o["qaEvidencePath"]=REPORT.as_posix()
    o["legacyCorrectedTextBeforeReview"]=origQ
    inv["perSubject"]["數學B"]["questionVerified"]=sum(
        x.get("questionVerified") is True and x.get("subject") in ("數學B","數學 B")
        for x in qs
    )
    val["stats"]["數學B"]["questionVerified"]=inv["perSubject"]["數學B"]["questionVerified"]
    inv["ocrTextIndependentlyVerified"]=sum(x.get("questionVerified") is True for x in qs)
    inv["textQaPass"]=sum(x.get("textQaStatus")=="PASS" for x in qs)
    val["ocrTextVerified"]=inv["ocrTextIndependentlyVerified"]
    assert inv["ocrTextIndependentlyVerified"]>=1
    val["integrationReady"]=False
    report={"schemaVersion":1,"year":115,"questionId":QID,
      "reviewer":"GPT-6 AI original source-image text comparison; no human review claimed",
      "reviewedAt":"2026-10-24",
      "originalQuestionSourcePdfSha256":ev["questionPdfSha256"],
      "singleQuestionWebpSha256":ev["imageSha256"],
      "qaOriginalEvidence":EVIDENCE.as_posix(),
      "priorQuestion":origQ,"priorOptions":origO,
      "correctedText":checked,
      "diff":"".join(difflib.unified_diff(
        (origQ+"\n"+"\n".join(origO)).splitlines(True),
        (checked["question"]+"\n"+"\n".join(checked["options"])).splitlines(True),
        fromfile="uncorrected-PDF-text",tofile="source-WebP-verified")),
      "rawOCRRetained":True,"questionVerified":True,
      "answerVerifiedPreviously":True,"newAnswerApprovalAdded":False,
      "releaseApproved":False,"studentReleaseApproved":False,
      "database":"205_JSON_SQLITE_PAYLOADS_ROUNDTRIP_VERIFIED"}
    with sqlite3.connect(path(dbfile)) as db:
        before=db.execute("SELECT "+field+" FROM questions WHERE question_id=?",(QID,)).fetchone()
        assert before and json.loads(before[0])["question"]==origQ
        wire=canon(q)
        h=hashlib.sha256(wire.encode("utf8")).hexdigest()
        assert db.execute("UPDATE questions SET "+field+"=?,payload_sha256=? WHERE question_id=?",
                (wire,h,QID)).rowcount==1
        db.commit()
    for name,obj in (("questions.json",bank),("ocr-raw-candidates.json",ocr),
                     ("inventory.json",inv),("VALIDATION.json",val)):
        write(BASE/name,obj)
    write(REPORT,report)
    assert verify_db(dbfile,qs)==field
    assert len(read(BASE/"questions.json")["questions"])==205
    assert read(BASE/"questions.json")["questions"][next(i for i,x in enumerate(qs) if x["questionId"]==QID)]["question"]==checked["question"]
    status["mode"]="PATCHED_ONE_Q_AND_SQLITE"
    status["roundtripCount"]=205
    return status

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--stage",action="store_true")
    args=parser.parse_args()
    print(json.dumps(execute(stage=args.stage),ensure_ascii=False))
