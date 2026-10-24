#!/usr/bin/env python3
"""Read-only byte-for-byte original WebP inspection transport for MB20..MB25.

Chunked base64 is printed ONLY in the no-deploy GitHub Actions job logs so that
the existing original bytes (not a redrawn/cropped/OCR image) can be inspected.
No QA approval or source edits are made by this script.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-drafts/preview-128-20261023"

def run(n: int):
    if n not in range(20, 26):
        raise ValueError("Frozen visual-review transport accepts MB20..25 only")
    qid = f"115-00-MB-{n:02d}"
    progress = json.loads((BASE / "progress.json").read_text(encoding="utf-8"))
    item = next(x for x in progress["items"] if x["questionId"] == qid)
    path = ROOT / "sudu" / item["image"]
    content = path.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    if actual != item["imageSha256"]:
        raise ValueError(f"{qid}: original image SHA mismatch, fail closed")
    if content[:4] != b"RIFF" or content[8:12] != b"WEBP":
        raise ValueError(f"{qid}: invalid WEBP file")
    encoded = base64.b64encode(content).decode("ascii")
    print(f"MB_VISUAL_BEGIN|{qid}|{actual}|{len(content)}", flush=True)
    for part, offset in enumerate(range(0, len(encoded), 1600)):
        print(f"MB_VISUAL_PART|{qid}|{part:04d}|{encoded[offset:offset + 1600]}", flush=True)
    print(f"MB_VISUAL_END|{qid}|{len(encoded)}", flush=True)

if __name__ == "__main__":
    run(int(sys.argv[1]))
