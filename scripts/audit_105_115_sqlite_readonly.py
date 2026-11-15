#!/usr/bin/env python3
"""Read-only SQLite vs JSON and isolated twice-import audit for 105-115.

Never edits any source DB, promotes G1/G3 flags, merges, or releases.
The in-memory twice-import is distinct from checking the on-disk DB contents.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'sudu/data/processed'
NEEDED = {'question_id', 'year', 'paper_code', 'original_number', 'payload_sha256'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(q):
    return json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def audit_year(year):
    root = DATA / str(year)
    report = {'year': year, 'g5Pass': False, 'originalDbReadOnly': True,
              'sandboxImportPasses': 0, 'blockers': []}
    qpath, dbpath = root/'questions.json', root/'question-bank.sqlite3'
    if not qpath.is_file() or not dbpath.is_file():
        report['blockers'].append('missing_questions_json_or_sqlite')
        return report
    try:
        rows = json.loads(qpath.read_text(encoding='utf-8'))['questions']
        assert isinstance(rows, list) and rows
    except (ValueError, KeyError, TypeError, AssertionError):
        report['blockers'].append('invalid_questions_json')
        return report
    indexed = {q.get('questionId'): q for q in rows if isinstance(q, dict)}
    ids = [(q.get('year'), q.get('paperCode'), q.get('originalQuestionNumber')) for q in rows]
    n = len(rows)
    report['jsonRows'] = n
    if len(indexed) != n or None in indexed or len(set(ids)) != n:
        report['blockers'].append('duplicate_or_missing_canonical_question_ids')
    report['sqliteSha256'] = digest(dbpath.read_bytes())
    try:
        uri = dbpath.resolve().as_uri()+'?mode=ro'
        with sqlite3.connect(uri, uri=True) as db:
            db.execute('PRAGMA query_only=ON')
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                report['blockers'].append('on_disk_integrity_check_failed')
            report['onDiskTables'] = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            cols = {r[1] for r in db.execute('PRAGMA table_info(questions)')}
            report['onDiskQuestionColumns'] = sorted(cols)
            payload_col = 'payload' if 'payload' in cols else ('payload_json' if 'payload_json' in cols else None)
            if not NEEDED <= cols or payload_col is None:
                report['blockers'].append('on_disk_question_schema_missing_columns')
            else:
                report['onDiskPayloadColumn'] = payload_col
                stored = db.execute('SELECT question_id,year,paper_code,original_number,'+payload_col+',payload_sha256 FROM questions').fetchall()
                report['onDiskRows'] = len(stored)
                if len(stored) != n:
                    report['blockers'].append('on_disk_row_count_mismatch')
                mismatches = []
                for qid, y, paper, num, payload, hsh in stored:
                    src = indexed.get(qid)
                    try:
                        saved = json.loads(payload)
                        valid = (src is not None and saved == src and
                                 y == src.get('year') and paper == src.get('paperCode') and
                                 num == src.get('originalQuestionNumber') and
                                 digest(payload.encode('utf-8')) == hsh)
                    except (TypeError, ValueError, AttributeError):
                        valid = False
                    if not valid:
                        mismatches.append(qid)
                report['onDiskMismatchCount'] = len(mismatches)
                report['onDiskMismatchIdsFirst20'] = mismatches[:20]
                if mismatches:
                    report['blockers'].append('on_disk_payload_or_SHA_mismatch')
                missing = set(indexed) - {r[0] for r in stored}
                if missing:
                    report['blockers'].append('on_disk_missing_json_question_ids')
                    report['missingIdsFirst20'] = sorted(missing)[:20]
    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
        report['blockers'].append('on_disk_sqlite_unreadable:'+type(exc).__name__)
    # Independent, disposable two-pass simulation, never the original database.
    try:
        with sqlite3.connect(':memory:') as db:
            db.executescript('''CREATE TABLE questions(
                question_id TEXT PRIMARY KEY, year INTEGER, paper_code TEXT,
                original_number INTEGER, payload TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                UNIQUE(year,paper_code,original_number));''')
            for k in range(2):
                for q in rows:
                    payload = canonical(q)
                    db.execute('''INSERT INTO questions VALUES(?,?,?,?,?,?)
                    ON CONFLICT(question_id) DO UPDATE SET
                    year=excluded.year,paper_code=excluded.paper_code,
                    original_number=excluded.original_number,
                    payload=excluded.payload,payload_sha256=excluded.payload_sha256''',
                    (q['questionId'], q['year'], q['paperCode'],
                     q['originalQuestionNumber'], payload,
                     digest(payload.encode('utf-8'))))
                db.commit()
                count = db.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
                if count != n:
                    raise ValueError('not_idempotent')
                report['sandboxImportPasses'] = k+1
            for qid, payload, hsh in db.execute('SELECT question_id,payload,payload_sha256 FROM questions'):
                if indexed[qid] != json.loads(payload) or digest(payload.encode()) != hsh:
                    raise ValueError('sandbox_readback_mismatch')
    except (sqlite3.DatabaseError, ValueError, KeyError, TypeError) as exc:
        report['blockers'].append('sandbox_two_pass_import_failed:'+type(exc).__name__)
    report['g5Pass'] = not report['blockers'] and report['sandboxImportPasses'] == 2
    return report


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--years', nargs='+', type=int, default=list(range(105,116)))
    cli.add_argument('--output', default='sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json')
    args = cli.parse_args()
    if any(not 105 <= y <= 115 for y in args.years):
        cli.error('Year must be between 105 and 115')
    records = [audit_year(y) for y in args.years]
    report = {'scope': '105-115', 'sourceDatabasesModified': False,
              'studentDataTouched': False, 'released': False,
              'yearsG5Pass': sum(x['g5Pass'] for x in records),
              'yearsReviewed': len(records), 'years': records}
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(f"G5 read-only audit: {report['yearsG5Pass']}/{report['yearsReviewed']} years with matching DB + two-pass sandbox import")
    for x in records:
        print(x['year'], x['blockers'][:4])


if __name__ == '__main__':
    main()
