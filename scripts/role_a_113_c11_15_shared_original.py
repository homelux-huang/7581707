#!/usr/bin/env python3
"""ROLE A 113 Chinese C11-C15 original multi-page reading, figures, 5-row draft SQL.

Only archived official WebP source pixels. Every image is a decoded original
page crop stored lossless (not AI redraw or OCR image generation). Existing
year JSON and independently authored lessons remain byte-identical.
"""
import argparse
import copy
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c01_05_source_pixels as archived

ROOT=Path(__file__).resolve().parents[1]
PAGES={
    4:ROOT/"sudu/data/original/113/00-C/p004-67c0d477e9-v2-w1400-q66.webp",
    5:ROOT/"sudu/data/original/113/00-C/p005-67c0d477e9-v2-w1400-q66.webp",
}
PAGE_GIT={
    4:"789a0cfb16e7871e2fb38c1089e14face508a8ed",
    5:"be92fa73cef1622f9ea8990195779b0e41699caa",
}
TASK="A-113-C11-15-SHARED-READING-20261025-13"
BASE=ROOT/"sudu/data/processed/113/role-a-c11-15"
MAN=BASE/"manifest.json"
DB=BASE/"question-bank.sqlite3"
SHARED_ID="113-00-C-SHARED-11-15"
SHARED_CROP=[90,155,1310,951]
CROPS={
  11:(4,[90,953,1310,1150]),
  12:(4,[90,1154,1310,1284]),
  13:(4,[90,1293,1310,1810]),
  14:(5,[90,165,1310,485]),
  15:(5,[90,492,1310,1600]),
}
ANS={11:"C",12:"B",13:"C",14:"A",15:"A"}
def sha(x):return hashlib.sha256(x).hexdigest()
def gitsha(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\0"+x).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def load_archive():
    doc,p,p2,ans_img,_=archived.source()
    raws={}
    for n,path in PAGES.items():
        b=path.read_bytes()
        assert b[:4]==b"RIFF" and b[8:12]==b"WEBP",path
        assert gitsha(b)==PAGE_GIT[n],"official archive page SHA changed"
        with Image.open(path) as im:
            im.load()
            assert im.format=="WEBP" and im.size==(1400,1981)
        raws[n]=b
    assert len(p["questions"])==38 and doc["year"]==113
    assert sum(len(x["questions"]) for x in doc["papers"])==205
    assert doc["questionsFound"]==196
    for n in range(11,16):
        q=p["questions"][n-1]
        assert q["id"]==f"113-00-C-{n:02d}" and q["page"]==CROPS[n][0]
        assert q["answer"]==ord(ANS[n])-ord("A")
        assert q["officialAnswerCandidate"]==ANS[n]
        assert len(q["options"])==4 and q["sourceVersion"]["questionPdfSha256"]==archived.SRC_PDF_RECORDED
        assert q["sourceVersion"]["answerPdfSha256"]==archived.ANS_PDF_RECORDED
        assert q["answerVerified"] is False and q["questionVerified"] is False and q["teachingVerified"] is False
    assert "第5 頁" in p["questions"][12]["options"][3] and "-4-" in p["questions"][12]["options"][3]
    assert "▲閱讀下文，回答第16-19 題" in p["questions"][14]["options"][3]
    assert "蘭亭集序" in p["questions"][12]["question"] and "蘭亭集序" in p["questions"][12]["question"]
    assert "下圖" in p["questions"][14]["question"]
    return doc,p,raws,ans_img
def pixel_asset(page,box,path):
    with Image.open(PAGES[page]) as p:
        p.load()
        cropped=archived.crop(p,box)
        archived.savepixels(cropped,path)
        with Image.open(path) as dec:
            dec.load()
            assert dec.format=="WEBP" and dec.size==cropped.size
            assert ImageChops.difference(dec.convert("RGB"),cropped).getbbox() is None
    data=path.read_bytes()
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":sha(data),
            "gitBlobSha1":gitsha(data),"sourceOriginalPageNumber":page,
            "sourceOriginalPageSha256":sha(PAGES[page].read_bytes()),
            "cropPixels":box,"pixelSize":[box[2]-box[0],box[3]-box[1]]}
def create():
    doc,p,raws,answer_raw=load_archive()
    sharedpath=BASE/"shared"/f"{SHARED_ID}.webp"
    shared_asset=pixel_asset(4,SHARED_CROP,sharedpath)
    shared={"sharedMaterialId":SHARED_ID,"originalQuestionNumbers":[11,12,13,14,15],
            "sourcePageNumber":4,"linkedQuestionPages":[4,5],
            "originalContentDescription":"完整 113 年國文梅花宴敘事閱讀段落，含▲題組11-15指示和全文，不含第11題",
            "asset":shared_asset,"pixelSource":"original archived official 113 00-C page4",
            "qaStatus":"DRAFT_NEEDS_SHA_BOUND_INDIVIDUAL_IMAGE_QA",
            "independentHumanReview":False,"independentRoleEContentReview":False}
    m={"schemaVersion":1,"taskId":TASK,"year":113,"paperCode":"00-C",
       "sourceIndex":doc["sourceIndex"],"originalYearCandidateCount":205,"originalYearLegacyQuestionsFound":196,
       "originalQuestionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
       "originalAnswerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
       "originalPdfsRehashedThisBatch":False,
       "officialFinalCorrectionNoticeChecked":False,
       "originalPages":{str(n):{"path":PAGES[n].relative_to(ROOT).as_posix(),
                                  "gitBlobSha1":PAGE_GIT[n],"sha256":sha(raws[n]),
                                  "pixelSize":[1400,1981]} for n in (4,5)},
       "originalAnnouncedAnswerPage":{"path":archived.ANSWER.relative_to(ROOT).as_posix(),
                                     "gitBlobSha1":archived.ANS_GIT,
                                     "sha256":sha(answer_raw)},
       "sharedMaterials":[shared],"questions":[],
       "partialCandidateSqliteRows":5,"partialSharedMaterials":1,
       "newQuestionVerified":0,"newAnswerVerified":0,"newTeachingVerified":0,
       "newIndependentEReview":0,"newReady":0,"newLive":0,
       "status":"ORIGINAL_MULTIPAGE_SOURCE_READING_CANDIDATE_NOT_RELEASED"}
    for n in range(11,16):
        orig=p["questions"][n-1]
        page,box=CROPS[n]
        path=BASE/"webp"/f"113-00-C-{n:02d}.webp"
        asset=pixel_asset(page,box,path)
        corrected=copy.deepcopy(orig["options"])
        if n in (13,15):
            assert "\n" in corrected[3]
            corrected[3]=corrected[3].split("\n",1)[0]
        assert len(corrected)==4 and all(x.strip() for x in corrected)
        assert "第5 頁" not in corrected[3] and "第6 頁" not in corrected[3]
        q={
           "questionId":orig["id"],"year":113,"paperCode":"00-C","originalQuestionNumber":n,
           "subject":"國文","question":orig["question"],"options":corrected,
           "originalRawQuestionText":orig["question"],"originalRawOptions":orig["options"],
           "originalRawOptionsSha256":sha(canon(orig["options"]).encode("utf-8")),
           "correctedOptionsSha256":sha(canon(corrected).encode("utf-8")),
           "optionDSurgicallyTrimmed":n in (13,15),
           "optionCorrectionNote":"cross-page footer/next reading removed from new candidate D; raw OCR retained" if n in (13,15) else "unchanged original PDF-text choice",
           "mandatoryOriginalTable":n==13,
           "mandatoryOriginalPoetryBlocks":n==14,
           "mandatoryOriginalIllustration":n==15,
           "mandatorySharedReadingOriginalPixels":True,
           "sharedMaterialId":SHARED_ID,"sharedMaterialAssetSha256":shared_asset["sha256"],
           "sourcePageNumber":page,"sourceAsset":asset,
           "originalContentSha256RecordedOnly":orig["sourceVersion"]["contentSha256"],
           "originalQuestionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
           "originalAnswerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
           "answerCandidate":ANS[n],"answerMatchedLegacy":bool(orig.get("answerMatched")),
           "answerVerified":False,"questionVerified":False,"teachingVerified":False,"studentReady":False,
           "originalSourceTextQaStatus":"PENDING_NUMBER_LEVEL_OFFICIAL_VISUAL_TEXT_QA",
           "officialAnswerStatus":"PUBLISHED_ANSWER_IMAGE_CANDIDATE_CORRECTION_PDF_NOT_CHECKED",
           "visualQaStatus":"DRAFT_NEEDS_SOURCE_PIXEL_VISUAL_QA",
           "independentRoleEContentReview":False
        }
        rev={k:q[k] for k in ("questionId","question","options","sourceAsset",
                            "sharedMaterialId","sharedMaterialAssetSha256",
                            "originalQuestionPdfSha256RecordedOnly")}
        q["sourceRevisionSha256"]=sha(canon(rev).encode("utf-8"))
        m["questions"].append(q)
    assert len(m["questions"])==5 and len({q["questionId"] for q in m["questions"]})==5
    return m
DDL="""
PRAGMA page_size=4096;
CREATE TABLE questions(
 question_id TEXT PRIMARY KEY,year INTEGER NOT NULL CHECK(year=113),
 paper_code TEXT NOT NULL,original_number INTEGER NOT NULL,
 question TEXT NOT NULL,options_json TEXT NOT NULL,
 answer_candidate TEXT NOT NULL,answer_verified INTEGER NOT NULL CHECK(answer_verified=0),
 question_verified INTEGER NOT NULL CHECK(question_verified=0),
 teaching_verified INTEGER NOT NULL CHECK(teaching_verified=0),
 student_ready INTEGER NOT NULL CHECK(student_ready=0),
 image_sha256 TEXT NOT NULL,shared_material_id TEXT NOT NULL,
 shared_image_sha256 TEXT NOT NULL,source_revision_sha256 TEXT NOT NULL,
 payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
CREATE TABLE shared_materials(shared_material_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""
def write_db(path,m):
    if path.exists():path.unlink()
    with sqlite3.connect(path) as db:
        db.executescript(DDL)
        shared=m["sharedMaterials"][0]
        s=canon(shared)
        db.execute("INSERT INTO shared_materials VALUES (?,?,?)",(SHARED_ID,s,sha(s.encode("utf-8"))))
        for q in m["questions"]:
            payload=canon(q)
            db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (q["questionId"],113,"00-C",q["originalQuestionNumber"],q["question"],canon(q["options"]),
                 q["answerCandidate"],0,0,0,0,q["sourceAsset"]["sha256"],SHARED_ID,
                 shared["asset"]["sha256"],q["sourceRevisionSha256"],payload,sha(payload.encode("utf-8"))))
        db.executemany("INSERT INTO metadata VALUES (?,?)",
           [("scope","113-00-C-11-15_partial_only"),("approval","SOURCE_CANDIDATE_UNVERIFIED"),
            ("origin","original_p4_5_lossless_images")])
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
def check_db(path,m):
    qmap={q["questionId"]:q for q in m["questions"]}
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        rows=db.execute("SELECT question_id,question,options_json,answer_candidate,answer_verified,question_verified,teaching_verified,student_ready,image_sha256,shared_material_id,shared_image_sha256,source_revision_sha256,payload_json,payload_sha256 FROM questions ORDER BY original_number").fetchall()
        assert len(rows)==5
        for row in rows:
            id_,stem,options,answer,av,qv,tv,ready,img,sid,sim,revision,payload,digest=row
            q=qmap[id_]
            assert stem==q["question"] and json.loads(options)==q["options"] and answer==q["answerCandidate"]
            assert (av,qv,tv,ready)==(0,0,0,0)
            assert img==q["sourceAsset"]["sha256"] and sid==SHARED_ID and sim==q["sharedMaterialAssetSha256"]
            assert revision==q["sourceRevisionSha256"]
            assert payload==canon(q) and sha(payload.encode("utf-8"))==digest and json.loads(payload)==q
        srow=db.execute("SELECT shared_material_id,payload_json,payload_sha256 FROM shared_materials").fetchall()
        assert len(srow)==1 and srow[0][0]==SHARED_ID
        assert srow[0][1]==canon(m["sharedMaterials"][0])
        assert srow[0][2]==sha(srow[0][1].encode("utf-8"))
        assert db.execute("SELECT value FROM metadata WHERE key='approval'").fetchone()[0]=="SOURCE_CANDIDATE_UNVERIFIED"
def verify_asset(asset):
    path=ROOT/asset["path"];b=path.read_bytes()
    assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
    assert sha(b)==asset["sha256"] and gitsha(b)==asset["gitBlobSha1"]
    page=asset["sourceOriginalPageNumber"];box=asset["cropPixels"]
    assert asset["sourceOriginalPageSha256"]==sha(PAGES[page].read_bytes())
    assert asset["pixelSize"]==[box[2]-box[0],box[3]-box[1]]
    with Image.open(path) as view,Image.open(PAGES[page]) as src:
        view.load();src.load()
        assert view.format=="WEBP" and list(view.size)==asset["pixelSize"]
        assert ImageChops.difference(view.convert("RGB"),archived.crop(src,box)).getbbox() is None
def check(m):
    doc,p,raws,answer_raw=load_archive()
    assert m["taskId"]==TASK and m["year"]==113 and m["paperCode"]=="00-C"
    assert m["originalYearCandidateCount"]==205 and m["originalYearLegacyQuestionsFound"]==196
    assert m["originalPdfsRehashedThisBatch"] is False
    assert m["officialFinalCorrectionNoticeChecked"] is False
    assert len(m["sharedMaterials"])==m["partialSharedMaterials"]==1
    assert len(m["questions"])==m["partialCandidateSqliteRows"]==5
    assert all(m[k]==0 for k in ("newQuestionVerified","newAnswerVerified","newTeachingVerified","newIndependentEReview","newReady","newLive"))
    for page in (4,5):
        assert m["originalPages"][str(page)]["gitBlobSha1"]==PAGE_GIT[page]
        assert m["originalPages"][str(page)]["sha256"]==sha(raws[page])
    shared=m["sharedMaterials"][0]
    assert shared["sharedMaterialId"]==SHARED_ID
    assert shared["originalQuestionNumbers"]==list(range(11,16))
    assert shared["asset"]["cropPixels"]==SHARED_CROP
    assert shared["qaStatus"]=="DRAFT_NEEDS_SHA_BOUND_INDIVIDUAL_IMAGE_QA"
    verify_asset(shared["asset"])
    for row in m["questions"]:
        n=row["originalQuestionNumber"]
        orig=p["questions"][n-1]
        assert row["questionId"]==orig["id"] and row["question"]==orig["question"]
        assert row["sourcePageNumber"]==CROPS[n][0]
        assert row["originalRawOptions"]==orig["options"]
        assert row["originalRawOptionsSha256"]==sha(canon(orig["options"]).encode("utf-8"))
        assert row["options"]==orig["options"][:3]+([orig["options"][3].split("\n",1)[0]] if n in (13,15) else [orig["options"][3]])
        assert len(row["options"])==4 and row["answerCandidate"]==ANS[n]
        assert row["sharedMaterialId"]==SHARED_ID
        assert row["sharedMaterialAssetSha256"]==shared["asset"]["sha256"]
        assert row["sourceAsset"]["cropPixels"]==CROPS[n][1]
        assert row["visualQaStatus"]=="DRAFT_NEEDS_SOURCE_PIXEL_VISUAL_QA"
        assert row["originalSourceTextQaStatus"]=="PENDING_NUMBER_LEVEL_OFFICIAL_VISUAL_TEXT_QA"
        assert not any(row[k] for k in ("answerVerified","questionVerified","teachingVerified","studentReady","independentRoleEContentReview"))
        verify_asset(row["sourceAsset"])
        digest={k:row[k] for k in ("questionId","question","options","sourceAsset",
                                 "sharedMaterialId","sharedMaterialAssetSha256",
                                 "originalQuestionPdfSha256RecordedOnly")}
        assert row["sourceRevisionSha256"]==sha(canon(digest).encode("utf-8"))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true");parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply==args.verify:parser.error("choose exactly --apply or --verify")
    if args.apply:
        if MAN.exists():
            existing=read(MAN);check(existing);check_db(DB,existing)
            print("IDEMPOTENT_VERIFIED_AFTER_SOURCE_PIXELS, no image or DB rewrite")
            return
        BASE.mkdir(parents=True,exist_ok=True)
        m=create()
        MAN.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        write_db(DB,m)
        print("CREATED_113_C11_15",json.dumps([{"qid":q["questionId"],"imgsha":q["sourceAsset"]["sha256"],
           "rev":q["sourceRevisionSha256"]} for q in m["questions"]],ensure_ascii=False))
        print("CREATED_SHARED_ORIGINAL",m["sharedMaterials"][0]["asset"]["sha256"])
    else:
        m=read(MAN);check(m);check_db(DB,m)
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"a.sqlite3";y=Path(td)/"b.sqlite3"
            write_db(x,m);write_db(y,m)
            check_db(x,m);check_db(y,m)
            assert sha(x.read_bytes())==sha(y.read_bytes())==sha(DB.read_bytes())
        print("PASS ORIGINAL_C11_C15_SHARED_P4_AND_5_PARTIAL_SQL_SHA="+sha(DB.read_bytes()))
if __name__=="__main__":main()
