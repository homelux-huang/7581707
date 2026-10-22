"""GitHub Pages post-deploy proof: exact commit and public student-safe data.

Runs after the unchanged same-commit release gate, production build and Pages deploy.
A successful upload is NOT a successful LIVE release until this script passes.
"""
import argparse
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
    if b"verifiedYearNav" not in js or b"data/approved" not in js:
        raise ValueError("LIVE yearly adapter is missing or stale")
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
        checked[y] = {"approved": count, "expected": stats["expected"]}
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
