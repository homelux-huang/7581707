#!/usr/bin/env python3
"""Source-pixel-only staging for previously missing 107 Chinese Q8-16 and Q35-38.
13 individual original-page WebP candidates, plus 3 independently linked shared materials.
All G1 DRAFT, G2/G3 unverified, NO RELEASE. Do not reprocess existing valid assets.
"""
import argparse,hashlib,io,json,sqlite3,os,shutil,tempfile
from pathlib import Path
from PIL import Image,ImageChops
from audit_105_115_sqlite_readonly import canonical,digest,audit_year

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/107"
BRANCH="qa/114-115-official-visual-review"
PDF_SHA="9dcc8c71c26d97aa1e71a2e1c673823d084d2a5985ce3a682caa5d46e3036430"
PAGE={
 3:("sudu/data/original/107/00-C/p003-9dcc8c71c2-v2-w1400-q66.webp","ef9d22515f19eaf2c0bdd18e6131f2d35bf08706"),
 4:("sudu/data/original/107/00-C/p004-9dcc8c71c2-v2-w1400-q66.webp","88907af20f1f0e209e1d6a411b2f78eb6e6a1522"),
 8:("sudu/data/original/107/00-C/p008-9dcc8c71c2-v2-w1400-q66.webp","f66a0018d9e34fb66a7273756e13329d6b0ec088"),
}
CROPS={
 "107-00-C-08":(3,[90,174,1310,448]),
 "107-00-C-09":(3,[90,449,1310,792]),
 "107-00-C-10":(3,[90,793,1310,977]),
 "107-00-C-11":(3,[90,978,1310,1400]),
 "107-00-C-12":(3,[90,1401,1310,1822]),
 "107-00-C-13":(4,[90,499,1310,616]),
 "107-00-C-14":(4,[90,617,1310,1137]),
 "107-00-C-15":(4,[90,1284,1310,1359]),
 "107-00-C-16":(4,[90,1360,1310,1522]),
 "107-00-C-35":(8,[90,171,1310,343]),
 "107-00-C-36":(8,[90,932,1310,1092]),
 "107-00-C-37":(8,[90,1093,1310,1197]),
 "107-00-C-38":(8,[90,1198,1310,1320]),
 "107-00-C-SHARED-13-14":(4,[90,167,1310,496]),
 "107-00-C-SHARED-15-16":(4,[90,1140,1310,1283]),
 "107-00-C-SHARED-36-38":(8,[90,348,1310,930]),
}
SHARED={
 "107-00-C-SHARED-13-14":[13,14],
 "107-00-C-SHARED-15-16":[15,16],
 "107-00-C-SHARED-36-38":[36,37,38],
}
IDS=[k for k in CROPS if k not in SHARED]
REPORT="sudu/data/processed/107/qa-drafts/DRAFT_107_CHINESE_13_MISSING_3_SHARED_20261024.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def at(p):
    x=(ROOT/p).resolve()
    assert x.is_relative_to(ROOT.resolve())
    return x
def read(p):return json.loads(at(p).read_text("utf8"))
def write(p,ob):
    target=at(p);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(ob,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def by(rows,key):
    z={x[key]:x for x in rows}
    assert len(z)==len(rows)
    return z
def images(stage):
    result={}
    for page,(source,blob) in PAGE.items():
        raw=at(source).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==blob
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            assert im.format=="WEBP" and im.size==(1400,1980)
            for id,(pn,box) in CROPS.items():
                if pn!=page:continue
                assert 0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height
                cropped=im.crop(tuple(box))
                buf=io.BytesIO()
                cropped.save(buf,format="WEBP",lossless=True,method=6,exact=True)
                b=buf.getvalue()
                with Image.open(io.BytesIO(b)) as reread:
                    reread.load()
                    assert reread.size==cropped.size
                    assert ImageChops.difference(cropped.convert("RGB"),reread.convert("RGB")).getbbox() is None
                folder="shared" if id in SHARED else "00-C"
                out=f"sudu/data/processed/107/qa-drafts/webp-v3/{folder}/{id}.webp"
                if at(out).exists():
                    assert sha(at(out).read_bytes())==sha(b),"Existing changed candidate; do not overwrite"
                elif stage:
                    at(out).parent.mkdir(parents=True,exist_ok=True)
                    at(out).write_bytes(b)
                result[id]={"id":id,"year":107,"paperCode":"00-C","sourcePage":page,
                  "source":source,"sourcePageWebpSha256":sha(raw),"sourcePageGitBlob":blob,
                  "officialQuestionPdfSha256":PDF_SHA,
                  "cropPixels":box,"output":out,"outputSha256":sha(b),
                  "outputSize":[box[2]-box[0],box[3]-box[1]],
                  "generationVersion":"assistant-located-source-pixel-v3-20261024",
                  "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
                  "issues":["DRAFT_PENDING_SEPARATE_SOURCE_CROP_G1","MUST_VERIFY_ABCD_AND_SHARED_CROPS"]}
    assert set(result)==set(CROPS)
    return result

def update_db(bank):
    dbfile=BASE/"question-bank.sqlite3"
    with tempfile.TemporaryDirectory(dir=BASE) as td:
        work=Path(td)/"question-bank.sqlite3"
        shutil.copyfile(dbfile,work)
        with sqlite3.connect(work) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
            assert {"question_id","payload","payload_sha256"}<=cols
            for rep in (1,2):
                for q in bank["questions"]:
                    payload=canonical(q)
                    c=db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                                 (payload,digest(payload.encode("utf8")),q["questionId"]))
                    assert c.rowcount==1
                for s in bank["sharedMaterials"]:
                    db.execute("INSERT INTO shared_materials(material_id,payload) VALUES(?,?) "
                               "ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload",
                               (s["sharedMaterialId"],canonical(s)))
                db.commit()
                assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
                assert db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==len(bank["sharedMaterials"])
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            qs={q["questionId"]:q for q in bank["questions"]}
            ss={s["sharedMaterialId"]:s for s in bank["sharedMaterials"]}
            for id,payload,hsh in db.execute("SELECT question_id,payload,payload_sha256 FROM questions"):
                assert json.loads(payload)==qs[id] and digest(payload.encode("utf8"))==hsh
            for id,payload in db.execute("SELECT material_id,payload FROM shared_materials"):
                assert json.loads(payload)==ss[id]
        os.replace(work,dbfile)

def run(stage):
    items=images(stage)
    f={x:read(f"sudu/data/processed/107/{x}") for x in (
       "questions.json","webp-manifest.json","ocr-raw-candidates.json",
       "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")}
    bank=f["questions.json"];m=f["webp-manifest.json"];ocr=f["ocr-raw-candidates.json"]
    v=f["VISUAL_QA.json"];inv=f["inventory.json"];val=f["VALIDATION.json"]
    rel=f["release-manifest.json"]
    assert len(bank["questions"])==len(m["items"])==len(ocr["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==191 and inv["visualQaPass"]==v["passCount"]==6
    assert inv["ocrTextIndependentlyVerified"]==5 and inv["answerOfficialFinalVerified"]==0
    assert len(m["sharedMaterialCrops"])==len(bank["sharedMaterials"])==len(v["sharedMaterials"])==2
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    questions=by(bank["questions"],"questionId")
    mm=by(m["items"],"questionId")
    oo=by(ocr["items"],"questionId")
    vv=by(v["items"],"questionId")
    for id in IDS:
        assert mm[id]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        assert not mm[id].get("output") and not questions[id]["assets"]["singleQuestionWebp"]
        assert vv[id]["status"]=="BLOCKED"
        assert not questions[id]["questionVerified"] and not questions[id]["answerVerified"]
        assert not questions[id]["integrationReady"]
        assert mm[id]["officialQuestionPdfSha256"]==PDF_SHA
        assert not questions[id]["sharedMaterialIds"]
    assert all(s not in {row["sharedMaterialId"] for row in bank["sharedMaterials"]} for s in SHARED)
    if not stage:
        print(json.dumps({"mode":"CHECK","draftQuestionIds":IDS,"draftSharedIds":list(SHARED),
         "validSourceGitBlobs":len(PAGE),"g1Added":0,"noRelease":True},ensure_ascii=False))
        return
    for id in IDS:
        row=items[id]
        mm[id].update(row)
        q=questions[id]
        q["assets"].update({"singleQuestionWebp":row["output"],
           "sourcePageWebp":row["source"],"sha256":row["outputSha256"],"sourcePage":row["sourcePage"]})
        q["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        q["issues"]=sorted(set(q.get("issues",[])+row["issues"]))
        oo[id]["imageSha256"]=row["outputSha256"]
        vv[id].update({"status":"PENDING","sourcePage":row["sourcePage"],
           "sourceWebp":row["source"],"candidateWebp":row["output"],
           "candidateSha256":row["outputSha256"],"reviewer":None,"visualEvidence":None})
    for sid,nums in SHARED.items():
        x=items[sid].copy();x.pop("id")
        x.update({"sharedMaterialId":sid,"originalQuestionNumbers":nums})
        m["sharedMaterialCrops"].append(x)
        bank["sharedMaterials"].append(x.copy())
        v["sharedMaterials"].append({"sharedMaterialId":sid,"sourcePage":x["sourcePage"],
           "sourceWebp":x["source"],"candidateWebp":x["output"],
           "candidateSha256":x["outputSha256"],"status":"PENDING",
           "reviewer":None,"visualEvidence":None})
        for n in nums:
            id=f"107-00-C-{n:02d}"
            questions[id]["sharedMaterialIds"]=[sid]
    inv["webpGeneratedDrafts"]=204
    inv["sourcePaperStats"]["00-C"]["imageDrafts"]=38
    inv["sourcePaperStats"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(8,17))+list(range(35,39))
    inv["sharedMaterialsDrafts"]=5
    inv["sharedMaterialsReviewRequired"]=5
    val["sourceGaps"]["00-C"]["imageDrafts"]=38
    val["sourceGaps"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(8,17))+list(range(35,39))
    assert inv["visualQaPass"]==6 and inv["answerOfficialFinalVerified"]==0
    for name in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
                 "VISUAL_QA.json","inventory.json","VALIDATION.json"):
        write("sudu/data/processed/107/"+name,f[name])
    update_db(bank)
    g5=[audit_year(y) for y in range(105,116)]
    assert all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in g5)
    aggregate="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    rep=read(aggregate)
    rep.update({"years":g5,"yearsG5Pass":11,"yearsReviewed":11,
                "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(aggregate,rep)
    write(REPORT,{"schemaVersion":1,"year":107,"paperCode":"00-C",
         "questionIds":IDS,"sharedMaterialIds":list(SHARED),
         "officialQuestionPdfSha256":PDF_SHA,"candidateCrops":items,
         "newCandidateSingleWebp":len(IDS),"newSharedMaterialDrafts":len(SHARED),
         "sourcePixelLosslessVerified":True,
         "newG1Pass":0,"newOCRQaPass":0,"newAnswerVerified":0,
         "g5YearsPass":11,"releaseAllowed":False,"integrationReady":False})
    print(json.dumps({"mode":"STAGED","newCandidateSingleWebp":len(IDS),
      "newSharedMaterialDrafts":len(SHARED),"year107LinkedWebp":204,
      "newG1Pass":0,"g5YearsPass":11,"noRelease":True},ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    x=p.add_mutually_exclusive_group(required=True)
    x.add_argument("--check",action="store_true")
    x.add_argument("--stage",action="store_true")
    args=p.parse_args();run(args.stage)
