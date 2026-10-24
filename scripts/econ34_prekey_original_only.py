#!/usr/bin/env python3
"""Read original question WebP ONLY for a genuine first-look economics solution.

Strictly forbidden to load answer-containing questions.json or official PDFs
during this stage. Do not produce answer flags or certification.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"sudu/data/processed/115/webp-manifest.json"
QID="115-09-2-34"
PIN="5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02"
m=json.loads(MANIFEST.read_text(encoding="utf-8"))
item=next(row for row in m["items"] if row["questionId"]==QID)
assert item["sha256"]==PIN and item["qaStatus"]=="PASS"
assert item["subject"]=="經濟學" and item["paperCode"]=="09-2"
assert (item["visualReviewEvidence"] or {}).get("reviewedSha256")==PIN
raw=(ROOT/item["output"]).read_bytes()
assert hashlib.sha256(raw).hexdigest()==PIN
assert raw.startswith(b"RIFF") and raw[8:12]==b"WEBP"
s=base64.b64encode(raw).decode("ascii")
print(f"ECON34_PREKEY_ORIGINAL_START|{QID}|{PIN}|{len(raw)}",flush=True)
for i,p in enumerate(range(0,len(s),1600)):
 print(f"ECON34_PREKEY_ORIGINAL_PART|{i:04d}|{s[p:p+1600]}",flush=True)
print(f"ECON34_PREKEY_ORIGINAL_END|{len(s)}",flush=True)
print("NO official key/question JSON/solution docs loaded by this script.",flush=True)
