#!/usr/bin/env python3
"""Build immutable isolated 105 QA SQLite v2 from current JSON, without touching v1.

Never updates question-bank.sqlite3, QA PASS flags, main, UI or student records.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sudu/data/processed/105'
JSON_SOURCE = BASE / 'questions.json'
ORIGINAL_DB = BASE / 'question-bank.sqlite3'
DRAFT_DB = BASE / 'qa-drafts/sqlite-v2/question-bank.sqlite3'
REPORT = BASE / 'qa-drafts/SQLITE_105_V2_STAGING_20261023.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def run():
    if not JSON_SOURCE.is_file() or not ORIGINAL_DB.is_file():
        raise FileNotFoundError('Required 105 bank or original isolated DB missing')
    data = json.loads(JSON_SOURCE.read_text(encoding='utf-8'))
    questions, materials = data['questions'], data.get('sharedMaterials', [])
    ids = {q['questionId'] for q in questions}
    keys = {(q['year'], q['paperCode'], q['originalQuestionNumber']) for q in questions}
    if not questions or len(ids) != len(questions) or len(keys) != len(questions):
        raise ValueError('Duplicate or missing canonical source keys')
    if not DRAFT_DB.exists():
        DRAFT_DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DRAFT_DB) as cx:
            cx.executescript('''CREATE TABLE questions(
                question_id TEXT PRIMARY KEY, year INTEGER, paper_code TEXT,
                original_number INTEGER, subject TEXT, payload TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL, UNIQUE(year,paper_code,original_number));
                CREATE TABLE shared_materials(material_id TEXT PRIMARY KEY, payload TEXT NOT NULL);''')
            for _ in range(2):
                for q in questions:
                    payload = canonical(q)
                    cx.execute('''INSERT INTO questions VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(question_id) DO UPDATE SET
                    payload=excluded.payload,payload_sha256=excluded.payload_sha256''',
                    (q['questionId'],q['year'],q['paperCode'],q['originalQuestionNumber'],
                     q.get('subject'),payload,hashlib.sha256(payload.encode()).hexdigest()))
                for m in materials:
                    cx.execute('''INSERT INTO shared_materials VALUES(?,?)
                    ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload''',
                    (m['sharedMaterialId'],canonical(m)))
                cx.commit()
    # The same verification runs when output already exists; never overwrite stale drafts.
    with sqlite3.connect(DRAFT_DB.resolve().as_uri()+'?mode=ro',uri=True) as cx:
        if cx.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Draft database integrity failure')
        records = cx.execute('SELECT question_id,payload,payload_sha256 FROM questions').fetchall()
        if len(records) != len(questions):
            raise ValueError('Draft database row mismatch')
        by_id = {q['questionId']:q for q in questions}
        for qid,payload,hsh in records:
            if qid not in by_id or json.loads(payload) != by_id[qid] or hashlib.sha256(payload.encode()).hexdigest() != hsh:
                raise ValueError('Draft database source JSON/SHA drift; refuse overwrite')
        n_shared = cx.execute('SELECT COUNT(*) FROM shared_materials').fetchone()[0]
        if n_shared != len(materials):
            raise ValueError('Shared materials row mismatch')
    report = {'schemaVersion':1,'year':105,'sourceQuestionsSha256':sha(JSON_SOURCE),
              'originalDatabasePath':ORIGINAL_DB.relative_to(ROOT).as_posix(),
              'originalDatabaseSha256Unchanged':sha(ORIGINAL_DB),
              'qaDraftDbPath':DRAFT_DB.relative_to(ROOT).as_posix(),
              'qaDraftDbSha256':sha(DRAFT_DB),
              'rows':len(records),'sharedMaterialRows':n_shared,
              'isolatedImportPasses':2,'qaStatus':'DRAFT_SQLITE_ROUNDTRIP_PASS_NOT_RELEASE',
              'originalDatabaseModified':False,'answerVerifiedChanged':False,
              'questionVerifiedChanged':False,'releaseAllowed':False,'integrationReady':False}
    payload=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if REPORT.exists():
        if REPORT.read_text(encoding='utf-8') != payload:
            raise ValueError('Existing draft report changed; require a new immutable version')
    else:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(payload,encoding='utf-8')
    print('105 QA SQLite v2 staged, round-trip checked; release remains prohibited')


if __name__ == '__main__':
    run()
