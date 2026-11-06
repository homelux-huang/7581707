#!/usr/bin/env python3
"""Immutable, source-SHA-pinned repairs of five 105 image DRAFTS.

Only creates new 105/qa-drafts/webp-v3 images and an UNVERIFIED ledger.
No official QA flags, manifests, answers, student data, UI or release are changed.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "qa/114-115-official-visual-review"
BASE = "sudu/data/processed/105/qa-drafts"
OLD = BASE + "/UNVERIFIED_105_GAPS_20261023.json"
FAIL = BASE + "/VISUAL_INSPECTION_105_GAPS_2026-10-23.json"
REPORT = BASE + "/UNVERIFIED_105_GAPS_V3_20261023.json"
SOURCES = {
    "00-C": ("sudu/data/original/105/00-C/p006-0a170905cb-v2-w1400-q66.webp",
             "1f2ee292527089d4feeba24db0ce69996569d7df0db1f02078ac5771021a8694", 6),
    "09-2": ("sudu/data/original/105/09-2/p008-e420528ee7-v2-w1400-q66.webp",
             "9af1d1daa25694f1605b9b828b72b3e8cab1bdd713fd0c79e55a684987135410", 8),
}
# Candidate coordinates, NOT visually verified output.
FIX = {
    "105-00-C-24": ("00-C", (90, 692, 1310, 774), "FAIL_ADJACENT_Q25_FRAGMENT"),
    "105-00-C-27": ("00-C", (90, 1618, 1310, 1860), "FAIL_PREVIOUS_FRAGMENT"),
    "105-09-2-49": ("09-2", (90, 372, 1310, 572), "FAIL_BOTTOM_CUT"),
    "105-09-2-50": ("09-2", (90, 586, 1310, 1128), "FAIL_PREVIOUS_FRAGMENT"),
    "105-00-C-SHARED-27-29": ("00-C", (90, 1050, 1310, 1614), "FAIL_BOTTOM_CUT"),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def p(relative):
    result = (ROOT / relative).resolve()
    if not result.is_relative_to(ROOT):
        raise RuntimeError("Refusing path outside repository")
    return result

def run(stage=False, validate_spec=False):
    assert len(FIX) == 5
    for name, (paper, box, reason) in FIX.items():
        assert paper in SOURCES and reason.startswith("FAIL_"), name
        x0, y0, x1, y1 = box
        assert 0 <= x0 < x1 <= 1400 and 0 <= y0 < y1 <= 1980, name
    if validate_spec:
        return {"specValid": True, "v3Drafts": 5, "imageQaPassAdded": 0}
    actual = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if actual != BRANCH:
        raise RuntimeError("Refusing to write outside isolated QA branch: " + actual)
    prev = json.loads(p(OLD).read_text(encoding="utf-8"))
    failures = json.loads(p(FAIL).read_text(encoding="utf-8"))
    if prev.get("draftSingleQuestionCount") != 7 or prev.get("draftSharedMaterialCount") != 2:
        raise RuntimeError("Original 105 v2 ledger unexpectedly changed")
    prior = {x["assetId"]: x for x in prev["items"]}
    got = {x["assetId"]: x["result"] for x in failures["records"] if x["result"].startswith("FAIL_")}
    if len(prior) != 9 or got != {qid: details[2] for qid, details in FIX.items()}:
        raise RuntimeError("Existing v2 failures do not match these five repairs")
    prepared = []
    items = []
    for qid, (paper, box, reason) in FIX.items():
        old = prior[qid]
        source, source_sha, page_no = SOURCES[paper]
        if old["source"] != source or old["sourcePageWebpSha256"] != source_sha:
            raise RuntimeError("Original source provenance changed: " + qid)
        source_bytes = p(source).read_bytes()
        if sha(source_bytes) != source_sha:
            raise RuntimeError("Official source page SHA changed: " + qid)
        if sha(p(old["output"]).read_bytes()) != old["outputSha256"]:
            raise RuntimeError("Original v2 crop SHA changed: " + qid)
        with Image.open(io.BytesIO(source_bytes)) as page:
            page.load()
            if page.format != "WEBP" or page.size != (1400, 1980):
                raise RuntimeError("Unexpected source render: " + qid)
            stream = io.BytesIO()
            page.crop(box).save(stream, format="WEBP", lossless=True, method=6)
        candidate = stream.getvalue()
        with Image.open(io.BytesIO(candidate)) as check:
            check.load()
            if check.format != "WEBP" or check.size != (box[2]-box[0], box[3]-box[1]):
                raise RuntimeError("v3 WebP decode failed: " + qid)
        category = "shared" if len(old["questionIds"]) > 1 else paper
        relative = f"{BASE}/webp-v3/{category}/{qid}.webp"
        target = p(relative)
        if target.exists() and sha(target.read_bytes()) != sha(candidate):
            raise RuntimeError("Will not overwrite an existing different v3: " + qid)
        prepared.append((target, candidate))
        items.append({
            "assetId": qid, "questionIds": old["questionIds"],
            "priorVisualFailure": reason, "sourcePage": page_no,
            "source": source, "sourcePageWebpSha256": source_sha,
            "priorV2Webp": old["output"], "priorV2WebpSha256": old["outputSha256"],
            "v3CropPixels": list(box), "v3CandidateWebp": relative,
            "v3CandidateSha256": sha(candidate),
            "imageQaStatus": "DRAFT_PENDING_DIRECT_SOURCE_TO_CROP_VISUAL_QA",
            "answerVerified": False, "questionVerified": False, "integrationReady": False,
        })
    data = {
        "year": 105, "kind": "IMMUTABLE_UNVERIFIED_WEBP_V3_CANDIDATES",
        "count": len(items), "oldFailuresFixedByVisualQA": 0,
        "imageQaPassAdded": 0, "answerVerifiedAdded": 0,
        "integrationReady": False,
        "note": "Candidates generated from SHA-pinned official page renders; still require actual original-to-crop visual review and final official answer/correction checks.",
        "items": items,
    }
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    report = p(REPORT)
    if report.exists() and report.read_bytes() != raw:
        raise RuntimeError("Will not overwrite inconsistent v3 ledger")
    if stage:
        for path, data in prepared:
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if not report.exists():
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_bytes(raw)
    return {"status": "STAGED_UNVERIFIED_V3_DRAFT" if stage else "SOURCE_SHA_AND_V2_SHA_PASS",
            "v3Drafts": len(items), "newImageQaPass": 0, "newAnswerVerified": 0,
            "oldImagesOverwritten": 0, "integrationReady": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate-spec", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(stage=args.stage, validate_spec=args.validate_spec), ensure_ascii=False))
