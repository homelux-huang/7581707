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


def canonical_digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,
                       separators=(",",":")).encode("utf-8")).hexdigest()

def inspect_live(base, sha, root=None):
    """Verify every published byte against this exact checked-out main commit.

    Source teaching/revision digests come from the QA-gated publisher's
    per-question release-integrity manifest, never from untrusted LIVE metadata
    alone. This function does NOT claim to inspect client localStorage.
    """
    from pathlib import Path
    import re
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    revision=json.loads(fetch(base,"sudu/release.json",sha))
    if revision.get("commit")!=sha or revision.get("testsRequired") is not True:
        raise ValueError("LIVE release.json is not the exact approved SHA")
    page=fetch(base,"sudu/v4-115-multisubject-review-demo.html",sha).decode("utf-8")
    if 'id="demoData"' not in page or "verified-questions-runtime.js" not in page:
        raise ValueError("LIVE V4 lacks original Demo and verified adapter")
    js=fetch(base,"sudu/verified-questions-runtime.js",sha)
    local_runtime=root/"sudu/verified-questions-runtime.js"
    if not local_runtime.is_file() or js!=local_runtime.read_bytes():
        raise ValueError("LIVE yearly runtime not identical to exact released main")
    adapter_rev=hashlib.sha256(js).hexdigest()[:12]
    if f"verified-questions-runtime.js?v={adapter_rev}" not in page:
        raise ValueError("LIVE V4 references stale yearly runtime")
    if (b"verifiedSingleQuestionWebp" not in js or b"data/approved" not in js
            or b"verifiedYearNav" in js or b"verifiedImagePreview" in js):
        raise ValueError("LIVE yearly adapter is missing inline source or contains QA overlays")
    dash=fetch(base,"sudu/question-bank-progress.html",sha).decode("utf-8")
    if "題庫接入平台部署進度表" not in dash:
        raise ValueError("LIVE progress dashboard missing")
    cache={}
    def local_public(relative):
        if not relative.startswith("sudu/data/approved/") or ".." in Path(relative).parts:
            raise ValueError("untrusted public manifest route "+relative)
        path=root/relative
        if not path.is_file() or path.is_symlink():
            raise ValueError("expected exact main manifest not present: "+relative)
        expected=path.read_bytes()
        live=fetch(base,relative,sha)
        if live!=expected:
            raise ValueError("LIVE manifest differs from main content: "+relative)
        return json.loads(live)
    def check_asset(image,expected,year):
        if (not isinstance(image,str) or not re.fullmatch(
             rf"data/approved/webp/{year}/{year}-(?:00-C|00-E|00-MB|09-1|09-2)-(?:[0-9]{{2}}|SHARED-[0-9]{{2}}-[0-9]{{2}})\.webp",image)
             or not isinstance(expected,str) or not re.fullmatch(r"[a-f0-9]{64}",expected)):
            raise ValueError(f"{year} unsafe or incomplete image reference: {image}")
        rel="sudu/"+image
        if rel in cache:
            if cache[rel]!=expected: raise ValueError("LIVE image manifest inconsistent: "+rel)
            return
        payload=fetch(base,rel,sha)
        actual=hashlib.sha256(payload).hexdigest()
        if actual!=expected or not (payload.startswith(b"RIFF") and payload[8:12]==b"WEBP"):
            raise ValueError("LIVE original single/shared image SHA invalid: "+rel)
        local_file=root/rel
        if not local_file.is_file() or local_file.is_symlink() or hashlib.sha256(local_file.read_bytes()).hexdigest()!=expected:
            raise ValueError("current main source WebP SHA invalid: "+rel)
        cache[rel]=actual

    progress=local_public("sudu/data/approved/progress.json")
    if progress.get("provenance",{}).get("commit") is None:
        raise ValueError("official source commit absent from release progress")
    results={}
    for year in (114,115):
        label=str(year)
        approved=local_public(f"sudu/data/approved/{year}.json")
        preview=local_public(f"sudu/data/approved/preview/{year}.json")
        integrity=local_public(f"sudu/data/approved/integrity/{year}.json")
        stats=progress["years"][label]
        questions=approved.get("questions")
        reviewed=preview.get("questions")
        proofs=integrity.get("questions")
        if not all(isinstance(v,list) for v in (questions,reviewed,proofs)):
            raise ValueError(f"{year} expected complete released lists")
        if not (approved.get("year")==year and integrity.get("year")==year
                and preview.get("year")==year and integrity.get("schemaVersion")==1
                and approved.get("sourceSha")==integrity.get("sourceSha")==progress["provenance"]["commit"]
                and approved.get("expected")==preview.get("expected")==stats.get("expected")==205
                and len(questions)==approved.get("approvedCount")==integrity.get("approvedCount")==stats.get("approvedCount")
                and len(proofs)==len(questions)
                and len(reviewed)==preview.get("imagePreviewCount")==stats.get("imagePreviewCount",0)):
            raise ValueError(f"{year} LIVE approved/source/integrity/preview counters mismatch")
        gids=[q.get("canonicalId") for q in questions]
        pids=[p.get("canonicalId") for p in proofs]
        if len(set(gids))!=len(gids) or gids!=pids or any(
             not isinstance(x,str) or not x.startswith(str(year)+"-") for x in gids):
            raise ValueError(f"{year} duplicate or inconsistent approved identifiers")
        for q,proof in zip(questions,proofs):
            qid=q["canonicalId"]
            if not (proof.get("year")==year
                    and proof.get("officialAnswer")==q.get("answer") in "ABCD"
                    and proof.get("image")==q.get("image")
                    and proof.get("imageSha256")==q.get("imageSha256")
                    and proof.get("approvedContentSha256")==canonical_digest(q)
                    and all(isinstance(proof.get(k),str) and re.fullmatch(r"[a-f0-9]{64}",proof[k])
                            for k in ("sourceQuestionRevision","teachingCanonicalSha256"))):
                raise ValueError(f"{qid} LIVE approved answer/text/teaching or original source revision SHA is stale")
            check_asset(q.get("image"),q.get("imageSha256"),year)
            shared=proof.get("sharedImages")
            if not isinstance(shared,list):
                raise ValueError("missing shared WebP manifest: "+qid)
            for item in shared:
                check_asset(item.get("image"),item.get("sha256"),year)
        seen=set()
        for q in reviewed:
            qid=q.get("canonicalId")
            if not isinstance(qid,str) or not qid.startswith(str(year)+"-") or qid in seen:
                raise ValueError(f"{year} duplicate or wrong image-only preview ID")
            seen.add(qid)
            if q.get("year")!=year or q.get("reviewStage")!="image_qa_pass_only":
                raise ValueError(f"{year} non QA-approved original image in preview")
            if any(k in q for k in ("answer","question","options","teaching","memory","independentSolve")):
                raise ValueError(f"{year} leaked unreviewed answer/OCR into image-only preview")
            check_asset(q.get("image"),q.get("imageSha256"),year)
            if not isinstance(q.get("sharedImages"),list):
                raise ValueError(f"{qid} sharedImages is not a complete explicit list")
            for item in q["sharedImages"]:
                check_asset(item.get("image"),item.get("sha256"),year)
        results[label]={"approved":len(questions),"imagePreviews":len(reviewed),
                        "expected":205}
    return {"live":"VERIFIED_ALL_PUBLISHED_BYTES","sha":sha,"years":results,
            "allDistinctAssetsChecked":len(cache),
            "url":base.rstrip("/")+"/sudu/v4-115-multisubject-review-demo.html"}


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
