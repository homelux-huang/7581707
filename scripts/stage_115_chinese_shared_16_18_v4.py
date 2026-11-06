#!/usr/bin/env python3
"""Lossless source-page draft of 115 Chinese Q16-18 shared-reading passage.

The old shared WebP v3 cuts the bottom text too tightly. Source is immutable
official PDF page render with SHA. Never overwrite old image, never mark QA PASS.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/115")
ID="115-00-C-SHARED-16-18"
NEW="sudu/data/processed/115/qa-drafts/webp-v4/shared/115-00-C-SHARED-16-18.webp"
LEDGER="sudu/data/processed/115/qa-drafts/SHARED_115_C_16_18_V4_SOURCE_CROP_CANDIDATE_20261023.json"
SHA="8b6c781a75a864b7220f686532225171b2f53346c68f5131470371f82731e6c6"
OLD="708a7236cdf91753bb86f385603922090105ace1a9f792c13b40869fd3686d45"
BOX=[90,161,1310,1059]
PDF="6b454d65902f2fb326b1ac1ae28aa44749532e30369ba2c599db97d20a542135"

def f(path):
    p=(ROOT/path).resolve()
    if not p.is_relative_to(ROOT):raise ValueError("Unsafe QA path")
    return p

def digest(b):return hashlib.sha256(b).hexdigest()

def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    m=json.loads(f(BASE/"webp-manifest.json").read_text("utf8"))
    a=next(x for x in m["sharedMaterialCrops"] if x["sharedMaterialId"]==ID)
    assert a["output"]=="sudu/data/processed/115/webp-v3/shared/115-00-C-SHARED-16-18.webp"
    assert a["sha256"]==OLD
    assert a["sourceSha256"]==SHA and a["sourcePage"]==6
    assert a["crop"]==[90,161,1310,1049] and sorted(a["originalQuestionNumbers"])==[16,17,18]
    assert a["qaStatus"]!="PASS"
    src=f(a["source"]).read_bytes()
    assert digest(src)==SHA and digest(f(a["output"]).read_bytes())==OLD
    with Image.open(io.BytesIO(src)) as im:
        im.load();assert im.size==(1400,1981)
        crop=im.crop(tuple(BOX))
        out=io.BytesIO()
        crop.save(out,format="WEBP",lossless=True,method=6,exact=True)
        candidate=out.getvalue()
    h=digest(candidate)
    p=f(NEW)
    if p.exists():
        assert digest(p.read_bytes())==h
    elif stage:
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(candidate)
    rec={
        "schemaVersion":1,"year":115,"sharedMaterialId":ID,"sourcePage":6,
        "sourcePagePath":a["source"],"sourcePageSha256":SHA,
        "officialQuestionPdfSha256Recorded":PDF,
        "oldCrop":a["crop"],"oldOutputPath":a["output"],"oldSha256":OLD,
        "newOutputPath":NEW,"newSha256":h,"newCrop":BOX,
        "newSizePixels":[crop.width,crop.height],
        "purpose":"restore entire byline at bottom without including adjacent Q16",
        "qaStatus":"PENDING_DIRECT_VISUAL_REVIEW",
        "officialAnswerVerified":False,"integrationReady":False,
        "releaseAllowed":False
    }
    text=(json.dumps(rec,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    p=f(LEDGER)
    if p.exists():
        assert p.read_bytes()==text
    elif stage:
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text)
    print(json.dumps({"mode":"stage" if stage else "check",
                      "sourceSha256":SHA,"candidateSha256":h,
                      "newSharedMaterialQaPass":0,
                      "releaseAllowed":False},ensure_ascii=False))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    args=a.parse_args()
    run(args.stage)
