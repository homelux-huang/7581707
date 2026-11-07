#!/usr/bin/env python3
"""Single-QID 114 E12 SOURCE reconciliation from immutable Role A visual evidence.
Never issues E trust, D UI PASS, student READY, approved JSON or a release.
"""
import argparse, copy, hashlib, json, sqlite3, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
QID="114-00-E-12"
FROZEN_BANK_BLOB="074bff8cbb9ca7bbc0aefd8580454892d21f7d6b"
FROZEN_MANIFEST_BLOB="249a41d5a64558ccaa3084b21f915922a55c6a1b"
FROZEN_SQLITE_BLOB="f841173ebc194ac24de4d49e2a056d769246e655"
STAGE_COMMIT="bc625d5eba9bf67f29b236258754941f0c9d999e"
STAGE_RECEIPT="sudu/data/processed/114/source-stage/114-00-E-12-staged-20261104.json"
OFFICIAL_RECEIPT="sudu/data/processed/114/review-evidence/114-00-E-12-official-20261102.json"
REPORT="sudu/data/processed/114/review-evidence/114-00-E-12-MASTER-QA-BRIDGE-20261107.json"
STAGE_RECEIPT_BLOB="3f0dc39251debf5f336edbcfa1b31c5e784e0dd3"
OFFICIAL_RECEIPT_BLOB="e166524f2e3f6921c1ba55fb23862e739307b518"
EXPECTED_REVISION="0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
EXPECTED_IMAGE="99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
EXPECTED_PAGE="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
EXPECTED_ANSWER_IMAGE="a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
EXPECTED_NOTICE="79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"

def ensure(test,message):
    if not test: raise RuntimeError("SOURCE_HOLD: "+message)
def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def sha(data):
    return hashlib.sha256(data).hexdigest()
def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
def canonical(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def revision(q,img):
    return sha(canonical({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":img}))
def check_image(rel,expected,git_blob):
    path=ROOT/rel
    ensure(path.is_file() and not path.is_symlink(),"missing actual original image "+rel)
    raw=path.read_bytes()
    ensure(raw[:4]==b"RIFF" and raw[8:12]==b"WEBP","invalid WebP bytes "+rel)
    ensure(sha(raw)==expected and blob(raw)==git_blob,"original WebP SHA/Blob mismatch "+rel)

def main(source_root,apply):
    bankpath=BASE/"questions.json"
    manifestpath=BASE/"webp-manifest.json"
    dbpath=BASE/"question-bank.sqlite3"
    rawbank=bankpath.read_bytes()
    rawmanifest=manifestpath.read_bytes()
    rawdb=dbpath.read_bytes()
    if not (ROOT/REPORT).exists():
        ensure(blob(rawbank)==FROZEN_BANK_BLOB and blob(rawdb)==FROZEN_SQLITE_BLOB,
               "source bank/SQLite no longer at frozen 205 baseline")
    ensure(blob(rawmanifest)==FROZEN_MANIFEST_BLOB,"manifest must remain immutable")
    bank=json.loads(rawbank)
    man=json.loads(rawmanifest)
    ensure(bank["year"]==114 and len(bank["questions"])==205,"bank not 205")
    ensure(man["year"]==114 and len(man["items"])==205,"manifest not 205")
    ids=[q["questionId"] for q in bank["questions"]]
    ensure(len(set(ids))==205 and ids.count(QID)==1,"205 QID uniqueness failed")
    before={q["questionId"]:canonical(q) for q in bank["questions"] if q["questionId"]!=QID}
    q=next(q for q in bank["questions"] if q["questionId"]==QID)
    item=next(v for v in man["items"] if v["questionId"]==QID)
    ensure(item["sha256"]==EXPECTED_IMAGE and item["qaStatus"]=="PASS","G1 manifest image not verified")
    ensure(item["visualReviewEvidence"]["reviewedSha256"]==EXPECTED_IMAGE,"original visual QA record stale")
    ensure(item["sourceSha256"]==EXPECTED_PAGE,"original source page mismatch")
    stage_rel=source_root/STAGE_RECEIPT
    official_rel=source_root/OFFICIAL_RECEIPT
    ensure(stage_rel.is_file() and official_rel.is_file(),"immutable Role A source-stage receipts absent")
    ensure(blob(stage_rel.read_bytes())==STAGE_RECEIPT_BLOB,"A source-stage receipt Git blob changed")
    ensure(blob(official_rel.read_bytes())==OFFICIAL_RECEIPT_BLOB,"A official printed-answer receipt Git blob changed")
    stage=load(stage_rel); official=load(official_rel)
    ensure(stage["questionId"]==QID and official["questionId"]==QID,"wrong original source receipt")
    ensure(stage["source"]["question"]==q["question"] and stage["source"]["options"]==q["options"],
           "G2 original full question/A-D differs from canonical")
    ensure(len(q["options"])==4 and all(isinstance(v,str) and v.strip() for v in q["options"]),
           "four source options missing")
    ensure(stage["source"]["revision"]==EXPECTED_REVISION and revision(q,EXPECTED_IMAGE)==EXPECTED_REVISION,
           "source revision does not match real canonical question/options/image")
    ensure(stage["source"]["originalSingleSha256"]==EXPECTED_IMAGE
           and stage["source"]["originalPageSha256"]==EXPECTED_PAGE,
           "source-stage WebP vs question/page SHA mismatch")
    ensure(official["originalQuestion"]["originalSingleWebpSha256"]==EXPECTED_IMAGE,
           "official source receipt original image mismatch")
    ensure(official["publishedOfficialAnswer"]["answer"]=="C"
           and stage["official"]["publishedAnswer"]=="C"
           and q["answer"]=="C" and q["answerMatched"] is True,
           "printed official answer is not exact Q12 C")
    ensure(official["publishedOfficialAnswer"]["originalAnswerWebpSha256"]==EXPECTED_ANSWER_IMAGE,
           "printed original answer image mismatched")
    ensure(official["finalOfficialNoticeScope"]["officialConfirmationPdfSha256Recorded"]==EXPECTED_NOTICE,
           "notice original PDF SHA differs")
    ensure(official["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishQuestionIds"]==["114-00-E-26"]
           and official["finalOfficialNoticeScope"]["q12ListedInOfficialCorrection"] is False
           and stage["official"]["noticeQuestionIds"]==["114-00-E-26"],
           "G3 notice cannot be asserted paper-wide")
    notice=load(BASE/"official-confirmation-status.json")
    ledger=load(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")
    record=notice["confirmations"]["00-E"]
    docs=[d for d in ledger["docs"] if d["paperCode"]=="00-E"]
    ensure(record["revisionDocumentSha256"]==EXPECTED_NOTICE
           and record["perQuestionOfficialNoticeScopeEvidenceComplete"] is True
           and record["revisionDocumentContent"]=="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED",
           "official 114 notice full-page status incomplete")
    ensure(len(docs)==1 and docs[0]["pdfSha256"]==EXPECTED_NOTICE
           and docs[0]["allPagesVisuallyReviewed"] is True
           and [v["questionId"] for v in docs[0]["confirmed"]]==["114-00-E-26"],
           "official original notice named scope mismatch")
    check_image(item["output"],EXPECTED_IMAGE,stage["source"]["originalSingleGitBlob"])
    check_image(stage["source"]["originalPageWebp"],EXPECTED_PAGE,stage["source"]["originalPageGitBlob"])
    check_image(stage["official"]["originalPublishedAnswerWebp"],
                EXPECTED_ANSWER_IMAGE,stage["official"]["originalPublishedAnswerGitBlob"])
    ensure(q["questionProvenance"]["webpSha256"]==EXPECTED_IMAGE
           and q["questionProvenance"]["pixelSourceSha256"]==EXPECTED_PAGE,
           "G1 source provenance changed")
    ensure(q["sourcePage"]==3 and q["paperCode"]=="00-E" and q["originalQuestionNumber"]==12,
           "source year/paper/printed number mismatched")

    accepted=copy.deepcopy(q)
    accepted["questionVerified"]=True
    accepted["answerVerified"]=True
    accepted["textQaStatus"]="PASS"
    accepted["textQaEvidence"]={
      "reviewer":"MASTER reconciled immutable ROLE A direct-source visual proof (not new visual inspection)",
      "reviewedAt":"2026-11-07",
      "evidencePath":OFFICIAL_RECEIPT,
      "sourceImageSha256":EXPECTED_PAGE,
      "questionRevision":EXPECTED_REVISION,
      "evidenceSha256":sha(official_rel.read_bytes())
    }
    accepted["answerProvenance"]["independentVisualVerification"]=True
    accepted["officialFinalAnswer"]="C"
    accepted["officialCorrectionChecked"]=True
    accepted["officialFinalQaEvidence"]={
      "reviewer":"MASTER reconciled ROLE A published-answer visual QA (NOT ROLE E AI review)",
      "reviewedAt":"2026-11-07",
      "evidencePath":OFFICIAL_RECEIPT,
      "answerPdfSha256":q["answerProvenance"]["officialPdfSha256"],
      "finalCorrectionsReviewed":True,
      "evidenceSha256":sha(official_rel.read_bytes())
    }
    accepted["reviewStatus"]="SOURCE_VERIFIED_PENDING_INDEPENDENT_AI_AND_EMITTED_UI"
    ensure("studentReleaseApproved" not in accepted
           and accepted.get("teachingQaStatus")!="PASS"
           and accepted.get("uiQaStatus")!="PASS",
           "source must never claim E or D completed")

    with sqlite3.connect("file:"+dbpath.as_posix()+"?mode=ro",uri=True) as cx:
        ensure(cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok","original SQLite corruption")
        ensure(cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205,"SQLite count")
        rows=cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    original_other={qid:(payload,digest) for qid,payload,digest in rows if qid!=QID}
    # Existing QA branch must preserve all 205 canonical JSON <-> SQLite source rows.
    # Refuse to silently repair other questions during an E12-only source bridge.
    current_bank={q["questionId"]:q for q in bank["questions"]}
    ensure(set(current_bank)=={qid for qid,_,_ in rows},
           "QA source 205 JSON/SQLite QID sets not identical")
    ensure(all(json.loads(payload)==current_bank[qid] for qid,payload,_ in rows),
           "QA source 205 JSON/SQLite payloads not identical")
    original=next((row for row in rows if row[0]==QID),None)
    ensure(original is not None and json.loads(original[1])==q,
           "frozen Q12 source/SQLite mismatch before admission")
    ensure(all(sha(payload.encode("utf-8"))==h for _,payload,h in rows),
           "pre-existing SQLite payload hash bad")
    if not apply:
        print("PASS SOURCE P0 G1+G2+G3 observed archival receipts, Q12 candidate C, 205 SQLite read-only")
        return
    ensure(q["questionVerified"] is False and q["answerVerified"] is False,
           "Q12 baseline already modified; refusing an unreviewed re-admission")
    fmt=json.dumps(bank,ensure_ascii=False,indent=2)+"\n"
    ensure(rawbank.decode("utf-8")==fmt,"bank formatting not canonical: stop rather than whole-file reformat")
    bank["questions"][ids.index(QID)]=accepted
    ensure({q["questionId"]:canonical(q) for q in bank["questions"] if q["questionId"]!=QID}==before,
           "some other 204 question content changed")
    bankpath.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    payload=canonical(accepted).decode("utf-8")
    with sqlite3.connect(dbpath) as cx:
        cx.execute("UPDATE questions SET payload_json=?,payload_sha256=? WHERE question_id=?",
                   (payload,sha(payload.encode("utf-8")),QID))
        ensure(cx.total_changes==1,"SQLite did not update precisely one QID")
        cx.commit()
    with sqlite3.connect("file:"+dbpath.as_posix()+"?mode=ro",uri=True) as cx:
        ensure(cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok","updated SQLite integrity failed")
        ensure(cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205,"updated SQLite rowcount")
        after_rows=cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
    ensure({qid:(val,h) for qid,val,h in after_rows if qid!=QID}==original_other,
           "other 204 SQLite payload bytes/hash changed")
    ensure(json.loads(next(val for qid,val,_ in after_rows if qid==QID))==accepted,
           "Q12 SQLite roundtrip diverges from canonical JSON")
    ensure(manifestpath.read_bytes()==rawmanifest,"manifest bytes changed")
    proof={
      "schemaVersion":1,"year":114,"questionId":QID,
      "taskId":"MASTER-P0-E12-QA-SOURCE-BRIDGE-20261107-02",
      "gate":"SOURCE_G1_G2_G3_ONLY_NOT_STUDENT_ADMISSION",
      "sourceBranchBaseline":"16d04a0d642fb433de289417a22c3050aa3e52b6",
      "roleAStageCommit":STAGE_COMMIT,
      "questionRevision":EXPECTED_REVISION,"originalSingleWebpSha256":EXPECTED_IMAGE,
      "originalSourcePageSha256":EXPECTED_PAGE,"officialPublishedAnswer":"C",
      "originalPublishedAnswerImageSha256":EXPECTED_ANSWER_IMAGE,
      "officialEnglishCorrectionPdfSha256":EXPECTED_NOTICE,
      "correctionNamedOnly":["114-00-E-26"],
      "sourceQuestionTextAndFourOptionsMatched":True,
      "sourceOriginalImagesSha256AndGitBlobMatched":True,
      "officialAnswerImageOriginalBytesMatched":True,
      "sourceQuestionVerified":True,"officialAnswerVerified":True,
      "sqliteIntegrityCheck":"ok","canonicalRows":205,"other204JsonRecordsUnchanged":True,
      "other204SqlitePayloadsUnchanged":True,"manifestUnchanged":True,
      "studentReady":False,"independentRoleETrustedReceipt":False,
      "roleDFormalEmitter16of16":False,"mainApprovedOrLive":False,
      "comment":"Historic ROLE A direct visual evidence reconciled against actual Git bytes; no new PDF download or fresh human/AI visual inspection claimed. Full distinct-Session E receipt, actual D and protected release remain mandatory."
    }
    target=ROOT/REPORT
    ensure(not target.exists(),"admission report already exists; no replace")
    target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SOURCE_ADMITTED_ONLY: 114-00-E-12 printed C, original QA exact, 205 SQLite ok, other 204 unchanged; NO E/D/READY/LIVE")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage-root",type=Path,required=True)
    ap.add_argument("--apply",action="store_true")
    options=ap.parse_args()
    main(options.stage_root,options.apply)
