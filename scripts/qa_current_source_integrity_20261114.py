#!/usr/bin/env python3
"""Read-only current bank payload integrity; no historic one-PR whitelist or release verdict.

Checks all 14 SQLite columns for 115, including strict canonical boolean projections.
A PASS is not complete source/answer/teaching admission.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_year(root, year):
    base = root / "sudu/data/processed" / str(year)
    rows = json.loads((base / "questions.json").read_text(encoding="utf-8"))["questions"]
    by_id = {q["questionId"]: q for q in rows}
    demand(len(rows) == len(by_id) == 205, f"{year}: exactly 205 unique canonical questions")
    demand(all(q["year"] == year for q in rows), f"{year}: canonical year mismatch")
    manifest = json.loads((base / "webp-manifest.json").read_text(encoding="utf-8"))["items"]
    demand(len(manifest) == 205 and {x["questionId"] for x in manifest} == set(by_id),
           f"{year}: manifest IDs/count mismatch")
    dbpath = base / "question-bank.sqlite3"
    with sqlite3.connect(dbpath.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        demand(db.execute("PRAGMA integrity_check").fetchall() == [("ok",)], f"{year}: corrupt SQLite")
        db.row_factory = sqlite3.Row
        stored = list(db.execute("SELECT * FROM questions"))
        demand(len(stored) == 205 and {x["question_id"] for x in stored} == set(by_id),
               f"{year}: SQLite IDs/count mismatch")
        for saved in stored:
            q = by_id[saved["question_id"]]
            payload = saved["payload_json"]
            demand(json.loads(payload) == q, f"{year}: JSON/SQLite mismatch {saved['question_id']}")
            demand(hashlib.sha256(payload.encode("utf-8")).hexdigest() == saved["payload_sha256"],
                   f"{year}: payload SHA mismatch {saved['question_id']}")
            columns = {"year": "year", "paper_code": "paperCode", "original_number": "originalQuestionNumber",
                       "subject": "subject"}
            for column, field in columns.items():
                if column in saved.keys():
                    demand(saved[column] == q.get(field),
                           f"{year}: denormalized {column} mismatch {saved['question_id']}")
    if year == 115:
        # Current-state projection checks; no frozen historic one-PR baseline.
        from role_a_115_sqlite_denorm_repair_20261114 import plan
        differences, _ = plan(root)
        demand(not differences, "115: stale denormalized projection")
    inventory = json.loads((base / "inventory.json").read_text(encoding="utf-8"))["sqlite"]
    demand(inventory["rows"] == 205 and inventory["roundtripPass"] is True, f"{year}: inventory rows/status")
    demand(inventory["dbSha256"] == sha(dbpath), f"{year}: inventory database SHA")
    demand(inventory["sourceQuestionsSha256"] == sha(base / "questions.json"), f"{year}: inventory bank SHA")
    return {"year": year, "rows": 205, "jsonSqlitePayloadManifestIntegrity": "PASS", "denormalizedColumnParity": "14_OF_14_PASS" if year == 115 else "CORE_METADATA_PASS", "studentReleaseVerdict": "NOT_EVALUATED"}


if __name__ == "__main__":
    for year in (114, 115):
        print(json.dumps(check_year(ROOT, year), ensure_ascii=False))
