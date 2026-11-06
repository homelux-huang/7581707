#!/usr/bin/env python3
"""Register six ACTUALLY visually checked official 106 English image crops.

Safe scope: isolated QA branch and staging 106 JSON, image ledger and SQLite.
Never edits original/source WebPs, main, UI, student records or official answers.
"""
import argparse,hashlib,json,sqlite3,subprocess
from pathlib import Path
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/106")
EVID=BASE/"qa-drafts/QA_106_EN_Q13_18_DIRECT_VISUAL_SHA_20261023.json"
IDS={f"106-00-E-{n:02d}" for n in range(13,19)}
FIELDS=("questions.json","webp-manifest.json","VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")
REQUIRED=("correctOriginalQuestionNumber","stemComplete","allFourChoicesPresent",
          "allFigureAndMath","noNeighborQuestion","noPageHeaderFooter",
          "legible","sourceShaCorrect","webpShaCorrect","exactPixelCrop")
def f(path):
    p=(ROOT/path).resolve()
    assert p.is_relative_to(ROOT)
    return p
def load(path):return json.loads(f(path).read_text("utf8"))
def digest(path):return hashlib.sha256(f(path).read_bytes()).hexdigest()
def asmap(rows):
    d={r["questionId"]:r for r in rows}
    assert len(d)==len(rows)
    return d
def pixeltest(src,srcsha,output,outsha,box):
    assert digest(src)==srcsha and digest(output)==outsha
    with Image.open(f(src)) as a,Image.open(f(output)) as b:
        a.load();b.load()
        assert a.format==b.format=="WEBP"
        assert a.crop(tuple(box)).size==b.size
        assert ImageChops.difference(a.crop(tuple(box)).convert("RGB"),b.convert("RGB")).getbbox() is None
def run(stage=False):
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if branch!=BRANCH:raise RuntimeError("Unsafe branch")
    e=load(EVID)
    m=load(BASE/"webp-manifest.json")
    vis=load(BASE/"VISUAL_QA.json")
    qb=load(BASE/"questions.json")
    inv=load(BASE/"inventory.json")
    val=load(BASE/"VALIDATION.json")
    release=load(BASE/"release-manifest.json")
    if (e["year"]!=106 or e["reviewedQuestionCount"]!=6 or e["imageQaPassAdded"]!=6
        or e["answerVerifiedAdded"] or e["ocrTextVerifiedAdded"]
        or e["questionVerifiedAdded"] or e["integrationReady"] or e["independentHumanReview"]):
        raise RuntimeError("QA evidence not eligible for image-only recording")
    records=asmap(e["items"]); items=asmap(m["items"]); qs=asmap(qb["questions"]); reviews=asmap(vis["items"])
    assert set(records)==IDS and set(items)==set(qs)==set(reviews) and len(items)==204
    assert inv["visualQaPass"] in (0,6) and inv["webpGeneratedDrafts"] in (182,188)
    assert val["imageVisualQaPass"] in (0,6) and vis["passCount"] in (0,6)
    assert inv["answerOfficialFinalVerified"]==val["answerOfficialFinalVerified"]==0
    assert not (inv.get("integrationReady") or val.get("integrationReady") or release.get("integrationReady"))
    pending={id for id in IDS if items[id].get("qaStatus")!="PASS"}
    if len(pending) not in (0,6):
        raise RuntimeError("Concurrent partial application; no automatic overwrite")
    if len(pending)==6 and inv["visualQaPass"]!=0:raise RuntimeError("Inventory conflicts with source")
    if len(pending)==0 and inv["visualQaPass"]!=6:raise RuntimeError("Already QA PASS yet inventory diverges")
    expected_letters={13:"B",14:"B",15:"D",16:"A",17:"B",18:"A"}
    for id in sorted(IDS):
        r=records[id];it=items[id];q=qs[id]
        assert r["result"]=="PASS" and not r["independentHumanReview"]
        assert all(r["criteria"].get(k) is True for k in REQUIRED)
        assert r["officialAnswerImage"]["candidateValue"]==r["officialAnswerImage"]["visuallyReadValue"]==expected_letters[r["originalQuestionNumber"]]
        assert r["officialAnswerImage"]["matched"] and r["officialCorrectionChecked"] is False
        assert not (r["answerVerified"] or r["questionVerified"] or r["integrationReady"])
        assert it["questionId"]==q["questionId"] and it["originalQuestionNumber"]==r["originalQuestionNumber"]
        assert it["officialQuestionPdfSha256"]==r["sourceOfficialPdfSha256"]
        assert digest(r["officialAnswerImage"]["source"])==r["officialAnswerImage"]["sourceSha256"]
        pixeltest(r["sourcePagePath"],r["sourcePageSha256"],
                  r["reviewedWebpPath"],r["reviewedWebpSha256"],r["cropPixels"])
        assert not (q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady"))
        if id in pending:
            assert not it.get("output") and it["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
            assert q["imageQaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        else:
            assert it["qaStatus"]=="PASS" and it["output"]==r["reviewedWebpPath"]
            assert it["outputSha256"]==r["reviewedWebpSha256"]
            assert it.get("visualReviewEvidence",{}).get("reference")==EVID.as_posix()
    if not stage or not pending:
        return {"mode":"CHECK" if not stage else "IDEMPOTENT",
                "passBefore":inv["visualQaPass"],"passAfter":inv["visualQaPass"]+len(pending),
                "newWebpQA":len(pending),"officialAnswerVerifiedAdded":0}
    for id in sorted(IDS):
        r=records[id]; it=items[id]; q=qs[id];review=reviews[id]
        it["sourcePage"]=r["sourcePage"]
        it["source"]=r["sourcePagePath"]
        it["sourcePageWebpSha256"]=r["sourcePageSha256"]
        it["sourceSize"]=[1400,1980]
        it["cropPixels"]=r["cropPixels"]
        it["output"]=r["reviewedWebpPath"]
        it["outputSha256"]=r["reviewedWebpSha256"]
        it["outputSize"]=[r["cropPixels"][2]-r["cropPixels"][0],r["cropPixels"][3]-r["cropPixels"][1]]
        it["generationVersion"]="manual-direct-visual-recovered-v2"
        it["qaStatus"]="PASS"
        it["originalAutomatedIssues"]=it.get("issues",[])
        it["issues"]=["PDF_NUMBER_ANCHOR_AUTO_EXTRACTION_FAILED_MANUAL_VISUAL_RECOVERY","OCR_TEXT_REVIEW_PENDING"]
        it["visualReviewEvidence"]={"reference":EVID.as_posix(),
           "sourceSha256":r["sourcePageSha256"],"reviewedSha256":r["reviewedWebpSha256"],
           "reviewedAt":"2026-10-23","reviewer":"ChatGPT assistant",
           "method":"direct_original_official_page_to_each_question_webp",
           "independentHumanReview":False}
        q["imageQaStatus"]="PASS"
        q["originalAutomatedIssues"]=q.get("issues",[])
        q["issues"]=["PDF_NUMBER_ANCHOR_AUTO_EXTRACTION_FAILED_MANUAL_VISUAL_RECOVERY","OCR_TEXT_REVIEW_PENDING"]
        q["assets"].update({"singleQuestionWebp":r["reviewedWebpPath"],
             "sourcePageWebp":r["sourcePagePath"],"sha256":r["reviewedWebpSha256"],
             "sourcePage":3,"imageQaEvidence":EVID.as_posix()})
        review.update({"status":"PASS","sourcePage":3,"sourceWebp":r["sourcePagePath"],
                       "candidateWebp":r["reviewedWebpPath"],"candidateSha256":r["reviewedWebpSha256"],
                       "reviewer":"ChatGPT assistant","visualEvidence":EVID.as_posix(),
                       "reviewedAt":"2026-10-23"})
    inv["webpGeneratedDrafts"]+=6
    inv["visualQaPass"]+=6
    inv["sourcePaperStats"]["00-E"]["imageDrafts"]+=6
    inv["sourcePaperStats"]["00-E"]["manualVisualAnchorRecoveredNumbers"]=[13,14,15,16,17,18]
    inv["sourcePaperStats"]["00-E"]["unresolvedAnchorNumbers"]=[
        n for n in inv["sourcePaperStats"]["00-E"]["unresolvedAnchorNumbers"] if n not in range(13,19)]
    inv["directVisualQaEvidence106English"]=EVID.as_posix()
    val["imageVisualQaPass"]+=6
    sg=val["sourceGaps"]["00-E"]
    sg["manualVisualAnchorRecoveredNumbers"]=[13,14,15,16,17,18]
    sg["unresolvedAnchorNumbers"]=[n for n in sg["unresolvedAnchorNumbers"] if n not in range(13,19)]
    val["releaseAllowed"]=val["integrationReady"]=False
    vis["passCount"]=6
    release["imageQA"]="PARTIAL_6_OF_204"
    release["releaseAllowed"]=release["integrationReady"]=False
    assert sum(x["qaStatus"]=="PASS" for x in m["items"])==6
    assert inv["visualQaPass"]==val["imageVisualQaPass"]==vis["passCount"]==6
    assert all(not (x.get("answerVerified") or x.get("questionVerified") or x.get("integrationReady")) for x in qb["questions"])
    if stage:
        db=f(BASE/"question-bank.sqlite3")
        with sqlite3.connect(db) as cx:
            cols={c[1] for c in cx.execute("PRAGMA table_info(questions)")}
            assert "question_id" in cols and "payload_sha256" in cols
            field="payload" if "payload" in cols else "payload_json"
            assert field in cols
            tables={r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "student_answers" not in tables and "student_results" not in tables
            for id in sorted(IDS):
                raw=json.dumps(qs[id],ensure_ascii=False,sort_keys=True,separators=(",",":"))
                hx=hashlib.sha256(raw.encode("utf8")).hexdigest()
                assert cx.execute(f"UPDATE questions SET {field}=?, payload_sha256=? WHERE question_id=?",(raw,hx,id)).rowcount==1
            assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
            assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            for id,raw,hx in cx.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
                assert hashlib.sha256(raw.encode("utf8")).hexdigest()==hx and json.loads(raw)["questionId"]==id
        for fn,obj in zip(FIELDS,(qb,m,vis,inv,val,release)):
            f(BASE/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"mode":"STAGE","passedImageQa":6,"webpCandidatesCount":188,
            "ocrQaAdded":0,"officialAnswerVerifiedAdded":0,"releaseAllowed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    args=p.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
