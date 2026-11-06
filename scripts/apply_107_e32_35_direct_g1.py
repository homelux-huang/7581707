#!/usr/bin/env python3
"""Promote 107 English Q32-35 and TWO shared passages after actual visual review.

Separate source page6 was opened and compared visually to the six candidate
original-pixel WebP images. No human third-party endorsement is implied.
QA of Q36/Q37 remains PENDING even when shared Golden Horse article passes.
"""
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from audit_105_115_sqlite_readonly import audit_year
from stage_107_e32_35_source_pixel_crops import read,write,sha,update_db,ROOT,BASE,SRC,IDS,SHARED,PDF_SHA,EVIDENCE
REV="sudu/data/processed/107/qa-drafts/DIRECT_VISUAL_107_E32_35_SHARED_20261024.json"

def run():
    ledger=read(EVIDENCE)
    m=read("sudu/data/processed/107/webp-manifest.json")
    q=read("sudu/data/processed/107/questions.json")
    v=read("sudu/data/processed/107/VISUAL_QA.json")
    inventory=read("sudu/data/processed/107/inventory.json")
    validation=read("sudu/data/processed/107/VALIDATION.json")
    release=read("sudu/data/processed/107/release-manifest.json")
    o=read("sudu/data/processed/107/ocr-raw-candidates.json")
    assert len(m["items"])==len(q["questions"])==len(v["items"])==204
    assert inventory["visualQaPass"]==v["passCount"]==validation["imageVisualQaPass"]==0
    assert inventory["webpGeneratedDrafts"]==189 and inventory["answerOfficialFinalVerified"]==0
    assert release["releaseAllowed"] is False and release["integrationReady"] is False
    assert set(ledger["candidateCrops"])==set(IDS)|set(SHARED)
    assert ledger["sourceGitBlob"]=="f87703a9bcf3d038f9da350e4fc41eae5cc73c47"
    assert ledger["officialQuestionPdfSha256"]==PDF_SHA
    mmap={x["questionId"]:x for x in m["items"]}
    questions={x["questionId"]:x for x in q["questions"]}
    visual={x["questionId"]:x for x in v["items"]}
    shared={x["sharedMaterialId"]:x for x in m["sharedMaterialCrops"]}
    bshared={x["sharedMaterialId"]:x for x in q["sharedMaterials"]}
    vshared={x["sharedMaterialId"]:x for x in v["sharedMaterials"]}
    reviewer="ChatGPT assistant"
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    evidence={"schemaVersion":1,"year":107,"paperCode":"00-E",
       "officialPdfSha256":PDF_SHA,"reviewedAt":now,"reviewer":reviewer,
       "independentHumanReview":False,"sourcePrintedPage":6,
       "method":"Assistant visually opened original TCTE printed page6 and all six SHA-bound lossless single/shared crops; compared exact A-D and passage text/table",
       "criteria":{"questionNumber":True,"fullStem":True,"allABCD":True,
          "noAdjacentQuestion":True,"noHeaderOrFooter":True,"sharpness":True,
          "completeSharedMaterial":True,"sourceAndCandidateSHA":True},
       "specificObservations":{
          "107-00-E-32":"Only question32 'On which day is it most likely to rain?' and Monday/Tuesday/Thursday/Friday options.",
          "107-00-E-33":"Only question33 Hualien two-day trip and all four day-range options, no question34.",
          "107-00-E-34":"Only question34 about Chi Po-lin recording Typhoon Morakot and complete A-D.",
          "107-00-E-35":"Only question35 raising closest meaning with A collecting B lifting C moving D promoting.",
          "107-00-E-SHARED-32-33":"Full Hualien five-day weather forecast, Monday through Friday, all 10%,0%,30%,80%,40%, diagrams and title. No Q32 stem.",
          "107-00-E-SHARED-34-37":"Full Golden Horse Chi Po-lin Beyond Beauty Taiwan from Above English passage, glossary documentary, no Q34 stem. Linked to 34-37; 36-37 remain pending independent question QA."},
       "items":[],"newG1QuestionPass":4,"newG1SharedPass":2,
       "newOCRQA":0,"newVerifiedAnswers":0,"releaseAllowed":False,"integrationReady":False
    }
    for id in IDS+list(SHARED):
        isshared=id in SHARED
        item=shared[id] if isshared else mmap[id]
        crop=ledger["candidateCrops"][id]
        assert crop["sourcePage"]==item["sourcePage"]==6
        assert crop["outputSha256"]==item["outputSha256"]
        assert sha((ROOT/crop["output"]).read_bytes())==item["outputSha256"]
        assert sha((ROOT/crop["source"]).read_bytes())==item["sourcePageWebpSha256"]
        assert crop["cropPixels"]==item["cropPixels"]
        assert item["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        ev={"questionIdOrSharedId":id,"sourcePage":6,
            "officialPdfSha256":PDF_SHA,"sourceWebp":SRC,
            "sourceWebpSha256":item["sourcePageWebpSha256"],
            "cropPixels":item["cropPixels"],"candidateWebp":item["output"],
            "reviewedSha256":item["outputSha256"],"result":"PASS",
            "reviewer":reviewer,"reviewedAt":now}
        evidence["items"].append(ev)
        proof={"reference":REV,"reviewedSha256":item["outputSha256"],
              "sourceSha256":item["sourcePageWebpSha256"],
              "reviewer":reviewer,"reviewedAt":now,"independentHumanReview":False,
              "sourcePage":6,"cropPixels":item["cropPixels"],
              "method":"assistant_direct_visual_original_pdf_pixel_webp_compare"}
        item["qaStatus"]="PASS"
        item["visualReviewEvidence"]=proof
        if isshared:
            bshared[id]["qaStatus"]="PASS"
            bshared[id]["visualReviewEvidence"]=proof.copy()
            vshared[id].update({"status":"PASS","reviewer":reviewer,"visualEvidence":REV})
        else:
            assert questions[id]["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
            assert questions[id]["questionVerified"] is False and questions[id]["answerVerified"] is False
            questions[id]["imageQaStatus"]="PASS"
            visual[id].update({"status":"PASS","reviewer":reviewer,"visualEvidence":REV})
    for n in (36,37):
        qq=questions[f"107-00-E-{n:02d}"]
        assert qq["sharedMaterialIds"]==["107-00-E-SHARED-34-37"]
        assert qq["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA", "Do not infer G1 from article"
    inventory["visualQaPass"]=4
    inventory["sharedMaterialsVerified"]=2
    validation["imageVisualQaPass"]=4
    v["passCount"]=4
    release["imageQA"]="PARTIAL_4_OF_204"
    for path,info in [
        ("sudu/data/processed/107/webp-manifest.json",m),
        ("sudu/data/processed/107/questions.json",q),
        ("sudu/data/processed/107/VISUAL_QA.json",v),
        ("sudu/data/processed/107/inventory.json",inventory),
        ("sudu/data/processed/107/VALIDATION.json",validation),
        ("sudu/data/processed/107/release-manifest.json",release),
        (REV,evidence)
    ]:
        write(path,info)
    update_db(q)
    all_g5=[audit_year(y) for y in range(105,116)]
    assert len(all_g5)==11 and all(x["g5Pass"] for x in all_g5)
    globalG5="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    report=read(globalG5)
    assert report["yearsG5Pass"]==11 and report["yearsReviewed"]==11
    report["years"]=all_g5
    report["sourceDatabasesModified"]=True
    report["studentDataTouched"]=False
    report["released"]=False
    write(globalG5,report)
    print(json.dumps({"year":107,"newSingleImageG1Pass":4,
                      "newIndependentSharedG1Pass":2,"g5Years":11,
                      "stillUnverifiedAnswers":204,
                      "newTextQa":0,"releaseAllowed":False}))

if __name__=="__main__":
    run()
