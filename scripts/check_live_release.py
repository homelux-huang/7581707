"""GitHub Pages post-deploy proof: exact commit and public student-safe data.

Runs after the unchanged same-commit release gate, production build and Pages deploy.
A successful upload is NOT a successful LIVE release until this script passes.
"""
import argparse
import hashlib
import json
import sys
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen


def fetch(base, route, sha):
    u = urljoin(base.rstrip("/") + "/", route.lstrip("/"))
    url = u + ("&" if "?" in u else "?") + urlencode({"release_probe": sha[:12]})
    with urlopen(Request(url, headers={"Cache-Control": "no-cache",
                                      "User-Agent": "7581707-Release-Verification/1.0"}),
                 timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"{route} returned {r.status}")
        return r.read()


def inspect_live(base, sha):
    revision = json.loads(fetch(base, "sudu/release.json", sha))
    if revision.get("commit") != sha or revision.get("testsRequired") is not True:
        raise ValueError("LIVE release.json is not the exact approved SHA")
    page = fetch(base, "sudu/v4-115-multisubject-review-demo.html", sha).decode("utf-8")
    if 'id="demoData"' not in page or "verified-questions-runtime.js" not in page:
        raise ValueError("LIVE V4 does not contain the original Demo or verified runtime adapter")
    js = fetch(base, "sudu/verified-questions-runtime.js", sha)
    adapter_revision = hashlib.sha256(js).hexdigest()[:12]
    if f'verified-questions-runtime.js?v={adapter_revision}' not in page:
        raise ValueError("LIVE HTML references a stale/cached yearly runtime")
    if (b"verifiedSingleQuestionWebp" not in js or b"data/approved" not in js
            or b"verifiedYearNav" in js or b"verifiedImagePreview" in js):
        raise ValueError("LIVE yearly adapter lacks inline WebP or contains obstructive QA blocks")
    dash = fetch(base, "sudu/question-bank-progress.html", sha).decode("utf-8")
    if "題庫接入平台部署進度表" not in dash:
        raise ValueError("LIVE progress dashboard missing")
    progress = json.loads(fetch(base, "sudu/data/approved/progress.json", sha))
    checked = {}
    for year in (114,115):
        y = str(year)
        item = json.loads(fetch(base, f"sudu/data/approved/{y}.json", sha))
        stats = progress["years"][y]
        if item.get("year") != year or not isinstance(item.get("questions"), list):
            raise ValueError(f"{year} LIVE approved format invalid")
        count = len(item["questions"])
        if count != item.get("approvedCount") or count != stats.get("approvedCount"):
            raise ValueError(f"{year} LIVE year count and progress disagree")
        if stats.get("expected") != 205:
            raise ValueError(f"{year} wrong expected question count")
        preview = json.loads(fetch(base, f"sudu/data/approved/preview/{y}.json", sha))
        reviewed = preview.get("questions")
        if (preview.get("year") != year or not isinstance(reviewed, list)
                or len(reviewed) != preview.get("imagePreviewCount")
                or len(reviewed) != stats.get("imagePreviewCount", 0)):
            raise ValueError(f"{year} LIVE image-only QA preview counts disagree")
        for q in reviewed[:2]:
            if q.get("year") != year or q.get("reviewStage") != "image_qa_pass_only":
                raise ValueError(f"{year} LIVE preview includes a non-approved image stage")
            if any(field in q for field in ("answer", "question", "options", "teaching", "memory")):
                raise ValueError(f"{year} LIVE preview leaked an unverified answer or OCR")
            if not isinstance(q.get("image"), str) or not q["image"].startswith(f"data/approved/webp/{year}/"):
                raise ValueError(f"{year} LIVE preview references another data area")
            for image in [{"image": q["image"], "sha256": q.get("imageSha256")},
                          *(q.get("sharedImages") or [])[:1]]:
                payload = fetch(base, "sudu/" + image["image"], sha)
                if hashlib.sha256(payload).hexdigest() != image["sha256"]:
                    raise ValueError(f"{year} LIVE image content SHA did not match audited source")
        checked[y] = {"approved": count, "imagePreviews": len(reviewed), "expected": stats["expected"]}
    return {"live": "VERIFIED", "sha": sha, "years": checked,
            "url": base.rstrip("/") + "/sudu/v4-115-multisubject-review-demo.html"}


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--url", required=True)
    cli.add_argument("--expected-sha", required=True)
    cli.add_argument("--attempts", type=int, default=12)
    cli.add_argument("--delay", type=int, default=12)
    args = cli.parse_args()
    if not (len(args.expected_sha) == 40 and all(c in "0123456789abcdef" for c in args.expected_sha)):
        raise SystemExit("Expected SHA must be 40 hex characters")
    if not args.url.startswith("https://homelux-huang.github.io/7581707/"):
        raise SystemExit("Refusing to probe an unrelated destination")
    errors = []
    for i in range(max(1, args.attempts)):
        try:
            data = inspect_live(args.url, args.expected_sha)
            print("LIVE_VERIFIED", json.dumps(data, ensure_ascii=False))
            return
        except (ValueError, KeyError, RuntimeError, URLError, HTTPError, OSError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            print(f"LIVE_NOT_YET_VERIFIED attempt={i + 1}/{args.attempts}: {exc}", file=sys.stderr)
            if i + 1 < args.attempts:
                time.sleep(args.delay)
    raise SystemExit(f"Live page did not match commit after {args.attempts} attempts: {errors[-1]}")


if __name__ == "__main__":
    main()
