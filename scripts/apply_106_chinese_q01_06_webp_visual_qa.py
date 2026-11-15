#!/usr/bin/env python3
"""Register SHA-directly-visually-checked 106 Chinese Q01-Q06 WebP; no OCR/answer release."""
import argparse,hashlib,json,sqlite3,subprocess
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE=Path("sudu/data/processed/106")
EVID=BASE/"qa-drafts/QA_106_CHINESE_Q01_06_DIRECT_VISUAL_20261023.json"
DRAFT=BASE/"qa-drafts/UNVERIFIED_106_CHINESE_Q01_06_20261023.json"
IDS={f"106-00-C-{i:02d}" for i in range(1,7)}
PDFSHA="93b8ec6eb319c8c7f5350ffa6267a2b4aed2f7acb1d1a2a7ca89e38f69ec5476"
def f(p):
    x=(ROOT/p).resolve();assert x.is_relative_to(ROOT);return x
def load(p):return json.loads(f(p).read_text("utf8"))
def sha(p):return hashlib.sha256(f(p).read_bytes()).hexdigest()
def indexed(items):
    d={r["questionId"]:r for r in items};assert len(d)==len(items);return d
def run(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    e=load(EVID);draft=load(DRAFT)
    bank=load(BASE/"questions.json");manifest=load(BASE/"webp-manifest.json")
    visual=load(BASE/"VISUAL_QA.json");inv=load(BASE/"inventory.json")
    val=load(BASE/"VALIDATION.json");release=load(BASE/"release-manifest.json")
    assert e["year"]==106 and e["questionsReviewed"]==e["imageVisualPassAdded"]==6
    assert not(e["answerVerifiedAdded"] or e["ocrVerifiedAdded"] or e["questionVerifiedAdded"] or e["integrationReady"])
    assert len(draft["items"])==6 and draft["newImageQaPass"]==0
    q=indexed(bank["questions"]);mi=indexed(manifest["items"])
    vis=indexed(visual["items"]);r=indexed(e["items"]);d=indexed(draft["items"])
    assert set(q)==set(mi)==set(vis) and len(q)==204
    assert set(r)==set(d)==IDS
    assert inv["visualQaPass"] in(6,12) and inv["webpGeneratedDrafts"] in(188,194)
    assert val["imageVisualQaPass"] in (6,12) and visual["passCount"] in(6,12)
    assert inv["answerOfficialFinalVerified"]==0 and inv["ocrTextIndependentlyVerified"]==6
    assert not (release["releaseAllowed"] or release["integrationReady"])
    pending={id for id in IDS if mi[id]["qaStatus"]!="PASS"}
    if len(pending) not in (0,6):raise RuntimeError("Concurrent partial results - abort")
    if pending and inv["visualQaPass"]!=6:raise RuntimeError("QA ledger diverged")
    for id in sorted(IDS):
        a=r[id];b=d[id];m=mi[id];qrec=q[id]
        assert a["result"]=="PASS" and a["officialQuestionPdfSha256"]==m["officialQuestionPdfSha256"]==PDFSHA
        assert a["officialSourcePage"]==b["sourcePage"]==2
        assert a["officialPageWebpSha256"]==b["sourcePageWebpSha256"]
        assert a["cropPixels"]==b["cropPixels"] and a["cropWebpSha256"]==b["outputSha256"]
        assert a["cropWebpPath"]==b["output"]
        assert all(a["criteria"].values())
        assert sha(b["source"])==b["sourcePageWebpSha256"] and sha(b["output"])==b["outputSha256"]
        assert sha(d[id]["officialAnswerImagePath"])==d[id]["officialAnswerImageSha256"]
        with Image.open(f(b["source"])) as src,Image.open(f(b["output"])) as img:
            src.load();img.load()
            assert src.format==img.format=="WEBP"
            assert ImageChops.difference(src.crop(tuple(b["cropPixels"])).convert("RGB"),img.convert("RGB")).getbbox() is None
        assert not (qrec.get("answerVerified") or qrec.get("questionVerified") or qrec.get("integrationReady"))
        if id in pending:
            assert not m.get("output") and m["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
        else:
            assert m["qaStatus"]=="PASS" and m["outputSha256"]==b["outputSha256"]
            assert m["visualReviewEvidence"]["reference"]==EVID.as_posix()
    if not stage or not pending:
        return {"mode":"CHECK" if not stage else "IDEMPOTENT","before":inv["visualQaPass"],
                "after":inv["visualQaPass"]+len(pending),"newQA":len(pending),"answersVerified":0}
    for id in sorted(IDS):
        a=r[id];b=d[id];m=mi[id];qq=q[id];v=vis[id]
        m.update({"sourcePage":2,"source":b["source"],"sourcePageWebpSha256":b["sourcePageWebpSha256"],
                  "sourceSize":[1400,1980],"cropPixels":b["cropPixels"],"output":b["output"],
                  "outputSize":[b["cropPixels"][2]-b["cropPixels"][0],b["cropPixels"][3]-b["cropPixels"][1]],
                  "outputSha256":b["outputSha256"],"generationVersion":"manual-qa-pixel-v2",
                  "qaStatus":"PASS","originalAutomatedIssues":m.get("issues",[]),
                  "issues":["PDF_AUTO_ANCHOR_FAILED_MANUAL_SOURCE_REVIEW","OCR_TEXT_QA_PENDING"]})
        m["visualReviewEvidence"]={"reference":EVID.as_posix(),"reviewedSha256":b["outputSha256"],
           "sourceSha256":b["sourcePageWebpSha256"],"qaReviewer":"ChatGPT assistant",
           "reviewedAt":"2026-10-23","method":"actual_direct_official_page_v2_to_question_pixel_crop",
           "independentHumanReview":False}
        qq["imageQaStatus"]="PASS"
        qq["originalAutomatedIssues"]=qq.get("issues",[])
        qq["issues"]=["PDF_AUTO_ANCHOR_FAILED_MANUAL_SOURCE_REVIEW","OCR_TEXT_QA_PENDING"]
        qq["assets"].update({"singleQuestionWebp":b["output"],"sourcePageWebp":b["source"],
                             "sha256":b["outputSha256"],"sourcePage":2,
                             "imageQaEvidence":EVID.as_posix()})
        v.update({"status":"PASS","sourcePage":2,"sourceWebp":b["source"],
                  "candidateWebp":b["output"],"candidateSha256":b["outputSha256"],
                  "reviewer":"ChatGPT assistant","visualEvidence":EVID.as_posix(),
                  "reviewedAt":"2026-10-23"})
    inv["webpGeneratedDrafts"]+=6
    inv["visualQaPass"]+=6
    inv["sourcePaperStats"]["00-C"]["imageDrafts"]+=6
    inv["sourcePaperStats"]["00-C"]["manualVisualAnchorRecoveredNumbers"]=list(range(1,7))
    inv["sourcePaperStats"]["00-C"]["unresolvedAnchorNumbers"]=[
        n for n in inv["sourcePaperStats"]["00-C"]["unresolvedAnchorNumbers"] if n not in range(1,7)]
    inv["directVisualQaEvidence106Chinese"]=EVID.as_posix()
    val["imageVisualQaPass"]+=6
    val["sourceGaps"]["00-C"]["manualVisualAnchorRecoveredNumbers"]=list(range(1,7))
    val["sourceGaps"]["00-C"]["unresolvedAnchorNumbers"]=[
        n for n in val["sourceGaps"]["00-C"]["unresolvedAnchorNumbers"] if n not in range(1,7)]
    val["releaseAllowed"]=val["integrationReady"]=False
    visual["passCount"]=inv["visualQaPass"]
    release["imageQA"]="PARTIAL_12_OF_204"
    release["integrationReady"]=release["releaseAllowed"]=False
    assert sum(x["qaStatus"]=="PASS" for x in manifest["items"])==12
    assert inv["visualQaPass"]==val["imageVisualQaPass"]==visual["passCount"]==12
    assert inv["answerOfficialFinalVerified"]==0 and inv["ocrTextIndependentlyVerified"]==6
    assert all(not(x.get("answerVerified") or x.get("integrationReady")) for x in bank["questions"])
    db=f(BASE/"question-bank.sqlite3")
    with sqlite3.connect(db) as cx:
        cols={r[1] for r in cx.execute("PRAGMA table_info(questions)")}
        assert {"question_id","payload_sha256"}<=cols
        field="payload" if "payload" in cols else "payload_json"
        assert field in cols
        assert "student_answers" not in {r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for id in sorted(IDS):
            raw=json.dumps(q[id],ensure_ascii=False,sort_keys=True,separators=(",",":"))
            assert cx.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
               (raw,hashlib.sha256(raw.encode("utf8")).hexdigest(),id)).rowcount==1
        assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
        for id,raw,h in cx.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
            assert hashlib.sha256(raw.encode("utf8")).hexdigest()==h and json.loads(raw)["questionId"]==id
    for file,obj in (("questions.json",bank),("webp-manifest.json",manifest),
                     ("VISUAL_QA.json",visual),("inventory.json",inv),
                     ("VALIDATION.json",val),("release-manifest.json",release)):
        f(BASE/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"mode":"STAGE","newVisualQaPass":6,"total106":12,"newWebpGenerated":6,
        "ocrPreserved":6,"answerVerifiedAdded":0,"integrationReady":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true");g.add_argument("--stage",action="store_true")
    a=p.parse_args();print(json.dumps(run(stage=a.stage),ensure_ascii=False))
