#!/usr/bin/env python3
"""Quarantine legacy false Q80 from 110 paper 09-1: official cover says 50 questions.

Preserves the original 110.json unchanged and exact phantom in quarantine.
Only changes isolated 110 processed staging JSON/SQLite; no students or main.
"""
import hashlib,json,sqlite3
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
D=R/"sudu/data/processed/110"
ORIG=R/"sudu/data/years/110.json"
COVER=R/"sudu/data/original/110/09-1/p001-f342faa802-v2-w1400-q66.webp"
ID="110-09-1-80"
def read(p):return json.loads(p.read_text("utf-8"))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert COVER.is_file() and ORIG.is_file()
    with Image.open(COVER) as im:
        im.load()
        assert im.format=="WEBP"
    original=read(ORIG)
    paper=next(p for p in original["papers"] if p["paper"]=="09-1")
    old=next(q for q in paper["questions"] if q["id"]==ID)
    assert old["number"]==80
    assert {q["number"] for q in paper["questions"] if q["id"]!=ID}==set(range(1,51))
    c=read(D/"questions.json")
    manifest=read(D/"webp-manifest.json")
    ocr=read(D/"ocr-raw-candidates.json")
    answer=read(D/"official-answer-evidence.json")
    visual=read(D/"VISUAL_QA.json")
    inv=read(D/"inventory.json")
    validation=read(D/"VALIDATION.json")
    release=read(D/"release-manifest.json")
    qx=next(q for q in c["questions"] if q["questionId"]==ID)
    mx=next(q for q in manifest["items"] if q["questionId"]==ID)
    ax=next(q for q in answer["items"] if q["questionId"]==ID)
    ox=next(q for q in ocr["items"] if q["questionId"]==ID)
    vx=next(q for q in visual["items"] if q["questionId"]==ID)
    assert not mx.get("output") and mx["qaStatus"]=="BLOCKED_NO_SINGLE_QUESTION_WEBP"
    assert not qx["answerVerified"] and not qx["questionVerified"] and not qx["integrationReady"]
    write(D/"QUARANTINED_LEGACY_Q80.json",{
        "year":110,"paperCode":"09-1","questionId":ID,
        "status":"EXCLUDED_FROM_STAGING_NOT_DELETED_FROM_ORIGINAL",
        "officialCoverImage":COVER.relative_to(R).as_posix(),
        "officialCoverImageSha256":sha(COVER),
        "officialCoverVisuallyReviewedBy":"ChatGPT assistant",
        "officialCoverEvidence":"110 professional subject (I) explicitly declares 50 total questions: Q1-25 and Q26-50.",
        "reason":"Legacy parser mistakenly labeled a text/option fragment as Q80; paper has 50 actual questions.",
        "originalYearJson":ORIG.relative_to(R).as_posix(),
        "originalYearJsonSha256":sha(ORIG),
        "preservedOriginalCandidate":old,
        "preservedProcessedRecord":qx,
        "preservedManifestRecord":mx,
        "preservedAnswerRecord":ax,
        "preservedOcrRecord":ox,
        "preservedVisualQaRecord":vx,
        "originalSourceUntouched":True,
        "userRecordsUntouched":True,
        "releaseAllowed":False})
    def exclude(items):
        new=[v for v in items if v["questionId"]!=ID]
        assert len(items)==len(new)+1
        return new
    c["questions"]=exclude(c["questions"])
    manifest["items"]=exclude(manifest["items"])
    answer["items"]=exclude(answer["items"])
    ocr["items"]=exclude(ocr["items"])
    visual["items"]=exclude(visual["items"])
    assert len(c["questions"])==204
    assert len({q["questionId"] for q in c["questions"]})==204
    assert {q["originalQuestionNumber"] for q in c["questions"] if q["paperCode"]=="09-1"}==set(range(1,51))
    inv["totalCandidateQuestions"]=204
    inv["expectedFromLegacy"]=204
    inv["webpGeneratedDrafts"]=204
    inv["legacyQuarantinedIds"]=[ID]
    inv["officialCoverQuestionCountCheck"]="09-1: 50, not 51"
    paper_stat=inv["sourcePaperStats"]["09-1"]
    paper_stat["candidateRecords"]=50
    paper_stat["imageDrafts"]=50
    paper_stat["legacyIdNumberGap"]=[]
    paper_stat["unresolvedAnchorNumbers"]=[]
    paper_stat["historicalFalsePositiveQuarantined"]=ID
    validation["sourceGaps"]["09-1"]=paper_stat
    validation["officialExpectedQuestionCountsConfirmed"]=False
    validation["officialCountExceptionsReviewed"]={"09-1":50}
    validation["releaseAllowed"]=False
    validation["integrationReady"]=False
    release["integrationReady"]=False
    release["releaseAllowed"]=False
    for path,x in [(D/"questions.json",c),(D/"webp-manifest.json",manifest),
                   (D/"official-answer-evidence.json",answer),
                   (D/"ocr-raw-candidates.json",ocr),(D/"VISUAL_QA.json",visual),
                   (D/"inventory.json",inv),(D/"VALIDATION.json",validation),
                   (D/"release-manifest.json",release)]:
        write(path,x)
    (D/"DATA_HANDOFF.md").write_text(
        "# 110 年 staging corpus（僅候選）\n\n"
        "- 官方 09-1 試卷封面證明總題數 50，舊擷取 110-09-1-80 已完整保存在 QUARANTINED_LEGACY_Q80.json。\n"
        "- 既有 sudu/data/years/110.json 原始資料未修改。\n"
        "- 本年候選正式試題 204 題，WebP 候選 204 題。\n"
        "- 所有單題 WebP 的逐題目視驗收仍為 0；最終官方答案／更正核對待辦。\n"
        "- SQLite 204 題重複導入讀回／SHA 待驗收；不得接入正式平台。\n",encoding="utf-8")
    checklist=["# 110 年單題目視 QA 待辦（不包括已保留的假第 80 題）","",
               "- 110-09-1-80 見 QUARANTINED_LEGACY_Q80.json（不得自動補造第80題）。",""]
    checklist += ["- [ ] "+x["questionId"]+" | "+(x.get("output") or "missing crop")
                  for x in manifest["items"] if x["qaStatus"]!="PASS"]
    (D/"REMAINING_QA.md").write_text("\n".join(checklist)+"\n",encoding="utf-8")
    with sqlite3.connect(D/"question-bank.sqlite3") as db:
        rows=db.execute("DELETE FROM questions WHERE question_id=?",(ID,)).rowcount
        assert rows==1
        db.commit()
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
        assert db.execute("SELECT COUNT(*) FROM questions WHERE paper_code='09-1'").fetchone()[0]==50
    print("110 09-1 official cover 50 questions; phantom legacy Q80 quarantined (original preserved); staging SQLite 204.")

if __name__=="__main__":main()
