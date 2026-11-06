#!/usr/bin/env python3
"""Stage 105 seven missing questions + two shared passages; DRAFT ONLY.

Uses existing SHA-pinned page WebPs; does not modify official manifests,
QA PASS, answers, OCR, SQLite, student data, UI, or release status.
Run on QA branch checkout only; no force and never overwrite different bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "qa/114-115-official-visual-review"
FOLDER = "sudu/data/processed/105"
SOURCES = {
    "00-C": (
        "sudu/data/original/105/00-C/p006-0a170905cb-v2-w1400-q66.webp",
        "1f2ee292527089d4feeba24db0ce69996569d7df0db1f02078ac5771021a8694",
        6,
    ),
    "09-2": (
        "sudu/data/original/105/09-2/p008-e420528ee7-v2-w1400-q66.webp",
        "9af1d1daa25694f1605b9b828b72b3e8cab1bdd713fd0c79e55a684987135410",
        8,
    ),
}
SINGLE = {
    ("00-C", 24): (90, 692, 1310, 783),
    ("00-C", 25): (90, 783, 1310, 861),
    ("00-C", 26): (90, 861, 1310, 1043),
    ("00-C", 27): (90, 1601, 1310, 1840),
    ("09-2", 48): (90, 168, 1310, 372),
    ("09-2", 49): (90, 372, 1310, 550),
    ("09-2", 50): (90, 550, 1310, 1128),
}
SHARED = {
    "105-00-C-SHARED-24-26": ("00-C", (90, 167, 1310, 690), [24, 25, 26]),
    "105-00-C-SHARED-27-29": ("00-C", (90, 1050, 1310, 1595), [27, 28, 29]),
}

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def safe_path(relative: str) -> Path:
    path = ROOT / relative
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Path escapes QA working tree")
    return path

def run(write: bool) -> dict:
    head = ROOT / ".git/HEAD"
    if not head.is_file() or head.read_text().strip() != "ref: refs/heads/" + BRANCH:
        raise RuntimeError("QA branch checkout required; never main or detached HEAD")
    manifest = json.loads(safe_path(FOLDER + "/webp-manifest.json").read_text())
    entries = {i["questionId"]: i for i in manifest["items"]}
    if len(entries) != 204:
        raise RuntimeError("105 inventory changed; manual re-review required")
    sources = {}
    for paper, (path, digest, page) in SOURCES.items():
        raw = safe_path(path).read_bytes()
        if sha(raw) != digest:
            raise RuntimeError("Source page SHA256 mismatch: " + path)
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            if im.format != "WEBP" or im.size != (1400, 1980):
                raise RuntimeError("Unexpected official page size: " + path)
        sources[paper] = raw
    rows, pending_files = [], []
    def append(paper: str, box: tuple, qid: str, refs: list[str]) -> None:
        src, source_digest, page = SOURCES[paper]
        raw = sources[paper]
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= 1400 and 0 <= y0 < y1 <= 1980):
            raise ValueError("Invalid crop: " + qid)
        with Image.open(io.BytesIO(raw)) as source_im:
            output = io.BytesIO()
            source_im.crop(box).save(output, "WEBP", lossless=True, method=6)
        data = output.getvalue()
        with Image.open(io.BytesIO(data)) as check_im:
            check_im.load()
            assert check_im.format == "WEBP" and check_im.size == (x1-x0, y1-y0)
        kind = "shared" if refs else paper
        dest = FOLDER + "/qa-drafts/webp-v2/" + kind + "/" + qid + ".webp"
        existing = safe_path(dest)
        if existing.exists() and existing.read_bytes() != data:
            raise RuntimeError("Immutable draft output differs: " + dest)
        pending_files.append((existing, data))
        rows.append({
            "assetId": qid, "questionIds": refs or [qid],
            "sourcePage": page, "source": src, "sourcePageWebpSha256": source_digest,
            "cropPixels": list(box), "output": dest, "outputSha256": sha(data),
            "imageQaStatus": "DRAFT_NEEDS_ORIGINAL_TO_CROP_DIRECT_VISUAL_QA",
            "questionVerified": False, "answerVerified": False,
            "integrationReady": False,
        })
    for (paper, number), box in SINGLE.items():
        qid = f"105-{paper}-{number:02d}"
        entry = entries.get(qid)
        if entry is None or entry.get("output") or entry.get("qaStatus") == "PASS":
            raise RuntimeError("Original target is no longer a missing draft: " + qid)
        append(paper, box, qid, [])
    for mid, (paper, box, nums) in SHARED.items():
        append(paper, box, mid, [f"105-{paper}-{n:02d}" for n in nums])
    index = safe_path(FOLDER + "/qa-drafts/UNVERIFIED_105_GAPS_20261023.json")
    body = (json.dumps({
        "year": 105, "source": "existing SHA-pinned TCTE official page WebP",
        "draftSingleQuestionCount": 7, "draftSharedMaterialCount": 2,
        "visualQaPassAdded": 0, "answerVerifiedAdded": 0,
        "releaseAllowed": False, "integrationReady": False,
        "warning": "All coordinates are candidate estimates; visual QA and final-answer corrections remain pending.",
        "items": rows,
    }, ensure_ascii=False, indent=2) + "\n").encode()
    if index.exists() and index.read_bytes() != body:
        raise RuntimeError("Existing index changed; refuse overwrite")
    if write:
        for path, data in pending_files:
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if not index.exists():
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_bytes(body)
    return {
        "result": "STAGED_DRAFTS_ONLY" if write else "SOURCE_CHECK_PASS",
        "singleQuestionDrafts": 7, "sharedMaterialDrafts": 2,
        "visualQaPassAdded": 0, "answerVerifiedAdded": 0,
        "officialManifestsModified": 0, "releaseAllowed": False,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(write=args.stage), ensure_ascii=False, sort_keys=True))
