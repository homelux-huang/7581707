#!/usr/bin/env python3
"""Non-destructive 106 C question 1-6 original-pixel WebP v2, SHA pinned and draft-only."""
import argparse,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
SRC="sudu/data/original/106/00-C/p002-93b8ec6eb3-v2-w1400-q66.webp"
SRCSHA="048b456cd43780af76d4deeed55809e13363312ff1dd2c425079b86a8ee55aa2"
ANSWER="sudu/data/original/106/00-C-answers/p001-ca4adaa741-v2-w1400-q66.webp"
ANSHA="de2dd7fa2c96ead2dd8b305b48f2d1d1af068c843c2648d39f2403f1f6c088f5"
BASE="sudu/data/processed/106"
OUT=BASE+"/qa-drafts/UNVERIFIED_106_CHINESE_Q01_06_20261023.json"
BOX={
1:(90,241,1310,411),2:(90,414,1310,590),3:(90,594,1310,1046),
4:(90,1046,1310,1290),5:(90,1293,1310,1611),6:(90,1635,1310,1827)
}
SHA={1:"731809f11a6c3eb34d9679996e8708d5edd8fd5b82023f125b2d1647bd8208d4",
2:"e81d343e340b6231427a8ce66f613ee8b13b3eab156b45b73d5cbea84a270565",
3:"9f437bea804d393fe604e2301f7997390cd7b275d3b51a243e117a4316d4090c",
4:"cdd9903d60297abb4b325482f26b7ca4cf348a34a3388269aaf896c9126d9fcb",
5:"d9d0a870f96ea09f919b27577d6c13a5311a99b0eaa63860727e7f5f21c7bc70",
6:"91f3dda70dcaa7ad75c96528c65f40925af69d69fb31353b9ac01918bb92c26c"}
def p(s):
    z=(ROOT/s).resolve()
    assert z.is_relative_to(ROOT)
    return z
def sha(b):return hashlib.sha256(b).hexdigest()
def run(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    raw=p(SRC).read_bytes()
    assert sha(raw)==SRCSHA and sha(p(ANSWER).read_bytes())==ANSHA
    m=json.loads(p(BASE+"/webp-manifest.json").read_text("utf8"))
    inv=json.loads(p(BASE+"/inventory.json").read_text("utf8"))
    qs={r["questionId"]:r for r in m["items"]}
    assert len(qs)==204 and inv["visualQaPass"]==6
    assert inv["webpGeneratedDrafts"]==188 and inv["answerOfficialFinalVerified"]==0
    candidates=[];records=[]
    with Image.open(io.BytesIO(raw)) as im:
        im.load();assert im.format=="WEBP" and im.size==(1400,1980)
        for n,box in BOX.items():
            id=f"106-00-C-{n:02d}"
            assert not qs[id].get("output") and qs[id]["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
            b=io.BytesIO();im.crop(box).save(b,"WEBP",lossless=True,method=6)
            data=b.getvalue()
            assert sha(data)==SHA[n],f"106 C Q{n} immutable local-direct-visual SHA changed"
            with Image.open(io.BytesIO(data)) as check:
                check.load();assert check.format=="WEBP" and check.size==(box[2]-box[0],box[3]-box[1])
            out=f"{BASE}/qa-drafts/webp-v2/00-C/{id}.webp"; dest=p(out)
            if dest.exists() and sha(dest.read_bytes())!=SHA[n]:raise RuntimeError("Immutable v2 conflict")
            candidates.append((dest,data))
            records.append({"questionId":id,"originalQuestionNumber":n,
                "sourcePage":2,"source":SRC,"sourcePageWebpSha256":SRCSHA,
                "cropPixels":list(box),"output":out,"outputSha256":SHA[n],
                "sourceImageVisuallyInspected":True,"githubVersionReviewPending":True,
                "imageQaStatus":"DRAFT_PENDING_SHA_BOUND_FINAL_VISUAL_REVIEW",
                "officialAnswerImagePath":ANSWER,"officialAnswerImageSha256":ANSHA,
                "answerVerified":False,"questionVerified":False,"integrationReady":False})
    report={"year":106,"paperCode":"00-C","generatedDrafts":6,"sourcePage":2,
        "officialSourceWebpSha256":SRCSHA,"officialAnswerImageSha256":ANSHA,
        "newImageQaPass":0,"newAnswerVerified":0,"integrationReady":False,
        "note":"Original page and these exact pixels visually prechecked; GitHub outputs must be SHA verified and separately recorded as PASS. Q3 full four-option excerpt and Q5 illustrated menu preserve original images.", "items":records}
    payload=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    dest=p(OUT)
    if dest.exists() and dest.read_bytes()!=payload:raise RuntimeError("Immutable report content mismatch")
    if stage:
        for dest,data in candidates:
            if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        if not p(OUT).exists():p(OUT).parent.mkdir(parents=True,exist_ok=True);p(OUT).write_bytes(payload)
    return {"stage":stage,"drafts":6,"allShaPinned":True,"newImageQaPass":0,"answerVerifiedAdded":0,"integrationReady":False}
if __name__=="__main__":
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true");g.add_argument("--stage",action="store_true")
    x=a.parse_args();print(json.dumps(run(stage=x.stage),ensure_ascii=False))
