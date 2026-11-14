#!/usr/bin/env python3
"""Promote already validated isolated 105/114 SQLite v2 into QA database, never LIVE.

This corrects stale on-disk QA payloads only after SHA-bound source comparison.
Preserves old DB in Git history and immutable v2 staging files. No QA flag promotions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "sudu/data/processed"
YEARS = (105, 114)

def sha(payload):
    return hashlib.sha256(payload).hexdigest()

def canonical(q):
    return json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def validate_candidate(year):
    base = PROCESSED / str(year)
    report = read(base / f"qa-drafts/SQLITE_{year}_V2_STAGING_20261023.json")
    src = base / "questions.json"
    old = base / "question-bank.sqlite3"
    v2 = base / "qa-drafts/sqlite-v2/question-bank.sqlite3"
    rows = read(src)["questions"]
    n = len(rows)
    assert n == report["rows"] and report["isolatedImportPasses"] == 2
    assert report["originalDatabaseModified"] is False and report["integrationReady"] is False
    assert sha(src.read_bytes()) == report["sourceQuestionsSha256"], f"{year} changed questions; no stale promotion"
    assert sha(v2.read_bytes()) == report["qaDraftDbSha256"], f"{year} staged DB changed"
    assert sha(old.read_bytes()) == report["originalDatabaseSha256Unchanged"], f"{year} original DB changed"
    assert len({q["questionId"] for q in rows}) == n
    assert len({(q["year"],q["paperCode"],q["originalQuestionNumber"]) for q in rows}) == n
    wanted = {q["questionId"]:q for q in rows}
    with sqlite3.connect(v2.resolve().as_uri()+"?mode=ro",uri=True) as cx:
        cx.execute("PRAGMA query_only=ON")
        assert cx.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        cols = {r[1] for r in cx.execute("PRAGMA table_info(questions)")}
        col = "payload" if "payload" in cols else "payload_json"
        rows_db = cx.execute("SELECT question_id, year, paper_code, original_number, "+col+",payload_sha256 FROM questions").fetchall()
        assert len(rows_db) == n
        for qid,y,paper,num,payload,digest in rows_db:
            q = wanted[qid]
            assert (y,paper,num) == (year,q["paperCode"],q["originalQuestionNumber"])
            assert json.loads(payload) == q and sha(payload.encode("utf-8")) == digest
        shared=read(src).get("sharedMaterials", [])
        actual_shared = cx.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]
        assert actual_shared == len(shared) == report["sharedMaterialRows"]
        for sid,payload in cx.execute("SELECT material_id,payload FROM shared_materials"):
            match = [m for m in shared if m["sharedMaterialId"] == sid]
            assert len(match) == 1 and json.loads(payload) == match[0]
    return {"year":year,"sourceQuestionsSha256":report["sourceQuestionsSha256"],
            "oldQaDatabaseSha256":report["originalDatabaseSha256Unchanged"],
            "promotedQaDatabaseSha256":report["qaDraftDbSha256"],
            "rows":n,"sharedMaterials":report["sharedMaterialRows"],
            "twoPassAlreadyValidated":True,"newImageQaPass":0,
            "newAnswerVerified":0,"releaseAllowed":False,"integrationReady":False}

def run(stage):
    infos = [validate_candidate(y) for y in YEARS]
    if not stage:
        print(json.dumps({"mode":"check","candidates":infos,"studentDataTouched":False},ensure_ascii=False))
        return
    from audit_105_115_sqlite_readonly import audit_year
    for info in infos:
        year=info["year"]
        previous=audit_year(year)
        assert previous["sandboxImportPasses"]==2
        assert previous["blockers"] == ["on_disk_payload_or_SHA_mismatch"], (
            year, previous["blockers"])
    for info in infos:
        year=info["year"]
        base=PROCESSED / str(year)
        src=base/"qa-drafts/sqlite-v2/question-bank.sqlite3"
        dst=base/"question-bank.sqlite3"
        with tempfile.NamedTemporaryFile(dir=base,suffix=".sqlite3",delete=False) as handle:
            name=handle.name
        try:
            shutil.copyfile(src,name)
            assert sha(Path(name).read_bytes()) == info["promotedQaDatabaseSha256"]
            os.replace(name,dst)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        assert audit_year(year)["g5Pass"] is True, f"G5 failed after {year} promotion"
        write(base/f"qa-drafts/SQLITE_{year}_G5_RECONCILED_20261024.json",info)
    # The 110 inventory's old 'sqlite.rows=205' contradicts the actual 204-row DB.
    base110=PROCESSED/"110"
    inv=read(base110/"inventory.json")
    audit110=audit_year(110)
    assert audit110["g5Pass"] and audit110["onDiskRows"] == 204
    assert inv["totalCandidateQuestions"] == 204
    assert inv["sqlite"]["rows"] == 205 and inv["sqlite"]["unique"] == 205
    inv["sqlite"]["rows"] = 204
    inv["sqlite"]["unique"] = 204
    inv["sqlite"]["correctionEvidence"] = (
        "105-115-SQLITE_G5_READONLY_AUDIT.json; exact 204 rows, "
        "false extra 110-09-1-80 already quarantined"
    )
    write(base110/"inventory.json",inv)
    results=[audit_year(y) for y in range(105,116)]
    assert len(results)==11 and all(q["g5Pass"] and q["sandboxImportPasses"]==2 for q in results), (
        [(x["year"],x["blockers"]) for x in results])
    report={"scope":"105-115","sourceDatabasesModified":True,
            "modificationScope":"QA isolated 105/114 database only, no student database",
            "studentDataTouched":False,"released":False,"yearsG5Pass":11,
            "yearsReviewed":11,"years":results}
    write(PROCESSED/"105-115-SQLITE_G5_READONLY_AUDIT.json",report)
    print(json.dumps({"mode":"reconciled","yearsG5Pass":11,"yearsReviewed":11,
                      "sqliteQaDatabasesRefreshed":[105,114],
                      "year110InventoryCorrection":"205 to 204, exact persisted DB",
                      "newImageQaPass":0,"newAnswerVerified":0,
                      "released":False,"studentDataTouched":False},ensure_ascii=False))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    args=p.parse_args()
    run(args.stage)
