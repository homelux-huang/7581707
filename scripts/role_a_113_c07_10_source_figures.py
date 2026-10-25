#!/usr/bin/env python3
"""ROLE A 113 Chinese C07-C10, original pixel question/figures, partial unapproved SQL.

Derived only from already archived official exam and answer WebPs, using
original-page crop pixels. Correct contaminated option transcriptions in
candidate ONLY, preserve complete historical raw text and images unmodified.
"""
import argparse
import copy
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from PIL import Image,ImageChops
from scripts import role_a_113_c01_05_source_pixels as archived

ROOT=Path(__file__).resolve().parents[1]
ORIGIN=ROOT/"sudu/data/original/113/00-C/p003-67c0d477e9-v2-w1400-q66.webp"
SOURCE_GIT="9578305e9c4181d3b339b830e23e12402f4893d3"
TASK="A-113-C07-10-DIAGRAM-AND-TEXT-20261025-12"
BASE=ROOT/"sudu/data/processed/113/role-a-c07-10"
MAN=BASE/"manifest.json";DB=BASE/"question-bank.sqlite3"
CROPS={7:[90,164,1310,502],8:[90,505,1310,657],9:[90,661,1310,1136],10:[90,1137,1310,1840]}
ANS={7:"A",8:"D",9:"B",10:"B"}
CLEAN_OPTIONS={
 9:["①、②皆正確","①、②皆錯誤","①正確，②錯誤","①錯誤，②正確"],
 10:["載人 ／ 重視人權 ／ 運貨 ／ 貶抑物價",
     "載人 ／ 怕走路累 ／ 運貨 ／ 互通有無",
     "北方 ／ 重視人權 ／ 南方 ／ 貶抑物價",
     "北方 ／ 怕走路累 ／ 南方 ／ 互通有無"],
}
Q10_LABELS=["①","①－1","②","②－1"]
def sha(b):return hashlib.sha256(b).hexdigest()
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def source():
    doc,p,p2,ans_img,_=archived.source()
    src=ORIGIN.read_bytes()
    assert src[:4]==b"RIFF" and src[8:12]==b"WEBP"
    assert gitsha(src)==SOURCE_GIT,"archived original page3 mutated"
    with Image.open(ORIGIN) as im:
        im.load()
        assert im.format=="WEBP" and im.size==(1400,1981)
    assert len(p["questions"])==38
    assert len([q for x in doc["papers"] for q in x["questions"]])==205
    assert doc["questionsFound"]==196
    assert doc["sourceIndex"]=="https://web1.tcte.edu.tw/EXAM/113_4y/"
    for n in range(7,11):
        q=p["questions"][n-1]
        assert q["id"]==f"113-00-C-{n:02d}" and q["number"]==n and q["page"]==3
        assert q["answer"]==ord(ANS[n])-ord("A")
        assert q["officialAnswerCandidate"]==ANS[n]
        assert q["sourceVersion"]["questionPdfSha256"]==archived.SRC_PDF_RECORDED
        assert q["sourceVersion"]["answerPdfSha256"]==archived.ANS_PDF_RECORDED
        assert not q["answerVerified"] and not q["questionVerified"] and not q["teachingVerified"]
        assert len(q["options"])==4
    assert "對立" in p["questions"][8]["question"], "expected original Q9 strategy-chart text missing"
    assert "配合他人的程度" in p["questions"][8]["options"][3], "expected actual Q9 axis spill into original option D missing"
    assert "▲閱讀下文，回答第11-15 題" in p["questions"][9]["options"][3], "expected Q10 cross-page bleed absent"
    assert "貶抑物價" in p["questions"][9]["options"][0], "Q10 original table content changed"
    return doc,p,src,ans_img
def exact():
    doc,p,original,answer=source()
    man={"schemaVersion":1,"taskId":TASK,"year":113,"paperCode":"00-C",
         "sourceIndex":doc["sourceIndex"],"yearCandidateQuestionCount":205,
         "yearLegacyQuestionsFound":196,"originalPageNumber":3,
         "rejectedInitialCrops":[
             {"questionId":"113-00-C-09","cropPixels":[90,661,1310,1123],"sha256":"2c42042d8f75bba4123e76e151e088659d769c90ad665fb26589f3fff87c54ac","reason":"bottom x-axis label touched and risked glyph clipping"},
             {"questionId":"113-00-C-10","cropPixels":[90,1125,1310,1840],"sha256":"d4491b6806725f979615be77164a943732f511991b680fdfc6383a21190c1491","reason":"shift Q10 start past Q09 complete axis caption without mixing"}],
         "originalPage":{"path":ORIGIN.relative_to(ROOT).as_posix(),"gitBlobSha1":SOURCE_GIT,
                         "sha256":sha(original),"pixelSize":[1400,1981]},
         "originalAnswerPage":{"path":archived.ANSWER.relative_to(ROOT).as_posix(),
                                "gitBlobSha1":archived.ANS_GIT,"sha256":sha(answer),
                                "pixelSize":[1400,1980]},
         "questionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
         "answerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
         "originalPdfsFreshlyDownloadedAndHashed":False,
         "officialFinalAmendmentCheckedForNumbers":False,
         "questionCount":4,"questions":[],
         "newQuestionVerified":0,"newAnswerVerified":0,"newTeachingVerified":0,
         "newIndependentEReview":0,"newReady":0,"newLive":0,
         "status":"ORIGINAL_PIXEL_SOURCE_CANDIDATES_UNRELEASED",
         "notes":"Source original retained intact. Q09 five-strategy axes and Q10 fishbone + A-D table are original pixels, not AI redrawn. Text corrections remain candidates."}
    with Image.open(ORIGIN) as image:
        image.load()
        for n in range(7,11):
            orig=p["questions"][n-1]
            out=BASE/"webp"/f"113-00-C-{n:02d}.webp"
            crop=archived.crop(image,CROPS[n])
            if n in (7,8) and out.exists():
                # Already original-image byte verified and genuinely visualized.
                # Never re-crop valid Q7/Q8 just to fix figure boundaries in Q9/Q10.
                pins={7:"dc654891d368033b5b422cf01181231aefc62e9a31452ad1e64aaca478291b4a",
                      8:"4ea59fb90d9bbec2f255944b0a5fc6be4f9a25257e3f74caa7aa3b5e10e88e49"}
                existing=out.read_bytes()
                assert sha(existing)==pins[n],"verified Q7/Q8 image drift"
                with Image.open(out) as verified:
                    verified.load()
                    assert verified.size==crop.size
                    assert ImageChops.difference(verified.convert("RGB"),crop).getbbox() is None
            else:
                archived.savepixels(crop,out)
            raw=out.read_bytes()
            correct=copy.deepcopy(CLEAN_OPTIONS.get(n,orig["options"]))
            if n==9:
                assert all("堅" not in s and "自" not in s for s in correct)
            if n==10:
                assert "▲閱讀下文" not in correct[3]
            entry={
                "questionId":orig["id"],"year":113,"paperCode":"00-C","originalQuestionNumber":n,
                "subject":"國文","question":orig["question"],"options":correct,
                "originalRawQuestionText":orig["question"],
                "originalRawOptions":orig["options"],
                "originalRawOptionsSha256":sha(canonical(orig["options"]).encode("utf-8")),
                "candidateCorrectedOptionsSha256":sha(canonical(correct).encode("utf-8")),
                "optionTextCorrection":n in (9,10),"optionDiffReason":(
                    "Q09 original axes/labels from adjacent strategy chart spilled into candidate choice strings" if n==9
                    else "Q10 original fishbone and A-D 4-column table plus next p4 article spilled into options" if n==10
                    else "unchanged original source PDF text"),
                "originalAnswerOptionColumnLabels":Q10_LABELS if n==10 else [],
                "mandatoryOriginalFigure":n in (9,10),
                "originalFigureKind":("five_strategy_positioning_matrix" if n==9 else "fishbone_cause_chart_and_four_column_AD_table" if n==10 else "none"),
                "originalQuestionTextQa":"PENDING_FINAL_PAGE_VISUAL_TEXT_QA",
                "candidateOptionTranscriptionReviewer":"ChatGPT Role A direct original full-page image; not independent E",
                "originalArchivedContentSha256RecordedOnly":orig["sourceVersion"]["contentSha256"],
                "answerCandidate":ANS[n],"answerMatchedLegacy":bool(orig.get("answerMatched")),
                "answerVerified":False,"questionVerified":False,"teachingVerified":False,"studentReady":False,
                "officialAnswerStatus":"ANNOUNCED_IMAGE_CANDIDATE_FINAL_CORRECTION_SCOPE_PENDING",
                "visualQaStatus":"DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA",
                "asset":{"path":out.relative_to(ROOT).as_posix(),"sha256":sha(raw),"gitBlobSha1":gitsha(raw),
                         "cropPixels":CROPS[n],"pixelSize":list(crop.size),
                         "sourceOriginalPageSha256":sha(original),"page":3},
                "originalQuestionPdfSha256RecordedOnly":archived.SRC_PDF_RECORDED,
                "originalAnswerPdfSha256RecordedOnly":archived.ANS_PDF_RECORDED,
            }
            revision={k:entry[k] for k in ("questionId","question","options","asset",
                                            "originalQuestionPdfSha256RecordedOnly")}
            entry["sourceRevisionSha256"]=sha(canonical(revision).encode("utf-8"))
            man["questions"].append(entry)
    assert len(man["questions"])==len({q["questionId"] for q in man["questions"]})==4
    return man
DDL="""
PRAGMA page_size=4096;
CREATE TABLE questions(
 question_id TEXT PRIMARY KEY,year INTEGER NOT NULL CHECK(year=113),paper_code TEXT NOT NULL,
 original_number INTEGER NOT NULL,question TEXT NOT NULL,options_json TEXT NOT NULL,
 answer_candidate TEXT NOT NULL,answer_verified INTEGER NOT NULL CHECK(answer_verified=0),
 question_verified INTEGER NOT NULL CHECK(question_verified=0),
 teaching_verified INTEGER NOT NULL CHECK(teaching_verified=0),
 student_ready INTEGER NOT NULL CHECK(student_ready=0),image_sha256 TEXT NOT NULL,
 source_revision_sha256 TEXT NOT NULL,payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL,
 UNIQUE(year,paper_code,original_number));
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""
def write_db(path,man):
    if path.exists():path.unlink()
    with sqlite3.connect(path) as db:
        db.executescript(DDL)
        for q in man["questions"]:
            blob=canonical(q)
            db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (q["questionId"],113,"00-C",q["originalQuestionNumber"],q["question"],
                        canonical(q["options"]),q["answerCandidate"],0,0,0,0,q["asset"]["sha256"],
                        q["sourceRevisionSha256"],blob,sha(blob.encode("utf-8"))))
        db.executemany("INSERT INTO metadata VALUES (?,?)",
                       [("scope","113_C07_10_partial_only"),("approval","PENDING_OFFICIAL_CORRECTIONS_AND_ROLE_E"),("originalPageBlob",SOURCE_GIT)])
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
def read_db(path,man):
    mapping={q["questionId"]:q for q in man["questions"]}
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        rows=db.execute("SELECT question_id,question,options_json,answer_candidate,answer_verified,question_verified,teaching_verified,student_ready,image_sha256,source_revision_sha256,payload_json,payload_sha256 FROM questions ORDER BY original_number").fetchall()
        assert len(rows)==len(mapping)==4
        for row in rows:
            qid,question,opts,answer,av,qv,tv,ready,img,rev,payload,digest=row
            q=mapping[qid]
            assert question==q["question"] and json.loads(opts)==q["options"]
            assert answer==q["answerCandidate"] and (av,qv,tv,ready)==(0,0,0,0)
            assert img==q["asset"]["sha256"] and rev==q["sourceRevisionSha256"]
            assert payload==canonical(q) and sha(payload.encode("utf-8"))==digest and json.loads(payload)==q
        assert db.execute("SELECT value FROM metadata WHERE key='approval'").fetchone()[0]=="PENDING_OFFICIAL_CORRECTIONS_AND_ROLE_E"
def check(man):
    doc,p,page_raw,answer_raw=source()
    assert man["taskId"]==TASK and man["year"]==113 and man["paperCode"]=="00-C"
    assert man["originalPage"]["sha256"]==sha(page_raw) and man["originalPage"]["gitBlobSha1"]==SOURCE_GIT
    assert man["originalAnswerPage"]["sha256"]==sha(answer_raw) and man["originalAnswerPage"]["gitBlobSha1"]==archived.ANS_GIT
    assert man["originalPdfsFreshlyDownloadedAndHashed"] is False
    assert man["officialFinalAmendmentCheckedForNumbers"] is False
    assert man["questionCount"]==len(man["questions"])==4
    assert all(man[k]==0 for k in ("newQuestionVerified","newAnswerVerified","newTeachingVerified","newIndependentEReview","newReady","newLive"))
    original={q["number"]:q for q in p["questions"]}
    with Image.open(ORIGIN) as page:
        page.load()
        for q in man["questions"]:
            n=q["originalQuestionNumber"];raw=original[n]
            assert n in CROPS and q["questionId"]==f"113-00-C-{n:02d}"
            assert q["question"]==raw["question"] and q["originalRawOptions"]==raw["options"]
            assert q["options"]==CLEAN_OPTIONS.get(n,raw["options"])
            assert q["optionTextCorrection"]==(n in (9,10))
            assert q["mandatoryOriginalFigure"]==(n in (9,10))
            assert q["originalRawOptionsSha256"]==sha(canonical(raw["options"]).encode("utf-8"))
            assert q["candidateCorrectedOptionsSha256"]==sha(canonical(q["options"]).encode("utf-8"))
            assert q["visualQaStatus"]=="DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA"
            assert q["officialAnswerStatus"]=="ANNOUNCED_IMAGE_CANDIDATE_FINAL_CORRECTION_SCOPE_PENDING"
            assert q["answerCandidate"]==ANS[n]
            assert q["asset"]["cropPixels"]==CROPS[n] and q["asset"]["page"]==3
            assert q["asset"]["pixelSize"]==[CROPS[n][2]-CROPS[n][0],CROPS[n][3]-CROPS[n][1]]
            assert not any(q[k] for k in ("answerVerified","questionVerified","teachingVerified","studentReady"))
            orig_asset=ROOT/q["asset"]["path"];b=orig_asset.read_bytes()
            assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
            assert sha(b)==q["asset"]["sha256"] and gitsha(b)==q["asset"]["gitBlobSha1"]
            with Image.open(orig_asset) as im:
                im.load()
                assert im.format=="WEBP"
                assert list(im.size)==q["asset"]["pixelSize"]
                assert ImageChops.difference(im.convert("RGB"),archived.crop(page,CROPS[n])).getbbox() is None
            rr={k:q[k] for k in ("questionId","question","options","asset","originalQuestionPdfSha256RecordedOnly")}
            assert q["sourceRevisionSha256"]==sha(canonical(rr).encode("utf-8"))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.apply==args.verify:parser.error("choose one of --apply or --verify")
    if args.apply:
        if MAN.exists():
            current=read(MAN)
            old_crops={q["originalQuestionNumber"]:q["asset"]["cropPixels"] for q in current["questions"]}
            if old_crops[9]==[90,661,1310,1123] and old_crops[10]==[90,1125,1310,1840]:
                # Tight bottom caption Q09 crop discovered by real image inspection.
                # Verify old exact SHA, preserve and never regenerate Q07/Q08.
                old_expected={7:"dc654891d368033b5b422cf01181231aefc62e9a31452ad1e64aaca478291b4a",
                              8:"4ea59fb90d9bbec2f255944b0a5fc6be4f9a25257e3f74caa7aa3b5e10e88e49",
                              9:"2c42042d8f75bba4123e76e151e088659d769c90ad665fb26589f3fff87c54ac",
                              10:"d4491b6806725f979615be77164a943732f511991b680fdfc6383a21190c1491"}
                assert {q["originalQuestionNumber"]:q["asset"]["sha256"] for q in current["questions"]}==old_expected
                for q in current["questions"]:
                    assert sha((ROOT/q["asset"]["path"]).read_bytes())==old_expected[q["originalQuestionNumber"]]
                read_db(DB,current)
                updated=exact()
                assert current["questions"][:2]==updated["questions"][:2]
                unchanged=copy.deepcopy(current)
                unchanged["questions"][2:]=updated["questions"][2:]
                unchanged["rejectedInitialCrops"]=updated["rejectedInitialCrops"]
                assert unchanged==updated,"changes beyond corrected Q09/Q10 pixels/digest"
                stage=DB.with_suffix(".sqlite3.stage")
                write_db(stage,updated)
                read_db(stage,updated)
                os.replace(stage,DB)
                MAN.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                print("SOURCE_IMAGE_Q09_Q10_BOUNDARY_ONLY_CORRECTED",[(n,old_expected[n],updated["questions"][n-7]["asset"]["sha256"]) for n in (9,10)])
                return
            check(current);read_db(DB,current)
            print("IDEMPOTENT_NO_IMAGE_REBUILD_AFTER_SOURCE_REVIEW",DB.as_posix())
            return
        BASE.mkdir(parents=True,exist_ok=True)
        man=exact()
        MAN.write_text(json.dumps(man,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        write_db(DB,man)
        print("CREATED_113_4_CANDIDATES",json.dumps([{"id":q["questionId"],"sha":q["asset"]["sha256"],
              "crop":q["asset"]["cropPixels"],"sourceRevision":q["sourceRevisionSha256"]} for q in man["questions"]],ensure_ascii=False))
    else:
        man=read(MAN);check(man);read_db(DB,man)
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"a.sqlite3";y=Path(td)/"b.sqlite3"
            write_db(x,man);write_db(y,man)
            read_db(x,man);read_db(y,man)
            assert sha(x.read_bytes())==sha(y.read_bytes())==sha(DB.read_bytes())
        print("PASS 113 C07-10 4 candidate WebPs original pixels, dual SQL SHA="+sha(DB.read_bytes())+" NO VERIFIED APPROVAL")
if __name__=="__main__":main()
