"""Two-pass canonical 114 SQLite reconciliation, with strict non-destructive QA gates.

This script changes only:
- sudu/data/processed/114/question-bank.sqlite3 (after full test)
- sudu/data/processed/114/inventory.json (actual roundtrip evidence)
- sudu/data/processed/114/SQLITE_QA_RECONCILED_20261024.json
Never modifies any question, answer, WebP, student flag, or official PDF.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,os
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"sudu/data/processed/114"
SOURCE=BASE/"questions.json"
DATABASE=BASE/"question-bank.sqlite3"
INVENTORY=BASE/"inventory.json"
REPORT=BASE/"SQLITE_QA_RECONCILED_20261024.json"

def bsha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def check_db(conn,expected):
    assert conn.execute("PRAGMA integrity_check").fetchone()==("ok",), "SQLite integrity check"
    assert conn.execute("PRAGMA foreign_key_check").fetchall()==[], "SQLite foreign keys"
    rows=conn.execute("SELECT question_id,year,paper_code,original_number,subject,payload_json,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205 and len({row[0] for row in rows})==205, "205 question IDs"
    assert {r[0] for r in rows}==set(expected), "canonical ID set"
    for qid,year,code,number,subject,payload,fieldsha in rows:
        assert year==114 and expected[qid]["paperCode"]==code, "year/paper code"
        assert expected[qid]["originalQuestionNumber"]==number, "original question number"
        assert expected[qid]["subject"]==subject, "subject"
        assert hashlib.sha256(payload.encode("utf-8")).hexdigest()==fieldsha, "payload SHA"
        assert json.loads(payload)==expected[qid], "payload-vs-source mismatch"
    shared=conn.execute("SELECT * FROM shared_materials").fetchall()
    return {"questionCount":len(rows),"sharedMaterialCount":len(shared),
            "logicalBankSha256":hashlib.sha256(
                "\n".join(canonical(expected[qid]) for qid in sorted(expected)).encode("utf-8")).hexdigest()}

def make_verified_copy(source,target,expected):
    orig=sqlite3.connect(f"file:{source}?mode=ro",uri=True)
    dest=sqlite3.connect(str(target))
    try:
        assert orig.execute("PRAGMA integrity_check").fetchone()==("ok",), "original SQLite corrupted"
        cols={r[1] for r in orig.execute("PRAGMA table_info(questions)")}
        assert {"question_id","year","paper_code","original_number",
                "subject","payload_json","payload_sha256"}<=cols, "canonical schema changed"
        n=orig.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert n==205, "missing original database rows"
        old_shared=orig.execute("SELECT * FROM shared_materials ORDER BY shared_material_id").fetchall()
        orig.backup(dest)
    finally:
        orig.close()
    changed=[]
    try:
        dest.execute("BEGIN IMMEDIATE")
        for qid,existing,fieldsha in dest.execute(
            "SELECT question_id,payload_json,payload_sha256 FROM questions ORDER BY question_id").fetchall():
            assert hashlib.sha256(existing.encode()).hexdigest()==fieldsha,"old SHA mismatch"
            desired=canonical(expected[qid])
            if json.loads(existing)==expected[qid]:
                continue
            new_sha=hashlib.sha256(desired.encode("utf-8")).hexdigest()
            dest.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                         (desired,new_sha,qid))
            changed.append(qid)
        dest.commit()
        verification=check_db(dest,expected)
        new_shared=dest.execute("SELECT * FROM shared_materials ORDER BY shared_material_id").fetchall()
        assert old_shared==new_shared, "shared-material metadata changed"
    finally:
        dest.close()
    return changed,verification

def main():
    raw=SOURCE.read_bytes()
    bank=load(SOURCE)
    expected={q["questionId"]:q for q in bank["questions"]}
    assert len(expected)==len(bank["questions"])==205, "invalid 205 canonical source"
    original_sha=bsha(DATABASE)
    with tempfile.TemporaryDirectory(prefix="114-sqlite-two-pass-") as temp:
        first=Path(temp)/"first.sqlite3"
        second=Path(temp)/"second.sqlite3"
        changed1,stats1=make_verified_copy(DATABASE,first,expected)
        changed2,stats2=make_verified_copy(DATABASE,second,expected)
        assert changed1==changed2 and stats1==stats2,"two isolated builds disagree"
        # Bytewise SQLite pages may differ only due to SQLite backup internals.
        # Complete canonical readback and logical SHA are both required.
        source_sha=hashlib.sha256(raw).hexdigest()
        new_sha=bsha(first)
        report={
            "schemaVersion":1,"year":114,"sourceQuestionsSha256":source_sha,
            "oldSqliteSha256":original_sha,"newSqliteSha256":new_sha,
            "originalTableRows":205,"twoIndependentBackups":True,
            "isolatedImportPasses":2,"changedQuestionCount":len(changed1),
            "changedQuestionIds":changed1,"sharedMaterialRowsUnchanged":True,
            "roundtripPass":True,"sourceQuestionTextAndOptionsModified":False,
            "answerVerifiedOrQaApprovalChanged":False,
            "releaseAllowedByThisDbReconciliation":False,
            "firstPass":stats1,"secondPass":stats2}
        os.replace(first,DATABASE)
        assert bsha(DATABASE)==new_sha,"final db sha changed"
        verify=sqlite3.connect(f"file:{DATABASE}?mode=ro",uri=True)
        try: assert check_db(verify,expected)==stats1,"final final roundtrip"
        finally: verify.close()
        inventory=load(INVENTORY)
        prior=inventory.get("sqlite") if isinstance(inventory.get("sqlite"),dict) else {}
        inventory["sqlite"]={**prior,
            "roundtripPass":True,"rows":205,"isolatedImportPasses":2,
            "sourceQuestionsSha256":source_sha,"dbSha256":new_sha,
            "evidencePath":"sudu/data/processed/114/SQLITE_QA_RECONCILED_20261024.json",
            "releaseApproved":False}
        REPORT.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        INVENTORY.write_text(json.dumps(inventory,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
        print("PASS: two isolated imports; all 205 canonical JSON records, all payload hashes, no source changes")

if __name__=="__main__":
    main()
