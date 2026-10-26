#!/usr/bin/env python3
"""Free-first, read-only TCTE source inventory and main-approved allowlist audit.

Input is GitHub's existing archived annual JSON plus published *main* allowlists.
No independent QA, original visual inspection, answer verification, UI QA,
READY or LIVE status may be inferred from these inputs. No network/model use.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

YEARS = tuple(range(104, 116))
APPROVED_YEARS = (114, 115)
PAPER_CODES = {"00-C", "00-E", "00-MB", "09-1", "09-2"}
QUESTION_ID = re.compile(r"^(10[4-9]|11[0-5])-(00-C|00-E|00-MB|09-1|09-2)-\d{1,3}$")
IMAGE_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def read_json(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return doc


def source_year(year: int, root: Path) -> tuple[dict, list[dict]]:
    file = root / "sudu" / "data" / "years" / f"{year}.json"
    document = read_json(file)
    if document.get("year") != year:
        raise ValueError(f"Wrong source year: {file}")
    expected_index = f"https://web1.tcte.edu.tw/EXAM/{year}_4y/"
    if document.get("sourceIndex") != expected_index:
        raise ValueError(f"Unexpected official source URL for {year}")
    papers = document.get("papers")
    if not isinstance(papers, list) or {p.get("paper") for p in papers} != PAPER_CODES:
        raise ValueError(f"Missing/duplicate original paper envelope(s) in {year}")
    if len(papers) != len(PAPER_CODES):
        raise ValueError(f"Duplicate original paper envelope in {year}")

    seen = set()
    questions = []
    paper_counts = {}
    by_paper = {}
    for paper in papers:
        code = paper["paper"]
        batch = paper.get("questions")
        if not isinstance(batch, list):
            raise ValueError(f"Invalid paper questions: {year}/{code}")
        paper_counts[code] = len(batch)
        for question in batch:
            qid = question.get("id")
            if not isinstance(qid, str) or not QUESTION_ID.fullmatch(qid):
                raise ValueError(f"Invalid official candidate ID: {year}/{qid}")
            if not qid.startswith(f"{year}-{code}-"):
                raise ValueError(f"Question-paper mismatch: {qid}")
            if qid in seen:
                raise ValueError(f"Duplicate candidate ID {qid}")
            seen.add(qid)
            questions.append(question)
            by_paper[qid] = code

    reported = document.get("questionsFound")
    if not isinstance(reported, int) or reported < 0:
        raise ValueError(f"Missing numeric questionsFound: {year}")
    answer_matches = sum(q.get("answerMatched") is True for q in questions)
    independent_answers = sum(q.get("answerVerified") is True for q in questions)
    verified_questions = sum(q.get("questionVerified") is True for q in questions)
    teaching_verified = sum(q.get("teachingVerified") is True for q in questions)
    issues = sum(bool(q.get("issues")) for q in questions)
    # These are values IN THE LEGACY YEAR FILE ONLY; newer isolated PR
    # A/B/C/D/E receipts may exist and require separate exact-commit merging.
    raw_subjects = sorted({str(q.get("subject")) for q in questions
                           if q.get("subject") is not None})
    result = {
        "year": year,
        "officialCompleteQuestionCount": None,
        "originalPaperEnvelopes": paper_counts,
        "rawSubjectLabelsNotVerifiedAgainstSevenDemo": raw_subjects,
        "rawCandidateCount": len(questions),
        "historicalQuestionsFound": reported,
        "countDiscrepancy": len(questions) - reported,
        "legacyAutoAnswerMatchedNOTFinalQA": answer_matches,
        "legacyQuestionVerifiedFlagOnly": verified_questions,
        "legacyAnswerVerifiedFlagOnly": independent_answers,
        "legacyTeachingVerifiedFlagOnly": teaching_verified,
        "rawQuestionIssuesCount": issues,
        "mainApprovedAllowlistCount": 0,
        "mainApprovalPercentOfExpected": None,
        "incrementalLiveVerified": None,
        "stage": "RAW_CANDIDATES__NOT_QA_CERTIFIED",
    }
    return result, questions


def main_allowlist(year: int, root: Path, raw_ids: set[str]) -> dict:
    file = root / "sudu" / "data" / "approved" / f"{year}.json"
    doc = read_json(file)
    if doc.get("year") != year:
        raise ValueError(f"Wrong main approved year: {file}")
    qs = doc.get("questions")
    if not isinstance(qs, list) or not isinstance(doc.get("approvedCount"), int):
        raise ValueError(f"Malformed main allowlist: {file}")
    ids = [q.get("canonicalId") for q in qs]
    if not all(isinstance(i, str) for i in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate/empty approved ID in {year}")
    if len(ids) != doc["approvedCount"]:
        raise ValueError(f"approvedCount disagrees with question entries: {year}")
    if set(ids) - raw_ids:
        raise ValueError(f"Main approved question not in annual candidate source: {year}")
    if any(not IMAGE_SHA256.fullmatch(q.get("imageSha256", "")) for q in qs):
        raise ValueError(f"Malformed approved original image hash in {year}")
    expected = doc.get("expected")
    if not isinstance(expected, int) or expected < len(ids):
        raise ValueError(f"Invalid main allowlist expected total in {year}")
    if not doc.get("sourceSha"):
        raise ValueError(f"Missing main approved sourceSha: {year}")
    return {
        "approvedIds": ids,
        "mainApprovedAllowlistCount": len(ids),
        "mainApprovalPercentOfExpected": round(100 * len(ids) / expected, 2),
        "expectedAsStatedInMainAllowlistNOTIndependentlyOfficial": expected,
        "publishedRevisionOnlyFromMain": doc["sourceSha"],
    }


def build_report(root: Path, observed_at: str) -> dict:
    result = []
    for year in YEARS:
        record, qs = source_year(year, root)
        ids = {q["id"] for q in qs}
        if year in APPROVED_YEARS:
            approved = main_allowlist(year, root, ids)
            record.update({k: v for k, v in approved.items() if k != "approvedIds"})
            approved_ids = set(approved["approvedIds"])
            # This is not a READY queue: source/official-answer/E/D verification
            # is mandatory before even considering any individual item.
            candidates = [
                q for q in qs if q["id"] not in approved_ids
            ]
            candidates.sort(key=lambda q: (
                bool(q.get("issues")),
                not (q.get("answerMatched") is True),
                q["id"],
            ))
            record["readOnlyCandidateIdsForNextSourceQA"] = [
                q["id"] for q in candidates[:12]
            ]
            record["pendingCandidateCountNOTReady"] = len(candidates)
        else:
            record["readOnlyCandidateIdsForNextSourceQA"] = []
            record["pendingCandidateCountNOTReady"] = record["rawCandidateCount"]
        result.append(record)
    return {
        "schemaVersion": 1,
        "kind": "FREE_DETERMINISTIC_INVENTORY__NO_AI_QA_OR_DEPLOY",
        "observedAtUTC": observed_at,
        "years": result,
        "totals": {
            "rawSourceCandidatesNotOfficialCompleteness":
                sum(x["rawCandidateCount"] for x in result),
            "legacyAutomaticAnswerMatchesNotFinalQA":
                sum(x["legacyAutoAnswerMatchedNOTFinalQA"] for x in result),
            "mainApprovedAllowlist114115":
                sum(x["mainApprovedAllowlistCount"] for x in result),
            "newReadyNotProven": None,
            "newLiveNotProven": None,
        },
        "guards": {
            "requiresOfficialSourceAndImageQA": True,
            "requiresFinalAnswerAndCorrectionEvidence": True,
            "requiresDistinctReviewAndExactTeachingDigest": True,
            "requiresSameRevisionV4_8x2": True,
            "onlyProtectedPublisherCanRelease": True,
            "writesToRepository": False,
            "modelInferenceUsed": False,
            "chargesPaidAI": False,
        },
        "limitations": [
            "This inventory reads main annual JSON, not unmerged A/B/C/D/E Draft PRs.",
            "Raw paper/subject labels are not proof of complete seven-subject mapping.",
            "Legacy answerMatched is automatic pairing only, never answerVerified.",
            "An existing main-approved row is NOT evidence of live Pages/browser QA.",
            "No question ID is automatically marked READY or LIVE.",
        ],
    }


def markdown_report(report: dict) -> str:
    lines = [
        "## 7581707 104-115 Free-first inventory (READ ONLY)",
        "No AI calls. No student READY or LIVE admission. Historical candidate totals are NOT official completeness.",
        "",
        "| Year | Raw source candidates | Legacy questionsFound gap | Auto matched (NOT verified) | Legacy Q/A verified flags | Main approved |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for record in report["years"]:
        lines.append(
            f"| {record['year']} | {record['rawCandidateCount']} | "
            f"{record['countDiscrepancy']:+d} | "
            f"{record['legacyAutoAnswerMatchedNOTFinalQA']} | "
            f"{record['legacyQuestionVerifiedFlagOnly']}/"
            f"{record['legacyAnswerVerifiedFlagOnly']} | "
            f"{record['mainApprovedAllowlistCount']} |"
        )
    lines.extend([
        "",
        "Main approved 114/115 ≠ LIVE verification; the existing protected "
        "publisher / Pages / exact V4 checks decide student admission.",
        "Older 104-113 raw candidate lists have no official completeness "
        "or per-subject READY percentage proven here.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default="audit/free-first")
    args = parser.parse_args()
    try:
        report = build_report(Path(args.root),
            datetime.now(timezone.utc).isoformat())
        folder = Path(args.output_dir)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "source-and-allowlist.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
            + "\n", encoding="utf-8")
        markdown = markdown_report(report)
        (folder / "source-and-allowlist.md").write_text(markdown, encoding="utf-8")
        print(markdown)
        import os
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(markdown)
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL_CLOSED free-first source/allowlist audit: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
