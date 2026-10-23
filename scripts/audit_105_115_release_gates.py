#!/usr/bin/env python3
"""Read-only release eligibility gate for 105-115 TCTE corpus.

CI intentionally passes when a year is NOT ready, while writing explicit blockers.
--require-ready changes the exit status to failure if even one year remains blocked.
Never rewrites QA flags or student records.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"sudu/data/processed"

def audit(year):
    base=D/str(year)
    report={"year":year,"integrationReady":False,"gates":{},"blockers":[]}
    def load(name):
        p=base/name
        if not p.is_file():
            report["blockers"].append("missing:"+name)
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    inv=load("inventory.json")
    manifest=load("webp-manifest.json")
    bank=load("questions.json")
    answer=load("official-answer-evidence.json")
    if not inv or not manifest or not bank or not answer:
        return report
    qs=bank.get("questions",[])
    ids=[x.get("questionId") for x in qs]
    n=len(ids)
    if n==0 or len(set(ids))!=n:
        report["blockers"].append("invalid_unique_question_inventory")
    images={x.get("questionId"):x for x in manifest.get("items",[])}
    if len(images)!=n or set(ids)!=set(images):
        report["blockers"].append("image_manifest_mismatch")
    image_pass=[]
    for qid in ids:
        x=images.get(qid,{})
        evidence=x.get("visualReviewEvidence") or {}
        if not isinstance(evidence,dict): evidence={}
        output_sha=x.get("sha256") or x.get("outputSha256")
        if x.get("qaStatus")=="PASS" and output_sha and evidence.get("reviewedSha256")==output_sha and evidence.get("reference"):
            image_pass.append(qid)
    pending=sorted(set(ids)-set(image_pass))
    if pending: report["blockers"].append("image_visual_qa_pending:"+str(len(pending)))
    qa_answers=sum(q.get("answerVerified") is True for q in qs)
    qa_questions=sum(q.get("questionVerified") is True for q in qs)
    if any(q.get("integrationReady") is not True for q in qs):
        report["blockers"].append("question_level_integration_not_ready")
    if qa_answers!=n:report["blockers"].append("official_final_answer_qa_pending:"+str(n-qa_answers))
    if qa_questions!=n:report["blockers"].append("question_text_qa_pending:"+str(n-qa_questions))
    shared=manifest.get("sharedMaterialCrops",[])
    shared_pending=[s.get("sharedMaterialId") for s in shared if s.get("qaStatus")!="PASS"]
    if shared_pending:report["blockers"].append("shared_material_qa_pending:"+str(len(shared_pending)))
    if inv.get("integrationReady") is not True:report["blockers"].append("inventory_not_release_ready")
    identities=[(q.get("year"),q.get("paperCode"),q.get("originalQuestionNumber")) for q in qs]
    if any(y is None or not p or number is None for y,p,number in identities):
        report["blockers"].append("missing_canonical_question_identity")
    if len(set(identities))!=n:
        report["blockers"].append("duplicate_canonical_question_identity")
    # G0-G6 evidence artifacts are mandatory even when the manifest says ready.
    # File existence is a necessary condition, never sufficient for QA PASS.
    for required in ("ocr-raw-candidates.json", "VISUAL_QA.json",
                     "question-bank.sqlite3", "REMAINING_QA.md", "DATA_HANDOFF.md"):
        if not (base/required).is_file():
            report["blockers"].append("missing:"+required)
    # Verify basic SQLite integrity without writing to any database.
    dbfile=base/"question-bank.sqlite3"
    if dbfile.is_file():
        import sqlite3
        try:
            with sqlite3.connect("file:"+str(dbfile)+"?mode=ro", uri=True) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                    report["blockers"].append("sqlite_integrity_failure")
                dbrows=db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
                if dbrows!=n:
                    report["blockers"].append("sqlite_question_count_mismatch")
        except (sqlite3.DatabaseError, OSError) as exc:
            report["blockers"].append("sqlite_unreadable:"+type(exc).__name__)
    # G5: a passing SQLite integrity check is not a two-pass import test.
    # Require separately recorded idempotent import and SHA comparison evidence.
    db_evidence=inv.get("sqlite") if isinstance(inv.get("sqlite"),dict) else {}
    if not isinstance(db_evidence.get("reimportCount"),int) or db_evidence["reimportCount"]<2:
        report["blockers"].append("sqlite_idempotent_reimport_not_evidenced")
    if db_evidence.get("shaMismatches") not in ([],0):
        report["blockers"].append("sqlite_sha_mismatch_or_unverified")
    validation=load("VALIDATION.json")
    if validation and validation.get("integrationReady") is not True:
        report["blockers"].append("validation_not_release_ready")
    release=load("release-manifest.json")
    if release and release.get("integrationReady") is not True:
        report["blockers"].append("release_manifest_not_release_ready")
    report.update({"candidateQuestions":n,"webpVisualPass":len(image_pass),
                   "pendingImageIds":pending,"answerVerified":qa_answers,
                   "questionVerified":qa_questions,"sharedMaterialsPending":shared_pending,
                   "integrationReady":not report["blockers"]})
    report["gates"]={"webp":len(image_pass)==n,"answer":qa_answers==n,
                       "text":qa_questions==n,"shared":not shared_pending,
                       "databaseAndRelease":not any(s.startswith(("missing:","inventory_","validation_","release_manifest_","sqlite_")) for s in report["blockers"])}
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--require-ready",action="store_true")
    args=p.parse_args()
    records=[audit(year) for year in range(105,116)]
    total=sum(x.get("candidateQuestions",0) for x in records)
    done=sum(x.get("webpVisualPass",0) for x in records)
    summary={"scope":"105-115","readOnly":True,"candidateQuestions":total,
             "imageVisualQaPass":done,"imageVisualQaPending":total-done,
             "yearsReady":sum(x["integrationReady"] for x in records),
             "allYearsReady":all(x["integrationReady"] for x in records),
             "years":records}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if args.require_ready and not summary["allYearsReady"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
