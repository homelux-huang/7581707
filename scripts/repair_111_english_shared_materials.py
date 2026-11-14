#!/usr/bin/env python3
"""Build separate source-pixel DRAFT passages for 111 English cloze groups 21-25/26-30.

These are not manually QA-passed until the output and full source are compared.
Never changes student records, main or any original source images.
"""
import hashlib,io,json,sqlite3
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/111"
GROUPS=[
("111-00-E-SHARED-21-25","sudu/data/original/111/00-E/p004-4fef546202-v2-w1400-q66.webp",
 "7d26e9485a860ded0fbef125b9b507127176092c35633a7909966559bc47a325",4,[90,980,1310,1495],list(range(21,26))),
("111-00-E-SHARED-26-30","sudu/data/original/111/00-E/p005-4fef546202-v2-w1400-q66.webp",
 "5b863eed47580b798a6a4dbda7486cd57788a0e5409424da4dbd063a65712a80",5,[90,158,1310,601],list(range(26,31)))
]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads((D/p).read_text(encoding="utf-8"))
def write(p,x):(D/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    manifest=read("webp-manifest.json")
    corpus=read("questions.json")
    inv=read("inventory.json")
    valid=read("VALIDATION.json")
    release=read("release-manifest.json")
    byid={x["questionId"]:x for x in corpus["questions"]}
    new=[]
    for groupid,srcpath,expected_hash,pageno,box,numbers in GROUPS:
        src=R/srcpath
        sourcebytes=src.read_bytes()
        assert sha(sourcebytes)==expected_hash
        with Image.open(io.BytesIO(sourcebytes)) as im:
            assert im.format=="WEBP"
            assert im.width==1400
            blob=io.BytesIO()
            im.crop(tuple(box)).save(blob,"WEBP",lossless=True,method=6)
        buf=blob.getvalue()
        filename=D/"webp-v2/shared"/(groupid+".webp")
        filename.parent.mkdir(parents=True,exist_ok=True)
        if filename.exists() and filename.read_bytes()!=buf:raise ValueError("Shared v2 would overwrite prior image")
        filename.write_bytes(buf)
        entry={"sharedMaterialId":groupid,"paperCode":"00-E","originalQuestionNumbers":numbers,
               "source":srcpath,"sourcePage":pageno,"sourcePageWebpSha256":expected_hash,
               "cropPixels":box,"output":filename.relative_to(R).as_posix(),
               "outputSha256":sha(buf),"qaStatus":"DRAFT_NEEDS_DIRECT_VISUAL_QA",
               "issues":["check_complete_passage_without_adjacent_questions","verify_headings_required"]}
        new.append(entry)
        for n in numbers:
            q=byid[f"111-00-E-{n:02d}"]
            links=q.setdefault("sharedMaterialIds",[])
            if groupid not in links:links.append(groupid)
            q["questionVerified"]=False
            q["integrationReady"]=False
        # Copy one canonical shared record to the bank for future viewer contract.
        matches=[x for x in corpus["sharedMaterials"] if x["sharedMaterialId"]==groupid]
        if matches:
            assert matches[0]["outputSha256"]==entry["outputSha256"]
        else:
            corpus["sharedMaterials"].append(entry)
        matches=[x for x in manifest["sharedMaterialCrops"] if x["sharedMaterialId"]==groupid]
        if matches:
            assert matches[0]["outputSha256"]==entry["outputSha256"]
        else:
            manifest["sharedMaterialCrops"].append(entry)
    inv["sharedMaterialsDrafts"]=len(manifest["sharedMaterialCrops"])
    inv["sharedMaterialsVerified"]=0
    valid["integrationReady"]=False
    valid["sharedMaterialsStatus"]="DRAFT_INDIVIDUAL_VISUAL_QA_REQUIRED"
    release["integrationReady"]=False
    release["releaseAllowed"]=False
    write("questions.json",corpus)
    write("webp-manifest.json",manifest)
    write("inventory.json",inv)
    write("VALIDATION.json",valid)
    write("release-manifest.json",release)
    write("111-EN-SHARED-MATERIAL-DRAFT.json",{
       "year":111,"sourceRule":"pixel crop only, not synthetic",
       "status":"DRAFT_VISUAL_REVIEW_REQUIRED",
       "items":new})
    with sqlite3.connect(D/"question-bank.sqlite3") as cx:
        for n in range(21,31):
            q=byid[f"111-00-E-{n:02d}"]
            raw=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
            assert cx.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                (raw,sha(raw.encode()),q["questionId"])).rowcount==1
        for e in new:
            cx.execute("INSERT OR REPLACE INTO shared_materials(material_id,payload) VALUES(?,?)",
                (e["sharedMaterialId"],json.dumps(e,ensure_ascii=False,sort_keys=True)))
        cx.commit()
        assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert cx.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==2
        assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
    print("111 English shared cloze pixel crops: 2 candidates; visual PASS 0; no release")

if __name__=="__main__":
    main()
