#!/usr/bin/env python3
"""Role A 113 C01-05: preserve archived original pixels; partial candidate data only."""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"sudu/data/years/113.json"
SOURCE=ROOT/"sudu/data/original/113/00-C/p002-67c0d477e9-v2-w1400-q66.webp"
ANSWER=ROOT/"sudu/data/original/113/00-C-answers/p001-9a6ce177b0-v2-w1400-q66.webp"
DEST=ROOT/"sudu/data/processed/113/role-a-c01-05"
MANIFEST=DEST/"manifest.json"
DB=DEST/"question-bank.sqlite3"
TASK="A-113-104-OFFICIAL-BASELINE-20261025-10-C01-05"
SRC_GIT="6796adb4df977d064baae8a3e066238014d096f6"
ANS_GIT="938f88435a9b21e257f11dfcfda71655e8a7a0c6"
SRC_PDF_RECORDED="67c0d477e99d07cd59af0e9c75b261692c3089fd5559185f41945de32316093f"
ANS_PDF_RECORDED="9a6ce177b0aec3f22957635cc9abc21539cf3356471b2e3dec65e550e8f9559a"
CROPS={1:[90,212,1310,335],2:[90,340,1310,530],3:[90,535,1310,768],4:[90,770,1310,1080],5:[90,1085,1310,1475]}
ANS=dict(zip(range(1,6),"CDDCD"))
def sha(x):return hashlib.sha256(x).hexdigest()
def gitsha(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\0"+x).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def source():
    d=read(DOC);p={x["paper"]:x for x in d["papers"]}
    assert d["year"]==113 and d["sourceIndex"]=="https://web1.tcte.edu.tw/EXAM/113_4y/"
    assert set(p)=={"00-C","00-E","00-MB","09-1","09-2"}
    assert len([q for x in d["papers"] for q in x["questions"]])==205
    assert d["questionsFound"]==196, "legacy 113 reported discovery gap changed"
    assert p["00-C"]["subject"]=="國文" and len(p["00-C"]["questions"])==38
    assert [q["number"] for q in p["00-C"]["questions"]]==list(range(1,39))
    a=SOURCE.read_bytes();b=ANSWER.read_bytes()
    assert a[:4]==b"RIFF" and a[8:12]==b"WEBP"
    assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
    assert gitsha(a)==SRC_GIT and gitsha(b)==ANS_GIT, "original page archive SHA changed"
    with Image.open(SOURCE) as im,Image.open(ANSWER) as answer:
        im.load();answer.load()
        assert im.format==answer.format=="WEBP"
        assert im.size[0]==answer.size[0]==1400
        assert im.size[1]>=1800 and answer.size[1]>=1800
        sizes=(list(im.size),list(answer.size))
    for n,q in enumerate(p["00-C"]["questions"][:5],1):
        assert q["id"]==f"113-00-C-{n:02d}" and q["page"]==2
        assert len(q["options"])==4 and all(x.strip() for x in q["options"])
        assert q["sourceVersion"]["questionPdfSha256"]==SRC_PDF_RECORDED
        assert q["sourceVersion"]["answerPdfSha256"]==ANS_PDF_RECORDED
        assert q["answer"]==ord(ANS[n])-ord("A")
        assert q["officialAnswerCandidate"]==ANS[n]
        assert q["questionVerified"] is False and q["answerVerified"] is False and q["teachingVerified"] is False
    return d,p["00-C"],a,b,sizes
def crop(im,box):
    assert 0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height
    return im.convert("RGB").crop(tuple(box))
def savepixels(im,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path,format="WEBP",lossless=True,method=6,exact=True)
    with Image.open(path) as dec:
        dec.load()
        assert dec.format=="WEBP" and dec.size==im.size
        assert ImageChops.difference(dec.convert("RGB"),im).getbbox() is None
def make():
    doc,p,raw,answer,(srcsize,anssize)=source()
    man={"schemaVersion":1,"taskId":TASK,"year":113,"paperCode":"00-C",
         "archivedYearJsonGitBlobSha1":"d800128217347c7c3c9c3ba1d425ef01e8b39946",
         "sourceIndex":doc["sourceIndex"],"candidateYearQuestions":205,"legacyYearQuestionsFound":196,
         "sourcePdfSha256RecordedOnly":SRC_PDF_RECORDED,
         "answerPdfSha256RecordedOnly":ANS_PDF_RECORDED,
         "pdfRehashStatus":"UNAVAILABLE_NOT_FRESHLY_DOWNLOADED",
         "originalPage":{"path":SOURCE.relative_to(ROOT).as_posix(),"gitBlobSha1":SRC_GIT,"sha256":sha(raw),"page":2,"pixelSize":srcsize},
         "answerPage":{"path":ANSWER.relative_to(ROOT).as_posix(),"gitBlobSha1":ANS_GIT,"sha256":sha(answer),"page":1,"pixelSize":anssize},
         "originalPublisherNote":"TCTE website says May 10 2024 final answer meeting; individual correction notice scope not audited",
         "sourceVisualReviewer":"Role A ChatGPT visual comparison of original full-page pixels; not a human or Role E lesson reviewer",
         "answerReviewStatus":"ORIGINAL_ANSWER_IMAGE_OBSERVED_CORRECTION_PDF_SCOPE_PENDING",
         "questions":[],"partialCandidateRows":5,"readyNew":0,"liveNew":0,
         "questionVerified":False,"answerVerified":False,"independentEReview":False,"uiQaVerified":False}
    with Image.open(SOURCE) as origin:
        origin.load()
        for n in range(1,6):
            old=p["questions"][n-1];box=CROPS[n]
            path=f"sudu/data/processed/113/role-a-c01-05/webp/113-00-C-{n:02d}.webp"
            part=crop(origin,box)
            savepixels(part,ROOT/path)
            data=(ROOT/path).read_bytes()
            q={"questionId":old["id"],"year":113,"paperCode":"00-C","originalQuestionNumber":n,
               "subject":"國文","question":old["question"],"options":old["options"],
               "answerCandidate":ANS[n],"officialAnswerCandidate":old["officialAnswerCandidate"],
               "answerMatchedLegacy":old.get("answerMatched") is True,
               "answerVerified":False,"questionVerified":False,"teachingVerified":False,"studentReady":False,
               "asset":{"path":path,"sha256":sha(data),"gitBlobSha1":gitsha(data),
                        "cropPixels":box,"pixelSize":list(part.size),"originalPageSha256":sha(raw)},
               "originalQuestionPdfSha256RecordedOnly":SRC_PDF_RECORDED,
               "officialAnswerPdfSha256RecordedOnly":ANS_PDF_RECORDED,
               "originalQuestionContentSha256RecordedOnly":old["sourceVersion"]["contentSha256"],
               "textSource":"Archived original 113 PDF-text layer, no new OCR",
               "sharedMaterialIds":[],
               "individualImageQa":"DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA",
               "textQa":"PENDING_FULL_OFFICIAL_PDF_PAGE_REVIEW",
               "officialFinalAnswerQa":"PENDING_CORRECTION_PDF_SCOPE"}
            rev={k:q[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
            q["sourceRevisionSha256"]=sha(canon(rev).encode("utf-8"))
            man["questions"].append(q)
    assert len(man["questions"])==len({q["questionId"] for q in man["questions"]})==5
    return man
DDL="""
PRAGMA page_size=4096;
CREATE TABLE questions (
 question_id TEXT PRIMARY KEY,year INTEGER NOT NULL CHECK(year=113),paper_code TEXT NOT NULL,
 original_number INTEGER NOT NULL,question TEXT NOT NULL,options_json TEXT NOT NULL,
 answer_candidate TEXT NOT NULL,answer_matched_legacy INTEGER NOT NULL,
 answer_verified INTEGER NOT NULL CHECK(answer_verified=0),
 question_verified INTEGER NOT NULL CHECK(question_verified=0),
 teaching_verified INTEGER NOT NULL CHECK(teaching_verified=0),
 student_ready INTEGER NOT NULL CHECK(student_ready=0),
 image_sha256 TEXT NOT NULL,source_revision_sha256 TEXT NOT NULL,
 payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL,
 UNIQUE(year,paper_code,original_number));
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""
def make_db(path,man):
    if path.exists():path.unlink()
    with sqlite3.connect(path) as db:
        db.executescript(DDL)
        for q in man["questions"]:
            payload=canon(q)
            db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (q["questionId"],113,"00-C",q["originalQuestionNumber"],q["question"],canon(q["options"]),
               q["answerCandidate"],int(q["answerMatchedLegacy"]),0,0,0,0,
               q["asset"]["sha256"],q["sourceRevisionSha256"],payload,sha(payload.encode("utf-8"))))
        db.executemany("INSERT INTO metadata VALUES (?,?)",
             [("scope","113-00-C-01-05_partial_only"),("approval","CANDIDATE_NOT_VERIFIED"),("originalPageGitBlob",SRC_GIT)])
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
def check_db(path,man):
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        rows=db.execute("SELECT question_id,question,options_json,answer_candidate,answer_verified,question_verified,teaching_verified,student_ready,image_sha256,source_revision_sha256,payload_json,payload_sha256 FROM questions ORDER BY original_number").fetchall()
        assert len(rows)==5
        for r,q in zip(rows,man["questions"]):
            id_,stem,opts,answer,av,qv,tv,ready,img,rev,payload,digest=r
            assert id_==q["questionId"] and stem==q["question"] and json.loads(opts)==q["options"]
            assert answer==q["answerCandidate"] and (av,qv,tv,ready)==(0,0,0,0)
            assert img==q["asset"]["sha256"] and rev==q["sourceRevisionSha256"]
            assert payload==canon(q) and sha(payload.encode("utf-8"))==digest and json.loads(payload)==q
        assert db.execute("SELECT value FROM metadata WHERE key='approval'").fetchone()[0]=="CANDIDATE_NOT_VERIFIED"
def check(man):
    d,p,raw,answer,(srcsize,anssize)=source()
    assert man["taskId"]==TASK and man["paperCode"]=="00-C" and man["year"]==113
    assert man["archivedYearJsonGitBlobSha1"]=="d800128217347c7c3c9c3ba1d425ef01e8b39946"
    assert man["originalPage"]["sha256"]==sha(raw) and man["originalPage"]["gitBlobSha1"]==SRC_GIT
    assert man["answerPage"]["sha256"]==sha(answer) and man["answerPage"]["gitBlobSha1"]==ANS_GIT
    assert man["sourcePdfSha256RecordedOnly"]==SRC_PDF_RECORDED and man["answerPdfSha256RecordedOnly"]==ANS_PDF_RECORDED
    assert man["pdfRehashStatus"]=="UNAVAILABLE_NOT_FRESHLY_DOWNLOADED"
    assert man["readyNew"]==man["liveNew"]==0 and man["independentEReview"] is False
    assert man["partialCandidateRows"]==len(man["questions"])==5
    with Image.open(SOURCE) as original:
        original.load()
        for n,q in enumerate(man["questions"],1):
            archived=p["questions"][n-1]
            assert q["questionId"]==f"113-00-C-{n:02d}" and q["question"]==archived["question"]
            assert q["options"]==archived["options"] and q["answerCandidate"]==ANS[n]
            assert q["asset"]["cropPixels"]==CROPS[n]
            assert q["individualImageQa"]=="DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA"
            assert q["officialFinalAnswerQa"]=="PENDING_CORRECTION_PDF_SCOPE"
            assert not any(q[k] for k in ("questionVerified","answerVerified","teachingVerified","studentReady"))
            path=ROOT/q["asset"]["path"];data=path.read_bytes()
            assert sha(data)==q["asset"]["sha256"] and gitsha(data)==q["asset"]["gitBlobSha1"]
            with Image.open(path) as part:
                part.load()
                assert part.format=="WEBP" and list(part.size)==q["asset"]["pixelSize"]
                assert ImageChops.difference(part.convert("RGB"),crop(original,CROPS[n])).getbbox() is None
            rev={k:q[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
            assert q["sourceRevisionSha256"]==sha(canon(rev).encode("utf-8"))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true");parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply==args.verify:parser.error("choose --apply or --verify")
    if args.apply:
        man=make();DEST.mkdir(parents=True,exist_ok=True)
        text=json.dumps(man,ensure_ascii=False,indent=2)+"\n"
        if MANIFEST.exists():
            assert MANIFEST.read_text(encoding="utf-8")==text,"manifest changed; refuse blind write"
        else:MANIFEST.write_text(text,encoding="utf-8")
        if DB.exists():check_db(DB,man)
        else:make_db(DB,man)
        print("CREATED_ARCHIVED_PIXELS",json.dumps({"ids":[x["questionId"] for x in man["questions"]],"sha":[x["asset"]["sha256"] for x in man["questions"]],"sourceWebpSha256":man["originalPage"]["sha256"],"answerWebpSha256":man["answerPage"]["sha256"],"qa":"DRAFT_NOT_PUBLISHED"},ensure_ascii=False))
    else:
        man=read(MANIFEST);check(man);check_db(DB,man)
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a.sqlite3";b=Path(td)/"b.sqlite3"
            make_db(a,man);make_db(b,man);check_db(a,man);check_db(b,man)
            assert sha(a.read_bytes())==sha(b.read_bytes())==sha(DB.read_bytes()),"dual SQL import SHA mismatch"
        print("EXACT_5_CANDIDATE_IMAGES_205_YEAR_113_GAP_9_NO_APPROVAL_SQL_SHA="+sha(DB.read_bytes()))
if __name__=="__main__":main()
