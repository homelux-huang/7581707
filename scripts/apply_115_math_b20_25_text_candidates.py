#!/usr/bin/env python3
"""Stage Math B 20-25 exact source-image text; never grant QA or student release.

This is a separate, review-only candidate branch. The original years/115.json
and original OCR/WebP remain unchanged. Six candidates never become officially
published without their own independent admission certificates.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
ID_SET={f"115-00-MB-{n:02d}" for n in range(20,26)}
LEDGER=BASE/"review-evidence/MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(data): return hashlib.sha256(data).hexdigest()
def canon(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def dump(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def read_db(file,expected):
    with sqlite3.connect(file) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        cols={r[1] for r in db.execute("PRAGMA table_info(questions)")}
        field="payload" if "payload" in cols else "payload_json"
        assert {"question_id",field,"payload_sha256"}<=cols
        rows=db.execute("SELECT question_id,"+field+",payload_sha256 FROM questions").fetchall()
        assert len(rows)==len(expected)==205
        seen=set()
        for qid,payload,h in rows:
            assert qid in expected and qid not in seen
            seen.add(qid)
            assert sha(payload.encode("utf-8"))==h,qid
            assert json.loads(payload)==expected[qid],qid
        return field

def prepare(stage):
    ledger=load(LEDGER)
    assert ledger["year"]==115 and ledger["formalTextQaPass"] is False
    refs=ledger["items"]
    assert {x["qid"] for x in refs}==ID_SET and len(refs)==6
    bank=load(BASE/"questions.json")
    questions=bank["questions"]
    assert len(questions)==205
    byid={x["questionId"]:x for x in questions}
    assert len(byid)==205 and ID_SET<=set(byid)
    original_other={qid:canon(q) for qid,q in byid.items() if qid not in ID_SET}
    manifest=load(BASE/"webp-manifest.json")
    images={x["questionId"]:x for x in manifest["items"]}
    source=load(ROOT/"sudu/data/years/115.json")
    old={q["id"]:q for p in source["papers"] if p["paper"]=="00-MB" for q in p["questions"]}
    dbpath=BASE/"question-bank.sqlite3"
    field=read_db(dbpath,byid)
    modifications=[]
    evidence=[]
    for item in refs:
        qid=item["qid"]
        correction=load(ROOT/item["entry"])
        assert correction["questionId"]==qid and correction["year"]==115
        assert correction["status"]["formalIndependentHumanTextQaPass"] is False
        assert correction["status"]["studentReleaseApproved"] is False
        assert correction["status"]["deploy"] is False
        assert correction["noNewOCR"] is True and correction["noNewWebpCropping"] is True
        image=images[qid]
        assert image["qaStatus"]=="PASS"
        assert image["sha256"]==item["sourceWebpSha256"]==correction["sourceWebpSha256"]
        assert image["visualReviewEvidence"]["reviewedSha256"]==image["sha256"]
        assert sha((ROOT/image["output"]).read_bytes())==image["sha256"]
        q=byid[qid]
        assert q["paperCode"]=="00-MB" and q["year"]==115
        assert q["questionProvenance"]["pdfSha256"]==correction["originalQuestionPdfSha256"]
        assert q["assets"]["sha256"]==image["sha256"]
        assert q["answer"]==correction["knownOfficialAnswer"] and q["answerMatched"] is True
        assert q.get("questionVerified") is not True and q.get("textQaStatus")!="PASS",qid
        assert q.get("studentReleaseApproved") is not True and q.get("integrationReady") is not True
        prev=correction["legacyUncorrectedSource"]
        new=correction["correctedText"]
        assert old[qid]["question"]==prev["question"] and old[qid]["options"]==prev["options"]
        assert isinstance(new["question"],str) and new["question"]
        assert len(new["options"])==4 and all(isinstance(z,str) and z for z in new["options"])
        assert new.get("figureRequired") is True
        assert not any("公告試題僅供參考" in z or "以下空白" in z for z in new["options"])
        if qid=="115-00-MB-23":
            assert len(new["table"]["rows"])==2 and all(len(row)==3 for row in new["table"]["rows"])
        if qid=="115-00-MB-25":
            assert "√2" in new["question"] and "距離為 2" not in new["question"]
        already=q["question"]==new["question"] and q["options"]==new["options"]
        if already:
            assert q.get("legacyUnverifiedQuestion")==prev["question"]
            assert q.get("legacyUnverifiedOptions")==prev["options"]
            assert q.get("formalTextApproval") is not True
        else:
            assert q["question"]==prev["question"],qid+" unexpected canonical stem; fail closed"
            assert q["options"]==prev["options"],qid+" unexpected options; fail closed"
            assert "legacyUnverifiedQuestion" not in q and "legacyUnverifiedOptions" not in q
            if stage:
                q["legacyUnverifiedQuestion"]=prev["question"]
                q["legacyUnverifiedOptions"]=prev["options"]
                q["question"]=new["question"]
                q["options"]=new["options"]
                q["originalWebpTextCorrectionCandidate"]=item["entry"]
                q["sourceFigureRequired"]=True
                if new.get("table"):
                    q["originalSourceTableCandidate"]=new["table"]
                q["formalTextApproval"]=False
                q["reviewStatus"]="source_text_image_corrected_pending_independent_admission"
                q["integrationReady"]=False
                q["studentReleaseApproved"]=False
                modifications.append(qid)
        evidence.append({"questionId":qid,"webpSha256":image["sha256"],
                         "staged":stage,"alreadyCorrected":already,
                         "studentReady":False,"questionVerified":q.get("questionVerified")})
    if stage and modifications:
        with sqlite3.connect(dbpath) as db:
            for qid in modifications:
                wire=canon(byid[qid])
                h=sha(wire.encode("utf-8"))
                assert db.execute("UPDATE questions SET "+field+"=?,payload_sha256=? WHERE question_id=?",
                    (wire,h,qid)).rowcount==1,qid
            db.commit()
        dump(BASE/"questions.json",bank)
    persisted=load(BASE/"questions.json")
    persisted_map={q["questionId"]:q for q in persisted["questions"]}
    assert len(persisted_map)==205
    read_db(dbpath,persisted_map)
    assert all(canon(persisted_map[qid])==original_other[qid] for qid in original_other)
    assert all(persisted_map[qid].get("studentReleaseApproved") is not True for qid in ID_SET)
    assert all(persisted_map[qid].get("questionVerified") is not True for qid in ID_SET)
    # Preserve original uncorrected year record, historical OCR and final keys.
    assert len(load(ROOT/"sudu/data/years/115.json")["papers"])>=5
    return {"scope":205,"target":sorted(ID_SET),"changed":modifications,
            "dbRoundtripPass":True,"originalOther199ByteCanonicalUnchanged":True,
            "newQuestionVerificationApprovals":0,"newStudentReleaseApprovals":0,
            "originalOCRAndYearsUnchanged":True,"evidence":evidence}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    opts=p.parse_args()
    print(json.dumps(prepare(opts.stage),ensure_ascii=False,indent=2))
