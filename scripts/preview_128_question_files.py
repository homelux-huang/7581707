#!/usr/bin/env python3
"""Frozen draft question file selection; suffixed review evidence isn't question 129."""
import re
from pathlib import Path

_CANONICAL_QUESTION = re.compile(
    r"1\d{2}-(?:\d{2}-[A-Z]{1,3}|\d{2}-\d)-\d{2}\.json"
)

def canonical_question_json_files(folder: Path):
    """Include every full-ID question file (even unknown IDs); exclude QA sidecars."""
    return [
        path for path in sorted(folder.glob("1??-*.json"))
        if _CANONICAL_QUESTION.fullmatch(path.name)
    ]
