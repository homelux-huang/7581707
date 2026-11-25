"""Authorize the exact protected-main Pages target before any target job.

The caller fetches refs/heads/main from origin and obtains the branch metadata
read-only from GitHub. This module does not dispatch or deploy anything.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

REPOSITORY = "homelux-huang/7581707"
MAIN_REF = "refs/heads/main"
PAGES_WORKFLOW_REF = f"{REPOSITORY}/.github/workflows/pages.yml@{MAIN_REF}"
SHA = re.compile(r"[0-9a-f]{40}")


def authorize(target: str, branch: dict, env: dict, root: Path) -> str:
    if (env.get("GITHUB_REPOSITORY") != REPOSITORY
            or env.get("GITHUB_EVENT_NAME") not in {"push", "workflow_dispatch"}
            or env.get("GITHUB_REF") != MAIN_REF
            or env.get("GITHUB_REF_PROTECTED") != "true"
            or env.get("GITHUB_WORKFLOW_REF") != PAGES_WORKFLOW_REF):
        raise ValueError("Pages must run from the protected main workflow")
    if not SHA.fullmatch(target or ""):
        raise ValueError("Pages target must be a full lowercase Git commit SHA")
    workflow_sha = env.get("GITHUB_WORKFLOW_SHA")
    if target != env.get("GITHUB_SHA") or target != workflow_sha:
        raise ValueError("Pages target must equal the event and executing workflow commits")
    if (not isinstance(branch, dict) or branch.get("name") != "main"
            or branch.get("protected") is not True or not isinstance(branch.get("commit"), dict)):
        raise ValueError("GitHub has not confirmed that main is protected")
    protected = branch["commit"].get("sha")
    if not isinstance(protected, str) or not SHA.fullmatch(protected):
        raise ValueError("Invalid GitHub protected main tip")

    def rev(ref: str) -> str:
        return subprocess.check_output(
            ["git", "rev-parse", "--verify", ref + "^{commit}"], cwd=root,
            stderr=subprocess.DEVNULL, text=True).strip()

    if rev("HEAD") != workflow_sha:
        raise ValueError("Preflight did not check out the executing workflow commit")
    if rev("refs/remotes/origin/main") != protected:
        raise ValueError("Fetched main differs from GitHub protected main; run again")
    if subprocess.run(["git", "merge-base", "--is-ancestor", target, protected], cwd=root,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        raise ValueError("Pages target is not in the protected main history")
    if target != protected:
        raise ValueError("Pages target is stale; dispatch the latest protected main tip")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--branch-response", type=Path, required=True)
    args = parser.parse_args()
    try:
        branch = json.loads(args.branch_response.read_text(encoding="utf-8"))
        print(authorize(args.target, branch, os.environ, Path.cwd()))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Pages target HOLD: {exc}\n")


if __name__ == "__main__":
    main()
