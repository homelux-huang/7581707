"""Fail-closed separate, signed reviewer authorization on new student admissions.

Evidence JSON and reviewer strings are self-editable by source authors. Trusted
keys and exact grandfathered original data are governed by main publisher, NEVER
read from QA sources. This code contains no private signing key.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"sudu/release-governance/independent-review-policy.json"
REPO="homelux-huang/7581707"
HEX40=re.compile(r"^[0-9a-f]{40}$")

def _no_duplicate_keys(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate signed reviewer configuration key")
        result[k]=v
    return result

def _time(value):
    if not isinstance(value,str):
        raise ValueError("missing ISO8601 UTC offset")
    ts=datetime.fromisoformat(value.replace("Z","+00:00"))
    if ts.tzinfo is None:
        raise ValueError("naive reviewer authorization time")
    return ts.astimezone(timezone.utc)

def _github_json(path):
    # External identity is verified from GitHub itself. No authored certificate
    # can substitute its own GitHub PR author, commits or APPROVED review event.
    if not (path.startswith("/pulls/") or path=="/branches/main"
            or re.fullmatch(r"/issues/comments/[1-9][0-9]*",path)
            or re.fullmatch(r"/commits/[0-9a-f]{40}",path)
            or path=="/contents/sudu/release-governance/independent-review-policy.json?ref=main") or ".." in path:
        raise ValueError("invalid GitHub review API path")
    headers={"Accept":"application/vnd.github+json","User-Agent":"7581707-release-review/1"}
    token=os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"]="Bearer "+token
    request=Request("https://api.github.com/repos/"+REPO+path,headers=headers)
    with urlopen(request,timeout=15) as response:
        if response.status!=200:
            raise ValueError("GitHub verification unavailable")
        return json.loads(response.read())

def _protected_main_trust_verified():
    # Main is presently UNPROTECTED (GitHub reports protected=false).
    # Even a mathematically valid signature cannot safely authorize a new
    # question until owner establishes a real branch ruleset and owns keys.
    try:
        main=_github_json("/branches/main")
        # GitHub protected=true covers both classic protection and repository
        # rulesets; the legacy .protection.enabled field alone does NOT cover rulesets.
        return main.get("name")=="main" and main.get("protected") is True
    except (ValueError,OSError,TypeError,KeyError,TimeoutError,UnicodeError):
        return False

def _author_and_github_review_verified(payload,signer):
    number=payload.get("reviewPullRequestNumber")
    review_id=payload.get("approvedReviewId")
    head=payload.get("reviewHeadSha")
    source_login=payload.get("sourceAuthorLogin")
    if (type(number) is not int or number<=0 or type(review_id) is not int
            or review_id<=0 or not HEX40.fullmatch(str(head))
            or not isinstance(source_login,str) or not source_login.strip()
            or source_login.casefold()==str(signer.get("login","")).casefold()):
        return False
    try:
        pr=_github_json(f"/pulls/{number}")
        review=_github_json(f"/pulls/{number}/reviews/{review_id}")
        total=pr.get("commits")
        if type(total) is not int or total<1 or total>100:
            return False  # large PR must be separately attested/paginated, not guessed
        commits=_github_json(f"/pulls/{number}/commits?per_page=100")
        author=pr.get("user") or {}
        actor=review.get("user") or {}
        if (pr.get("draft") is True or (pr.get("base",{}).get("repo",{}) or {}).get("full_name")!=REPO
                or (pr.get("head",{}) or {}).get("sha")!=head
                or (author.get("login") or "").casefold()!=source_login.casefold()
                or author.get("id")!=payload.get("sourceAuthorGithubId")
                or (actor.get("login") or "").casefold()!=str(signer.get("login","")).casefold()
                or actor.get("id")!=signer.get("githubUserId")
                or review.get("id")!=review_id
                or review.get("state")!="APPROVED" or review.get("commit_id")!=head
                or type(commits) is not list or len(commits)!=total):
            return False
        if _time(review.get("submitted_at")) > _time(payload.get("reviewedAt")):
            return False
        if _time(payload.get("reviewedAt")) > datetime.now(timezone.utc):
            return False
        all_contributors=set()
        for commit in commits:
            if commit.get("sha") is None or not HEX40.fullmatch(commit["sha"]):
                return False
            # Refuse unverifiable authors/committers, especially bot/self reviews.
            for part in ("author","committer"):
                person=commit.get(part) or {}
                login=person.get("login")
                if not isinstance(login,str) or not login:
                    return False
                all_contributors.add(login.casefold())
        if source_login.casefold() not in all_contributors:
            return False
        if str(signer.get("login","")).casefold() in all_contributors:
            return False
        if not any(c["sha"]==head for c in commits):
            return False
        return True
    except (OSError,ValueError,TypeError,KeyError,TimeoutError,UnicodeError):
        return False

def _official_document_sha(source,audit,qid):
    e=(audit or {}).get("evidence") or {}
    rel=e.get("official")
    if (not isinstance(rel,str) or not rel.startswith("sudu/data/processed/")
            or ".." in Path(rel).parts or Path(rel).is_absolute()
            or not rel.endswith(".json")):
        return None
    root=Path(source)
    path=root/rel
    try:
        if (not path.resolve().is_relative_to(root.resolve())
                or not path.is_file() or path.is_symlink()):
            return None
        raw=path.read_bytes()
        doc=json.loads(raw)
        if doc.get("questionId")!=qid:
            return None
        return digest(raw)
    except (OSError,ValueError,UnicodeError,AttributeError):
        return None

SHA=re.compile(r"^[0-9a-f]{64}$")

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def digest(x):
    return hashlib.sha256(x).hexdigest()

def blob_oid(x):
    return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\x00"+x).hexdigest()

def policy_from_trusted_main():
    try:
        data=json.loads(POLICY.read_text(encoding="utf-8"),object_pairs_hook=_no_duplicate_keys)
        return data if data.get("schemaVersion")==1 and data.get("githubRepository")==REPO else None
    except (ValueError,OSError,AttributeError):
        return None

def substantive_notes_verified(source,rel,sha):
    if (not isinstance(rel,str) or not rel.startswith("sudu/data/processed/")
            or ".." in Path(rel).parts or Path(rel).is_absolute()
            or not rel.endswith(".md") or not SHA.fullmatch(str(sha))):
        return False
    root=Path(source)
    target=root/rel
    try:
        return (target.resolve().is_relative_to(root.resolve())
                and target.is_file() and not target.is_symlink()
                and digest(target.read_bytes())==sha)
    except (OSError,ValueError):
        return False

def _ai_official_receipt_consistent(source,audit,question):
    """Require actual official document ANSWER and correction fields, not only SHA.

    Final official-answer notice scope and PDF-pixel verification must ALSO
    be checked independently by the original publisher G0-G10 gates.
    """
    qid=question.get("questionId")
    official=(audit or {}).get("evidence") or {}
    relative=official.get("official")
    root=Path(source)
    if (not isinstance(relative,str) or not relative.startswith(
            "sudu/data/processed/"+str(question.get("year"))+"/review-evidence/")
            or ".." in Path(relative).parts or Path(relative).is_absolute()
            or not relative.endswith(".json")):
        return None
    path=root/relative
    try:
        if (not path.resolve().is_relative_to(root.resolve())
                or path.is_symlink() or not path.is_file()):
            return None
        raw=path.read_bytes()
        doc=json.loads(raw,object_pairs_hook=_no_duplicate_keys)
    except (OSError,ValueError,TypeError,UnicodeError):
        return None
    ans=question.get("answer")
    if (not isinstance(doc,dict) or doc.get("year")!=question.get("year")
            or doc.get("questionId")!=qid or not isinstance(ans,str) or ans not in "ABCD"
            or doc.get("finalAnswer")!=ans or doc.get("correctionNoticeReviewed") is not True
            or doc.get("officialFinalAnswerImageQaPassed") is not True
            or doc.get("officialPage") !=
               "https://web1.tcte.edu.tw/EXAM/"+str(question.get("year"))+"_4y/"
            or not SHA.fullmatch(str(doc.get("officialPdfSha256")))):
        return None
    source_pdf=(question.get("answerProvenance") or {})
    source_pdf_sha=source_pdf.get("officialPdfSha256") or source_pdf.get("pdfSha256")
    if source_pdf_sha and doc.get("officialPdfSha256")!=source_pdf_sha:
        return None
    return digest(raw)


def _ai_real_issue36_return_verified(statement,registry):
    """Never trust a positive-looking numeric comment ID or task label alone."""
    if not _protected_main_trust_verified():
        return False,"ai_review_main_registry_unprotected"
    id_=statement["reviewIssueCommentId"]
    if (registry.get("reviewIssueCommentId")!=id_
            or registry.get("sourceCommit")!=statement["sourceCommit"]
            or type(registry.get("reviewerGithubUserId")) is not int
            or registry["reviewerGithubUserId"]<=0
            or not isinstance(registry.get("reviewerGithubLogin"),str)
            or not registry["reviewerGithubLogin"]):
        return False,"ai_review_registry_identity_or_source_not_pinned"
    try:
        comment=_github_json("/issues/comments/"+str(id_))
        commit=_github_json("/commits/"+statement["sourceCommit"])
        if (not isinstance(comment,dict) or not isinstance(commit,dict)
                or commit.get("sha")!=statement["sourceCommit"]
                or not HEX40.fullmatch(str(
                    ((commit.get("commit") or {}).get("tree") or {}).get("sha")))):
            return False,"ai_review_source_commit_not_verified"
        if (comment.get("id")!=id_
                or comment.get("issue_url") !=
                    "https://api.github.com/repos/"+REPO+"/issues/36"
                or (comment.get("user") or {}).get("id")!=registry["reviewerGithubUserId"]
                or (comment.get("user") or {}).get("login")!=registry["reviewerGithubLogin"]):
            return False,"ai_review_issue36_comment_identity_mismatch"
        body=comment.get("body")
        if (not isinstance(body,str) or not body.lstrip().upper().startswith("RETURN")
                or "role E" not in body and "role: E" not in body
                or any(str(statement[key]) not in body for key in (
                    "reviewTaskId","reviewerSessionId","questionId",
                    "questionRevision","webpSha256","teachingDigest",
                    "officialEvidenceSha256","sourceCommit"))):
            return False,"ai_review_comment_not_bound_to_actual_findings"
        posted=_time(comment.get("created_at"))
        reviewed=_time(statement["reviewedAt"])
        if not (reviewed<=posted<=datetime.now(timezone.utc)):
            return False,"ai_review_comment_timestamp_not_valid"
        return True,"actual_issue36_comment_and_source_commit_checked"
    except (ValueError,OSError,TypeError,KeyError,TimeoutError,UnicodeError):
        return False,"ai_review_github_verification_unavailable"


def _ai_registry_exactly_matches_protected_main_policy(trust):
    """Never accept a source-branch self-granted AI reviewer allowlist.

    The currently running checkout can be a PR from an untrusted author. The
    registry is admissible only if it equals the GitHub Blob at PROTECTED main.
    This is a trust-root check, not a teacher authorization requirement.
    """
    if not _protected_main_trust_verified():
        return False
    try:
        doc=_github_json(
            "/contents/sudu/release-governance/independent-review-policy.json?ref=main")
        if (not isinstance(doc,dict)
                or doc.get("path") !=
                    "sudu/release-governance/independent-review-policy.json"
                or doc.get("encoding")!="base64"):
            return False
        raw=base64.b64decode("".join(doc["content"].split()),validate=True)
        if doc.get("sha")!=blob_oid(raw):
            return False
        remote=json.loads(raw,object_pairs_hook=_no_duplicate_keys)
        return remote == trust and remote.get("reviewMode")=="DISTINCT_AI_CONTENT_RECEIPT_V1"
    except (OSError,ValueError,TypeError,AttributeError,KeyError,UnicodeError):
        return False


def separate_ai_content_receipt_verified(source,audit,question,manifest,
                                         teaching_document,raw_teaching,*,
                                         trusted_receipts=None):
    """Verify a distinctly authored AI CONTENT REVIEW receipt, not admission.

    The registry is deliberately a required caller-supplied *trusted main*
    approval of an exact Git Blob and author/reviewer provenance, never a
    source-branch registry. This function is NOT yet wired to the publisher.
    It cannot grant READY or override G0-G10 by itself.
    """
    qid=question.get("questionId")
    revision=teaching_document.get("questionRevision")
    webp=(manifest or {}).get("sha256")
    content=teaching_document.get("content")
    if (not isinstance(qid,str) or not SHA.fullmatch(str(revision))
            or not SHA.fullmatch(str(webp)) or not isinstance(content,dict)
            or not isinstance(raw_teaching,(bytes,bytearray))):
        return False,"invalid_ai_review_input"
    registry=trusted_receipts.get(qid) if isinstance(trusted_receipts,dict) else None
    if not isinstance(registry,dict):
        return False,"separate_ai_reviewer_trusted_receipt_absent"
    rel=(audit or {}).get("independentAiContentEvidence")
    if (not isinstance(rel,str) or not rel.startswith(
            "sudu/data/processed/"+str(question.get("year"))+"/review-evidence/")
            or not rel.endswith(".json") or ".." in Path(rel).parts
            or Path(rel).is_absolute()):
        return False,"ai_review_evidence_path_untrusted"
    root=Path(source)
    target=root/rel
    try:
        if (not target.resolve().is_relative_to(root.resolve())
                or target.is_symlink() or not target.is_file()):
            return False,"ai_review_evidence_missing"
        original=target.read_bytes()
        statement=json.loads(original,object_pairs_hook=_no_duplicate_keys)
    except (OSError,ValueError,UnicodeError,AttributeError):
        return False,"ai_review_evidence_invalid"
    if (not isinstance(statement,dict)
            or registry.get("evidencePath")!=rel
            or registry.get("evidenceGitBlobSha")!=blob_oid(original)
            or registry.get("reviewTaskId")!=statement.get("reviewTaskId")
            or registry.get("reviewerSessionId")!=statement.get("reviewerSessionId")
            or registry.get("sourceAuthorSessionId")!=statement.get("sourceAuthorSessionId")):
        return False,"ai_review_receipt_not_trusted_or_modified"
    official=_ai_official_receipt_consistent(source,audit,question)
    if not official:
        return False,"ai_review_official_document_missing_or_answer_conflict"
    expected={
        "schemaVersion":1,"year":question.get("year"),"questionId":qid,
        "questionRevision":revision,"webpSha256":webp,
        "teachingDigest":digest(canonical(content)),
        "teachingEvidenceSha256":digest(bytes(raw_teaching)),
        "officialEvidenceSha256":official,
        "officialAnswerCandidate":question.get("answer"),
    }
    if any(statement.get(k)!=v for k,v in expected.items()):
        return False,"ai_review_material_revision_mismatch"
    if (not SHA.fullmatch(str(statement.get("questionRevision")))
            or not SHA.fullmatch(str(statement.get("webpSha256")))
            or registry.get("questionRevision")!=revision
            or registry.get("webpSha256")!=webp
            or registry.get("teachingDigest")!=expected["teachingDigest"]
            or registry.get("officialEvidenceSha256")!=official):
        return False,"ai_review_trusted_registry_version_mismatch"
    author=statement.get("sourceAuthorSessionId")
    reviewer=statement.get("reviewerSessionId")
    author_task=statement.get("sourceAuthorTaskId")
    review_task=statement.get("reviewTaskId")
    if (not isinstance(author,str) or len(author.strip())<6
            or not isinstance(reviewer,str) or len(reviewer.strip())<6
            or reviewer.casefold()==author.casefold()
            or statement.get("sourceAuthorRole") not in ("B","C")
            or statement.get("reviewerRole")!="E"
            or not isinstance(author_task,str) or not author_task.startswith(
                statement["sourceAuthorRole"]+"-")
            or not isinstance(review_task,str) or not review_task.startswith("E-")
            or review_task==author_task):
        return False,"ai_review_author_or_reviewer_not_distinct"
    if (statement.get("reviewIssueNumber")!=36
            or type(statement.get("reviewIssueCommentId")) is not int
            or statement["reviewIssueCommentId"]<=0
            or type(statement.get("sourceCommit")) is not str
            or not HEX40.fullmatch(statement["sourceCommit"])):
        return False,"ai_review_traceability_missing"
    try:
        reviewed=_time(statement.get("reviewedAt"))
        if reviewed>datetime.now(timezone.utc):
            return False,"ai_review_time_in_future"
    except (TypeError,ValueError):
        return False,"ai_review_timestamp_invalid"
    findings=statement.get("optionByOptionFindings")
    if (not isinstance(findings,dict) or set(findings)!=set("ABCD")
            or any(not isinstance(findings[k],str) or
                   len(findings[k].strip())<20 for k in "ABCD")
            or len({findings[k].strip() for k in "ABCD"})!=4):
        return False,"ai_review_four_distinct_substantive_option_findings_missing"
    if (statement.get("teacherAndElementaryReviewed") is not True
            or statement.get("correctAnswerComparedToOfficial") is not True
            or statement.get("officialCorrectionsReviewed") is not True
            or statement.get("calculationReview") not in
               ("APPLICABLE_ALL_STEPS_CHECKED","NOT_APPLICABLE_EXPLAINED")):
        return False,"ai_review_required_teaching_or_answer_checks_missing"
    if (not substantive_notes_verified(source,statement.get("reviewNotesPath"),
                                       statement.get("reviewNotesSha256"))
            or registry.get("reviewNotesSha256")!=statement.get("reviewNotesSha256")):
        return False,"ai_review_substantive_notes_not_sha_bound"
    # A registry from unprotected main or a source-authored, invented Issue36
    # comment cannot certify actual independent AI review.
    authentic,why=_ai_real_issue36_return_verified(statement,registry)
    if not authentic:
        return False,why
    # Even with all these conditions, publisher must separately run all
    # source/correction, independent solve, QA, original image, V4 and LIVE gates.
    return True,"distinct_ai_content_receipt_exact_registry_and_material_match"


def certified(source,audit,question,manifest,teaching_document,raw_teaching,*,policy=None):
    """Return (approved,reason); signature verification is *additional* to all G0-G10."""
    trust=policy if policy is not None else policy_from_trusted_main()
    if not isinstance(trust,dict) or trust.get("schemaVersion")!=1:
        return False,"trusted_review_policy_missing"
    if trust.get("githubRepository")!=REPO:
        return False,"wrong_trusted_repository"
    qid=question.get("questionId")
    revision=teaching_document.get("questionRevision")
    webp=(manifest or {}).get("sha256")
    if (not isinstance(qid,str) or not SHA.fullmatch(str(revision))
            or not SHA.fullmatch(str(webp))
            or not isinstance(teaching_document.get("content"),dict)
            or not isinstance(raw_teaching,(bytes,bytearray))):
        return False,"invalid_review_source"
    previous=(trust.get("legacyAlreadyPublished") or {}).get(qid)
    if previous is not None:
        if (previous.get("year")==question.get("year")
                and previous.get("questionRevision")==revision
                and previous.get("webpSha256")==webp
                and previous.get("teachingEvidenceGitBlob")==blob_oid(raw_teaching)):
            return True,"exact_five_historical_students_preserved"
        return False,"legacy_content_changed_must_be_reapproved"
    # Current owner directive: teacher describes teaching STYLE, not an
    # actual person or certificate. Source, answer, V4 and CI gates still run
    # separately in the unchanged verified publisher after this function.
    mode=trust.get("reviewMode")
    if mode=="DISTINCT_AI_CONTENT_RECEIPT_V1":
        if trust.get("requireHumanTeacher") is not False:
            return False,"ai_review_policy_has_legacy_teacher_requirement"
        # No trust in author-controlled QA review fields, no auto PASS:
        # a verified E receipt must already be pinned in protected main.
        receipts=trust.get("trustedAiReviewReceipts")
        if not isinstance(receipts,dict) or qid not in receipts:
            return False,"distinct_ai_content_review_missing"
        if not _ai_registry_exactly_matches_protected_main_policy(trust):
            return False,"ai_review_registry_not_verified_against_protected_main"
        return separate_ai_content_receipt_verified(
            source,audit,question,manifest,teaching_document,raw_teaching,
            trusted_receipts=receipts)
    if mode is not None:
        return False,"unknown_new_admission_review_mode"
    # Pre-policy signed-human path below is retained ONLY for archived
    # backwards-compatibility tests/custom legacy snapshots. It is not called
    # by the current repository policy's explicit AI reviewMode.
    att=(audit or {}).get("independentReviewAttestation")
    if not isinstance(att,dict):
        return False,"not_independently_attested"
    keys=trust.get("authorizedReviewers")
    signer=keys.get(att.get("keyId")) if isinstance(keys,dict) and isinstance(att.get("keyId"),str) else None
    if not isinstance(signer,dict) or signer.get("enabled") is not True:
        return False,"no_externally_authorized_reviewer_key"
    # Revocation and expiration must be enforced by the owner-controlled
    # registry even if old signed payloads were once approved.
    if signer.get("revokedAt") is not None:
        return False,"reviewer_key_revoked"
    if type(signer.get("githubUserId")) is not int or signer["githubUserId"]<=0:
        return False,"reviewer_github_identity_not_proven"
    try:
        now=datetime.now(timezone.utc)
        earliest=_time(signer.get("validFrom"))
        latest=_time(signer.get("expiresAt"))
        if not earliest<=now<latest:
            return False,"reviewer_key_outside_authorization_window"
    except (ValueError,TypeError):
        return False,"reviewer_authorization_dates_invalid"
    statement=att.get("payload")
    if not isinstance(statement,dict):
        return False,"no_signed_statement"
    official_sha=_official_document_sha(source,audit,qid)
    if not official_sha or not isinstance(question.get("answer"),str):
        return False,"signed_official_document_missing"
    expected={
        "schemaVersion":1,"year":question.get("year"),"questionId":qid,
        "questionRevision":revision,"webpSha256":webp,
        "teachingDigest":digest(canonical(teaching_document["content"])),
        "teachingEvidenceSha256":digest(raw_teaching),
        "officialAnswer":question.get("answer"),
        "officialEvidenceSha256":official_sha,
        "reviewerLogin":signer.get("login"),"reviewerRole":signer.get("role")
    }
    if any(statement.get(k)!=v for k,v in expected.items()):
        return False,"signed_material_or_identity_mismatch"
    author=statement.get("sourceAuthorLogin")
    if not isinstance(author,str) or not author.strip() or author.casefold()==str(signer.get("login","")).casefold():
        return False,"not_distinct_from_author"
    if (trust.get("requireHumanTeacher") is True
            and signer.get("role")!="qualified_human_teacher"):
        return False,"qualified_teacher_required"
    if signer.get("organizationVerified") is not True:
        return False,"no_offline_reviewer_identity_validation"
    if not isinstance(statement.get("reviewedAt"),str) or not statement["reviewedAt"].strip():
        return False,"review_timestamp_missing"
    try:
        reviewed=_time(statement["reviewedAt"])
        if not _time(signer["validFrom"])<=reviewed<_time(signer["expiresAt"]):
            return False,"review_outside_signer_authorization"
    except (ValueError,TypeError):
        return False,"review_time_unverified"
    if not _protected_main_trust_verified():
        return False,"unprotected_main_cannot_authorize_reviewer_keys"
    if not _author_and_github_review_verified(statement,signer):
        return False,"github_pr_author_or_review_event_unverified"
    options=statement.get("optionByOptionFindings")
    if (not isinstance(options,dict) or set(options)!=set("ABCD")
            or any(not isinstance(options[k],str) or len(options[k].strip())<12 for k in "ABCD")):
        return False,"no_substantive_four_option_review"
    if (statement.get("teacherAndElementaryReviewed") is not True
            or statement.get("reviewedCalculationOrNoncalculation") is not True):
        return False,"no_complete_teaching_review"
    if not substantive_notes_verified(source,statement.get("reviewNotesPath"),statement.get("reviewNotesSha256")):
        return False,"signed_independent_review_notes_absent_or_changed"
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        pub=base64.b64decode(signer.get("ed25519PublicKey",""),validate=True)
        sig=base64.b64decode(att.get("signature",""),validate=True)
        if len(pub)!=32 or len(sig)!=64:
            return False,"malformed_signature"
        Ed25519PublicKey.from_public_bytes(pub).verify(sig,canonical(statement))
    except (ValueError,TypeError,ImportError,InvalidSignature):
        return False,"signed_review_not_validated"
    return True,"trusted_distinct_reviewer_signed_material_and_substantive_notes"
