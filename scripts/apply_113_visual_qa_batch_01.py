#!/usr/bin/env python3
"""Apply five actually displayed and visually compared 113 Chinese source/crop records.
Only records exact hashes matching the reviewed images. No answer QA promotion.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
from PIL import Image

R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/113"
E=D/"VISUAL_QA_BATCH_01_2026-10-22.json"

def load(name):return json.loads((D/name).read_text(encoding="utf-8"))
def write(name,obj):(D/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
  evidence=json.loads(E.read_text("utf-8"))
  assert evidence["reviewer"]=="ChatGPT assistant"
  assert evidence["independentHumanReview"] is False
  checks={x["questionId"]:x for x in evidence["records"]}
  assert set(checks)=={f"113-00-C-{n:02d}" for n in range(1,6)}
  src=R/evidence["sourcePage"]
  assert sha(src)==evidence["sourceSha256"]
  images=load("webp-manifest.json")
  corpus=load("questions.json")
  visual=load("VISUAL_QA.json")
  inv=load("inventory.json")
  validation=load("VALIDATION.json")
  release=load("release-manifest.json")
  m={x["questionId"]:x for x in images["items"]}
  q={x["questionId"]:x for x in corpus["questions"]}
  v={x["questionId"]:x for x in visual["items"]}
  for qid,rec in checks.items():
    entry=m[qid]
    assert entry["source"]==evidence["sourcePage"]
    assert entry["sourcePageWebpSha256"]==evidence["sourceSha256"]
    assert entry["cropPixels"]==rec["cropPixels"]
    assert entry["outputSha256"]==rec["reviewedSha256"]
    assert entry["output"]==rec["webpPath"]
    assert sha(R/entry["output"])==rec["reviewedSha256"]
    with Image.open(R/entry["output"]) as im:
      im.load()
      assert im.format=="WEBP" and list(im.size)==entry["outputSize"]
    assert all(rec["criteria"].values())
    entry["qaStatus"]="PASS"
    entry["visualReviewEvidence"]={
      "reference":E.relative_to(R).as_posix(),
      "reviewedSha256":rec["reviewedSha256"],
      "reviewer":evidence["reviewer"],"method":evidence["method"],
      "date":evidence["reviewedOn"],"independentHumanReview":False,
      "note":rec["note"]}
    q[qid]["imageQaStatus"]="PASS"
    q[qid]["assets"]["imageQaEvidence"]=E.relative_to(R).as_posix()
    q[qid]["reviewStatus"]="needs_review"
    q[qid]["questionVerified"]=False
    q[qid]["answerVerified"]=False
    q[qid]["integrationReady"]=False
    v[qid]["status"]="PASS"
    v[qid]["reviewer"]=evidence["reviewer"]
    v[qid]["visualEvidence"]=E.relative_to(R).as_posix()
    v[qid]["reviewedWebpSha256"]=rec["reviewedSha256"]
  total=sum(x["qaStatus"]=="PASS" for x in images["items"])
  assert total==len(checks)==5
  visual["passCount"]=total
  inv["visualQaPass"]=total
  validation["imageVisualQaPass"]=total
  validation["releaseAllowed"]=False
  validation["integrationReady"]=False
  release["imageQA"]="PARTIAL_5_OF_205"
  release["releaseAllowed"]=False
  release["integrationReady"]=False
  write("webp-manifest.json",images)
  write("questions.json",corpus)
  write("VISUAL_QA.json",visual)
  write("inventory.json",inv)
  write("VALIDATION.json",validation)
  write("release-manifest.json",release)
  with sqlite3.connect(D/"question-bank.sqlite3") as cx:
    for qid in checks:
      raw=json.dumps(q[qid],ensure_ascii=False,sort_keys=True,separators=(",",":"))
      hx=hashlib.sha256(raw.encode()).hexdigest()
      assert cx.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                         (raw,hx,qid)).rowcount==1
    cx.commit()
    rows=cx.execute("SELECT question_id,payload,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205
    for qid,raw,hx in rows:
      assert hashlib.sha256(raw.encode()).hexdigest()==hx
      assert json.loads(raw)["questionId"]==qid
    assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
  print("113 direct visual image QA pass 5/205; answer verification 0; released NO")

if __name__=="__main__":
  main()
