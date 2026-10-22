#!/usr/bin/env python3
"""115 data-only acceptance audit. Distinguish generation, OCR, visual QA, answers and DB.

No student DB, teaching, platform UI, other years or main branch are modified.
Writes only the 115 processed inventory/validation reports.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"sudu/data/processed/115"
EXPECTED={"國文":38,"英文":42,"數學B":25,"商業概論":25,"數位科技":25,"會計學":24,"經濟學":26}
PAPERS={"00-C":38,"00-E":42,"00-MB":25,"09-1":50,"09-2":50}
def read(p):return json.loads((P/p).read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(path):return sha(path.read_bytes())
def write(path,object):
    (P/path).write_text(json.dumps(object,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    qs=read("questions.json")["questions"]
    images=read("webp-manifest.json")
    original=read("questions.json")
    answers=read("official-answer-evidence.json")
    ocr=read("ocr-raw-candidates.json")
    ids=[q["questionId"] for q in qs]
    failure=[]
    if len(qs)!=205 or len(set(ids))!=205:failure.append("canonical_id_count_or_uniqueness")
    if len(images["items"])!=205 or images["generated"]!=205:failure.append("missing_single_question_crop")
    if len(images["sharedMaterialCrops"])!=20:failure.append("missing_20_shared_materials")
    bysubject=defaultdict(list)
    bypaper=defaultdict(list)
    for q in qs:
        bysubject[q["subject"]].append(q)
        bypaper[q["paperCode"]].append(q)
        expectedid=f"115-{q['paperCode']}-{q['originalQuestionNumber']:02d}"
        if q["questionId"]!=expectedid:failure.append("canonical_drift:"+q["questionId"])
        if q["year"]!=115:failure.append("wrong_year:"+q["questionId"])
        if q.get("answerVerified") or q.get("questionVerified"):
            failure.append("unreviewed_true_verification_flag:"+q["questionId"])
        if q["answer"] not in ("A","B","C","D"):failure.append("answer_invalid:"+q["questionId"])
    for paper,n in PAPERS.items():
        if {q["originalQuestionNumber"] for q in bypaper[paper]}!=set(range(1,n+1)):
            failure.append("paper_original_number_gap_or_overlap:"+paper)
    for s,n in EXPECTED.items():
        if len(bysubject[s])!=n:failure.append("subject_count_mismatch:"+s)
    m_byid={x["questionId"]:x for x in images["items"]}
    cropstat={"pixelGenerated":0,"decoded":0,"hashVerified":0,"visualPass":0,"imageOnlyOptions":0}
    pending=[]
    for q in qs:
        id=q["questionId"];m=m_byid.get(id)
        if not m or not m.get("output"):
            failure.append("missing_manifest_output:"+id);pending.append(id);continue
        f=ROOT/m["output"]
        if not f.is_file():
            failure.append("missing_file:"+id);pending.append(id);continue
        cropstat["pixelGenerated"]+=1
        if digest(f)!=m["sha256"]:failure.append("webp_hash_mismatch:"+id)
        else:cropstat["hashVerified"]+=1
        with Image.open(f) as img:
            img.load()
            if img.format!="WEBP" or list(img.size)!=m["outputSize"]:
                failure.append("invalid_webp:"+id)
            else:cropstat["decoded"]+=1
        source=ROOT/m["source"]
        if not source.is_file() or digest(source)!=m["sourceSha256"]:
            failure.append("source_sha_mismatch:"+id)
        if not m["source"].startswith("sudu/data/original/115/"):
            failure.append("source_not_official_original:"+id)
        if m["crop"][3]-m["crop"][1]>=m["sourceSize"][1]*0.6:
            failure.append("whole_page_or_oversize:"+id)
        if q.get("optionPresentation") and "image_only" in q["optionPresentation"]:
            cropstat["imageOnlyOptions"]+=1
        if q["assets"]["singleQuestionWebp"]!=m["output"] or q["assets"]["sha256"]!=m["sha256"]:
            failure.append("asset_contract_mismatch:"+id)
        if m.get("qaStatus")=="PASS":
            # Exact current WebP, the recorded evidence, and the evidence file
            # must all agree. Assistant page-visual QA is not external human QA.
            e=q.get("assets",{}).get("visualReviewEvidence")
            if (not e or e.get("reviewedSha256")!=m["sha256"]
                    or e.get("reference") not in {
                        "sudu/DEMO_VISUAL_QA.md",
                        "sudu/data/processed/115/VISUAL_QA_2026-10-22.json",
                        "sudu/data/processed/115/VISUAL_QA_2026-10-22_B2.json"}
                    or not (ROOT/e["reference"]).is_file()
                    or digest(ROOT/e["reference"])!=e.get("referenceSha256")):
                failure.append("unsubstantiated_visual_pass:"+id)
            else:
                cropstat["visualPass"]+=1
        else:pending.append(id)
    shared_ids={x["sharedMaterialId"] for x in original["sharedMaterials"]}
    if len(shared_ids)!=20:failure.append("shared_material_duplicate_count")
    shared_verified=0
    for asset in images["sharedMaterialCrops"]:
        if asset["sharedMaterialId"] not in shared_ids:failure.append("shared_material_orphan")
        f=ROOT/asset["output"]
        if not f.is_file() or digest(f)!=asset["sha256"]:
            failure.append("missing_or_corrupt_shared:"+asset["sharedMaterialId"])
        else:
            with Image.open(f) as img:
                img.load()
                if img.format=="WEBP":shared_verified+=1
    for q in qs:
        if q.get("sharedMaterialId") and q["sharedMaterialId"] not in shared_ids:
            failure.append("missing_shared_ref:"+q["questionId"])
    matched={x["questionId"] for x in answers["items"] if x["comparison"]=="MATCHED"}
    no_auto_false=[x["questionId"] for x in answers["items"] if x.get("answerVerified")]
    if no_auto_false:failure.extend("unreviewed_official_verified:"+x for x in no_auto_false)
    if any(q["answerMatched"]!=(q["questionId"] in matched) for q in qs):
        failure.append("answer_match_evidence_mismatch")
    DB=P/"question-bank.sqlite3"
    roundtrip={"performed":False,"rows":0,"shaMismatches":[]}
    if DB.exists():
        with sqlite3.connect(f"file:{DB}?mode=ro",uri=True) as cx:
            rows=cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
        roundtrip["performed"]=True
        roundtrip["rows"]=len(rows)
        for id,payload,hashvalue in rows:
            if sha(payload.encode())!=hashvalue or json.loads(payload)["questionId"]!=id:
                roundtrip["shaMismatches"].append(id)
        if len(rows)!=205 or roundtrip["shaMismatches"]:failure.append("sqlite_roundtrip_incomplete")
    else:failure.append("sqlite_missing")
    stats={}
    for sub,expected in EXPECTED.items():
        arr=bysubject[sub]
        stats[sub]={
          "officialExpectedQuestions":expected,
          "candidateRecords":len(arr),
          "generatedPerQuestionWebp":sum(bool(m_byid.get(q["questionId"],{}).get("output")) for q in arr),
          "visualQaPass":sum(m_byid[q["questionId"]].get("qaStatus")=="PASS" for q in arr),
          "rawOcrEngineOutput":sum(bool(q.get("extraction",{}).get("ocrRaw")) for q in arr),
          "nativePdfOrManualTextAvailable":sum(bool(q.get("question") and q.get("options")) for q in arr),
          "questionVerified":sum(bool(q["questionVerified"]) for q in arr),
          "officialAnswerMatchedPdfText":sum(q["questionId"] in matched for q in arr),
          "officialAnswerIndependentlyVerified":sum(bool(q["answerVerified"]) for q in arr),
          "sqliteRecordCount":sum(q["questionId"] in ids for q in arr) if roundtrip["rows"]==205 else 0,
          "needsFullVisualReview":sum(m_byid[q["questionId"]]["qaStatus"]!="PASS" for q in arr),
        }
    report={"schemaVersion":2,"year":115,"generatedAt":datetime.now(timezone.utc).isoformat(),
            "mainBaseline":"40ffa920d8efb8e7dc54471a62bb70ecb14ee096",
            "notice":"Generated/decoded does not imply visual QA. Assistant-reviewed images are SHA-backed; independent external human recheck is still pending.",
            "perSubject":stats,"sourcePaperCounts":PAPERS,
            "officialPdfTextAnswerMatched":len(matched),"officialAnswerIndependentVerified":0,
            "generatedWebp":cropstat["pixelGenerated"],"webpDecodePass":cropstat["decoded"],
            "webpShaPass":cropstat["hashVerified"],
            "imageVisualQaPass":cropstat["visualPass"],
            "sharedMaterialWebp":shared_verified,
            "rawOcrRecords":ocr["count"],"imageOnlyOptionQuestions":cropstat["imageOnlyOptions"],
            "sqlite":roundtrip,"pendingVisualReviewIds":pending,
            "blockingStructuralFailures":failure}
    write("inventory.json",report)
    write("VALIDATION.json",{
        "schemaVersion":2,"year":115,
        "structuralStatus":"PASS" if not failure else "FAIL",
        "blockingFailures":failure,
        "webpImageVisualReview":"PARTIAL_ASSISTANT_VISUAL_QA" if cropstat["visualPass"]<205 else "ASSISTANT_VISUAL_QA_COMPLETE_INDEPENDENT_HUMAN_REVIEW_PENDING",
        "officialAnswers":"SHA-pinned PDF textual agreement, independent review not complete",
        "sqlite":"SQLITE_ROUNDTRIP_PASS" if roundtrip["rows"]==205 and not roundtrip["shaMismatches"] else "FAILED",
        "published":"NO","integration":"NO",
        "stats":stats})
    print(json.dumps({"success":not failure,"total":len(qs),
                      "webpDecoded":cropstat["decoded"],
                      "sharedImages":shared_verified,"answerMatched":len(matched),
                      "rawOcr":ocr["count"],"sqlite":roundtrip["rows"],
                      "blockingFailures":failure},ensure_ascii=False))
    if failure:raise SystemExit(1)
if __name__=="__main__":main()
