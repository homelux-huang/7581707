#!/usr/bin/env python3
"""Admit only original MB24 source evidence into QA; never author/E/UI/release."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "4e365a75ed98e73223987d81041693a476196881"
QID = "115-00-MB-24"
PREFIX = "sudu/data/processed/115/"
TASK = "A-115-MB24-NATIVE-SOURCE-ADMISSION-20261114-01"
REV = "9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267"
IMAGE_SHA = "c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb"
IMAGE_BLOB = "cfe5c8eeaf4496d5d98856f96a2c310186ef5893"
PAGE_SHA = "3272c1a1df85614af3e65ae56aac3d819c9d25a7e44366d3a514de4fa8cd0555"
PAGE_BLOB = "4c98df22dd3096c5d59178f4f2b6b3e88415bbee"
ANSWER_IMAGE_SHA = "1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d"
ANSWER_IMAGE_BLOB = "5ea4b86e929506d595f96fa162d1aae021f68440"
SOURCE_PDF = "e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082"
ANSWER_PDF = "d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
STAGE_REL = PREFIX + "source-stage/115-00-MB-24-stage-20261104.json"
STAGE_BLOB = "88faf4ee767b20c15db603e91aa250bc59eba84c"
OLD_G2_REL = PREFIX + "review-evidence/115-00-MB-24-image-transcription-correction-20261024.json"
OLD_G2_BLOB = "ede8ce34695bc9e9429aab40079115f94610d669"
ANSWER_CERT = PREFIX + "QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
ANSWER_CERT_BLOB = "ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
NOTICE_REL = PREFIX + "official-confirmation-status.json"
NOTICE_BLOB = "6d21432395294d9ccbcfe1dea8be01f88597bbf3"
G1_REL = PREFIX + "VISUAL_QA_2026-10-22.json"
G1_SHA = "ca6507c62081bc1bbfa30cdd24172484a1c9b25b517ab04f7ae0f4caa74fa142"
IMAGE_REL = PREFIX + "webp-v2/00-MB/115-00-MB-24.webp"
PAGE_REL = "sudu/data/original/115/00-MB/p008-e82e34d9cd-v2-w1400-q66.webp"
ANSWER_IMAGE_REL = "sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"
G2_REL = PREFIX + "review-evidence/115-00-MB-24-ocr-publisher-20261114.json"
G3_REL = PREFIX + "review-evidence/115-00-MB-24-official-publisher-20261114.json"
REPORT_REL = PREFIX + "review-evidence/115-00-MB-24-source-admission-20261114.json"
SQL_REPORT = PREFIX + "SQLITE_QA_MB24_SOURCE_BRIDGE_20261114.json"
MAIN_PUBLISHER_BLOB = "64db5dd620dec230287ff0ea92a64b6e181e45a9"
SOURCE_STATUS = "SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI"


def demand(ok, message):
    if not ok:
        raise ValueError("MB24_SOURCE_HOLD: " + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def raw(rel):
    path = ROOT / rel
    demand(path.is_file() and not path.is_symlink(), "missing or symlink " + rel)
    return path.read_bytes()


def js(rel):
    return json.loads(raw(rel))


def historic(rel):
    return subprocess.check_output(["git", "show", BASE + ":" + rel], cwd=ROOT)


def write(rel, value):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snapshot(path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        demand(db.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "SQLite integrity")
        schema = db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
        columns = db.execute("PRAGMA table_info(questions)").fetchall()
        rows = {row[0]: row for row in db.execute("SELECT * FROM questions ORDER BY question_id")}
        shared = db.execute("SELECT * FROM shared_materials ORDER BY shared_material_id").fetchall()
    demand(len(rows) == 205 and len(columns) == 14, "205 rows / 14 columns")
    return schema, rows, shared


def originals():
    from PIL import Image, ImageChops
    for rel, oid in [(STAGE_REL, STAGE_BLOB), (OLD_G2_REL, OLD_G2_BLOB),
                     (ANSWER_CERT, ANSWER_CERT_BLOB), (NOTICE_REL, NOTICE_BLOB)]:
        demand(blob(raw(rel)) == oid, "original evidence Blob changed " + rel)
    demand(sha(raw(G1_REL)) == G1_SHA, "original image QA changed")
    for rel, expected_sha, oid in [(IMAGE_REL, IMAGE_SHA, IMAGE_BLOB),
                                   (PAGE_REL, PAGE_SHA, PAGE_BLOB),
                                   (ANSWER_IMAGE_REL, ANSWER_IMAGE_SHA, ANSWER_IMAGE_BLOB)]:
        data = raw(rel)
        demand(data[:4] == b"RIFF" and data[8:12] == b"WEBP", "original WebP header")
        demand(sha(data) == expected_sha and blob(data) == oid, "original image SHA/Blob changed")
    single = Image.open(io.BytesIO(raw(IMAGE_REL))).convert("RGB")
    page = Image.open(io.BytesIO(raw(PAGE_REL))).convert("RGB").crop((90, 614, 1310, 1092))
    demand(single.size == (1220, 478) and ImageChops.difference(single, page).getbbox() is None,
           "original full formula/options crop pixel mismatch")
    stage, old_g2 = js(STAGE_REL), js(OLD_G2_REL)
    demand(stage["questionId"] == old_g2["questionId"] == QID, "original QID")
    demand(stage["G2"]["correctedTextQuestion"] == old_g2["correctedText"]["question"]
           and stage["G2"]["correctedTextOptions"] == old_g2["correctedText"]["options"], "original corrected G2")
    clean = {"question": stage["G2"]["correctedTextQuestion"],
             "options": stage["G2"]["correctedTextOptions"], "singleQuestionWebpSha256": IMAGE_SHA}
    demand(sha(canonical(clean)) == REV == stage["G2"]["existingRoleCAuthorSourceRevisionWithoutTable"],
           "exact frozen author/source revision")
    records = [x for x in js(ANSWER_CERT)["records"] if x["questionId"] == QID]
    demand(len(records) == 1 and records[0]["officialFinalAnswerReadDirectlyFromPublishedImage"] == "C"
           and records[0]["answerVerified"] is True, "original official answer C")
    demand(js(NOTICE_REL)["confirmations"]["00-MB"]["officialStatus"] == "no_objection_submitted", "notice")
    return stage


def issuers(stage):
    g2 = {"schemaVersion": 1, "year": 115, "questionId": QID,
          "role": "A_SOURCE_ONLY_NOT_DISTINCT_E", "taskId": TASK,
          "questionRevision": REV, "webpSha256": IMAGE_SHA,
          "question": stage["G2"]["correctedTextQuestion"], "options": stage["G2"]["correctedTextOptions"],
          "visualTextCompared": True, "reviewer": "ROLE A Work original source inspection; not authenticated E content review",
          "reviewedAt": "2026-11-14", "originalPage": 8, "originalPageSha256": PAGE_SHA,
          "originalSingleWebpGitBlob": IMAGE_BLOB, "sourcePageWebpGitBlob": PAGE_BLOB,
          "sourceStagePath": STAGE_REL, "sourceStageGitBlob": STAGE_BLOB,
          "sourceCorrectionsPath": OLD_G2_REL, "historicalCorrectionGitBlob": OLD_G2_BLOB,
          "sourcePdfSha256PreviouslyRecorded": SOURCE_PDF, "sourceCrop": [90, 614, 1310, 1092],
          "formulaDescription": stage["G2"]["figureDescription"], "sourcePixelDifference": "ZERO_RGB_ALL_CHANNELS",
          "noNewOCR": True, "noRecrop": True, "originalRawOcrPreserved": True,
          "independentE": False, "studentReady": False, "studentLive": False}
    g3 = {"schemaVersion": 1, "year": 115, "questionId": QID,
          "reviewer": "ROLE A existing original published Q24 C/no-objection verification; not independent Role E",
          "reviewedAt": "2026-11-14", "officialPage": "https://web1.tcte.edu.tw/EXAM/115_4y/",
          "officialPdfSha256": ANSWER_PDF, "finalAnswer": "C", "officialFinalAnswerImageQaPassed": True,
          "correctionNoticeReviewed": True, "noObjectionForPaper": True,
          "noCorrectionForThisQuestion": False, "correctionForQuestionReviewed": False,
          "officialNoticeStatus": "no_objection_submitted", "officialNoticePath": NOTICE_REL,
          "originalOfficialAnswerImagePath": ANSWER_IMAGE_REL,
          "originalOfficialAnswerImageSha256": ANSWER_IMAGE_SHA, "originalOfficialAnswerImageGitBlob": ANSWER_IMAGE_BLOB,
          "originalSourcePageSha256": PAGE_SHA, "originalSingleQuestionWebpSha256": IMAGE_SHA,
          "sourceQuestionRevision": REV, "directPublishedAnswerRecord": ANSWER_CERT,
          "directPublishedAnswerRecordGitBlob": ANSWER_CERT_BLOB,
          "originalOfficialAnswerPdfNewlyRehashedThisTask": False,
          "sourceOnly": True, "independentE": False, "studentReady": False, "studentLive": False}
    return g2, g3


def apply():
    stage = originals()
    for name in ("questions.json", "question-bank.sqlite3", "inventory.json", "webp-manifest.json"):
        demand(raw(PREFIX + name) == historic(PREFIX + name), "latest frozen QA drift: " + name)
    for rel in (G2_REL, G3_REL, REPORT_REL, SQL_REPORT):
        demand(not (ROOT / rel).exists(), "output already exists " + rel)
    schema, before, shared = snapshot(ROOT / PREFIX / "question-bank.sqlite3")
    bank = js(PREFIX + "questions.json")
    question = next(q for q in bank["questions"] if q["questionId"] == QID)
    demand(question["questionVerified"] is False and question["answerVerified"] is True
           and question["answer"] == "C", "canonical baseline flags")
    demand(question["question"] == stage["G2"]["rawOCRQuestion"]
           and question["options"] == stage["G2"]["rawOCROptions"], "raw baseline text changed")
    g2, g3 = issuers(stage)
    write(G2_REL, g2)
    write(G3_REL, g3)
    question.update({"question": g2["question"], "options": g2["options"], "questionVerified": True,
                     "textQaStatus": "PASS", "imageQaStatus": "PASS", "answerVerified": True,
                     "officialFinalAnswer": "C", "officialCorrectionChecked": True,
                     "officialAnswerQaStatus": "PASS_FINAL_OFFICIAL_ANSWER_AND_NO_OBJECTION_NOTICE",
                     "reviewStatus": SOURCE_STATUS, "integrationReady": False,
                     "correctionVersion": "ROLE_A_MB24_ORIGINAL_G2_SOURCE_ONLY_20261114"})
    question["issues"] = [x for x in question["issues"] if x != "single_question_crop_not_yet_generated"]
    question["extraction"]["correctionOverlay"] = {"origin": "FROZEN_ROLE_A_PR157_SOURCE_ONLY",
        "sourceStagePath": STAGE_REL, "sourceStageGitBlob": STAGE_BLOB, "sourceRevision": REV,
        "originalRawOcrUnchanged": True, "originalImageGitBlob": IMAGE_BLOB}
    question["extraction"]["ocrReviewStatus"] = "PASS_SOURCE_G2_ORIGINAL_FULL_FRACTIONS"
    question["extraction"]["correctedAt"] = "2026-11-14"
    question["answerProvenance"]["officialRevisionChecked"] = True
    question["textQaEvidence"] = {"reviewer": g2["reviewer"], "reviewedAt": g2["reviewedAt"],
        "evidencePath": G2_REL, "evidenceSha256": sha(raw(G2_REL)), "questionRevision": REV, "sourceImageSha256": PAGE_SHA}
    question["officialFinalQaEvidence"] = {"reviewer": g3["reviewer"], "reviewedAt": g3["reviewedAt"],
        "evidencePath": G3_REL, "evidenceSha256": sha(raw(G3_REL)), "answerPdfSha256": ANSWER_PDF,
        "finalCorrectionsReviewed": True}
    write(PREFIX + "questions.json", bank)
    payload = canonical(question).decode()
    with sqlite3.connect(ROOT / PREFIX / "question-bank.sqlite3") as db:
        cur = db.execute("UPDATE questions SET question=?,answer_verified=?,question_verified=?,review_status=?,payload_json=?,payload_sha256=? WHERE question_id=?",
            (question["question"], 1, 1, question["reviewStatus"], payload, sha(payload.encode()), QID))
        demand(cur.rowcount == 1, "one target row update")
    new_schema, after, new_shared = snapshot(ROOT / PREFIX / "question-bank.sqlite3")
    demand(schema == new_schema and shared == new_shared, "schema/shared rows changed")
    demand([qid for qid in before if before[qid] != after[qid]] == [QID], "other 204 complete tuples changed")
    inventory = js(PREFIX + "inventory.json")
    inventory["sqlite"].update({"performed": True, "rows": 205, "shaMismatches": [], "roundtripPass": True,
        "sourceQuestionsSha256": sha(raw(PREFIX + "questions.json")),
        "dbSha256": sha(raw(PREFIX + "question-bank.sqlite3")), "evidencePath": SQL_REPORT, "releaseApproved": False})
    write(PREFIX + "inventory.json", inventory)
    report = {"schemaVersion": 1, "year": 115, "questionId": QID, "role": "A", "taskId": TASK,
        "baseSourceCommit": BASE, "sourceStageGitBlob": STAGE_BLOB, "sourceRevision": REV,
        "webpSha256": IMAGE_SHA, "officialAnswer": "C", "sourcePixelDifference": "ZERO_RGB_ALL_CHANNELS",
        "publisherOcrEvidencePath": G2_REL, "publisherOcrEvidenceSha256": sha(raw(G2_REL)),
        "publisherOfficialEvidencePath": G3_REL, "publisherOfficialEvidenceSha256": sha(raw(G3_REL)),
        "sourceQuestionsSha256": inventory["sqlite"]["sourceQuestionsSha256"], "dbSha256": inventory["sqlite"]["dbSha256"],
        "rows": 205, "columns": 14, "other204CompleteSqliteTuplesUnchanged": True,
        "other204CanonicalQuestionsUnchanged": True, "allManifestBytesUnchanged": True,
        "schemaAndSharedRowsUnchanged": True, "denormalizedProjectionRepairPreserved": True,
        "formalETrust": False, "formalDRealEmitter16": False, "studentReady": False, "newLive": False,
        "status": "SOURCE_ONLY_G1_G2_G3_NOT_E_TRUST_NOT_UI_NOT_READY_NOT_LIVE"}
    write(REPORT_REL, report)
    write(SQL_REPORT, {**report, "sqliteIntegrity": "ok", "releaseApproved": False})
    verify()


def publisher():
    path = Path(os.environ.get("PUBLISHER_CHECKER_PATH", str(ROOT / "_publisher_main/scripts/sudu_verified_publish.py")))
    demand(path.is_file() and blob(path.read_bytes()) == MAIN_PUBLISHER_BLOB, "exact protected-main publisher missing/changed")
    spec = importlib.util.spec_from_file_location("mb24_pinned_main_publisher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    originals()
    # Historical snapshot comparison is intentionally confined to this MB24 branch/check.
    before_bank = json.loads(historic(PREFIX + "questions.json"))
    bank = js(PREFIX + "questions.json")
    old = {q["questionId"]: q for q in before_bank["questions"]}
    current = {q["questionId"]: q for q in bank["questions"]}
    demand(len(old) == len(current) == 205 and old.keys() == current.keys(), "205 canonical IDs")
    demand([qid for qid in old if old[qid] != current[qid]] == [QID], "other 204 canonical objects changed")
    demand({k: v for k, v in bank.items() if k != "questions"} ==
           {k: v for k, v in before_bank.items() if k != "questions"}, "bank metadata changed")
    demand(raw(PREFIX + "webp-manifest.json") == historic(PREFIX + "webp-manifest.json"), "manifest changed")
    with tempfile.TemporaryDirectory() as td:
        old_path = Path(td) / "before.sqlite3"
        old_path.write_bytes(historic(PREFIX + "question-bank.sqlite3"))
        old_schema, old_rows, old_shared = snapshot(old_path)
    schema, rows, shared = snapshot(ROOT / PREFIX / "question-bank.sqlite3")
    demand(schema == old_schema and shared == old_shared, "schema/shared rows changed")
    demand([qid for qid in old_rows if old_rows[qid] != rows[qid]] == [QID], "other 204 full SQL tuples changed")
    from qa_current_source_integrity_20261114 import check_year
    check_year(ROOT, 115)  # Includes every denormalized column and inventory hash.
    q = current[QID]
    manifest = next(m for m in js(PREFIX + "webp-manifest.json")["items"] if m["questionId"] == QID)
    pub = publisher()
    demand(pub.text_revision(q, IMAGE_SHA) == REV and q["reviewStatus"] == SOURCE_STATUS, "normalized source revision/status")
    demand(q["extraction"]["rawQuestion"] == old[QID]["extraction"]["rawQuestion"]
           and q["extraction"]["rawOptions"] == old[QID]["extraction"]["rawOptions"]
           and q["extraction"]["ocrRaw"] == old[QID]["extraction"]["ocrRaw"], "original raw OCR changed")
    demand(pub.image_proof(q, manifest, {}, ROOT) and pub.visual_certificate(ROOT, manifest, QID)
           and pub.verify_bytes(ROOT, IMAGE_REL, IMAGE_SHA), "native G1")
    demand(pub.source_proof(q, True, True, REV) == (True, True), "native G2/G3")
    g2, g3 = pub.review_document(ROOT, 115, G2_REL, QID), pub.review_document(ROOT, 115, G3_REL, QID)
    demand(g2 and g3 and g2[0]["question"] == q["question"] and g2[0]["options"] == q["options"]
           and g2[0]["questionRevision"] == REV and g2[0]["webpSha256"] == IMAGE_SHA, "native issuer G2")
    demand(g3[0]["finalAnswer"] == q["answer"] == "C"
           and pub.official_notice_scope_certified(ROOT, 115, q, g3[0]), "native official C/no-objection G3")
    for key, rel in [("textQaEvidence", G2_REL), ("officialFinalQaEvidence", G3_REL)]:
        demand(q[key]["evidenceSha256"] == sha(raw(rel)), "issuer SHA binding")
    demand("finalAnswer" not in g2[0] and "officialAnswer" not in g2[0], "G2 must remain source-only")
    demand(not q.get("studentReleaseApproved", False) and q.get("teachingQaStatus") != "PASS"
           and q.get("uiQaStatus") != "PASS" and not pub.certificates_complete(ROOT, q, manifest, {}), "false student certification")
    receipt = js(REPORT_REL)
    demand(all(receipt[k] is False for k in ["formalETrust", "formalDRealEmitter16", "studentReady", "newLive"]), "false receipt approval")
    demand(receipt["sourceQuestionsSha256"] == sha(raw(PREFIX + "questions.json"))
           and receipt["dbSha256"] == sha(raw(PREFIX + "question-bank.sqlite3")), "source report hashes")
    return pub, q, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply() if args.apply else verify()
    print("MB24 native source G1/G2/G3 and 205x14 parity PASS; other204/projection/manifest preserved; NO READY/LIVE")
