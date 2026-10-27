#!/usr/bin/env python3
"""Record G1 only for 26 source-page directly visually reviewed 108 single question crops
and one complete accounting common-material crop. All source pixels rechecked,
all v2/v3/v4 SHA-bound. This is assistant, NOT independent human review.
Never promote any G2/G3/answerVerified/integrationReady or release.
"""
import hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from stage_108_all_26_missing_original_page_webps import (
  PAGE,IDS,SHARED_ID,at,sha,read,write,db_rebuild
)
from audit_105_115_sqlite_readonly import audit_year
BASE="sudu/data/processed/108/"
EVIDENCE=BASE+"qa-drafts/DIRECT_VISUAL_108_ALL_26_AND_ACCOUNTING_SHARED_20261024.json"
OBS={
 "00-MB":{11:"chicken egg probability",12:"rebounds fraction",13:"95 percent confidence interval",
          14:"parabola opening and intercept",15:"L1 L2 slopes and four fractions",
          16:"five colored segment diagram A-E and permutations",17:"two determinants and A-D"},
 "09-1":{15:"personnel annual performance assessment",16:"complete industrial radar chart A vs industry",
         17:"self-service washing machine patent and A-D",18:"intellectual property law and four choices",
         26:"PowerPoint print-page icons in all A-D images",27:"display connector formats",
         28:"natural-person digital certificate full D",29:"OSI network model four options",
         30:"HTML 1 row 2 column table and literal HTML choices",
         31:"Word tab stop symbols A-D",32:"SSL SET ecommerce four alternatives",
         33:"BIOS PC motherboard A-D"},
 "09-2":{23:"accounts receivable journal entry and all amounts",
         24:"asset exchange with commercial substance A-D, separate common data",
         25:"asset exchange without commercial substance A-D, separate common data",
         26:"production possibility curve full graph and 4 choices",
         27:"reserve deposit credit multiplier four choices",
         28:"elasticity and complete long D option",29:"supply-demand Qd Qs formulas A-D"}
}
def by(items,key):
    d={x[key]:x for x in items}
    assert len(d)==len(items)
    return d
def run():
    assert subprocess.check_output(["git","branch","--show-current"],cwd=Path(__file__).resolve().parents[1],text=True).strip()=="qa/114-115-official-visual-review"
    files={n:read(BASE+n) for n in ("questions.json","webp-manifest.json","VISUAL_QA.json",
         "inventory.json","VALIDATION.json","release-manifest.json")}
    b=files["questions.json"];m=files["webp-manifest.json"];v=files["VISUAL_QA.json"]
    inv=files["inventory.json"];val=files["VALIDATION.json"];rel=files["release-manifest.json"]
    assert len(b["questions"])==len(m["items"])==len(v["items"])==204
    assert len(m["sharedMaterialCrops"])==len(b["sharedMaterials"])==len(v["sharedMaterials"])==1
    assert inv["webpGeneratedDrafts"]==204 and inv["answerOfficialFinalVerified"]==0
    assert inv["ocrTextIndependentlyVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    im=by(m["items"],"questionId");qs=by(b["questions"],"questionId")
    vv=by(v["items"],"questionId")
    ms=m["sharedMaterialCrops"][0];bs=b["sharedMaterials"][0];vs=v["sharedMaterials"][0]
    assert ms["sharedMaterialId"]==bs["sharedMaterialId"]==vs["sharedMaterialId"]==SHARED_ID
    assert len(IDS)==26
    inspected=[]
    for id in list(IDS)+[SHARED_ID]:
        shared=(id==SHARED_ID)
        item=ms if shared else im[id]
        paper=item["paperCode"];page=item["sourcePage"]
        source,source_blob,pdfsha=PAGE[(paper,page)]
        assert item["source"]==source and item["officialQuestionPdfSha256"]==pdfsha
        assert item["sourceGitBlob"]==source_blob
        assert item["qaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
        assert "/qa-drafts/webp-v" in item["output"] and item["outputSize"][0]==1220
        raw=at(source).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==source_blob
        assert sha(raw)==item["sourcePageWebpSha256"]
        candidate=at(item["output"]).read_bytes()
        assert sha(candidate)==item["outputSha256"]
        with Image.open(io.BytesIO(raw)) as src,Image.open(io.BytesIO(candidate)) as cropped:
            src.load();cropped.load()
            assert src.size==(1400,1980) and cropped.size==tuple(item["outputSize"])
            assert ImageChops.difference(src.crop(tuple(item["cropPixels"])).convert("RGB"),cropped.convert("RGB")).getbbox() is None
        if shared:
            assert bs["qaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
            assert qs["108-09-2-24"]["sharedMaterialIds"]==[SHARED_ID]
            assert qs["108-09-2-25"]["sharedMaterialIds"]==[SHARED_ID]
            observation="Complete equipment-exchange shared passage including costs, useful life, carrying value, exchanged fair value and cash"
        else:
            q=qs[id]
            assert q["assets"]["sha256"]==item["outputSha256"]
            assert q["imageQaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
            assert not q["questionVerified"] and not q["answerVerified"] and not q["integrationReady"]
            _,n=IDS[id][0],int(id.split("-")[-1])
            observation=OBS[paper][n]
        inspected.append({"questionIdOrSharedId":id,"year":108,"paperCode":paper,
             "sourcePage":page,"originalQuestionPdfSha256FromRepository":pdfsha,
             "sourceOriginalPageWebp":source,"sourceOriginalPageSha256":sha(raw),
             "candidateWebp":item["output"],"candidateSha256":sha(candidate),
             "cropPixels":item["cropPixels"],
             "result":"PASS","observation":observation,"pixelDifferenceZero":True})
    if all(im[id]["qaStatus"]=="PASS" for id in IDS):
        assert ms["qaStatus"]=="PASS" and inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==26
        assert inv["sharedMaterialsVerified"]==1 and at(EVIDENCE).is_file()
        print(json.dumps({"mode":"IDEMPOTENT","G1":26,"shared":1,"NO_RELEASE":True}))
        return
    assert all(im[id]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA" for id in IDS)
    assert ms["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==0
    assert inv.get("sharedMaterialsVerified",0)==0
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    for item in inspected:
        id=item["questionIdOrSharedId"];shared=(id==SHARED_ID)
        row=ms if shared else im[id]
        proof={"reference":EVIDENCE,"reviewer":"ChatGPT assistant",
               "reviewedAt":now,"independentHumanReview":False,
               "sourceSha256":item["sourceOriginalPageSha256"],
               "reviewedSha256":item["candidateSha256"],
               "sourcePage":item["sourcePage"],"cropPixels":item["cropPixels"],
               "method":"assistant_direct_original_page_and_current_version_visual_check_and_zero_pixel_diff"}
        row["qaStatus"]="PASS"
        row["visualReviewEvidence"]=proof
        if shared:
            bs["qaStatus"]="PASS"
            bs["visualReviewEvidence"]=proof.copy()
            vs.update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EVIDENCE})
        else:
            qs[id]["imageQaStatus"]="PASS"
            vv[id].update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EVIDENCE})
    inv["visualQaPass"]=v["passCount"]=val["imageVisualQaPass"]=26
    inv["sharedMaterialsVerified"]=1
    rel["imageQA"]="PARTIAL_26_OF_204"
    certificate={"schemaVersion":1,"year":108,
        "reviewer":"ChatGPT assistant","independentHumanReview":False,"reviewedAt":now,
        "method":"Assistant directly visually inspected four distinct official-source page rasters against all current 26 individual and 1 shared original pixel crops, correcting seven v3 and four v4 cuts first",
        "officialPdfBytesReDownloadedForIndependentG0":False,
        "items":inspected,"newIndividualG1Pass":26,"newSharedMaterialG1Pass":1,
        "newTextQaPass":0,"newOfficialFinalAnswerVerified":0,
        "releaseAllowed":False,"integrationReady":False}
    for name in ("questions.json","webp-manifest.json","VISUAL_QA.json",
                 "inventory.json","VALIDATION.json","release-manifest.json"):
        write(BASE+name,files[name])
    write(EVIDENCE,certificate)
    db_rebuild(b)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audits)
    g5="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    report=read(g5)
    report.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                   "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(g5,report)
    print(json.dumps({"year":108,"newSingleWebpG1Pass":26,"newSharedG1Pass":1,
        "yearG1Pass":26,"yearTextVerified":0,"yearOfficialFinalAnswerVerified":0,
        "g5Years":11,"noRelease":True}))
if __name__=="__main__":run()
