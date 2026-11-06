#!/usr/bin/env python3
"""SHA-bound original source-page candidate crops for 107 English Q32-35.

The complete weather forecast and Chi Po-lin article are separately cropped as
shared material; no OCR, false visual QA PASS, official answer changes or release.
Coordinates are candidate only, directly located from existing original page 6.
"""
import argparse
import hashlib
import io
import json
import sqlite3
import tempfile
import os
import shutil
from pathlib import Path
from PIL import Image,ImageChops
from audit_105_115_sqlite_readonly import audit_year,canonical,digest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/107"
SRC="sudu/data/original/107/00-E/p006-6fa77b536c-v2-w1400-q66.webp"
GIT_BLOB_SHA="f87703a9bcf3d038f9da350e4fc41eae5cc73c47"
PDF_SHA="6fa77b536c5a991af6ad12f33427d362614109fad4f7d701ec25bc453dec7440"
CROPS={
 "107-00-E-32":[90,649,1310,739],
 "107-00-E-33":[90,745,1310,899],
 "107-00-E-34":[90,1483,1310,1696],
 "107-00-E-35":[90,1705,1310,1829],
 "107-00-E-SHARED-32-33":[90,256,1310,645],
 "107-00-E-SHARED-34-37":[90,916,1310,1476]
}
IDS=[f"107-00-E-{i:02d}" for i in (32,33,34,35)]
SHARED={"107-00-E-SHARED-32-33":[32,33],
        "107-00-E-SHARED-34-37":[34,35,36,37]}
EVIDENCE="sudu/data/processed/107/qa-drafts/DRAFT_107_E32_35_SHARED_P006_20261024.json"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def read(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))

def write(p,data):
    path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def file(rel):
    assert isinstance(rel,str) and rel.startswith("sudu/data/")
    result=(ROOT/rel).resolve()
    assert result.is_relative_to(ROOT.resolve())
    return result

def create_crops(stage):
    source=file(SRC).read_bytes()
    assert hashlib.sha1(b"blob "+str(len(source)).encode()+b"\x00"+source).hexdigest()==GIT_BLOB_SHA
    rows={}
    with Image.open(io.BytesIO(source)) as page:
        page.load()
        assert page.format=="WEBP" and page.width==1400 and 1900<page.height<2050
        for qid,box in CROPS.items():
            assert 0<=box[0]<box[2]<=page.width and 0<=box[1]<box[3]<=page.height
            crop=page.crop(tuple(box))
            buf=io.BytesIO()
            crop.save(buf,format="WEBP",lossless=True,method=6,exact=True)
            payload=buf.getvalue()
            with Image.open(io.BytesIO(payload)) as reread:
                reread.load()
                assert reread.size==crop.size
                assert ImageChops.difference(crop.convert("RGB"),reread.convert("RGB")).getbbox() is None
            kind="shared" if qid in SHARED else "00-E"
            output=f"sudu/data/processed/107/qa-drafts/webp-v2/{kind}/{qid}.webp"
            target=file(output)
            if target.exists():
                assert sha(target.read_bytes())==sha(payload), "Never overwrite changed crop"
            elif stage:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(payload)
            rows[qid]={
                "id":qid,"year":107,"paperCode":"00-E","sourcePage":6,
                "source":SRC,"sourcePageWebpSha256":sha(source),
                "officialQuestionPdfSha256":PDF_SHA,
                "cropPixels":box,"output":output,"outputSha256":sha(payload),
                "outputSize":[crop.width,crop.height],
                "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
                "issues":["REQUIRES_DIRECT_INDIVIDUAL_SOURCE_CROP_QA",
                          "SHARED_ARTICLE_OR_CHART_REQUIRES_INDEPENDENT_QA"]
            }
    return rows

def update_db(bank):
    dbfile=BASE/"question-bank.sqlite3"
    with tempfile.TemporaryDirectory(dir=BASE) as temp:
        dst=Path(temp)/"question-bank.sqlite3"
        shutil.copyfile(dbfile,dst)
        with sqlite3.connect(dst) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
            assert {"question_id","payload","payload_sha256"}<=cols
            for iteration in (1,2):
                for q in bank["questions"]:
                    payload=canonical(q)
                    cursor=db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                                      (payload,digest(payload.encode()),q["questionId"]))
                    assert cursor.rowcount==1
                for shared in bank["sharedMaterials"]:
                    db.execute("INSERT INTO shared_materials (material_id,payload) VALUES(?,?) "
                               "ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload",
                               (shared["sharedMaterialId"],canonical(shared)))
                db.commit()
                assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
                assert db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==2
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            indexed={q["questionId"]:q for q in bank["questions"]}
            for qid,payload,hsh in db.execute("SELECT question_id,payload,payload_sha256 FROM questions"):
                assert json.loads(payload)==indexed[qid] and digest(payload.encode())==hsh
        os.replace(dst,dbfile)

def run(stage):
    crops=create_crops(stage)
    m=read("sudu/data/processed/107/webp-manifest.json")
    bank=read("sudu/data/processed/107/questions.json")
    o=read("sudu/data/processed/107/ocr-raw-candidates.json")
    v=read("sudu/data/processed/107/VISUAL_QA.json")
    inv=read("sudu/data/processed/107/inventory.json")
    valid=read("sudu/data/processed/107/VALIDATION.json")
    rel=read("sudu/data/processed/107/release-manifest.json")
    assert len(m["items"])==len(bank["questions"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==185 and inv["visualQaPass"]==v["passCount"]==0
    assert inv["sourcePaperStats"]["00-E"]["imageDrafts"]==37
    assert not m["sharedMaterialCrops"] and not bank["sharedMaterials"]
    assert not inv["answerOfficialFinalVerified"] and not rel["releaseAllowed"]
    mmap={z["questionId"]:z for z in m["items"]}
    questions={z["questionId"]:z for z in bank["questions"]}
    ocr={z["questionId"]:z for z in o["items"]}
    visual={z["questionId"]:z for z in v["items"]}
    for qid in IDS:
        assert mmap[qid]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not mmap[qid].get("output") and not questions[qid]["assets"]["singleQuestionWebp"]
        assert visual[qid]["status"]=="BLOCKED"
        assert questions[qid]["questionVerified"] is False and questions[qid]["answerVerified"] is False
    if not stage:
        print(json.dumps({"mode":"check","missingQuestionIds":IDS,"sharedIds":list(SHARED),
                          "sourceGitBlobVerified":True,"newVisualQaPass":0,
                          "released":False}))
        return
    for qid in IDS:
        crop=crops[qid]
        mmap[qid].update(crop)
        questions[qid]["assets"].update({
            "singleQuestionWebp":crop["output"],"sourcePageWebp":SRC,
            "sha256":crop["outputSha256"],"sourcePage":6})
        questions[qid]["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        questions[qid]["issues"]=sorted(set(questions[qid].get("issues",[])+crop["issues"]))
        ocr[qid]["imageSha256"]=crop["outputSha256"]
        visual[qid].update({"status":"PENDING","sourcePage":6,"sourceWebp":SRC,
                            "candidateWebp":crop["output"],"candidateSha256":crop["outputSha256"],
                            "reviewer":None,"visualEvidence":None})
    for sid,nums in SHARED.items():
        e=crops[sid].copy()
        e.pop("id")
        e.update({"sharedMaterialId":sid,"originalQuestionNumbers":nums})
        m["sharedMaterialCrops"].append(e)
        bank["sharedMaterials"].append(e.copy())
        v["sharedMaterials"].append({"sharedMaterialId":sid,"sourcePage":6,"sourceWebp":SRC,
                                     "candidateWebp":e["output"],"candidateSha256":e["outputSha256"],
                                     "status":"PENDING","reviewer":None,"visualEvidence":None})
        for n in nums:
            qid=f"107-00-E-{n:02d}"
            assert not questions[qid]["sharedMaterialIds"]
            questions[qid]["sharedMaterialIds"]=[sid]
    inv["webpGeneratedDrafts"]=189
    inv["sourcePaperStats"]["00-E"]["imageDrafts"]=41
    inv["sourcePaperStats"]["00-E"]["manualCandidateRecoveredNumbers"]=[32,33,34,35]
    inv["sharedMaterialsReviewRequired"]=2
    inv["sharedMaterialsDrafts"]=2
    valid["sourceGaps"]["00-E"]["imageDrafts"]=41
    valid["sourceGaps"]["00-E"]["manualCandidateRecoveredNumbers"]=[32,33,34,35]
    assert inv["visualQaPass"]==0 and inv["answerOfficialFinalVerified"]==0
    for path,data in [
        ("sudu/data/processed/107/webp-manifest.json",m),
        ("sudu/data/processed/107/questions.json",bank),
        ("sudu/data/processed/107/ocr-raw-candidates.json",o),
        ("sudu/data/processed/107/VISUAL_QA.json",v),
        ("sudu/data/processed/107/inventory.json",inv),
        ("sudu/data/processed/107/VALIDATION.json",valid)
    ]:
        write(path,data)
    update_db(bank)
    after=audit_year(107)
    assert after["g5Pass"] and after["sandboxImportPasses"]==2 and after["onDiskRows"]==204
    statusfile="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    report=read(statusfile)
    report["years"]=[audit_year(y) for y in range(105,116)]
    assert all(s["g5Pass"] for s in report["years"]) and report["yearsG5Pass"]==11
    report["sourceDatabasesModified"]=True
    report["studentDataTouched"]=False
    report["released"]=False
    write(statusfile,report)
    write(EVIDENCE,{
        "year":107,"paperCode":"00-E","questionIds":IDS,
        "sharedMaterialIds":list(SHARED),
        "candidateCrops":crops,"sourcePage":6,
        "sourceGitBlob":GIT_BLOB_SHA,"officialQuestionPdfSha256":PDF_SHA,
        "originalPixelProvedByLosslessReread":True,
        "newVisualQaPass":0,"newOfficialAnswerVerified":0,
        "newOcrTextQaPass":0,"sqliteG5Passed":True,
        "integrationReady":False,"releaseAllowed":False
    })
    print(json.dumps({"mode":"staged","newWebpDrafts":4,"sharedMaterialDrafts":2,
                      "yearWebpDrafts":189,"G5":True,"newG1Pass":0,"released":False}))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    args=ap.parse_args()
    run(args.stage)
