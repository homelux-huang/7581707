#!/usr/bin/env python3
"""ROLE A: 114 C23 original official D admission stacked after earlier C20–22.

Only one answer + notice source receipt and one 114 canonical SQLite payload row.
Preserve archived raw Q23/end-page warning, original SHA, role separation, NO RELEASE.
"""
import argparse
import copy
import json
import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from scripts import role_a_114_c20_c22_final_official as earlier

ROOT=earlier.ROOT
BANK=earlier.BANK
DB=earlier.DB
QID="114-00-C-23"
TASK="A-114-C23-FINAL-ANSWER-SHARED-20261026-16"
BASE_SHA="e448bf0c814ae3a2075faea23ba75b244519928d"
BASE_BANK_GIT="924edbd8eb6576a844f2d8145781b339b23f3b45"
BASE_DB_GIT="e7e0e589a2bfbc51115884802958aff934841829"
ORIGINAL_GIT="ba29b99f00b9b556b834e27b88918831a5ffe35b"
ORIGINAL_SHA="50547b2a2daa71dea457bd11bf4ebb1a4bcc780e0443ac6cda15374829e67cc1"
ORIGINAL_CROP=[90,1582,1310,1823]
ORIGINAL_PATH=ROOT/"sudu/data/processed/114/webp-v1/00-C/114-00-C-23.webp"
PROOF=earlier.EVIDENCE/(QID+"-official.json")
def verify_previous_c20_to22_with_fixed_pr98_baseline():
    # Prior PR98's OWN 8 tests are independently replayed at their immutable
    # original worktree/DB by CI. On this successor branch, require all three
    # exact SHA-bound source and official proofs to remain byte/semantic equal
    # to PR98, while allowing ONLY newly leased C23 to change.
    earlier.verify_archives()
    original=subprocess.run(["git","show",BASE_SHA+":sudu/data/processed/114/questions.json"],
        cwd=ROOT,capture_output=True,check=True).stdout
    assert earlier.gitsha(original)==BASE_BANK_GIT
    was={q["questionId"]:q for q in json.loads(original)["questions"]}
    now=earlier.read(BANK)
    present={q["questionId"]:q for q in now["questions"]}
    assert len(was)==len(present)==205
    assert set(was)==set(present)
    for qid,letter in earlier.ANSWER.items():
        old=was[qid];q=present[qid]
        assert q==old,(qid,"previous official admission mutated")
        proof=earlier.read(earlier.receipt_path(qid))
        assert proof["questionId"]==qid and proof["finalAnswer"]==letter
        assert proof["officialAnswerImageSha256"]==earlier.sha(earlier.ORIGINAL_ANSWER.read_bytes())
        assert proof["officialAnswerImageGitBlobSha1"]==earlier.ORIGINAL_ANSWER_GIT
        assert proof["reviewedSingleQuestionWebpSha256"]==earlier.IMAGE[qid][1]
        assert proof["confirmationPdfSha256"]==earlier.NOTICE_PDF_SHA
        assert earlier.publisher.official_notice_scope_certified(ROOT,114,q,proof)
        assert q["answerVerified"] is True and q["officialFinalAnswer"]==letter
        assert q["questionVerified"] is False
        assert not proof["independentRoleEContentQaPerformed"]
        assert not proof["readyOrLivePromoted"]
    earlier.db_precheck(DB,now)
def source():
    verify_previous_c20_to22_with_fixed_pr98_baseline()
    sha=earlier.assert_webp(ORIGINAL_PATH,ORIGINAL_GIT,ORIGINAL_SHA,[1220,241])
    assert sha==ORIGINAL_SHA
    qa=earlier.read(earlier.VISUAL)
    item=next(x for x in qa["items"] if x["questionId"]==QID)
    assert item["result"]=="PASS_DIRECT_ORIGINAL_PAGE_IMAGE"
    assert item["reviewedWebpPath"]==ORIGINAL_PATH.relative_to(ROOT).as_posix()
    assert item["reviewedWebpSha256"]==ORIGINAL_SHA
    assert item["sourcePageWebpSha256"]==earlier.ORIGINAL_QUESTION_SHA
    assert item["cropSourcePixelBounds"]==ORIGINAL_CROP
    assert item["sharedMaterialIds"]==[earlier.SHARED_ID]
    assert item["independentHumanReview"] is False
    assert item["answerVerified"] is False and item["questionVerified"] is False
    assert all(item["visualCriteria"].values())
    man=earlier.read(earlier.MANIFEST)
    m=next(x for x in man["items"] if x["questionId"]==QID)
    assert m["output"]==ORIGINAL_PATH.relative_to(ROOT).as_posix()
    assert m["sha256"]==ORIGINAL_SHA and m["qaStatus"]=="PASS"
    assert m["crop"]==ORIGINAL_CROP and m["sourceSha256"]==earlier.ORIGINAL_QUESTION_SHA
    bank=earlier.read(BANK)
    assert bank["year"]==114 and len(bank["questions"])==205
    record=next(x for x in bank["questions"] if x["questionId"]==QID)
    assert record["year"]==114 and record["paperCode"]=="00-C"
    assert record["originalQuestionNumber"]==23 and record["answer"]=="D" and record["answerMatched"] is True
    assert record["assets"]["sha256"]==ORIGINAL_SHA
    assert record["assets"]["sharedMaterialIds"]==[earlier.SHARED_ID]
    assert record["questionProvenance"]["webpSha256"]==ORIGINAL_SHA
    assert record["questionProvenance"]["officialPdfSha256"]==earlier.QUESTION_PDF_SHA
    assert record["answerProvenance"]["officialPdfSha256"]==earlier.ANSWER_PDF_SHA
    assert record["imageQaStatus"]=="PASS"
    assert len(record["options"])==4 and all(str(z).strip() for z in record["options"])
    assert record["options"][3]=="旦視而暮撫，已去而復顧。甚者爪其膚以驗其生枯，搖其本以觀其疏密"
    assert record["issues"]==["last_on_page_check_possible_continuation_or_footer"]
    assert record["questionVerified"] is False and record["reviewStatus"]=="needs_review"
    return bank,record
def make_receipt():
    # Reuse established per-paper audited schema, without expanding the already
    # completed C20-22 list or falsifying a new distinct teacher/E role.
    answer_sha=earlier.sha(earlier.ORIGINAL_ANSWER.read_bytes())
    item=earlier.receipt("114-00-C-20",answer_sha)
    item.update({"taskId":TASK,"questionId":QID,"finalAnswer":"D",
                 "reviewedSingleQuestionWebpSha256":ORIGINAL_SHA,
                 "evidenceStatus":"ORIGINAL_C23_FINAL_ANNOUNCED_D_IMAGE_AND_OFFICIAL_NOTICE__QUESTION_TEXT_END_PAGE_WARNING_STILL_OPEN_NO_RELEASE"})
    item["individualPrintedAnswerCell"].update({"number":23,"observedLetter":"D",
        "manualDirectObservation":"Direct visual original archived TCTE p1 answer number23 D, original p7 whole C23 and C20-23 shared 455px article"})
    item["sourceOriginalOCRFooterRisk"]="C23 historical end-of-page warning retained, original options[3] clean; no questionVerified or complete text QA claimed"
    item["individualSourceQuestionImageQaOnly"]=True
    assert earlier.publisher.official_notice_scope_certified(ROOT,114,{"questionId":QID,"paperCode":"00-C"},item)
    assert item["officialConfirmationNamedQuestionIds"]==earlier.NAMED
    assert QID not in earlier.NAMED
    return item
def promote(old,proof):
    new=copy.deepcopy(old)
    rev=earlier.publisher.text_revision(old,ORIGINAL_SHA)
    assert old["answerVerified"] is False
    assert old["questionVerified"] is False
    assert old.get("officialCorrectionChecked") is not True
    assert old.get("officialFinalQaEvidence") is None
    assert proof["questionId"]==QID and proof["finalAnswer"]=="D"
    assert earlier.publisher.official_notice_scope_certified(ROOT,114,old,proof)
    new["answerVerified"]=True
    new["officialFinalAnswer"]="D"
    new["officialCorrectionChecked"]=True
    new["answerProvenance"]["independentVisualVerification"]=True
    new["officialFinalQaEvidence"]={
        "reviewer":earlier.REVIEWER,"reviewedAt":earlier.REVIEWED_AT,
        "evidencePath":PROOF.relative_to(ROOT).as_posix(),
        "answerPdfSha256":earlier.ANSWER_PDF_SHA,"finalCorrectionsReviewed":True}
    assert earlier.publisher.text_revision(new,ORIGINAL_SHA)==rev
    assert new["questionVerified"] is False
    assert new["issues"]==old["issues"]
    assert new["reviewStatus"]=="needs_review"
    assert new.get("studentReleaseApproved") is not True and new.get("integrationReady") is not True
    return new
def verify():
    bank,q=source()
    proof=earlier.read(PROOF)
    assert proof["questionId"]==QID and proof["taskId"]==TASK
    assert proof["finalAnswer"]=="D"
    assert proof["individualPrintedAnswerCell"]["observedLetter"]=="D"
    assert proof["individualPrintedAnswerCell"]["number"]==23
    assert proof["reviewedSingleQuestionWebpSha256"]==ORIGINAL_SHA
    assert proof["officialAnswerImageSha256"]==earlier.sha(earlier.ORIGINAL_ANSWER.read_bytes())
    assert proof["confirmationPdfSha256"]==earlier.NOTICE_PDF_SHA
    assert proof["noObjectionForPaper"] is False and proof["noCorrectionForThisQuestion"] is True
    assert proof["officialFinalAnswerImageQaPassed"] is True
    assert not any(proof[x] for x in ("humanReviewerClaimed","independentRoleEContentQaPerformed",
                 "sourceTextVerifiedPromoted","questionVerifiedPromoted","teachingQaPromoted",
                 "uiQaPromoted","readyOrLivePromoted","officialAnswerPdfDownloadedAndRehashedThisSession"))
    assert earlier.publisher.official_notice_scope_certified(ROOT,114,q,proof)
    assert q["answerVerified"] is True and q["officialFinalAnswer"]=="D"
    assert q["officialCorrectionChecked"] is True
    assert q["answerProvenance"]["independentVisualVerification"] is True
    assert q["officialFinalQaEvidence"]["evidencePath"]==PROOF.relative_to(ROOT).as_posix()
    assert q["questionVerified"] is False
    earlier.db_precheck(DB,bank)
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)/"base.sqlite3"
        old=subprocess.run(["git","show",BASE_SHA+":sudu/data/processed/114/question-bank.sqlite3"],
            cwd=ROOT,check=True,capture_output=True).stdout
        assert earlier.gitsha(old)==BASE_DB_GIT
        base.write_bytes(old)
        one=Path(td)/"one.sqlite3";two=Path(td)/"two.sqlite3"
        for path in [one,two]:
            earlier.update_db(base,path,{QID:q})
            assert earlier.sha(path.read_bytes())==earlier.sha(DB.read_bytes())
        with sqlite3.connect(base) as con,sqlite3.connect(DB) as now:
            orig={i:(p,h) for i,p,h in con.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
            curr={i:(p,h) for i,p,h in now.execute("SELECT question_id,payload_json,payload_sha256 FROM questions")}
        assert {i for i in orig if orig[i]!=curr[i]}=={QID}
    print("ROLE_A_114_C23_OFFICIAL_D_205_SQL_SHA_SOURCE_REVISION",
          earlier.publisher.text_revision(q,ORIGINAL_SHA),"imageSHA",ORIGINAL_SHA)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");ap.add_argument("--verify",action="store_true")
    args=ap.parse_args()
    if args.apply==args.verify:ap.error("one mode")
    bank,q=source()
    if args.verify:verify();return
    if q["answerVerified"] is True:
        verify()
        print("IDEMPOTENT ZERO NEW CHANGES")
        return
    assert earlier.gitsha(BANK.read_bytes())==BASE_BANK_GIT,"source drift: refuse overwrite"
    assert earlier.gitsha(DB.read_bytes())==BASE_DB_GIT,"SQLite drift: refuse overwrite"
    earlier.db_precheck(DB,bank)
    assert not PROOF.exists(),"do not overwrite prior evidence"
    proof=make_receipt()
    revised=promote(q,proof)
    new=copy.deepcopy(bank)
    for i,item in enumerate(new["questions"]):
        if item["questionId"]==QID:new["questions"][i]=revised
        else:assert item==bank["questions"][i],item["questionId"]
    with tempfile.TemporaryDirectory(prefix="role-a114-c23-",dir=earlier.BASE) as td:
        td=Path(td)
        path=td/"question-bank.sqlite3"
        earlier.update_db(DB,path,{QID:revised})
        bfile=td/"questions.json"
        bfile.write_text(json.dumps(new,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        p=td/"114-00-C-23-official.json"
        p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        os.replace(bfile,BANK);os.replace(path,DB);os.replace(p,PROOF)
    verify()
    print("ACTUAL_114_C23_FINAL_OFFICIAL_D_ONLY_SQL_SOURCE_QA_NOT_STUDENT_READY")
if __name__=="__main__":
    main()
