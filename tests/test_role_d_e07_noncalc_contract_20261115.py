#!/usr/bin/env python3
"""ROLE D E07 NON-ADMISSION serializer/renderer contract precheck only."""
import copy
import hashlib
import json
import os
from pathlib import Path
from scripts import sudu_verified_publish as pub
from scripts import sudu_independent_review_gate as gate

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get("SUDU_D_E07_SOURCE",str(ROOT/"_e07_source")))
G5=Path(os.environ.get("SUDU_D_E07_ISSUER",str(ROOT/"_e07_g5")))
QID="114-00-E-07"
QREV="8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c"
WEBP="0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc"
DIGEST="d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf"
G5_BLOB="8ec2b0b87c916f6eb04d2852a6fab50ec04dd274"

def raw(path):
    return path.read_bytes()
def sha256(data):
    return hashlib.sha256(data).hexdigest()
def check(cond, reason):
    if not cond:
        raise AssertionError(reason)
def jsonfile(path):
    return json.loads(raw(path))

def run():
    issuer_path=G5/"sudu/data/processed/114/review-evidence/114-00-E-07-teaching-publisher-20261115.json"
    issuer_bytes=raw(issuer_path)
    import subprocess
    gitblob=subprocess.check_output(['git','hash-object',str(issuer_path)],text=True).strip()
    check(gitblob==G5_BLOB,"G5 actual byte Git Blob mismatch")
    issuer=json.loads(issuer_bytes)
    teach=issuer["content"]
    check(issuer["questionId"]==QID and issuer["questionRevision"]==QREV and issuer["webpSha256"]==WEBP,"G5 source pin mismatch")
    check(gate.digest(gate.canonical(teach))==DIGEST,"canonical teachingDigest mismatch")
    check(issuer["canonicalTeachingSha256"]==DIGEST,"issuer self-claimed digest mismatch")
    check(teach.get("hasExamCalculation") is False and teach.get("examCalculation") is None,"E07 must be true noncalculation")
    for letter in "ABCD":
        d=teach["optionExplanations"][letter]
        check(all(isinstance(d.get(k),str) and d[k].strip() for k in ("teacher","elementary","reason")),letter+" 2-level explanation missing")
    check(bool(teach.get("teacherSummary")) and bool(teach.get("elementarySummary")),"two teaching levels required")
    check(teach.get("highlights") and "automatically" in teach["highlights"],"real highlights missing")

    base=SOURCE/"sudu/data/processed/114"
    bank=jsonfile(base/"questions.json")
    items=bank["questions"]
    check(len(items)==205,"original 205 candidate bank changed")
    matches=[q for q in items if q.get("questionId")==QID]
    check(len(matches)==1,"E07 original question missing/duplicate")
    original=matches[0]
    manifest=jsonfile(base/"webp-manifest.json")
    asset=next(x for x in manifest["items"] if x["questionId"]==QID)
    check(asset["sha256"]==WEBP,"original manifest WebP digest changed")
    check(sha256(raw(SOURCE/asset["output"]))==WEBP,"original WebP binary changed")
    check(pub.text_revision(original,WEBP,SOURCE)==QREV,"sourceRevision changed")
    g2=jsonfile(base/"review-evidence/114-00-E-07-ocr-publisher-20261115.json")
    g3=jsonfile(base/"review-evidence/114-00-E-07-official-publisher-20261115.json")
    check(g2["question"]==original["question"] and g2["options"]==original["options"],"original whitespace/options changed")
    check(g3["finalAnswer"]=="A","actual G3 answer mismatch")
    check(len(original["options"])==4 and original["options"][0]=="automatically","official A-D mismatched")

    # ONLY in-memory serializer shape examination. Never writes an approved row or gate PASS.
    candidate=copy.deepcopy(original)
    candidate["teaching"]=teach
    candidate["officialFinalAnswer"]=g3["finalAnswer"]
    subject=pub.stable(candidate,114)[1]
    row=pub.public_question(candidate,114,subject,"data/approved/webp/114/"+QID+".webp")
    check(row["canonicalId"]==QID and row["answer"]=="A","native serializer identity/answer mismatch")
    check(row["question"]==original["question"] and row["options"]==original["options"],"native serializer changed source text")
    check(row["examCalculation"] is None,"noncalculation row leaked calculation card")
    check(row["optionExplanations"]==teach["optionExplanations"],"native four-option lesson mismatch")
    check(row["teacherSummary"]==teach["teacherSummary"] and row["elementarySummary"]==teach["elementarySummary"],"native two-level teaching mismatch")
    check(row["highlights"]==teach["highlights"],"native highlights mismatch")
    check(row["imageSha256"]==WEBP,"native original WebP digest mismatch")

    runtime=raw(ROOT/"sudu/verified-questions-runtime.js").decode()
    html=raw(ROOT/"sudu/v4-115-multisubject-review-demo.html").decode()
    check("calc&&calc.hasExamCalculation===true&&Array.isArray(calc.lines)&&calc.lines.length" in runtime,"runtime calc guard missing")
    check("renderOptionDetail=function(q,L)" in runtime and "['高職生理解',detail.teacher]" in runtime and "['國小學生也聽得懂',detail.elementary]" in runtime,"runtime option levels absent")
    check("function guideEntries(q)" in html and "x[0]==='考題計算式'" in html,"V4 calculation guide contract changed")

    # Negative: a future publisher accidentally turning noncalc into calc must fail.
    tampered=copy.deepcopy(candidate)
    tampered["teaching"]["hasExamCalculation"]=True
    check(tampered["teaching"]["examCalculation"] is None,"negative fixture setup unexpected")
    try:
        pub.public_question(tampered,114,subject,row["image"])
    except (TypeError, KeyError):
        pass
    else:
        raise AssertionError("tampered hasExamCalculation=true with null calculation unexpectedly serialized")

    print("PASS ROLE D E07 non-admission original source/G2/G3/G5/byte SHA/4 options/2 levels/noncalc serialization/guards/negative tamper")
    print("PRECHECK_ONLY; no Chromium, no formal G8, no owner E/G6/G7, no approved or LIVE write")
if __name__=="__main__":
    run()
