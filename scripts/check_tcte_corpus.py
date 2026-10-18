#!/usr/bin/env python3
"""Smoke audit of generated TCTE student data. Incomplete OCR is reported, never silently passed as complete."""
import json,collections,sys,re
from pathlib import Path
P=Path("sudu/data/years")
errors=[];summary=[]
for y in range(90,116):
    path=P/(str(y)+".json")
    if not path.exists():summary.append((y,0,0,"NO_FILE"));continue
    try:obj=json.loads(path.read_text("utf8"))
    except Exception as exc:errors.append(f"{y} malformed JSON: {exc}");continue
    if obj.get("year")!=y:errors.append(f"{y} year mismatch")
    seen=set();total=matched=reviewed=0
    for paper in obj.get("papers",[]):
        codes=set()
        for q in paper.get("questions",[]):
            id=q.get("id")
            if id in seen:errors.append(f"{y} repeated id {id}")
            seen.add(id);total+=1
            if q.get("official") is not True:errors.append(f"{y} unofficial entry in official corpus {id}")
            url=q.get("source","")
            if not url.startswith("https://web1.tcte.edu.tw/EXAM/"):errors.append(f"{id} untrusted source URL")
            opts=q.get("options") or []
            if q.get("answerVerified"):
                matched+=1
                if len(opts)!=4 or not all(isinstance(x,str) and x.strip() for x in opts):errors.append(f"{id} flagged answer verified but missing options")
                if q.get("answer") not in range(4):errors.append(f"{id} verified answer not A-D index")
                if "OCR_missing_question" in q.get("issues",[]):errors.append(f"{id} false answerVerified on OCR placeholder")
            if q.get("teachingVerified"):
                reviewed+=1
                for f in ["explanation","principle","steps","extension","wrongOptions","practice","textbook","source"]:
                    if not q.get(f):errors.append(f"{id} teaching published missing {f}")
                if not isinstance(q.get("textbook"),dict) or not q.get("textbook",{}).get("chapter"):errors.append(f"{id} teaching marked verified but textbook chapter missing")
            if q.get("number") in codes:errors.append(f"{id} duplicated question number in paper")
            codes.add(q.get("number"))
        exp=paper.get("expectedCount")
        if exp and paper.get("complete") and (len(codes)!=exp or any(not q.get("teachingVerified") for q in paper.get("questions",[]))):
            errors.append(f"{y}-{paper.get('paper')} FALSE_COMPLETE")
    summary.append((y,total,matched,reviewed))
for row in summary:print("AUDIT_YEAR",*row)
print("AUDIT_TOTAL",len(summary),"year entries,",sum(r[1] for r in summary),"question records")
for err in errors:print("ERROR",err)
if errors:sys.exit(1)
