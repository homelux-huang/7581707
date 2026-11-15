#!/usr/bin/env python3
"""106 Chinese 36-38 cross-page source-original per-question WebP candidates.

Crops use exact pixels of existing TCTE printed-paper page 8 and separate
printed shared passage on page 7. No OCR, AI redrawing, G1 promotion or release.
Coordinates are candidate bounds from direct page visual inspection 2026-10-24;
they must be independently visually QA reviewed before release.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageChops
from link_106_c14_20_existing_webp_drafts import db_rebuild, read, resolved, sha, write

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/106"
PDF_SHA="93b8ec6eb319c8c7f5350ffa6267a2b4aed2f7acb1d1a2a7ca89e38f69ec5476"
PAGE={
 7:("sudu/data/original/106/00-C/p007-93b8ec6eb3-v2-w1400-q66.webp",
    "3d0cf18a9c6c27c7a368d4fbfe2df6979f0792f2"),
 8:("sudu/data/original/106/00-C/p008-93b8ec6eb3-v2-w1400-q66.webp",
    "5e4f43ced0a51d2e700a8a5ca002c0553f63bec3")
}
CROPS={
  "106-00-C-36":(8,[90,155,1310,356]),
  "106-00-C-37":(8,[90,364,1310,568]),
  "106-00-C-38":(8,[90,585,1310,682]),
  "106-00-C-SHARED-36-38":(7,[90,1260,1310,1810])
}
EXPECTED={f"106-00-C-{i:02d}" for i in (36,37,38)}
SID="106-00-C-SHARED-36-38"
REPORT=BASE/"qa-drafts/DRAFT_106_C36_38_SHARED_CROSSPAGE_20261024.json"

def gitblob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\x00"+data).hexdigest()

def make_crops(write_images):
    sources={}
    for page,(location,expected_blob) in PAGE.items():
        payload=resolved(location).read_bytes()
        assert gitblob(payload)==expected_blob, "Source WebP Git blob differs"
        with Image.open(io.BytesIO(payload)) as img:
            img.load()
            assert img.format=="WEBP" and img.size[0]==1400 and 1950<=img.size[1]<=2000
        sources[page]={"bytes":payload,"path":location,"sha256":sha(payload)}
    result={}
    for qid,(page,box) in CROPS.items():
        src=sources[page]
        with Image.open(io.BytesIO(src["bytes"])) as img:
            img.load()
            assert 0<=box[0]<box[2]<=img.width
            assert 0<=box[1]<box[3]<=img.height
            crop=img.crop(tuple(box))
            buf=io.BytesIO()
            crop.save(buf,"WEBP",lossless=True,method=6,exact=True)
            content=buf.getvalue()
            with Image.open(io.BytesIO(content)) as decoded:
                decoded.load()
                assert decoded.size == crop.size
                assert ImageChops.difference(crop.convert("RGB"),decoded.convert("RGB")).getbbox() is None
        typ="shared" if qid==SID else "00-C"
        out=(BASE/"qa-drafts/webp-v3"/typ/(qid+".webp")).relative_to(ROOT).as_posix()
        file=resolved(out)
        if file.exists():
            assert sha(file.read_bytes())==sha(content), "Existing candidate differs; refuse overwrite"
        elif write_images:
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes(content)
        result[qid]={
          "id":qid,"sourcePage":page,"source":src["path"],
          "sourcePageWebpSha256":src["sha256"],"officialQuestionPdfSha256":PDF_SHA,
          "cropPixels":box,"output":out,"outputSha256":sha(content),
          "outputSize":[box[2]-box[0],box[3]-box[1]],
          "generationVersion":"manual-source-pixel-candidate-v3-crosspage",
          "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
          "issues":["PENDING_INDIVIDUAL_VISUAL_SOURCE_TO_CROP_COMPARISON",
                    "PENDING_SHARED_PASSAGE_INDEPENDENT_QA"]}
    return result

def run(stage):
    existing=make_crops(stage)
    m=read(BASE/"webp-manifest.json")
    q=read(BASE/"questions.json")
    o=read(BASE/"ocr-raw-candidates.json")
    v=read(BASE/"VISUAL_QA.json")
    inv=read(BASE/"inventory.json")
    valid=read(BASE/"VALIDATION.json")
    release=read(BASE/"release-manifest.json")
    assert len(m["items"])==len(q["questions"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==201 and len(m["sharedMaterialCrops"])==len(q["sharedMaterials"])==3
    assert inv["visualQaPass"]==v["passCount"]==12 and inv["answerOfficialFinalVerified"]==0
    assert release["releaseAllowed"] is False and release["integrationReady"] is False
    byid={r["questionId"]:r for r in m["items"]}
    questions={r["questionId"]:r for r in q["questions"]}
    review={r["questionId"]:r for r in v["items"]}
    ocr={r["questionId"]:r for r in o["items"]}
    assert len(byid)==len(questions)==len(review)==len(ocr)==204
    for qid in sorted(EXPECTED):
        item=byid[qid]
        assert item["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not item.get("output") and not questions[qid]["assets"].get("singleQuestionWebp")
        assert review[qid]["status"]=="BLOCKED"
        assert questions[qid]["questionVerified"] is False
        assert questions[qid]["answerVerified"] is False
        assert questions[qid]["integrationReady"] is False
    if not stage:
        print(json.dumps({"mode":"check","threeNewCandidateCropIds":sorted(EXPECTED),
                          "sharedCrossPage":SID,"newG1Pass":0,"released":False},ensure_ascii=False))
        return
    for qid in sorted(EXPECTED):
        crop=existing[qid]
        byid[qid].update(crop)
        questions[qid]["assets"].update({
            "singleQuestionWebp":crop["output"],
            "sourcePageWebp":crop["source"],
            "sha256":crop["outputSha256"],
            "sourcePage":crop["sourcePage"]
        })
        questions[qid]["sharedMaterialIds"]=[SID]
        questions[qid]["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        questions[qid]["issues"]=sorted(set(questions[qid].get("issues",[])+crop["issues"]))
        ocr[qid]["imageSha256"]=crop["outputSha256"]
        review[qid].update({
            "status":"PENDING","sourcePage":8,"sourceWebp":crop["source"],
            "candidateWebp":crop["output"],"candidateSha256":crop["outputSha256"],
            "reviewer":None,"visualEvidence":None
        })
    shared=existing[SID].copy()
    shared.pop("id")
    shared.update({"sharedMaterialId":SID,"paperCode":"00-C",
                   "originalQuestionNumbers":[36,37,38]})
    assert SID not in {r["sharedMaterialId"] for r in m["sharedMaterialCrops"]}
    m["sharedMaterialCrops"].append(shared)
    q["sharedMaterials"].append(shared.copy())
    v["sharedMaterials"].append({
        "sharedMaterialId":SID,"status":"PENDING",
        "sourcePage":7,"sourceWebp":shared["source"],
        "candidateWebp":shared["output"],"candidateSha256":shared["outputSha256"],
        "reviewer":None,"visualEvidence":None
    })
    inv["webpGeneratedDrafts"]=204
    inv["sourcePaperStats"]["00-C"]["imageDrafts"]=38
    inv["sourcePaperStats"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(14,21))+[36,37,38]
    inv["sharedMaterialsDrafts"]=4
    valid["sourceGaps"]["00-C"]["imageDrafts"]=38
    valid["sourceGaps"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(14,21))+[36,37,38]
    # The PDF text layer still fails to anchor these. Keep G0 unresolved for manual QA.
    assert inv["visualQaPass"]==12 and not inv["integrationReady"]
    write(BASE/"webp-manifest.json",m)
    write(BASE/"questions.json",q)
    write(BASE/"ocr-raw-candidates.json",o)
    write(BASE/"VISUAL_QA.json",v)
    write(BASE/"inventory.json",inv)
    write(BASE/"VALIDATION.json",valid)
    db_rebuild(q)
    from audit_105_115_sqlite_readonly import audit_year
    g5=audit_year(106)
    assert g5["g5Pass"] is True and g5["onDiskRows"]==204 and g5["sandboxImportPasses"]==2
    write(REPORT, {
        "schemaVersion":1,"year":106,"questionIds":sorted(EXPECTED),
        "sharedMaterialId":SID,"questionCandidatesCreated":3,"sharedCandidatesCreated":1,
        "sourceOfficialPdfSha256":PDF_SHA,
        "candidateCrops":existing,
        "origin":"direct inspected printed page 7 shared passage and printed page 8 Q36-Q38",
        "actualVisualQaNotPromoted":True,
        "needsQuestionAndSharedVisualQa":True,
        "answerVerifiedChange":0,"textQaPassChange":0,
        "questionVerifiedChange":0,"visualQaPassChange":0,
        "sqliteG5Pass":True,"sqliteRows":204,"sqliteImportPasses":2,
        "releaseAllowed":False,"integrationReady":False
    })
    print(json.dumps({"mode":"staged","newWebpCandidates":3,"newSharedCandidate":1,
                      "all106WebpDrafts":inv["webpGeneratedDrafts"],
                      "g5Pass":g5["g5Pass"],"newG1Pass":0,
                      "officialAnswerVerifiedChange":0,"released":False},ensure_ascii=False))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    group=cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    args=cli.parse_args()
    run(args.stage)
