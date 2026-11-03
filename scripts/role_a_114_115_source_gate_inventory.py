#!/usr/bin/env python3
"""ROLE A: READ-ONLY audit of 410 source candidates; never a G1 visual/G2/G3/E/D/READY admission."""
from __future__ import annotations
import hashlib
import json
import sqlite3
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed"
OUT = ROOT / "docs/ROLE_A_114_115_SOURCE_GATES_20261103.json"
AUDIT_BASE_SHA = "e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5"
YEARS = (114, 115)
EXPECTED = 205

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def is_real_webp(raw: bytes) -> bool:
    return len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"

@lru_cache(maxsize=2048)
def asset_info(rel: str) -> dict:
    if not rel or not isinstance(rel, str):
        return {"present":False, "sha256":None, "isWebp":False}
    # All referenced inputs must stay within the repository checkout.
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as e:
        raise ValueError("unsafe out-of-repo source asset: %s" % rel) from e
    if not path.is_file():
        return {"present":False, "sha256":None, "isWebp":False}
    raw = path.read_bytes()
    return {"present":True, "sha256":sha256(raw), "isWebp":is_real_webp(raw)}

def inspect_asset(path: str | None, expected_sha: str | None) -> dict:
    info = asset_info(path or "")
    matched = bool(info["present"] and info["isWebp"] and expected_sha and info["sha256"] == expected_sha)
    return {
        "path":path,
        "present":info["present"],
        "isWebp":info["isWebp"],
        "expectedSha256":expected_sha,
        "actualSha256":info["sha256"],
        "shaMatched":matched,
    }

def inspect_db(year: int) -> dict:
    path = BASE / str(year) / "question-bank.sqlite3"
    if not path.is_file():
        return {"filePresent":False, "integrityCheck":None,"tableRowCounts":{}}
    con = sqlite3.connect("file:"+str(path)+"?mode=ro", uri=True)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        tables = sorted(row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        counts={}
        for table in tables:
            # SQLite quote quoted identifiers derived solely from sqlite_master.
            ident = '"' + table.replace('"','""') + '"'
            counts[table] = con.execute("SELECT COUNT(*) FROM "+ident).fetchone()[0]
        return {"filePresent":True, "integrityCheck":integrity,"tableRowCounts":counts}
    finally:
        con.close()

def one_year(year: int) -> dict:
    directory=BASE / str(year)
    qpath=directory / "questions.json"
    mpath=directory / "webp-manifest.json"
    bank=json.loads(qpath.read_text(encoding="utf-8"))
    manifest=json.loads(mpath.read_text(encoding="utf-8"))
    qs=bank["questions"]
    images=manifest["items"]
    if bank.get("year") != year or manifest.get("year") != year:
        raise ValueError("year mismatch")
    qids=[x["questionId"] for x in qs]
    mids=[x["questionId"] for x in images]
    if len(qids)!=EXPECTED or len(mids)!=EXPECTED or len(set(qids))!=EXPECTED or len(set(mids))!=EXPECTED:
        raise ValueError("duplicate or missing canonical year QID "+str(year))
    if set(qids)!=set(mids):
        raise ValueError("canonical and image manifest QID sets disagree year "+str(year))
    image_map={x["questionId"]:x for x in images}
    shared=manifest.get("sharedMaterialCrops") or []
    shared_records=[]
    shared_index=defaultdict(list)
    for s in shared:
        sid=s.get("sharedMaterialId",s.get("id"))
        qa=s.get("qaStatus","UNKNOWN")
        obj=inspect_asset(s.get("output"), s.get("sha256"))
        source=inspect_asset(s.get("source"),s.get("sourceSha256"))
        material={"id":sid,"questionNumbers":s.get("originalQuestionNumbers",[]),
                  "paperCode":s.get("paperCode"),"historicalManifestQaStatus":qa,
                  "originalShared":obj,"originalPage":source}
        shared_records.append(material)
        for n in s.get("originalQuestionNumbers",[]):
            shared_index[(s.get("paperCode"),n)].append(material)
    rows=[]
    per_paper=defaultdict(Counter)
    counts=Counter()
    for q in sorted(qs,key=lambda x:x["questionId"]):
        qid=q["questionId"]; im=image_map[qid]
        if q.get("year")!=year or im.get("paperCode")!=q.get("paperCode"):
            raise ValueError("question/manifest paper mismatch: "+qid)
        if q.get("originalQuestionNumber")!=im.get("originalQuestionNumber"):
            raise ValueError("question/manifest number mismatch: "+qid)
        num=q.get("originalQuestionNumber")
        paper=q.get("paperCode")
        source=inspect_asset(im.get("source"),im.get("sourceSha256"))
        single=inspect_asset(im.get("output"),im.get("sha256"))
        historicalG1 = im.get("qaStatus")=="PASS"
        historicalG1WithRealAsset = historicalG1 and single["shaMatched"] and source["shaMatched"]
        q_verified=q.get("questionVerified") is True
        a_verified=q.get("answerVerified") is True
        requiredShared=shared_index.get((paper,num),[])
        issues=[]
        if not single["present"]:issues.append("SINGLE_WEBP_FILE_MISSING_IN_BASE")
        elif not single["shaMatched"]:issues.append("SINGLE_WEBP_SHA_OR_FORMAT_MISMATCH")
        if not source["present"]:issues.append("SOURCE_PAGE_WEBP_MISSING_IN_BASE")
        elif not source["shaMatched"]:issues.append("SOURCE_PAGE_SHA_OR_FORMAT_MISMATCH")
        if not historicalG1:issues.append("HISTORICAL_MANIFEST_G1_QA_NOT_PASS")
        elif not historicalG1WithRealAsset:issues.append("HISTORICAL_G1_PASS_BUT_SOURCE_ASSET_MISSING_OR_MISMATCH")
        for ref in requiredShared:
            if not ref["originalShared"]["shaMatched"]:
                issues.append("SHARED_WEBP_MISSING_OR_MISMATCH:"+str(ref["id"]))
            if ref["historicalManifestQaStatus"]!="PASS":
                issues.append("HISTORICAL_SHARED_G1_QA_NOT_PASS:"+str(ref["id"]))
        if not q_verified:issues.append("CANONICAL_QUESTION_VERIFIED_FLAG_FALSE_NOT_G2")
        if not a_verified:issues.append("CANONICAL_ANSWER_VERIFIED_FLAG_FALSE_NOT_G3")
        row={"qid":qid,"year":year,"paperCode":paper,"number":num,
             "subject":q.get("subject"),"historicalManifestG1Status":im.get("qaStatus","UNKNOWN"),
             "historicalG1ManifestPass":historicalG1,
             "historicalG1PassWithMatchingBytes":historicalG1WithRealAsset,
             "sourceSingleWebp":single,"sourcePageWebp":source,
             "sharedIds":[r["id"] for r in requiredShared],
             "canonicalQuestionVerifiedFlag":q_verified,
             "canonicalAnswerVerifiedFlag":a_verified,
             "issues":issues}
        rows.append(row)
        counts["sourceSingleWebpPresent"] += int(single["present"])
        counts["sourceSingleWebpShaMatch"] += int(single["shaMatched"])
        counts["sourcePageWebpShaMatch"] += int(source["shaMatched"])
        counts["historicalG1ManifestPass"] += int(historicalG1)
        counts["historicalG1PassWithMatchingBytes"] += int(historicalG1WithRealAsset)
        counts["canonicalQuestionVerifiedFlagTrue"] += int(q_verified)
        counts["canonicalAnswerVerifiedFlagTrue"] += int(a_verified)
        counts["candidatesWithAnyGapOrUnverifiedFlag"] += int(bool(issues))
        p=per_paper[paper]
        p["total"]+=1
        p["imageBytesValid"]+=int(single["shaMatched"] and source["shaMatched"])
        p["historicalG1ManifestPass"]+=int(historicalG1)
        p["historicalG1WithByteEvidence"]+=int(historicalG1WithRealAsset)
        p["canonicalQuestionVerifiedTrue"]+=int(q_verified)
        p["canonicalAnswerVerifiedTrue"]+=int(a_verified)
    counts["sourceCandidates"]=len(rows)
    counts["sharedMaterialCount"]=len(shared_records)
    counts["sharedWebpBytesValid"]=sum(int(x["originalShared"]["shaMatched"]) for x in shared_records)
    counts["historicalSharedManifestPass"]=sum(int(x["historicalManifestQaStatus"]=="PASS") for x in shared_records)
    return {
        "year":year,
        "canonicalQuestionsSha256":sha256(qpath.read_bytes()),
        "manifestSha256":sha256(mpath.read_bytes()),
        "summary":dict(sorted(counts.items())),
        "byPaper":{k:dict(sorted(v.items())) for k,v in sorted(per_paper.items())},
        "sqliteReadOnly":inspect_db(year),
        "questions":rows,
        "sharedOriginals":shared_records
    }

def build() -> dict:
    years=[one_year(y) for y in YEARS]
    totals=Counter()
    for y in years:
        for k,v in y["summary"].items():
            if isinstance(v,int): totals[k]+=v
    assert sum(y["summary"]["sourceCandidates"] for y in years)==410
    return {
       "schemaVersion":1,
       "type":"ROLE_A_ANNUAL_410_READ_ONLY_SOURCE_GAP_INVENTORY_NOT_G1_G2_G3_READY",
       "snapshotSourceBaseCommit":AUDIT_BASE_SHA,
       "auditDateLabel":"2026-11-03",
       "scope":"114 and 115 (205 canonical source candidate rows each); old PR35 base only",
       "notMergedIndependentLaterSourcePRs":[120,126,123,131,129],
       "gateDefinitions":{
           "sourceSingleWebpShaMatch":"Exactly matching stored SHA256 and WebP signature; NOT human/AI direct original visual review.",
           "historicalG1ManifestPass":"Previously stored manifest qaStatus PASS only; not new image validation.",
           "historicalG1PassWithMatchingBytes":"Historical PASS with existing single and page file SHA; still not newly reviewed by this script.",
           "canonicalQuestionVerifiedFlag":"Existing source Boolean only. False is a pending source G2 review; true does not imply independent E.",
           "canonicalAnswerVerifiedFlag":"Existing source Boolean only. Does not replace per-QID last official correction scope or MASTER admission.",
           "sharedOriginals":"Historical shared items and source bytes; no inheritance of shared QA as individual QID approval.",
           "sourceCandidates":"410 input rows, not 410 official individually verified or published questions.",
           "formalREADYorLIVE":"NOT EVALUATED; never infer from source flags."
       },
       "overallSummary":dict(sorted(totals.items())),
       "years":years,
       "status":"SOURCE_FILES_READONLY_INSPECTED; NO G1 VISUAL, G2 TEXT, G3 FINAL, E, D OR RELEASE PASS GENERATED"
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args=ap.parse_args()
    report=build()
    output=Path(args.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    summary={"total":report["overallSummary"].get("sourceCandidates",0),
             "years":[{"year":x["year"],"summary":x["summary"],"sqlite":x["sqliteReadOnly"]} for x in report["years"]],
             "reportFile":str(output),"auditType":report["type"]}
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
