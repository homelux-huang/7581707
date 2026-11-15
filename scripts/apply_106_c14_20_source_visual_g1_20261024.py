#!/usr/bin/env python3
"""Apply actual assistant source-page visual Q14-20 G1 with versioned WebPs.
Exact original bytes, per-version SHA/pixel/crop, seven independent single Qs,
three separate shared materials. Existing Q35-38 G1 untouched. Never promote
official final answers, OCR text G2, year release, or independent human QA.
"""
import hashlib
import io
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from link_106_c14_20_existing_webp_drafts import db_rebuild
from audit_105_115_sqlite_readonly import audit_year
from stage_106_chinese_14_20_v3_boundary_previews import (
    ROOT,at,sha,read,YEAR_DIR,SOURCE,SOURCE_SHA,SOURCE_BLOB
)
QNUMS=range(14,21)
SID=("106-00-C-SHARED-15-16","106-00-C-SHARED-17-18","106-00-C-SHARED-19-20")
EVIDENCE=YEAR_DIR+"qa-drafts/DIRECT_VISUAL_106_C14_20_AND_THREE_SHARED_20261024.json"
OBS={
 "106-00-C-14":"Original poem and song bubbles, all A-D and full stem; v3 avoids shared 15-16 paragraph",
 "106-00-C-15":"Full conditional grammar Q15 plus A-D; v4 excludes next Q16 heading",
 "106-00-C-16":"Complete 馮諼 reading question and four alternatives; v4 excludes next reading prompt",
 "106-00-C-17":"Complete Q17 heading, stem, A-D; v4 no Q18 head, shared 17-18 separated",
 "106-00-C-18":"Full Q18 omitted-subject grammar stem and all four underlined literary alternatives; no next 19-20 prompt",
 "106-00-C-19":"Full shark information Q19 number, stem and four choices in left-only v4; right-side diagram is shared",
 "106-00-C-20":"Full shark advocacy Q20 number, two stem lines and A-D in left-only v4; right-side shared diagram separately linked",
 "106-00-C-SHARED-15-16":"Complete 孟嘗君 paragraph and 15-16 prompt; original v2 valid unchanged",
 "106-00-C-SHARED-17-18":"Complete 聚芳園記 text with heading and end citation + footnote; v4 stops before question 17",
 "106-00-C-SHARED-19-20":"Complete right-hand shark infographic, framed text, counts and both panels; top extended to original drawing"
}
BATCH={f"106-00-C-{n:02d}" for n in QNUMS}|set(SID)
def canon(rows,key):
    v={x[key]:x for x in rows}
    assert len(v)==len(rows)
    return v
def verify_source_crop(row,page,src):
    assert row["source"]==SOURCE and row["sourcePage"]==4
    assert row["sourcePageWebpSha256"]==SOURCE_SHA
    old_path=at(row["output"])
    old_bytes=old_path.read_bytes()
    assert sha(old_bytes)==row["outputSha256"]
    x1,y1,x2,y2=row["cropPixels"]
    assert 0<=x1<x2<=page.width and 0<=y1<y2<=page.height
    with Image.open(io.BytesIO(old_bytes)) as im:
        im.load()
        assert im.format=="WEBP"
        assert im.size==(x2-x1,y2-y1)
        assert ImageChops.difference(page.crop((x1,y1,x2,y2)).convert("RGB"),im.convert("RGB")).getbbox() is None
    return sha(old_bytes)

def run():
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    assert branch=="qa/114-115-official-visual-review",branch
    data={name:read(YEAR_DIR+name) for name in [
        "webp-manifest.json","questions.json","ocr-raw-candidates.json",
        "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json"]}
    manifest=data["webp-manifest.json"];bank=data["questions.json"]
    ocr=data["ocr-raw-candidates.json"];visual=data["VISUAL_QA.json"]
    inv=data["inventory.json"];valid=data["VALIDATION.json"];rel=data["release-manifest.json"]
    assert len(manifest["items"])==len(bank["questions"])==len(ocr["items"])==len(visual["items"])==204
    assert inv["visualQaPass"]==visual["passCount"]==valid["imageVisualQaPass"]==16
    assert inv["ocrTextIndependentlyVerified"]==valid["ocrTextVerified"]==10
    assert inv["answerOfficialFinalVerified"]==valid["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not valid["releaseAllowed"] and not valid["integrationReady"]
    mi=canon(manifest["items"],"questionId")
    qi=canon(bank["questions"],"questionId")
    oi=canon(ocr["items"],"questionId")
    vi=canon(visual["items"],"questionId")
    ms=canon(manifest["sharedMaterialCrops"],"sharedMaterialId")
    bs=canon(bank["sharedMaterials"],"sharedMaterialId")
    vs=canon(visual["sharedMaterials"],"sharedMaterialId")
    assert len(ms)==len(bs)==len(vs)==4
    assert inv["sharedMaterialsVerified"]==1
    v3=canon(read(YEAR_DIR+"qa-drafts/DRAFT_106_C14_20_V3_BOUNDARY_PREVIEWS_20261024.json")["items"],"questionIdOrSharedId")
    v4=canon(read(YEAR_DIR+"qa-drafts/DRAFT_106_C14_20_V4_SECOND_PASS_20261024.json")["items"],"questionIdOrSharedId")
    v5=read(YEAR_DIR+"qa-drafts/DRAFT_106_C19_20_SHARED_V5_TOP_BOUNDARY_20261024.json")
    expected={}
    for n in QNUMS:
        id=f"106-00-C-{n:02d}"
        r=v4[id] if id in v4 else v3[id]
        expected[id]=(r["newPath"],r.get("newCropPixels",r.get("newPixels")),r["newSha256"])
    expected[SID[0]]=(ms[SID[0]]["output"],ms[SID[0]]["cropPixels"],ms[SID[0]]["outputSha256"])
    expected[SID[1]]=(v4[SID[1]]["newPath"],v4[SID[1]]["newCropPixels"],v4[SID[1]]["newSha256"])
    expected[SID[2]]=(v5["newV5"],v5["newCropPixels"],v5["newV5Sha256"])
    assert set(expected)==BATCH
    source=at(SOURCE).read_bytes()
    assert sha(source)==SOURCE_SHA
    assert hashlib.sha1(b"blob "+str(len(source)).encode()+b"\x00"+source).hexdigest()==SOURCE_BLOB
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    records=[]
    with Image.open(io.BytesIO(source)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for id,(path,pixels,digest) in expected.items():
            old=ms[id] if id in ms else mi[id]
            assert old["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
            old_sha=verify_source_crop(old,page,source)
            assert old_sha==old["outputSha256"]
            new_bytes=at(path).read_bytes()
            assert sha(new_bytes)==digest
            x1,y1,x2,y2=pixels
            with Image.open(io.BytesIO(new_bytes)) as im:
                im.load()
                assert im.format=="WEBP" and im.size==(x2-x1,y2-y1)
                assert ImageChops.difference(page.crop((x1,y1,x2,y2)).convert("RGB"),im.convert("RGB")).getbbox() is None
            if id in qi:
                q=qi[id]
                assert q["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
                assert not q["questionVerified"] and not q["answerVerified"] and not q["integrationReady"]
                assert q["assets"]["sha256"]==old_sha
                assert oi[id]["imageSha256"]==old_sha
                assert vi[id]["status"]=="PENDING"
                assert not vi[id]["reviewer"] and not vi[id]["visualEvidence"]
            else:
                assert vs[id]["status"]=="PENDING"
                assert not vs[id]["reviewer"]
                assert bs[id]["outputSha256"]==old_sha
            records.append({"questionIdOrSharedId":id,"sourcePage":4,
                "originalPdfSha256FromRepository":mi["106-00-C-14"]["officialQuestionPdfSha256"],
                "sourceWebp":SOURCE,"sourceSha256":SOURCE_SHA,
                "oldVersion":old["output"],"oldSha256":old_sha,
                "oldCropPixels":old["cropPixels"],
                "reviewedVersion":path,"reviewedSha256":digest,
                "cropPixels":pixels,"sourcePixelDifferenceZero":True,
                "visualObservation":OBS[id],"result":"PASS"})
    for row in records:
        id=row["questionIdOrSharedId"]
        shared=id in ms
        obj=ms[id] if shared else mi[id]
        box=row["cropPixels"]
        sha_new=row["reviewedSha256"]
        out_path=row["reviewedVersion"]
        method="assistant-direct-source-page4-and-versioned-question-only-visual"
        proof={"reference":EVIDENCE,"reviewedSha256":sha_new,
            "sourceSha256":SOURCE_SHA,"sourcePage":4,"cropPixels":box,
            "reviewer":"ChatGPT assistant","independentHumanReview":False,
            "reviewedAt":now,"method":method}
        obj.update({"output":out_path,"outputSha256":sha_new,"cropPixels":box,
                    "outputSize":[box[2]-box[0],box[3]-box[1]],
                    "generationVersion":"source-pixel-reviewed-version-"+out_path.split("/webp-")[-1].split("/")[0],
                    "qaStatus":"PASS","visualReviewEvidence":proof})
        obj["issues"]=sorted(set(obj.get("issues",[])+["V2_BOUNDARY_DEFECT_REPAIRED_AND_REVIEWED"]))
        if shared:
            bs[id].update(obj.copy())
            vs[id].update({"candidateWebp":out_path,"candidateSha256":sha_new,
                           "status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EVIDENCE})
        else:
            qi[id]["assets"].update({"singleQuestionWebp":out_path,"sha256":sha_new,"sourcePage":4})
            qi[id]["imageQaStatus"]="PASS"
            vi[id].update({"candidateWebp":out_path,"candidateSha256":sha_new,
                           "status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EVIDENCE})
            oi[id]["imageSha256"]=sha_new
    inv["visualQaPass"]=visual["passCount"]=valid["imageVisualQaPass"]=23
    inv["sharedMaterialsVerified"]=4
    rel["imageQA"]="PARTIAL_23_OF_204"
    rel["sharedMaterialQA"]="IMAGE_G1_PASS_4_OF_4_ASSISTANT"
    proof={"schemaVersion":1,"reviewedAt":now,"reviewer":"ChatGPT assistant",
        "independentHumanReview":False,"year":106,"paperCode":"00-C",
        "sourcePage":4,"originalPageImageSha256":SOURCE_SHA,"originalPageBlob":SOURCE_BLOB,
        "officialPdfShaFromExistingRepoOnly":True,
        "method":"Actual visual comparison of full official raster P4 with all seven v3/v4 individual crops and three distinct shared passages/artwork, plus zero-difference Pillow source pixel checks",
        "items":records,"newIndividualG1Pass":7,"newSharedG1Pass":3,
        "newTextG2Pass":0,"newOfficialFinalAnswersVerified":0,
        "releaseAllowed":False,"integrationReady":False}
    for name in ("webp-manifest.json","questions.json","ocr-raw-candidates.json","VISUAL_QA.json",
                 "inventory.json","VALIDATION.json","release-manifest.json"):
        at(YEAR_DIR+name).write_text(json.dumps(data[name],ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    at(EVIDENCE).write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    db_rebuild(bank)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(a["g5Pass"] and a["sandboxImportPasses"]==2 for a in audits)
    g5="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    current=read(g5)
    current.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                    "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    at(g5).write_text(json.dumps(current,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"year":106,"newIndividualG1":7,"newSharedG1":3,
         "yearG1":23,"sharedG1":4,"yearG2Unchanged":10,
         "officialFinalVerifiedAdded":0,"G5":11,"NO_RELEASE":True}))
if __name__=="__main__":run()
