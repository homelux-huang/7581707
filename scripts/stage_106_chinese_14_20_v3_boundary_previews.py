#!/usr/bin/env python3
"""Versioned 106 Chinese Q14-20 + shared 17-18 boundary remediation candidates.
Works only with original official page 4 SHA and byte-exact lossless crops.
This step deliberately stages no G1/G2/G3 PASS and does not touch SQLite or release.
Candidates require fresh visual inspection before any manifest/database promotion.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
YEAR_DIR="sudu/data/processed/106/"
SOURCE="sudu/data/original/106/00-C/p004-93b8ec6eb3-v2-w1400-q66.webp"
SOURCE_SHA="b7e6a32272b74c7788caa1f413919b46359589162096f72afe1050c56a4e8bc4"
SOURCE_BLOB="b325a5fa1ec5073151077503de87929f3681130e"
ID_BOUNDS={
  "106-00-C-14":[90,155,1310,421],
  "106-00-C-15":[90,560,1310,701],
  "106-00-C-16":[90,703,1310,816],
  "106-00-C-17":[90,1006,1310,1115],
  "106-00-C-18":[90,1117,1310,1321],
  "106-00-C-19":[90,1345,765,1524],
  "106-00-C-20":[90,1526,765,1762],
  "106-00-C-SHARED-17-18":[90,827,1310,1004]
}
ISSUES={
 "106-00-C-14":"Old Q14 and 15-16 shared material overlapped by 2 pixels",
 "106-00-C-15":"Old Q15 crop included Q16 leading pixels",
 "106-00-C-16":"Old Q16 crop included following Q17-18 reading prompt",
 "106-00-C-17":"Old crop lost Q17 number/stem and included Q18 heading",
 "106-00-C-18":"Old crop lost Q18 leading stem and included Q19-20 shared prompt",
 "106-00-C-19":"Old crop lost Q19 number/leading stem and included Q20 leading text",
 "106-00-C-20":"Old crop lost Q20 number/leading stem; left-half text separately linked to shark shared panel",
 "106-00-C-SHARED-17-18":"Old shared reading passage included Q17 question stem"
}
EVIDENCE=YEAR_DIR+"qa-drafts/DRAFT_106_C14_20_V3_BOUNDARY_PREVIEWS_20261024.json"
def at(path):
    out=(ROOT/path).resolve()
    assert out.is_relative_to(ROOT.resolve()) and not out.is_symlink()
    return out
def sha(data):
    return hashlib.sha256(data).hexdigest()
def read(path):
    return json.loads(at(path).read_text(encoding="utf8"))
def outpath(qid):
    folder="shared" if "SHARED" in qid else "00-C"
    return YEAR_DIR+f"qa-drafts/webp-v3/{folder}/{qid}.webp"
def main(stage):
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    assert branch=="qa/114-115-official-visual-review",branch
    old=read(YEAR_DIR+"webp-manifest.json")
    q=read(YEAR_DIR+"questions.json")
    v=read(YEAR_DIR+"VISUAL_QA.json")
    rel=read(YEAR_DIR+"release-manifest.json")
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert len(old["items"])==len(q["questions"])==len(v["items"])==204
    assert v["passCount"]==16
    rows={x["questionId"]:x for x in old["items"]}
    shared={x["sharedMaterialId"]:x for x in old["sharedMaterialCrops"]}
    source_bytes=at(SOURCE).read_bytes()
    assert sha(source_bytes)==SOURCE_SHA
    blob=hashlib.sha1(b"blob "+str(len(source_bytes)).encode()+b"\x00"+source_bytes).hexdigest()
    assert blob==SOURCE_BLOB
    reviews=[]
    with Image.open(io.BytesIO(source_bytes)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for qid,box in ID_BOUNDS.items():
            obj=shared[qid] if "SHARED" in qid else rows[qid]
            assert obj["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
            assert obj["source"]==SOURCE and obj["sourcePageWebpSha256"]==SOURCE_SHA
            oldpath=at(obj["output"])
            assert sha(oldpath.read_bytes())==obj["outputSha256"],qid
            assert obj["cropPixels"]!=box
            assert 0<=box[0]<box[2]<=page.width and 0<=box[1]<box[3]<=page.height
            segment=page.crop(tuple(box))
            buf=io.BytesIO()
            segment.save(buf,format="WEBP",lossless=True,method=6,exact=True)
            newbytes=buf.getvalue()
            with Image.open(io.BytesIO(newbytes)) as reread:
                reread.load()
                assert reread.format=="WEBP" and reread.size==segment.size
                assert ImageChops.difference(segment.convert("RGB"),reread.convert("RGB")).getbbox() is None
            target=at(outpath(qid))
            if target.is_file():
                assert sha(target.read_bytes())==sha(newbytes),"Never overwrite changed v3 asset"
            elif stage:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(newbytes)
            reviews.append({
                "questionIdOrSharedId":qid,"oldPath":obj["output"],
                "oldSha256":obj["outputSha256"],"oldPixels":obj["cropPixels"],
                "newPath":outpath(qid),"newSha256":sha(newbytes),
                "newPixels":box,"size":[segment.width,segment.height],
                "sourcePageWebp":SOURCE,"sourcePageSha256":SOURCE_SHA,
                "sourcePageBlob":SOURCE_BLOB,"sourcePage":4,
                "defectFound":ISSUES[qid],"qaStatus":"DRAFT_PENDING_DIRECT_VISUAL_QA"
            })
    result={
        "schemaVersion":1,"year":106,"paperCode":"00-C",
        "sourcePage":4,"sourceOriginalWebp":SOURCE,"sourceSha256":SOURCE_SHA,
        "sourceGitBlob":SOURCE_BLOB,
        "reviewer":"ChatGPT assistant","independentHumanReview":False,
        "method":"SHA-pinned original pixel crops only, await actual individual visual review",
        "candidateCount":7,"changedSharedCount":1,"untouchedSharedIds":[
             "106-00-C-SHARED-15-16","106-00-C-SHARED-19-20"],
        "newG1Pass":0,"newG2Pass":0,"newFinalAnswerVerified":0,
        "releaseAllowed":False,"integrationReady":False,
        "items":reviews,
    }
    if stage:
        at(EVIDENCE).parent.mkdir(parents=True,exist_ok=True)
        at(EVIDENCE).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"mode":"STAGED_PREVIEW" if stage else "PREFLIGHT",
        "candidates":7,"sharedRecrops":1,"sourcePixelVerified":True,
        "newG1":0,"newG2":0,"noRelease":True},ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    main(p.parse_args().stage)
