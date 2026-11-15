#!/usr/bin/env python3
"""Apply assistant-direct inspected 106 Chinese Q36-38 + shared passage G1 evidence.

Prior to workflow authored direct visual inspection compared printed original
WebP P7/P8 and generated lossless exact crops; record self/assistant reviewer
unambiguously, independentHumanReview=false. NO OCR/answer/question verification
or final release. Use immutable SHA and pixel source copy, keep all prior assets.
"""
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from link_106_c14_20_existing_webp_drafts import read,write,sha,db_rebuild
from audit_105_115_sqlite_readonly import audit_year

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/106"
EVIDENCE=BASE/"qa-drafts/DIRECT_VISUAL_106_C36_38_SHARED_20261024.json"
EVIDENCE_REL=EVIDENCE.relative_to(ROOT).as_posix()
YEAR=106
IDS=[f"106-00-C-{n:02d}" for n in (36,37,38)]
SID="106-00-C-SHARED-36-38"

def main():
    m=read(BASE/"webp-manifest.json")
    b=read(BASE/"questions.json")
    v=read(BASE/"VISUAL_QA.json")
    inv=read(BASE/"inventory.json")
    val=read(BASE/"VALIDATION.json")
    rel=read(BASE/"release-manifest.json")
    raw=read(BASE/"ocr-raw-candidates.json")
    led=read(BASE/"qa-drafts/DRAFT_106_C36_38_SHARED_CROSSPAGE_20261024.json")
    im={x["questionId"]:x for x in m["items"]}
    qs={x["questionId"]:x for x in b["questions"]}
    vis={x["questionId"]:x for x in v["items"]}
    shared={x["sharedMaterialId"]:x for x in m["sharedMaterialCrops"]}
    bankshared={x["sharedMaterialId"]:x for x in b["sharedMaterials"]}
    visShared={x["sharedMaterialId"]:x for x in v["sharedMaterials"]}
    assert len(m["items"])==len(b["questions"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==204 and inv["visualQaPass"]==12
    assert v["passCount"]==12 and val["imageVisualQaPass"]==12
    assert SID in shared and SID in bankshared and SID in visShared
    assert m["sharedMaterialCrops"][-1]["sharedMaterialId"]==SID
    assert led["candidateCrops"] and led["questionCandidatesCreated"]==3
    assert all(im[qid]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
               and qs[qid]["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
               and vis[qid]["status"]=="PENDING"
               and not qs[qid]["questionVerified"] and not qs[qid]["answerVerified"]
               and not qs[qid]["integrationReady"] for qid in IDS)
    assert shared[SID]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert bankshared[SID]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert visShared[SID]["status"]=="PENDING"
    assert rel["releaseAllowed"] is False and rel["integrationReady"] is False
    reviewer="ChatGPT assistant"
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    evidence={
      "schemaVersion":1,"reviewDate":now,"reviewer":reviewer,
      "independentHumanReview":False,"year":106,
      "paperCode":"00-C","officialPdfSha256":led["sourceOfficialPdfSha256"],
      "sourceInspectionPages":[7,8],"imageVisualQaResult":"PASS_ASSISTANT_DIRECT_SOURCE_CROP",
      "newIndividualQaPassCount":3,"newSharedQaPassCount":1,
      "method":"actual visual side-by-side of source original printed pages 7/8 and immutable lossless source-pixel WebPs; verified in chat session + GitHub cropped source byte/pixel SHA",
      "notAnIndependentExternalHumanAudit":True,
      "criteria":{"originalQuestionNumber":True,"completeStem":True,
                 "allOptionsABCD":True,"allNecessaryTablesAndGraphics":True,
                 "noAdjacentQuestion":True,"noPrintedHeaderOrFooter":True,
                 "sharpLegible":True,"sourceAndCropShaBound":True,
                 "crossPageSharedPassageIndividuallyReviewed":True},
      "specificObservations":{
       "106-00-C-36":"Image contains only printed question 36 and complete A-D comparing prose甲、乙, page 8. No question37.",
       "106-00-C-37":"Image contains only printed question37 and complete A-D, 莊子藏天下於天下 vs 蘇軾自其不變者而觀之.",
       "106-00-C-38":"Image contains only question38 and A心有拘執 B天下無道 C藏才隱智 D物我無盡. Excludes writing essay section.",
       SID:"Original printed page7 passage starting ▲閱讀下文回答第36–38題, complete 甲蘇軾赤壁賦 and 乙改寫李一冰蘇東坡新傳, ending exactly before page footer. Separately linked Q36-38."},
      "items":[],
      "answerVerifiedChange":0,"questionVerifiedChange":0,
      "newOcrTextQaPass":0,"releaseAllowed":False,"integrationReady":False
    }
    for name in IDS+[SID]:
        item=shared[name] if name==SID else im[name]
        c=led["candidateCrops"][name]
        output=ROOT/c["output"]
        source=ROOT/c["source"]
        assert output.is_file() and source.is_file()
        assert sha(output.read_bytes())==c["outputSha256"]
        assert sha(source.read_bytes())==c["sourcePageWebpSha256"]
        assert item["outputSha256"]==c["outputSha256"]
        assert item["sourcePage"]==c["sourcePage"]
        assert item["cropPixels"]==c["cropPixels"]
        e={"questionIdOrSharedId":name,"sourcePage":c["sourcePage"],
           "sourcePath":c["source"],"sourceSha256":c["sourcePageWebpSha256"],
           "originalOfficialPdfSha256":c["officialQuestionPdfSha256"],
           "cropPixels":c["cropPixels"],"candidateWebpPath":c["output"],
           "reviewedSha256":c["outputSha256"],"result":"PASS",
           "reviewer":reviewer,"reviewedAt":now}
        evidence["items"].append(e)
        proof={"reference":EVIDENCE_REL,"reviewedSha256":c["outputSha256"],
               "sourceSha256":c["sourcePageWebpSha256"],"reviewer":reviewer,
               "reviewedAt":now,"independentHumanReview":False,
               "sourcePage":c["sourcePage"],"cropPixels":c["cropPixels"],
               "method":"direct_original_printed_page_to_extracted_lossless_WebP_visual_compare",
               "noAdjacentQuestion":True,"completeOptions":True}
        item["qaStatus"]="PASS"
        item["visualReviewEvidence"]=proof
        if name==SID:
            bankshared[SID]["qaStatus"]="PASS"
            bankshared[SID]["visualReviewEvidence"]=proof.copy()
            visShared[SID].update({"status":"PASS","reviewer":reviewer,"visualEvidence":EVIDENCE_REL})
        else:
            qs[name]["imageQaStatus"]="PASS"
            assert qs[name]["answerVerified"] is False and qs[name]["questionVerified"] is False
            vis[name].update({"status":"PASS","reviewer":reviewer,"visualEvidence":EVIDENCE_REL})
    v["passCount"]=15
    inv["visualQaPass"]=15
    inv["sharedMaterialsVerified"]=1
    val["imageVisualQaPass"]=15
    rel["imageQA"]="PARTIAL_15_OF_204"
    assert inv["answerOfficialFinalVerified"]==0 and val["answerOfficialFinalVerified"]==0
    assert not inv["integrationReady"] and not rel["integrationReady"]
    for path,data in [
       (BASE/"webp-manifest.json",m),(BASE/"questions.json",b),
       (BASE/"VISUAL_QA.json",v),(BASE/"inventory.json",inv),
       (BASE/"VALIDATION.json",val),(BASE/"release-manifest.json",rel),
       (EVIDENCE,evidence)]:
        write(path,data)
    # G5 must reflect changed image-QA flags but not promote any G2 or G3 evidence.
    db_rebuild(b)
    report=read(ROOT/"sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json")
    assert report["yearsReviewed"]==11 and report["yearsG5Pass"]==11
    status=[audit_year(y) for y in range(105,116)]
    assert len(status)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in status)
    report["years"]=status
    report["sourceDatabasesModified"]=True
    report["studentDataTouched"]=False
    report["released"]=False
    report["yearsG5Pass"]=11
    write(ROOT/"sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json",report)
    print(json.dumps({"G1newSinglePass":3,"G1newSharedPass":1,
                      "year106WebpCandidates":204,"year106ImageQaPass":15,
                      "year106FinalAnswers":0,"year106TextQaNew":0,
                      "sqliteG5Years":11,"released":False},ensure_ascii=False))

if __name__=="__main__":
    main()
