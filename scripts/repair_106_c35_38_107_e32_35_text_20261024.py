#!/usr/bin/env python3
"""Versioned 106 C35 source-pixel crop + 106 C35-38 / 107 E32-35 direct-source G2.
No official-final answer verification, independent human review, release or student writes.
Do not invent OCR raw text: preserve legacy PDF-layer candidates and record corrected diff.
"""
import argparse
import difflib
import hashlib
import io
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageChops
from link_106_c14_20_existing_webp_drafts import db_rebuild
from stage_107_e32_35_source_pixel_crops import update_db
from audit_105_115_sqlite_readonly import audit_year

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
CROP_ID="106-00-C-35"
SRC="sudu/data/original/106/00-C/p007-93b8ec6eb3-v2-w1400-q66.webp"
SOURCE_BLOB="3d0cf18a9c6c27c7a368d4fbfe2df6979f0792f2"
SOURCE_SHA="c2094dd3dc2d2c7221be4abf109bb19e0af7d546d79ed1f4a4505d75586fefc7"
CROP_BOX=[90,1057,1310,1248]
CROP_PATH="sudu/data/processed/106/qa-drafts/webp-v4/00-C/106-00-C-35.webp"
EVIDENCE={
 106:"sudu/data/processed/106/qa-drafts/TEXT_QA_106_C35_38_SOURCE_20261024.json",
 107:"sudu/data/processed/107/qa-drafts/TEXT_QA_107_E32_35_SOURCE_20261024.json",
}
TEXT={
 106:{
 35:("依據上文，下列「」內的解釋，何者正確？",[
 "且將與之謀「所以驚人耳目者」：令人稱奇之事",
 "「誤為刀傷其頂」，解衣帶：斗笠被刀子割毀",
 "「羅漢亡杖」已半年：羅漢攜帶禪杖走失",
 "頂有傷處，「血漬藥傅如昔」：藥效持久"]),
 36:("下列關於甲、乙二文的敘述，何者正確？",[
 "甲文是乙文的創作基礎，甲文所顯現的儒、道衝突為乙文闡發的重點",
 "甲文的蘇子是蘇軾的化身，乙文中的蘇軾融合了史實與李一冰的闡釋",
 "甲文用蘇子與客對話來敘寫，乙文則用蘇軾閱讀《莊子》來開展故事",
 "甲文強調蘇子深陷人生無常的傷悲，乙文則凸顯蘇軾超越生死的智慧"]),
 37:("乙文認為：莊子「藏天下於天下」可做為甲文「自其不變者而觀之」的註解，應是基於：",[
 "蘇軾從「不變」體悟了「萬物與我為一」，其哲理與莊子贊同的「以不藏為藏」相近",
 "蘇軾從「不變」體悟了「萬物與我為一」，其哲理與莊子贊同的「用行而舍藏」相近",
 "蘇軾從「不變」體悟了「世事終有定數」，其哲理與莊子贊同的「以不藏為藏」相近",
 "蘇軾從「不變」體悟了「世事終有定數」，其哲理與莊子贊同的「用行而舍藏」相近"]),
 38:("乙文所說的「失落」，主要是由什麼原因所造成？",[
 "心有拘執","天下無道","藏才隱智","物我無盡"]),
 },
 107:{
 32:("On which day is it most likely to rain?",[
 "Monday","Tuesday","Thursday","Friday"]),
 33:("Jane is planning a two-day trip to Hualien. She likes sunny days, so which period would be the best choice for the trip?",[
 "Monday to Tuesday","Tuesday to Wednesday","Wednesday to Thursday","Thursday to Friday"]),
 34:("According to the passage, which of the following best describes Chi at the time he recorded Typhoon Morakot?",[
 "Chi had been a famous movie director for twenty years.",
 "Chi had been an award-winning typhoon photographer.",
 "Chi was an employee hired by the government at that time.",
 "Chi was sent to record the pace and movement of the typhoon."]),
 35:("Which of the following has the closest meaning to the word “raising” in paragraph 3?",[
 "collecting","lifting","moving","promoting"]),
 }
}

def at(rel):
    loc=(ROOT/rel).resolve()
    assert loc.is_relative_to(ROOT.resolve())
    return loc

def read(rel):
    return json.loads(at(rel).read_text(encoding="utf8"))

def write(rel,value):
    p=at(rel);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def image_crop(stage):
    raw=at(SRC).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert blob==SOURCE_BLOB and sha(raw)==SOURCE_SHA
    with Image.open(io.BytesIO(raw)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        out=page.crop(tuple(CROP_BOX))
        buf=io.BytesIO()
        out.save(buf,format="WEBP",lossless=True,method=6,exact=True)
        result=buf.getvalue()
        with Image.open(io.BytesIO(result)) as check:
            check.load()
            assert check.size==(1220,191)
            assert ImageChops.difference(out.convert("RGB"),check.convert("RGB")).getbbox() is None
    p=at(CROP_PATH)
    if p.exists():
        assert sha(p.read_bytes())==sha(result),"Changed v4 crop exists: refuse overwrite"
    elif stage:
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(result)
    return sha(result)

def index(rows):
    result={r["questionId"]:r for r in rows}
    assert len(result)==len(rows)
    return result

def lines(n,question,options):
    return str(n)+". "+question+"\n"+"".join("("+letter+") "+v+"\n" for letter,v in zip("ABCD",options))

def apply(stage):
    branch=subprocess.check_output(["git","branch","--show-current"],text=True,cwd=ROOT).strip()
    assert branch==BRANCH,"Wrong branch"
    heads={}
    for year in (106,107):
        base="sudu/data/processed/"+str(year)+"/"
        ledger={}
        for name in ("questions.json","ocr-raw-candidates.json","webp-manifest.json",
                     "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json"):
            ledger[name]=read(base+name)
        b=ledger["questions.json"];m=ledger["webp-manifest.json"]
        o=ledger["ocr-raw-candidates.json"];v=ledger["VISUAL_QA.json"]
        inv=ledger["inventory.json"];val=ledger["VALIDATION.json"]
        rel=ledger["release-manifest.json"]
        assert len(b["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
        assert rel["releaseAllowed"] is False and rel["integrationReady"] is False
        assert val["releaseAllowed"] is False and val["integrationReady"] is False
        assert inv["visualQaPass"]==(15 if year==106 else 4)
        assert inv["answerOfficialFinalVerified"]==0
        heads[year]=(base,ledger,index(b["questions"]),index(o["items"]),index(m["items"]),index(v["items"]))
    base,ledger,questions,ocr,manifest,visual=heads[106]
    assert manifest[CROP_ID]["sourcePageWebpSha256"]==SOURCE_SHA
    assert manifest[CROP_ID]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert visual[CROP_ID]["status"]=="PENDING"
    expected_old_path="sudu/data/processed/106/webp-v1/00-C/106-00-C-35.webp"
    m=manifest[CROP_ID]
    assert m["output"] in (expected_old_path,CROP_PATH),"Unexpected C35 replacement by another session"
    if m["output"]==expected_old_path:
        assert m["outputSha256"]=="55b57b4a090ecc693550cd585dd1339d36b215fc0e152989ed9458814796d413"
        assert sha(at(expected_old_path).read_bytes())==m["outputSha256"]
    new_sha=image_crop(stage)
    if stage:
        m.update({"output":CROP_PATH,"outputSha256":new_sha,
                  "cropPixels":CROP_BOX,"outputSize":[1220,191],
                  "generationVersion":"assistant-direct-source-pixel-candidate-v4-20261024",
                  "qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA"})
        m["issues"]=sorted(set(m.get("issues",[])+["PENDING_DIRECT_G1_Q35_V4"]))
        q=questions[CROP_ID]
        q["assets"].update({"singleQuestionWebp":CROP_PATH,"sha256":new_sha,"sourcePage":7})
        q["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        visual[CROP_ID].update({"candidateWebp":CROP_PATH,"candidateSha256":new_sha,
                               "status":"PENDING","reviewer":None,"visualEvidence":None})
        ocr[CROP_ID]["imageSha256"]=new_sha
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    outcome={}
    for year in (106,107):
        base,ledger,qs,os,imgs,vs=heads[year]
        original_count=6 if year==106 else 0
        reviewed={x["questionId"] for x in ledger["questions.json"]["questions"]
                  if x.get("questionVerified")}
        selected={f"{year}-{'00-C' if year==106 else '00-E'}-{n:02d}" for n in TEXT[year]}
        assert reviewed.issuperset(set()) and reviewed<=selected.union(reviewed)
        unexpected=reviewed & selected
        if unexpected and unexpected!=selected:
            raise RuntimeError("Partial other-session G2 changes; reconcile before writing")
        if ledger["inventory.json"].get("ocrTextIndependentlyVerified",0) != original_count+len(unexpected):
            raise RuntimeError("Unexpected current G2 count")
        records=[]
        for n,(question,options) in TEXT[year].items():
            qid=f"{year}-{'00-C' if year==106 else '00-E'}-{n:02d}"
            q=qs[qid];o=os[qid];m=imgs[qid]
            assert len(options)==4 and all(isinstance(x,str) and x.strip() for x in options)
            assert not q["answerVerified"] and not q["integrationReady"]
            assert q["assets"]["sha256"]==m["outputSha256"], "Existing source-linked asset changed"
            if year==106 and n==35:
                target_sha=new_sha
            else:
                target_sha=m["outputSha256"]
                assert sha(at(m["output"]).read_bytes())==target_sha
                assert m["qaStatus"]=="PASS","Existing G1 not PASS"
            raw_q=o["legacyQuestion"]; raw_options=o["legacyOptions"]
            assert isinstance(raw_q,str) and isinstance(raw_options,list)
            assert o.get("rawOcrText") is None, "Do not overwrite real raw OCR"
            raw=lines(n,raw_q,raw_options)
            corrected=lines(n,question,options)
            diff="".join(difflib.unified_diff(raw.splitlines(True),corrected.splitlines(True),
                fromfile="legacy-PDF-text-preserved",tofile="source-image-corrected"))
            assert raw and corrected
            rec={"questionId":qid,"sourcePage":7 if (year,n)==(106,35) else
                 (8 if year==106 else 6),
                 "sourcePageWebp":m["source"],"sourcePageSha256":m["sourcePageWebpSha256"],
                 "questionWebp":CROP_PATH if (year,n)==(106,35) else m["output"],
                 "questionWebpSha256":target_sha,
                 "legacyQuestion":raw_q,"legacyOptions":raw_options,
                 "correctedQuestion":question,"correctedOptions":options,
                 "legacyToCorrectedUnifiedDiff":diff,
                 "rawOcrTextPreservedAsNull":True,
                 "rawBasis":"existing legacy PDF text (not fabricated Tesseract output)",
                 "textQaResult":"PASS_DIRECT_SOURCE_PAGE_VISUAL",
                 "reviewer":"ChatGPT assistant","independentHumanReview":False}
            records.append(rec)
            if qid in unexpected:
                assert q["question"]==question and q["options"]==options
                assert o["correctedQuestion"]==question and o["correctedOptions"]==options
            elif stage:
                q["legacyUnverifiedQuestion"]=q["question"]
                q["legacyUnverifiedOptions"]=q["options"]
                q.update({"question":question,"options":options,
                          "questionVerified":True,"textQaStatus":"PASS",
                          "textQaEvidence":EVIDENCE[year],
                          "ocrStatus":"PASS_REVIEWED_ORIGINAL_PAGE_IMAGE"})
                o.update({"correctedQuestion":question,"correctedOptions":options,
                          "diff":diff,"qaStatus":"PASS",
                          "qaReviewer":"ChatGPT assistant","qaReviewedAt":now,
                          "qaEvidencePath":EVIDENCE[year],
                          "imageSha256":target_sha})
        payload={"schemaVersion":1,"year":year,
          "paperCode":"00-C" if year==106 else "00-E",
          "reviewer":"ChatGPT assistant","independentHumanReview":False,
          "reviewedAt":now,
          "method":"Direct visual inspection of TCTE source raster pages and SHA-bound candidate crops; no invented OCR raw; legacy PDF text preserved",
          "officialPdfByteHashIndependentlyRedownloaded":False,
          "sourcePageNote":"106 pages 7/8" if year==106 else "107 page 6",
          "questionTextQaNew":len(selected)-len(unexpected),
          "newG1QuestionPass":0,"newOfficialFinalAnswersVerified":0,
          "candidateC35NeedsSeparateVisualG1":year==106,
          "releaseAllowed":False,"integrationReady":False,"records":records}
        if stage and not unexpected:
            inv=ledger["inventory.json"];val=ledger["VALIDATION.json"]
            inv["ocrTextIndependentlyVerified"]=original_count+len(selected)
            inv["textQaPass"]=original_count+len(selected)
            val["ocrTextVerified"]=original_count+len(selected)
            for name in ("questions.json","ocr-raw-candidates.json","webp-manifest.json",
                         "VISUAL_QA.json","inventory.json","VALIDATION.json"):
                write(base+name,ledger[name])
            write(EVIDENCE[year],payload)
            if year==106: db_rebuild(ledger["questions.json"])
            else: update_db(ledger["questions.json"])
        outcome[year]={"newG2":len(selected)-len(unexpected),
                       "g2Total":original_count+len(selected),
                       "g1NoChange":True}
    if stage:
        audits=[audit_year(i) for i in range(105,116)]
        assert len(audits)==11 and all(a["g5Pass"] and a["sandboxImportPasses"]==2 for a in audits)
        report=read("sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json")
        report["years"]=audits
        report["yearsG5Pass"]=11
        report["yearsReviewed"]=11
        report["sourceDatabasesModified"]=True
        report["studentDataTouched"]=False
        report["released"]=False
        write("sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json",report)
    print(json.dumps({"mode":"STAGED" if stage else "CHECK",
      "years":outcome,"c35Candidate":CROP_PATH,"c35CandidateSha256":new_sha,
      "g5Required":11,"officialAnswerVerifiedAdded":0,
      "releaseAllowed":False,"integrationReady":False},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    a=p.parse_args()
    apply(a.stage)
