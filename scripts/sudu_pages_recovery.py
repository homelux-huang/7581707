"""Decide whether the existing SAME-SHA GitHub Pages gate needs a retry.

Never deploys by itself, never switches to another repo or commit. Each GitHub
Actions schedule evaluates the latest main SHA and the Pages workflow status;
only missing/cancelled/failed runs are candidates for redispatch.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
ACTIVE = frozenset(("in_progress", "queued", "pending", "waiting", "requested"))


def decision(commit: str, data: dict) -> str:
    """Returns active, verified or retry for exactly one SHA."""
    if not SHA.fullmatch(commit):
        raise ValueError("Invalid 40-char main SHA")
    runs = data.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("Unexpected Pages workflow response")
    candidates = []
    for item in runs:
        if not isinstance(item, dict):
            raise ValueError("Malformed workflow run")
        if item.get("head_sha") == commit:
            candidates.append(item)
    if any(run.get("status") in ACTIVE for run in candidates):
        return "active"
    # pages.yml now reports success ONLY when verify_live and all prior jobs pass.
    if any(run.get("status") == "completed" and run.get("conclusion") == "success"
           for run in candidates):
        return "verified"
    return "retry"


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--main-sha", required=True)
    args.add_argument("--runs", type=Path, required=True)
    config = args.parse_args()
    print(decision(config.main_sha, json.loads(config.runs.read_text(encoding="utf-8"))))


if __name__ == "__main__":
    main()
