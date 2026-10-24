#!/usr/bin/env python3
"""Apply assistant-direct reviewed 107 Chinese 13 question + 3 shared G1 evidence.
Checks current selected v3/v4 WebPs source pixels, versioned SHA, all A-D, source
page; image pass does NOT verify question text, official final answer or G6.
Independent human review=false. No students, merge or deploy.
"""
import hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from stage_107_c08_16_c35_38_original_page_crops import (
    PAGE,IDS,SHARED,at,read,write,sha,update_db
)
from audit_105_115_sqlite_readonly import audit_year
BASE="sudu/data/processed/107/"
REVIEW=BASE+"qa-drafts/DIRECT_VISUAL_107_CHINESE_13_3_SHARED_20261024.json"
OBS={
 "107-00-C-08":"Full flower-market prose and A-D, no Q9",
 "107-00-C-09":"Full Hawking universe article and A-D, no Q10",
 "107-00-C-10":"Full ancient market passage and A-D, no Q11",
 "107-00-C-11":"Word cloud 甲/乙 plus all four combinations, no Q12",
 "107-00-C-12":"Original two postcard graphics 甲/乙 plus A-D",
 "107-00-C-13":"A-D including D after versioned v4 boundary repair, table in shared",
 "107-00-C-14":"Four examples and A-D matrix, no Q13 D after v4",
 "107-00-C-15":"Short question and four options, shared article separately in v4",
 "107-00-C-16":"Four options complete, no following Q17 paragraph after v4",
 "107-00-C-35":"Only Q35 and A-D, before shared Q36-38",
 "107-00-C-36":"Full 小康/大同 stem and all A-D",
 "107-00-C-37":"Four fill-in interpretations, no Q38 after v4",
 "107-00-C-38":"Full 論語 question and A-D, excludes writing test",
 "107-00-C-SHARED-13-14":"Entire Western cartoon culture 甲/乙 comparative table including final row",
 "107-00-C-SHARED-15-16":"Two complete poem extracts 甲/乙 and definition note after v4",
 "107-00-C-SHARED-36-38":"Both 大同/小康 articles 甲/乙 and source citations, no question stems",
}
def by(items,key):
    z={x[key]:x for x in items}
    assert len(z)==len(items)
    return z
def run():
    assert subprocess.check_output(["git","branch","--show-current"],cwd=Path(__file__).resolve().parents[1],text=True).strip()=="qa/114-115-official-visual-review"
    d={x:read(BASE+x) for x in ("webp-manifest.json","questions.json","VISUAL_QA.json",
       "inventory.json","VALIDATION.json","release-manifest.json")}
    m=d["webp-manifest.json"];b=d["questions.json"];v=d["VISUAL_QA.json"]
    inv=d["inventory.json"];val=d["VALIDATION.json"];rel=d["release-manifest.json"]
    assert len(m["items"])==len(b["questions"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==204 and inv["answerOfficialFinalVerified"]==0
    assert inv["ocrTextIndependentlyVerified"]==5
    assert len(m["sharedMaterialCrops"])==len(b["sharedMaterials"])==len(v["sharedMaterials"])==5
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    mm=by(m["items"],"questionId");qq=by(b["questions"],"questionId")
    vv=by(v["items"],"questionId")
    ms=by(m["sharedMaterialCrops"],"sharedMaterialId")
    qs=by(b["sharedMaterials"],"sharedMaterialId")
    vs=by(v["sharedMaterials"],"sharedMaterialId")
    reviewed=[]
    for id in IDS+list(SHARED):
        shared=id in SHARED
        img=ms[id] if shared else mm[id]
        assert img["qaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
        assert img["output"].startswith(f"{BASE}qa-drafts/webp-v")
        assert img["sourcePage"] in (3,4,8)
        page=img["sourcePage"]
        expected_src,expected_blob=PAGE[page]
        assert img["source"]==expected_src and img["sourcePageGitBlob"]==expected_blob
        raw=at(expected_src).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==expected_blob
        assert sha(raw)==img["sourcePageWebpSha256"]
        image=at(img["output"]).read_bytes()
        assert sha(image)==img["outputSha256"]
        with Image.open(io.BytesIO(raw)) as src,Image.open(io.BytesIO(image)) as crop:
            src.load();crop.load()
            assert src.size==(1400,1980)
            assert crop.size==tuple(img["outputSize"])
            assert ImageChops.difference(src.crop(tuple(img["cropPixels"])).convert("RGB"),crop.convert("RGB")).getbbox() is None
        if shared:
            assert qs[id]["qaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
        else:
            assert qq[id]["assets"]["sha256"]==img["outputSha256"]
            assert not qq[id]["answerVerified"] and not qq[id]["integrationReady"]
            assert qq[id]["imageQaStatus"] in ("DRAFT_NEEDS_DIRECT_VISUAL_QA","PASS")
        reviewed.append({"questionIdOrSharedId":id,"sourcePage":page,
            "sourceWebp":expected_src,"sourcePageSha256":sha(raw),
            "officialQuestionPdfSha256":img["officialQuestionPdfSha256"],
            "candidateWebp":img["output"],"cropPixels":img["cropPixels"],
            "reviewedSha256":sha(image),"visualObservation":OBS[id],
            "result":"PASS","sourcePixelDifferenceZero":True})
    if all(mm[id]["qaStatus"]=="PASS" for id in IDS):
        assert all(ms[id]["qaStatus"]=="PASS" for id in SHARED)
        assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==19
        assert inv["sharedMaterialsVerified"]==5 and at(REVIEW).is_file()
        print(json.dumps({"mode":"IDEMPOTENT","g1Pass":19,"shared":5,"NO_RELEASE":True}))
        return
    assert all(mm[id]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA" for id in IDS)
    assert all(ms[id]["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA" for id in SHARED)
    assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==6
    assert inv["sharedMaterialsVerified"]==2
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    for ev in reviewed:
        id=ev["questionIdOrSharedId"];shared=id in SHARED
        img=ms[id] if shared else mm[id]
        proof={"reference":REVIEW,"reviewer":"ChatGPT assistant","reviewedAt":now,
             "independentHumanReview":False,
             "reviewedSha256":ev["reviewedSha256"],"sourceSha256":ev["sourcePageSha256"],
             "sourcePage":ev["sourcePage"],"cropPixels":ev["cropPixels"],
             "method":"assistant_direct_original_page_and_exact_sha_bound_crop_visual_review"}
        img["qaStatus"]="PASS"
        img["visualReviewEvidence"]=proof
        if shared:
            qs[id]["qaStatus"]="PASS"
            qs[id]["visualReviewEvidence"]=proof.copy()
            vs[id].update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":REVIEW})
        else:
            qq[id]["imageQaStatus"]="PASS"
            vv[id].update({"status":"PASS","reviewer":"ChatGPT assistant","visualEvidence":REVIEW})
    inv["visualQaPass"]=v["passCount"]=val["imageVisualQaPass"]=19
    inv["sharedMaterialsVerified"]=5
    rel["imageQA"]="PARTIAL_19_OF_204"
    document={"schemaVersion":1,"year":107,"paperCode":"00-C",
       "reviewer":"ChatGPT assistant","independentHumanReview":False,
       "reviewedAt":now,
       "method":"Assistant independently opened original TCTE printed pages 3,4,8 and each current SHA-bound 13 single-question, 3 shared versioned crop image. Corrected six first-pass failures before G1.",
       "sourcePages":[3,4,8],
       "sourceOfficialPdfShaFromRepositoryOnly":True,
       "items":reviewed,"newIndividualG1Pass":13,"newSharedG1Pass":3,
       "newG2Pass":0,"newOfficialFinalAnswersVerified":0,
       "releaseAllowed":False,"integrationReady":False}
    for name in ("webp-manifest.json","questions.json","VISUAL_QA.json",
                 "inventory.json","VALIDATION.json","release-manifest.json"):
        write(BASE+name,d[name])
    write(REVIEW,document)
    update_db(b)
    audited=[audit_year(y) for y in range(105,116)]
    assert len(audited)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audited)
    global_audit="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
    db=read(global_audit)
    db.update({"years":audited,"yearsG5Pass":11,"yearsReviewed":11,
               "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
    write(global_audit,db)
    print(json.dumps({"year":107,"newG1Question":13,"newG1Shared":3,
        "yearG1Pass":19,"yearSharedVerified":5,"G2Unchanged":5,
        "newFinalOfficialAnswersVerified":0,"G5PassYears":11,
        "released":False}))
if __name__=="__main__":run()
