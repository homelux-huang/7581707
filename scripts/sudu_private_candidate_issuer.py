"""Fail-closed, NONPUBLIC E12 native-publisher candidate bootstrap.

This is a private two-phase issuer, NOT a bypass of G0-G10 or a way to publish
without ROLE E. The candidate gets identical V4 runtime and public_question()
assembly, but ONLY in an out-of-repo, runner-private temporary directory.
No production approved JSON, Pages or trust registry is ever edited.

Pre-UI gate: immutable A/G1/G2/G3 + original B teaching document + genuine
independent blinded answer + protected-main E reviewer trust.
Post-UI gate: the UNMODIFIED sudu_verified_publish.py processes real D UI
evidence/16 screenshots and final-review authorization through normal PR/CI.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import sudu_verified_publish as pub
from scripts import sudu_independent_review_gate as e_gate

ROOT = Path(__file__).resolve().parents[1]
QID = "114-00-E-12"
MAIN_SHA = "5546a603abfe0af2e62c0e5f63f775be0bfb24cf"
B_SHA = "57d969888c57fdcd2b16c933e92c7a2c9eebb3a5"
QA_MIN_SHA = "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2"
REV = "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
WEBP = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
TEACHING_CANONICAL = "c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a"
TEACHING_RAW_SHA = "cccc7c5fcc5491d4004c8e72d3e9fca696f2e1a9bdcca23ec7e28b298610c51d"
TEACHING_DOC_SHA = "6a9235ac6c1af701c9e414ec106ebc2e56b905ad3c61373041d5cb05b2f2714f"
TEACHING_DOC_REL = "sudu/data/processed/114/review-evidence/114-00-E-12-teaching-publisher-20261107.json"
OCR_REL = "sudu/data/processed/114/review-evidence/114-00-E-12-ocr-publisher-20261107.json"
OFFICIAL_REL = "sudu/data/processed/114/review-evidence/114-00-E-12-official-publisher-20261107.json"
OCR_SHA = "8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc"
OFFICIAL_SHA = "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"
B_REL = "sudu/teaching-candidates/114-role-b-20261025-batch02/114-00-E-12.json"
EXPECTED_MAIN_PUBLISHER = "aa7a774e8f0dde288210a5c584b874a7ded3d45d008d023abf7494dc133232d8"

def git_head(root: Path) -> str:
    return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def certificate(source: Path, rel: str, expected: str):
    verified=pub.review_document(source,114,rel,QID)
    return verified[0] if verified and verified[1]==expected else None

def _fail(reason, field, path):
    return {"pass":False,"reason":reason,"field":field,"path":path}

def evaluate(source: Path, author: Path, request: dict | None):
    """Check original issuer/lesson/source and external trust, never write files."""
    failures=[]
    def require(cond, reason, field, path):
        if not cond:
            failures.append(_fail(reason, field, path))
        return bool(cond)
    root=Path(source)
    author=Path(author)
    require(git_head(author)==B_SHA,"author_original_git_head_mismatch","B HEAD",str(author))
    require(git_head(root)==QA_MIN_SHA,"official_qa_exact_head_mismatch_refresh_pins",
            "QA HEAD",str(root))
    require(sha((ROOT/"scripts/sudu_verified_publish.py").read_bytes())==EXPECTED_MAIN_PUBLISHER,
            "not_current_main_native_publisher","publisherSha256",
            "scripts/sudu_verified_publish.py")
    data=pub.read(root/"sudu/data/processed/114/questions.json")
    man=pub.read(root/"sudu/data/processed/114/webp-manifest.json")
    inv=pub.read(root/"sudu/data/processed/114/inventory.json")
    q=next(x for x in data["questions"] if x.get("questionId")==QID)
    item=next(x for x in man["items"] if x.get("questionId")==QID)
    require(len(data["questions"])==len(man["items"])==205 and
            inv.get("sqlite",{}).get("roundtripPass") is True and
            inv.get("sqlite",{}).get("rows")==205,
            "205_bank_sqlite_integrity_missing","inventory.sqlite",
            "sudu/data/processed/114/inventory.json")
    require(pub.image_proof(q,item,{},root) and pub.visual_certificate(root,item,QID)
            and sha((root/item["output"]).read_bytes())==WEBP,
            "original_image_visual_QA_hash_invalid",
            "webpSha256+visualReviewEvidence",item["output"])
    revision=pub.text_revision(q,WEBP)
    srcok,answerok=pub.source_proof(q,True,True,revision)
    require(revision==REV and srcok and answerok and q.get("officialFinalAnswer")=="C",
            "original_question_or_official_answer_not_verified",
            "questionRevision+sourceProof+officialFinalAnswer",
            "sudu/data/processed/114/questions.json")
    ocr=certificate(root,OCR_REL,OCR_SHA)
    require(bool(ocr and ocr.get("questionRevision")==REV
                 and ocr.get("question")==q.get("question")
                 and ocr.get("options")==q.get("options")
                 and ocr.get("visualTextCompared") is True),
            "source_OCR_G2_exact_SHA_or_content_missing","evidence.ocr",OCR_REL)
    official=certificate(root,OFFICIAL_REL,OFFICIAL_SHA)
    require(bool(official and pub.official_notice_scope_certified(root,114,q,official)
                 and official.get("finalAnswer")=="C"),
            "source_G3_named_official_notice_sha_invalid","evidence.official",OFFICIAL_REL)
    teach=certificate(root,TEACHING_DOC_REL,TEACHING_DOC_SHA)
    raw_author=(author/B_REL).read_bytes()
    lesson=json.loads(raw_author)
    actual_digest=e_gate.digest(e_gate.canonical(lesson.get("teaching",{})))
    good_lesson=(sha(raw_author)==TEACHING_RAW_SHA and
                 actual_digest==TEACHING_CANONICAL and
                 lesson.get("questionId")==QID and
                 lesson.get("source",{}).get("questionRevision")==REV and
                 lesson.get("source",{}).get("webpSha256")==WEBP)
    require(good_lesson,"original_B_canonical_lesson_hash_mismatch",
            "content+authorSHA",B_REL)
    teach_matches=(teach and good_lesson and teach.get("content")==lesson["teaching"]
                   and teach.get("canonicalTeachingSha256")==TEACHING_CANONICAL
                   and teach.get("sourceAuthorCommit")==B_SHA
                   and teach.get("allFourOptionsReviewed") is True
                   and teach.get("calculationReviewed") is True)
    require(bool(teach_matches),"B_native_teaching_issuer_missing_or_modified",
            "evidence.teaching+canonicalTeachingSha256",TEACHING_DOC_REL)
    if not isinstance(request,dict):
        failures.append(_fail("pre_ui_candidate_request_missing","preUiCandidateRequest",
                              "private intake outside GitHub Pages"))
        return failures,None
    requested=request.get("evidence") or {}
    require(request.get("schemaVersion")==1
            and request.get("questionId")==QID
            and request.get("sourceCommit")==QA_MIN_SHA
            and request.get("status")=="PRE_UI_CANDIDATE_PENDING_D_TEST"
            and requested.get("ocr")==OCR_REL
            and requested.get("official")==OFFICIAL_REL
            and requested.get("teaching")==TEACHING_DOC_REL,
            "pre_ui_request_is_not_bound_to_exact_original_material",
            "candidateRequest/status+evidence", "external signed intake")
    blind_rel=requested.get("blind")
    blind=pub.review_document(root,114,blind_rel,QID) if blind_rel else None
    good_blind=bool(blind and blind[0].get("questionRevision")==REV
                    and blind[0].get("webpSha256")==WEBP
                    and blind[0].get("officialAnswerHiddenDuringSolve") is True
                    and blind[0].get("solvedWithoutOfficialAnswer") is True
                    and blind[0].get("answer")=="C"
                    and len(str(blind[0].get("blindReasoning") or ""))>=60
                    and "officialAnswer" not in blind[0]
                    and "officialPdfSha256" not in blind[0])
    require(good_blind,"genuine_answer_hidden_blind_issuer_document_absent",
            "evidence.blind+officialAnswerHiddenDuringSolve",str(blind_rel))
    # A self-written boolean is never proof of a blinded ChatGPT conversation.
    # Require externally authenticated provider execution result from a
    # protection-owned issuer; no such key/provider-verification is currently
    # available. A cryptographically signed chain must pass in production;
    # the separate experimental V2 prototype is NOT an admission authority.
    require(False,"blind_provider_attestation_external_authentication_NOT_YET_IMPLEMENTED",
            "blindProviderAttestation+authenticIssuer",str(blind_rel))
    if not (teach and good_lesson):
        return failures,None
    policy=pub.read(ROOT/"sudu/release-governance/independent-review-policy.json")
    require(isinstance(policy,dict) and
            policy.get("reviewMode")=="DISTINCT_AI_CONTENT_RECEIPT_V1",
            "protected_main_distinct_AI_policy_unavailable",
            "reviewMode","sudu/release-governance/independent-review-policy.json")
    require(bool(policy and QID in (policy.get("trustedAiReviewReceipts") or {})),
            "E12_protected_trusted_AI_receipt_absent",
            "trustedAiReviewReceipts."+QID,
            "sudu/release-governance/independent-review-policy.json")
    # Only a verified, protected-main trusted receipt can authorize later review.\n    # No experimental or self-asserted review can satisfy this condition.\n    require(False,"formal_E_independent_gate_not_yet_integrated_fail_closed",\n            "sourceAuthorSessionId+reviewerSessionId+E original SHA",\n            "scripts/sudu_independent_review_gate.py")
    return failures,(q,item,teach)

def emit_private(source: Path, author: Path, request: dict, dest: Path, *,
                 runner_temp: Path):
    failures,record=evaluate(source,author,request)
    if failures:
        raise ValueError(json.dumps(failures,ensure_ascii=False))
    destination=dest.resolve()
    allowed=runner_temp.resolve()
    if (not destination.is_relative_to(allowed) or destination==allowed
            or ROOT.resolve().is_relative_to(destination) or
            destination.is_relative_to(ROOT.resolve())):
        raise ValueError("NONPUBLIC staging output MUST be under runner-private temp")
    if destination.exists():
        raise ValueError("NONPUBLIC staging output must not exist")
    q,item,teach=record
    assert q["questionId"]==QID and teach["canonicalTeachingSha256"]==TEACHING_CANONICAL
    # Use original verified publisher question assembly; ONLY omission is
    # post-UI admission step. Never set studentReleaseApproved or READY.
    composed=copy.deepcopy(q)
    composed["teaching"]=teach["content"]
    composed["officialFinalAnswer"]=q["officialFinalAnswer"]
    image_rel=f"data/approved/webp/114/{QID}.webp"
    native=pub.public_question(composed,114,"英文",image_rel)
    destination.mkdir(parents=True,mode=0o700)
    shutil.copytree(ROOT/"sudu/data/approved",destination/"sudu/data/approved")
    runtime=["v4-115-multisubject-review-demo.html","verified-questions-runtime.js",
             "v4-score-feedback.js","demo-subject-learning.js"]
    for name in runtime:
        shutil.copy2(ROOT/"sudu"/name,destination/"sudu"/name)
    webp_dest=destination/"sudu"/image_rel
    webp_dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source/item["output"],webp_dest)
    assert sha(webp_dest.read_bytes())==WEBP
    out={"schemaVersion":1,"year":114,"sourceSha":git_head(source),
         "expected":205,"approvedCount":1,"questions":[native]}
    pub.dump(destination/"sudu/data/approved/114.json",out)
    progress=pub.read(destination/"sudu/data/approved/progress.json")
    progress["years"]["114"]["approvedCount"]=1
    progress["years"]["114"]["pending"]=204
    progress["years"]["114"]["approvedPercent"]=round(100/205,1)
    progress["years"]["114"]["subjects"]["英文"]["studentReady"]=1
    pub.dump(destination/"sudu/data/approved/progress.json",progress)
    # Must pass original publisher site_check against ephemeral data.
    pub.site_check(destination)
    # Never put a public TRUE READY flag in source or actual main.
    pub.dump(destination/"private-run-metadata.json",{
        "schemaVersion":1,"private":True,"stage":"NONPUBLIC_PRE_UI_CANDIDATE_NOT_LIVE",
        "originalQuestionId":QID,"qaHead":git_head(source),
        "originalWebpSha256":WEBP,"teachingCanonicalSha256":TEACHING_CANONICAL,
        "nativeAssembler":"scripts.sudu_verified_publish.public_question",
        "livePublished":False,"uiQaPassed":False})
    return destination

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--author",required=True,type=Path)
    p.add_argument("--intake",type=Path)
    p.add_argument("--emit-dir",type=Path)
    a=p.parse_args()
    request=pub.read(a.intake) if a.intake else None
    failures,record=evaluate(a.source,a.author,request)
    print(json.dumps({"QID":QID,"status":"GATED_PRIVATE_CANDIDATE" if not failures
        else "FAIL_CLOSED_NOT_PUBLISHED","failures":failures,
        "actualPublisherSha256":sha((ROOT/"scripts/sudu_verified_publish.py").read_bytes()),
        "originalTeachingSha256":TEACHING_CANONICAL,
        "originalImageSha256":WEBP},ensure_ascii=False,indent=2))
    if failures:
        return 2
    if a.emit_dir is None:
        return 0
    allowed=os.getenv("RUNNER_TEMP")
    if not allowed:
        raise ValueError("GitHub private RUNNER_TEMP required for candidate emitter")
    emit_private(a.source,a.author,request,a.emit_dir,runner_temp=Path(allowed))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
