#!/usr/bin/env python3
"""Fill only absent 115 raw OCR entries from current SHA-pinned per-question WebPs.

Never overwrite existing raw OCR or corrections; never mark textual QA as PASS.
Run after source-pixel crop refinement, before merging and SQLite rebuilding.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from PIL import Image
import pytesseract

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"sudu/data/processed/115"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    path=OUT/"ocr-raw-candidates.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    manifest=json.loads((OUT/"webp-manifest.json").read_text(encoding="utf-8"))
    existing={row["questionId"] for row in data["items"]}
    if len(existing)!=len(data["items"]) or data.get("count")!=len(existing):
        raise ValueError("Duplicate/inconsistent original OCR evidence; refuse modification")
    if len(manifest["items"])!=205:
        raise ValueError("Expected 205 single-question assets")
    created=[]
    for item in manifest["items"]:
        qid=item["questionId"]
        if qid in existing:
            continue
        if item.get("qaStatus")=="BLOCKED" or not item.get("output"):
            raise ValueError("OCR source unavailable: "+qid)
        source=ROOT/item["output"]
        official=ROOT/item["source"]
        if not source.is_file() or sha(source)!=item["sha256"]:
            raise ValueError("Single-question OCR WebP SHA mismatch: "+qid)
        if not official.is_file() or sha(official)!=item["sourceSha256"]:
            raise ValueError("Official source SHA mismatch: "+qid)
        with Image.open(io.BytesIO(source.read_bytes())) as image:
            image.load()
            if image.format!="WEBP" or list(image.size)!=item["outputSize"]:
                raise ValueError("Unreadable OCR source: "+qid)
            raw=pytesseract.image_to_string(image,lang="chi_tra+eng",config="--psm 6")
        created.append({
            "questionId":qid,
            "engine":"Tesseract chi_tra+eng PSM6 (uncorrected candidate)",
            "ocrRawText":raw,
            "ocrDate":datetime.now(timezone.utc).isoformat(),
            "sourceWebp":item["output"],
            "sourceSha256":item["sha256"],
            "correctedText":None,
            "qaStatus":"NOT_VISUALLY_VERIFIED",
            "notes":"Gap-fill only; raw OCR may be empty or inaccurate. Existing native/manual text is authoritative until individually verified."
        })
    if len(created)!=205-len(existing):
        raise ValueError("OCR coverage check failed")
    data["items"].extend(created)
    data["count"]=len(data["items"])
    data["missingRawOcrQuestionIds"]=[]
    data["gapFill"]={"added":len(created),"questionIds":[x["questionId"] for x in created],
                     "method":"SHA-pinned current per-question WebP only",
                     "existingRawOcrPreserved":len(existing),
                     "independentTextVerification":False}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"originalPreserved":len(existing),"added":len(created),
                      "total":data["count"],"questionIds":[x["questionId"] for x in created]},ensure_ascii=False))

if __name__=="__main__":
    main()
