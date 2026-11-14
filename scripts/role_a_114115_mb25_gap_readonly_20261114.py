#!/usr/bin/env python3
"""Source-only, no-mutation 114/115 410-candidate & MB25 official-image gap audit.

The Work MASTER owns MB24 and the 115 questions.json/SQLite write lease.
This auditor never writes 114/115 source, image manifest, SQLite, or issuer data.
"""
from __future__ import annotations
import hashlib
import io
import json
import sqlite3
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_audit_reports"
STAGE = ROOT / "_role_a_original_stage" / "sudu/data/processed/115/source-stage"
AUDIT_ID = "A-114115-MB25-E03-ECON34-READONLY-BASELINE-AUDIT-20261114-01"
QA_BASE = "4e365a75ed98e73223987d81041693a476196881"
PR157_HEAD = "24decc38c6e16e2a22b6204207db1922ce1a1ee8"
EXPECTED = {
    "115-00-MB-24": {
        "stage_name": "115-00-MB-24-stage-20261104.json",
        "stage_blob": "88faf4ee767b20c15db603e91aa250bc59eba84c",
        "webp_sha": "c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb",
        "webp_blob": "cfe5c8eeaf4496d5d98856f96a2c310186ef5893",
        "crop": [90, 614, 1310, 1092],
        "answer": "C",
        "source_revision": "9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267",
    },
    "115-00-MB-25": {
        "stage_name": "115-00-MB-25-stage-20261104.json",
        "stage_blob": "cf1ef0d369e3aced81886a518b47cdeddd4ad175",
        "webp_sha": "92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896",
        "webp_blob": "10adb24ab36c35bd86b63c0d3ab4cb83b757393f",
        "crop": [90, 1102, 1310, 1557],
        "answer": "C",
        "source_revision": "8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f",
    }
}
def bsha(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def path(root:Path, relative:str)->Path: return root/relative
def load(p:Path): return json.loads(p.read_bytes())
def check(cond:bool, msg:str):
    if not cond: raise RuntimeError("READONLY_SOURCE_AUDIT_FAIL_CLOSED: "+msg)

def snapshot_year(year:int):
    base=ROOT/f"sudu/data/processed/{year}"
    bank_path=base/"questions.json"
    db_path=base/"question-bank.sqlite3"
    manifest_path=base/"webp-manifest.json"
    inv_path=base/"inventory.json"
    bank=load(bank_path); manifest=load(manifest_path); inv=load(inv_path)
    questions=bank["questions"]; items=manifest["items"]
    ids=[x["questionId"] for x in questions]; mids=[x["questionId"] for x in items]
    check(len(questions)==205 and len(set(ids))==205, f"{year} bank 205 QIDs")
    check(len(items)==205 and len(set(mids))==205, f"{year} 205 image manifest")
    check(set(ids)==set(mids), f"{year} source/image QID sets")
    with sqlite3.connect("file:"+str(db_path)+"?mode=ro",uri=True) as con:
        intact=con.execute("PRAGMA integrity_check").fetchone()[0]
        cols=[r[1] for r in con.execute("PRAGMA table_info(questions)")]
        db=con.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    check(intact=="ok",f"{year} DB integrity")
    check(len(db)==205 and len(cols)==(7 if year==114 else 14),f"{year} actual DB rows={len(db)} columns={len(cols)} names={cols}; expected 114=7,115=14")
    mapped={q["questionId"]:q for q in questions}
    db_qid=set(row[0] for row in db)
    check(db_qid==set(ids),f"{year} DB canonical QIDs")
    good=sum(1 for qid,payload,h in db if sha(payload.encode())==h and json.loads(payload)==mapped[qid])
    check(good==205,f"{year} 205 JSON DB payload mismatch")
    check(inv["sqlite"]["rows"]==205 and inv["sqlite"]["sourceQuestionsSha256"]==sha(bank_path.read_bytes()) and inv["sqlite"]["dbSha256"]==sha(db_path.read_bytes()),f"{year} inventory hashes")
    return {
       "year":year, "bank":mapped,"manifest":{v["questionId"]:v for v in items},
       "summary":{"questionCount":len(questions),"manifestCount":len(items),"sqliteRows":len(db),
          "sqliteColumns":len(cols),"sqlitePayloadShaAndJsonEqualCount":good,
          "sqliteIntegrity":intact, "bankSha256":sha(bank_path.read_bytes()),
          "sqliteSha256":sha(db_path.read_bytes()),"manifestSha256":sha(manifest_path.read_bytes()),
          "questionVerified":sum(x.get("questionVerified") is True for x in questions),
          "answerVerified":sum(x.get("answerVerified") is True for x in questions),
          "imageQaPass":sum(x.get("qaStatus")=="PASS" for x in items),
          "sourceOnlyUnapproved":inv["sqlite"].get("releaseApproved") is False}
    }

def audit_mb(qid:str, current):
    from PIL import Image,ImageChops
    ep=EXPECTED[qid]
    st_path=STAGE/ep["stage_name"]
    check(st_path.is_file(),qid+" original PR157 stage not checked out")
    raw=st_path.read_bytes()
    check(bsha(raw)==ep["stage_blob"],qid+" PR157 stage GitBlob not same")
    stage=json.loads(raw)
    g2=stage["G2"]; g3=stage["G3"]; o=stage["sourceOriginal"]
    check(stage["questionId"]==qid and o["paper"]=="115-00-MB",qid+" A stage paper")
    check(g2["existingRoleCAuthorSourceRevisionWithoutTable"]==ep["source_revision"],qid+" original C revision")
    check(g3["printedAnswer"]==ep["answer"]=="C",qid+" A original official paper")
    q=current["bank"][qid]; m=current["manifest"][qid]
    check(m["output"]==o["originalSingleWebp"],qid+" manifest path")
    check(m["sha256"]==o["originalSingleSha256"]==ep["webp_sha"],qid+" immutable image SHA")
    check(m["crop"]==o["existingOriginalCrop"]==ep["crop"],qid+" original crop")
    wpath=ROOT / o["originalSingleWebp"]
    ppath=ROOT / o["originalPage"]
    check(wpath.is_file() and ppath.is_file(),qid+" existing original WebP missing")
    webp=wpath.read_bytes(); page=ppath.read_bytes()
    check(webp[:4]==b"RIFF" and webp[8:12]==b"WEBP",qid+" WEBP bytes header")
    check(sha(webp)==ep["webp_sha"] and bsha(webp)==ep["webp_blob"],qid+" WebP binary changed")
    check(sha(page)==o["originalPageSha256"] and bsha(page)==o["originalPageGitBlob"],qid+" original page binary changed")
    w=Image.open(io.BytesIO(webp)).convert("RGB")
    full=Image.open(io.BytesIO(page)).convert("RGB")
    cut=full.crop(tuple(ep["crop"]))
    check(w.size==cut.size==tuple(o["sizePixels"]),qid+" old crop dimensions")
    check(ImageChops.difference(cut,w).getbbox() is None,qid+" original source pixel mismatch")
    # Historic clean A-G2 staging is not yet canonical! Report match/mismatch only.
    qcorrect=(q["question"]==g2["correctedTextQuestion"] and q["options"]==g2["correctedTextOptions"])
    passflags=q.get("questionVerified") is True
    # Validate official printed answer independently from official answer QA ledger and notice.
    cert=load(ROOT/"sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json")
    recs=[r for r in cert["records"] if r["questionId"]==qid]
    check(len(recs)==1 and recs[0]["officialFinalAnswerReadDirectlyFromPublishedImage"]=="C" and recs[0]["answerVerified"],qid+" published answer C original QA")
    notice=load(ROOT/"sudu/data/processed/115/official-confirmation-status.json")
    check(notice["confirmations"]["00-MB"]["officialStatus"]=="no_objection_submitted",qid+" published correction scope")
    check(q["answer"]=="C" and q["officialFinalAnswer"]=="C",qid+" QA answer source")
    negative=deepcopy(m)
    negative["sha256"]="0"*64
    check(negative["sha256"]!=ep["webp_sha"],qid+" SHA negative guard")
    check(not (qid.endswith("25") and g2["correctedTextQuestion"].find("√2")==-1),qid+" printed radius sqrt(2) original")
    check(not (qid.endswith("24") and "110/r" not in g2["correctedTextQuestion"]),qid+" printed complete fraction")
    return {
      "qid":qid,"canonicalQuestionVerified":passflags,
      "canonicalMatchesArchivedOriginalCleanG2":qcorrect,
      "canonicalCurrentOptions":q["options"],
      "canonicalHasOcrContamination":not qcorrect,
      "currentQuestionRevision":(q.get("textQaEvidence") or {}).get("questionRevision") or (q.get("extraction") or {}).get("correctionOverlay",{}).get("sourceRevision"),
      "originalCorrectedQuestion":g2["correctedTextQuestion"],
      "originalCorrectedOptions":g2["correctedTextOptions"],
      "sourceOriginalStageGitBlob":ep["stage_blob"],
      "originalSingleWebpSha256":ep["webp_sha"],"originalWebpPixelEqual":True,
      "webpDimensions":list(w.size),"officialAnswer":"C","officialAnswerVerifiedInOriginalPrintedLedger":True,
      "officialNotice":"no_objection_submitted",
      "originalRoleCSourceRevision":ep["source_revision"],
      "originalRoleCTeachingDigest":g2["existingRoleCAuthorTeachingDigest"],
      "sourceG1ImagePass":True,
      "formalNativePublisherG2G3FromCurrentQa":"NOT_TESTED_READONLY",
      "studentReady":False
    }

def focused(ys):
    summary=[]
    for year,qid in [(114,"114-00-E-11"),(114,"114-00-E-12"),(115,"115-00-MB-20"),
                     (115,"115-00-MB-21"),(115,"115-00-MB-22"),(115,"115-00-MB-23"),
                     (115,"115-00-MB-24"),(115,"115-00-MB-25")]:
        s=ys[year]
        q=s["bank"].get(qid)
        im=s["manifest"].get(qid)
        summary.append({
          "qid":qid,"exists":bool(q),"sourceQuestionVerified":q.get("questionVerified") if q else None,
          "answerVerified":q.get("answerVerified") if q else None,
          "originalWebpSha256":im.get("sha256") if im else None,
          "manifestQaStatus":im.get("qaStatus") if im else None,
          "publishedFinalAnswer":q.get("officialFinalAnswer") if q else None,
          "sourceRevision":(q.get("textQaEvidence") or {}).get("questionRevision") if q else None
        })
    return summary

def diagnose_additional(ys):
    rows=ys[115]["bank"]
    chosen={}
    for target in ["115 English E03","115 Economics 34"]:
        c=[]
        for qid,q in rows.items():
            subj=str(q.get("subject",""))
            if target=="115 English E03" and qid.endswith("E-03") and ("00-E" in qid or "英文" in subj): c.append(qid)
            if target=="115 Economics 34" and qid.endswith("-34") and ("經濟" in subj or qid.startswith("115-09-2")):c.append(qid)
        chosen[target]=[
            {"qid":qid,"subject":rows[qid].get("subject"),
             "questionVerified":rows[qid].get("questionVerified"),
             "answerVerified":rows[qid].get("answerVerified"),
             "imageQaStatus":ys[115]["manifest"].get(qid,{}).get("qaStatus"),
             "originalImageSha256":ys[115]["manifest"].get(qid,{}).get("sha256"),
             "issues":rows[qid].get("issues",[]),
             "questionExcerpt":rows[qid].get("question","")[:230],
             "options":rows[qid].get("options",[]) }
             for qid in c]
    return chosen

def main():
    years={n:snapshot_year(n) for n in (114,115)}
    report={
        "taskId":AUDIT_ID,"status":"READ_ONLY_SOURCE_GAP_AUDIT_NOT_NATIVE_G2G3_ADMISSION",
        "officialQaBase":QA_BASE,"archivedOriginalPR157":PR157_HEAD,
        "activeForeignLease":"Issue36#6873884674 MB24 shared bank/SQLite — DO NOT MODIFY",
        "counts":{str(k):v["summary"] for k,v in years.items()},
        "candidateTotal":sum(v["summary"]["questionCount"] for v in years.values()),
        "focused":focused(years),
        "mathOriginal":{qid:audit_mb(qid,years[115]) for qid in EXPECTED},
        "otherGaps":diagnose_additional(years),
        "expectedNextAction":"MB25 one-Q source CLAIM only after MB24 original owner releases shared database lease and official QA HEAD refresh; source G2 G3 postcommit real CI needed.",
        "formalETrust":False,"formalDRealEmitter16":False,"newStudentReady":False,"newLive":False
    }
    check(report["candidateTotal"]==410,"410 candidate-only source records not present")
    OUT.mkdir(exist_ok=True)
    (OUT/"role-a-mb25-readonly-gap-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ROLE_A_AUDIT_REPORT_BEGIN")
    print(json.dumps(report,ensure_ascii=False))
    print("ROLE_A_AUDIT_REPORT_END")
    print("READ_ONLY_PASS: both years 205 JSON+SQLite+manifest QID parity; no source bytes modified")
if __name__=="__main__": main()
