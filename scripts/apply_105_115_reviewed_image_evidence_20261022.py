#!/usr/bin/env python3
"""Apply existing direct source-vs-crop image QA evidence, keyed by exact SHA.
NOT a visual reviewer. No correction of OCR, official answers or release flags.
Only use on the isolated QA branch. --check is read-only, --apply updates QA metadata.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed"
EVIDENCE = {
    113: "VISUAL_QA_BATCH_02_2026-10-22.json",
    114: "VISUAL_QA_BATCH_01_2026-10-22.json",
    115: "VISUAL_QA_BATCH_03_2026-10-22.json",
}
EXPECTED_IDS = {
    113: {f"113-00-C-{n:02d}" for n in range(6, 11)},
    114: {f"114-00-C-{n:02d}" for n in range(1, 11)},
    115: {"115-00-C-04", "115-00-C-05"},
}
PASS_CRITERIA = "number_stem_ABCD_figures_no_adjacent_no_header_legible"
FAIL_ID = "114-00-C-01"


def load(folder, filename):
    return json.loads((folder / filename).read_text(encoding="utf-8"))


def write(folder, filename, data):
    (folder / filename).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_safe_repo_path(s):
    p = Path(s)
    assert not p.is_absolute() and ".." not in p.parts and p.parts
    return ROOT / p


def check_evidence(year, evidence, manifest):
    assert evidence["year"] == year
    assert evidence["reviewer"] == "ChatGPT assistant"
    assert evidence["independentHumanReview"] is False
    assert evidence["reviewedOn"] == "2026-10-22"
    assert evidence["method"] == "direct_visual_official_page_webp_against_each_question_webp"
    records = evidence["records"]
    assert len(records) == len(EXPECTED_IDS[year])
    assert {x["questionId"] for x in records} == EXPECTED_IDS[year]
    items = {x["questionId"]: x for x in manifest["items"]}
    assert len(items) == len(manifest["items"])
    for rec in records:
        qid = rec["questionId"]
        assert qid in items and qid.startswith(f"{year}-")
        item = items[qid]
        assert rec["sourcePagePath"] == item["source"]
        assert rec["webpPath"] == item["output"]
        assert rec["sourcePage"] == item["sourcePage"]
        assert rec["cropPixels"] == (item.get("cropPixels") or item.get("crop"))
        assert rec["sourceSha256"] == (
            item.get("sourcePageWebpSha256") or item.get("sourceSha256")
        )
        assert rec["webpSha256"] == (item.get("outputSha256") or item.get("sha256"))
        source = as_safe_repo_path(rec["sourcePagePath"])
        crop = as_safe_repo_path(rec["webpPath"])
        assert source.is_file() and crop.is_file()
        assert digest(source) == rec["sourceSha256"]
        assert digest(crop) == rec["webpSha256"]
        with Image.open(source) as src, Image.open(crop) as im:
            src.load()
            im.load()
            assert src.format == "WEBP" and im.format == "WEBP"
            assert list(src.size) == item["sourceSize"]
            assert list(im.size) == item["outputSize"]
            x1, y1, x2, y2 = rec["cropPixels"]
            assert 0 <= x1 < x2 <= src.width and 0 <= y1 < y2 <= src.height
            assert im.size == (x2 - x1, y2 - y1)
        if qid == FAIL_ID:
            assert rec["result"] == "FAIL_HEADER_FRAGMENT"
            assert rec["criteria"] == "contains_previous_line_fragment"
        else:
            assert rec["result"] == "PASS"
            assert rec["criteria"] == PASS_CRITERIA
    return items


def apply(year):
    folder = BASE / str(year)
    evidence = load(folder, EVIDENCE[year])
    manifest = load(folder, "webp-manifest.json")
    items = check_evidence(year, evidence, manifest)
    questions = load(folder, "questions.json")
    byid = {q["questionId"]: q for q in questions["questions"]}
    assert len(byid) == len(questions["questions"]) == len(manifest["items"]) == 205
    assert set(byid) == set(items)
    inv = load(folder, "inventory.json")
    before = sum(i["qaStatus"] == "PASS" for i in items.values())
    assert all(not q.get(f, False) for q in byid.values()
               for f in ("answerVerified", "questionVerified", "integrationReady"))
    reference = (folder / EVIDENCE[year]).relative_to(ROOT).as_posix()
    modified_ids = set()
    blocked_ids = set()
    for rec in evidence["records"]:
        qid = rec["questionId"]
        entry = items[qid]
        question = byid[qid]
        if qid == FAIL_ID:
            assert entry["qaStatus"] != "PASS"
            entry["qaStatus"] = "BLOCKED_VISUAL_HEADER_FRAGMENT"
            if "crop_contains_previous_line_fragment" not in entry.setdefault("issues", []):
                entry["issues"].append("crop_contains_previous_line_fragment")
            question["imageQaStatus"] = "BLOCKED"
            question.setdefault("assets", {})["imageQaEvidence"] = reference
            blocked_ids.add(qid)
        else:
            old_evidence = entry.get("visualReviewEvidence")
            if entry["qaStatus"] == "PASS":
                assert old_evidence and old_evidence["reviewedSha256"] == rec["webpSha256"]
                continue
            entry["qaStatus"] = "PASS"
            entry["visualReviewEvidence"] = {
                "reference": reference,
                "reviewedSha256": rec["webpSha256"],
                "sourceSha256": rec["sourceSha256"],
                "reviewer": evidence["reviewer"],
                "method": evidence["method"],
                "date": evidence["reviewedOn"],
                "independentHumanReview": False,
                "criteria": rec["criteria"],
                "note": rec.get("note", ""),
            }
            question["imageQaStatus"] = "PASS"
            question.setdefault("assets", {})["imageQaEvidence"] = reference
            modified_ids.add(qid)
        question["questionVerified"] = False
        question["answerVerified"] = False
        question["integrationReady"] = False

    after = sum(i["qaStatus"] == "PASS" for i in items.values())
    assert after == before + len(modified_ids)
    assert all(not q.get(f, False) for q in byid.values()
               for f in ("answerVerified", "questionVerified", "integrationReady"))
    visual = None
    if year in (113, 114):
        visual = load(folder, "VISUAL_QA.json")
        review_items = visual["items"] if year == 113 else visual["questions"]
        vi = {v["questionId"]: v for v in review_items}
        assert set(vi) == set(byid)
        for rec in evidence["records"]:
            qid = rec["questionId"]
            v = vi[qid]
            if qid == FAIL_ID:
                v["result"] = "BLOCKED"
                v["failureReason"] = "HEADER_FRAGMENT"
                v["evidenceReference"] = reference
            elif year == 113:
                v["status"] = "PASS"
                v["reviewer"] = evidence["reviewer"]
                v["visualEvidence"] = reference
                v["reviewedWebpSha256"] = rec["webpSha256"]
            else:
                v["result"] = "PASS"
                v["reviewer"] = evidence["reviewer"]
                v["evidenceReference"] = reference
                v["reviewedWebpSha256"] = rec["webpSha256"]
        visual["passCount"] = after

    if year == 113:
        inv["visualQaPass"] = after
        validation = load(folder, "VALIDATION.json")
        validation["imageVisualQaPass"] = after
        validation["releaseAllowed"] = validation["integrationReady"] = False
        release = load(folder, "release-manifest.json")
        release["imageQA"] = f"PARTIAL_{after}_OF_205"
        release["releaseAllowed"] = release["integrationReady"] = False
    elif year == 114:
        inv["webpVisualQaPassed"] = after
        manifest["visualQaPass"] = after
        validation = {
            "year": 114, "structuralStatus": "DRAFT_WITH_UNRESOLVED_QA",
            "imageVisualQaPass": after,
            "answerOfficialFinalVerified": 0,
            "ocrTextVerified": 0,
            "officialCorrectionQaComplete": False,
            "releaseAllowed": False, "integrationReady": False,
            "blockedCropIds": sorted(blocked_ids),
        }
        release = {
            "year": 114, "imageQA": f"PARTIAL_{after}_OF_205",
            "officialFinalAnswerQA": "PENDING",
            "questionTextQA": "PENDING",
            "sharedMaterialQA": "PENDING",
            "releaseAllowed": False, "integrationReady": False,
        }
    else:
        inv["imageVisualQaPass"] = after
        inv["pendingVisualReviewIds"] = [
            qid for qid in inv["pendingVisualReviewIds"] if qid not in modified_ids
        ]
        cn = "國文"
        inv["perSubject"][cn]["visualQaPass"] += len(modified_ids)
        inv["perSubject"][cn]["needsFullVisualReview"] -= len(modified_ids)
        validation = load(folder, "VALIDATION.json")
        validation["stats"][cn]["visualQaPass"] += len(modified_ids)
        validation["stats"][cn]["needsFullVisualReview"] -= len(modified_ids)
        validation["integration"] = "NO"
        validation["published"] = "NO"
        assert inv["imageVisualQaPass"] + len(inv["pendingVisualReviewIds"]) == 205
        assert sum(v["visualQaPass"] for v in inv["perSubject"].values()) == after
        release = None

    if not modified_ids and not blocked_ids:
        print(f"{year}: already applied, nothing to commit")
        return
    assert year in (113, 114, 115)
    # Update the isolated SQLite question payloads so JSON and DB remain in sync.
    # No schema changes, no student tables, and no activity outside processed/year.
    db = folder / "question-bank.sqlite3"
    with sqlite3.connect(db) as cx:
        cols = {r[1] for r in cx.execute("PRAGMA table_info(questions)")}
        assert {"question_id", "payload_sha256"} <= cols, cols
        # Historical 105-113 uses payload; 114 and 115 use payload_json.
        # Reject any unrecognized schema rather than migrating student data.
        payload_column = "payload" if "payload" in cols else "payload_json"
        assert payload_column in cols, cols
        assert "student_answers" not in cols
        for qid in sorted(modified_ids | blocked_ids):
            raw = json.dumps(byid[qid], ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"))
            hx = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            assert cx.execute(
                f"UPDATE questions SET {payload_column}=?, payload_sha256=? WHERE question_id=?",
                (raw, hx, qid)
            ).rowcount == 1
        assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 205
        for qid, raw, sha in cx.execute(
            f"SELECT question_id,{payload_column},payload_sha256 FROM questions"
        ):
            assert hashlib.sha256(raw.encode("utf-8")).hexdigest() == sha
            assert json.loads(raw)["questionId"] == qid
        assert cx.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    write(folder, "webp-manifest.json", manifest)
    write(folder, "questions.json", questions)
    write(folder, "inventory.json", inv)
    write(folder, "VALIDATION.json", validation)
    if release is not None:
        write(folder, "release-manifest.json", release)
    if visual is not None:
        write(folder, "VISUAL_QA.json", visual)
    print(f"{year}: {before} -> {after}/205 image QA PASS, "
          f"new={len(modified_ids)}, crop_failures={len(blocked_ids)}, release=BLOCKED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, choices=tuple(EVIDENCE), required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    folder = BASE / str(args.year)
    manifest = load(folder, "webp-manifest.json")
    evidence = load(folder, EVIDENCE[args.year])
    check_evidence(args.year, evidence, manifest)
    if args.check:
        print(f"{args.year}: {len(evidence['records'])} SHA-bound evidence entries verified; no files changed")
    else:
        apply(args.year)


if __name__ == "__main__":
    main()
