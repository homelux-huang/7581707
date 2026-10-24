"""CI-ONLY V4 UI preflight of three genuine 114 source questions, not release.

Reads immutable QA original text, SHA-matched source WebP, prior independent
pre-key reasoning, teaching drafts, and existing official final-answer visuals.
Builds a temporary student-mode dataset in a separate formal-main checkout
solely for Chromium testing. No QA is approved by this staging script.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
LETTERS=("A","B","C","D")
EXPECTED=("114-00-E-07","114-00-E-08","114-00-E-09")
def load(p):
    return json.loads(p.read_text(encoding="utf-8"))
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def revision(q,sha):
    data={"question":q.get("question"),"options":q.get("options"),"singleQuestionWebpSha256":sha}
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default=".")
    parser.add_argument("--formal",required=True)
    a=parser.parse_args()
    src=Path(a.source).resolve()
    formal=Path(a.formal).resolve()
    base=src/"sudu/data/processed/114"
    question_bank={x["questionId"]:x for x in load(base/"questions.json")["questions"]}
    crops={x["questionId"]:x for x in load(base/"webp-manifest.json")["items"]}
    blind=load(base/"review-evidence/EN07_09_PREKEY_BLIND_SOLVE_ORIGINAL_20261024.json")
    teaching=load(base/"review-evidence/EN07_09_POSTKEY_TEACHING_DRAFT_20261024.json")
    oev={x["questionId"]:x for x in load(base/"official-answer-evidence.json")["items"]}
    answer_qa={x["questionId"]:x for x in load(base/"QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json")["items"]}
    blind_by_id={x["questionId"]:x for x in blind["items"]}
    teacher_by_id={x["id"]:x for x in teaching["items"]}
    assert all(set(EXPECTED)==set(d) for d in (blind_by_id,teacher_by_id))
    assert blind["approvalGranted"] is False and teaching["formalStudentQaApproved"] is False
    output=[]
    provenance=[]
    for id_ in EXPECTED:
        q,m,b,t,answer_e,answer_visual=(question_bank[id_],crops[id_],blind_by_id[id_],
                                      teacher_by_id[id_],oev[id_],answer_qa[id_])
        assert q["questionId"]==id_ and len(q["options"])==4 and m["qaStatus"]=="PASS"
        assert b["answer"]==q["answer"]==answer_e["officialPdfExtractedCandidate"]==answer_visual["officialVisualAnswerCandidate"]
        assert b["officialAnswerHiddenDuringSolve"] is True and b["solvedWithoutOfficialAnswer"] is True
        assert answer_visual["directImageMatch"] is True
        assert t["answer"]==q["answer"] and len(t["optionExplanations"])==4
        assert all(set(t["optionExplanations"][k])>=set(("teacher","elementary","reason")) for k in LETTERS)
        assert not t["hasExamCalculation"] and t["examCalculation"] is None
        img=src/m["output"]
        original=src/m["source"]
        answer_png=src/answer_visual["officialAnswerImageWebpPath"]
        assert digest(img)==m["sha256"]==b["webpSha256"]
        assert digest(original)==m["sourceSha256"]
        assert digest(answer_png)==answer_visual["officialAnswerImageWebpSha256"]
        with Image.open(img) as im:
            im.load()
            assert im.format=="WEBP" and im.width > 200 and im.height > 50 and im.height < 1000
        image_rel=f"data/approved/webp/114/{id_}.webp"
        staged_img=formal/"sudu"/image_rel
        staged_img.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(img,staged_img)
        assert digest(staged_img)==m["sha256"]
        rec=revision(q,m["sha256"])
        output.append({
            "id":q["originalQuestionNumber"],"canonicalId":id_,"year":114,
            "subject":"英文","topic":t["topic"],
            "question":q["question"],"options":q["options"],"answer":q["answer"],
            "memory":t["memory"],"concept":t["concept"],
            "extension":t["extension"],"formula":t.get("formula") or "",
            "sourceText":t["source"],"extra":{},"highlights":["英文","考題重點"],
            "teacherSummary":t["teacherSummary"],
            "elementarySummary":t["elementarySummary"],
            "optionExplanations":t["optionExplanations"],
            "examCalculation":None,
            "image":image_rel,"imageSha256":m["sha256"]
        })
        provenance.append({
            "id":id_,"questionRevision":rec,"WebpSha256":m["sha256"],
            "sourceOriginalPageSha256":m["sourceSha256"],
            "officialFinalAnswerPdfSha256":answer_e["officialPdfSha256"],
            "officialAnswerImageSha256":answer_visual["officialAnswerImageWebpSha256"],
            "historicalBlindCommit":"e676be923200587288e653e373fb57641eb84066",
            "teachingSource":t["id"],"independentSourceVisualQaAlreadyRecorded":True,
            "uiFormalStudentModePass":False,"studentQaApproved":False
        })
    f114=formal/"sudu/data/approved/114.json"
    assert f114.is_file(),"formal main missing approved 114 source"
    saved=load(f114)
    assert saved["approvedCount"]==0, "not a clean formal 114 baseline"
    snapshot={"schemaVersion":1,"year":114,"expected":205,"approvedCount":3,
        "sourceSha":"CI_ONLY_NOT_OFFICIAL_QA_APPROVAL","questions":output,
        "_temporaryCiUiPreflight":True,"_notForPagesRelease":True}
    f114.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    progress=formal/"sudu/data/approved/progress.json"
    p=load(progress)
    assert p["years"]["114"]["approvedCount"]==0
    p["years"]["114"]["approvedCount"]=3
    p["years"]["114"]["subjects"]["英文"]["studentReady"]=3
    p["years"]["114"]["reviewStatus"]="CI_ONLY_TEMPORARY_BROWSER_FIXTURE_NOT_RELEASE"
    p["_temporaryCiUiPreflight"]=True
    progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    records={"schemaVersion":1,"year":114,"studentQaApproved":False,
       "formalSourceQaCommitToBePinnedByCI":True,"questionCount":3,"questions":provenance}
    Path("/tmp/qa114-v4-source-hashes.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS: staged exactly THREE genuine 114 original WebP and two-level lessons in CI-only formal V4; ZERO QA approvals")

if __name__=="__main__":main()
