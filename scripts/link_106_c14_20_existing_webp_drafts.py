#!/usr/bin/env python3
"""Link existing, SHA-pinned 106 Chinese 14-20 candidate crops without granting QA.

NO new OCR, no source recrop, no artificial QA PASS and no live/student writes.
Runs only on the 105-115 isolated QA branch. Original Git commits preserve DB history.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/106"
LEDGER = BASE / "qa-drafts/DRAFT_106_CHINESE_Q14_20_SHARED_SOURCE_P004_20261023.json"
REVIEW = BASE / "qa-drafts/LINKED_106_C14_20_DRAFT_ONLY_20261024.json"
EXPECTED = [f"106-00-C-{n:02d}" for n in range(14, 21)]
SHARED = {
    "106-00-C-SHARED-15-16": [15, 16],
    "106-00-C-SHARED-17-18": [17, 18],
    "106-00-C-SHARED-19-20": [19, 20],
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def resolved(rel):
    assert isinstance(rel, str) and rel.startswith("sudu/data/")
    p = (ROOT / rel).resolve()
    assert p.is_relative_to(ROOT.resolve()), "No path traversal"
    return p

def verify_source_crop(entry, page_bytes, page_img):
    qid = entry["id"]
    assert entry["qaStatus"] == "PENDING_DIRECT_VISUAL_REVIEW"
    assert entry["sourcePage"] == 4
    assert entry["sourcePageSha256"] == sha(page_bytes)
    target_path = resolved(entry["candidatePath"])
    payload = target_path.read_bytes()
    assert sha(payload) == entry["candidateSha256"], f"candidate SHA mismatches: {qid}"
    box = entry["sourceCropPixels"]
    assert len(box) == 4
    assert 0 <= box[0] < box[2] <= page_img.width
    assert 0 <= box[1] < box[3] <= page_img.height
    with Image.open(io.BytesIO(payload)) as candidate:
        candidate.load()
        assert candidate.format == "WEBP"
        assert list(candidate.size) == [box[2]-box[0], box[3]-box[1]]
        # Lossless cropped source pixels must match. Does NOT substitute for G1 visual QA.
        difference = ImageChops.difference(page_img.crop(tuple(box)).convert("RGB"),
                                           candidate.convert("RGB"))
        assert difference.getbbox() is None, f"pixel crop mismatch: {qid}"
    return target_path, payload

def data():
    led = read(LEDGER)
    assert led["year"] == 106 and led["paperCode"] == "00-C"
    assert led["questionCandidates"] == 7 and led["sharedCandidates"] == 3
    assert led["newImageQaPass"] == 0 and led["releaseAllowed"] is False
    assert {r["id"] for r in led["items"]} == set(EXPECTED) | set(SHARED)
    page_path = resolved(led["sourceImagePath"])
    page = page_path.read_bytes()
    assert sha(page) == led["sourceImageSha256"]
    git_hash = hashlib.sha1(b"blob " + str(len(page)).encode() + b"\x00" + page).hexdigest()
    assert git_hash == led["sourceGitBlobSha"]
    with Image.open(io.BytesIO(page)) as original:
        original.load()
        assert original.format == "WEBP"
        for e in led["items"]:
            verify_source_crop(e, page, original)
    manifest = read(BASE/"webp-manifest.json")
    bank = read(BASE/"questions.json")
    ocr = read(BASE/"ocr-raw-candidates.json")
    visual = read(BASE/"VISUAL_QA.json")
    inventory = read(BASE/"inventory.json")
    validation = read(BASE/"VALIDATION.json")
    release = read(BASE/"release-manifest.json")
    assert len(manifest["items"]) == len(bank["questions"]) == len(ocr["items"]) == len(visual["items"]) == 204
    assert bank["year"] == manifest["year"] == 106
    assert inventory["answerOfficialFinalVerified"] == 0
    assert not inventory["integrationReady"] and not release["releaseAllowed"]
    assert visual["passCount"] == inventory["visualQaPass"] == 12
    im = {x["questionId"]: x for x in manifest["items"]}
    qs = {x["questionId"]: x for x in bank["questions"]}
    os_ = {x["questionId"]: x for x in ocr["items"]}
    vs = {x["questionId"]: x for x in visual["items"]}
    assert len(im) == len(qs) == len(os_) == len(vs) == 204
    return led, manifest, bank, ocr, visual, inventory, validation, release, im, qs, os_, vs

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def db_rebuild(bank):
    original_db = BASE / "question-bank.sqlite3"
    assert original_db.is_file()
    with tempfile.TemporaryDirectory(dir=BASE) as td:
        temp_db = Path(td) / "question-bank.sqlite3"
        shutil.copyfile(original_db, temp_db)
        with sqlite3.connect(temp_db) as db:
            cols = {r[1] for r in db.execute("PRAGMA table_info(questions)")}
            assert {"question_id","year","paper_code","original_number","payload","payload_sha256"} <= cols
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            for round_number in (1, 2):
                for q in bank["questions"]:
                    payload = canonical(q)
                    res = db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                                     (payload, sha(payload.encode()), q["questionId"]))
                    assert res.rowcount == 1
                for m in bank["sharedMaterials"]:
                    payload = canonical(m)
                    db.execute("INSERT INTO shared_materials(material_id,payload) VALUES(?,?) "
                               "ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload",
                               (m["sharedMaterialId"], payload))
                db.commit()
                assert db.execute("SELECT count(*) FROM questions").fetchone()[0] == 204
                assert db.execute("SELECT count(*) FROM shared_materials").fetchone()[0] == len(bank["sharedMaterials"])
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            indexed = {q["questionId"]:q for q in bank["questions"]}
            for qid,y,c,n,payload,hsh in db.execute(
                "SELECT question_id,year,paper_code,original_number,payload,payload_sha256 FROM questions"):
                src=indexed[qid]
                assert src == json.loads(payload) and sha(payload.encode()) == hsh
                assert (y,c,n) == (src["year"],src["paperCode"],src["originalQuestionNumber"])
        os.replace(temp_db, original_db)

def run(stage):
    led,m,b,o,v,inv,valid,rel,im,qs,ocr,vis=data()
    if all(im[qid].get("output") for qid in EXPECTED):
        for entry in led["items"]:
            if entry["id"] in im:
                assert im[entry["id"]].get("output") == entry["candidatePath"]
                assert im[entry["id"]].get("outputSha256") == entry["candidateSha256"]
                assert im[entry["id"]]["qaStatus"] == "DRAFT_NEEDS_DIRECT_VISUAL_QA"
        print("Already linked. No duplicate work.")
        return
    assert all(im[qid]["qaStatus"] == "BLOCKED_NO_SINGLE_QUESTION_WEBP"
               and not im[qid].get("output") and not qs[qid]["assets"]["singleQuestionWebp"]
               and not qs[qid]["integrationReady"] and not qs[qid]["answerVerified"]
               and vis[qid]["status"] == "BLOCKED" for qid in EXPECTED), "Concurrent revisions: stop"
    assert inv["webpGeneratedDrafts"] == 194 and not m["sharedMaterialCrops"] and not b["sharedMaterials"]
    assert inv["sourcePaperStats"]["00-C"]["imageDrafts"] == 28
    byid={e["id"]:e for e in led["items"]}
    for qid in EXPECTED:
        e=byid[qid]
        entry=im[qid]
        entry.update({
            "sourcePage":4,
            "source":e["sourcePageWebp"],
            "sourcePageWebpSha256":e["sourcePageSha256"],
            "cropPixels":e["sourceCropPixels"],
            "output":e["candidatePath"],
            "outputSha256":e["candidateSha256"],
            "outputSize":e["candidateSizePixels"],
            "generationVersion":"existing-official-page-pixel-candidate-v2",
            "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA"
        })
        entry["issues"]=sorted(set(entry.get("issues",[])+["PENDING_DIRECT_VISUAL_AND_SHARED_MATERIAL_QA"]))
        q=qs[qid]
        q["assets"].update({
            "singleQuestionWebp":e["candidatePath"],
            "sourcePageWebp":e["sourcePageWebp"],
            "sha256":e["candidateSha256"],
            "sourcePage":4
        })
        q["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        q["issues"]=sorted(set(q.get("issues",[])+["PENDING_DIRECT_VISUAL_AND_SHARED_MATERIAL_QA"]))
        assert q["questionVerified"] is False and q["answerVerified"] is False and q["integrationReady"] is False
        ocr[qid]["imageSha256"]=e["candidateSha256"]
        vis[qid].update({
            "status":"PENDING",
            "sourcePage":4,
            "sourceWebp":e["sourcePageWebp"],
            "candidateWebp":e["candidatePath"],
            "candidateSha256":e["candidateSha256"],
            "reviewer":None,
            "visualEvidence":None
        })
    for sid,numbers in SHARED.items():
        e=byid[sid]
        mrow={
            "sharedMaterialId":sid, "paperCode":"00-C", "originalQuestionNumbers":numbers,
            "source":e["sourcePageWebp"],"sourcePage":4,
            "sourcePageWebpSha256":e["sourcePageSha256"],
            "cropPixels":e["sourceCropPixels"],"output":e["candidatePath"],
            "outputSha256":e["candidateSha256"],
            "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
            "issues":["SHARED_MATERIAL_SOURCE_ONLY_PENDING_INDEPENDENT_VISUAL_QA"]
        }
        m["sharedMaterialCrops"].append(mrow)
        b["sharedMaterials"].append(dict(mrow))
        v["sharedMaterials"].append({
            "sharedMaterialId":sid,"status":"PENDING","sourcePage":4,
            "sourceWebp":e["sourcePageWebp"],"candidateWebp":e["candidatePath"],
            "candidateSha256":e["candidateSha256"],
            "reviewer":None,"visualEvidence":None})
        for number in numbers:
            q=qs[f"106-00-C-{number:02d}"]
            q["sharedMaterialIds"].append(sid)
    inv["webpGeneratedDrafts"]=201
    inv["sourcePaperStats"]["00-C"]["imageDrafts"]=35
    inv["sourcePaperStats"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(14,21))
    inv["sharedMaterialsDrafts"]=3
    valid["sourceGaps"]["00-C"]["imageDrafts"]=35
    valid["sourceGaps"]["00-C"]["manualCandidateRecoveredNumbers"]=list(range(14,21))
    # Unverified automatic number anchors stay unresolved, even with safe draft crops.
    assert inv["visualQaPass"] == v["passCount"] == valid["imageVisualQaPass"] == 12
    assert inv["answerOfficialFinalVerified"] == 0
    assert not inv["integrationReady"] and not valid["releaseAllowed"] and not rel["releaseAllowed"]
    if not stage:
        print(json.dumps({"mode":"check","sourceSha256":led["sourceImageSha256"],
                          "candidatesToLink":7,"sharedDraftsToLink":3,
                          "newVisualQaPass":0,"releaseAllowed":False},ensure_ascii=False))
        return
    write(BASE/"webp-manifest.json",m)
    write(BASE/"questions.json",b)
    write(BASE/"ocr-raw-candidates.json",o)
    write(BASE/"VISUAL_QA.json",v)
    write(BASE/"inventory.json",inv)
    write(BASE/"VALIDATION.json",valid)
    db_rebuild(b)
    evidence={
        "year":106,"paperCode":"00-C","candidateCount":7,"sharedCandidateCount":3,
        "questionIds":EXPECTED,"sourceOfficialPdfSha256":led["sourceOfficialPdfSha256"],
        "sourceWebpSha256":led["sourceImageSha256"],
        "immutableStageEvidence":LEDGER.relative_to(ROOT).as_posix(),
        "reviewRequired":True,"newVisualQaPass":0,"newOfficialAnswerVerified":0,
        "newOcrTextQaPass":0,"releaseAllowed":False,"integrationReady":False,
        "sqliteRows":204,"sqliteImportPasses":2,
        "shaBeforeAfter": {
            "sourcePage":led["sourceImageSha256"],
            "singleCandidates":{qid:byid[qid]["candidateSha256"] for qid in EXPECTED}
        }
    }
    write(REVIEW,evidence)
    print(json.dumps({"mode":"staged","questionsLinked":7,"sharedDraftsLinked":3,
                      "newVisualQaPass":0,"newFinalAnswers":0,
                      "sqlite":204,"releaseAllowed":False},ensure_ascii=False))

if __name__ == "__main__":
    cli=argparse.ArgumentParser()
    group=cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    args=cli.parse_args()
    run(args.stage)
