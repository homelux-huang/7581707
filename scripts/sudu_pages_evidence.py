"""Compare Pages output with the authenticated formal G8 file inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import subprocess

from scripts import sudu_independent_review_gate as gate

MARKER = "sudu/release.json"
HEX = re.compile(r"[0-9a-f]{40}")


def inventory(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Public output must be a real directory")
    files = {}
    for item in sorted(root.rglob("*")):
        if item.is_symlink() or not (item.is_file() or item.is_dir()):
            raise ValueError(f"Invalid public output: {item.relative_to(root)}")
        if item.is_file():
            files[item.relative_to(root).as_posix()] = digest(item.read_bytes())
    return files


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_marker(site, commit):
    if not HEX.fullmatch(commit):
        raise ValueError("Invalid release commit")
    expected = json.dumps({"commit": commit, "testsRequired": True}) + "\n"
    if (site / MARKER).read_bytes() != expected.encode():
        raise ValueError("Release marker does not match the deployment checkout")


def original_stage(report, entry):
    raw = report["stageManifest"].encode("utf-8")
    if digest(raw) != entry["stageManifestSha256"]:
        raise ValueError("Original G8 stage manifest hash differs")
    stage = json.loads(raw, object_pairs_hook=gate._no_duplicate_keys)
    for key in ("codeCommit", "codeBindings", "payloadSha256", "rowSha256", "authorizationSha256"):
        if entry[key] != stage[key]:
            raise ValueError(f"G8 stage binding differs: {key}")
    if stage.get("status") != "PRE_G8_ONLY" or stage.get("pagesEligible") is not False:
        raise ValueError("Expected original private G8 staging manifest")
    if not isinstance(stage.get("siteFiles"), dict) or not stage["siteFiles"]:
        raise ValueError("Missing formal G8 public file inventory")
    return stage


def verify_output(site, stage, target):
    verify_marker(site, target)
    expected = dict(stage["siteFiles"])
    # The release marker is generated for each checkout. Its staged and final
    # versions are independently checked, while every other byte must match.
    staged_marker = json.dumps({"commit": stage["codeCommit"], "testsRequired": True}) + "\n"
    if expected.pop(MARKER, None) != digest(staged_marker.encode()):
        raise ValueError("Missing or invalid original G8 release marker")
    actual = inventory(site)
    del actual[MARKER]
    if actual != expected:
        diff = sorted(set(actual) ^ set(expected) |
                      {name for name in actual.keys() & expected.keys() if actual[name] != expected[name]})
        raise ValueError("Public output differs from formal G8: " + ", ".join(diff[:12]))


def public_rows(site):
    ids = set()
    rows = {}
    for year in (114, 115):
        payload = json.loads((site / f"sudu/data/approved/{year}.json").read_bytes(),
                             object_pairs_hook=gate._no_duplicate_keys)
        if payload["approvedCount"] != len(payload["questions"]):
            raise ValueError("Public approvedCount differs from question rows")
        for row in payload["questions"]:
            qid = row["canonicalId"]
            if qid in ids or not qid.startswith(f"{year}-"):
                raise ValueError("Duplicate or cross-year public question")
            ids.add(qid)
            rows[qid] = row
    return rows


def verify_deployment(site, target, policy, load_report):
    verify_marker(site, target)
    rows = public_rows(site)
    # The original five retain the repository's existing historical exception.
    new = rows.keys() - gate.LEGACY_FIVE_IDS
    if not new:
        return
    matches = []
    for qid in sorted(new):
        entry = policy.get("trustedG8Receipts", {}).get(qid)
        if not isinstance(entry, dict):
            raise ValueError(f"Missing protected G8 receipt: {qid}")
        from scripts.sudu_g8_release_bridge import authorization
        if entry["authorizationSha256"] != authorization(policy, qid):
            raise ValueError(f"Current E/G6 authorization differs: {qid}")
        if entry["rowSha256"] != digest(gate.canonical(rows[qid])):
            raise ValueError(f"Public row differs from protected G8: {qid}")
        stage = original_stage(load_report(entry), entry)
        if stage["qid"] != qid:
            raise ValueError("G8 manifest belongs to a different question")
        try:
            verify_output(site, stage, target)
        except ValueError as error:
            matches.append(str(error))
        else:
            matches.append(None)
    if None not in matches:
        raise ValueError("No protected G8 inventory matches the whole release: " + matches[-1])


def align_sync_candidate(candidate, source, target, policy, load_report):
    """Re-emit the normal sync candidate with the authenticated provenance."""
    from scripts import sudu_g8_release_bridge as bridge
    from scripts import sudu_verified_publish as publisher

    ids = public_rows(candidate).keys()
    new = ids - gate.LEGACY_FIVE_IDS
    if not new:
        return
    reports = {}
    source_commits = set()
    for qid in sorted(new):
        entry = policy["trustedG8Receipts"][qid]
        report = load_report(entry)
        reports[entry["reportSha256"]] = report
        stage = original_stage(report, entry)
        commit = stage["sourceCommit"]
        if not HEX.fullmatch(commit):
            raise ValueError("Invalid G8 source commit")
        source_commits.add(commit)
    for commit in sorted(source_commits):
        with tempfile.TemporaryDirectory(prefix="sudu-sync-g8-") as scratch:
            root = Path(scratch)
            native, site = root / "native", root / "site"
            publisher.stage(source, native, commit, review_policy=policy)
            publisher.site_check(native)
            if public_rows(native).keys() != ids:
                continue
            bridge.build_committed_site(target, site)
            bridge.replace_approved(native, site)
            try:
                verify_deployment(site, target, policy, lambda entry: reports[entry["reportSha256"]])
            except ValueError:
                continue
            bridge.replace_approved(native, candidate)
            return
    raise ValueError("No sync candidate reproduces the formal G8 output")



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--align-source", type=Path)
    args = parser.parse_args()
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != args.target:
        raise ValueError("Wrong Pages checkout")
    from scripts import sudu_g8_archive as archive
    from scripts import sudu_verified_publish
    sudu_verified_publish.site_check(args.site)
    _, policy = archive.current_policy()
    if args.align_source is None:
        verify_deployment(args.site, args.target, policy, archive.owned_report)
    else:
        align_sync_candidate(args.site, args.align_source, args.target, policy, archive.owned_report)
    print("Pages output verified for", args.target)


if __name__ == "__main__":
    main()
