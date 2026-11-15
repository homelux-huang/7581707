#!/usr/bin/env python3
"""G1 for 106 Chinese Q35 v4 after real review of P7 against new single-question crop.
Do not promote G2/G3 beyond existing independent text work or any release status.
Old mixed V1 remains in Git for traceability. Human independent review: false.
"""
import hashlib,io,json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from link_106_c14_20_existing_webp_drafts import db_rebuild
from audit_105_115_sqlite_readonly import audit_year
ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/106/"
ID="106-00-C-35"
ORIGINAL="sudu/data/original/106/00-C/p007-93b8ec6eb3-v2-w1400-q66.webp"
NEW="sudu/data/processed/106/qa-drafts/webp-v4/00-C/106-00-C-35.webp"
OLD="sudu/data/processed/106/webp-v1/00-C/106-00-C-35.webp"
EV=BASE+"qa-drafts/DIRECT_VISUAL_106_C35_V4_20261024.json"
PDF_SHA="93b8ec6eb319c8c7f5350ffa6267a2b4aed2f7acb1d1a2a7ca89e38f69ec5476"
SOURCE_SHA="c2094dd3dc2d2c7221be4abf109bb19e0af7d546d79ed1f4a4505d75586fefc7"
BOX=[90,1057,1310,1248]

def sha(x):return hashlib.sha256(x).hexdigest()
def at(p):
    t=(ROOT/p).resolve()
    assert t.is_relative_to(ROOT.resolve())
    return t
def load(p):return json.loads(at(p).read_text("utf8"))
def write(p,d):at(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def run():
    m=load(BASE+"webp-manifest.json")
    q=load(BASE+"questions.json")
    v=load(BASE+"VISUAL_QA.json")
    inv=load(BASE+"inventory.json")
    val=load(BASE+"VALIDATION.json")
    rel=load(BASE+"release-manifest.json")
    ocr=load(BASE+"ocr-raw-candidates.json")
    assert len(m["items"])==len(q["questions"])==len(v["items"])==len(ocr["items"])==204
    manifest={x["questionId"]:x for x in m["items"]}[ID]
    question={x["questionId"]:x for x in q["questions"]}[ID]
    visual={x["questionId"]:x for x in v["items"]}[ID]
    text={x["questionId"]:x for x in ocr["items"]}[ID]
    assert inv["answerOfficialFinalVerified"]==0 and not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    assert question["questionVerified"] is True and text["qaStatus"]=="PASS"
    assert question["answerVerified"] is False and question["integrationReady"] is False
    assert manifest["officialQuestionPdfSha256"]==PDF_SHA
    assert manifest["sourcePage"]==7 and manifest["cropPixels"]==BOX
    assert manifest["output"]==NEW and question["assets"]["singleQuestionWebp"]==NEW
    assert manifest["outputSha256"]==question["assets"]["sha256"]==text["imageSha256"]
    raw=at(ORIGINAL).read_bytes();new=at(NEW).read_bytes();old=at(OLD).read_bytes()
    assert sha(raw)==manifest["sourcePageWebpSha256"]==SOURCE_SHA
    assert sha(new)==manifest["outputSha256"]
    assert sha(old)=="55b57b4a090ecc693550cd585dd1339d36b215fc0e152989ed9458814796d413"
    with Image.open(io.BytesIO(raw)) as src,Image.open(io.BytesIO(new)) as crop:
        src.load();crop.load()
        assert src.size==(1400,1980) and crop.size==(1220,191)
        expected=src.crop(tuple(BOX))
        assert ImageChops.difference(expected.convert("RGB"),crop.convert("RGB")).getbbox() is None
    if manifest["qaStatus"]=="PASS":
        assert visual["status"]=="PASS" and at(EV).is_file()
        assert manifest["visualReviewEvidence"]["reference"]==EV
        assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==16
        print(json.dumps({"mode":"IDEMPOTENT","G1":16,"NO_RELEASE":True}))
        return
    assert manifest["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert question["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA" and visual["status"]=="PENDING"
    assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==15
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    proof={"reference":EV,"reviewedSha256":sha(new),"sourceSha256":sha(raw),
        "reviewer":"ChatGPT assistant","reviewedAt":now,"independentHumanReview":False,
        "sourcePage":7,"cropPixels":BOX,
        "method":"assistant_second_original_page7_to_v4_single_crop_visual_review_and_lossless_pixel_check"}
    manifest.update({"qaStatus":"PASS","visualReviewEvidence":proof})
    manifest["issues"]=["V1_MIXED_Q36_Q38_SHARED_MATERIAL_REPLACED_WITH_V4"]
    question["imageQaStatus"]="PASS"
    question["issues"]=sorted(set(question.get("issues",[])+["V1_MIXED_QUESTION_REPLACED_BY_VALIDATED_V4"]))
    visual.update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":EV})
    inv["visualQaPass"]=v["passCount"]=val["imageVisualQaPass"]=16
    rel["imageQA"]="PARTIAL_16_OF_204"
    evidence={"schemaVersion":1,"year":106,"paperCode":"00-C","questionId":ID,
        "reviewedAt":now,"reviewer":"ChatGPT assistant","independentHumanReview":False,
        "method":"Assistant opened TCTE-source p7 and new v4 crop, directly visually verified full Q35 stem and four choices, no Q36 material; pixel difference zero.",
        "oldV1Path":OLD,"oldV1Sha256":sha(old),"oldV1Defect":"Q35 crop included full Q36-38 passage",
        "sourceOfficialPdfSha256":PDF_SHA,"sourcePage":7,"sourcePageWebp":ORIGINAL,
        "sourcePageWebpSha256":sha(raw),"cropPixels":BOX,
        "newCandidateWebp":NEW,"newCandidateWebpSha256":sha(new),
        "checks":{"question35Number":True,"fullStem":True,"completeABCD":True,
                 "noAdjacentQuestion36":True,"noMixedPassage":True,
                 "noHeaderOrFooter":True,"sharpLegible":True,
                 "sourcePixelDifferenceZero":True,"sha256Correct":True},
        "newIndividualG1Pass":1,"newG2Pass":0,"newAnswerVerified":0,
        "releaseAllowed":False,"integrationReady":False}
    for name,valobj in [("webp-manifest.json",m),("questions.json",q),
        ("VISUAL_QA.json",v),("inventory.json",inv),("VALIDATION.json",val),
        ("release-manifest.json",rel)]:
        write(BASE+name,valobj)
    write(EV,evidence)
    db_rebuild(q)
    audits=[audit_year(y) for y in range(105,116)]
    assert len(audits)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audits)
    p="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    g5=load(p)
    g5.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
               "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(p,g5)
    print(json.dumps({"newG1Pass":1,"year106G1":16,"year106G2":inv["ocrTextIndependentlyVerified"],
                      "g5Years":11,"newAnswerVerified":0,"NO_RELEASE":True}))
if __name__=="__main__":run()
