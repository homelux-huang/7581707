#!/usr/bin/env python3
"""After committed pre-key Econ34 answer, visually retrieve SHA-pinned published official answer page."""
import base64
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"sudu/data/original/115/09-2-answers/p001-6a2aacc705-v2-w1400-q66.webp"
CORRECTIONS=ROOT/"sudu/data/processed/115/official-confirmation-status.json"
assert DOC.is_file()
status=json.loads(CORRECTIONS.read_text(encoding="utf-8"))
assert status["confirmations"]["09-2"]["revisionDocumentContent"]=="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED"
raw=DOC.read_bytes()
assert raw.startswith(b"RIFF") and raw[8:12]==b"WEBP"
h=hashlib.sha256(raw).hexdigest()
s=base64.b64encode(raw).decode("ascii")
print(f"ECON34_OFFICIAL_ANSWER_IMAGE_START|{h}|{len(raw)}|TCTE_115_09-2_P1",flush=True)
for i,p in enumerate(range(0,len(s),1600)):
 print(f"ECON34_OFFICIAL_ANSWER_PART|{i:04d}|{s[p:p+1600]}",flush=True)
print(f"ECON34_OFFICIAL_ANSWER_IMAGE_END|{len(s)}",flush=True)
