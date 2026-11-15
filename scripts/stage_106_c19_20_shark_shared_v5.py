#!/usr/bin/env python3
"""Source-pixel candidate for 106 C19/C20 shared shark graphic upper boundary.
Keep V2/V4 untouched, no G1 change, no SQLite change, no release.
"""
import argparse,hashlib,io,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from stage_106_chinese_14_20_v3_boundary_previews import ROOT,at,sha,SOURCE,SOURCE_SHA,SOURCE_BLOB,YEAR_DIR
OLD=YEAR_DIR+"qa-drafts/webp-v4/shared/106-00-C-SHARED-19-20.webp"
NEW=YEAR_DIR+"qa-drafts/webp-v5/shared/106-00-C-SHARED-19-20.webp"
REPORT=YEAR_DIR+"qa-drafts/DRAFT_106_C19_20_SHARED_V5_TOP_BOUNDARY_20261024.json"
CROP=[765,1317,1310,1854]
def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    source=at(SOURCE).read_bytes()
    assert sha(source)==SOURCE_SHA
    assert hashlib.sha1(b"blob "+str(len(source)).encode()+b"\0"+source).hexdigest()==SOURCE_BLOB
    old=at(OLD).read_bytes()
    with Image.open(io.BytesIO(source)) as image:
        image.load()
        assert image.size==(1400,1980)
        cropped=image.crop(tuple(CROP))
        buffer=io.BytesIO()
        cropped.save(buffer,format="WEBP",lossless=True,method=6,exact=True)
        out=buffer.getvalue()
        with Image.open(io.BytesIO(out)) as new:
            new.load()
            assert new.format=="WEBP" and new.size==cropped.size
            assert ImageChops.difference(cropped.convert("RGB"),new.convert("RGB")).getbbox() is None
    if at(NEW).exists():
        assert sha(at(NEW).read_bytes())==sha(out)
    elif stage:
        at(NEW).parent.mkdir(parents=True,exist_ok=True)
        at(NEW).write_bytes(out)
    cert={"year":106,"questionIdOrSharedId":"106-00-C-SHARED-19-20","oldV4":OLD,
          "oldV4Sha256":sha(old),"newV5":NEW,"newV5Sha256":sha(out),
          "sourcePageWebp":SOURCE,"sourcePageSha256":SOURCE_SHA,
          "sourcePage":4,"newCropPixels":CROP,
          "status":"DRAFT_PENDING_DIRECT_VISUAL",
          "newG1":0,"newG2":0,"releaseAllowed":False,"integrationReady":False}
    if stage:
        at(REPORT).write_text(json.dumps(cert,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"stage":stage,"candidateSha256":sha(out),"G1":0,"NO_RELEASE":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stage",action="store_true")
    run(p.parse_args().stage)
