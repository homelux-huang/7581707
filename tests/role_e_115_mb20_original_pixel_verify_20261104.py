#!/usr/bin/env python3
"""ROLE E: extract exact original 115 MB20 WebP pixels; do NOT approve students."""
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

DEST = Path("_role_e_mb20_pixel_qa")
DEST.mkdir(parents=True, exist_ok=True)
files = {
    "corrected_v5": (
        Path("sudu/data/processed/115/webp-v5/00-MB/115-00-MB-20.webp"),
        "f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf",
        "bd77281f8ee755074cf3b7ebcada5c06f3720c12",
    ),
    "official_p7": (
        Path("sudu/data/original/115/00-MB/p007-e82e34d9cd-v2-w1400-q66.webp"),
        "7a1732ce33ee6b9f1cc4fcc6f705b2aa1f29a117e0562a62b50428d94845464d",
        "c8e3e806d812a01d417abe83dac7f46adcf84ff7",
    ),
    "official_answer_p1": (
        Path("sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp"),
        "1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d",
        "5ea4b86e929506d595f96fa162d1aae021f68440",
    ),
    "historical_defective_v2": (
        Path("_old_source/sudu/data/processed/115/webp-v2/00-MB/115-00-MB-20.webp"),
        None,
        "fb055f43e0d186343015a6f6542cdc302e9ef5d5",
    ),
}
proof = {
    "role": "E",
    "taskId": "E-115-MB20-ORIGINAL-V5-PIXEL-DIRECT-QA-20261104-07",
    "questionId": "115-00-MB-20",
    "sourceHead": "80f87ddcbc1de06202a59d45e12557a20cc1394c",
    "oldSourceCommit": "fbd7756b995e3d27dc31a99ecc54fe66af4d82c6",
    "source": {},
    "imageReviewOutcome": "PENDING_INDEPENDENT_E_ACTUAL_VISUAL_REVIEW",
    "studentReleaseApproved": False,
}
images = {}
for kind, (path, expected_sha, expected_blob) in files.items():
    raw = path.read_bytes()
    observed_sha = hashlib.sha256(raw).hexdigest()
    if expected_sha is not None:
        assert observed_sha == expected_sha, (kind, "source SHA256 mismatch")
    observed_gitblob = subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()
    assert observed_gitblob == expected_blob, (kind, "Git Blob sha mismatch")
    img = Image.open(path)
    img.load()
    images[kind] = img
    if kind == "corrected_v5":
        assert img.size == (1220, 433), ("incorrect Q20 crop", img.size)
    converted = DEST / (kind + ".png")
    img.convert("RGB").save(converted, "PNG")
    proof["source"][kind] = {
        "path": str(path),
        "gitBlob": observed_gitblob,
        "sha256": observed_sha,
        "dimensions": list(img.size),
        "exportedPreview": str(converted),
        "previewSha256": hashlib.sha256(converted.read_bytes()).hexdigest(),
    }

original_crop = images["official_p7"].crop((90, 469, 1310, 902))
assert original_crop.size == images["corrected_v5"].size
cropfile = DEST / "original_p7_matching_crop.png"
original_crop.convert("RGB").save(cropfile)
delta = ImageChops.difference(original_crop.convert("RGB"), images["corrected_v5"].convert("RGB"))
proof["pixelComparison"] = {
    "crop": [90, 469, 1310, 902],
    "sameDimensions": True,
    "differenceRGBMean": ImageStat.Stat(delta).mean,
    "cropPreview": str(cropfile),
    "note": "Lossy WebP may introduce nonzero pixel difference; actual independent visual comparison required",
}
output = DEST / "source-bound-proof.json"
output.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS SHA-BOUND 115 MB20 v5, printed original p7, original official answer p1 and defective v2 binary checks")
print("SOURCE IMAGE MANUAL E REVIEW STILL PENDING; no source flag, reviewer registry or student approval changed")
print(json.dumps(proof["pixelComparison"], ensure_ascii=False))
