#!/usr/bin/env python3
"""115-only non-destructive asset and native-PDF-text evidence attachment.

Consume generated source-pixel draft WebPs, independently pinned official
PDF sources, and raw OCR results. Do not promote any review/answer flags.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse,urljoin
import fitz
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/data/processed/115"
QUESTIONS=DIR/"questions.json"
ORIGINAL=ROOT/"sudu/data/years/115.json"
ALLOWED={"web1.tcte.edu.tw","www.tcte.edu.tw","tcte.edu.tw"}

def read(name):
    return json.loads((DIR/name).read_text(encoding="utf-8"))
def write(name,data):
    (DIR/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def hashfile(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def pin_download(url,expected):
    for _ in range(5):
        p=urlparse(url)
        if p.scheme!="https" or p.hostname not in ALLOWED:
            raise ValueError("Official HTTPS source only: "+url)
        r=requests.get(url,headers={"User-Agent":"7581707-115-shared-material-geo/1.0"},
                       timeout=(20,80),allow_redirects=False)
        if r.is_redirect:
            url=urljoin(url,r.headers["Location"])
            continue
        r.raise_for_status()
        if not r.content.startswith(b"%PDF") or hashlib.sha256(r.content).hexdigest()!=expected:
            raise ValueError("Official PDF source changed or is invalid: "+url)
        return r.content
    raise ValueError("too many redirects")
def main():
    src=read("questions.json")
    original=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    manifest=read("webp-manifest.json")
    evidence=read("ocr-raw-candidates.json")
    ocr={q["questionId"]:q for q in evidence.get("items",[])}
    byid={q["questionId"]:q for q in src["questions"]}
    if len(byid)!=205 or len(manifest["items"])!=205 or manifest["generated"]!=205:
        raise ValueError("Full 205 canonical set not available; no partial overwrite")
    if len({x["questionId"] for x in manifest["items"]})!=205:
        raise ValueError("Duplicate canonical IDs in image manifest")
    timestamp=datetime.now(timezone.utc).isoformat()
    unmatched=[]
    for asset in manifest["items"]:
        q=byid[asset["questionId"]]
        assert q["paperCode"]==asset["paperCode"]
        assert q["originalQuestionNumber"]==asset["originalQuestionNumber"]
        path=ROOT/asset["output"]
        if not path.is_file() or hashfile(path)!=asset["sha256"]:
            raise ValueError("Missing/bad crop: "+asset["questionId"])
        source=ROOT/asset["source"]
        if not source.is_file() or hashfile(source)!=asset["sourceSha256"]:
            raise ValueError("Missing/bad official original: "+asset["questionId"])
        with Image.open(path) as im:
            im.load()
            if im.format!="WEBP" or list(im.size)!=asset["outputSize"]:
                raise ValueError("WebP decode failed: "+asset["questionId"])
        # Never replace user's historic question/teaching answer or attempts.
        before_assets=copy.deepcopy(q.get("assets",{}))
        q["assets"]={
          **before_assets,
          "singleQuestionWebp":asset["output"],
          "sourcePageWebp":asset["source"],"sourcePage":asset["sourcePage"],
          "sourceSize":asset["sourceSize"],"sourceSha256":asset["sourceSha256"],
          "cropCoordinates":asset["crop"],"outputSize":asset["outputSize"],
          "sha256":asset["sha256"],"processingVersion":asset["processingVersion"],
          "cropMethod":asset["cropMethod"],
          "visualQa":"PENDING_INDIVIDUAL_VISUAL_QA"
        }
        q["questionProvenance"]["originalPageWebp"]=asset["source"]
        q["questionProvenance"]["sourcePage"]=asset["sourcePage"]
        o=ocr.get(q["questionId"])
        if o:
            q["extraction"]["ocrRaw"]=o["ocrRawText"]
            q["extraction"]["ocrEngine"]="tesseract"
            q["extraction"]["ocrEngineVersion"]="runner_build_115_full_assets.py_psm6"
            q["extraction"]["ocrLanguages"]=["chi_tra","eng"]
            q["extraction"]["ocrDate"]=o["ocrDate"]
            q["extraction"]["ocrPerformed"]=True
            q["extraction"]["ocrReviewStatus"]="PENDING_INDIVIDUAL_VISUAL_QA"
        for issue in asset.get("issues",[]):
            if issue not in q["issues"]:
                q["issues"].append(issue)
        if asset.get("qaStatus")!="PASS":
            q["questionVerified"]=False
            q["reviewStatus"]="needs_review"
        q["answerVerified"]=False
    bycode={x["paper"]:x for x in original["papers"]}
    changed=0
    for mat in src["sharedMaterials"]:
        item=next((x for x in manifest["sharedMaterialCrops"]
                   if x["sharedMaterialId"]==mat["sharedMaterialId"]),None)
        if not item:
            unmatched.append(mat["sharedMaterialId"])
            continue
        f=ROOT/item["output"]
        if hashfile(f)!=item["sha256"]:
            raise ValueError("Common passage WebP SHA changed")
        mat["asset"]={
           "output":item["output"],"source":item["source"],
           "sourcePage":item["sourcePage"],"crop":item["crop"],
           "sha256":item["sha256"],"sourceSha256":item["sourceSha256"],
           "qaStatus":"PENDING_INDIVIDUAL_VISUAL_QA"
        }
        # PDF-layer text is a DISTINCT extraction. Preserve any previously
        # transcribed/corrected original shared text instead of overwriting.
        paper=mat["paperCode"]
        PDF=bycode[paper]
        sha=byid[f"115-{paper}-01"]["questionProvenance"]["pdfSha256"]
        mat.setdefault("questionNumbers",item["originalQuestionNumbers"])
        mat.setdefault("sourceImage",item["source"])
        if not mat.get("pdfNativeRaw"):
            data=pin_download(PDF["questionPdf"],sha)
            with fitz.open(stream=data,filetype="pdf") as pdf:
                page=pdf[item["sourcePage"]-1]
                source=ROOT/item["source"]
                with Image.open(source) as im:
                    fx=im.width/page.rect.width
                    fy=im.height/page.rect.height
                x0,y0,x1,y1=item["crop"]
                rect=fitz.Rect(x0/fx,y0/fy,x1/fx,y1/fy)
                native=page.get_text("text",clip=rect,sort=True)
            mat["pdfNativeRaw"]=native
            mat["pdfNativeRawMethod"]="pymupdf_native_pdf_text_layer_only"
            mat["nativeTextExtractedAt"]=timestamp
            if not mat.get("text"):
                mat["text"]=native
                mat["extractionMethod"]="native_pdf_text_layer_unreviewed"
            changed+=1
        mat["reviewStatus"]="second_pass_pending"
    for q in src["questions"]:
        if q.get("sharedMaterialId"):
            shared=next((m for m in src["sharedMaterials"]
                         if m["sharedMaterialId"]==q["sharedMaterialId"]),None)
            if shared and shared.get("asset"):
                q["assets"]["sharedMaterialWebps"]=[shared["asset"]["output"]]
            else:
                raise ValueError("Unresolved shared material: "+q["questionId"])
    if unmatched:
        raise ValueError("Some common materials have no pixel crop: "+str(unmatched))
    # No independent review may accidentally be promoted by this script.
    if any(q["questionVerified"] or q["answerVerified"] for q in src["questions"]):
        raise ValueError("Unreviewed true verification flag")
    src["assetManifest"]="sudu/data/processed/115/webp-manifest.json"
    src["assetProcessingVersion"]=manifest["processingVersion"]
    src["rawOcrCandidates"]=len(ocr)
    src["sharedNativeMaterialCount"]=changed
    write("questions.json",src)
    print(json.dumps({"questions":len(src["questions"]),"cropAssets":len(manifest["items"]),
                      "rawOcr":len(ocr),"commonPassages":len(src["sharedMaterials"]),
                      "nativePassageExtracts":changed,"questionVerified":0,
                      "answerVerified":0},ensure_ascii=False))
if __name__=="__main__":
    main()
