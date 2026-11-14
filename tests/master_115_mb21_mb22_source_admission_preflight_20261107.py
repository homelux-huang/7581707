"""Read-only, fail-closed source admission preflight for 115 MB21/22.

This is NOT a publisher, content receipt, source certification, or approval.
The official QA bank, ROLE A staged original and ROLE C authored file are
checked out to separate immutable source trees by the workflow. Never write
back to any source tree or allow a fake E receipt.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QIDS = ("115-00-MB-21", "115-00-MB-22")
SRC = "sudu/data/processed/115"
AUTH = "sudu/teaching-candidates/114-115-20261025"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def state(qa, stage, author, qid, official):
    bank = next(q for q in load(qa / SRC / "questions.json")["questions"] if q["questionId"] == qid)
    manifest = next(q for q in load(qa / SRC / "webp-manifest.json")["items"] if q["questionId"] == qid)
    s = load(stage / SRC / "source-stage" / f"{qid}-staged-20261104.json")
    c = load(author / AUTH / f"{qid}.json")
    original = s["originalSource"]
    proof = s["officialAnswer"]
    assert s["questionId"] == c["questionId"] == bank["questionId"] == qid
    assert s["stageStatus"].endswith("CANONICAL_SQLITE_UNMODIFIED_NO_RELEASE")
    assert original["originalCleanQuestion"] == c["question"], "A staged text and C author's source changed"
    assert original["originalCleanOptions"] == c["options"], "A staged options and C author's source changed"
    assert original["singleSha256"] == c["imageSha256"] == manifest["sha256"], "Source/author/manifest image changed"
    assert original["singleWebp"] == c["image"] == manifest["output"], "Actual single-WebP path conflict"
    actual = (qa / manifest["output"])
    assert actual.is_file() and hashlib.sha256(actual.read_bytes()).hexdigest() == manifest["sha256"]
    assert manifest["qaStatus"] == "PASS"
    assert proof["officialPublishedLetter"] == official == bank["officialFinalAnswer"] == bank["answer"]
    assert bank["answerVerified"] is True
    assert c.get("studentReleaseApproved") is False and c.get("deploy") is False
    assert s["frozenCanonicalReadOnly"]["canonicalBankModified"] is False
    # Old canonical question text may disagree with corrected staged transcription:
    # report it, NEVER silently overwrite or infer source certification.
    question_equal = bank["question"] == original["originalCleanQuestion"]
    options_equal = bank["options"] == original["originalCleanOptions"]
    formal_source = (
        bank["questionVerified"] is True
        and bank.get("textQaStatus") == "PASS"
        and question_equal and options_equal
    )
    return {
        "questionId": qid, "originalOfficialLetter": official,
        "webpSha256": manifest["sha256"],
        "authorTeachingCanonicalSha256": c["teachingCanonicalSha256"],
        "sourceAStageBlobRelease": False,
        "formalSourceGate": "PASS" if formal_source else "HOLD",
        "canonicalQuestionVerified": bank["questionVerified"],
        "canonicalAnswerVerified": bank["answerVerified"],
        "questionTextMatchesStagedOriginal": question_equal,
        "optionsMatchStagedOriginal": options_equal,
        "canonicalSourceImportRequired": not formal_source,
        "G6ExternalBlindVerified": False,
        "G7ProtectedTrustedReceiptVerified": False,
        "G8FormalPublisherEmitted16": False,
        "READY": False,
        "LIVE": False,
    }


def main():
    qa = ROOT / "_source_qa"
    stage = ROOT / "_source_a"
    author = ROOT / "_source_c"
    results = [state(qa, stage, author, qid, key) for qid, key in
               (("115-00-MB-21", "A"), ("115-00-MB-22", "B"))]
    assert len(load(qa / SRC / "questions.json")["questions"]) == 205
    assert len(load(qa / SRC / "webp-manifest.json")["items"]) == 205
    original_batch = load(qa / SRC / "verified-student-batch.json")
    admitted = set(original_batch["approvedQuestionIds"])
    assert len(admitted) == 5
    assert not admitted.intersection(QIDS)
    approved = load(ROOT / "sudu/data/approved/115.json")
    assert approved["approvedCount"] == len(approved["questions"]) == 5
    assert not {q["canonicalId"] for q in approved["questions"]}.intersection(QIDS)
    policy = load(ROOT / "sudu/release-governance/independent-review-policy.json")
    assert policy["reviewMode"] == "DISTINCT_AI_CONTENT_RECEIPT_V1"
    assert not any(qid in policy["trustedAiReviewReceipts"] for qid in QIDS)
    assert all(r["canonicalSourceImportRequired"] for r in results), "Pinned QA source unexpectedly promoted; re-triage"
    assert all(not r["READY"] and not r["LIVE"] for r in results)
    output = {
        "taskId": "MASTER-115-MB21-MB22-NATIVE-SOURCE-ADMISSION-PREFLIGHT-20261107-06",
        "status": "REAL_ORIGINAL_SOURCE_MATCHED__CANONICAL_115_G2_AND_TRUST_PENDING__NO_STUDENT_RELEASE",
        "purpose": "Negative admission inventory; CI SUCCESS DOES NOT imply READY",
        "qaCommit": "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2",
        "sourceAStageCommit": "38ab6b53f75f0da5a6e83087464e962e31430e64",
        "authorCCommit": "e50198cad6821a5252008bd474d8240510832f85",
        "sourceCount": 205, "existingLiveCount": 5, "newReady": 0,
        "newLive": 0, "items": results,
    }
    out = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "115-mb21-mb22-gate-preflight.json"
    out.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    print("READ_ONLY_PREFLIGHT_PASS__RELEASE_HOLD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
