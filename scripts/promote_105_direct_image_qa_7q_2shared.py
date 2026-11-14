#!/usr/bin/env python3
"""Promote ONLY already directly visually inspected SHA-pinned 105 WebP images.

The exact 7 question SHA hashes and 2 shared-material SHA hashes have
independent source-to-output *assistant visual inspection* evidence.
This does NOT verify text, answers, explanations, official corrections,
SQLite round-trips or a release; every integrationReady stays false.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/105")
DRAFT=BASE/"qa-drafts"
BRANCH="qa/114-115-official-visual-review"
E7=DRAFT/"DIRECT_VISUAL_QA_105_7Q_2SHARED_20261023.json"
E4=DRAFT/"DIRECT_VISUAL_QA_105_SHARED_27_29_V4_20261023.json"
Q_IDS=["105-00-C-24","105-00-C-25","105-00-C-26","105-00-C-27",
       "105-09-2-48","105-09-2-49","105-09-2-50"]
SHARED_IDS=["105-00-C-SHARED-24-26","105-00-C-SHARED-27-29"]
FILES=["questions.json","webp-manifest.json","VISUAL_QA.json","inventory.json","VALIDATION.json"]

def file(p):
    resolved=(ROOT/p).resolve()
    if not resolved.is_relative_to(ROOT): raise RuntimeError("Unsafe repository path")
    return resolved

def load(p):return json.loads(file(p).read_text("utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def one_by_id(rows,key):return {x[key]:x for x in rows}

def validate_evidence():
    old=load(E7)
    revised=load(E4)
    if (old["directlyVisuallyPassedQuestionWebp"]!=7
        or old["directlyVisuallyPassedSharedWebp"]!=1
        or old["failedSharedWebp"]!=1 or old["integrationReady"]):
        raise RuntimeError("Unexpected 7-question QA evidence")
    if revised["imageQaStatus"]!="PASS" or revised["integrationReady"]:
        raise RuntimeError("Shared v4 visual evidence is not a verified image-only PASS")
    original=one_by_id(old["records"],"assetId")
    if len(original)!=9 or set(Q_IDS+SHARED_IDS)!=set(original):
        raise RuntimeError("Unexpected directly visually reviewed assets")
    reviewed={x:original[x].copy() for x in Q_IDS+[SHARED_IDS[0]]}
    revised_old=original[SHARED_IDS[1]]
    if not revised_old["imageQaStatus"].startswith("FAIL_"):
        raise RuntimeError("Must preserve the v3 visual failure")
    reviewed[SHARED_IDS[1]]={
        "assetId":revised["assetId"],"questionIds":revised["questionIds"],
        "sourceOfficialPdfUrl":revised["sourceOfficialPdfUrl"],
        "sourceOfficialPdfSha256":revised["sourceOfficialPdfSha256"],
        "originalPageWebp":revised["sourcePageWebp"],
        "sourcePageWebpSha256":revised["sourcePageWebpSha256"],
        "sourcePage":revised["sourcePage"],"cropPixels":revised["cropPixels"],
        "reviewedWebpPath":revised["reviewedWebpPath"],
        "reviewedWebpSha256":revised["reviewedWebpSha256"],
        "imageQaStatus":revised["imageQaStatus"],
        "reviewer":revised["qaReviewer"],"reviewedAt":revised["qaReviewedAt"],
        "pixelExactSourceCropMatch":revised["pixelExactSourceCropMatch"],
        "evidencePath":str(E4)
    }
    for key,r in reviewed.items():
        if key!=SHARED_IDS[1]:r["evidencePath"]=str(E7)
        if r["assetId"]!=key or r["imageQaStatus"]!="PASS" or not r["reviewer"]:
            raise RuntimeError("Insufficient direct visual review: "+key)
        if not r["pixelExactSourceCropMatch"]:
            raise RuntimeError("Missing pixel-match proof: "+key)
        if r.get("independentHumanReview"): # assistant review is explicit, not external human sign-off
            raise RuntimeError("Incorrect reviewer identity: "+key)
        src=file(r["originalPageWebp"])
        dst=file(r["reviewedWebpPath"])
        if not src.is_file() or not dst.is_file():
            raise RuntimeError("Required image not found: "+key)
        if sha(src.read_bytes())!=r["sourcePageWebpSha256"]:
            raise RuntimeError("Source SHA mismatch: "+key)
        if sha(dst.read_bytes())!=r["reviewedWebpSha256"]:
            raise RuntimeError("Reviewed output SHA mismatch: "+key)
        with Image.open(src) as s, Image.open(dst) as d:
            s.load();d.load()
            if s.format!="WEBP" or d.format!="WEBP":
                raise RuntimeError("Non-WebP: "+key)
            crop=s.crop(tuple(r["cropPixels"]))
            if crop.size!=d.size or ImageChops.difference(crop.convert("RGB"),d.convert("RGB")).getbbox() is not None:
                raise RuntimeError("Source/crop pixel mismatch: "+key)
    return reviewed

def apply(stage=False):
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if branch!=BRANCH:raise RuntimeError("Only allowed on isolated QA branch")
    approved=validate_evidence()
    bank=load(BASE/"questions.json")
    manifest=load(BASE/"webp-manifest.json")
    visual=load(BASE/"VISUAL_QA.json")
    inv=load(BASE/"inventory.json")
    validation=load(BASE/"VALIDATION.json")
    if not (len(bank["questions"])==len(manifest["items"])==len(visual["items"])==204):
        raise RuntimeError("Unexpected historical question count")
    if int(inv["visualQaPass"]) not in (0,7):
        raise RuntimeError("Refusing to alter pre-existing other image QA")
    if int(inv["webpGeneratedDrafts"]) not in (197,204):
        raise RuntimeError("Refusing to alter unexpected candidate counts")
    by_question=one_by_id(bank["questions"],"questionId")
    by_manifest=one_by_id(manifest["items"],"questionId")
    by_visual=one_by_id(visual["items"],"questionId")
    if len(by_question)!=204 or len(by_manifest)!=204 or len(by_visual)!=204:
        raise RuntimeError("Duplicate QA question IDs")
    for qid in Q_IDS:
        evidence=approved[qid];q=by_question[qid];m=by_manifest[qid];v=by_visual[qid]
        if (q["questionId"]!=m["questionId"] or
            m["officialQuestionPdfSha256"]!=evidence["sourceOfficialPdfSha256"] or
            m["officialQuestionPdfUrl"]!=evidence["sourceOfficialPdfUrl"]):
            raise RuntimeError("Official source mismatch: "+qid)
        if m.get("qaStatus")=="PASS" and m.get("outputSha256")!=evidence["reviewedWebpSha256"]:
            raise RuntimeError("Do not redo an already-passed different SHA: "+qid)
        original_issues=m.get("issues",[])
        m.update({
            "sourcePage":evidence["sourcePage"],"source":evidence["originalPageWebp"],
            "sourcePageWebpSha256":evidence["sourcePageWebpSha256"],
            "cropPixels":evidence["cropPixels"],"output":evidence["reviewedWebpPath"],
            "outputSha256":evidence["reviewedWebpSha256"],
            "outputSize":[evidence["cropPixels"][2]-evidence["cropPixels"][0],
                          evidence["cropPixels"][3]-evidence["cropPixels"][1]],
            "generationVersion":"manual-visual-SHA-reviewed-v2-or-v3",
            "qaStatus":"PASS",
            "visualReviewEvidence":{
                "reference":evidence["evidencePath"],
                "reviewedSha256":evidence["reviewedWebpSha256"],
                "sourcePageSha256":evidence["sourcePageWebpSha256"],
                "qaReviewer":evidence["reviewer"],"qaReviewedAt":"2026-10-23",
                "method":"direct_original_page_to_exact_WebP_visual_inspection",
                "independentHumanReview":False
            },
            "issues":[x for x in original_issues if x!="UNVERIFIED_PDF_QUESTION_NUMBER_ANCHOR"]
        })
        v.update({
            "status":"PASS","sourcePage":evidence["sourcePage"],
            "sourceWebp":evidence["originalPageWebp"],
            "sourceSha256":evidence["sourcePageWebpSha256"],
            "candidateWebp":evidence["reviewedWebpPath"],
            "candidateSha256":evidence["reviewedWebpSha256"],
            "cropPixels":evidence["cropPixels"],
            "reviewer":evidence["reviewer"],"reviewedAt":"2026-10-23",
            "visualEvidence":evidence["evidencePath"]
        })
        if q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady"):
            raise RuntimeError("Unexpected verified/release flag: "+qid)
        q.setdefault("assets",{})
        q["assets"].update({
            "singleQuestionWebp":evidence["reviewedWebpPath"],
            "sourcePageWebp":evidence["originalPageWebp"],
            "sha256":evidence["reviewedWebpSha256"],
            "sourcePage":evidence["sourcePage"],
            "imageQaEvidence":evidence["evidencePath"]
        })
        q["sourcePage"]=evidence["sourcePage"]
        q["imageQaStatus"]="PASS"
        q["issues"]=[x for x in q.get("issues",[]) if x!="UNVERIFIED_PDF_QUESTION_NUMBER_ANCHOR"]
    shared_link={
        SHARED_IDS[0]:["105-00-C-24","105-00-C-25","105-00-C-26"],
        SHARED_IDS[1]:["105-00-C-27","105-00-C-28","105-00-C-29"]
    }
    for sid,related in shared_link.items():
        item=approved[sid]
        evidence_ref=item["evidencePath"]
        material={
            "sharedMaterialId":sid,"year":105,"paperCode":"00-C",
            "questionIds":related,"sourcePage":item["sourcePage"],
            "source":item["originalPageWebp"],
            "sourcePageWebpSha256":item["sourcePageWebpSha256"],
            "cropPixels":item["cropPixels"],"output":item["reviewedWebpPath"],
            "outputSha256":item["reviewedWebpSha256"],
            "qaStatus":"PASS",
            "visualReviewEvidence":{
                "reference":evidence_ref,"reviewedSha256":item["reviewedWebpSha256"],
                "sourcePageSha256":item["sourcePageWebpSha256"],
                "qaReviewer":item["reviewer"],"qaReviewedAt":"2026-10-23",
                "method":"direct_original_page_to_shared_material_WebP_visual_inspection",
                "independentHumanReview":False
            },
            "integrationReady":False
        }
        for container,key in [(manifest,"sharedMaterialCrops"),(bank,"sharedMaterials"),(visual,"sharedMaterials")]:
            arr=container.setdefault(key,[])
            present=[x for x in arr if x.get("sharedMaterialId")==sid]
            if present and any(x.get("outputSha256")!=item["reviewedWebpSha256"] for x in present):
                raise RuntimeError("Existing SHA-different shared material: "+sid)
            arr[:]=[x for x in arr if x.get("sharedMaterialId")!=sid]+[material.copy()]
        for qid in related:
            q=by_question[qid]
            old=q.setdefault("sharedMaterialIds",[])
            if sid not in old:old.append(sid)
            q.setdefault("assets",{})["sharedMaterialIds"]=old.copy()
    visual["passCount"]=sum(q.get("status")=="PASS" for q in visual["items"])
    if visual["passCount"]!=7:raise RuntimeError("Unexpected verified image pass tally")
    inv["webpGeneratedDrafts"]=204
    inv["visualQaPass"]=7
    inv["sharedMaterialsVerified"]=2
    inv["directVisualQaEvidence"]=str(E7)
    inv["directVisualSharedV4Evidence"]=str(E4)
    inv["integrationReady"]=False
    validation["imageVisualQaPass"]=7
    validation["directVisualQaNote"]="7 image WebP and 2 shared WebP directly inspected; source SHA and crop pixels verified; OCR, final answers and DB association still pending."
    validation["integrationReady"]=False
    if any(q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady") for q in bank["questions"]):
        raise RuntimeError("Invalid release gate: question, answer or release promoted")
    for p,obj in [(BASE/"questions.json",bank),(BASE/"webp-manifest.json",manifest),
                  (BASE/"VISUAL_QA.json",visual),(BASE/"inventory.json",inv),
                  (BASE/"VALIDATION.json",validation)]:
        raw=(json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        if stage and file(p).read_bytes()!=raw:file(p).write_bytes(raw)
    return {
        "status":"APPLIED" if stage else "VALIDATED_NOT_WRITTEN",
        "questionWebpDirectVisualPass":7,"sharedWebpDirectVisualPass":2,
        "officialFinalAnswersVerified":0,"questionTextVerified":0,
        "integrationReady":False,"writesOnly":list(FILES)
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    a=p.parse_args()
    print(json.dumps(apply(stage=a.stage),ensure_ascii=False))
