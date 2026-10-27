#!/usr/bin/env python3
"""Versioned second-pass boundary fixes to SHA-pinned official source page 4.
Preserves v2/v3 for audit; writes v4 only for reviewed edge errors. NO QA PASS,
no data manifest promotion, no answer or student release. 106 C14 and S15-16
remain at their previously verified original pixel candidate versions.
"""
import argparse,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from stage_106_chinese_14_20_v3_boundary_previews import (
    at,read,sha,ROOT,YEAR_DIR,SOURCE,SOURCE_SHA,SOURCE_BLOB,EVIDENCE
)
CHANGES={
    "106-00-C-15":[90,560,1310,693],
    "106-00-C-16":[90,695,1310,808],
    "106-00-C-17":[90,1006,1310,1107],
    "106-00-C-18":[90,1111,1310,1321],
    "106-00-C-19":[90,1350,744,1512],
    "106-00-C-20":[90,1523,744,1762],
    "106-00-C-SHARED-17-18":[90,817,1310,1004],
    "106-00-C-SHARED-19-20":[765,1345,1310,1854]
}
OLD_SHARED_19_SHA="34bfbe09b39e6583ea34c52935b581e2c714596b9b64ef87ba707685f30f36cc"
REPORT=YEAR_DIR+"qa-drafts/DRAFT_106_C14_20_V4_SECOND_PASS_20261024.json"
def main(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    first=read(EVIDENCE)
    manifest=read(YEAR_DIR+"webp-manifest.json")
    v=read(YEAR_DIR+"VISUAL_QA.json")
    rel=read(YEAR_DIR+"release-manifest.json")
    inv=read(YEAR_DIR+"inventory.json")
    assert inv["visualQaPass"]==v["passCount"]==16
    assert inv["answerOfficialFinalVerified"]==0 and not rel["releaseAllowed"] and not rel["integrationReady"]
    assert len(manifest["items"])==204
    v3={x["questionIdOrSharedId"]:x for x in first["items"]}
    ids={x["questionId"]:x for x in manifest["items"]}
    shared={x["sharedMaterialId"]:x for x in manifest["sharedMaterialCrops"]}
    raw=at(SOURCE).read_bytes()
    assert sha(raw)==SOURCE_SHA
    assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()==SOURCE_BLOB
    output=[]
    with Image.open(io.BytesIO(raw)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for id,box in CHANGES.items():
            sid="SHARED" in id
            old=shared[id] if sid else ids[id]
            assert old["qaStatus"]=="DRAFT_NEEDS_DIRECT_VISUAL_QA"
            assert old["sourcePageWebpSha256"]==SOURCE_SHA
            previous=v3.get(id)
            if previous:
                old_path=previous["newPath"]
                old_box=previous["newPixels"]
                old_sha=previous["newSha256"]
            else:
                assert id=="106-00-C-SHARED-19-20"
                old_path=old["output"]
                old_box=old["cropPixels"]
                old_sha=OLD_SHARED_19_SHA
            assert sha(at(old_path).read_bytes())==old_sha
            crop=page.crop(tuple(box))
            buf=io.BytesIO(); crop.save(buf,format="WEBP",lossless=True,method=6,exact=True)
            blob=buf.getvalue()
            with Image.open(io.BytesIO(blob)) as reread:
                reread.load()
                assert reread.format=="WEBP" and reread.size==crop.size
                assert ImageChops.difference(crop.convert("RGB"),reread.convert("RGB")).getbbox() is None
            dest=YEAR_DIR+"qa-drafts/webp-v4/"+("shared/" if sid else "00-C/")+id+".webp"
            if at(dest).exists():
                assert sha(at(dest).read_bytes())==sha(blob),"Existing v4 differs; refuse overwrite"
            elif stage:
                at(dest).parent.mkdir(parents=True,exist_ok=True)
                at(dest).write_bytes(blob)
            output.append({"questionIdOrSharedId":id,"previousCandidatePath":old_path,
                           "previousCropPixels":old_box,"previousSha256":old_sha,
                           "newPath":dest,"newCropPixels":box,"newSha256":sha(blob),
                           "newSize":[crop.width,crop.height],
                           "sourcePageWebp":SOURCE,"sourcePageSha256":SOURCE_SHA,
                           "visualQaStatus":"DRAFT_PENDING_SECOND_DIRECT_VISUAL"})
    record={"schemaVersion":1,"year":106,"paperCode":"00-C",
            "sourcePage":4,"sourceSha256":SOURCE_SHA,"originalPageBlob":SOURCE_BLOB,
            "newV4Files":len(output),"items":output,
            "keptV3Ids":["106-00-C-14"],
            "keptV2SharedIds":["106-00-C-SHARED-15-16"],
            "reviewer":"ChatGPT assistant","independentHumanReview":False,
            "newG1":0,"newG2":0,"newOfficialAnswerVerified":0,
            "releaseAllowed":False,"integrationReady":False}
    if stage:
        at(REPORT).parent.mkdir(parents=True,exist_ok=True)
        at(REPORT).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"status":"STAGED" if stage else "CHECK","v4Files":len(output),
                     "newG1":0,"originalPixelProof":True,"NO_RELEASE":True}))
if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--stage",action="store_true")
    main(cli.parse_args().stage)
