#!/usr/bin/env python3
"""G1 shared-material-only direct visual QA of 115 Chinese Q16-18 source.

Direct original-page-vs-v4-WebP reviewed by ChatGPT. New immutable v4 includes
complete source and byline, excluding neighboring Q16 stem. Does NOT promote
individual question images, text/OCR, final answers, or release.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import sqlite3
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/115")
EVID=BASE/"qa-drafts/DIRECT_VISUAL_SHARED_115_C_16_18_V4_20261023.json"
DRAFT=BASE/"qa-drafts/SHARED_115_C_16_18_V4_SOURCE_CROP_CANDIDATE_20261023.json"
SID="115-00-C-SHARED-16-18"
IDS={f"115-00-C-{i:02d}" for i in (16,17,18)}

def file(p):
    x=(ROOT/p).resolve()
    assert x.is_relative_to(ROOT)
    return x

def load(p):
    return json.loads(file(p).read_text("utf8"))

def sha(p):
    return hashlib.sha256(file(p).read_bytes()).hexdigest()

def write(p,obj):
    file(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def ix(items,key):
    d={x[key]:x for x in items}
    assert len(d)==len(items)
    return d

def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    r=load(EVID);d=load(DRAFT)
    assert r["sharedMaterialId"]==d["sharedMaterialId"]==SID
    assert set(r["questionIds"])==IDS
    assert r["sharedQaPassAdded"]==1 and not r["releaseAllowed"]
    assert r["result"]=="PASS_DIRECT_ORIGINAL_OFFICIAL_PAGE_SHARED_MATERIAL_VISUAL"
    assert all(x is True for x in r["criteria"].values())
    assert not r["answerVerifiedAdded"] and not r["questionVerifiedAdded"]
    assert not r["questionImageQaAdded"] and not r["integrationReady"]
    assert not r["independentHumanReview"]
    assert r["sourcePageWebpSha256"]==d["sourcePageSha256"]
    assert r["newWebpSha256"]==d["newSha256"] and r["oldWebpSha256"]==d["oldSha256"]
    assert r["newWebp"]==d["newOutputPath"]
    assert sha(r["sourcePageWebp"])==r["sourcePageWebpSha256"]
    assert sha(r["newWebp"])==r["newWebpSha256"]
    assert sha(r["oldWebp"])==r["oldWebpSha256"]
    with Image.open(file(r["sourcePageWebp"])) as source,Image.open(file(r["newWebp"])) as target:
        source.load();target.load()
        piece=source.crop(tuple(r["newCrop"]))
        assert target.size==piece.size
        assert ImageChops.difference(piece.convert("RGB"),target.convert("RGB")).getbbox() is None
    bank=load(BASE/"questions.json")
    manifest=load(BASE/"webp-manifest.json")
    inv=load(BASE/"inventory.json")
    validation=load(BASE/"VALIDATION.json")
    release=load(BASE/"release-manifest.json")
    visual=load(BASE/"VISUAL_QA.json")
    shared=ix(manifest["sharedMaterialCrops"],"sharedMaterialId")[SID]
    questions=ix(bank["questions"],"questionId")
    assert len(questions)==205 and len(manifest["items"])==205
    assert len(manifest["sharedMaterialCrops"])==20
    assert inv["imageVisualQaPass"]==143
    assert inv["officialAnswerIndependentVerified"] in (16,56)
    previous=sum(x.get("qaStatus")=="PASS" for x in manifest["sharedMaterialCrops"])
    assert previous in (4,5)
    already=shared.get("qaStatus")=="PASS"
    if already:
        assert shared["output"]==r["newWebp"]
        assert shared["sha256"]==r["newWebpSha256"]
        assert shared["visualReviewEvidence"]["reference"]==EVID.as_posix()
        for qid in IDS:
            assert questions[qid]["assets"]["sharedMaterialWebps"]==[r["newWebp"]]
        return {"mode":"IDEMPOTENT","sharedMaterialPass":previous,
                "questionImagePass":143,"releaseAllowed":False}
    assert previous==4
    assert shared["qaStatus"]!="PASS"
    assert shared["output"]==r["oldWebp"] and shared["sha256"]==r["oldWebpSha256"]
    assert shared["crop"]==r["oldCrop"]
    for qid in IDS:
        q=questions[qid]
        assert q["sharedMaterialId"]==SID
        assert q["assets"]["sharedMaterialWebps"]==[r["oldWebp"]]
        assert not q.get("questionVerified") and not q.get("integrationReady")
    if not stage:
        return {"mode":"CHECK","pendingShared":1,"existingSharedPass":previous,
                "releaseAllowed":False}
    shared["previousCropRecord"]={
        "output":shared["output"],"sha256":shared["sha256"],
        "crop":shared["crop"],"qaStatus":shared["qaStatus"],
        "issues":shared.get("issues",[])
    }
    shared["output"]=r["newWebp"]
    shared["sha256"]=r["newWebpSha256"]
    shared["crop"]=r["newCrop"]
    shared["outputSize"]=d["newSizePixels"]
    shared["processingVersion"]="source-pixel-v4-review-2026-10-23"
    shared["qaStatus"]="PASS"
    shared["issues"]=[]
    shared["visualReviewEvidence"]={
        "reference":EVID.as_posix(),
        "reviewedSha256":r["newWebpSha256"],
        "sourceSha256":r["sourcePageWebpSha256"],
        "reviewer":"ChatGPT assistant","reviewedAt":"2026-10-23",
        "method":"direct_original_page_vs_shared_paper_v4_WebP",
        "independentHumanReview":False,
        "text":"Reading text and byline complete; Q16 excluded"
    }
    for qid in IDS:
        q=questions[qid]
        q["assets"]["sharedMaterialWebps"]=[r["newWebp"]]
        q["assets"]["sharedMaterialQaEvidence"]=EVID.as_posix()
        q["integrationReady"]=False
    after=sum(x.get("qaStatus")=="PASS" for x in manifest["sharedMaterialCrops"])
    assert after==5
    inv["sharedMaterialVisualQaPassed"]=after
    validation["sharedMaterialVisualQaPassed"]=after
    release["sharedMaterialQA"]=f"PARTIAL_{after}_OF_20"
    release["releaseAllowed"]=False
    release["integrationReady"]=False
    inv["integrationReady"]=False
    validation["integrationReady"]=False
    assert visual["passCount"]==143
    index={x["sharedMaterialId"]:x for x in visual["sharedMaterials"]}
    assert SID in index
    index[SID]["qaStatus"]="PASS"
    index[SID]["reference"]=EVID.as_posix()
    index[SID]["sha256"]=r["newWebpSha256"]
    visual["sharedMaterialPassCount"]=after
    dbfile=file(BASE/"question-bank.sqlite3")
    with sqlite3.connect(dbfile) as db:
        cols={c[1] for c in db.execute("PRAGMA table_info(questions)")}
        assert {"question_id","payload_sha256"}<=cols
        field="payload" if "payload" in cols else "payload_json"
        assert field in cols
        tables={t[0] for t in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert not {"student_answers","student_results","student_progress"}.intersection(tables)
        for qid in sorted(IDS):
            wire=json.dumps(questions[qid],ensure_ascii=False,sort_keys=True,separators=(",",":"))
            assert db.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                              (wire,hashlib.sha256(wire.encode("utf8")).hexdigest(),qid)).rowcount==1
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        for qid,payload,digest in db.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
            assert hashlib.sha256(payload.encode("utf8")).hexdigest()==digest
            assert json.loads(payload)["questionId"]==qid
    for name,obj in (("questions.json",bank),("webp-manifest.json",manifest),
                     ("inventory.json",inv),("VALIDATION.json",validation),
                     ("release-manifest.json",release),("VISUAL_QA.json",visual)):
        write(BASE/name,obj)
    return {"mode":"STAGE","sharedMaterialPassAdded":1,"sharedMaterialPassTotal":after,
            "individualImagePassUnchanged":143,"answerVerifiedUnchanged":inv["officialAnswerIndependentVerified"],
            "releaseAllowed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    q=p.parse_args()
    print(json.dumps(run(stage=q.stage),ensure_ascii=False))
