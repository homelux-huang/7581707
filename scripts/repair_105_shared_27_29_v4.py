#!/usr/bin/env python3
"""Repair only 105 Chinese shared passage 27-29 with an immutable v4 crop.

v3 contains an adjacent Q27 illustration fragment. The v4 source crop
excludes it, preserves the complete reading passages, and is still a DRAFT
until direct visual review of the exact v4 SHA is recorded.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
QA_BRANCH="qa/114-115-official-visual-review"
PREFIX="sudu/data/processed/105/qa-drafts"
SOURCE="sudu/data/original/105/00-C/p006-0a170905cb-v2-w1400-q66.webp"
SOURCE_SHA="1f2ee292527089d4feeba24db0ce69996569d7df0db1f02078ac5771021a8694"
V3=PREFIX+"/webp-v3/shared/105-00-C-SHARED-27-29.webp"
V3_SHA="7f5dfdd7d34b20136cc0943d92639575aeb24dc49cae78b6e64d1926e78a5566"
V4=PREFIX+"/webp-v4/shared/105-00-C-SHARED-27-29.webp"
REPORT=PREFIX+"/UNVERIFIED_105_SHARED_27_29_V4_20261023.json"
FAIL=PREFIX+"/DIRECT_VISUAL_QA_105_7Q_2SHARED_20261023.json"
CROP=(90,1050,1310,1608)

def digest(b):
    return hashlib.sha256(b).hexdigest()

def path(p):
    resolved=(ROOT/p).resolve()
    if not resolved.is_relative_to(ROOT):
        raise RuntimeError("Unsafe output path")
    return resolved

def execute(stage=False,validate=False):
    assert CROP==(90,1050,1310,1608)
    if validate: return {"specValid":True,"newSharedDrafts":1,"imageQaPassAdded":0}
    current=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if current!=QA_BRANCH: raise RuntimeError("QA branch only")
    evidence=json.loads(path(FAIL).read_text("utf-8"))
    failed=[x for x in evidence["records"] if x["assetId"]=="105-00-C-SHARED-27-29"]
    if len(failed)!=1 or not failed[0]["imageQaStatus"].startswith("FAIL_"):
        raise RuntimeError("Cannot repair without the original visual FAIL record")
    original=path(SOURCE).read_bytes()
    old=path(V3).read_bytes()
    if digest(original)!=SOURCE_SHA or digest(old)!=V3_SHA:
        raise RuntimeError("Pinned source/v3 SHA mismatch: do not overwrite")
    with Image.open(io.BytesIO(original)) as im:
        im.load()
        if im.format!="WEBP" or im.size!=(1400,1980):
            raise RuntimeError("Unexpected original source page dimensions")
        output=io.BytesIO()
        im.crop(CROP).save(output,format="WEBP",lossless=True,method=6)
        data=output.getvalue()
    with Image.open(io.BytesIO(data)) as check:
        check.load()
        if check.size!=(1220,558): raise RuntimeError("Invalid v4 output dimensions")
    target=path(V4)
    if target.exists() and digest(target.read_bytes())!=digest(data):
        raise RuntimeError("Refusing to overwrite a different existing v4")
    ledger={
        "year":105,"assetId":"105-00-C-SHARED-27-29",
        "questionIds":["105-00-C-27","105-00-C-28","105-00-C-29"],
        "previousVisualFailure":"FAIL_ADJACENT_QUESTION_GRAPHIC",
        "sourcePage":6,"sourcePageWebp":SOURCE,"sourcePageWebpSha256":SOURCE_SHA,
        "oldV3Webp":V3,"oldV3WebpSha256":V3_SHA,
        "v4CropPixels":list(CROP),"v4CandidateWebp":V4,"v4CandidateSha256":digest(data),
        "imageQaStatus":"DRAFT_PENDING_DIRECT_ORIGINAL_V4_VISUAL_QA",
        "imageQaPassAdded":0,"answerVerified":False,"questionVerified":False,
        "integrationReady":False,
        "note":"v4 candidate must be compared directly with original source image. No automated QA PASS."
    }
    raw=(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    report=path(REPORT)
    if report.exists() and report.read_bytes()!=raw:
        raise RuntimeError("Inconsistent existing v4 ledger")
    if stage:
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(data)
        if not report.exists():report.write_bytes(raw)
    return {"stage":stage,"v4CandidateSha256":digest(data),"imageQaPassAdded":0,"answerVerified":False,"oldAssetsChanged":0}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    g.add_argument("--validate-spec",action="store_true")
    a=p.parse_args()
    print(json.dumps(execute(stage=a.stage,validate=a.validate_spec),ensure_ascii=False))
