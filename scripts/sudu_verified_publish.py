"""Promote only fully audited 114/115 questions to the existing GitHub Pages UI.

Reads the existing QA branch as DATA, never invokes its scripts or modifies any
original OCR, WebP, SQLite, source, localStorage or student history.
Import is per-question; audit/correction or teaching failures fail CLOSED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

YEARS = (114, 115)
PAPERS = {"00-C": "國文", "00-E": "英文", "00-MB": "數學 B"}
COUNT = {114: 205, 115: 205}
LETTERS = set("ABCD")
SHA = re.compile(r"^[0-9a-f]{64}$")
QID = re.compile(r"^(114|115)-(00-C|00-E|00-MB|09-1|09-2)-(\d{2})$")
EMPTY = re.compile(r"^\s*(?:NA|N/A|待補|未完成|本題無金額計算)\s*$", re.I)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)

def dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def good(text):
    return isinstance(text, str) and bool(text.strip()) and not EMPTY.fullmatch(text)

def subject_for(year: int, code: str, n: int) -> str | None:
    if code in PAPERS:
        return PAPERS[code]
    if code == "09-1":
        return "商業概論" if n <= 25 else "數位科技"
    if code == "09-2":
        return "會計學" if n <= 24 else "經濟學"
    return None

def stable(q: dict, year: int) -> tuple[str, str] | None:
    qid = q.get("questionId")
    m = QID.fullmatch(qid) if isinstance(qid, str) else None
    if not m or int(m.group(1)) != year or int(m.group(3)) < 1:
        return None
    number = int(m.group(3))
    subject = subject_for(year, m.group(2), number)
    if not subject or q.get("paperCode") != m.group(2) or q.get("originalQuestionNumber") != number:
        return None
    if q.get("subject") not in (subject, "數學B", "專業科目（一）", "專業科目(一)"):
        return None
    return qid, subject

def text_revision(q: dict, sha_webp: str) -> str:
    """Hash excludes answer so independent solving cannot derive the official key."""
    payload = {"question": q.get("question"), "options": q.get("options"), "singleQuestionWebpSha256": sha_webp}
    return digest(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())

def shared_material_ids(q: dict) -> tuple[str, ...] | None:
    """115 uses sharedMaterialId; 114 can use assets.sharedMaterialIds."""
    values = [q.get("sharedMaterialId"), q.get("sharedMaterialIds"),
              (q.get("assets") or {}).get("sharedMaterialIds")]
    found = []
    for value in values:
        if value in (None, "", []):
            continue
        if isinstance(value, str):
            ids = [value]
        elif isinstance(value, list) and all(isinstance(x, str) for x in value):
            ids = value
        else:
            return None
        for item in ids:
            if not item or item not in found:
                if not item:
                    return None
                found.append(item)
    return tuple(found)


def asset_rel_ok(rel: object, year: int, name: str, kind: str) -> bool:
    """Reject traversal and cross-question/cross-year WebP paths in QA data."""
    if not isinstance(rel, str):
        return False
    path = Path(rel)
    parts = path.parts
    if path.is_absolute() or ".." in parts or len(parts) != 7 or path.suffix != ".webp":
        return False
    if parts[:4] != ("sudu","data","processed",str(year)):
        return False
    if not re.fullmatch(r"webp-v[1-9][0-9]*",parts[4]):
        return False
    if kind == "single":
        match = QID.fullmatch(name)
        return bool(match and parts[5] == match.group(2) and path.name == name + ".webp")
    return parts[5] == "shared" and path.name == name + ".webp"


def image_sha(q: dict) -> str:
    return str((q.get("questionProvenance") or {}).get("webpSha256") or
               (q.get("assets") or {}).get("sha256") or "")


def pdf_sha(q: dict, kind: str) -> str:
    p = q.get("answerProvenance") if kind == "answer" else q.get("questionProvenance")
    return str((p or {}).get("officialPdfSha256") or (p or {}).get("pdfSha256") or "")


def individual_image_proof(q: dict, item: dict, src: Path) -> bool:
    if not item or item.get("qaStatus") != "PASS":
        return False
    out = item.get("output")
    h = item.get("sha256")
    ev = item.get("visualReviewEvidence") or {}
    year = int(q.get("year", 0))
    if not asset_rel_ok(out,year,str(q.get("questionId","")),"single"):
        return False
    if not SHA.fullmatch(str(h)) or ev.get("reviewedSha256") != h or not ev.get("reference"):
        return False
    if (q.get("assets") or {}).get("singleQuestionWebp") != out or image_sha(q) != h:
        return False
    file=src / out
    return file.is_file() and not file.is_symlink() and file.resolve().is_relative_to(src.resolve())


def image_proof(q: dict, item: dict, shared: dict, src: Path) -> bool:
    if not individual_image_proof(q,item,src):
        return False
    ids=shared_material_ids(q)
    if ids is None:
        return False
    for sid in ids:
        group = shared.get(sid)
        gev = (group or {}).get("visualReviewEvidence") or {}
        if not group or group.get("qaStatus") != "PASS" or gev.get("reviewedSha256") != group.get("sha256"):
            return False
        if not asset_rel_ok(group.get("output"),int(q["year"]),sid,"shared"):
            return False
        file=src/group["output"]
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(src.resolve()):
            return False
    return True

def source_proof(q: dict, image_good: bool, db_good: bool, revision: str) -> tuple[bool, bool]:
    """Separate question/OCR and official-final-answer gates; no legacy flags."""
    prov = q.get("questionProvenance") or {}
    ans = q.get("answerProvenance") or {}
    text = q.get("textQaEvidence") or {}
    official = q.get("officialFinalQaEvidence") or {}
    options = q.get("options")
    correct_text = (
        image_good and db_good and q.get("questionVerified") is True
        and q.get("textQaStatus") == "PASS"
        and good(q.get("question")) and isinstance(options, list)
        and len(options) == 4 and all(good(x) for x in options)
        and SHA.fullmatch(pdf_sha(q,"question")) is not None
        and text.get("questionRevision") == revision
        and text.get("sourceImageSha256") == (prov.get("pixelSourceSha256") or (q.get("assets") or {}).get("sourceSha256"))
        and good(text.get("reviewer")) and good(text.get("reviewedAt"))
        and good(text.get("evidencePath"))
    )
    final_answer = (
        q.get("answerVerified") is True and q.get("officialCorrectionChecked") is True
        and str(q.get("officialFinalAnswer", "")).upper() in LETTERS
        and SHA.fullmatch(pdf_sha(q,"answer")) is not None
        and official.get("answerPdfSha256") == pdf_sha(q,"answer")
        and official.get("finalCorrectionsReviewed") is True
        and good(official.get("reviewer")) and good(official.get("reviewedAt"))
        and good(official.get("evidencePath"))
    )
    return correct_text, final_answer

def independently_solved(q: dict, revision: str) -> str:
    """No solve evidence = pending, NEVER copy q.answer into a second column."""
    s = q.get("independentSolve") or {}
    if not all((
        s.get("solvedWithoutOfficialAnswer") is True,
        s.get("officialAnswerHiddenDuringSolve") is True,
        s.get("questionRevision") == revision,
        good(s.get("solvedAt")), good(s.get("solver")),
        good(s.get("reasoning")), good(s.get("auditEvidencePath")),
        str(s.get("answer", "")).upper() in LETTERS,
        str(q.get("officialFinalAnswer", "")).upper() in LETTERS,
    )):
        return "not_checked"
    return "matched" if s["answer"].upper() == q["officialFinalAnswer"].upper() else "mismatch"

def teaching_complete(q: dict, subject: str, official_answer: str) -> bool:
    t = q.get("teaching") or {}
    if not (q.get("teachingQaStatus") == "PASS" and q.get("uiQaStatus") == "PASS"
            and q.get("studentReleaseApproved") is True
            and good(t.get("teacherSummary")) and good(t.get("elementarySummary"))
            and good(t.get("memory")) and good(t.get("concept")) and good(t.get("extension"))
            and good(t.get("source"))):
        return False
    opts = t.get("optionExplanations") or {}
    if not isinstance(opts, dict) or set(opts) != LETTERS:
        return False
    if not all(isinstance(opts[L], dict) and good(opts[L].get("teacher")) and good(opts[L].get("elementary"))
               and good(opts[L].get("reason")) for L in LETTERS):
        return False
    if t.get("calculationReviewed") is not True or type(t.get("hasExamCalculation")) is not bool:
        return False
    if t["hasExamCalculation"]:
        c = t.get("examCalculation") or {}
        if not (isinstance(c.get("given"), list) and len(c["given"]) >= 1
                and all(good(x) for x in c["given"])
                and good(c.get("formulaUse"))
                and isinstance(c.get("substitution"), list) and c["substitution"]
                and all(good(x) for x in c["substitution"])
                and isinstance(c.get("steps"), list) and c["steps"]
                and all(good(x) for x in c["steps"])
                and good(c.get("result"))
                and c.get("option") == official_answer):
            return False
    elif t.get("examCalculation"):
        # No irrelevant examples or "no amount" placeholders masquerading as a calculation.
        return False
    evidence = q.get("teachingQaEvidence") or {}
    return bool(good(evidence.get("reviewer")) and good(evidence.get("reviewedAt"))
                and good(evidence.get("evidencePath")) and evidence.get("allFourOptionsReviewed") is True
                and evidence.get("calculationReviewed") is True)

def verify_bytes(source: Path, rel: str, expected: str) -> bool:
    try:
        if not isinstance(rel,str) or ".." in Path(rel).parts or Path(rel).is_absolute():
            return False
        file = source / rel
        if not file.resolve().is_relative_to(source.resolve()):
            return False
        if file.is_symlink() or any(x.is_symlink() for x in file.parents if x != source.parent):
            return False
        if not file.is_file() or digest(file.read_bytes()) != expected:
            return False
        from PIL import Image
        with Image.open(file) as im:
            im.load()
            return im.format == "WEBP" and im.width > 0 and im.height > 0 and im.height < 2000
    except (OSError, ValueError, ImportError):
        return False

def certificate_exists(source: Path, proof: dict, field: str, hash_field: str) -> bool:
    """Reject synthetic PASS flags without the original SHA-pinned review document."""
    relative = proof.get(field)
    digest_expected = proof.get(hash_field)
    if not isinstance(relative, str) or not relative or not SHA.fullmatch(str(digest_expected)):
        return False
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.suffix.lower() not in {".json", ".md", ".txt"}:
        return False
    document = source / path
    return document.is_file() and not document.is_symlink() and digest(document.read_bytes()) == digest_expected


def certificates_complete(source: Path, q: dict, item: dict, shared: dict) -> bool:
    """Source page, OCR, official final, independent solve and teaching audit all exist."""
    checks = [
        (item.get("visualReviewEvidence") or {}, "reference", "referenceSha256"),
        (q.get("textQaEvidence") or {}, "evidencePath", "evidenceSha256"),
        (q.get("officialFinalQaEvidence") or {}, "evidencePath", "evidenceSha256"),
        (q.get("independentSolve") or {}, "auditEvidencePath", "auditEvidenceSha256"),
        (q.get("teachingQaEvidence") or {}, "evidencePath", "evidenceSha256"),
        (q.get("uiQaEvidence") or {}, "evidencePath", "evidenceSha256"),
    ]
    for sid in shared_material_ids(q) or []:
        ev = shared[sid].get("visualReviewEvidence") or {}
        checks.append((ev, "reference", "referenceSha256"))
    return all(certificate_exists(source, evidence, field, hash_field)
               for evidence, field, hash_field in checks)


def visual_certificate(source: Path, item: dict, identity: str) -> bool:
    """Confirm the reviewed image SHA against an existing, versioned QA record.

    Modern QA records contain referenceSha256. Older 114 image-only JSON
    evidence instead must contain the same question ID, image SHA and PASS.
    This is image QA only: it never verifies OCR, official answers or teaching.
    """
    evidence = item.get("visualReviewEvidence") or {}
    rel = evidence.get("reference")
    if evidence.get("reviewedSha256") != item.get("sha256"):
        return False
    if not isinstance(rel, str) or not rel:
        return False
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts or p.suffix not in {".json", ".md"}:
        return False
    record = source / p
    if not record.resolve().is_relative_to(source.resolve()) or record.is_symlink() or not record.is_file():
        return False
    payload = record.read_bytes()
    expected = evidence.get("referenceSha256")
    if expected is not None:
        return bool(SHA.fullmatch(str(expected)) and digest(payload) == expected)
    if p.suffix != ".json":
        return False
    try:
        parsed = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    # Older source does not have a file SHA claim. Validate the immutable Git
    # source copy by matching a genuine per-question visual-QA record.
    for row in parsed.get("records", []):
        if (row.get("questionId") == identity and row.get("result") == "PASS"
                and row.get("webpSha256") == item.get("sha256")
                and row.get("webpPath") == item.get("output")):
            return True
    return False


def certified_visual_assets(source: Path, q: dict, item: dict, shared: dict) -> list[tuple[str, str, str]] | None:
    """Return original source path, destination basename and sha for review-only assets."""
    if not image_proof(q, item, shared, source):
        return None
    qid = q["questionId"]
    if not visual_certificate(source,item,qid):
        return None
    ids = shared_material_ids(q)
    if ids is None:
        return None
    assets = [(item["output"], qid, item["sha256"])]
    for sid in ids:
        group = shared.get(sid)
        if not group or not visual_certificate(source,group,sid):
            return None
        assets.append((group["output"], sid, group["sha256"]))
    if not all(verify_bytes(source,rel,sha) for rel,_,sha in assets):
        return None
    return assets


def public_question(q: dict, year: int, subject: str, image_path: str) -> dict:
    t = q["teaching"]
    calc = t["examCalculation"] if t["hasExamCalculation"] else None
    lines = []
    if calc:
        lines = (
            ["已知條件："+x for x in calc["given"]]
            + ["公式用途："+calc["formulaUse"]]
            + ["代入："+x for x in calc["substitution"]]
            + calc["steps"]
            + ["結果："+calc["result"]+(("；單位："+calc["unit"]) if calc.get("unit") else ""),
               "對應選項："+calc["option"]]
        )
    return {
        "id": q["originalQuestionNumber"], "canonicalId":q["questionId"],
        "year":year, "subject":subject, "topic":str(t.get("topic") or subject),
        "question":q["question"], "options":q["options"], "answer":q["officialFinalAnswer"].upper(),
        "memory":re.sub(r"\*\*(.*?)\*\*",r"\1",t["memory"]),
        "highlights":t.get("highlights") or [],
        "concept":t["concept"],"extension":t["extension"],
        "formula":str(t.get("formula") or ""),"sourceText":t["source"],"extra":t.get("extra") or {},
        "teacherSummary":t["teacherSummary"], "elementarySummary":t["elementarySummary"],
        "optionExplanations":t["optionExplanations"],
        "examCalculation":{"hasExamCalculation":bool(calc),"lines":lines} if calc else None,
        "image":image_path,
        "imageSha256":image_sha(q),
    }

def reviewed_student_batches(source: Path, year: int) -> dict[str, dict]:
    """Additive, SHA-anchored certificates without rewriting huge OCR/DB sources."""
    file = source / f"sudu/data/processed/{year}/verified-student-batch.json"
    if not file.exists():
        return {}
    data = read(file)
    if data.get("schemaVersion") != 1 or data.get("year") != year:
        raise ValueError(f"{year} invalid verified-student-batch header")
    result = {}
    for item in data.get("items", []):
        qid = item.get("questionId")
        if not isinstance(qid,str) or not QID.fullmatch(qid) or not qid.startswith(str(year)+"-"):
            raise ValueError(f"{year} wrong student certificate ID")
        if qid in result:
            raise ValueError(f"Duplicate student certificate {qid}")
        result[qid] = item
    return result


def review_document(source: Path, year: int, rel: object, qid: str) -> tuple[dict, str] | None:
    """Proof is versioned in source commit; SHA is pinned to its actual bytes."""
    if not isinstance(rel,str):
        return None
    prefix=f"sudu/data/processed/{year}/review-evidence/"
    if not rel.startswith(prefix) or Path(rel).is_absolute() or ".." in Path(rel).parts or not rel.endswith(".json"):
        return None
    path=source/rel
    if not path.resolve().is_relative_to(source.resolve()) or path.is_symlink() or not path.is_file():
        return None
    raw=path.read_bytes()
    data=json.loads(raw)
    if data.get("questionId") != qid or data.get("year") != year or data.get("schemaVersion") != 1:
        return None
    return data,digest(raw)


def apply_independently_certified_review(source: Path, year: int, q: dict, manifest: dict,
                                        audit: dict | None) -> dict:
    """Fail closed: a source or answer change invalidates the entire certificate.

    Never changes original QID, answer candidate, OCR source, crop or SQLite.
    OCR and answer review are separately evidenced; blind-solve doc does not
    contain the official key and is checked only after the independent solve.
    """
    if audit is None or audit.get("status") != "STUDENT_QA_APPROVED":
        return q
    qid=q["questionId"]
    if (audit.get("questionId") != qid or audit.get("year") != year
            or audit.get("questionBeforeReview") != q.get("question")
            or audit.get("optionsBeforeReview") != q.get("options")
            or audit.get("webpSha256") != (manifest or {}).get("sha256")
            or audit.get("officialPdfSha256") != pdf_sha(q,"answer")
            or audit.get("questionPdfSha256") != pdf_sha(q,"question")
            or audit.get("originalAnswerCandidate") != q.get("answer")
            or q.get("answerMatched") is not True):
        return q
    docs={}
    for key in ("ocr","official","blind","teaching","ui"):
        value=review_document(source,year,(audit.get("evidence") or {}).get(key),qid)
        if value is None:
            return q
        docs[key]=value
    ocr,off,blind,teach,ui=[docs[key][0] for key in ("ocr","official","blind","teaching","ui")]
    revision=text_revision(q,manifest["sha256"])
    if not all((
        ocr.get("questionRevision") == revision,
        ocr.get("webpSha256") == manifest["sha256"],
        ocr.get("question") == q.get("question"),
        ocr.get("options") == q.get("options"),
        ocr.get("visualTextCompared") is True,
        off.get("officialPdfSha256") == pdf_sha(q,"answer"),
        off.get("finalAnswer") == q.get("answer"),
        off.get("correctionNoticeReviewed") is True,
        off.get("officialPage") == "https://web1.tcte.edu.tw/EXAM/115_4y/",
        off.get("noObjectionForPaper") is True,
        blind.get("questionRevision") == revision,
        blind.get("webpSha256") == manifest["sha256"],
        blind.get("officialAnswerHiddenDuringSolve") is True,
        blind.get("solvedWithoutOfficialAnswer") is True,
        blind.get("blindReasoning") and blind.get("answer") in LETTERS,
        "officialAnswer" not in blind and "officialPdfSha256" not in blind,
        teach.get("questionRevision") == revision,
        teach.get("allFourOptionsReviewed") is True,
        teach.get("calculationReviewed") is True,
        isinstance(teach.get("content"),dict),
        ui.get("testedQuestionRevision") == revision,
        ui.get("browserSmokePassed") is True,
        ui.get("rwdPassed") is True,
        ui.get("verifiedYearQaMode") is True,
        isinstance(ui.get("ciRunUrl"),str) and ui["ciRunUrl"].startswith(
            "https://github.com/homelux-huang/7581707/actions/runs/"),
    )):
        return q
    reviewer=ocr.get("reviewer")
    date=ocr.get("reviewedAt")
    if not good(reviewer) or not good(date):
        return q
    def ev(key: str) -> dict:
        return {"reviewer":docs[key][0].get("reviewer") or reviewer,
                "reviewedAt":docs[key][0].get("reviewedAt") or date,
                "evidencePath":audit["evidence"][key],"evidenceSha256":docs[key][1]}
    reviewed=dict(q)
    reviewed.update({
        "questionVerified":True,"textQaStatus":"PASS",
        "textQaEvidence":{**ev("ocr"),"questionRevision":revision,
            "sourceImageSha256":(q.get("questionProvenance") or {}).get("pixelSourceSha256")
                or (q.get("assets") or {}).get("sourceSha256")},
        "officialFinalAnswer":off["finalAnswer"],"answerVerified":True,
        "officialCorrectionChecked":True,
        "officialFinalQaEvidence":{**ev("official"),"answerPdfSha256":pdf_sha(q,"answer"),
                                    "finalCorrectionsReviewed":True},
        "independentSolve":{
            **ev("blind"),"answer":blind["answer"],"reasoning":blind["blindReasoning"],
            "questionRevision":revision,"officialAnswerHiddenDuringSolve":True,
            "solvedWithoutOfficialAnswer":True,"solver":blind.get("solver") or reviewer,
            "solvedAt":blind.get("solvedAt") or date,
            "auditEvidencePath":audit["evidence"]["blind"],
            "auditEvidenceSha256":docs["blind"][1]},
        "teaching":teach["content"],"teachingQaStatus":"PASS",
        "teachingQaEvidence":{**ev("teaching"),"allFourOptionsReviewed":True,
                              "calculationReviewed":True},
        "uiQaStatus":"PASS",
        "uiQaEvidence":ev("ui"),"studentReleaseApproved":True
    })
    return reviewed


def snapshot(src: Path, output: Path, year: int, source_sha: str) -> dict:
    d = src / f"sudu/data/processed/{year}"
    bank, manifest = read(d / "questions.json"), read(d / "webp-manifest.json")
    inventory = read(d / "inventory.json")
    questions = bank["questions"]
    certified_reviews = reviewed_student_batches(src,year)
    entries = {i["questionId"]:i for i in manifest["items"]}
    shared = {i["sharedMaterialId"]:i for i in manifest.get("sharedMaterialCrops", [])}
    db_good = bool((d/"question-bank.sqlite3").is_file()) and (
        (year == 115 and (d/"VALIDATION.json").is_file() and read(d/"VALIDATION.json").get("sqlite") == "SQLITE_ROUNDTRIP_PASS")
        or (year == 114 and bool(inventory.get("sqlite",{}).get("roundtripPass"))))
    qa_per_subject = defaultdict(lambda:{"expected":0, "candidate":0,"webpQaPass":0,"imagePreviewReady":0,"ocrQaPass":0,"finalAnswerQaPass":0,"studentReady":0})
    released, previewed, approved_files, blocked, ai = [], [], set(), [], Counter()
    seen=set()
    for q in questions:
        identity = stable(q, year)
        if not identity:
            blocked.append({"id":str(q.get("questionId")),"reason":"invalid_id_mapping"})
            continue
        qid,subject = identity
        if qid in seen:
            raise ValueError(f"Duplicate stable question ID: {qid}")
        seen.add(qid)
        item = entries.get(qid)
        q = apply_independently_certified_review(src,year,q,item,certified_reviews.get(qid))
        qa_per_subject[subject]["candidate"] += 1
        image_ok = image_proof(q, item, shared, src)
        if individual_image_proof(q,item,src):
            qa_per_subject[subject]["webpQaPass"] += 1
        certified = certified_visual_assets(src,q,item,shared) if image_ok else None
        if certified is not None:
            image_list=[]
            for source_rel,asset_id,asset_sha in certified:
                destination_rel=f"data/approved/webp/{year}/{asset_id}.webp"
                destination=output/"sudu"/destination_rel
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(src/source_rel,destination)
                approved_files.add(destination.resolve())
                image_list.append({"image":destination_rel,"sha256":asset_sha})
            previewed.append({
                "canonicalId":qid,"year":year,"subject":subject,
                "questionNumber":q["originalQuestionNumber"],
                "image":image_list[0]["image"],"imageSha256":image_list[0]["sha256"],
                "sharedImages":image_list[1:],
                "reviewStage":"image_qa_pass_only",
            })
            qa_per_subject[subject]["imagePreviewReady"] += 1
        revision = text_revision(q, item.get("sha256", "") if item else "")
        ocr_ok, official_ok = source_proof(q,image_ok,db_good,revision)
        qa_per_subject[subject]["ocrQaPass"] += int(ocr_ok)
        qa_per_subject[subject]["finalAnswerQaPass"] += int(official_ok)
        solve = independently_solved(q,revision)
        ai[solve] += 1
        reason = ("image_pending" if not image_ok else "ocr_or_db_pending" if not ocr_ok
                  else "official_final_pending" if not official_ok else "ai_"+solve if solve != "matched"
                  else "teaching_pending")
        if not (ocr_ok and official_ok and solve == "matched"
                and teaching_complete(q,subject,str(q.get("officialFinalAnswer","")).upper())):
            blocked.append({"id":qid,"reason":reason})
            continue
        if not certificates_complete(src,q,item,shared):
            blocked.append({"id":qid,"reason":"sha_pinned_qa_certificate_missing"})
            continue
        rel = item["output"]
        if not verify_bytes(src,rel,item["sha256"]):
            blocked.append({"id":qid,"reason":"asset_sha_or_decode_failed"})
            continue
        shared_ids = shared_material_ids(q) or []
        if not all(verify_bytes(src,shared[s]["output"],shared[s]["sha256"]) for s in shared_ids):
            blocked.append({"id":qid,"reason":"shared_asset_sha_or_decode_failed"})
            continue
        location = f"data/approved/webp/{year}/{qid}.webp"
        target = output / "sudu" / location
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src/rel,target)
        approved_files.add(target.resolve())
        released.append(public_question(q,year,subject,location))
        qa_per_subject[subject]["studentReady"] += 1
    expected = int(inventory.get("expected",manifest.get("expected",COUNT[year])))
    if expected != COUNT[year] or len(questions) != expected or len(entries) != expected or len(seen) != expected:
        raise ValueError(f"{year} mismatch expected/candidates/manifest/IDs: {expected}/{len(questions)}/{len(entries)}/{len(seen)}")
    # Revoke obsolete public copies; originals in QA source branch remain untouched.
    webp_dir = output / f"sudu/data/approved/webp/{year}"
    for p in webp_dir.glob("*.webp") if webp_dir.exists() else []:
        if p.resolve() not in approved_files:
            p.unlink()
    out = {"schemaVersion":1,"year":year,"sourceSha":source_sha,"expected":expected,
           "approvedCount":len(released),"questions":released}
    dump(output / f"sudu/data/approved/{year}.json",out)
    # Public preview contains ONLY individually reviewed original WebP images.
    # Never serialize draft OCR, answer candidates, option keys or teaching.
    dump(output / f"sudu/data/approved/preview/{year}.json",{
        "schemaVersion":1,"year":year,"expected":expected,"sourceSha":source_sha,
        "imagePreviewCount":len(previewed),"questions":previewed
    })
    shared_pass = sum(x.get("qaStatus") == "PASS" and
                      (x.get("visualReviewEvidence") or {}).get("reviewedSha256") == x.get("sha256")
                      for x in shared.values())
    return {
        "year":year,"expected":expected,"candidate":len(questions),
        "webpGenerated":len(entries), "webpQaPass":sum(x["webpQaPass"] for x in qa_per_subject.values()),
        "sharedWebpQaPass":shared_pass, "sharedWebpTotal":len(shared),
        "ocrCandidate":int(inventory.get("rawOcrRecords",len(questions))),
        "ocrQaPass":sum(x["ocrQaPass"] for x in qa_per_subject.values()),
        "officialCandidateMatches":int(inventory.get("answerCandidatesMatchedAcrossTextAndImage",
                                              inventory.get("officialPdfTextAnswerMatched",0))),
        "officialFinalQaPass":sum(x["finalAnswerQaPass"] for x in qa_per_subject.values()),
        "aiSolvedMatched":ai["matched"],"aiMismatch":ai["mismatch"],"aiNotChecked":ai["not_checked"],
        "approvedCount":len(released), "imagePreviewCount":len(previewed),
        "imagePreviewPercent":round(100*len(previewed)/expected,1),
        "imageQaPercent":round(100*sum(x["webpQaPass"] for x in qa_per_subject.values())/expected,1),
        "approvedPercent":round(100*len(released)/expected,1),
        "subjects":dict(sorted(qa_per_subject.items())),
        "pending":len(blocked), "pendingReasonCounts":dict(Counter(x["reason"] for x in blocked)),
        "reviewStatus":"not_all_gates_passed" if len(released)<expected else "all_question_gates_passed",
        "sourceSha":source_sha,
    }

def stage(source: Path, dest: Path, source_sha: str, source_tree_signature: str = ""):
    report = { "schemaVersion":1, "dataStage":"qa_verified_only",
        "notYetLiveUntilPagesSuccess":True,
        "provenance":{"ref":"qa/114-115-official-visual-review","commit":source_sha,
                      "sourceTreeSignature":source_tree_signature or source_sha,
                      "certificationSchemaVersion":"student-reviewed-batch-v1"},
        "years":{}}
    for year in YEARS:
        report["years"][str(year)] = snapshot(source,dest,year,source_sha)
    dump(dest/"sudu/data/approved/progress.json",report)
    return report

def site_check(dest: Path):
    status=read(dest/"sudu/data/approved/progress.json")
    for year in YEARS:
        p=read(dest/f"sudu/data/approved/{year}.json")
        qs=p["questions"]
        assert p["year"]==year and p["expected"]==COUNT[year]
        assert len(qs)==p["approvedCount"]==status["years"][str(year)]["approvedCount"]
        seen=set()
        preview_file=read(dest/f"sudu/data/approved/preview/{year}.json")
        pictures=preview_file.get("questions")
        assert isinstance(pictures,list)
        assert preview_file["year"]==year and preview_file["expected"]==COUNT[year]
        assert preview_file["imagePreviewCount"]==len(pictures)==status["years"][str(year)].get("imagePreviewCount",0)
        seen_preview=set()
        for item in pictures:
            identity=item["canonicalId"]
            assert identity not in seen_preview and QID.fullmatch(identity)
            seen_preview.add(identity)
            assert item["year"]==year and item["reviewStage"]=="image_qa_pass_only"
            assert item["image"]==f"data/approved/webp/{year}/{identity}.webp"
            assert digest((dest/"sudu"/item["image"]).read_bytes())==item["imageSha256"]
            for shared_image in item["sharedImages"]:
                assert shared_image["image"].startswith(f"data/approved/webp/{year}/{year}-")
                assert digest((dest/"sudu"/shared_image["image"]).read_bytes())==shared_image["sha256"]
            # Public image-only previews MUST NEVER leak answer candidates or OCR.
            assert not ({"answer","question","options","teaching","memory","independentSolve"} & set(item))
        for q in qs:
            qid=q["canonicalId"]
            assert qid not in seen and QID.fullmatch(qid)
            seen.add(qid)
            assert q["year"]==year and q["answer"] in LETTERS
            assert len(q["options"])==4 and all(good(x) for x in q["options"])
            assert set(q["optionExplanations"])==LETTERS
            assert all(good(q["optionExplanations"][l]["teacher"]) and good(q["optionExplanations"][l]["elementary"]) for l in LETTERS)
            c=q.get("examCalculation")
            if c is not None:
                assert c["hasExamCalculation"] is True and len(c["lines"])>=5
            path=dest/"sudu"/q["image"]
            assert path.is_file() and path.suffix==".webp"
            assert digest(path.read_bytes()) == q["imageSha256"], qid
    return status

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("stage","check"))
    parser.add_argument("--source",type=Path)
    parser.add_argument("--dest",type=Path,default=Path("."))
    parser.add_argument("--sha",default="unknown")
    parser.add_argument("--signature",default="")
    a=parser.parse_args()
    if a.command=="stage":
        if a.source is None:
            parser.error("--source is required")
        print(json.dumps(stage(a.source,a.dest,a.sha,a.signature),ensure_ascii=False,indent=2))
    else:
        result=site_check(a.dest)
        print("PASS: only QA-released 114/115 records can enter the official Pages artifact:",{k:v["approvedCount"] for k,v in result["years"].items()})

if __name__=="__main__":
    main()
