#!/usr/bin/env python3
"""Read-only 128-question draft QA ledger. NEVER grants student release approval."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu" / "teaching-drafts" / "preview-128-20261023"
WEBP = ROOT / "sudu"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    problems = []
    progress = load(BASE / "progress.json")
    official = load(BASE / "official-final-evidence-20261023.json")["questions"]
    items = progress.get("items", [])
    ids = [x.get("questionId") for x in items]
    files = {p.stem for p in BASE.glob("1??-*.json")}
    if len(ids) != 128 or len(set(ids)) != 128 or set(ids) != files or set(ids) != set(official):
        problems.append("Frozen question IDs differ across manifest, files and official evidence")
    if progress.get("scopeTotal") != 128 or progress.get("deploymentForbidden") is not True:
        problems.append("Frozen draft scope or fail-closed release rule was changed")

    image_ok = 0
    checked_visual = 0
    shared_by_path = {}
    pending_teaching = 0
    pending_ui = 0
    disagreement = []
    subjects = Counter()
    sourced_news = set()
    checked_english_lexical = set()
    checked_numeric_reasoning = set()

    def verify_asset(qid, year, relative, sha, kind):
        if not isinstance(relative, str) or not relative.startswith(
            f"data/approved/webp/{year}/"
        ) or not relative.endswith(".webp") or ".." in Path(relative).parts:
            problems.append(f"{qid}: invalid {kind} path")
            return False
        asset = WEBP / relative
        if not asset.is_file() or not isinstance(sha, str) or digest(asset) != sha:
            problems.append(f"{qid}: {kind} original bytes do not match pinned SHA256")
            return False
        return True

    for item in items:
        qid = item.get("questionId")
        if qid not in files:
            continue
        record = load(BASE / f"{qid}.json")
        year = item.get("year")
        subjects[str(item.get("subject"))] += 1
        if record.get("questionId") != qid or record.get("year") != year:
            problems.append(f"{qid}: question/year mismatches manifest")
        if item.get("image") != record.get("image") or item.get("imageSha256") != record.get("imageSha256"):
            problems.append(f"{qid}: pinned image reference changed")
        if verify_asset(qid, year, record.get("image"), record.get("imageSha256"), "single-question WebP"):
            image_ok += 1
        links = record.get("sharedImages") or []
        if links != (item.get("sharedImages") or []):
            problems.append(f"{qid}: shared passage list differs from manifest")
        if record.get("visualReview", {}).get("sharedMaterialsRequired") and not links:
            problems.append(f"{qid}: shared reading passage is required but missing")
        for link in links:
            relative = link.get("image")
            sha = link.get("sha256")
            if verify_asset(qid, year, relative, sha, "shared passage WebP"):
                if relative in shared_by_path and shared_by_path[relative] != sha:
                    problems.append(f"{qid}: shared passage has conflicting pinned digests")
                shared_by_path[relative] = sha
        visual = item.get("supplementalImageQa") or {}
        if str(visual.get("status", "")).startswith("PASS_"):
            checked_visual += 1
            if visual.get("sha256") != record.get("imageSha256"):
                problems.append(f"{qid}: manifest visual QA SHA differs from source")
        if record.get("studentReleaseApproved") is not False or record.get("deploy") is not False:
            problems.append(f"{qid}: draft record release gate improperly enabled")
        answer = official.get(qid, {}).get("officialAnswer")
        comp = record.get("answerComparison", {})
        if not answer or comp.get("officialAnswer") != answer:
            problems.append(f"{qid}: official answer does not match signed evidence registry")
        if record.get("aiAnswer") != answer:
            disagreement.append(qid)
            if not comp.get("conflictWarningRequired"):
                problems.append(f"{qid}: AI/official mismatch lacks visible warning requirement")
        if record.get("subject") == "英文":
            english = record.get("teaching", {}).get("english") or {}
            if not english.get("pronunciationIPA") or not english.get("sentenceTranslationZh"):
                problems.append(f"{qid}: English IPA or full-sentence Chinese translation missing")
            if set((english.get("optionMeaningZh") or {}).keys()) != set("ABCD"):
                problems.append(f"{qid}: four English option meanings missing")
            for level in ("初級", "中級", "高級"):
                if not (english.get("synonyms") or {}).get(level):
                    problems.append(f"{qid}: synonym level {level} missing")
                if not (english.get("antonyms") or {}).get(level):
                    problems.append(f"{qid}: antonym level {level} missing")
            sample = english.get("exampleEnglish") or ""
            surface = english.get("exampleHighlightedSurfaceForm") or ""
            if not sample or not english.get("exampleChinese") or not surface or surface.casefold() not in sample.casefold():
                problems.append(f"{qid}: self-authored English example/translation/highlight incomplete")
            news_url = english.get("newsExampleSourceUrl")
            if news_url:
                sourced_news.add(qid)
                news_sentence = english.get("newsExampleEnglish") or ""
                news_surface = english.get("newsExampleHighlightedSurfaceForm") or ""
                if not str(news_url).startswith("https://") or not news_sentence or not english.get("newsExampleChinese"):
                    problems.append(f"{qid}: source-backed news example or Chinese translation incomplete")
                if not news_surface or news_surface.casefold() not in news_sentence.casefold():
                    problems.append(f"{qid}: sourced news highlight absent from sentence")
                if not english.get("newsExampleSourceDate") or not english.get("newsExampleSourceTitle"):
                    problems.append(f"{qid}: news source publication date or title missing")
                if "PARAPHRASE" not in (english.get("newsExampleStatus") or ""):
                    problems.append(f"{qid}: news must be clearly labeled a paraphrase rather than a direct quote")
            elif "SOURCE_VERIFIED" in (english.get("newsExampleStatus") or ""):
                problems.append(f"{qid}: news falsely labeled source-verified without a URL")

        qa = record.get("qa") or {}
        lexical_review = qa.get("lexicalAndFourOptionReview20261023")
        if lexical_review:
            checked_english_lexical.add(qid)
            if record.get("subject") != "英文":
                problems.append(f"{qid}: English lexical review incorrectly attached to another subject")
            if not lexical_review.get("status", "").startswith("PARTIAL_"):
                problems.append(f"{qid}: partial English review claims unsupported status")
            if lexical_review.get("officialOption") != answer or not lexical_review.get("independentRecheckNotes"):
                problems.append(f"{qid}: English semantic review has missing notes or mismatched official answer")
            if lexical_review.get("releaseApproved") is True or lexical_review.get("studentReleaseApproved") is True:
                problems.append(f"{qid}: partial English review must not approve publication")
        numeric_review = qa.get("sourceLinkedCalculationRecheck20261023")
        if numeric_review:
            checked_numeric_reasoning.add(qid)
            if record.get("subject") != "會計學" or numeric_review.get("officialAnswer") != answer:
                problems.append(f"{qid}: numeric ledger has wrong subject or answer")
            if "PARTIAL" in numeric_review.get("status", "") and numeric_review.get("fullTeachingQA") == "PASS":
                problems.append(f"{qid}: partial numeric review misrepresented as full QA")
            if not numeric_review.get("independentlyRecomputedSteps") or not numeric_review.get("evidenceFile"):
                problems.append(f"{qid}: numeric review lacks actual recomputation evidence")
        pending_teaching += qa.get("independentTeachingReview") != "PASS"
        pending_ui += qa.get("uiReview") != "PASS"

    news_ledger = progress.get("partialEnglishNewsSourceLedger") or {}
    if set(news_ledger.get("questionIds", [])) != sourced_news:
        problems.append("Recorded English sourced-news IDs do not match source-bearing records")
    if news_ledger.get("sourcedExampleCount") != len(sourced_news):
        problems.append("English news-source count differs from verified records")

    lexical_ledger = progress.get("partialEnglishLexicalReviewLedger") or {}
    lexical_ids = lexical_ledger.get("questionIds", [])
    if (len(lexical_ids) != len(set(lexical_ids))
            or set(lexical_ids) != checked_english_lexical
            or lexical_ledger.get("reviewedQuestionCount") != len(checked_english_lexical)):
        problems.append("English partial QA count/IDs inconsistent with per-question evidence")
    numeric_ledger = progress.get("partialTeachingReviewLedger") or {}
    numeric_ids = numeric_ledger.get("reviewedQuestionIds", [])
    if (len(numeric_ids) != len(set(numeric_ids))
            or set(numeric_ids) != checked_numeric_reasoning):
        problems.append("Numeric partial QA ID list inconsistent with per-question evidence")

    binary = progress.get("binaryRecheckedLatest") or {}
    if binary.get("recheckedDistinctQuestions", 0) > checked_visual:
        problems.append("Binary rechecked tally exceeds recorded per-question visual QA")
    if binary.get("notYetRecheckedThisCycle") != 128 - checked_visual:
        problems.append("Binary image remaining tally is not consistent with per-question QA")
    if progress.get("fullyAccepted", 0) > 128 - max(pending_teaching, pending_ui):
        problems.append("Fully accepted tally exceeds completed teaching/UI reviews")
    if progress.get("deployed", 0) > progress.get("fullyAccepted", 0):
        problems.append("Published count exceeds fully accepted draft count")
    if set(disagreement) != set((progress.get("officialFinalEvidence") or {}).get("unresolvedIds", [])):
        problems.append("AI/official disagreement registry is inconsistent")

    report = {
        "kind": "DRAFT_ONLY_INTEGRITY_AND_RELEASE_READINESS",
        "noApprovalGranted": True,
        "scope": len(ids),
        "subjects": dict(sorted(subjects.items())),
        "singleWebpBytesVerified": image_ok,
        "distinctSharedPassagesVerified": len(shared_by_path),
        "visuallyReviewedPerQuestionLedger": checked_visual,
        "officialFinalEvidenceRecorded": progress.get("officialFinalCorrectionVerified"),
        "pendingIndependentTeachingReview": pending_teaching,
        "pendingUiReview": pending_ui,
        "aiOfficialConflicts": disagreement,
        "newsContextExamplesWithSource": len(sourced_news),
        "englishPartialSemanticReviews": len(checked_english_lexical),
        "accountingPartialNumericReviews": len(checked_numeric_reasoning),
        "englishNewsUnverifiedCount": 28 - len(sourced_news),
        "fullyAcceptedPerManifest": progress.get("fullyAccepted"),
        "deployedPerManifest": progress.get("deployed"),
        "errors": problems,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
