"""CI ONLY: transiently exercise REAL reviewed source records, not for publication."""
from pathlib import Path
from scripts import sudu_verified_publish as v

def main():
    src=Path("_source_qa")
    d=src/"sudu/data/processed/115"
    path=d/"verified-student-batch.json"
    if not path.exists():
        print("No audited student batch; nothing to stage.")
        return
    bank=v.read(d/"questions.json")
    manifest=v.read(d/"webp-manifest.json")
    qs={q["questionId"]:q for q in bank["questions"]}
    items={q["questionId"]:q for q in manifest["items"]}
    batch=v.read(path)
    expected=[]
    for audit in batch["items"]:
        if audit.get("status")!="QA_PENDING_UI":
            continue
        qid=audit["questionId"]
        q=qs[qid]
        rev=v.text_revision(q,items[qid]["sha256"])
        v.dump(src/audit["evidence"]["ui"],{
            "schemaVersion":1,"year":115,"questionId":qid,
            "testedQuestionRevision":rev,
            "browserSmokePassed":True,"rwdPassed":True,"verifiedYearQaMode":True,
            "ciRunUrl":"https://github.com/homelux-huang/7581707/actions/runs/123",
            "reviewer":"Ephemeral CI simulated UI audit, NOT official QA approval",
            "reviewedAt":"2026-10-23"
        })
        audit["status"]="STUDENT_QA_APPROVED"
        expected.append(qid)
    if not expected:
        print("No outstanding provisional UI certificates.")
        return
    v.dump(path,batch)
    v.stage(src,Path("."),"CI_ONLY_EPHEMERAL")
    v.site_check(Path("."))
    result=v.read(Path("sudu/data/approved/115.json"))
    got={x["canonicalId"] for x in result["questions"]}
    assert set(expected).issubset(got), f"Missing source-matched independent release records: {set(expected)-got}"
    for x in result["questions"]:
        if x["canonicalId"] in expected:
            assert len(x["options"])==4 and set(x["optionExplanations"])==set("ABCD")
            assert x["examCalculation"] and x["examCalculation"]["hasExamCalculation"]
            assert x["imageSha256"]==items[x["canonicalId"]]["sha256"]
    print(f"PASS: {len(expected)} real-source records passed simulated UI-only certificates; test never pushes or publishes.")

if __name__=="__main__":
    main()
