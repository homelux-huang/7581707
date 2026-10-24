#!/usr/bin/env python3
"""Versioned refinement of six DRAFT 107 Chinese crops after first visual inspection.
Fix Q13 missing D, Q14 mixed Q13 D, Q15 shared-footnote edge, Q16 next-heading
edge, Q37 Q38-edge, and shared 15-16 clipped footnote. Preserve previous v3 bytes.
Keep new v4 candidates at DRAFT, G1/G2/G3 unchanged, NO RELEASE.
"""
import argparse,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from stage_107_c08_16_c35_38_original_page_crops import (
    PAGE,CROPS,SHARED,at,sha,read,write,update_db
)
from audit_105_115_sqlite_readonly import audit_year
ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/107/"
REFINE={
 "107-00-C-13":[90,499,1310,648],
 "107-00-C-14":[90,649,1310,1137],
 "107-00-C-15":[90,1298,1310,1359],
 "107-00-C-16":[90,1359,1310,1510],
 "107-00-C-37":[90,1093,1310,1186],
 "107-00-C-SHARED-15-16":[90,1140,1310,1297],
}
REPORT=BASE+"qa-drafts/DRAFT_107_CHINESE_V4_BOUNDARY_REFINEMENT_20261024.json"
def main(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    data={k:read(BASE+k) for k in ("webp-manifest.json","questions.json","ocr-raw-candidates.json",
                                    "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")}
    m=data["webp-manifest.json"];b=data["questions.json"];o=data["ocr-raw-candidates.json"]
    v=data["VISUAL_QA.json"];inv=data["inventory.json"];val=data["VALIDATION.json"]
    rel=data["release-manifest.json"]
    assert len(m["items"])==len(b["questions"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==204 and inv["visualQaPass"]==v["passCount"]==6
    assert inv["ocrTextIndependentlyVerified"]==5 and inv["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    mm={z["questionId"]:z for z in m["items"]}
    qs={z["questionId"]:z for z in b["questions"]}
    oo={z["questionId"]:z for z in o["items"]}
    vv={z["questionId"]:z for z in v["items"]}
    ss={z["sharedMaterialId"]:z for z in m["sharedMaterialCrops"]}
    bs={z["sharedMaterialId"]:z for z in b["sharedMaterials"]}
    vs={z["sharedMaterialId"]:z for z in v["sharedMaterials"]}
    assert len(ss)==len(bs)==len(vs)==5
    records={}
    for id,box in REFINE.items():
        isshared=id in SHARED
        item=ss[id] if isshared else mm[id]
        assert item["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        pn=CROPS[id][0]
        source,blob=PAGE[pn]
        assert item["sourcePage"]==pn and item["source"]==source
        raw=at(source).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==blob
        assert item["sourcePageWebpSha256"]==sha(raw)
        old_path=f"sudu/data/processed/107/qa-drafts/webp-v3/{'shared' if isshared else '00-C'}/{id}.webp"
        assert item["output"]==old_path and item["cropPixels"]==CROPS[id][1]
        old=at(old_path).read_bytes()
        assert sha(old)==item["outputSha256"]
        with Image.open(io.BytesIO(raw)) as original:
            original.load()
            assert original.size==(1400,1980)
            crop=original.crop(tuple(box))
            buff=io.BytesIO()
            crop.save(buff,"WEBP",lossless=True,method=6,exact=True)
            image=buff.getvalue()
            with Image.open(io.BytesIO(image)) as check:
                check.load()
                assert check.size==crop.size
                assert ImageChops.difference(crop.convert("RGB"),check.convert("RGB")).getbbox() is None
        new_path=f"sudu/data/processed/107/qa-drafts/webp-v4/{'shared' if isshared else '00-C'}/{id}.webp"
        if at(new_path).exists():
            assert sha(at(new_path).read_bytes())==sha(image),"Never overwrite divergent newer crop"
        elif stage:
            at(new_path).parent.mkdir(parents=True,exist_ok=True)
            at(new_path).write_bytes(image)
        record={"id":id,"sourcePage":pn,"sourcePageSha256":sha(raw),"officialPdfSha256":item["officialQuestionPdfSha256"],
            "oldCropPath":old_path,"oldCropPixels":item["cropPixels"],"oldSha256":sha(old),
            "newCropPath":new_path,"newCropPixels":box,"newSha256":sha(image),
            "visualQaStatus":"DRAFT_PENDING_SECOND_DIRECT_REVIEW"}
        records[id]=record
        if stage:
            item.update({"cropPixels":box,"output":new_path,"outputSha256":sha(image),
                         "outputSize":[box[2]-box[0],box[3]-box[1]],
                         "generationVersion":"assistant-original-pixel-refinement-v4-20261024",
                         "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA"})
            item["issues"]=sorted(set(item.get("issues",[])+["PENDING_SECOND_INDEPENDENT_IMAGE_BOUNDARY_REVIEW"]))
            if isshared:
                bs[id].update(item.copy())
                vs[id].update({"candidateWebp":new_path,"candidateSha256":sha(image),
                               "status":"PENDING","reviewer":None,"visualEvidence":None})
            else:
                qs[id]["assets"].update({"singleQuestionWebp":new_path,"sha256":sha(image),"sourcePage":pn})
                assert qs[id]["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
                oo[id]["imageSha256"]=sha(image)
                vv[id].update({"candidateWebp":new_path,"candidateSha256":sha(image),
                               "status":"PENDING","reviewer":None,"visualEvidence":None})
    if not stage:
        print(json.dumps({"mode":"CHECK","refinedIds":list(REFINE),"existingG1Unchanged":6,
                          "released":False}))
        return
    for name in ("webp-manifest.json","questions.json","ocr-raw-candidates.json",
                 "VISUAL_QA.json","inventory.json","VALIDATION.json"):
        write(BASE+name,data[name])
    update_db(b)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audits)
    agg="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    rep=read(agg);rep.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                              "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(agg,rep)
    write(REPORT,{"schemaVersion":1,"year":107,"paperCode":"00-C","cropRefinements":records,
          "newG1Pass":0,"newG2Pass":0,"newG3Pass":0,"g5Years":11,
          "releaseAllowed":False,"integrationReady":False})
    print(json.dumps({"mode":"STAGED","refinedImages":len(REFINE),"G1":6,
                      "G5":11,"NO_RELEASE":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    main(p.parse_args().stage)
