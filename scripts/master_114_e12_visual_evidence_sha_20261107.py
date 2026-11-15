#!/usr/bin/env python3
"""Attach only actual historical E12 visual-record byte SHA; never grant READY."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QID="114-00-E-12"
BASE_SHA="1f27ddcd8edf746da49cbecc52e04779e44f016b"
MANIFEST_REL="sudu/data/processed/114/webp-manifest.json"
MANIFEST_ORIGINAL_GIT_BLOB="249a41d5a64558ccaa3084b21f915922a55c6a1b"
EVIDENCE_REL="sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
EVIDENCE_ORIGINAL_GIT_BLOB="c1154562fa30cb4b2720a6000a970cf09ef460ff"
WEBP_REL="sudu/data/processed/114/webp-v1/00-E/114-00-E-12.webp"
WEBP_SHA="99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
SOURCE_PAGE_SHA="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
CROP=[90,589,1310,872]

def check(condition,message):
    if not condition: raise RuntimeError("E12_VISUAL_HOLD: "+message)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def jcanon(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def main(apply=False):
    mp=ROOT/MANIFEST_REL
    qp=ROOT/EVIDENCE_REL
    wp=ROOT/WEBP_REL
    check(mp.is_file() and qp.is_file() and wp.is_file(),"missing source images or QA record")
    check(not mp.is_symlink() and not qp.is_symlink() and not wp.is_symlink(),
          "symlink cannot be trusted for source proof")
    mr=mp.read_bytes()
    qr=qp.read_bytes()
    wr=wp.read_bytes()
    check(blob(qr)==EVIDENCE_ORIGINAL_GIT_BLOB,"original QA Git Blob modified")
    check(wr[:4]==b"RIFF" and wr[8:12]==b"WEBP" and sha(wr)==WEBP_SHA,
          "original single WebP SHA/decoding header differs")
    obj=json.loads(mr)
    check(obj.get("year")==114 and len(obj.get("items",[]))==205,
          "year or 205 manifest count mismatched")
    ids=[x.get("questionId") for x in obj["items"]]
    check(len(set(ids))==205 and ids.count(QID)==1,"manifest QID not unique")
    idx=ids.index(QID)
    item=obj["items"][idx]
    old=[jcanon(x) for i,x in enumerate(obj["items"]) if i!=idx]
    proof=json.loads(qr)
    rows=[x for x in proof.get("items",[]) if x.get("questionId")==QID]
    check(len(rows)==1,"archived direct visual QA record absent or duplicated")
    row=rows[0]
    check(proof.get("year")==114 and row.get("result")=="PASS",
          "archived original visual QA not PASS")
    check(item.get("qaStatus")=="PASS" and item.get("output")==WEBP_REL
          and item.get("sha256")==WEBP_SHA and item.get("sourceSha256")==SOURCE_PAGE_SHA
          and item.get("crop")==CROP,"manifest incorrect source identity")
    ev=item.get("visualReviewEvidence") or {}
    check(ev.get("reference")==EVIDENCE_REL
          and ev.get("reviewedSha256")==WEBP_SHA
          and ev.get("sourcePageSha256")==SOURCE_PAGE_SHA,
          "manifest original visual evidence references differ")
    check(row.get("reviewedWebpPath")==WEBP_REL and row.get("reviewedWebpSha256")==WEBP_SHA
          and row.get("sourcePageSha256")==SOURCE_PAGE_SHA
          and row.get("cropPixels")==CROP,"old direct visual evidence does not match original crop")
    criteria=row.get("criteria") or {}
    check(all(criteria.get(key) is True for key in (
          "original_number","complete_stem","all_four_options","no_neighboring_question",
          "readable","source_and_output_sha256_matched","exact_source_crop_pixel_match")),
          "source visual quality criteria not all PASS")
    expected_sha=sha(qr)
    current=ev.get("referenceSha256")
    check(current in (None,expected_sha),"source manifest contains a stale reference SHA")
    if current is None:
        check(blob(mr)==MANIFEST_ORIGINAL_GIT_BLOB,
              "manifest no longer exact original before byte-SHA binding")
        if apply:
            after=copy.deepcopy(obj)
            after["items"][idx]["visualReviewEvidence"]["referenceSha256"]=expected_sha
            check([jcanon(x) for i,x in enumerate(after["items"]) if i!=idx]==old,
                  "some other 204 item changed")
            check(after.get("sharedMaterialCrops")==obj.get("sharedMaterialCrops"),
                  "some shared material changed")
            formatted=json.dumps(obj,ensure_ascii=False,indent=2)+"\n"
            check(formatted.encode("utf-8")==mr,"original manifest formatting changed")
            mp.write_text(json.dumps(after,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("E12 original visual-review SHA ADDED only; other 204 unchanged; NO RELEASE")
        else:
            print("G1 VERIFIED; E12 reference SHA missing; exact original byte SHA="+expected_sha)
    else:
        print("G1 VERIFIED; already bound exact E12 visual-document SHA="+expected_sha)
    return expected_sha

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    main(args.apply)
