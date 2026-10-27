#!/usr/bin/env python3
"""Apply genuine direct source-image QA evidence for 111 EN cloze Q21-Q29+two shared.
Q30 is excluded until v2 crop is visually reviewed. No answer verification or release.
"""
import hashlib,json,sqlite3
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/"sudu/data/processed/111"
E=D/"VISUAL_QA_111_EN_CLOZE_BATCH_01.json"
def read(name):return json.loads((D/name).read_text("utf-8"))
def write(name,data):(D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ev=json.loads(E.read_text("utf-8"))
    assert ev["independentHumanReview"] is False and len(ev["records"])==9
    assert {x["questionId"] for x in ev["records"]}=={f"111-00-E-{n:02d}" for n in range(21,30)}
    assert ev["notReviewed"]==["111-00-E-30"]
    mani=read("webp-manifest.json");corpus=read("questions.json")
    qa=read("VISUAL_QA.json");inv=read("inventory.json")
    val=read("VALIDATION.json");rel=read("release-manifest.json")
    m={x["questionId"]:x for x in mani["items"]}
    q={x["questionId"]:x for x in corpus["questions"]}
    v={x["questionId"]:x for x in qa["items"]}
    ms={x["sharedMaterialId"]:x for x in mani["sharedMaterialCrops"]}
    qs={x["sharedMaterialId"]:x for x in corpus["sharedMaterials"]}
    for r in ev["records"]:
        ident=r["questionId"];x=m[ident]
        assert r["webp"]==x["output"] and r["webpSha256"]==x["outputSha256"]
        assert r["source"]==x["source"] and r["sourceSha256"]==x["sourcePageWebpSha256"]
        assert r["cropPixels"]==x["cropPixels"]
        assert sha(R/r["webp"])==r["webpSha256"] and sha(R/r["source"])==r["sourceSha256"]
        assert all(r["criteria"].values())
        with Image.open(R/r["webp"]) as im:
            im.load(); assert im.format=="WEBP" and list(im.size)==x["outputSize"]
        x["qaStatus"]="PASS"
        x["visualReviewEvidence"]={"reference":E.relative_to(R).as_posix(),
            "reviewedSha256":r["webpSha256"],"reviewer":"ChatGPT assistant",
            "reviewedOn":ev["reviewDate"],"independentHumanReview":False,
            "criteria":r["criteria"]}
        q[ident]["imageQaStatus"]="PASS"
        q[ident]["assets"]["imageQaEvidence"]=E.relative_to(R).as_posix()
        q[ident]["questionVerified"]=False
        q[ident]["answerVerified"]=False
        q[ident]["integrationReady"]=False
        v[ident]["status"]="PASS"
        v[ident]["reviewer"]="ChatGPT assistant"
        v[ident]["visualEvidence"]=E.relative_to(R).as_posix()
        v[ident]["reviewedWebpSha256"]=r["webpSha256"]
    for a in ev["sharedMaterials"]:
        ident=a["sharedMaterialId"]
        cur=ms[ident]
        assert cur["outputSha256"]==a["outputSha256"]
        assert cur["sourcePageWebpSha256"]==a["sourcePageWebpSha256"]
        assert cur["cropPixels"]==a["cropPixels"]
        assert sha(R/cur["output"])==cur["outputSha256"]
        assert sha(R/cur["source"])==cur["sourcePageWebpSha256"]
        cur["qaStatus"]="PASS"
        cur["visualReviewEvidence"]={"reference":E.relative_to(R).as_posix(),
            "reviewedSha256":cur["outputSha256"],"reviewer":"ChatGPT assistant",
            "reviewedOn":ev["reviewDate"],"independentHumanReview":False}
        qs[ident].update({"qaStatus":"PASS","visualReviewEvidence":cur["visualReviewEvidence"]})
    assert m["111-00-E-30"]["qaStatus"]!="PASS"
    pass_count=sum(x["qaStatus"]=="PASS" for x in mani["items"])
    assert pass_count==9
    qa["passCount"]=pass_count;inv["visualQaPass"]=pass_count
    inv["sharedMaterialsVerified"]=2
    val["imageVisualQaPass"]=pass_count
    val["sharedMaterialsStatus"]="PARTIAL_ASSISTANT_DIRECT_VISUAL_2_PASS"
    val["integrationReady"]=False;val["releaseAllowed"]=False
    rel["imageQA"]="PARTIAL_9_OF_205"
    rel["sharedMaterialQA"]="PARTIAL_2_PASS"
    rel["integrationReady"]=False;rel["releaseAllowed"]=False
    for path,data in [("webp-manifest.json",mani),("questions.json",corpus),
                      ("VISUAL_QA.json",qa),("inventory.json",inv),
                      ("VALIDATION.json",val),("release-manifest.json",rel)]:
        write(path,data)
    with sqlite3.connect(D/"question-bank.sqlite3") as db:
        for ident in (x["questionId"] for x in ev["records"]):
            raw=json.dumps(q[ident],ensure_ascii=False,sort_keys=True,separators=(",",":"))
            assert db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                (raw,hashlib.sha256(raw.encode()).hexdigest(),ident)).rowcount==1
        for ident in qs:
            db.execute("INSERT OR REPLACE INTO shared_materials(material_id,payload) VALUES(?,?)",
                (ident,json.dumps(qs[ident],ensure_ascii=False,sort_keys=True)))
        db.commit()
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        assert db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==2
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    print("111 English: 9 questions and 2 shared WebP visually inspected; Q30 BLOCKED; official final answer QA pending")

if __name__=="__main__":main()
