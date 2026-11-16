#!/usr/bin/env python3
"""114-only pixel crop, OCR gap candidates and official answer comparison.

Never edits 114.json, 115 assets, student records, or deployment files.
All generated crops remain DRAFT until actual page-to-crop visual evidence exists.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlparse, urljoin

import fitz
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
YEAR = ROOT / "sudu/data/years/114.json"
OUT = ROOT / "sudu/data/processed/114"
ORIGINAL = ROOT / "sudu/data/original/114"
VERSION = "114-source-pixel-draft-v1"
EXPECTED = {"00-C": 38, "00-E": 42, "00-MB": 25, "09-1": 50, "09-2": 50}
ALLOWED = {"web1.tcte.edu.tw", "www.tcte.edu.tw", "tcte.edu.tw"}
ANCHOR = re.compile(r"^(\d{1,2})[.．、](?:\S*)$")
ANSWER = re.compile(r"(?<!\d)(\d{1,3})[ \t]+([ABCD])(?=\s|$)")


def digest(binary):
    return hashlib.sha256(binary).hexdigest()


def jsonwrite(name, obj):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def official_pdf(url, expected_sha):
    current = url
    for _ in range(5):
        p = urlparse(current)
        if p.scheme != "https" or p.hostname not in ALLOWED:
            raise ValueError("Nonofficial URL: " + current)
        r = requests.get(current, allow_redirects=False, timeout=(20, 90),
                         headers={"User-Agent": "7581707-114-official-source-validator/1.0"})
        if r.is_redirect:
            current = urljoin(current, r.headers["Location"])
            continue
        r.raise_for_status()
        payload = r.content
        if not payload.startswith(b"%PDF") or len(payload) > 40_000_000:
            raise ValueError("Bad PDF payload: " + current)
        actual_sha = digest(payload)
        if actual_sha != expected_sha:
            raise ValueError("Official PDF changed: expected " + expected_sha +
                             ", actual " + actual_sha + "; do NOT silently update source")
        return payload
    raise ValueError("Too many redirects")


def source_page(paper, page):
    files = list((ORIGINAL / paper).glob(f"p{page:03d}-*-v2-w1400-q66.webp"))
    return files[0] if len(files) == 1 else None


def anchors_for_pdf(pdf, expected, paper):
    candidates = defaultdict(list)
    words = {}
    for ix, page in enumerate(pdf):
        if ix == 0:
            continue
        number = ix + 1
        tokens = page.get_text("words", sort=True)
        words[number] = tokens
        for x0, y0, x1, y1, token, *_ in tokens:
            match = ANCHOR.match(token.strip())
            if not match:
                continue
            n = int(match.group(1))
            if not (1 <= n <= expected and 20 <= x0 <= 105 and
                    35 <= y0 <= page.rect.height - 45):
                continue
            if paper == "00-MB" and number == 2 and n in (1, 2, 3, 4) and y0 < 210:
                # The Mathematics-B instruction page contains numbered formulae.
                continue
            candidates[n].append({"page": number, "y0": round(y0, 2),
                                  "y1": round(y1, 2), "x0": round(x0, 2)})
    chosen, ambiguities, missing = {}, {}, []
    previous = (1, 0)
    for n in range(1, expected + 1):
        possibilities = sorted((x for x in candidates[n]
                               if (x["page"], x["y0"]) > previous),
                               key=lambda x: (x["page"], x["y0"]))
        if not possibilities:
            missing.append(n)
            continue
        chosen[n] = possibilities[0]
        previous = (chosen[n]["page"], chosen[n]["y0"])
        if len(possibilities) > 1:
            ambiguities[str(n)] = possibilities
    return chosen, ambiguities, missing, words


def last_ink_row(img, top, limit):
    # This is only a crop candidate heuristic, NOT visual review.
    import numpy as np
    if limit <= top:
        return top
    grayscale = np.asarray(img.convert("L").crop((90, top, min(1310, img.width), limit)))
    rows = np.where((grayscale < 170).sum(axis=1) >= 5)[0]
    return top + int(rows[-1]) if len(rows) else top


def crop_geometry(pdf, chosen, n, source):
    anchor = chosen[n]
    page = pdf[anchor["page"] - 1]
    with Image.open(source) as im:
        W, H = im.size
        sx, sy = W / page.rect.width, H / page.rect.height
        first_y = max(100, int(anchor["y0"] * sy) - 12)
        next_anchors = sorted((v for k, v in chosen.items()
                               if k > n and v["page"] == anchor["page"] and
                               v["y0"] > anchor["y0"]),
                              key=lambda t: t["y0"])
        bound = min(H - 110, int(next_anchors[0]["y0"] * sy) - 10) if next_anchors else H - 110
        if bound < first_y + 35:
            return None, ["candidate_band_too_short"]
        last = last_ink_row(im, first_y, bound)
        bottom = min(bound, max(first_y + 46, last + 16))
        box = [90, first_y, min(1310, W), bottom]
        warnings = []
        if not next_anchors:
            warnings.append("last_on_page_check_possible_continuation_or_footer")
        if bottom - first_y > H * 0.60:
            warnings.append("oversize_crop_requires_manual_review")
        return box, warnings


def save_pixel_crop(source, box, outpath):
    source_bytes = source.read_bytes()
    with Image.open(io.BytesIO(source_bytes)) as img:
        if img.format != "WEBP":
            raise AssertionError("Input page is not WebP")
        W, H = img.size
        if not (0 <= box[0] < box[2] <= W and 0 <= box[1] < box[3] <= H):
            raise ValueError("Invalid pixel crop: " + str(box))
        dst = io.BytesIO()
        img.crop(tuple(box)).save(dst, "WEBP", lossless=True, method=6)
        dims = [box[2] - box[0], box[3] - box[1]]
    payload = dst.getvalue()
    with Image.open(io.BytesIO(payload)) as img:
        img.load()
        assert img.format == "WEBP"
    outpath.parent.mkdir(parents=True, exist_ok=True)
    if outpath.exists() and outpath.read_bytes() != payload:
        raise ValueError("Existing version differs: " + str(outpath) +
                         "; create v2 instead of overwriting reviewed bytes")
    outpath.write_bytes(payload)
    return {"source": source.relative_to(ROOT).as_posix(),
            "sourceSize": [W, H], "sourceSha256": digest(source_bytes),
            "crop": box, "output": outpath.relative_to(ROOT).as_posix(),
            "outputSize": dims, "sha256": digest(payload)}


def official_answers(pdfbytes, max_number):
    found, conflicts = {}, set()
    with fitz.open(stream=pdfbytes, filetype="pdf") as doc:
        for page_no, page in enumerate(doc, 1):
            for match in ANSWER.finditer(page.get_text(sort=True)):
                n = int(match.group(1))
                if not 1 <= n <= max_number:
                    continue
                value = match.group(2)
                if n in found and found[n]["letter"] != value:
                    conflicts.add(n)
                else:
                    found[n] = {"letter": value, "page": page_no}
    for n in conflicts:
        found.pop(n, None)
    return found, sorted(conflicts)


def legacy_letter(q):
    ans = q.get("answer")
    return "ABCD"[ans] if type(ans) is int and 0 <= ans <= 3 else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    data = json.loads(YEAR.read_text(encoding="utf-8"))
    priorpath = OUT / "webp-manifest.json"
    prior = {}
    if priorpath.exists():
        previous = json.loads(priorpath.read_text(encoding="utf-8"))
        prior = {x["questionId"]: x for x in previous["items"]}
    bank, image_items, answer_items, ocr_items, shared = [], [], [], [], []
    anchor_report, paper_counts = {}, {}
    for paper in data["papers"]:
        code = paper["paper"]
        count = EXPECTED[code]
        questions = paper["questions"]
        if len(questions) != count:
            raise AssertionError(f"{code}: expected {count}, found {len(questions)}")
        qpdfsha = questions[0]["sourceVersion"]["questionPdfSha256"]
        apdfsha = questions[0]["sourceVersion"]["answerPdfSha256"]
        qbinary = official_pdf(paper["questionPdf"], qpdfsha)
        abinary = official_pdf(paper["answerPdf"], apdfsha)
        answer_map, answer_conflicts = official_answers(abinary, count)
        with fitz.open(stream=qbinary, filetype="pdf") as pdf:
            anchor_map, ambiguity, missing, words = anchors_for_pdf(pdf, count, code)
            anchor_report[code] = {"source": paper["questionPdf"],
                "sourcePdfSha256": qpdfsha, "selected": anchor_map,
                "ambiguous": ambiguity, "missing": missing,
                "selectionMethod": "monotonic PDF-text question-number geometry; candidate only"}
            success = 0
            ocr_count = 0
            for q in questions:
                n, qid = q["number"], q["id"]
                if qid != f"114-{code}-{n:02d}":
                    raise AssertionError("Wrong canonical question ID: " + qid)
                issues, asset = [], {}
                anchor = anchor_map.get(n)
                if anchor is None:
                    issues.append("NO_RELIABLE_PDF_QUESTION_NUMBER_ANCHOR")
                else:
                    src = source_page(code, anchor["page"])
                    if src is None:
                        issues.append("NO_UNIQUE_VERSIONED_OFFICIAL_SOURCE_PAGE")
                    else:
                        rect, warnings = crop_geometry(pdf, anchor_map, n, src)
                        issues.extend(warnings)
                        if rect:
                            dest = OUT / "webp-v1" / code / (qid + ".webp")
                            asset = save_pixel_crop(src, rect, dest)
                            success += 1
                        else:
                            issues.append("INVALID_CROP_BOUND")
                old = prior.get(qid, {})
                pass_evidence = old.get("visualReviewEvidence") or {}
                reused_pass = (bool(asset) and old.get("qaStatus") == "PASS" and
                    old.get("sha256") == asset["sha256"] and
                    old.get("sourceSha256") == asset["sourceSha256"] and
                    pass_evidence.get("reviewedSha256") == asset["sha256"])
                qa_status = "PASS" if reused_pass else (
                    "DRAFT_NEEDS_DIRECT_VISUAL_QA" if asset else "BLOCKED_NO_WEBP")
                image = {"questionId": qid, "paperCode": code, "subject": q["subject"],
                    "originalQuestionNumber": n, "officialPdf": paper["questionPdf"],
                    "sourcePdfSha256": qpdfsha, "sourcePage": anchor["page"] if anchor else None,
                    "processingVersion": VERSION, "qaStatus": qa_status,
                    "issues": issues, **asset}
                if reused_pass:
                    image["visualReviewEvidence"] = pass_evidence
                image_items.append(image)

                prior_answer = legacy_letter(q)
                official = answer_map.get(n)
                extracted = official["letter"] if official else None
                old_candidate = q.get("officialAnswerCandidate")
                matched = bool(extracted and (prior_answer == extracted or
                               prior_answer is None and old_candidate == extracted))
                answer_items.append({"questionId": qid, "officialPdf": paper["answerPdf"],
                    "officialPdfSha256": apdfsha, "officialAnswerPdfPage": official["page"] if official else None,
                    "officialPdfExtractedCandidate": extracted,
                    "legacyAnswer": prior_answer, "legacyOfficialAnswerCandidate": old_candidate,
                    "comparison": "MATCHED" if matched else "MISMATCH" if extracted else "UNRESOLVED",
                    "answerMatched": matched, "answerVerified": False,
                    "independentVisualAnswerReview": "PENDING",
                    "officialFinalizationAnnouncement": "https://web1.tcte.edu.tw/EXAM/114_4y/"})
                legacy_options = q.get("options") or []
                incomplete = len(legacy_options) != 4 or q.get("page") is None
                # Reuse existing extracted text; run optical OCR only for gaps.
                if incomplete and asset:
                    import pytesseract
                    with Image.open(ROOT / asset["output"]) as im:
                        raw = pytesseract.image_to_string(im, lang="chi_tra+eng",
                                 config="--psm 6")
                    ocr_count += 1
                    ocr_items.append({"questionId": qid, "engine": "Tesseract chi_tra+eng PSM6",
                        "rawText": raw, "legacyQuestion": q.get("question"),
                        "legacyOptions": legacy_options, "correctedText": None,
                        "correctedOptions": None, "difference": None,
                        "imageSha256": asset["sha256"], "reviewStatus": "PENDING_MANUAL_CORRECTION"})
                if len(legacy_options) != 4:
                    issues.append("MISSING_FOUR_VERIFIED_TEXT_OPTIONS")
                question = {"schemaVersion": 1, "questionId": qid, "year": 114,
                    "paperCode": code, "originalQuestionNumber": n, "subject": q["subject"],
                    "question": q.get("question") or "", "options": legacy_options,
                    "answer": extracted if matched else None,
                    "answerMatched": matched, "answerVerified": False, "questionVerified": False,
                    "reviewStatus": "needs_review", "sharedMaterialIds": [],
                    "assets": {"singleQuestionWebp": asset.get("output"), "sharedMaterialIds": []},
                    "issues": issues, "sourcePage": asset.get("sourcePage", q.get("page")),
                    "questionProvenance": {"officialPdf": paper["questionPdf"],
                        "officialPdfSha256": qpdfsha, "pixelSourceSha256": asset.get("sourceSha256"),
                        "webpSha256": asset.get("sha256"), "legacyYearJsonId": qid},
                    "answerProvenance": {"officialPdf": paper["answerPdf"],
                        "officialPdfSha256": apdfsha, "extractMethod": "pymupdf_official_pdf_text",
                        "independentVisualVerification": False}}
                bank.append(question)
            paper_counts[code] = {"expected": count, "candidateWebp": success,
                "anchorMissing": missing, "answerPdfKeys": len(answer_map),
                "answerPdfConflicts": answer_conflicts, "ocrGapCandidates": ocr_count}
            print(f"114 {code}: candidate WebP {success}/{count}, OCR-gap {ocr_count}, "
                  f"official text answer keys {len(answer_map)}/{count}", flush=True)

            # Shared reading instructions are separate SOURCE-PIXEL draft candidates.
            # If a prior question appears on the same page, do not include its pixels.
            for first, last in ((21, 24), (25, 28)) if code == "00-E" else ():
                a = anchor_map.get(first)
                if not a:
                    continue
                preceding = [k for k, x in anchor_map.items()
                             if k < first and x["page"] == a["page"] and x["y0"] < a["y0"]]
                if preceding:
                    continue
                src = source_page(code, a["page"])
                if not src:
                    continue
                with Image.open(src) as im:
                    scale = im.height / pdf[a["page"] - 1].rect.height
                    top, bottom = 143, int(a["y0"] * scale) - 14
                    if bottom <= top + 60 or bottom - top > im.height * 0.65:
                        continue
                group_id = f"114-{code}-SHARED-{first}-{last}"
                dest = OUT / "webp-v1/shared" / (group_id + ".webp")
                asset = save_pixel_crop(src, [90, top, 1310, bottom], dest)
                shared.append({"sharedMaterialId": group_id, "paperCode": code,
                    "originalQuestionNumbers": list(range(first, last + 1)),
                    "qaStatus": "DRAFT_NEEDS_DIRECT_VISUAL_QA",
                    "issues": ["shared_crop_geometry_candidate_not_visually_verified"], **asset})
                for qb in bank:
                    if qb["paperCode"] == code and first <= qb["originalQuestionNumber"] <= last:
                        qb["sharedMaterialIds"].append(group_id)
                        qb["assets"]["sharedMaterialIds"].append(group_id)

    ids = [x["questionId"] for x in bank]
    if len(ids) != 205 or len(set(ids)) != 205:
        raise AssertionError("205 unique official number inventory required")
    review_records = [{"questionId": x["questionId"], "result":
            "PASS" if x["qaStatus"] == "PASS" else "PENDING",
            "asset": x.get("output"), "assetSha256": x.get("sha256"),
            "source": x.get("source"), "sourceSha256": x.get("sourceSha256"),
            "sourcePage": x.get("sourcePage"),
            "criteria": ["number", "complete_stem", "four_options_or_original_visual_choices",
                         "formula_tables_units", "no_other_question", "no_header_footer", "clarity",
                         "input_output_sha256"],
            "evidenceReference": x.get("visualReviewEvidence", {}).get("reference")}
            for x in image_items]
    qa_pass = sum(x["qaStatus"] == "PASS" for x in image_items)
    manifest = {"schemaVersion": 1, "year": 114, "processingVersion": VERSION,
        "generatedAt": timestamp, "expected": 205,
        "generated": sum(bool(x.get("output")) for x in image_items),
        "visualQaPass": qa_pass,
        "reviewPolicy": "Automated source pixels/decoding are DRAFT, not visual QA.",
        "sharedMaterialCrops": shared, "paperStats": paper_counts, "items": image_items}
    jsonwrite("webp-manifest.json", manifest)
    jsonwrite("questions.json", {"schemaVersion": 1, "year": 114, "generatedAt": timestamp,
        "notice": "Unverified source-only 114 draft; NEVER use answerVerified/questionVerified from legacy.",
        "questions": bank, "sharedMaterials": shared})
    jsonwrite("ocr-raw-candidates.json", {"year": 114, "status": "uncorrected_gap_candidates",
        "legacyTextCandidatesRetained": 205 - len(ocr_items),
        "ocrTriggered": len(ocr_items), "items": ocr_items})
    jsonwrite("official-answer-evidence.json", {"year": 114, "reviewStatus":
        "PDF_TEXT_ONLY_NOT_INDEPENDENT_VISUAL_VERIFICATION",
        "answerVerifiedCount": 0, "items": answer_items})
    jsonwrite("anchor-report.json", anchor_report)
    jsonwrite("VISUAL_QA.json", {"year": 114, "definition":
        "A PASS requires genuine official-source-page versus exact crop comparison.",
        "passCount": qa_pass, "questions": review_records,
        "sharedMaterials": [{"sharedMaterialId": x["sharedMaterialId"], "result": "PENDING",
            "asset": x["output"], "sha256": x["sha256"]} for x in shared]})
    inventory = {"year": 114, "expected": 205, "canonicalUnique": len(set(ids)),
        "webpDrafts": manifest["generated"], "webpVisualQaPassed": qa_pass,
        "missingImageIds": [x["questionId"] for x in image_items if not x.get("output")],
        "missingFourTextOptionIds": [x["questionId"] for x in bank if len(x["options"]) != 4],
        "answerTextMatched": sum(x["answerMatched"] for x in answer_items),
        "answerUnmatchedIds": [x["questionId"] for x in answer_items if not x["answerMatched"]],
        "answerIndependentlyVerified": 0, "questionIndependentlyVerified": 0,
        "perPaper": paper_counts}
    jsonwrite("inventory.json", inventory)
    print(json.dumps(inventory, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
