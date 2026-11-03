#!/usr/bin/env python3
"""Generate ONLY missing p6 lamp shared reading from exact original source decoded pixels (no OCR / AI)."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops
ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "sudu/data/processed/114/review-evidence/114-00-C-16-18-original-lamps-20261103.json"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
def main():
    ev = json.loads(EVID.read_text(encoding="utf-8"))
    shared = ev["sharedMaterial"]
    src_file = ROOT / shared["sourcePage"]
    raw_src = src_file.read_bytes()
    assert git_blob(raw_src) == shared["sourcePageGitBlob"]
    assert sha(raw_src) == ev["officialQuestionImages"][0]["sha256"]
    crop = tuple(shared["cropPixels"])
    assert crop == (90, 155, 1310, 1360)
    assert ev["questionImageRecords"][0]["number"] == 16
    # Original Q16 crop begins at y=1362. Shared bottom y=1360, so the shared image never includes Q16 choices.
    assert crop[3] <= 1360
    with Image.open(src_file) as source:
        assert source.size == (1400, 1981)
        assert source.format == "WEBP"
        wanted = source.convert("RGB").crop(crop)
    assert wanted.size == tuple(shared["cropWidthHeight"])
    output = ROOT / shared["isolatedSharedWebp"]
    output.parent.mkdir(parents=True, exist_ok=True)
    wanted.save(output, format="WEBP", lossless=True, method=6)
    with Image.open(output) as actual:
        assert actual.format == "WEBP"
        obtained = actual.convert("RGB")
        assert obtained.size == wanted.size
        assert ImageChops.difference(obtained, wanted).getbbox() is None, "lossless original source pixel mismatch"
    raw = output.read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
    shared["sha256"] = sha(raw)
    shared["gitBlob"] = git_blob(raw)
    shared["visualReviewStatus"] = shared.get("visualReviewStatus", "PENDING_DIRECT_ASSISTANT_INSPECTION")
    if shared["visualReviewStatus"] == "PENDING_GENERATE_AND_DIRECT_ASSISTANT_INSPECTION":
        shared["visualReviewStatus"] = "PENDING_DIRECT_ASSISTANT_INSPECTION"
    seed = "ROLE_A_114_LAMPS_SHARED_G1_V1\n" + shared["sha256"] + "\n" + "\n".join(r["sha256"] for r in ev["questionImageRecords"])
    shared["sourceRevisionSeed"] = seed
    shared["sourceRevisionSha256"] = sha(seed.encode("utf-8"))
    ev["status"] = "ROLE_A_SOURCE_G1_SHARED_PIXEL_GENERATED_PENDING_DIRECT_VISUAL_REVIEW_NO_RELEASE" if shared["visualReviewStatus"] != "PASS_AI_ASSISTANT_DIRECT_VISUAL_ORIGINAL" else "ROLE_A_SOURCE_IMAGE_VISUAL_REVIEW_CANDIDATE_NO_RELEASE"
    EVID.write_text(json.dumps(ev, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"sharedWebp":str(output.relative_to(ROOT)), "sha256":shared["sha256"], "blob":shared["gitBlob"],"sourceRevision":shared["sourceRevisionSha256"],"status":shared["visualReviewStatus"]},ensure_ascii=False))
if __name__ == "__main__":
    main()
