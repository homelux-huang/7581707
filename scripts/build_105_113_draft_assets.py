#!/usr/bin/env python3
"""Generate 105-113 official-source single-question DRAFT assets only.

Reuses existing years JSON and source page WebP; never overwrites them.
Draft OCR, source-text answer matching, and structural checks are NOT visual QA.
No UI, student state, main, production, or released files are touched.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import urljoin, urlparse

import fitz
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {"tcte.edu.tw", "www.tcte.edu.tw", "web1.tcte.edu.tw"}
PAPERS = ("00-C", "00-E", "00-MB", "09-1", "09-2")
NUMBER = re.compile(r"^(\d{1,2})[.．、](?:\S*)$")
ANSWER = re.compile(r"(?<!\d)(\d{1,3})[ \t]+([ABCD])(?=\s|$)")
VERSION = "historical-official-pixel-draft-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def official_pdf(url, expected, cache):
    path = urlparse(url)
    if path.scheme != "https" or path.hostname not in HOSTS:
        raise ValueError("Not a TCTE official URL: " + url)
    cache.mkdir(parents=True, exist_ok=True)
    cached = cache / (expected + ".pdf")
    if cached.exists():
        payload = cached.read_bytes()
        if sha(payload) == expected and payload.startswith(b"%PDF"):
            return payload
    current = url
    for attempt in range(5):
        parsed = urlparse(current)
        if parsed.scheme != "https" or parsed.hostname not in HOSTS:
            raise ValueError("Unofficial redirect: " + current)
        response = requests.get(
            current, timeout=(20, 100), allow_redirects=False,
            headers={"User-Agent": "7581707-historical-official-review/1.0"})
        if response.is_redirect:
            current = urljoin(current, response.headers["Location"])
            continue
        response.raise_for_status()
        payload = response.content
        if not payload.startswith(b"%PDF") or len(payload) > 40_000_000:
            raise ValueError("Invalid official PDF bytes")
        actual = sha(payload)
        if actual != expected:
            raise ValueError("Official PDF SHA mismatch expected=" + expected + " actual=" + actual)
        cached.write_bytes(payload)
        return payload
    raise ValueError("Too many redirects")


def official_answers(pdfdata, upper):
    out, conflict = {}, set()
    with fitz.open(stream=pdfdata, filetype="pdf") as doc:
        for page_idx, page in enumerate(doc, 1):
            for match in ANSWER.finditer(page.get_text(sort=True)):
                n = int(match.group(1))
                if not (1 <= n <= upper):
                    continue
                letter = match.group(2)
                if n in out and out[n]["answer"] != letter:
                    conflict.add(n)
                else:
                    out[n] = {"answer": letter, "page": page_idx}
    for n in conflict:
        out.pop(n, None)
    return out, sorted(conflict)


def pdf_number_anchors(doc, valid_numbers):
    by_number = defaultdict(list)
    for ix, page in enumerate(doc, 1):
        if ix == 1:
            continue
        for x0, y0, x1, y1, word, *_ in page.get_text("words", sort=True):
            match = NUMBER.match(word.strip())
            if not match:
                continue
            n = int(match.group(1))
            if n in valid_numbers and 20 <= x0 <= 110 and 35 <= y0 <= page.rect.height - 40:
                by_number[n].append({"page": ix, "y": float(y0), "x": float(x0)})
    return by_number


def decide_anchors(questions, candidates):
    selected, ambiguous, missing, suspect = {}, {}, [], []
    last = (1, 0.0)
    for q in sorted(questions, key=lambda x: int(x["number"])):
        n = int(q["number"])
        possible = sorted(
            (v for v in candidates.get(n, [])
             if (v["page"], v["y"]) > last),
            key=lambda x: (x["page"], x["y"]))
        recorded_page = q.get("page")
        if type(recorded_page) is int:
            on_page = [v for v in possible if v["page"] == recorded_page]
            if on_page:
                possible = on_page
            elif possible:
                suspect.append({"number": n, "legacyPage": recorded_page,
                                "possiblePages": [v["page"] for v in possible]})
                # The conflicting page could indicate a parser issue; don't trust a guess.
                missing.append(n)
                continue
        if not possible:
            missing.append(n)
            continue
        anchor = possible[0]
        selected[n] = anchor
        last = (anchor["page"], anchor["y"])
        if len(possible) != 1:
            ambiguous[str(n)] = possible
    return selected, ambiguous, missing, suspect


def find_source_page(year, paper, page):
    folder = ROOT / "sudu/data/original" / str(year) / paper
    candidates = list(folder.glob(f"p{page:03d}-*-v2-w1400-q66.webp"))
    return candidates[0] if len(candidates) == 1 else None


def crop_candidate(doc, anchors, number, image_path):
    a = anchors[number]
    p = doc[a["page"] - 1]
    with Image.open(image_path) as im:
        width, height = im.size
        sy = height / p.rect.height
        top = max(85, round(a["y"] * sy) - 11)
        following = sorted(
            (v for k, v in anchors.items() if k > number and
             v["page"] == a["page"] and v["y"] > a["y"]),
            key=lambda x: x["y"])
        bound = min(height - 106, round(following[0]["y"] * sy) - 11) if following else height - 105
        if bound <= top + 35:
            return None, ["CROP_TOO_SHORT"]
        import numpy as np
        area = np.asarray(im.convert("L").crop((90, top, min(1310, width), bound)))
        ink = np.flatnonzero((area < 175).sum(axis=1) >= 6)
        bottom = max(top + 55, top + int(ink[-1]) + 18) if len(ink) else top + 55
        bottom = min(bound, bottom)
        warnings = []
        if not following:
            warnings.append("LAST_ON_PAGE_REQUIRES_FOOTER_AND_CONTINUATION_QA")
        if bottom - top > height * .56:
            warnings.append("OVERLARGE_CROP_CHECK_CROSS_PAGE")
        return [90, top, min(1310, width), bottom], warnings


def save_image(src, box, dest):
    srcbytes = src.read_bytes()
    with Image.open(io.BytesIO(srcbytes)) as im:
        assert im.format == "WEBP"
        W, H = im.size
        if not (0 <= box[0] < box[2] <= W and 0 <= box[1] < box[3] <= H):
            raise ValueError("Invalid crop bounds")
        result = io.BytesIO()
        im.crop(tuple(box)).save(result, "WEBP", lossless=True, method=6)
        dimensions = [box[2] - box[0], box[3] - box[1]]
    encoded = result.getvalue()
    with Image.open(io.BytesIO(encoded)) as im:
        im.load()
        assert im.format == "WEBP" and list(im.size) == dimensions
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_bytes() != encoded:
        raise ValueError("Existing output changed. Must issue next version, not overwrite.")
    if not dest.exists():
        dest.write_bytes(encoded)
    return {
        "source": src.relative_to(ROOT).as_posix(),
        "sourcePageWebpSha256": sha(srcbytes),
        "sourceSize": [W, H],
        "cropPixels": box,
        "output": dest.relative_to(ROOT).as_posix(),
        "outputSize": dimensions,
        "outputSha256": sha(encoded)
    }


def raw_ocr(candidate):
    import pytesseract
    with Image.open(candidate) as im:
        return pytesseract.image_to_string(im, lang="chi_tra+eng", config="--psm 6")


def sqlite_roundtrip(outdir, questions, shared):
    db = outdir / "question-bank.sqlite3"
    with sqlite3.connect(db) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id TEXT PRIMARY KEY, year INTEGER NOT NULL, paper_code TEXT NOT NULL,
            original_number INTEGER NOT NULL, subject TEXT, payload TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL, UNIQUE(year,paper_code,original_number));
        CREATE TABLE IF NOT EXISTS shared_materials (
            material_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        """)
        def import_once():
            for q in questions:
                payload = json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                cx.execute("""INSERT INTO questions VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(question_id) DO UPDATE SET
                payload=excluded.payload,payload_sha256=excluded.payload_sha256""",
                (q["questionId"],q["year"],q["paperCode"],q["originalQuestionNumber"],
                 q["subject"],payload,sha(payload.encode("utf-8"))))
            for m in shared:
                cx.execute("""INSERT INTO shared_materials VALUES(?,?)
                ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload""",
                (m["sharedMaterialId"], json.dumps(m, sort_keys=True, ensure_ascii=False)))
            cx.commit()
        import_once()
        import_once()
        stored = cx.execute("SELECT question_id, payload, payload_sha256 FROM questions").fetchall()
        assert len(stored) == len(questions)
        assert cx.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        for qid, data, hashvalue in stored:
            assert sha(data.encode("utf-8")) == hashvalue and json.loads(data)["questionId"] == qid
        assert cx.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0] == len(shared)
        return {"rows": len(stored), "unique": len(set(x[0] for x in stored)),
                "integrity": "ok", "reimportCount": 2, "shaMismatches": 0}


def year_process(year, cache):
    assert 105 <= year <= 113
    now = datetime.now(timezone.utc).isoformat()
    outdir = ROOT / "sudu/data/processed" / str(year)
    outdir.mkdir(parents=True, exist_ok=True)
    source = json.loads((ROOT / "sudu/data/years" / f"{year}.json").read_text(encoding="utf-8"))
    questions, manifest, answers, ocr_entries, review = [], [], [], [], []
    paper_stats, shared = {}, []
    assert len(source["papers"]) == 5
    for paper in source["papers"]:
        code = paper["paper"]
        assert code in PAPERS
        records = sorted(paper["questions"], key=lambda x: int(x["number"]))
        original_numbers = [int(q["number"]) for q in records]
        assert len(set(original_numbers)) == len(original_numbers)
        assert all(q["id"] == f"{year}-{code}-{q['number']:02d}" for q in records)
        qsha = records[0]["sourceVersion"]["questionPdfSha256"]
        asha = records[0]["sourceVersion"]["answerPdfSha256"]
        qpdf, apdf, pdf_issues = None, None, []
        try:
            qpdf = official_pdf(paper["questionPdf"], qsha, cache)
        except Exception as e:
            pdf_issues.append("QUESTION_PDF_UNAVAILABLE_OR_HASH_MISMATCH:" + str(e)[:180])
        try:
            apdf = official_pdf(paper["answerPdf"], asha, cache)
        except Exception as e:
            pdf_issues.append("ANSWER_PDF_UNAVAILABLE_OR_HASH_MISMATCH:" + str(e)[:180])
        amap, conflicts = official_answers(apdf, max(original_numbers)) if apdf else ({}, [])
        doc = fitz.open(stream=qpdf, filetype="pdf") if qpdf else None
        selected, ambiguities, missing, suspects = (
            decide_anchors(records, pdf_number_anchors(doc, set(original_numbers)))
            if doc else ({}, {}, original_numbers, []))
        crop_count = 0
        for q in records:
            n = int(q["number"])
            qid = q["id"]
            issues = list(pdf_issues)
            crop = {}
            anchor = selected.get(n)
            if anchor:
                src = find_source_page(year, code, anchor["page"])
                if src:
                    rect, warns = crop_candidate(doc, selected, n, src)
                    issues.extend(warns)
                    if rect:
                        output = outdir / "webp-v1" / code / (qid + ".webp")
                        try:
                            crop = save_image(src, rect, output)
                            crop_count += 1
                        except Exception as e:
                            issues.append("CROP_FAILURE:" + str(e)[:120])
                    else:
                        issues.append("UNSAFE_CROP_COORDINATES")
                else:
                    issues.append("MISSING_VERSIONED_SOURCE_PAGE_WEBP")
            else:
                issues.append("UNVERIFIED_PDF_QUESTION_NUMBER_ANCHOR")
            official = amap.get(n)
            official_candidate = official["answer"] if official else None
            legacy_int = q.get("answer")
            legacy = "ABCD"[legacy_int] if type(legacy_int) is int and 0 <= legacy_int < 4 else None
            candidate = legacy or q.get("officialAnswerCandidate")
            matched = bool(official_candidate and candidate == official_candidate)
            options = q.get("options") if isinstance(q.get("options"), list) else []
            complete_text = len(options) == 4 and all(isinstance(s, str) and s.strip() for s in options)
            raw = q.get("ocrRaw") or q.get("rawOcr")
            ocr_status = "REUSED_EXISTING_RAW" if raw else "PENDING_NEEDS_OCR"
            if not raw and crop and not complete_text:
                try:
                    raw = raw_ocr(ROOT / crop["output"])
                    ocr_status = "DRAFT_UNCORRECTED_OCR"
                except Exception as e:
                    issues.append("OCR_ENGINE_ERROR:" + str(e)[:140])
            elif not raw and complete_text:
                ocr_status = "REUSED_LEGACY_PDF_TEXT_OCR_NOT_REPEATED"
            if not complete_text:
                issues.append("NEEDS_VERIFIED_FOUR_TEXT_OPTIONS_OR_IMAGE_ONLY_FALLBACK")
            if code == "110-09-1":
                pass
            image_status = "DRAFT_NEEDS_DIRECT_VISUAL_QA" if crop else "BLOCKED_NO_SINGLE_QUESTION_WEBP"
            entry = {"questionId": qid, "year": year, "paperCode": code, "subject": q.get("subject"),
                     "originalQuestionNumber": n, "officialQuestionPdfUrl": paper["questionPdf"],
                     "officialQuestionPdfSha256": qsha, "sourcePage": anchor["page"] if anchor else None,
                     "generationVersion": VERSION, "qaStatus": image_status,
                     "issues": issues, **crop}
            manifest.append(entry)
            answers.append({"questionId": qid, "officialAnswerPdfUrl": paper["answerPdf"],
                "officialAnswerPdfSha256": asha, "officialAnswerPdfPage": official["page"] if official else None,
                "pdfExtractedAnswerCandidate": official_candidate, "legacyAnswerCandidate": candidate,
                "comparison": "MATCHED_PDF_TEXT_ONLY" if matched else "MISMATCH" if official_candidate else "UNRESOLVED",
                "answerMatched": matched, "answerVerified": False, "officialCorrectionsChecked": False,
                "qaStatus": "PENDING_OFFICIAL_FINAL_ANSWER_VISUAL_AND_REVISION_REVIEW"})
            ocr_entries.append({"questionId": qid, "rawOcrText": raw, "rawOrigin": ocr_status,
                "legacyQuestion": q.get("question"), "legacyOptions": options,
                "correctedQuestion": None, "correctedOptions": None, "diff": None,
                "imageSha256": crop.get("outputSha256"), "qaStatus": "PENDING"})
            questions.append({"schemaVersion": 1, "questionId": qid, "year": year, "paperCode": code,
                "originalQuestionNumber": n, "subject": q.get("subject"),
                "question": q.get("question"), "options": options,
                "answer": official_candidate if matched else None, "answerMatched": matched,
                "answerVerified": False, "questionVerified": False, "integrationReady": False,
                "sharedMaterialIds": [], "issues": issues,
                "assets": {"singleQuestionWebp": crop.get("output"), "sourcePageWebp": crop.get("source"),
                           "sha256": crop.get("outputSha256"), "sourcePage": entry["sourcePage"]},
                "source": {"questionPdf": paper["questionPdf"], "questionPdfSha256": qsha,
                           "answerPdf": paper["answerPdf"], "answerPdfSha256": asha},
                "ocrStatus": ocr_status, "imageQaStatus": image_status,
                "officialAnswerQaStatus": "PENDING_FINAL_SOURCE_RECHECK",
                "reviewStatus": "needs_review"})
            review.append({"questionId": qid, "status": "PENDING" if crop else "BLOCKED",
                "sourcePage": entry["sourcePage"], "sourceWebp": crop.get("source"),
                "candidateWebp": crop.get("output"), "candidateSha256": crop.get("outputSha256"),
                "criteria": ["official_number", "whole_stem", "all_four_options",
                             "all_figures_formulas_units", "no_adjacent_question",
                             "no_header_footer", "sharpness", "original_and_output_sha256"],
                "reviewer": None, "visualEvidence": None})
        if doc:
            doc.close()
        paper_stats[code] = {"candidateRecords": len(records), "numberedAnchors": len(selected),
            "imageDrafts": sum(bool(m.get("output")) for m in manifest if m["paperCode"] == code),
            "unresolvedAnchorNumbers": missing, "suspectedPageConflicts": suspects,
            "ambiguousAnchorNumbers": list(ambiguities), "officialAnswerTextKeys": len(amap),
            "answerTextConflicts": conflicts, "issues": pdf_issues,
            "legacyIdNumberGap": sorted(set(range(1, max(original_numbers) + 1)) - set(original_numbers))}
        print(f"{year} {code}: DRAFT webp {paper_stats[code]['imageDrafts']}/{len(records)};"
              f" official answer text keys {len(amap)}; image PASS=0", flush=True)
    ids = [q["questionId"] for q in questions]
    if len(ids) != len(set(ids)) or len(ids) < 100:
        raise RuntimeError("Duplicated or implausible year question inventory")
    db_audit = sqlite_roundtrip(outdir, questions, shared)
    summary = {"year": year, "expectedFromLegacy": len(questions),
        "note": "Expected count from EXISTING JSON, not independently final-verified official paper counts",
        "totalCandidateQuestions": len(questions),
        "webpGeneratedDrafts": sum(bool(m.get("output")) for m in manifest),
        "visualQaPass": 0, "ocrGapCandidatesGenerated": sum(
            x["rawOrigin"] == "DRAFT_UNCORRECTED_OCR" for x in ocr_entries),
        "ocrTextIndependentlyVerified": 0, "missingFourTextOptions": [
            x["questionId"] for x in questions if len(x["options"]) != 4 or
            not all(isinstance(t, str) and t.strip() for t in x["options"])],
        "answerPdfTextMatchedOnly": sum(x["answerMatched"] for x in answers),
        "answerOfficialFinalVerified": 0, "sourcePaperStats": paper_stats,
        "sharedMaterialsVerified": 0, "sharedMaterialsReviewRequired": True,
        "sqlite": db_audit, "integrationReady": False}
    write_json(outdir / "questions.json", {"year": year, "schemaVersion": 1,
        "generatedAt": now, "warning": "UNVERIFIED DRAFT. Never publish.", "questions": questions,
        "sharedMaterials": shared})
    write_json(outdir / "webp-manifest.json", {"year": year, "schemaVersion": 1,
        "generatedAt": now, "reviewPolicy": "no automated image QA PASS",
        "expectedFromLegacy": len(questions), "items": manifest,
        "sharedMaterialCrops": shared})
    write_json(outdir / "ocr-raw-candidates.json", {"year": year, "items": ocr_entries})
    write_json(outdir / "official-answer-evidence.json", {"year": year,
        "independentOfficialFinalVerified": 0, "reviewPending": True, "items": answers})
    write_json(outdir / "VISUAL_QA.json", {"year": year, "passCount": 0,
        "items": review, "sharedMaterials": []})
    write_json(outdir / "inventory.json", summary)
    write_json(outdir / "VALIDATION.json", {"year": year, "structuralStatus":
        "PASS_DRAFT_WITH_WARNINGS" if db_audit["rows"] == len(questions) else "FAIL",
        "imageVisualQaPass": 0, "answerOfficialFinalVerified": 0, "ocrTextVerified": 0,
        "officialExpectedQuestionCountsConfirmed": False,
        "releaseAllowed": False, "integrationReady": False, "sourceGaps": paper_stats})
    write_json(outdir / "release-manifest.json", {"year": year, "releaseAllowed": False,
        "integrationReady": False, "imageQA": "PENDING", "officialFinalAnswerQA": "PENDING",
        "questionTextQA": "PENDING", "sharedMaterialQA": "PENDING", "database": db_audit})
    waiting = "\n".join(
        f"- [ ] {m['questionId']} | {m.get('output') or 'NO WEBP'} | "
        f"page {m.get('sourcePage')} | {', '.join(m.get('issues', [])) or 'needs comparison'}"
        for m in manifest)
    (outdir / "REMAINING_QA.md").write_text(
        f"# {year} 年逐題來源比對待辦（非 QA 證據）\n\n"
        "未對照官方來源頁和單題圖之前，禁止標 PASS。答案亦需核對最終版與更正公告。\n\n" +
        waiting + "\n", encoding="utf-8")
    (outdir / "DATA_HANDOFF.md").write_text(
        f"# {year} 年資料工程交接 — 僅候選，禁止平台正式接入\n\n"
        f"- 候選題號：{len(questions)}\n"
        f"- 已產生候選單題 WebP：{summary['webpGeneratedDrafts']}\n"
        "- 逐張視覺驗收通過：0\n"
        f"- PDF 自動答案候選相符：{summary['answerPdfTextMatchedOnly']}\n"
        "- 官方最終答案與疑義更正逐題完成：0\n"
        f"- SQLite 雙次匯入讀回：{db_audit['rows']}\n"
        "- integrationReady = false\n"
        "- 參閱 docs/SUDU_QUESTION_BANK_QA_GATE_105_115.md\n",
        encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "sourcePaperStats"}, ensure_ascii=False),
          flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    year_process(args.year, ROOT / ".qa-tcte-pdf-cache")


if __name__ == "__main__":
    main()
