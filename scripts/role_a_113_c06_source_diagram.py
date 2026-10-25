#!/usr/bin/env python3
"""113 Role A original Q06 right-column Chinese couplet + cross-page OCR repair.

Read-only archived year JSON and official-page raster; zero global approvals,
zero invented PDF byte verification, no teaching, no role-E review, no student release.
"""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c01_05_source_pixels as archived

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/113/role-a-c06"
MAN=BASE/"manifest.json"
DB=BASE/"question-bank.sqlite3"
WEBP=BASE/"webp/113-00-C-06.webp"
TASK="A-113-C06-ORIGINAL-DIAGRAM-OCR-20261025-11"
CROP=[90,1450,1310,1881]
D_OPTION="齊物、無為"
QID="113-00-C-06"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def fromjson(path):return json.loads(path.read_text(encoding="utf-8"))
def source():
    doc,p,sourcebytes,answerbytes,(imsize,anssize)=archived.source()
    q=p["questions"][5]
    assert q["id"]==QID and q["number"]==6 and q["page"]==2 and len(q["options"])==4
    assert q["questionVerified"] is False and q["answerVerified"] is False and q["teachingVerified"] is False
    assert q["answer"]==1 and q["officialAnswerCandidate"]=="B" and q["answerMatched"] is True
    assert q["options"][3].startswith(D_OPTION)
    assert "第3 頁" in q["options"][3] and "公告試題僅供參考" in q["options"][3]
    assert q["sourceVersion"]["questionPdfSha256"]==archived.SRC_PDF_RECORDED
    assert q["sourceVersion"]["answerPdfSha256"]==archived.ANS_PDF_RECORDED
    assert sha(sourcebytes)=="2fee23a8e46c17fda589989a3d32eafc032460831e83453a016aaa67b8ef6134"
    assert sha(answerbytes)=="a3c8154f5186c925a9408e4c4b50cd9a0c2b92db2fe3375d3d13d8491b9c7bc3"
    return q,sourcebytes,answerbytes,imsize,anssize
def make():
    q,sourcebytes,answerbytes,originsize,answersize=source()
    assert all(q["options"][i].strip() for i in range(3))
    assert q["options"][3].startswith(D_OPTION) and q["options"][3]!=D_OPTION
    with Image.open(archived.SOURCE) as page:
        page.load()
        image=archived.crop(page,CROP)
        archived.savepixels(image,WEBP)
        assert image.size==(1220,CROP[3]-CROP[1])
    raw=WEBP.read_bytes()
    entry={
        "questionId":QID,"year":113,"paperCode":"00-C","originalQuestionNumber":6,"subject":"國文",
        "question":q["question"],"options":q["options"][:3]+[D_OPTION],
        "answerCandidate":"B","officialAnswerCandidate":q["officialAnswerCandidate"],
        "answerMatchedLegacy":True,"answerVerified":False,"questionVerified":False,
        "teachingVerified":False,"studentReady":False,
        "sourceArchiveQuestionId":q["id"],"sourceArchiveOriginalPage":2,
        "sourceArchiveOriginalOptions":q["options"],
        "sourceArchiveOptionDSha256":sha(q["options"][3].encode("utf-8")),
        "correctedOptionDSha256":sha(D_OPTION.encode("utf-8")),
        "sourceRawOptionDChanged":False,
        "textCorrectionScope":"only structured Q06 option D removed original p2 footer and p3 next header",
        "sourceOriginalTextStatus":"CORRECTED_CANDIDATE_WAITING_FINAL_SOURCE_PDF_REVIEW",
        "sourceOriginalFigureStatus":"FULL_RIGHT_COUPLET_FIGURE_DIRECT_VISUAL_QA_PENDING",
        "sharedMaterialIds":[],
        "asset":{"path":WEBP.relative_to(ROOT).as_posix(),"sha256":sha(raw),
                 "gitBlobSha1":archived.gitsha(raw),"cropPixels":CROP,
                 "pixelSize":[1220,CROP[3]-CROP[1]],
                 "originalPageSha256":sha(sourcebytes),"containsOriginalFigure":True},
        "originalQuestionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
        "originalAnswerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
        "answerStatus":"ANNOUNCED_ANSWER_PAGE_IMAGE_B_OBSERVED_FINAL_AMENDMENT_PDF_PENDING",
        "individualImageQa":"DRAFT_NEEDS_DIRECT_ORIGINAL_DIAGRAM_VISUAL_QA"
    }
    revision={k:entry[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
    entry["sourceRevisionSha256"]=sha(canonical(revision).encode("utf-8"))
    return {
        "schemaVersion":1,"taskId":TASK,"scope":"113-00-C-06_ONLY",
        "year":113,"paperCode":"00-C",
        "sourceIndex":"https://web1.tcte.edu.tw/EXAM/113_4y/",
        "sourceOriginalPageWebpSha256":sha(sourcebytes),
        "rejectedOldImage":{"cropPixels":[90,1472,1310,1881],"sha256":"289e16a96ceeeb1c691075b0b553adbd9e31652af0821ab24ad77cf8e15daeb7","reason":"first diagram crop top border touched/cut upper calligraphy strokes; fixed original pixels with y1 1450"},
        "answerOriginalPageWebpSha256":sha(answerbytes),
        "sourceOriginalGitBlobSha1":archived.SRC_GIT,
        "answerOriginalGitBlobSha1":archived.ANS_GIT,
        "questionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
        "answerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
        "actualPdfRedownloadedAndRehashed":False,
        "officialFinalCorrectionNoticeChecked":False,
        "questions":[entry],"partialCandidateSqliteRows":1,
        "newQuestionVerified":0,"newAnswerVerified":0,"newTeachingVerified":0,
        "newReady":0,"newLive":0,
        "status":"SINGLE_ORIGINAL_FIGURE_IMAGE_QA_PENDING_NO_RELEASE"
    }
DDL="""
PRAGMA page_size=4096;
CREATE TABLE questions (
 question_id TEXT PRIMARY KEY,year INTEGER NOT NULL CHECK(year=113),
 paper_code TEXT NOT NULL, original_number INTEGER NOT NULL,
 question TEXT NOT NULL,options_json TEXT NOT NULL,
 answer_candidate TEXT NOT NULL,answer_verified INTEGER NOT NULL CHECK(answer_verified=0),
 question_verified INTEGER NOT NULL CHECK(question_verified=0),
 teaching_verified INTEGER NOT NULL CHECK(teaching_verified=0),
 student_ready INTEGER NOT NULL CHECK(student_ready=0),
 image_sha256 TEXT NOT NULL,source_revision_sha256 TEXT NOT NULL,
 payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""
def make_db(path,manifest):
    if path.exists():path.unlink()
    q=manifest["questions"][0];payload=canonical(q)
    with sqlite3.connect(path) as db:
        db.executescript(DDL)
        db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (QID,113,"00-C",6,q["question"],canonical(q["options"]),
             "B",0,0,0,0,q["asset"]["sha256"],q["sourceRevisionSha256"],
             payload,sha(payload.encode("utf-8"))))
        db.executemany("INSERT INTO metadata VALUES (?,?)",
            [("scope","113-00-C-06_only"),("approval","UNVERIFIED_NO_RELEASE"),("originalPageGitBlob",archived.SRC_GIT)])
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
def check(manifest):
    old,page_bytes,ans_bytes,_,_=source()
    assert manifest["taskId"]==TASK and manifest["scope"]=="113-00-C-06_ONLY"
    assert manifest["sourceOriginalPageWebpSha256"]==sha(page_bytes)
    assert manifest["answerOriginalPageWebpSha256"]==sha(ans_bytes)
    assert manifest["sourceOriginalGitBlobSha1"]==archived.SRC_GIT
    assert manifest["answerOriginalGitBlobSha1"]==archived.ANS_GIT
    assert manifest["actualPdfRedownloadedAndRehashed"] is False
    assert manifest["officialFinalCorrectionNoticeChecked"] is False
    assert all(manifest[k]==0 for k in ("newQuestionVerified","newAnswerVerified","newTeachingVerified","newReady","newLive"))
    assert manifest["partialCandidateSqliteRows"]==len(manifest["questions"])==1
    q=manifest["questions"][0]
    assert q["questionId"]==QID and q["question"]==old["question"]
    assert q["options"]==old["options"][:3]+[D_OPTION]
    assert "第3 頁" not in q["options"][3]
    assert "第3 頁" in q["sourceArchiveOriginalOptions"][3]
    assert q["sourceArchiveOriginalOptions"]==old["options"]
    assert q["sourceArchiveOptionDSha256"]==sha(old["options"][3].encode("utf-8"))
    assert not any(q[k] for k in ("answerVerified","questionVerified","teachingVerified","studentReady"))
    assert q["answerCandidate"]=="B" and q["asset"]["cropPixels"]==CROP
    assert q["individualImageQa"]=="DRAFT_NEEDS_DIRECT_ORIGINAL_DIAGRAM_VISUAL_QA"
    b=WEBP.read_bytes()
    assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
    assert sha(b)==q["asset"]["sha256"] and archived.gitsha(b)==q["asset"]["gitBlobSha1"]
    with Image.open(WEBP) as image,Image.open(archived.SOURCE) as source_image:
        image.load();source_image.load()
        assert image.format=="WEBP" and image.size==(1220,CROP[3]-CROP[1])
        assert ImageChops.difference(image.convert("RGB"),archived.crop(source_image,CROP)).getbbox() is None
    revision={k:q[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
    assert q["sourceRevisionSha256"]==sha(canonical(revision).encode("utf-8"))
def check_db(path,manifest):
    q=manifest["questions"][0]
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        rows=db.execute("SELECT question_id,question,options_json,answer_candidate,answer_verified,question_verified,teaching_verified,student_ready,image_sha256,source_revision_sha256,payload_json,payload_sha256 FROM questions").fetchall()
        assert len(rows)==1
        id_,stem,opts,letter,av,qv,tv,ready,img,rev,payload,h=rows[0]
        assert id_==QID and stem==q["question"] and json.loads(opts)==q["options"] and letter=="B"
        assert (av,qv,tv,ready)==(0,0,0,0)
        assert img==q["asset"]["sha256"] and rev==q["sourceRevisionSha256"]
        assert json.loads(payload)==q and payload==canonical(q) and sha(payload.encode("utf-8"))==h
        assert db.execute("SELECT value FROM metadata WHERE key='approval'").fetchone()[0]=="UNVERIFIED_NO_RELEASE"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply==args.verify:parser.error("choose exactly --apply or --verify")
    if args.apply:
        if MAN.exists():
            saved=fromjson(MAN)
            if saved["questions"][0]["asset"]["cropPixels"]==[90,1472,1310,1881]:
                # Only the first imaged original diagram candidate is defective:
                # its calligraphy top touches crop boundary. Refuse all unknown
                # hashes and do NOT recreate or touch Q01-Q05 images/DB.
                old=saved["questions"][0]["asset"]
                assert old["sha256"]=="289e16a96ceeeb1c691075b0b553adbd9e31652af0821ab24ad77cf8e15daeb7"
                assert old["gitBlobSha1"]=="ec5150173ecf4edcbdc19737d5c58ffc19f41747"
                assert sha(WEBP.read_bytes())==old["sha256"]
                check_db(DB,saved)
                updated=make()
                assert updated["questions"][0]["asset"]["cropPixels"]==CROP
                assert saved["questions"][0]["options"]==updated["questions"][0]["options"]
                assert saved["questions"][0]["answerCandidate"]==updated["questions"][0]["answerCandidate"]=="B"
                assert updated["rejectedOldImage"]["sha256"]==old["sha256"]
                staged=DB.with_suffix(".sqlite3.stage")
                make_db(staged,updated)
                check_db(staged,updated)
                import os
                os.replace(staged,DB)
                MAN.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                print("SURGICAL_C06_TOP_FIGURE_BOUNDARY",old["sha256"],"->",updated["questions"][0]["asset"]["sha256"])
                return
            check(saved);check_db(DB,saved)
            print("IDEMPOTENT verified existing source, no recrop, no SQLite write")
            return
        BASE.mkdir(parents=True,exist_ok=True)
        m=make();MAN.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        make_db(DB,m)
        print("CREATED_Q06_ONLY",json.dumps({"crop":CROP,"sha":m["questions"][0]["asset"]["sha256"],
             "sourceRevision":m["questions"][0]["sourceRevisionSha256"],
             "originalOptionDSha":m["questions"][0]["sourceArchiveOptionDSha256"],
             "fixedOptionD":D_OPTION,"answerCandidate":"B","newReady":0},ensure_ascii=False))
    else:
        m=fromjson(MAN);check(m);check_db(DB,m)
        with tempfile.TemporaryDirectory() as td:
            first=Path(td)/"first.sqlite3";second=Path(td)/"second.sqlite3"
            make_db(first,m);make_db(second,m)
            check_db(first,m);check_db(second,m)
            assert sha(first.read_bytes())==sha(second.read_bytes())==sha(DB.read_bytes())
        print("PASS Q06 original figure and corrected D, SQL SHA:"+sha(DB.read_bytes()))
if __name__=="__main__":main()
