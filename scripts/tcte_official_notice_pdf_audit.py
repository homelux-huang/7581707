"""Read-only official 114 TCTE correction-document PDF evidence collector.

This script NEVER approves a question and NEVER writes to the repository.
Downloader filenames are hypotheses until actual official PDF bytes are checked.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import fitz
import requests

INDEX = "https://web1.tcte.edu.tw/EXAM/114_4y/"
CODES = ("00-C", "00-E", "09-1", "09-2")
CONTROL_115 = {
    "url": "https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=MTE1LTR5LTA5LTItY29uZmlybS5wZGY=",
    "sha256": "b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def official_get(session: requests.Session, url: str, limit: int = 15000000) -> bytes:
    hostname = (urlsplit(url).hostname or "").lower()
    if hostname != "web1.tcte.edu.tw":
        raise ValueError(f"non-TCTE URL rejected: {url}")
    with session.get(url, timeout=(15, 55), stream=True) as resp:
        resp.raise_for_status()
        final = (urlsplit(resp.url).hostname or "").lower()
        if final != "web1.tcte.edu.tw":
            raise ValueError(f"non-TCTE redirect rejected: {resp.url}")
        result = bytearray()
        for chunk in resp.iter_content(chunk_size=131072):
            result.extend(chunk)
            if len(result) > limit:
                raise ValueError("official response exceeds size limit")
        return bytes(result)


def downloader_url(year: int, code: str) -> tuple[str, str]:
    # A filename derived from the known TCTE naming pattern is not evidence.
    # Only an actual official PDF response can pass the automated fetch step.
    name = f"{year}-4y-{code}-confirm.pdf"
    obj = base64.b64encode(name.encode("ascii")).decode("ascii")
    return name, f"https://web1.tcte.edu.tw/EXAM/{year}_4y/downloader.php?obj={obj}"


def open_pdf(data: bytes):
    if not data.startswith(b"%PDF-"):
        raise ValueError("non-PDF official response")
    return fitz.open(stream=data, filetype="pdf")


def collect(session: requests.Session, outdir: Path, year: int, code: str) -> dict:
    name, url = downloader_url(year, code)
    row = {"year": year, "paperCode": code, "filenameHypothesis": name, "source": url,
           "studentQaApproved": False, "manualFullPageReview": False}
    try:
        data = official_get(session, url)
        with open_pdf(data) as pdf:
            if not len(pdf):
                raise ValueError("zero PDF pages")
            text_pages = []
            for page_num, page in enumerate(pdf, start=1):
                text_pages.append(f"\n\n===== PDF PAGE {page_num} =====\n" + page.get_text("text"))
                pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False)
                pix.save(str(outdir / f"{year}-{code}-page-{page_num:02}.png"))
            (outdir / name).write_bytes(data)
            (outdir / f"{year}-{code}-extracted.txt").write_text(
                "".join(text_pages), encoding="utf-8")
            row.update({"fetchedPdf": True, "pdfSha256": digest(data),
                        "pageCount": len(pdf), "byteCount": len(data),
                        "pageTextMustBeVisuallyChecked": True})
    except Exception as error:
        row.update({"fetchedPdf": False, "error": str(error),
                    "pdfSha256": None, "pageCount": None})
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="/tmp/tcte-114-notice-audit")
    args = p.parse_args()
    outdir = Path(args.output).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "7581707-QA-official-check/1.0", "Accept": "*/*"})
    audit = {
        "schemaVersion": 1, "year": 114,
        "recordedAtUTC": datetime.now(timezone.utc).isoformat(),
        "sourceIndex": INDEX, "readOnly": True, "requests": [],
        "claimLevel": "AUTOMATED_PDF_BYTES_ONLY_NOT_STUDENT_QA",
        "studentQaApprovedNewQuestions": 0, "approvalFlagsChanged": False,
    }
    try:
        raw_index = official_get(session, INDEX, limit=3000000)
        html = raw_index.decode("utf-8", "replace")
        audit["indexRead"] = ("114學年度" in html and all(
            f"4-{code}" in html for code in CODES))
        audit["indexSha256"] = digest(raw_index)
        (outdir / "114-official-index-received.html").write_bytes(raw_index)
        if not audit["indexRead"]:
            raise ValueError("official 114 index does not include all four paper codes")
    except Exception as error:
        audit["indexRead"] = False
        audit["indexError"] = str(error)
    try:
        data = official_get(session, CONTROL_115["url"])
        with open_pdf(data) as pdf:
            audit["control115"] = {
                "pdfSha256": digest(data), "pageCount": len(pdf),
                "expectedPdfSha256": CONTROL_115["sha256"],
                "matchesExistingVerifiedSha": digest(data) == CONTROL_115["sha256"],
            }
    except Exception as error:
        audit["control115"] = {"matchesExistingVerifiedSha": False, "error": str(error)}
    if audit["indexRead"] and audit["control115"]["matchesExistingVerifiedSha"]:
        for code in CODES:
            audit["requests"].append(collect(session, outdir, 114, code))
    audit["allFourPdfBytesFetched"] = len(audit["requests"]) == 4 and all(
        r["fetchedPdf"] for r in audit["requests"])
    audit["perQuestionReleaseCertified"] = False
    (outdir / "evidence-automated-only.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    if not audit["allFourPdfBytesFetched"]:
        raise SystemExit("Official PDF fetch incomplete; do NOT approve any question")


if __name__ == "__main__":
    main()
