#!/usr/bin/env python3
"""Non-destructive 114 inventory audit. Never treat parsed text as visual QA."""
from pathlib import Path
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/"sudu/data/years/114.json"
out=ROOT/"sudu/data/processed/114"
out.mkdir(parents=True,exist_ok=True)
j=json.loads(src.read_text(encoding="utf-8"))
expected={"00-C":38,"00-E":42,"00-MB":25,"09-1":50,"09-2":50}
rows=[]
for paper in j["papers"]:
    code=paper["paper"]
    for q in paper["questions"]:
        rows.append({"questionId":q["id"],"paperCode":code,"number":q["number"],"questionTextPresent":bool(q.get("question")),"textOptions":len(q.get("options") or []),"answerMatched":q.get("answerMatched") is True,"questionVerified":q.get("questionVerified") is True,"answerVerified":q.get("answerVerified") is True,"sourcePdf":paper["questionPdf"],"answerPdf":paper["answerPdf"]})
ids=[x["questionId"] for x in rows]
errors=[]
if len(rows)!=205 or len(set(ids))!=205:errors.append("205_unique_question_ids")
for code,n in expected.items():
    found={x["number"] for x in rows if x["paperCode"]==code}
    if found!=set(range(1,n+1)):errors.append("missing_official_numbers:"+code)
if any(x["answerVerified"] or x["questionVerified"] for x in rows):
    errors.append("unverified_flags_true")
r={"year":114,"generatedAt":datetime.now(timezone.utc).isoformat(),"expected":205,"inventoryRecords":len(rows),"canonicalUnique":len(set(ids)),"withFourTextOptions":sum(x["textOptions"]==4 for x in rows),"missingFourTextOptions":[x["questionId"] for x in rows if x["textOptions"]!=4],"answerMatched":sum(x["answerMatched"] for x in rows),"unmatchedAnswerIds":[x["questionId"] for x in rows if not x["answerMatched"]],"perPaper":{code:sum(x["paperCode"]==code for x in rows) for code in expected},"singleQuestionWebpVisualQaPass":0,"ocrIndependentlyVerified":0,"officialAnswerIndependentlyVerified":0,"blockingFailures":errors,"note":"Inventory-only baseline. Existing official original images remain unmodified. No visual QA inferred."}
(out/"inventory.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(r,ensure_ascii=False))
if errors:raise SystemExit(1)
