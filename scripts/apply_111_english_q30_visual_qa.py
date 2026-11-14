#!/usr/bin/env python3
"""Apply real Q30 v2 page-to-image QA without altering official answer state."""
import hashlib,json,sqlite3
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/111"
ID="111-00-E-30"
E=D/"VISUAL_QA_111_EN_Q30_V2_2026-10-22.json"
def read(p):return json.loads((D/p).read_text("utf-8"))
def write(p,obj):(D/p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    e=json.loads(E.read_text("utf-8"))
    assert e["questionId"]==ID and e["result"]=="PASS_ASSISTANT_DIRECT_VISUAL"
    assert all(e["criteria"].values()) and not e["independentHumanReview"]
    m=read("webp-manifest.json")
    corpus=read("questions.json")
    qa=read("VISUAL_QA.json")
    inv=read("inventory.json")
    val=read("VALIDATION.json")
    rel=read("release-manifest.json")
    a=next(x for x in m["items"] if x["questionId"]==ID)
    q=next(x for x in corpus["questions"] if x["questionId"]==ID)
    v=next(x for x in qa["items"] if x["questionId"]==ID)
    assert a["qaStatus"]!="PASS"
    assert a["output"]==e["webp"] and a["outputSha256"]==e["webpSha256"]
    assert a["source"]==e["source"] and a["sourcePageWebpSha256"]==e["sourceSha256"]
    assert a["cropPixels"]==e["cropPixels"]
    assert digest(R/e["webp"])==e["webpSha256"]
    assert digest(R/e["source"])==e["sourceSha256"]
    with Image.open(R/e["webp"]) as img:
        img.load()
        assert img.format=="WEBP" and list(img.size)==a["outputSize"]
    assert e["sharedMaterialId"] in q["sharedMaterialIds"]
    assert any(x["sharedMaterialId"]==e["sharedMaterialId"] and x["qaStatus"]=="PASS" for x in m["sharedMaterialCrops"])
    a["qaStatus"]="PASS"
    a["visualReviewEvidence"]={"reference":E.relative_to(R).as_posix(),
        "reviewedSha256":e["webpSha256"],"reviewer":e["reviewer"],
        "reviewedAt":e["reviewedOn"],"independentHumanReview":False}
    q["imageQaStatus"]="PASS"
    q["assets"]["imageQaEvidence"]=E.relative_to(R).as_posix()
    q["answerVerified"]=False
    q["questionVerified"]=False
    q["integrationReady"]=False
    v["status"]="PASS"
    v["reviewer"]=e["reviewer"]
    v["visualEvidence"]=E.relative_to(R).as_posix()
    v["reviewedWebpSha256"]=e["webpSha256"]
    n=sum(x["qaStatus"]=="PASS" for x in m["items"])
    assert n==10
    qa["passCount"]=n
    inv["visualQaPass"]=n
    val["imageVisualQaPass"]=n
    val["integrationReady"]=False
    val["releaseAllowed"]=False
    rel["imageQA"]="PARTIAL_10_OF_205"
    rel["integrationReady"]=False
    rel["releaseAllowed"]=False
    for file,data in [("webp-manifest.json",m),("questions.json",corpus),
                      ("VISUAL_QA.json",qa),("inventory.json",inv),
                      ("VALIDATION.json",val),("release-manifest.json",rel)]:
        write(file,data)
    with sqlite3.connect(D/"question-bank.sqlite3") as db:
        raw=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        assert db.execute("UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                          (raw,hashlib.sha256(raw.encode()).hexdigest(),ID)).rowcount==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
    print("111 English Q21-Q30: 10/205 image QA PASS, 2 shared PASS, independent official-answer verification PENDING")

if __name__=="__main__":main()
