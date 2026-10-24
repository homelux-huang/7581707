#!/usr/bin/env python3
"""Read-only 115 economics 34 source admission gap inspection after pre-key commit."""
import hashlib
import importlib.util
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
PUB=ROOT/"current-main/scripts/sudu_verified_publish.py"
QID="115-09-2-34"
spec=importlib.util.spec_from_file_location("formal_publisher",PUB)
pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
bank=pub.read(BASE/"questions.json")["questions"]
q=next(x for x in bank if x["questionId"]==QID)
m=next(x for x in pub.read(BASE/"webp-manifest.json")["items"] if x["questionId"]==QID)
print("SOURCE_ECON34_INFO",json.dumps({
 "questionId":q["questionId"],"paperCode":q.get("paperCode"),"number":q.get("originalQuestionNumber"),
 "subject":q.get("subject"),"question":q.get("question"),"options":q.get("options"),
 "answer":q.get("answer"),"officialFinalAnswer":q.get("officialFinalAnswer"),
 "answerMatched":q.get("answerMatched"),"answerVerified":q.get("answerVerified"),
 "questionVerified":q.get("questionVerified"),"officialCorrectionChecked":q.get("officialCorrectionChecked"),
 "textQaStatus":q.get("textQaStatus"),"reviewStatus":q.get("reviewStatus"),
 "imagePath":m.get("output"),"imageSha256":m.get("sha256"),"imageQaStatus":m.get("qaStatus"),
 "sourcePagePdfSha":q.get("questionProvenance",{}).get("pdfSha256"),
 "officialPdfSha":q.get("answerProvenance",{}).get("pdfSha256"),
 "releaseApproved":q.get("studentReleaseApproved"),"integrationReady":q.get("integrationReady"),
 "questionRevision":pub.text_revision(q,m["sha256"]),
 "availableEvidenceFields":{k:q.get(k) for k in ("textQaEvidence","officialFinalQaEvidence","independentSolve","teachingQaEvidence","uiQaEvidence")},
 "imageProof":pub.image_proof(q,m,{},ROOT),
 "admissionSourceProof":pub.source_proof(q,True,True,pub.text_revision(q,m["sha256"])),
 "certifiedInput":QID in pub.reviewed_student_batches(ROOT,115)
},ensure_ascii=False,sort_keys=True),flush=True)
with sqlite3.connect((BASE/"question-bank.sqlite3").resolve().as_uri()+"?mode=ro",uri=True) as db:
 assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
 p,h=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(QID,)).fetchone()
 assert json.loads(p)==q and hashlib.sha256(p.encode()).hexdigest()==h
print("ECON34_SQLITE_EXACT_ROUNDTRIP_PASS",flush=True)
