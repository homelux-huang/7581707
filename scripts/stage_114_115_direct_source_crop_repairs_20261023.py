#!/usr/bin/env python3
"""Stage immutable WebP repair candidates for three visually identified crop defects.

Never promotes QA PASS, never replaces v1/v2 assets, never touches release flags.
The source page images are archived in sudu/data/original with official PDF SHA
provenance. Candidates require a *second direct visual source/crop comparison*.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "qa/114-115-official-visual-review"
STAMP = "2026-10-23"
RECORD_PATH = "sudu/data/processed/114/qa-drafts/CROP_REPAIRS_114C01_115C16_17_V20261023.json"
SPECS = {
    "114-00-C-01": {
        "year": 114, "page": 2,
        "sourceSha": "a025b08d693c5ddcf71e53007da12008c31f15fe295ff65b16165de384a01f35",
        "oldSha": "60653e0190fa55af6d1fdb3f2a942ee128e673744b711c0b70b58f2c92651c6e",
        "sourcePdfSha": "f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74",
        "candidate": "sudu/data/processed/114/qa-drafts/webp-v2/00-C/114-00-C-01.webp",
        "method": "crop", "cropPixels": [90, 210, 1310, 329],
        "problem": "Old crop contains preceding question-section text fragment."
    },
    "115-00-C-16": {
        "year": 115, "page": 6,
        "sourceSha": "8b6c781a75a864b7220f686532225171b2f53346c68f5131470371f82731e6c6",
        "oldSha": "a09e042e11b0c1927bf8d0ff63ccc617230c0bf9d3011407c31fa0940f033400",
        "sourcePdfSha": "6b454d65902f2fb326b1ac1ae28aa44749532e30369ba2c599db97d20a542135",
        "candidate": "sudu/data/processed/115/qa-drafts/webp-v3/00-C/115-00-C-16.webp",
        "method": "composite_wheel_only_extension",
        "cropPixels": [90, 1060, 1310, 1330],
        "problem": "Bottom of Q16 social-emotional wheel clipped in v2; neighbor Q17 starts before wheel ends."
    },
    "115-00-C-17": {
        "year": 115, "page": 6,
        "sourceSha": "8b6c781a75a864b7220f686532225171b2f53346c68f5131470371f82731e6c6",
        "oldSha": "c195e20b574658c0e9ee0c4e10622c15f04f16f3376d8df09146b363eaef8350",
        "sourcePdfSha": "6b454d65902f2fb326b1ac1ae28aa44749532e30369ba2c599db97d20a542135",
        "candidate": "sudu/data/processed/115/qa-drafts/webp-v3/00-C/115-00-C-17.webp",
        "method": "crop_and_mask_previous_wheel_only",
        "cropPixels": [90, 1302, 1310, 1432],
        "problem": "Previous Q16 wheel arc contaminates top-right of Q17 image."
    },
}

def abs_path(p):
    out = (ROOT / p).resolve()
    if not out.is_relative_to(ROOT):
        raise RuntimeError("Repository path traversal blocked")
    return out

def sha_file(p):
    return hashlib.sha256(abs_path(p).read_bytes()).hexdigest()

def assert_branch():
    actual = subprocess.check_output(["git", "branch", "--show-current"],
                                     cwd=ROOT, text=True).strip()
    assert actual == BRANCH, f"Refusing branch {actual}"

def load_manifest(year):
    return json.loads(abs_path(f"sudu/data/processed/{year}/webp-manifest.json").read_text("utf8"))

def make(source, qid):
    img = Image.open(abs_path(source)).convert("RGB")
    assert img.size == (1400, 1981)
    if qid == "114-00-C-01":
        out = img.crop((90, 210, 1310, 329))
    elif qid == "115-00-C-16":
        out = Image.new("RGB", (1220, 270), "white")
        # Preserve original Q16 pixels and append only the final wheel strip.
        # Left side beyond Q16 is white rather than copying neighboring Q17.
        out.paste(img.crop((90, 1060, 1310, 1302)), (0, 0))
        out.paste(img.crop((975, 1302, 1310, 1330)), (885, 242))
    elif qid == "115-00-C-17":
        out = img.crop((90, 1302, 1310, 1432))
        # Remove the preceding Q16 wheel arc only, above Q17's own choices.
        out.paste(Image.new("RGB", (320, 24), "white"), (900, 0))
    else:
        raise ValueError(qid)
    buf = io.BytesIO()
    out.save(buf, format="WEBP", lossless=True, method=6, exact=True)
    return buf.getvalue(), out.size

def main(stage):
    assert_branch()
    manifests = {y: load_manifest(y) for y in (114, 115)}
    rows = []
    for qid, spec in SPECS.items():
        m = next(x for x in manifests[spec["year"]]["items"] if x["questionId"] == qid)
        source = m["source"]
        assert m["sourcePage"] == spec["page"]
        assert m["sourceSha256"] == spec["sourceSha"]
        assert m["sourcePdfSha256"] == spec["sourcePdfSha"]
        assert m["sha256"] == spec["oldSha"]
        assert sha_file(source) == spec["sourceSha"]
        assert sha_file(m["output"]) == spec["oldSha"]
        assert not m.get("qaStatus", "").startswith("PASS")
        payload, size = make(source, qid)
        digest = hashlib.sha256(payload).hexdigest()
        target = abs_path(spec["candidate"])
        if target.exists():
            assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, (
                "Immutable candidate SHA changed: " + qid)
        elif stage:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        rows.append({
            "questionId": qid, "year": spec["year"], "source": source,
            "sourcePage": spec["page"], "sourcePageSha256": spec["sourceSha"],
            "officialPdfSha256Recorded": spec["sourcePdfSha"],
            "oldCrop": m["crop"], "oldWebp": m["output"],
            "oldWebpSha256": spec["oldSha"], "candidatePath": spec["candidate"],
            "candidateSha256": digest, "candidateSizePixels": list(size),
            "cropBoundsSourcePixels": spec["cropPixels"],
            "cropMethod": spec["method"], "reason": spec["problem"],
            "imageQaStatus": "PENDING_DIRECT_VISUAL_REVIEW",
            "answerVerified": False, "integrationReady": False
        })
    record = {
        "schemaVersion": 1,
        "createdAtDate": STAMP,
        "source": "archived original official PDF page render with recorded PDF and page SHA",
        "method": "lossless deterministic pixel-only crop/composite; non-question fragments removed",
        "directVisualReviewStatus": "PENDING",
        "newImageQaPass": 0, "releaseAllowed": False, "integrationReady": False,
        "items": rows,
        "note": "Only immutable draft candidates. Verify each candidate against official original page; do not auto-promote."
    }
    encoded = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    target = abs_path(RECORD_PATH)
    if target.exists():
        assert target.read_bytes() == encoded, "Refusing to rewrite existing evidence"
    elif stage:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print(json.dumps({
        "mode": "stage" if stage else "check", "candidates": len(rows),
        "newImageQaPass": 0, "records": [{"id": r["questionId"], "sha": r["candidateSha256"]} for r in rows],
        "releaseAllowed": False
    }, ensure_ascii=False))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--stage", action="store_true")
    args = p.parse_args()
    main(stage=args.stage)
