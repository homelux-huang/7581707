#!/usr/bin/env python3
import json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'sudu/data/years'
summary={"schema":1,"generatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"years":[]}
for y in range(90,116):
  p=folder/(str(y)+'.json')
  if p.exists():
    try:
      doc=json.loads(p.read_text('utf-8'))
      arr=doc.get('papers',[])
      row={"year":y,"available":True,"questions":sum(len(z.get("questions",[])) for z in arr),"papers":len(arr),
           "officialAnswers":sum(sum(bool(q.get("answerVerified")) for q in z.get("questions",[])) for z in arr),
           "completePapers":sum(bool(z.get("complete")) for z in arr),
           "teachingVerified":sum(sum(bool(q.get("teachingVerified")) for q in z.get("questions",[])) for z in arr),
           "paperCodes":[z.get("paper") for z in arr],"errors":doc.get('errors',[])}
    except Exception as e:
      row={"year":y,"available":False,"error":str(e)}
  else:
    row={"year":y,"available":False,"questions":0,"papers":0,"officialAnswers":0,"completePapers":0,"teachingVerified":0,"errors":["尚未完成擷取"]}
  summary["years"].append(row)
out=ROOT/'sudu/data/index.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(summary,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print("COVERAGE",json.dumps([{"year":z["year"],"questions":z.get("questions",0),"answers":z.get("officialAnswers",0),"teaching":z.get("teachingVerified",0)} for z in summary["years"]],ensure_ascii=False))
