#!/usr/bin/env python3
"""Repair only stale 115 SQLite projections of unchanged canonical JSON. No release admission."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "099f26b120fa350c5d88beb8e4642996be1ceac2"
REL = Path("sudu/data/processed/115")
REPORT = REL / "SQLITE_DENORMALIZED_REPAIR_20261114.json"
EXPECTED_COUNTS = {"answer_verified": 77, "question": 1, "question_verified": 1, "review_status": 1}
MAPPING = {"schema_version": "schemaVersion", "year": "year", "paper_code": "paperCode",
           "original_number": "originalQuestionNumber", "subject": "subject", "question": "question",
           "answer": "answer", "answer_matched": "answerMatched", "answer_verified": "answerVerified",
           "question_verified": "questionVerified", "review_status": "reviewStatus"}
BOOLEANS = {"answer_matched", "answer_verified", "question_verified"}
ALLOWED = set(EXPECTED_COUNTS)


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot(dbpath):
    with sqlite3.connect(dbpath.resolve().as_uri() + "?mode=ro", uri=True) as db:
        demand(db.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "SQLite integrity failure")
        schema = db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
        db.row_factory = sqlite3.Row
        rows = {r["question_id"]: dict(r) for r in db.execute("SELECT * FROM questions ORDER BY question_id")}
        shared = [tuple(r) for r in db.execute("SELECT * FROM shared_materials ORDER BY shared_material_id")]
    demand(len(rows) == 205, "Expected 205 distinct database rows")
    return schema, rows, shared


def expected(q, column):
    field = MAPPING[column]
    demand(field in q, f"Missing canonical field {field}")
    value = q[field]
    if column in BOOLEANS:
        demand(type(value) is bool, f"Canonical {field} must be a boolean")
        return int(value)
    return value


def plan(root):
    base = root / REL
    questions = load(base / "questions.json")["questions"]
    indexed = {q["questionId"]: q for q in questions}
    schema, rows, shared = snapshot(base / "question-bank.sqlite3")
    demand(len(questions) == len(indexed) == 205 and set(indexed) == set(rows), "Canonical IDs/count mismatch")
    changes = []
    for qid, saved in rows.items():
        q = indexed[qid]
        payload = saved["payload_json"]
        demand(json.loads(payload) == q, f"Payload mismatch: {qid}")
        demand(sha(payload.encode("utf-8")) == saved["payload_sha256"], f"Payload SHA mismatch: {qid}")
        for column in MAPPING:
            value = expected(q, column)
            if saved[column] != value:
                demand(column in ALLOWED, f"Unexpected projection mismatch: {qid}/{column}")
                changes.append({"questionId": qid, "column": column, "before": saved[column], "after": value})
    return changes, (schema, rows, shared)


def apply(root):
    base = root / REL
    changes, before = plan(root)
    inventory = load(base / "inventory.json")
    demand(inventory["sqlite"]["sourceQuestionsSha256"] == sha((base / "questions.json").read_bytes()), "Inventory source SHA mismatch")
    demand(inventory["sqlite"]["dbSha256"] == sha((base / "question-bank.sqlite3").read_bytes()), "Inventory DB SHA mismatch")
    if not changes:
        return []
    demand(dict(Counter(x["column"] for x in changes)) == EXPECTED_COUNTS, "Unexpected repair counts")
    db_before = sha((base / "question-bank.sqlite3").read_bytes())
    inventory_before = (base / "inventory.json").read_bytes()
    with sqlite3.connect(base / "question-bank.sqlite3") as db:
        for change in changes:
            column = change["column"]  # Whitelisted above; never derived from command-line input.
            result = db.execute(f'UPDATE questions SET "{column}"=? WHERE question_id=? AND "{column}" IS ?',
                                (change["after"], change["questionId"], change["before"]))
            demand(result.rowcount == 1, "Concurrent database change")
    demand(not plan(root)[0], "Repair did not reconcile all projections")
    after = snapshot(base / "question-bank.sqlite3")
    verify_changes(before, after, changes)
    db_after = sha((base / "question-bank.sqlite3").read_bytes())
    inventory["sqlite"]["dbSha256"] = db_after
    (base / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"baseCommit": BASE_COMMIT, "scope": "115_SQLITE_DENORMALIZED_PROJECTIONS_ONLY",
              "rows": 205, "changedRows": len({x["questionId"] for x in changes}),
              "changedCells": len(changes), "countsByColumn": dict(Counter(x["column"] for x in changes)),
              "databaseSha256Before": db_before, "databaseSha256After": db_after,
              "inventorySha256Before": sha(inventory_before),
              "canonicalQuestionsSha256": sha((base / "questions.json").read_bytes()),
              "manifestSha256": sha((base / "webp-manifest.json").read_bytes()),
              "schemaUnchanged": True, "payloadBytesAndHashesUnchanged": True, "sharedMaterialsUnchanged": True,
              "canonicalJsonUnchanged": True, "sourceOrAnswerVerificationGranted": False,
              "studentReady": False, "live": False, "changes": changes}
    (root / REPORT).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changes


def verify_changes(before, after, changes):
    demand(before[0] == after[0] and before[2] == after[2], "Schema/shared materials changed")
    expected_rows = {qid: dict(row) for qid, row in before[1].items()}
    for change in changes:
        demand(change["column"] in ALLOWED, "Forbidden changed column")
        demand(expected_rows[change["questionId"]][change["column"]] == change["before"], "Before-value mismatch")
        expected_rows[change["questionId"]][change["column"]] = change["after"]
    demand(expected_rows == after[1], "Unexpected database row/column/payload change")


def verify(root):
    report = load(root / REPORT)
    demand(report["baseCommit"] == BASE_COMMIT, "Wrong base commit")
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp)
        (original / REL).mkdir(parents=True)
        for name in ("questions.json", "question-bank.sqlite3", "inventory.json", "webp-manifest.json"):
            raw = subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{REL / name}"], cwd=root)
            (original / REL / name).write_bytes(raw)
        changes, before = plan(original)
        demand(changes == report["changes"], "Report differs from actual baseline changes")
        demand(dict(Counter(x["column"] for x in changes)) == EXPECTED_COUNTS, "Baseline counts mismatch")
        demand(not plan(root)[0], "Remaining projection mismatch")
        verify_changes(before, snapshot(root / REL / "question-bank.sqlite3"), changes)
        for name in ("questions.json", "webp-manifest.json"):
            demand((root / REL / name).read_bytes() == (original / REL / name).read_bytes(), f"Immutable {name} changed")
        old_inventory = load(original / REL / "inventory.json")
        expected_inventory = json.loads(json.dumps(old_inventory))
        expected_inventory["sqlite"]["dbSha256"] = sha((root / REL / "question-bank.sqlite3").read_bytes())
        demand(load(root / REL / "inventory.json") == expected_inventory, "Unexpected inventory change")
        demand(report["databaseSha256Before"] == sha((original / REL / "question-bank.sqlite3").read_bytes()), "Original DB SHA")
        demand(report["databaseSha256After"] == expected_inventory["sqlite"]["dbSha256"], "Repaired DB SHA")
        demand(report["studentReady"] is False and report["live"] is False, "Forbidden release verdict")
    print(json.dumps({"status": "115_SQLITE_PROJECTIONS_RECONCILED", "rows": 205,
                      "changedCells": len(changes), "payloadsUnchanged": True, "ready": False, "live": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        demand(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASE_COMMIT,
               "Apply requires the exact frozen QA base")
        print(f"Repaired {len(apply(ROOT))} stale projection cells; no source or release change")
    else:
        verify(ROOT)
