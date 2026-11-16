#!/usr/bin/env python3
"""Isolated 114 corpus SQLite builder; preserve incomplete records as flagged drafts."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"sudu/data/processed/114"
data=json.loads((D/"questions.json").read_text(encoding="utf-8"))
questions=data["questions"]
assert data["year"]==114 and len(questions)==205
assert len({q["questionId"] for q in questions})==205
expected={"00-C":38,"00-E":42,"00-MB":25,"09-1":50,"09-2":50}
for paper,count in expected.items():
    assert {q["originalQuestionNumber"] for q in questions if q["paperCode"]==paper}==set(range(1,count+1))
db=D/"question-bank.sqlite3"
with sqlite3.connect(db) as c:
    c.executescript("""
    CREATE TABLE IF NOT EXISTS questions(
      question_id TEXT PRIMARY KEY, year INTEGER NOT NULL CHECK(year=114),
      paper_code TEXT NOT NULL, original_number INTEGER NOT NULL,
      subject TEXT NOT NULL, payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
      UNIQUE(year,paper_code,original_number));
    CREATE TABLE IF NOT EXISTS shared_materials(
      shared_material_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL);
    """)
    for q in questions:
        raw=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        sha=hashlib.sha256(raw.encode()).hexdigest()
        c.execute("""INSERT INTO questions VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(question_id) DO UPDATE SET payload_json=excluded.payload_json,
        payload_sha256=excluded.payload_sha256""",
        (q["questionId"],114,q["paperCode"],q["originalQuestionNumber"],q["subject"],raw,sha))
    for x in data["sharedMaterials"]:
        c.execute("""INSERT INTO shared_materials VALUES(?,?)
        ON CONFLICT(shared_material_id) DO UPDATE SET payload_json=excluded.payload_json""",
        (x["sharedMaterialId"],json.dumps(x,ensure_ascii=False,sort_keys=True)))
    c.commit()
    rows=c.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205
    for qid,raw,sha in rows:
        assert hashlib.sha256(raw.encode()).hexdigest()==sha
        assert json.loads(raw)["questionId"]==qid
    assert c.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    assert c.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==len(data["sharedMaterials"])
print("PASS 114 SQLite roundtrip 205; rerunnable; independent from student DB")
