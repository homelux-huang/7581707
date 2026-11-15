#!/usr/bin/env python3
"""Generate only 106 English Q13-Q18 single-question WebP v2 DRAFTS.

Six original lines were visibly inspected against official page 3, but the
generated exact GitHub WebP must itself be SHA-bound and visually compared
before promotion to QA PASS. No overwrite of old image assets or main.
"""
import argparse
import hashlib
import io
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
SOURCE="sudu/data/original/106/00-E/p003-190985dceb-v2-w1400-q66.webp"
SOURCE_SHA="50714aec6e0fbe36b75d3fe4f85d8bd5641a0a2eac87626d3f451f6fe25d23ae"
ANSWER="sudu/data/original/106/00-E-answers/p001-0ee00ea745-v2-w1400-q66.webp"
ANSWER_SHA="f4679e8b9a8f6fac2ed345e9b7afca50962f7d57ae10758be80b51c031f17aee"
BASE="sudu/data/processed/106"
REPORT=BASE+"/qa-drafts/UNVERIFIED_106_ENGLISH_Q13_18_20261023.json"
BOXES={
    13:[90,159,1310,438],
    14:[90,442,1310,650],
    15:[90,656,1310,927],
    16:[90,935,1310,1143],
    17:[90,1147,1310,1454],
    18:[90,1456,1310,1790],
}
ANSWERS={13:"B",14:"B",15:"D",16:"A",17:"B",18:"A"}

def p(path):
    f=(ROOT/path).resolve()
    if not f.is_relative_to(ROOT):raise RuntimeError("Disallowed path")
    return f
def sha(raw):return hashlib.sha256(raw).hexdigest()

def run(stage=False):
    current=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if current!=BRANCH:raise RuntimeError("Only isolated QA branch allowed")
    raw=p(SOURCE).read_bytes()
    assert sha(raw)==SOURCE_SHA
    assert sha(p(ANSWER).read_bytes())==ANSWER_SHA
    man=json.loads(p(BASE+"/webp-manifest.json").read_text("utf8"))
    inv=json.loads(p(BASE+"/inventory.json").read_text("utf8"))
    answers=json.loads(p(BASE+"/official-answer-evidence.json").read_text("utf8"))
    q={x["questionId"]:x for x in man["items"]}
    qa={x["questionId"]:x for x in answers["items"]}
    assert len(q)==204 and inv["visualQaPass"]==0 and inv["answerOfficialFinalVerified"]==0
    expected={f"106-00-E-{n:02d}" for n in BOXES}
    assert len(expected)==6
    new=[]
    candidates=[]
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        assert im.format=="WEBP" and im.size==(1400,1980)
        for n,rect in BOXES.items():
            qid=f"106-00-E-{n:02d}"
            assert qid in q and qid in qa
            assert not q[qid].get("output") and q[qid]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
            assert qa[qid]["pdfExtractedAnswerCandidate"]==qa[qid]["legacyAnswerCandidate"]==ANSWERS[n]
            assert not qa[qid]["answerVerified"]
            x0,y0,x1,y1=rect
            assert 90<=x0<x1<=1310 and 155<=y0<y1<=1790
            stream=io.BytesIO()
            im.crop(tuple(rect)).save(stream,"WEBP",lossless=True,method=6)
            payload=stream.getvalue()
            with Image.open(io.BytesIO(payload)) as decoded:
                decoded.load()
                assert decoded.format=="WEBP" and decoded.size==(x1-x0,y1-y0)
            output=f"{BASE}/qa-drafts/webp-v2/00-E/{qid}.webp"
            target=p(output)
            if target.exists() and sha(target.read_bytes())!=sha(payload):
                raise RuntimeError("Unapproved modification of existing v2 image "+qid)
            candidates.append((target,payload))
            new.append({
                "questionId":qid,"year":106,"paperCode":"00-E","originalQuestionNumber":n,
                "sourcePage":3,"source":SOURCE,"sourcePageWebpSha256":SOURCE_SHA,
                "cropPixels":rect,"output":output,"outputSha256":sha(payload),
                "sourcePageImageMethod":"SHA-pinned official page WebP pixel crop",
                "originalImageDirectVisualPrecheck":"LOCAL_CANDIDATE_ONLY",
                "sourceVisualNote":"Original page 3 Q13-18; stem and options A-D individually checked, all crop boundaries in blank bands. Final GitHub-byte visual QA pending.",
                "imageQaStatus":"DRAFT_PENDING_FINAL_GITHUB_BYTE_VISUAL_REVIEW",
                "officialAnswerPage":ANSWER,"officialAnswerPageSha256":ANSWER_SHA,
                "officialAnswerImageCandidate":ANSWERS[n],
                "officialFinalCorrectionsReviewed":False,"answerVerified":False,
                "questionVerified":False,"integrationReady":False
            })
    record={
        "schemaVersion":1,"year":106,"subject":"英文","draftSingleQuestionCount":6,
        "sourcePage":3,"source":SOURCE,"sourceSha256":SOURCE_SHA,
        "officialAnswerImageSha256":ANSWER_SHA,
        "visualQaPassAdded":0,"answerVerifiedAdded":0,"ocrTextVerifiedAdded":0,
        "releaseAllowed":False,"integrationReady":False,
        "note":"DRAFT only; official source page manually inspected, exact output SHA must be visually reviewed after GitHub staging. Never substitute this for final official correction PDF review.",
        "items":new
    }
    wire=(json.dumps(record,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    target=p(REPORT)
    if target.exists() and target.read_bytes()!=wire:
        raise RuntimeError("Existing report differs")
    if stage:
        for path,data in candidates:
            if not path.exists():
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(wire)
    return {"mode":"STAGE" if stage else "CHECK","drafts":len(new),
            "officialSourceSha256":SOURCE_SHA,"newVisualQaPass":0,"answerVerifiedAdded":0,"integrationReady":False}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    args=parser.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
