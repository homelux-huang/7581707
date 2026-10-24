#!/usr/bin/env python3
"""Read-only, per-question teaching RELEASE-CANDIDATE gate; never publishes drafts.

A draft's answer match, official key, visual QA or complete fields do NOT grant
student release. An independently reviewed, SHA-pinned teaching+UI certificate
is required for each individual question, separate from draft flags.
"""
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/teaching-drafts/preview-128-20261023"
RWD = ("360x800", "375x812", "390x844", "412x915", "430x932",
       "768x1024", "1024x768", "1440x900")
INTERACTIONS = ("answer_scroll", "memory_dismiss_restore", "single_webp_id",
                "wrong_review_no_selection", "highlight_actual_surface",
                "bottom_nav_no_occlusion", "no_horizontal_overflow")


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def teaching_digest(teaching):
    return sha256_bytes(json.dumps(
        teaching, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8"))


def proof_valid(proof, root):
    if not isinstance(proof, dict):
        return False
    if (proof.get("result") != "PASS" or not isinstance(proof.get("reviewer"), str)
            or len(proof["reviewer"].strip()) < 3):
        return False
    try:
        reviewed = date.fromisoformat(proof["reviewedAt"])
        if reviewed > date.today():
            return False
        rel = proof["path"]
        if not isinstance(rel, str) or rel.startswith("/") or ".." in Path(rel).parts:
            return False
        path = (root / rel).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            return False
        digest = proof.get("sha256")
        return (isinstance(digest, str) and len(digest) == 64
                and sha256_bytes(path.read_bytes()) == digest)
    except (KeyError, TypeError, ValueError, OSError, AttributeError):
        return False


def assess_record(item, record, official, certificate, root=ROOT):
    """Return explicit blockers. No flag mutation, no write, no student data."""
    fail = []
    qid = item.get("questionId")
    if record.get("questionId") != qid or record.get("year") != item.get("year"):
        fail.append("identity_or_year_mismatch")
    if (record.get("image") != item.get("image")
            or record.get("imageSha256") != item.get("imageSha256")):
        fail.append("original_image_pin_mismatch")
    else:
        rel = record.get("image")
        try:
            if (not isinstance(rel, str)
                    or not rel.startswith(f"data/approved/webp/{item['year']}/")
                    or ".." in Path(rel).parts):
                fail.append("invalid_original_image_path")
            elif sha256_bytes((root / "sudu" / rel).read_bytes()) != record.get("imageSha256"):
                fail.append("original_image_bytes_mismatch")
        except (OSError, KeyError, TypeError):
            fail.append("original_image_missing")
    answer = official.get("officialAnswer") if isinstance(official, dict) else None
    comparison = record.get("answerComparison") or {}
    qa = record.get("qa") or {}
    if (answer not in ("A", "B", "C", "D")
            or comparison.get("officialAnswer") != answer
            or comparison.get("officialFinalCorrectionVerified") is not True
            or (qa.get("officialFinalEvidence") or {}).get("officialFinalCorrectionVerified") is not True):
        fail.append("official_final_evidence_pending")
    # Separate literal wrong AI conclusions from the three historical
    # first-pass differences that were corrected only after seeing the key.
    # A non-boolean warning value is NOT proof of an independent clean solve.
    if record.get("aiAnswer") != answer:
        fail.append("ai_literal_official_disagreement")
    elif comparison.get("conflictWarningRequired") is not False:
        fail.append("historic_disagreement_or_unresolved_warning")
    if record.get("studentReleaseApproved") is not False or record.get("deploy") is not False:
        fail.append("draft_release_isolation_modified")
    teaching = record.get("teaching") or {}
    options = teaching.get("optionExplanations") or {}
    if (set(options) != set("ABCD") or
            any(not isinstance(options[k], dict)
                or not options[k].get("teacher")
                or not options[k].get("elementary") for k in "ABCD") or
            [k for k in "ABCD" if options[k].get("isCorrect") is True] != [answer]):
        fail.append("four_option_content_or_answer_mismatch")
    if teaching.get("hasExamCalculation") is True:
        calc = teaching.get("examCalculation") or {}
        if not calc.get("substitutionAndSteps") or not calc.get("result"):
            fail.append("calculation_working_missing")
    if qa.get("independentTeachingReview") != "PASS":
        fail.append("teaching_review_pending")
    if qa.get("uiReview") != "PASS" or qa.get("textHighlightRendering") != "PASS":
        fail.append("ui_or_highlight_review_pending")
    if not isinstance(certificate, dict):
        fail.append("release_certificate_absent")
        return fail
    if (certificate.get("questionId") != qid
            or certificate.get("status") != "QA_APPROVED"
            or certificate.get("releaseApproved") is not True
            or certificate.get("officialAnswer") != answer
            or certificate.get("originalImageSha256") != record.get("imageSha256")
            or certificate.get("teachingDigestSha256") != teaching_digest(teaching)):
        fail.append("release_certificate_not_bound_to_question_content")
    teaching_proof = certificate.get("teachingReviewEvidence")
    ui_proof = certificate.get("uiReviewEvidence")
    if not proof_valid(teaching_proof, root) or not proof_valid(ui_proof, root):
        fail.append("review_evidence_not_sha_verified")
    elif (teaching_proof["path"] == ui_proof["path"]
          or teaching_proof["sha256"] == ui_proof["sha256"]):
        # A single generic PASS file cannot serve as both independent teaching
        # content review and real V4 UI/browser interaction evidence.
        fail.append("teaching_and_ui_evidence_not_independent")
    viewports = certificate.get("rwdResults") or {}
    if any((viewports.get(theme) or {}).get(dim) != "PASS"
           for theme in ("light", "dark") for dim in RWD):
        fail.append("eight_viewports_or_theme_qa_pending")
    checks = certificate.get("interactionChecks") or {}
    if any(checks.get(name) is not True for name in INTERACTIONS):
        fail.append("student_interactions_qa_pending")
    if certificate.get("textbookUnknownClearlyLabeled") is not True:
        fail.append("textbook_provenance_disclosure_pending")
    return fail


def main():
    progress = json.loads((BASE / "progress.json").read_text(encoding="utf-8"))
    official = json.loads((BASE / "official-final-evidence-20261023.json").read_text(encoding="utf-8"))["questions"]
    ledger_file = BASE / "release-certificates-128.json"
    registry = json.loads(ledger_file.read_text(encoding="utf-8")) if ledger_file.exists() else {"certificates": {}}
    certs = registry.get("certificates") or {}
    items = progress.get("items") or []
    ids = [x.get("questionId") for x in items]
    if (len(ids) != 128 or len(set(ids)) != 128 or set(ids) != set(official)
            or progress.get("scopeTotal") != 128):
        raise SystemExit("Invalid frozen 128 registry; NO RELEASE")
    counts = Counter()
    blocker_ids = {}
    accepted = []
    for item in items:
        qid = item["questionId"]
        record = json.loads((BASE / (qid + ".json")).read_text(encoding="utf-8"))
        reasons = assess_record(item, record, official[qid], certs.get(qid))
        if reasons:
            counts.update(reasons)
            for reason in reasons:
                blocker_ids.setdefault(reason, []).append(qid)
        else:
            accepted.append(qid)
    if progress.get("fullyAccepted", 0) < len(accepted):
        raise SystemExit("Manifest approval count smaller than verified release candidates; NO RELEASE")
    result = {
        "scope": 128,
        "releaseEligibleCount": len(accepted),
        "releaseEligibleQuestionIds": accepted,
        "blockedCount": 128 - len(accepted),
        "blockerCounts": dict(sorted(counts.items())),
        "answerDisagreementIds": {
            key: sorted(blocker_ids.get(key, []))
            for key in ("ai_literal_official_disagreement",
                        "historic_disagreement_or_unresolved_warning")
        },
        "doesNotChangeAnyDraftOrApprovedData": True,
        "meaning": "Dry-run eligibility only, not automatic publication or full teaching QA"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
