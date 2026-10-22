#!/usr/bin/env python3
"""115-only source-preserving WebP asset builder.

All raster crops originate from already committed official page WebPs. Download
the SHA-pinned official PDFs only to recover text-layer question coordinates.
Coordinates / all unverified issues are exported; no UI, grading or student
records are changed. Never set questionVerified or answerVerified here.
"""
from __future__ import annotations
import argparse
import base64
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

import fitz
import numpy as np
import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "sudu/data/processed/115/questions.json"
YEAR = ROOT / "sudu/data/years/115.json"
CROPS = ROOT / "sudu/demo-question-crops.json"
HTML = ROOT / "sudu/v4-115-multisubject-review-demo.html"
OUT = ROOT / "sudu/data/processed/115"
ALLOWED = {"web1.tcte.edu.tw", "www.tcte.edu.tw", "tcte.edu.tw"}
OPT = re.compile(r"[\(（]\s*([ABCD])\s*[\)）]", re.I)
ANCHOR = re.compile(r"^(\d{1,2})[.．、](?:\S*)$")
VERSION = "115-draft-pixelcrop-v2"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download_official(url: str, expected: str) -> bytes:
    current = url
    for _ in range(5):
        parsed = urlparse(current)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED:
            raise ValueError("Nonofficial or non-HTTPS source: " + current)
        response = requests.get(current, allow_redirects=False, timeout=(20, 80),
                                headers={"User-Agent":"7581707-115-visual-geometry-check/1.0"})
        if response.is_redirect:
            current = urljoin(current, response.headers["Location"])
            continue
        response.raise_for_status()
        content = response.content
        if len(content) > 40_000_000 or not content.startswith(b"%PDF"):
            raise ValueError("Not a valid PDF or PDF too large")
        if sha256(content) != expected:
            raise ValueError("Official PDF SHA-256 changed; manual source version review required")
        return content
    raise ValueError("Too many official redirects")

def page_asset(paper: str, page: int) -> Path | None:
    folder = ROOT / "sudu/data/original/115" / paper
    choices = sorted(folder.glob(f"p{page:03d}-*-v2-w1400-q66.webp"))
    return choices[0] if len(choices) == 1 else None

def read_pdf_geometry(doc: fitz.Document, maxnumber: int):
    candidates = defaultdict(list)
    allwords = {}
    for pidx, page in enumerate(doc):
        if pidx == 0:  # title/cover instructions are never questions
            continue
        words = page.get_text("words", sort=True)
        allwords[pidx + 1] = words
        for x0,y0,x1,y1,word,*_ in words:
            m = ANCHOR.match(word.strip())
            if not m:
                continue
            n=int(m.group(1))
            if not (1<=n<=maxnumber and 22<=x0<=90 and 38<=y0<=page.rect.height-48):
                continue
            candidates[n].append({"page":pidx+1,"x0":round(x0,2),
                                  "y0":round(y0,2),"y1":round(y1,2),
                                  "token":word})
    return candidates, allwords

def select_anchors(candidates, expected, legacy):
    chosen={}
    ambiguous=[]
    missing=[]
    last=(1,0.0)
    for n in range(1,expected+1):
        items=sorted(candidates.get(n,[]),key=lambda z:(z["page"],z["y0"]))
        # Prefer sequential ordering; legacy page is only a hint and may be wrong.
        valid=[z for z in items if (z["page"],z["y0"])>last]
        if not valid:
            missing.append(n)
            continue
        previous_page=legacy.get(n)
        if len(valid)>1:
            ambiguous.append({"number":n,"candidates":valid})
            # Keep the first real sequence position unless an exact legacy
            # page matches; either way status remains ambiguous.
            same=[z for z in valid if z["page"]==previous_page]
            best=same[0] if same else valid[0]
        else:
            best=valid[0]
        chosen[n]=best
        last=(best["page"],best["y0"])
    return chosen,missing,ambiguous

def ink_last_row(im:Image.Image, x0:int, top:int, x1:int, limit:int) -> int:
    if limit<=top+4:
        return top
    a=np.asarray(im.convert("L").crop((x0,top,x1,limit)),dtype=np.uint8)
    # Ignore isolated compression pixels; require a horizontal ink cluster.
    black=(a<170).sum(axis=1)
    rows=np.flatnonzero(black>=5)
    return int(top+rows[-1]) if rows.size else top

def bbox_for_question(doc, words, paper, chosen, n, source, report):
    anchor=chosen[n]
    page_num=anchor["page"]
    page=doc[page_num-1]
    with Image.open(source) as image:
        im=ImageOps.exif_transpose(image).convert("RGB")
        W,H=im.size
        sx=W/page.rect.width
        sy=H/page.rect.height
        start=max(96,int(anchor["y0"]*sy)-11)
        next_anchors=sorted((a for k,a in chosen.items()
                             if a["page"]==page_num and a["y0"]>anchor["y0"]),
                            key=lambda a:a["y0"])
        next_y=int(next_anchors[0]["y0"]*sy)-10 if next_anchors else H-115
        bound=min(H-115,next_y)
        if bound<=start+30:
            report.append("question_band_too_short")
            return None,None
        # Approximate last content row using original source pixels, not OCR.
        end=ink_last_row(im,93,start,1310,bound)+16
        end=min(max(start+45,end),bound)
        this_words=[w for w in words if start/sy-3 <= w[1] <=bound/sy
                    and 30 <=w[0]<=page.rect.width-25]
        marked=[(w[1],w[3],m.group(1).upper()) for w in this_words
                for m in [OPT.search(w[4])] if m]
        found={label for _,_,label in marked}
        # A full shared text for the NEXT group can occur between q24 and
        # q25; where A..D are located, clip before that unrelated passage.
        d_bottom=max((z[1] for z in marked if z[2]=="D"),default=None)
        if d_bottom is not None:
            dpx=int(d_bottom*sy)
            if end-dpx>90:
                after=[w for w in this_words if d_bottom<w[1]<=d_bottom+22]
                continuation=max((int(w[3]*sy) for w in after),default=dpx)
                end=min(end,max(dpx,continuation)+22)
                report.append("long_gap_after_D_clipped_candidate")
        if found !={"A","B","C","D"}:
            report.append("option_markers_in_pdf_text_not_complete:"+"".join(sorted(found)))
        if not next_anchors:
            report.append("last_question_on_page_check_footer_and_continuation")
        if end-start>int(H*0.6):
            report.append("oversize_crop_manual_review")
        return (90,start,1310,end),(W,H)

def old_inline_accounting():
    """Preserve previously QA'd accounting images without modifying pixels."""
    text=HTML.read_text(encoding="utf-8")
    m=re.search(r'<script id="demoData" type="application/json">(.*?)</script>',text,re.S)
    if not m:
        return {}
    data=json.loads(m.group(1))
    result={}
    for q in data.get("questions",[]):
        if q.get("subject")!="會計學" or q.get("id") not in (2,3,4,5,6):
            continue
        uri=q.get("image","")
        if not uri.startswith("data:image/webp;base64,"):
            continue
        payload=base64.b64decode(uri.split(",",1)[1],validate=True)
        result[q["id"]]=payload
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--no-ocr", action="store_true", help="Skip Tesseract and write crop/geometry only")
    args=ap.parse_args()
    record=json.loads(INPUT.read_text(encoding="utf-8"))
    original=json.loads(YEAR.read_text(encoding="utf-8"))
    old_map=json.loads(CROPS.read_text(encoding="utf-8"))["crops"]
    questions=record["questions"]
    bypaper=defaultdict(list)
    for q in questions:
        bypaper[q["paperCode"]].append(q)
    for code in bypaper:
        bypaper[code].sort(key=lambda q:q["originalQuestionNumber"])
    prior_inline=old_inline_accounting()
    manifest=[]
    anchor_report={}
    ocr_records=[]
    summary={}
    run_ts=datetime.now(timezone.utc).isoformat()
    for p in original["papers"]:
        paper=p["paper"]
        current=bypaper[paper]
        expectedsha=current[0]["questionProvenance"]["pdfSha256"]
        pdfbin=download_official(p["questionPdf"],expectedsha)
        with fitz.open(stream=pdfbin,filetype="pdf") as pdf:
            candidates, allwords=read_pdf_geometry(pdf,len(current))
            if paper == "00-MB":
                # Page 2 begins with numbered reference FORMULAS 1-4, not exam
                # questions. Remove only their confirmed early anchors.
                for refno in (1,2,3,4):
                    candidates[refno] = [
                        a for a in candidates.get(refno, [])
                        if not (a["page"] == 2 and a["y0"] < 210)
                    ]
            legacy={q["originalQuestionNumber"]:q["questionProvenance"]["sourcePage"] for q in current}
            chosen,missing,ambiguous=select_anchors(candidates,len(current),legacy)
            anchor_report[paper]={"pdfSource":p["questionPdf"],"pdfSha256":expectedsha,
                                  "downloadReason":"read exact coordinate anchors; official PDF missing as local persisted binary",
                                  "anchorsFound":len(chosen),"missing":missing,
                                  "ambiguous":ambiguous,
                                  "allCandidateCounts":{str(k):len(v) for k,v in candidates.items()},
                                  "selected":{str(k):v for k,v in chosen.items()}}
            successful=0
            ocrdone=0
            for q in current:
                n=q["originalQuestionNumber"]
                qid=q["questionId"]
                issues=[]
                if n not in chosen:
                    manifest.append({"questionId":qid,"paperCode":paper,"subject":q["subject"],
                                     "sourcePdfSha256":expectedsha,"output":None,
                                     "qaStatus":"BLOCKED_NO_ANCHOR","issues":["original_number_anchor_not_identified"]})
                    continue
                anchor=chosen[n]
                pagenum=anchor["page"]
                source=page_asset(paper,pagenum)
                if source is None:
                    manifest.append({"questionId":qid,"paperCode":paper,"subject":q["subject"],
                                     "sourcePdfSha256":expectedsha,"output":None,
                                     "qaStatus":"BLOCKED_SOURCE_PAGE_MISSING",
                                     "issues":["versioned_original_webp_page_missing_or_ambiguous"]})
                    continue
                box,srcSize=bbox_for_question(pdf,allwords[pagenum],paper,chosen,n,source,issues)
                if box is None:
                    manifest.append({"questionId":qid,"paperCode":paper,"subject":q["subject"],
                                     "sourcePdfSha256":expectedsha,"output":None,
                                     "qaStatus":"BLOCKED_INVALID_BBOX","issues":issues})
                    continue
                existing=next((z for z in old_map if z["question"]==n and
                               (z["source"].split("/115/")[1].split("/")[0]==paper)),None)
                if existing:
                    # Existing human-reviewed demo geometry takes precedence.
                    esource=ROOT/existing["source"]
                    if esource.is_file():
                        source=esource
                        box=tuple(existing["box"])
                        with Image.open(source) as chk:
                            srcSize=chk.size
                        issues.append("reused_preexisting_demo_crop_coordinates")
                if paper == "00-E" and n == 24:
                    # Prevent next group heading leaking into question 24.
                    box=(90,927,1310,1016)
                    issues.append("reading_group_boundary_manually_measured_v2")
                path=OUT / "webp-v2" / paper / f"{qid}.webp"
                path.parent.mkdir(parents=True,exist_ok=True)
                with Image.open(source) as original_image:
                    if original_image.format!="WEBP":
                        raise AssertionError("Crop source is not original WebP")
                    if not (0<=box[0]<box[2]<=original_image.width and
                            0<=box[1]<box[3]<=original_image.height):
                        raise AssertionError("Crop outside original page")
                    cropped=original_image.crop(box)
                    output=io.BytesIO()
                    cropped.save(output,"WEBP",lossless=True,method=6)
                    encoded=output.getvalue()
                source_method="pixel_crop_of_official_page_webp"
                if paper=="09-2" and n in prior_inline:
                    # Previously verified Demo bytes must not be replaced by
                    # a fresh AI reconstruction or an unreviewed recrop.
                    encoded=prior_inline[n]
                    source_method="preserved_existing_inline_demo_webp_bytes"
                    issues.append("inline_bytes_preserved_but_crop_coordinates_are_candidate_only")
                with Image.open(io.BytesIO(encoded)) as check:
                    check.load()
                    if check.format!="WEBP" or min(check.size)<25:
                        raise ValueError("Unable to decode generated WebP")
                    outputSize=check.size
                if path.exists() and path.read_bytes()!=encoded:
                    raise ValueError("Refuse to overwrite differing versioned output "+str(path))
                path.write_bytes(encoded)
                successful+=1
                ocr_text=""
                ocr_engine=None
                if not args.no_ocr and (not q.get("options") or q.get("issues")):
                    import pytesseract
                    with Image.open(io.BytesIO(encoded)) as check:
                        ocr_text=pytesseract.image_to_string(check,lang="chi_tra+eng",
                                                             config="--psm 6")
                    ocr_engine="Tesseract chi_tra+eng PSM6 (uncorrected candidate)"
                    ocrdone+=1
                if ocr_engine:
                    ocr_records.append({"questionId":qid,"engine":ocr_engine,
                                        "ocrRawText":ocr_text,"ocrDate":run_ts,
                                        "sourceWebp":path.relative_to(ROOT).as_posix(),
                                        "correctedText":q.get("question"),
                                        "qaStatus":"NOT_VISUALLY_VERIFIED"})
                sourcebytes=source.read_bytes()
                manifest.append({
                    "schemaVersion":1,"questionId":qid,"paperCode":paper,"subject":q["subject"],
                    "originalQuestionNumber":n,"source":source.relative_to(ROOT).as_posix(),
                    "sourcePage":pagenum,"sourceSize":list(srcSize),
                    "crop":list(box),"sourceSha256":sha256(sourcebytes),
                    "sourcePdfSha256":expectedsha,"sourcePagePdfPoint":[anchor["x0"],anchor["y0"]],
                    "output":path.relative_to(ROOT).as_posix(),
                    "outputSize":list(outputSize),"sha256":sha256(encoded),
                    "processingVersion":VERSION,"generatedAt":run_ts,
                    "cropMethod":source_method,"qaStatus":"DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA",
                    "ocrPerformed":bool(ocr_engine),"issues":issues,
                })
            summary[paper]={"expected":len(current),"anchorsFound":len(chosen),
                            "webpGenerated":successful,"ocrTriggered":ocrdone}
    # Passage images MUST be independent source-pixel crops; never substitute
    # a page image for a single question, or pack neighboring options together.
    shared=[]
    groups=[
      ("115-00-E-SHARED-21-24",5, (90,174,1310,759), list(range(21,25))),
      ("115-00-E-SHARED-25-28",5, (90,1019,1310,1568), list(range(25,29))),
      ("115-00-E-SHARED-29-30",6, (90,165,1310,1498), [29,30]),
      ("115-00-E-SHARED-31-32",7, (90,166,1310,1328), [31,32]),
      ("115-00-E-SHARED-33-35",8, (90,164,1310,1230), [33,34,35]),
      ("115-00-E-SHARED-36-38",9, (90,164,1310,772), [36,37,38]),
      ("115-00-E-SHARED-39-42",10,(90,166,1310,971), [39,40,41,42]),
    ]
    for group_id, page_no, box, numbers in groups:
        source=page_asset("00-E",page_no)
        if source is None:
            raise ValueError(f"Missing official shared page for {group_id}")
        with Image.open(source) as im:
            if not (0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height):
                raise ValueError("Common passage crop out of bounds")
            result=io.BytesIO()
            im.crop(box).save(result,"WEBP",lossless=True,method=6)
        payload=result.getvalue()
        dest=OUT/"webp-v2"/"shared"/(group_id+".webp")
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=payload:
            raise ValueError("Refuse to overwrite prior shared crop")
        dest.write_bytes(payload)
        shared.append({"sharedMaterialId":group_id,"paperCode":"00-E",
                       "originalQuestionNumbers":numbers,"source":source.relative_to(ROOT).as_posix(),
                       "sourcePage":page_no,"crop":list(box),
                       "output":dest.relative_to(ROOT).as_posix(),
                       "sha256":sha256(payload),"sourceSha256":sha256(source.read_bytes()),
                       "qaStatus":"DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA",
                       "issues":["shared_text_must_be_visually_reviewed_separately"]})
    done=sum(bool(item.get("output")) for item in manifest)
    allmanifest={"schemaVersion":1,"year":115,"processingVersion":VERSION,"generatedAt":run_ts,
                 "sourceRule":"Pixel crop from existing 115 official WebP; official SHA-pinned PDF accessed solely for coordinates.",
                 "reviewPolicy":"DRAFT images only. Automated decode, bounds and PDF anchor checks are NOT manual visual QA.",
                 "expected":len(questions),"generated":done,"missing":len(questions)-done,
                 "summary":summary,"sharedMaterialCrops":shared,"items":manifest}
    (OUT/"webp-manifest.json").write_text(json.dumps(allmanifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"anchor-report.json").write_text(json.dumps(anchor_report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"ocr-raw-candidates.json").write_text(json.dumps({"year":115,"count":len(ocr_records),
                                           "status":"unreviewed_raw_OCR_candidates",
                                           "items":ocr_records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"summary":summary,"webpGenerated":done,"missing":len(questions)-done,
                      "ocrRecords":len(ocr_records),"shared":len(shared)},ensure_ascii=False))
    if done==0:
        raise RuntimeError("No single-question WebP was safely generated")

if __name__=="__main__":
    main()
