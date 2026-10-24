#!/usr/bin/env python3
"""Repair 114 five official answer-PDF text-parser gaps from existing direct image evidence.
This is a preliminary image match, NOT confirmation of official revisions.
No original years JSON, main, student data, deployment or other year is touched.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"sudu/data/processed/114"
REPORT=ROOT/"sudu/data/QA_114_115_OFFICIAL_ANSWER_VISUAL_2026-10-22.json"
IDS={
  "114-00-C-15":"B",
  "114-00-E-15":"A",
  "114-00-MB-15":"C",
  "114-09-1-15":"C",
  "114-09-2-15":"A"
}

def read(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p,j): p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def hashbytes(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
  qa=read(REPORT)
  visual={x["questionId"]:x for x in qa["results"] if x["questionId"] in IDS}
  assert set(visual)==set(IDS)
  qpath=DIR/"questions.json"
  apath=DIR/"official-answer-evidence.json"
  ipath=DIR/"inventory.json"
  questions=read(qpath)
  answers=read(apath)
  inventory=read(ipath)
  qmap={q["questionId"]:q for q in questions["questions"]}
  amap={a["questionId"]:a for a in answers["items"]}
  assert set(IDS).issubset(qmap) and set(IDS).issubset(amap)
  evidence=[]
  for qid, letter in IDS.items():
    v=visual[qid]
    assert v["officialVisualAnswer"]==letter
    assert v["candidateAnswer"]==letter
    assert v["officialImageVisualCheck"]=="PASS"
    assert v["officialPdfSha256"]==amap[qid]["officialPdfSha256"]
    assert v["priorPdfTextExtractedAnswer"] is None
    glob=list((ROOT/v["officialAnswerPagePath"]).glob("p001-*-v2-w1400-q66.webp"))
    assert len(glob)==1, (qid,glob)
    image_path=glob[0]
    with Image.open(image_path) as im:
      im.load()
      assert im.format=="WEBP"
    q=qmap[qid]
    a=amap[qid]
    if q["answer"] not in (None,letter):
      raise ValueError("Existing answer differs from official image: "+qid)
    if a["officialPdfExtractedCandidate"] not in (None, letter):
      raise ValueError("Official PDF text conflicts: "+qid)
    q["answer"]=letter
    q["answerMatched"]=True
    q["answerVerified"]=False
    q["questionVerified"]=False
    q["reviewStatus"]="needs_review"
    q["answerProvenance"]["extractMethod"]="direct_official_answer_page_visual_with_original_pdf_text_gap"
    q["answerProvenance"]["officialImageVisualCandidate"]=letter
    q["answerProvenance"]["officialAnswerPageWebp"]=image_path.relative_to(ROOT).as_posix()
    q["answerProvenance"]["officialAnswerPageWebpSha256"]=hashbytes(image_path)
    q["answerProvenance"]["independentVisualVerification"]=False
    q["answerProvenance"]["officialCorrectionsChecked"]=False
    a["comparison"]="MATCHED_OFFICIAL_IMAGE_PRELIMINARY"
    a["answerMatched"]=True
    a["answerVerified"]=False
    a["officialImageVisualCandidate"]=letter
    a["officialAnswerPdfPage"]=1
    a["officialAnswerPageWebp"]=image_path.relative_to(ROOT).as_posix()
    a["officialAnswerPageWebpSha256"]=hashbytes(image_path)
    a["independentVisualAnswerReview"]="ASSISTANT_DIRECT_COMPARISON_ONLY_FINAL_CORRECTIONS_PENDING"
    evidence.append({
      "questionId":qid,
      "originalPdfTextExtractedAnswer":None,
      "officialImageVisualAnswer":letter,
      "officialAnswerPageWebp":image_path.relative_to(ROOT).as_posix(),
      "officialAnswerPageWebpSha256":hashbytes(image_path),
      "officialAnswerPdfSha256":a["officialPdfSha256"],
      "officialFinalCorrectionChecked":False,
      "answerMatched":True,
      "answerVerified":False
    })
  assert len(questions["questions"])==len(answers["items"])==205
  assert sum(bool(x["answerMatched"]) for x in questions["questions"])==205
  assert not any(x["answerVerified"] for x in questions["questions"])
  save(qpath,questions)
  save(apath,answers)
  inventory["answerTextMatched"]=200
  inventory["answerOfficialImageMatchedWithoutPdfText"]=5
  inventory["answerCandidatesMatchedAcrossTextAndImage"]=205
  inventory["answerUnmatchedIds"]=[]
  inventory["answerIndependentlyVerified"]=0
  inventory["officialCorrectionQaComplete"]=False
  save(ipath,inventory)
  db=DIR/"question-bank.sqlite3"
  with sqlite3.connect(db) as conn:
    for qid in IDS:
      q=qmap[qid]
      raw=json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(",",":"))
      digest=hashlib.sha256(raw.encode()).hexdigest()
      cur=conn.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                       (raw,digest,qid))
      assert cur.rowcount==1
    conn.commit()
    assert conn.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    rows=conn.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    assert len(rows)==205
    for qid,raw,digest in rows:
      assert hashlib.sha256(raw.encode()).hexdigest()==digest
      assert json.loads(raw)["questionId"]==qid
  save(DIR/"114-ANSWER-15-IMAGE-EVIDENCE.json",
       {"year":114,"status":"FIVE_IMAGE_MATCHES_NOT_FINAL_OFFICIAL_VERIFICATION",
        "sourceReport":REPORT.relative_to(ROOT).as_posix(),"items":evidence})
  print(json.dumps({"repairedTextParserGaps":5,"answerCandidateMatchedNow":205,
       "finalAnswersVerified":0,"sqlite":205,"noDeployment":True},ensure_ascii=False))

if __name__=="__main__":
  main()
