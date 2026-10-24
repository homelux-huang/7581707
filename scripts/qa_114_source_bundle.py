"""Strict read-only collection of official 114 answer images and 3 original WebP crops.

Do NOT approve answers merely because PDF text candidates match. All PDF bytes
and source images are SHA-pinned, rendered for later independent visual review.
No changes to production, SQLite or any original source file.
"""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sqlite3
import sys
import requests
import fitz
from PIL import Image,ImageChops
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
YEAR=ROOT/"sudu/data/processed/114"
OUT=Path("/tmp/114-answer-qa-original").resolve()
OUT.mkdir(parents=True,exist_ok=True)
TARGETS=("114-00-E-07","114-00-E-08","114-00-E-09")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def sha(b):
    return hashlib.sha256(b).hexdigest()
def require(ok,message):
    if not ok: raise AssertionError(message)

def official_download(session,url):
    require(urlparse(url).hostname=="web1.tcte.edu.tw","official URL must be TCTE")
    with session.get(url,timeout=(15,65),stream=True) as r:
        r.raise_for_status()
        require(urlparse(r.url).hostname=="web1.tcte.edu.tw","official redirect must remain TCTE")
        chunks=[]
        total=0
        for chunk in r.iter_content(131072):
            total+=len(chunk)
            require(total<12000000,"PDF too large")
            chunks.append(chunk)
        data=b"".join(chunks)
    require(data.startswith(b"%PDF-"),"official non-PDF")
    return data

def official_papers(session):
    ev=read(YEAR/"official-answer-evidence.json")
    paper=defaultdict(dict)
    for row in ev["items"]:
        qid=row["questionId"]
        code=qid.rsplit("-",1)[0].split("114-",1)[1]
        if code not in paper: paper[code]={}
        if paper[code]:
            require(paper[code]["url"]==row["officialPdf"] and
                    paper[code]["sha256"]==row["officialPdfSha256"],
                    f"inconsistent official {code}")
        else:
            paper[code]={"url":row["officialPdf"],"sha256":row["officialPdfSha256"]}
    result=[]
    for code,v in sorted(paper.items()):
        data=official_download(session,v["url"])
        require(sha(data)==v["sha256"],f"official PDF sha wrong {code}")
        (OUT/f"114-{code}-official-final-answer.pdf").write_bytes(data)
        doc=fitz.open(stream=data,filetype="pdf")
        pages=[]
        for i,page in enumerate(doc):
            pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
            png=OUT/f"114-{code}-official-answer-p{i+1:02}.png"
            pix.save(png)
            text=page.get_text("text")
            (OUT/f"114-{code}-official-answer-p{i+1:02}.txt").write_text(text,encoding="utf-8")
            pages.append({"number":i+1,"png":png.name,"pngSha256":sha(png.read_bytes()),"textLength":len(text)})
        result.append({"paperCode":code,"pdfSha256":sha(data),"url":v["url"],
                       "pages":pages,"byteCount":len(data),"independentlyVisualVerified":False})
    return result

def source_crops():
    qs={x["questionId"]:x for x in read(YEAR/"questions.json")["questions"]}
    crops={x["questionId"]:x for x in read(YEAR/"webp-manifest.json")["items"]}
    prior=read(YEAR/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json")
    prev={x["questionId"]:x for x in prior["items"]}
    ans=read(YEAR/"QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json")
    prev_ans={x["questionId"]:x for x in ans["items"]}
    out=[]
    for qid in TARGETS:
        q,c,e,a=qs[qid],crops[qid],prev[qid],prev_ans[qid]
        src=ROOT/c["source"]
        crop=ROOT/c["output"]
        answer=ROOT/a["officialAnswerImageWebpPath"]
        for file,h,label in ((src,c["sourceSha256"],"page"),
                             (crop,c["sha256"],"crop"),
                             (answer,a["officialAnswerImageWebpSha256"],"answer-image")):
            require(file.is_file() and sha(file.read_bytes())==h,f"{qid} {label} SHA")
        require(c["sha256"]==e["reviewedWebpSha256"] and c["qaStatus"]=="PASS",
                f"{qid} not original QA PASS")
        require(e["cropPixels"]==c["crop"],f"{qid} coordinates")
        with Image.open(src) as ims, Image.open(crop) as imc:
            orig=ims.crop(tuple(c["crop"]))
            require(orig.size==imc.size,f"{qid} geometry")
            require(ImageChops.difference(orig.convert("RGB"),imc.convert("RGB")).getbbox() is None,
                    f"{qid} crop pixels NOT identical")
            orig.save(OUT/f"{qid}-crop-uncompressed-original.png")
        with Image.open(answer) as ima:
            ima.save(OUT/"114-00-E-original-answer-page.png")
        (OUT/f"{qid}-source.webp").write_bytes(src.read_bytes())
        (OUT/f"{qid}-crop.webp").write_bytes(crop.read_bytes())
        out.append({"qid":qid,"manifestWebpSha256":c["sha256"],
                    "sourcePageSha256":c["sourceSha256"],"originalPixelIdentical":True,
                    "originalCropping":c["crop"],"priorImageQAStatus":c["qaStatus"],
                    "officialAnswerImagePageSha256":a["officialAnswerImageWebpSha256"],
                    "existingAnswerImageVisualCandidate":a["officialVisualAnswerCandidate"],
                    "publishedAnswerIndependentlyRecheckedThisStep":False,
                    "textRevisionWillBeCheckedSeparately":True})
    return out

def sqlite_roundtrip():
    path=YEAR/"question-bank.sqlite3"
    require(path.is_file(),"missing SQLite database")
    connection=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try:
        tables=[x[0] for x in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        schemas={t:[r[1] for r in connection.execute(
            'PRAGMA table_info("'+t.replace('"','""')+'")')] for t in tables}
        counts={t:connection.execute('SELECT COUNT(*) FROM "'+t.replace('"','""')+'"').fetchone()[0] for t in tables}
        snapshot={"dbSha256":sha(path.read_bytes()),"tables":schemas,"rowCounts":counts,"schemaCompared":False}
        ids=[q["questionId"] for q in read(YEAR/"questions.json")["questions"]]
        require(len(ids)==len(set(ids))==205,"JSON canonical IDs")
        candidates=[t for t in tables if any(c in schemas[t] for c in ("question_id","questionId","canonical_id","canonicalId"))]
        matches=[]
        for t in candidates:
            for field in ("question_id","questionId","canonical_id","canonicalId"):
                if field in schemas[t]:
                    got=[str(row[0]) for row in connection.execute(
                        'SELECT "'+field+'" FROM "'+t+'" ORDER BY "'+field+'"')]
                    matches.append({"table":t,"field":field,
                                    "count":len(got),"matchesAllCanonicalIds":len(got)==205 and set(got)==set(ids)})
        snapshot["idMatches"]=matches
        snapshot["sqliteRoundtripVerified"]=any(x["matchesAllCanonicalIds"] for x in matches)
    finally:
        connection.close()
    return snapshot

def main():
    session=requests.Session()
    session.headers.update({"User-Agent":"7581707-source-audit-114/1.0"})
    docs=official_papers(session)
    crops=source_crops()
    sqlite=sqlite_roundtrip()
    summary={"schemaVersion":1,"year":114,"source":"TCTE verified live PDF bytes", 
       "papers":docs,"targetSourceWebp":crops,"sqlite":sqlite,
       "officialAnswerImageVisualQAApprovedThisRun":0,
       "webpExistingQAPromotedThisRun":0,
       "answerVerifiedChanged":0,"studentQaApprovedChanged":0,
       "runMode":"read-only source evidence for subsequent independent image review"}
    (OUT/"source-bundle-sha.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    require(len(docs)==5 and len(crops)==3,"missing docs/crops")
    require(sqlite["sqliteRoundtripVerified"],"SQLite canonical roundtrip missing: REVIEW DB structure before release")

if __name__=="__main__":
    main()
