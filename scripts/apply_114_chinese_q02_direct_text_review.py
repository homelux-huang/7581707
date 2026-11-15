#!/usr/bin/env python3
"""Apply one original-image-reviewed 114 Chinese Q02 text correction to isolated QA data.

The right explanatory box was interleaved into A-D by PDF text extraction.
Keep the old text, correct from the original page/WebP, and round-trip SQLite.
Do not modify image PASS count, official answers, releases, or student records.
"""
import argparse
import difflib
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/114")
EVIDENCE=BASE/"qa-drafts/OCR_114_00_C_02_DIRECT_REVIEW_20261023.json"
QID="114-00-C-02"
BRANCH="qa/114-115-official-visual-review"

def full(path):
    p=(ROOT/path).resolve()
    assert p.is_relative_to(ROOT)
    return p

def load(path):
    return json.loads(full(path).read_text(encoding="utf8"))

def sha(path):
    return hashlib.sha256(full(path).read_bytes()).hexdigest()

def serialized(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2)+"\n"

def run(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    r=load(EVIDENCE)
    assert r["questionId"]==QID and not r["answerVerified"] and not r["integrationReady"]
    assert r["textReview"]=="DIRECT_VISUAL_CORRECTION_EVIDENCED"
    assert len(r["correctedOptions"])==4 and all(r["correctedOptions"])
    assert sha(r["sourcePageWebp"])==r["sourcePageWebpSha256"]
    assert sha(r["reviewedWebpPath"])==r["reviewedWebpSha256"]
    m=next(x for x in load(BASE/"webp-manifest.json")["items"] if x["questionId"]==QID)
    assert m["qaStatus"]=="PASS"
    assert m["visualReviewEvidence"]["reviewedSha256"]==r["reviewedWebpSha256"]
    assert m["sourceSha256"]==r["sourcePageWebpSha256"]
    b=load(BASE/"questions.json")
    q=next(x for x in b["questions"] if x["questionId"]==QID)
    assert len(b["questions"])==205
    assert q["questionProvenance"]["webpSha256"]==r["reviewedWebpSha256"]
    assert q["imageQaStatus"]=="PASS" and not q["answerVerified"] and not q["integrationReady"]
    assert q["answer"]=="C"
    o=load(BASE/"ocr-raw-candidates.json")
    inv=load(BASE/"inventory.json")
    val=load(BASE/"VALIDATION.json")
    box="\n".join(x["label"]+"："+x["text"] for x in r["stemSupplementalBox"])
    corrected=r["correctedQuestion"]+"\n【右框】\n"+box
    already=q.get("textQaEvidence")==EVIDENCE.as_posix()
    if already:
        assert q["questionVerified"] and q["question"]==corrected
        assert q["options"]==r["correctedOptions"]
        assert sum(x["questionId"]==QID for x in o["items"])==1
        assert inv.get("ocrTextIndependentlyVerified")==1
        return {"mode":"already-applied","textVerified":1,"imageAdded":0,"answerAdded":0}
    assert not q["questionVerified"]
    assert q["question"]==r["originalLegacyQuestion"]
    assert q["options"]==r["originalLegacyOptions"]
    assert not any(x["questionId"]==QID for x in o["items"])
    if not stage:
        return {"mode":"check","pending":1,"imageAdded":0,"answerAdded":0}
    q["legacyUnverifiedQuestion"]=q["question"]
    q["legacyUnverifiedOptions"]=q["options"]
    q["question"]=corrected
    q["questionStemOnly"]=r["correctedQuestion"]
    q["stemSupplementalBox"]=r["stemSupplementalBox"]
    q["options"]=r["correctedOptions"]
    q["textQaEvidence"]=EVIDENCE.as_posix()
    q["textQaStatus"]="PASS_DIRECT_ORIGINAL_IMAGE"
    q["ocrSource"]="legacy_native_pdf_text_cross_column_contamination"
    q["questionVerified"]=True
    q["reviewStatus"]="text_reviewed_image_pass_answer_pending"
    q["answerVerified"]=q["integrationReady"]=False
    old=r["originalLegacyQuestion"]+"\n"+"\n".join(r["originalLegacyOptions"])
    new=corrected+"\n"+"\n".join(r["correctedOptions"])
    diff="".join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
                                     fromfile="legacy_native_pdf_text",
                                     tofile="direct_original_image_corrected"))
    o["items"].append({
       "questionId":QID, "engine":"legacy native PDF text (not OCR engine)",
       "rawText":old, "rawOrigin":"existing questions.json before correction",
       "correctedText":corrected, "correctedOptions":r["correctedOptions"],
       "difference":diff, "imageSha256":r["reviewedWebpSha256"],
       "reviewStatus":"PASS_DIRECT_ORIGINAL_IMAGE",
       "qaReviewer":"ChatGPT assistant", "qaReviewedAt":"2026-10-23",
       "qaEvidencePath":EVIDENCE.as_posix(),
       "answerVerified":False, "integrationReady":False
    })
    inv["ocrTextIndependentlyVerified"]=1
    inv["textQaPass"]=1
    val["ocrTextVerified"]=1
    val["releaseAllowed"]=val["integrationReady"]=False
    with sqlite3.connect(full(BASE/"question-bank.sqlite3")) as db:
        cols={c[1] for c in db.execute("PRAGMA table_info(questions)")}
        assert {"question_id","payload_sha256"}<=cols
        field="payload" if "payload" in cols else "payload_json"
        assert field in cols
        student_tables={"student_answers","student_results","student_progress"}
        assert not student_tables.intersection({x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")})
        oldrow=db.execute(f"SELECT {field} FROM questions WHERE question_id=?",(QID,)).fetchone()
        assert oldrow is not None
        previous=json.loads(oldrow[0])
        assert previous["questionId"]==QID and previous["options"]==r["originalLegacyOptions"]
        wire=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        digest=hashlib.sha256(wire.encode("utf8")).hexdigest()
        assert db.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                          (wire,digest,QID)).rowcount==1
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        for question_id,payload,payload_sha in db.execute(
                f"SELECT question_id,{field},payload_sha256 FROM questions"):
            assert hashlib.sha256(payload.encode("utf8")).hexdigest()==payload_sha
            assert json.loads(payload)["questionId"]==question_id
    for fn,obj in (("questions.json",b),("ocr-raw-candidates.json",o),
                   ("inventory.json",inv),("VALIDATION.json",val)):
        full(BASE/fn).write_text(serialized(obj),encoding="utf8")
    assert sum(x["questionVerified"] is True for x in b["questions"])==1
    assert not any(x.get("answerVerified") or x.get("integrationReady") for x in b["questions"])
    return {"mode":"stage","textVerifiedAdded":1,"imageAdded":0,
            "answerAdded":0,"releaseAllowed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--check",action="store_true")
    m.add_argument("--stage",action="store_true")
    args=p.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
