#!/usr/bin/env python3
"""Stage only 108's 26 missing Q WebPs from four official-page source rasters.
One Q24/25 common accounting material is independent and SHA-bound.
Every new image is DRAFT pending individual direct G1; no verified OCR, final answer, release.
"""
import argparse,hashlib,io,json,sqlite3,tempfile,shutil,os,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_105_115_sqlite_readonly import audit_year,canonical,digest

ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/108/"
PAGE={
 ("00-MB",3):("sudu/data/original/108/00-MB/p003-bcda540c72-v2-w1400-q66.webp",
              "98769b8e7b656bde3abd55264667ef60c876ec7d","bcda540c72f5d88f400aed994d58496e66761466aa5438e54d156c773b25722c"),
 ("09-1",4):("sudu/data/original/108/09-1/p004-3556f26b5a-v2-w1400-q66.webp",
             "a964cce80773785d57c5f6d189c13b114135e795","3556f26b5a84a3209ffe7d2dea638586fc717417a5618c2742739f8388dd12e3"),
 ("09-1",6):("sudu/data/original/108/09-1/p006-3556f26b5a-v2-w1400-q66.webp",
             "a5150b1fa1fa7e3e8e92406929d45d4f16270739","3556f26b5a84a3209ffe7d2dea638586fc717417a5618c2742739f8388dd12e3"),
 ("09-2",5):("sudu/data/original/108/09-2/p005-bc374a3459-v2-w1400-q66.webp",
             "21a8df7fdf5a7d3b02816f3add6d1cad8ada0808","bc374a3459c00327cc893560f39a696b589fa44be4c4c3e98d92f942aa3f9f6a"),
}
PAPER_BOX={
 "00-MB":{11:(3,[90,169,1310,351]),12:(3,[90,352,1310,524]),
          13:(3,[90,525,1310,918]),14:(3,[90,919,1310,1060]),
          15:(3,[90,1061,1310,1248]),16:(3,[90,1249,1310,1667]),
          17:(3,[90,1668,1310,1825])},
 "09-1":{15:(4,[90,163,1310,546]),16:(4,[90,547,1310,1129]),
         17:(4,[90,1130,1310,1450]),18:(4,[90,1451,1310,1782]),
         26:(6,[90,220,1310,497]),27:(6,[90,498,1310,585]),
         28:(6,[90,586,1310,747]),29:(6,[90,748,1310,980]),
         30:(6,[90,981,1310,1208]),31:(6,[90,1209,1310,1435]),
         32:(6,[90,1436,1310,1637]),33:(6,[90,1638,1310,1785])},
 "09-2":{23:(5,[90,170,1310,359]),24:(5,[90,511,1310,619]),
         25:(5,[90,620,1310,690]),26:(5,[90,737,1310,1134]),
         27:(5,[90,1135,1310,1380]),28:(5,[90,1381,1310,1567]),
         29:(5,[90,1568,1310,1810])},
}
SHARED_ID="108-09-2-SHARED-24-25"
SHARED_BOX=(5,[90,366,1310,510])
IDS={f"108-{paper}-{num:02d}":(paper,page,box) for paper,specs in PAPER_BOX.items() for num,(page,box) in specs.items()}
CROPS={**IDS,SHARED_ID:("09-2",*SHARED_BOX)}
REPORT=BASE+"qa-drafts/DRAFT_108_26_MISSING_AND_ACCOUNTING_SHARED_20261024.json"
def at(rel):
    p=(ROOT/rel).resolve()
    assert p.is_relative_to(ROOT.resolve())
    return p
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(at(p).read_text(encoding="utf8"))
def write(p,obj):
    f=at(p);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def by(rows,key):
    z={x[key]:x for x in rows}
    assert len(z)==len(rows)
    return z
def source_images(stage):
    rows={}
    for (paper,page),(source,blob,pdfsha) in PAGE.items():
        raw=at(source).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==blob
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            assert img.format=="WEBP" and img.size==(1400,1980)
            for id,(subject,number,box) in CROPS.items():
                if subject!=paper or number!=page:continue
                assert 0<=box[0]<box[2]<=img.width and 0<=box[1]<box[3]<=img.height
                crop=img.crop(tuple(box))
                buf=io.BytesIO()
                crop.save(buf,format="WEBP",lossless=True,method=6,exact=True)
                content=buf.getvalue()
                with Image.open(io.BytesIO(content)) as out:
                    out.load()
                    assert out.size==crop.size
                    assert ImageChops.difference(crop.convert("RGB"),out.convert("RGB")).getbbox() is None
                folder="shared" if id==SHARED_ID else paper
                path=f"{BASE}qa-drafts/webp-v2/{folder}/{id}.webp"
                if at(path).exists():
                    assert sha(at(path).read_bytes())==sha(content),"Changed existing candidate: stop"
                elif stage:
                    at(path).parent.mkdir(parents=True,exist_ok=True)
                    at(path).write_bytes(content)
                rows[id]={"id":id,"year":108,"paperCode":paper,"sourcePage":page,
                    "source":source,"sourceGitBlob":blob,
                    "sourcePageWebpSha256":sha(raw),"officialQuestionPdfSha256":pdfsha,
                    "cropPixels":box,"output":path,"outputSha256":sha(content),
                    "outputSize":[crop.width,crop.height],
                    "generationVersion":"assistant-original-page-pixel-only-v2-20261024",
                    "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
                    "issues":["DRAFT_NEEDS_INDEPENDENT_G1_VISUAL_REVIEW"]}
    assert set(rows)==set(CROPS)
    return rows
def db_rebuild(bank):
    src=at(BASE+"question-bank.sqlite3")
    with tempfile.TemporaryDirectory(dir=src.parent) as td:
        temp=Path(td)/"question-bank.sqlite3"
        shutil.copyfile(src,temp)
        with sqlite3.connect(temp) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
            assert {"question_id","payload","payload_sha256"}<=cols
            for i in (1,2):
                for q in bank["questions"]:
                    payload=canonical(q)
                    c=db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                                 (payload,digest(payload.encode("utf8")),q["questionId"]))
                    assert c.rowcount==1
                for shared in bank["sharedMaterials"]:
                    db.execute("INSERT INTO shared_materials(material_id,payload) VALUES(?,?) "
                               "ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload",
                               (shared["sharedMaterialId"],canonical(shared)))
                db.commit()
                assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
                assert db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==len(bank["sharedMaterials"])
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            expected={q["questionId"]:q for q in bank["questions"]}
            for id,raw,hsh in db.execute("SELECT question_id,payload,payload_sha256 FROM questions"):
                assert json.loads(raw)==expected[id] and digest(raw.encode("utf8"))==hsh
        os.replace(temp,src)
def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    images=source_images(stage)
    data={name:read(BASE+name) for name in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
            "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")}
    b=data["questions.json"];m=data["webp-manifest.json"];o=data["ocr-raw-candidates.json"]
    v=data["VISUAL_QA.json"];inv=data["inventory.json"];val=data["VALIDATION.json"]
    rel=data["release-manifest.json"]
    assert len(b["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==178 and inv["visualQaPass"]==v["passCount"]==0
    assert inv["answerOfficialFinalVerified"]==0 and inv["ocrTextIndependentlyVerified"]==0
    assert not m["sharedMaterialCrops"] and not b["sharedMaterials"] and not v["sharedMaterials"]
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    q=by(b["questions"],"questionId");mm=by(m["items"],"questionId")
    oo=by(o["items"],"questionId");vv=by(v["items"],"questionId")
    assert len(IDS)==26 and len(images)==27
    for id,(paper,page,box) in IDS.items():
        assert mm[id]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not mm[id].get("output") and not q[id]["assets"].get("singleQuestionWebp")
        assert vv[id]["status"]=="BLOCKED"
        assert mm[id]["officialQuestionPdfSha256"]==images[id]["officialQuestionPdfSha256"]
        assert not q[id]["questionVerified"] and not q[id]["answerVerified"] and not q[id]["integrationReady"]
    if not stage:
        print(json.dumps({"mode":"CHECK","missingIds":sorted(IDS),
         "newSharedId":SHARED_ID,"sourcePages":len(PAGE),
         "newVisualQaPass":0,"noRelease":True},ensure_ascii=False))
        return
    for id,(paper,page,box) in IDS.items():
        crop=images[id]
        mm[id].update(crop)
        q[id]["assets"].update({"singleQuestionWebp":crop["output"],
            "sourcePageWebp":crop["source"],"sha256":crop["outputSha256"],"sourcePage":page})
        q[id]["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        q[id]["issues"]=sorted(set(q[id].get("issues",[])+crop["issues"]))
        oo[id]["imageSha256"]=crop["outputSha256"]
        vv[id].update({"status":"PENDING","sourcePage":page,"sourceWebp":crop["source"],
                        "candidateWebp":crop["output"],"candidateSha256":crop["outputSha256"],
                        "reviewer":None,"visualEvidence":None})
    shared=images[SHARED_ID].copy();shared.pop("id")
    shared.update({"sharedMaterialId":SHARED_ID,"originalQuestionNumbers":[24,25]})
    m["sharedMaterialCrops"].append(shared)
    b["sharedMaterials"].append(shared.copy())
    v["sharedMaterials"].append({"sharedMaterialId":SHARED_ID,
        "sourcePage":5,"sourceWebp":shared["source"],
        "candidateWebp":shared["output"],"candidateSha256":shared["outputSha256"],
        "status":"PENDING","reviewer":None,"visualEvidence":None})
    for n in (24,25):q[f"108-09-2-{n:02d}"]["sharedMaterialIds"]=[SHARED_ID]
    inv["webpGeneratedDrafts"]=204
    for paper,ns in PAPER_BOX.items():
        inv["sourcePaperStats"][paper]["imageDrafts"]=len([x for x in b["questions"] if x["paperCode"]==paper])
        inv["sourcePaperStats"][paper]["manualCandidateRecoveredNumbers"]=sorted(ns)
        val["sourceGaps"][paper]["imageDrafts"]=inv["sourcePaperStats"][paper]["imageDrafts"]
        val["sourceGaps"][paper]["manualCandidateRecoveredNumbers"]=sorted(ns)
    inv["sharedMaterialsDrafts"]=1
    inv["sharedMaterialsReviewRequired"]=1
    assert inv["answerOfficialFinalVerified"]==0 and inv["visualQaPass"]==0
    for name in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
                 "VISUAL_QA.json","inventory.json","VALIDATION.json"):
        write(BASE+name,data[name])
    db_rebuild(b)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(a["g5Pass"] and a["sandboxImportPasses"]==2 for a in audits)
    agg="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    report=read(agg)
    report.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                   "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(agg,report)
    write(REPORT,{"schemaVersion":1,"year":108,"ids":sorted(IDS),
        "sharedId":SHARED_ID,"questionCrops":images,
        "sourceOriginalPageBlobsValidated":len(PAGE),
        "newWebpDrafts":26,"newSharedDrafts":1,"newG1Pass":0,
        "newG2Pass":0,"newOfficialFinalAnswerVerified":0,
        "g5PassYears":11,"releaseAllowed":False,"integrationReady":False})
    print(json.dumps({"mode":"STAGED","newIndividualWebpDrafts":26,
          "year108LinkedWebp":204,"sharedMaterialDrafts":1,
          "G1Added":0,"G5":11,"NO_RELEASE":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    x=p.add_mutually_exclusive_group(required=True)
    x.add_argument("--check",action="store_true")
    x.add_argument("--stage",action="store_true")
    a=p.parse_args()
    run(a.stage)
