#!/usr/bin/env python3
"""Review 107 09-1 Q49/50 source page8 against two immutable crop candidates;
verify Q49 exact Visual Basic code text, preserve old extraction, keep Q50 diagram G2 pending.
Not external human review. No answers verified, no release, no student writes.
"""
import difflib,hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from stage_107_e32_35_source_pixel_crops import update_db
from audit_105_115_sqlite_readonly import audit_year

ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/107/"
SOURCE="sudu/data/original/107/09-1/p008-8e8d72b201-v2-w1400-q66.webp"
SOURCE_BLOB="25d1ec2105a71286828f52d1d6af2dd6720f7424"
PDF_SHA="8e8d72b2016553f29184fd3795dab4a6f4ed0bc57e9cb861c9ce2ccf5b0bc2db"
CROPS={49:[90,169,1310,548],50:[90,554,1310,944]}
EVIDENCE=BASE+"qa-drafts/DIRECT_VISUAL_107_09_1_Q49_50_AND_Q49_TEXT_20261024.json"
Q49="執行下列 Visual Basic 程式片段後，陣列元素 A(3)的值為何？\nDim X, Y As Integer\nDim A(6) As Integer\nFor X = 1 To 6\n    A(1) = 1\n    A(X) = 0\n    For Y = X - 1 To 2 Step -1\n        A(Y) = A(Y - 1) + A(Y)\n    Next Y\nNext X"
OPTIONS=["3","4","6","10"]
def at(x):
    p=(ROOT/x).resolve()
    assert p.is_relative_to(ROOT.resolve())
    return p
def sha(b):return hashlib.sha256(b).hexdigest()
def load(x):return json.loads(at(x).read_text(encoding="utf8"))
def save(x,d):at(x).write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def by(rows):
    z={v["questionId"]:v for v in rows}
    assert len(z)==len(rows)
    return z
def run():
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    data={n:load(BASE+n) for n in ["questions.json","webp-manifest.json","ocr-raw-candidates.json",
          "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json"]}
    bank=data["questions.json"];m=data["webp-manifest.json"]
    o=data["ocr-raw-candidates.json"];v=data["VISUAL_QA.json"]
    inv=data["inventory.json"];val=data["VALIDATION.json"]
    rel=data["release-manifest.json"]
    assert len(bank["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==191 and inv["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    qs=by(bank["questions"]);imgs=by(m["items"]);ocr=by(o["items"]);vis=by(v["items"])
    src=at(SOURCE).read_bytes()
    assert hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()==SOURCE_BLOB
    records=[]
    with Image.open(io.BytesIO(src)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for num,box in CROPS.items():
            id=f"107-09-1-{num:02d}"
            item=imgs[id];row=qs[id];r=vis[id]
            assert item["sourcePage"]==8 and item["source"]==SOURCE
            assert item["officialQuestionPdfSha256"]==PDF_SHA
            assert item["cropPixels"]==box and item["sourcePageWebpSha256"]==sha(src)
            assert item["qaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
            assert row["assets"]["sha256"]==item["outputSha256"]
            raw=at(item["output"]).read_bytes()
            assert sha(raw)==item["outputSha256"]
            with Image.open(io.BytesIO(raw)) as crop:
                crop.load()
                assert crop.size==(box[2]-box[0],box[3]-box[1])
                assert ImageChops.difference(page.crop(tuple(box)).convert("RGB"),crop.convert("RGB")).getbbox() is None
            assert row["answerVerified"] is False and row["integrationReady"] is False
            rec={"questionId":id,"sourcePage":8,"cropPixels":box,
                 "sourceWebp":SOURCE,"sourceWebpSha256":sha(src),
                 "candidateWebp":item["output"],"candidateSha256":sha(raw),
                 "reviewedResult":"PASS_DIRECT_SOURCE_PIXEL_AND_VISUAL",
                 "observed":"Q49 complete VB program and A-D numeric options, excludes Q50" if num==49 else
                            "Q50 full HTML code plus all four large diagram choices, excludes Q49 and printed blank-page section"}
            records.append(rec)
    if all(imgs[f"107-09-1-{n:02d}"]["qaStatus"]=="PASS" for n in (49,50)):
        assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==6
        assert inv["ocrTextIndependentlyVerified"]==5
        assert at(EVIDENCE).is_file()
        print(json.dumps({"mode":"IDEMPOTENT","newG1":0,"NO_RELEASE":True}))
        return
    assert all(imgs[f"107-09-1-{n:02d}"]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA" for n in (49,50))
    assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==4
    assert inv["ocrTextIndependentlyVerified"]==val["ocrTextVerified"]==4
    assert ocr["107-09-1-49"]["rawOcrText"] is None
    assert ocr["107-09-1-49"]["qaStatus"]=="PENDING"
    assert qs["107-09-1-49"]["questionVerified"] is False
    assert qs["107-09-1-50"]["questionVerified"] is False
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    proof_base={"reference":EVIDENCE,"reviewer":"ChatGPT assistant",
                "independentHumanReview":False,"reviewedAt":now,"sourcePage":8,
                "sourceSha256":sha(src),"method":"assistant_original_printed_page8_direct_visual_and_sha_pixel_comparison"}
    for row in records:
        id=row["questionId"]
        image=imgs[id]
        image["qaStatus"]="PASS"
        image["visualReviewEvidence"]={**proof_base,
                  "reviewedSha256":row["candidateSha256"],"cropPixels":row["cropPixels"]}
        qs[id]["imageQaStatus"]="PASS"
        vis[id].update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EVIDENCE})
    q=qs["107-09-1-49"];r=ocr["107-09-1-49"]
    assert len(r["legacyOptions"])==4
    old=q["question"]+"\n"+"\n".join(r["legacyOptions"])
    new=Q49+"\n"+"\n".join(OPTIONS)
    diff="".join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
       fromfile="legacy-PDF-layer-preserved",tofile="original-source-corrected"))
    q["legacyUnverifiedQuestion"]=q["question"];q["legacyUnverifiedOptions"]=q["options"]
    q.update({"question":Q49,"options":OPTIONS,"ocrStatus":"PASS_REVIEWED_ORIGINAL_PAGE_IMAGE",
              "textQaStatus":"PASS","textQaEvidence":EVIDENCE,"questionVerified":True})
    r.update({"correctedQuestion":Q49,"correctedOptions":OPTIONS,
              "diff":diff,"qaStatus":"PASS","qaReviewer":"ChatGPT assistant",
              "qaReviewedAt":now,"qaEvidencePath":EVIDENCE})
    assert r["rawOcrText"] is None,"Do not invent raw OCR"
    # Q50 has diagram choices, and must remain image-only G2 pending, not falsely verified.
    inv["visualQaPass"]=v["passCount"]=val["imageVisualQaPass"]=6
    inv["ocrTextIndependentlyVerified"]=inv["textQaPass"]=val["ocrTextVerified"]=5
    rel["imageQA"]="PARTIAL_6_OF_204"
    ev={"schemaVersion":1,"year":107,"paperCode":"09-1",
        "reviewedAt":now,"reviewer":"ChatGPT assistant","independentHumanReview":False,
        "officialPdfSha256ClaimFromExistingRepository":PDF_SHA,
        "sourceOfficialPageImageGitBlob":SOURCE_BLOB,
        "sourcePageSha256":sha(src),"sourcePage":8,
        "newIndividualG1Pass":2,"newQ49TextG2Pass":1,"q50TextG2Status":"PENDING_IMAGE_DIAGRAM_OPTIONS",
        "q49LegacyQuestion":q["legacyUnverifiedQuestion"],
        "q49LegacyOptions":q["legacyUnverifiedOptions"],
        "q49CorrectedQuestion":Q49,"q49CorrectedOptions":OPTIONS,
        "q49TextUnifiedDiff":diff,
        "newAnswerVerified":0,"releaseAllowed":False,"integrationReady":False,
        "records":records}
    for file in ("questions.json","webp-manifest.json","ocr-raw-candidates.json",
                 "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json"):
        save(BASE+file,data[file])
    save(EVIDENCE,ev)
    update_db(bank)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audits)
    gpath="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    report=load(gpath)
    report.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                   "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    save(gpath,report)
    print(json.dumps({"newG1Pass":2,"newG2Pass":1,"year107G1":6,"year107G2":5,
      "g5Years":11,"newOfficialAnswerVerified":0,"releaseAllowed":False}))
if __name__=="__main__":run()
