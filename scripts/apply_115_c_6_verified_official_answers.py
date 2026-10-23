#!/usr/bin/env python3
"""G3 only: six 115 Chinese TCTE final answers, SHA-bound official source and correction PDF.

No OCR/teaching/questionVerified changes. No modification of original PDFs/WebPs,
main, release flags, user/student records, or LIVE. Only isolated 115 data branch.
"""
import argparse,hashlib,json,sqlite3,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/115")
BRANCH="qa/114-115-official-visual-review"
EVID=BASE/"QA_115_C_6_FINAL_OFFICIAL_ANSWERS_20261023.json"
CONFIRM=BASE/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
A_PDF="ec9871b659d81726de5b6412ed5252d62541afb287951b5d6cf923c1ea763e64"
A_IMG="5422c00920ef4f18fa32fffd51c7edb78acd80aac84974713a61e2a02987126f"
C_PDF="231f21ac52bb1006717ec6a17b325454a37269317a1f49944dbfd0a31d28c4c0"
VALUES={"115-00-C-06":"B","115-00-C-11":"D","115-00-C-12":"C",
        "115-00-C-13":"D","115-00-C-14":"B","115-00-C-15":"B"}
STAGED={"questions.json","official-answer-evidence.json","inventory.json",
        "VALIDATION.json","official-confirmation-status.json"}
def path(p):
    target=(ROOT/p).resolve()
    assert target.is_relative_to(ROOT)
    return target
def get(p):return json.loads(path(p).read_text(encoding="utf8"))
def digest(p):return hashlib.sha256(path(p).read_bytes()).hexdigest()
def idx(rows):
    d={x["questionId"]:x for x in rows}
    assert len(d)==len(rows)
    return d
def correct_answer(q,a):
    v=q.get("answer")
    assert v==a or type(v) is int and 0<=v<=3 and "ABCD"[v]==a, (q["questionId"],v,a)

def run(stage=False):
    if subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()!=BRANCH:
        raise RuntimeError("Refusing to update anything outside isolated QA branch")
    ev=get(EVID);ledger=get(CONFIRM)
    assert ev["year"]==115 and ev["paperCode"]=="00-C" and ev["finalAnswerVerifiedAdded"]==6
    assert not ev["releaseAllowed"] and not ev["integrationReady"] and not ev["independentHumanReview"]
    assert ledger["allPagesInThreeDocumentsReviewed"] and ledger["officialNoticeAnswerConflicts"]==0
    notice={x["paperCode"]:x for x in ledger["docs"]}
    assert {x["paperCode"] for x in ledger["docs"]}=={"00-C","00-E","09-2"}
    assert notice["00-C"]["pdfSha256"]==C_PDF
    assert len(notice["00-C"]["confirmed"])==6
    assert notice["00-C"]["pageCount"]==10
    assert next(x for x in notice["00-C"]["confirmed"] if x["questionId"]=="115-00-C-12")["officialConfirmedAnswer"]=="C"
    records=idx(ev["records"])
    assert set(records)==set(VALUES)
    official_img=BASE.parents[1]/"original/115/00-C-answers/p001-ec9871b659-v2-w1400-q66.webp"
    assert official_img.exists() and hashlib.sha256(official_img.read_bytes()).hexdigest()==A_IMG
    bank=get(BASE/"questions.json")
    ae=get(BASE/"official-answer-evidence.json")
    inv=get(BASE/"inventory.json")
    val=get(BASE/"VALIDATION.json")
    confirmations=get(BASE/"official-confirmation-status.json")
    q=idx(bank["questions"]); answers=idx(ae["items"])
    assert len(q)==len(answers)==205 and set(q)==set(answers)
    assert ae["papers"]["00-C"]["pdfSha256"]==A_PDF
    assert inv["imageVisualQaPass"]==141 and inv["perSubject"]["國文"]["visualQaPass"]==15
    assert inv["officialAnswerIndependentVerified"] in (0,6)
    assert ae["answerVerifiedCount"] in (0,6)
    assert inv["perSubject"]["國文"]["officialAnswerIndependentlyVerified"] in (0,6)
    assert val["stats"]["國文"]["officialAnswerIndependentlyVerified"] in (0,6)
    pending={id for id in VALUES if not q[id].get("answerVerified")}
    if len(pending) not in (0,6):
        raise RuntimeError("Unexpected partial answer approval, manual reconcile needed")
    if bool(pending) != (ae["answerVerifiedCount"]==0):
        raise RuntimeError("Answer evidence summary conflicts with per-question state")
    for id,letter in VALUES.items():
        e=records[id];qrec=q[id];a=answers[id]
        assert e["officialPublishedFinalAnswer"]==e["candidateValue"]==letter
        assert e["officialPublishedAnswerSourcePdfSha256"]==a["officialSourceSha256"]==A_PDF
        assert e["officialPublishedAnswerImageSha256"]==A_IMG
        assert e["officialConfirmationDocumentSha256"]==C_PDF
        assert e["officialCorrectionChecked"] and e["officialFinalAnswerImageDirectVisualChecked"]
        assert e["answerVerified"] and not e["questionVerified"] and not e["integrationReady"]
        assert a["candidateValue"]==a["officialExtractedValue"]==letter and a["answerMatched"]==True
        assert a["sourcePage"]==1 and a["officialSource"]==e["sourceOfficialAnswerUrl"]
        correct_answer(qrec,letter)
        assert qrec["imageQaStatus"]=="PASS"
        assert not qrec.get("questionVerified") and not qrec.get("integrationReady")
        if id not in pending:
            assert a.get("answerVerified") and a.get("officialCorrectionPdfSha256")==C_PDF
            assert qrec.get("answerQaEvidence")==EVID.as_posix()
        else:assert a["answerVerified"] is False
    if not pending or not stage:
        return {"mode":"CHECK" if not stage else "NO_CHANGES","pending":len(pending),
                "answerVerifiedBefore":ae["answerVerifiedCount"],
                "answerVerifiedAfter":ae["answerVerifiedCount"]+len(pending),
                "questionVerifiedAdded":0,"releaseAllowed":False}
    for id,letter in VALUES.items():
        a=answers[id];r=records[id];x=q[id]
        a["answerVerified"]=True
        a["qaStatus"]="PASS_OFFICIAL_FINAL_ANSWER_AND_CORRECTION_PDF"
        a["visualReviewStatus"]="PASS_DIRECT_OFFICIAL_ANSWER_IMAGE"
        a["officialCorrectionStatus"]="REVIEWED_EXPLICIT_CONFIRMATION_Q12_C" if id=="115-00-C-12" else "REVIEWED_FULL_C_PDF_NO_ENTRY_FOR_THIS_ID"
        a["officialCorrectionPdfUrl"]=notice["00-C"]["url"]
        a["officialCorrectionPdfSha256"]=C_PDF
        a["officialCorrectionChecked"]=True
        a["officialAnswerImageSha256"]=A_IMG
        a["officialFinalAnswer"]=letter
        a["qaReviewer"]="ChatGPT assistant"
        a["qaReviewedAt"]="2026-10-23"
        a["qaEvidencePath"]=EVID.as_posix()
        x["answerVerified"]=True
        x["officialFinalAnswer"]=letter
        x["officialCorrectionChecked"]=True
        x["officialAnswerQaStatus"]="PASS_FINAL_TCTE_PUBLISHED_ANSWER_AND_CONFIRMATION"
        x["answerQaEvidence"]=EVID.as_posix()
        x["questionVerified"]=False
        x["integrationReady"]=False
    ae["answerVerifiedCount"]=6
    ae["verificationRule"]="Official PDF/image and official confirmation notice individually SHA-bound for 6 Chinese questions; all others unverified"
    inv["officialAnswerIndependentVerified"]=6
    inv["perSubject"]["國文"]["officialAnswerIndependentlyVerified"]=6
    val["stats"]["國文"]["officialAnswerIndependentlyVerified"]=6
    val["officialAnswers"]="PARTIAL_6_SHA_BOUND_TCTE_FINAL_ANSWERS_ALL_OTHERS_PENDING"
    confirmations["checkedOn"]="2026-10-23"
    confirmations["officialNoticeEvidencePath"]=CONFIRM.as_posix()
    for code in ("00-C","00-E","09-2"):
        confirmations["confirmations"][code]["revisionDocumentContent"]="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED"
        confirmations["confirmations"][code]["revisionDocumentSha256"]=notice[code]["pdfSha256"]
        confirmations["confirmations"][code]["revisionDocumentPages"]=notice[code]["pageCount"]
        confirmations["confirmations"][code]["reviewedAt"]="2026-10-23"
    confirmations["interpretation"]="All TCTE confirmation PDFs for 00-C 00-E 09-2 read; only six source-image-verified Chinese G3 answers promoted. Others remain unverified; no G2/G6 promotion."
    assert inv["imageVisualQaPass"]==141
    assert sum(bool(x.get("answerVerified")) for x in bank["questions"])==6
    assert sum(bool(x.get("answerVerified")) for x in ae["items"])==6
    assert all(not (x.get("questionVerified") or x.get("integrationReady")) for x in bank["questions"])
    if stage:
        db=path(BASE/"question-bank.sqlite3")
        with sqlite3.connect(db) as cx:
            cols={r[1] for r in cx.execute("PRAGMA table_info(questions)")}
            assert {"question_id","payload_sha256"}<=cols
            field="payload" if "payload" in cols else "payload_json"
            assert field in cols
            table_names={r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "student_answers" not in table_names and "student_results" not in table_names
            for id in sorted(VALUES):
                raw=json.dumps(q[id],ensure_ascii=False,sort_keys=True,separators=(",",":"))
                n=cx.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                  (raw,hashlib.sha256(raw.encode("utf8")).hexdigest(),id)).rowcount
                assert n==1
            assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
            for id,raw,d in cx.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
                assert hashlib.sha256(raw.encode("utf8")).hexdigest()==d and json.loads(raw)["questionId"]==id
        for fn,obj in (("questions.json",bank),("official-answer-evidence.json",ae),
                      ("inventory.json",inv),("VALIDATION.json",val),
                      ("official-confirmation-status.json",confirmations)):
            path(BASE/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"mode":"STAGE","answerVerifiedAdded":6,"officialFinalAnswerVerified":6,
            "imageQaRemain":141,"questionVerifiedAdded":0,"releaseAllowed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    args=p.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
