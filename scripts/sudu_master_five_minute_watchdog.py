#!/usr/bin/env python3
"""Read-only GitHub Issue #36 watchdog. NEVER an AI agent or publishing gate."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

REPO = "homelux-huang/7581707"
ISSUE = 36
PRS = (30, 35, 46, 57, 58, 62, 65)
TASKS = (
    ("E-PR57-EXACT-AI-PUBLISHER-SECURITY-20261025-18", "E"),
    ("D-PR62-NONCALC-MATRIX-INDEPENDENT-20261025-08", "D"),
    ("A-115-C15-OPTION-D-CROSSPAGE-SQLITE-20261025-09", "A"),
    ("B-114-C15-C23-E10-E15-E20-IMGTRANS-20261025-08", "B"),
    ("C-115-NEXT-SOURCE-BOUND-AFTER-A-20261025-07", "C"),
    ("A-113-104-OFFICIAL-BASELINE-20261025-10", "A"),
    ("D-104-113-V4-ROUTING-CONTRACT-20261025-01", "D"),
)
TASK_ID = re.compile(r"\btaskId\s*[:=]?\s*[\x60*_]*([A-Z][A-Z0-9_-]{5,})", re.I)
EVENT_HEAD = re.compile(r"^\s*(CLAIMED|RETURN)\b", re.I)
LINE_ID = re.compile(
    r"^\s*(?:CLAIMED|RETURN)\b[^\n]{0,75}?"
    r"\b((?:MASTER|[ABCDE])-[A-Z0-9]+(?:-[A-Z0-9]+){2,})\b", re.I,
)


def events_from_comments(comments: list[dict]) -> dict[str, dict]:
    """An Issue dispatch mention is not a role ACK."""
    events = {}
    for item in comments:
        body = item.get("body") or ""
        match = EVENT_HEAD.search(body)
        if not match:
            continue
        task = TASK_ID.search(body[:1200]) or LINE_ID.search(body[:250])
        if not task:
            continue
        events[task.group(1)] = {
            "event": "CLAIM" if match.group(1).upper() == "CLAIMED" else "RETURN",
            "commentId": item.get("id"),
            "createdAt": item.get("created_at"),
            "url": item.get("html_url"),
        }
    return events


def make_report(main_sha: str, issue: dict, comments: list[dict],
                prs: dict[int, dict], now: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", main_sha):
        raise ValueError("main SHA invalid")
    events = events_from_comments(comments)
    queue = []
    for task_id, role in TASKS:
        previous = events.get(task_id)
        state = ("QUEUED_NOT_ACKNOWLEDGED" if not previous else
                 "CLAIM_RECORDED_NOT_PROOF_RUNNING" if previous["event"] == "CLAIM"
                 else "RETURN_RECORDED_REVIEW_PENDING")
        queue.append({
            "taskId": task_id, "role": role, "state": state,
            "issueEvidence": previous,
            "nextAction": "Refresh issue, claim exclusive lease, work, test and RETURN",
        })
    snapshots = {}
    for n, p in prs.items():
        head = (p.get("head") or {}).get("sha")
        if not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head):
            raise ValueError("PR SHA missing or invalid: " + str(n))
        snapshots[str(n)] = {
            "head": head, "state": p.get("state"), "draft": p.get("draft"),
            "base": (p.get("base") or {}).get("ref"),
        }
    return {
        "schemaVersion": 1,
        "kind": "READ_ONLY_COORDINATION_NOT_AGENT_EXECUTION",
        "observedAtUTC": now, "repository": REPO,
        "mainSHA": main_sha,
        "issue36": {"updatedAt": issue.get("updated_at"),
                    "reportedComments": issue.get("comments"),
                    "fetchedComments": len(comments)},
        "pullRequests": snapshots,
        "workQueue": queue,
        "release": {
            "newReady": "NOT_VERIFIED",
            "newMain": "NOT_VERIFIED",
            "newLive": "NOT_VERIFIED",
            "independentEQA": "NOT_VERIFIED",
            "mainProtection": "NOT_VERIFIED",
            "neverApproveMergeOrDeploy": True,
        },
        "limitations": [
            "Five-minute cron requires this workflow on default branch",
            "GitHub Actions cannot wake sleeping ChatGPT sessions",
            "Cron may be delayed or dropped",
            "Green CI or Issue CLAIM is not verified student READY",
        ],
    }


def summary_markdown(report: dict) -> str:
    lines = [
        "### 7581707 five-minute watchdog (read only)",
        "main SHA: " + report["mainSHA"],
        "Issue #36 comments: " + str(report["issue36"]["fetchedComments"]),
        "**Not an AI worker; no READY/main/LIVE is granted.**",
        "| Role | Task | Status |", "|---|---|---|",
    ]
    for t in report["workQueue"]:
        lines.append("| " + t["role"] + " | " + t["taskId"] +
                     " | " + t["state"] + " |")
    return "\n".join(lines) + "\n"


def api_get(path: str, token: str):
    if not path.startswith("/") or "//" in path:
        raise ValueError("bad API path")
    request = Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "Authorization": "Bearer " + token,
                 "User-Agent": "7581707-readonly-five-minute-watchdog"},
    )
    with urlopen(request, timeout=18) as response:
        return json.loads(response.read().decode("utf-8"))


def get_comments(path: str, token: str) -> list[dict]:
    comments = []
    for page in range(1, 21):
        batch = api_get(path + f"?per_page=100&page={page}", token)
        if not isinstance(batch, list):
            raise ValueError("missing Issue comments")
        comments.extend(batch)
        if len(batch) < 100:
            return comments
    raise RuntimeError("pagination limit reached; refuse partial Issue evidence")


def collect(token: str) -> dict:
    base = "/repos/" + REPO
    issue = api_get(base + f"/issues/{ISSUE}", token)
    comments = get_comments(base + f"/issues/{ISSUE}/comments", token)
    if len(comments) < (issue.get("comments") or 0):
        raise RuntimeError("Issue comments changed mid-snapshot; retry next tick")
    main_sha = api_get(base + "/branches/main", token)["commit"]["sha"]
    prs = {n: api_get(base + f"/pulls/{n}", token) for n in PRS}
    return make_report(main_sha, issue, comments, prs,
                       datetime.now(timezone.utc).isoformat())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="audit/7581707-five-minute-status.json")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("FAIL_CLOSED: GH_TOKEN missing", file=sys.stderr)
        return 2
    try:
        report = collect(token)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                     sort_keys=True) + "\n", encoding="utf-8")
        summary = summary_markdown(report)
        print(summary, end="")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(summary)
    except (HTTPError, URLError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print("FAIL_CLOSED: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
