#!/usr/bin/env python3
"""115 original-photo crop refinement: preserve old drafts; create traceable v3.

Fix visually identified Math B Q1 plot/caption cropping and English reading
charts, then prepare separate professional-paper shared material crops.
Only official source WebP pixels; no fake text, full-page substitute or OCR.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import io
import json
import re
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"sudu/data/processed/115"
MANIFEST=OUT/"webp-manifest.json"
RULE="v3-visual-review-draft-source-pixel-only"
def digest(b):return hashlib.sha256(b).hexdigest()
def page(paper,pagenum):
    choices=sorted((ROOT/"sudu/data/original/115"/paper).glob(f"p{pagenum:03d}-*-v2-w1400-q66.webp"))
    if len(choices)!=1:raise ValueError(f"Ambiguous original page {paper} {pagenum}: {len(choices)}")
    return choices[0]
def write_original_crop(source,box,dest):
    payload_source=source.read_bytes()
    with Image.open(io.BytesIO(payload_source)) as im:
        if im.format!="WEBP" or not (0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height):
            raise ValueError("Invalid original WebP crop bounds")
        buf=io.BytesIO()
        im.crop(box).save(buf,"WEBP",lossless=True,method=6)
        size=[box[2]-box[0],box[3]-box[1]]
        source_size=list(im.size)
    payload=buf.getvalue()
    with Image.open(io.BytesIO(payload)) as check:
        check.load()
        if check.format!="WEBP":raise ValueError("Invalid generated WebP")
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=payload:
        raise ValueError("Versioned output changed: "+str(dest))
    dest.write_bytes(payload)
    return {"source":source.relative_to(ROOT).as_posix(),
            "sourceSize":source_size,"sourceSha256":digest(payload_source),
            "crop":list(box),"output":dest.relative_to(ROOT).as_posix(),
            "outputSize":size,"sha256":digest(payload)}
def main():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["generated"]!=205:raise ValueError("Full draft manifest required")
    q={e["questionId"]:e for e in data["items"]}
    for qid in ("115-00-MB-01",):
        item=q[qid]
        official=page("00-MB",2)
        rect=(90,503,1310,867)  # Q1 full diagram caption, Q2 starts lower.
        asset=write_original_crop(official,rect,OUT/"webp-v3"/"00-MB"/(qid+".webp"))
        item.update(asset)
        item["processingVersion"]=RULE
        item["qaStatus"]="DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA"
        item["cropMethod"]="refined_source_pixel_crop_after_visual_QA_detection"
        item.setdefault("issues",[]).append("v2_clip_cut_off_figure_caption_fixed_by_new_candidate_crop")
    # The 2026-10-22 visual crop QA found two independent defects that a
    # filename/hash/decode-only audit did not catch. Source pages remain intact.
    # Q13: option graphs C/D are cut off; Q20: figure IV lower edge/caption
    # is clipped. Store corrected source-pixel-only drafts under a new version.
    v5_question_repairs={
        "115-00-MB-13":(5,(90,174,1310,933),
                        "previous_candidate_missing_lower_C_D_option_graphs"),
        "115-00-MB-20":(7,(90,469,1310,902),
                        "previous_candidate_missing_figure_IV_lower_edge_and_caption"),
    }
    for qid,(page_num,box,reason) in v5_question_repairs.items():
        item=q[qid]
        nxt=q[f"115-00-MB-{item['originalQuestionNumber']+1:02d}"]
        if nxt["sourcePage"]==page_num and box[3]>nxt["crop"][1]:
            raise ValueError(f"Candidate crop overlaps next question: {qid}")
        source=page("00-MB",page_num)
        corrected=write_original_crop(source,box,OUT/"webp-v5"/"00-MB"/(qid+".webp"))
        item.update(corrected)
        item["processingVersion"]="v5-math-figure-boundary-repair-draft"
        item["qaStatus"]="DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA"
        item["cropMethod"]="original_pixel_replacement_after_explicit_visual_defect"
        item.setdefault("issues",[]).append(reason)
        item["visualDefectHistory"]={
            "detectedOn":"2026-10-22",
            "originalCandidateVersion":"webp-v2",
            "finding":reason,
            "repairStatus":"generated_pending_independent_visual_recheck",
        }
    # Accounting Q22 v2 extends below its D option into the standalone
    # shared paragraph for Q23-24. A question WebP may never contain material
    # for a different question group; preserve v2 for audit, create new v6.
    qid="115-09-2-22"
    item=q[qid]
    source=page("09-2",6)
    rect=(90,714,1310,910)  # all Q22 options, before Q23-24 shared heading
    corrected=write_original_crop(source,rect,OUT/"webp-v6"/"09-2"/(qid+".webp"))
    item.update(corrected)
    item["processingVersion"]="v6-accounting-exclude-next-reading-material"
    item["qaStatus"]="DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA"
    item["cropMethod"]="original_pixel_crop_Q22_end_before_Q23-24_shared_text"
    item.setdefault("issues",[]).append("v2_Q22_included_Q23_24_shared_reading_heading")
    item["visualDefectHistory"]={
        "detectedOn":"2026-10-22",
        "originalCandidateVersion":"webp-v2",
        "finding":"Q22 D option followed by unrelated Q23-24 reading material",
        "repairStatus":"generated_pending_independent_visual_recheck",
    }
    shared={e["sharedMaterialId"]:e for e in data["sharedMaterialCrops"]}
    specs=[
      # Correct English axis labels/last sentence without including first question.
      ("115-00-E-SHARED-33-35","00-E",8,(90,164,1310,1238),[33,34,35]),
      ("115-00-E-SHARED-39-42","00-E",10,(90,166,1310,978),[39,40,41,42]),
      # Professional-paper materials are cropped independently from their questions.
      ("115-09-1-SHARED-18-19","09-1",5,(90,340,1310,628),[18,19]),
      ("115-09-1-SHARED-20-21","09-1",5,(90,1075,1310,1307),[20,21]),
      ("115-09-1-SHARED-22-23","09-1",6,(90,162,1310,1184),[22,23]),
      ("115-09-1-SHARED-24-25","09-1",7,(90,163,1310,785),[24,25]),
      ("115-09-2-SHARED-23-24","09-2",6,(90,918,1310,1072),[23,24]),
      # Economics 49/50 share the official factory batch/currency-rate table.
      # Their question strips alone intentionally exclude this reading material.
      ("115-09-2-SHARED-49-50","09-2",11,(90,160,1310,740),[49,50]),
      # Chinese common reading material is separate from numbered question crops.
      ("115-00-C-SHARED-11-15","00-C",4,(90,160,1310,1530),[11,12,13,14,15]),
      ("115-00-C-SHARED-16-18","00-C",6,(90,161,1310,1049),[16,17,18]),
      ("115-00-C-SHARED-19-22","00-C",7,(90,160,1310,1063),[19,20,21,22]),
      ("115-00-C-SHARED-23-26","00-C",8,(90,161,1310,1230),[23,24,25,26]),
      ("115-00-C-SHARED-27-30","00-C",9,(90,332,1310,1100),[27,28,29,30]),
      ("115-00-C-SHARED-31-34","00-C",10,(90,162,1310,1033),[31,32,33,34]),
      ("115-00-C-SHARED-35-38","00-C",11,(90,162,1310,1018),[35,36,37,38]),
    ]
    # v4: source-image visual inspection found a previous option bleeding into
    # business q18-19 material, and several shared last rows near cut boundaries.
    # Never replace older v3 files; preserve SHA provenance and make v4 only for
    # individually identified shared-material boundaries.
    v4_fixes={
      "115-09-1-SHARED-18-19":(90,365,1310,628),
      "115-09-1-SHARED-24-25":(90,163,1310,793),
      "115-00-C-SHARED-19-22":(90,160,1310,1071),
      "115-00-C-SHARED-23-26":(90,161,1310,1237),
      "115-00-C-SHARED-27-30":(90,332,1310,1108),
      "115-00-C-SHARED-31-34":(90,162,1310,1041),
      "115-00-C-SHARED-35-38":(90,162,1310,1026),
    }
    for group,paper,pg,box,nums in specs:
        box=v4_fixes.get(group,box)
        current=shared.get(group)
        # Need official question anchor gap to prevent other question content.
        qstart=q[f"115-{paper}-{nums[0]:02d}"]["crop"][1]
        first_q=q[f"115-{paper}-{nums[0]:02d}"]
        if first_q["sourcePage"]==pg and box[3]>=qstart:
            raise ValueError(f"Shared material overlaps {group} first question")
        image=page(paper,pg)
        version="webp-v4" if group in v4_fixes else "webp-v3"
        asset=write_original_crop(image,box,OUT/version/"shared"/(group+".webp"))
        value={**asset,"sharedMaterialId":group,"paperCode":paper,"sourcePage":pg,
               "originalQuestionNumbers":nums,"processingVersion":RULE,
               "qaStatus":"DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA",
               "issues":["Visually compare entire shared passage against official full page."]}
        if current is not None:
            current.update(value)
        else:
            data["sharedMaterialCrops"].append(value)
    # Reuse the 30 already individually reviewed Demo crops ONLY if exact
    # pixels match the documented 2026-10-21 visual-QA SHA-256 per image.
    # This is evidence reuse, not a fresh new vision inspection. Accounting
    # inline items have no 30-row SHA mapping and are not promoted here.
    qa_file=ROOT/"sudu/DEMO_VISUAL_QA.md"
    qa_bytes=qa_file.read_bytes()
    qa_sha=digest(qa_bytes)
    reviewed=0
    qa_regex=re.compile(r"^\|\s*([^|]+)\s*\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*PASS\s*\|\s*`([a-f0-9]{64})`\s*\|")
    for line in qa_bytes.decode("utf-8").splitlines():
        found=qa_regex.match(line)
        if not found:continue
        subject,num,hashvalue=found.group(1).strip(),int(found.group(2)),found.group(3)
        possible=[entry for entry in data["items"]
                  if entry["subject"].replace(" ","")==subject.replace(" ","")
                  and entry["originalQuestionNumber"]==num]
        if len(possible)!=1:
            raise ValueError("QA subject/number ambiguous "+subject+str(num))
        entry=possible[0]
        if entry["sha256"]!=hashvalue:
            raise ValueError("Previously visually reviewed pixel digest changed: "+entry["questionId"])
        entry["qaStatus"]="PASS"
        entry["visualReviewEvidence"]={
          "reviewedAt":"2026-10-21",
          "reviewMethod":"historical_individual_visual_QA_reused_by_exact_output_sha256",
          "reference":"sudu/DEMO_VISUAL_QA.md",
          "referenceSha256":qa_sha,
          "reviewedSha256":hashvalue,
          "freshReviewInThisRun":False,
          "criteria":"original number, stem, 4 options, diagrams, no adjacent question or header/footer"
        }
        reviewed+=1
    if reviewed!=30:
        raise ValueError("Expected exactly 30 separately SHA-recorded Demo WebP reviews")
    data["historicalVisualQaReused"]=reviewed
    data["refinements"]=data.get("refinements",[])+[{
        "revision":RULE,"timestamp":datetime.now(timezone.utc).isoformat(),
        "notes":"Q1 original maths diagram caption, Q13 lower graph options and Q20 lower figure IV corrected; material groups are source-only. Earlier versions retained.",
        "questionOverrides":["115-00-MB-01","115-00-MB-13","115-00-MB-20"],
        "sharedMaterials":[x[0] for x in specs]
    }]
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"expected":data["expected"],"generated":data["generated"],
                      "shared":len(data["sharedMaterialCrops"]),
                      "refinedQuestion":"115-00-MB-01"},ensure_ascii=False))
if __name__=="__main__":main()
