#!/usr/bin/env python3
"""Check 115 candidate letters against SHA-pinned TCTE official answer PDFs.

Only changes the 115 candidate corpus. No questionVerified/answerVerified
promotion, no change to main/teaching/gradebook, no inference from solutions.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import fitz
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data/processed/115"
IN=DATA/"questions.json"
YEAR=ROOT/"sudu/data/years/115.json"
ALLOWED={"web1.tcte.edu.tw","www.tcte.edu.tw","tcte.edu.tw"}

def download(url, sha):
    current=url
    for _ in range(4):
        p=urlparse(current)
        if p.scheme!="https" or p.hostname not in ALLOWED:
            raise ValueError("Answer source must be the official HTTPS host")
        r=requests.get(current,timeout=(20,70),allow_redirects=False,
                       headers={"User-Agent":"7581707-115-answer-version-comparator/1.0"})
        if r.is_redirect:
            current=urljoin(current,r.headers["Location"])
            continue
        r.raise_for_status()
        if not r.content.startswith(b"%PDF") or hashlib.sha256(r.content).hexdigest()!=sha:
            raise ValueError("Answer PDF no longer matches prior official SHA-256: "+current)
        return r.content
    raise ValueError("Too many redirects")

def parse(pdfbin):
    out={}
    conflicts=[]
    with fitz.open(stream=pdfbin,filetype="pdf") as doc:
        for page_num,page in enumerate(doc,1):
            text=page.get_text(sort=True)
            # Matches the legacy TCTE answer parser, with explicit conflict audit.
            for m in re.finditer(r"(?<!\d)(\d{1,3})[ \t]+([ABCD])(?=\s|$)",text):
                n=int(m.group(1))
                if not (1<=n<=60):
                    continue
                val=m.group(2)
                if n in out and out[n]["raw"]!=val:
                    conflicts.append(n)
                else:
                    out[n]={"raw":val,"page":page_num}
    for n in conflicts:
        out.pop(n,None)
    return out,sorted(set(conflicts))

def main():
    year=json.loads(YEAR.read_text(encoding="utf-8"))
    corpus=json.loads(IN.read_text(encoding="utf-8"))
    timestamp=datetime.now(timezone.utc).isoformat()
    papers={p["paper"]:p for p in year["papers"]}
    qs={q["questionId"]:q for q in corpus["questions"]}
    report={"schemaVersion":1,"year":115,"generatedAt":timestamp,
            "verificationRule":"SHA-pinned official answer PDF text extraction + candidate letter match; no visual human verification",
            "answerVerifiedCount":0,"papers":{},"items":[]}
    per={}
    for paper,src in papers.items():
        related=sorted((q for q in qs.values() if q["paperCode"]==paper),
                       key=lambda x:x["originalQuestionNumber"])
        expectedsha=related[0]["answerProvenance"]["pdfSha256"]
        data=download(src["answerPdf"],expectedsha)
        parsed,conflicts=parse(data)
        stats={"expected":len(related),"parsedKeys":len(parsed),
               "conflicts":conflicts,"matches":0,"mismatches":0,"missing":0}
        report["papers"][paper]={"source":src["answerPdf"],
                                 "pdfSha256":expectedsha,"page":1,"stats":stats}
        for q in related:
            n=q["originalQuestionNumber"]
            key=parsed.get(n)
            actual=key["raw"] if key else None
            matched=actual is not None and actual==q.get("answer")
            result="MATCHED" if matched else "MISMATCH" if actual else "UNRESOLVED"
            stats[{"MATCHED":"matches","MISMATCH":"mismatches","UNRESOLVED":"missing"}[result]]+=1
            item={"questionId":q["questionId"],"year":115,"paperCode":paper,
                  "originalQuestionNumber":n,"officialSource":src["answerPdf"],
                  "officialSourceSha256":expectedsha,"sourcePage":key["page"] if key else None,
                  "officialExtractedValue":actual,"candidateValue":q.get("answer"),
                  "comparison":result,"answerMatched":matched,"answerVerified":False,
                  "visualReviewStatus":"PENDING_SECOND_REVIEW",
                  "officialCorrectionStatus":"consult_official-confirmation-status.json"}
            report["items"].append(item)
            q["answerMatched"]=matched
            q["answerVerified"]=False
            prov=q["answerProvenance"]
            prov["matchingMethod"]="sha_pinned_official_pdf_text_extraction_comparison"
            prov["answerReconciledAt"]=timestamp
            prov["officialExtractedValue"]=actual
            prov["sourcePage"]=key["page"] if key else None
            if not matched:
                token="official_answer_"+result.lower()
                if token not in q["issues"]:
                    q["issues"].append(token)
                q["reviewStatus"]="needs_review"
        per[paper]=stats
    corpus["notice"]="CANDIDATE QUESTIONS. Answer letters PDF-text matched where indicated, but NONE independently visual-reviewed."
    total=sum(x["matches"] for x in per.values())
    corpus["answerMatchedCount"]=total
    IN.write_text(json.dumps(corpus,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (DATA/"official-answer-evidence.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"paperStats":per,"answerTextMatches":total,
                      "officialVisualVerified":0},ensure_ascii=False))
    if not total:
        raise RuntimeError("No official PDF answer letters parsed; do not adopt candidates")

if __name__=="__main__":
    main()
