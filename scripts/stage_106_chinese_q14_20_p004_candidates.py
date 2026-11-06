#!/usr/bin/env python3
"""Create candidate-only per-question WebPs for 106 Chinese Q14-Q20, and three shared sources.

Original TCTE printed paper page 4, SHA-pinned (source Git blob and official PDF
SHA). Q14-Q20 currently lack an individual WebP in manifest; preserve records.
Candidates remain PENDING_DIRECT_VISUAL_REVIEW until directly inspected and
related shared passages are also reviewed. This script touches NO validated
assets, flags, answers, OCR, SQLite, or UI.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/106")
SOURCE="sudu/data/original/106/00-C/p004-93b8ec6eb3-v2-w1400-q66.webp"
SOURCE_GIT_BLOB="b325a5fa1ec5073151077503de87929f3681130e"
PDF_SHA="93b8ec6eb319c8c7f5350ffa6267a2b4aed2f7acb1d1a2a7ca89e38f69ec5476"
PAGE=4
# Candidate crop bounds require direct source-to-output visual review.
CROPS={
 "106-00-C-14":[90,155,1310,426],
 "106-00-C-15":[90,560,1310,705],
 "106-00-C-16":[90,707,1310,821],
 "106-00-C-17":[90,1032,1310,1145],
 "106-00-C-18":[90,1144,1310,1344],
 "106-00-C-19":[90,1382,765,1565],
 "106-00-C-20":[90,1563,765,1762],
 "106-00-C-SHARED-15-16":[90,424,1310,558],
 "106-00-C-SHARED-17-18":[90,828,1310,1031],
 "106-00-C-SHARED-19-20":[765,1370,1310,1854]
}
LEDGER=BASE/"qa-drafts/DRAFT_106_CHINESE_Q14_20_SHARED_SOURCE_P004_20261023.json"

def safe(p):
    x=(ROOT/p).resolve()
    if not x.is_relative_to(ROOT):raise ValueError("Repository path traversal")
    return x

def sha(data):return hashlib.sha256(data).hexdigest()
def blobsha(data):return hashlib.sha1(("blob "+str(len(data))).encode("ascii")+bytes([0])+data).hexdigest()

def run(stage):
    actual=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    assert actual==BRANCH
    bank=json.loads(safe(BASE/"questions.json").read_text("utf8"))
    manifest=json.loads(safe(BASE/"webp-manifest.json").read_text("utf8"))
    byid={r["questionId"]:r for r in bank["questions"]}
    imap={r["questionId"]:r for r in manifest["items"]}
    assert len(byid)==len(imap)==204
    for i in range(14,21):
        qid=f"106-00-C-{i:02d}"
        assert qid in byid and qid in imap
        assert not imap[qid].get("output") and imap[qid].get("qaStatus")=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not byid[qid].get("answerVerified") and not byid[qid].get("integrationReady")
    data=safe(SOURCE).read_bytes()
    assert blobsha(data)==SOURCE_GIT_BLOB
    source_sha=sha(data)
    rows=[]
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        assert image.size[0]==1400 and 1950<=image.size[1]<=2000
        for qid,box in CROPS.items():
            assert 0<=box[0]<box[2]<=image.width and 0<=box[1]<box[3]<=image.height
            picture=image.crop(tuple(box))
            b=io.BytesIO()
            picture.save(b,format="WEBP",lossless=True,method=6,exact=True)
            content=b.getvalue();h=sha(content)
            is_shared="SHARED" in qid
            path=(BASE/"qa-drafts/webp-v2"/("shared" if is_shared else "00-C")/(qid+".webp")).as_posix()
            f=safe(path)
            if f.exists():
                assert sha(f.read_bytes())==h,"Existing immutable candidate differs: "+qid
            elif stage:
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(content)
            rows.append({"id":qid,"candidateType":"SHARED_PASSAGE_OR_GRAPHIC" if is_shared else "INDIVIDUAL_QUESTION",
                         "originalQuestionNumber":int(qid[-2:]) if not is_shared else None,
                         "sourcePage":PAGE,"sourcePageWebp":SOURCE,
                         "sourcePageSha256":source_sha,"officialPdfSha256Recorded":PDF_SHA,
                         "sourceCropPixels":box,"candidatePath":path,"candidateSha256":h,
                         "candidateSizePixels":list(picture.size),
                         "qaStatus":"PENDING_DIRECT_VISUAL_REVIEW",
                         "officialFinalAnswerVerified":False,
                         "integrationReady":False})
    out={"schemaVersion":1,"year":106,"paperCode":"00-C","sourceOfficialPdfSha256":PDF_SHA,
         "sourcePage":PAGE,"sourceImagePath":SOURCE,"sourceGitBlobSha":SOURCE_GIT_BLOB,
         "sourceImageSha256":source_sha,"questionCandidates":7,"sharedCandidates":3,
         "newImageQaPass":0,"newSharedQaPass":0,
         "reviewDate":"2026-10-23","imageQaStatus":"PENDING_DIRECT_VISUAL_REVIEW",
         "officialCorrectionChecked":False,"releaseAllowed":False,"integrationReady":False,
         "items":rows}
    encoded=(json.dumps(out,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    f=safe(LEDGER)
    if f.exists():assert f.read_bytes()==encoded
    elif stage:
        f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(encoded)
    print(json.dumps({"mode":"stage" if stage else "check","questionCandidates":7,
                      "sharedCandidates":3,"sourceImageSha256":source_sha,
                      "newImageQaPass":0,"integrationReady":False}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    args=p.parse_args()
    run(args.stage)
