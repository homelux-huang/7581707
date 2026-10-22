#!/usr/bin/env python3
"""Apply strict 115-only, SHA-locked direct visual QA evidence.

This never invents a visual review and never promotes grading answer evidence.
Historical failures stay in the review JSON. Exact-image matching is mandatory.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"sudu/data/processed/115"
QAS=[OUT/"VISUAL_QA_2026-10-22.json", OUT/"VISUAL_QA_2026-10-22_B2.json"]
MANIFEST=OUT/"webp-manifest.json"


def digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    reviewed_batches=[]
    for path in QAS:
        raw=path.read_bytes()
        reviewed_batches.append((json.loads(raw),path.relative_to(ROOT).as_posix(),
                                 hashlib.sha256(raw).hexdigest()))
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["year"]!=115 or data["expected"]!=205:
        raise ValueError("Only 115 expected 205 entries")
    good={}
    # Corrections are append-only provenance: first failure may be followed
    # by a separately reviewed, exact-hash v5 replacement.
    for reviews,reference,refsha in reviewed_batches:
        for item in reviews["questions"]+reviews.get("repairRechecks",[]):
            if item["result"]!="PASS_ASSISTANT_VISUAL_QA":
                continue
            if not item.get("reviewer") and not item.get("secondHumanReview"):
                raise ValueError("Missing reviewer")
            if item["questionId"] in good and item["questionId"] not in {
                    "115-00-MB-13","115-00-MB-20"}:
                raise ValueError("Duplicate visual review: "+item["questionId"])
            good[item["questionId"]]=(item,reference,refsha)
    if len(good)!=113:
        raise ValueError(f"Unexpected number of visual reviews {len(good)} != 113")
    seen=set()
    promoted=0
    historical=0
    for item in data["items"]:
        qid=item["questionId"]
        if qid in seen:
            raise ValueError("Duplicate question ID "+qid)
        seen.add(qid)
        review_record=good.get(qid)
        if review_record is None:
            continue
        review,reference,refsha=review_record
        if item["sha256"]!=review["assetSha256"] or item["output"]!=review["asset"]:
            raise ValueError("Image SHA/path changed since visual review: "+qid)
        if item["source"]!=review["source"] or item["sourcePage"]!=review["sourcePage"]:
            raise ValueError("Source page changed since visual review: "+qid)
        actual=ROOT/item["output"]
        if digest(actual)!=review["assetSha256"]:
            raise ValueError("Reviewed WebP bytes missing or modified: "+qid)
        if item.get("qaStatus")=="PASS" and item.get("visualReviewEvidence",{}).get(
                "reference")=="sudu/DEMO_VISUAL_QA.md":
            # Don't replace the existing 2026-10-21 hash-backed review.
            # Store current cross-check as additional evidence.
            historical+=1
            item["secondVisualComparison"]={
                "reference":reference,"referenceSha256":refsha,
                "reviewedSha256":item["sha256"],"reviewedAt":"2026-10-22",
                "reviewer":"ChatGPT assistant","independentHumanReview":False,
            }
            continue
        item["qaStatus"]="PASS"
        item["visualReviewEvidence"]={
            "reviewedAt":"2026-10-22",
            "reviewMethod":"assistant_visual_comparison_of_official_source_page_and_single_question_crop",
            "reference":reference,
            "referenceSha256":refsha,
            "reviewedSha256":item["sha256"],
            "reviewer":"ChatGPT assistant",
            "independentHumanReview":False,
            "criteria":"official question number, full stem, 4 original options including figure choices, no adjacent question text, no page header/footer"
        }
        promoted+=1
    if seen != {x["questionId"] for x in data["items"]}:
        raise ValueError("Manifest question loss")
    sharedreviews={x["sharedMaterialId"]:(x,reference,refsha)
                   for reviews,reference,refsha in reviewed_batches
                   for x in reviews.get("sharedMaterials",[])}
    accepted=0
    for asset in data["sharedMaterialCrops"]:
        shared_record=sharedreviews.get(asset["sharedMaterialId"])
        if not shared_record:
            continue
        s,reference,refsha=shared_record
        if (s["result"]!="PASS_ASSISTANT_VISUAL_QA" or s["output"]!=asset["output"]
                or s["sha256"]!=asset["sha256"] or s["source"]!=asset["source"]
                or digest(ROOT/asset["output"])!=s["sha256"]):
            raise ValueError("Shared source/WebP image review mismatch: "+asset["sharedMaterialId"])
        asset["qaStatus"]="PASS"
        asset["visualReviewEvidence"]={
            "reference":reference,"referenceSha256":refsha,
            "reviewedSha256":asset["sha256"],"reviewedAt":"2026-10-22",
            "reviewer":"ChatGPT assistant","independentHumanReview":False,
            "criteria":"complete shared passage/chart, no neighboring numbered question stems/options"
        }
        accepted+=1
    if promoted+historical!=113 or accepted!=3:
        raise ValueError("QA record count mismatch")
    data["qaDirectVisualComparison"]={
        "reviewed":len(good),"reusedHistoricalOfThose":historical,
        "newlyPromoted":promoted,"sharedVerified":accepted,
        "references":[{"path":ref,"sha256":digest(ROOT/ref)} for _,ref,_ in reviewed_batches],
        "independentHumanReview":False,
        "note":"Assistant direct visual page-to-crop review, not independent external human review; grading flags remain false.",
    }
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"reviewed":len(good),"oldPassCrossChecked":historical,
                      "newlyPromoted":promoted,"totalPass":sum(x["qaStatus"]=="PASS" for x in data["items"]),
                      "sharedPass":accepted},ensure_ascii=False))

if __name__=="__main__":
    main()
