#!/usr/bin/env python3
"""Non-destructive candidate scan of historical text for page footer / adjacent OCR drift."""
from pathlib import Path
from datetime import datetime,timezone
import json
import re

ROOT=Path(__file__).resolve().parents[1]
INDICATORS=[
("OFFICIAL_PAGE_WATERMARK",re.compile(r"公告試題僅供參考")),
("PAGE_HEADER_NUMBER",re.compile(r"第\s*\d+\s*頁")),
("TOTAL_PAGES_FOOTER",re.compile(r"共\s*(?:8|10|12|14|16)\s*頁")),
("FOOTER_PAGE_DASHES",re.compile(r"(?m)^\s*[-–－]\s*\d{1,2}\s*[-–－]\s*$")),
("EXAM_YEAR_PAGE_HEADER",re.compile(r"1(?:0[5-9]|1[0-4])\s*年四技")),
("NEXT_QUESTION_NUMBER_IN_OPTIONS",re.compile(r"(?m)^\s*(?:\d{1,2})\s*[.．、]\s*[^\n]{5,}")),
]
PLACEHOLDER=re.compile(r"原卷文字.*(?:尚未成功擷取|尚未辨識)|不能把此提示當作正式題幹")

def write(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def run(year):
    folder=ROOT/"sudu/data/processed"/str(year)
    data=json.loads((folder/"questions.json").read_text(encoding="utf-8"))
    records=data["questions"]
    problems=[]
    for q in records:
        fields=[("question",q.get("question"))]
        fields += [(f"option_{i+1}",v) for i,v in enumerate(q.get("options") or [])]
        for field,s in fields:
            if not isinstance(s,str):
                continue
            for label,regex in INDICATORS:
                match=regex.search(s)
                if not match:
                    continue
                excerpt=s[max(0,match.start()-65):min(len(s),match.end()+150)]
                problems.append({"questionId":q["questionId"],"field":field,
                    "indicator":label,"matched":match.group(),"excerpt":excerpt,
                    "status":"SUSPECT_REQUIRES_OFFICIAL_SOURCE_VISUAL_QA"})
        qtext=q.get("question") or ""
        if PLACEHOLDER.search(qtext):
            problems.append({"questionId":q["questionId"],"field":"question",
                "indicator":"LEGACY_OCR_PLACEHOLDER","matched":"source-not-reliably-extracted",
                "excerpt":qtext[:190],"status":"PENDING_SOURCE_IMAGE_AND_OCR_QA"})
        if len(q.get("options") or [])!=4:
            problems.append({"questionId":q["questionId"],"field":"options",
                "indicator":"FOUR_TEXT_OPTIONS_MISSING","matched":str(len(q.get("options") or [])),
                "excerpt":"","status":"PENDING_IMAGE_ONLY_FALLBACK_OR_OCR_CORRECTION"})
    ids=sorted(set(x["questionId"] for x in problems))
    report={"schemaVersion":1,"year":year,"generatedAt":datetime.now(timezone.utc).isoformat(),
        "inspection":"DETERMINISTIC_TEXT_SCAN_ONLY_NOT_MANUAL_QA",
        "suspectQuestionCount":len(ids),"suspectIds":ids,
        "findingCount":len(problems),"findings":problems,
        "rules":"Do not auto-strip text: footer-like text could be quote/content. Inspect official source first.",
        "readyForIntegration":False}
    write(folder/"TEXT_QA_SUSPECTS.json",report)
    lines=[f"# {year} 年 OCR 舊文字疑點（非 QA PASS）","",
           f"- 受影響候選題號：{len(ids)}；共 {len(problems)} 個疑點。",
           "- 不允許自動刪改公式、引文、題目或答案；需逐張對照官方來源後才修正。",
           "- 依 docs/SUDU_QUESTION_BANK_QA_GATE_105_115.md，正式接入仍禁止。",
           ""]
    for ident in ids:
        types=", ".join(sorted(set(x["indicator"] for x in problems if x["questionId"]==ident)))
        lines.append(f"- [ ] {ident} -- {types}")
    (folder/"TEXT_QA_SUSPECTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return {"year":year,"questions":len(records),"suspects":len(ids),"findings":len(problems)}

if __name__=="__main__":
    print(json.dumps([run(y) for y in range(105,115)],ensure_ascii=False))
