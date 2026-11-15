#!/usr/bin/env python3
"""111 English Q24 old crop visibly contained Q25. Fix to two source-pixel v2 crops.

Direct source-page evidence recorded by assistant; v2 outputs remain DRAFT until
v2 images are individually opened and compared. Keeps original v1 image immutable.
"""
import hashlib,io,json,sqlite3
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/111"
SRC=R/"sudu/data/original/111/00-E/p004-4fef546202-v2-w1400-q66.webp"
CROPS={
    "111-00-E-24": [90,1650,1310,1705],
    "111-00-E-25": [90,1705,1310,1759],
}
def read(n):return json.loads((D/n).read_text("utf-8"))
def write(n,data):(D/n).write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    imbytes=SRC.read_bytes()
    with Image.open(io.BytesIO(imbytes)) as im:
        assert im.format=="WEBP" and im.size==(1400,1980)
    manifest=read("webp-manifest.json")
    corpus=read("questions.json")
    visual=read("VISUAL_QA.json")
    inv=read("inventory.json")
    valid=read("VALIDATION.json")
    release=read("release-manifest.json")
    ocr=read("ocr-raw-candidates.json")
    mi={x["questionId"]:x for x in manifest["items"]}
    qi={x["questionId"]:x for x in corpus["questions"]}
    vi={x["questionId"]:x for x in visual["items"]}
    oi={x["questionId"]:x for x in ocr["items"]}
    history=[]
    for qid,box in CROPS.items():
        old=mi[qid]
        previous={k:old.get(k) for k in
            ["qaStatus","output","outputSha256","cropPixels","source","sourcePage"]}
        if old.get("output"):
            oldpath=R/old["output"]
            assert oldpath.is_file() and sha(oldpath.read_bytes())==old["outputSha256"]
        dest=D/"webp-v2/00-E"/(qid+".webp")
        with Image.open(io.BytesIO(imbytes)) as original:
            out=io.BytesIO()
            original.crop(tuple(box)).save(out,"WEBP",lossless=True,method=6)
        data=out.getvalue()
        with Image.open(io.BytesIO(data)) as restored:
            restored.load()
            assert restored.format=="WEBP" and list(restored.size)==[box[2]-box[0],box[3]-box[1]]
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=data:
            raise RuntimeError("v2 exists with different bytes; never overwrite an existing version")
        if not dest.exists():dest.write_bytes(data)
        newpath=dest.relative_to(R).as_posix()
        digest=sha(data)
        old.update({"source":SRC.relative_to(R).as_posix(),
            "sourcePageWebpSha256":sha(imbytes),"sourcePage":4,
            "cropPixels":box,"output":newpath,
            "outputSize":[box[2]-box[0],box[3]-box[1]],
            "outputSha256":digest,"qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
            "generationVersion":"111-english-q24-q25-crop-split-v2"})
        old.setdefault("issues",[])
        for marker in ["PREVIOUS_Q24_INCLUDED_ADJACENT_Q25",
                       "V2_NEEDS_DIRECT_VISUAL_INSPECTION"]:
            if marker not in old["issues"]:old["issues"].append(marker)
        old.setdefault("previousVersion",previous)
        q=qi[qid]
        q["assets"].update({"singleQuestionWebp":newpath,
            "sourcePageWebp":SRC.relative_to(R).as_posix(),"sourcePage":4,"sha256":digest})
        q["imageQaStatus"]="DRAFT_NEEDS_DIRECT_VISUAL_QA"
        q["questionVerified"]=False
        q["answerVerified"]=False
        q["integrationReady"]=False
        v=vi[qid]
        v.update({"status":"PENDING","sourcePage":4,"sourceWebp":SRC.relative_to(R).as_posix(),
                  "candidateWebp":newpath,"candidateSha256":digest,
                  "reviewer":None,"visualEvidence":None})
        if qid.endswith("-25"):
            import pytesseract
            with Image.open(dest) as im:
                raw=pytesseract.image_to_string(im,lang="eng",config="--psm 6")
            oi[qid]["rawOcrText"]=raw
            oi[qid]["rawOrigin"]="DRAFT_UNCORRECTED_OCR_111_EN_Q25_V2"
            oi[qid]["imageSha256"]=digest
            oi[qid]["qaStatus"]="PENDING"
            q["ocrStatus"]="DRAFT_UNCORRECTED_OCR"
        history.append({"questionId":qid,"oldVersion":previous,
            "v2Path":newpath,"v2Sha256":digest,"v2CropPixels":box,
            "result":"REPAIRED_CANDIDATE_PENDING_QA"})
    assert sum(bool(x.get("output")) for x in manifest["items"])==205
    inv["webpGeneratedDrafts"]=205
    inv["visualQaPass"]=0
    inv["sourcePaperStats"]["00-E"]["imageDrafts"]=42
    inv["sourcePaperStats"]["00-E"]["unresolvedAnchorNumbers"]=[]
    inv["sourcePaperStats"]["00-E"]["manualAnchorRepair"]="Q25 was visually located directly below Q24 on original page 4"
    valid["sourceGaps"]["00-E"]=inv["sourcePaperStats"]["00-E"]
    valid["imageVisualQaPass"]=0
    valid["integrationReady"]=False
    release["releaseAllowed"]=False
    release["integrationReady"]=False
    write("webp-manifest.json",manifest)
    write("questions.json",corpus)
    write("VISUAL_QA.json",visual)
    write("inventory.json",inv)
    write("VALIDATION.json",valid)
    write("release-manifest.json",release)
    write("ocr-raw-candidates.json",ocr)
    write("111-EN-Q24-Q25-REPAIR-EVIDENCE.json",{
        "year":111,"paperCode":"00-E","officialSourcePage":SRC.relative_to(R).as_posix(),
        "originalPageSha256":sha(imbytes),
        "reviewNote":"Direct visual view showed v1 Q24 included both Q24 and Q25; Q25 originally had no single-question crop.",
        "repairStatus":"DRAFT_UNTIL_INDEPENDENT_V2_VISUAL_RECHECK",
        "records":history})
    with sqlite3.connect(D/"question-bank.sqlite3") as cx:
        for qid in CROPS:
            payload=json.dumps(qi[qid],ensure_ascii=False,sort_keys=True,separators=(",",":"))
            assert cx.execute(
                "UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                (payload,sha(payload.encode()),qid)).rowcount==1
        cx.commit()
        rows=cx.execute("SELECT question_id,payload,payload_sha256 FROM questions").fetchall()
        assert len(rows)==205 and cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        for qid,payload,hashvalue in rows:
            assert sha(payload.encode())==hashvalue
    print("111 English Q24/Q25 split v2 generated; 205 candidate WebP; 0 visual QA; source originals preserved.")

if __name__=="__main__":
    main()
