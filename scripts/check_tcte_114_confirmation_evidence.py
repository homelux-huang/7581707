"""Fail-closed, READ-ONLY integrity check for 114 TCTE confirmation evidence.

This is NOT a year-114 publisher admission gate. Matching a PDF-text
candidate does not make an answer independently visually verified.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "sudu/data/processed/114"
LEDGER_FILE = "QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
STATUS_FILE = "official-confirmation-status.json"
LEDGER_REL = f"sudu/data/processed/114/{LEDGER_FILE}"
EXPECTED = {"00-C":4, "00-E":1, "09-1":9, "09-2":4}
SHA = re.compile(r"^[0-9a-f]{64}$")


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def valid(status, ledger, official_evidence, questions):
    problems = []
    def need(value, message):
        if not value:
            problems.append(message)
    need(ledger.get("schemaVersion") == 1 and ledger.get("year") == 114, "ledger year/schema")
    need(status.get("year") == 114 and status.get("schemaVersion") == 1, "status year/schema")
    need(ledger.get("sourceIndexUrl") == status.get("source"), "source index URL mismatch")
    need(ledger.get("sourceIndexUrl") == "https://web1.tcte.edu.tw/EXAM/114_4y/", "wrong official host/year")
    need(status.get("officialNoticeEvidencePath") == LEDGER_REL, "not SHA ledger path")
    need(ledger.get("sourceIndexSha256") == status.get("sourceIndexSha256"), "index SHA mismatch")
    need(SHA.fullmatch(str(ledger.get("sourceIndexSha256"))) is not None, "index SHA malformed")
    need(ledger.get("allPagesInFourDocumentsReviewed") is True, "all pages not reviewed")
    need(ledger.get("officialConfirmationNamedQuestionCount") == 18, "named count")
    need(ledger.get("releaseApproved") is False, "ledger claims approval")
    need(ledger.get("independentFinalAnswerImageQa") is False, "ledger claims answer image QA")
    need(ledger.get("independentHumanReview") is False, "human claim")
    need(status.get("reviewLimits", {}).get("studentQaApprovedNewQuestions") == 0, "approval count")
    need(status.get("reviewLimits", {}).get("perQuestionReleaseApproved") is False, "release flag")
    need(status.get("reviewLimits", {}).get("yearSpecificPublisherGateReady") is False,
         "source notice accidentally claims publisher gate")
    need(official_evidence.get("answerVerifiedCount") == 0, "independent official answer count")
    need(official_evidence.get("reviewStatus") == "PDF_TEXT_ONLY_NOT_INDEPENDENT_VISUAL_VERIFICATION",
         "answer evidence improperly upgraded")
    docs=ledger.get("docs", [])
    need(isinstance(docs, list) and len(docs) == 4, "four official PDFs required")
    by_paper={}
    seen=set()
    answer_ev={q.get("questionId"):q for q in official_evidence.get("items", [])}
    originals={q.get("questionId"):q for q in questions.get("questions", [])}
    for d in docs if isinstance(docs,list) else []:
        paper=d.get("paperCode")
        if paper in by_paper:
            problems.append("duplicate official paper " + str(paper))
            continue
        by_paper[paper]=d
        if paper not in EXPECTED:
            problems.append("unexpected paper " + str(paper))
            continue
        count=EXPECTED[paper]
        rows=d.get("confirmed")
        record=(status.get("confirmations") or {}).get(paper, {})
        need(d.get("pageCount") and isinstance(d.get("pageCount"),int), f"{paper} page count")
        need(d.get("noticeScopeOnly") is True and d.get("allPagesVisuallyReviewed") is True,
             f"{paper} not confirmed scope")
        need(SHA.fullmatch(str(d.get("pdfSha256"))) is not None, f"{paper} invalid SHA")
        need(record.get("revisionDocumentSha256") == d.get("pdfSha256"),
             f"{paper} SHA mismatch")
        need(record.get("revisionDocumentPages") == d.get("pageCount"),
             f"{paper} pages mismatch")
        need(record.get("revisionDocumentContent") == "SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED",
             f"{paper} incomplete PDF review")
        need(record.get("perQuestionReleaseCertified") is False, f"{paper} approval escalated")
        need(record.get("officialStatus") == "question_or_answer_confirmation_document_exists",
             f"{paper} incorrectly says no objection")
        need(d.get("url", "").startswith("https://web1.tcte.edu.tw/EXAM/114_4y/downloader.php?obj="),
             f"{paper} incorrect source URL")
        need(isinstance(rows,list) and len(rows) == count, f"{paper} expected {count} named questions")
        ids=[]
        for row in rows if isinstance(rows,list) else []:
            qid=row.get("questionId")
            ids.append(qid)
            if qid in seen:
                problems.append("duplicate question ID " + str(qid))
            seen.add(qid)
            need(bool(re.fullmatch(f"114-{re.escape(paper)}-[0-9]{{2}}",str(qid))), f"{qid} bad ID")
            need(row.get("officialConfirmedAnswer") in "ABCD", f"{qid} non-ABCD answer")
            pages=row.get("pdfPageNumbers")
            need(isinstance(pages,list) and len(pages)>0 and all(
                isinstance(p,int) and 1<=p<=d.get("pageCount",0) for p in pages),
                f"{qid} missing page refs")
            ev=answer_ev.get(qid,{})
            q=originals.get(qid,{})
            need(row.get("comparedToExistingOfficialPdfTextCandidate")=="MATCHED",
                 f"{qid} missing text-only comparison")
            need(row.get("publishedFinalAnswerImageIndependentlyVerified") is False,
                 f"{qid} false independent final-answer claim")
            need(ev.get("officialPdfExtractedCandidate")==row.get("officialConfirmedAnswer")
                 and q.get("answer")==row.get("officialConfirmedAnswer"),
                 f"{qid} differs from unverified candidate")
            need(ev.get("answerVerified") is False, f"{qid} answer QA incorrectly upgraded")
        need(record.get("confirmedQuestionIds") == ids, f"{paper} ID list differs")
    need(set(by_paper)==set(EXPECTED), "missing or extra confirmation papers")
    math_b=(status.get("confirmations") or {}).get("00-MB",{})
    need(math_b.get("officialStatus")=="no_objection_submitted", "MathB notice wrong")
    need(math_b.get("revisionDocumentContent")=="not_applicable", "MathB invented PDF")
    need(math_b.get("perQuestionReleaseCertified") is False, "MathB approval escalated")
    need(len(seen)==18, "not 18 distinct named questions")
    return problems


def main():
    status=load(STATUS_FILE)
    ledger=load(LEDGER_FILE)
    official=load("official-answer-evidence.json")
    questions=load("questions.json")
    errors=valid(status,ledger,official,questions)
    assert errors==[], "evidence integrity: "+repr(errors)
    for mutation,label in (
        ({"officialConfirmationNamedQuestionCount":17}, "wrong count"),
        ({"releaseApproved":True}, "approval bypass"),
        ({"independentFinalAnswerImageQa":True}, "false image QA")
    ):
        bad=copy.deepcopy(ledger)
        bad.update(mutation)
        assert valid(status,bad,official,questions), "bad ledger passed: "+label
    bad=copy.deepcopy(ledger)
    bad["docs"][0]["pdfSha256"]="0"*64
    assert valid(status,bad,official,questions), "bad source SHA passed"
    bad=copy.deepcopy(ledger)
    bad["docs"][0]["confirmed"][0]["officialConfirmedAnswer"]="D"
    assert valid(status,bad,official,questions), "incorrect notice answer passed"
    bad=copy.deepcopy(status)
    bad["confirmations"]["09-2"]["officialStatus"]="no_objection_submitted"
    assert valid(bad,ledger,official,questions), "false paper no-objection passed"
    print("PASS: 114 official notice scope 4 PDFs / 19 pages / 18 IDs, "
          "18 exact matches to UNVERIFIED official PDF-text candidates; "
          "six fail-closed negative cases; ZERO approvals/deploys")


if __name__=="__main__":
    main()
