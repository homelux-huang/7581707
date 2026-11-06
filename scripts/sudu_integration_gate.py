"""Read-only 115 integration gate. Never modifies official data or student history.

This is isolated QA staging, not a student publication path. Source assets are
linked by existing Git blobs, not regenerated or OCR'd here.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
VISUAL = ROOT / "sudu/data/QA_114_115_OFFICIAL_ANSWER_VISUAL_2026-10-22.json"
PAPERS = {
    "國文": "00-C", "英文": "00-E", "數學 B": "00-MB", "數學B": "00-MB",
    "商業概論": "09-1", "數位科技": "09-1",
    "會計學": "09-2", "經濟學": "09-2",
}
DEMO = {
    "國文": (1, 2, 3, 7, 9),
    "英文": (1, 2, 3, 4, 5),
    "數學 B": (7, 9, 10, 11, 12),
    "商業概論": (1, 3, 5, 6, 7),
    "數位科技": (26, 27, 28, 32, 34),
    "會計學": (2, 3, 4, 5, 6),
    "經濟學": (25, 26, 27, 28, 29),
}
ID = re.compile(r"^115-(00-C|00-E|00-MB|09-1|09-2)-\d{2}$")

def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def canonical_id(q: dict) -> str:
    subject = str(q.get("subject", ""))
    paper = str(q.get("paperCode", ""))
    year = q.get("year")
    number = q.get("originalQuestionNumber")
    if str(year) != "115" or paper != PAPERS.get(subject):
        raise ValueError("Invalid year / subject / paper mapping: " + str(q.get("questionId")))
    if not isinstance(number, int) or not (1 <= number <= 50):
        raise ValueError("Invalid original question number: " + repr(number))
    result = f"115-{paper}-{number:02d}"
    if not ID.fullmatch(result) or q.get("questionId") != result:
        raise ValueError("Canonical ID mismatch: " + str(q.get("questionId")) + " vs " + result)
    return result

def demo_id_map() -> dict:
    """Read-only mapping. Old subject|number learning-history keys stay untouched."""
    return {
        subject + "|" + str(n): f"115-{PAPERS[subject]}-{n:02d}"
        for subject, numbers in DEMO.items() for n in numbers
    }

def has_asset_proof(q: dict, item: dict, shared: dict) -> bool:
    """A PASS must describe this exact byte hash and every required shared crop."""
    if not item or item.get("qaStatus") != "PASS":
        return False
    qasset = (q.get("assets") or {}).get("singleQuestionWebp")
    qhash = (q.get("questionProvenance") or {}).get("webpSha256")
    output = item.get("output")
    digest = item.get("sha256")
    ev = item.get("visualReviewEvidence") or {}
    if not qasset or not digest or qasset != output or qhash != digest:
        return False
    if ev.get("reviewedSha256") != digest or not ev.get("reference"):
        return False
    for sid in q.get("sharedMaterialIds") or []:
        shared_item = shared.get(sid)
        if not shared_item or shared_item.get("qaStatus") != "PASS":
            return False
        sev = shared_item.get("visualReviewEvidence") or {}
        if sev.get("reviewedSha256") != shared_item.get("sha256"):
            return False
    return True

def source_data_eligible(q: dict, image_proof: bool, db_roundtrip: bool) -> bool:
    """G0-G5 are independent: no PDF-extracted answer or raw OCR implies verification."""
    return all((
        image_proof,
        bool((q.get("questionProvenance") or {}).get("officialPdfSha256")),
        db_roundtrip,
        q.get("textQaStatus") == "PASS",
        q.get("questionVerified") is True,
        q.get("answerVerified") is True,
        q.get("officialCorrectionChecked") is True,
        bool((q.get("answerProvenance") or {}).get("officialPdfSha256")),
    ))

def independent_comparison(q: dict) -> str:
    """AI evidence must be independent and answer-source-version bound."""
    audit = q.get("independentSolve") or {}
    if not isinstance(audit, dict) or audit.get("solvedWithoutOfficialAnswer") is not True:
        return "not_checked"
    if not audit.get("solvedAt") or not audit.get("questionRevision"):
        return "not_checked"
    if audit.get("questionRevision") != q.get("questionRevision"):
        return "not_checked"
    ai = str(audit.get("answer", "")).strip().upper()
    official = str(q.get("officialFinalAnswer", "")).strip().upper()
    if not re.fullmatch("[A-D]", ai) or not re.fullmatch("[A-D]", official):
        return "not_checked"
    return "matched" if ai == official else "mismatch"

def student_eligible(q: dict, data_eligible: bool) -> bool:
    return all((
        data_eligible,
        independent_comparison(q) == "matched",
        q.get("teachingQaStatus") == "PASS",
        q.get("uiQaStatus") == "PASS",
        q.get("studentReleaseApproved") is True,
    ))

def report() -> dict:
    bank = load(BASE / "questions.json")
    manifest = load(BASE / "webp-manifest.json")
    inventory = load(BASE / "inventory.json")
    validation = load(BASE / "VALIDATION.json")
    official = load(VISUAL)
    questions = bank.get("questions", [])
    items = {i["questionId"]: i for i in manifest.get("items", [])}
    shared = {i["sharedMaterialId"]: i for i in manifest.get("sharedMaterialCrops", [])}
    if not isinstance(questions, list):
        raise ValueError("questions.json requires questions array")
    rows, ids, issues = [], set(), []
    db_roundtrip = validation.get("sqlite") == "SQLITE_ROUNDTRIP_PASS"
    for q in questions:
        try:
            qid = canonical_id(q)
            if qid in ids:
                raise ValueError("Duplicate canonical ID " + qid)
            ids.add(qid)
        except ValueError as exc:
            issues.append(str(exc))
            continue
        item = items.get(qid)
        proof = has_asset_proof(q, item, shared)
        data_ok = source_data_eligible(q, proof, db_roundtrip)
        comparison = independent_comparison(q)
        rows.append({
            "id": qid, "subject": q["subject"], "imageManifestPass": bool(item and item.get("qaStatus") == "PASS"),
            "imageExactQaPass": proof, "textQaPass": q.get("textQaStatus") == "PASS" and q.get("questionVerified") is True,
            "answerFinalQaPass": q.get("answerVerified") is True and q.get("officialCorrectionChecked") is True,
            "dataReady": data_ok, "aiComparison": comparison,
            "studentReady": student_eligible(q, data_ok),
        })
    if len(items) != len(questions):
        issues.append("Question / manifest count mismatch")
    if len(ids) != len(questions):
        issues.append("Missing or duplicate canonical question IDs")
    counts = Counter(r["subject"] for r in rows)
    return {
        "snapshot": "115-candidate-isolated-from-main",
        "year": 115, "expected": inventory.get("rawOcrRecords"), "candidateQuestions": len(questions),
        "perSubject": {k: {
            "candidate": counts[k],
            "webpManifestPass": sum(x["subject"] == k and x["imageManifestPass"] for x in rows),
            "webpExactQaPass": sum(x["subject"] == k and x["imageExactQaPass"] for x in rows),
            "studentReady": sum(x["subject"] == k and x["studentReady"] for x in rows),
        } for k in sorted(counts)},
        "imageManifestPass": sum(x["imageManifestPass"] for x in rows),
        "imageExactQaPass": sum(x["imageExactQaPass"] for x in rows),
        "sharedImagePass": sum(x.get("qaStatus") == "PASS" for x in shared.values()),
        "sharedImageTotal": len(shared),
        "rawOcrCandidates": inventory.get("rawOcrRecords"),
        "textQaPass": sum(x["textQaPass"] for x in rows),
        "candidateOfficialVisualMatches": sum(
            x.get("year") == 115 and x.get("officialImageVisualCheck") == "PASS"
            and x.get("candidateComparison") == "MATCH"
            for x in official.get("results", [])
        ),
        "officialRevisionsAllChecked": bool(official.get("summary", {}).get("officialRevisionDocumentsReviewed")),
        "answerFinalQaPass": sum(x["answerFinalQaPass"] for x in rows),
        "dbRoundtripPass": db_roundtrip,
        "dataReady": sum(x["dataReady"] for x in rows),
        "aiAgreement": dict(Counter(x["aiComparison"] for x in rows)),
        "studentReady": sum(x["studentReady"] for x in rows),
        "demoLegacyIdMap": demo_id_map(),
        "issues": issues,
        "publication": "BLOCKED: no processed assets enter GitHub Pages allowlist",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = report()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    if args.check and (result["issues"] or result["candidateQuestions"] != 205
                       or result["imageManifestPass"] != 133
                       or result["sharedImageTotal"] != 20
                       or result["studentReady"] != 0):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
