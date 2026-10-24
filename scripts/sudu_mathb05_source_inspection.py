#!/usr/bin/env python3
"""Read-only MB05 actual canonical source and pinned WebP observation (NO RELEASE)."""
import base64
import hashlib
import importlib.util
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT / "current-qa-source"
PUBLISHER=ROOT / "current-main"
OUT=ROOT / "mb05-inspect"
OUT.mkdir(exist_ok=True)
src=SOURCE/"sudu/data/processed/115"
qid="115-00-MB-05"
spec=importlib.util.spec_from_file_location("sudu_verified_publish",(PUBLISHER/"scripts/sudu_verified_publish.py"))
pub=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)
bank=json.loads((src/"questions.json").read_text(encoding="utf-8"))
q=next(x for x in bank["questions"] if x["questionId"]==qid)
m=json.loads((src/"webp-manifest.json").read_text(encoding="utf-8"))
item=next(x for x in m["items"] if x["questionId"]==qid)
s=pub.reviewed_student_batches(SOURCE,115)
revision=pub.text_revision(q,item["sha256"])
original=SOURCE/item["output"]
payload=original.read_bytes()
assert hashlib.sha256(payload).hexdigest()==item["sha256"],"original SHA mismatch"
with sqlite3.connect((src/"question-bank.sqlite3").resolve().as_uri()+"?mode=ro",uri=True) as db:
 row=db.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(qid,)).fetchone()
assert row and hashlib.sha256(row[0].encode()).hexdigest()==row[1],"SQLite checksum"
assert json.loads(row[0])==q,"canonical DB mismatch"
blindpath=src/"review-evidence/115-00-MB-05-blind-original-20261024.json"
blind=json.loads(blindpath.read_text(encoding="utf-8"))
corrected=json.loads((src/"review-evidence/115-00-MB-05-source-text-applied-20261024.json").read_text(encoding="utf-8"))
assert q["question"]==corrected["correctedText"]["question"]
assert q["options"]==corrected["correctedText"]["options"]
assert q["question"]==blind["sourceQuestionTranscriptionFromImage"]
assert q["options"]==blind["sourceOptionsFromImage"]
assert item["sha256"]==blind["webpSha256"]==corrected["singleQuestionWebpSha256"]
note={
 "sourceCommit":subprocess.check_output(["git","-C",str(SOURCE),"rev-parse","HEAD"],text=True).strip(),
 "publisherCommit":subprocess.check_output(["git","-C",str(PUBLISHER),"rev-parse","HEAD"],text=True).strip(),
 "qid":qid,"questionRevision":revision,"question":q["question"],"options":q["options"],
 "answerMatched":q.get("answerMatched"),"officialAnswerCandidate":q.get("answer"),
 "sourceImageSha256":item["sha256"],
 "imageQaStatus":item.get("qaStatus"),
 "currentAlreadyCertified":qid in s,
 "imageProof":pub.image_proof(q,item,{},SOURCE),
 "sourceProof":pub.source_proof(q,True,True,revision),
 "blindMatchedIfOriginalHistoryAccepted":blind.get("answer")==q.get("answer"),
 "blindGitOriginalCommit":"cf6a4efede233b0e447d52498209adf1b721c13e",
 "sourceProvenance":q.get("questionProvenance"),
 "answerProvenance":q.get("answerProvenance"),
 "presentEvidenceFields":{k:q.get(k) for k in ("textQaEvidence","officialFinalQaEvidence","independentSolve","teachingQaEvidence","uiQaEvidence")},
 "sourceQuestionHash":hashlib.sha256(json.dumps({"question":q.get("question"),"options":q.get("options"),"singleQuestionWebpSha256":item["sha256"]},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
}
print("MB05_SOURCE_INSPECTION_JSON_START",flush=True)
print(json.dumps(note,ensure_ascii=False,sort_keys=True),flush=True)
print("MB05_SOURCE_INSPECTION_JSON_END",flush=True)
(OUT/"source-summary.json").write_text(json.dumps(note,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"MB05_VISUAL_BEGIN|{qid}|{item['sha256']}|{len(payload)}",flush=True)
encoded=base64.b64encode(payload).decode("ascii")
for part,offset in enumerate(range(0,len(encoded),1600)):
 print(f"MB05_VISUAL_PART|{part:04d}|{encoded[offset:offset+1600]}",flush=True)
print(f"MB05_VISUAL_END|{len(encoded)}",flush=True)
