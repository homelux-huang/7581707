"""Strong 114 student evidence admission preflight. Must fail closed.

Real official, original WebP, independent-solve and teacher documents must
individually pass. A pending UI review cannot silently create READY or alter
the original records; release requires a complete student-reviewed-batch.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from scripts import sudu_verified_publish as pub
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
IDS=("114-00-E-07","114-00-E-08","114-00-E-09")
def load(x):
    return json.loads(Path(x).read_text(encoding="utf-8"))
def cert(id_,field):
    return load(BASE/"review-evidence"/(id_+"-"+field+".json"))

def main():
    qs={q["questionId"]:q for q in load(BASE/"questions.json")["questions"]}
    images={q["questionId"]:q for q in load(BASE/"webp-manifest.json")["items"]}
    original=load(BASE/"review-evidence/EN07_09_PREKEY_BLIND_SOLVE_ORIGINAL_20261024.json")
    blindOriginal={q["questionId"]:q for q in original["items"]}
    expected={"114-00-E-07":"A","114-00-E-08":"D","114-00-E-09":"D"}
    source=load(BASE/"official-answer-evidence.json")
    answers={q["questionId"]:q for q in source["items"]}
    imageAnswers=load(BASE/"QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json")
    imageAnswerRows={q["questionId"]:q for q in imageAnswers["items"]}
    inventory=load(BASE/"inventory.json")
    assert inventory["sqlite"]["roundtripPass"] is True
    assert inventory["sqlite"]["rows"]==205
    assert (BASE/"SQLITE_QA_RECONCILED_20261024.json").exists()
    evidence=[]
    for id_ in IDS:
        q,m=qs[id_],images[id_]
        rev=pub.text_revision(q,m["sha256"])
        o,off,bl,teach=(cert(id_,x) for x in ("ocr","official","blind","teaching"))
        assert pub.stable(q,114)==(id_,"英文")
        assert pub.individual_image_proof(q,m,ROOT)
        assert pub.visual_certificate(ROOT,m,id_)
        assert pub.verify_bytes(ROOT,m["output"],m["sha256"])
        assert q["question"]==o["question"] and q["options"]==o["options"]
        assert len(q["options"])==4 and all(pub.good(v) for v in q["options"])
        assert rev==o["questionRevision"]==bl["questionRevision"]==teach["questionRevision"]
        assert o["webpSha256"]==bl["webpSha256"]==m["sha256"]
        assert o["visualTextCompared"] is True and o["sourceCropsExactPixelMatched"] is True
        assert off["officialPdfSha256"]==pub.pdf_sha(q,"answer")
        assert off["finalAnswer"]==answers[id_]["officialPdfExtractedCandidate"]==q["answer"]==expected[id_]
        assert imageAnswerRows[id_]["officialVisualAnswerCandidate"]==off["finalAnswer"]
        assert imageAnswerRows[id_]["officialAnswerImageWebpSha256"]==off["officialAnswerImageSha256"]
        assert off["officialFinalAnswerImageQaPassed"] is True and off["noObjectionForPaper"] is False
        assert pub.official_notice_scope_certified(ROOT,114,q,off)
        assert bl["answer"]==blindOriginal[id_]["answer"]==expected[id_]
        assert bl["blindReasoning"]==blindOriginal[id_]["blindReasoning"]
        assert bl["historicalPreKeyCommit"]=="e676be923200587288e653e373fb57641eb84066"
        assert bl["officialAnswerHiddenDuringSolve"] and bl["solvedWithoutOfficialAnswer"]
        assert teach["allFourOptionsReviewed"] and teach["calculationReviewed"]
        assert teach["content"]["hasExamCalculation"] is False
        assert teach["content"]["examCalculation"] is None
        assert set(teach["content"]["optionExplanations"])==set("ABCD")
        for letter in "ABCD":
            each=teach["content"]["optionExplanations"][letter]
            assert all(pub.good(each.get(x)) for x in ("teacher","elementary","reason"))
        evidence.append({"id":id_,"sha256":m["sha256"],"revision":rev,
                         "actualSourceImage":True,"officialPdfImage":True,
                         "blindPreKey":True,"teacherAllFour":True,
                         "officialCorrectionScope":True})
    batch_file=BASE/"verified-student-batch.json"
    if batch_file.exists():
        batch=load(batch_file)
        actual={x["questionId"] for x in batch.get("items",[])}
        assert actual==set(IDS), "Only these three exact QA certificates are authorized in this branch"
        assert batch.get("schemaVersion")==1 and batch.get("year")==114
        promoted=[]
        for id_ in IDS:
            certs=pub.reviewed_student_batches(ROOT,114)
            revised=pub.apply_independently_certified_review(ROOT,114,qs[id_],images[id_],certs[id_])
            assert revised.get("questionVerified") is True and revised.get("answerVerified") is True
            assert pub.source_proof(revised,True,True,pub.text_revision(qs[id_],images[id_]["sha256"]))==(True,True)
            assert pub.independently_solved(revised,pub.text_revision(qs[id_],images[id_]["sha256"]))=="matched"
            assert pub.teaching_complete(revised,"英文",expected[id_])
            assert pub.certificates_complete(ROOT,revised,images[id_],{})
            promoted.append(id_)
        state="THREE_SOURCE_READY_REQUIRE_STAGED_PUBLISHER_AND_LIVE_TEST"
    else:
        promoted=[]
        state="OFFICIAL_SOURCE_AND_TEACHING_VALID_BUT_FINAL_UI_BATCH_NOT_YET_PRESENT"
    result={"schemaVersion":1,"year":114,"status":state,
            "genuineProofCount":len(evidence),"checked":evidence,
            "completeStudentCertificates":promoted,
            "officialSourceReleaseQAIndependentlyReviewed":True,
            "sourceFilesMutatedByThisCheck":False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if len(promoted)!=len(actual) if batch_file.exists() else False:
        raise AssertionError("promoted count")
if __name__=="__main__":
    main()
