"""Read-only, per-record 114 SQLite reconciliation with original questions.json.

No QA or release flags are changed. Only an all-205 exact JSON payload readback
from the original canonical database can satisfy the 114 publisher DB gate.
"""
from pathlib import Path
import sqlite3,json,hashlib
ROOT=Path(__file__).resolve().parents[1]/"sudu/data/processed/114"
BANK=json.loads((ROOT/"questions.json").read_text())["questions"]
expected={x["questionId"]:x for x in BANK}
report={"schemaVersion":1,"year":114,"bankCount":len(BANK),"original":{},"staged":{}}
assert len(expected)==205
for label,rel in (("original","question-bank.sqlite3"),("staged","qa-drafts/sqlite-v2/question-bank.sqlite3")):
    path=ROOT/rel
    state={"path":str(rel),"dbSha256":hashlib.sha256(path.read_bytes()).hexdigest(),"exists":path.exists()}
    conn=sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True)
    try:
        rows=conn.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    finally:
        conn.close()
    mismatch=[]
    invalid_hash=[]
    seen=set()
    for id_,raw,sha in rows:
        if id_ in seen:
            mismatch.append({"id":id_,"reason":"duplicate"})
        seen.add(id_)
        try: payload=json.loads(raw)
        except Exception as e:
            mismatch.append({"id":id_,"reason":"non-json"}); continue
        if hashlib.sha256(raw.encode()).hexdigest()!=sha:
            invalid_hash.append(id_)
        if payload!=expected.get(id_):
            mismatch.append({"id":id_,"reason":"different-content",
                "dbKeys":sorted(payload) if isinstance(payload,dict) else "not-object",
                "questionKeys":sorted(expected.get(id_,{})),
                "jsonSha256":hashlib.sha256(json.dumps(expected.get(id_,{}),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
                "storedHash":sha})
    state.update({"rowCount":len(rows),"allIdsMatch":set(expected)==seen,
                  "payloadHashMatchesRawBytes":len(invalid_hash)==0,
                  "hashMismatchIds":invalid_hash[:25],
                  "allPayloadsMatchCurrentQuestions":len(mismatch)==0,
                  "payloadMismatchCount":len(mismatch),
                  "payloadMismatchSample":mismatch[:12],
                  "publisherReady":len(rows)==205 and set(expected)==seen and not mismatch and not invalid_hash})
    report[label]=state
report["originalStrictRoundtripPass"]=report["original"]["publisherReady"]
p=Path("/tmp/114-sqlite-reconciliation.json")
p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False,indent=2))
