#!/usr/bin/env python3
"""Versioned repair of 7 detected 108 single-question DRAFT crop boundary defects.
Math16/17 determinant, 09-1 Q28/29 D option, 09-2 Q24/25 edge & Q28/29 D.
Old WebP v2 remains immutable and G1/G2/G3 gates remain unchanged.
"""
import argparse,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from stage_108_all_26_missing_original_page_webps import (
  PAGE,PAPER_BOX,at,sha,read,write,db_rebuild
)
from audit_105_115_sqlite_readonly import audit_year
BASE="sudu/data/processed/108/"
FIXES={
 ("00-MB",16):[90,1249,1310,1647],
 ("00-MB",17):[90,1648,1310,1825],
 ("09-1",28):[90,586,1310,795],
 ("09-1",29):[90,796,1310,980],
 ("09-2",24):[90,511,1310,612],
 ("09-2",28):[90,1381,1310,1595],
 ("09-2",29):[90,1596,1310,1810],
}
EVIDENCE=BASE+"qa-drafts/DRAFT_108_SEVEN_CROP_BOUNDARY_V3_20261024.json"
def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=Path(__file__).resolve().parents[1],text=True).strip()=="qa/114-115-official-visual-review"
    data={n:read(BASE+n) for n in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
              "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")}
    b=data["questions.json"];m=data["webp-manifest.json"];o=data["ocr-raw-candidates.json"]
    v=data["VISUAL_QA.json"];inv=data["inventory.json"];val=data["VALIDATION.json"]
    rel=data["release-manifest.json"]
    assert len(b["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==204 and inv["visualQaPass"]==v["passCount"]==0
    assert inv["answerOfficialFinalVerified"]==inv["ocrTextIndependentlyVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    mm={x["questionId"]:x for x in m["items"]}
    qs={x["questionId"]:x for x in b["questions"]}
    oo={x["questionId"]:x for x in o["items"]}
    vv={x["questionId"]:x for x in v["items"]}
    records=[]
    for (paper,n),box in FIXES.items():
        id=f"108-{paper}-{n:02d}"
        page,oldbox=PAPER_BOX[paper][n]
        source,blob,pdfsha=PAGE[(paper,page)]
        mitem=mm[id];q=qs[id]
        assert mitem["source"]==source and mitem["sourcePage"]==page
        assert mitem["cropPixels"]==oldbox and mitem["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        assert mitem["officialQuestionPdfSha256"]==pdfsha
        assert q["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        assert not q["questionVerified"] and not q["answerVerified"] and not q["integrationReady"]
        old_path=BASE+f"qa-drafts/webp-v2/{paper}/{id}.webp"
        assert mitem["output"]==old_path
        old=at(old_path).read_bytes()
        assert sha(old)==mitem["outputSha256"]
        raw=at(source).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==blob
        assert sha(raw)==mitem["sourcePageWebpSha256"]
        with Image.open(io.BytesIO(raw)) as pg:
            pg.load()
            assert pg.format=="WEBP" and pg.size==(1400,1980)
            crop=pg.crop(tuple(box))
            buf=io.BytesIO()
            crop.save(buf,"WEBP",lossless=True,method=6,exact=True)
            content=buf.getvalue()
            with Image.open(io.BytesIO(content)) as reread:
                reread.load()
                assert reread.size==crop.size
                assert ImageChops.difference(crop.convert("RGB"),reread.convert("RGB")).getbbox() is None
        out_path=BASE+f"qa-drafts/webp-v3/{paper}/{id}.webp"
        if at(out_path).exists():
            assert sha(at(out_path).read_bytes())==sha(content),"Versioned candidate changed"
        elif stage:
            at(out_path).parent.mkdir(parents=True,exist_ok=True)
            at(out_path).write_bytes(content)
        ev={"questionId":id,"paperCode":paper,"sourcePage":page,
            "officialPdfSha256":pdfsha,"sourcePageSha256":sha(raw),
            "oldCandidate":old_path,"oldPixels":oldbox,"oldSha256":sha(old),
            "newCandidate":out_path,"newPixels":box,"newSha256":sha(content),
            "qaStatus":"DRAFT_PENDING_DIRECT_VISUAL_G1"}
        records.append(ev)
        if stage:
            mitem.update({"cropPixels":box,"output":out_path,"outputSha256":sha(content),
                           "outputSize":[box[2]-box[0],box[3]-box[1]],
                           "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
                           "generationVersion":"assistant-source-pixel-boundary-refinement-v3-20261024"})
            mitem["issues"]=sorted(set(mitem.get("issues",[])+["PENDING_V3_BOUNDARY_DIRECT_VISUAL_G1"]))
            q["assets"].update({"singleQuestionWebp":out_path,"sha256":sha(content)})
            oo[id]["imageSha256"]=sha(content)
            vv[id].update({"candidateWebp":out_path,"candidateSha256":sha(content),
                           "status":"PENDING","reviewer":None,"visualEvidence":None})
    if not stage:
        print(json.dumps({"mode":"CHECK","revisionIds":[x["questionId"] for x in records],
            "newG1":0,"newG2":0,"noRelease":True}))
        return
    for n in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
              "VISUAL_QA.json","inventory.json","VALIDATION.json"):
        write(BASE+n,data[n])
    db_rebuild(b)
    reports=[audit_year(y) for y in range(105,116)]
    assert len(reports)==11 and all(r["g5Pass"] and r["sandboxImportPasses"]==2 for r in reports)
    g5="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    rd=read(g5);rd.update({"years":reports,"yearsG5Pass":11,"yearsReviewed":11,
                           "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(g5,rd)
    write(EVIDENCE,{"schemaVersion":1,"year":108,"revisions":records,"newG1":0,
                    "newG2":0,"newAnswerVerified":0,"g5Years":11,
                    "releaseAllowed":False,"integrationReady":False})
    print(json.dumps({"mode":"STAGED","revised":len(records),"G1":0,"G2":0,
                      "g5PassYears":11,"NO_RELEASE":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    run(p.parse_args().stage)
