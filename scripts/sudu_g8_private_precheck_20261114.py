"""Build a PRIVATE technical V4-shape preview, never an admission.

This intentionally does not call the distinct-AI gate, mark UI PASS, mutate
a canonical source bank, or write official approved files. Its only purpose is
to inspect the REAL production serializer shape on G2/G3/source-verified data
and an immutable author G5 issuer, ahead of a separately reviewed G8 bridge.

The resulting content INCLUDES answer text: keep it inside a local private
OS-temp directory, never as a GitHub/public artifact or Pages asset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from scripts import sudu_independent_review_gate as reviewer_gate
from scripts import sudu_verified_publish as publisher

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^(114|115)-(00-C|00-E|00-MB|09-1|09-2)-[0-9]{2}$")
STATE = "TECHNICAL_PRECHECK_ONLY"


class PrecheckHold(ValueError):
    """Fail closed without creating a student artifact."""


def _private_location(destination: Path, source: Path) -> Path:
    """Permit only a new, non-symlink OS temp subdirectory."""
    raw = Path(destination).expanduser()
    temp = Path(tempfile.gettempdir()).resolve()
    if not raw.is_absolute():
        raise PrecheckHold("absolute private temp destination required")
    # Resolve without following a late-created path in the returned location.
    for path in (raw, *raw.parents):
        if path.exists() and path.is_symlink():
            raise PrecheckHold("symlink destination refused")
    path = raw.resolve(strict=False)
    if (path == temp or not path.is_relative_to(temp)
            or not path.name.startswith("sudu-private-g8-")
            or path.is_relative_to(source.resolve())
            or path.is_relative_to(Path.cwd().resolve())
            or any(part.lower() in {"approved", "public", "pages"} for part in path.parts)):
        raise PrecheckHold("not a quarantined OS temp location")
    return path


def _one_native_evidence(source: Path, year: int, qid: str, kind: str) -> dict:
    folder = source / f"sudu/data/processed/{year}/review-evidence"
    matches = sorted(folder.glob(f"{qid}-{kind}-publisher-*.json"))
    if len(matches) != 1:
        raise PrecheckHold(f"expected exactly one {kind} native issuer")
    relative = matches[0].relative_to(source).as_posix()
    doc = publisher.review_document(source, year, relative, qid)
    if doc is None:
        raise PrecheckHold(f"invalid {kind} native issuer")
    return doc[0]


def _valid_author_teaching(teaching: object) -> bool:
    if not isinstance(teaching, dict):
        return False
    keys = ("teacherSummary", "elementarySummary", "memory", "concept",
            "extension", "source")
    if not all(publisher.good(teaching.get(k)) for k in keys):
        return False
    explanations = teaching.get("optionExplanations")
    if not isinstance(explanations, dict) or set(explanations) != set("ABCD"):
        return False
    for key in "ABCD":
        entry = explanations[key]
        if not isinstance(entry, dict) or not all(
            publisher.good(entry.get(k)) for k in ("teacher", "elementary", "reason")
        ):
            return False
    if type(teaching.get("hasExamCalculation")) is not bool:
        return False
    calc = teaching.get("examCalculation")
    if teaching["hasExamCalculation"]:
        if not isinstance(calc, dict):
            return False
        if not isinstance(calc.get("given"), list) or not calc["given"]:
            return False
        if not isinstance(calc.get("substitution"), list) or not calc["substitution"]:
            return False
        if not isinstance(calc.get("steps"), list) or not calc["steps"]:
            return False
        if not all(publisher.good(x) for x in
                   [*calc["given"], *calc["substitution"], *calc["steps"]]):
            return False
        return (publisher.good(calc.get("formulaUse"))
                and publisher.good(calc.get("result"))
                and calc.get("option") in "ABCD")
    return calc in (None, {})


def _exclusive_write(path: Path, payload: bytes) -> None:
    # Exclusive creation means subsequent reruns cannot silently overwrite
    # a previous privacy-sensitive snapshot.
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    os.chmod(path, 0o600)


def build_private_precheck(source: Path, destination: Path, qid: str,
                           source_commit: str, expected_teaching_sha: str) -> dict:
    """Write one non-public local preview; NEVER authorize a release."""
    source = Path(source).resolve()
    out = _private_location(destination, source)
    if not SAFE_ID.fullmatch(qid):
        raise PrecheckHold("invalid or non-114/115 QID")
    if not SHA40.fullmatch(source_commit):
        raise PrecheckHold("actual source commit SHA required")
    if not SHA64.fullmatch(expected_teaching_sha):
        raise PrecheckHold("expected original teaching digest required")
    year = int(qid[:3])
    base = source / f"sudu/data/processed/{year}"
    if not base.is_dir() or base.is_symlink():
        raise PrecheckHold("real QA source directory missing")
    try:
        bank = publisher.read(base / "questions.json")
        manifest = publisher.read(base / "webp-manifest.json")
        inventory = publisher.read(base / "inventory.json")
    except (OSError, ValueError, TypeError) as exc:
        raise PrecheckHold("official source files missing or malformed") from exc
    rows = bank.get("questions", [])
    assets = manifest.get("items", [])
    if (len(rows) != 205 or len(assets) != 205
            or len({r.get("questionId") for r in rows}) != 205
            or len({a.get("questionId") for a in assets}) != 205):
        raise PrecheckHold("205-row native bank/manifest consistency failed")
    matched = [row for row in rows if row.get("questionId") == qid]
    manifest_rows = [a for a in assets if a.get("questionId") == qid]
    if len(matched) != 1 or len(manifest_rows) != 1:
        raise PrecheckHold("QID absent or ambiguous")
    q, image = matched[0], manifest_rows[0]
    identity = publisher.stable(q, year)
    if identity is None or identity[0] != qid:
        raise PrecheckHold("QID/subject/number mapping invalid")
    if not (q.get("questionVerified") is True and q.get("answerVerified") is True
            and q.get("officialCorrectionChecked") is True
            and q.get("answerMatched") is True):
        raise PrecheckHold("native source/official flags incomplete")
    if q.get("officialFinalAnswer") != q.get("answer"):
        raise PrecheckHold("candidate and official answer disagree")
    shared = {a["sharedMaterialId"]: a for a in manifest.get("sharedMaterialCrops", [])}
    certified_assets = publisher.certified_visual_assets(source, q, image, shared)
    if certified_assets is None:
        raise PrecheckHold("original image WebP/crop/SHA is not certified")
    revision = publisher.text_revision(q, image["sha256"])
    sqlite_ok = (base / "question-bank.sqlite3").is_file() and (
        (year == 114 and bool((inventory.get("sqlite") or {}).get("roundtripPass")))
        or (year == 115 and (base / "VALIDATION.json").is_file()
            and publisher.read(base / "VALIDATION.json").get("sqlite")
            == "SQLITE_ROUNDTRIP_PASS")
    )
    text_ok, answer_ok = publisher.source_proof(q, True, sqlite_ok, revision)
    if not text_ok or not answer_ok:
        raise PrecheckHold("G2/G3 source proof incomplete")
    ocr = _one_native_evidence(source, year, qid, "ocr")
    official = _one_native_evidence(source, year, qid, "official")
    teach = _one_native_evidence(source, year, qid, "teaching")
    if not all((
        ocr.get("questionRevision") == revision,
        ocr.get("webpSha256") == image["sha256"],
        ocr.get("question") == q.get("question"),
        ocr.get("options") == q.get("options"),
        ocr.get("visualTextCompared") is True,
        official.get("finalAnswer") == q["answer"],
        official.get("correctionNoticeReviewed") is True,
        official.get("officialPage") == publisher.official_source_index(year),
        publisher.official_notice_scope_certified(source, year, q, official),
        teach.get("questionRevision") == revision,
        teach.get("webpSha256") == image["sha256"],
        teach.get("allFourOptionsReviewed") is True,
        teach.get("calculationReviewed") is True,
        teach.get("studentReleaseApproved") is False,
        teach.get("independentAiContentReviewed") is False,
    )):
        raise PrecheckHold("native source/author issuer mismatch")
    authored = teach.get("content")
    if not _valid_author_teaching(authored):
        raise PrecheckHold("incomplete original teacher/elementary A-D or calculation")
    canonical = reviewer_gate.digest(reviewer_gate.canonical(authored))
    if (canonical != expected_teaching_sha
            or teach.get("canonicalTeachingSha256") != canonical):
        raise PrecheckHold("original author teaching changed")
    reviewed = dict(q)
    reviewed["teaching"] = authored
    reviewed["officialFinalAnswer"] = official["finalAnswer"]
    # This is the actual protected-main student serializer, not a retyped
    # interpretation of the V4 data contract. It does not authorize release.
    preview = publisher.public_question(
        reviewed, year, identity[1], f"images/{qid}.webp"
    )
    if (preview.get("canonicalId") != qid
            or preview.get("imageSha256") != image["sha256"]
            or preview.get("answer") != official["finalAnswer"]):
        raise PrecheckHold("native serializer returned inconsistent material")

    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(out, 0o700)
    image_dir = out / "images"
    image_dir.mkdir(mode=0o700, exist_ok=True)
    os.chmod(image_dir, 0o700)
    original_webp = source / certified_assets[0][0]
    raw_image = original_webp.read_bytes()
    if hashlib.sha256(raw_image).hexdigest() != image["sha256"]:
        raise PrecheckHold("original image changed during preview emission")
    _exclusive_write(image_dir / (qid + ".webp"), raw_image)
    payload = {
        "schemaVersion": 1, "status": STATE,
        "privateOnly": True, "studentReleaseApproved": False,
        "distinctAiReviewAuthorized": False, "firstBlindProven": False,
        "formalG8": False, "pagesEligible": False,
        "year": year, "questionId": qid, "sourceCommitClaim": source_commit,
        "questionRevision": revision, "originalWebpSha256": image["sha256"],
        "canonicalTeachingSha256": canonical,
        "serializer": "scripts.sudu_verified_publish.public_question",
        "serializedStudentShapeForPrivateInspectionOnly": preview
    }
    serialized = (json.dumps(payload, sort_keys=True, ensure_ascii=False,
                             indent=2) + "\n").encode("utf-8")
    target = out / (qid + ".technical-precheck.json")
    _exclusive_write(target, serialized)
    return {
        "status": STATE, "questionId": qid,
        "sourceCommitClaim": source_commit,
        "questionRevision": revision,
        "originalWebpSha256": image["sha256"],
        "canonicalTeachingSha256": canonical,
        "privateJsonSha256": hashlib.sha256(serialized).hexdigest(),
        "studentReady": False, "formalG8": False, "pagesEligible": False,
        "destination": str(out)
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--qid", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--teaching-sha", required=True)
    args = parser.parse_args()
    try:
        status = build_private_precheck(
            args.source, args.dest, args.qid, args.source_sha, args.teaching_sha
        )
    except PrecheckHold as exc:
        parser.exit(2, f"TECHNICAL_PRECHECK_HOLD: {exc}\n")
    # Never dump the private student serialization/answer into job logs.
    print(json.dumps(status, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
