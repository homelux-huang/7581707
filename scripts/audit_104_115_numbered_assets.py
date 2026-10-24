#!/usr/bin/env python3
"""G0-G5 question-number/asset inventory, read-only, 104 extra + 105-115 QA.

Writes audit reports only. This can prove file/SHA/DB consistency, NOT human
visual QA or that historical legacy candidate paper counts are official-final.
No OCR, PDF rewrite, image recrop, QA flag mutation, release, or student writes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"sudu/data"
PROCESSED=DATA/"processed"
OUT_JSON=PROCESSED/"104-115-QUESTION_ID_GAPS_20261024.json"
OUT_MD=ROOT/"docs/SUDU_104_115_NUMBERED_QUESTION_ASSET_AUDIT_20261024.md"
PAPERS=("00-C","00-E","00-MB","09-1","09-2")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def four_options(q):
    opts=q.get("options")
    return (isinstance(opts,list) and len(opts)==4 and
            all(isinstance(o,str) and o.strip() for o in opts))

def ids(questions):
    return [q.get("questionId") for q in questions]

def source(year):
    return read(DATA/"years"/f"{year}.json")

def expected_legacy(year):
    p=source(year)["papers"]
    assert len(p)==5 and {q["paper"] for q in p}==set(PAPERS)
    groups={}
    for paper in p:
        code=paper["paper"]
        numbers=[int(q["number"]) for q in paper["questions"]]
        assert len(numbers)==len(set(numbers))
        groups[code]={
            "subject":paper.get("subject"),
            "legacyRecordCount":len(numbers),
            "numberRange": [min(numbers),max(numbers)],
            "legacyNumberHoles": sorted(set(range(min(numbers),max(numbers)+1))-set(numbers)),
            "expectedIdsFromLegacy":[f"{year}-{code}-{n:02d}" for n in sorted(numbers)]
        }
    return groups

def audit(year, g5audit):
    legacy=expected_legacy(year)
    if year==104:
        rows=[q for p in source(104)["papers"] for q in p["questions"]]
        return {
            "year":104,"scope":"EXTRA_BEFORE_DOCUMENTED_105_114_TEN_YEARS",
            "officialActualQuestionCountsIndependentlyConfirmed":False,
            "legacyCandidateQuestions":len(rows),
            "legacyFourOptionTextCandidates":sum(four_options(q) for q in rows),
            "processedDirectoryPresent":(PROCESSED/"104").is_dir(),
            "candidateNumberHoles":sum(len(g["legacyNumberHoles"]) for g in legacy.values()),
            "webpLinked":0,"webpVisualQaRecorded":0,"ocrTextQa":0,
            "answerFinalVerified":0,"sqliteG5Pass":False,"integrationReady":False,
            "papers":{k:{key:v for key,v in d.items() if key!="expectedIdsFromLegacy"}
                      for k,d in legacy.items()},
            "note":"104 source candidate exists, but no processed/104 QA pipeline or isolated DB; 203 is legacy count only"
        }
    folder=PROCESSED/str(year)
    qbank=read(folder/"questions.json")
    manifest=read(folder/"webp-manifest.json")
    inventory=read(folder/"inventory.json")
    answers=read(folder/"official-answer-evidence.json")
    ocr=read(folder/"ocr-raw-candidates.json")
    visual=read(folder/"VISUAL_QA.json")
    yearquestions=qbank["questions"]
    mf=manifest["items"]
    answer_items=answers["items"]
    ocr_items=ocr["items"]
    seen=ids(yearquestions)
    mid=ids(mf)
    if len(seen)!=len(set(seen)) or len(mid)!=len(set(mid)):
        raise ValueError(f"{year}: duplicate canonical id in questions or WebP manifest")
    qmap={q["questionId"]:q for q in yearquestions}
    mmap={m["questionId"]:m for m in mf}
    amap={a["questionId"]:a for a in answer_items}
    omap={o["questionId"]:o for o in ocr_items}
    source_expected={qid for group in legacy.values() for qid in group["expectedIdsFromLegacy"]}
    if set(qmap)!=source_expected or set(mmap)!=source_expected or set(amap)!=source_expected:
        # Keep full report of mismatches, don't invent replacement records.
        pass
    missing_assets=[]
    bad_sha=[]
    qa_evidence_missing=[]
    verified_pass=[]
    papers={}
    for code,group in legacy.items():
        wanted=group["expectedIdsFromLegacy"]
        actual=[qid for qid in wanted if qid in qmap]
        missing_q=sorted(set(wanted)-set(qmap))
        missing_manifest=sorted(set(wanted)-set(mmap))
        image_ids=[]
        candidate_ids=[]
        visual_ids=[]
        text_missing=[]
        answer_verified=[]
        for qid in wanted:
            q=qmap.get(qid,{})
            m=mmap.get(qid,{})
            candidate=m.get("output") or m.get("webpPath")
            h=m.get("outputSha256") or m.get("sha256")
            if not four_options(q):
                text_missing.append(qid)
            if amap.get(qid,{}).get("answerVerified") is True:
                answer_verified.append(qid)
            if candidate:
                path=(ROOT/candidate).resolve()
                if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
                    missing_assets.append(qid)
                elif not (isinstance(h,str) and len(h)==64 and digest(path)==h):
                    bad_sha.append(qid)
                else:
                    candidate_ids.append(qid)
                    if m.get("qaStatus")=="PASS":
                        ev=m.get("visualReviewEvidence") or {}
                        if (ev.get("reviewedSha256")!=h or
                                not ev.get("reference") or
                                not (ROOT/ev["reference"]).is_file()):
                            qa_evidence_missing.append(qid)
                        else:
                            visual_ids.append(qid)
            else:
                image_ids.append(qid)
        papers[code]={
            "subject":group["subject"],"legacyCandidateCount":len(wanted),
            "candidateNumberRange":group["numberRange"],
            "missingCanonicalRecords":missing_q,
            "missingManifestRecords":missing_manifest,
            "legacyNumberHoles":group["legacyNumberHoles"],
            "withExistingShaVerifiedWebp":len(candidate_ids),
            "missingSingleQuestionWebpIds":image_ids,
            "qaPassWithReferenceEvidenceIds":visual_ids,
            "qaPassWithReferenceEvidence":len(visual_ids),
            "missingFourTextOptionsIds":text_missing,
            "officialFinalAnswerVerified":len(answer_verified)
        }
        verified_pass.extend(visual_ids)
    raw_count=sum(isinstance(x.get("rawOcrText") or x.get("rawText") or x.get("ocrRawText"),str)
                  and bool((x.get("rawOcrText") or x.get("rawText") or x.get("ocrRawText")).strip())
                  for x in ocr_items)
    shared=manifest.get("sharedMaterialCrops",[])
    official_ids=set(qmap)
    g5=g5audit.audit_year(year)
    return {
        "year":year,"legacyCandidateQuestions":len(source_expected),
        "questionJsonRows":len(yearquestions),"webpManifestRows":len(mf),
        "officialAnswerEvidenceRows":len(answer_items),"ocrRawCandidateRows":len(ocr_items),
        "webpLinkedAndShaVerified":sum(p["withExistingShaVerifiedWebp"] for p in papers.values()),
        "missingSingleQuestionWebpIds":sorted(x for p in papers.values() for x in p["missingSingleQuestionWebpIds"]),
        "webpFileMissingIds":missing_assets,"webpShaMismatchIds":bad_sha,
        "webpQaPassWithSourceReference":len(verified_pass),
        "qaPassReferenceMissingIds":qa_evidence_missing,
        "ocrRawNonblank":raw_count,
        "missingFourTextOptionsIds":sorted(x for p in papers.values() for x in p["missingFourTextOptionsIds"]),
        "ocrTextIndependentlyVerified":inventory.get("ocrTextIndependentlyVerified",inventory.get("textQaPass",0)),
        "answerFinalVerified":sum(p["officialFinalAnswerVerified"] for p in papers.values()),
        "questionVerifiedFlagCount":sum(q.get("questionVerified") is True for q in yearquestions),
        "sourceLegacyCanonicalMismatchIds":sorted(source_expected ^ official_ids),
        "sharedMaterialCandidates":len(shared),
        "sharedMaterialQaPassRecorded":sum(s.get("qaStatus")=="PASS" for s in shared),
        "sqliteG5Pass":g5["g5Pass"],"sqliteRows":g5.get("onDiskRows"),
        "sqliteMismatchCount":g5.get("onDiskMismatchCount"),"sqliteReadbackPasses":g5.get("sandboxImportPasses"),
        "sqliteBlockers":g5["blockers"],
        "integrationReady":False,
        "officialActualQuestionCountsIndependentlyConfirmed":False if year<=113 else "REQUIRES_TCTE_G0_EVIDENCE",
        "papers":papers
    }

def build_report():
    import sys
    sys.path.insert(0,str(ROOT/"scripts"))
    import audit_105_115_sqlite_readonly as g5
    result=[audit(year,g5) for year in range(104,116)]
    totals={
        "candidateQuestions105_115":sum(r["legacyCandidateQuestions"] for r in result if r["year"]>=105),
        "webpLinkedAndShaVerified105_115":sum(r["webpLinkedAndShaVerified"] for r in result if r["year"]>=105),
        "webpQaPassWithReference105_115":sum(r["webpQaPassWithSourceReference"] for r in result if r["year"]>=105),
        "missingWebp105_115":sum(len(r["missingSingleQuestionWebpIds"]) for r in result if r["year"]>=105),
        "g5PassYears105_115":sum(r["sqliteG5Pass"] for r in result if r["year"]>=105),
        "readyYears":0
    }
    metadata={
        "generatedAtUTC":datetime.now(timezone.utc).isoformat(),
        "qaCommitAtStart":subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),
        "documentedOriginalScope":"105-114 inclusive = 10 years, plus 115; 104 is supplementary",
        "year104Status":"EXTRA_SOURCE_ONLY_UNVERIFIED_COUNT",
        "noNewQAFlagsOrAnswerFlagsSet":True,"notForRelease":True,
        "noImagesRecropped":True,"officialCountIndependentlyRecheckedThisRun":False,
        "totals":totals,"years":result
    }
    md=[
        "# 7581707｜104–115 年逐題號 WebP、OCR、QA、SQLite 缺口稽核",
        "",
        "> 這是隔離 QA 分支唯讀 SHA/JSON/SQLite 核查，**不是**原卷人工目視 PASS 或正式題庫放行。"
        "歷史年度題數源自現有 years JSON，仍要獨立核對 TCTE 官方實際題數。",
        "",
        f"- 基準 Commit：`{metadata['qaCommitAtStart']}`。",
        "- 正式十年度定義：**105–114（含），加 115 年**。104 年另作範圍外來源-only 補充盤點。",
        f"- 105–115 候選 `{totals['candidateQuestions105_115']}` 題；具檔案與 SHA 的 WebP "
        f"`{totals['webpLinkedAndShaVerified105_115']}` 題；尚缺單題 WebP "
        f"`{totals['missingWebp105_115']}`；有既存 G1 PASS 及路徑證據 "
        f"`{totals['webpQaPassWithReference105_115']}` 題；SQLite G5 "
        f"`{totals['g5PassYears105_115']}/11` 年。",
        "- 所有年度仍 NO RELEASE，不因圖片解碼、候選答案或 SQLite PASS 宣告完整 QA。",
        "",
        "| 年度 | 候選題數 | WebP SHA 一致 | WebP 待補 | 目視 PASS 紀錄+證據 | OCR 文字QA | 最終答案 | SQLite G5 |",
        "|---|---:|---:|---:|---:|---:|---:|---|"
    ]
    for r in result:
        if r["year"]==104:
            md.append(f"| 104（額外） | {r['legacyCandidateQuestions']} | 0 | 尚未建 processed | 0 | 0 | 0 | 無獨立資料庫 |")
        else:
            md.append(f"| {r['year']} | {r['legacyCandidateQuestions']} | {r['webpLinkedAndShaVerified']} | "
                      f"{len(r['missingSingleQuestionWebpIds'])} | {r['webpQaPassWithSourceReference']} | "
                      f"{r['ocrTextIndependentlyVerified']} | {r['answerFinalVerified']} | "
                      f"{'PASS' if r['sqliteG5Pass'] else 'BLOCKED'} |")
    md += ["","## 按試卷代碼／題號核查","",
           "歷史 09-1／09-2 合併專業科目以官方試卷代碼為準；未確認年度內分科題號前不推定每科各25題。",
           ""]
    for r in result:
        md.append(f"### {r['year']} 年")
        for code,p in r["papers"].items():
            missing=p.get("missingSingleQuestionWebpIds",[])
            options=p.get("missingFourTextOptionsIds",[])
            md.append(f"- `{code}` {p['subject']}：候選 {p.get('legacyCandidateCount',p.get('legacyRecordCount'))}；"
                      + (f"單題 WebP 缺 {len(missing)}：{', '.join(missing)}；" if missing else "無漏列單題 WebP；")
                      + (f"文字四選項待修 {len(options)} 題；" if options else "")
                      + (f"G1 {p.get('qaPassWithReferenceEvidence',0)}。" if r["year"]>=105 else "104 只有 legacy 候選，沒有 processed/104。"))
        if r["year"]>=105:
            if r["qaPassReferenceMissingIds"]:
                md.append("- 注意：已有 PASS 標記但缺 SHA 綁定之引用路徑："+", ".join(r["qaPassReferenceMissingIds"]))
            if r["webpShaMismatchIds"]:
                md.append("- SHA MISMATCH："+", ".join(r["webpShaMismatchIds"]))
            if r["sourceLegacyCanonicalMismatchIds"]:
                md.append("- 來源/候選題號集合不一致："+", ".join(r["sourceLegacyCanonicalMismatchIds"]))
        md.append("")
    md += ["## 待補與執行限制",
           "",
           "- 106 國文14–20已有 SHA 綁定的7個**草稿**裁切及3個共用材料，仍要逐張官方原頁直接比對才能從 DRAFT 改 PASS。",
           "- 106 國文36–38、107 國文／英文／商科、108 數學B／商科為其餘最優先缺單題候選圖批次，必須先核對原頁位置與選項。",
           "- 105／114 先前 SQLite JSON 差異已由本次 QA 分支 G5 機制處理（如報表 G5=PASS），不能推論 G0–G4 也過。",
           "- 114/115 全部候選 WebP 已有題號，仍大量缺 G1、G2、G3 與共用材料獨立 QA。",
           "- 104 年原始來源已存在，必須另建版本化 processed/104 並查核官方 5 份試卷實際題數；不得強行改成205題。",
           "- **任何 WebP 候選不等於可發佈**，所有 `integrationReady`、`answerVerified`、`questionVerified` 皆不由本稽核自動變更。",
           ""]
    return metadata,"\n".join(md)

def main():
    c=argparse.ArgumentParser()
    c.add_argument("--write",action="store_true")
    args=c.parse_args()
    result,md=build_report()
    if args.write:
        OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
        OUT_MD.parent.mkdir(parents=True,exist_ok=True)
        OUT_JSON.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        OUT_MD.write_text(md+"\n",encoding="utf-8")
    print(json.dumps({"totals":result["totals"],
                      "missingIdsByYear":{str(y["year"]):y["missingSingleQuestionWebpIds"]
                                          for y in result["years"] if y["year"]>=105},
                      "reportsWritten":args.write},ensure_ascii=False))

if __name__ == "__main__":
    main()
