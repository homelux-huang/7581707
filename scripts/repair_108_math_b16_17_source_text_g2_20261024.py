#!/usr/bin/env python3
"""108 Math B Q16-17 direct original-image G2, preserve G1 and release isolation.
Source is SHA-bound official-page raster and existing G1 verified question crops.
No invented OCR raw; matrix notation is row-by-row with original image fallback.
Answer candidate A stays unverified (no final official notice G3).
"""
import argparse,difflib,hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from stage_108_all_26_missing_original_page_webps import db_rebuild
from audit_105_115_sqlite_readonly import audit_year
ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/108/"
SRC="sudu/data/original/108/00-MB/p003-bcda540c72-v2-w1400-q66.webp"
SRC_BLOB="98769b8e7b656bde3abd55264667ef60c876ec7d"
SRC_SHA="3599ba878ebce5fa685c590b1872ff74a1019d4c8f750e64978294969651f585"
PDF_SHA="bcda540c72f5d88f400aed994d58496e66761466aa5438e54d156c773b25722c"
EVIDENCE=BASE+"qa-drafts/TEXT_QA_108_MATH_B16_17_ORIGINAL_IMAGE_20261024.json"
PLACEHOLDER="本題原卷文字、圖表或公式尚未成功擷取，請點選原始 PDF 對照，不能把此提示當作正式題幹。"
TEXT={
16: {
    "question":"如圖（一）所示，使用8種不同顏色塗在圖中標號A、B、C、D、E的5個格子內，顏色不可重複使用，若規定同一格子僅塗同一顏色，則共可塗出幾種不同的著色樣式？",
    "options":["P⁸₅","C⁸₅","5⁶","6⁵"],
    "crop":[90,1249,1310,1637],
    "sha":"d472b5e3f0c9383ea0585dc7201feec57a050eba8652fa5d108d479b407c90e7",
    "formulaNote":"P⁸₅ denotes ordered selection of 5 different colors from 8; original WebP is authoritative for superscript/subscript typesetting.",
    "graphicNote":"All five regions A B C D E, their touching boundaries and legend 圖（一） are required."
},
17: {
    "question":"若實數x滿足行列式|1−x, 2, 0; 4, 6−2x, 2; 0, 3, 1|＝4，則行列式|2, 3−x, 1; 0, 6, 2; 1−x, −1, −1|＝？",
    "options":["4","−4","8","−8"],
    "crop":[90,1638,1310,1825],
    "sha":"8db038429ad97927dbfa8e989e497c8948254f058f755a09546b31ac8144222e",
    "formulaNote":"Matrices are transcribed exactly as three semicolon-delimited rows, left-to-right in each row. Compare minus signs and 1−x against the official original WebP.",
    "graphicNote":"Preserve both full three-by-three determinants and their outer vertical bars."
},
}
def at(rel):
    p=(ROOT/rel).resolve()
    assert p.is_relative_to(ROOT.resolve()) and not p.is_symlink()
    return p
def sha(data):return hashlib.sha256(data).hexdigest()
def load(rel):return json.loads(at(rel).read_text("utf8"))
def write(rel,d):at(rel).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def index(items):
    d={q["questionId"]:q for q in items}
    assert len(d)==len(items)
    return d
def main(stage):
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    assert branch=="qa/114-115-official-visual-review",branch
    names=["questions.json","ocr-raw-candidates.json","webp-manifest.json",
           "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json"]
    data={n:load(BASE+n) for n in names}
    b=data["questions.json"];o=data["ocr-raw-candidates.json"]
    m=data["webp-manifest.json"];v=data["VISUAL_QA.json"]
    inv=data["inventory.json"];val=data["VALIDATION.json"]
    rel=data["release-manifest.json"]
    assert len(b["questions"])==len(o["items"])==len(m["items"])==len(v["items"])==204
    assert inv["visualQaPass"]==val["imageVisualQaPass"]==v["passCount"]==26
    assert inv["answerOfficialFinalVerified"]==val["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    rows=index(b["questions"]);os=index(o["items"]);ims=index(m["items"]);vs=index(v["items"])
    original=at(SRC).read_bytes()
    assert sha(original)==SRC_SHA
    blob=hashlib.sha1(b"blob "+str(len(original)).encode()+b"\x00"+original).hexdigest()
    assert blob==SRC_BLOB
    old_status={n for n in TEXT if rows[f"108-00-MB-{n}"].get("questionVerified")}
    assert old_status in (set(),set(TEXT)),"Other session partially changed Q16/17; reconcile before write"
    assert inv["ocrTextIndependentlyVerified"]==val["ocrTextVerified"]==5+len(old_status)
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    records=[]
    with Image.open(io.BytesIO(original)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for n,t in TEXT.items():
            id=f"108-00-MB-{n}"
            row=rows[id];ocr=os[id];asset=ims[id];visual=vs[id]
            assert asset["qaStatus"]==row["imageQaStatus"]==visual["status"]=="PASS"
            assert asset["visualReviewEvidence"]["reviewedSha256"]==t["sha"]
            assert asset["sourcePage"]==3 and asset["source"]==SRC
            assert asset["sourcePageWebpSha256"]==SRC_SHA
            assert asset["officialQuestionPdfSha256"]==PDF_SHA
            assert asset["cropPixels"]==t["crop"] and asset["outputSha256"]==t["sha"]
            assert row["assets"]["sha256"]==ocr["imageSha256"]==t["sha"]
            assert not row["answerVerified"] and not row["integrationReady"]
            assert row["answer"]=="A" and row["answerMatched"] is True
            original_crop=at(asset["output"]).read_bytes()
            assert sha(original_crop)==t["sha"]
            with Image.open(io.BytesIO(original_crop)) as candidate:
                candidate.load()
                assert candidate.format=="WEBP"
                assert candidate.size==(t["crop"][2]-t["crop"][0],t["crop"][3]-t["crop"][1])
                assert ImageChops.difference(page.crop(tuple(t["crop"])).convert("RGB"),candidate.convert("RGB")).getbbox() is None
            assert ocr["rawOcrText"] is None,"No invented OCR raw permitted"
            assert ocr["legacyQuestion"]==PLACEHOLDER and ocr["legacyOptions"]==[]
            assert len(t["options"])==4 and all(s.strip() for s in t["options"])
            diff="".join(difflib.unified_diff(
                [ocr["legacyQuestion"]+"\n"]+[x+"\n" for x in ocr["legacyOptions"]],
                [t["question"]+"\n"]+[x+"\n" for x in t["options"]],
                fromfile="legacy-source-placeholder",tofile="image-reviewed-text"
            ))
            assert diff
            records.append({
                "questionId":id,"sourcePage":3,"sourcePageWebp":SRC,"sourcePageSha256":SRC_SHA,
                "sourceGitBlob":SRC_BLOB,"originalPdfSha256Claim":PDF_SHA,
                "cropPixels":t["crop"],"singleQuestionWebp":asset["output"],
                "singleQuestionWebpSha256":t["sha"],"sourcePixelDifferenceZero":True,
                "legacyQuestion":ocr["legacyQuestion"],"legacyOptions":ocr["legacyOptions"],
                "correctedQuestion":t["question"],"correctedOptions":t["options"],
                "unifiedDiff":diff,"formulaNote":t["formulaNote"],
                "graphicNote":t["graphicNote"],
                "rawOcrText":None,"rawOcrNeverFabricated":True,
                "imageQaExistingPass":True,"textQaResult":"PASS_DIRECT_SOURCE_IMAGE_REVIEW",
                "officialAnswerStillUnverified":True
            })
            if old_status:
                assert row["question"]==t["question"] and row["options"]==t["options"]
                assert ocr["correctedQuestion"]==t["question"] and ocr["correctedOptions"]==t["options"]
            elif stage:
                assert row["question"]==PLACEHOLDER and row["options"]==[]
                row["legacyUnverifiedQuestion"]=row["question"]
                row["legacyUnverifiedOptions"]=row["options"]
                row.update({"question":t["question"],"options":t["options"],
                    "questionVerified":True,"textQaStatus":"PASS",
                    "textQaEvidence":EVIDENCE,"ocrStatus":"PASS_REVIEWED_ORIGINAL_PAGE_IMAGE"})
                ocr.update({"correctedQuestion":t["question"],"correctedOptions":t["options"],
                    "diff":diff,"qaStatus":"PASS","qaReviewer":"ChatGPT assistant",
                    "qaReviewedAt":now,"qaEvidencePath":EVIDENCE})
    if old_status:
        assert at(EVIDENCE).is_file()
        print(json.dumps({"mode":"IDEMPOTENT","newG2":0,"G2":7,"NO_RELEASE":True}))
        return
    if stage:
        inv["ocrTextIndependentlyVerified"]=inv["textQaPass"]=val["ocrTextVerified"]=7
        rel["questionTextQA"]="PARTIAL_7_OF_204"
        e={"schemaVersion":1,"year":108,"paperCode":"00-MB","reviewedAt":now,
           "reviewer":"ChatGPT assistant","independentHumanReview":False,
           "method":"Actual source page3/individual Q16/Q17 visual transcription; SHA/pixel proof; formal-matrix row/column preservation",
           "sourceOriginalOfficialPdfDownloadedAgain":False,
           "newG2Pass":2,"newG1Pass":0,"newOfficialFinalAnswerVerified":0,
           "releaseAllowed":False,"integrationReady":False,"records":records}
        for key in names:write(BASE+key,data[key])
        write(EVIDENCE,e)
        db_rebuild(b)
        reportpath="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
        g5=load(reportpath)
        audits=[audit_year(y) for y in range(105,116)]
        assert len(audits)==11 and all(r["g5Pass"] and r["sandboxImportPasses"]==2 for r in audits)
        g5.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                   "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
        write(reportpath,g5)
    print(json.dumps({"mode":"STAGED" if stage else "CHECK","newG2":2,"year108G2":7,
                      "year108G1":26,"year108FinalOfficialAnswerVerified":0,
                      "G5YearsRequired":11,"NO_RELEASE":True},ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stage",action="store_true")
    main(p.parse_args().stage)
