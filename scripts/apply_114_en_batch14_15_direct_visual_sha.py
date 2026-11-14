#!/usr/bin/env python3
"""Idempotently record 15 already-visually-reviewed 114 English question WebPs.

All source and output SHA256 values are bound to a direct visual evidence record.
Existing image bytes are never rewritten. This is image-only QA, NOT answer,
OCR, tutorial or release approval. QA branch only.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/114")
EVIDENCE=BASE/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
NAMES=[
    "questions.json","webp-manifest.json","VISUAL_QA.json",
    "inventory.json","VALIDATION.json","release-manifest.json"
]
QIDS={f"114-00-E-{n:02d}" for n in range(6,21)}

def file(p):
    result=(ROOT/p).resolve()
    if not result.is_relative_to(ROOT):raise RuntimeError("Unsafe path")
    return result

def get(p):return json.loads(file(p).read_text("utf-8"))
def digest(p):return hashlib.sha256(file(p).read_bytes()).hexdigest()
def grouped(data,key):
    result={x[key]:x for x in data}
    if len(result)!=len(data): raise RuntimeError("Duplicate ids in "+key)
    return result

def run(stage=False):
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if branch!=BRANCH:raise RuntimeError("Only QA branch is authorized")
    e=get(EVIDENCE)
    if (e["passedQuestionWebp"]!=15 or e["failedQuestionWebp"]!=0
            or len(e["items"])!=15 or not e["unchangedSourceAndCropSha"]
            or e["answerVerifiedAdded"] or e["questionVerifiedAdded"] or e["integrationReady"]):
        raise RuntimeError("Missing accepted prior visual QA evidence")
    records=grouped(e["items"],"questionId")
    if set(records)!=QIDS:raise RuntimeError("Unexpected English batch IDs")
    bank=get(BASE/"questions.json")
    manifest=get(BASE/"webp-manifest.json")
    visual=get(BASE/"VISUAL_QA.json")
    inv=get(BASE/"inventory.json")
    val=get(BASE/"VALIDATION.json")
    release=get(BASE/"release-manifest.json")
    qs=grouped(bank["questions"],"questionId")
    m=grouped(manifest["items"],"questionId")
    v=grouped(visual["questions"],"questionId")
    if len(qs)!=205 or len(m)!=205 or len(v)!=205:
        raise RuntimeError("Unexpected annual question count")
    if inv["webpVisualQaPassed"] not in (9,24) or manifest["visualQaPass"] not in (9,24):
        raise RuntimeError("Detected concurrent ledger changes; manual merge required")
    if val["imageVisualQaPass"] not in (9,24) or visual["passCount"] not in (9,24):
        raise RuntimeError("Unexpected QA ledger count")
    for qid in sorted(QIDS):
        r=records[qid];a=m[qid];z=v[qid];q=qs[qid]
        expected={"officialPdf":r["sourceOfficialPdfUrl"],
                  "sourcePdfSha256":r["sourceOfficialPdfSha256"],
                  "source":r["sourcePagePath"],"sourceSha256":r["sourcePageSha256"],
                  "sourcePage":r["sourcePage"],"crop":r["cropPixels"],
                  "output":r["reviewedWebpPath"],"sha256":r["reviewedWebpSha256"]}
        for key,value in expected.items():
            if a.get(key)!=value:raise RuntimeError("Official source/crop SHA mismatch for "+qid+" : "+key)
        if (z["asset"]!=r["reviewedWebpPath"] or z["assetSha256"]!=r["reviewedWebpSha256"]
            or z["sourceSha256"]!=r["sourcePageSha256"] or z["sourcePage"]!=r["sourcePage"]):
            raise RuntimeError("Current VISUAL_QA conflicts with reviewed image for "+qid)
        if a.get("qaStatus")=="PASS" and a.get("visualReviewEvidence",{}).get("reviewedSha256")!=r["reviewedWebpSha256"]:
            raise RuntimeError("Different previously passed SHA; do not overwrite "+qid)
        if not all(x is True for x in r["criteria"].values()) or r["result"]!="PASS":
            raise RuntimeError("Not directly visually approved: "+qid)
        if digest(r["sourcePagePath"])!=r["sourcePageSha256"] or digest(r["reviewedWebpPath"])!=r["reviewedWebpSha256"]:
            raise RuntimeError("Actual bytes SHA differs: "+qid)
        with Image.open(file(r["sourcePagePath"])) as src, Image.open(file(r["reviewedWebpPath"])) as crop:
            src.load();crop.load()
            reference=src.crop(tuple(r["cropPixels"]))
            if (src.format!="WEBP" or crop.format!="WEBP" or reference.size!=crop.size
                or ImageChops.difference(reference.convert("RGB"),crop.convert("RGB")).getbbox() is not None):
                raise RuntimeError("Actual original pixels and reviewed crop differ: "+qid)
        if q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady"):
            raise RuntimeError("Refusing to alter previously verified question: "+qid)
        a["qaStatus"]="PASS"
        a["visualReviewEvidence"]={
            "reference":str(EVIDENCE),
            "reviewedSha256":r["reviewedWebpSha256"],
            "sourcePageSha256":r["sourcePageSha256"],
            "qaReviewer":r["qaReviewer"],
            "reviewedAt":"2026-10-23",
            "method":"direct_official_page_to_single_question_WebP",
            "independentHumanReview":False
        }
        z.update({
            "result":"PASS","evidenceReference":str(EVIDENCE),
            "reviewer":r["qaReviewer"],"reviewedWebpSha256":r["reviewedWebpSha256"],
            "cropPixels":r["cropPixels"],"reviewedAt":"2026-10-23"
        })
        q["imageQaStatus"]="PASS"
        q.setdefault("assets",{})["imageQaEvidence"]=str(EVIDENCE)
    new_sum=sum(x.get("result")=="PASS" for x in visual["questions"])
    new_manifest=sum(x.get("qaStatus")=="PASS" for x in manifest["items"])
    if new_sum!=24 or new_manifest!=24:
        raise RuntimeError(f"Expected exactly 9 previous + 15 reviewed, found {new_sum}/{new_manifest}")
    visual["passCount"]=24
    manifest["visualQaPass"]=24
    inv["webpVisualQaPassed"]=24
    val["imageVisualQaPass"]=24
    release["imageQA"]="PARTIAL_24_OF_205"
    for x in [inv,val,release]:
        if x.get("integrationReady") is True or x.get("releaseAllowed") is True:
            raise RuntimeError("Unsafe release-ready flags")
        x["integrationReady"]=False
        if "releaseAllowed" in x:x["releaseAllowed"]=False
    if any(q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady") for q in bank["questions"]):
        raise RuntimeError("Unverified 114 question flags must stay false")
    for fn,obj in zip(NAMES,[bank,manifest,visual,inv,val,release]):
        out=(json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        target=file(BASE/fn)
        if stage and target.read_bytes()!=out:target.write_bytes(out)
    return {"state":"STAGED_IMAGE_ONLY" if stage else "CHECKED_IMAGE_ONLY",
            "newVisualWebpPass":15,"total114VisualWebpPass":24,
            "answerVerifiedAdded":0,"questionVerifiedAdded":0,
            "integrationReady":False,"existingWebpByteEdits":0}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--check",action="store_true")
    a.add_argument("--stage",action="store_true")
    z=p.parse_args()
    print(json.dumps(run(stage=z.stage),ensure_ascii=False))
