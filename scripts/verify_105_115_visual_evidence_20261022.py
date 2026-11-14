#!/usr/bin/env python3
"""Validate SHA-pinned source-page/crop visual evidence, without marking QA PASS."""
import hashlib, json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for year, fname in ((113,"VISUAL_QA_BATCH_02_2026-10-22.json"),(114,"VISUAL_QA_BATCH_01_2026-10-22.json"),(115,"VISUAL_QA_BATCH_03_2026-10-22.json")):
    d=ROOT/"sudu/data/processed"/str(year)
    evidence=json.loads((d/fname).read_text(encoding="utf-8"))
    manifest=json.loads((d/"webp-manifest.json").read_text(encoding="utf-8"))
    entries={i["questionId"]:i for i in manifest["items"]}
    seen=set()
    for rec in evidence["records"]:
        qid=rec["questionId"]
        assert qid not in seen and qid in entries
        seen.add(qid)
        item=entries[qid]
        assert rec["sourcePagePath"]==item["source"] and rec["webpPath"]==item["output"]
        assert rec["sourcePage"]==item["sourcePage"]
        assert rec["cropPixels"]==(item.get("cropPixels") or item.get("crop"))
        assert rec["sourceSha256"]==(item.get("sourcePageWebpSha256") or item.get("sourceSha256"))
        assert rec["webpSha256"]==(item.get("outputSha256") or item.get("sha256"))
        for filename, digest in ((rec["sourcePagePath"],rec["sourceSha256"]),(rec["webpPath"],rec["webpSha256"])):
            assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest
        with Image.open(ROOT/rec["webpPath"]) as im:
            im.load()
            assert im.format=="WEBP" and list(im.size)==item["outputSize"]
        assert rec["result"] in ("PASS","FAIL_HEADER_FRAGMENT")
        if rec["result"]=="FAIL_HEADER_FRAGMENT":
            assert qid=="114-00-C-01"
    print(year,len(seen),sum(i["result"]=="PASS" for i in evidence["records"]),"PASS-EVIDENCE","NO-RELEASE")
