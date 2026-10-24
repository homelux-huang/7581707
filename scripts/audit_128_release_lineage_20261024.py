#!/usr/bin/env python3
"""READ-ONLY 128 frozen-draft/source/approved/LIVE ledger and MB05 proof chain.

Source objects, source-gate admissions, draft QA, live data and historical UI
are separate facts; no script action grants release or edits original data.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import sqlite3
import subprocess
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://homelux-huang.github.io/7581707/"
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_UI_SHA="2b48a4aee849e38eee7ac47a77a3977c34c3779c"
FIRST_BLIND_COMMIT="cf6a4efede233b0e447d52498209adf1b721c13e"
PRE_SOURCE_APPROVAL_COMMIT="b78a14c8cc6081a7a01613238255fce0a22ba60b"
EXPECTED_IDS={"115-00-MB-02","115-00-MB-03","115-00-MB-04","115-00-MB-05","115-00-MB-09"}
MB05_IMAGE_SHA="be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2"
MB05_SOURCE_REV="3b0a4236f9298edd225b445592faee3b222c8ecfc1b62425278a0de576cc1df9"
MB05_TEACHING_SHA="70063f1c4b68979aac9828cdb0dc36a7562591da4f0537bdd0e6f791609827c3"

def check(cond, text):
    if not cond: raise AssertionError(text)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def stable(obj): return sha_bytes(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def git(cwd,*args): return subprocess.check_output(["git","-C",str(cwd),*args])
def fetch(route,commit):
    url=BASE_URL+route+"?"+urlencode({"release_probe":commit[:12]})
    with urlopen(Request(url,headers={"Cache-Control":"no-cache","User-Agent":"7581707-MB05-Audit/1.0"}),timeout=30) as r:
        check(r.status==200,f"LIVE {route} HTTP status {r.status}")
        return r.read()

def api_run(run_id):
    u=f"https://api.github.com/repos/homelux-huang/7581707/actions/runs/{run_id}"
    with urlopen(Request(u,headers={"User-Agent":"7581707-audit/1.0","Accept":"application/vnd.github+json"}),timeout=30) as r:
        j=json.loads(r.read())
    check(j.get("status")=="completed" and j.get("conclusion")=="success",
          f"Actions {run_id} did NOT conclude SUCCESS")
    return {"runId":run_id,"headSha":j["head_sha"],"status":j["status"],"conclusion":j["conclusion"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--draft",required=True,type=Path)
    p.add_argument("--historical",required=True,type=Path)
    p.add_argument("--expected-live-sha",required=True)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    src=args.source.resolve();draft=args.draft.resolve();hist=args.historical.resolve()
    main_sha=args.expected_live_sha
    check(len(main_sha)==40, "FULL 40-digit expected LIVE SHA required")
    check(git(hist,"rev-parse","HEAD").decode().strip()==ORIGINAL_UI_SHA,
          "Historical V4 is not the 8x2 tested SHA")
    for rel in ("sudu/v4-115-multisubject-review-demo.html","sudu/verified-questions-runtime.js"):
        check((ROOT/rel).read_bytes()==(hist/rel).read_bytes(),
              f"V4 changed since MB05 browser QA; re-test required: {rel}")
    # Audit branch may add only review files, never modify the production input data.
    for rel in ("sudu/data/approved/115.json","sudu/verified-questions-runtime.js",
                "sudu/v4-115-multisubject-review-demo.html"):
        check((ROOT/rel).read_bytes()==git(ROOT,"show",main_sha+":"+rel),
              f"Release audit checkout differs from published main: {rel}")
    spec=importlib.util.spec_from_file_location("verified_publisher",ROOT/"scripts/sudu_verified_publish.py")
    pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
    bank={};images={};certs={}
    for year in (114,115):
        path=src/f"sudu/data/processed/{year}"
        arr=load(path/"questions.json")["questions"]
        bank.update({q["questionId"]:q for q in arr})
        images.update({i["questionId"]:i for i in load(path/"webp-manifest.json")["items"]})
        certs.update(pub.reviewed_student_batches(src,year))
    check(len(bank)==410,"Original canonical source must contain 205 per year")
    program=load(ROOT/"sudu/data/approved/115.json")
    check(program.get("approvedCount")==5 and
          {q["canonicalId"] for q in program["questions"]}==EXPECTED_IDS,
          "EXACT five MB approved subjects expected; new release cannot be inferred")
    public={q["canonicalId"]:q for q in program["questions"]}
    before=load(hist/"sudu/data/approved/115.json")
    check(before["approvedCount"]==4 and
          {q["canonicalId"] for q in before["questions"]}==EXPECTED_IDS-{"115-00-MB-05"},
          "Four preexisting formal questions not present historically")
    for q in before["questions"]:
        check(q==public[q["canonicalId"]],"Prior four already-approved objects changed")
    legacy_notes=load(draft/"sudu/teaching-drafts/preview-128-20261023/progress.json")
    frozen=legacy_notes["items"]
    frozen_ids=[i["questionId"] for i in frozen]
    check(len(frozen_ids)==128 and len(set(frozen_ids))==128,
          "Frozen 128 denominator is wrong")
    check(set(frozen_ids)<=bank.keys(),"Draft ID missing canonical source")
    check(set(public)<=set(frozen_ids),"Unexpected question added outside frozen 128")
    # Build and validate complete publisher/source certificate chain for MB05.
    qid="115-00-MB-05"
    q=bank[qid];item=images[qid];audit=certs[qid]
    check(item["sha256"]==MB05_IMAGE_SHA and q["answer"]=="B", "Original MB05 WebP/answer mismatch")
    image_file=src/item["output"];check(image_file.is_file(), "MB05 original source WebP absent")
    check(sha_bytes(image_file.read_bytes())==MB05_IMAGE_SHA, "MB05 original WebP changed")
    source_revision=pub.text_revision(q,MB05_IMAGE_SHA)
    check(source_revision==MB05_SOURCE_REV,"MB05 exact source text revision changed")
    ocr_official={"status":"documented (AI + official image), not renewed human QA"}
    reviewed=pub.apply_independently_certified_review(src,115,q,item,audit)
    check(reviewed.get("studentReleaseApproved") is True,
          "MB05 publisher did not admit source certificate")
    check(pub.source_proof(reviewed,True,True,source_revision)==(True,True),
          "MB05 formal original text and official final source proofs failed")
    check(pub.independently_solved(reviewed,source_revision)=="matched",
          "MB05 preserved pre-answer original solve failed")
    check(pub.teaching_complete(reviewed,"數學 B","B"),"MB05 formal teaching content gate failed")
    check(pub.certificates_complete(src,reviewed,item,{}),
          "MB05 SHA-bound source teaching/official/UI evidence absent")
    check(pub.official_notice_scope_certified(src,115,q,load(
          src/"sudu/data/processed/115/review-evidence/115-00-MB-05-official.json")),
          "MB05 no-objection official PDF state not certified")
    teaching=reviewed["teaching"];teach_sha=stable(teaching)
    check(teach_sha==MB05_TEACHING_SHA,"MB05 certified teaching digest has drifted")
    uipath=src/"sudu/data/processed/115/review-evidence/115-00-MB-05-ui.json"
    ui=load(uipath)
    check(ui["testedTeachingCanonicalSha256"]==teach_sha
          and ui["testedQuestionRevision"]==source_revision
          and ui["testedWebpSha256"]==MB05_IMAGE_SHA,
          "MB05 UI data digest not source aligned")
    mapped=pub.public_question(reviewed,115,"數學 B",f"data/approved/webp/115/{qid}.webp")
    check(mapped==public[qid],"MB05 main production lesson differs from certified source content")
    official_path=src/"sudu/data/processed/115/review-evidence/115-00-MB-05-blind-original-20261024.json"
    first=git(src,"show",FIRST_BLIND_COMMIT+":"+
        "sudu/data/processed/115/review-evidence/115-00-MB-05-blind-original-20261024.json")
    check(first==official_path.read_bytes(),
          "Original MB05 blind reasoning modified after official answer!")
    subprocess.run(["git","-C",str(src),"merge-base","--is-ancestor",
                   FIRST_BLIND_COMMIT,PRE_SOURCE_APPROVAL_COMMIT],check=True)
    check(load(official_path).get("answer")=="B", "Original blind solution not B")
    # Verify SQLite source record is the same canonical current revision.
    conn=sqlite3.connect(f"file:{(src/'sudu/data/processed/115/question-bank.sqlite3').resolve()}?mode=ro",uri=True)
    try:
        cols={x[1] for x in conn.execute("pragma table_info(questions)")}
        field="payload_json" if "payload_json" in cols else "payload"
        record,refsha=conn.execute(f"select {field},payload_sha256 from questions where question_id=?",(qid,)).fetchone()
        check(sha_bytes(record.encode())==refsha and json.loads(record)==q,
              "MB05 205-record canonical JSON / SQLite roundtrip mismatch")
    finally:conn.close()
    # Force public deployment, instead of relying only on a historical SUCCESS badge.
    release=load_bytes_json(fetch("sudu/release.json",main_sha))
    check(release.get("commit")==main_sha and release.get("testsRequired") is True,
          "LIVE release.json SHA mismatch")
    live=load_bytes_json(fetch("sudu/data/approved/115.json",main_sha))
    check(live==program,"LIVE 115 approved lesson content differs from main commit")
    live_webp=fetch("sudu/data/approved/webp/115/"+qid+".webp",main_sha)
    check(sha_bytes(live_webp)==MB05_IMAGE_SHA,"LIVE MB05 image differs from audited original")
    live_js=fetch("sudu/verified-questions-runtime.js",main_sha)
    check(live_js==(ROOT/"sudu/verified-questions-runtime.js").read_bytes(),
          "LIVE V4 runtime differs from tested main code")
    tested_run=api_run(40085323981)
    check(tested_run["headSha"]==ui["testedTeachingDraftCommit"],
          "8x2 CI does not match documented teaching draft test commit")
    pages_run=api_run(40097988371)
    check(pages_run["headSha"]==main_sha,
          "Pages LIVE verification run belongs to another production commit")
    # First-pass draft model is a DIFFERENT teaching payload from formally published MB05.
    rows=[]
    for draft_item in frozen:
        rid=draft_item["questionId"]
        record=load(draft/f"sudu/teaching-drafts/preview-128-20261023/{rid}.json")
        check(record["questionId"]==rid,f"Frozen draft file identity mismatch {rid}")
        q=bank[rid]; img=images[rid]
        rev=pub.text_revision(q,img.get("sha256",""))
        cert=certs.get(rid)
        admitted=pub.apply_independently_certified_review(src,record["year"],q,img,cert) if cert else q
        source_accepted=admitted.get("studentReleaseApproved") is True
        src_digest=stable(admitted["teaching"]) if source_accepted else None
        certificates={}
        if source_accepted:
            for kind,rel in cert["evidence"].items():
                f=src/rel
                check(f.is_file(),f"Certified file missing for {rid}:{kind}")
                certificates[kind]={"path":rel,"sha256":sha_bytes(f.read_bytes())}
            check(pub.certificates_complete(src,admitted,img,{}),
                  f"Accepted source record {rid} has missing SHA-pinned certificate")
        d_sha=stable(record["teaching"])
        accepted=public.get(rid)
        tested=load(src/cert["evidence"]["ui"]).get("testedTeachingCanonicalSha256") if source_accepted else None
        if accepted:
            check(source_accepted and pub.public_question(admitted,record["year"],
                   accepted["subject"],accepted["image"])==accepted,
                  f"LIVE student content/source mismatch for {rid}")
        rows.append({
            "questionId":rid,
            "draftTeachingDigest":d_sha,
            "draftCompleteStructure":bool(record.get("qa",{}).get("explanationWritten")),
            "draftIndependentTeachingQa":record.get("qa",{}).get("independentTeachingReview")=="PASS",
            "draftReleaseCertificate":False,
            "sourceQuestionRevision":rev,
            "sourceTeachingDigest":src_digest,
            "sourceCertificatePathsAndSha":certificates,
            "sourceCertified":source_accepted,
            "sourceIndependentHumanTeacherCertified":False,
            "approvedContentDigest":stable(accepted) if accepted else None,
            "uiTestedDigest":tested,
            "mainCommit":main_sha if accepted else None,
            "pagesRun":pages_run["runId"] if accepted else None,
            "liveVerifiedAt":datetime.datetime.now(datetime.timezone.utc).isoformat() if accepted else None,
            "liveBySameSha":bool(accepted),
            "draftAndSourceSameTeachingDigest":d_sha==src_digest if src_digest else None,
            "blockers":[] if accepted else ["independent_source_teaching_ui_release_evidence_required"]
        })
    approved_rows=[row for row in rows if row["sourceCertified"]]
    check(len(approved_rows)==5 and sum(r["liveBySameSha"] for r in rows)==5,
          "Unexpected 128 draft/source/production scope transition")
    check(sum(r["draftIndependentTeachingQa"] for r in rows)==0,
          "Draft independent QA unexpectedly changed; re-review required")
    check(sum(r["draftReleaseCertificate"] for r in rows)==0,
          "Draft certificate state changed; re-review required")
    result={
       "kind":"READ_ONLY_128_RELEASE_LINEAGE_AND_MB05_FULL_SAME_SHA_LIVE_AUDIT",
       "generatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "mainSha":main_sha,"sourceSha":git(src,"rev-parse","HEAD").decode().strip(),
       "draftSha":git(draft,"rev-parse","HEAD").decode().strip(),
       "MB05":{"questionId":qid,"sourceQuestionRevision":source_revision,
               "imageSha256":MB05_IMAGE_SHA,"teachingSha256":teach_sha,
               "testHead":tested_run["headSha"],
               "testRun":tested_run["runId"],"mainHTMLAndRuntimeUnchangedSinceTest":True,
               "pagesLiveRun":pages_run["runId"],"liveSha":main_sha,
               "firstBlindGitBlobUnchanged":True,"formalSourcePublisherAdmitted":True,
               "livePublishedContentMatchesReconstructedSource":True,
               "previousFourUnchanged":True,"humanIndependentReviewerVerified":False,
               "reviewerStatus":"GPT-6 AI post-answer review, independent human signoff NOT documented"},
       "totals":{"frozen":len(rows),"draftTeachingDraftStructure":sum(x["draftCompleteStructure"] for x in rows),
                 "draftIndependentTeachingQa":0,"draftReleaseCertificates":0,
                 "sourceCertified":len(approved_rows),
                 "formalProductionMain":len(public),"liveVerified":5,
                 "this128BatchNewSinceOriginalFour":1},
       "items":rows}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("MB05_SOURCE_TEACHING_UI_LIVE_VERIFIED",json.dumps(result["MB05"],ensure_ascii=False))
    print("FROZEN_128_TRUE_RELEASE_CROSSWALK",json.dumps(result["totals"],ensure_ascii=False))

def load_bytes_json(raw): return json.loads(raw.decode("utf-8"))

if __name__=="__main__":
    main()
