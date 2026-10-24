#!/usr/bin/env python3
"""Stage two missing original-pixel 107 09-1 Q49/50 WebPs from pinned TCTE page 8.
They remain independent-image G1 DRAFT until direct visual crop review.
Do not regenerate existing WebPs, fabricate OCR or alter official answers/release.
"""
import argparse,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
from stage_107_e32_35_source_pixel_crops import update_db
from audit_105_115_sqlite_readonly import audit_year

ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/107/"
SRC="sudu/data/original/107/09-1/p008-8e8d72b201-v2-w1400-q66.webp"
SRC_BLOB="25d1ec2105a71286828f52d1d6af2dd6720f7424"
PDF_SHA="8e8d72b2016553f29184fd3795dab4a6f4ed0bc57e9cb861c9ce2ccf5b0bc2db"
CROPS={
  "107-09-1-49":[90,169,1310,548],
  "107-09-1-50":[90,554,1310,944],
}
REPORT=BASE+"qa-drafts/DRAFT_107_09_1_Q49_50_P008_20261024.json"

def at(p):
    z=(ROOT/p).resolve()
    assert z.is_relative_to(ROOT.resolve())
    return z
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(at(p).read_text(encoding="utf8"))
def write(p,info):
    dest=at(p);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def indexed(rows):
    z={r["questionId"]:r for r in rows};assert len(z)==len(rows)
    return z
def source_crops(stage):
    raw=at(SRC).read_bytes()
    gitblob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert gitblob==SRC_BLOB
    outputs={}
    with Image.open(io.BytesIO(raw)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for id,box in CROPS.items():
            assert box[0]>=0 and box[2]<=page.width and box[3]<=page.height
            portion=page.crop(tuple(box))
            buf=io.BytesIO()
            portion.save(buf,"WEBP",lossless=True,method=6,exact=True)
            content=buf.getvalue()
            with Image.open(io.BytesIO(content)) as check:
                check.load()
                assert check.size==portion.size
                assert ImageChops.difference(portion.convert("RGB"),check.convert("RGB")).getbbox() is None
            path=BASE+"qa-drafts/webp-v3/09-1/"+id+".webp"
            if at(path).exists():
                assert sha(at(path).read_bytes())==sha(content),"Existing crop version changed"
            elif stage:
                at(path).parent.mkdir(parents=True,exist_ok=True)
                at(path).write_bytes(content)
            outputs[id]={"id":id,"year":107,"paperCode":"09-1",
              "sourcePage":8,"source":SRC,"sourcePageWebpSha256":sha(raw),
              "officialQuestionPdfSha256":PDF_SHA,"cropPixels":box,
              "output":path,"outputSha256":sha(content),
              "outputSize":[box[2]-box[0],box[3]-box[1]],
              "generationVersion":"manual-source-pixel-candidate-v3-p008",
              "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
              "issues":["REQUIRES_INDIVIDUAL_DIRECT_SOURCE_CROP_G1"]}
    return outputs

def run(stage):
    candidate=source_crops(stage)
    files={name:read(BASE+name) for name in (
        "questions.json","webp-manifest.json","ocr-raw-candidates.json",
        "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")}
    bank=files["questions.json"];m=files["webp-manifest.json"]
    o=files["ocr-raw-candidates.json"];v=files["VISUAL_QA.json"]
    inv=files["inventory.json"];val=files["VALIDATION.json"]
    rel=files["release-manifest.json"]
    assert len(bank["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==189 and inv["visualQaPass"]==v["passCount"]==4
    assert inv["ocrTextIndependentlyVerified"]==4 and inv["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    questions=indexed(bank["questions"]);img=indexed(m["items"])
    ocr=indexed(o["items"]);vis=indexed(v["items"])
    for id,c in candidate.items():
        assert img[id]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not img[id].get("output") and not questions[id]["assets"]["singleQuestionWebp"]
        assert vis[id]["status"]=="BLOCKED"
        assert not questions[id]["questionVerified"] and not questions[id]["answerVerified"] and not questions[id]["integrationReady"]
        assert img[id]["officialQuestionPdfSha256"]==PDF_SHA
    if not stage:
        print(json.dumps({"mode":"CHECK","newCandidates":list(candidate),
          "sourcePageBlobVerified":True,"G1Added":0,"released":False}))
        return
    for id,c in candidate.items():
        img[id].update(c)
        question=questions[id]
        question["assets"].update({"singleQuestionWebp":c["output"],
          "sourcePageWebp":SRC,"sha256":c["outputSha256"],"sourcePage":8})
        question["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        question["issues"]=sorted(set(question.get("issues",[])+c["issues"]))
        ocr[id]["imageSha256"]=c["outputSha256"]
        vis[id].update({"status":"PENDING","sourcePage":8,
          "sourceWebp":SRC,"candidateWebp":c["output"],
          "candidateSha256":c["outputSha256"],"reviewer":None,"visualEvidence":None})
    inv["webpGeneratedDrafts"]=191
    inv["sourcePaperStats"]["09-1"]["imageDrafts"]=50
    inv["sourcePaperStats"]["09-1"]["manualCandidateRecoveredNumbers"]=[49,50]
    val["sourceGaps"]["09-1"]["imageDrafts"]=50
    val["sourceGaps"]["09-1"]["manualCandidateRecoveredNumbers"]=[49,50]
    for name in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
                 "VISUAL_QA.json","inventory.json","VALIDATION.json"):
        write(BASE+name,files[name])
    update_db(bank)
    checks=[audit_year(y) for y in range(105,116)]
    assert len(checks)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in checks)
    aggregate="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    r=read(aggregate);r["years"]=checks;r["yearsG5Pass"]=11
    r["sourceDatabasesModified"]=True;r["studentDataTouched"]=False;r["released"]=False
    write(aggregate,r)
    write(REPORT,{"schemaVersion":1,"year":107,"paperCode":"09-1","sourcePage":8,
      "officialPdfSha256":PDF_SHA,"sourceWebp":SRC,"sourceGitBlob":SRC_BLOB,
      "candidateCrops":candidate,"newWebpDrafts":2,"newG1Pass":0,
      "newTextQA":0,"newFinalOfficialAnswerVerified":0,"sqliteG5Years":11,
      "releaseAllowed":False,"integrationReady":False,
      "note":"Page 8 contains Q49 Visual Basic and Q50 HTML table visual options; only separate original-pixel candidates are staged. Require actual QA before PASS."})
    print(json.dumps({"mode":"STAGED","addedDraftIds":list(candidate),
       "year107WebpDrafts":191,"newG1Pass":0,"g5Years":11,
       "releaseAllowed":False},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    a=p.parse_args()
    run(a.stage)
