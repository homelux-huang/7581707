#!/usr/bin/env python3
"""Non-destructive 115 corpus SQLite build and GitHub Pages JSON export.

Only writes the explicitly chosen output paths. Never touches backend/private.sqlite3
or any student, attempt, teaching, or device state.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "sudu/data/processed/115/questions.json"
DEFAULT_DB = ROOT / "sudu/data/processed/115/question-bank.sqlite3"
DEFAULT_EXPORT = ROOT / "sudu/data/processed/115/pages-questions.json"

DDL = """
CREATE TABLE IF NOT EXISTS questions (
  question_id TEXT PRIMARY KEY NOT NULL,
  schema_version INTEGER NOT NULL,
  year INTEGER NOT NULL CHECK (year=115),
  paper_code TEXT NOT NULL,
  original_number INTEGER NOT NULL,
  subject TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT,
  answer_matched INTEGER NOT NULL CHECK(answer_matched IN (0,1)),
  answer_verified INTEGER NOT NULL CHECK(answer_verified IN (0,1)),
  question_verified INTEGER NOT NULL CHECK(question_verified IN (0,1)),
  review_status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  UNIQUE (year,paper_code,original_number)
);
CREATE TABLE IF NOT EXISTS shared_materials (
  shared_material_id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS questions_subject_idx ON questions(subject,original_number);
"""

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def verify(data):
    if data.get("year") != 115:
        raise ValueError("Only 115 year corpus is permitted")
    questions = data["questions"]
    if len(questions) != 205:
        raise ValueError(f"115 question count changed from inventory: {len(questions)}")
    seen = set()
    per_paper = {}
    for q in questions:
        paper = q["paperCode"]
        number = q["originalQuestionNumber"]
        key = (115, paper, number)
        if key in seen:
            raise ValueError(f"duplicate original key: {key}")
        seen.add(key)
        required_id = f"115-{paper}-{number:02d}"
        if q["questionId"] != required_id:
            raise ValueError(f"canonical ID drift: {q['questionId']} != {required_id}")
        if q["year"] != 115 or len(q["options"]) != 4:
            # Unresolved source gaps must be explicitly marked, not repaired by invention.
            if q["year"] != 115 or not q["issues"]:
                raise ValueError(f"bad year or unexplained missing options: {required_id}")
        if q.get("answer") is not None and q["answer"] not in ("A","B","C","D"):
            raise ValueError(f"unrecognized answer value: {required_id}")
        if q.get("answerVerified") or q.get("questionVerified"):
            # This import cannot confer official verification.
            raise ValueError(f"unexpected unreviewed verified flag: {required_id}")
        per_paper.setdefault(paper, set()).add(number)
    for paper, expected in {"00-C":38,"00-E":42,"00-MB":25,"09-1":50,"09-2":50}.items():
        if per_paper.get(paper, set()) != set(range(1, expected+1)):
            raise ValueError(f"gaps or wrong number sequence: {paper}")
    return questions

def run(input_path, db_path, export_path):
    data = json.loads(input_path.read_text(encoding="utf-8"))
    questions = verify(data)
    if db_path.resolve() == (ROOT / "backend/private.sqlite3").resolve():
        raise ValueError("Never modify student database")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as cx:
        cx.executescript(DDL)
        for q in questions:
            blob = canonical(q)
            cx.execute(
                """INSERT INTO questions(question_id,schema_version,year,paper_code,
                original_number,subject,question,answer,answer_matched,
                answer_verified,question_verified,review_status,payload_json,payload_sha256)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(question_id) DO UPDATE SET
                schema_version=excluded.schema_version,subject=excluded.subject,
                question=excluded.question,answer=excluded.answer,
                answer_matched=excluded.answer_matched,answer_verified=excluded.answer_verified,
                question_verified=excluded.question_verified,review_status=excluded.review_status,
                payload_json=excluded.payload_json,payload_sha256=excluded.payload_sha256
                """,
                (q["questionId"],q["schemaVersion"],115,q["paperCode"],
                 q["originalQuestionNumber"],q["subject"],q["question"],q.get("answer"),
                 int(q["answerMatched"]),int(q["answerVerified"]),int(q["questionVerified"]),
                 q["reviewStatus"],blob,hashlib.sha256(blob.encode()).hexdigest())
            )
        for item in data["sharedMaterials"]:
            cx.execute("""INSERT INTO shared_materials(shared_material_id,payload_json)
                VALUES(?,?) ON CONFLICT(shared_material_id)
                DO UPDATE SET payload_json=excluded.payload_json""",
                (item["sharedMaterialId"], canonical(item)))
        cx.commit()
        count = cx.execute("SELECT COUNT(*) FROM questions WHERE year=115").fetchone()[0]
        if count != len(questions):
            raise AssertionError(f"roundtrip count mismatch: {count}")
        by_id = {json.loads(row[0])["questionId"]: json.loads(row[0]) for row
                 in cx.execute("SELECT payload_json FROM questions WHERE year=115")}
        for q in questions:
            if by_id[q["questionId"]] != q:
                raise AssertionError(f"roundtrip data mismatch: {q['questionId']}")
        print(f"PASS SQLite roundtrip: {count} records; rerun is idempotent")
    export = {"schemaVersion":data["schemaVersion"],"year":115,
              "generatedFromMain":data["generatedFromMain"],
              "notice":data["notice"],"questions":questions,
              "sharedMaterials":data["sharedMaterials"]}
    export_path.write_text(json.dumps(export,ensure_ascii=False,separators=(",",":"))+"\n",
                           encoding="utf-8")
    print(f"PASS static JSON export: {export_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=DEFAULT_INPUT)
    parser.add_argument("--db",type=Path,default=DEFAULT_DB)
    parser.add_argument("--export",type=Path,default=DEFAULT_EXPORT)
    args=parser.parse_args()
    run(args.input,args.db,args.export)
