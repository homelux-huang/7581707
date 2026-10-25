#!/usr/bin/env python3
"""Repair ONLY 114-00-C-19 stale v1 provenance after verifying exact archived v2.

Fail closed: never OCR, recrop, elevate QA/official answer, or authorize release.
The official PDF SHA is a previously recorded provenance value, not re-downloaded
or independently recalculated by this script. Run in isolated source branch only.
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
QID = "114-00-C-19"
OLD = "8147b8baad0b1757a4d4793cfc3ce225fbc21d9597a5c75220165a9c256b2fd6"
NEW = "4c549405cfef2061a42abdac873c6146bb61e52a5cccae2f232d1a5ca35baff1"
PAGE = "63d68af4507fd198cd045a5a24b4efd4f33f95b1c234e991fe0f9ed65c76bfa2"
PDF = "f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74"
V1 = "sudu/data/processed/114/webp-v1/00-C/114-00-C-19.webp"
V2 = "sudu/data/processed/114/webp-v2/00-C/114-00-C-19.webp"
DIRECT = "sudu/data/processed/114/qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json"
OCR = "sudu/data/processed/114/qa-drafts/OCR_VISUAL_114_C19_C23_20261023.json"
RECEIPT = ROOT / "docs/ROLE_A_114_C19_RECONCILIATION_20261025.json"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def canonical(q):
    return json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def check_webp(relative, expected):
    raw = (ROOT / relative).read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", relative
    assert sha(raw) == expected, relative + " exact source bytes changed"
    return len(raw)

def rows(dbpath):
    assert dbpath.is_file()
    with sqlite3.connect(dbpath.as_uri() + "?mode=ro", uri=True) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        names = {r[1] for r in conn.execute("PRAGMA table_info(questions)")}
        field = "payload" if "payload" in names else "payload_json"
        assert {"question_id", field, "payload_sha256"} <= names
        items = conn.execute(
            "SELECT question_id," + field + ",payload_sha256 FROM questions"
        ).fetchall()
    assert len(items) == 205
    result = {}
    for qid, raw, digest in items:
        assert qid not in result
        assert sha(raw.encode("utf-8")) == digest, qid
        result[qid] = json.loads(raw)
    assert len(result) == 205
    return field, result

def evidence_and_source():
    bank = read(BASE / "questions.json")
    manifest = read(BASE / "webp-manifest.json")
    assert bank["year"] == manifest["year"] == 114
    questions = bank["questions"]
    assets = manifest["items"]
    byid = {q["questionId"]: q for q in questions}
    images = {a["questionId"]: a for a in assets}
    assert len(byid) == len(questions) == len(images) == len(assets) == 205
    assert set(byid) == set(images)
    q, asset = byid[QID], images[QID]
    assert q["paperCode"] == asset["paperCode"] == "00-C"
    assert q["originalQuestionNumber"] == asset["originalQuestionNumber"] == 19
    assert q["year"] == 114 and q["answerVerified"] is False
    assert q["questionVerified"] is False and q["integrationReady"] is False
    assert q["answer"] == "B" and q["answerMatched"] is True
    assert q["assets"]["singleQuestionWebp"] == asset["output"] == V2
    assert q["assets"]["sha256"] == asset["sha256"] == NEW
    assert asset["qaStatus"] == "PASS"
    assert asset["sourceSha256"] == q["questionProvenance"]["pixelSourceSha256"] == PAGE
    assert asset["sourcePdfSha256"] == q["questionProvenance"]["officialPdfSha256"] == PDF
    assert asset["sourcePage"] == q["sourcePage"] == 7
    assert asset["oldAssetBeforeDirectVisualRepair"]["output"] == V1
    assert asset["oldAssetBeforeDirectVisualRepair"]["sha256"] == OLD
    assert asset["oldAssetBeforeDirectVisualRepair"]["qaStatus"].startswith("BLOCKED")
    assert asset["crop"] == [90, 284, 1310, 563]
    assert asset["oldAssetBeforeDirectVisualRepair"]["crop"] == [90, 284, 1310, 1024]
    assert q["assets"]["cropCoordinates"] == asset["crop"]
    assert q["questionProvenance"]["webpSha256"] in (OLD, NEW)
    check_webp(asset["source"], PAGE)
    size_v1 = check_webp(V1, OLD)
    size_v2 = check_webp(V2, NEW)

    direct = read(ROOT / DIRECT)
    assert direct["independentExternalHumanRecheck"] is False
    assert direct["answerVerifiedAdded"] == direct["questionVerifiedAdded"] == 0
    d = next(x for x in direct["items"] if x["questionId"] == QID)
    assert d["reviewedWebpPath"] == V2 and d["reviewedWebpSha256"] == NEW
    assert d["priorWebpPath"] == V1 and d["priorWebpSha256"] == OLD
    assert d["sourcePageWebpSha256"] == PAGE
    assert d["independentHumanReview"] is False and d["integrationReady"] is False
    assert d["cropSourcePixelBounds"] == asset["crop"]
    assert all(d["visualCriteria"].values())
    old_ocr = read(ROOT / OCR)
    o = next(x for x in old_ocr["items"] if x["questionId"] == QID)
    assert old_ocr["textFullQaPassAdded"] == old_ocr["answerVerifiedAdded"] == 0
    assert o["webpPath"] == V1 and o["webpSha256Recorded"] == OLD
    assert "▲閱讀下文" in o["rawOptionDFromQuestionsJson"]
    assert o["correctedOptionD"] == q["options"][3]
    assert q["textQaStatus"] == "PARTIAL_OPTION_D_CORRECTED_NOT_FULL_TEXT_QA"
    return bank, byid, asset, {"v1Size": size_v1, "v2Size": size_v2}

def target_record(q):
    fixed = copy.deepcopy(q)
    fixed["questionProvenance"]["webpSha256"] = NEW
    assert q["questionProvenance"]["webpSha256"] in (OLD, NEW)
    assert fixed["assets"]["sha256"] == NEW
    return fixed

def modify_sqlite(path, old, fixed, expected_other):
    field, before = rows(path)
    assert set(before) == set(expected_other) | {QID}
    for qid, target in expected_other.items():
        assert before[qid] == target, "unexpected unowned SQLite row " + qid
    assert before[QID] in (old, fixed), "C19 SQLite content drifted"
    if before[QID] != fixed:
        wire = canonical(fixed)
        with sqlite3.connect(path) as conn:
            count = conn.execute(
                "UPDATE questions SET " + field + "=?,payload_sha256=? WHERE question_id=?",
                (wire, sha(wire.encode("utf-8")), QID)
            ).rowcount
            assert count == 1
            conn.commit()
    _, after = rows(path)
    assert after[QID] == fixed
    for qid, target in expected_other.items():
        assert after[qid] == target
    return sha(path.read_bytes())

def validate_fixed():
    _, byid, asset, sizes = evidence_and_source()
    q = byid[QID]
    assert q["questionProvenance"]["webpSha256"] == NEW, "C19 stale v1 provenance"
    field, db = rows(BASE / "question-bank.sqlite3")
    assert set(db) == set(byid) and len(db) == 205
    assert all(db[qid] == value for qid, value in byid.items()), "SQLite <> JSON"
    assert asset["visualReviewEvidence"]["reviewedSha256"] == NEW
    return {"qid": QID, "rows": 205, "sqliteField": field,
            "sqliteSha256": sha((BASE / "question-bank.sqlite3").read_bytes()),
            "sourceQuestionCanonicalSha256": sha(canonical(q).encode("utf-8")),
            "v1Sha256": OLD, "v2Sha256": NEW, "sourcePageSha256": PAGE,
            "officialPdfSha256RecordedNotRecomputed": PDF, **sizes}

def apply():
    bank, byid, asset, sizes = evidence_and_source()
    q = byid[QID]
    before = copy.deepcopy(q)
    after = target_record(q)
    unowned = {k: copy.deepcopy(v) for k, v in byid.items() if k != QID}
    _, original_db = rows(BASE / "question-bank.sqlite3")
    assert len(original_db) == 205
    assert all(original_db[qid] == value for qid, value in unowned.items())
    old_record = copy.deepcopy(after)
    old_record["questionProvenance"]["webpSha256"] = OLD
    assert original_db[QID] in (old_record, after)
    old_sqlite_sha = sha((BASE / "question-bank.sqlite3").read_bytes())
    old_json_sha = sha((BASE / "questions.json").read_bytes())

    with tempfile.TemporaryDirectory(prefix="role-a-c19-") as temp:
        copies = [Path(temp) / f"isolated-{i}.sqlite3" for i in (1, 2)]
        digests = []
        for dbcopy in copies:
            shutil.copy2(BASE / "question-bank.sqlite3", dbcopy)
            digests.append(modify_sqlite(dbcopy, old_record, after, unowned))
        assert digests[0] == digests[1], "two isolated SQLite imports not deterministic"

        bank_fixed = copy.deepcopy(bank)
        target = next(item for item in bank_fixed["questions"] if item["questionId"] == QID)
        target["questionProvenance"]["webpSha256"] = NEW
        assert len(bank_fixed["questions"]) == 205
        assert all(canonical(item) == canonical(unowned[item["questionId"]])
                   for item in bank_fixed["questions"] if item["questionId"] != QID)
        dump = json.dumps(bank_fixed, ensure_ascii=False, indent=2) + "\n"
        draft = Path(temp) / "questions.json"
        draft.write_text(dump, encoding="utf-8")
        assert read(draft)["questions"][next(i for i,x in enumerate(bank_fixed["questions"])
                                      if x["questionId"] == QID)] == after
        os.replace(copies[0], BASE / "question-bank.sqlite3")
        if before != after:
            os.replace(draft, BASE / "questions.json")

    result = validate_fixed()
    result.update({
        "taskId": "A-114-C19-PROVENANCE-20261025-01",
        "role": "A",
        "sourceEvidence": DIRECT,
        "originalOcrEvidence": OCR,
        "previousWebpSha256": OLD,
        "previousJsonSha256": old_json_sha,
        "previousSqliteSha256": old_sqlite_sha,
        "twoIsolatedImportsSameBinarySha256": digests[0],
        "twoIsolatedImportsEqual": True,
        "other204CanonicalRecordsUnchanged": True,
        "independentHumanQaNewApproval": False,
        "officialAnswerNewApproval": False,
        "questionVerified": False,
        "answerVerified": False,
        "studentReleaseApproved": False,
        "mainOrLiveModified": False
    })
    RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(apply() if args.apply else validate_fixed(),
                     ensure_ascii=False, indent=2))
