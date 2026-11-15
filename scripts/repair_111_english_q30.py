#!/usr/bin/env python3
"""Split 111 English Q30 choices from adjacent Q31/32 graph; never mark PASS automatically."""
import hashlib,io,json,sqlite3
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/111"
QID="111-00-E-30"
BOX=[90,781,1310,838]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((D/n).read_text("utf-8"))
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    manifest=load("webp-manifest.json")
    corpus=load("questions.json")
    qa=load("VISUAL_QA.json")
    ocr=load("ocr-raw-candidates.json")
    inv=load("inventory.json")
    valid=load("VALIDATION.json")
    release=load("release-manifest.json")
    x=next(i for i in manifest["items"] if i["questionId"]==QID)
    q=next(i for i in corpus["questions"] if i["questionId"]==QID)
    v=next(i for i in qa["items"] if i["questionId"]==QID)
    o=next(i for i in ocr["items"] if i["questionId"]==QID)
    assert x["qaStatus"]!="PASS"
    old_sha=x["outputSha256"]
    oldpath=R/x["output"]
    assert oldpath.is_file() and sha(oldpath.read_bytes())==old_sha
    src=R/x["source"]
    sourcebytes=src.read_bytes()
    assert sha(sourcebytes)==x["sourcePageWebpSha256"]
    with Image.open(io.BytesIO(sourcebytes)) as im:
        assert im.format=="WEBP" and im.size==(1400,1980)
        destbuf=io.BytesIO()
        im.crop(tuple(BOX)).save(destbuf,"WEBP",lossless=True,method=6)
    new=destbuf.getvalue()
    dest=D/"webp-v2/00-E"/(QID+".webp")
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=new:
        raise ValueError("Existing v2 differs; must create new immutable version")
    if not dest.exists():dest.write_bytes(new)
    with Image.open(dest) as im:
        im.load()
        assert im.format=="WEBP" and im.size==(1220,57)
    old={"path":x["output"],"sha256":old_sha,"crop":x["cropPixels"],
         "visualFailure":"INCLUDED_SECTION_IV_AND_NEXT_Q31_Q32_GRAPH"}
    newpath=dest.relative_to(R).as_posix()
    x.update({"output":newpath,"outputSha256":sha(new),"cropPixels":BOX,
        "outputSize":[1220,57],"qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
        "generationVersion":"111-Q30-split-v2",
        "previousVersion":old})
    x["issues"].append("OLD_V1_INCLUDED_UNRELATED_Q31_Q32_GRAPH")
    q["assets"]["singleQuestionWebp"]=newpath
    q["assets"]["sha256"]=sha(new)
    q["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
    q["questionVerified"]=False
    q["answerVerified"]=False
    q["integrationReady"]=False
    v.update({"status":"PENDING","candidateWebp":newpath,"candidateSha256":sha(new),
              "visualEvidence":None,"reviewer":None})
    import pytesseract
    with Image.open(dest) as im:
        raw=pytesseract.image_to_string(im,lang="eng",config="--psm 6")
    if "previousRawOcrText" not in o:o["previousRawOcrText"]=o.get("rawOcrText")
    o["rawOcrText"]=raw
    o["rawOrigin"]="111-English-Q30-V2-DRAFT_UNCORRECTED_OCR"
    o["imageSha256"]=sha(new)
    o["qaStatus"]="PENDING"
    q["ocrStatus"]="DRAFT_UNCORRECTED_OCR"
    assert sum(x["qaStatus"]=="PASS" for x in manifest["items"])==9
    inv["visualQaPass"]=9
    valid["imageVisualQaPass"]=9
    valid["integrationReady"]=False
    release["releaseAllowed"]=False
    release["integrationReady"]=False
    for file,obj in [("webp-manifest.json",manifest),("questions.json",corpus),
        ("VISUAL_QA.json",qa),("ocr-raw-candidates.json",ocr),
        ("inventory.json",inv),("VALIDATION.json",valid),("release-manifest.json",release)]:
        save(file,obj)
    save("111-EN-Q30-OLD-CROP-FAILURE-AND-V2.json",{
        "year":111,"questionId":QID,"sourcePage":x["sourcePage"],"source":x["source"],
        "old":old,"new":{"webp":newpath,"sha256":sha(new),"cropPixels":BOX,
                        "qaStatus":"PENDING_DIRECT_VISUAL_QA"},
        "note":"Old Q30 WebP visibly contained section IV and subsequent graph. New v2 is pixel-only crop; visual PASS cannot be presumed."})
    with sqlite3.connect(D/"question-bank.sqlite3") as db:
        raw=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        assert db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
            (raw,sha(raw.encode()),QID)).rowcount==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
    print("111 Q30 source-pixel v2 generated, old failure retained; QA still 9/205, Q30 PENDING.")

if __name__=="__main__":main()
