#!/usr/bin/env python3
"""107 English E37: create source-pixel-only candidate excluding unrelated Q38-41 passage.

NO G1 PASS, NO G2, no source DB mutation, no answer verification, NO RELEASE.
The prior v1 crop contains the Q38-41 robot passage; retain v1 unchanged.
"""
import argparse, hashlib, io, json, subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/107/"
PAGE="sudu/data/original/107/00-E/p007-6fa77b536c-v2-w1400-q66.webp"
PAGE_SHA="89997a38a422f25589afd9632ad558f76f44684c2c0aa75c3f15429020ac8fac"
PAGE_BLOB="dacba885baae37a8290476026df3a2cf0eda2be3"
PDF_SHA="6fa77b536c5a991af6ad12f33427d362614109fad4f7d701ec25bc453dec7440"
LEGACY="sudu/data/processed/107/webp-v1/00-E/107-00-E-37.webp"
LEGACY_SHA="f56de328933f3387afbe87c2d6f0f53731d52726c486a7d559a4812089f5a16b"
BOX=(90,372,1310,568)
CANDIDATE="sudu/data/processed/107/qa-drafts/webp-v2/00-E/107-00-E-37.webp"
EVIDENCE=BASE+"qa-drafts/DRAFT_107_E37_Q38_ARTICLE_REMOVED_V2_20261024.json"

def loc(s):
    p=(ROOT/s).resolve()
    assert p.is_relative_to(ROOT.resolve())
    return p
def read(s):
    return json.loads(loc(s).read_text("utf8"))
def sha(b):
    return hashlib.sha256(b).hexdigest()

def main(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    b=read(BASE+"questions.json");m=read(BASE+"webp-manifest.json")
    v=read(BASE+"VISUAL_QA.json");inv=read(BASE+"inventory.json")
    val=read(BASE+"VALIDATION.json");rel=read(BASE+"release-manifest.json")
    q=next(x for x in b["questions"] if x["questionId"]=="107-00-E-37")
    im=next(x for x in m["items"] if x["questionId"]==q["questionId"])
    vi=next(x for x in v["items"] if x["questionId"]==q["questionId"])
    assert im["output"]==LEGACY and im["outputSha256"]==LEGACY_SHA
    assert im["source"]==PAGE and im["sourcePage"]==7
    assert im["officialQuestionPdfSha256"]==PDF_SHA
    assert im["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert q["imageQaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    assert vi["status"]=="PENDING" and not q["questionVerified"] and not q["answerVerified"]
    assert inv["visualQaPass"]==val["imageVisualQaPass"]==v["passCount"]==19
    assert inv["ocrTextIndependentlyVerified"]==val["ocrTextVerified"]==5
    assert inv["answerOfficialFinalVerified"]==val["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    source=loc(PAGE).read_bytes()
    assert sha(source)==PAGE_SHA
    assert hashlib.sha1(b"blob "+str(len(source)).encode()+b"\0"+source).hexdigest()==PAGE_BLOB
    old=loc(LEGACY).read_bytes()
    assert sha(old)==LEGACY_SHA
    with Image.open(io.BytesIO(source)) as img:
        img.load()
        assert img.size==(1400,1980)
        with Image.open(io.BytesIO(old)) as oc:
            oc.load()
            assert ImageChops.difference(img.crop(tuple(im["cropPixels"])).convert("RGB"),oc.convert("RGB")).getbbox() is None
        fresh=img.crop(BOX).convert("RGB")
        output=loc(CANDIDATE)
        if stage and not output.exists():
            output.parent.mkdir(parents=True,exist_ok=True)
            fresh.save(output,format="WEBP",lossless=True,method=6,exact=True)
        candidate_sha=None
        if output.exists():
            data=output.read_bytes()
            candidate_sha=sha(data)
            with Image.open(io.BytesIO(data)) as candidate:
                candidate.load()
                assert candidate.size==(1220,196)
                assert ImageChops.difference(fresh,candidate.convert("RGB")).getbbox() is None
    proof={
        "schemaVersion":1,"questionId":"107-00-E-37","year":107,"paperCode":"00-E",
        "officialQuestionPdfSha256FromRepository":PDF_SHA,
        "officialSourcePdfFreshlyRedownloaded":False,
        "sourceOriginalPageWebp":PAGE,"sourceOriginalPageSha256":PAGE_SHA,"sourceGitBlob":PAGE_BLOB,
        "historicalLegacyCrop":LEGACY,"historicalLegacySha256":LEGACY_SHA,
        "legacyCropPixels":im["cropPixels"],
        "legacyObservedProblem":"Original Q37 WebP v1 included the next Q38-41 social-robots reading heading and article; Q37 D option was contaminated in historical legacy PDF extraction.",
        "candidateWebp":CANDIDATE,"candidateCropPixels":list(BOX),"candidateSha256":candidate_sha,
        "candidatePixelDifferenceZero":candidate_sha is not None,
        "candidateReviewStatus":"DRAFT_AWAITING_NEW_INDIVIDUAL_VISUAL_G1",
        "independentHumanReview":False,
        "questionTextG2StillPending":True,"officialFinalAnswerG3StillPending":True,
        "released":False,"releaseAllowed":False,"integrationReady":False,
        "nextAction":"Directly open new candidate against source page: verify Q37 title/A-D, no Q38 heading/passage, SHA; only then apply G1 and correct OCR D."
    }
    if stage:
        loc(EVIDENCE).write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"mode":"DRAFT_STAGED" if stage else "CHECK","newCandidate":CANDIDATE,
      "candidateSha256":candidate_sha,"originalG1Pass":19,"newG1":0,"newG2":0,"NO_RELEASE":True}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    main(p.parse_args().stage)
